from __future__ import print_function

import os, sys, socket

# Make sure that the Python libraries also contained within this course package
# are on the load path.  This adds the parent folder to the load path, assuming that this
# script is still located with the scripts/ subfolder of the Python library tree.

sys.path.insert(0, os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import optirx as rx

from optitrack.geometry import quaternion_to_xaxis_yaxis

sdk_version = (2, 9, 0, 0)  # the latest SDK version

# Arbitrary UDP port number at which to receive data in Grasshopper.
RHINO_PORT=35443

def make_udp_sender(ip_address=None):
    """Create a normal UDP socket for sending unicast data to Rhino."""
    ip_address = rx.gethostip() if not ip_address else ip_address
    sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sender.bind((ip_address, 0))
    return sender

def body_record(body):
    """Create a one-line ASCII data record to transmit for each body."""
    position = "%f %f %f " % body.position
    xaxis, yaxis = quaternion_to_xaxis_yaxis(body.orientation)
    xvec = "%f %f %f " % tuple(xaxis)
    yvec = "%f %f %f\n" % tuple(yaxis)
    return position + xvec + yvec
    
def main():
    # create a multicast UDP receiver socket
    receiver = rx.mkdatasock()

    # create a unicast UDP sender socket
    sender = make_udp_sender()

    # the hostname running Grasshopper, assumed to be the same machine
    host = gethostip()
    
    while True:
        data = receiver.recv(rx.MAX_PACKETSIZE)
        packet = rx.unpack(data, version=sdk_version)
        if type(packet) is rx.SenderData:
            version = packet.natnet_version
            print("NatNet version received:", version)

        if type(packet)==rx.FrameOfData:
            print("Received frame data.")
            records = [body_record(body) for body in packet.rigid_bodies]
            msg = "".join(records)
            print("Sending", msg)
            sender.sendto( msg, (host, RHINO_PORT))

if __name__ == "__main__":
    main()
