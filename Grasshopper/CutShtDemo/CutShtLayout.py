# CutShtLayout.py - contents of the CutShtLayout ghpython script

# inputs
#   features -  any geometry associated with parts to be placed on stock
#   stockOutline - a srf defining the extent of the stock
#   partSpacing - spacing btwn parts on stock (float)
#   margin - offset from stock edge (float)
# outputs
#   out    - console debugging output
#   basePlanes   - a list of part base planes
#   targetPlanes - a list of part target planes
#   cutShtGeo - part slots and features stored in branches
# notes
#   Part Array read directly from specified Rhino layer ("Cards" default). 
#   Part labels derived from Rhino object names. 

import rhinoscriptsyntax as rs
import ghutil.ghrhinodoc as ghutil
import ghutil.trees as trees
import scriptcontext as sc
import Rhino as r


#=============================================================================
def set_part_base_plane(part):
    """returns an alinged plane at (U.5,V.5) of a planar surface"""
    x = True
    if x == True:#rs.IsPlaneSurface(part):
        normalizedParameter = (.5,.5)
        frameParameter = rs.SurfaceParameter(part,normalizedParameter)
        frame = rs.SurfaceFrame(part,frameParameter)
        return frame
    else: return "object is not a planar surface"

#==============================================================================
def set_partAligned_boundingBox(part):
    """returns a bounding box aligned to a planar surface"""
    basePlane = set_part_base_plane(part)
    boundingBox = rs.BoundingBox(part,basePlane)
    return boundingBox

#=============================================================================
def dimension_boundingBox(part):
    """returns a tuple with the height and width of bounding box"""
    boundingBox = set_partAligned_boundingBox(part)
    lineHeight = rs.AddLine(boundingBox[0],boundingBox[1])
    lineWidth = rs.AddLine(boundingBox[0],boundingBox[3])
    partHeight = rs.CurveLength(lineHeight)
    partWidth = rs.CurveLength(lineWidth)
    dimensions = (partHeight,partWidth)
    return dimensions

#=============================================================================
def generate_base_planes_from_array(array):
    """returns a list of base planes aligned to objects in an array"""
    basePlanes = []
    for i in range(len(array)):
        part = array[i]
        basePlanes.append(set_part_base_plane(part))
    return basePlanes

#=============================================================================
def create_cut_sht_targets(stockOutline,array,margin,partSpacing):
    """returns a list of target planes to evenly space parts on a given stock"""
    numParts = len(array)
    stockDimensions = dimension_boundingBox(stockOutline)
    partDimensions = dimension_boundingBox(array[0])
    stockHeight = stockDimensions[0]
    stockWidth = stockDimensions[1]
    partHeight = partDimensions[0]
    partWidth = partDimensions[1]
    
    yStartPt = partWidth/2.0 + margin
    xStartPt = partHeight/2.0 + margin
    ySpacing = partWidth + partSpacing
    xSpacing = partHeight + partSpacing
    rowWidth = stockWidth - (2*margin)
    columnHeight = stockHeight - (2*margin)
    
    currentX = xStartPt
    currentY = yStartPt
    locationPts = []
    targetPlanes = []

    for i in range (len(array)):
        xLimit = currentX + (partWidth/2.0) 
        yLimit = currentY + (partHeight/2.0)
        if yLimit > columnHeight:
            print "parts do not fit on stock"
            return None 
        elif xLimit > rowWidth:
            currentY += ySpacing
            currentX = xStartPt
            partCenterPt = rs.AddPoint(currentX,currentY,0)
            locationPts.append(partCenterPt)
            targetPlane = rs.PlaneFromFrame( partCenterPt, [1,0,0], [0,1,0] )
            targetPlanes.append(targetPlane)
            currentX += xSpacing
        else:
            partCenterPt = rs.AddPoint(currentX,currentY,0)
            locationPts.append(partCenterPt)
            targetPlane = rs.PlaneFromFrame( partCenterPt, [1,0,0], [0,1,0] )
            targetPlanes.append(targetPlane)
            currentX += xSpacing
    return targetPlanes

#=============================================================================
def reorient_objects(objects,basePlane,targetPlane, copy = True):
    """performs a plane to plane reorient on an object w/ or w/out copying"""
    if targetPlane == None:
        return None
    else:
        world = rs.WorldXYPlane()
        xform1 = rs.XformChangeBasis(world,basePlane)
        xform2 = rs.XformChangeBasis (targetPlane,world)
        xform_final = rs.XformMultiply(xform2,xform1)
        transform = rs.TransformObjects(objects,xform_final,copy)
        return transform

def create_cut_sht(stockOutline,array,features,partSpacing,margin):
    """ """
    numParts = len(array)
    basePlanes = generate_base_planes_from_array(array)
    targetPlanes = create_cut_sht_targets(stockOutline,array,margin,partSpacing)
    if targetPlanes == None:
        return None
    else:
        # converts GH branch to python list for a set of features
        features = [item for item in features.Branches]
        cut_sht = []
        for i in range(numParts):
            objects = [array[i]]
            for item in features[i]:
                objects.append(item)
            cutPart = reorient_objects(objects,basePlanes[i],targetPlanes[i])
            cut_sht.append(cutPart)
    return cut_sht
    
###############################################################################
a = trees.list_to_tree(generate_base_planes_from_array(array))
b = create_cut_sht_targets(stockOutline,array,margin,partSpacing)
c = trees.list_to_tree(create_cut_sht(stockOutline,array,features,partSpacing,margin))