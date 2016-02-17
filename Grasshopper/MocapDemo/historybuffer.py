"""\
historybuffer.py : fixed-length buffer for a time-series of objects

Copyright (c) 2016, Garth Zeglin. All rights reserved. Licensed under the
terms of the BSD 3-clause license.
"""

class History(object):
    """Implement a fixed-length buffer for keeping the recent history of a
    time-series of objects.  This is optimized for the case of a relatively
    short buffer receiving blocks of elements at a time, possibly longer than
    the buffer.  It keeps track of the total number of objects appended whether
    or not they are stored.

    The [] (__getitem__) operator uses time-offset addressing: history[0] is the
    most recent element, history[-1] the one before that, etc.

    Attributes:

    samples - the total number of samples appended

    """

    def __init__(self, length):
        # length of the fixed-length history buffer
        self._buf_len = length

        # Keep track of the number of samples observed.
        # N.B. the most recent (last) point in the buffer has sample index = self.samples - 1
        #      the   oldest (first)   point in the buffer has sample index = self.samples - self._buf_len
        self.samples = 0  

        # create fixed-length data buffer filled with None
        self.reset()

        return
    
    def reset(self):
        """Reset buffer state."""
        self._buffer = [None for i in range(self._buf_len)]
        return

    def append(self, object_list):
        """Given a list of objects, append them to the fixed-length history buffer.
        """

        # Compute the pieces of the old and new buffers to concatenate,
        # considering the possibility there may be an excess of new data.
        num_new_samples = min(self._buf_len, len(object_list))
        first_source_sample = len(object_list) - num_new_samples
        first_new_dest_sample = self._buf_len - num_new_samples
        self.samples += len(object_list)

        # construct a new buffer array
        self._buffer = self._buffer[num_new_samples:] + object_list[first_source_sample:]
        return

    def __getitem__(self, index):
        """Look up an element using a time-offset based address.  An index of zero is
        the most recent sample and negative indices return values farther back
        in time. Positive indices are not available as they represent the
        future.
        """

        if index > 0:
            raise IndexError('History time offset must be non-positive', index)

        elif index < (1 - self._buf_len):
            raise IndexError('History time offset out of range', index)

        # use Python negative indexing relative to buffer end
        return self._buffer[index-1]
