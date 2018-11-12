"""Python Web server implementation"""
from socket import socket, AF_INET, SOCK_STREAM
from datetime import datetime
import sys

server = socket(AF_INET, SOCK_STREAM)

ADDRESS = "127.0.0.1"  # Local client is going to be 127.0.0.1
PORT = 4300  # Open http://127.0.0.2:4300 in a browser
LOGFILE = "webserver.log"

def read_file(filename: str) -> str:
    '''Read file and return String object'''
    strObj = ""

    with open(filename, 'r') as f:
        strObj = f.read()

    return strObj

def serve(strObj: str) -> None:
    '''Main server loop'''
    
    server.bind((ADDRESS, PORT))
    server.listen(1)
    
    with server:
        while True:
            conn, addr = server.accept()
            print("Connection Opened...")
            with conn:
                data = conn.recv(1024)
                # do we need to deal with multiple requests?
                if not data:
                    print("Connection Closed.")
                    
                    """
                    ['GET /alice30.txt HTTP/1.1\r', 'Host: 127.0.0.1:4300\r', 'Connection: keep-alive\r', 'Upgrade-Insecure-Requests: 1\r', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36\r', 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8\r', 'Accept-Encoding: gzip, deflate, br\r', 'Accept-Language: en-US,en;q=0.9,ar;q=0.8\r', '\r', '']
                    """

                    request = data.decode()
                    rlst = request.split()
                    query = rlst[0].split(' ')
                    qtype = query[0]
                    qdoc = query[1]
                    qver = query[2]
                    host = rlst[1]
                    useragent = rlst[2]

                    
                    # conn.sendall(strObj.encode())

def alice():
    """Serve Alice in Wonderland"""
    alice = read_file("alice30.txt")
    serve(alice)


def main():
    """Main server loop"""
    alice() # Serving Alice!


if __name__ == "__main__":
    main()
