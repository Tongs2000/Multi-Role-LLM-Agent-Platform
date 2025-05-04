import React from 'react';

export default function PreviewPanel({ state }) {
  const { image, edits } = state;

  // Placeholder for applying edits to the preview
  const previewImage = image; // In a real app, apply edits here

  return (
    <div className="preview-panel">
      <h3>Preview</h3>
      {previewImage ? (
        <img src={previewImage} alt="Preview" />
      ) : (
        <p>No image to preview</p>
      )}
    </div>
  );
}