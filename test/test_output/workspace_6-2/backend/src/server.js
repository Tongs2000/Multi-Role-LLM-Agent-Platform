const http = require('http');
const socketIo = require('socket.io');
const app = require('./app');
const { setupWebSocket } = require('./services/websocket');
const { connectToDatabase } = require('./config/database');

const PORT = process.env.PORT || 3000;
const server = http.createServer(app);

// Initialize WebSocket
const io = socketIo(server, {
  cors: {
    origin: '*',
    methods: ['GET', 'POST'],
  },
});

// Connect to database
connectToDatabase()
  .then(() => {
    // Set up WebSocket events
    setupWebSocket(io);

    // Start the server
    server.listen(PORT, () => {
      console.log(`Server running on port ${PORT}`);
    });
  })
  .catch((error) => {
    console.error('Failed to connect to the database:', error);
    process.exit(1);
  });