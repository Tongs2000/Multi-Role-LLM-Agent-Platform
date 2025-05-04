from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
from cachetools import TTLCache
import os

app = FastAPI()

# Configure CORS (for frontend access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache setup (10-minute TTL)
cache = TTLCache(maxsize=100, ttl=600)

# Open-Meteo API base URL
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

@app.get("/weather")
async def get_weather(latitude: float, longitude: float, units: str = "celsius"):
    cache_key = f"{latitude}_{longitude}_{units}"
    
    # Check cache
    if cache_key in cache:
        return cache[cache_key]
    
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
        return weather_data
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Weather API error: {str(e)}")