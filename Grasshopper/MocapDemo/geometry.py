"""\
optitrack.geometry : plain-Python geometric utility functions.

This uses only Python modules common between CPython, IronPython, and
RhinoPython for compatibility with both Rhino and offline testing.

Copyright (c) 2016, Garth Zeglin. All rights reserved. Licensed under the
terms of the BSD 3-clause license as included in LICENSE.

"""

#================================================================
# The Optitrack quaternion format is a [x,y,z,w] list.

def quaternion_to_rotation_matrix(q):
    """Return a 3x3 rotation matrix representing the orientation specified by a quaternion in x,y,z,w format.
    The matrix is a Python list of lists.
    """

    x = q[0]
    y = q[1]
    z = q[2]
    w = q[3]
    
    return [[ w*w + x*x - y*y - z*z,       2*(x*y - w*z),               2*(x*z + w*y)         ],
            [ 2*(x*y + w*z),               w*w - x*x + y*y - z*z,       2*(y*z - w*x)         ],
            [ 2*(x*z - w*y),               2*(y*z + w*x),               w*w - x*x - y*y + z*z ]]

#================================================================
def quaternion_to_xaxis_yaxis(q):
    """Return the (xaxis, yaxis) unit vectors representing the orientation specified by a quaternion in x,y,z,w format."""

    x = q[0]
    y = q[1]
    z = q[2]
    w = q[3]

    xaxis = [ w*w + x*x - y*y - z*z,       2*(x*y + w*z),             2*(x*z - w*y) ]
    yaxis = [ 2*(x*y - w*z),               w*w - x*x + y*y - z*z,     2*(y*z + w*x) ]

    return xaxis, yaxis

#================================================================
