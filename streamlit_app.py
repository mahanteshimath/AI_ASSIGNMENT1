import streamlit as st
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import folium
from queue import PriorityQueue
import heapq, time
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

# --------------------- Warehouse Logistics Optimization ---------------------
def setup_warehouse(N=8, M=8, P=4, O=5):
    warehouse = np.full((N, M), '.')
    package_locations, dropoff_locations, obstacle_locations = [], [], []
    for i in range(P):
        while True:
            package = (np.random.randint(0, N), np.random.randint(0, M))
            dropoff = (np.random.randint(0, N), np.random.randint(0, M))
            if package != dropoff and package not in package_locations and dropoff not in dropoff_locations:
                package_locations.append(package)
                dropoff_locations.append(dropoff)
                break
    for idx, (x, y) in enumerate(package_locations):
        warehouse[x][y] = f'P{idx+1}'
    for idx, (x, y) in enumerate(dropoff_locations):
        warehouse[x][y] = f'D{idx+1}'
    for _ in range(O):
        while True:
            obstacle = (np.random.randint(0, N), np.random.randint(0, M))
            if warehouse[obstacle[0]][obstacle[1]] == '.':
                warehouse[obstacle[0]][obstacle[1]] = 'O'
                obstacle_locations.append(obstacle)
                break
    return warehouse, package_locations, dropoff_locations, obstacle_locations

def ucs(start, goal, grid, N, M):
    frontier = PriorityQueue()
    frontier.put((0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}
    directions = [(-1,0), (1,0), (0,-1), (0,1)]
    while not frontier.empty():
        cost, current = frontier.get()
        if current == goal:
            break
        for d in directions:
            next_pos = (current[0] + d[0], current[1] + d[1])
            if 0 <= next_pos[0] < N and 0 <= next_pos[1] < M:
                if grid[next_pos[0]][next_pos[1]] == 'O': 
                    continue
                new_cost = cost + 1
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    frontier.put((new_cost, next_pos))
                    came_from[next_pos] = current
    if goal in cost_so_far:
        path = []
        cur = goal
        while cur is not None:
            path.append(cur)
            cur = came_from[cur]
        path.reverse()
        return path, cost_so_far[goal]
    else:
        return None, None

def run_agent_simulation(warehouse, package_locations, dropoff_locations, start=(0,0)):
    N, M = warehouse.shape
    total_cost = 0
    total_reward = 0
    paths = []
    current_position = start
    for i in range(len(package_locations)):
        package = package_locations[i]
        dropoff = dropoff_locations[i]
        path_to_package, cost_to_package = ucs(current_position, package, warehouse, N, M)
        path_to_dropoff, cost_to_dropoff = ucs(package, dropoff, warehouse, N, M)
        total_cost += (cost_to_package + cost_to_dropoff)
        total_reward += 10  # delivery reward per package
        paths.append({
            "package": package,
            "path_to_package": path_to_package,
            "cost_to_package": cost_to_package,
            "dropoff": dropoff,
            "path_to_dropoff": path_to_dropoff,
            "cost_to_dropoff": cost_to_dropoff
        })
        current_position = dropoff
    final_reward = total_reward - total_cost
    return total_cost, total_reward, final_reward, paths

# --------------------- City Meetup Search ---------------------
def run_city_meetup_search():
    # For demonstration, we create a GeoDataFrame with three dummy districts.
    data = {
        "District": ["Alpha", "Beta", "Gamma"],
        "lat": [28.6139, 27.1767, 26.8467],
        "lon": [77.2090, 78.0081, 80.9462]
    }
    gdf = gpd.GeoDataFrame(data, geometry=gpd.points_from_xy(data["lon"], data["lat"]))
    
    # Dummy search results for Greedy Best First and A* search algorithms.
    result_greedy = {
        "path": ["Alpha", "Beta", "Beta"],
        "nodes_generated": 15,
        "time_taken": 0.01
    }
    result_astar = {
        "path": ["Alpha", "Gamma", "Gamma"],
        "nodes_generated": 20,
        "time_taken": 0.015
    }
    return gdf, result_greedy, result_astar

def build_meetup_map(gdf):
    # Create a Folium map centered at approximate center of India
    m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)
    # Add markers for each district
    for idx, row in gdf.iterrows():
        folium.Marker(
            location=[row.geometry.y, row.geometry.x],
            popup=f"{row['District']}",
            icon=folium.Icon(color="blue")
        ).add_to(m)
    return m

# --------------------- Streamlit App ---------------------
st.title("Artificial Intelligence– A1(IITJ)")
st.markdown("**Prepared by:** Mahantesh Hiremath- G24AIT2178")

section = st.sidebar.selectbox("Select Section", ["Warehouse Logistics Optimization", "City Meetup Search"])

if section == "Warehouse Logistics Optimization":
    st.header("Dynamic Goal-Based Agent for Warehouse Logistics Optimization")
    seed = st.sidebar.number_input("Random Seed", min_value=0, value=42)
    np.random.seed(seed)
    
    # Set parameters (can be made dynamic via sidebar inputs)
    N, M = 8, 8
    P = 4
    O = 5
    warehouse, package_locations, dropoff_locations, obstacle_locations = setup_warehouse(N, M, P, O)
    
    st.subheader("Initial Warehouse Configuration")
    st.write("Warehouse Grid:")
    st.text(warehouse)
    st.write("Package Locations:", package_locations)
    st.write("Drop-off Locations:", dropoff_locations)
    st.write("Obstacle Locations:", obstacle_locations)
    
    st.subheader("Agent Simulation")
    total_cost, total_reward, final_reward, paths = run_agent_simulation(warehouse, package_locations, dropoff_locations)
    for i, step in enumerate(paths):
        st.write(f"Package {i+1}:")
        st.write("  Path to package:", step["path_to_package"])
        st.write("  Cost:", step["cost_to_package"])
        st.write("  Path to drop-off:", step["path_to_dropoff"])
        st.write("  Cost:", step["cost_to_dropoff"])
    st.write("Total Cost:", total_cost)
    st.write("Total Reward:", total_reward)
    st.write("Final Reward (Reward - Cost):", final_reward)

elif section == "City Meetup Search":
    st.header("Optimal Common Meetup Search")
    st.markdown("Select your city, your friend’s city, heuristic function, and search strategy, then click Analyze.")

    # --- Data and Graph Setup ---
    # Define a small set of cities and their coordinates, plus a simple neighbor graph.
    cities = {
        "Alpha": {"lat": 28.6139, "lon": 77.2090},
        "Beta": {"lat": 27.1767, "lon": 78.0081},
        "Gamma": {"lat": 26.8467, "lon": 80.9462}
    }
    # Simple neighbor relations (assumed bidirectional)
    neighbors = {
        "Alpha": ["Beta"],
        "Beta": ["Alpha", "Gamma"],
        "Gamma": ["Beta"]
    }

    # --- UI Controls ---
    my_city = st.selectbox("Select Your City", list(cities.keys()))
    friend_city = st.selectbox("Select Friend's City", list(cities.keys()))
    heuristic_choice = st.selectbox("Select Heuristic Function", ["Straight-line", "Realistic"])
    search_strategy = st.selectbox("Select Search Strategy", ["Greedy", "A*"])

    if st.button("Analyze"):
        # --- Helper Functions ---
        def distance(city1, city2):
            # Euclidean distance on lat-lon (for demonstration)
            return np.sqrt((cities[city1]["lat"] - cities[city2]["lat"])**2 +
                           (cities[city1]["lon"] - cities[city2]["lon"])**2)

        def transition_cost(from_city, to_city):
            # Transition cost is twice the distance
            return 2 * distance(from_city, to_city)

        def heuristic(state):
            # 'state' is a tuple (cityA, cityB)
            d = distance(state[0], state[1])
            return 1.3 * d if heuristic_choice == "Realistic" else d

        def goal_condition(state):
            # Goal reached when both are in same city
            return state[0] == state[1]

        def get_successors(state):
            # Generate successors by moving each friend to a neighboring city.
            successors = []
            for nbr1 in neighbors.get(state[0], []):
                for nbr2 in neighbors.get(state[1], []):
                    cost = max(transition_cost(state[0], nbr1),
                               transition_cost(state[1], nbr2))
                    successors.append(( (nbr1, nbr2), cost ))
            return successors

        # --- Search Algorithms ---
        def greedy_search(initial_state):
            start_time = time.time()
            nodes = 0
            frontier = [(heuristic(initial_state), initial_state, [initial_state], 0)]
            while frontier:
                frontier.sort(key=lambda x: x[0])
                h_val, state, path, cost_so_far = frontier.pop(0)
                nodes += 1
                if goal_condition(state):
                    return {"path": path, "total_cost": cost_so_far, "nodes_generated": nodes, "time_taken": time.time()-start_time}
                for succ, step_cost in get_successors(state):
                    new_cost = cost_so_far + step_cost
                    frontier.append((heuristic(succ), succ, path + [succ], new_cost))
            return None

        def a_star_search(initial_state):
            start_time = time.time()
            nodes = 0
            frontier = [(heuristic(initial_state), 0, initial_state, [initial_state])]
            explored = set()
            while frontier:
                frontier.sort(key=lambda x: x[1] + heuristic(x[2]))
                f, cost_so_far, state, path = frontier.pop(0)
                nodes += 1
                if goal_condition(state):
                    return {"path": path, "total_cost": cost_so_far, "nodes_generated": nodes, "time_taken": time.time()-start_time}
                if state in explored:
                    continue
                explored.add(state)
                for succ, step_cost in get_successors(state):
                    new_cost = cost_so_far + step_cost
                    frontier.append((new_cost + heuristic(succ), new_cost, succ, path + [succ]))
            return None

        # --- Execution ---
        initial_state = (my_city, friend_city)
        if search_strategy == "Greedy":
            result = greedy_search(initial_state)
        else:
            result = a_star_search(initial_state)

        if result:
            st.write("Solution Path:", result["path"])
            st.write("Total Cost:", result["total_cost"])
            st.write("Nodes Generated:", result["nodes_generated"])
            st.write("Time Taken (s):", result["time_taken"])
        else:
            st.write("No solution found.")

        # --- Map Visualization ---
        # Center map between the two selected cities.
        center_lat = (cities[my_city]["lat"] + cities[friend_city]["lat"]) / 2
        center_lon = (cities[my_city]["lon"] + cities[friend_city]["lon"]) / 2
        m = folium.Map(location=[center_lat, center_lon], zoom_start=6)
        for city_name, info in cities.items():
            color = "green" if city_name == my_city else "blue" if city_name == friend_city else "orange"
            folium.Marker(location=[info["lat"], info["lon"]],
                          popup=city_name,
                          icon=folium.Icon(color=color)).add_to(m)
        st.subheader("City Map")
        st_folium(m, width=700, height=500)
