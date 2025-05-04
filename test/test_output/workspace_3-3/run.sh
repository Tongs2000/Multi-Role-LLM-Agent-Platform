#!/bin/bash

# Install Python dependencies
pip install -r requirements.txt

# Start Redis server in the background
redis-server --daemonize yes

# Start Flask backend in the background
python backend/app.py &

# Serve the frontend using Python's built-in HTTP server
cd frontend && python -m http.server 8000 &

chmod +x run_app.sh
./run_app.sh
