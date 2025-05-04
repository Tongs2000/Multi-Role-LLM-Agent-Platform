import React from 'react';

export default function Toolbar({ state, dispatch }) {
  const { activeTool } = state;

  const handleToolClick = (tool) => {
    dispatch({ type: 'SET_ACTIVE_TOOL', payload: tool });
  };

  const handleAddLayer = () => {
    const newLayer = {
      id: Date.now(),
      name: `Layer ${state.layers.length + 1}`,
      visible: true,
      opacity: 100,
    };
    dispatch({ type: 'SET_LAYERS', payload: [...state.layers, newLayer] });
  };

  return (
    <div className="toolbar">
      <button onClick={() => handleToolClick('crop')} className={activeTool === 'crop' ? 'active' : ''}>
        Crop
      </button>
      <button onClick={() => handleToolClick('freehand')} className={activeTool === 'freehand' ? 'active' : ''}>
        Freehand
      </button>
      <button onClick={() => handleToolClick('rotate')} className={activeTool === 'rotate' ? 'active' : ''}>
        Rotate
      </button>
      <button onClick={handleAddLayer}>
        Add Layer
      </button>
    </div>
  );
}