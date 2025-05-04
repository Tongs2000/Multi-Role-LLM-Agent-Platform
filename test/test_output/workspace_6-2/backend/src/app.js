const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const { createErrorHandler } = require('./middlewares/errorHandler');
const authRoutes = require('./routes/auth');
const messageRoutes = require('./routes/messages');
const userRoutes = require('./routes/users');
const achievementRoutes = require('./routes/achievements');
const reactionRoutes = require('./routes/reactions');
const presenceRoutes = require('./routes/presence');

const app = express();

// Middleware
app.use(cors());
app.use(helmet());
app.use(express.json());

// Rate limiting
const limiter = rateLimit({
  windowMs: 60 * 1000, // 1 minute
  max: 100, // 100 requests per minute
});
app.use(limiter);

// Routes
app.use('/api/auth', authRoutes);
app.use('/api/messages', messageRoutes);
app.use('/api/users', userRoutes);
app.use('/api/achievements', achievementRoutes);
app.use('/api/reactions', reactionRoutes);
app.use('/api/presence', presenceRoutes);

// Error handling
app.use(createErrorHandler());

module.exports = app;