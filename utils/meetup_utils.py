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
            # Skip entries with missing coordinates.
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
        distance_threshold = 150  # kilometers
        
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

def run_search(my_city, friend_city, algorithm, heuristic_type, cities, neighbors):
    def heuristic(state):
        city1, city2 = state
        if heuristic_type == "Straight-line":
            return haversine_distance(cities[city1]["lat"], cities[city1]["lon"], cities[city2]["lat"], cities[city2]["lon"])
        elif heuristic_type == "Road Distance":
            return 1.4 * haversine_distance(cities[city1]["lat"], cities[city1]["lon"], cities[city2]["lat"], cities[city2]["lon"])
        return 0

    def get_neighbors(city):
        return neighbors.get(city, [])

    def search(start, goal, strategy):
        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}
        nodes_generated = 0

        while frontier:
            _, current = heapq.heappop(frontier)
            nodes_generated += 1

            if current == goal:
                break

            for next_city in get_neighbors(current):
                new_cost = cost_so_far[current] + 2 * haversine_distance(cities[current]["lat"], cities[current]["lon"], cities[next_city]["lat"], cities[next_city]["lon"])
                if next_city not in cost_so_far or new_cost < cost_so_far[next_city]:
                    cost_so_far[next_city] = new_cost
                    priority = new_cost + heuristic((next_city, goal)) if strategy == "A*" else heuristic((next_city, goal))
                    heapq.heappush(frontier, (priority, next_city))
                    came_from[next_city] = current

        path = []
        if goal in came_from:
            current = goal
            while current:
                path.append(current)
                current = came_from[current]
            path.reverse()

        return path, cost_so_far.get(goal, float('inf')), nodes_generated

    start_state = (my_city, friend_city)
    goal_state = (friend_city, my_city)

    start_time = time.time()
    path, total_cost, nodes_generated = search(my_city, friend_city, algorithm)
    time_taken = time.time() - start_time

    meeting_point = path[len(path) // 2] if path else None

    return {
        "path": path,
        "total_cost": total_cost,
        "nodes_generated": nodes_generated,
        "time_taken": time_taken,
        "meeting_point": meeting_point
    }
