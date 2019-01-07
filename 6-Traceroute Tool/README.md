# Tracing the Route

Implement `traceroute` utility.

Language of implementation: any.

Use UDP (preferred) or ICMP (acceptable) socket to send probing messages to the specified host.

Display relevant statistics of the probe.

For you convenience, lines of Python implementation are provided.

## C++

```
g++ --std=gnu++14 traceroute.cpp -o traceroute.out
./traceroute.out example.com
```

## Java

```
javac Traceroute.java
java Traceroute example.com
```

## Python

```
python3 traceroute.py example.com
```

### Functions

* `print_raw_bytes`: takes *packet* as an argument and prints prints all the bytes as hexadecimal values.

* `checksum`: takes *packet* as an argument and returns its Internet **checksum**.

* `format_request`: takes *ICMP type*, *ICMP code*, *request ID*, and *sequence number* as arguments and returns a properly formatted **ICMP request packet** with current time as *data*. This function has to compute the packet's *checksum* and add it to the header of the outgoing message.

* `send_request`: takes *packet* bytes, *destination address*, and *Time-to-Live* value as arguments and returns a new **raw socket**. This function sets the socket's time-to-live option to the supplied value. 

* `receive_reply`: takes a *socket* and *timeout* as arguments and returns a tuple of the **received packet** and the **IP address** of the responding host. This function uses `select` and may raise a `TimeoutError` is the response does not come soon enough.

* `parse_reply`: takes a *packet* as an argument and returns `True` if it is a valid (expected) response. This function parses the response header and verifies that the *ICMP type* is 0, 3, or 11. It also validates the response checksum and raises a `ValueError` if it's incorrect.

* `traceroute`: takes *host* (domain) name as an argument and traces a path to that host. The general approach is to have a big loop that sends *ICMP Echo Request* messages to the host, incrementally increasing TTL value. Each iteration of this loop generates ATTEMPTS (3) messages. There are two possible sources of errors: `Timeout` (response was not received within **timeout**) and `Value` (something is wrong with the response). For each attempts you should do the following:
    1. Format an ICMP Request
    2. Send the request to the destination host
    3. Receive a response (may or may not be a proper ICMP Reply)
    4. Parse the response and check for errors
    5. Print the relevant statistics, if possible
    6. Print the error message, if any
    7. Stop the probe after MAX_HOPS attempts or once a response from the destination host is received

* `main`: takes command line arguments and starts the probe.


## References

* [Traceroute - Wikipedia](https://en.wikipedia.org/wiki/Traceroute)

* [traceroute(8) - Linux man page](https://linux.die.net/man/8/traceroute)

* [Linux Howtos: C/C++ -> Sockets Tutorial](http://www.linuxhowtos.org/C_C++/socket.htm)

* [Socket (Java SE 10 & JDK 10 )](https://docs.oracle.com/javase/10/docs/api/java/net/Socket.html)

* [socket — Low-level networking interface — Python 3.7.1 documentation](https://docs.python.org/3/library/socket.html)
