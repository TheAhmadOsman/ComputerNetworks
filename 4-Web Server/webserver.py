"""Python Web server implementation"""
from socket import socket, AF_INET, SOCK_STREAM
from datetime import datetime

server = socket(AF_INET, SOCK_STREAM)

ADDRESS = "127.0.0.2"  # Local client is going to be 127.0.0.1
PORT = 4300  # Open http://127.0.0.2:4300 in a browser
LOGFILE = "webserver.log"

def read_file(filename: str) -> str:
    '''Read file and return String object'''
    strObj = ""

    with open(filename, 'r') as f:
        strObj = f.read()

    return strObj

def serve(strObj: str, request_type: str, request_uri: str) -> None:
    '''Serving content'''
    
    server.bind((ADDRESS, PORT))
    server.listen(1)

    with server:
        # Server loop - this will keep the server going until we close it ourselves!
        while True:
            conn, addr = server.accept()
            print("Connection Opened...")
            with conn:
                data = conn.recv(1024)
                if not data:
                    print("Connection Closed.")
                    continue

                # Getting request decoded
                request = data.decode()
                r_lst = request.splitlines()
                query = r_lst[0].split()
                qtype, quri = query[0], query[1]
                r_lst = [s.split(": ") for s in r_lst[1:]]
                r_dct = {}
                for element in r_lst:
                    try:
                        r_dct[element[0]] = element[1]
                    except:
                        continue
                
                rsp = []

                with open(LOGFILE, "a+") as f:
                    f.write(str(datetime.isoformat(datetime.now()).replace('T', ' ')) + \
                        " | " + quri  + " | " + str(addr[0]) + " | " + r_dct["User-Agent"] + '\n') 

                # Checking for errors and encoding the sent data
                error = True
                if qtype != request_type:
                    msg = "405 Method Not Allowed\n"
                    strE = msg.encode()
                    rsp.append("HTTP/1.1 405 Method Not Allowed")
                elif quri != request_uri:
                    msg = "404 Not Found"
                    strE = msg.encode()
                    rsp.append("HTTP/1.1 404 Not Found")
                else:
                    error = False
                    strE = strObj.encode()
                    rsp.append("HTTP/1.1 200 OK")

                # Building response header
                rsp.append(("Content-Length: " + str(len(strE))))
                rsp.append("Content-Type: text/plain; charset=utf-8")
                rsp.append(("Date: " + datetime.now().strftime("%c")))
                if error:
                    rsp.append("Last-Modified: " + datetime.now().strftime("%c"))
                else:
                    rsp.append("Last-Modified: Wed Aug 29 11:00:00 2018")
                rsp.append("Server: CS430-Ahmad M. Osman")
                rsp.append("\n")
                rsp = '\n'.join(rsp)

                # try/except in case of a broken pipe!
                try:
                    conn.sendall(rsp.encode())
                    conn.sendall(strE)
                except:
                    pass
            print("Connection Closed.")

def alice():
    """Serve Alice in Wonderland"""
    alice = read_file("alice30.txt")
    serve(alice, "GET", "/alice30.txt")


def main():
    """Main server loop"""
    alice() # Serving Alice!


if __name__ == "__main__":
    main()
