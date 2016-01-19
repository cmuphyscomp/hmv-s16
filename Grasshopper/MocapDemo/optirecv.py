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

#================================================================
# Convert from default Optitrack coordinates with a XZ ground plane to default
# Rhino coordinates with XY ground plane.

def rotated_point(pt):
    return [pt[0], -pt[2], pt[1]]

def rotated_orientation(q):
    return [q[0], -q[2], q[1], q[3]]

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
        self.positions = list()  # list of [x,y,z] points
        self.rotations = list()  # list of [x,y,z,w] quaternions
        return

    def make_data_trees(self):
        """Return all received or computed values as Grasshopper data trees."""

        if len(self.rotations) == 0:
            return None, None, None, None

        # generate a list of (xaxis,yaxis) tuples and then transpose it into separate lists
        xaxes, yaxes = zip( *[quaternion_to_xaxis_yaxis(rot) for rot in self.rotations] )

        # return the positions as a list of Point3d objects
        p_tree = [Rhino.Geometry.Point3d(*pt) for pt in self.positions]

        # convert the quaternions stored as a Python lists of lists into a Grasshopper data tree object
        r_tree = vectors_to_data_tree(self.rotations)

        # return the basis vectors as lists of Point3d objecs
        x_tree = [Rhino.Geometry.Point3d(*vec) for vec in xaxes]
        y_tree = [Rhino.Geometry.Point3d(*vec) for vec in yaxes]

        return p_tree, r_tree, x_tree, y_tree

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

        if type(packet) is optirx.FrameOfData:
            nbodies = len(packet.rigid_bodies)
            print "Received frame data with %d rigid bodies." % nbodies
            if nbodies > 0:
                print packet.rigid_bodies[0]

                # rotate the coordinates into Rhino conventions and save them in the object instance as Python lists
                self.positions = [ rotated_point(body.position) for body in packet.rigid_bodies]
                self.rotations = [ rotated_orientation(body.orientation) for body in packet.rigid_bodies]

                # return a new data indication
                return True

        # else return a null result
        return True

#================================================================
