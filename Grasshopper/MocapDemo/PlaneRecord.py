# PlaneRecord.py - the plane data recording script in the ghpython object in MocapDemo.gh.
#
# inputs
#  inputs   - list of Plane objects
#  capture  - None or integer sample time offset indicating which recent object should be added to the set
#  clear    - Boolean indicating the the data set should be erased
#  N.B. the 'inputs' input must be set to 'List Access'
#  N.B. the 'capture' input should have a type hint of Int

# other ideas:
#   path       - string with the full path to the CSV file
#   selection  - currently selected set

# outputs
#   out      - debugging text stream
#   planes   - list of Plane objects

# use RhinoCommon API
import Rhino

# use persistent state context
import scriptcontext

# use the history utility class
import historybuffer

################################################################
class PlaneRecorder(object):
    def __init__(self):
        # list of selected objects
        self.planes = []
 
        # keep track of about a quarter-second of mocap data
        self.buffer = historybuffer.History(30)
        return

    def add_planes(self, planes):
        if planes is not None:
            self.buffer.append(planes)
        return
    
    def capture_plane(self, offset):
        self.planes.append(self.buffer[offset])
        return

################################################################
if clear:
    # create an empty data recorder
    recorder = PlaneRecorder()
    scriptcontext.sticky['plane_recorder'] = recorder

else:
    # fetch or create a persistent data recorder
    recorder = scriptcontext.sticky.get('plane_recorder')
    if recorder is None:
        recorder = PlaneRecorder()
        scriptcontext.sticky['plane_recorder'] = recorder
    recorder.add_planes(inputs)

if capture is not None:
    # The capture index is non-positive: zero means 'now', negative means a recent sample.  So the value is
    # biased by -1 to be an index relative to the end of the recorded poses.
    recorder.capture_plane(capture-1)
 
planes = recorder.planes
print "Buffer has seen %d planes, currently holding %d selected planes." % (recorder.buffer.samples, len(planes))
