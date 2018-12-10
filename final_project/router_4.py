"""Router implementation using UDP sockets"""
#!/usr/bin/env python3
# encoding: UTF-8


import os
import random
import select
from socket import socket, AF_INET, SOCK_DGRAM
import struct
import sys
import time

HOST_ID = os.path.splitext(__file__)[0].split("_")[-1]
THIS_NODE = f"127.0.0.{HOST_ID}"
PORT = 4300
NEIGHBORS = set()
ROUTING_TABLE = {}
TIMEOUT = 5
MESSAGES = [
    "Cosmic Cuttlefish",
    "Bionic Beaver",
    "Xenial Xerus",
    "Trusty Tahr",
    "Precise Pangolin"
]

# MINE = {}  # TODO
# NEIGHBORS_EXTENDED = {}  # TODO

INPUTS = []


def read_file(filename: str) -> None:
    """Read config file"""

    # Can be as simple as
    with open(filename, "r") as f:
        lines = f.readlines()
        found = False
        for line in lines:
            line = line.split()
            if len(line) == 1:
                if line[0] == THIS_NODE:
                    found = True
                elif found == True:
                    found = False
            elif len(line) == 2 and found:
                if found:
                    ROUTING_TABLE.update({line[0]: [int(line[1]), line[0]]})
                    NEIGHBORS.add(line[0])

    # This is way more complicated - meant for Dijkstra's comparison with Distance Vector
    """ skip = False
    current_neighbor = ""

    # This is more complicated than it should be - but I was debugging and some of the stuff here is used later for doulbe checking results with Dijkstras
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
                    ROUTING_TABLE[line[0]] = [line[1], line[0]]
                    continue
                if not current_neighbor in NEIGHBORS_EXTENDED:
                    NEIGHBORS_EXTENDED[current_neighbor] = []
                NEIGHBORS_EXTENDED[current_neighbor].append(
                    [line[0], line[1]])

        # print(MINE)
        # print(NEIGHBORS)
        # print(NEIGHBORS_EXTENDED)

    # print(THIS_NODE)

    # print(ROUTING_TABLE)

    # Simulating Distance Vector Algorithm with Dijkstras Algorithm

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

    # print(ROUTING_TABLE) """


def format_update():
    """Format update message"""

    msg = bytearray()
    msg_type = 0
    msg.extend(msg_type.to_bytes(1, byteorder='big'))

    for dest, cost in ROUTING_TABLE.items():
        a, b, c, d = tuple(map(lambda x: int(x), dest.split(".")))
        cost = int(cost[0])
        msg_bytes = struct.pack("bbbbb", a, b, c, d, cost)
        msg.extend(msg_bytes)

    return msg


def parse_update(msg, neigh_addr):
    """Update routing table"""

    msg = msg[1:]
    update = False

    for val in range(0, len(msg), 5):
        if len(msg) < 5:
            break
        temp = msg[val:val+5]

        values = struct.unpack('BBBBB', temp)
        values = list(map(lambda x: str(x), values))
        ip = ".".join(values[:4])
        cost = int(values[4])

        if ip in ROUTING_TABLE:
            if ROUTING_TABLE[ip][0] > int(cost + ROUTING_TABLE[neigh_addr][0]):
                ROUTING_TABLE[ip] = [
                    (cost + int(ROUTING_TABLE[neigh_addr][0])), ROUTING_TABLE[neigh_addr][1]]
                update = True
        elif ip == THIS_NODE:
            continue
        else:
            ROUTING_TABLE[ip] = [
                (cost + int(ROUTING_TABLE[neigh_addr][0])), neigh_addr]
            update = True

    return update


def send_update(node):
    """Send update"""
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind((THIS_NODE, PORT))
    msg = format_update()

    port_id = node.split(".")[-1]
    table = format_update()

    sock.sendto(msg, (node, PORT+int(port_id)))
    sock.close()


def format_hello(msg_txt, src_node, dst_node):
    """Format hello message"""
    msg_type = 1

    a, b, c, d = tuple(map(lambda x: int(x), src_node.split(".")))
    e, f, g, h = tuple(map(lambda x: int(x), dst_node.split(".")))

    rest = bytes(msg_txt, "utf-8")
    msg = struct.pack("bbbbbbbbb{}s".format(
        len(rest)), msg_type, a, b, c, d, e, f, g, h, rest)

    return msg


def parse_hello(msg):
    """Send the message to an appropriate next hop"""
    msg_type, a, b, c, d, e, f, g, h, msg_txt = struct.unpack(
        'bbbbbbbbb{}s'.format(len(msg[9:])), msg)

    ip = list(map(lambda x: str(x), [a, b, c, d]))
    src_addr = ".".join(ip)

    ip = list(map(lambda x: str(x), [e, f, g, h]))
    dst_addr = ".".join(ip)

    if dst_addr == THIS_NODE:
        print(time.strftime('%H:%M:%S'),
              f'| Received {msg_txt.decode()} from {src_addr}')
    else:
        print(time.strftime('%H:%M:%S'),
              f'| Forwarding message from {src_addr} to {dst_addr}')
        send_hello(msg_txt.decode(), src_addr, dst_addr)


def send_hello(msg_txt, src_node, dst_node):
    """Send a message"""
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind((THIS_NODE, PORT))

    msg = format_hello(msg_txt, src_node, dst_node)

    port_id = ROUTING_TABLE[dst_node][1].split(".")[-1]

    sock.sendto(msg, (ROUTING_TABLE[dst_node][1], PORT+int(port_id)))
    sock.close()


def print_status():
    """Print status"""

    print('{:^20}{:^10}{:^20}'.format('Host', "Cost", "Via"))
    for node in ROUTING_TABLE:
        print('{:^20}{:^10}{:^20}'.format(
            node, ROUTING_TABLE[node][0], ROUTING_TABLE[node][1]))


def main(args: list):
    """Router main loop"""

    print(time.strftime("%H:%M:%S"), "| Router", THIS_NODE, "here")

    read_file(args[1])

    with socket(AF_INET, SOCK_DGRAM) as server:
        print(time.strftime('%H:%M:%S'),
              f'| Binding to {THIS_NODE}:{PORT+int(HOST_ID)}')
        server.bind((THIS_NODE, PORT+int(HOST_ID)))

        INPUTS = [server]

        print(time.strftime('%H:%M:%S'),
              f'| Listening on {THIS_NODE}:{PORT+int(HOST_ID)}')

        time.sleep(random.randint(2, 8))

        for n in NEIGHBORS:
            send_update(n)

        print_status()

        while INPUTS:
            readable, writable, exceptional = select.select(
                INPUTS, [], [], TIMEOUT)
            update_vector = False

            if random.randint(0, 100) < 10:
                send_msg = random.choice(MESSAGES)
                send_to = random.choice(list(ROUTING_TABLE.keys()))
                send_hello(send_msg, THIS_NODE, send_to)
                print(time.strftime('%H:%M:%S'),
                      f'| Sending {send_msg} to {send_to} via {ROUTING_TABLE[send_to][1]}')

            for r in readable:

                time.sleep(2)

                recv, addr = server.recvfrom(1024)
                if recv:
                    msg_type = int.from_bytes(recv[0:1], byteorder='big')
                    if msg_type == 0:
                        update_vector = parse_update(recv, addr[0])
                        if update_vector:
                            print(time.strftime('%H:%M:%S'),
                                  f'| Table updated with information from {addr[0]}')
                            print_status()
                    elif msg_type == 1:
                        parse_hello(recv)
                    else:
                        print(time.strftime('%H:%M:%S'),
                              f'| Received unexpected message from {addr}. Message will be ignored.')

            if update_vector:
                for n in NEIGHBORS:
                    send_update(n)

            for n in NEIGHBORS:
                if not n in INPUTS:
                    send_update(n)

if __name__ == "__main__":
    main(sys.argv)
