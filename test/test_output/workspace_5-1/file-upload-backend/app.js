const express = require('express');
const app = express();
const uploadRoutes = require('./routes/uploadRoutes');
const redis = require('redis');

// Middleware
app.use(express.json());

// Initialize Redis
const redisClient = redis.createClient({
  url: process.env.REDIS_URL || 'redis://localhost:6379',
});
redisClient.connect().catch(console.error);

// Routes
app.use('/api', uploadRoutes);
app.get('/', (req, res) => {
  res.send('File Upload Backend API');
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Internal Server Error' });
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});