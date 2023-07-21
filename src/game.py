import pygame
from .board import Board
from .config import Config
from .dragger import Dragger
from .theme import Theme
from .button import Button
from .clock import Clock
from .move import Move
from .piece import Piece
from .constants import *
import sys, time


class Game:
    """
    Initialise tout ce qui est relatif au jeu (graphique ou non):
        - la fenêtre
        - La pièce sélectionnée par le joueur courant (selected_piece)
        - Le carré qui est survolé par la souris (hovered_square_pos)
        - le plateau de jeu (board)
        - le dragger (dragger)
        - le tour du joueur qui commence (turn)
        - la liste des déplacements valides (valid_moves)

    Gère l'affichage, les déplacements, la fin de partie.
    """
    
    def __init__(self, game_config: Config, board_config):
        self._init(game_config, board_config)

        self.screen = pygame.display.set_mode([self.game_config.window.screen_width, self.game_config.window.screen_height], pygame.SRCALPHA)
        self.screen.set_alpha(self.game_config.transparency)
        self.board_window = pygame.Surface([self.game_config.window.board_width, self.game_config.window.board_height], pygame.SRCALPHA)
        self.board_window.set_alpha(self.game_config.transparency)
        self.board_rect = pygame.Rect(self.game_config.get_board_pos()[0], self.game_config.get_board_pos()[1],
                                      self.game_config.window.board_width, self.game_config.window.board_height)

        self.clock1 = Clock(self.game_config, self.screen, 'white', self.game_config.game_duration, self.player_side)
        self.clock2 =  Clock(self.game_config, self.screen, 'black', self.game_config.game_duration, self.player_side)

        self.dragger = Dragger(game_config)

    # Méthode privée
    def _init(self, game_config: Config, board_config):
        self.game_config = game_config
        self.selected_piece: Piece = None
        self.hovered_square_pos = None
        self.player_side = "bottom"
        self.board = Board(board_config, self.player_side)
        self.turn = 'white'
        self.valid_moves = self.board.get_valid_moves(self.turn)

        self.winner = None
        self.playing = False
        self.start_time = time.time()
        self.player1_remaining_time = self.player2_remaining_time = self.game_config.game_duration
        self.remaining_time = self.game_config.game_duration
        self.elapsed_time = 0

    def get_remaining_time(self):
        """ Retourne le temps de jeu restant pour le joueur courant. """
        if self.turn == 'white':
            return self.player1_remaining_time
        return self.player2_remaining_time

    def select_piece(self, piece):
        """ Définit la pièce comme étant sélectionnée par le joueur. """
        self.selected_piece = piece

    def unselect_piece(self):
        """ Définit la pièce comme n'étant plus sélectionnée par le joueur. """
        self.selected_piece = None

    def get_move(self, initial, final) -> Move:
        """ Recherche un move parmi la liste des déplacements valides. """
        for move in self.valid_moves:
            if move.initial_pos == initial and move.final_pos == final:
                return move
        return None

    def set_hover(self, row, col):
        """ Définit la case de coordonnées (row, col) comme étant survolée par la souris. """
        self.hovered_square_pos = (row, col)

    def change_theme(self):
        """ Change le thème de l'interface graphique (bleu, vert, ...) """
        self.game_config.change_theme()
    
    def change_resolution(self):
        """ Modifie la résolution d'écran. """
        self.game_config.change_resolution()

        self.screen = pygame.display.set_mode([self.game_config.window.screen_width, self.game_config.window.screen_height], pygame.SRCALPHA)
        self.screen.set_alpha(self.game_config.transparency)

        self.board_window = pygame.Surface([self.game_config.window.board_width, self.game_config.window.board_height], pygame.SRCALPHA)
        self.board_window.set_alpha(self.game_config.transparency)

        self.board_rect = pygame.Rect(self.game_config.get_board_pos()[0], self.game_config.get_board_pos()[1],
                                self.game_config.window.board_width, self.game_config.window.board_height)

    def round_board(self):
        """ Dessine le bord arrondi du plateau. """
        pygame.draw.rect(self.screen, BG, 
                    (self.game_config.get_board_pos()[0] - 5, self.game_config.get_board_pos()[1] - 5, 
                    self.game_config.window.board_width + 10, self.game_config.window.board_height + 10),
                    width=5, border_radius=15)

    def update(self, tick):
        """ Met à jour l'écran. """
        theme = self.game_config.theme
        self.screen.fill(BG)

        # Position du plateau
        self.game_config.set_board_pos((200, (self.screen.get_height() - self.board_window.get_height()) // 2))
        self.screen.blit(self.board_window, self.game_config.get_board_pos())
        # Bords arrondis
        self.round_board()
        self.draw_board(self.board_window, theme)

        if self.dragger.dragging:
            self.show_hover(self.board_window, theme)
            self.dragger.update_blit(self.board_window)

        self.winner = self.get_winner()
        if self.winner is not None:
            self.show_end_screen(self.winner)

        self.show_fps(self.screen, tick)
        self.show_clock()

        pygame.display.update()
    
    def reset(self, board_config=1):
        """ Réinitialise la partie. """
        self._init(self.game_config, board_config)

    def draw_squares(self, window, theme: Theme):
        """
        Dessine le plateau de jeu. Si la ligne est paire, on dessine
        les cases claires à partir de la première colonne, sinon, à partir
        de la deuxième.
        """
        square_size = self.game_config.window.square_size
        for row in range(ROWS):
            for col in range(COLS):
                color = theme.light_background if (row + col) % 2 == 0 else theme.dark_background
                pygame.draw.rect(window, color, 
                                    (col*square_size, row*square_size, square_size, square_size))

    def draw_pieces(self, window):
        square_size = self.game_config.window.square_size
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board.get_piece(row, col)
                if piece != 0 and piece is not self.dragger.piece:
                    x, y = (square_size * piece.col + square_size // 2, 
                                square_size * piece.row + square_size // 2)
                    piece.draw_piece(window, x, y, square_size)

    def draw_board(self, window, theme: Theme):
        """ 
        Dessine le plateau (cases vides, pièces).
        Cette fonction prend en compte l'affichage du dernier déplacement,
        des moves valides, des cases survolées et de la pièce sélectionnée.
        """
        self.draw_squares(window, theme)
        self.show_selected_piece(window, theme)
        self.show_last_move(window, theme)
        self.show_valid_moves(window, theme)
        self.draw_pieces(window)
    
    def change_turn(self):
        """
        Change le tour et calcul les déplacements valides
        du joueur auquel le tour vient de passer.
        """
        if self.turn == 'white':
            self.player1_remaining_time = self.remaining_time + self.game_config.bonus_time
            self.remaining_time = self.player2_remaining_time
            self.turn = 'black'
        else:
            self.player2_remaining_time = self.remaining_time + self.game_config.bonus_time
            self.remaining_time = self.player1_remaining_time
            self.turn = 'white'

        self.start_time = time.time()
        self.valid_moves = self.board.get_valid_moves(self.turn)

    def move(self, row, col):
        """ 
        Déplace une pièce sur le plateau (en prenant en compte les règles).
        Comme on essaye de déplacer une pièce seulement si elle a pu être selectionnée,
        on considère que selected_piece est différent de None.
        """
        selected_coords = (self.selected_piece.row, self.selected_piece.col)
        move = self.get_move(selected_coords, (row, col))
        if move is not None:
            # On déplace la pièce selectionnée
            self.board.move_piece(move)
            # On récupère la liste des pièces capturées par ce déplacement.
            skipped_pieces = move.get_skipped_list()
            # Si le déplacement n'est pas libre, on supprime toutes ces pièces du plateau
            if len(skipped_pieces) > 0:
                self.board.remove_pieces(skipped_pieces)
            self.change_turn()
            return True
        return False
    
    def show_rect(self, window, color, row, col, width=100):
        """ Dessine une case. """
        square_size = self.game_config.window.square_size
        draw_start_position = col * square_size, row * square_size
        draw_size = (square_size, square_size)
        pygame.draw.rect(window, color, (draw_start_position, draw_size), width)

    def show_selected_piece(self, window, theme: Theme):
        """ Dessine la case sélectionnée par le joueur. """
        if self.selected_piece != None:
            self.show_rect(window, theme.selected_piece_color, self.selected_piece.row, self.selected_piece.col, width=100)

    def show_hover(self, window, theme: Theme):
        """ Ajoute un effet visuel aux cases survolées par le curseur de la souris. """
        row, col = self.hovered_square_pos
        if self.hovered_square_pos is not None and self.selected_piece is not None:
            if row == self.selected_piece.row and col == self.selected_piece.col:
                color = theme.selected_hover_color
            elif (row + col) % 2 == 0:
                color = theme.light_hover_color
            else:
                color = theme.dark_hover_color
            self.show_rect(window, color, row, col, width=5)

    def show_valid_moves(self, window, theme: Theme):
        """ 
        Ajoute des effets visuels permettant de discerner
        les cases d'arrivées possibles ainsi que les pièce sautées.
        """
        square_size = self.game_config.window.square_size
        if self.selected_piece is not None:
            selected_coords = (self.selected_piece.row, self.selected_piece.col)
            color = theme.valid_moves_color
            radius = square_size // 2 - self.game_config.window.padding
            for move in self.valid_moves:
                if move.get_initial_pos() == selected_coords:
                    final_pos = move.get_final_pos()
                    center = (square_size * final_pos[1] + square_size // 2, 
                                square_size * final_pos[0] + square_size // 2)
                    pygame.draw.circle(window, color, center, radius)
                    skipped_pieces = move.get_skipped_list()
                    for (row, col) in skipped_pieces:
                        self.show_rect(window, color, row, col, width=100)

    def show_last_move(self, window, theme: Theme):
        """ 
        Re-dessine les cases qui correspondent au dernier
        mouvement effectué sur le plateau
        """
        if self.board.last_move is not None:
            for pos in [self.board.last_move.initial_pos, self.board.last_move.final_pos]:
                self.show_rect(window, theme.selected_piece_color, pos[0], pos[1], width=100)

    def show_fps(self, window, framerate):
        """ Affiche le framerate. """
        max_fps = self.game_config.get_fps()
        if framerate > 0.9 * max_fps:
            color = (81, 194, 47)
        elif 0.5 * max_fps <= framerate < 0.9 * max_fps:
            color = (217, 224, 16)
        else:
            color = (224, 73, 18)
        text = self.game_config.digital_font.render(str(framerate).split('.')[0], True, color)
        text.set_alpha(self.game_config.transparency)
        window.blit(text, [10, 0])

    def show_clock(self):
        """ Affiche les horloges. """
        if self.playing:
            if self.turn == 'white':
                self.clock1.set_remaining_time(self.remaining_time)
                self.clock1.tick()
                self.clock2.set_remaining_time(self.player2_remaining_time)
                self.clock2.pause()
            else:
                self.clock2.set_remaining_time(self.remaining_time)
                self.clock2.tick()
                self.clock1.set_remaining_time(self.player1_remaining_time)
                self.clock1.pause()
        self.clock1.update()
        self.clock2.update()

    def show_end_screen(self, winner):
        """ Affiche l'écran de fin. """
        board_origin = self.game_config.get_board_pos()

        end_screen_width, end_screen_height = self.game_config.window.board_width // 2,  self.game_config.window.board_height // 3
        end_screen_center_x = board_origin[0] + (self.game_config.window.board_width - end_screen_width) // 2
        end_screen_center_y = board_origin[1] + (self.game_config.window.board_height - end_screen_height) // 2

        restart_button = Button(
            id="restart_button",
            screen=self.screen,
            text="Rejouer",
            bg_color=GREEN,
            text_color=(255, 255, 255),
            width=end_screen_width // 2,
            height=end_screen_height // 3,
            border_radius=15,
            position= [end_screen_center_x + (end_screen_width - (end_screen_width // 2)) // 2, 
                       end_screen_center_y + end_screen_height // 2],
            command=self.reset,
            font="assets/recharge.rg-bold.otf",
            font_size=self.game_config.window.text_font_size
        )
        
        if restart_button not in self.game_config.get_buttons_list():
            self.game_config.add_button(restart_button)

        end_screen = pygame.Surface([end_screen_width, end_screen_height], pygame.SRCALPHA)
        pygame.draw.rect(end_screen, BG, (0, 0, end_screen_width, end_screen_height), border_radius=15)
        screen_text_surface = self.game_config.text_font.render(f"Le joueur {winner} a gagné la partie !", True, (255, 255, 255))
        
        end_screen.blit(screen_text_surface, [(end_screen_width - screen_text_surface.get_width()) // 2, end_screen_height // 4])
        self.screen.blit(end_screen, [end_screen_center_x, end_screen_center_y])
        restart_button.show()

    def get_winner(self):
        """ Renvoi le gagnant de la partie. """
        if self.board.white_pieces_left == 0 and self.board.black_pieces_left > 0 \
                or self.remaining_time == 0 and self.turn == 'white':
            return 'noir'
        elif self.board.black_pieces_left == 0 and self.board.white_pieces_left > 0 \
                or self.remaining_time == 0 and self.turn == 'black':
            return 'blanc'
        return None

    def quit_game(self):
        """ Permet de quitter le jeu. """
        pygame.quit()
        sys.exit()
