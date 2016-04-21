# LayerGeometry.py - contents of the LayerGeometry ghpython script

# inputs
#   layer  - string naming the layer to address within the current Rhino document
#  update  - any input will force recomputing the output (dummy value)

# outputs
#   out     - console debugging output
#   geoms   - list of geometry primitives currently present in the layer
#   guids   - list of GUID strings for the geometry primitives
#   names   - list of user-visible object names

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

# Fetch all objects on the layer and report out individual properties.
all_objects = ghrhinodoc.all_doc_objects(layer_name)

geoms = [obj.Geometry for obj in all_objects]
guids = [str(obj.Id) for obj in all_objects]
names = [obj.Attributes.Name for obj in all_objects]
