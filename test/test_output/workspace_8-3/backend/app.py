from flask import Flask, request, jsonify
from typing import List, Dict
import sqlite3
from dataclasses import dataclass

app = Flask(__name__)

@dataclass
class Score:
    id: int
    player: str
    score: int
    timestamp: str

def init_db():
    conn = sqlite3.connect('scores.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS scores
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  player TEXT NOT NULL,
                  score INTEGER NOT NULL,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

@app.route('/scores', methods=['GET'])
def get_scores():
    limit = request.args.get('limit', default=10, type=int)
    
    conn = sqlite3.connect('scores.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM scores ORDER BY score DESC LIMIT ?', (limit,))
    scores = [dict(row) for row in c.fetchall()]
    conn.close()
    
    return jsonify(scores)

@app.route('/scores', methods=['POST'])
def add_score():
    data = request.get_json()
    if not data or 'player' not in data or 'score' not in data:
        return jsonify({"error": "Invalid data"}), 400
    
    conn = sqlite3.connect('scores.db')
    c = conn.cursor()
    c.execute('INSERT INTO scores (player, score) VALUES (?, ?)',
              (data['player'], data['score']))
    conn.commit()
    score_id = c.lastrowid
    conn.close()
    
    return jsonify({"id": score_id}), 201

if __name__ == '__main__':
    init_db()
    app.run(debug=True)