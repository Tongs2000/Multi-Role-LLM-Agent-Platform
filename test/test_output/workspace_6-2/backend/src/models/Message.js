const mongoose = require('mongoose');

const messageSchema = new mongoose.Schema({
  content: { type: String, required: true },
  senderId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
  chatId: { type: mongoose.Schema.Types.ObjectId, ref: 'Chat', required: true },
  timestamp: { type: Date, default: Date.now },
  status: { type: String, enum: ['sent', 'delivered', 'read'], default: 'sent' },
  metadata: {
    editHistory: [
      {
        content: { type: String, required: true },
        timestamp: { type: Date, default: Date.now },
      },
    ],
    reactions: { type: Map, of: mongoose.Schema.Types.ObjectId, default: {} }, // emoji → userIDs
  },
});

// Add content hash for integrity verification
messageSchema.methods.generateContentHash = function () {
  const crypto = require('crypto');
  return crypto.createHash('sha256').update(this.content).digest('hex');
};

module.exports = mongoose.model('Message', messageSchema);