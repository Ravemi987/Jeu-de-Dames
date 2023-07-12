from .constants import *

class Dragger:
    """
    Classe qui permet de gérer le mouvement d'une pièce lorsqu'on la sélectionne avec la
    souris et qu'on la déplace en gardant le clique de la souris enfoncé. Cette action vient
    de l'anglais 'to drag = traîner'.
    La classe a comme attributs, une pièce, un booléen pour savoir si cette pièce est en mouvement,
    et les coordonnées du curseur de la souris que la pièce doit suivre.
    """
    
    def __init__(self, config):
        self.piece = None
        self.dragging = False
        self.config = config
        self.mouseX = 0
        self.mouseY = 0

    def in_window(self, coord, mouse_pos):
        """ Vérifie que le curseur de la souris est dans la fenêtre de jeu. """
        pos = self.config.get_board_pos()
        if coord == mouse_pos[0]:
            return pos[0] <= coord <= pos[0] + self.config.window.board_width
        else:
            return pos[1] <= coord <= pos[1] + self.config.window.board_width

    def update_blit(self, window):
        """ Dessine la pièce à l'endroit où se trouve le curseur de la souris. """
        self.piece.draw_piece(window, self.mouseX , self.mouseY, self.config.window.square_size)

    def update_mouse(self, mouse_pos):
        """ 
        Met à jour les coordonnées du curseur
        (uniquement si la souris est dans la fenêtre de jeu). 
        """
        x, y = mouse_pos
        if self.in_window(x, mouse_pos):
            self.mouseX = x - self.config.get_board_pos()[0]
        if self.in_window(y, mouse_pos):
            self.mouseY = y - self.config.get_board_pos()[1]

    def drag_piece(self, piece):
        """ Active le dragger pour la pièce. """
        self.piece = piece
        self.dragging = True
    
    def undrag_piece(self):
        """ Désactive le dragger pour la pièce. """
        self.piece = None
        self.dragging = False
