import paramiko
from socket import *
import threading
import sys

class Server(paramiko.ServerInterface):
    """Create an instance for bhSession.start_server method"""

    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chaid):
        """Check to see what kind of a request we get"""
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        """Check connection credentials provided by the client"""
        if username == "foo"  and password == "bar":
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

def serve_channel(chan, bhSession):
    """Send command line request to client"""
    print(chan.recv(1024))      # get client's connected header
    chan.send("Welcome to bh_ssh".encode()) # send welcome header

    try:
        while True:
            command = input("Enter command: ")
            if len(command) == 0:
                continue
            if command != "exit":
                chan.send(command)
                response = chan.recv(4096).decode()
                while response[-1] != "\n":
                    response += chan.recv(4096).decode()
                print(response)
            else:
                raise KeyboardInterrupt("exit")
    except KeyboardInterrupt:
        chan.send("exit")
        bhSession.close()
        print("[-] Session terminated")
        return

def start_session(client):
    """Start an ssh session"""

    server_key = paramiko.RSAKey(filename="test_rsa.key")
    bhSession = paramiko.Transport(client)

    bhSession.add_server_key(server_key)
    try:
        bhSession.start_server(server=Server())
    except:
        print("[-] SSH negotiation failed.")
        client.close()
        bhSession.close()
        return None, None

    chan = bhSession.accept(20)
    return chan, bhSession

def main(argc, argv):

    if argc != 3:
        print("Usage: %s <IPaddress> <PortNumber>" % argv[0])
        sys.exit(1)

    addr, port = argv[1], int(argv[2])

    print("[+] Initializing the server")

    try:
        server = socket(AF_INET, SOCK_STREAM, 0)
        server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        server.bind((addr, port))
        server.listen(100)
    except Exception as e:
        print(e)
        print("[-] Failed to initialize the server")
        sys.exit(1)

    try:
        while True:
            print("[+] Listening for connection requests")
            client, cli_addr = server.accept()
            print("[+] Got a connection from %s:%d" % cli_addr)
            chan, bhSession = start_session(client)
            if not chan or not bhSession:
                continue
            serve_channel(chan, bhSession)
            client.close()

    except KeyboardInterrupt:
        print("[+] Gracefully shutting down")

    sys.exit(0)


if __name__ == '__main__':
    main(len(sys.argv), sys.argv)    