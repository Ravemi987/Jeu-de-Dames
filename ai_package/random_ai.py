from src.game import Game
import random

"""
random_ai est une IA aléatoire aussi appelée IA naïve.
Elle prend en paramètre une instance de la classe game et
choisi aléatoirement* un élément de la liste game.valid_moves
de type : list[Move]

* pseudo-aléatoirement
"""

def random_ai(game: Game):
    return game.valid_moves[random.randint(0, len(game.valid_moves)-1)]
