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
import Rhino

################################################################
class EditorLogic(object):
    """Utility class to manage the state of the interactive editor."""

    def __init__(self):
        self._last_setselect = False # debounce variable
        self.attached = False
        self.new_object_poses = list()
        self.new_object_names = list()
        self.selection = None
        self.docguids = None
        self.transform = None  # coordinate transformation for group edits
        self.motion    = None  # coordinate transformation for group edits
        self.log       = ["Editor initialized."]    # list of string in which to accumulate messages for output
        return

    def add_new_object_pose(self, plane):   
        if plane is not None:
            name = self.choose_new_name()
            if name is not None:
                self.new_object_poses.append(plane)
                self.new_object_names.append(name)
        return
        
    def clear_edits(self):
        """Reset all transient editor state, either at user request or after editing cycle is complete."""
        self.new_object_poses = list()
        self.new_object_names = list()
        self.attached = False
        self.selection = None
        self.docguids = None
        return

    def logprint(self, msg):
        self.log.append(msg)
        
    def clear_log(self):
        self.log = []
        
    def set_namesets(self, all_names, used_names):
        """Update the name manager given a list of all possible object names and the list of object names currently in use."""
        self.all_names = set(all_names)
        self.used_names = set()
        
        # check for duplicate names
        for used in used_names:
            if used in self.used_names:
                self.logprint("Warning: object name %s appears more than once." % used)
            else:
                self.used_names.add(used)
                
        # check for used names not listed in the all_names set
        invalid_names = self.used_names - self.all_names
        if invalid_names:
            self.logprint("Warning: invalid names in use: %s" % invalid_names)
            
        # compute the list of available names
        self.unused_names = self.all_names - self.used_names
        self.logprint("Found the following unused object names: %s" % self.unused_names)
        return

    def choose_new_name(self):
        """Pick an name arbitrarily from the set of unused names."""
        if len(self.unused_names) == 0:
            self.logprint("Warning: no more object names available.")
            return None
        new_name = [name for name in self.unused_names][0]
        self.unused_names.remove(new_name)
        return new_name
        
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
xform   = None

if reset:
    print "Interaction logic in reset state."
    status = "Reset"
    
else:
    # for all modes, record the set of selected objects when indicated
    if setselect != editor._last_setselect:
        # debounce input to just trigger once
        editor._last_setselect = setselect
        if setselect == True:
            editor.selection = selection
            editor.docguids = selguids
    
            # reset the pick and place state
            editor.attached = False
            editor.transform = None
            
            editor.logprint("Selection set with %d objects." % len(selection))
            editor.set_namesets(all_names, used_names)
        
    if mode == 1:
        # tap create mode: each gesture creates a new object
        if gesture is not None:
            editor.logprint("Gesture detected with sample offset %d." % gesture)
            # gesture is an integer sample where zero is the most recent pose;
            # index the current cursor poses from the end to select the correct
            # pose
            editor.add_new_object_pose(cursor[gesture-1])

        if clear == True:
            editor.logprint( "Abandoning editor changes (dropping new object poses).")
            editor.clear_edits()         

        # by default, always emit the new poses so they can be visualized
        newloc = editor.new_object_poses

        if update == True:
            editor.logprint("Writing new objects to RhinoDoc: %s" % editor.new_object_names)
            names = editor.new_object_names
            add = True
            editor.clear_edits() # note: the current list has already been emitted, this just resets the buffer

    elif mode == 3:
        # pick and move: each gesture toggles whether selected objects are attached to cursor or not
 
        objects = editor.selection
        guids = editor.docguids
        motion = Rhino.Geometry.Transform(1) # motion transform is identity value by default
        if clear == True:
            editor.logprint("Abandoning editor changes (clearing movement).")
            editor.transform = None
            
        # detect the singular gesture events (for now, a flick of the wand)
        if gesture is not None:
            # if we are ending a motion segment, save the most recent transformation as the new base transform
            if editor.attached:
                editor.transform = editor.transform * editor.motion
                editor.logprint("Motion ended, new transform saved.")
            else:
                editor.logprint("Motion beginning.")
                
            # toggle the 'attached' state
            editor.attached = not editor.attached
            
        if editor.attached:
            if len(poses) > 0 and len(cursor) > 0:
                # compute a tranform the from most recent saved pose to the newest cursor position
                motion = Rhino.Geometry.Transform.PlaneToPlane(poses[-1], cursor[-1])
        
        # compute an output transformation from the accumulated transform plus any transient movement
        if editor.transform is None:
            editor.transform = Rhino.Geometry.Transform(1) # identity
        xform = editor.transform * motion
        editor.motion = motion

        if update == True:
            editor.logprint("Updating RhinoDoc selection with new poses.")
            move = True
            editor.clear_edits()

    # emit terse status for remote panel
    status = "M:%s C:%d P:%d N:%d" % (editor.attached, len(cursor), len(poses), len(editor.new_object_poses))

    # re-emit the log output
    for str in editor.log: print str