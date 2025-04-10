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

col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.image(
        "https://upload.wikimedia.org/wikipedia/en/4/41/Flag_of_India.svg",
        width=200
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
   - Compare different search algorithms (A* and Greedy Best-First Search)
   - Interactive map visualization with real Indian cities data

3. **🎮 Sudoku Solver**
   - Solve Sudoku puzzles using CSP and backtracking
   - Visualize the solving process step-by-step
   - Interactive grid input interface

4. **👑 N-Queens Solver**
   - Solve N-Queens problem using Simulated Annealing and Hill Climbing
   - Configure board size (4-20)
   - Interactive visualization of solutions

Use the sidebar to navigate between sections.
""")

st.markdown("""
### Technical Details:
- Built with Streamlit, NumPy, Pandas, and Plotly
- Implements various AI search algorithms and optimization techniques
- Interactive visualizations and real-time updates
- Constraint satisfaction problem solving
""")

st.markdown("""
### Available Problems:
1. 📦 Warehouse Logistics
2. 🤝 City Meetup
3. 🎮 Sudoku Solver
4. 👑 N-Queens Solver
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