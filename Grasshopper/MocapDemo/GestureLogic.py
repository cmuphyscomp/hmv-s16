# GestureLogic - state machine for interface logic for the gesture-based editing.
#
# This encompasses all the logic for the editor which is easier to write in
# Python than Grasshopper objects.  Only one EditorLogic instance is expected to
# exist since it holds and tracks user inputs.
#
# Objectives for this block:
#
# 1. Only hold transient user state.  All persistent data is read from the
#    RhinoDoc, manipulated in a transient way, and then written back to the
#    RhinoDoc or discarded.
#
# 2. Emit signals to read and write the model rather than directly manipulate
#    the RhinoDoc.  This does increase the number of I/O variables, but
#    is intended to make the operation easier to observe, debug, and extend.
# 
# inputs:
#  name    - name token string for sticky
#  reset   - bool to reset to lowest value
#  gesture - None or relative sample index (integer) of detected gesture event
#  cursor  - list of Planes with recent cursor object trajectory
#  poses   - list of Planes saved at gesture events
#  mode
#  update
#  selection
#  selguids
#  setselect
#  clear
#  used_names
#  all_names

# Note: the following must have 'List Access' set: cursor, poses, selection, selguids, used_names, all_names
#
# outputs:
#  out    - log string output for display; the log is persistent to reduce the amount of flickering
#  add
#  move
#  names
#  newloc
#  status
#  objects
#  guids
#  xform

################################################################
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
        self.log       = ["Editor initialized."]    # list of strings in which to accumulate messages for output
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

    def manage_user_selection(self, setselect, selection, selguids, all_names, used_names):
        """Process the user 'Set Selection' input, updating the editor state for any new
        objects and names as needed."""
        
        if setselect != self._last_setselect:
            # debounce input to just trigger once
            self._last_setselect = setselect
            if setselect == True:
                self.selection = selection
                self.docguids = selguids

                # reset the pick and place state
                self.attached = False
                self.transform = None

                self.logprint("Selection set with %d objects." % len(selection))
                self.set_namesets(all_names, used_names)

    #================================================================
    def update_tap_create_mode(self, gesture, cursor):
        """Update state for the 'tap create' mode in which gestures create individual cards.
        gesture - the integer gesture sample index or None
        cursor  - the list of recent cursor poses

        returns newlog, names, add
        """

        # default outputs
        names, add = None, None
        
        # tap create mode: each gesture creates a new object
        if gesture is not None:
            self.logprint("Gesture detected with sample offset %d." % gesture)
            # gesture is an integer sample where zero is the most recent pose;
            # index the current cursor poses from the end to select the correct
            # pose
            self.add_new_object_pose(cursor[gesture-1])

        if clear == True:
            self.logprint( "Abandoning editor changes (dropping new object poses).")
            self.clear_edits()         

        # by default, always emit the new poses so they can be visualized
        newloc = self.new_object_poses

        if update == True:
            self.logprint("Writing new objects to RhinoDoc: %s" % self.new_object_names)
            names = self.new_object_names
            add = True
            self.clear_edits() # note: the current list has already been emitted, this just resets the buffer

        return newloc, names, add

    #================================================================
    def update_block_move_mode(self, gesture, cursor, poses, update, clear):
        """Update state for the 'block move' mode in which each gesture alternately
        attaches or detaches the selection from the cursor.

        returns objects, guids, xform, move
        """

        # set default outputs
        objects = self.selection
        guids = self.docguids
        move = False
        
        motion = Rhino.Geometry.Transform(1) # motion transform is identity value by default

        if clear == True:
            self.logprint("Abandoning editor changes (clearing movement).")
            self.transform = None
            
        # detect the singular gesture events (for now, a flick of the wand)
        if gesture is not None:
            # if we are ending a motion segment, save the most recent transformation as the new base transform
            if self.attached:
                self.transform = self.transform * self.motion
                self.logprint("Motion ended, new transform saved.")
            else:
                self.logprint("Motion beginning.")
                
            # toggle the 'attached' state
            self.attached = not self.attached
            
        if self.attached:
            if len(poses) > 0 and len(cursor) > 0:
                # compute a tranform the from most recent saved pose to the newest cursor position
                motion = Rhino.Geometry.Transform.PlaneToPlane(poses[-1], cursor[-1])
        
        # compute an output transformation from the accumulated transform plus any transient movement
        if self.transform is None:
            self.transform = Rhino.Geometry.Transform(1) # identity
        xform = self.transform * motion
        self.motion = motion

        if update == True:
            self.logprint("Updating RhinoDoc selection with new poses.")
            move = True
            self.clear_edits()

        return objects, guids, xform, move


################################################################
# create or re-create the editor state as needed
editor = sc.sticky.get(name)
if editor is None or reset:
    editor = EditorLogic()
    sc.sticky[name] = editor

# set default output values
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
    editor.manage_user_selection(setselect, selection, selguids, all_names, used_names)

    # handle the state update for each individual mode
    if mode == 1:
        newloc, names, add = editor.update_tap_create_mode(gesture, cursor)
        
    elif mode == 3:
        objects, guids, xform, move = editor.update_block_move_mode(gesture, cursor, poses, update, clear)
        
    # emit terse status for remote panel
    status = "M:%s C:%d P:%d N:%d" % (editor.attached, len(cursor), len(poses), len(editor.new_object_poses))

    # re-emit the log output
    for str in editor.log: print str
