# Custom BIND

Complete the following programming project and push code to your GitHub repository.

**Process records of type A (IPv4) or AAAA (IPv6) only. If a client requests anything else, ignore it.**

Use your DNS resolver to initiate requests to the server.

```
python3 nameserver.py zoo.zone
```

1. Read the zone file *zoo.zone* and resolve names found there.

2. Create a UDP socket connection and wait for a message from the DNS resolver.

3. Parse the DNS request.

4. Find the domain in the zone file.

5. Format the response, byte by byte (you may want to use Python's bytearray for that).

6. Return answer(s).

7. Pass all tests provided.

```
python3 -m pytest test_nameserver.py
```

8. Use your `resolver.py` or `nslookup` to resolve some somain name from the zone file. Note that you need to connect to port **43053** on your **localhost**.


## Usage example

Using `resolver.py` to resolve type **A** address.

```
> python3 resolver.py A ant.cs430.luther.edu 127.0.0.1
DNS server used: 127.0.0.1
Domain: ant.cs430.luther.edu
TTL: 3600
Address: 185.84.224.89
Domain: ant.cs430.luther.edu
TTL: 3600
Address: 199.83.67.158
```

Using `resolver.py` to resolve type **AAAA** address.

```
python3 resolver.py AAAA ant.cs430.luther.edu 127.0.0.1
DNS server used: 127.0.0.1
Domain: ant.cs430.luther.edu
TTL: 3600
Address: 4a9a:70ec:3ac0:c684:359e:8d37:9486:5959
```

Using `nslookup` to resolve type **A** address.

```
> nslookup -port=43053 -type=A ant.cs430.luther.edu 127.0.0.1
Server:		127.0.0.1
Address:	127.0.0.1#43053

Non-authoritative answer:
Name:	ant.cs430.luther.edu
Address: 185.84.224.89
Name:	ant.cs430.luther.edu
Address: 199.83.67.158
```

Using `nslookup` to resolve type **AAAA** address.

```
> nslookup -port=43053 -type=AAAA ant.cs430.luther.edu 127.0.0.1
Server:		127.0.0.1
Address:	127.0.0.1#43053

Non-authoritative answer:
Name:	ant.cs430.luther.edu
Address: 4a9a:70ec:3ac0:c684:359e:8d37:9486:5959
```

## Approach

* Look at a valid DNS response (eg. ping www.luther.edu and capture the traffic)

* Analyze the structure of a message (see the links below for details) and replicate it

## Functions

### val_to_bytes(value: int, n_bytes: int) -> list

`val_to_bytes` takes an integer and a number of bytes and returns that integer as a list of the specified length. Most fields in DNS response use 2 bytes, but TTL uses 4 bytes. Use shift (<<, >>) and masking (&) to generate the list.

### bytes_to_val(bytes_lst: list) -> int

`bytes_to_val` takes a list of bytes (values 0..255) and returns the value. Most values in DNS use 2 bytes, but you should implement a more generic algorithm to process a list of any length.

### get_left_bits(bytes_lst: list, n_bits: int) -> int

`get_left_bits` takes a 2-byte list and a number *n* and returns leftmost *n* bits of that sequence as an integer.

### get_right_bits(bytes_lst: list, n_bits: int) -> int

`get_right_bits` takes a 2-byte list and a number *n* and returns rightmost *n* bits of that sequence as an integer.

### read_zone_file(filename: str) -> tuple

`read_zone_file` takes file name as a parameter and reads the **zone** from that file. This function builds a dictionary of the following format: `{domain: [(ttl, class, type, address)]}` where each record is a list of tuples (answers). The function should return a tuple of `(origin, zone_dict)`. If the requested domain is not in our zon, `parse_request` should raise a `ValueError`. Note that the records in the zone file may be incomplete (missing a domain name or TTL). The missing domain name should be replaced with the one from the previous line, missing TTL should be replaced with the default one (2nd line of the zone file). If a record contains multiple answers, return them all.

### parse_request(origin: str, msg_req: bytes) -> tuple

`parse_request` takes `origin` and the request bytes and returns a tuple of (transaction id, domain, query type, query). The query is required as it is included in the response. This function must raise `ValueError`s if the type, class, or zone (origin) cannot be processed. Those exceptions are caught in the `run` function.

```
56 f0 01 00 00 01 00 00 00 00 00 00 06 6c 75 74 68 65 72 03 65 64 75 00 00 01 00 01
|---| |---| |---| |---| |---| |---| |------------------| |---------| || |---| |---| 
|id | |flags, # of questions etc  | | luther           | | edu     | \0 |typ| |cls|
                                    |------------------query----------------------|
```

### format_response(zone: dict, trans_id: int, qry_name: str, qry_type: int, qry: bytearray) -> bytearray

`format_response` takes the zone dictionary, transaction_id, domain name, and the query. It formats the DNS response (bytearray) based on those values and returns it to the calling function. Your should either *label* or *pointer* to format the domain name.

### run(filename: str) -> None

`run` is the main loop of the server and is implemented for your convenience.

## Resources

* [RFC 1034 - Domain names - concepts and facilities](https://tools.ietf.org/html/rfc1034)

* [RFC 1035 - Domain names - implementation and specification](https://tools.ietf.org/html/rfc1035)

* [The TCP/IP Guide - DNS Messaging and Message, Resource Record and Master File Formats](http://www.tcpipguide.com/free/t_DNSMessagingandMessageResourceRecordandMasterFileF.htm)

* [Chapter 15 DNS Messages](http://www.zytrax.com/books/dns/ch15/)

* [Domain Name System (DNS) Parameters](http://www.iana.org/assignments/dns-parameters/dns-parameters.xhtml)
