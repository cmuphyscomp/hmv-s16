# demo_plane_recorder.py - the plane data recording script in the ghpython object in MocapDemo.gh.
#
# inputs
#  input    - single Plane object
#  capture  - Boolean indicating the object should be added to the set
#  clear    - Boolean indicating the the data set should be erased

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

################################################################
class PlaneRecorder(object):
    def __init__(self):
        self.planes = []
        return

    def add_plane(self, plane):
        self.planes.append(plane)
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

if capture:
    recorder.add_plane(input)

planes = recorder.planes
print "Currently holding %d planes." % len(planes)
