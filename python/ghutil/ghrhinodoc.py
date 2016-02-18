# ghrhinodoc.py - utility functions for manipulating the RhinoDoc database from within Grasshopper

import Rhino
import System.Guid

#================================================================
def fetch_or_create_layer_index(name):
    """Given a layer name, return the integer layer index value.  If the layer doesn't exist, create it."""
    layers = Rhino.RhinoDoc.ActiveDoc.Layers
    existing = layers.Find(name, True) # flag: ignore deleted layers

    if existing == -1:
        # create a new layer in the active document
        new_layer = Rhino.DocObjects.Layer()
        new_layer.Name = name
        return layers.Add(new_layer)
    else:
        return existing
#================================================================
def add_geometry(geometry, layer_index = None, name = None):
    """Add the general geometry object (type GeometryBase) to the document,
    optionally on the given layer, and optionally with the given object name.
    Returns the GUID of the new DocObject wrapping the geometry object.
    This GUID is only valid within the RhinoDoc database.
    """

    attributes = Rhino.DocObjects.ObjectAttributes()
    if layer_index is not None:
        attributes.LayerIndex = layer_index
    if name is not None:
        attributes.Name = name
    return Rhino.RhinoDoc.ActiveDoc.Objects.Add(geometry, attributes)

#================================================================
def all_doc_objects(layer):
    """Return a list of all DocObjects on the given layer, specified by layer name."""
    return Rhino.RhinoDoc.ActiveDoc.Objects.FindByLayer(layer)

#================================================================
def find_ghdoc_geometry(ghdoc, gobj):
    """Find the Rhino.Geometry object identified by the given script input.  If an
    input has a 'ghdoc' type hint supplied, it will be supplied as a GUID
    identifying an object in the ghdoc document, and this function looks up the
    object.  Otherwise, it may be supplied as a Rhino.Geometry object which is
    simply returned.
    """
    
    if type(gobj) is System.Guid:
        # print "Looking up object GUID in Grasshopper document."
        # Find() returns an AttributedGeometry object with properties Geometry and ObjectAttributes
        item = ghdoc.Objects.Find(gobj)
        # print "Item is", item, type(item)
        return item.Geometry
    
    else:
        # print "Geometry was directly supplied."
        return gobj
    
#================================================================
