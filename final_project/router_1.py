"""Router implementation using UDP sockets"""
#!/usr/bin/env python3
# encoding: UTF-8


import os
import random
import select
import socket
import struct
import sys
import time

HOST_ID = os.path.splitext(__file__)[0].split("_")[-1]
THIS_NODE = f"127.0.0.{HOST_ID}"
PORT = int("4300" + HOST_ID)
MINE = {}
NEIGHBORS = set()
NEIGHBORS_EXTENDED = {}
ROUTING_TABLE = {}
TIMEOUT = 5
MESSAGES = [
    "Cosmic Cuttlefish",
    "Bionic Beaver",
    "Xenial Xerus",
    "Trusty Tahr",
    "Precise Pangolin"
]


def read_file(filename: str) -> None:
    """
        Read config file.

        We start with a simple application that reads a router's configuration from a text file, displays its status (neighbors and cost of getting to them), and starts listening for incoming UDP connections on port 4300. The configuration contains names of your directly connected neighbors and the cost to reach those neighbors.

        You should write 4 identical files, each one for a different address (127.0.0.x) and port (4300x). By the end of the project you should be able to test your routers locally, at the very least.

        Configuration file format
            Router_1_IP_address
            Neighbor_1_IP_addres Cost_of_getting_to_neighbor_1
            Neighbor_2_IP_addres Cost_of_getting_to_neighbor_2

            Router_2_IP_address
            Neighbor_1_IP_addres Cost_of_getting_to_neighbor_1
            Neighbor_2_IP_addres Cost_of_getting_to_neighbor_2
            Neighbor_3_IP_addres Cost_of_getting_to_neighbor_3

        Read a configuration file for your specific router and add each neighbor to a set of neighbors.
        Build an initial routing table as a dictionary with nodes as keys.
        Dictionary values should be a distance to the node and the next hop address (ie. {'destination':[cost, 'next_hop']}).
        Initially, the dictionary must contain your neighbors only.
    """

    skip = False
    current_neighbor = ""
    with open(filename, "r") as f:
        for line in f:
            line = line.split()

            if len(line) == 0:
                skip = False
                continue
            elif len(line) == 1:
                if line[0] == THIS_NODE:
                    skip = True
                    continue
                current_neighbor = line[0]
            elif len(line) == 2:
                if skip:
                    NEIGHBORS.add(line[0])
                    MINE[line[0]] = line[1]
                    ROUTING_TABLE[line[0]] = [line[1], None]
                    continue
                if not current_neighbor in NEIGHBORS_EXTENDED:
                    NEIGHBORS_EXTENDED[current_neighbor] = []
                NEIGHBORS_EXTENDED[current_neighbor].append(
                    [line[0], line[1]])

        # print(MINE)
        # print(NEIGHBORS)
        # print(NEIGHBORS_EXTENDED)

    print(THIS_NODE)

    print(ROUTING_TABLE)

    # Distance Vector Algorithm
    for neighbor in NEIGHBORS:
        neighbor_cost = int(MINE[neighbor])
        # print("\t Neighbor:", neighbor, "cost:", neighbor_cost)
        for node in NEIGHBORS_EXTENDED[neighbor]:
            if THIS_NODE == node[0]:
                continue

            hop_cost = int(node[1]) + neighbor_cost

            if (not node[0] in ROUTING_TABLE) or (int(ROUTING_TABLE[node[0]][0]) > hop_cost):
                ROUTING_TABLE[node[0]] = [hop_cost, neighbor]

            # print("\t\t   ", node[0], "cost", hop_cost)

        # break
    # print(NEIGHBORS_EXTENDED[neighbor])

    print(ROUTING_TABLE)


def format_update():
    """Format update message"""
    raise NotImplementedError


def parse_update(msg, neigh_addr):
    """Update routing table"""
    raise NotImplementedError


def send_update(node):
    """Send update"""
    raise NotImplementedError


def format_hello(msg_txt, src_node, dst_node):
    """Format hello message"""
    raise NotImplementedError


def parse_hello(msg):
    """Send the message to an appropriate next hop"""
    raise NotImplementedError


def send_hello(msg_txt, src_node, dst_node):
    """Send a message"""
    raise NotImplementedError


def print_status():
    """Print status"""
    raise NotImplementedError


def main(args: list):
    """Router main loop"""
    read_file(args[1])


if __name__ == "__main__":
    main(sys.argv)
