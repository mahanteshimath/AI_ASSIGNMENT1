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
    
    # ... existing initialization and helper methods ...
    
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
            new_board, new_conflicts = self.make_random_move()
            
            delta_e = new_conflicts - current_conflicts
            
            if delta_e < 0 or random.random() < math.exp(-delta_e / temperature):
                current_board = new_board.copy()
                current_conflicts = new_conflicts
                
                if current_conflicts < best_conflicts:
                    best_board = current_board.copy()
                    best_conflicts = current_conflicts
            
            temperature *= cooling_rate
            iteration += 1
            
            self.temperature_history.append(temperature)
            self.energy_history.append(current_conflicts)
            
            if current_conflicts == 0:
                break
        
        return {
            "solution": best_board,
            "conflicts": best_conflicts,
            "iterations": iteration,
            "time": time() - start_time,
            "solved": best_conflicts == 0
        }
    
    def hill_climbing(self, max_iterations=10000):
        """Hill climbing implementation (SA with T=0)"""
        self.initialize_random_state()
        
        current_board = self.board.copy()
        current_conflicts = self.current_conflicts
        
        best_board = current_board.copy()
        best_conflicts = current_conflicts
        
        iteration = 0
        self.energy_history = [current_conflicts]
        
        start_time = time()
        
        while current_conflicts > 0 and iteration < max_iterations:
            new_board, new_conflicts = self.make_random_move()
            
            if new_conflicts <= current_conflicts:
                current_board = new_board.copy()
                current_conflicts = new_conflicts
                
                if current_conflicts < best_conflicts:
                    best_board = current_board.copy()
                    best_conflicts = current_conflicts
            
            iteration += 1
            self.energy_history.append(current_conflicts)
            
            if current_conflicts == 0:
                break
        
        return {
            "solution": best_board,
            "conflicts": best_conflicts,
            "iterations": iteration,
            "time": time() - start_time,
            "solved": best_conflicts == 0
        }
