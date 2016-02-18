# CSVLoader.py - the file loader script in the ghpython object in MocapDemo.gh.

# Demonstration of parsing an Optitrack motion capture CSV file.
#
# inputs
#   path    - string with the full path to the CSV file
#   stride  - the sequence interval between successive points; 1 returns all points, >1 subsamples
#
# outputs
#   out      - debugging text stream
#   names    - data tree of body names
#   planes   - data tree of Plane trajectories, one branch per rigid body, each leaf a list of Planes

# import the Optitrack file loader from the same folder
import optiload

# load the file
take = optiload.load_csv_file(path)

print "Found rigid bodies:", take.rigid_bodies.keys()

# emit all return values
names = take.rigid_bodies.keys()
planes = optiload.all_Planes(take, int(stride))
