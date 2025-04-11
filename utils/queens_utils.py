import numpy as np
import random
import math
from time import time

class NQueensSolver:
    def __init__(self, n=8):
        self.n = n
        self.board = None
        self.current_conflicts = 0
        self.temperature_history = []
        self.energy_history = []
    
    def initialize_random_state(self):
        """Initialize board with random queen positions (one per row)"""
        # Create empty board
        self.board = np.zeros((self.n, self.n))
        # Place queens randomly, one per row
        for i in range(self.n):
            j = random.randint(0, self.n-1)
            self.board[i][j] = 1
        self.current_conflicts = self.count_conflicts()
    
    def count_conflicts(self):
        """Count number of queen pairs that can attack each other"""
        conflicts = 0
        queen_positions = self.get_queen_positions()
        
        for i in range(len(queen_positions)):
            for j in range(i + 1, len(queen_positions)):
                if self.can_attack(queen_positions[i], queen_positions[j]):
                    conflicts += 1
        return conflicts
    
    def get_queen_positions(self):
        """Return list of (row, col) positions of all queens"""
        return [(row, col) for row in range(self.n) 
                for col in range(self.n) if self.board[row][col] == 1]
    
    def can_attack(self, pos1, pos2):
        """Check if two queens at given positions can attack each other"""
        row1, col1 = pos1
        row2, col2 = pos2
        return (col1 == col2 or  # Same column
                abs(row1 - row2) == abs(col1 - col2))  # Same diagonal
    
    def make_random_move(self):
        """Make a random move by moving a random queen to a new position in its row"""
        row = random.randint(0, self.n-1)
        old_col = np.where(self.board[row] == 1)[0][0]
        
        # Store the current state
        old_board = self.board.copy()
        old_conflicts = self.count_conflicts()
        
        # Try all possible positions in the row
        possible_cols = list(range(self.n))
        possible_cols.remove(old_col)
        new_col = random.choice(possible_cols)
        
        # Make the move
        self.board[row][old_col] = 0
        self.board[row][new_col] = 1
        new_conflicts = self.count_conflicts()
        
        return old_board, old_conflicts, self.board.copy(), new_conflicts

    def get_all_neighbors(self):
        """Get all possible neighbor states by moving each queen"""
        neighbors = []
        conflicts = []
        
        for row in range(self.n):
            old_col = np.where(self.board[row] == 1)[0][0]
            for new_col in range(self.n):
                if new_col != old_col:
                    new_board = self.board.copy()
                    new_board[row][old_col] = 0
                    new_board[row][new_col] = 1
                    self.board = new_board
                    neighbors.append(new_board.copy())
                    conflicts.append(self.count_conflicts())
            # Restore original position
            self.board[row][old_col] = 1
            self.board[row, :old_col] = 0
            self.board[row, old_col+1:] = 0
            
        return neighbors, conflicts

    def simulated_annealing(self, initial_temp=100.0, cooling_rate=0.99, min_temp=0.0001, max_iterations=100000):
        """Enhanced simulated annealing with aggressive restarts"""
        start_time = time()
        best_solution = None
        best_conflicts = float('inf')
        restart_count = 0
        max_restarts = 20  # Increased max restarts
        plateau_count = 0
        max_plateau = 1000  # Maximum iterations without improvement
        
        while (restart_count < max_restarts and best_conflicts > 0):
            self.initialize_random_state()
            current_board = self.board.copy()
            current_conflicts = self.current_conflicts
            
            temperature = initial_temp
            iteration = 0
            last_conflicts = current_conflicts
            plateau_count = 0
            
            self.temperature_history = [temperature]
            self.energy_history = [current_conflicts]
            
            while current_conflicts > 0 and iteration < max_iterations:
                neighbors, neighbor_conflicts = self.get_all_neighbors()
                
                # Try all possible moves at current temperature
                improvement_found = False
                for new_board, new_conflicts in zip(neighbors, neighbor_conflicts):
                    delta_e = new_conflicts - current_conflicts
                    
                    # More aggressive acceptance probability
                    if delta_e < 0 or (temperature > 0 and random.random() < math.exp(-delta_e / (temperature + 0.01))):
                        current_board = new_board.copy()
                        current_conflicts = new_conflicts
                        self.board = new_board.copy()
                        improvement_found = True
                        
                        if current_conflicts < best_conflicts:
                            best_solution = current_board.copy()
                            best_conflicts = current_conflicts
                            plateau_count = 0
                        
                        if current_conflicts == 0:
                            break
                
                if not improvement_found:
                    plateau_count += 1
                
                # Restart if stuck on plateau
                if plateau_count >= max_plateau:
                    temperature = initial_temp  # Reset temperature
                    plateau_count = 0
                    self.initialize_random_state()
                    current_board = self.board.copy()
                    current_conflicts = self.current_conflicts
                
                temperature *= cooling_rate
                if temperature < min_temp:
                    temperature = initial_temp * 0.5  # Reset with lower temperature
                
                iteration += 1
                self.temperature_history.append(temperature)
                self.energy_history.append(current_conflicts)
                
                if current_conflicts == 0:
                    break
            
            restart_count += 1
        
        self.board = best_solution if best_solution is not None else self.board
        return {
            "solution": self.board,
            "conflicts": best_conflicts,
            "iterations": iteration,
            "time": time() - start_time,
            "solved": best_conflicts == 0,
            "restarts": restart_count
        }
    
    def hill_climbing(self, max_iterations=100000):
        """Enhanced hill climbing with aggressive sideways moves"""
        start_time = time()
        best_solution = None
        best_conflicts = float('inf')
        restart_count = 0
        max_restarts = 30  # Increased max restarts
        max_sideways = self.n * 4  # Increased sideways moves
        plateau_count = 0
        max_plateau = 1000
        
        while restart_count < max_restarts and best_conflicts > 0:
            self.initialize_random_state()
            current_board = self.board.copy()
            current_conflicts = self.current_conflicts
            
            iteration = 0
            sideways_moves = 0
            plateau_count = 0
            
            self.energy_history = [current_conflicts]
            
            while iteration < max_iterations and current_conflicts > 0:
                neighbors, neighbor_conflicts = self.get_all_neighbors()
                min_conflict = min(neighbor_conflicts)
                
                if min_conflict < current_conflicts:
                    best_idx = neighbor_conflicts.index(min_conflict)
                    current_board = neighbors[best_idx].copy()
                    current_conflicts = min_conflict
                    self.board = current_board.copy()
                    sideways_moves = 0
                    plateau_count = 0
                    
                    if current_conflicts < best_conflicts:
                        best_solution = current_board.copy()
                        best_conflicts = current_conflicts
                
                elif min_conflict == current_conflicts and sideways_moves < max_sideways:
                    equal_indices = [i for i, c in enumerate(neighbor_conflicts) if c == current_conflicts]
                    best_idx = random.choice(equal_indices)
                    current_board = neighbors[best_idx].copy()
                    sideways_moves += 1
                    plateau_count += 1
                else:
                    plateau_count += 1
                
                # Restart if stuck on plateau
                if plateau_count >= max_plateau:
                    break  # Force restart
                
                iteration += 1
                self.energy_history.append(current_conflicts)
                
                if current_conflicts == 0:
                    break
            
            restart_count += 1
        
        self.board = best_solution if best_solution is not None else self.board
        return {
            "solution": self.board,
            "conflicts": best_conflicts,
            "iterations": iteration,
            "time": time() - start_time,
            "solved": best_conflicts == 0,
            "restarts": restart_count
        }
