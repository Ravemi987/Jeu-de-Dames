from .constants import *

class Piece:
    """
    Une pièce est représentée par sa position (row, col) dans la matrice (le plateau),
    une couleur (1 pour les blancs et 2 pour les noirs),
    un attribut 'name' qui permet de savoir si la pièce est une dame,
    une liste des déplacements valides de la pièces,
    une position sur l'écran (x, y.)
    """
    
    def __init__(self, row, col, color, name='pawn', side=1, sprite=None):
        self.row = row
        self.col = col
        self.color = color
        self.name = name
        self.sprite = sprite
        self.set_sprite()

        if self.color == 'white':
            self.direction, self.last_row = (-1, 0) if side == 1 else (1, ROWS - 1)
        else:
             self.direction, self.last_row = (1, ROWS - 1) if side == 1 else (-1, 0)

    def set_sprite(self):
        """ Load l'image correspondant à la pièce. """
        self.sprite = pygame.image.load(f'assets/{self.color}_{self.name}.png')

    def is_queen(self):
        """ Vérifie si une pièce est une dame. """
        return self.name == 'queen'

    def make_queen(self):
        """ Tranforme une pièce en dame. """
        self.name = 'queen'
        self.set_sprite()

    def check_promotion(self):
        """ Vérifie si une pièce doit devenir une dame. Si oui, elle est transformée. """
        if self.row == self.last_row and not(self.is_queen()):
            self.make_queen()

    def update_pos(self, row, col):
        """" 
        Actualisation de la position d'une pièce après son déplacement.
        """
        self.row = row
        self.col = col

    def draw_piece(self, window, x, y, square_size):
        """ Dessine une pièce qui est soit une reine, soit un pion normal """
        piece_to_draw = pygame.transform.scale(self.sprite, (0.80 * square_size, 0.80 * square_size))
        window.blit(piece_to_draw, (x - piece_to_draw.get_width()//2, y - piece_to_draw.get_height()//2))

    def __eq__(self, other):
        if isinstance(other, Piece):
            return self.row == other.row and self.col == other.col and self.name == other.name
        return False

    def __repr__(self):
        color = 'White' if self.color == 1 else 'Black'
        return f"Piece [x = {self.row}; y = {self.col}; Color = {color}; Name = {self.name}]"
