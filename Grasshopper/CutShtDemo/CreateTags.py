# CreateTags.py - contents of the CreateTags ghpython script

# inputs
#   array - a list of srfs representing parts
#   names - a list of strs to label parts
#   prefix - str to be added as prefix to string labels
# outputs
#   tagLabels    - a list of strs to label tags
#   tagLocations   - a list of points to locate tags
# Notes 
#   Part Array read directly from specified Rhino layer ("Cards" default). 
#   Part labels derived from Rhino object names.

import rhinoscriptsyntax as rs
import scriptcontext as sc
import ghutil.ghrhinodoc as ghutil
import Rhino as r

#==============================================================================
def create_tag_label(prefix,obj_name):
    """ Given an object and prefix, create a tag label that combines the prefix
        and Rhino object name. Return label as a string"""
    lable = prefix + "_"+ obj_name
    return lable

#==============================================================================
def create_tag_location (part,u,v):
    """Given a srf., create a tag location on the srf at a given normalized
        u,v parameter"""
    parameter = rs.SurfaceParameter(part,(u,v))
    tagPt = rs.EvaluateSurface(part,parameter[0],parameter[1])
    return tagPt

#==============================================================================
def tag_array (u,v,array,names):
    """ Create tag labels and locations for an array of srfs.. Returns a list of
        tuples with labels and locations."""
    labels = []
    locations = []
    for i in range(len(array)):
        labels.append (create_tag_label (prefix,names[i]))
        locations.append (create_tag_location (array[i],.5,.5))
    tags = (labels,locations)
    return tags

###############################################################################
tags = tag_array (.5,.5,array,names)
labels,positions = tags[0],tags[1]





