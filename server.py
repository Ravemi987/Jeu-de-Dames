# ai-server

import socket
import threading
import pickle
import pygame
import sys

from ai_package.ai import AI
from ai_package import random_ai
from ai_package import minimax
from ai_package import alphabeta

HEADER_SIZE = 10
PORT = 5050
HOST = socket.gethostbyname(socket.gethostname())
ADDR = (HOST, PORT)
FORMAT = 'utf-8' 


class Server:
    """
    Le serveur est utilisé pour recevoir et traiter les données envoyées par le client
    à un moment donner. Lorsque c'est au tour de l'IA, le client envoie un copie de l'objet 'game'.
    Avant ça, il envoie la taille de ce transfère en octet.
    Le serveur récupère les données maintenant qu'il connaît la taille pour effectuer le transfère en
    une seule fois. Il utilise les algorithmes d'IA qui lui sont fournies pour renvoyer un objet de type Move 
    au client qui gère également l'interface graphique et appliquera le déplacement choisi par l'ordi.
    """

    def __init__(self, ai: AI):
        """
        # AF_INET = Internet adress family for IPv4
        # SOCK_STREAM = socket type for TCP
        """
        self.ai = ai
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(ADDR)
        self.start()

    def start(self):
        """ Démarre et met le serveur sur écoute. """
        self.server.listen()
        print(f"[LISTENING] Server is listening on {HOST}")
        while True:
            # conn is a new socket object representing the connection.
            conn, addr = self.server.accept() # blocking
            thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}")

    def handle_client(self, conn: socket.socket, addr):
        """
        Reçoit une instance de la classe Game.
        Renvoi une instance de la classe Move.
        """
        print(f"[NEW CONNECTION] {addr} connected.")
        
        connected = True
        while connected: # Tant que le client est connecté
            try:
                # conn.recv est une méthode bloquante
                recv_header = conn.recv(HEADER_SIZE).decode(FORMAT) # reception du header
            except OSError as err:
                print(f"Header can't be received.\n{err}")
                sys.exit(99)
        
            if recv_header: # != None
                recv_data_length = int(recv_header) # on récupère la longueur des données suivantes
                try:
                    data_input = pickle.loads(conn.recv(recv_data_length)) # on récupère les données
                except OSError as err:
                    print(f"No data can be received.\n{err}")
                    sys.exit(98)
                if not data_input: connected = False

                print(f"[{addr}] : {data_input}")

                # Traitement des données
                data_output = self.ai.engine(data_input, 5, float('-inf'), float('+inf'), True)
                
                # Renvoi des données
                try:
                    data_output = pickle.dumps(data_output) # sérialisation
                except OSError as err:
                    print(f"Can't pickle object.\n{err}")
                    sys.exit(97)

                send_data_length = len(data_output) # longueur en octets
                send_header = str(send_data_length).encode(FORMAT) # encodage
                send_header += b' ' * (HEADER_SIZE - len(send_header)) # complétion
                conn.send(send_header) # Envoi du header 
                conn.send(data_output) # Envoi des données
        
        conn.close()


server = Server(AI(alphabeta.AlphaBeta, 'black'))
