# ReplaceGeometry.py - contents of the ReplaceGeometry ghpython script

# inputs
#   layer  - string naming the layer to address within the current Rhino document
#  update  - Boolean indicating the action is enabled
#   guid   - GUID string identifying a single object within the RhinoDoc to replace
#   gobj   - geometry object to add, either a raw Geometry type or a ghdoc GUID

# outputs
#   out    - console debugging output
#  newid   - GUID strings for the new geometry primitive
# Note: the GUIDs are for objects located in the RhinoDoc database, *not* the
# Grasshopper document database, so they are only useful for requesting updates
# to the current Rhino document.

import Rhino
import System.Guid
import pythonlibpath; pythonlibpath.add_library_path()
import ghutil.ghrhinodoc as ghrhinodoc

if update and guid is not None:
    # Fetch the layer index, creating the layer if not present.
    layer_name = str(layer)
    layer_index = ghrhinodoc.fetch_or_create_layer_index(layer_name)
    
    # Look up the object to delete.
    print "GUID to modify is", guid, type(guid)
    
    # convert from a string to a Guid object
    guid = System.Guid(guid)
    
    existing = Rhino.RhinoDoc.ActiveDoc.Objects.Find(guid)
    print "Found RhinoDoc object", existing
    if existing is not None:
        name = existing.Attributes.Name
        print "Existing object has name", name
        # Delete the geometry from the RhinoDoc with the given layer and name.
        Rhino.RhinoDoc.ActiveDoc.Objects.Delete(guid, True)

        # If needed, find the geometry corresponding with the given input, possibly looking it up by GUID.
        item = ghrhinodoc.find_ghdoc_geometry(ghdoc, gobj)
        print "Input item is ", item, type(item)

        # Add the geometry to the RhinoDoc with the given layer and name.
        newid = str(ghrhinodoc.add_geometry(item, layer_index, name))