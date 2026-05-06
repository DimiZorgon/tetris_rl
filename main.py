import pygame
import sys
from settings import *
from game import Game
from tetromino import Tetromino

pygame.font.init()

class Main:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Tetris Premium')
        self.clock = pygame.time.Clock()
        self.state = MENU
        self.game = Game()
        self.font = pygame.font.SysFont('Arial', 30)
        self.large_font = pygame.font.SysFont('Arial', 60)
        
        self.fall_time = 0
        
    def draw_grid(self, surface, grid_colors):
        for y in range(ROWS):
            for x in range(COLS):
                color = grid_colors[y][x]
                rect = (GRID_OFFSET_X + x * GRID_SIZE, GRID_OFFSET_Y + y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                
                if color == 0:
                    pygame.draw.rect(surface, BLACK, rect)
                    pygame.draw.rect(surface, GRAY, rect, 1) # Grille fine
                else:
                    pygame.draw.rect(surface, color, rect)
                    pygame.draw.rect(surface, BLACK, rect, 1) # Bordure bloc

    def get_current_speed(self):
        speed = INITIAL_FALL_SPEED - (self.game.level - 1) * SPEED_INCREMENT
        return max(speed, MIN_FALL_SPEED)

    def draw_menu(self):
        self.screen.fill(BLACK)
        title = self.large_font.render('TETRIS', True, WHITE)
        self.screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 100))
        
        options = ["1. JOUER", "2. NIVEAUX", "3. COULEURS", "4. QUITTER"]
        for i, opt in enumerate(options):
            txt = self.font.render(opt, True, WHITE)
            self.screen.blit(txt, (WINDOW_WIDTH//2 - txt.get_width()//2, 250 + i * 50))
        pygame.display.update()

    def draw_level_select(self):
        self.screen.fill(BLACK)
        title = self.font.render('CHOISIR NIVEAU', True, WHITE)
        self.screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 100))
        
        for i in range(1, 6):
            txt = self.font.render(f"Niveau {i}", True, WHITE)
            self.screen.blit(txt, (WINDOW_WIDTH//2 - txt.get_width()//2, 200 + i * 40))
        pygame.display.update()

    def draw_settings(self):
        self.screen.fill(BLACK)
        title = self.font.render('PARAMÈTRES - COULEURS', True, WHITE)
        self.screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 100))
        
        theme_name = "Classic" if CURRENT_THEME_IDX == 0 else "Neon"
        txt = self.font.render(f"Thème Actuel: {theme_name}", True, WHITE)
        self.screen.blit(txt, (WINDOW_WIDTH//2 - txt.get_width()//2, 250))
        
        hint = self.font.render("Appuyez sur ESPACE pour changer", True, WHITE)
        self.screen.blit(hint, (WINDOW_WIDTH//2 - hint.get_width()//2, 350))
        pygame.display.update()

    def run(self):
        import settings # Pour modifier CURRENT_THEME_IDX
        run = True
        while run:
            if self.state == MENU:
                self.draw_menu()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: run = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_1: self.state = PLAYING
                        if event.key == pygame.K_2: self.state = LEVEL_SELECT
                        if event.key == pygame.K_3: self.state = SETTINGS
                        if event.key == pygame.K_4: run = False

            elif self.state == SETTINGS:
                self.draw_settings()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: run = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            settings.CURRENT_THEME_IDX = (settings.CURRENT_THEME_IDX + 1) % len(settings.THEMES)
                        if event.key == pygame.K_ESCAPE: self.state = MENU

            elif self.state == LEVEL_SELECT:
                self.draw_level_select()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: run = False
                    if event.type == pygame.KEYDOWN:
                        if pygame.K_1 <= event.key <= pygame.K_5:
                            self.game = Game()
                            self.game.level = event.key - pygame.K_0
                            self.state = PLAYING
                        if event.key == pygame.K_ESCAPE: self.state = MENU

            elif self.state == PLAYING:
                self.clock.tick(FPS)
                self.fall_time += self.clock.get_rawtime()
                
                speed = self.get_current_speed()
                if self.fall_time > speed:
                    self.fall_time = 0
                    if not self.game.move_piece(0, 1):
                        if self.game.check_lost():
                            self.state = MENU
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: run = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT: self.game.move_piece(-1, 0)
                        if event.key == pygame.K_RIGHT: self.game.move_piece(1, 0)
                        if event.key == pygame.K_UP: self.game.rotate_piece()
                        if event.key == pygame.K_DOWN: pass # Soft drop géré par vitesse ? non.
                
                # Gestion flèche bas (Soft Drop)
                keys = pygame.key.get_pressed()
                if keys[pygame.K_DOWN]:
                    if self.fall_time > FAST_FALL_SPEED:
                        self.fall_time = 0
                        self.game.move_piece(0, 1)

                self.draw_game()
        pygame.quit()

    def draw_game(self):
        self.screen.fill(BLACK)
        
        # Grille de base
        grid_colors = self.game.create_grid_colors()
        self.draw_grid(self.screen, grid_colors)
        
        # Ghost piece
        if self.game.current_piece:
            ghost = Tetromino(self.game.current_piece.x, self.game.current_piece.y)
            ghost.shape_type = self.game.current_piece.shape_type
            ghost.rotation = self.game.current_piece.rotation
            
            while self.game.valid_space(ghost):
                ghost.y += 1
            ghost.y -= 1
            
            for x, y in ghost.get_blocks():
                if y >= 0:
                    rect = (GRID_OFFSET_X + x * GRID_SIZE, GRID_OFFSET_Y + y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                    pygame.draw.rect(self.screen, (50, 50, 50), rect, 2)

        score_txt = self.font.render(f'Score: {self.game.score}', True, WHITE)
        level_txt = self.font.render(f'Niveau: {self.game.level}', True, WHITE)
        self.screen.blit(score_txt, (20, 20))
        self.screen.blit(level_txt, (20, 50))
        pygame.display.update()

if __name__ == '__main__':
    Main().run()
