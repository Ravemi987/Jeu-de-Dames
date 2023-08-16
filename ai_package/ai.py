from src.game import Game
from src.move import Move
import time


class AI:
    """
    # =======================
    Intelligence Artificielle
    # =======================
    engine : fonction qui retourne un move choisi
        parmi la liste de tous les moves possibles.
    game : instance 'game' de la classe Main
    """
    
    def __init__(self, engine, color):
        self.engine = engine
        self.color = color

    def move(self, game: Game, move: Move):
        """ 
        Joue le move passé en paramètre en appelant
        la méthode apply_move de la classe game
        """
        game.apply_move(move)

    @staticmethod
    def simulate_move(move: Move, game: Game):
        """ 
        Simule un déplacement et renvoi l'instance de la 
        classe game modifiée.
        """
        current_game: Game = game.copy()
        #debut = time.time()
        current_game.apply_move(move.copy())
        #print(time.time() - debut)
        return current_game
