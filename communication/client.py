# ai-client

import socket
from queue import Queue

HOST = "127.0.0.1" # The server's IP adress
PORT = 65534 # The port used by the server

class Client:

    def __init__(self):
        """
        # AF_INET = Internet adress family for IPv4
        # SOCK_STREAM = socket type for TCP
        """
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bufsize = 2048
        self.data_queue = Queue()
        self.connect()

    def connect(self):
        self.s.connect((HOST, PORT))

    def send(self, data: str):
        self.s.send(bytes(data))

    def round_trip(self, data_in):
        self.send(data_in)
        data_out = self.s.recv(self.bufsize)
        self.data_queue.put(data_out)
        print(f"Received data from server.")

    def get_data(self):
        return self.data_queue.get()
