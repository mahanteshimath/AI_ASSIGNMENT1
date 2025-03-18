import numpy as np
import time
import heapq
from math import radians, cos, sin, asin, sqrt
import geopandas as gpd
import os

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate the great circle distance between two points in kilometers."""
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of Earth in kilometers
    return c * r

def load_city_data():
    """Load city data from India taluka GeoJSON file."""
    try:
        # Define the absolute path to the data file
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_path = os.path.join(base_dir, "data", "india_taluk.geojson")
        
        # Check if file exists
        if not os.path.exists(data_path):
            print(f"Data file not found at: {data_path}")
            raise FileNotFoundError("GeoJSON file not found")

        # Load the GeoJSON file
        gdf = gpd.read_file(data_path)
        
        # Project to a suitable CRS for India
        # EPSG:32643 is UTM zone 43N which covers most of India
        gdf = gdf.to_crs("EPSG:32643")
        
        # Calculate centroids (now in meters)
        gdf['centroid'] = gdf.geometry.centroid
        
        # Project back to WGS84 (EPSG:4326) for lat/lon coordinates
        gdf = gdf.to_crs("EPSG:4326")
        # Recalculate centroids in WGS84
        gdf['centroid'] = gdf['centroid'].to_crs("EPSG:4326")
        
        # Create cities dictionary
        cities = {}
        for idx, row in gdf.iterrows():
            city_key = f"{row['NAME_3']}, {row['NAME_2']}"  # City, District
            cities[city_key] = {
                "lat": row.centroid.y,
                "lon": row.centroid.x,
                "state": row['NAME_1'],
                "district": row['NAME_2'],
                "city": row['NAME_3']
            }
        
        # Build neighbors dictionary using projected geometries for accurate spatial operations
        gdf_projected = gdf.to_crs("EPSG:32643")
        neighbors = {}
        for city1 in cities.keys():
            neighbors[city1] = []
            city1_geom = gdf_projected[
                (gdf_projected['NAME_3'] == cities[city1]['city']) & 
                (gdf_projected['NAME_2'] == cities[city1]['district'])
            ].geometry.iloc[0]
            
            for city2 in cities.keys():
                if city1 != city2:
                    city2_geom = gdf_projected[
                        (gdf_projected['NAME_3'] == cities[city2]['city']) & 
                        (gdf_projected['NAME_2'] == cities[city2]['district'])
                    ].geometry.iloc[0]
                    
                    # Use projected geometries for distance calculation (now in meters)
                    if city1_geom.touches(city2_geom) or city1_geom.distance(city2_geom) < 100:  # 100 meters threshold
                        neighbors[city1].append(city2)
        
        return cities, neighbors

    except Exception as e:
        print(f"Error loading city data: {e}")
        # Fallback data with major Indian cities
        cities = {
            "Delhi": {
                "lat": 28.6139, "lon": 77.2090,
                "state": "Delhi", "district": "Central Delhi",
                "city": "Delhi"
            },
            "Mumbai": {
                "lat": 19.0760, "lon": 72.8777,
                "state": "Maharashtra", "district": "Mumbai City",
                "city": "Mumbai"
            },
            "Bangalore": {
                "lat": 12.9716, "lon": 77.5946,
                "state": "Karnataka", "district": "Bangalore Urban",
                "city": "Bangalore"
            },
            "Chennai": {
                "lat": 13.0827, "lon": 80.2707,
                "state": "Tamil Nadu", "district": "Chennai",
                "city": "Chennai"
            },
            "Kolkata": {
                "lat": 22.5726, "lon": 88.3639,
                "state": "West Bengal", "district": "Kolkata",
                "city": "Kolkata"
            },
            "Hyderabad": {
                "lat": 17.3850, "lon": 78.4867,
                "state": "Telangana", "district": "Hyderabad",
                "city": "Hyderabad"
            },
            "Ahmedabad": {
                "lat": 23.0225, "lon": 72.5714,
                "state": "Gujarat", "district": "Ahmedabad",
                "city": "Ahmedabad"
            },
            "Pune": {
                "lat": 18.5204, "lon": 73.8567,
                "state": "Maharashtra", "district": "Pune",
                "city": "Pune"
            },
            "Jaipur": {
                "lat": 26.9124, "lon": 75.7873,
                "state": "Rajasthan", "district": "Jaipur",
                "city": "Jaipur"
            },
            "Lucknow": {
                "lat": 26.8467, "lon": 80.9462,
                "state": "Uttar Pradesh", "district": "Lucknow",
                "city": "Lucknow"
            }
        }

        # Define realistic connections between major cities
        neighbors = {
            "Delhi": ["Jaipur", "Lucknow"],
            "Mumbai": ["Pune", "Ahmedabad"],
            "Bangalore": ["Chennai", "Hyderabad"],
            "Chennai": ["Bangalore", "Hyderabad"],
            "Kolkata": ["Hyderabad"],
            "Hyderabad": ["Chennai", "Mumbai", "Bangalore"],
            "Ahmedabad": ["Mumbai", "Jaipur"],
            "Pune": ["Mumbai", "Hyderabad"],
            "Jaipur": ["Delhi", "Ahmedabad"],
            "Lucknow": ["Delhi", "Kolkata"]
        }
        
        return cities, neighbors

def run_search(city1, city2, algorithm="A*", heuristic_type="Straight-line", cities=None, neighbors=None):
    """Run the specified search algorithm to find optimal meeting point."""
    
    def get_heuristic(state):
        """Get heuristic value based on selected type."""
        c1, c2 = state
        dist = haversine_distance(
            cities[c1]["lat"], cities[c1]["lon"],
            cities[c2]["lat"], cities[c2]["lon"]
        )
        return dist if heuristic_type == "Straight-line" else dist * 1.4  # 1.4 factor for road distance
    
    def get_step_cost(city_from, city_to):
        """Calculate actual cost between neighboring cities."""
        return 2 * haversine_distance(
            cities[city_from]["lat"], cities[city_from]["lon"],
            cities[city_to]["lat"], cities[city_to]["lon"]
        )
    
    start_time = time.time()
    nodes_generated = 0
    
    # Priority queue elements: (priority, path_cost, current_state, path)
    if algorithm == "Greedy Best-First":
        frontier = [(get_heuristic((city1, city2)), 0, (city1, city2), [city1, city2])]
    else:  # A*
        frontier = [(get_heuristic((city1, city2)) + 0, 0, (city1, city2), [city1, city2])]
    
    explored = set()
    
    while frontier:
        _, cost_so_far, current_state, path = heapq.heappop(frontier)
        current_city1, current_city2 = current_state
        
        # Check if cities are same (meeting point found)
        if current_city1 == current_city2:
            return {
                "path": path,
                "total_cost": cost_so_far,
                "nodes_generated": nodes_generated,
                "time_taken": time.time() - start_time
            }
        
        if current_state in explored:
            continue
            
        explored.add(current_state)
        
        # Generate successors
        for next_city1 in neighbors[current_city1]:
            for next_city2 in neighbors[current_city2]:
                nodes_generated += 1
                new_state = (next_city1, next_city2)
                
                # Calculate costs
                step_cost = max(
                    get_step_cost(current_city1, next_city1),
                    get_step_cost(current_city2, next_city2)
                )
                new_cost = cost_so_far + step_cost
                
                if algorithm == "Greedy Best-First":
                    priority = get_heuristic(new_state)
                else:  # A*
                    priority = new_cost + get_heuristic(new_state)
                
                heapq.heappush(frontier, (
                    priority,
                    new_cost,
                    new_state,
                    path + [next_city1, next_city2]
                ))
    
    return None  # No solution found
