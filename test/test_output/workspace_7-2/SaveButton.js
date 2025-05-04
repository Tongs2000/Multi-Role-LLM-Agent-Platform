import React from 'react';

export default function SaveButton({ state, dispatch }) {
  const { image, edits } = state;

  const handleSave = async () => {
    if (!image) {
      dispatch({ type: 'SET_ERROR', payload: 'No image to save' });
      return;
    }

    dispatch({ type: 'SET_LOADING', payload: true });
    
    try {
      const response = await fetch('http://localhost:3001/api/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ imagePath: image }),
      });
      
      if (!response.ok) {
        throw new Error('Save failed');
      }
      
      const data = await response.json();
      console.log('Image saved:', data.path);
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  return (
    <button onClick={handleSave} disabled={!image}>
      Save Image
    </button>
  );
}