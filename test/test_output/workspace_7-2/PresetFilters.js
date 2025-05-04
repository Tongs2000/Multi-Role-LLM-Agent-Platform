import React from 'react';

export default function PresetFilters({ presets, onPresetSelect }) {
  return (
    <div className="preset-filters">
      <h3>Presets</h3>
      <div className="preset-grid">
        {presets.map((preset) => (
          <button key={preset.id} onClick={() => onPresetSelect(preset)}>
            {preset.name}
          </button>
        ))}
      </div>
    </div>
  );
}