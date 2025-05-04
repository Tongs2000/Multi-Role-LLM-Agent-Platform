import React, { useState } from 'react';

const MultiLocation = ({ locations, setLocations, fetchMultiLocationData }) => {
  const [newLocation, setNewLocation] = useState('');

  const handleAddLocation = () => {
    if (newLocation.trim() && !locations.includes(newLocation.trim())) {
      setLocations([...locations, newLocation.trim()]);
      setNewLocation('');
    }
  };

  const handleRemoveLocation = (locationToRemove) => {
    setLocations(locations.filter((loc) => loc !== locationToRemove));
  };

  return (
    <div className="multi-location">
      <div className="location-input">
        <input
          type="text"
          placeholder="Add a location"
          value={newLocation}
          onChange={(e) => setNewLocation(e.target.value)}
        />
        <button onClick={handleAddLocation}>Add</button>
      </div>
      <div className="location-list">
        {locations.map((location) => (
          <div key={location} className="location-item">
            <span>{location}</span>
            <button onClick={() => handleRemoveLocation(location)}>Remove</button>
          </div>
        ))}
      </div>
      <button onClick={fetchMultiLocationData} disabled={locations.length === 0}>
        Compare Locations
      </button>
    </div>
  );
};

export default MultiLocation;