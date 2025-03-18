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
    """Load city data with major Indian cities and their direct connections."""
    # Simplified city data with major cities and realistic connections
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
        "Hyderabad": {
            "lat": 17.3850, "lon": 78.4867,
            "state": "Telangana", "district": "Hyderabad",
            "city": "Hyderabad"
        }
    }
    
    # Define direct connections between cities (bidirectional)
    neighbors = {
        "Delhi": ["Mumbai", "Hyderabad"],
        "Mumbai": ["Delhi", "Bangalore", "Hyderabad"],
        "Bangalore": ["Mumbai", "Chennai", "Hyderabad"],
        "Chennai": ["Bangalore", "Hyderabad"],
        "Hyderabad": ["Delhi", "Mumbai", "Bangalore", "Chennai"]
    }
    
    return cities, neighbors

def run_search(city1, city2, algorithm="A*", heuristic_type="Straight-line", cities=None, neighbors=None):
    """Run the specified search algorithm to find optimal meeting point."""
    
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
    max_nodes = 1000  # Limit search space
    
    frontier = []
    initial_h = get_heuristic((city1, city2))
    heapq.heappush(frontier, (initial_h, 0, (city1, city2), [city1, city2]))
    explored = set()
    
    while frontier and nodes_generated < max_nodes:
        priority, cost_so_far, (city_a, city_b), path = heapq.heappop(frontier)
        nodes_generated += 1
        
        # Goal test
        if city_a == city_b:
            return {
                "path": path,
                "total_cost": cost_so_far,
                "nodes_generated": nodes_generated,
                "time_taken": time.time() - start_time,
                "meeting_point": city_a
            }
            
        if (city_a, city_b) in explored:
            continue
            
        explored.add((city_a, city_b))
        
        # Generate successors - one or both agents move to neighboring cities
        for next_a in neighbors[city_a]:
            cost_a = get_step_cost(city_a, next_a)
            
            # Option 1: Only agent A moves
            new_state = (next_a, city_b)
            if new_state not in explored:
                new_cost = cost_so_far + cost_a
                h = get_heuristic(new_state)
                priority = h if algorithm == "Greedy Best-First" else new_cost + h
                heapq.heappush(frontier, (priority, new_cost, new_state, path + [next_a, city_b]))
            
            # Option 2: Both agents move
            for next_b in neighbors[city_b]:
                cost_b = get_step_cost(city_b, next_b)
                new_state = (next_a, next_b)
                if new_state not in explored:
                    new_cost = cost_so_far + max(cost_a, cost_b)  # Parallel movement
                    h = get_heuristic(new_state)
                    priority = h if algorithm == "Greedy Best-First" else new_cost + h
                    heapq.heappush(frontier, (priority, new_cost, new_state, path + [next_a, next_b]))
        
        # Option 3: Only agent B moves
        for next_b in neighbors[city_b]:
            new_state = (city_a, next_b)
            if new_state not in explored:
                new_cost = cost_so_far + get_step_cost(city_b, next_b)
                h = get_heuristic(new_state)
                priority = h if algorithm == "Greedy Best-First" else new_cost + h
                heapq.heappush(frontier, (priority, new_cost, new_state, path + [city_a, next_b]))
    
    return {
        "path": None,
        "total_cost": None,
        "nodes_generated": nodes_generated,
        "time_taken": time.time() - start_time,
        "meeting_point": None
    }
