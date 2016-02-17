# optirecv.py : motion capture data receiver for use within Grasshopper ghpython objects

# Copyright (c) 2016, Garth Zeglin. All rights reserved. Licensed under the
# terms of the BSD 3-clause license.

# use RhinoCommon API
import Rhino

# Make sure that the Python libraries that are also contained within this course
# package are on the load path. This adds the python/ folder to the load path
# *after* the current folder.  The path manipulation assumes that this module is
# still located within the Grasshopper/MocapDemo subfolder, and so the package
# modules are at ../../python.
import sys, os
sys.path.insert(1, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__)))), "python"))

# import the Optitrack stream decoder
import optirx

# import a quaternion conversion function
from optitrack.geometry import quaternion_to_xaxis_yaxis

# load the Grasshopper utility functions from the course packages
from ghutil import *

# share the mocap coordinate conversion code with the CSV loader
from optiload import rotated_point, rotated_orientation, plane_or_null

#================================================================
class OptitrackReceiver(object):
    def __init__(self, version_string):
        # The version string should be of the form "2900" and should match the SDK version of the Motive software.
        # E.g. Motive 1.9 == SDK 2.9.0.0 == "2900"
        self.sdk_version = tuple(map(int,version_string)) # e.g. result is (2,9,0,0)

        # create a multicast UDP receiver socket
        self.receiver = optirx.mkdatasock()

        # set non-blocking mode so the socket can be polled
        self.receiver.setblocking(0)

        # Keep track of the most recent results.  These are stored as normal Python list structures, but
        # already rotated into Rhino coordinate conventions.
        self.positions = list()  # list of Point3d objects
        self.rotations = list()  # list of [x,y,z,w] quaternions as Python list of numbers
        self.bodynames = list()  # list of name strings associated with the bodies
        return

    #================================================================
    def make_plane_list(self):
        """Return the received rigid body frames as a list of Plane or None (for missing data), one entry per rigid body stream."""

        # convert each quaternion into a pair of X,Y basis vectors
        basis_vectors = [quaternion_to_xaxis_yaxis(rot) for rot in self.rotations]

        # Extract the X and Y axis basis elements into lists of Vector3d objects.
        xaxes = [Rhino.Geometry.Vector3d(*(basis[0])) for basis in basis_vectors]
        yaxes = [Rhino.Geometry.Vector3d(*(basis[1])) for basis in basis_vectors]

        # Generate either Plane or None for each coordinate frame.
        planes = [plane_or_null(origin, x, y) for origin,x,y in zip(self.positions, xaxes, yaxes)]
        return planes

    #================================================================
    def _markers_coincide(self, m1, m2):
        """For now, an exact match (could be fuzzy match)."""
        return m1[0] == m2[0] and m1[1] == m2[1] and m1[2] == m2[2]
        
    def _identify_rigid_bodies(self, sets, bodies):
        """Compare marker positions to associate a named marker set with a rigid body.
        :param sets: dictionary of lists of marker coordinate triples
        :param bodies: list of rigid bodies
        :return: dictionary mapping body ID numbers to body name

        Some of the relevant fields:
        bodies[].markers  is a list of marker coordinate triples
        bodies[].id       is an integer body identifier with the User Data field specified for the body in Motive
        """

        # for now, do a simple direct comparison on a single marker on each body
        mapping = dict()
        for body in bodies:
            marker1 = body.markers[0]
            try:
                for name,markerset in sets.items():
                    if name != 'all':
                        for marker in markerset:
                            if self._markers_coincide(marker1, marker):
                                mapping[body.id] = name
                                raise StopIteration
            except StopIteration:
                pass

        return mapping
                         
    #================================================================
    def poll(self):
        """Poll the mocap receiver port and return True if new data is available."""
        try:
            data = self.receiver.recv(optirx.MAX_PACKETSIZE)
        except:
            return False

        packet = optirx.unpack(data, version=self.sdk_version)

        if type(packet) is optirx.SenderData:
            version = packet.natnet_version
            print "NatNet version received:", version

        elif type(packet) is optirx.FrameOfData:
            nbodies = len(packet.rigid_bodies)
            # print "Received frame data with %d rigid bodies." % nbodies
            # print "Received FrameOfData with sets:", packet.sets
            # There appears to be one marker set per rigid body plus 'all'.
            # print "Received FrameOfData with names:", packet.sets.keys()
            # print "First marker of first marker set:", packet.sets.values()[0][0]
            # print "Received FrameOfData with rigid body IDs:", [body.id for body in packet.rigid_bodies]
            # print "First marker of first rigid body:", packet.rigid_bodies[0].markers[0]
            # print "First tracking flag of first rigid body:", packet.rigid_bodies[0].tracking_valid

            # compare markers to associate the numbered rigid bodies with the named marker sets
            mapping = self._identify_rigid_bodies( packet.sets, packet.rigid_bodies)
            # print "Body identification:", mapping
            
            if nbodies > 0:
                # print packet.rigid_bodies[0]

                # rotate the coordinates into Rhino conventions and save them in the object instance as Python lists
                self.positions = [ rotated_point(body.position) if body.tracking_valid else None for body in packet.rigid_bodies]
                self.rotations = [ rotated_orientation(body.orientation) for body in packet.rigid_bodies]
                self.bodynames = [ mapping.get(body.id, '<Missing>') for body in packet.rigid_bodies]
                
                # return a new data indication
                return True

        elif type(packet) is optirx.ModelDefs:
            print "Received ModelDefs:", packet

        else:
            print "Received unhandled NatNet packet type:", packet
            
        # else return a null result
        return False

#================================================================
