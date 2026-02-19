import React, { useState } from 'react';

function LocationSearch({ onLocationSelect, placeholder }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [showResults, setShowResults] = useState(false);

  const searchLocation = async () => {
    if (!query) return;
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}`
      );
      const data = await response.json();
      setResults(data.slice(0, 5));
      setShowResults(true);
    } catch (error) {
      console.error('Error searching location:', error);
    }
  };

  const handleSelect = (result) => {
    onLocationSelect({ 
      lat: parseFloat(result.lat), 
      lng: parseFloat(result.lon) 
    });
    setQuery(result.display_name);
    setShowResults(false);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      searchLocation();
    }
  };

  return (
    <div className="location-search">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder={placeholder}
      />
      {showResults && results.length > 0 && (
        <div className="search-results">
          {results.map((result, index) => (
            <div 
              key={index} 
              className="search-result-item" 
              onClick={() => handleSelect(result)}
            >
              {result.display_name}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default LocationSearch;