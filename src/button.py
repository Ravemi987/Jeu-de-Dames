import pygame

class Button:

    def __init__(self, name, screen: pygame.Surface, text, bg_color, text_color, 
                 width, height, border_radius, position, command, font, font_size):
        self.name = name
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
        self.button.blit(self.text, [(self.width - self.text.get_width())//2, (self.height - self.text.get_height())//2])

    def draw(self):
        pygame.draw.rect(self.button, self.bg_color, (0, 0, self.width, self.height), border_radius=self.border_radius)

    def hover(self):
        x, y = pygame.mouse.get_pos()
        if self.rect.collidepoint([x, y]):
            self.bg_color = self.hover_color

    def click(self):
        x, y = pygame.mouse.get_pos()
        if self.rect.collidepoint([x, y]):
            if pygame.mouse.get_pressed()[0] and not self.pressed:
                self.pressed = True
                self.command()

    def show(self):
        self.hover()
        self.draw()
        self.blit_text()
        self.screen.blit(self.button, self.position)
        self.click()

    def __eq__(self, other):
        if isinstance(other, Button):
            return self.name == other.name
        return False
