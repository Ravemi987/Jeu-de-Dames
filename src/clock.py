import pygame
from .config import Config
from .constants import *
import math

class Clock:
    """
        - config: permet d'obtenir toutes les informations permettant de placer 
            l'horloge sur l'écran (taille du plateau, emplacement du plateau, etc...)
        - screen: fenêtre de l'application
        - remaining_time: temps restant pour le joueur courant
        - height_pos: référence en x pour placer l'horloge:
            - board_height (taille du plateau) pour en bas à droite
            - 0 pour en haut à droite
        - width_pos: référence en y pour placer l'horloge (c'est un coefficient):
            - 1 pour en bas à droite
            - (-3) pour en haut à droite
    """

    def __init__(self, config: Config, screen: pygame.Surface, color,
                 remaining_time, player_side):
        self.config = config
        self.screen = screen
        self.color = color
        self.remaining_time = remaining_time
        self.bg_color = None
        self.text_color = None
        self.height_pos = 0
        self.width_pos = 0
        self.side = player_side
        self.ticking = False

    def set_colors(self):
        """ Définit les couleurs. """
        if self.color == 'white':
            self.bg_color, self.text_color = (WHITE, BLACK) if self.ticking else (WHITE1, GREY1)
        else:
            self.bg_color, self.text_color = (BLACK, WHITE) if self.ticking else (BLACK1, GREY2)

    def set_pos(self):
        """ Définit la position de l'horlgoe (en haut ou en bas). """
        if self.color == 'white':
            self.height_pos, self.width_pos = \
            (self.config.window.board_height, 1) if self.side == "bottom" else (0, -3)
        else:
            self.height_pos, self.width_pos = \
                (self.config.window.board_height, 1) if self.side == "top" else (0, -3)

    def set_remaining_time(self, time):
        """ Définit le temps restant. """
        self.remaining_time = time

    def pause(self):
        """ Met en pause la clock. """
        self.ticking = False

    def tick(self):
        """ Démarre la clock. """
        self.ticking = True

    def draw(self):
        """ 
        Dessine le rectangle et le timer de l'horloge. 
        On choisit la taille d'une case du plateau comme référence pour la taille de l'horloge
        et ainsi obtenir un affichage satifsaisant. 
        On aurait très bien pu choisir une autre valeur / variable comme référence
        """
        square_size = self.config.window.square_size 
        self.clock_width, self.clock_height = 0.95 * 2 * square_size, 0.6 * square_size
        board_origin = self.config.get_board_pos()

        self.clock_origin = [(board_origin[0] + self.config.window.board_width) - 0.95 * 2 * square_size, 
                        (board_origin[1] + self.height_pos) + self.width_pos * self.clock_height // 2]

        min, sec = int(self.remaining_time // 60), int(self.remaining_time % 60)
        time_text = "{:02d}:{:02d}".format(min, sec)
        self.text_surface = self.config.digital_font.render(time_text, True, self.text_color)
        self.clock = pygame.Surface([self.clock_width, self.clock_height], pygame.SRCALPHA)
        pygame.draw.rect(self.clock, self.bg_color, (0, 0, self.clock_width, self.clock_height), border_radius=15)

    def show(self):
        """ 
        Affiche la clock:
            - Le rectangle et le timer si pause
            - le rectangle, l'animation de l'horloge et le timer en direct sinon
        """
        if self.ticking:
            # Aiguille
            hand_length = - (self.clock_height // 5)
            angle = - (math.pi / 2) * (5 - (int(self.remaining_time % 4) + 1))
            center_x, center_y = self.clock_height // 2, self.clock_height // 2

            # Calcul des coordonnées de l'extrémité de l'aiguille
            end_x = center_x + math.cos(angle) * hand_length
            end_y = center_y - math.sin(angle) * hand_length

            # Création d'une liste de points pour dessiner l'aiguille avec des coins arrondis
            points = [(center_x, center_y), (end_x, end_y)]

            # Dessin de l'aiguille avec coins arrondis
            pygame.draw.lines(self.clock, self.text_color, True, points, 4)
            pygame.draw.circle(self.clock, self.text_color, (center_x, center_y), radius=self.clock_height//3, width=3)

        self.screen.blit(self.clock, self.clock_origin)
        self.screen.blit(self.text_surface, (self.clock_origin[0] + self.clock_width // 2 - 10, 
                                             self.clock_origin[1] + (self.clock_height - self.text_surface.get_height()) // 2))

    def update(self):
        """ Mise à jour. """
        self.set_pos()
        self.set_colors()
        self.draw()
        self.show()
