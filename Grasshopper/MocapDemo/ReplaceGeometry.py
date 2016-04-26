# ReplaceGeometry.py - contents of the ReplaceGeometry ghpython script
#
# inputs
#   layer  - string naming the layer to address within the current Rhino document
#  update  - Boolean indicating the action is enabled
#   guids  - list of GUID strings identifying a single object within the RhinoDoc to replace
#   gobjs  - equal-length list of geometry objects to add, either a raw Geometry type or a ghdoc GUID
#
# Note: guids and gobjs must be set to 'List Access'
#
# outputs
#   out    - console debugging output
#  newids  - list of GUID strings for the new geometry primitive
#
# Note: the GUIDs are for objects located in the RhinoDoc database, *not* the
# Grasshopper document database, so they are only useful for requesting updates
# to the current Rhino document.

# Note: the new object Name attributes are copied from the objects to be deleted so they persist.  This could
# be extended to other user-specified properties if desired.

import Rhino
import System.Guid
import pythonlibpath; pythonlibpath.add_library_path()
import ghutil.ghrhinodoc as ghrhinodoc

if update and guids is not None:
    # Fetch the layer index, creating the layer if not present.
    layer_name = str(layer)
    layer_index = ghrhinodoc.fetch_or_create_layer_index(layer_name)
    newids = list()
    
    for guid, gobj in zip(guids, gobjs):
        # Look up the object to delete.  Convert from a string to a Guid object, then search the active document.
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
            newids.append(str(ghrhinodoc.add_geometry(item, layer_index, name)))
            
        else:
            # if something goes wrong, make sure the output indicates a null for this object
            newids.append(None)