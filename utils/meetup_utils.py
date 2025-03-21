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

def run_search(city1, city2, algorithm="A*", heuristic_type="Straight-line", cities=None, neighbors=None):
    """Run the specified search algorithm to find optimal meeting point with complete paths for both."""
    
    def get_heuristic(state):
        c1, c2 = state
        dist = haversine_distance(
            cities[c1]["lat"], cities[c1]["lon"],
            cities[c2]["lat"], cities[c2]["lon"]
        )
        return dist if heuristic_type == "Straight-line" else dist * 1.4

    def get_step_cost(city_from, city_to):
        return haversine_distance(
            cities[city_from]["lat"], cities[city_from]["lon"],
            cities[city_to]["lat"], cities[city_to]["lon"]
        )

    start_time = time.time()
    nodes_generated = 0
    
    # Initialize state with separate paths for each person
    frontier = []
    initial_h = get_heuristic((city1, city2))
    heapq.heappush(frontier, (initial_h, 0, (city1, city2, [city1], [city2])))
    explored = set()
    
    while frontier:
        priority, cost_so_far, state = heapq.heappop(frontier)
        city_a, city_b, path_a, path_b = state
        nodes_generated += 1
        
        # Goal test: when both persons meet
        if city_a == city_b:
            return {
                "my_path": path_a,
                "friend_path": path_b,
                "total_cost": cost_so_far,
                "nodes_generated": nodes_generated,
                "time_taken": time.time() - start_time,
                "meeting_point": city_a
            }
            
        if (city_a, city_b) in explored:
            continue
            
        explored.add((city_a, city_b))
        
        # Generate successors
        successors = []
        # Option 1: Only first person moves
        for next_a in neighbors[city_a]:
            cost_a = get_step_cost(city_a, next_a)
            new_state = (next_a, city_b, path_a + [next_a], path_b)
            successors.append((new_state, cost_a))
        
        # Option 2: Only second person moves
        for next_b in neighbors[city_b]:
            cost_b = get_step_cost(city_b, next_b)
            new_state = (city_a, next_b, path_a, path_b + [next_b])
            successors.append((new_state, cost_b))
        
        # Option 3: Both move simultaneously
        for next_a in neighbors[city_a]:
            for next_b in neighbors[city_b]:
                cost_a = get_step_cost(city_a, next_a)
                cost_b = get_step_cost(city_b, next_b)
                step_cost = max(cost_a, cost_b)
                new_state = (next_a, next_b, path_a + [next_a], path_b + [next_b])
                successors.append((new_state, step_cost))
        
        for new_state, step_cost in successors:
            new_cost = cost_so_far + step_cost
            new_city_a, new_city_b, _, _ = new_state
            if (new_city_a, new_city_b) not in explored:
                h = get_heuristic((new_city_a, new_city_b))
                prio = h if algorithm == "Greedy Best-First" else new_cost + h
                heapq.heappush(frontier, (prio, new_cost, new_state))
    
    return {
        "my_path": None,
        "friend_path": None,
        "total_cost": None,
        "nodes_generated": nodes_generated,
        "time_taken": time.time() - start_time,
        "meeting_point": None
    }
