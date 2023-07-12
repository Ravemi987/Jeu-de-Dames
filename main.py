import pygame
from src.constants import *
from src.game import Game
from src.config import Config
import threading
from queue import Queue
import ctypes
from ctypes import wintypes
import json, os, sys
import time


# Définir l'ID de l'application (AppUserModelID)
myappid = u'remi_airiau.jeux.jeu_de_dames.2'  # Chaîne arbitraire
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
        pygame.init()
        pygame.display.set_icon(ICON)
        pygame.display.set_caption('Jeu de Dames')
        self.config = Config()
        self.game = Game(self.config, 2)
        self.command_queue = Queue()

    def _init_loop(self):
        # On créé un nouveau thread
        input_thread = threading.Thread(target=self.input_thread)
        # Type de thread qui s'exécute en arrière-plan sans bloquer la fin de l'exécution du programme
        input_thread.daemon = True
        input_thread.start()

        board = self.game.board
        dragger = self.game.dragger
        previously_selected_piece = None

        return board, dragger, previously_selected_piece
    
    def check_command(self, user_input):
        """ 
        Charge la liste des commandes à partir du fichier de configuration
        correspondant. Ces commandes peuvent être exécutées à n'importe quel moment.
        """
        string_list = user_input.split(" ")

        with open(CMDS_CONFIG_PATH, "r", encoding='UTF-8') as f:
            commands = json.load(f)

        if string_list[0] in commands:
            try:
                method = commands[string_list[0]]
                eval(method)(*string_list[1::])
            except NameError:
                print(f"La commande '{string_list[0]}' n'est pas valide.")
            except OSError as err:
                print(err, file=sys.stderr)
        else:
            print("La commande que vous avez entré n'existe pas.")
    
    @staticmethod
    def print_commands():
        """ Exécutée lors de la commnade /help """
        with open(CMDS_CONFIG_PATH, "r", encoding='UTF-8') as f:
            data = json.load(f)

        commands = list(data.keys())
        for command in commands:
            print(f"- {command}\n")

    @staticmethod
    def print_configs():
        """ Exécutée lors de la commande /configs """
        with open(BOARD_CONFIG_PATH, "r", encoding='UTF-8') as f:
            data = json.load(f)

        config_names = list(data.keys())
        for config in config_names:
            print(f"- {config}\n")

    def get_pos_from_mouse(self, mouse_pos):
        """ 
        Renvoi la ligne et la colonne de la matrice de la case
        sur laquelle pointe notre souris.
        """
        x, y = mouse_pos
        row = y // self.config.window.square_size
        col = x // self.config.window.square_size
        
        return row, col
    
    def input_thread(self):
        """ Créé une boucle infinie qui demande simplement une entrée utilisateur. """
        while True:
            user_input = input()
            # 'put' ajoute un élément dans la file
            self.command_queue.put(user_input)

    def mainloop(self):
        """ 
        Boucle principal qui créé et démarre le thread et gère les évènements
        comme les cliques de la souris et les touches du claviers.
        """
        run = True
        clock = pygame.time.Clock()
        
        board, dragger, previously_selected_piece = self._init_loop()

        while run:
            self.game.elapsed_time = time.time() - self.game.start_time
            self.game.remaining_time = self.game.get_remaining_time() - self.game.elapsed_time
            if self.game.remaining_time < 0:
                self.game.remaining_time = 0

            clock.tick(self.config.get_fps())
            self.game.update(clock.get_fps())

            run = self.game.check_win()

            # pygame.event.get() renvoie une liste des actions (events)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                
                # Clique enfoncé (gauche ou droit)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    dragger.update_mouse(mouse_pos)
                    clicked_row, clicked_col = self.get_pos_from_mouse((dragger.mouseX, dragger.mouseY))
                    #print(f"mouse: {pygame.mouse.get_pos()}, dragger: {dragger.mouseX, dragger.mouseY}, origin: {self.config.get_board_pos()}, {clicked_row, clicked_col}, {self.config.window.square_size}")

                    window_check = dragger.in_window(mouse_pos[0], mouse_pos) and dragger.in_window(mouse_pos[1], mouse_pos)
                    if window_check and board.in_range(clicked_row, clicked_col) and not(board.is_empty_square(clicked_row, clicked_col)):
                        clicked_piece = board.get_piece(clicked_row, clicked_col)
                        dragger.drag_piece(clicked_piece)
                        self.game.select_piece(clicked_piece)
                        if not self.game.playing:
                            self.game.playing = True
                            self.game.start_time = time.time()
                    else:
                        if self.game.selected_piece is not None and self.game.selected_piece.color == self.game.turn:
                            can_move = self.game.move(clicked_row, clicked_col)
                            if not can_move:
                                self.game.unselect_piece()
                        else:
                            self.game.unselect_piece()

                    self.game.update(clock.get_fps())

                # Déplacement de la souris
                elif event.type == pygame.MOUSEMOTION:
                    hovered_row, hovered_col = self.get_pos_from_mouse((dragger.mouseX, dragger.mouseY))
                    self.game.set_hover(hovered_row, hovered_col)

                    if dragger.dragging:
                        dragger.update_mouse(pygame.mouse.get_pos())

                # Clique relâché (gauche ou droit)
                elif event.type == pygame.MOUSEBUTTONUP:
                    mouse_pos = pygame.mouse.get_pos()
                    dragger.update_mouse(mouse_pos)

                    released_row, released_col = self.get_pos_from_mouse((dragger.mouseX, dragger.mouseY))
                    window_check = dragger.in_window(mouse_pos[0], mouse_pos) and dragger.in_window(mouse_pos[1], mouse_pos)
                    # Check pas normal
                    if window_check and board.in_range(released_row, released_col):
                        released_piece = board.get_piece(released_row, released_col)

                    if previously_selected_piece is not None and released_piece == previously_selected_piece \
                            and clicked_piece == previously_selected_piece:
                        self.game.unselect_piece()
                    elif self.game.selected_piece is not None and self.game.selected_piece.color == self.game.turn:
                        self.game.move(released_row, released_col)
                    
                    dragger.undrag_piece()
                    previously_selected_piece = self.game.selected_piece

                # Touche 't' pour changer le thème
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_t:
                        self.game.change_theme()
                
                    elif event.key == pygame.K_F11:
                        self.game.change_resolution()

            # Si la file n'est pas vide, on récupère la commande et on essaye de l'exécuter
            if not self.command_queue.empty():
                command = self.command_queue.get()
                self.check_command(command)
                board, dragger, previously_selected_piece = self._init_loop()

            pygame.display.update() 

        pygame.quit()


main = Main()
main.mainloop()
