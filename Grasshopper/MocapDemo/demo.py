# this is a copy of the receiver script in the ghpython object

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
#   position - data tree of position tuples
#   orient   - data tree of quaternion tuples, orientations are (x,y,z,w) quaternions
#   xaxis    - data tree of X axis unit vectors (computed from orientations)
#   yaxis    - data tree of Y axis unit vectors (computed from orientations)

# use persistent state context
import scriptcontext

# import the Optitrack stream receiver
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
    
    received = port.poll()
        
    # always set the output variables so the most recent values are available
    position, orient, xaxis, yaxis = port.make_data_trees()
