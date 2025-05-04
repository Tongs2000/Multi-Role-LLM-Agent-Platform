import os
import time
import json
import redis
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Redis cache setup
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=os.getenv('REDIS_PORT', 6379),
    db=0
)

OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
if not OPENWEATHER_API_KEY:
    raise ValueError("OPENWEATHER_API_KEY environment variable not set")

@dataclass
class WeatherData:
    city: str
    country: str
    temperature: float
    feels_like: float
    humidity: int
    pressure: int
    wind_speed: float
    description: str
    icon: str
    forecast: list

def get_cached_weather(city: str) -> Optional[WeatherData]:
    cached_data = redis_client.get(f"weather:{city.lower()}")
    if cached_data:
        return WeatherData(**json.loads(cached_data))
    return None

def cache_weather(city: str, data: WeatherData, ttl: int = 3600) -> None:
    redis_client.setex(
        f"weather:{city.lower()}",
        ttl,
        json.dumps(data.__dict__)
    )

def fetch_weather_data(city: str) -> WeatherData:
    # Check cache first
    cached_data = get_cached_weather(city)
    if cached_data:
        return cached_data

    # Current weather
    current_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    current_response = requests.get(current_url)
    current_response.raise_for_status()
    current_data = current_response.json()

    # Forecast
    forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={OPENWEATHER_API_KEY}&units=metric&cnt=5"
    forecast_response = requests.get(forecast_url)
    forecast_response.raise_for_status()
    forecast_data = forecast_response.json()

    # Process forecast
    forecast = []
    for item in forecast_data['list']:
        forecast.append({
            'dt': item['dt'],
            'temp': item['main']['temp'],
            'description': item['weather'][0]['description'],
            'icon': item['weather'][0]['icon']
        })

    weather = WeatherData(
        city=current_data['name'],
        country=current_data['sys']['country'],
        temperature=current_data['main']['temp'],
        feels_like=current_data['main']['feels_like'],
        humidity=current_data['main']['humidity'],
        pressure=current_data['main']['pressure'],
        wind_speed=current_data['wind']['speed'],
        description=current_data['weather'][0]['description'],
        icon=current_data['weather'][0]['icon'],
        forecast=forecast
    )

    cache_weather(city, weather)
    return weather

@app.route('/api/weather', methods=['GET'])
def get_weather():
    city = request.args.get('city')
    if not city:
        return jsonify({'error': 'City parameter is required'}), 400

    try:
        weather_data = fetch_weather_data(city)
        return jsonify(weather_data.__dict__)
    except requests.exceptions.HTTPError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)