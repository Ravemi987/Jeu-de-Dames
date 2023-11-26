import pygame
from src.constants import *
from src.game import Game
from src.config import Config
from src.move import Move
from src.event_handler import EventHandler
import threading
import ctypes
from ctypes import wintypes
import pickle
import json
import os
import time

from ai_package.ai import AI
from src.command_listener import CommandListener
from communication.client import Client


if SYSTEM == "Windows":
    # Définir l'ID de l'application (AppUserModelID)
    myappid = u'ravemi_987.jeux.jeu_de_dames.5'
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

class MainClient:
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
        self.game = Game(self.config, self.config.board_config)
        self.command_listener = CommandListener(self.game)
        self.event_handler = EventHandler(self.game, self.config)
        self.client = None
        self.run = True

        if self.config.gamemode != 'self.player_vs_player':
            self.client = Client()
            self.ai_index = 0
            self.load_ai()
    
    def switch_ai(self):
        self.ai_index += 1
        self.ai_index %= len(self.ai_list)
        self.current_ai = self.ai_list[self.ai_index]
            
    def deserialize(self, serialized_data: str):
        """ 
        Nous utilisé latin1 pour encoder et décoder la chaîne afin de préserver 
        la correspondance univoque entre les octets et les caractères 
        lors de la transformation des données pickle encodées en une représentation 
        lisible. Cela permet de restaurer correctement l'objet pickle original.
        """
        # On élimine le préfixe <b'> et la fin <'> pour obtenir la représentation pickle
        pickle_string = serialized_data[2:-1].encode('latin1').decode('unicode_escape')
        # Désérialisez la représentation pickle
        deserialized_object = pickle.loads(pickle_string.encode('latin1'))
        return deserialized_object

    def load_ai(self):
        """ Créé plusieurs instances de la classe AI. """
        multiple_ai = self.config.gamemode == 'self.ai_vs_ai'

        with open(AI_OBJECTS_PATH, "r", encoding='UTF-8') as f:
            data = json.load(f)

        self.ai_list, ai_name_list = [], []

        if multiple_ai:
            ai_name_list = [
                f'{self.config.ai_1_engine}_{self.config.ai_1_color}',
                f'{self.config.ai_2_engine}_{self.config.ai_2_color}'    
            ]
        else:
            ai_name_list = [f'{self.config.ai_1_engine}_{self.config.ai_1_color}']

        for ai_name in ai_name_list:
            deserialized_ai = self.deserialize(data[ai_name])
            self.ai_list.append(deserialized_ai)

        self.client.send_ai(ai_list=self.ai_list, ai_switch=multiple_ai)
        self.current_ai: AI = self.ai_list[0]

    def ai_loop(self):
        """ Boucle principale qui gère l'IA. """
        while True:
            time.sleep(0.030)
            if self.current_ai.color == self.game.turn and not self.game.is_finished:
                if not self.client.is_close():
                    game_copy = self.game.copy()
                    self.client.apply_protocol(game_copy)

    def create_ai_thread(self):
        ai_thread = threading.Thread(target=self.ai_loop)
        ai_thread.daemon = True
        ai_thread.start()

    def update_clocks(self):
        """ Met à jour les pendules du jeu. """
        if self.game.has_start:
            self.game.elapsed_time = time.time() - self.game.start_time
            self.game.remaining_time = self.game.get_remaining_time() - self.game.elapsed_time
            if self.game.remaining_time < 0:
                self.game.remaining_time = 0

    def player_turn(self, board, dragger):
        """ 
        Permet au joueur humain de jouer un tour.
        Active le dragger, les cliques de la souris etc...
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run = False
            self.event_handler.check_event(event, board, dragger)

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

    def ai_vs_ai(self, board, dragger):
        """ Mode de jeu 'ordi contre ordi'. """
        if not self.game.has_start:
            self.game.start()

        if not self.game.is_finished:
            self.update_clocks()

        self.player_turn(board, dragger)

    def command_queue(self, board, dragger):
        if not self.command_listener.get_queue().empty():
            command = self.command_listener.get_command()
            self.command_listener.check_command(command)
            board = self.game.board
            dragger = self.game.dragger
        
        return board, dragger
    
    def client_queue(self):
        if self.client and not self.client.get_queue().empty():
            best_move: Move = self.client.get_data()
            best_move.piece.set_sprite()
            self.current_ai.move(self.game, best_move)
            self.switch_ai()

    def check_queues(self, board, dragger):
        board, dragger = self.command_queue(board, dragger)
        self.client_queue()

        return board, dragger

    def mainloop(self):
        """ 
        Boucle principal qui créé et démarre le thread et gère les évènements
        comme les cliques de la souris et les touches du claviers.
        """
        self.command_listener.create_thread()
        if self.config.gamemode != 'self.player_vs_player':
            self.create_ai_thread()

        board = self.game.board
        dragger = self.game.dragger
        self.previously_selected_piece = None

        while self.run:
            
            self.event_handler.get_clock().tick(self.config.get_fps()) # Clock
            self.event_handler.mouse_pos = pygame.mouse.get_pos() # Mouse
            dragger.update_mouse(self.event_handler.mouse_pos)
            self.game.update(self.event_handler.get_clock().get_fps()) # GUI

            eval(self.config.gamemode)(board, dragger)

            board, dragger = self.check_queues(board, dragger)
            board, dragger = self.event_handler.check_ButtonClick(board, dragger)

            pygame.display.update() 

        if self.client:
            self.client.close()
        pygame.quit()
