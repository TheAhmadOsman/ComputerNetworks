'''
DNS Name Server
'''
#!/usr/bin/env python3

import sys
from random import randint, choice
from socket import socket, SOCK_DGRAM, AF_INET
import re


HOST = "localhost"
PORT = 43053

DNS_TYPES = {
    1: 'A',
    2: 'NS',
    5: 'CNAME',
    12: 'PTR',
    15: 'MX',
    16: 'TXT',
    28: 'AAAA'
}

TTL_SEC = {
    '1s': 1,
    '1m': 60,
    '1h': 60*60,
    '1d': 60*60*24,
    '1w': 60*60*24*7,
    '1y': 60*60*24*365
    }


def val_to_bytes(value: int, n_bytes: int) -> list:
    '''Split a value into n bytes'''

    '''
        val_to_bytes takes an integer and a number of bytes and returns that integer as a list of the specified length. Most fields in DNS response use 2 bytes, but TTL uses 4 bytes. Use shift (<<, >>) and masking (&) to generate the list.
    '''
    
    try:
        bytes = list(value.to_bytes(n_bytes, byteorder='big'))
    except OverflowError as e:
        raise OverflowError(
            "Could not store value into the specified number of bytes!")
    return bytes


def bytes_to_val(bytes_lst: list) -> int:
    '''Merge n bytes into a value'''

    '''
        bytes_to_val takes a list of bytes (values 0..255) and returns the value. Most values in DNS use 2 bytes, but you should implement a more generic algorithm to process a list of any length.
    '''

    value = int.from_bytes(bytes_lst, byteorder="big")
    return value


def get_left_bits(bytes_lst: list, n_bits: int) -> int:
    '''Extract left n bits of a two-byte sequence'''

    '''
        get_left_bits takes a 2-byte list and a number n and returns leftmost n bits of that sequence as an integer.
    '''
    
    b = bytes_to_val(bytes_lst)
    b = b >> (16-n_bits)
    return b


def get_right_bits(bytes_lst: list, n_bits) -> int:
    '''Extract right n bits bits of a two-byte sequence'''

    '''
        get_right_bits takes a 2-byte list and a number n and returns rightmost n bits of that sequence as an integer.
    '''

    b = bytes_to_val(bytes_lst)
    b = b & int("1"*n_bits, 2)
    return b


def read_zone_file(filename: str) -> tuple:
    '''Read the zone file and build a dictionary'''

    '''
        read_zone_file takes file name as a parameter and reads the zone from that file. This function builds a dictionary of the following format: {domain: [(ttl, class, type, address)]} where each record is a list of tuples (answers). The function should return a tuple of (origin, zone_dict). If the requested domain is not in our zon, parse_request should raise a ValueError. Note that the records in the zone file may be incomplete (missing a domain name or TTL). The missing domain name should be replaced with the one from the previous line, missing TTL should be replaced with the default one (2nd line of the zone file). If a record contains multiple answers, return them all.
    '''

    zone = dict()
    with open(filename) as zone_file:
        origin = zone_file.readline().split()[1].rstrip('.')
        origin_ttl = zone_file.readline().split()[1].rstrip('.')
        domain = ""
        for line in zone_file:
            line_lst = line.strip().split()
            if len(line_lst) == 5:
                domain = line_lst[0]
                zone[domain] = [(TTL_SEC[line_lst[1]], line_lst[2], line_lst[3], line_lst[4])]
            elif len(line_lst) == 4:
                if line_lst[0] in TTL_SEC:
                    zone[domain].append((TTL_SEC[line_lst[0]], line_lst[1], line_lst[2], line_lst[3]))
                else:
                    domain = line_lst[0]
                    zone[domain] = [(TTL_SEC[origin_ttl], line_lst[1], line_lst[2], line_lst[3])]
            else:
                zone[domain].append((TTL_SEC[origin_ttl], line_lst[0], line_lst[1], line_lst[2]))
    
    return (origin, zone)


def parse_request(origin: str, msg_req: bytes) -> tuple:
    '''Parse the request'''

    '''
        parse_request takes origin and the request bytes and returns a tuple of (transaction id, domain, query type, query). The query is required as it is included in the response. This function must raise ValueErrors if the type, class, or zone (origin) cannot be processed. Those exceptions are caught in the run function.

        56 f0 01 00 00 01 00 00 00 00 00 00 06 6c 75 74 68 65 72 03 65 64 75 00 00 01 00 01
        |---| |---| |---| |---| |---| |---| |------------------| |---------| || |---| |---| 
        |id | |flags, # of questions etc  | | luther           | | edu     | \0 |typ| |cls|
                                            |------------------query----------------------|
    '''

    raise NotImplementedError


def format_response(zone: dict, trans_id: int, qry_name: str, qry_type: int, qry: bytearray) -> bytearray:
    '''Format the response'''
    raise NotImplementedError


def run(filename: str) -> None:
    '''Main server loop'''
    server_sckt = socket(AF_INET, SOCK_DGRAM)
    server_sckt.bind((HOST, PORT))
    origin, zone = read_zone_file(filename)
    print("Listening on %s:%d" % (HOST, PORT))

    while True:
        (request_msg, client_addr) = server_sckt.recvfrom(512)
        try:
            trans_id, domain, qry_type, qry = parse_request(origin, request_msg)
            msg_resp = format_response(zone, trans_id, domain, qry_type, qry)
            server_sckt.sendto(msg_resp, client_addr)
        except ValueError as ve:
            print('Ignoring the request: {}'.format(ve))
    server_sckt.close()


def main(*argv):
    '''Main function'''
    if len(argv[0]) != 2:
        print('Proper use: python3 nameserver.py <zone_file>')
        exit()
    run(argv[0][1])


if __name__ == '__main__':
    main(sys.argv)
