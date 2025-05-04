#!/bin/bash

# Install Python dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Initialize database
cd backend
python -c "from database import Base; from models import *; Base.metadata.create_all(bind=engine)"
cd ..

# Install Node dependencies
cd frontend
npm install
cd ..

# Run backend and frontend in parallel
uvicorn backend.main:app --reload & 
cd frontend && npm start
