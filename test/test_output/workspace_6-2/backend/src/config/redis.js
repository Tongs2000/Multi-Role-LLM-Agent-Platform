const redis = require('redis');
const { promisify } = require('util');

const client = redis.createClient({
  url: process.env.REDIS_URL || 'redis://localhost:6379',
});

// Promisify Redis methods for async/await support
const getAsync = promisify(client.get).bind(client);
const setAsync = promisify(client.set).bind(client);
const publishAsync = promisify(client.publish).bind(client);

// Handle connection events
client.on('connect', () => {
  console.log('Redis client connected');
});

client.on('error', (err) => {
  console.error('Redis error:', err);
});

module.exports = {
  client,
  getAsync,
  setAsync,
  publishAsync,
};