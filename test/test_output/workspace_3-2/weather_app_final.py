from flask import Flask, request, jsonify
import requests
from flask_caching import Cache
import os

app = Flask(__name__)

# Configure caching
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Weatherstack API base URL and access key (use environment variable in production)
WEATHERSTACK_BASE_URL = "http://api.weatherstack.com"
WEATHERSTACK_ACCESS_KEY = os.getenv("WEATHERSTACK_ACCESS_KEY", "your_access_key_here")

@app.route('/locations/autocomplete', methods=['GET'])
def autocomplete_locations():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400

    # Cache key
    cache_key = f"autocomplete_{query}"
    cached_data = cache.get(cache_key)
    if cached_data:
        return jsonify(cached_data)

    # Fetch autocomplete results from weatherstack
    params = {
        'access_key': WEATHERSTACK_ACCESS_KEY,
        'query': query,
        'limit': request.args.get('limit', 10)
    }
    response = requests.get(f"{WEATHERSTACK_BASE_URL}/autocomplete", params=params)
    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch autocomplete results'}), 500

    data = response.json()
    if not data.get('success', False):
        return jsonify({'error': data.get('error', 'Unknown error')}), 500

    # Cache the data for 1 hour
    cache.set(cache_key, data, timeout=3600)
    return jsonify(data)

@app.route('/weather/marine', methods=['GET'])
def get_marine_weather():
    location_id = request.args.get('location_id')
    if not location_id:
        return jsonify({'error': 'Location ID parameter is required'}), 400

    # Cache key
    cache_key = f"marine_weather_{location_id}"
    cached_data = cache.get(cache_key)
    if cached_data:
        return jsonify(cached_data)

    # Fetch marine weather from weatherstack
    params = {
        'access_key': WEATHERSTACK_ACCESS_KEY,
        'query': location_id,
        'marine': 'true'
    }
    response = requests.get(f"{WEATHERSTACK_BASE_URL}/marine", params=params)
    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch marine weather data'}), 500

    data = response.json()
    if not data.get('success', False):
        return jsonify({'error': data.get('error', 'Unknown error')}), 500

    # Cache the data for 1 hour
    cache.set(cache_key, data, timeout=3600)
    return jsonify(data)

@app.route('/cache/clear', methods=['POST'])
def clear_cache():
    cache.clear()
    return jsonify({'message': 'Cache cleared successfully'})

if __name__ == '__main__':
    app.run(debug=True)