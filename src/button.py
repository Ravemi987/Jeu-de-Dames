import pygame

class Button:
    """
    Un bouton est représenté par:
        - un id
        - une couleur de fond qui change si la souris est passée dessus
        - une couleur de texte
        - une largeur et une hauteur
        - l'arrondi des coins
        - la position sur l'écran (game.screen)
        - une commande lorsqu'il est cliqué
        - un police et une taille d'écriture
    """

    def __init__(self, id, screen: pygame.Surface, text, bg_color, text_color, 
                 width, height, border_radius, position, command, font, font_size):
        self.id = id
        self.bg_color = bg_color
        self.hover_color = [val + 10 for val in self.bg_color]
        self.text_color = text_color
        self.width = width
        self.height = height
        self.border_radius = border_radius
        self.position = position
        self.command = command
        self.screen = screen
        self.pressed = False

        self.font = pygame.font.Font(font, font_size)
        self.rect = pygame.Rect(self.position[0], self.position[1], self.width, self.height)
        self.button = pygame.Surface([self.width, self.height], pygame.SRCALPHA)
        self.text = self.font.render(text, True, text_color)

    def blit_text(self):
        """ Affiche le texte sur le bouton. """
        self.button.blit(self.text, [(self.width - self.text.get_width())//2, (self.height - self.text.get_height())//2])

    def draw(self):
        """ Dessine le bouton. (le rectangle) """
        pygame.draw.rect(self.button, self.bg_color, (0, 0, self.width, self.height), border_radius=self.border_radius)

    def hover(self):
        """ Change la couleur de fond si la souris survole le bouton. """
        x, y = pygame.mouse.get_pos()
        if self.rect.collidepoint([x, y]):
            self.bg_color = self.hover_color

    def click(self):
        """ Exécute la commande suite au click. """
        x, y = pygame.mouse.get_pos()
        if self.rect.collidepoint([x, y]):
            if pygame.mouse.get_pressed()[0] and not self.pressed:
                self.pressed = True
                self.command()

    def show(self):
        """ 
        Affiche le bouton :
            - dessine le bouton
            - affiche le texte par dessus)
            - dessine l'ensemble sur l'écran
            - Vérifie s'i faut exécuter la commande
        """
        self.hover()
        self.draw()
        self.blit_text()
        self.screen.blit(self.button, self.position)
        self.click()

    def __eq__(self, other):
        if isinstance(other, Button):
            return self.id == other.id
        return False
