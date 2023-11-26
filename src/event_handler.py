import pygame
from src.board import Board
from src.dragger import Dragger
from src.game import Game
from src.config import Config

class EventHandler:

    def __init__(self, game: Game, config: Config):
        self.game = game
        self.config = config
        self.clock = pygame.time.Clock()
        self.mouse_pos = (0, 0)
        self.previously_selected_piece = None
        self.clicked_piece = None
        self.released_piece = None

    def get_pos_from_mouse(self, mouse_pos):
        """ 
        Renvoi la ligne et la colonne de la matrice de la case
        sur laquelle pointe notre souris.
        """
        x, y = mouse_pos
        row = y // self.config.window.square_size
        col = x // self.config.window.square_size
        return row, col
    
    def check_MouseButtonDown(self, board: Board, dragger: Dragger):
        """ Gère l'évènement: pygame.MOUSEBUTTONDOWN. """
        clicked_row, clicked_col = self.get_pos_from_mouse([dragger.mouseX, dragger.mouseY])

        if self.game.board_rect.collidepoint(self.mouse_pos) and not(board.is_empty_square(clicked_row, clicked_col)):
            self.clicked_piece = board.get_piece(clicked_row, clicked_col)
            dragger.drag_piece(self.clicked_piece)
            self.game.select_piece(self.clicked_piece)
            
            if not self.game.has_start:
                self.game.start()
        else:
            if self.game.selected_piece is not None and self.game.selected_piece.color == self.game.turn:
                can_move = self.game.check_human_move(clicked_row, clicked_col)
                if not can_move:
                    self.game.unselect_piece()
            else:
                self.game.unselect_piece()
    
    def check_MouseMotion(self, dragger: Dragger):
        """ Gère l'évènement: pygame.MOUSEMOTION. """
        hovered_row, hovered_col = self.get_pos_from_mouse([dragger.mouseX, dragger.mouseY])
        self.game.set_hover(hovered_row, hovered_col)

    def check_MouseButtonUp(self, board: Board, dragger: Dragger):
        """ Gère l'évènement: pygame.MOUSEBUTTONUP. """
        released_row, released_col = self.get_pos_from_mouse([dragger.mouseX, dragger.mouseY])

        if self.game.board_rect.collidepoint(self.mouse_pos):
            self.released_piece = board.get_piece(released_row, released_col)

        if self.previously_selected_piece is not None and self.released_piece == self.previously_selected_piece \
                and self.clicked_piece == self.previously_selected_piece:
            self.game.unselect_piece()
        elif self.game.selected_piece is not None and self.game.selected_piece.color == self.game.turn:
            self.game.check_human_move(released_row, released_col)
        
        dragger.undrag_piece()
        self.previously_selected_piece = self.game.selected_piece
    
    def check_ButtonClick(self, board, dragger):
        """ Vérifie si un bouton a été cliqué. """
        for button in self.config.get_buttons_list():
            if button.pressed and button.id == 'restart_button':
                board = self.game.board
                dragger = self.game.dragger
                button.pressed = False
        return board, dragger

    def check_KeyDown(self, event: pygame.event.Event):
        """ Vérifie les actions à réaliser si une touche est enfoncée. """
        # Touche 't' pour changer le thème
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_t:
                self.game.change_theme()
        
            elif event.key == pygame.K_F11:
                self.game.change_resolution()

    def check_event(self, event: pygame.event.Event, board, dragger):
        if not self.game.is_finished:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.check_MouseButtonDown(board, dragger)
                self.game.update(self.clock.get_fps())

            elif event.type == pygame.MOUSEMOTION:
                self.check_MouseMotion(dragger)

            elif event.type == pygame.MOUSEBUTTONUP:
                self.check_MouseButtonUp(board, dragger)
        
        self.check_KeyDown(event)

    def get_clock(self):
        return self.clock
