# optiload.py : motion capture data loader for use within Grasshopper ghpython objects

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

# import the Optitrack CSV file parser
import optitrack.csv_reader as csv

# import a quaternion conversion function
from optitrack.geometry import quaternion_to_xaxis_yaxis

# load the Grasshopper utility functions from the course packages
from ghutil import *

#================================================================ 
def load_csv_file(path):
    take = csv.Take().readCSV(path)
    return take

#================================================================
# Convert from default Optitrack coordinates with a XZ ground plane to default
# Rhino coordinates with XY ground plane.

def rotated_point(pt):
    return Rhino.Geometry.Point3d( pt[0], -pt[2], pt[1])

def rotated_orientation(q):
    return [q[0], -q[2], q[1], q[3]]

#================================================================

def make_data_trees(take):
    """Convert all the position and orientation trajectories into data trees in a Rhino-convenient coordinate frame."""
    
    # The 'positions' data tree contains Point objects as leaves in a 2-D tree with
    # dimensions (num_bodies, num_frames).  First, extract all position data and
    # convert to Point3d objects within a Python list structure.  The inner
    # comprehension is a filter which simply deletes all missing frames.  Each
    # 'body' in the take.rigid_bodies dictionary is a RigidBody object.
    # body.positions is a list with one element per frame, either None or [x,y,z].

    py_position = [ [rotated_point(pos) for pos in body.positions if pos is not None] for body in take.rigid_bodies.values()]

    # Next recursively convert from a Python tree to a data tree.
    position = list_to_tree(py_position)

    # Extract a tree of quaternion trajectories.  The leaves are numbers, the dimensions are (num_bodies, num_frames, 4).
    py_rotation = [ [rotated_orientation(rot) for rot in body.rotations if rot is not None] for body in take.rigid_bodies.values()]

    # Generate a tree of basis vector pairs (xaxis, yaxis).  Dimensions are (num_bodies, num_frames, 2, 3)
    basis_vectors = [[quaternion_to_xaxis_yaxis(rot) for rot in body] for body in py_rotation]

    # Extract the X axis basic elements into a tree of Points with dimension (num_bodies, num_frames).
    xaxis = list_to_tree([[Rhino.Geometry.Point3d(*(basis[0])) for basis in body] for body in basis_vectors])

    # Same for Y.
    yaxis = list_to_tree([[Rhino.Geometry.Point3d(*(basis[1])) for basis in body] for body in basis_vectors])

    return position, xaxis, yaxis
