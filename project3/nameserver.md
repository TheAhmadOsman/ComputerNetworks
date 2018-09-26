# Custom BIND

Complete the following programming project and push code to your GitHub repository.

**Process records of type A (IPv4) or AAAA (IPv6) only. If a client requests anything else, ignore it.**

Use your custom DNS resolver to initiate requests to this server.

```
python3 nameserver.py zoo.zone
```

1. Read the zone file *zoo.zone* and build a dictionary of domain names.

2. Listen on port 43053 (set Wireshark to recognize such messages as DNS).

3. Create a UDP socket connection and wait for a message from the DNS resolver.

4. Parse the DNS request.

5. Find the domain in the zone and return its address(es) (IPv4 or IPv6, and TTL).

6. Pass all tests provided.

```
python3 -m pytest test_nameserver.py
```

## Approach

* Parse the request

* Format the response, byte by byte (you may want to use Python's bytearray for that)

## Resources

* [RFC 1035 - Domain names - implementation and specification](https://tools.ietf.org/html/rfc1035)

* [The TCP/IP Guide - DNS Messaging and Message, Resource Record and Master File Formats](http://www.tcpipguide.com/free/t_DNSMessagingandMessageResourceRecordandMasterFileF.htm)

* [Chapter 15 DNS Messages](http://www.zytrax.com/books/dns/ch15/)

* [Domain Name System (DNS) Parameters](http://www.iana.org/assignments/dns-parameters/dns-parameters.xhtml)
