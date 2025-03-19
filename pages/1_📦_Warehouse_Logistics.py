import streamlit as st
import numpy as np
from utils.warehouse_utils import setup_warehouse, run_agent_simulation

st.set_page_config(page_title="Warehouse Logistics", page_icon="📦")

st.logo(
    image="https://upload.wikimedia.org/wikipedia/en/4/41/Flag_of_India.svg",
    link="https://www.linkedin.com/in/mahantesh-hiremath/",
    icon_image="https://upload.wikimedia.org/wikipedia/en/4/41/Flag_of_India.svg"
)

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
    
    # Create a stylized version of the warehouse grid with row and column numbers
    html_grid = "<div style='font-family: monospace; line-height: 1.2;'>"
    
    # Add column numbers header
    html_grid += "<div style='margin-left: 25px;'>"  # Offset for row numbers
    html_grid += "".join([f"<span style='display: inline-block; width: 30px; text-align: center; color: #666;'>{i}</span>" for i in range(M)])
    html_grid += "</div>"
    
    # Add rows with row numbers
    for i, row in enumerate(warehouse):
        html_grid += "<div>"
        # Add row number
        html_grid += f"<span style='display: inline-block; width: 25px; color: #666;'>{i}</span>"
        # Add cells
        for cell in row:
            if cell == '.':
                html_grid += "<span style='display: inline-block; width: 30px; text-align: center;'>⬜</span>"  # Empty space
            elif cell == 'O':
                html_grid += "<span style='display: inline-block; width: 30px; text-align: center;'>🚫</span>"  # Obstacle
            elif cell.startswith('P'):
                html_grid += f"<span style='display: inline-block; width: 30px; text-align: center; color: #1f77b4;'>📦<sub>{cell[1]}</sub></span>"  # Package with number
            elif cell.startswith('D'):
                html_grid += f"<span style='display: inline-block; width: 30px; text-align: center; color: #2ca02c;'>🎯<sub>{cell[1]}</sub></span>"  # Drop-off with number
        html_grid += "</div>"
    html_grid += "</div>"
    
    # Display the grid
    st.markdown(html_grid, unsafe_allow_html=True)
    
    # Add legend
    st.markdown("""
    **Legend:**
    - ⬜ Empty space
    - 🚫 Obstacle
    - 📦₁ Package (numbered)
    - 🎯₁ Drop-off point (numbered)
    """)

with col2:
    st.subheader("Locations")
    st.write("📦 Packages:", package_locations)
    st.write("🎯 Drop-offs:", dropoff_locations)
    st.write("🚫 Obstacles:", obstacle_locations)

# Simulation section
st.subheader("Agent Simulation with UCS")
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

st.markdown(
    '''
    <style>
    .streamlit-expanderHeader {
        background-color: blue;
        color: white; # Adjust this for expander header color
    }
    .streamlit-expanderContent {
        background-color: blue;
        color: white; # Expander content color
    }
    </style>
    ''',
    unsafe_allow_html=True
)

footer="""<style>

.footer {
position: fixed;
left: 0;
bottom: 0;
width: 100%;
background-color: #2C1E5B;
color: white;
text-align: center;
}
</style>
<div class="footer">
<p>Developed with ❤️ by <a style='display: inline; text-align: center;' href="https://www.linkedin.com/in/mahantesh-hiremath/" target="_blank">MAHANTESH HIREMATH</a></p>
</div>
"""
st.markdown(footer,unsafe_allow_html=True)