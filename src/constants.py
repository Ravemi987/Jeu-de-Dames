# ======= FICHIER SPECIFIQUE AU JEU =======
import pygame

# ==== PLATEAU ====
ROWS, COLS = 10, 10

# ==== IMAGES ====
ICON = pygame.image.load('assets/icon.ico')

# ==== COULEURS ====
BG = (49, 46, 43)
WHITE = (233, 233, 233)
BLACK = (39, 37, 34)
GREY1 = (64, 61, 57)
GREY2 = (79, 77, 73)

# ==== DOSSIERS DONNEES ====
DATA_PATH = "D:\Programmation_Python\Projets\Dames\Jeu-de-Dames\data"
BOARD_CONFIG_PATH = f"{DATA_PATH}\\board_config.json"
CMDS_CONFIG_PATH = f"{DATA_PATH}\commands.json"
