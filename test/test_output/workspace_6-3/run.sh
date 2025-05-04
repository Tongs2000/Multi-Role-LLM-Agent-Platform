#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Create database file if it doesn't exist
touch chat.db

# Run FastAPI server in background
uvicorn src.main:app --reload &

# Serve static files (HTML, CSS, JS) using Python's built-in HTTP server
cd static && python -m http.server 8001 &
