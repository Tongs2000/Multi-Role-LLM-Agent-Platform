from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Configure SQLite database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'todo.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define Task model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    category = db.Column(db.String(50))
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, nullable=True)  # For future authentication

    def __repr__(self):
        return f'<Task {self.title}>'

# Create database tables
with app.app_context():
    db.create_all()

# API Endpoints
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    return jsonify([{
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'category': task.category,
        'completed': task.completed,
        'created_at': task.created_at.isoformat(),
        'last_updated': task.last_updated.isoformat()
    } for task in tasks])

@app.route('/api/tasks', methods=['POST'])
@limiter.limit("10 per minute")
def add_task():
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400

    task = Task(
        title=data['title'],
        description=data.get('description', ''),
        category=data.get('category', 'General'),
        completed=data.get('completed', False),
        user_id=data.get('user_id')  # Optional for future use
    )
    db.session.add(task)
    db.session.commit()
    return jsonify({'message': 'Task added successfully'}), 201

@app.route('/api/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted successfully'}), 200

@app.route('/api/tasks/<int:id>', methods=['PATCH'])
def update_task(id):
    task = Task.query.get_or_404(id)
    data = request.get_json()

    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'category' in data:
        task.category = data['category']
    if 'completed' in data:
        task.completed = data['completed']

    db.session.commit()
    return jsonify({'message': 'Task updated successfully'}), 200

@app.route('/api/tasks/sync', methods=['POST'])
def sync_tasks():
    local_tasks = request.get_json()
    if not isinstance(local_tasks, list):
        return jsonify({'error': 'Invalid task list format'}), 400

    for local_task in local_tasks:
        task = Task.query.get(local_task.get('id'))
        if task:
            # Conflict resolution: Use the most recent update
            local_updated = datetime.fromisoformat(local_task.get('last_updated'))
            if local_updated > task.last_updated:
                task.title = local_task.get('title', task.title)
                task.description = local_task.get('description', task.description)
                task.category = local_task.get('category', task.category)
                task.completed = local_task.get('completed', task.completed)
        else:
            # Add new task
            task = Task(
                id=local_task.get('id'),
                title=local_task.get('title'),
                description=local_task.get('description', ''),
                category=local_task.get('category', 'General'),
                completed=local_task.get('completed', False),
                created_at=datetime.fromisoformat(local_task.get('created_at')),
                last_updated=datetime.fromisoformat(local_task.get('last_updated'))
            )
            db.session.add(task)
    db.session.commit()
    return jsonify({'message': 'Sync successful'}), 200

@app.route('/api/tasks/history', methods=['GET'])
def get_task_history():
    tasks = Task.query.order_by(Task.last_updated.desc()).limit(10).all()
    return jsonify([{
        'id': task.id,
        'title': task.title,
        'last_updated': task.last_updated.isoformat(),
        'action': 'updated'  # Simplified for demo
    } for task in tasks])

if __name__ == '__main__':
    app.run(debug=True)