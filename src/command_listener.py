from .constants import *
from .game import Game

import sys
import json
import threading
from queue import Queue

class CommandListener:

    def __init__(self, game: Game):
        self.game = game
        self.command_queue = Queue()

    def listen(self):
        """ Créé une boucle infinie qui demande simplement une entrée utilisateur. """
        while True:
            user_input = input()
            self.command_queue.put(user_input)

    def create_thread(self):
        """ Thread pour les commandes. """
        input_thread = threading.Thread(target=self.listen)
        input_thread.daemon = True
        input_thread.start()

    def check_command(self, user_input: str):
        """ 
        Charge la liste des commandes à partir du fichier de configuration
        correspondant. Ces commandes peuvent être exécutées à n'importe quel moment.
        """
        string_list = user_input.split(" ")

        with open(CMDS_CONFIG_PATH, "r", encoding='UTF-8') as f:
            commands = json.load(f)

        if string_list[0] in commands:
            try:
                method = commands[string_list[0]]
                eval(method)(*string_list[1::])
            except NameError:
                print(f"La commande '{string_list[0]}' n'est pas valide.")
            except OSError as err:
                print(err, file=sys.stderr)
        else:
            print("La commande que vous avez entré n'existe pas.")
    
    @staticmethod
    def print_commands():
        """ Exécutée lors de la commnade /help """
        with open(CMDS_CONFIG_PATH, "r", encoding='UTF-8') as f:
            data: dict = json.load(f)

        commands = list(data.keys())
        for command in commands:
            print(f"- {command}\n")

    @staticmethod
    def print_configs():
        """ Exécutée lors de la commande /configs """
        with open(BOARD_CONFIG_PATH, "r", encoding='UTF-8') as f:
            data = json.load(f)

        config_names = list(data.keys())
        for config in config_names:
            print(f"- {config}\n")

    def get_queue(self):
        """ Retourne la file. """
        return self.command_queue
    
    def get_command(self):
        """ Retourne le dernier élément de la file. """
        return self.command_queue.get()
