import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time
import seaborn as sns
from matplotlib.patches import Rectangle

def calculate_conflicts(state):
    n = len(state)
    conflicts = 0
    for i in range(n):
        for j in range(i + 1, n):
            if state[i] == state[j] or abs(state[i] - state[j]) == abs(i - j):
                conflicts += 1
    return conflicts

def simulated_annealing(n, max_iterations=10000, initial_temp=1.0, cooling_rate=0.995, T_min=0.0):
    # Initial state: random queen positions
    current_state = np.random.randint(0, n, size=n)
    current_cost = calculate_conflicts(current_state)
    temperature = initial_temp
    
    costs = []
    temperatures = []
    acceptance_probs = []  # Track acceptance probabilities
    
    for iteration in range(max_iterations):
        if current_cost == 0 or temperature < T_min:
            break
            
        # Generate neighbor by moving one random queen
        new_state = current_state.copy()
        queen = np.random.randint(0, n)
        new_position = np.random.randint(0, n)
        new_state[queen] = new_position
        
        new_cost = calculate_conflicts(new_state)
        cost_diff = new_cost - current_cost
        
        # Calculate acceptance probability
        if cost_diff < 0:
            acceptance_prob = 1.0
        else:
            acceptance_prob = np.exp(-cost_diff / temperature) if temperature > 0 else 0.0
        
        # Accept if better or probabilistically if worse
        if np.random.random() < acceptance_prob:
            current_state = new_state
            current_cost = new_cost
            
        temperature *= cooling_rate
        costs.append(current_cost)
        temperatures.append(temperature)
        acceptance_probs.append(acceptance_prob)
        
    return current_state, costs, temperatures, acceptance_probs

def hill_climbing(n, max_iterations=10000):
    current_state = np.random.randint(0, n, size=n)
    current_cost = calculate_conflicts(current_state)
    
    costs = []
    
    for iteration in range(max_iterations):
        if current_cost == 0:
            break
            
        # Try all possible moves for each queen
        improved = False
        for queen in range(n):
            original_pos = current_state[queen]
            best_cost = current_cost
            best_pos = original_pos
            
            for new_pos in range(n):
                if new_pos != original_pos:
                    current_state[queen] = new_pos
                    new_cost = calculate_conflicts(current_state)
                    if new_cost < best_cost:
                        best_cost = new_cost
                        best_pos = new_pos
                        improved = True
            
            current_state[queen] = best_pos
            current_cost = best_cost
        
        costs.append(current_cost)
        if not improved:
            break
            
    return current_state, costs, [0] * len(costs)  # Dummy temperatures

def plot_board(queens):
    n = len(queens)
    board = np.zeros((n, n))
    for i, q in enumerate(queens):
        board[q, i] = 1
    
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(board, cmap='binary')
    
    for i in range(n):
        for j in range(n):
            if (i + j) % 2 == 0:
                ax.add_patch(Rectangle((j - 0.5, i - 0.5), 1, 1, fill=True, color='lightgray'))
            
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.grid(True)
    return fig

st.set_page_config(page_title="N-Queens Solver", page_icon="👑")
st.title("N-Queens Solver")
st.markdown("""
This page implements N-Queens solver using:
- Simulated Annealing (SA)
- Hill Climbing (HC)

And compares their performance and behavior.
""")

n_queens = st.slider("Select board size (N)", min_value=4, max_value=20, value=8)
algorithm = st.radio("Select Algorithm", ["Simulated Annealing", "Hill Climbing"])

# Add temperature controls
col1, col2 = st.columns(2)
with col1:
    initial_temp = st.number_input("Initial Temperature", 0.0, 10.0, 1.0, 0.1)
with col2:
    cooling_rate = st.number_input("Cooling Rate", 0.9, 0.999, 0.995, 0.001)

if st.button("Solve"):
    start_time = time.time()
    
    if algorithm == "Simulated Annealing":
        solution, costs, temperatures, acceptance_probs = simulated_annealing(
            n_queens, initial_temp=initial_temp, cooling_rate=cooling_rate
        )
    else:
        # For Hill Climbing, use SA with T=0
        solution, costs, temperatures, acceptance_probs = simulated_annealing(
            n_queens, initial_temp=0.0, cooling_rate=1.0
        )
        
    end_time = time.time()
    
    # Display solution
    st.subheader("Solution")
    if calculate_conflicts(solution) == 0:
        st.success(f"Found solution in {end_time - start_time:.4f} seconds!")
    else:
        st.error("No solution found!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.pyplot(plot_board(solution))
    
    with col2:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(costs, label='Conflicts')
        ax.set_xlabel('Iteration')
        ax.set_ylabel('Number of Conflicts')
        ax.legend()
        st.pyplot(fig)
    
    # Enhanced analysis section
    st.subheader("Algorithm Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(costs, label='Conflicts')
        ax.set_xlabel('Iteration')
        ax.set_ylabel('Number of Conflicts')
        ax.legend()
        st.pyplot(fig)
    
    with col2:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(acceptance_probs, label='Acceptance Probability')
        ax.set_xlabel('Iteration')
        ax.set_ylabel('P(accept)')
        ax.legend()
        st.pyplot(fig)
    
    # Theoretical comparison
    st.subheader("Theoretical Analysis")
    st.markdown("""
    #### SA vs HC Comparison
    - **Hill Climbing (T=0)**: Only accepts improving moves
        - P(accept) = 1 if ΔE < 0
        - P(accept) = 0 if ΔE > 0
    
    - **Simulated Annealing (T>0)**:
        - P(accept) = 1 if ΔE < 0
        - P(accept) = exp(-ΔE/T) if ΔE > 0
        
    The temperature T controls exploration:
    - High T → More random exploration
    - Low T → More exploitation
    - T=0 → Pure hill climbing behavior
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
