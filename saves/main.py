import pygame
from src.constants import *
from src.game import Game
from src.config import Config
from src.board import Board
from src.dragger import Dragger
from src.move import Move
import threading
import ctypes
from ctypes import wintypes
import os
import time

from src.command_listener import CommandListener
from communication.client import Client

from ai_package.ai import AI
from ai_package import random_ai
from ai_package import minimax
from ai_package import alphabeta

if SYSTEM == "Windows":
    # Définir l'ID de l'application (AppUserModelID)
    myappid = u'ravemi_987.jeux.jeu_de_dames.5'  # Chaîne arbitraire
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    # Obtenir l'ID de l'application
    lpBuffer = wintypes.LPWSTR()
    AppUserModelID = ctypes.windll.shell32.GetCurrentProcessExplicitAppUserModelID
    AppUserModelID(ctypes.cast(ctypes.byref(lpBuffer), wintypes.LPWSTR))
    appid = lpBuffer.value
    ctypes.windll.kernel32.LocalFree(lpBuffer)

    # Afficher l'ID de l'application
    if appid is not None:
        print(appid)
        
    screen_position = (0, 30)
    os.environ['SDL_VIDEO_WINDOW_POS'] = str(screen_position[0]) + "," + str(screen_position[1])

class Main:
    """
    Dans cette classe:
    On initialise pygame, l'icône de jeu, la fenêtre de jeu et le jeu avec ses paramètres.
    On utilise des threads pour pouvoir jouer au jeu dans la fenêtre et 'en même temps' entrer des commandes
    dans le terminal si besoin. On utilise une file pour synchroniser correctement les threads.
    """

    def __init__(self):
        """ Attributs, instances de classes. """
        pygame.init()
        pygame.display.set_icon(ICON)
        pygame.display.set_caption('Jeu de Dames')
        self.config = Config()
        self.game = Game(self.config, 1)
        self.command_listener = CommandListener(self.game)
        self.clock = pygame.time.Clock()

        self._init()

        if self.config.gamemode != 'self.player_vs_player':
            self.client = Client()
            self._create_ai()
    
    def _init(self):
        """ Attributs liés à la classe Main. """
        self.mouse_pos = (0, 0)
        self.previously_selected_piece = None
        self.clicked_piece = None
        self.released_piece = None
        self.run = True

    def _create_ai(self):
        """ Créé plusieurs instances de la classe AI. """
        self.random_ai = AI(random_ai.random_ai, 'black')
        self.minimax_ai = AI(minimax.MiniMax_Max, 'black')
        self.alphabeta_ai = AI(alphabeta.AlphaBeta, 'black')
        self.ai = self.alphabeta_ai

    def get_pos_from_mouse(self, mouse_pos):
        """ 
        Renvoi la ligne et la colonne de la matrice de la case
        sur laquelle pointe notre souris.
        """
        x, y = mouse_pos
        row = y // self.config.window.square_size
        col = x // self.config.window.square_size
        
        return row, col

    def ai_loop(self):
        """ Boucle principale qui gère l'IA. """
        while True:
            time.sleep(0.030)
            if self.ai.color == self.game.turn and not self.game.is_finished:
                if len(self.game.valid_moves) == 1:
                    best_move = self.game.valid_moves[0]
                    self.ai.move(self.game, best_move)
                else:
                    if not self.client.is_close():
                        game_copy = self.game.copy()
                        self.client.apply_protocol(game_copy)

    def create_ai_thread(self):
        """ Thread pour l'IA. """
        ai_thread = threading.Thread(target=self.ai_loop)
        ai_thread.daemon = True
        ai_thread.start()

    def _init_loop(self):
        """ Initialise la boucle principale de jeu. """
        self.command_listener.create_thread()
        if self.config.gamemode != 'self.player_vs_player':
            self.create_ai_thread()

        board = self.game.board
        dragger = self.game.dragger
        self.previously_selected_piece = None

        return board, dragger
    
    def update_clocks(self):
        """ Met à jour les pendules du jeu. """
        if self.game.has_start:
            self.game.elapsed_time = time.time() - self.game.start_time
            self.game.remaining_time = self.game.get_remaining_time() - self.game.elapsed_time
            if self.game.remaining_time < 0:
                self.game.remaining_time = 0

    def check_MouseButtonDown(self, board: Board, dragger: Dragger):
        """ Gère l'évènement: pygame.MOUSEBUTTONDOWN. """
        clicked_row, clicked_col = self.get_pos_from_mouse([dragger.mouseX, dragger.mouseY])

        if self.game.board_rect.collidepoint(self.mouse_pos) and not(board.is_empty_square(clicked_row, clicked_col)):
            self.clicked_piece = board.get_piece(clicked_row, clicked_col)
            dragger.drag_piece(self.clicked_piece)
            self.game.select_piece(self.clicked_piece)
            
            if not self.game.has_start:
                self.game.has_start = True
                self.game.start_time = time.time()
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

    def player_turn(self, board, dragger):
        """ 
        Permet au joueur humain de jouer un tour.
        Active le dragger, les cliques de la souris etc...
        """
        # pygame.event.get() renvoie une liste des actions (events)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run = False

            if not self.game.is_finished:
                # Clique enfoncé (gauche ou droit)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.check_MouseButtonDown(board, dragger)
                    self.game.update(self.clock.get_fps())

                # Déplacement de la souris
                elif event.type == pygame.MOUSEMOTION:
                    self.check_MouseMotion(dragger)

                # Clique relâché (gauche ou droit)
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.check_MouseButtonUp(board, dragger)
            
            self.check_KeyDown(event)

    def player_vs_player(self, board, dragger):
        """ Mode de jeu 'joueur contre joueur'. """
        if not self.game.is_finished:
            self.update_clocks()

        self.player_turn(board, dragger)

    def player_vs_ai(self, board, dragger):
        """ Mode de jeu 'joueur contre ordi'. """
        if not self.game.is_finished:
            self.update_clocks()
        
        self.player_turn(board, dragger)

    def ai_vs_ai(self):
        """ Mode de jeu 'ordi contre ordi'. """
        if not self.game.has_start:
            self.game.has_start = True
            self.game.start_time = time.time()

        if not self.game.is_finished:
            self.update_clocks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run = False

            self.check_KeyDown(event)

    def mainloop(self):
        """ 
        Boucle principal qui créé et démarre le thread et gère les évènements
        comme les cliques de la souris et les touches du claviers.
        """
        board, dragger = self._init_loop()

        while self.run:
            # Clock
            self.clock.tick(self.config.get_fps())
            # Mouse
            self.mouse_pos = pygame.mouse.get_pos()
            dragger.update_mouse(self.mouse_pos)
            # GUI
            self.game.update(self.clock.get_fps())

            #self.player_vs_ai('black', board, dragger)
            eval(self.config.gamemode)(board, dragger)

            # Si la file n'est pas vide, on récupère la commande et on essaye de l'exécuter
            if not self.command_listener.get_queue().empty():
                command = self.command_listener.get_command()
                self.command_listener.check_command(command)
                board = self.game.board
                dragger = self.game.dragger

            if not self.client.get_queue().empty():
                best_move: Move = self.client.get_data()[1]
                best_move.piece.set_sprite()
                self.ai.move(self.game, best_move)
            
            board, dragger = self.check_ButtonClick(board, dragger)

            pygame.display.update() 

        self.client.close()
        pygame.quit()

main = Main()
main.mainloop()