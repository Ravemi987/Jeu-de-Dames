# ======= FICHIER SPECIFIQUE AU JEU =======
import pygame

# ==== PLATEAU ====
ROWS, COLS = 10, 10

# ==== IMAGES ====
ICON = pygame.image.load('assets/icon.ico')

# ==== COULEURS ====
BG = (49, 46, 43)

BLACK1 = (28, 27, 25)
BLACK2 = (55, 53, 50)
BLACK = (39, 37, 34)
GREY = (102, 101, 100)
GREY1 = (160, 160, 160)
GREY2 = (180, 180, 180)
GREY3 = (199, 198, 197)
WHITE1 = (220, 220, 220)
WHITE = (233, 233, 233)
GREEN = (129, 182, 76)

# ==== DOSSIERS DONNEES ====
DATA_PATH = "D:\Programmation_Python\Projets\Dames\Jeu-de-Dames\data"
BOARD_CONFIG_PATH = f"{DATA_PATH}\\board_config.json"
CMDS_CONFIG_PATH = f"{DATA_PATH}\commands.json"
