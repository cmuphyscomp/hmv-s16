# MocapReceiver.py - the motion capture script in the ghpython object in MocapDemo.gh

# Demonstration of receiving and parsing an Optitrack motion capture real-time stream.
# This is normally polled from a timer.
#
# inputs
#   reset   - Boolean flag to reset the receiver system
#   version - string defining the protocol version number (e.g. "2900" for Motive 1.9)
#
# outputs
#   out      - debugging text stream
#   received - integer number of new frames received
#   planes   - list of Plane objects or None, one per rigid body stream

# use persistent state context
import scriptcontext

# import the Optitrack stream receiver
# reload(optirecv)
import optirecv

# If the user reset input is set, then clear any existing state and do nothing.
if reset:
    print "Resetting receiver state."
    scriptcontext.sticky['mocap_port'] = None
 
else:
    # fetch or create the persistent motion capture streaming receiver port
    port = scriptcontext.sticky.get('mocap_port')
    if port is None:
        port = optirecv.OptitrackReceiver(version)
        scriptcontext.sticky['mocap_port'] = port

    # Poll the port as long as data is available, accumulating all
    # frames.  It is unlikely that Grasshopper will keep up with the
    # 120 Hz mocap sampling rate, butit is important to have the
    # continuous trajectory available for analysis and recording.
    receiving = True
    frames = list()
    while receiving:
        receiving = port.poll()
        if receiving:
            frames.append(port.make_plane_list())

    # Convert the frame list into a data tree for output.  As accumulated, it is a Python list of lists:
    # [[body1_sample0, body2_sample0, body3_sample0, ...], [body1_sample1, body2_sample1, body3_sample1, ...], ...]
    planes = optirecv.frames_to_tree(frames)
    received = len(frames)
    
    # Emit the list of body names in the order corresponding to the
    # branches in the trajectory data tree.  The ordering is stable as
    # determined by the configuration in the Motive project.
    names  = port.bodynames

