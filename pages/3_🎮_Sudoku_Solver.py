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

st.logo(
    image="https://upload.wikimedia.org/wikipedia/en/4/41/Flag_of_India.svg",
    link="https://www.linkedin.com/in/mahantesh-hiremath/",
    icon_image="https://upload.wikimedia.org/wikipedia/en/4/41/Flag_of_India.svg"
)

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

def generate_solved_sudoku():
    grid = np.zeros((9, 9), dtype=int)
    # Fill diagonal 3x3 boxes
    for box in range(0, 9, 3):
        nums = list(range(1, 10))
        np.random.shuffle(nums)
        for i in range(3):
            for j in range(3):
                grid[box + i][box + j] = nums[i * 3 + j]
    
    # Solve the rest using backtracking
    solve_with_backtracking(grid, "None")
    return grid

def create_puzzle(solved_grid, difficulty=0.6):
    puzzle = solved_grid.copy()
    cells = [(i, j) for i in range(9) for j in range(9)]
    np.random.shuffle(cells)
    
    # Remove numbers while ensuring unique solution
    for i, j in cells:
        temp = puzzle[i][j]
        puzzle[i][j] = 0
        # Make copy for solving
        board_copy = puzzle.copy()
        # If it doesn't have a unique solution, restore the number
        if len([solve_with_backtracking(board_copy, "None")]) != 1:
            puzzle[i][j] = temp
        # Stop if we've reached desired difficulty
        if np.count_nonzero(puzzle == 0) >= difficulty * 81:
            break
    
    return puzzle

# Add random puzzle button
if st.button("Fill Numbers"):
    # Generate a complete solved Sudoku
    solved_grid = generate_solved_sudoku()
    # Create puzzle by removing numbers while ensuring unique solution
    puzzle = create_puzzle(solved_grid)
    st.session_state.sudoku_grid = puzzle

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
        # Store results for all combinations
        results = []
        algorithms = ["Backtracking", "Forward Checking", "Arc Consistency"]
        heuristics = ["None", "MRV", "Degree", "LCV"]
        
        # Run each combination 10 times
        for alg in algorithms:
            for heur in heuristics:
                times = []
                for _ in range(10):
                    start_time = time.time()
                    grid = st.session_state.sudoku_grid.copy()
                    
                    if alg == "Backtracking":
                        solved = solve_with_backtracking(grid, heur)
                    elif alg == "Forward Checking":
                        solved = solve_with_forward_checking(grid, heur)
                    else:
                        solved = solve_with_arc_consistency(grid, heur)
                    
                    end_time = time.time()
                    times.append(end_time - start_time)
                
                # Store average results
                results.append({
                    'Algorithm': alg,
                    'Heuristic': heur,
                    'Avg Time': f"{np.mean(times):.4f}",
                    'Std Dev': f"{np.std(times):.4f}"
                })
        
        # Display current solution
        st.subheader("Solution:")
        st.write(solved)
        
        # Display performance comparison table
        st.subheader("Performance Comparison")
        df = pd.DataFrame(results)
        st.dataframe(df)
        
        # Display analysis
        st.subheader("Analysis")
        st.markdown("""
        **Algorithm Performance Analysis:**
        1. Forward Checking typically performs better than simple Backtracking due to early constraint detection
        2. Arc Consistency provides additional pruning but has overhead for constraint propagation
        
        **Heuristic Impact:**
        1. MRV helps by selecting variables with fewer remaining values first
        2. Degree heuristic prioritizes more constrained variables
        3. LCV can reduce branching factor but has overhead for value ordering
        """)

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
