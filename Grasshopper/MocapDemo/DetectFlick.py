# DetectFlick.py - contents of the ghpython object in MocapDemo.gh
#
# inputs
#   reset   - Boolean to deactivate and reset state
#   points  - list of Point3D objects representing the path of the tip of an indicating stick
#             Note: the 'points' input must be set to 'List Access'
# threshold - the acceleration value above which to output an event

# outputs
#   out      - debugging text stream
#   flick    - true if a flick event is detected
#   sample   - sample offset for the flick event; zero is 'now', negative values are relative to now.

# use persistent state context
import scriptcontext
sc_identifier = 'flick_detector'

# use point filter with acceleration estimator
# reload(pointfilter)
import pointfilter

# If the user reset input is set, then clear any existing state and do nothing.
if reset:
    print "Resetting receiver state."
    scriptcontext.sticky[sc_identifier] = None 

else:
    # fetch or create the persistent motion capture streaming receiver port
    filter = scriptcontext.sticky.get(sc_identifier)
    if filter is None:
        filter = pointfilter.Point3dFilter(20)
        scriptcontext.sticky[sc_identifier] = filter
        
    # add the new data
    filter.add_points(points)
    # print filter._position
    # print "Adding %d points to filter." % len(points)
    # offset, mag, acc, pos = filter.find_accel_peak()
    # print "Peak at %d of %f" % (offset, mag)
    
    flick, sample = filter.detect_acceleration_event( threshold )
    if flick:
        print "Acceleration peak observed at %d" % sample
    
    print "Filter has seen %d points, buffer starts at %d, blanking ends at %d." % (filter.samples, filter.samples - filter._buf_len, filter.last_event + filter.blanking)
 
    
