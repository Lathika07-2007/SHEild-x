import React from 'react';




function RouteInstructions({ routeStats, instructions }) {
  if (!instructions) return null;

  return (
    <div className="route-instructions">
      <h1 >📍 Turn-by-Turn Directions</h1>
      
      <div className="route-summary">
        <div>Distance: {routeStats?.distance_km.toFixed(2)} km</div>
        <div>Time: {Math.round(routeStats?.time_min)} mins</div>
      </div>
      
     

    </div>
  );
}

export default RouteInstructions;