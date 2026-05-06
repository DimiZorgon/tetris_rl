import pygame
from settings import *
from tetromino import Tetromino

class Game:
    def __init__(self):
        # Grille de jeu: stocke les couleurs des blocs fixés (0 = vide)
        self.grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        
        self.current_piece = self.get_new_piece()
        self.next_piece = self.get_new_piece()
        
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        
    def get_new_piece(self):
        return Tetromino(COLS // 2, 0)
    
    def create_grid_colors(self):
        """Retourne la grille colorée actuelle, en y ajoutant la pièce courante en mouvement"""
        grid_copy = [[self.grid[y][x] for x in range(COLS)] for y in range(ROWS)]
        
        if self.current_piece:
            blocks = self.current_piece.get_blocks()
            for x, y in blocks:
                if y > -1 and y < ROWS and x >= 0 and x < COLS:
                    grid_copy[y][x] = self.current_piece.color
        return grid_copy

    def valid_space(self, piece) -> bool:
        """Vérifie si la position de la pièce est valide (Version Ultra-Rapide)"""
        for x, y in piece.get_blocks():
            # 1. Vérifie si on sort des murs gauche/droite ou si on traverse le sol
            if x < 0 or x >= COLS or y >= ROWS:
                return False
            # 2. Vérifie si on rentre dans un bloc existant (on ignore y < 0 quand elle spawn en haut)
            if y >= 0 and self.grid[y][x] != 0:
                return False
        return True

    def check_lost(self):
        for x in range(COLS):
            if self.grid[0][x] != 0:
                self.game_over = True
                return True
        return False
        
    def lock_piece(self):
        """Bloque la pièce dans la grille et génère la suivante"""
        blocks = self.current_piece.get_blocks()
        for x, y in blocks:
            if y > -1:
                self.grid[y][x] = self.current_piece.color
                
        self.current_piece = self.next_piece
        self.next_piece = self.get_new_piece()
        self.clear_rows()
        self.check_lost()

    def clear_rows(self):
        """Enlève les lignes complètes et fait descendre le reste"""
        inc = 0
        for i in range(len(self.grid)-1, -1, -1):
            if 0 not in self.grid[i]:
                inc += 1
                for j in range(COLS):
                    self.grid[i][j] = 0
            elif inc > 0:
                for j in range(COLS):
                    self.grid[i + inc][j] = self.grid[i][j]
                    self.grid[i][j] = 0
                    
        # Update score
        if inc > 0:
            self.lines_cleared += inc
            if inc == 1: self.score += 100
            elif inc == 2: self.score += 300
            elif inc == 3: self.score += 500
            elif inc >= 4: self.score += 800
            
            self.level = 1 + self.score // SCORE_PER_LEVEL
                
    def move_piece(self, dx, dy):
        if not self.current_piece: return False
        
        self.current_piece.x += dx
        self.current_piece.y += dy
        if not self.valid_space(self.current_piece):
            self.current_piece.x -= dx
            self.current_piece.y -= dy
            if dy > 0: # Si la collision bas est atteinte
                self.lock_piece()
            return False
        return True
        
    def rotate_piece(self):
        if not self.current_piece: return
        self.current_piece.rotate()
        if not self.valid_space(self.current_piece):
            self.current_piece.rotate_back()
