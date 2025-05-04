#!/bin/bash

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run backend server in background
python backend/app.py &

# Run the game
python src/main.py

# Clean up
kill %1
deactivate
