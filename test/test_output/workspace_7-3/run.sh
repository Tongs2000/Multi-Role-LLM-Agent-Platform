#!/bin/bash

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p uploads processed static/css static/js templates

# Run the Flask application
python app.py

chmod +x run_app.sh

./run_app.sh
