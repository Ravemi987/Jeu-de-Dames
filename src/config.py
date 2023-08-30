import pygame
from .theme import Theme
from .screen import Screen
from .button import Button
from .constants import *
import pickle
import json
import os


class Config:
    """
    Classe qui permet de gérer:
        - les thèmes
        - Les dimensions de la fenêtre de jeu,
        - les polices d'écritures
        - les fps
        - la clock (durée maximum et bonus de temps)
    """
    
    def __init__(self, copy=False):
        
        self.themes, self.windows = [], []
        self.buttons_list = []
        self.board_pos = (0, 0)

        # Si la configuration est une copie, alors c'est une simulation.
        # Pas besoin d'interface graphique
        if not copy:
            self.init_settings()
            self.init_GUI()
            self.dump_ai_objects()

    def init_settings(self):
        """ Initialise les attributs liés au jeu à partir du fichier settings. """
        with open(SETTINGS_PATH, "r", encoding='UTF-8') as f:
            settings: dict = json.load(f)

        settings_keys: list[str] = list(settings.keys())
        for setting_key in settings_keys:
            setattr(self, setting_key, settings[setting_key])

    def init_GUI(self):
        """ 
        Méthode publique appelée uniquement si la configuration 
        nécessite un affichage graphique.
        """
        self._add_themes()
        self._add_windows()
        self.theme_index, self.window_index = 0, 0
        self.theme = self.themes[self.theme_index]
        self.window = self.windows[self.window_index]
        pygame.font.init()
        self.set_font()

    def dump_ai_objects(self):
        """ 
        Initialise des objets de la classe IA
        et les intègrent au fichier de configuration.
        """
        from ai_package.ai import AI

        ai_dict = {}

        for file_name in os.listdir(AI_PACKAGE_PATH):
            if file_name not in ['__pycache__', '__init__.py', 'ai.py', 'args.json']:
                module_name = os.path.splitext(file_name)[0]
                module = __import__(f'ai_package.{module_name}', fromlist=[''])

                for color in ['white', 'black']:
                    ai_dict[f'{module_name}_{color}'] = str(pickle.dumps(AI(module_name, module.MAIN_FUNC, color)))
            
        with open(AI_OBJECTS_PATH, "w", encoding='UTF-8') as f:
            json.dump(ai_dict, f, indent=4, ensure_ascii=False)

    def set_font(self):
        """ Récupère les polices de caractères. """
        self.digital_font = pygame.font.Font("assets/digital-7.regular.ttf", self.window.digital_font_size)
        self.text_font = pygame.font.Font("assets/recharge.rg-bold.otf", self.window.text_font_size)

    def change_theme(self):
        self.theme_index += 1
        self.theme_index %= len(self.themes)
        self.theme = self.themes[self.theme_index]

    def change_resolution(self):
        self.window_index += 1
        self.window_index %= len(self.windows)
        self.window = self.windows[self.window_index]
        self.digital_font = pygame.font.Font("assets/digital-7.regular.ttf", self.window.digital_font_size)
        self.text_font = pygame.font.Font("assets/recharge.rg-bold.otf", self.window.text_font_size)

    def _add_themes(self):
        """ 
        light_background, dark_background, 
        selected_piece_color, valid_moves_color, 
        selected_hover_color, light_hover_color, dark_hover_color
        """
        orange = Theme((234, 233, 210), (209, 139, 71), (245, 185, 125), (186, 123, 61), (247, 195, 143), (249, 249, 239), (217, 224, 209))
        green = Theme((238, 238, 210), (118, 150, 86), (187, 203, 43), (106, 135, 77), (252, 252, 203), (249, 249, 239), (207, 218, 196))
        brown = Theme((240, 217, 181), (181, 136, 99), (218, 196, 49), (163, 122, 89), (242, 234, 183), (250, 242, 229), (229, 213, 201))
        blue = Theme((234, 233, 210), (75, 115, 153), (37, 140, 204), (67, 103, 137), (179, 215, 237), (248, 247, 239), (192, 206, 219))
        gray = Theme((220, 220, 220), (171, 171, 171), (167, 177, 183), (154, 154, 154), (224, 228, 230), (243, 243, 243), (226, 226, 226))
        black = Theme((242, 235, 228), (89, 87, 84), (171, 165, 155), (56, 55, 53), (194, 187, 176), (250, 248, 245), (77, 75, 72))

        self.themes = [green, brown, blue, gray, black, orange]

    def _add_windows(self):
        """ Ajoute une résolution d'écran. """
        if SYSTEM == 'Windows':
            windowed = Screen(1920, 1080, 850, 850, 40)
            fullscreen = Screen(2560, 1440, 1100, 1100, 50)
        else:
            windowed = Screen(1280, 720, 600, 600, 27)   
            fullscreen = Screen(1600, 900, 750, 750, 35)

        self.windows = [windowed, fullscreen]

    def get_fps(self):
        return self.fps

    def get_board_pos(self):
        return self.board_pos

    def set_board_pos(self, pos):
        self.board_pos = pos

    def add_button(self, button):
        self.buttons_list.append(button)

    def get_buttons_list(self) -> list[Button]:
        return self.buttons_list

    def set_game_duration(self, duration=600):
        """ Met à jour la durée de l'horloge. """
        self.game_duration = duration

    def set_time_increment(self, time=2):
        """ Modifie le temp rajouté à chaque joueur au début de son tour. """
        self.increment = time
