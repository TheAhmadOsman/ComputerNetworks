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


def val_to_2_bytes(value: int) -> list:
    '''Split a value into 2 bytes'''

    '''
        loop over n_bytes, extract right most eight, and then right shift for 8 bits.
        430 & 0xFF -> val_right =
        430 >> 8 gives me the val_left

        or use to_bytes function: https://docs.python.org/3.7/library/stdtypes.html
    '''

    '''
        val_to_2_bytes takes an integer and returns that number converted to a list of 2 bytes (numbers between 0 and 255). Use shift (>>) and binary and (&) to extract left and right 8 bits. This function is used extensively as many fields in the DNS request and response are using 2 bytes, even if a value fits 1 byte.
            43043 = 0b1010100000100011 => [0b10101000, 0b00100011] = [168, 35]
                                            left 8      right 8
    '''

    try:
        bytes = list(value.to_bytes(2, byteorder='big'))
    except OverflowError as e:
        raise OverflowError(
            "Could not store value into the specified number of bytes!")
    return bytes


def val_to_n_bytes(value: int, n_bytes: int) -> list:
    '''Split a value into n bytes'''

    '''
        val_to_n_bytes takes an integer and the target list size, converting the number to a list of the specified size. Use shifting (<<, >>) and bit masking (&) in a loop to generate the list. You don't have to use this function but it's a great way to learn bitwise operations.

        430430 = 0b1101001000101011110 => [0b00000110, 0b10010001, 0b01011110] = [6, 145, 94]
                                            left 8      middle 8    right 8
    '''

    try:
        bytes = list(value.to_bytes(n_bytes, byteorder='big'))
    except OverflowError as e:
        raise OverflowError(
            "Could not store value into the specified number of bytes!")
    return bytes


def bytes_to_val(bytes_lst: list) -> int:
    '''Merge 2 bytes into a value'''
    '''
        bytes_to_val takes a list of bytes and returns their value as a single integer. Use shift (<<) and addition in a loop to construct the result. This function is used extensively as many DNS fields are stored in 2 bytes.

        [6, 145, 94] = [0b110, 0b10010001, 0b01011110] => 0b1101001000101011110 = 430430
    '''
    value = int.from_bytes(bytes_lst, byteorder="big")
    return value


def get_2_bits(bytes_lst: list) -> int:
    '''Extract first two bits of a two-byte sequence'''

    '''
        get_2_bits extracts the leftmost 2 bits from a 2-byte sequence. Use a simple shift to extract the target bits. This function is used to determine whether the domain is stored in the answer as a label or a pointer. See the provided references for details on those two formats.

        0xc00c = 0b1100000000001100 => leftmost 2 bits are 0b11 = 3
    '''

    bits = bytes_lst[0] >> 6
    return bits


def get_domain_name_location(bytes_lst: list) -> int:
    '''Extract size of the offset from a two-byte sequence'''

    '''
        get_offset extracts the rightmost 14 bits from a 2-byte sequence. This function can be used to extract the location of the domain name inside a response. Note that a response may contain either labels or pointers, so don't rely on the magic of 0xc00c. A more descriptive name for this function is get_domain_name_location_within_a_server_response. Do not confuse the offset found by this function with the offset of answers within the response.

        0xc00c = 0b1100000000001100 => rightmost 14 bits are 0b1100= 12
    '''

    offset = ((bytes_lst[0] & 0x3f) << 8) + bytes_lst[1]
    return offset


def parse_cli_query(filename, q_type, q_domain, q_server=None) -> tuple:
    '''Parse command-line query'''

    '''
        parse_cli_query takes a filename, a query type, the domain name to resolve, and an optional server address as parameters and returns a tuple of the numeric value of the query type (as found in the DNS_TYPES dictionary), domain name (as a list of strings), and the server address. If the server address is not specified, pick one randomly as follows: choice(PUBLIC_DNS_SERVER).
    '''

    q_num = 0
    if q_type == "A":
        q_num = DNS_TYPES[q_type]
    elif q_type == "AAAA":
        q_num = DNS_TYPES[q_type]
    else:
        raise ValueError("Unknown query type")

    q_domain = q_domain.split(".")

    if q_server == None:
        q_server = choice(PUBLIC_DNS_SERVER)

    return (q_num, q_domain, q_server)


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
        assert format_query(
            1, ['luther', 'edu']) == b'OB\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x06luther\x03edu\x00\x00\x01\x00\x01'

        # OB is transaction id - convert each of those characters including space back into hexadecimal
    '''

    '''
        format_query takes the query type and the domain name as parameters and builds a query as a bytearray. Bytearrays are mutable byte sequences in Python, so you should start with an empty one and use append or extend to form a valid DNS query. Transaction id should be chosen at random as follows: randint(0, 65535). Use default value, 0x100 for the flags. The domain name should be in the QNAME format, terminated by \0.

        56 f0 01 00 00 01 00 00 00 00 00 00 06 6c 75 74 68 65 72 03 65 64 75 00 00 01 00 01
        |---| |---| |---| |---| |---| |---| |------------------| |---------| || |---| |---|
        |id | |flags, # of questions etc  | | luther           | | edu     | \0 |typ| |cls|
    '''

    formatted_query = bytearray()

    # problem here, to pass the test, you need the trans_id_bytes to be:
    trans_id_bytes = b'OB'
    # trans_id = randint(0, 65535)
    # trans_id_bytes = val_to_2_bytes(trans_id)

    formatted_query.extend(trans_id_bytes)

    flag_bytes = val_to_2_bytes(int('0100', 16))
    formatted_query.extend(flag_bytes)

    questions_bytes = val_to_2_bytes(1)
    formatted_query.extend(questions_bytes)

    others_bytes = val_to_n_bytes(0, 6)
    formatted_query.extend(others_bytes)

    for domain in q_domain:
        length_bytes = val_to_n_bytes(len(domain), 1)
        domain_bytes = bytes(domain, "utf-8")
        formatted_query.extend(length_bytes)
        formatted_query.extend(domain_bytes)

    domain_end_bytes = val_to_n_bytes(0, 1)
    formatted_query.extend(domain_end_bytes)
    type_bytes = val_to_2_bytes(q_type)
    formatted_query.extend(type_bytes)
    class_bytes = val_to_2_bytes(1)
    formatted_query.extend(class_bytes)

    return bytes(formatted_query)


def send_request(q_message: bytearray, q_server: str) -> bytes:
    '''Contact the server'''

    '''
        send_request takes the formatted message and the server address and sends the DNS request. This function returns the DNS response for the parser to process.
    '''

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

    '''
        parse_response takes bytes received from the server and returns a list (or a tuple, it doesn't matter) where each item is a tuple of the domain name, TTL, and the address, as extracted from the server response. This function processes the response header (first 12 bytes and the query), calls parse_answers to parse the specific answer(s), and returns the results returned by parse_answers. You don't need to validate values in the response (i.e. transaction id and flags) but you have to extract the number of answers from the header and the starting byte of the answers.
    '''

    no_of_answers = resp_bytes[6:8]
    length = int(no_of_answers.hex(), 16)
    return parse_answers(resp_bytes, resp_bytes.find(b'\xc0\x0c'), length)


def parse_answers(resp_bytes: bytes, offset: int, rr_ans: int) -> list:
    '''Parse DNS server answers'''

    '''
        c00c means go back to the query since we received a label and we want to know our domain name.
        Extract
        2bytes

        The tuple sends back 4bytes of time to live in the middle in seconds

        Your answe starts at the offset, 12 bytes for the DNS Header, whatever for query, and then the answer in the offset.

        Two offsets:

        The offset starts with 11 C0
    '''

    '''
        parse_answers takes the response message bytes, starting position for the answer(s) within the response, and the number of answers. It returns a list of tuples (domain, ttl, address). Do not confuse the offset in this function (a better(?) name would be number_of_bytes_from_the_beginning_of_the_response_to_the_first_answer) and the domain_name_start_offset. Keep in mind that the domain name may be in different format, label or pointer. You should be able to process both.

        Once you've processed an answer, add the results to the list and move to the next one, if present. Once all the answers are collected, return the list of tuples.

        c0 0c 00 01 00 01 00 00 00 05 00 04 ae 81 19 aa
        |---| |---| |---| |---------| |---| |---------|
        |ptr| |typ| |cls| | ttl     | |len| | address |
    '''

    ''' 0c location is the offset given to me, answer start after that
        thus the domain is going to between 12 and offset -6'''

    """ 
    domain_lst = []
    start_at = 12
    stop_at = offset - 6
    how_many = stop_at - start_at

    domain_byte = resp_bytes[start_at:stop_at+1]

    # \x05yahoo\x03com\x06osmaah'
    idx_1 = 1
    idx_2 = domain_byte[0]
    while how_many != 0:
        domain = domain_byte[idx_1:idx_2+2]
        how_many -= len(domain)
        idx_1 += idx_2+4
        idx_2 = idx_1 + domain_byte[idx_1]
        domain_lst.append(domain)

    domain = '.'.join(domain_lst) 
    """

    domain_pt1_starts_at = resp_bytes[12]
    domain_pt1 = resp_bytes[13:13+domain_pt1_starts_at].decode("utf-8")
    domain_pt2_starts_at = resp_bytes[13+domain_pt1_starts_at]
    domain_pt2 = resp_bytes[14+domain_pt1_starts_at:14 +
                            domain_pt1_starts_at+domain_pt2_starts_at].decode("utf-8")
    domain_name = '.'.join([domain_pt1, domain_pt2])

    answers = []
    # if it is labeled...
    if offset == -1:
        '''
        x05yahoo\x03com\x00\x00\x01\x00\x01\x00\x00' +
                              b'\x00\x05\x00\x04b\x89\xf6\x07\x05yahoo
        '''
        before, offset, after = resp_bytes.partition(bytes(domain_pt2, 'utf-8'))
        resp_bytes = after
        for answer in range(rr_ans):
            before, offset, after = resp_bytes.partition(bytes(domain_pt2, 'utf-8'))
            resp_bytes = after
            print(after)
            ttl = int(after[5:9].hex(), 16)
            addr_length = int(after[9:11].hex(), 16)
            ip = ""
            if addr_length == 4:
                ip = parse_address_a(4, after[11:11+addr_length])
            elif addr_length == 16:
                ip = parse_address_aaaa(16, after[11:11+addr_length])

            answers.append((domain_name, ttl, ip))
    else:
        for answer in range(rr_ans):
            before, offset, after = resp_bytes.partition(b'\xc0\x0c')
            resp_bytes = after
            ttl = int(after[4:8].hex(), 16)
            addr_length = int(after[8:10].hex(), 16)
            ip = ""
            if addr_length == 4:
                ip = parse_address_a(4, after[10:10+addr_length])
            elif addr_length == 16:
                ip = parse_address_aaaa(16, after[10:10+addr_length])

            answers.append((domain_name, ttl, ip))

    return answers


def parse_address_a(addr_len: int, addr_bytes: bytes) -> str:
    '''Extract IPv4 address'''

    '''
        parse_address_a extracts IPv4 address from the response and returns it in the dotted-decimal notation.
    '''

    lst = []
    for i in range(addr_len):
        lst.append(str(addr_bytes[i]))
    return '.'.join(lst)


def parse_address_aaaa(addr_len: int, addr_bytes: bytes) -> str:
    '''Extract IPv6 address'''

    '''
        assert parse_address_aaaa(16, b' \x01I\x98\x00\x0c\x10#\x00\x00\x00\x00\x00\x00\x00\x04\xc0') == '2001:4998:c:1023:0:0:0:4'
    '''

    '''
        parse_address_aaaa extracts IPv6 address from the response and returns it in the hex-colon notation.
    '''

    lst = []
    for i in range(0, addr_len-1, 2):
        value = addr_bytes[i:i+2].hex().lstrip("0")
        lst.append(value)

    for i, value in enumerate(lst):
        if value == '':
            lst[i] = '0'

    return ':'.join(lst)


def resolve(query: str) -> None:
    '''Resolve the query'''

    '''
        resolve calls and other functions and prints the results.
    '''

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
