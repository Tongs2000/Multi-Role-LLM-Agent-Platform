from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from cachetools import TTLCache

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Cache setup (10-minute TTL)
cache = TTLCache(maxsize=100, ttl=600)

# Open-Meteo API base URL
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

@app.route('/weather', methods=['GET'])
def get_weather():
    latitude = request.args.get('latitude', type=float)
    longitude = request.args.get('longitude', type=float)
    units = request.args.get('units', default='celsius', type=str)
    
    if not latitude or not longitude:
        return jsonify({"error": "Latitude and longitude are required"}), 400
    
    cache_key = f"{latitude}_{longitude}_{units}"
    
    # Check cache
    if cache_key in cache:
        return jsonify(cache[cache_key])
    
    # Define parameters for Open-Meteo
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
        "hourly": "temperature_2m",
        "temperature_unit": units[:1].lower()  # "c" or "f"
    }
    
    try:
        response = requests.get(OPEN_METEO_URL, params=params)
        response.raise_for_status()
        weather_data = response.json()
        
        # Cache the response
        cache[cache_key] = weather_data
        return jsonify(weather_data)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Weather API error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)