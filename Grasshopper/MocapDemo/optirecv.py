# optirecv.py : motion capture data receiver for use within Grasshopper ghpython objects

# Copyright (c) 2016, Garth Zeglin. All rights reserved. Licensed under the
# terms of the BSD 3-clause license.

# import the Grasshopper Data Tree API
import clr
clr.AddReference("Grasshopper")
import Grasshopper as gh

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

#== support functions ====================================================
def vectors_to_data_tree(vector_list):
    """ Converts a list of Python tuples to a GH datatree."""
    dataTree = gh.DataTree[float]()
    for i,vec in enumerate(vector_list):
        for value in vec:
            dataTree.Add(value,gh.Kernel.Data.GH_Path(i))
    return dataTree
        
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

        # Keep track of the most recent results.  These are stored as normal Python list structures.
        self.positions = list()  # list of [x,y,z] points
        self.rotations = list()  # list of [x,y,z,w] quaternions
        return

    def make_data_trees(self):
        """Return all received or computed values as Grasshopper data trees."""

        if len(self.rotations) == 0:
            return None, None, None, None

        # generate a list of (xaxis,yaxis) tuples and then transpose it into
        # separate lists
        xaxes, yaxes = zip( *[quaternion_to_xaxis_yaxis(rot) for rot in self.rotations] )

        # convert all Python lists of lists into Grasshopper data tree objects
        p_tree = vectors_to_data_tree(self.positions)
        r_tree = vectors_to_data_tree(self.rotations)
        x_tree = vectors_to_data_tree(xaxes)
        y_tree = vectors_to_data_tree(yaxes)

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
                self.positions = [ body.position for body in packet.rigid_bodies]
                self.rotations = [ body.orientation for body in packet.rigid_bodies]
                # return a new data indication
                return True
                
        # else return a null result
        return True

#================================================================ 
