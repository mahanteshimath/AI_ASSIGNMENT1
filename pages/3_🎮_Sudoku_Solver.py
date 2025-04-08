import streamlit as st
import numpy as np
import time
import pandas as pd
from utils.sudoku_utils import (
    SudokuSolver,
    solve_with_backtracking,
    solve_with_forward_checking,
    solve_with_arc_consistency,
    is_valid_sudoku
)

st.set_page_config(page_title="Sudoku Solver", page_icon="🎮")

st.title("Sudoku Puzzle Solver")

st.markdown("""
This page implements a Sudoku solver using different CSP (Constraint Satisfaction Problem) algorithms:
- Simple Backtracking
- Forward Checking
- Arc Consistency

And various heuristics:
- MRV (Minimum Remaining Values)
- Degree Heuristic
- Least Constraining Value
""")

# Initialize session state
if 'sudoku_grid' not in st.session_state:
    st.session_state.sudoku_grid = np.zeros((9, 9), dtype=int)

# Input grid
st.subheader("Input Sudoku Grid")
cols = st.columns(9)
for i in range(9):
    for j in range(9):
        with cols[j]:
            st.session_state.sudoku_grid[i][j] = st.number_input(
                f"Cell ({i+1},{j+1})",
                min_value=0,
                max_value=9,
                value=int(st.session_state.sudoku_grid[i][j]),
                key=f"cell_{i}_{j}"
            )

# Algorithm selection
algorithm = st.selectbox(
    "Select Algorithm",
    ["Backtracking", "Forward Checking", "Arc Consistency"]
)

# Heuristic selection
heuristic = st.selectbox(
    "Select Heuristic",
    ["None", "MRV", "Degree", "LCV"]
)

if st.button("Solve"):
    if not is_valid_sudoku(st.session_state.sudoku_grid):
        st.error("Invalid Sudoku configuration!")
    else:
        times = []
        solved_grids = []
        
        for _ in range(10):
            start_time = time.time()
            grid = st.session_state.sudoku_grid.copy()
            
            if algorithm == "Backtracking":
                solved = solve_with_backtracking(grid, heuristic)
            elif algorithm == "Forward Checking":
                solved = solve_with_forward_checking(grid, heuristic)
            else:
                solved = solve_with_arc_consistency(grid, heuristic)
                
            end_time = time.time()
            times.append(end_time - start_time)
            solved_grids.append(solved)
        
        st.subheader("Solution:")
        st.write(solved_grids[0])
        
        st.subheader("Performance Analysis")
        st.write(f"Average solving time over 10 runs: {np.mean(times):.4f} seconds")
        st.write(f"Standard deviation: {np.std(times):.4f} seconds")

# Footer
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
