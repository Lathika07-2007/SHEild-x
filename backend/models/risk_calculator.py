import numpy as np
import json
import os
from datetime import datetime

class RiskCalculator:  # Make sure this class name matches exactly
    def __init__(self, graph):
        self.graph = graph
        self.incident_locations = []
        print("✅ RiskCalculator initialized")
        
    def assign_base_risk_by_road_type(self):
        """Assign different risk levels to different road types"""
        risk_by_road_type = {
            'motorway': 0.15,
            'trunk': 0.18,
            'primary': 0.22,
            'secondary': 0.28,
            'tertiary': 0.35,
            'residential': 0.55,
            'living_street': 0.60,
            'service': 0.75,
            'unclassified': 0.70,
            'track': 0.85,
            'path': 0.95,
            'footway': 0.90
        }
        
        count = 0
        for u, v, key, data in self.graph.edges(keys=True, data=True):
            try:
                road_type = data.get('highway', 'residential')
                if isinstance(road_type, list):
                    road_type = road_type[0] if road_type else 'residential'
                
                base_risk = risk_by_road_type.get(road_type, 0.5)
                length = data.get('length', 100)
                length_factor = min(length / 500, 1.0)
                
                self.graph.edges[u, v, key]['base_risk'] = base_risk
                self.graph.edges[u, v, key]['risk'] = min(base_risk * (1 + 0.3 * length_factor), 1.0)
                count += 1
            except:
                continue
        
        print(f"✅ Assigned base risk to {count} edges")
        return self.graph
    
    def create_sample_incidents(self):
        """Create sample incident data"""
        incidents = [
            {"lat": 11.0183, "lon": 76.9725, "severity": 0.95, "type": "accident_hotspot"},
            {"lat": 11.0168, "lon": 76.9750, "severity": 0.85, "type": "theft_prone"},
            {"lat": 11.0145, "lon": 76.9690, "severity": 0.80, "type": "accident"},
            {"lat": 11.0054, "lon": 76.9611, "severity": 0.75, "type": "snatching"},
            {"lat": 11.0259, "lon": 76.9795, "severity": 0.60, "type": "accident"},
            {"lat": 11.0220, "lon": 76.9820, "severity": 0.55, "type": "theft"},
            {"lat": 11.0149, "lon": 76.9934, "severity": 0.50, "type": "accident"},
            {"lat": 11.0350, "lon": 76.9980, "severity": 0.45, "type": "snatching"},
            {"lat": 11.0400, "lon": 76.9600, "severity": 0.25, "type": "minor"},
        ]
        
        os.makedirs("backend/data", exist_ok=True)
        with open("backend/data/incidents.json", "w") as f:
            json.dump(incidents, f, indent=2)
            
        self.incident_locations = incidents
        print(f"✅ Created {len(incidents)} sample incidents")
        return incidents
    
    def add_incident_risk(self):
        """Increase risk near incident locations"""
        if not self.incident_locations:
            try:
                with open("backend/data/incidents.json", "r") as f:
                    self.incident_locations = json.load(f)
            except FileNotFoundError:
                self.create_sample_incidents()
        
        count = 0
        for u, v, key, data in self.graph.edges(keys=True, data=True):
            try:
                u_lat = self.graph.nodes[u]['y']
                u_lon = self.graph.nodes[u]['x']
                v_lat = self.graph.nodes[v]['y']
                v_lon = self.graph.nodes[v]['x']
                
                center_lat = (u_lat + v_lat) / 2
                center_lon = (u_lon + v_lon) / 2
                
                additional_risk = 0
                for incident in self.incident_locations:
                    # Calculate distance in km
                    lat_diff = abs(center_lat - incident['lat']) * 111
                    lon_diff = abs(center_lon - incident['lon']) * 111 * np.cos(np.radians(center_lat))
                    distance = np.sqrt(lat_diff**2 + lon_diff**2)
                    
                    if distance < 0.5:  # Within 500m
                        additional_risk += incident['severity'] * (1 - distance/0.5)
                
                if additional_risk > 0:
                    current_risk = data.get('risk', 0.5)
                    data['risk'] = min(current_risk + additional_risk, 1.0)
                    count += 1
                    
            except:
                continue
        
        print(f"✅ Added incident risk to {count} edges")
        return self.graph
    
    def apply_time_factor(self, current_hour=None):
        """Apply time-based risk multipliers"""
        if current_hour is None:
            current_hour = datetime.now().hour
        
        # Time multipliers
        if current_hour < 5:  # Late night
            multiplier = 2.0
        elif current_hour < 7:  # Early morning
            multiplier = 1.4
        elif current_hour < 10:  # Morning rush
            multiplier = 1.2
        elif current_hour < 16:  # Day time
            multiplier = 0.8
        elif current_hour < 19:  # Evening rush
            multiplier = 1.3
        elif current_hour < 22:  # Evening
            multiplier = 1.6
        else:  # Night
            multiplier = 1.8
        
        count = 0
        for u, v, key, data in self.graph.edges(keys=True, data=True):
            try:
                original_risk = data.get('risk', 0.5)
                data['risk'] = min(original_risk * multiplier, 1.0)
                data['original_risk'] = original_risk
                data['time_multiplier'] = multiplier
                count += 1
            except:
                continue
        
        print(f"✅ Applied time factor {multiplier}x to {count} edges")
        return self.graph
    
    def propagate_risk(self, iterations=2):
        """Propagate risk to neighboring edges"""
        for iteration in range(iterations):
            changes = 0
            new_risks = {}
            
            for u, v, key, data in self.graph.edges(keys=True, data=True):
                try:
                    neighbor_risks = []
                    
                    # Check neighbors
                    for neighbor in self.graph.neighbors(u):
                        if self.graph.has_edge(u, neighbor):
                            for edge_key in self.graph[u][neighbor]:
                                if (u, neighbor, edge_key) != (u, v, key):
                                    neighbor_data = self.graph.edges[u, neighbor, edge_key]
                                    neighbor_risks.append(neighbor_data.get('risk', 0.5))
                    
                    for neighbor in self.graph.neighbors(v):
                        if self.graph.has_edge(v, neighbor):
                            for edge_key in self.graph[v][neighbor]:
                                if (v, neighbor, edge_key) != (u, v, key):
                                    neighbor_data = self.graph.edges[v, neighbor, edge_key]
                                    neighbor_risks.append(neighbor_data.get('risk', 0.5))
                    
                    if neighbor_risks:
                        avg_neighbor = sum(neighbor_risks) / len(neighbor_risks)
                        current = data.get('risk', 0.5)
                        new_risk = 0.7 * current + 0.3 * avg_neighbor
                        if abs(new_risk - current) > 0.01:
                            new_risks[(u, v, key)] = min(new_risk, 1.0)
                            changes += 1
                except:
                    continue
            
            # Apply new risks
            for (u, v, key), new_risk in new_risks.items():
                if self.graph.has_edge(u, v, key):
                    self.graph.edges[u, v, key]['risk'] = new_risk
            
            print(f"  Iteration {iteration+1}: updated {changes} edges")
        
        return self.graph
    
    def calculate_node_risk(self):
        """Calculate risk for each node"""
        count = 0
        for node in self.graph.nodes():
            try:
                incident_edges = list(self.graph.edges(node, data=True))
                if incident_edges:
                    edge_risks = [data.get('risk', 0.5) for _, _, data in incident_edges]
                    self.graph.nodes[node]['risk'] = sum(edge_risks) / len(edge_risks)
                    count += 1
            except:
                continue
        
        print(f"✅ Calculated risk for {count} nodes")
        return self.graph