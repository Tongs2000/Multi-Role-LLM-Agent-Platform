import React from 'react';

function ProgressIndicator({ progress }) {
  return (
    <div className="progress-indicator">
      <div className="progress-bar">
        <div
          className="progress-fill"
          style={{ width: `${progress}%` }}
        ></div>
      </div>
      <span className="progress-text">{Math.round(progress)}% Complete</span>
    </div>
  );
}

export default ProgressIndicator;