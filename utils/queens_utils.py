import random
import math
import numpy as np
import time

class NQueensSolver:
    def __init__(self, n=8):
        self.n = n
        self.temperature_history = []
        self.energy_history = []
        self.initial_state = None
        self.final_state = None
        
        # Default parameters
        self.INIT_TEMP = 1000
        self.COOLING_RATE = 0.99
        self.MIN_TEMP = 0.1
        self.MAX_ITER = 10000
        self.RECORD_HISTORY = True

    def _random_state(self):
        state = list(range(self.n))
        random.shuffle(state)
        return state

    def _count_conflicts(self, state):
        conflicts = 0
        for i in range(self.n):
            for j in range(i + 1, self.n):
                if abs(state[i] - state[j]) == abs(i - j):
                    conflicts += 1
        return conflicts

    def _random_neighbor(self, state):
        neighbor = state.copy()
        i, j = random.sample(range(self.n), 2)
        neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
        return neighbor

    def _state_to_board(self, state):
        board = np.zeros((self.n, self.n))
        for col, row in enumerate(state):
            board[row][col] = 1
        return board

    def simulated_annealing(self, initial_temp=None, cooling_rate=None, min_temp=None, max_iter=None):
        start_time = time.time()
        
        # Use default values if not provided
        initial_temp = initial_temp or self.INIT_TEMP
        cooling_rate = cooling_rate or self.COOLING_RATE
        min_temp = min_temp or self.MIN_TEMP
        max_iter = max_iter or self.MAX_ITER
        
        current_state = self._random_state()
        self.initial_state = self._state_to_board(current_state)
        current_cost = self._count_conflicts(current_state)
        
        T = initial_temp
        iteration = 0
        self.temperature_history = [T]
        self.energy_history = [current_cost]
        
        while current_cost > 0 and iteration < max_iter:
            neighbor = self._random_neighbor(current_state)
            neighbor_cost = self._count_conflicts(neighbor)
            delta = neighbor_cost - current_cost
            
            if delta <= 0 or random.random() < math.exp(-delta / T):
                current_state = neighbor
                current_cost = neighbor_cost
            
            T *= cooling_rate
            iteration += 1
            
            self.temperature_history.append(T)
            self.energy_history.append(current_cost)
            
            if T < min_temp:
                break
        
        self.final_state = self._state_to_board(current_state)
        return {
            'solution': self.final_state,
            'initial_board': self.initial_state,
            'conflicts': current_cost,
            'iterations': iteration,
            'time': time.time() - start_time
        }

    def hill_climbing(self, max_iter=None):
        start_time = time.time()
        max_iter = max_iter or self.MAX_ITER
        
        current_state = self._random_state()
        self.initial_state = self._state_to_board(current_state)
        current_cost = self._count_conflicts(current_state)
        
        iteration = 0
        self.temperature_history = [0] * max_iter  # Flat temperature
        self.energy_history = [current_cost]
        
        while current_cost > 0 and iteration < max_iter:
            neighbor = self._random_neighbor(current_state)
            neighbor_cost = self._count_conflicts(neighbor)
            
            if neighbor_cost < current_cost:
                current_state = neighbor
                current_cost = neighbor_cost
                self.energy_history.append(current_cost)
            
            iteration += 1
        
        self.final_state = self._state_to_board(current_state)
        return {
            'solution': self.final_state,
            'initial_board': self.initial_state,
            'conflicts': current_cost,
            'iterations': iteration,
            'time': time.time() - start_time
        }
