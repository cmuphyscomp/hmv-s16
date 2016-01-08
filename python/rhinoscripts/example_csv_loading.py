"""Example code for importing a single rigid body trajectory into Rhino from a Optitrack CSV file.

Copyright (c) 2016, Garth Zeglin.  All rights reserved. Licensed under the terms
of the BSD 3-clause license as included in LICENSE.

Example code for generating a path of Rhino 'planes' (e.g. coordinate frame)
from a trajectory data file.  The path is returned as a list of Plane objects.

Each plane is created using an origin vector and X and Y basis vectors.  The
time stamps and Z basis vectors in the trajectory file are ignored.
"""

# Load the Rhino API.
import rhinoscriptsyntax as rs


# Make sure that the Python libraries also contained within this course package
# are on the load path.  This adds the parent folder to the load path, assuming that this
# script is still located with the rhinoscripts/ subfolder of the Python library tree.
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

# Load the Optitrack CSV file parser module.
import optitrack.csv_reader as csv
from optitrack.geometry import *

# Find the path to the test data file located alongside the script.
filename = os.path.join( os.path.abspath(os.path.dirname(__file__)), "sample_optitrack_take.csv")

# Read the file.
take = csv.Take().readCSV(filename)

# Print out some statistics
print "Found rigid bodies:", take.rigid_bodies.keys()

# Process the first rigid body into a set of planes.
bodies = take.rigid_bodies.values()

# for now:
xaxis = [1,0,0]
yaxis = [0,1,0]

if len(bodies) > 0:
    body = bodies[0]
    for pos,rot in zip(body.positions, body.rotations):
        if pos is not None and rot is not None:
            xaxis, yaxis = quaternion_to_xaxis_yaxis(rot)
            plane = rs.PlaneFromFrame(pos, xaxis, yaxis)

            # create a visible plane, assuming units are in meters
            rs.AddPlaneSurface( plane, 0.1, 0.1 )
