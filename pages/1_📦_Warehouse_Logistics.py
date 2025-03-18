import streamlit as st
import numpy as np
from utils.warehouse_utils import setup_warehouse, run_agent_simulation

st.set_page_config(page_title="Warehouse Logistics", page_icon="📦")

st.title("Warehouse Logistics Optimization")

# Sidebar controls
with st.sidebar:
    st.header("Configuration")
    seed = st.number_input("Random Seed", min_value=0, value=42)
    N = st.slider("Warehouse Width", min_value=5, max_value=10, value=8)
    M = st.slider("Warehouse Height", min_value=5, max_value=10, value=8)
    P = st.slider("Number of Packages", min_value=2, max_value=6, value=4)
    O = st.slider("Number of Obstacles", min_value=1, max_value=10, value=5)

# Set random seed
np.random.seed(seed)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Warehouse Configuration")
    warehouse, package_locations, dropoff_locations, obstacle_locations = setup_warehouse(N, M, P, O)
    
    # Create a stylized version of the warehouse grid
    html_grid = "<div style='font-family: monospace; line-height: 1;'>"
    for row in warehouse:
        html_grid += "<div>"
        for cell in row:
            if cell == '.':
                html_grid += "⬜"  # Empty space
            elif cell == 'O':
                html_grid += "🚫"  # Obstacle
            elif cell.startswith('P'):
                html_grid += "📦"  # Package
            elif cell.startswith('D'):
                html_grid += "🎯"  # Drop-off point
        html_grid += "</div>"
    html_grid += "</div>"
    
    st.markdown(html_grid, unsafe_allow_html=True)

with col2:
    st.subheader("Locations")
    st.write("📦 Packages:", package_locations)
    st.write("🎯 Drop-offs:", dropoff_locations)
    st.write("🚫 Obstacles:", obstacle_locations)

# Simulation section
st.subheader("Agent Simulation")
if st.button("Run Simulation"):
    with st.spinner("Running simulation..."):
        total_cost, total_reward, final_reward, paths = run_agent_simulation(
            warehouse, package_locations, dropoff_locations
        )
        
        # Display results in an organized way
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Cost", total_cost)
        with col2:
            st.metric("Total Reward", total_reward)
        with col3:
            st.metric("Final Reward", final_reward)
        
        # Show detailed path information in an expander
        with st.expander("View Detailed Paths"):
            for i, step in enumerate(paths, 1):
                st.markdown(f"**Package {i}**")
                st.write("Path to package:", step["path_to_package"])
                st.write("Path to drop-off:", step["path_to_dropoff"])
                st.write("---")
# Adding a footer
footer="""<style>
a:link , a:visited{
color: blue;
background-color: transparent;
text-decoration: underline;
}

a:hover,  a:active {
color: red;
background-color: transparent;
text-decoration: underline;
}

.footer {
position: fixed;
left: 0;
bottom: 0;
width: 100%;
background-color: white;
color: black;
text-align: center;
}
</style>
<div class="footer">
<p>Developed with ❤️ by <a style='display: inline; text-align: center;' href="https://bit.ly/atozaboutdata" target="_blank">MAHANTESH HIREMATH</a></p>
</div>
"""
st.markdown(footer,unsafe_allow_html=True)