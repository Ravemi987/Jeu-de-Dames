from src.game import Game
from src.move import Move
from src.constants import *
import os
import json
import time


class AI:
    """
    Intelligence Artificielle
    name: nom de l'IA
    engine : fonction qui retourne un move choisi
        parmi la liste de tous les moves possibles.
    color : couleur de l'IA
    """
    
    def __init__(self, name, engine, color):
        self.name = name
        self.engine = engine
        self.color = color

        # paramètres passés à l'IA
        self.args = self.set_args()

    def move(self, game: Game, move: Move):
        """ 
        Joue le move passé en paramètre en appelant
        la méthode apply_move de la classe game
        """
        game.apply_move(move)

    def set_args(self):
        """ 
        Récupère dans un fichier de configuration
        les paramètres passés à la fonction principale de l'IA
        lors de son exécution.
        """
        with open(os.path.join(AI_PACKAGE_PATH, "args.json"), "r", encoding='UTF-8') as f:
            data = json.load(f)

        return eval(data[self.name])
    
    def choose_move(self, game: Game, addr):
        """ Renvoie le déplacement choisi par l'IA. """
        start_time = time.time()
        score, move, depth, nodes = self.engine(game, self.color, *self.args)
        search_time = time.time() - start_time

        print(f"{addr}: {move} found in {round(search_time, 3)}s with depth of {depth+1} and score of {score} exploring {nodes} nodes.")
        #time.sleep(0.8 - search_time)

        return move

    @staticmethod
    def simulate_move(move: Move, game: Game):
        """ 
        Simule un déplacement et renvoi l'instance de la 
        classe game modifiée.
        """
        current_game: Game = game.copy()
        current_game.apply_move(move.copy())
        return current_game
