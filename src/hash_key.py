from .board import Board
from .piece import Piece
from .move import Move
from .constants import *
from .hash_values import *

class HashKey:
    
    def __init__(self, starting_board: Board, turn, white_side):
        self.board = starting_board
        self.turn = turn
        self.side = white_side
        self.value = 0
        self.generate()
        self.list_values =  []
        self.last_move_value = 0

    def get_pos_value(self, row, col):
        """ Retourne la valeur de la position"""
        return row * ROWS + col + 2

    def generate(self):
        """
        Génère une clé de hachage unique pour représenter l'état du plateau de jeu.
        """
        for row in range(ROWS):
            for col in range(COLS):
                piece: Piece = self.board.get_piece(row, col)

                if piece == 0:
                    piece_type = EMPTY
                else:
                    piece_type = PAWN if piece.is_pawn() else QUEEN
                    color = WHITE_PIECE if piece.color == 'white' else BLACK_PIECE
                    player = PLAYER1 if self.turn == 'white' else PLAYER2
                    side = BOT_SIDE if self.side == 'bottom' else TOP_SIDE

                    position_value = self.get_pos_value(row, col)
                    self.value ^= piece_type ^ color ^ player ^ side ^ position_value

        self.value ^= TOUR_START
    
    def get_move_value(self, init_row, init_col, final_row, final_col, is_capture):
        """ Retourne la valeur d'un move selon sa direction et s'il s'agit d'une capture ou non. """
        delta_row = final_row - init_row
        delta_col = final_col - init_col

        if is_capture:
            return CAPTURES.get((delta_row, delta_col), abs(delta_row + delta_col))
        else:
            return MOVES.get((delta_row, delta_col), abs(delta_row + delta_col))

    def update(self, move: Move, player_turn):
        """ Met à jour la valeur de la clé de hachage."""
        init_row, init_col = move.get_initial_pos()
        final_row, final_col = move.get_final_pos()
        is_capture = move.is_capture()
        move_value = self.get_move_value(init_row, init_col, final_row, final_col, is_capture)
        position_value = self.get_pos_value(init_row, init_col) ^ self.get_pos_value(final_row, final_col)
        self.value ^= move_value ^ self.last_move_value ^ position_value ^ (PLAYER1 if player_turn == 'white' else PLAYER2)
        self.last_move_value = move_value

    def get_value(self):
        """ Retourne la valeur de la clé de hachage. """
        return self.value

    def __repr__(self):
        return f"{self.value}"
