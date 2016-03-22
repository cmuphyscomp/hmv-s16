# CreateSlots.py - contents of the CreateSlots ghpython script

# inputs
#   array - srfs output from orderedParts gh component
# outputs
#   out    - console debugging output
#  slots   - a collection of curves for slotting parts together

import rhinoscriptsyntax as rs
import ghutil.ghrhinodoc as ghutil
import ghutil.trees as trees
import scriptcontext as sc
import Rhino as r

#=============================================================================
def find_neighbor_intersections(array,partIndex):
    """Given an array of srfs. find all intersections with a given srf. 
       Return a list of tuples with neighbor index and 
       crvs. representing intersections"""
    intersections = []
    numItems = len(array)
    if partIndex >= numItems:
        return "part index outside of array"
    part = array[partIndex]
    #only searches neighbors indexed higher in the array
    for i in range (partIndex, numItems):
        neighbor = array[i]
        intersectionTest = rs.IntersectBreps(part,neighbor)
        if intersectionTest != None:
            intersections.append((i,intersectionTest))
    # if there are no intersections alert the user
    if len(intersections) == 0:
        return "this part does not intersect with its neighbors"
    else:
        return intersections

#=============================================================================
def evaluateCrv (crv,normalizedParameter):
    """Returns a point on a curve given a normalized parameter."""
    crvParam = rs.CurveParameter(crv,normalizedParameter)
    crvPt = rs.EvaluateCurve(crv,crvParam)
    return crvPt

#=============================================================================
def create_slots (array,partIndex):
    """ Creates half-lap slots for a given part with its intersecting neighbors.
        Returns a list of tuples with part index and slot curve."""
    numItems = len(array)
    if partIndex >= numItems:
        return "part index outside of array"
    part = array[partIndex]
    intersections = find_neighbor_intersections(array,partIndex)
    boundary = rs.DuplicateSurfaceBorder(part)
    slots = []
    ## check intersections with the part's boundary to determine joint case
    ## rs.CurveCurveIntersection returns case specific lists see F1 help.
    for line in intersections:
        if len(line) == 1: return
        intersectTest = rs.CurveCurveIntersection(line[1],boundary)
        ## Case 1: slot is floating in part boundary (Only works in some cases)
        if intersectTest == None:
            slots.append((partIndex,line[1]))
        ## Case 2: intersection coincedent along an edge and can't be slotted 
        elif intersectTest[0][0] == 2:
            print "no slot needed"
        ## Case 3: part and neighbor have a valid connection and slot is drawn
        else:    
            ## create Current Part slot
            startPoint = intersectTest[0][1]
            endPoint = evaluateCrv(line[1],.5)
            slot = rs.AddLine(startPoint,endPoint)
            slots.append((partIndex,slot))
            ## create neighbor slot
            testPoint = rs.CurveEndPoint(line[1])
            distance = rs.Distance(startPoint,testPoint)
            if distance != 0:
                startPoint = testPoint
            else:
                startPoint = rs.CurveStartPoint(line[1])
            slot = rs.AddLine(startPoint,endPoint)
            slots.append((line[0],slot))
    return slots

#=============================================================================
def create_all_slots (array):
    """Creates slots for all srfs. in an array. Returns a 2D list with 
       slots grouped by part."""
    numItems = len(array)
    slotCollection =[[] for i in range(numItems)]
    
    for i in xrange (numItems):
        currentSlots = create_slots(array,i)
        if currentSlots != None:
            for slot in currentSlots:
                slotCollection[slot[0]].append(slot[1])
    return slotCollection

######################################################
slots = trees.list_to_tree(create_all_slots (array))

