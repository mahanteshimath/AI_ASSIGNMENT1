import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
import time, heapq, math
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static

# ================================
# 1. LOAD DATA AND PREPARE
# ================================

@st.cache_data
def load_data():
    # Adjust the file path as necessary.
    taluka_data = gpd.read_file("../archive/india_taluk.geojson")
    file_path = r"D:\IITJ AI\AI SLIDES\ASSIGNMENT\AI_ASSIGNMENT1\archive\india_taluk.geojson"
    taluka_data = gpd.read_file(file_path)

    taluka_data["centroid"] = taluka_data.geometry.centroid
    return taluka_data

taluka_data = load_data()

# For demonstration purposes, we select a subset of the data via a bounding box.
minx, miny, maxx, maxy = 75, 15, 85, 30
subset = taluka_data.cx[minx:maxx, miny:maxy].copy().reset_index(drop=True)

# Build a spatial index for efficient neighbor lookup.
spatial_index = subset.sindex

# ================================
# 2. BUILD THE NEIGHBOR DICTIONARY
# ================================

# Assume that talukas whose polygons "touch" are neighbors.
neighbors = {}
for idx, row in subset.iterrows():
    possible = list(spatial_index.query(row.geometry, predicate="touches"))
    possible = [i for i in possible if i != idx]  # Exclude self
    neighbors[idx] = possible

# ================================
# 3. DEFINE DISTANCE AND HEURISTICS
# ================================

def euclidean_distance(idx1, idx2):
    """Compute Euclidean distance between centroids of two talukas."""
    pt1 = subset.loc[idx1, "centroid"]
    pt2 = subset.loc[idx2, "centroid"]
    return pt1.distance(pt2)

# Heuristic 1: Straight-line distance.
def h_straight(state):
    cityA, cityB = state
    return euclidean_distance(cityA, cityB)

# Heuristic 2: Modified "road" distance (simulated by scaling).
def h_road(state, factor=1.3):
    return factor * h_straight(state)

# ================================
# 4. STATE-TRANSITION FUNCTION
# ================================

def get_neighbors(state):
    """
    For a state (city_A, city_B), generate all possible next states.
    Each agent moves to a neighboring city.
    The cost is the maximum of the two moves: cost = max(2 * d(A, A'), 2 * d(B, B')).
    """
    cityA, cityB = state
    next_states = []
    for nA in neighbors.get(cityA, []):
        for nB in neighbors.get(cityB, []):
            cost_A = 2 * euclidean_distance(cityA, nA)
            cost_B = 2 * euclidean_distance(cityB, nB)
            step_cost = max(cost_A, cost_B)
            next_states.append(((nA, nB), step_cost))
    return next_states

# ================================
# 5. SEARCH ALGORITHM IMPLEMENTATIONS
# ================================

def search(start_state, heuristic_fn, strategy="astar"):
    """
    General search routine for the two-agent meeting problem.
    
    Parameters:
      - start_state: tuple (city_index_A, city_index_B)
      - heuristic_fn: heuristic function to use
      - strategy: "greedy" for Greedy Best First Search, "astar" for A* Search.
      
    Returns a dictionary with:
      - path: list of states from start to goal,
      - total_cost: cumulative cost,
      - nodes_generated: total nodes expanded,
      - max_frontier_size: maximum size of the frontier,
      - execution_time: time taken in seconds.
    """
    frontier = []
    initial_priority = heuristic_fn(start_state) if strategy == "greedy" else (0 + heuristic_fn(start_state))
    heapq.heappush(frontier, (initial_priority, 0, start_state, [start_state]))
    
    explored = set()
    nodes_generated = 1
    max_frontier_size = 1
    start_time = time.time()
    
    while frontier:
        max_frontier_size = max(max_frontier_size, len(frontier))
        priority, cost_so_far, current_state, path = heapq.heappop(frontier)
        
        # Goal: both agents are in the same city.
        if current_state[0] == current_state[1]:
            elapsed_time = time.time() - start_time
            return {
                "path": path,
                "total_cost": cost_so_far,
                "nodes_generated": nodes_generated,
                "max_frontier_size": max_frontier_size,
                "execution_time": elapsed_time
            }
        
        if current_state in explored:
            continue
        explored.add(current_state)
        
        for next_state, step_cost in get_neighbors(current_state):
            new_cost = cost_so_far + step_cost
            if strategy == "greedy":
                new_priority = heuristic_fn(next_state)
            elif strategy == "astar":
                new_priority = new_cost + heuristic_fn(next_state)
            else:
                raise ValueError("Unknown strategy")
            heapq.heappush(frontier, (new_priority, new_cost, next_state, path + [next_state]))
            nodes_generated += 1
            
    elapsed_time = time.time() - start_time
    return {
        "path": None,
        "total_cost": None,
        "nodes_generated": nodes_generated,
        "max_frontier_size": max_frontier_size,
        "execution_time": elapsed_time
    }

# ================================
# 6. HELPER FUNCTION: PLOTTING
# ================================

def plot_meeting_path(result, start_state, title="Meeting Path"):
    if result["path"] is None:
        st.write("No solution path to plot.")
        return None
    path = result["path"]
    meeting_idx = path[-1][0]
    meeting_city = subset.loc[meeting_idx, "centroid"]
    
    fig, ax = plt.subplots(figsize=(8, 8))
    subset.plot(ax=ax, color="lightgray", edgecolor="black")
    
    startA = subset.loc[start_state[0], "centroid"]
    startB = subset.loc[start_state[1], "centroid"]
    ax.plot(startA.x, startA.y, marker="o", color="green", markersize=10, label="Your City")
    ax.plot(startB.x, startB.y, marker="o", color="blue", markersize=10, label="Friend's City")
    ax.plot(meeting_city.x, meeting_city.y, marker="*", color="red", markersize=15, label="Meeting City")
    
    ax.set_title(title)
    ax.legend()
    return fig

# ================================
# 7. STREAMLIT USER INTERFACE
# ================================

st.title("Common Meetup Finder")
st.markdown("Select two different cities from the sidebar and click **Run Analysis** to find an optimal meeting point.")

# Build a dictionary for city options from the subset.
# Format: "CityName (State)" mapped to the index.
city_options = {}
for idx, row in subset.iterrows():
    city_label = f"{row.get('NAME_3', 'City ' + str(idx))} ({row.get('NAME_1', 'Unknown')})"
    city_options[city_label] = idx

st.sidebar.title("City Selection")
your_city = st.sidebar.selectbox("Select Your City", list(city_options.keys()))
friend_city = st.sidebar.selectbox("Select Friend's City", list(city_options.keys()))

if city_options[your_city] == city_options[friend_city]:
    st.sidebar.warning("Please select two different cities!")

if st.sidebar.button("Run Analysis"):
    # Set the start state based on selected city indices.
    start_state = (city_options[your_city], city_options[friend_city])
    st.write("### Start State")
    st.write(f"Your City: **{your_city}**  |  Friend's City: **{friend_city}**")
    st.write(f"State indices: {start_state}")
    
    # Run search algorithms and display their metrics.
    st.write("## Search Results")
    
    st.write("### Greedy Best First Search (Straight-line heuristic)")
    result_greedy = search(start_state, heuristic_fn=h_straight, strategy="greedy")
    st.write(result_greedy)
    
    st.write("### A* Search (Straight-line heuristic)")
    result_astar = search(start_state, heuristic_fn=h_straight, strategy="astar")
    st.write(result_astar)
    
    st.write("### A* Search (Modified Road heuristic)")
    result_astar_road = search(start_state, heuristic_fn=lambda s: h_road(s, factor=1.3), strategy="astar")
    st.write(result_astar_road)
    
    # Display the meeting path plot (using A* with straight-line heuristic).
    st.write("## Meeting Path Plot (Matplotlib)")
    fig = plot_meeting_path(result_astar, start_state, title="A* (Straight-line Heuristic) Meeting Path")
    if fig is not None:
        st.pyplot(fig)
    
    # ================================
    # 8. INTERACTIVE MAP WITH FOLIUM
    # ================================
    
    st.write("## Interactive Map")
    avg_lat = subset["centroid"].y.mean()
    avg_lon = subset["centroid"].x.mean()
    india_map = folium.Map(location=[avg_lat, avg_lon], zoom_start=5)
    
    marker_cluster = MarkerCluster().add_to(india_map)
    for idx, row in subset.iterrows():
        lat = row["centroid"].y
        lon = row["centroid"].x
        city_name = row.get("NAME_3", f"City {idx}")
        folium.Marker(location=[lat, lon], popup=str(city_name)).add_to(marker_cluster)
    
    # Mark selected starting cities.
    startA = subset.loc[start_state[0], "centroid"]
    startB = subset.loc[start_state[1], "centroid"]
    folium.Marker(location=[startA.y, startA.x], popup="Your City",
                  icon=folium.Icon(color="green", icon="user")).add_to(india_map)
    folium.Marker(location=[startB.y, startB.x], popup="Friend's City",
                  icon=folium.Icon(color="blue", icon="user")).add_to(india_map)
    
    # If a meeting point was found, mark it.
    if result_astar["path"] is not None:
        meeting_idx = result_astar["path"][-1][0]
        meeting_city = subset.loc[meeting_idx, "centroid"]
        folium.Marker(location=[meeting_city.y, meeting_city.x], popup="Meeting City",
                      icon=folium.Icon(color="red", icon="star")).add_to(india_map)
    
    folium_static(india_map)
