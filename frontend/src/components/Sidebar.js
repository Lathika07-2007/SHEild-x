import React, { useState } from 'react';
import { FaShieldAlt, FaRoute, FaDownload, FaFolder, FaBalanceScale } from 'react-icons/fa';

function Sidebar({ 
  startPoint, 
  endPoint, 
  routeStats, 
  mode, 
  setMode, 
  onFindRoute, 
  onClearRoute, 
  loading,
  savedLocations,
  onLoadLocation,
  onDownloadLocation,
  safeHavens,
  riskWeight,
  setRiskWeight
}) {
  const [showSaved, setShowSaved] = useState(false);
  const [showDownload, setShowDownload] = useState(false);
  const [downloadLocation, setDownloadLocation] = useState('');
  const [downloadRadius, setDownloadRadius] = useState(5000);
  const [selectedMode, setSelectedMode] = useState(mode);

  const handleModeChange = (newMode) => {
    setSelectedMode(newMode);
    setMode(newMode);
  };

  const handleDownload = () => {
    if (downloadLocation) {
      onDownloadLocation(downloadLocation, downloadRadius);
      setShowDownload(false);
      setDownloadLocation('');
    }
  };

  const getRiskDescription = (weight) => {
    if (weight < 0.3) return "🔵 Speed优先 (Prioritize Speed)";
    if (weight < 0.5) return "🟢 Slightly Safe";
    if (weight < 0.7) return "🟡 Balanced";
    if (weight < 0.9) return "🟠 Quite Safe";
    return "🔴 Very Safe";
  };

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <FaShieldAlt size={40} />
        <h1>SHEild-X</h1>
        <p>Safe Route Planning for Women</p>
      </div>

      {/* DOWNLOAD SECTION */}
      <div className="sidebar-section">
        <h3><FaDownload /> Download New Location</h3>
        <button 
          onClick={() => setShowDownload(!showDownload)} 
          className="toggle-btn"
        >
          {showDownload ? 'Cancel' : 'Download New Area'}
        </button>
        
        {showDownload && (
          <div className="download-form">
            <input
              type="text"
              placeholder="Enter city name (e.g., Coimbatore, India)"
              value={downloadLocation}
              onChange={(e) => setDownloadLocation(e.target.value)}
            />
            <select 
              value={downloadRadius} 
              onChange={(e) => setDownloadRadius(Number(e.target.value))}
            >
              <option value={2000}>2 km radius</option>
              <option value={5000}>5 km radius</option>
              <option value={10000}>10 km radius</option>
              <option value={20000}>20 km radius</option>
            </select>
            <button 
              onClick={handleDownload} 
              disabled={!downloadLocation || loading}
            >
              {loading ? 'Downloading...' : 'Download'}
            </button>
          </div>
        )}
      </div>

      {/* SAVED LOCATIONS */}
      <div className="sidebar-section">
        <h3><FaFolder /> Saved Locations</h3>
        <button 
          onClick={() => setShowSaved(!showSaved)} 
          className="toggle-btn"
        >
          {showSaved ? 'Hide' : 'Show'} Locations
        </button>
        
        {showSaved && (
          <div className="saved-list">
            {savedLocations.length === 0 ? (
              <p>No saved locations yet</p>
            ) : (
              savedLocations.map((loc, idx) => (
                <div key={idx} className="saved-item">
                  <span>{loc.name}</span>
                  <button onClick={() => onLoadLocation(loc.file)}>
                    Load
                  </button>
                </div>
              ))
            )}
          </div>
        )}
      </div>

      {/* ROUTE OPTIONS - ONLY SAFEST AND USER DEFINED */}
      <div className="sidebar-section">
        <h3><FaRoute /> Route Options</h3>
        
        {/* Mode selector - Only 2 options */}
        <div className="mode-selector">
          <button
            className={selectedMode === 'safest' ? 'active' : ''}
            onClick={() => handleModeChange('safest')}
          >
            🛡️ Safest Route
          </button>
          
        </div>

        {/* USER RISK PREFERENCE SLIDER - Only shows for Custom Balance */}
        

        {/* Selected points info */}
        <div className="points-info">
          {startPoint && (
            <div className="point">
              <span className="green-dot"></span>
              Start Selected
            </div>
          )}
          {endPoint && (
            <div className="point">
              <span className="red-dot"></span>
              Destination Selected
            </div>
          )}
        </div>

        {/* Action buttons */}
        <div className="action-buttons">
          <button 
            onClick={onFindRoute} 
            disabled={!startPoint || !endPoint || loading}
          >
            {loading ? 'Finding...' : 'Find Route'}
          </button>
          <button onClick={onClearRoute} className="secondary">
            Clear
          </button>
        </div>
      </div>

      {/* Route Statistics */}
      {routeStats && (
        <div className="sidebar-section stats">
          <h3>Route Statistics</h3>
          
          <div className="stat-item">
            <span>Distance:</span>
            <strong>{routeStats.distance_km.toFixed(2)} km</strong>
          </div>
          
          <div className="stat-item">
            <span>Est. Time:</span>
            <strong>{Math.round(routeStats.time_min)} mins</strong>
          </div>
          
          

          {routeStats.mode === 'user_defined' && routeStats.used_weight && (
            <div className="stat-item">
              <span>Your Balance:</span>
              <strong>{Math.round(routeStats.used_weight * 100)}% Safe</strong>
            </div>
          )}
        </div>
      )}

      {/* Safe Havens */}
      {safeHavens && safeHavens.length > 0 && (
        <div className="sidebar-section">
          <h4>Safe Havens Nearby</h4>
          <div className="havens-summary">
            <div className="haven-stat">
              <span className="blue-dot"></span>
              Police: {safeHavens.filter(h => h.type === 'police').length}
            </div>
            <div className="haven-stat">
              <span className="red-dot"></span>
              Hospitals: {safeHavens.filter(h => h.type === 'hospital').length}
            </div>
          </div>
        </div>
      )}

      <div className="sidebar-footer">
        <p>Click map to select points</p>
        <p className="note">🛡️ Safest Route vs ⚖️ Your Choice</p>
      </div>
    </div>
  );
}

export default Sidebar;