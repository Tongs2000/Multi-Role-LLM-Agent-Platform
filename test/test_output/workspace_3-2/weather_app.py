from flask import Flask, request, jsonify
import requests
from flask_caching import Cache
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# Configure caching
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Open-Meteo API base URL
BASE_URL = "https://api.open-meteo.com/v1"

@app.route('/weather/current', methods=['GET'])
def get_current_weather():
    city = request.args.get('city')
    if not city:
        return jsonify({'error': 'City parameter is required'}), 400

    # Simulate fetching coordinates (in a real app, use a geocoding API)
    coordinates = {
        'latitude': 52.52,
        'longitude': 13.41
    }

    # Cache key
    cache_key = f"current_weather_{city}"
    cached_data = cache.get(cache_key)
    if cached_data:
        return jsonify(cached_data)

    # Fetch current weather from Open-Meteo
    params = {
        'latitude': coordinates['latitude'],
        'longitude': coordinates['longitude'],
        'current': 'temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code'
    }
    response = requests.get(f"{BASE_URL}/forecast", params=params)
    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch weather data'}), 500

    data = response.json()
    current_weather = {
        'temperature': data['current']['temperature_2m'],
        'humidity': data['current']['relative_humidity_2m'],
        'wind_speed': data['current']['wind_speed_10m'],
        'condition': data['current']['weather_code']
    }

    # Cache the data for 30 minutes
    cache.set(cache_key, current_weather, timeout=1800)
    return jsonify(current_weather)

@app.route('/weather/forecast', methods=['GET'])
def get_forecast():
    city = request.args.get('city')
    if not city:
        return jsonify({'error': 'City parameter is required'}), 400

    # Simulate fetching coordinates (in a real app, use a geocoding API)
    coordinates = {
        'latitude': 52.52,
        'longitude': 13.41
    }

    # Cache key
    cache_key = f"forecast_{city}"
    cached_data = cache.get(cache_key)
    if cached_data:
        return jsonify(cached_data)

    # Fetch forecast from Open-Meteo
    params = {
        'latitude': coordinates['latitude'],
        'longitude': coordinates['longitude'],
        'daily': 'temperature_2m_max,temperature_2m_min,weather_code'
    }
    response = requests.get(f"{BASE_URL}/forecast", params=params)
    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch forecast data'}), 500

    data = response.json()
    forecast = []
    for i in range(5):
        forecast.append({
            'date': data['daily']['time'][i],
            'max_temp': data['daily']['temperature_2m_max'][i],
            'min_temp': data['daily']['temperature_2m_min'][i],
            'condition': data['daily']['weather_code'][i]
        })

    # Cache the data for 30 minutes
    cache.set(cache_key, forecast, timeout=1800)
    return jsonify(forecast)

@app.route('/cache/clear', methods=['POST'])
def clear_cache():
    cache.clear()
    return jsonify({'message': 'Cache cleared successfully'})

if __name__ == '__main__':
    app.run(debug=True)