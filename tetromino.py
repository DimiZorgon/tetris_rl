import random
from settings import *

# Dictionnaires contenant les formes et chaque état de rotation.
# '0' = vide, '1' = un bloc de la pièce
SHAPES = {
    'S': [
        ['00000',
         '00000',
         '00110',
         '01100',
         '00000'],
        ['00000',
         '00100',
         '00110',
         '00010',
         '00000']
    ],
    'Z': [
        ['00000',
         '00000',
         '01100',
         '00110',
         '00000'],
        ['00000',
         '00010',
         '00110',
         '00100',
         '00000']
    ],
    'I': [
        ['00100',
         '00100',
         '00100',
         '00100',
         '00000'],
        ['00000',
         '11110',
         '00000',
         '00000',
         '00000']
    ],
    'O': [
        ['00000',
         '00000',
         '01100',
         '01100',
         '00000']
    ],
    'J': [
        ['00000',
         '01000',
         '01110',
         '00000',
         '00000'],
        ['00000',
         '00110',
         '00100',
         '00100',
         '00000'],
        ['00000',
         '00000',
         '01110',
         '00010',
         '00000'],
        ['00000',
         '00100',
         '00100',
         '01100',
         '00000']
    ],
    'L': [
        ['00000',
         '00010',
         '01110',
         '00000',
         '00000'],
        ['00000',
         '00100',
         '00100',
         '00110',
         '00000'],
        ['00000',
         '00000',
         '01110',
         '01000',
         '00000'],
        ['00000',
         '01100',
         '00100',
         '00100',
         '00000']
    ],
    'T': [
        ['00000',
         '00100',
         '01110',
         '00000',
         '00000'],
        ['00000',
         '00100',
         '00110',
         '00100',
         '00000'],
        ['00000',
         '00000',
         '01110',
         '00100',
         '00000'],
        ['00000',
         '00100',
         '01100',
         '00100',
         '00000']
    ]
}

class Tetromino:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.shape_type = random.choice(list(SHAPES.keys()))
        self.color = get_colors()[self.shape_type]
        self.rotation = 0
    
    @property
    def image(self):
        return SHAPES[self.shape_type][self.rotation]

    def rotate(self):
        self.rotation = (self.rotation + 1) % len(SHAPES[self.shape_type])
    
    def rotate_back(self):
        self.rotation = (self.rotation - 1) % len(SHAPES[self.shape_type])
        
    def get_blocks(self):
        """Retourne la position (en coordonnées de grille) de chaque bloc formant la pièce."""
        positions = []
        format = self.image
        
        for i, line in enumerate(format):
            for j, column in enumerate(line):
                if column == '1':
                    positions.append((self.x + j - 2, self.y + i - 4))
        return positions
