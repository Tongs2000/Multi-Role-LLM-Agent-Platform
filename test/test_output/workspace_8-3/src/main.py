from game.game_engine import SnakeGame
from game.game_renderer import GameRenderer
from score_service import ScoreService

def main():
    score_service = ScoreService()
    game = SnakeGame()
    renderer = GameRenderer(game, score_service)
    
    while True:
        renderer.handle_events()
        game.update()
        renderer.render()
        
        if game.game_over:
            score_service.submit_score(game.score)
            break

if __name__ == "__main__":
    main()