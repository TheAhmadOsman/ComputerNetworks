#!/usr/bin/env python3

import sys
from random import randint, choice, seed
from socket import socket, SOCK_DGRAM, AF_INET


PORT = 53

DNS_TYPES = {
    'A': 1,
    'AAAA': 28,
    'CNAME': 5,
    'MX': 15,
    'NS': 2,
    'PTR': 12,
    'TXT': 16
}

PUBLIC_DNS_SERVER = [
    '1.0.0.1',  # Cloudflare
    '1.1.1.1',  # Cloudflare
    '8.8.4.4',  # Google
    '8.8.8.8',  # Google
    '8.26.56.26',  # Comodo
    '8.20.247.20',  # Comodo
    '9.9.9.9',  # Quad9
    '64.6.64.6',  # Verisign
    '208.67.222.222',  # OpenDNS
    '208.67.220.220'  # OpenDNS
]

# loop over n_bytes, extract right most eight, and then right shift for 8 bits.
# 430 & 0xFF -> val_right =
# 430 >> 8 gives me the val_left


def val_to_2_bytes(value: int) -> list:
    '''Split a value into 2 bytes'''
    if (len(bin(value))-2) > 16:
        raise ValueError(
            "Could not store value into the specified number of bytes!")

    raise NotImplementedError


def val_to_n_bytes(value: int, n_bytes: int) -> list:
    '''Split a value into n bytes'''
    if (len(bin(value))-2) > (n_bytes*8):
        raise ValueError(
            "Could not store value into the specified number of bytes!")
    raise NotImplementedError


def bytes_to_val(bytes_lst: list) -> int:
    '''Merge 2 bytes into a value'''
    raise NotImplementedError


def get_2_bits(bytes_lst: list) -> int:
    '''Extract first two bits of a two-byte sequence'''
    raise NotImplementedError


def get_offset(bytes_lst: list) -> int:
    '''Extract size of the offset from a two-byte sequence'''
    return ((bytes_lst[0] & 0x3f) << 8) + bytes_lst[1]


def parse_cli_query(filename, q_type, q_domain, q_server=None) -> tuple:
    '''Parse command-line query'''
    raise NotImplementedError


def format_query(q_type: int, q_domain: list) -> bytearray:
    '''Format DNS query'''
    '''
    Head is always 12 bytes - Query, message size of varying size ending with 00 - Answers
    0100 -> request flag or 8180 for response flag
    ID: An arbitrary 16 bit request identifier. The same ID is used in the response to the query so we can match them up. Let’s go with AA AA.

    QR: A 1 bit flag specifying whether this message is a query (0) or a response (1). As we’re sending a query, we’ll set this bit to 0.

    Opcode: A 4 bit field that specifies the query type. We’re sending a standard query, so we’ll set this to 0. The possibilities are:
        0: Standard query
        1: Inverse query
        2: Server status request
        3-15: Reserved for future use
 
    TC: 1 bit flag specifying if the message has been truncated. Our message is short, and won’t need to be truncated, so we can set this to 0.

    RD: 1 bit flag specifying if recursion is desired. If the DNS server we send our request to doesn’t know the answer to our query, it can recursively ask other DNS servers. We do wish recursion to be enabled, so we will set this to 1.

    QDCOUNT: An unsigned 16 bit integer specifying the number of entries in the question section. We’ll be sending 1 question.
    '''
    '''
        assert format_query(1, ['luther', 'edu']) == b'OB\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x06luther\x03edu\x00\x00\x01\x00\x01'
    '''
    # OB is transaction id - convert each of those characters including space back into hexadecimal
    raise NotImplementedError


def send_request(q_message: bytearray, q_server: str) -> bytes:
    '''Contact the server'''
    client_sckt = socket(AF_INET, SOCK_DGRAM)
    client_sckt.sendto(q_message, (q_server, PORT))
    (q_response, _) = client_sckt.recvfrom(2048)
    client_sckt.close()

    return q_response


def parse_response(resp_bytes: bytes):
    '''Parse server response'''
    '''
        c00c means go back to the query since we received a label and we want to know our domain name.
        Extract 
        2bytes

        The tuple sends back 4bytes of time to live in the middle in seconds

        Your answe starts at the offset, 12 bytes for the DNS Header, whatever for query, and then the answer in the offset.

        Two offsets:

        The offset starts with 11 C0
    '''
    raise NotImplementedError


def parse_answers(resp_bytes: bytes, offset: int, rr_ans: int) -> list:
    '''Parse DNS server answers'''
    raise NotImplementedError


def parse_address_a(addr_len: int, addr_bytes: bytes) -> str:
    '''Extract IPv4 address'''
    raise NotImplementedError


def parse_address_aaaa(addr_len: int, addr_bytes: bytes) -> str:
    '''Extract IPv6 address'''

    # assert parse_address_aaaa(16, b' \x01I\x98\x00\x0c\x10#\x00\x00\x00\x00\x00\x00\x00\x04\xc0') == '2001:4998:c:1023:0:0:0:4'

    

    raise NotImplementedError


def resolve(query: str) -> None:
    '''Resolve the query'''
    q_type, q_domain, q_server = parse_cli_query(*query[0])
    query_bytes = format_query(q_type, q_domain)
    response_bytes = send_request(query_bytes, q_server)
    answers = parse_response(response_bytes)
    print('DNS server used: {}'.format(q_server))
    for a in answers:
        print('Domain: {}'.format(a[0]))
        print('TTL: {}'.format(a[1]))
        print('Address: {}'.format(a[2]))


def main(*query):
    '''Main function'''
    if len(query[0]) < 3 or len(query[0]) > 4:
        print('Proper use: python3 resolver.py <type> <domain> <server>')
        exit()
    resolve(query)


if __name__ == '__main__':
    main(sys.argv)
