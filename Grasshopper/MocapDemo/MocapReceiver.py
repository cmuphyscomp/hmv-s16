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
#   received - flag true if new data was received
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

    # Poll the port as long as data is available, throwing away any redundant
    # samples.  It is more important to keep up with real time, and at 120Hz, it
    # is unlikely that this will keep up.
    received = True
    while received:
        received = port.poll()
        
    # always set the output variables so the most recent values are available
    # position, orient, xaxis, yaxis = port.make_data_trees()
    planes = port.make_plane_list()
    names  = port.bodynames

