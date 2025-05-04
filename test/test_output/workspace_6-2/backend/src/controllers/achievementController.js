const User = require('../models/User');
const redis = require('../config/redis');

// Unlock a badge for a user
const unlockBadge = async (userId, badgeId) => {
  try {
    const user = await User.findById(userId);
    if (!user) throw new Error('User not found');

    if (!user.achievements.unlocked.includes(badgeId)) {
      user.achievements.unlocked.push(badgeId);
      await user.save();

      // Publish achievement event to Redis for real-time updates
      await redis.publish('achievement_unlocked', JSON.stringify({ userId, badgeId }));
    }

    return { success: true, badgeId };
  } catch (error) {
    throw new Error(`Failed to unlock badge: ${error.message}`);
  }
};

// Track progress for an achievement
const trackProgress = async (userId, achievementId, progress) => {
  try {
    const user = await User.findById(userId);
    if (!user) throw new Error('User not found');

    user.achievements.progress.set(achievementId, progress);
    await user.save();

    return { success: true, progress };
  } catch (error) {
    throw new Error(`Failed to track progress: ${error.message}`);
  }
};

module.exports = {
  unlockBadge,
  trackProgress,
};