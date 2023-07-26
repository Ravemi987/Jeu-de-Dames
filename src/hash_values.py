"""
Type de pièce:
Case vide: 0
Pions: 200
Dame: 300

Couleur de la pièce:
Blanc: 440
Noir: 550

Joueur courant:
Joueur 1 (blanc): 400
Joueur 2 (noir): 500

Côté des blancs:
Bottom: 480
Top: 580

Position des pièce:
pour un plateau 10x10:
de 2 à 102
(0, 0) -> 2
(0, 1) -> 3
...
(1, 0) -> 12
...
(9, 9) -> 102

Tour actuel:
600 + numéro du tour

Suppression d'un pion:
1200
Suppression d'une dame:
1300

Déplacement vers le haut à gauche : 103
Déplacement vers le haut à droite : 104
Déplacement vers le bas à gauche : 105
Déplacement vers le bas à droite : 106
Prise vers le haut à gauche : 107
Prise vers le haut à droite : 108
Prise vers le bas à gauche : 109
Prise vers le bas à droite : 110
"""

EMPTY = 0
PAWN = 200
QUEEN = 300
PLAYER1 = 400
PLAYER2 = 500
BOT_SIDE = 480
TOP_SIDE = 580
WHITE_PIECE = 440
BLACK_PIECE = 550
TOUR_START = 600
CAPTURE_PAWN = 1200
CAPTURE_DAME = 1300
MOVE_UP_LEFT = 103
MOVE_UP_RIGHT = 104
MOVE_DOWN_LEFT = 105
MOVE_DOWN_RIGHT = 106
CAPTURE_UP_LEFT = 107
CAPTURE_UP_RIGHT = 108
CAPTURE_DOWN_LEFT = 109
CAPTURE_DOWN_RIGHT = 110

MOVES = {
    (1, 1): MOVE_DOWN_RIGHT,
    (1, -1): MOVE_DOWN_LEFT,
    (-1, 1): MOVE_UP_RIGHT,
    (-1, -1): MOVE_UP_LEFT,
}

CAPTURES = {
    (2, 2): CAPTURE_DOWN_RIGHT,
    (2, -2): CAPTURE_DOWN_LEFT,
    (-2, 2): CAPTURE_UP_RIGHT,
    (-2, -2): CAPTURE_UP_LEFT,
}
