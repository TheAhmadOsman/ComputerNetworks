# Custom dig

Complete the following programming project and push code to your GitHub repository.

**Process records of type A (IPv4) or AAAA (IPv6) only. If a server returns CNAME record instead, ignore it.**

Use *yahoo.com* as an example of a clean and simple response.

Read record type (**A** or **AAAA**), domain name, and an optional DNS server as parameters passed to your program.

```
python3 resolver.py A luther.edu 1.1.1.1
```
or
```
python3 resolver.py AAAA yahoo.com
```

1. Format a DNS request using the following values:

    * Transaction ID: auto-incremental or random
    * Flags: standard query (recursion bit set to 1, other bits are 0)
    * Questions: 1
    * Answer RRs: 0
    * Authority RRs: 0
    * Additional RRs: 0
    * Name: user-provided
    * Type: user-provided
    * Class: IN (0x0001)

2. If the DNS address is not specified, pick one of the well-known public servers.

3. Create a UDP socket connection and send the request to the DNS server.

4. Parse the response message from the DNS server to extract all addresses (there could be more than 1).

5. Print the address of the DNS server used.

6. Display the received information in the following format:

```
Name: <domain name>
TTL: record time-to-live
Addresses: <list of addresses received>
```

7. Pass all tests provided.

```
python3 -m pytest test_resolver.py
```

## Approach

* Look at a valid DNS request (eg. ping www.luther.edu and capture the traffic)

![DNS request](dns_query.png)

* Analyze the structure of a message (see the links below for details) and replicate it

![DNS request](dns_query_hex.png)

* Format your own message, byte by byte (you may want to use Python's bytearray for that)

* Make your client format a message based on user input (domain, record type)

* Send the message and receive the response

* Parse the response and present the result (IP address). Consider simple cases (domain - one or more address(es)), ignore complex paypal-like resolutions with multiple pseudos.

## Resources

* [RFC 1035 - Domain names - implementation and specification](https://tools.ietf.org/html/rfc1035)

* [The TCP/IP Guide - DNS Messaging and Message, Resource Record and Master File Formats](http://www.tcpipguide.com/free/t_DNSMessagingandMessageResourceRecordandMasterFileF.htm)

* [Chapter 15 DNS Messages](http://www.zytrax.com/books/dns/ch15/)

* [Domain Name System (DNS) Parameters](http://www.iana.org/assignments/dns-parameters/dns-parameters.xhtml)
