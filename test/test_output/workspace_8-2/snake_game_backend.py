from flask import Flask, request, jsonify
from datetime import datetime
import sqlite3
import os

# Initialize Flask app
app = Flask(__name__)

# Database setup
DATABASE = 'highscores.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists(DATABASE):
        conn = get_db_connection()
        conn.execute('''
            CREATE TABLE IF NOT EXISTS highscores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                playerName TEXT,
                score INTEGER NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

# Initialize the database
init_db()

@app.route('/api/highscore', methods=['GET'])
def get_highscore():
    conn = get_db_connection()
    highscore = conn.execute('SELECT * FROM highscores ORDER BY score DESC LIMIT 1').fetchone()
    conn.close()
    if highscore:
        return jsonify({
            'playerName': highscore['playerName'],
            'score': highscore['score'],
            'timestamp': highscore['timestamp']
        })
    return jsonify({'message': 'No high scores yet'}), 404

@app.route('/api/highscore', methods=['POST'])
def update_highscore():
    data = request.get_json()
    if not data or 'score' not in data:
        return jsonify({'error': 'Invalid data'}), 400

    # Validate score
    try:
        score = int(data['score'])
        if score < 0:
            return jsonify({'error': 'Score cannot be negative'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid score format'}), 400

    player_name = data.get('playerName', 'Anonymous')
    timestamp = datetime.now().isoformat()

    conn = get_db_connection()
    conn.execute(
        'INSERT INTO highscores (playerName, score, timestamp) VALUES (?, ?, ?)',
        (player_name, score, timestamp)
    )
    conn.commit()
    conn.close()

    return jsonify({'message': 'High score updated successfully'}), 201

if __name__ == '__main__':
    app.run(debug=True)