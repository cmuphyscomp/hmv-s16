from __future__ import print_function

import os, sys, socket, argparse, time

# Make sure that the Python libraries also contained within this course package
# are on the load path.  This adds the parent folder to the load path, assuming that this
# script is still located with the scripts/ subfolder of the Python library tree.

sys.path.insert(0, os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import optirx as rx

MULTICAST_ADDRESS =           "239.255.42.99"     # IANA, local network
PORT_DATA =                   1511                # Default multicast group

def gethostip():
    return socket.gethostbyname(socket.gethostname())

def make_data_sender_socket(ip_address=None):
    """Create a socket for sending multicast data."""
    ip_address = gethostip() if not ip_address else ip_address
    datasock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
    datasock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    datasock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    datasock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 20)
    
    # print("Binding source socket to %s" % ip_address)
    datasock.bind((ip_address, 0))
    return datasock

def send_optitrack_packet(datasock, data, multicast_address=MULTICAST_ADDRESS, port=PORT_DATA):
    datasock.sendto(data, (multicast_address, port))
    return

def main(paths):
    datasock = make_data_sender_socket()
    for path in paths:
        with open(path, "rb") as input:
            print("Sending %s" % path)
            data = input.read()
            send_optitrack_packet(datasock, data)
            time.sleep(0.1)
            
if __name__ == "__main__":
    parser = argparse.ArgumentParser( description = """Send Optitrack test data packets.""")
    parser.add_argument( '-v', '--verbose', action='store_true', help='Enable more detailed output.' )
    parser.add_argument( 'filename', nargs='+', help = 'Names of binary packet files to send.')
    args = parser.parse_args()
    main(args.filename)
