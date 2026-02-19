from flask import Flask, request, jsonify
from flask_cors import CORS
from models.road_network import RoadNetwork
from models.risk_calculator import RiskCalculator
from models.path_finder import PathFinder
from models.safe_havens import SafeHavenFinder
from datetime import datetime
import traceback
import os
import pickle
import json
import networkx as nx

app = Flask(__name__)
CORS(app, origins="http://localhost:3000", supports_credentials=True)

# Global variables
current_graph = None
current_location = None
pf = None
shf = None
rc = None

DATA_DIR = "backend/data"

def ensure_data_directory():
    """Create data directory if it doesn't exist"""
    os.makedirs(DATA_DIR, exist_ok=True)

def initialize_components(graph, location_name):
    """Initialize all components with a graph"""
    global rc, pf, shf
    
    try:
        rc = RiskCalculator(graph)
        rc.assign_base_risk_by_road_type()
        rc.create_sample_incidents()
        rc.add_incident_risk()
        rc.apply_time_factor()
        rc.propagate_risk()
        rc.calculate_node_risk()
        
        pf = PathFinder(graph)
        shf = SafeHavenFinder(graph, location_name)
        shf.create_sample_safe_locations()
        
        print(f"✅ Components initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Error initializing components: {e}")
        traceback.print_exc()
        return False

# Try to load existing location on startup
print("=" * 50)
print("SHEild-X Backend Server")
print("=" * 50)

ensure_data_directory()
existing_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.pkl')]

if existing_files:
    file_path = os.path.join(DATA_DIR, existing_files[0])
    print(f"📂 Found existing data: {existing_files[0]}")
    try:
        with open(file_path, 'rb') as f:
            current_graph = pickle.load(f)
        current_location = existing_files[0].replace('.pkl', '')
        if initialize_components(current_graph, current_location):
            print(f"✅ Loaded {current_location} with {len(current_graph.nodes)} nodes")
        else:
            current_graph = None
            current_location = None
    except Exception as e:
        print(f"❌ Error loading existing file: {e}")
        current_graph = None
        current_location = None
else:
    print("📂 No existing data found. Please download a location.")

print("🚀 Server ready for connections!")
print("=" * 50)

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get backend status"""
    global current_graph, current_location
    return jsonify({
        'status': 'running',
        'location_loaded': current_location is not None,
        'current_location': current_location,
        'nodes': len(current_graph.nodes) if current_graph else 0,
        'edges': len(current_graph.edges) if current_graph else 0
    })

@app.route('/api/locations', methods=['GET'])
def get_saved_locations():
    """Get list of saved locations"""
    ensure_data_directory()
    locations = []
    try:
        for file in os.listdir(DATA_DIR):
            if file.endswith('.pkl'):
                name = file.replace('.pkl', '')
                file_path = os.path.join(DATA_DIR, file)
                locations.append({
                    'id': name,
                    'name': name.replace('_', ' ').title(),
                    'file': file_path
                })
    except Exception as e:
        print(f"Error listing locations: {e}")
    
    return jsonify({'locations': locations})

@app.route('/api/load-location', methods=['POST'])
def load_location():
    """Load a saved location"""
    global current_graph, current_location, rc, pf, shf
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    file_path = data.get('file')
    if not file_path or not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    try:
        with open(file_path, 'rb') as f:
            current_graph = pickle.load(f)
        
        current_location = os.path.basename(file_path).replace('.pkl', '')
        
        if initialize_components(current_graph, current_location):
            return jsonify({
                'success': True,
                'location': current_location,
                'nodes': len(current_graph.nodes),
                'edges': len(current_graph.edges)
            })
        else:
            return jsonify({'error': 'Failed to initialize components'}), 500
            
    except Exception as e:
        print(f"Error loading location: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/download-location', methods=['POST'])
def download_location():
    """Download a new location"""
    global current_graph, current_location, rc, pf, shf
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    location = data.get('location')
    radius = data.get('radius', 5000)
    
    if not location:
        return jsonify({'error': 'Location required'}), 400
    
    try:
        import osmnx as ox
        print(f"📥 Downloading {location} with radius {radius}m...")
        
        # Download graph
        G = ox.graph_from_address(location, dist=radius, network_type='drive', simplify=True)
        
        # Create safe filename
        safe_name = location.lower().replace(',', '').replace(' ', '_')[:50]
        ensure_data_directory()
        filename = os.path.join(DATA_DIR, f"{safe_name}.pkl")
        
        # Save graph
        with open(filename, 'wb') as f:
            pickle.dump(G, f)
        
        # Save metadata
        metadata = {
            'location': location,
            'nodes': len(G.nodes),
            'edges': len(G.edges),
            'download_time': datetime.now().isoformat(),
            'radius': radius
        }
        
        with open(filename.replace('.pkl', '_metadata.json'), 'w') as f:
            json.dump(metadata, f)
        
        # Auto-load the downloaded location
        current_graph = G
        current_location = safe_name
        
        if initialize_components(current_graph, current_location):
            print(f"✅ Downloaded and loaded: {location}")
            return jsonify({
                'success': True,
                'location': current_location,
                'stats': metadata
            })
        else:
            return jsonify({'error': 'Failed to initialize components'}), 500
        
    except Exception as e:
        print(f"❌ Download error: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/route-with-instructions', methods=['POST', 'OPTIONS'])
def find_route_with_instructions():
    """Find route and generate turn-by-turn instructions"""
    global pf
    
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response, 200
    
    # Check if path finder is initialized
    if pf is None:
        return jsonify({'error': 'No location loaded. Please download a location first.'}), 400
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        print(f"📍 Route request received")
        
        start = data.get('start')
        end = data.get('end')
        
        if not start or not end:
            return jsonify({'error': 'Start and end points required'}), 400
        
        # Extract coordinates
        try:
            start_lat = float(start.get('lat', 0))
            start_lon = float(start.get('lon', start.get('lng', 0)))
            end_lat = float(end.get('lat', 0))
            end_lon = float(end.get('lon', end.get('lng', 0)))
        except (ValueError, TypeError) as e:
            return jsonify({'error': f'Invalid coordinate format: {e}'}), 400
        
        print(f"From: ({start_lat:.4f}, {start_lon:.4f}) To: ({end_lat:.4f}, {end_lon:.4f})")
        
        # Find nearest nodes
        source = pf.find_nearest_node(start_lat, start_lon)
        target = pf.find_nearest_node(end_lat, end_lon)
        
        if source is None or target is None:
            return jsonify({'error': 'Could not find nearby roads'}), 404
        
        print(f"Source node: {source}, Target node: {target}")
        
        # Find safest path
        path_nodes = pf.find_safest_route(source, target)
        
        if not path_nodes:
            return jsonify({'error': 'No path found between these points'}), 404
        
        print(f"✅ Path found with {len(path_nodes)} nodes")
        
        # Convert to coordinates
        path_coords = pf.path_to_coordinates(path_nodes)
        
        # Calculate statistics
        risk = pf.calculate_path_risk(path_nodes)
        distance = pf.calculate_path_distance(path_nodes)
        instructions = pf.generate_route_instructions(path_nodes)
        
        response_data = {
            'success': True,
            'path': path_coords,
            'instructions': instructions,
            'statistics': {
                'risk': risk,
                'distance_m': distance,
                'distance_km': round(distance / 1000, 2),
                'time_min': round((distance / 1000) / 40 * 60, 1),
                'mode': 'safest'
            }
        }
        
        print(f"📊 Route stats: {response_data['statistics']['distance_km']}km, {response_data['statistics']['time_min']}min, risk: {risk:.2f}")
        return jsonify(response_data)
        
    except nx.NetworkXNoPath:
        return jsonify({'error': 'No path found between these points'}), 404
    except Exception as e:
        print(f"❌ Route error: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/safe-havens', methods=['GET'])
def get_safe_havens():
    """Get all safe havens"""
    global shf
    if shf is None or not hasattr(shf, 'safe_havens'):
        return jsonify({'havens': []})
    return jsonify({'havens': shf.safe_havens})

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')