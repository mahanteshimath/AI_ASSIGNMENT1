import streamlit as st
import numpy as np
import time
import pandas as pd
import random
from utils.sudoku_utils import (
    SudokuCSP,
    backtracking_search,
    backtracking_with_inference,
    evaluate_heuristics
)

st.set_page_config(page_title="Sudoku Solver", page_icon="🎮", layout="wide")
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

# Create tabs for different parts
tab1, tab2, tab3, tab4 = st.tabs([
    "Part 1: CSP Representation", 
    "Part 2: Basic Backtracking", 
    "Part 3: Constraint Propagation",
    "Part 4: Heuristics Analysis"
])

# Initialize session state for grid
if 'sudoku_grid' not in st.session_state:
    st.session_state.sudoku_grid = "..3.2.6..9..3.5..1..18.64....81.29..7.......8..67.82....26.95..8..2.3..9..5.1.3.."

def create_styled_sudoku_df(grid_dict):
    """Convert grid dict to styled dataframe"""
    # Create 9x9 DataFrame
    data = np.zeros((9, 9), dtype=int)
    rows = 'ABCDEFGHI'
    cols = '123456789'
    
    for i, r in enumerate(rows):
        for j, c in enumerate(cols):
            data[i][j] = grid_dict[r + c]
    
    df = pd.DataFrame(data, columns=list(range(1, 10)), index=list(rows))
    
    # Style the dataframe
    def color_cells(val):
        if val == 0:
            color = '#f4f4f4'  # Light gray for empty cells
        else:
            color = '#e6f3ff'  # Light blue for filled cells
        return f'background-color: {color}; color: black; font-weight: bold; font-size: 18px; text-align: center'
    
    styled_df = df.style.apply(lambda x: [color_cells(v) for v in x], axis=1)
    styled_df.set_properties(**{
        'width': '60px',
        'height': '60px',
        'border': '2px solid #000'
    })
    
    return styled_df

def generate_random_sudoku(difficulty='medium'):
    """Generate random solvable Sudoku puzzle"""
    # Difficulty settings (percentage of cells to remove)
    difficulty_levels = {
        'easy': 0.4,
        'medium': 0.5,
        'hard': 0.6,
        'expert': 0.7
    }
    
    # Start with a solved Sudoku
    base = 3
    side = base * base
    
    def pattern(r,c): 
        return (base*(r%base)+r//base+c)%side

    def shuffle(s): 
        return random.sample(s,len(s)) 
    
    # Generate solved puzzle
    rows = [g*base + r for g in shuffle(range(base)) for r in shuffle(range(base))] 
    cols = [g*base + c for g in shuffle(range(base)) for c in shuffle(range(base))]
    nums = shuffle(range(1,base*base+1))
    
    board = [[nums[pattern(r,c)] for c in cols] for r in rows]
    
    # Convert to string format
    solved = ''.join([str(board[i][j]) for i in range(9) for j in range(9)])
    
    # Create puzzle by removing numbers
    cells = list(range(81))
    random.shuffle(cells)
    remove_count = int(81 * difficulty_levels[difficulty])
    
    puzzle = list(solved)
    for i in range(remove_count):
        puzzle[cells[i]] = '.'
    
    return ''.join(puzzle)

def show_no_solution_theory():
    """Show theory dialog explaining why no solution exists"""
    with st.expander("Why No Solution Exists?", expanded=True):
        st.markdown("""
        ### Causes of No Solution:

        1. **Domain Wipeout** 🚫
        - Variable has no valid values remaining
        - All potential values violate constraints
        """)

with tab1:
    st.markdown("""
    ## Part 1: CSP Representation
    The Sudoku puzzle is represented as a Constraint Satisfaction Problem (CSP) with:
    - **Variables**: The 81 cells in the 9x9 grid
    - **Domain**: Each cell can take values from 1-9
    - **Constraints**: No number repeats in any row, column, or 3x3 box
    """)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Initial Sudoku Grid")
        input_method = st.radio(
            "Choose input method:",
            ["Generate Random Puzzle", "Enter Custom Puzzle"]
        )
        
        if input_method == "Generate Random Puzzle":
            difficulty = st.select_slider(
                "Select difficulty level:",
                options=['easy', 'medium', 'hard', 'expert'],
                value='medium'
            )
            if st.button("Generate New Puzzle"):
                st.session_state.sudoku_grid = generate_random_sudoku(difficulty)
        else:
            st.session_state.sudoku_grid = st.text_input(
                "Enter Sudoku puzzle (use dots for empty cells):", 
                value=st.session_state.sudoku_grid
            )
    
    with col2:
        st.markdown("""
        ### How to Input:
        - Use dots (.) for empty cells
        - Enter digits (1-9) for filled cells
        - No spaces needed
        - Must be 81 characters long
        """)
    
    # Display current grid
    if st.session_state.sudoku_grid:
        csp = SudokuCSP(st.session_state.sudoku_grid)
        st.write("Current Grid:")
        styled_df = create_styled_sudoku_df(csp.grid)
        st.dataframe(styled_df, height=600)
        
        if st.button("Display CSP Representation"):
            st.write("Domain sizes for empty cells:")
            domain_data = []
            for square in csp.squares:
                if csp.grid[square] == 0:
                    domain_data.append({
                        'Cell': square,
                        'Possible Values': sorted(list(csp.domains[square])),
                        'Domain Size': len(csp.domains[square])
                    })
            if domain_data:
                st.dataframe(
                    pd.DataFrame(domain_data)
                    .style.background_gradient(subset=['Domain Size'])
                )

with tab2:
    st.markdown("""
    ## Part 2: Basic Backtracking
    Implement simple backtracking search without any optimizations.
    """)
    
    if st.button("Solve with Basic Backtracking"):
        csp = SudokuCSP(st.session_state.sudoku_grid)
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("Initial Grid:")
            styled_df = create_styled_sudoku_df(csp.grid)
            st.dataframe(styled_df, height=600)
        
        start_time = time.time()
        result = backtracking_search(csp)  # Changed to single assignment
        solve_time = time.time() - start_time
        
        with col2:
            if result:
                solution, iterations = result  # Unpack after checking result exists
                st.write(f"Solution found in {solve_time:.6f} seconds")
                st.write(f"Number of iterations: {iterations}")
                styled_df = create_styled_sudoku_df(solution)
                st.dataframe(styled_df, height=600)
            else:
                st.error("No solution found!")

with tab3:
    st.markdown("""
    ## Part 3: Constraint Propagation
    Compare different constraint propagation methods:
    - Forward Checking
    - Arc Consistency (AC-3)
    """)
    
    method = st.radio(
        "Select Constraint Propagation Method:",
        ["Forward Checking", "Arc Consistency (AC-3)"]
    )
    
    if st.button("Solve with Constraint Propagation"):
        try:
            csp = SudokuCSP(st.session_state.sudoku_grid)
            inference = "forward_checking" if method == "Forward Checking" else "ac3"
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("Initial Grid:")
                styled_df = create_styled_sudoku_df(csp.grid)
                st.dataframe(styled_df, height=600)
                
                # Show initial domains
                st.write("Initial Domains:")
                domain_data = []
                for square in csp.squares:
                    if csp.grid[square] == 0:
                        domain_data.append({
                            'Cell': square,
                            'Possible Values': sorted(list(csp.domains[square])),
                            'Domain Size': len(csp.domains[square])
                        })
                if domain_data:
                    st.dataframe(
                        pd.DataFrame(domain_data)
                        .style.background_gradient(subset=['Domain Size'])
                    )
            
            start_time = time.time()
            result = backtracking_with_inference(csp, inference=inference)  # Changed to single assignment
            solve_time = time.time() - start_time
            
            with col2:
                if result:
                    solution, iterations = result  # Unpack after checking result exists
                    st.write(f"Solution found in {solve_time:.6f} seconds!")
                    st.write(f"Number of iterations: {iterations}")
                    styled_df = create_styled_sudoku_df(solution)
                    st.dataframe(styled_df, height=600)
                else:
                    st.error("No solution found!")
                    st.warning("This could be due to:")
                    st.markdown("""
                    1. **Domain Wipeout**: No valid values left for some cell
                    2. **Constraint Violation**: Conflicting assignments
                    3. **Invalid Initial State**: Starting puzzle is unsolvable
                    """)
                    
                    # Show problematic cells
                    conflicts = []
                    for square in csp.squares:
                        if square in csp.domains and len(csp.domains[square]) == 0:
                            conflicts.append(square)
                    
                    if conflicts:
                        st.write("Cells with empty domains:")
                        st.write(conflicts)
        
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.write("Please check your input puzzle format.")

with tab4:
    st.markdown("""
    ## Part 4: Heuristics Analysis

    ### Q1(d): Analysis of Different Heuristic Methods
    
    This section analyzes how different heuristics affect backtracking search performance:
    
    1. **Variable Selection Heuristics**
       - MRV (Minimum Remaining Values): Selects variables with fewest legal values
       - Degree Heuristic: Prefers variables that constrain most other variables
       
    2. **Value Selection Heuristic**
       - LCV (Least Constraining Value): Orders values by their impact on future assignments
    """)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        runs = st.slider("Number of test runs:", min_value=5, max_value=50, value=10)
    with col2:
        difficulty = st.select_slider(
            "Test puzzle difficulty:",
            options=['easy', 'medium', 'hard', 'expert'],
            value='medium'
        )
    
    if st.button("Analyze Heuristic Performance"):
        with st.spinner("Running performance analysis..."):
            # Generate multiple test puzzles
            test_puzzles = [generate_random_sudoku(difficulty) for _ in range(3)]
            
            # Run analysis
            results = []
            for puzzle in test_puzzles:
                puzzle_results = evaluate_heuristics([puzzle], runs_per_puzzle=runs)
                results.extend(puzzle_results)
            
            # Aggregate results
            df = pd.DataFrame(results)
            
            # Display comprehensive comparison table
            st.subheader("Heuristic Performance Comparison")
            
            comparison_df = pd.DataFrame({
                'Metric': [
                    'Average Time (sec)',
                    'Standard Deviation',
                    'Average Iterations',
                    'Success Rate (%)',
                    'Memory Usage (units)',
                    'Speed Improvement (%)'
                ]
            })
            
            base_time = df[df['Algorithm']=='Basic Backtracking']['Avg Time'].mean()
            
            for algo in df['Algorithm'].unique():
                algo_data = df[df['Algorithm']==algo]
                improvement = ((base_time - algo_data['Avg Time'].mean()) / base_time * 100)
                
                comparison_df[algo] = [
                    f"{algo_data['Avg Time'].mean():.4f}",
                    f"{np.std(algo_data['Avg Time']):.4f}",
                    f"{algo_data['Avg Iterations'].mean():.0f}",
                    f"{algo_data['Success Rate'].mean()*100:.1f}%",
                    f"{algo_data['Peak Memory'].mean():.0f}",
                    f"{improvement:.1f}%" if algo != "Basic Backtracking" else "Baseline"
                ]
            
            st.table(comparison_df)
            
            # Visualizations
            st.subheader("Performance Metrics")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("Computational Time Comparison")
                time_data = pd.DataFrame({
                    'Algorithm': df['Algorithm'],
                    'Time (seconds)': df['Avg Time'],
                    'Standard Deviation': df.groupby('Algorithm')['Avg Time'].transform(np.std)
                })
                st.bar_chart(time_data.set_index('Algorithm')['Time (seconds)'])
            
            with col2:
                st.write("Iteration Count Comparison")
                st.bar_chart(df.set_index('Algorithm')['Avg Iterations'])
            
            # Analysis findings
            st.subheader("Analysis of Performance Improvements")
            st.markdown("""
            ### Key Findings:
            
            1. **MRV (Minimum Remaining Values)**
               - Reduces search space by {:.1f}% compared to basic backtracking
               - Most effective for highly constrained variables
               - Optimal for early-game decisions
            
            2. **MRV + Degree Heuristic**
               - Additional {:.1f}% improvement over MRV alone
               - Better tie-breaking in variable selection
               - Most effective in mid-game situations
            
            3. **Full Heuristic Combination**
               - Total improvement of {:.1f}% over basic backtracking
               - Optimal for difficult puzzles
               - Balances computational overhead with search efficiency
            
            ### Recommendations:
            
            - Easy Puzzles: Basic backtracking or MRV alone
            - Medium Puzzles: MRV + Degree heuristic
            - Hard/Expert Puzzles: Full heuristic combination
            """.format(
                (1 - df[df['Algorithm']=='MRV Only']['Avg Time'].mean() / base_time) * 100,
                (1 - df[df['Algorithm']=='MRV + Degree']['Avg Time'].mean() / 
                 df[df['Algorithm']=='MRV Only']['Avg Time'].mean()) * 100,
                (1 - df[df['Algorithm']=='MRV + Degree + LCV']['Avg Time'].mean() / base_time) * 100
            ))

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
