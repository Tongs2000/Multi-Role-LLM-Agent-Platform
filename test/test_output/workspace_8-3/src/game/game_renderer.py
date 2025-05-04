import pygame
from typing import Optional
from game.game_engine import Direction, SnakeGame
from score_service import ScoreService

class GameRenderer:
    def __init__(self, game: SnakeGame, score_service: ScoreService, 
                 cell_size: int = 20, margin: int = 20):
        self.game = game
        self.score_service = score_service
        self.cell_size = cell_size
        self.margin = margin
        self.width = game.grid_size * cell_size + 2 * margin
        self.height = game.grid_size * cell_size + 2 * margin + 40  # Extra space for score
        
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.game.change_direction(Direction.UP)
                elif event.key == pygame.K_DOWN:
                    self.game.change_direction(Direction.DOWN)
                elif event.key == pygame.K_LEFT:
                    self.game.change_direction(Direction.LEFT)
                elif event.key == pygame.K_RIGHT:
                    self.game.change_direction(Direction.RIGHT)
    
    def render(self):
        self.screen.fill((0, 0, 0))
        
        # Draw score
        score_text = self.font.render(f"Score: {self.game.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (self.margin, self.margin // 2))
        
        # Draw game area
        game_area = pygame.Rect(
            self.margin,
            self.margin + 30,
            self.game.grid_size * self.cell_size,
            self.game.grid_size * self.cell_size
        )
        pygame.draw.rect(self.screen, (50, 50, 50), game_area)
        
        # Draw snake
        for segment in self.game.snake:
            rect = pygame.Rect(
                self.margin + segment.x * self.cell_size,
                self.margin + 30 + segment.y * self.cell_size,
                self.cell_size,
                self.cell_size
            )
            pygame.draw.rect(self.screen, (0, 255, 0), rect)
        
        # Draw food
        food_rect = pygame.Rect(
            self.margin + self.game.food.x * self.cell_size,
            self.margin + 30 + self.game.food.y * self.cell_size,
            self.cell_size,
            self.cell_size
        )
        pygame.draw.rect(self.screen, (255, 0, 0), food_rect)
        
        if self.game.game_over:
            self._render_game_over()
        
        pygame.display.flip()
        self.clock.tick(self.game.speed)
    
    def _render_game_over(self):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = self.font.render("GAME OVER", True, (255, 255, 255))
        score_text = self.font.render(f"Final Score: {self.game.score}", True, (255, 255, 255))
        
        self.screen.blit(game_over_text, 
                        (self.width//2 - game_over_text.get_width()//2, 
                         self.height//2 - 50))
        self.screen.blit(score_text, 
                        (self.width//2 - score_text.get_width()//2, 
                         self.height//2))