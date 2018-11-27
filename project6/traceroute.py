"""Python traceroute implementation"""
#!/usr/bin/env python3
# encoding: UTF-8


import os
import select
import socket
import struct
import sys
import time


ATTEMPTS = 3
ECHO_REQUEST_CODE = 0
ECHO_REQUEST_TYPE = 8
MAX_HOPS = 30
TIMEOUT = 1


def print_raw_bytes(pkt: bytes) -> None:
    """
        Print the packet bytes.
        Takes packet as an argument and prints prints all the bytes as hexadecimal values.
    """
    for i in range(len(pkt)):
        sys.stdout.write("{:02x} ".format(pkt[i]))
        if (i + 1) % 16 == 0:
            sys.stdout.write("\n")
        elif (i + 1) % 8 == 0:
            sys.stdout.write("  ")
    sys.stdout.write("\n")


def checksum(pkt: bytes) -> int:
    """
        Calculate and return checksum.
        Takes packet as an argument and returns its Internet checksum.
    """
    csum = 0
    count = 0
    count_to = (len(pkt) // 2) * 2

    while count < count_to:
        this_val = (pkt[count + 1]) * 256 + (pkt[count])
        csum = csum + this_val
        csum = csum & 0xFFFFFFFF
        count = count + 2

    if count_to < len(pkt):
        csum = csum + (pkt[len(pkt) - 1])
        csum = csum & 0xFFFFFFFF

    csum = (csum >> 16) + (csum & 0xFFFF)
    csum = csum + (csum >> 16)
    result = ~csum
    result = result & 0xFFFF
    result = result >> 8 | (result << 8 & 0xFF00)

    return result


def format_request(icmp_type: int, icmp_code: int, req_id: int, seq_num: int) -> bytes:
    """
        Format an Echo request.
        Takes ICMP type, ICMP code, request ID, and sequence number as arguments and returns a properly formatted ICMP request packet with current time as data. This function has to compute the packet's checksum and add it to the header of the outgoing message.
    """
    chk_header = struct.pack("bbHHh", icmp_type, icmp_code, 0, req_id, seq_num)
    data = struct.pack("d", time.time())

    calculated_checksum = socket.htons(checksum(chk_header + data))

    header = struct.pack("bbHHh", icmp_type, icmp_code,
                         calculated_checksum, req_id, seq_num)

    return header + data


def send_request(packet: bytes, addr_dst: str, ttl: int) -> socket:
    """
        Send an Echo Request.
        Takes packet bytes, destination address, and Time-to-Live value as arguments and returns a new raw socket. This function sets the socket's time-to-live option to the supplied value.
    """
    proto = socket.getprotobyname("icmp")
    my_icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, proto)
    my_icmp_socket.settimeout(TIMEOUT)
    my_icmp_socket.setsockopt(
        socket.IPPROTO_IP, socket.IP_TTL, struct.pack("I", ttl))
    my_icmp_socket.sendto(packet, (addr_dst, 1))
    return my_icmp_socket


def receive_reply(open_socket: socket, timeout: int = 1) -> tuple:
    """
        Receive an ICMP reply.
        Takes a socket and timeout as arguments and returns a tuple of the received packet and the IP address of the responding host. This function uses select and may raise a TimeoutError is the response does not come soon enough.
    """

    time_left = timeout
    started_select = time.time()

    what_ready = select.select([open_socket], [], [], time_left)

    how_long_in_select = time.time() - started_select
    time_left = time_left - how_long_in_select

    pkt_rcvd, addr = open_socket.recvfrom(1024)

    if not what_ready[0]:
        raise TimeoutError("Request timed out")
    if time_left <= 0:
        raise TimeoutError("Request timed out")
        
    return (pkt_rcvd, addr[0])


def parse_reply(packet: bytes) -> bool:
    """
        Parse an ICMP reply.
        Takes a packet as an argument and returns True if it is a valid (expected) response. This function parses the response header and verifies that the ICMP type is 0, 3, or 11. It also validates the response checksum and raises a ValueError if it's incorrect.
    """
    expected_types = [0, 3, 11]
    
    icmp_data = packet[28:]
    icmp_header = packet[20:28]

    pseudo_header = bytearray()
    pseudo_header.append(0)
    pseudo_header.append(0)
    pseudo_header.extend(icmp_header[0:2])
    pseudo_header.extend(icmp_header[4:])

    icmp_msg_type, icmp_msg_code, check_sum_rcvd, repl_id, sequence = struct.unpack(
        "bbHHh", icmp_header)

    if icmp_msg_type not in expected_types:
        raise ValueError(f"Incorrect type: {icmp_msg_type}. Expected {', '.join([str(x) for x in expected_types])}.")

    check_sum_comptd = checksum(pseudo_header + icmp_data)

    if check_sum_rcvd != socket.htons(check_sum_comptd):
        raise ValueError(f"Incorrect checksum: {check_sum_rcvd}")
    
    return True


def traceroute(hostname: str) -> None:
    """
        Trace the route to a domain.
        Takes host (domain) name as an argument and traces a path to that host. The general approach is to have a big loop that sends ICMP Echo Request messages to the host, incrementally increasing TTL value. Each iteration of this loop generates ATTEMPTS (3) messages. There are two possible sources of errors: Timeout (response was not received within timeout) and Value (something is wrong with the response). For each attempts you should do the following:
            Format an ICMP Request
            Send the request to the destination host
            Receive a response (may or may not be a proper ICMP Reply)
            Parse the response and check for errors
            Print the relevant statistics, if possible
            Print the error message, if any
            Stop the probe after MAX_HOPS attempts or once a response from the destination host is received
    """
    dest_addr = socket.gethostbyname(hostname)
    print(
        f"Tracing route to {hostname} [{dest_addr}] over a maximum of {MAX_HOPS} hops\n")

    my_id = os.getpid() & 0xFFFF
    delim = " "

    for ttl in range(1, MAX_HOPS + 1):
        received_success=0
        parsed_success = 0

        print(f"{ttl:<5d}", end="")

        for att in range(ATTEMPTS):
            to_error_msg=""
            v_error_msg=""
            
            time_sent=time.time()
            packet=format_request(ECHO_REQUEST_TYPE, ECHO_REQUEST_CODE, my_id, att)
            my_icmp_socket=send_request(packet, hostname, ttl)
            

            try:
                pkt_rcvd, responder=receive_reply(my_icmp_socket, TIMEOUT)
                received_success += 1
            except TimeoutError as te:
                to_error_msg=str(te)
            finally:
                my_icmp_socket.close()
                
            if to_error_msg:
                continue

            time_rcvd=time.time()
            rtt=(time_rcvd - time_sent) * 1000
            try:
                parse_reply(pkt_rcvd)
                parsed_success += 1
            except ValueError as ve:
                v_error_msg=str(ve)

            if v_error_msg:
                continue

    
        if to_error_msg:
            print("{:>5s} {:2s}".format("TIME", " "), end="")
            print(f"{delim:3s} {to_error_msg}")
        elif v_error_msg:
            print("{:>5s} {:2s}".format("ERR", " "), end="")
            print(f"{delim:3s} {v_error_msg}")
        else:
            print(f"{rtt:>5.0f} ms", end="")
            print(f"{delim:3s} {responder}")
                    
        if responder == dest_addr:
            break

    print("\nTrace complete.")
    sys.exit(1)


def main(args):
    """
        Main Program.
        Takes command line arguments and starts the probe.
    """
    try:
        traceroute(args[1])
    except IndexError:
        print(f"Usage: {args[0]} <hostname>")


if __name__ == "__main__":
    """
        Running Main
    """
    main(sys.argv)
