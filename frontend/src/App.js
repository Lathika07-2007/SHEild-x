import React, { useState, useEffect } from 'react';
import Map from './components/Map';
import Sidebar from './components/Sidebar';
import LocationSearch from './components/LocationSearch';
import RouteInstructions from './components/RouteInstructions';
import axios from 'axios';

const API_BASE = 'http://localhost:5000/api';

function App() {
  const [startPoint, setStartPoint] = useState(null);
  const [endPoint, setEndPoint] = useState(null);
  const [route, setRoute] = useState(null);
  const [routeStats, setRouteStats] = useState(null);
  const [routeInstructions, setRouteInstructions] = useState(null);
  const [safeHavens, setSafeHavens] = useState([]);
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState('user_defined');
  const [riskWeight, setRiskWeight] = useState(0.7);
  const [showInstructions, setShowInstructions] = useState(false);
  const [savedLocations, setSavedLocations] = useState([]);
  const [currentLocation, setCurrentLocation] = useState(null);

  useEffect(() => { 
    loadSavedLocations();
    fetchSafeHavens(); 
  }, []);

  useEffect(() => {
    if (currentLocation) {
      fetchSafeHavens();
    }
  }, [currentLocation]);

  const clearPreviousRoute = () => {
    setRoute(null);
    setRouteStats(null);
    setRouteInstructions(null);
    setShowInstructions(false);
  };

  const loadSavedLocations = async () => {
    try { 
      const res = await axios.get(`${API_BASE}/locations`); 
      setSavedLocations(res.data.locations); 
    } 
    catch (error) { 
      console.error('Error loading locations:', error); 
    }
  };

  const fetchSafeHavens = async () => {
    try { 
      const res = await axios.get(`${API_BASE}/safe-havens`); 
      setSafeHavens(res.data.havens || []); 
    } 
    catch (error) { 
      console.error('Error fetching safe havens:', error); 
    }
  };

  // THIS IS THE FUNCTION THAT WAS MISSING!
  const downloadLocation = async (location, radius) => {
    setLoading(true);
    try { 
      const res = await axios.post(`${API_BASE}/download-location`, { 
        location, 
        radius: parseInt(radius) 
      }); 
      alert(`✅ Downloaded ${location}`);
      loadSavedLocations();
      clearPreviousRoute();
      setStartPoint(null);
      setEndPoint(null);
    } 
    catch (error) { 
      alert('❌ Error downloading location'); 
      console.error(error);
    }
    setLoading(false);
  };

  const loadLocation = async (file) => {
    setLoading(true);
    try { 
      const res = await axios.post(`${API_BASE}/load-location`, { file }); 
      setCurrentLocation(res.data);
      alert(`✅ Loaded ${res.data.location}`);
      clearPreviousRoute();
      setStartPoint(null);
      setEndPoint(null);
    } 
    catch (error) { 
      alert('❌ Error loading location'); 
    }
    setLoading(false);
  };

  const findRoute = async () => {
    if (!startPoint || !endPoint) { 
      alert('Please select start and end points'); 
      return; 
    }

    setLoading(true);
    try {
      const requestData = {
        start: {
          lat: parseFloat(startPoint.lat),
          lon: parseFloat(startPoint.lon || startPoint.lng)
        },
        end: {
          lat: parseFloat(endPoint.lat),
          lon: parseFloat(endPoint.lon || endPoint.lng)
        },
        mode: mode,
        risk_weight: riskWeight
      };

      const res = await axios.post(`${API_BASE}/route-with-instructions`, requestData);
      
      setRoute(res.data.path);
      setRouteStats({
        ...res.data.statistics,
        used_weight: riskWeight
      });
      setRouteInstructions(res.data.instructions);
      setShowInstructions(true);
    } catch (error) {
      alert('Error finding route');
    }
    setLoading(false);
  };

  const handleMapClick = (type, latlng) => {
    clearPreviousRoute();
    const point = { lat: latlng.lat, lon: latlng.lng, lng: latlng.lng };
    if (type === 'start') setStartPoint(point);
    else if (type === 'end') setEndPoint(point);
  };

  const handleSearchSelect = (type, location) => {
    clearPreviousRoute();
    const point = { lat: location.lat, lon: location.lng, lng: location.lng };
    if (type === 'start') setStartPoint(point);
    else setEndPoint(point);
  };

  const clearRoute = () => {
    clearPreviousRoute();
    setStartPoint(null);
    setEndPoint(null);
  };

  return (
    <div className="app">
      <Sidebar
        startPoint={startPoint}
        endPoint={endPoint}
        routeStats={routeStats}
        mode={mode}
        setMode={setMode}
        riskWeight={riskWeight}
        setRiskWeight={setRiskWeight}
        onFindRoute={findRoute}
        onClearRoute={clearRoute}
        loading={loading}
        savedLocations={savedLocations}
        onLoadLocation={loadLocation}
        onDownloadLocation={downloadLocation}  // ← NOW IT'S HERE!
        safeHavens={safeHavens}
      />
      
      <div className="main-content">
        <div className="search-containers">
          <LocationSearch 
            onLocationSelect={(latlng) => handleSearchSelect('start', latlng)} 
            placeholder="🔍 Search start..." 
          />
          <LocationSearch 
            onLocationSelect={(latlng) => handleSearchSelect('end', latlng)} 
            placeholder="🔍 Search destination..." 
          />
        </div>
        
        <div className="map-instructions-container">
          <div className="map-wrapper">
            <Map
              center={[11.0168, 76.9558]}
              zoom={13}
              startPoint={startPoint}
              endPoint={endPoint}
              route={route}
              safeHavens={safeHavens}
              onMapClick={(latlng) => {
                const type = !startPoint ? 'start' : (!endPoint ? 'end' : null);
                if (type) handleMapClick(type, latlng);
                else alert('Both points selected. Click Clear to reset.');
              }}
            />
          </div>
          
          {showInstructions && routeInstructions && (
            <div className="instructions-wrapper">
              <button className="close-instructions" onClick={() => setShowInstructions(false)}>×</button>
              <RouteInstructions routeStats={routeStats} instructions={routeInstructions} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;