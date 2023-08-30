# ai-server

import time
import socket
import threading
import pickle
import signal
import sys

from .network_constants import *
from ai_package.ai import AI


class Server:
    """
    Le serveur est utilisé pour recevoir et traiter les données envoyées par le client
    à un moment donner. Lorsque c'est au tour de l'IA, le client envoie un copie de l'objet 'game'.
    Avant ça, il envoie la taille de ce transfère en octet.
    Le serveur récupère les données maintenant qu'il connaît la taille pour effectuer le transfère en
    une seule fois. Il utilise les algorithmes d'IA qui lui sont fournies pour renvoyer un objet de type Move 
    au client qui gère également l'interface graphique et appliquera le déplacement choisi par l'ordi.
    """

    def __init__(self):
        """
        # AF_INET = Internet adress family for IPv4
        # SOCK_STREAM = socket type for TCP
        """
        self.ai_index = 0
        self.ai_list: list[AI] = []
        self.current_ai: AI = None
        self.is_server_running = True
        self.number_of_connections = 0
        self.threads: list[threading.Thread] = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(ADDR)

    def running_thread(self):
        while self.is_server_running:
            # conn is a new socket object representing the connection.
            try:
                conn, addr = self.server_socket.accept() # blocking
                thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                thread.daemon = True
                thread.start()
                self.threads.append(thread)
                self.number_of_connections = threading.activeCount() - 2
                print(f"[ACTIVE CONNECTIONS] {self.number_of_connections}")
            except OSError:
                self.is_server_running = False

    def start(self):
        """ Démarre et met le serveur sur écoute. """
        self.server_socket.listen()
        print(f"[LISTENING] Server is listening on {HOST}")

        running_thread = threading.Thread(target=self.running_thread)
        running_thread.daemon = True
        running_thread.start()
        self.threads.append(running_thread)

        #Gestionnaire de signal
        signal.signal(signal.SIGTERM, self.shutdown_server)
        signal.signal(signal.SIGINT, self.shutdown_server)

        while self.is_server_running: continue

    def shutdown_server(self, signum, frame):
        """ 
        Méthode appelée quand l'un des signaux pour fermer
        manuellement le serveur est reçu. Elle permet un arrêt propre.
        TODO: enlver les threads daemons et fermer proprement tous les threads
        """
        print("Server is shutting down...")
        self.is_server_running = False
        print(f"Current threads: {self.threads}")
        self.server_socket.close()
        print("Done.")
        sys.exit()

    def handle_client(self, conn: socket.socket, addr):
        """
        Reçoit une instance de la classe Game.
        Renvoi une instance de la classe Move.
        """
        print(f"[NEW CONNECTION] {addr} connected.")
        
        # On reçoit les IA qui vont être joué et le mode de jeu.
        self.ai_list, can_switch = self.recv_ai(conn, addr)
        self.current_ai: AI = self.ai_list[0]

        try:
            while True: # Tant que le client est connecté
                # conn.recv est une méthode bloquante
                recv_header = conn.recv(HEADER_SIZE).decode(FORMAT) # reception du header
                if not recv_header:
                    break
            
                recv_data_length = int(recv_header) # on récupère la longueur des données suivantes
                try:
                    data_input = pickle.loads(conn.recv(recv_data_length)) # on récupère les données
                except OSError as err:
                    print(f"[ERROR] No data can be received.\n{err}")
                    break

                # Traitement des données
                move = self.current_ai.choose_move(data_input, addr)

                # Renvoi des données
                try:
                    data_output = pickle.dumps(move) # sérialisation
                except OSError as err:
                    print(f"[ERROR] Can't pickle object.\n{err}")
                    break

                send_data_length = len(data_output) # longueur en octets
                send_header = str(send_data_length).encode(FORMAT) # encodage
                send_header += b' ' * (HEADER_SIZE - len(send_header)) # complétion
                conn.send(send_header) # Envoi du header 
                conn.send(data_output) # Envoi des données

                if can_switch:
                    # On change d'IA après le tour            
                    self.switch_ai()

        except OSError as err:
            print(f"[ERROR] Error occured: {err}")

        finally:
            conn.close()
            print(f"[DECONNECTION] {addr} has disconnected.")

    def switch_ai(self):
        self.ai_index += 1
        self.ai_index %= len(self.ai_list)
        self.current_ai = self.ai_list[self.ai_index]

    def recv_ai(self, conn: socket.socket, addr):
        recv_header = conn.recv(HEADER_SIZE).decode(FORMAT) # reception du header
        if not recv_header:
            conn.close()
    
        recv_data_length = int(recv_header) # on récupère la longueur des données suivantes
        try:
            data_input = pickle.loads(conn.recv(recv_data_length)) # on récupère les données
        except OSError as err:
            print(f"[ERROR] No data can be received.\n{err}")
            conn.close()

        print(f"[FIRST SEND] [{addr}] : {data_input}")
        
        return data_input
