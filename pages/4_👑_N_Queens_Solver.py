import streamlit as st
import numpy as np
import time
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from utils.queens_utils import NQueensSolver

def create_board_figure(board, n_queens):
    fig = go.Figure()
    
    # Add chess board pattern
    for i in range(n_queens):
        for j in range(n_queens):
            color = '#B58863' if (i + j) % 2 == 0 else '#F0D9B5'
            fig.add_trace(go.Scatter(
                x=[j, j+1, j+1, j, j],
                y=[i, i, i+1, i+1, i],
                fill="toself",
                fillcolor=color,
                line=dict(color='rgba(0,0,0,0)'),
                showlegend=False
            ))
    
    # Add queens
    for i in range(n_queens):
        for j in range(n_queens):
            if board[i][j] == 1:
                fig.add_trace(go.Scatter(
                    x=[j + 0.5],
                    y=[i + 0.5],
                    mode='text',
                    text=['♕'],
                    textfont=dict(size=32, color='#00008B'),
                    showlegend=False
                ))
    
    fig.update_layout(
        width=400, height=400,
        showlegend=False,
        xaxis=dict(range=[0, n_queens], showgrid=False, zeroline=False, visible=False),
        yaxis=dict(range=[0, n_queens], showgrid=False, zeroline=False, visible=False)
    )
    
    return fig

st.set_page_config(page_title="N-Queens Solver", page_icon="👑", layout="wide")

st.title("N-Queens Problem Solver")
st.markdown("""
Compare Simulated Annealing (SA) vs Hill Climbing (HC) for solving N-Queens problem.
- Simulated Annealing with temperature control
- Hill Climbing (SA with T=0)
- Interactive visualization and analysis
""")

# Move configuration to sidebar
with st.sidebar:
    st.subheader("Problem Configuration")
    n_queens = st.slider("Number of Queens (N)", min_value=4, max_value=20, value=8)
    algorithm = st.radio(
        "Select Algorithm",
        ["Simulated Annealing", "Hill Climbing"]
    )
    
    if algorithm == "Simulated Annealing":
        initial_temp = st.slider("Initial Temperature", 1.0, 20.0, 10.0, 0.5)
        cooling_rate = st.slider("Cooling Rate", 0.8, 0.99, 0.95, 0.01)

# Main content
col1, col2 = st.columns(2)

# Create button container for disable functionality
button_container = st.container()
with button_container:
    if st.button("Generate New Board and Solve", key="solve_button"):
        # Disable button during solving
        st.session_state.solving = True
        button_container.empty()  # Clear the enabled button
        # Show disabled button
        st.button("Generating Solution...", disabled=True)
        
        solver = NQueensSolver(n=n_queens)
        
        with st.spinner("Generating new board and solving..."):
            if algorithm == "Simulated Annealing":
                result = solver.simulated_annealing(
                    initial_temp=initial_temp,
                    cooling_rate=cooling_rate
                )
            else:
                result = solver.hill_climbing()
            
            # Display results
            st.write(f"Solution found in {result['time']:.4f} seconds")
            st.write(f"Iterations: {result['iterations']}")
            st.write(f"Final conflicts: {result['conflicts']}")
            
            # Display boards side by side
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Initial Board")
                fig_initial = create_board_figure(result['initial_board'], n_queens)
                st.plotly_chart(fig_initial)
                
            with col2:
                st.subheader("Final Board")
                fig_final = create_board_figure(result['solution'], n_queens)
                st.plotly_chart(fig_final)

        # Re-enable button after solving
        st.session_state.solving = False

# Show theory
with st.expander("Algorithm Details"):
    if algorithm == "Simulated Annealing":
        st.markdown("""
        ### Simulated Annealing
        1. **Temperature Control**
            - Starts with high temperature (T)
            - Gradually decreases T using cooling rate
            - Higher T means more exploration
            
        2. **Acceptance Probability**
            - P(accept) = exp(-ΔE/T)
            - Accepts worse moves when T is high
            - Becomes more selective as T decreases
            
        3. **Advantages**
            - Can escape local minima
            - Better global optimization
            - More robust solutions
        """)
    else:
        st.markdown("""
        ### Hill Climbing (SA with T=0)
        1. **Movement Strategy**
            - Only accepts better moves
            - No probability of accepting worse states
            - Equivalent to SA with T=0
            
        2. **Characteristics**
            - Fast convergence
            - Can get stuck in local minima
            - Less exploration of solution space
            
        3. **Limitations**
            - No escape from local optima
            - Solution quality depends on start state
            - May miss global optimum
        """)

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
