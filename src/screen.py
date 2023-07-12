from .constants import COLS

class Screen:
    """
    Classe qui gère la résolution graphique
        - taille (hauteur et largeur) de la fenêtre principale
        - taille (hauteur et largeur) de la fenêtre de jeu (plateau)
        - taille d'une case
        - marge pour tracer des cercles dans les cases

    """

    def __init__(self, screen_width, screen_height, board_width, board_height, font_size):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.board_width = board_width
        self.board_height = board_height
        self.font_size = font_size
        self.square_size = self.board_width // COLS
        self.padding = 0.33 * self.square_size
