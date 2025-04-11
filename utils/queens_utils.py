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

    def simulated_annealing(self, initial_temp=10.0, cooling_rate=0.95, min_temp=0.01, max_iterations=10000):
        """Solve N-Queens using simulated annealing with improved visualization"""
        self.initialize_random_state()
        
        current_board = self.board.copy()
        current_conflicts = self.current_conflicts
        
        best_board = current_board.copy()
        best_conflicts = current_conflicts
        
        temperature = initial_temp
        iteration = 0
        
        self.temperature_history = [temperature]
        self.energy_history = [current_conflicts]
        
        start_time = time()
        
        while temperature > min_temp and current_conflicts > 0 and iteration < max_iterations:
            old_board, old_conflicts, new_board, new_conflicts = self.make_random_move()
            
            delta_e = new_conflicts - current_conflicts
            
            # Improved acceptance probability calculation
            if delta_e < 0 or (temperature > 0 and random.random() < math.exp(-delta_e / temperature)):
                current_board = new_board.copy()
                current_conflicts = new_conflicts
                
                if current_conflicts < best_conflicts:
                    best_board = current_board.copy()
                    best_conflicts = current_conflicts
            else:
                # Restore old state if move rejected
                self.board = old_board.copy()
                current_conflicts = old_conflicts
            
            temperature *= cooling_rate
            iteration += 1
            
            self.temperature_history.append(temperature)
            self.energy_history.append(current_conflicts)
            
            if current_conflicts == 0:
                break
        
        self.board = best_board
        return {
            "solution": best_board,
            "conflicts": best_conflicts,
            "iterations": iteration,
            "time": time() - start_time,
            "solved": best_conflicts == 0
        }
    
    def hill_climbing(self, max_iterations=10000):
        """Hill climbing implementation"""
        self.initialize_random_state()
        
        current_board = self.board.copy()
        current_conflicts = self.current_conflicts
        
        best_board = current_board.copy()
        best_conflicts = current_conflicts
        
        iteration = 0
        self.energy_history = [current_conflicts]
        
        start_time = time()
        no_improvement_count = 0
        
        while current_conflicts > 0 and iteration < max_iterations and no_improvement_count < self.n * 2:
            old_board, old_conflicts, new_board, new_conflicts = self.make_random_move()
            
            if new_conflicts < current_conflicts:  # Only accept strictly better moves
                current_board = new_board.copy()
                current_conflicts = new_conflicts
                no_improvement_count = 0
                
                if current_conflicts < best_conflicts:
                    best_board = current_board.copy()
                    best_conflicts = current_conflicts
            else:
                # Restore old state
                self.board = old_board.copy()
                no_improvement_count += 1
            
            iteration += 1
            self.energy_history.append(current_conflicts)
            
            if current_conflicts == 0:
                break
        
        self.board = best_board
        return {
            "solution": best_board,
            "conflicts": best_conflicts,
            "iterations": iteration,
            "time": time() - start_time,
            "solved": best_conflicts == 0
        }
