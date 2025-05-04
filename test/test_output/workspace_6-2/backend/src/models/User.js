const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');

const userSchema = new mongoose.Schema({
  username: { type: String, required: true, unique: true },
  email: { type: String, required: true, unique: true },
  passwordHash: { type: String, required: true },
  lastSeen: { type: Date, default: Date.now },
  avatarUrl: { type: String },
  achievements: {
    unlocked: { type: [String], default: [] },
    progress: { type: Map, of: Number, default: {} } // AchievementID → completion %
  },
  stats: {
    messageCount: { type: Number, default: 0 },
    lastActive: { type: Date, default: Date.now },
    reactionGiven: { type: Number, default: 0 },
    reactionReceived: { type: Number, default: 0 },
  },
});

// Hash password before saving
userSchema.pre('save', async function (next) {
  if (this.isModified('passwordHash')) {
    this.passwordHash = await bcrypt.hash(this.passwordHash, 10);
  }
  next();
});

// Method to verify password
userSchema.methods.verifyPassword = async function (password) {
  return await bcrypt.compare(password, this.passwordHash);
};

module.exports = mongoose.model('User', userSchema);