import React from 'react';
import RichTextEditor from './RichTextEditor';
import './App.css';

function App() {
  const handleSave = (content) => {
    console.log('Note saved:', content); // Placeholder for save logic
  };

  return (
    <div className="app">
      <div className="sidebar">
        <h2>Categories</h2>
        {/* Placeholder for categories/tags */}
      </div>
      <div className="main-content">
        <div className="search-bar">
          <input type="text" placeholder="Search notes..." />
        </div>
        <RichTextEditor onSave={handleSave} />
      </div>
    </div>
  );
}

export default App;
