import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Map from './Map';
import HistoricalToggle from './HistoricalToggle';
import MultiLocation from './MultiLocation';
import HourlyChart from './HourlyChart';
import './WeatherApp.css';

const WeatherApp = () => {
  const [city, setCity] = useState('');
  const [weatherData, setWeatherData] = useState(null);
  const [forecastData, setForecastData] = useState(null);
  const [historicalData, setHistoricalData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [unit, setUnit] = useState('celsius');
  const [showHistorical, setShowHistorical] = useState(false);
  const [dateRange, setDateRange] = useState({ start: '', end: '' });
  const [locations, setLocations] = useState([]);

  const fetchWeatherData = async () => {
    setLoading(true);
    setError(null);
    try {
      if (showHistorical) {
        const response = await axios.get(`/weather/historical?city=${city}&start=${dateRange.start}&end=${dateRange.end}`);
        setHistoricalData(response.data);
      } else {
        const currentResponse = await axios.get(`/weather/current?city=${city}`);
        setWeatherData(currentResponse.data);
        const forecastResponse = await axios.get(`/weather/forecast?city=${city}`);
        setForecastData(forecastResponse.data);
      }
    } catch (err) {
      setError('Failed to fetch weather data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const fetchMultiLocationData = async () => {
    if (locations.length === 0) return;
    setLoading(true);
    try {
      const response = await axios.get(`/weather/multi?cities=${locations.join(',')}`);
      setWeatherData(response.data);
    } catch (err) {
      setError('Failed to fetch multi-location data.');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (city.trim()) fetchWeatherData();
  };

  const toggleUnit = () => {
    setUnit(unit === 'celsius' ? 'fahrenheit' : 'celsius');
  };

  const toggleHistorical = () => {
    setShowHistorical(!showHistorical);
  };

  return (
    <div className="weather-app">
      <h1>Weather App</h1>
      <form onSubmit={handleSearch}>
        <input
          type="text"
          placeholder="Enter city name"
          value={city}
          onChange={(e) => setCity(e.target.value)}
        />
        <button type="submit">Search</button>
      </form>

      <HistoricalToggle 
        showHistorical={showHistorical} 
        toggleHistorical={toggleHistorical} 
        dateRange={dateRange} 
        setDateRange={setDateRange} 
      />

      <MultiLocation 
        locations={locations} 
        setLocations={setLocations} 
        fetchMultiLocationData={fetchMultiLocationData} 
      />

      {loading && <div className="loading-spinner">Loading...</div>}
      {error && <div className="error-message">{error}</div>}

      {weatherData && (
        <div className="weather-card">
          <h2>{city || 'Current Location'}</h2>
          <p>Temperature: {weatherData.temperature}°{unit === 'celsius' ? 'C' : 'F'}</p>
          <p>Humidity: {weatherData.humidity}%</p>
          <p>Wind Speed: {weatherData.windSpeed} km/h</p>
          <button onClick={toggleUnit}>
            Switch to {unit === 'celsius' ? 'Fahrenheit' : 'Celsius'}
          </button>
        </div>
      )}

      {forecastData && <HourlyChart data={forecastData} unit={unit} />}
      {historicalData && <Map data={historicalData} />}
    </div>
  );
};

export default WeatherApp;