'''
GEO TCP Client
'''
#!/usr/bin/env python3

from socket import socket, AF_INET, SOCK_STREAM

HOST = 'localhost'
PORT = 4300


def client():
    '''Main client loop'''
    with socket(AF_INET, SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print('>You are connected to {}:{}'.format(HOST, PORT))
        country = input('>Enter a country or BYE to quit\n')
        while country.upper() != "BYE":
            s.sendall(country.encode())
            data = s.recv(1024)
            if data.decode() == "NOT FOUND":
                print("-There is no such country")                
            else:
                print('+{}'.format(data.decode()))
            country = input('>Enter another country to try again or BYE to quit\n')
        s.close()
        print('Connection ')

def main():
    '''Main function'''
    client()


if __name__ == "__main__":
    main()
