import React from 'react';

export default function ImageUploader({ dispatch }) {
  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.type.match('image.*')) {
      dispatch({ type: 'SET_ERROR', payload: 'Please upload a valid image file (JPEG, PNG, etc.)' });
      return;
    }

    dispatch({ type: 'SET_LOADING', payload: true });
    
    const formData = new FormData();
    formData.append('image', file);

    try {
      const response = await fetch('http://localhost:3001/api/upload', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error('Upload failed');
      }
      
      const data = await response.json();
      dispatch({ type: 'SET_IMAGE', payload: data.path });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  return (
    <div className="uploader">
      <input type="file" accept="image/*" onChange={handleFileChange} />
      <p>Drag and drop an image or click to browse</p>
    </div>
  );
}