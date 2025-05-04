import React from 'react';

export default function LayerPanel({ layers, onLayerUpdate }) {
  return (
    <div className="layer-panel">
      <h3>Layers</h3>
      {layers.map((layer) => (
        <div key={layer.id}>
          <label>
            <input
              type="checkbox"
              checked={layer.visible}
              onChange={() => onLayerUpdate(layer.id, { visible: !layer.visible })}
            />
            {layer.name}
          </label>
          <input
            type="range"
            min="0"
            max="100"
            value={layer.opacity}
            onChange={(e) => onLayerUpdate(layer.id, { opacity: e.target.value })}
          />
        </div>
      ))}
    </div>
  );
}