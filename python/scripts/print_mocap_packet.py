from __future__ import print_function

import os, sys, socket, argparse

# Make sure that the Python libraries also contained within this course package
# are on the load path.  This adds the parent folder to the load path, assuming that this
# script is still located with the scripts/ subfolder of the Python library tree.

sys.path.insert(0, os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import optirx as rx

def main(paths):
    for path in paths:
        with open(path, "rb") as input:
            print("Reading %s" % path)
            data = input.read()
            packet = rx.unpack(data, version=(2,9,0,0))
            print(packet)
            
if __name__ == "__main__":
    parser = argparse.ArgumentParser( description = """Print Optitrack test data packets.""")
    parser.add_argument( '-v', '--verbose', action='store_true', help='Enable more detailed output.' )
    parser.add_argument( 'filename', nargs='+', help = 'Names of binary packet files to read.')
    args = parser.parse_args()
    main(args.filename)
