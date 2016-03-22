# CreateCutSht.py - contents of the CreateCutsht ghpython script

# inputs
#   layers -  a list of strs representing cut sht layers to create in Rhino
#   no_cut - geo for no_cut layer
#   score - geo for score layer
#   cut_1 - geo for cut_1 layer
#   cut_2 - geo for cut_2 layer
# outputs
#   out    - console debugging output
# notes
#   script currently hard coded to take in geo from only those layers reprsented 
#   in input.


import scriptcontext as sc
import Rhino as r
import ghutil.ghrhinodoc as ghutil

#==============================================================================

# take in all geo inputs and order them by layer name list
allItems = [no_cut,score,cut_1,cut_2]
layerNum = 0
for name in layers:
    # create or fetch cut sht layers
    layer =  ghutil.fetch_or_create_layer_index(name)
    # delete any current items on these layers 
    all_objects = ghutil.all_doc_objects(name)
    for obj in all_objects:
        r.RhinoDoc.ActiveDoc.Objects.Delete(obj, True)
    # add all objects associated with layer
    layerItems = allItems[layerNum]
    layerNum +=1
    for item in layerItems:
        ghutil.add_geometry(item,layer)


