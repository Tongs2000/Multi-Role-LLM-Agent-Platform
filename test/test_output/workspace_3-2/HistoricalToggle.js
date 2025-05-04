import React from 'react';

const HistoricalToggle = ({ showHistorical, toggleHistorical, dateRange, setDateRange }) => {
  return (
    <div className="historical-toggle">
      <label>
        <input
          type="checkbox"
          checked={showHistorical}
          onChange={toggleHistorical}
        />
        Show Historical Data
      </label>
      {showHistorical && (
        <div className="date-range">
          <input
            type="date"
            value={dateRange.start}
            onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })}
            placeholder="Start Date"
          />
          <input
            type="date"
            value={dateRange.end}
            onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })}
            placeholder="End Date"
          />
        </div>
      )}
    </div>
  );
};

export default HistoricalToggle;