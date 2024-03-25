#!/opt/anaconda3/bin/python3

import socket
import struct
import os
import logging

# Configure logging
logging.basicConfig(filename='firewall_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

def packet_callback(packet):
    # Parse Ethernet header
    eth_header = struct.unpack("!6s6sH", packet[:14])

    # Check if the packet is an IPv4 packet (Ethernet type 0x0800)
    if eth_header[2] == 0x0800:
        # Extract IP header (20 bytes for IPv4)
        ip_header = struct.unpack("!BBHHHBBH4s4s", packet[14:34])

        # Extract source and destination IP addresses
        src_ip = socket.inet_ntoa(ip_header[8])
        dst_ip = socket.inet_ntoa(ip_header[9])

        # Extract protocol information
        protocol = ip_header[6]

        # Check if the packet is a TCP packet
        if protocol == socket.IPPROTO_TCP:
            # Extract TCP header (20 bytes for TCP)
            tcp_header = struct.unpack("!HHLLBBHHH", packet[34:54])

            # Extract source and destination ports
            src_port = tcp_header[0]
            dst_port = tcp_header[1]

            # Check if the packet matches the rule (e.g., allow only TCP packets to port 80)
            if (
                src_ip == "10.23.7.37"
                and dst_ip == "10.23.7.36"
                and dst_port == 80
            ):
                logging.info(f"Allowed TCP packet from {src_ip}:{src_port} to {dst_ip}:{dst_port}")
                print(f"Allowed TCP packet from {src_ip}:{src_port} to {dst_ip}:{dst_port}")
            else:
                logging.info(f"Blocked TCP packet from {src_ip}:{src_port} to {dst_ip}:{dst_port}")
                print(f"Blocked TCP packet from {src_ip}:{src_port} to {dst_ip}:{dst_port}")

def main():
    # Check if running with sudo
    if os.geteuid() != 0:
        print("[ERROR1] Please run this script with sudo.")
        return

    # Create a raw socket to capture network packets
    raw_socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))

    while True:
        # Receive a packet
        packet, _ = raw_socket.recvfrom(65536)

        # Process the packet
        packet_callback(packet)

if __name__ == "__main__":
    main()
