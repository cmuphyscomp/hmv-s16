# AddGeometry.py - contents of the AddGeometry ghpython script

# inputs
#   layer  - string naming the layer to address within the current Rhino document
#   gobjs  - list of geometry objects to add, either a raw Geometry type or a ghdoc GUID
#   names  - list of object name strings
# enabled  - Boolean to indicate the action is enabled
#
# Note: gobjs and names must be set to 'List Access'
#
# outputs
#   out    - console debugging output
#   guids  - list of GUID strings for the new geometry primitive
#
# Note: the GUIDs are for objects located in the RhinoDoc database, *not* the
# Grasshopper document database, so they are only useful for requesting updates
# to the current Rhino document.

import Rhino
import System.Guid
import pythonlibpath; pythonlibpath.add_library_path()
import ghutil.ghrhinodoc as ghrhinodoc

# Fetch the layer index, creating the layer if not present.
if enabled:
    layer_name = str(layer)
    layer_index = ghrhinodoc.fetch_or_create_layer_index(layer_name)
    guids = list()
    
    for gobj, name in zip(gobjs, names):
        # If needed, find the geometry corresponding with the given input, possibly looking it up by GUID.
        item = ghrhinodoc.find_ghdoc_geometry(ghdoc, gobj)

        # Add the geometry to the RhinoDoc with the given layer and name, returning the new RhinoDoc GUID as a string.
        guids.append(str(ghrhinodoc.add_geometry(item, layer_index, name)))
