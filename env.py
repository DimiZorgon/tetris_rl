import pygame
import numpy as np
from game import Game
from settings import *
from tetromino import SHAPES

class TetrisEnv:
    def __init__(self):
        self.game = Game()
        self.last_reward = 0.0
        self.pieces_placed = 0

    def reset(self):
        self.game = Game()
        self.last_reward = 0.0
        self.pieces_placed = 0
        return self._get_state()

    def get_possible_states(self):
        states = {}
        piece = self.game.current_piece
        if not piece:
            return states

        original_x = piece.x
        original_y = piece.y
        original_rot = piece.rotation

        for rot in range(len(SHAPES[piece.shape_type])):
            piece.rotation = rot
            for x in range(COLS):
                piece.x = x
                piece.y = 0
                
                if not self.game.valid_space(piece):
                    continue
                
                while self.game.valid_space(piece):
                    piece.y += 1
                piece.y -= 1 
                
                states[(x, rot)] = self._get_state()

        piece.x = original_x
        piece.y = original_y
        piece.rotation = original_rot

        return states

    def step(self, action):
        target_x, target_rot = action
        old_score = self.game.score
        
        self.game.current_piece.x = target_x
        self.game.current_piece.rotation = target_rot

        from tetromino import Tetromino
        ghost = Tetromino(target_x, self.game.current_piece.y)
        ghost.shape_type = self.game.current_piece.shape_type
        ghost.rotation = target_rot
        
        while self.game.valid_space(ghost):
            ghost.y += 1
        ghost.y -= 1 

        contacts = 0
        for bx, by in ghost.get_blocks():
            if by == ROWS - 1 or (by + 1 < ROWS and self.game.grid[by+1][bx] != 0):
                contacts += 1
            if bx == 0 or (bx > 0 and self.game.grid[by][bx-1] != 0):
                contacts += 1
            if bx == COLS - 1 or (bx + 1 < COLS and self.game.grid[by][bx+1] != 0):
                contacts += 1

        while self.game.move_piece(0, 1):
            pass
            
        done = self.game.check_lost()
        
        reward = 0.0

        if not done:
            self.pieces_placed += 1
            reward += 0.1 

            reward += (contacts * 0.2)
            
            lignes_faites = (self.game.score - old_score) // 100
            if lignes_faites == 1:
                reward += 10.0
            elif lignes_faites == 2:
                reward += 40.0 
            elif lignes_faites == 3:
                reward += 100.0 
            elif lignes_faites >= 4:
                reward += 300.0 
            
            trous = 0
            for x in range(COLS): 
                block_found = False
                for y in range(ROWS): 
                    if self.game.grid[y][x] != 0:
                        block_found = True 
                    elif block_found and self.game.grid[y][x] == 0:
                        trous += 1 
            reward -= (trous * 0.5) 

        if done:
            reward -= 10.0 

        self.last_reward = reward

        return self._get_state(), reward, done

    def _get_state(self):
        grid_with_piece = self.game.create_grid_colors()
        numeric_grid = [[1 if cell != 0 else 0 for cell in row] for row in grid_with_piece]
        return self._get_features(numeric_grid)

    def _get_features(self, grid):
        grid_np = np.array(grid, dtype=bool) 
        
        has_blocks = grid_np.any(axis=0)
        first_blocks = np.argmax(grid_np, axis=0)
        hauteurs = np.where(has_blocks, ROWS - first_blocks, 0)
        hauteur_totale = np.sum(hauteurs)

        rugosite = np.sum(np.abs(np.diff(hauteurs)))
        trous = np.sum((np.cumsum(grid_np, axis=0) > 0) & (~grid_np))
        lignes = np.sum(grid_np.all(axis=1))

        puits = 0
        for x in range(COLS):
            for y in range(ROWS):
                if grid_np[y, x]:
                    break 
                left_filled = (x == 0) or grid_np[y, x-1]
                right_filled = (x == COLS - 1) or grid_np[y, x+1]
                if left_filled and right_filled:
                    puits += 1

        piece_names = ['I', 'J', 'L', 'O', 'S', 'T', 'Z']
        try:
            next_piece_idx = piece_names.index(self.game.next_piece.shape_type)
        except ValueError:
            next_piece_idx = 0
            
        next_piece_one_hot = [1.0 if i == next_piece_idx else 0.0 for i in range(7)]

        features = [lignes, trous, hauteur_totale, rugosite, puits] + next_piece_one_hot
        return np.array(features, dtype=np.float32)

    def render(self, screen):
        screen.fill(BLACK)
        grid_colors = self.game.create_grid_colors()
        for y in range(ROWS):
            for x in range(COLS):
                color = grid_colors[y][x]
                rect = (GRID_OFFSET_X + x * GRID_SIZE, GRID_OFFSET_Y + y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                if color == 0:
                    pygame.draw.rect(screen, BLACK, rect)
                    pygame.draw.rect(screen, GRAY, rect, 1)
                else:
                    pygame.draw.rect(screen, color, rect)
                    pygame.draw.rect(screen, BLACK, rect, 1)
        
        font = pygame.font.SysFont('Arial', 30)
        score_txt = font.render(f'Score: {self.game.score}', True, WHITE)
        screen.blit(score_txt, (20, 20))
        
        reward_txt = font.render(f'Reward: {self.last_reward:.1f}', True, (255, 200, 0))
        screen.blit(reward_txt, (20, 60))

        pieces_txt = font.render(f'Pieces: {self.pieces_placed}', True, (100, 255, 100))
        screen.blit(pieces_txt, (20, 100))
        
        pygame.display.update()