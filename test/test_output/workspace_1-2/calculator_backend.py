from flask import Flask, request, jsonify
import re

app = Flask(__name__)

# Optional: Database setup (SQLite for simplicity)
import sqlite3
from sqlite3 import Error

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect('calculator.db')
        print(f"SQLite connection established")
    except Error as e:
        print(e)
    return conn

def create_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS calculations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                expression TEXT NOT NULL,
                result TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("Table created successfully")
    except Error as e:
        print(e)

# Initialize database
conn = create_connection()
if conn is not None:
    create_table(conn)
else:
    print("Error: Cannot create database connection.")

# Helper function to validate expressions
def validate_expression(expression):
    # Basic validation: Only allow numbers, operators, and parentheses
    if not re.match(r'^[\d\+\-\*\/\(\)\.\s]+$', expression):
        return False
    try:
        eval(expression)  # Safe for basic arithmetic, but ensure no malicious input
        return True
    except:
        return False

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    expression = data.get('expression', '').strip()
    
    if not expression:
        return jsonify({'error': 'No expression provided'}), 400
    
    if not validate_expression(expression):
        return jsonify({'error': 'Invalid expression'}), 400
    
    try:
        result = eval(expression)
        
        # Log the calculation (optional)
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO calculations (expression, result) VALUES (?, ?)", (expression, str(result)))
            conn.commit()
        
        return jsonify({'result': result})
    except ZeroDivisionError:
        return jsonify({'error': 'Division by zero'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)