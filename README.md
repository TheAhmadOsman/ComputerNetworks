# Tracing the Route

Implement `traceroute` utility.

Language of implementation: any.

Use UDP (preferred) or ICMP (acceptable) socket to send probing messages to the specified host.

Display relevant statistics of the probe.

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

## References

* [Traceroute - Wikipedia](https://en.wikipedia.org/wiki/Traceroute)

* [traceroute(8) - Linux man page](https://linux.die.net/man/8/traceroute)

* [Linux Howtos: C/C++ -> Sockets Tutorial](http://www.linuxhowtos.org/C_C++/socket.htm)

* [Socket (Java SE 10 & JDK 10 )](https://docs.oracle.com/javase/10/docs/api/java/net/Socket.html)

* [socket — Low-level networking interface — Python 3.7.1 documentation](https://docs.python.org/3/library/socket.html)
