import networkx as nx
import math

class PathFinder:  # Make sure this class name matches
    def __init__(self, graph):
        self.graph = graph
        print(f"✅ PathFinder initialized with {len(graph.nodes)} nodes")
        
    def find_nearest_node(self, lat, lon):
        """Find nearest node to given coordinates"""
        min_dist = float('inf')
        nearest_node = None
        
        for node in self.graph.nodes():
            try:
                node_lat = self.graph.nodes[node]['y']
                node_lon = self.graph.nodes[node]['x']
                
                # Calculate Euclidean distance
                lat_diff = (lat - node_lat) * 111320
                lon_diff = (lon - node_lon) * 111320 * math.cos(math.radians(lat))
                dist = math.sqrt(lat_diff**2 + lon_diff**2)
                
                if dist < min_dist:
                    min_dist = dist
                    nearest_node = node
            except:
                continue
                
        return nearest_node
    
    def find_safest_route(self, source, target):
        """Find the safest path by minimizing risk"""
        try:
            if source not in self.graph:
                print(f"Source node {source} not in graph")
                return None
            if target not in self.graph:
                print(f"Target node {target} not in graph")
                return None
            
            def weight_function(u, v, d):
                risk = d.get('risk', 0.5)
                distance = d.get('length', 100)
                return (risk * 1000) + (distance * 0.1)
            
            path = nx.shortest_path(self.graph, source, target, weight=weight_function)
            return path
            
        except nx.NetworkXNoPath:
            print(f"No path found between nodes")
            return None
        except Exception as e:
            print(f"Error in find_safest_route: {e}")
            return None
    
    def calculate_path_risk(self, path):
        """Calculate average risk of the path"""
        if not path or len(path) < 2:
            return 0.5
        
        total_risk = 0
        count = 0
        
        for i in range(len(path)-1):
            u, v = path[i], path[i+1]
            if self.graph.has_edge(u, v):
                try:
                    edge_data = self.graph.get_edge_data(u, v)
                    if edge_data:
                        first_key = list(edge_data.keys())[0]
                        risk = edge_data[first_key].get('risk', 0.5)
                        total_risk += risk
                        count += 1
                except:
                    continue
        
        return total_risk / count if count > 0 else 0.5
    
    def calculate_path_distance(self, path):
        """Calculate total distance of the path in meters"""
        if not path or len(path) < 2:
            return 0
        
        total_dist = 0
        for i in range(len(path)-1):
            u, v = path[i], path[i+1]
            if self.graph.has_edge(u, v):
                try:
                    edge_data = self.graph.get_edge_data(u, v)
                    if edge_data:
                        first_key = list(edge_data.keys())[0]
                        total_dist += edge_data[first_key].get('length', 100)
                except:
                    continue
        
        return total_dist
    
    def path_to_coordinates(self, path):
        """Convert path nodes to list of coordinates"""
        if not path:
            return []
        
        coordinates = []
        for node in path:
            try:
                if node in self.graph.nodes:
                    coordinates.append({
                        'lat': self.graph.nodes[node]['y'],
                        'lon': self.graph.nodes[node]['x']
                    })
            except:
                continue
                
        return coordinates
    
    def generate_route_instructions(self, path):
        """Generate simple turn-by-turn instructions"""
        if not path or len(path) < 2:
            return []
        
        instructions = []
        
        for i in range(len(path) - 1):
            current = path[i]
            next_node = path[i + 1]
            
            if not self.graph.has_edge(current, next_node):
                continue
                
            try:
                edge_data = self.graph.get_edge_data(current, next_node)
                first_key = list(edge_data.keys())[0]
                data = edge_data[first_key]
                
                road_name = data.get('name', 'Unnamed road')
                if isinstance(road_name, list):
                    road_name = road_name[0] if road_name else 'Unnamed road'
                
                distance = data.get('length', 0)
                
                if i == 0:
                    instruction = f"Start on {road_name}"
                else:
                    instruction = f"Continue on {road_name}"
                
                instructions.append({
                    'step': i + 1,
                    'instruction': instruction,
                    'road': road_name,
                    'distance': round(distance, 0)
                })
            except:
                continue
        
        if instructions:
            instructions.append({
                'step': len(instructions) + 1,
                'instruction': "You have reached your destination",
                'road': '',
                'distance': 0
            })
        
        return instructions