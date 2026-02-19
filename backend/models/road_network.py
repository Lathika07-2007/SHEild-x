import osmnx as ox
import networkx as nx
import pickle
import os

class RoadNetwork:
    def __init__(self, city_name="Coimbatore, India"):
        self.city_name = city_name
        self.graph = None
        self.nodes_gdf = None
        self.edges_gdf = None
        
    def fetch_network(self):
        print(f"Fetching road network for {self.city_name}...")
        self.graph = ox.graph_from_place(self.city_name, network_type='drive', simplify=True)
        self.nodes_gdf, self.edges_gdf = ox.graph_to_gdfs(self.graph)
        print(f"Graph has {len(self.graph.nodes)} nodes and {len(self.graph.edges)} edges")
        return self.graph
    
    def save_graph(self, filename="data/coimbatore_graph.pkl"):
        os.makedirs("data", exist_ok=True)
        with open(filename, 'wb') as f:
            pickle.dump(self.graph, f)
        print(f"Graph saved to {filename}")
    
    def load_graph(self, filename="data/coimbatore_graph.pkl"):
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                self.graph = pickle.load(f)
            self.nodes_gdf, self.edges_gdf = ox.graph_to_gdfs(self.graph)
            return self.graph
        else:
            return self.fetch_network()