# RePyX
# Readable Python eXecutor

import inspect
import socket
import time
import sys
import os

from traceback import format_exc
from threading import Thread

def runCmd(cmd: str) -> str:

    if cmd.startswith("exec "):
        try:
            return exec(cmd[5:], globals()) or ""
        except Exception:
            return format_exc()
        
    try:
        return str(eval(cmd))
    except Exception:
        return format_exc()


class Server:

    def __init__(self, ip="127.0.0.1", port=1337, readLen=1024):

        self.ip      = ip
        self.port    = port
        self.socket  = None
        self.clients = []
        self.readLen = readLen


    def accepter(self):
        # loop to continuously accept new incoming connections
        
        connected = False
        shutup = False

        while not connected:

            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.bind((self.ip, self.port))
                self.socket.listen(5) # https://docs.python.org/3/library/socket.html#socket.socket.listen

                print("repyx: receiver started") # redundant new line for thread friendlier printing
                connected = True

            except OSError:
                if not shutup:
                    print("repyx: Address already in use. Retrying indefinitely...", retryCount)
                    shutup = True
                time.sleep(4)

        while True:
            try:
                client, address = self.socket.accept()
                self.clients.append(client)
                
                client.send(b"Connected to JC")

                print(f"repyx: Connection from {address} has been accepted.")
                self.threcver(client)

            except OSError:
                # from previous testing, "self.socket.accept()" throws an OSError
                # when the socket is shutdown, so we want to exit quietely.
                pass


    def start(self):
        Thread(target=self.accepter, daemon=True).start()


    def recver(self, client: socket.socket):
        while True:
            try:
                received = client.recv(self.readLen)

                if received:

                    try: returnVal = runCmd(received.decode())    

                    except Exception:
                        client.send(b"Decode error.")
                        continue
                    
                    try: client.send(returnVal.encode())

                    except Exception as e:
                        client.send(b"Encode error.")
                    
            except Exception as e:
                try: peername = client.getpeername()
                except Exception: peername = client

                print(f"repyx: Error trying to receive from {peername}. Stopping receiver.")
                try: self.clients.remove(client)
                except Exception: pass
                try: client.close()
                except Exception: pass

                return
            

    def threcver(self, socket):
        Thread(target=self.recver, args=[socket], daemon=True).start()
        # TODO: Make this thread killable in the case where the client accidentally runs an endless loop
        # ^ https://stackoverflow.com/a/325528



class Client:

    def __init__(self, ip="127.0.0.1", port=1337, readLen=1024):

        self.ip      = ip
        self.port    = port
        self.readLen = readLen

        self.server: socket.socket

    
    def connect(self):
        connected = False
        retryCount = 0

        while not connected:
            try:
                self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server.connect((self.ip, self.port))

                print("connected\n")
                connected = True

            except ConnectionRefusedError as error:
                print("Address already in use. Waiting 4 seconds.", retryCount)
                retryCount+=1
                time.sleep(4)

        Thread(target=self.recver, daemon=True).start()

    
    def recver(self):
        while True:
            try:
                received = self.server.recv(self.readLen)

                if received:

                    try: decoded = received.decode()

                    except Exception:
                        self.server.send(b"repyx: Decode error.")
                        print(received)
                        continue
                    
                    print(decoded)
                    
            except Exception as e:
                try: peername = self.server.getpeername()
                except Exception: peername = None

                if self.server: print(f"Error trying to receive from {peername}. Stopping receiver.")
                else: print(f"Encountered error in receiver: {str(e)}")
                
                self.server.close()
                return
            

    def sendCmd(self, cmd: str) -> None:
        try: cmd = cmd.encode()
        except Exception:
            return print("Could not encode cmd.")
        
        self.server.send(cmd)


    @staticmethod
    def _printJC():
        def _a():
            time.sleep(0.01)
            print("JC: ", end="")
            sys.stdout.flush()

        Thread(target=_a, daemon=True).start()


    def start(self):
        while True:
            self._printJC()
            cmd = input()
            
            if cmd == "exit":
                return print("Exiting JC.")
            
            self.sendCmd(cmd)


# here we perform logic to detect if AutoStart has been explicity imported I.E 
# "from repyx import AutoStart" as opposed to "import repyx" or "from repyx import Server"

class AutoStart: pass
# I chose to use a class here arbitrarily, any type of variable should work really

stacks = inspect.stack()

def _autoStart():
    global stacks
    time.sleep(1)
    
    for frame in stacks:
        
        if os.path.basename(__file__) in frame.filename:
            # exclude occurrences of AutoStart in this file (stack)
            continue
        
        if "AutoStart" in frame.frame.f_globals.keys():
            if frame.frame.f_globals["AutoStart"] is AutoStart:
                # there seems to be 2 stacks with the same globals,
                # so in my case the code here gets run twice
                print("repyx: Auto starting...")
                s = Server()
                s.start()
                return


Thread(target=_autoStart).start()
