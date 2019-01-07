'''
GEO TCP Server
'''
#!/usr/bin/env python3

from socket import socket, AF_INET, SOCK_STREAM
import time

FILE_NAME = 'geo_world.txt'
HOST = 'localhost'
PORT = 4300


def read_file(filename: str) -> dict:
    '''Read world territories and their capitals from the provided file'''
    world = dict()

    print(time.strftime('%H:%M:%S Reading a file'))
    
    t = time.process_time()
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            line = line.split('-')
            world[line[0].strip()] = line[1].strip()
    elapsed_time = time.process_time() - t
    
    print(time.strftime('%H:%M:%S'), "Read in {0:.5f}".format(elapsed_time), "sec")

    return world


def server(world: dict) -> None:
    '''Main server loop'''
    with socket(AF_INET, SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        print(time.strftime('%H:%M:%S'), 'Listening on {}:{}'.format(HOST, PORT))
        conn, addr = s.accept()
        with conn:
            print(time.strftime('%H:%M:%S'), 'Connected: {}'.format(addr[0]))
            while True:
                data = conn.recv(1024)
                if not data:
                    print(time.strftime('%H:%M:%S'), 'Disconnected: {}'.format(addr[0]))
                    break
                country = data.decode()
                print(time.strftime('%H:%M:%S'), 'User Query: {}'.format(country))
                if country in world:
                    conn.sendall(world[country].encode('utf-8'))
                else:
                    conn.sendall("NOT FOUND".encode('utf-8'))


def main():
    '''Main function'''
    world = read_file(FILE_NAME)
    server(world)


if __name__ == "__main__":
    main()
