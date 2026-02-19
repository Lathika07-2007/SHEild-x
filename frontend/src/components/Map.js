import React, { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default markers
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Custom icons
const startIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41]
});

const endIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41]
});

const policeIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41]
});

const hospitalIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41]
});

// Map click handler component
function MapClickHandler({ onMapClick }) {
  const map = useMap();
  
  useEffect(() => {
    if (!onMapClick) return;
    
    const handleClick = (e) => {
      onMapClick(e.latlng);
    };
    
    map.on('click', handleClick);
    
    return () => {
      map.off('click', handleClick);
    };
  }, [map, onMapClick]);
  
  return null;
}

function Map({ center, zoom, startPoint, endPoint, route, safeHavens, onMapClick }) {
  return (
    <MapContainer 
      center={center} 
      zoom={zoom} 
      style={{ height: '100%', width: '100%' }}
    >
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      
      <MapClickHandler onMapClick={onMapClick} />
      
      {/* Start marker - ONLY ONE */}
      {startPoint && (
        <Marker position={[startPoint.lat, startPoint.lon]} icon={startIcon}>
          <Popup>Start Point</Popup>
        </Marker>
      )}
      
      {/* End marker - ONLY ONE */}
      {endPoint && (
        <Marker position={[endPoint.lat, endPoint.lon]} icon={endIcon}>
          <Popup>Destination</Popup>
        </Marker>
      )}
      
      {/* Safe havens */}
      {safeHavens && safeHavens.map((haven, index) => (
        <Marker 
          key={index} 
          position={[haven.lat, haven.lon]} 
          icon={haven.type === 'police' ? policeIcon : hospitalIcon}
        >
          <Popup>
            <strong>{haven.name}</strong><br/>
            Type: {haven.type}
          </Popup>
        </Marker>
      ))}
      
      {/* Route line - simplified to avoid duplicate points */}
      {route && route.length > 0 && (
        <Polyline 
          positions={route.map(point => [point.lat, point.lon])} 
          color="#f44336" 
          weight={5}
          opacity={0.7}
        />
      )}
    </MapContainer>
  );
}

export default Map;