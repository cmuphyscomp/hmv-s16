"""\
pythonlibpath.py : utility module to ensure the course Python library is included in the load path.

The add_library_path function should be run from any ghpython object which needs
to directly import a module from the course library. This file should be present
in the same folder as the .gh file so it can be found using the default ghpython
load path.
"""

# Make sure that the Python libraries that are also contained within this course
# package are on the load path. This adds the python/ folder to the load path
# *after* the current folder.  The path manipulation assumes that this module is
# still located within a Grasshopper/* subfolder, and so the package modules are
# at ../../python.

# In Rhino Python, sys.path does not appear to be shared *between* ghpython
# blocks, but *is* persistent across invocations of the same block.

# However, the module cache *is* shared, so different blocks may not see the
# same value of sys.path, but they will use a cached module during import.  For
# this reason, if only one block successfully sets sys.path and loads a library
# module, other blocks can also import it even if sys.path doesn't include the
# library.  However, it is tricky to guarantee evaluation order of ghpython
# blocks, so it isn't reliable to depend upon other scripts having imported a
# module first.

import sys, os

def add_library_path():
    library_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__)))), "python")
    if sys.path[1] != library_path:
        sys.path.insert(1, library_path)
