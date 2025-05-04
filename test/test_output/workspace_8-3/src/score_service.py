import requests
from typing import List, Dict, Optional

class ScoreService:
    def __init__(self, api_url: str = "http://localhost:5000"):
        self.api_url = api_url
    
    def submit_score(self, score: int, player_name: str = "Player") -> bool:
        try:
            response = requests.post(
                f"{self.api_url}/scores",
                json={"player": player_name, "score": score}
            )
            return response.status_code == 201
        except requests.exceptions.RequestException:
            return False
    
    def get_high_scores(self, limit: int = 10) -> List[Dict]:
        try:
            response = requests.get(f"{self.api_url}/scores?limit={limit}")
            return response.json()
        except requests.exceptions.RequestException:
            return []