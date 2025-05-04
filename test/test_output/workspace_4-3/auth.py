from flask_jwt_extended import create_access_token
from flask import jsonify
from models import User, db

def register(username, email, password):
    if User.query.filter_by(username=username).first():
        return {'error': 'Username already exists'}, 400
    if User.query.filter_by(email=email).first():
        return {'error': 'Email already exists'}, 400
    
    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    
    return {'message': 'User created successfully'}, 201

def login(username, password):
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return {'error': 'Invalid credentials'}, 401
    
    access_token = create_access_token(identity=user.id)
    return {'access_token': access_token}, 200