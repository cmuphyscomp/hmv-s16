#!/usr/bin/env python
"""\
generate_filter_coefficients.py : use scipy to generate coefficients for an estimation filter

This script generates an FIR filter for estimating acceleration from a uniformly sampled signal.

It uses the scipy libraries, so it doesn't work within Rhino Python; this must
be run using a CPython installation which has scipy installed.

References:

  https://en.wikipedia.org/wiki/Savitzky%E2%80%93Golay_filter
  http://docs.scipy.org/doc/scipy-0.16.1/reference/generated/scipy.signal.savgol_coeffs.html

"""

import numpy as np
import scipy.signal

window_length = 9       # filter length (number of samples required, must be an odd number)
polyorder     = 2       # fit a quadratic curve
sampling_rate = 120     # Hz

if __name__=="__main__":

    coeff = scipy.signal.savgol_coeffs( window_length = window_length, \
                                     polyorder = polyorder, \
                                     deriv = 2, \
                                     delta = (1.0/sampling_rate), \
                                     pos = window_length-1,
                                     use = 'dot')

    # emit a single line of Python to insert in the code
    print "accel_filter_coeff = [",
    for c in coeff[:-1]:
        print ("%f," % c),
    print "%f]" % coeff[-1]
    
# accel_filter_coeff = [ 872.727273, 218.181818, -249.350649, -529.870130, -623.376623, -529.870130, -249.350649, 218.181818, 872.727273]    
    
