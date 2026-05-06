# Paramètres généraux
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 600
GRID_SIZE = 30 # Taille d'un bloc en pixels
COLS = WINDOW_WIDTH // GRID_SIZE
ROWS = WINDOW_HEIGHT // GRID_SIZE

FPS = 60

# Couleurs (R, G, B)
BLACK = (10, 10, 15)
WHITE = (240, 240, 240)
GRAY = (40, 40, 50)  # Plus fin pour la grille
HIGHLIGHT = (255, 255, 255, 50)

# Thèmes de couleurs
THEMES = [
    { # Classic
        'I': (0, 255, 255), 'J': (0, 0, 255), 'L': (255, 165, 0),
        'O': (255, 255, 0), 'S': (0, 255, 0), 'T': (128, 0, 128), 'Z': (255, 0, 0)
    },
    { # Neon
        'I': (255, 0, 255), 'J': (0, 255, 127), 'L': (255, 20, 147),
        'O': (0, 191, 255), 'S': (50, 205, 50), 'T': (255, 165, 0), 'Z': (220, 20, 60)
    }
]

CURRENT_THEME_IDX = 0

def get_colors():
    return THEMES[CURRENT_THEME_IDX]

# Mapping de la grille
GRID_OFFSET_X = (WINDOW_WIDTH - (COLS * GRID_SIZE)) // 2
GRID_OFFSET_Y = WINDOW_HEIGHT - (ROWS * GRID_SIZE)

# Vitesse initiale de chute (en ms par déplacement vers le bas)
INITIAL_FALL_SPEED = 600
FAST_FALL_SPEED = 50 

# Paramètres de niveau
SCORE_PER_LEVEL = 1000
SPEED_INCREMENT = 50
MIN_FALL_SPEED = 100

# États du jeu
MENU = 0
PLAYING = 1
SETTINGS = 2
LEVEL_SELECT = 3

