from .constants import *
from .piece import Piece
from .move import Move
import json, os


class Board:
    """
    Le plateau de jeu est représenté par une matrice.
    L'objet a aussi pour attributs le nombre de pièces de chaque joueur
    ainsi que la dernière pièce déplacée.
    """

    def __init__(self, config, player):
        self.board = []
        self.black_pieces_left = 20 if config == 1 else len(self.get_team_pieces('black'))
        self.white_pieces_left = 20 if config == 1 else len(self.get_team_pieces('white'))
        self.last_move = None
        self.init_board(config, player)

    def get_piece(self, row, col) -> Piece:
        """ 
        Récupère les caractéristiques de la pièce contenue dans la case
        de coordonnées (row, col). Il faut d'abord vérifier que cette case n'est pas vide.
        """
        return self.board[row][col]
    
    def is_empty_square(self, row, col):
        """ Vérifie si une case du plateau est vide, c'est-à-dire ne contient pas d'objets Piece. """
        return self.board[row][col] == 0

    @staticmethod
    def in_range(row, col):
        """ Vérifie si les coordonnées (row, col) sont dans le plateau. """
        return (0 <= row < 10) and (0 <= col < 10)
    
    def is_in_range_and_empty(self, row, col):
        """ Vérifie les coordonnées (row, col) correspondent à une case vide du plateau. """
        return self.in_range(row, col) and self.is_empty_square(row, col)
    
    def get_team_pieces(self, color):
        """ 
        Renvoi sous forme de liste la totalité des pions appartenant au joueur courant.
        Réinitialise également la liste des déplacements de chaque pièce. 
        """
        team_pieces_list = []
        for row in range(len(self.board)):
            for col in range(len(self.board)):
                if not(self.is_empty_square(row, col)) and self.board[row][col].color == color:
                    piece = self.get_piece(row, col)
                    team_pieces_list.append(piece)

        return team_pieces_list
    
    def get_all_pieces(self) -> list[Piece]:
        """ Renvoi sous forme de liste la totalité des pions du plateau """
        pieces_list = []
        for row in range(len(self.board)):
            for col in range(len(self.board)):
                if not(self.is_empty_square(row, col)):
                    pieces_list.append(self.get_piece(row, col))
        return pieces_list

    def move_piece(self, move: Move):
        """ Déplace une pièce sur le plateau (sans prendre en compte les règles). """
        piece = self.get_piece(move.initial_pos[0], move.initial_pos[1])
        initial_pos, final_pos = move.get_initial_pos(), move.get_final_pos()

        # On déplace la pièce
        self.board[initial_pos[0]][initial_pos[1]] = 0
        self.board[final_pos[0]][final_pos[1]] = piece
        
        # On sauvegarde le dernier déplacement
        self.last_move = move

        # On actualise la position de la pièce et on vérifie si elle doit devenir une dame
        piece.update_pos(final_pos[0], final_pos[1])
        piece.check_promotion()
    
    def _add_piece(self, row, col, color, name, side):
        """ Ajoute une pièce sur le plateau. Par défaut, ce n'est pas une dame. """
        piece = Piece(row, col, color, name, side)
        self.board[row][col] = piece
        if color == 'white':
            self.white_pieces_left += 1
        else:
            self.black_pieces_left += 1
        
    def remove_pieces(self, skipped_pieces):
        """ 
        Supprime l'ensemble des pièces contenues dans la liste 'skipped_pieces'
        et qui ont été sautées suite à une capture. La liste contient au moins 1 élément.
        Met à jour le conmpteur des pièces.
        """
        for coords in skipped_pieces:
            piece = self.get_piece(coords[0], coords[1])
            self.board[piece.row][piece.col] = 0
            if piece.color == 'white':
                self.white_pieces_left -= 1
            else:
                self.black_pieces_left -= 1

    @staticmethod
    def print_valid_moves(valid_moves):
        """ Méthode utilitaire pour visualiser les déplacements valides. """
        for move in valid_moves:
            print(move)
        print('\n')
    
    @staticmethod
    def get_most_effective_move(possible_moves: list[Move]):
        """"
        Cherche le mouvement le plus efficace parmi tous les déplacements possibles
        de toutes les pièces. Il s'agit du déplacement qui n'est pas libre et dont
        la liste contient le plus de pions qui seraient capturés et éliminés du plateau.
        Si ce déplacement n'existe pas (il n'y a donc que des déplacements libres), on renvoie None.
        """
        most_effective_move: Move = None
        for move in possible_moves:
            if most_effective_move is None or len(move.get_skipped_list()) > len(most_effective_move.get_skipped_list()):
                most_effective_move = move

        return most_effective_move
    
    def _extract_valid_moves(self, possible_moves: list[Move], most_effective_move: Move):
        """"
        Extrait les déplacement qui ont la même valeur que le mouvement le plus efficient (most_effective_capture).
        Cela désigne les déplacement dont le nombre de pions capturés est le même.
        """
        valid_moves = []
        for move in possible_moves:
            if len(move.get_skipped_list()) == len(most_effective_move.get_skipped_list()):
                valid_moves.append(move)
        
        return valid_moves

    def _clean_possible_moves(self, possible_moves):
        """"
        Prend en paramètre une liste d'objets de types "Move" qui contient l'ensemble des
        déplacements possibles pour toutes les pièces, et renvoie une liste d'objets de même type
        qui contient l'ensemble des déplacements valides pour toutes les pièces.
        """
        # On cherche le déplacement qui permet de capturer le plus de pions possibles.
        most_effective_move = self.get_most_effective_move(possible_moves)

        # S'il existe, on cherche les déplacements similaires vis-à-vis de la règle.
        if most_effective_move is not None:
            return self._extract_valid_moves(possible_moves, most_effective_move)
        # Sinon, on retourne la liste d'origine car cela signifie qu'il n'y a aucune prise possible.
        else:
            return possible_moves

    def get_valid_moves(self, color_turn) -> list[Move]:
        """"
        Récupère l'ensemble des déplacements valides de toutes les pièces
        de couleur 'color_turn' présentes sur le plateau à un certain tour.
        La valeur de retour une liste qui contient des objets de la classe 'Move'.
        """
        possible_directions = [(-1, -1), (-1, 1), (1, 1), (1, -1)]
        last_dir = (0, 0)
        team_pieces_list = self.get_team_pieces(color_turn)
        possible_moves = []
        for piece in team_pieces_list:
            skipped_list = []
            start_position = (piece.row, piece.col)
            possible_moves.extend(self._get_piece_moves(piece, start_position, last_dir, skipped_list,
                                         possible_directions, piece.row, piece.col))
        
        valid_moves = self._clean_possible_moves(possible_moves)
        #self.print_valid_moves(valid_moves)
        
        return valid_moves


    def _get_piece_moves(self, piece: Piece, start_position, last_direction, skipped_list,
                  possible_directions, current_row, current_col):
        """
        Récupère l'ensemble des déplacements possibles d'une pièce.
        La valeur de retour est une liste d'objets de la classe 'Move.'
        """
        # Liste qui va contenir l'ensembles des déplacements de types 'Move'
        piece_moves = []
        for current_direction in possible_directions:
            # On vérifie que l'on ne revient pas "en arrière" ce qui pourrait provoquer des cas de récursion infinie.
            if current_direction == (-1 * last_direction[0], -1 * last_direction[1]):
                continue

            dx, dy = current_direction
            target_row, target_col = current_row + dx, current_col + dy

            # Vérification pour un potentiel déplacement libre
            if last_direction == (0, 0) and self.is_in_range_and_empty(target_row, target_col):
                is_free_move_available, piece_moves, target_row, target_col = self._check_free_moves(
                    piece, dx, dy, piece_moves, target_row, target_col
                )
                if is_free_move_available:
                    continue

            # On vérifie si l'on passe dans le cas d'arrêt ou dans le cas récursif
            can_continue_recurion, updated_coords = self._check_recursion_stop_condition(
                current_direction, piece, target_row, target_col
            )

            if not can_continue_recurion:
                continue
            else:
                target_row, target_col = updated_coords
                new_target_row, new_target_col = target_row + dx, target_col + dy
                
                if self.is_in_range_and_empty(new_target_row, new_target_col) and (new_target_row, new_target_col) != start_position:
                    # On met à jour la dernière direction parcourue et la liste des pièces capturées.
                    new_last_dir = current_direction
                    skipped = skipped_list + [(target_row, target_col)]
                    # On ajoute le nouveau déplacement et on appelle la fonction récursivement
                    piece_moves.append(Move((piece.row, piece.col), (new_target_row, new_target_col), skipped))
                    piece_moves.extend(self._get_piece_moves(piece, start_position, new_last_dir, skipped,
                                                     possible_directions, new_target_row, new_target_col))
        return piece_moves
    
    def _check_diagonal_squares(self, dx, dy, row, col, append_empty_squares=False):
        """
        A partir d'une position de départ (row, col), vérifie le contenu de toutes les cases
        situées en diagonale dans la direction (row + dx, col + dy) jusqu'à sortir du plateau 
        ou bien arriver dans une situation ou on pourrait potentiellement effectuer une capture.
        On peut décider de récupérer la liste des cases vides qui peuvent être ajoutées aux 
        déplacements possibles pour une dame.
        """
        move_row, move_col = row, col
        squares_list = []
        while self.is_in_range_and_empty(move_row, move_col):
            if append_empty_squares:
                squares_list.append((move_row, move_col))
            move_row += dx
            move_col += dy
        if append_empty_squares:
            return move_row, move_col, squares_list
        return move_row, move_col
    
    def _check_free_moves(self, piece:Piece, dx, dy, piece_moves, row, col):
        """
        S'occupe de la partie "déplacement libre" de la fonction récursive '_get_piece_moves'.
        Si un déplacement libre est possible, on renvoie True ainsi que la liste des déplacements mise à jour.
        La liste des pièces capturées est alors une liste vide '[]'.
        Dans tous les cas, il faut mettre à jour et renvoyer row et col car si la pièce est une dame et que
        le déplacement libre n'est pas possible, il faut pouvoir vérifier la capture (cas d'arrêt et cas récursif)
        à partir de la nouvelle position sur la diagonale suite à l'appel de la fonction ci-dessus.
        Si l'on ne sait pas encore si pour une dame une déplacement libre est valide, on le compte comme possible
        et on renvoie False, laissant ainsi la vérification aux fonctions de tris.
        """
        if not piece.is_queen():
            if dx == piece.direction:
                piece_moves.append(Move((piece.row, piece.col), (row, col), []))
                return True, piece_moves, row, col
        else:
            row, col, empty_squares_list = self._check_diagonal_squares(dx, dy, row, col, True)
            for square in empty_squares_list:
                piece_moves.append(Move((piece.row, piece.col), (square[0], square[1]), []))

        return False, piece_moves, row, col
    
    def _check_recursion_stop_condition(self, direction, piece: Piece, row, col):
        """
        S'occupe du cas d'arrêt de la fonction récursive '_get_piece_moves'.
        Soit la capture n'est pas possible donc on renvoie le couple (False, None), soit
        la capture est possible est on renvoie (True, (row, col)) où (row, col) sont les coordonnées
        de la pièce qui peut être sautée.
        """
        if piece.is_queen():
            row, col = self._check_diagonal_squares(direction[0], direction[1], row, col)
            
        if not(self.in_range(row, col)) or self.is_empty_square(row, col) \
                or self.board[row][col].color == piece.color:
            return False, None
        
        return True, (row, col)

    def _init_empty_board(self):
        """ Créé un plateau 'vide' dont les cases vides sont représentées par 0. """
        for row in range(ROWS):
            self.board.append([])
            for _ in range(COLS):
                self.board[row].append(0)

    def _init_starting_board(self, player_side):
        """ Créé le plateau de départ des jeux de dames, 20 pions dans chaque équipe. """
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                # Les pièces sont uniquement sur les cases foncées
                if col % 2 == ((row + 1) % 2):
                    if row < 4:
                        if player_side == "bottom":
                            self.board[row].append(Piece(row, col, 'black', side=player_side)) 
                        else:
                            self.board[row].append(Piece(row, col, 'white', side=player_side))
                    elif row > 5:
                        if player_side == "bottom":
                            self.board[row].append(Piece(row, col, 'white', side=player_side))  
                        else:
                            self.board[row].append(Piece(row, col, 'black', side=player_side))
                    else:
                        # 0 est la case vide
                        self.board[row].append(0)
                else:
                    # Les cases claires sont forcément vides
                    self.board[row].append(0)

    def save_board_config(self, config_name): 
        """ 
        Sauvegarde la configuration acutelle du plateau dans un fichier json.
        Cette configuration pourra ainsi être chargée afin d'effectuer des tests, de débugger le code
        ou de jouer.
        """
        if os.path.getsize(BOARD_CONFIG_PATH) == 0:
            config_dict = {}
        else:
            with open(BOARD_CONFIG_PATH, "r", encoding='UTF-8') as f:
                config_dict = json.load(f)
        
        pieces_list = self.get_all_pieces()
        config_dict[config_name] = {}
        for i, piece in enumerate(pieces_list):
            piece_infos = {
                "row": piece.row,
                "col": piece.col,
                "color": piece.color,
                "name": piece.name
            }
            config_dict[config_name][f"piece_{i+1}"] = piece_infos

        with open(BOARD_CONFIG_PATH, "w", encoding='UTF-8') as f:
            json.dump(config_dict, f, indent=4, ensure_ascii=False)

        print(f"Configuration du plateau enregistrée sous le nom '{config_name}'.")

    def _init_custom_board(self, config_name, player_side):
        """ 
        Permet de créer un plateau de jeu selon la configuration enregistrée sous le nom
        'config_name' dans le fichier de configuration.
        """
        with open(BOARD_CONFIG_PATH, "r", encoding='UTF-8') as f:
            data = json.load(f)
        
        self._init_empty_board()
        board_config = data[config_name]
        for piece in board_config:
            if player_side == "bottom":
                row =  board_config[piece]['row']
                col = board_config[piece]['col']
            else:
                row =  ROWS - 1 - board_config[piece]['row']
                col = COLS - 1 - board_config[piece]['col']
            color = board_config[piece]['color']
            name = board_config[piece]['name']
            
            self._add_piece(row, col, color, name, player_side)

    def init_board(self, config, player_side):
        """ Charge la configuration de plateau de numéro 'config' à partir du fichier json. """
        with open(BOARD_CONFIG_PATH, "r", encoding='UTF-8') as f:
            data = json.load(f)

        config_names = list(data.keys())

        # Plateau vide
        if int(config) == 1:
            self._init_starting_board(player_side)
        # Configuration de départ
        elif int(config) in range(len(config_names)):
            self._init_custom_board(config_names[int(config)], player_side)
        else:
            print("Configuration non trouvée.")
            self._init_empty_board()
