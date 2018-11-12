# The Story about Ping

Implement a *ping* application using ICMP request and reply messages. You have to use Python's *RAW* sockets to properly send ICMP messages. You should complete the provided ping application so that it sends 10 Echo requests to each RIR (ARIN, RIPE, LACNIC, AFRINIC, APNIC), 1 request every second. Each message contains a payload of data that includes a timestamp. After sending each packet, the application waits up to one second to receive a reply. If the one-second timer expires, assume the packet is lost or the server is down. Report the following statistics for each host:

* packet loss
* maximum round-trip time
* minimum RTT
* average RTT

## Code notes

You need to receive the structure ICMP_ECHO_REPLY and fetch the information you need, such as checksum, sequence number, time to live (TTL), etc.

This application requires the use of raw sockets. You may need administrator/root privileges to run your program.

When running this application as a root, make sure to use `python3`.

### Functions

* `checksum`: calculates packet checksum. Can be used without modifications.

* `receive_a_ping`: receives and processes and echo reply.

* `send_a_ping`: formats and send echo request.

* `do_a_ping`: creates a socket and uses `send_a_ping` to actually send the message. Can be used without modifications.

* `ping`: main loop. Can be used without modifications.

## References

* [socket — Low-level networking interface — Python 3.7.1 documentation](https://docs.python.org/3/library/socket.html)

* [https://sock-raw.org/papers/sock_raw](https://sock-raw.org/papers/sock_raw)

* [TCP/IP Raw Sockets | Microsoft Docs](https://docs.microsoft.com/en-us/windows/desktop/WinSock/tcp-ip-raw-sockets-2)

* [Converting between Structs and Byte Arrays – GameDev<T>](http://genericgamedev.com/general/converting-between-structs-and-byte-arrays/)

* [select — Waiting for I/O completion — Python 3.7.1 documentation](https://docs.python.org/3/library/select.html)

* [How to Work with TCP Sockets in Python (with Select Example)](https://steelkiwi.com/blog/working-tcp-sockets/)

* [select — Wait for I/O Efficiently — PyMOTW 3](https://pymotw.com/3/select/)
