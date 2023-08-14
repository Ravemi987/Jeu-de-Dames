# ai-server

import socket

HOST = "127.0.0.1" # Standart loopback interface adress
PORT = 65534 # Port to listen on

class Server:

    def __init__(self):
        """
        # AF_INET = Internet adress family for IPv4
        # SOCK_STREAM = socket type for TCP
        """
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bufsize = 2048
        self.bind()
        self.listen()
        self.check_connection()
        self.round_trip_loop()

    def bind(self):
        self.s.bind((HOST, PORT))

    def listen(self):
        self.s.listen()
        print("Waiting for data...")

    def check_connection(self):
        """ conn is a new socket object representing the connection. """
        self.conn, self.addr = self.s.accept()
        print(f"Connected by {self.addr}")

    def round_trip_loop(self):
        while True:
            data_in = self.conn.recv(self.bufsize)
            if not data_in:
                break
            ai_engine = data_in[0]
            self.conn.send(eval(ai_engine)(*data_in[1::]))

server = Server()
