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

# use itertools for subsampling sequences
import itertools

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
    if pt is None:
        return None
    else:
        return Rhino.Geometry.Point3d( pt[0], -pt[2], pt[1])

def rotated_orientation(q):
    if q is None:
        return [0,0,0,1]
    else:
        return [q[0], -q[2], q[1], q[3]]

def plane_or_null(origin,x,y):
    """Utility function to create a Plane unless the origin is None, in which case it returns None."""
    if origin is None:
        return None
    else:
        return Rhino.Geometry.Plane(origin, x, y)

#================================================================
def all_Planes(take, stride=1):
    """Return a DataTree of trajectories containing Planes or None.

    The tree has one branch for each rigid body; each branch contains a list of
    objects, either Plane for a valid sample or None if the sample is missing.

    Due to implicit ghpython conversions, the branches will end up described by
    paths {0;0},{0;1},{0;2}, etc.

    :param stride: the skip factor to apply for subsampling input (default=1, no subsampling)
    """

    # Extract the origin position data and convert to Point3d objects within a
    # Python list structure.  The subsampling is handled within the
    # comprehension.  Note that missing data is returned as None.  Each 'body'
    # in the take.rigid_bodies dictionary is a RigidBody object.  body.positions
    # is a list with one element per frame, either None or [x,y,z].
    origins = [ [rotated_point(pos) for pos in itertools.islice(body.positions, 0, len(body.positions), stride)] \
                for body in take.rigid_bodies.values()]

    # Similar to extract a tree of quaternion trajectories.  The leaves are
    # numbers, the dimensions are (num_bodies, num_frames, 4).
    quats = [ [rotated_orientation(rot) for rot in itertools.islice(body.rotations, 0, len(body.rotations), stride)] \
              for body in take.rigid_bodies.values()]

    # Generate a tree of basis vector pairs (xaxis, yaxis).  Dimensions are (num_bodies, num_frames, 2, 3)
    basis_vectors = [[quaternion_to_xaxis_yaxis(rot) for rot in body] for body in quats]

    # Extract the X axis basis elements into a tree of Vector3d objects with dimension (num_bodies, num_frames).
    xaxes = [[Rhino.Geometry.Vector3d(*(basis[0])) for basis in body] for body in basis_vectors]

    # Same for Y.
    yaxes = [[Rhino.Geometry.Vector3d(*(basis[1])) for basis in body] for body in basis_vectors]

    # Iterate over the 2D list structures, combining them into a 2D list of Plane objects.
    planes = [[plane_or_null(origin, x, y) for origin,x,y in zip(os,xs,ys)] for os,xs,ys in zip(origins, xaxes, yaxes)]

    # Recursively convert from a Python tree to a data tree.
    return list_to_tree(planes)

#================================================================
def frames_to_tree(frame_list):
    """Utility function to convert a list of list of Plane objects representing a trajectory segment into a GH data tree."""

    # Transpose the frame list for output.  As accumulated, it is a list of lists:
    # [[body1_sample0, body2_sample0, body3_sample0, ...], [body1_sample1, body2_sample1, body3_sample1, ...], ...]
    segment = zip(*frame_list)
    
    # Convert a Python list-of-lists into a data tree.  Segment is a list of trajectories:
    # [[body1_sample0, body1_sample1, body1_sample2, ...], [body2_sample0, body2_sample1, body2_sample2, ...], ...]
    planes = list_to_tree(segment)
