#!/usr/bin/env python
"""\
test_optitrack_csv_reader.py : offline test for thee Optitrack CSV file parser.

Copyright (c) 2016, Garth Zeglin. All rights reserved. Licensed under the
terms of the BSD 3-clause license as included in LICENSE.
"""

import sys, os, argparse

# Make sure that the Python libraries also contained within this course package
# are on the load path.  This adds the parent folder to the load path, assuming that this
# script is still located with the scripts/ subfolder of the Python library tree.
sys.path.insert(0, os.path.abspath(".."))

import optitrack.csv_reader as csv

################################################################
# begin the script

if __name__=="__main__":

    # process command line arguments

    parser = argparse.ArgumentParser( description = """Parse an Optitrack v1.2 or v1.21 CSV file and report summary information.""")
    parser.add_argument( '-v', '--verbose', action='store_true', help='Enable more detailed output.' )
    parser.add_argument( 'csv', help = 'Filename of Optitrack CSV motion capture data to process.' )

    args = parser.parse_args()

    take = csv.Take().readCSV(args.csv, args.verbose)

    print "Found rigid bodies:", take.rigid_bodies.keys()

    for body in take.rigid_bodies.values():
        print "Body %s: %d valid frames out of %d." % (body.label, body.num_valid_frames(), body.num_total_frames())
        
        if args.verbose:
            print "Position track:"
            for point in body.positions: print point
