'''
GEO TCP Server
'''
#!/usr/bin/env python3

from socket import socket, AF_INET, SOCK_STREAM

FILE_NAME = 'geo_world.txt'
HOST = 'localhost'
PORT = 4300


def read_file(filename: str) -> dict:
    '''Read world territories and their capitals from the provided file'''
    world = dict()
    return world


def server(world: dict) -> None:
    '''Main server loop'''
    # TODO: Implement server-side tasks
    pass


def main():
    '''Main function'''
    world = read_file(FILE_NAME)
    server(world)


if __name__ == "__main__":
    main()
