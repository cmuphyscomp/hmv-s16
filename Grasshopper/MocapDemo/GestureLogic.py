# GestureLogic - state machine for interface logic
# inputs
#  name   - name token string for sticky
#  reset  - bool to reset to lowest value
#  sample - None or relative sample index of detected gesture event
#  cursor - list of Planes with recent cursor object trajectory
#  poses  - list of Planes saved at gesture events
# Note: cursor and poses must have 'List Access' set
#
# outputs
#  moving - Boolean to indicate when selection is actively in motion
#  start  - None or Plane to indicate origin for transformation
#  end    - None or Plane to indicate target for transformation

import scriptcontext as sc

value = sc.sticky.get(name)

if value is None or reset:
    value = { "attached" : False }
    sc.sticky[name] = value


    
if reset:
    print "Interaction logic in reset state."
    moving = False
    start = None # could be world XY
    end = start # no coordinate offset
    
else:
    # on every flick, toggle whether objects are attached to cursor or not
    if sample is not None:
        value["attached"] = not value["attached"]
 
    moving = value["attached"]
    if moving:
        if len(poses) > 0 and len(cursor) > 0:
            start = poses[-1] # most recent saved pose
            end   = cursor[-1] # newest cursor position
        else:
            start = None
            end = None
    else:
        if len(poses) > 1:
            start = poses[-2] # use most recent saved poses to transform part
            end   = poses[-1]
        else:
            start = None
            end = None
            
# emit terse status for remote panel
print "M:%s C:%d P:%d" % (moving, len(cursor), len(poses))