const mongoose = require('mongoose');

const chatSchema = new mongoose.Schema({
  name: { type: String }, // For group chats
  isGroup: { type: Boolean, default: false },
  participants: [{ type: mongoose.Schema.Types.ObjectId, ref: 'User' }],
  createdAt: { type: Date, default: Date.now },
  lastMessage: { type: mongoose.Schema.Types.ObjectId, ref: 'Message' },
  ttl: { type: Number, default: null }, // For ephemeral chats (in seconds)
});

// Add TTL index for ephemeral chats
if (process.env.ENABLE_EPHEMERAL_CHATS === 'true') {
  chatSchema.index({ createdAt: 1 }, { expireAfterSeconds: 86400 }); // 24h expiry
}

module.exports = mongoose.model('Chat', chatSchema);