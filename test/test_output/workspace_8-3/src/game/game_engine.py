from dataclasses import dataclass
from enum import Enum, auto
import random
from typing import List, Tuple

class Direction(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()

@dataclass
class Point:
    x: int
    y: int

class SnakeGame:
    def __init__(self, grid_size: int = 20, difficulty: str = "medium"):
        self.grid_size = grid_size
        self.snake: List[Point] = [Point(grid_size//2, grid_size//2)]
        self.direction = Direction.RIGHT
        self.food = self._generate_food()
        self.game_over = False
        self.score = 0
        self.speed = self._set_speed(difficulty)
        
    def _set_speed(self, difficulty: str) -> int:
        speeds = {
            "easy": 10,
            "medium": 15,
            "hard": 20
        }
        return speeds.get(difficulty, 15)
    
    def _generate_food(self) -> Point:
        while True:
            food = Point(
                random.randint(0, self.grid_size-1),
                random.randint(0, self.grid_size-1)
            )
            if food not in self.snake:
                return food
    
    def change_direction(self, new_direction: Direction):
        opposite_directions = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT
        }
        if new_direction != opposite_directions[self.direction]:
            self.direction = new_direction
    
    def _check_collision(self, head: Point) -> bool:
        # Check wall collision
        if (head.x < 0 or head.x >= self.grid_size or 
            head.y < 0 or head.y >= self.grid_size):
            return True
        # Check self collision
        if head in self.snake[1:]:
            return True
        return False
    
    def update(self):
        if self.game_over:
            return
            
        # Move snake
        head = self.snake[0]
        new_head = Point(head.x, head.y)
        
        if self.direction == Direction.UP:
            new_head.y -= 1
        elif self.direction == Direction.DOWN:
            new_head.y += 1
        elif self.direction == Direction.LEFT:
            new_head.x -= 1
        elif self.direction == Direction.RIGHT:
            new_head.x += 1
            
        # Check for collisions
        if self._check_collision(new_head):
            self.game_over = True
            return
            
        self.snake.insert(0, new_head)
        
        # Check if food eaten
        if new_head == self.food:
            self.score += 1
            self.food = self._generate_food()
        else:
            self.snake.pop()