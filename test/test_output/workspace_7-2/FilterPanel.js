import React from 'react';

export default function FilterPanel({ filters, onFilterChange }) {
  return (
    <div className="filter-panel">
      <h3>Filters</h3>
      {Object.entries(filters).map(([name, value]) => (
        <div key={name}>
          <label>{name}</label>
          <input
            type="range"
            min="0"
            max="100"
            value={value}
            onChange={(e) => onFilterChange(name, e.target.value)}
          />
        </div>
      ))}
    </div>
  );
}