from .piece import Piece

class Move:
    """
    Un 'Move' ou déplacement, ou bien encore mouvement,
    possède une case de départ, une case d'arrivée et une liste des cases
    qui on été sautées par le déplacement de la case de départ à la case d'arrivée.
    """
    def __init__(self, turn, piece: Piece, initial_pos, final_pos, skipped_list=[]):
        self.turn = turn
        self.piece = piece
        self.initial_pos = initial_pos
        self.final_pos = final_pos
        self.skipped_list = skipped_list

    def get_initial_pos(self):
        return self.initial_pos
    
    def get_final_pos(self):
        return self.final_pos
    
    def is_empty_skipped_list(self):
        """ Vérifie si la liste des pièces capturées est vide. """
        return len(self.skipped_list) == 0

    def get_skipped_list(self):
        return self.skipped_list
    
    def get_piece(self):
        """ Retourne la pièce déplacée. """
        return self.piece
    
    def get_player_turn(self):
        return "player1" if self.turn == 'white' else "player2"
    
    def is_capture(self):
        """ Vérifie si un déplacement est une capture. """
        return not self.is_empty_skipped_list()
    
    def is_pawn_move(self):
        """ Vérifie si un pion est déplacé. """
        return self.piece.name == 'pawn'

    def copy(self):
        """ Copie une instance de la classe Move. """
        move_copy = Move(self.turn, self.piece.copy(), self.initial_pos,
            self.final_pos, self.skipped_list)
        return move_copy

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Move):
            return self.initial_pos == other.initial_pos and self.final_pos == other.final_pos
        return False

    def __repr__(self):
        return f"[{self.initial_pos}, {self.final_pos}]"
