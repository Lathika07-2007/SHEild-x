import networkx as nx
import numpy as np

class SafeHavenFinder:  # Make sure this class name matches
    def __init__(self, graph, city_name="Coimbatore"):
        self.graph = graph
        self.city_name = city_name
        self.safe_havens = []
        print("✅ SafeHavenFinder initialized")
        
    def create_sample_safe_locations(self):
        """Create sample safe locations"""
        self.safe_havens = [
            {"name": "Gandhipuram Police Station", "lat": 11.0183, "lon": 76.9725, "type": "police"},
            {"name": "RS Puram Police Station", "lat": 11.0259, "lon": 76.9795, "type": "police"},
            {"name": "City Hospital", "lat": 11.0149, "lon": 76.9934, "type": "hospital"},
            {"name": "Government Hospital", "lat": 11.0054, "lon": 76.9611, "type": "hospital"},
            {"name": "Race Course Police Station", "lat": 11.0168, "lon": 76.9618, "type": "police"},
            {"name": "Saibaba Colony Police Station", "lat": 11.0220, "lon": 76.9820, "type": "police"},
        ]
        
        for haven in self.safe_havens:
            haven['nearest_node'] = self.find_nearest_node(haven['lat'], haven['lon'])
        
        print(f"✅ Created {len(self.safe_havens)} sample safe havens")
        return self.safe_havens
    
    def find_nearest_node(self, lat, lon):
        """Find nearest graph node to coordinates"""
        min_dist = float('inf')
        nearest = None
        
        for node in self.graph.nodes():
            try:
                node_lat = self.graph.nodes[node]['y']
                node_lon = self.graph.nodes[node]['x']
                
                lat_diff = (lat - node_lat) * 111320
                lon_diff = (lon - node_lon) * 111320 * np.cos(np.radians(lat))
                dist = np.sqrt(lat_diff**2 + lon_diff**2)
                
                if dist < min_dist:
                    min_dist = dist
                    nearest = node
            except:
                continue
                
        return nearest