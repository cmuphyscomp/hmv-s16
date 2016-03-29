# GestureLogic - state machine for interface logic

# FIXME: this is out of date
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

################################################################
class EditorLogic(object):
    """Utility class to manage the state of the interactive editor."""

    def __init__(self):
        self.attached = False
        self.new_object_poses = list()
        self.selection = None
        self.docguids = None
        return

    def add_new_object_pose(self, plane):
        if plane is not None:
            self.new_object_poses.append(plane)
        return
        
    def clear_edits(self):
        """Reset all transient editor state, either at user request or after editing cycle is complete."""
        self.new_object_poses = list()
        self.attached = False
        self.selection = None
        self.docguids = None
        return

################################################################
editor = sc.sticky.get(name)

if editor is None or reset:
    editor = EditorLogic()
    sc.sticky[name] = editor

# set default outputs
start  = None
end    = None
add    = False
move   = False
names  = None
newloc = None
objects = None
guids   = None

if reset:
    print "Interaction logic in reset state."
    status = "Reset"
    
else:
    # for all modes, record the set of selected objects when indicated
    if setselect == True:
        editor.selection = selection
        editor.docguids = selguids
    
    if mode == 1:
        # tap create mode: each gesture creates a new object
        if gesture is not None:
            print "Gesture detected."
            # gesture is an integer sample where zero is the most recent pose;
            # index the current cursor poses from the end to select the correct
            # pose
            editor.add_new_object_pose(cursor[gesture-1])

        if clear == True:
            print "Abandoning editor changes."
            editor.clear_edits()         

        # by default, always emit the new poses so they can be visualized
        newloc = editor.new_object_poses

        if update == True:
            print "Writing new cards."
            names = ["Card"] * len(editor.new_object_poses)             # FIXME
            add = True
            editor.clear_edits() # note: the current list has already been emitted, this just resets the buffer

    elif mode == 3:
        # pick and move: each gesture toggles whether selected objects are attached to cursor or not
 
        objects = editor.selection
        guids = editor.docguids
        
        if gesture is not None:
            editor.attached = not editor.attached
            
        if editor.attached:
            if len(poses) > 0 and len(cursor) > 0:
                start = poses[-1] # most recent saved pose
                end   = cursor[-1] # newest cursor position

        else:
            if len(poses) > 1:
                start = poses[-2] # use most recent saved poses to transform part
                end   = poses[-1]

        if update == True:
            print "Updating selection with new poses."
            move = True
            editor.clear_edits()

    # emit terse status for remote panel
    status = "M:%s C:%d P:%d N:%d" % (editor.attached, len(cursor), len(poses), len(editor.new_object_poses))
