import streamlit as st

st.set_page_config(
    page_title="AI Assignment 1&2",
    page_icon="🏠",
    layout="wide"
)

st.logo(
    image="https://upload.wikimedia.org/wikipedia/en/4/41/Flag_of_India.svg",
    link="https://www.linkedin.com/in/mahantesh-hiremath/",
    icon_image="https://upload.wikimedia.org/wikipedia/en/4/41/Flag_of_India.svg"
)

st.title("Artificial Intelligence– A1 and A2 (IITJ)")
st.markdown("**Prepared by:** Mahantesh Hiremath- G24AIT2178")

st.markdown("""
### Navigation Guide:
1. **📦 Warehouse Logistics Optimization**
   - Simulate a warehouse robot optimizing package delivery
   - Configure warehouse size, packages, and obstacles
   - Visualize paths and performance metrics

2. **🤝 City Meetup Search**
   - Find optimal meeting points between two cities
   - Compare different search algorithms and heuristics
   - Interactive map visualization

3. **🎮 Sudoku Solver**
   - Solve Sudoku puzzles using backtracking algorithm
   - Visualize the solving process
   - User-friendly interface for inputting puzzles



Use the sidebar to navigate between sections.
""")

st.markdown("""
### Available Problems:
1. 📦 Warehouse Logistics
2. 🤝 City Meetup
3. 🎮 Sudoku Solver
""")

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