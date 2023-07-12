class Theme:
    """ Classe qui gère les couleurs des différents thèmes. """
    
    def __init__(self, light_background, dark_background, 
                    selected_piece_color, valid_moves_color, 
                    selected_hover_color, light_hover_color, dark_hover_color):
        self.light_background = light_background
        self.dark_background = dark_background
        self.selected_piece_color =  selected_piece_color
        self.valid_moves_color = valid_moves_color
        self.selected_hover_color = selected_hover_color
        self.light_hover_color = light_hover_color
        self.dark_hover_color = dark_hover_color
