const { client, publishAsync } = require('../config/redis');

const setupWebSocket = (io) => {
  io.on('connection', (socket) => {
    console.log('New WebSocket connection:', socket.id);

    // Subscribe to Redis channels for real-time events
    client.subscribe('achievement_unlocked');
    client.subscribe('presence_updates');
    client.subscribe('reaction_events');

    // Handle achievement unlocks
    client.on('message', (channel, message) => {
      if (channel === 'achievement_unlocked') {
        const { userId, badgeId } = JSON.parse(message);
        socket.emit('achievement_unlocked', { userId, badgeId });
      }

      if (channel === 'presence_updates') {
        const { userId, status } = JSON.parse(message);
        socket.emit('presence_update', { userId, status });
      }

      if (channel === 'reaction_events') {
        const { messageId, emoji, userId } = JSON.parse(message);
        socket.emit('reaction_added', { messageId, emoji, userId });
      }
    });

    // Handle disconnection
    socket.on('disconnect', () => {
      console.log('WebSocket disconnected:', socket.id);
      client.unsubscribe();
    });
  });
};

module.exports = { setupWebSocket };