import React, { useEffect, useState } from 'react';
import { useAtomValue } from 'jotai';
import { motion, AnimatePresence } from 'framer-motion';

const AchievementToast = ({ achievement }) => {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(false), 5000);
    return () => clearTimeout(timer);
  }, []);

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          className="achievement-toast"
        >
          <div className="achievement-icon">🏆</div>
          <div className="achievement-content">
            <h3>{achievement.title}</h3>
            <p>{achievement.description}</p>
            {achievement.progress && (
              <div className="progress-bar">
                <div
                  className="progress"
                  style={{ width: `${achievement.progress}%` }}
                />
              </div>
            )}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default AchievementToast;