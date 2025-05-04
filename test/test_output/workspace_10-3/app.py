from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///shop.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv('SECRET_KEY', 'dev')

db = SQLAlchemy(app)

from models import Product, Cart
from routes import init_routes

with app.app_context():
    db.create_all()
    init_routes(app)

if __name__ == '__main__':
    app.run(debug=True)