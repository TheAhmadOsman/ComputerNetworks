"""Python Pinger"""
#!/usr/bin/env python3
# encoding: UTF-8

import binascii
import os
import select
import struct
import sys
import time
import socket
from statistics import mean, stdev

ECHO_REQUEST_TYPE = 8
ECHO_REPLY_TYPE = 0
ECHO_REQUEST_CODE = 0
ECHO_REPLY_CODE = 0
REGISTRARS = ["afrinic.net", "apnic.net", "arin.net", "lacnic.net", "ripe.net"]
# REGISTRARS = ["example.com"]


def print_raw_bytes(pkt: bytes) -> None:
    """Printing the packet bytes"""
    for i in range(len(pkt)):
        sys.stdout.write("{:02x} ".format(pkt[i]))
        if (i + 1) % 16 == 0:
            sys.stdout.write("\n")
        elif (i + 1) % 8 == 0:
            sys.stdout.write("  ")
    sys.stdout.write("\n")


def checksum(pkt: bytes) -> int:
    """Calculate checksum"""
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


def parse_reply(my_socket: socket.socket, req_id: int, timeout: int, addr_dst: str) -> tuple:
    """
        Receive an Echo reply and parses it.
        Takes the following arguments: socket, request id, timeout, and the destination address. 
        Returns a tuple of the destination address, packet size, roundtrip time, time to live, and sequence number. 
        You need to modify lines between labels TODO and DONE. 
        This function should raise an error if the response message type, code, or checksum are incorrect.
    """
    time_left = timeout
    while True:
        started_select = time.time()
        what_ready = select.select([my_socket], [], [], time_left)
        how_long_in_select = time.time() - started_select
        if what_ready[0] == []:  # Timeout
            raise TimeoutError("Request timed out after 1 sec")

        time_rcvd = time.time()
        pkt_rcvd, addr = my_socket.recvfrom(1024)
        if addr[0] != addr_dst:
            raise ValueError(f"Wrong sender: {addr[0]}")
        
        # TODO: Extract ICMP header from the IP packet and parse it
        
        # print_raw_bytes(pkt_rcvd)
        
        pkt_size = len(pkt_rcvd)
        ICMP_header = pkt_rcvd[20:28]
        ICMP_type, code, chksum, pkt_id, seq_num = struct.unpack("bbHHh", ICMP_header)
        
        # print_raw_bytes(ICMP_header)
        # print_raw_bytes(struct.unpack("bbHHh", ICMP_header))
        
        if ICMP_type != ECHO_REPLY_TYPE:
            raise ValueError(f"Wrong ICMP Type: {ICMP_type}")
        elif code != ECHO_REPLY_CODE:
            raise ValueError(f"Wrong Code Type: {code}")
        elif pkt_id != req_id:
            raise ValueError("Request ID is not the same as the Packet ID")

        bts = struct.calcsize("d")
        timestamp = struct.unpack("d", pkt_rcvd[28:28 + bts])[0]
        rtt = time_rcvd - timestamp

        ttl = pkt_rcvd[8]

        my_checksum = 0
        hdr = struct.pack("bbHHh", ICMP_type, code, my_checksum, pkt_id, seq_num)
        my_checksum = checksum(hdr + pkt_rcvd[28:])

        v = list(my_checksum.to_bytes(2, byteorder='big'))
        my_hex_chksum = hex(v[0]).replace("0x", '') + hex(v[1]).replace("0x", '')

        chksum_raw_bytes = pkt_rcvd[22:24]

        tmp = []
        for i in range(len(chksum_raw_bytes)):
            tmp.append("{:02x} ".format(chksum_raw_bytes[i]))
        
        tmp = ''.join(tmp)
        tmp = tmp.replace(' ', '')
        # print(tmp)

        if my_hex_chksum != tmp:
            raise ValueError("Incorrect Checksum")
        
        # DONE: End of ICMP parsing
        
        time_left = time_left - how_long_in_select
        if time_left <= 0:
            raise TimeoutError("Request timed out after 1 sec")

        return (addr_dst, pkt_size, rtt, ttl, seq_num)

def format_request(req_id: int, seq_num: int) -> bytes:
    """Format an Echo request"""
    my_checksum = 0
    header = struct.pack(
        "bbHHh", ECHO_REQUEST_TYPE, ECHO_REQUEST_CODE, my_checksum, req_id, seq_num
    )
    data = struct.pack("d", time.time())
    my_checksum = checksum(header + data)

    if sys.platform == "darwin":
        my_checksum = socket.htons(my_checksum) & 0xFFFF
    else:
        my_checksum = socket.htons(my_checksum)

    header = struct.pack(
        "bbHHh", ECHO_REQUEST_TYPE, ECHO_REQUEST_CODE, my_checksum, req_id, seq_num
    )
    packet = header + data
    return packet


def send_request(addr_dst: str, seq_num: int, timeout: int = 1) -> tuple:
    """Send an Echo Request"""
    result = None
    proto = socket.getprotobyname("icmp")
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, proto)
    my_id = os.getpid() & 0xFFFF

    packet = format_request(my_id, seq_num)
    my_socket.sendto(packet, (addr_dst, 1))

    try:
        result = parse_reply(my_socket, my_id, timeout, addr_dst)
    except ValueError as ve:
        raise(f"Packet error: {ve}")
    finally:
        my_socket.close()
    return result


def ping(host: str, pkts: int, timeout: int = 1) -> None:
    """
        Main loop
        Takes a destination host, number of packets to send, and timeout as arguments. 
        Displays host statistics. You need to modify lines between labels TODO and DONE.
    """
    # TODO: Implement the main loop
    addr_dst = socket.gethostbyname(host)
    
    print()
    print("--- Ping", host, '(' + addr_dst + ')', "using Python ---")
    print()

    pkts_lost = 0
    rttlst = []
    for i in range(pkts):
        result = ""
        try:
            result = send_request(addr_dst, seq_num = i, timeout = timeout)
            rttlst.append(round(result[2] * pow(10, 3), 2))
            print(result[1], "bytes from", str(result[0]) + ": icmm_seq=" + str(result[4] + 1), "TTL=" + str(result[3]), "time=" + str(round(result[2] * pow(10, 3), 2)), "ms")
        except TimeoutError as e:
            result = "No response: " + str(e)
            pkts_lost += 1
            print(result)
        except Exception as e:
            pkts_lost += 1
            print("Error:", e)
    
    print()
    print("---", host, "ping statistics ---")
    
    if pkts_lost == pkts:
        print(pkts, "packets transmitted,", pkts-pkts_lost, "received, 100% packet loss")
    else:
        print(pkts, "packets transmitted,", pkts-pkts_lost, "received,", str(int(pkts_lost/pkts * 100)) + "% packet loss")
        try:
            rttMin = round(min(rttlst), 3)
            rttMax = round(max(rttlst), 3)
            rttAvg = round(mean(rttlst), 3)
            rttStdev = round(stdev(rttlst), 3)
            print(f"rtt min/avg/max/mdev = {rttMin}/{rttAvg}/{rttMax}/{rttStdev} ms")
        except:
            pass
    # DONE
    return


if __name__ == "__main__":
    for rir in REGISTRARS:
        ping(rir, 5)
