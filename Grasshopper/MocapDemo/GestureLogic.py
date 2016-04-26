# GestureLogic - state machine for interface logic for the gesture-based editing.
#
# This encompasses all the logic for the editor which is easier to write in
# Python than Grasshopper objects.  Only one GestureLogic instance is expected to
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
#  all_names
#  layer_name  - name of the editable layer in the RhinoDoc
#  create_interval - integer number of cycles between creating new objects

# Note: the following must have 'List Access' set: cursor, poses, selection, selguids, all_names
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
import clr
import System.Guid
import math

import Rhino
import pythonlibpath; pythonlibpath.add_library_path()
import ghutil.ghrhinodoc as ghrhinodoc

################################################################
class EditorLogic(object):
    """Utility class to manage the state of the interactive editor."""

    def __init__(self, _layer_name = 'Cards', _all_names = []):
        self.layer_name = _layer_name
        self._last_setselect = False # debounce variable
        self.attached = False
        self.interval_counter = 0
        self.mocap_dt = 1.0 / 120 # sampling rate of the motion capture stream

        # list of strings in which to accumulate messages for output
        self.log       = ["Editor initialized for layer %s." % self.layer_name]    
         
        # initialize the default sets of object names based on those found on the RhinoDoc layer
        self._update_namesets(_all_names)
        
        # freshly created objects: poses and names
        self.new_object_poses = list()
        self.new_object_names = list()

        # the current selection
        self.selection = None
        self.docguids = None
        self.selection_bb = None
        self.selection_bb_size = None
        
        # coordinate transformation for group edits
        self.transform = None  
        self.motion    = None
        self.xforms    = []    # list of transforms, one per selected object
        
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
        # return new names in numerical order for clarity
        new_name = sorted(self.unused_names)[0]
        self.unused_names.remove(new_name)
        return new_name

    def _update_namesets(self, all_names):
        all_objects = ghrhinodoc.all_doc_objects(layer_name)        
        names = [obj.Attributes.Name for obj in all_objects]
        self.set_namesets(all_names, names)
        return
  
    def _compute_set_bounding_box(self, selection):
        if selection is None or len(selection) == 0:
            return None
            
        # compute bounding box for all objects in a set
        boxes = [obj.GetBoundingBox(True) for obj in selection]

        # compute union of all boxes
        union = boxes[0]
        # destructively merge this with the other boxes
        for b in boxes[1:]:
            union.Union(b)
        return union, union.Diagonal.Length


    def manage_user_selection(self, setselect, selection, selguids, all_names):
        """Process the user 'Set Selection' input, updating the editor state for any new
        objects and names as needed."""
        
        if setselect != self._last_setselect:
            # debounce input to just trigger once
            self._last_setselect = setselect
            if setselect == True:
                self.selection = selection
                self.docguids = selguids
                
                self.selection_bb, self.selection_bb_size = self._compute_set_bounding_box(selection)
                self.logprint("Updated selection bounding box to %s, diagonal size %f" % (self.selection_bb, self.selection_bb_size))

                # reset the pick and place state
                self.attached  = False
                self.transform = None
                self.xforms    = []

                self.logprint("Selection set with %d objects." % len(selection))
                self._update_namesets(all_names)
                
    #================================================================
    def read_objects_from_layer(self, layer_name):
        """Read the user-visible names of all objects on a specific RhinoDoc layer.
        Returns a tuple (geoms, guids, names) with lists of all geometry
        objects, RhinoDoc GUID strings, and name attributes.
        """
        layer_index = ghrhinodoc.fetch_or_create_layer_index(layer_name)

        # Fetch all objects on the layer and report out individual properties.
        all_objects = ghrhinodoc.all_doc_objects(layer_name)

        geoms = [obj.Geometry for obj in all_objects]
        guids = [str(obj.Id) for obj in all_objects]
        names = [obj.Attributes.Name for obj in all_objects]
        return geoms, guids, names

    #================================================================
    def update_tap_create_mode(self, gesture, cursor, update, clear):
        """Update state for the 'tap create' mode in which gestures create individual cards.
        gesture - the integer gesture sample index or None
        cursor  - the list of recent cursor poses

        returns newloc, names, add
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
    def update_path_create_mode(self, _gesture, _cursor, _update, _clear, _all_names, _create_rate):

        """Update state for the 'symbol sprayer' mode which places new objects along a
        cursor path.  Each gesture event toggles the creation events on or off.

        returns newloc, names, add
        """

        # default outputs
        names, add = None, False
        
        # detect the singular gesture events (for now, a flick of the wand)
        if _gesture is not None:
            if self.attached:
                self.logprint("Creation path ended.")
            else:
                self.logprint("Creation path beginning.")
                self.interval_counter = 0
                self._update_namesets(_all_names)
                
            # toggle the 'attached' state
            self.attached = not self.attached

        # while 'attached' to the sprayer, create new objects at regular intervals
        if self.attached:
            self.interval_counter += 1
            
            if self.interval_counter > _create_rate:
               self.interval_counter = 0
               self.add_new_object_pose(_cursor[-1])

        if _clear == True:
            self.logprint( "Abandoning editor changes (dropping new object poses).")
            self.clear_edits()         

        # by default, always emit the new poses so they can be visualized
        newloc = self.new_object_poses

        if _update == True:
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

    #================================================================
    def update_path_move_mode(self, gesture, cursor, poses, update, clear):
        """Update state for the 'path move' mode in which each gesture toggles the
        enable, and the cursor velocity affects object positions within a 'brush'
        radius.

        returns objects, guids, xform, move
        """

        # set default outputs
        objects = self.selection
        guids = self.docguids
        move = False
        
        delta = Rhino.Geometry.Transform(1) # motion transform is identity value by default

        # FIXME: this is probably moot
        if self.transform is None:
            self.transform = Rhino.Geometry.Transform(1) # identity

        if self.selection is not None and (self.xforms is None or len(self.xforms) != len(self.selection)):
            self.xforms = [Rhino.Geometry.Transform(1) for x in self.selection]
            
        if clear == True:
            self.logprint("Abandoning editor changes (clearing movement).")
            self.transform = Rhino.Geometry.Transform(1)
            
        # detect the singular gesture events (for now, a flick of the wand)
        if gesture is not None:
            # if we are ending a motion segment
            if self.attached:
                self.logprint("Motion deactivated.")
            else:
                self.logprint("Motion activated.")
                
            # toggle the 'attached' state
            self.attached = not self.attached
            
        if self.attached:
            if len(cursor) > 1 and cursor[-1] is not None and cursor[-2] is not None:
                # Compute separate translation and rotation thresholds to
                # determine whether the velocity is high enough to be a gesture.

                # Find the rotation and translation between the last pair of samples:
                rot = Rhino.Geometry.Quaternion.Rotation(cursor[-2], cursor[-1])
                delta = cursor[-1].Origin - cursor[-2].Origin
                displacement = delta.Length

                # Convert the rotation to axis-angle form to find the magnitude.  The function uses C# call by reference to return
                # the parameters as 'out' values:
                angle = clr.Reference[float]()
                axis  = clr.Reference[Rhino.Geometry.Vector3d]()
                rot.GetRotation(angle, axis)
                angle = angle.Value # get rid of the StrongBox around the number
                axis  = axis.Value  # get rid of the StrongBox around the vector

                # The angle is returned on (0,2*pi); manage the wraparound
                if angle > math.pi:
                    angle -= 2*math.pi
                    
                # normalize to a velocity measure: m/sec, radians/sec
                speed = displacement / self.mocap_dt
                omega = angle / self.mocap_dt
                
                # compute object to cursor distances
                boxes = [obj.GetBoundingBox(False) for obj in self.selection]
                center = cursor[-1].Origin 
                distances = [box.Center.DistanceTo(center) for box in boxes]
                
                # Apply thresholds to determine whether the gesture represents intentional motion:
                if speed > 1.0 and True:
                    self.transform = self.transform * Rhino.Geometry.Transform.Translation(delta)
                    
                if abs(omega) > 2.0 and True:
                    # self.logprint("detected motion on speed %f and angular rate %f" % (speed, omega))
                    # apply the movement to the output tranform
                    # FIXME: transform should be a list, one per object, selective via a spherical cursor                                       
                    # choose a specific method from the set of overloaded signatures
                    Rotation_Factory = Rhino.Geometry.Transform.Rotation.Overloads[float, Rhino.Geometry.Vector3d, Rhino.Geometry.Point3d]
                    rot_xform = Rotation_Factory(angle, axis, center)
                    self.transform = self.transform * rot_xform
                    
                    # Apply a weighted displacement to each object transform.  The scaling matches the rolloff of the 
                    # effect to be proportional to the size of the bounding box of the moving objects.
                    scale = 0.1 * self.selection_bb_size * self.selection_bb_size
                    weights = [min(1.0, scale/(dist*dist)) if dist > 0.0 else 1.0 for dist in distances]
                    # self.logprint("Weights: %s" % (weights,))
                    rotations = [Rotation_Factory(angle*weight, axis, center) for weight in weights]
                    self.xforms = [xform*rot for xform,rot in zip(self.xforms, rotations)]

        if update == True:
            self.logprint("Updating RhinoDoc selection with new poses.")
            move = True
            self.clear_edits()

        return objects, guids, self.xforms, move


################################################################
# create or re-create the editor state as needed
editor = sc.sticky.get(name)
if editor is None or reset:
    editor = EditorLogic('Cards', all_names)
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
    editor.manage_user_selection(setselect, selection, selguids, all_names)

    # handle the state update for each individual mode
    if mode == 1:
        newloc, names, add = editor.update_tap_create_mode(gesture, cursor, update, clear)

    elif mode == 2:
        newloc, names, add = editor.update_path_create_mode(gesture, cursor, update, clear, all_names, create_interval)
        
    elif mode == 3:
        objects, guids, xform, move = editor.update_block_move_mode(gesture, cursor, poses, update, clear)

    elif mode == 4:
        objects, guids, xform, move = editor.update_path_move_mode(gesture, cursor, poses, update, clear)
        
    # emit terse status for remote panel
    status = "M:%s C:%d P:%d N:%d" % (editor.attached, len(cursor), len(poses), len(editor.new_object_poses))

    # re-emit the log output
    for str in editor.log: print str
