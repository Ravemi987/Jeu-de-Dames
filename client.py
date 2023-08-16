# ai-client

import socket
from queue import Queue
import pickle
import sys

HEADER_SIZE = 10
PORT = 5050
HOST = socket.gethostbyname(socket.gethostname())
ADDR = (HOST, PORT)
FORMAT = 'utf-8' 


class Client:
    """
    Le client est utilisé pour envoyer à un serveur l'état du jeu à un moment donné. 
    Lorsque c'est au tour de l'IA, le client sérialise une copie de l'objet 'game'. 
    Il calcule la taille des données à envoyer et envoie un premier message de taille HEADER_SIZE au serveur, 
    message contenant la taille des informations à founir. On dit qu'on utilise un protocol header. 
    Le serveur pourra ensuite lire la taille des prochaines données qui arrive car il connaît lui aussi HEADER_SIZE
    Ainsi, il pourra récupérer la totalité de l'objet 'game' en une seule fois, sans perte de packets.
    De la même manière, le serveur renvoie un objet 'move' récupéré par le client.
    """

    def __init__(self):
        """
        # AF_INET = Internet adress family for IPv4
        # SOCK_STREAM = socket type for TCP
        """
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.data_queue = Queue()

        try:
            self.client.connect(ADDR)
        except ConnectionRefusedError as err:
            print(f"Connection refused because server is offline.\n{err}")
            sys.exit(1)

    def send(self, data: object):
        """ 
        Envoie une instance de la classe Game.
        Reçoit une instance de la classe Move
        """
        try:
            data_output = pickle.dumps(data) # sérialisation
        except OSError as err:
            print(f"Can't pickle data.\n{err}")
            sys.exit(87)

        send_data_length = len(data_output) # longueur en octets
        send_header = str(send_data_length).encode(FORMAT) # encodage
        send_header += b' ' * (HEADER_SIZE - len(send_header)) # complétion
        try:
            self.client.send(send_header) # Envoi du header 
        except OSError as err:
            print(f"Can't send header because server has been closed.\n{err}")
        self.client.send(data_output) # Envoi des données
        
        try:
            recv_header = self.client.recv(HEADER_SIZE).decode(FORMAT) # reception du header
        except OSError as err:
            print(f"Header can't be received.\n{err}")
            sys.exit(89)

        if recv_header: # != None
            recv_data_length = int(recv_header) # on récupère la longueur des données suivantes
            try:
                data_input = pickle.loads(self.client.recv(recv_data_length)) # on récupère les données
            except OSError as err:
                print(f"No data can be received.\n{err}")
                sys.exit(88)

            if data_input:
                self.data_queue.put(data_input) # On met les données dans la file
    
    def get_data(self):
        """ Retourne le dernier élément de la file. """
        return self.data_queue.get()
