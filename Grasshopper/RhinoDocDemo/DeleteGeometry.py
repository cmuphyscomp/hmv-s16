# DeleteGeometry.py - contents of the DeleteGeometry ghpython script

# inputs
#   layer  - string naming the layer to address within the current Rhino document
#   guid   - GUID string identifying a single object within the RhinoDoc

# outputs
#   out    - console debugging output
#
# Note: the GUIDs are for objects located in the RhinoDoc database, *not* the
# Grasshopper document database, so they are only useful for requesting updates
# to the current Rhino document.

import Rhino
import System.Guid
import ghrhinodoc

if guid is not None:
    # Fetch the layer index, creating the layer if not present.
    layer_name = str(layer)
    layer_index = ghrhinodoc.fetch_or_create_layer_index(layer_name)
    
    # Look up the object to delete.
    print "GUID to modify is", guid, type(guid)
    
    # convert from a string to a Guid object
    guid = System.Guid(guid)
    
    existing = Rhino.RhinoDoc.ActiveDoc.Objects.Find(guid)
    print "Found RhinoDoc object", existing
    
    # Delete the geometry from the RhinoDoc with the given layer and name.
    Rhino.RhinoDoc.ActiveDoc.Objects.Delete(guid, True)
