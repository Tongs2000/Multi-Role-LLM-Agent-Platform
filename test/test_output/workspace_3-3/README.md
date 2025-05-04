# Weather Application

A full-stack weather application with Flask backend and JavaScript frontend.

## Features
- City search for weather information
- Current weather display with temperature, humidity, wind speed
- 5-day forecast with chart visualization
- Temperature unit conversion (Celsius/Fahrenheit)
- Caching for API responses

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up Redis server
4. Create `.env` file with your OpenWeatherMap API key
5. Run the backend: `python backend/app.py`
6. Open `frontend/index.html` in your browser

## Requirements
- Python 3.7+
- Redis server
- OpenWeatherMap API key