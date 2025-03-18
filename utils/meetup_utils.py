import numpy as np
import time
import heapq
from math import radians, cos, sin, asin, sqrt

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate the great circle distance between two points in kilometers."""
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of Earth in kilometers
    return c * r

def load_city_data():
    """Load city data with real Indian cities and their connections."""
    cities = {
        "Delhi": {"lat": 28.6139, "lon": 77.2090, "state": "Delhi"},
        "Mumbai": {"lat": 19.0760, "lon": 72.8777, "state": "Maharashtra"},
        "Bangalore": {"lat": 12.9716, "lon": 77.5946, "state": "Karnataka"},
        "Chennai": {"lat": 13.0827, "lon": 80.2707, "state": "Tamil Nadu"},
        "Kolkata": {"lat": 22.5726, "lon": 88.3639, "state": "West Bengal"},
        "Hyderabad": {"lat": 17.3850, "lon": 78.4867, "state": "Telangana"},
        "Ahmedabad": {"lat": 23.0225, "lon": 72.5714, "state": "Gujarat"},
        "Jaipur": {"lat": 26.9124, "lon": 75.7873, "state": "Rajasthan"}
    }
    
    # Define realistic city connections based on major routes
    neighbors = {
        "Delhi": ["Jaipur", "Ahmedabad"],
        "Mumbai": ["Ahmedabad", "Bangalore", "Hyderabad"],
        "Bangalore": ["Chennai", "Hyderabad", "Mumbai"],
        "Chennai": ["Bangalore", "Hyderabad"],
        "Kolkata": ["Hyderabad"],
        "Hyderabad": ["Chennai", "Mumbai", "Kolkata", "Bangalore"],
        "Ahmedabad": ["Mumbai", "Delhi", "Jaipur"],
        "Jaipur": ["Delhi", "Ahmedabad"]
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
