import numpy as np
import time
import heapq
from math import radians, cos, sin, asin, sqrt
import pandas as pd
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
    """Load city data from CSV file containing Indian cities."""
    try:
        # Get absolute path to the data file
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_path = os.path.join(base_dir, "data", "india_states_districts_cities_coordinates.csv")
        
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"CSV file not found at: {data_path}")

        # Load CSV file
        df = pd.read_csv(data_path)
        
        # Create cities dictionary
        cities = {}
        for _, row in df.iterrows():
            # Skip entries with missing coordinates
            if pd.isna(row['LATITUDE']) or pd.isna(row['LONGITUDE']):
                continue
                
            city_key = f"{row['CITY']}"
            cities[city_key] = {
                "lat": float(row['LATITUDE']),
                "lon": float(row['LONGITUDE']),
                "state": row['STATE'],
                
                "city": row['CITY']
            }
        
        # Build neighbors dictionary based on distance
        neighbors = {}
        distance_threshold = 100  # kilometers
        
        for city1 in cities:
            neighbors[city1] = []
            city1_info = cities[city1]
            
            for city2 in cities:
                if city1 != city2:
                    city2_info = cities[city2]
                    # Calculate distance between cities
                    distance = haversine_distance(
                        city1_info['lat'], city1_info['lon'],
                        city2_info['lat'], city2_info['lon']
                    )
                    # If cities are within threshold distance and in same or adjacent state
                    if distance < distance_threshold:
                        neighbors[city1].append(city2)
            
            # Ensure each city has at least 2-3 neighbors
            if len(neighbors[city1]) < 2:
                # Find closest cities if not enough neighbors
                distances = [(city2, haversine_distance(
                    city1_info['lat'], city1_info['lon'],
                    cities[city2]['lat'], cities[city2]['lon']
                )) for city2 in cities if city2 != city1]
                
                distances.sort(key=lambda x: x[1])
                # Add closest cities as neighbors
                for city, _ in distances[:3]:
                    if city not in neighbors[city1]:
                        neighbors[city1].append(city)
        
        return cities, neighbors

    except Exception as e:
        print(f"Error loading city data: {e}")
        # Return minimal fallback data
        cities = {
            "Delhi, Central Delhi": {
                "lat": 28.6139, "lon": 77.2090,
                "state": "Delhi", "district": "Central Delhi",
                "city": "Delhi"
            },
            "Mumbai, Mumbai City": {
                "lat": 19.0760, "lon": 72.8777,
                "state": "Maharashtra", "district": "Mumbai City",
                "city": "Mumbai"
            },
            # ... more fallback cities if needed ...
        }
        
        neighbors = {
            "Delhi, Central Delhi": ["Mumbai, Mumbai City"],
            "Mumbai, Mumbai City": ["Delhi, Central Delhi"],
            # ... more fallback neighbors if needed ...
        }
        return cities, neighbors

def run_search(start_city, end_city, algorithm, heuristic_type, cities, neighbors):
    start_time = time.time()
    nodes_generated = 0
    
    def heuristic(current, goal):
        # Calculate straight-line distance using haversine
        h = haversine_distance(
            cities[current]["lat"], cities[current]["lon"],
            cities[goal]["lat"], cities[goal]["lon"]
        )
        # Add 40% for road distance heuristic to account for real roads
        if heuristic_type == "Road Distance":
            h *= 1.4
        return h
    
    def get_path_cost(path):
        # Calculate actual cost of path
        cost = 0
        for i in range(len(path) - 1):
            cost += haversine_distance(
                cities[path[i]]["lat"], cities[path[i]]["lon"],
                cities[path[i + 1]]["lat"], cities[path[i + 1]]["lon"]
            )
        return cost
    
    # Priority queue based on algorithm type
    if algorithm == "A*":
        # For A*, we use f(n) = g(n) + h(n)
        frontier = [(0, 0, [start_city])]  # (f_score, g_score, path)
    else:  # Greedy Best-First
        # For Greedy, we only use h(n)
        frontier = [(heuristic(start_city, end_city), 0, [start_city])]  # (h_score, path_cost, path)
    
    visited = set()
    
    while frontier:
        if algorithm == "A*":
            f_score, g_score, current_path = heapq.heappop(frontier)
        else:
            h_score, _, current_path = heapq.heappop(frontier)
        
        current_city = current_path[-1]
        nodes_generated += 1
        
        if current_city == end_city:
            return {
                "path": current_path,
                "total_cost": get_path_cost(current_path),
                "meeting_point": current_path[len(current_path)//2],
                "nodes_generated": nodes_generated,
                "time_taken": time.time() - start_time
            }
        
        if current_city in visited:
            continue
        
        visited.add(current_city)
        
        for next_city in neighbors[current_city]:
            if next_city not in visited:
                new_path = current_path + [next_city]
                if algorithm == "A*":
                    # A* uses both path cost and heuristic
                    new_g_score = get_path_cost(new_path)
                    new_h_score = heuristic(next_city, end_city)
                    new_f_score = new_g_score + new_h_score
                    heapq.heappush(frontier, (new_f_score, new_g_score, new_path))
                else:
                    # Greedy Best-First only uses heuristic
                    new_h_score = heuristic(next_city, end_city)
                    path_cost = get_path_cost(new_path)  # Only for record keeping
                    heapq.heappush(frontier, (new_h_score, path_cost, new_path))
    
    return {
        "path": None,
        "total_cost": None,
        "meeting_point": None,
        "nodes_generated": nodes_generated,
        "time_taken": time.time() - start_time
    }
