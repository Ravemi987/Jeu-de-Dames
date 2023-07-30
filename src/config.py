import pygame
from .theme import Theme
from .screen import Screen
from .button import Button
from .constants import *

class Config:
    """
    Classe qui permet de gérer:
        - les thèmes
        - Les dimensions de la fenêtre de jeu,
        - les polices d'écritures
        - les fps
        - l'opacité
        - la clock (durée maximum et bonus de temps)
    """
    
    def __init__(self):
        pygame.font.init()
        self.themes, self.windows = [], []
        self.buttons_list = []
        self._add_themes()
        self._add_windows()
        self.theme_index, self.window_index = 0, 0
        self.theme = self.themes[self.theme_index]
        self.window = self.windows[self.window_index]
        self.digital_font = pygame.font.Font("assets/digital-7.regular.ttf", self.window.digital_font_size)
        self.text_font = pygame.font.Font("assets/recharge.rg-bold.otf", self.window.text_font_size)
        self.board_pos = (0, 0)
        self.fps = 120
        self.transparency = 255
        self.game_duration = 300
        self.bonus_time = 0

    def change_theme(self):
        """ Change le thème. """
        self.theme_index += 1
        self.theme_index %= len(self.themes)
        self.theme = self.themes[self.theme_index]

    def change_resolution(self):
        """ Change la résolution d'écran. """
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

        self.themes = [orange, green, brown, blue, gray, black]

    def _add_windows(self):
        """ Ajoute une résolution d'écran. """
        if SYSTEM == 'Windows':
            windowed = Screen(1920, 1080, 850, 850, 40)
            fullscreen = Screen(2560, 1440, 1100, 1100, 50)
        else:
            windowed = Screen(1280, 720, 600, 600, 27)   
            fullscreen = Screen(1600, 900, 750, 750, 35)

        self.windows = [windowed, fullscreen]

    def get_board_pos(self):
        """ Renvoi la position du plateau. """
        return self.board_pos

    def set_board_pos(self, pos):
        """ Place le plateau sur la fenêtre de jeu. """
        self.board_pos = pos

    def get_fps(self):
        """ Renvoi le framerate. """
        return self.fps

    def set_fps(self, fps):
        """ Met à jour le framerate. """
        self.fps = fps

    def get_transparency(self):
        """ Renvoi la valeur de l'opacité. """
        return self.transparency
    
    def set_tansparency(self, transparency):
        """ Met à jour l'opacité. """
        self.transparency = transparency

    def add_button(self, button):
        """ Ajoute un bouton. """
        self.buttons_list.append(button)

    def get_buttons_list(self) -> list[Button]:
        """ Renvoie la liste des boutons. """
        return self.buttons_list
