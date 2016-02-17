# pointfilter.py : filtering operations on Point3d trajectories

# Copyright (c) 2016, Garth Zeglin. All rights reserved. Licensed under the
# terms of the BSD 3-clause license.

# normal Python packages
import math

# use RhinoCommon API
import Rhino

# Define a Savitzky-Golay filter for estimating acceleration, assuming a 120Hz sampling rate.
# See generate_filter_coefficients.py for details.
accel_filter_coeff = [ 872.727273, 218.181818, -249.350649, -529.870130, -623.376623, -529.870130, -249.350649, 218.181818, 872.727273]

class Point3dFilter(object):
    def __init__(self, length):
        # length of the estimation filter
        self._filter_len = len(accel_filter_coeff)

        # length of the fixed-length history buffer
        self._buf_len = length


        # Keep track of the number of samples observed.
        # N.B. the most recent (last) point in the buffer has sample index = self.samples - 1
        #      the   oldest (first)   point in the buffer has sample index = self.samples - self._buf_len
        self.samples = 0  

        # number of samples to ignore after an event
        self.blanking = 60

        # sample number for the last 'event' observed
        self.last_event = -self.blanking
        
        # create fixed-length data buffers with zeros
        self.reset()

        return
    
    def reset(self):
        """Reset filter state."""
        self._position  = [Rhino.Geometry.Point3d(0,0,0) for i in range(self._buf_len)]
        self._accel = [Rhino.Geometry.Vector3d(0,0,0) for i in range(self._buf_len)]
        self._accel_mag = [0.0 for i in range(self._buf_len)]

        # reset the blanking interval to the filter length
        self.last_event = self.samples - self.blanking + self._filter_len
        
        return

    def add_points(self, point_list):
        """Given a list of objects which are either Point3d or None, append them to the
        fixed-length filter history buffer.  Null samples are converted to zero
        points but also suppress event results for an interval.
        """

        # Compute the pieces of the old and new buffers to concatenate,
        # considering the possibility there may be an excess of new data.
        num_new_samples = min(self._buf_len, len(point_list))
        first_source_sample = len(point_list) - num_new_samples
        first_new_dest_sample = self._buf_len - num_new_samples
        self.samples += len(point_list)

        # Check for null points; if found, convert them to zeros but start a blanking interval.
        if None in point_list:
            # find the position of the last null
            self._last_event = self.samples - point_list[::-1].index(None) - 1
            print "Found null in input, samples=%d, last_event=%d, pts=%s" % (self.samples, self._last_event, point_list)
            # convert nulls to zero points
            point_list = [pt if pt is not None else Rhino.Geometry.Point3d(0,0,0) for pt in point_list]
            
        # construct a new position buffer
        self._position = self._position[num_new_samples:] + point_list[first_source_sample:]
        
        # update the acceleration vector buffer for the new data
        new_accel = [self._estimate_acceleration(p) for p in range(first_new_dest_sample, self._buf_len)]
        self._accel = self._accel[num_new_samples:] + new_accel

        # update the acceleration magnitude buffer
        new_mag = [math.sqrt(a*a) for a in new_accel]
        self._accel_mag = self._accel_mag[num_new_samples:] + new_mag
        
        return

    def _estimate_acceleration(self, pos):
        """Estimate the acceleration vector for the given buffer position,
        where pos=self._buf_len-1 is the newest data point.  Return a
        zero vector for positions for which not enough samples are
        present for the filter length.

        :param pos:  buffer position for which to compute acceleration
        :return:     Rhino Vector3d object with acceleration.

        """

        # Compute the dot product of the filter coefficients and the point
        # history.
        accum = Rhino.Geometry.Point3d(0,0,0)
        first_datum = pos - self._filter_len
        if first_datum >= 0:
            for term,coeff in zip(self._position[first_datum:], accel_filter_coeff):
                accum += term * coeff

        # A Point multiplied by a scalar is a Point, but the output of the
        # filter should be interpreted as a Vector.
        return Rhino.Geometry.Vector3d(accum)
            
    def find_accel_peak(self):
        """Finds the peak acceleration within the current time history.  The
        offset is the negative time position in samples; 0 is the most
        current data, -1 one sample prior, etc.

        :return:   (offset, magnitude, acceleration, position) tuple
        """

        maximum = max(self._accel_mag)
        idx = self._accel_mag.index(maximum)
        offset = idx - self._buf_len + 1
        return offset, maximum, self._accel[idx], self._position[idx]
    
    def detect_acceleration_event(self, threshold):
        """Check the point trajectory buffer for a new event in which the acceleration
        magnitude is greater than a threshold.  A blanking interval is applied
        after each event to suppress multiple returns from spiky signals.  A
        sample offset of zero means the most recent point is the peak, other
        offsets are negative.

        :return: (event flag, None or the sample offset of the peak)

        """
        # check blanking interval to see which samples can be inspected
        first_buffer_sample = self.samples - self._buf_len
        after_blanking = self.last_event + self.blanking
        first_checked_sample = max(first_buffer_sample, after_blanking)
        first_valid_index = first_checked_sample - first_buffer_sample
        
        # if the next data to inspect is still in the future, return False
        if first_checked_sample >= self.samples:
            return False, None

        # find the maximum within the valid range
        maximum = max(self._accel_mag[first_valid_index:])
        if maximum > threshold:
            # compute the offset of the maximum
            idx = self._accel_mag[first_valid_index:].index(maximum)
            offset = first_valid_index + idx + 1 - self._buf_len

            # start the blanking interval
            self.last_event = self.samples - 1 + offset

            # and return a valid peak indication
            return True, offset
        
        else:
            return False, None            
    
    
