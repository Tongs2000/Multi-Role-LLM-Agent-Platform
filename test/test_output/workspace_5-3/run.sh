#!/bin/bash

# Install Python dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install Node dependencies for frontend
cd frontend
npm install
cd ..

# Create necessary directories
mkdir -p uploads temp_uploads

# Start Redis server in background
redis-server --daemonize yes

# Start FastAPI server in background
uvicorn src.main:app --reload &

# Start React frontend in background
cd frontend
npm start &

# Wait for all background processes
wait
