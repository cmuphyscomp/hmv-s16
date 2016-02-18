# AddGeometry.py - contents of the AddGeometry ghpython script

# inputs
#   layer  - string naming the layer to address within the current Rhino document
#   gobj   - geometry object to add, either a raw Geometry type or a ghdoc GUID
#   name   - object name string
#  update  - dummy input to force adding again

# outputs
#   out    - console debugging output
#   guid   - GUID strings for the new geometry primitive
#
# Note: the GUIDs are for objects located in the RhinoDoc database, *not* the
# Grasshopper document database, so they are only useful for requesting updates
# to the current Rhino document.

import Rhino
import System.Guid
import pythonlibpath; pythonlibpath.add_library_path()
import ghutil.ghrhinodoc as ghrhinodoc

# Fetch the layer index, creating the layer if not present.
layer_name = str(layer)
layer_index = ghrhinodoc.fetch_or_create_layer_index(layer_name)

# If needed, find the geometry corresponding with the given input, possibly looking it up by GUID.
item = ghrhinodoc.find_ghdoc_geometry(ghdoc, gobj)
print "Input item is ", item, type(item)

# Add the geometry to the RhinoDoc with the given layer and name.
guid = str(ghrhinodoc.add_geometry(item, layer_index, name))
