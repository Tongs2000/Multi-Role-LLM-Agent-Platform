from flask import Flask, request, jsonify
import requests
from flask_caching import Cache
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

@app.route('/weather/historical', methods=['GET'])
def get_historical_weather():
    city = request.args.get('city')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if not city or not start_date or not end_date:
        return jsonify({'error': 'City, start_date, and end_date parameters are required'}), 400

    # Validate date format (YYYY-MM-DD)
    try:
        datetime.strptime(start_date, '%Y-%m-%d')
        datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    # Simulate fetching coordinates (in a real app, use a geocoding API)
    coordinates = {
        'latitude': 52.52,
        'longitude': 13.41
    }

    # Cache key
    cache_key = f"historical_weather_{city}_{start_date}_{end_date}"
    cached_data = cache.get(cache_key)
    if cached_data:
        return jsonify(cached_data)

    # Fetch historical weather from Open-Meteo
    params = {
        'latitude': coordinates['latitude'],
        'longitude': coordinates['longitude'],
        'start_date': start_date,
        'end_date': end_date,
        'daily': 'temperature_2m_max,temperature_2m_min,weather_code'
    }
    response = requests.get(f"{BASE_URL}/forecast", params=params)
    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch historical weather data'}), 500

    data = response.json()
    historical_weather = []
    for i in range(len(data['daily']['time'])):
        historical_weather.append({
            'date': data['daily']['time'][i],
            'max_temp': data['daily']['temperature_2m_max'][i],
            'min_temp': data['daily']['temperature_2m_min'][i],
            'condition': data['daily']['weather_code'][i]
        })

    # Cache the data for 24 hours
    cache.set(cache_key, historical_weather, timeout=86400)
    return jsonify(historical_weather)

@app.route('/weather/multi', methods=['GET'])
def get_multi_weather():
    cities = request.args.getlist('city')
    if not cities:
        return jsonify({'error': 'At least one city parameter is required'}), 400

    # Simulate fetching coordinates (in a real app, use a geocoding API)
    coordinates_list = [
        {'latitude': 52.52, 'longitude': 13.41},
        {'latitude': 40.71, 'longitude': -74.01}
    ]

    # Cache key
    cache_key = f"multi_weather_{'_'.join(cities)}"
    cached_data = cache.get(cache_key)
    if cached_data:
        return jsonify(cached_data)

    # Fetch weather for each city
    multi_weather = {}
    for i, city in enumerate(cities):
        params = {
            'latitude': coordinates_list[i]['latitude'],
            'longitude': coordinates_list[i]['longitude'],
            'current': 'temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code'
        }
        response = requests.get(f"{BASE_URL}/forecast", params=params)
        if response.status_code != 200:
            multi_weather[city] = {'error': 'Failed to fetch weather data'}
            continue

        data = response.json()
        multi_weather[city] = {
            'temperature': data['current']['temperature_2m'],
            'humidity': data['current']['relative_humidity_2m'],
            'wind_speed': data['current']['wind_speed_10m'],
            'condition': data['current']['weather_code']
        }

    # Cache the data for 30 minutes
    cache.set(cache_key, multi_weather, timeout=1800)
    return jsonify(multi_weather)

@app.route('/cache/clear', methods=['POST'])
def clear_cache():
    cache.clear()
    return jsonify({'message': 'Cache cleared successfully'})

if __name__ == '__main__':
    app.run(debug=True)