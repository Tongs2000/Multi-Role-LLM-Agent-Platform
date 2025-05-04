import React from 'react';

export default function CanvasEditor({ state, dispatch }) {
  const { image, activeTool, selectedRegion } = state;

  const handleCanvasClick = (e) => {
    if (!image || !activeTool) return;

    // Placeholder for canvas interaction logic (e.g., crop selection)
    console.log('Canvas clicked:', e);
  };

  return (
    <div className="canvas-editor">
      {image ? (
        <img
          src={image}
          alt="Uploaded"
          onClick={handleCanvasClick}
          style={{ cursor: activeTool ? 'crosshair' : 'default' }}
        />
      ) : (
        <p>Upload an image to start editing</p>
      )}
    </div>
  );
}