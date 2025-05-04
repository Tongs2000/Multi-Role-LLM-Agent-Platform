#!/bin/bash

# Install Python dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install Node dependencies
cd src
npm install
cd ..

# Create database and run Flask backend
python app.py &

# Run React frontend
cd src
npm start
