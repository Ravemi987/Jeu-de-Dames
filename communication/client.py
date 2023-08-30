# ai-client

import socket
from queue import Queue
import pickle
import sys

from .network_constants import *
from ai_package.ai import AI


class Client:
    """
    Le client est utilisé pour envoyer à un serveur l'état du jeu à un moment donné. 
    Lorsque c'est au tour de l'IA, le client sérialise une copie de l'objet 'game'. 
    Il calcule la taille des données à envoyer et envoie un premier message de taille HEADER_SIZE au serveur, 
    message contenant la taille des informations à founir. 
    Le serveur pourra ensuite lire la taille des prochaines données qui arrive car il connaît lui aussi HEADER_SIZE
    Ainsi, il pourra récupérer la totalité de l'objet 'game' en une seule fois, sans perte de packets.
    De la même manière, le serveur renvoie un objet 'move' récupéré par le client.
    """

    def __init__(self):
        """
        # AF_INET = Internet adress family for IPv4
        # SOCK_STREAM = socket type for TCP
        """
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.data_queue = Queue()
        self.close_connection = False

        try:
            self.client_socket.connect(ADDR)
        except ConnectionRefusedError as err:
            print(f"Connection refused because server is offline.\n{err}")
            sys.exit(1)

    def throw_error(self, msg):
        """ Affiche un message et ferme la connexion en cas d'erreurs. """
        print(f"[CLIENT ERROR] {msg}")
        self.client_socket.close()

    def send(self, data: object):
        """ Envoi des données au serveur. """
        try:
            data_output = pickle.dumps(data) # sérialisation
        except OSError as err:
            self.throw_error(f"Can't pickle data.\n{err}")

        send_data_length = len(data_output) # longueur en octets
        send_header = str(send_data_length).encode(FORMAT) # encodage
        send_header += b' ' * (HEADER_SIZE - len(send_header)) # complétion

        try:
            self.client_socket.send(send_header) # Envoi du header 
            self.client_socket.send(data_output) # Envoi des données
        except OSError as err:
            print("Server has been closed.")
            self.close()

    def apply_protocol(self, data: object):
        """ 
        Envoie une instance de la classe Game.
        Reçoit une instance de la classe Move
        """
        self.send(data)

        try:
            recv_header = self.client_socket.recv(HEADER_SIZE).decode(FORMAT) # reception du header

            if recv_header: # != None
                recv_data_length = int(recv_header) # on récupère la longueur des données suivantes
                data_input = pickle.loads(self.client_socket.recv(recv_data_length)) # on récupère les données
                if data_input:
                    self.data_queue.put(data_input) # On met les données dans la file
        except OSError:
           print("Server has been closed.")
           self.close()

    def send_ai(self, ai_list: list[AI], ai_switch: bool):
        """ 
        Première étape du protocol de communication:
        On envoie la liste des IA qui vont être utilisées et le booléen représentant
        le mode de jeu. Le serveur pourra ainsi changer d'IA à chaque tour ou bien
        jouer la même IA toute la partie.
        """
        data = (ai_list, ai_switch)
        self.send(data)

    def get_queue(self):
        """ Retourne la file. """
        return self.data_queue
    
    def get_data(self):
        """ Retourne le dernier élément de la file. """
        return self.data_queue.get()
    
    def close(self):
        """ Ferme la connexion du client. """
        self.close_connection = True
        self.client_socket.close()

    def is_close(self):
        return self.close_connection
