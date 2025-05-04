from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['JWT_SECRET_KEY'] = 'your-jwt-secret-key'

# Initialize extensions
socketio = SocketIO(app, cors_allowed_origins="*")
jwt = JWTManager(app)

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['chat_app']
users_collection = db['users']
messages_collection = db['messages']

# User registration
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if users_collection.find_one({'username': username}):
        return jsonify({'message': 'Username already exists'}), 400

    users_collection.insert_one({'username': username, 'password': password})
    return jsonify({'message': 'User registered successfully'}), 201

# User login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = users_collection.find_one({'username': username, 'password': password})
    if not user:
        return jsonify({'message': 'Invalid credentials'}), 401

    access_token = create_access_token(identity=username)
    return jsonify({'access_token': access_token}), 200

# WebSocket event for sending messages
@socketio.on('send_message')
@jwt_required()
def handle_send_message(data):
    username = get_jwt_identity()
    message = data.get('message')
    timestamp = datetime.now()

    # Save message to MongoDB
    messages_collection.insert_one({
        'username': username,
        'message': message,
        'timestamp': timestamp
    })

    # Broadcast the message to all clients
    emit('receive_message', {'username': username, 'message': message, 'timestamp': str(timestamp)}, broadcast=True)

# Fetch message history
@app.route('/messages', methods=['GET'])
@jwt_required()
def get_messages():
    messages = list(messages_collection.find({}, {'_id': 0}))
    return jsonify(messages), 200

if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)