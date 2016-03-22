import os,sys

# The first system path element always appears to be the folder containing the Grasshopper sketch.
# Construct a valid path to the library code, then check to see if it needs to be added to sys.path.
python_library_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(sys.path[0]))), "python")

# sys.path is persistent, so only insert the library path on the first invocation
if sys.path[1] != python_library_path:
    print "Inserting python library path."
    sys.path.insert(1, python_library_path)
    print "sys.path is now", sys.path

# load the Grasshopper utility functions from the course packages
from ghutil import *

import ghutil.ghrhinodoc as ghutil
import ghutil.trees as trees

