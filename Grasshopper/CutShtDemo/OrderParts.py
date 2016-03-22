# OrderParts.py - contents of the OrderParts ghpython script

# inputs
#   layer_name - str indicating Rhino layer name where parts are stored
# outputs
#   out    - console debugging output
#   array   - list of srfs representing part boundaries
#   names - a list of strs corresponding to Rhino.DocObject Names
# notes
#   Best if Rhino parts are named with sequential integers
#   script reorders grasshopper list to correspond to Rhino part order and 
#   maintains Rhio naming convention

import rhinoscriptsyntax as rs
import ghutil.ghrhinodoc as ghutil
import ghutil.trees as trees
import scriptcontext as sc
import Rhino as r

#============================================================================

#fetch all objects on specified layer
all_objects = ghutil.all_doc_objects(layer_name)

# get and order Rhino object names
name = [obj.Name for obj in all_objects]
names = sorted(name)
geom = [obj.Geometry for obj in all_objects]

# create a list of srfs based on ordered name list
dict_tuple = zip(name,geom)
parts = dict(dict_tuple)
array = []
items = sorted(parts)
for item in items:
    array.append (parts[str(item)])
    