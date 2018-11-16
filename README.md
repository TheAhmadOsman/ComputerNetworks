# Router
*This is the first draft of the final project description. Source file(s) will be posted at a later date.*

In this project you will be writing a set of procedures to implement a distributed asynchronous distance-vector routing protocol. Eventually we'll try to make all the routers work together in the lab environment. In order to achieve general compatibility, it's mandatory that you use Python 3 for the implementation.

I recommend you implement your router application in stages, from a basic socket application to a full-fledged router.

This is going to be a challenging project, not only in the sense of correctly implementing the distance-vector routing algorithm but also because your program must handle multiple connections that will operate asynchronously. There are several approaches to correctly deal with a bunch of asynchronous sockets, we are going to use the Python `select` method. The `select` method takes three lists, (sockets I want to read from, sockets I want to write to, sockets that might have errors) and checks all of the sockets lists. When the function returns (either right away, or after a set time), the lists you passed in will have been transformed into lists of sockets that you may want to read, write or check for errors respective. You can be assured that when you make a read or write call, the call will not block.

I would strongly suggest that you take the time to write yourself a high-level design for this project before you start to write code. You may also find it useful to write a simple little server program that keeps multiple connections active and adds messages to a queue. Doing something very simple like this is a good way to learn and check out the problems you are likely to run into with asynchronous communications before you get mired in the whole distance-vector routing.

## Stage 1: Read the Configuration File

We start with a simple application that reads a router's configuration from a text file, displays its status (neighbors and cost of getting to them), and starts listening for incoming UDP connections on port 4300. The configuration contains names of your directly connected neighbors and the cost to reach those neighbors.

You should write 4 (almost) identical files, each one for a different address (127.0.0.x). By the end of the project you should be able to test your routers locally, at the very least.

## Configuration file format

```
<Router 1 IP address>
<Neighbor 1 IP address> <Neighbor 1 cost>
<Neighbor 2 IP address> <Neighbor 2 cost>
<blank line>
<Router 2 IP address>
<Neighbor 1 IP address> <Neighbor 1 cost>
<Neighbor 2 IP address> <Neighbor 2 cost>
<Neighbor 3 IP address> <Neighbor 3 cost>
```

File *network_simple.txt* represents the following network:

![Simple network](network_simple.png)

network_simple.txt
```
127.0.0.1
127.0.0.2 1
127.0.0.3 3
127.0.0.4 7

127.0.0.2
127.0.0.1 1
127.0.0.3 1

127.0.0.3
127.0.0.1 3
127.0.0.2 1
127.0.0.4 2

127.0.0.4
127.0.0.1 7
127.0.0.3 2
```

### Stage 1 Functionality

1. Read the configuration file
2. Pick an appropriate address
3. Display the chosen router's neighborhood (names and costs)
4. Start listening on UDP port 4300

## Stage 2: Close Encounters of the Third Kind

Your program must connect to the IP addresses specified in the configuration file. Your client should accept a path to the configuration file as a command line argument so that we can try out a couple of different configurations. Note that in order to bootstrap the network you are going to need to have your program retry connections that fail.

Your program must also accept incoming IP connections from neighbors which may inform you of a link cost change, or may ask you to deliver a message to a particular IP address.

Our protocol will use two types of messages: **UPDATE (0)** and** DELIVERY (1)**. You should use `bytearray` or `struct` to format and parse messages.

### UPDATE message format

* The first byte of the message (0): 0

* Next four bytes (1-4): IP address

* The next byte (5): cost

* The same pattern (IP address followed by cost) repeats. 

### DELIVERY message format

* The first byte of the message (0): 1

* Next four bytes (1-4): source IP address

* Next four bytes (5-8): destination IP address

* The rest of the message (9+): text (characters)

### Event loop

1. Do we have pending connections?

    1. accept new connections

    2. add to the listener list

    3. add IP addresses to the neighbor list

2. Process incoming messages

    1. if UPDATE then update my routing table.

    2. Does my vector change?  If so, then set flag to update_vector

    3. if DELIVERY, then lookup who it should be passed on to

    4. Does my vector change?  If so, then set flag to update_vector

3. Is update_vector flag set?

    1. send the new vector to all neighbors that can accept data

4. Check my neighbor list against the list of currently connected neighbors

    1. if I'm missing neighbors then try to initiate connections to them.

    2. If I'm successful then add the new neighbor to list

    3. send the new neighbor my distance vector.

### Stage 2 Functionality

1. Read the configuration file name as a command line parameter
2. Read the neighborhood information from the configuration file
3. Send a router's table to all neighbors
4. Receive updates from the neighbors
5. Keep listening and be ready to update the routing table

## Stage 3: Routing

Write the following routing functions.

* Read a configuration file for your specific router and add each neighbor to a set of neighbors.

* Build an initial routing table as a dictionary with nodes as keys. Dictionary values should be a distance to the node and the next hop address. Initially, the dictionary must contain your neighbors only.

```python
{'destination':[cost, 'next_hop']}
```

* Format the update message based on the values in the routing table and return the message. For example, a message advertising routes to **127.0.0.1** of cost **10** and to **127.0.0.2** of cost **5** is the following `bytearray`:

```
0x0 0x7f 0x0 0x0 0x1 0xA 0x7f 0x0 0x0 0x2 0x5
```

* Parse the update message and return `True` if the table has been updated. The function must take a message (raw bytes) and the neighbor's address and update the routing table, if necessary.

* Print current routing table. The function must print the current routing table in a human-readable format (rows, columns, spacing).

* Parse a message to deliver. The function must parse the message and extract the destination address. Look up the destination address in the routing table and return the next hop address.

* Router works with properly implemented routers of other students.
