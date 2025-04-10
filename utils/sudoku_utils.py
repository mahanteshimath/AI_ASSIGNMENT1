import numpy as np
from typing import List, Tuple, Set, Optional, Dict
import random
import time

class SudokuCSP:
    def __init__(self, grid_string: str):
        """Initialize Sudoku CSP with a string representation of the grid"""
        # Parse the string into a grid
        self.grid = {}
        rows = 'ABCDEFGHI'
        cols = '123456789'
        chars = [c for c in grid_string if c in '123456789.']
        
        # Create all squares
        self.squares = [r + c for r in rows for c in cols]
        
        # Create units and peers
        self.row_units = [[r + c for c in cols] for r in rows]
        self.col_units = [[r + c for r in rows] for c in cols]
        self.box_units = [[rows[i:i+3][r] + cols[j:j+3][c] 
                          for r in range(3) for c in range(3)]
                         for i in range(0, 9, 3) for j in range(0, 9, 3)]
        
        self.all_units = self.row_units + self.col_units + self.box_units
        self.units = {s: [u for u in self.all_units if s in u] for s in self.squares}
        self.peers = {s: set().union(*[u for u in self.units[s]]) - {s} for s in self.squares}
        
        # Parse grid
        for i, s in enumerate(self.squares):
            self.grid[s] = int(chars[i]) if chars[i] != '.' else 0
        
        # Initialize domains
        self.domains = self._init_domains()

    def _init_domains(self) -> Dict[str, Set[int]]:
        """Initialize domains for all variables"""
        domains = {}
        for s in self.squares:
            if self.grid[s] != 0:
                domains[s] = {self.grid[s]}
            else:
                domains[s] = set(range(1, 10))
        return domains

    def display(self, grid=None):
        """Display the grid"""
        if grid is None:
            grid = self.grid
        width = 2
        line = '+'.join(['-' * (width * 3)] * 3)
        for r in 'ABCDEFGHI':
            print(''.join(f"{grid[r+c]:2}" + ('|' if c in '36' else '') 
                        for c in '123456789'))
            if r in 'CF': 
                print(line)
        print()

def backtracking_search(csp: SudokuCSP) -> Optional[Dict[str, int]]:
    """Basic backtracking search"""
    return _backtrack({}, csp)

def backtracking_with_inference(csp: SudokuCSP, inference: str = 'forward_checking') -> Optional[Dict[str, int]]:
    """Backtracking search with inference"""
    if inference == 'forward_checking':
        return _backtrack_fc({}, csp)
    elif inference == 'ac3':
        return _backtrack_ac3({}, csp)
    return None

def evaluate_heuristics(num_puzzles: int = 2, runs_per_puzzle: int = 3) -> List[Dict]:
    """Evaluate different heuristic combinations"""
    results = []
    puzzle = "..3.2.6..9..3.5..1..18.64....81.29..7.......8..67.82....26.95..8..2.3..9..5.1.3.."
    
    heuristics = [
        ('Basic', None),
        ('MRV', 'mrv'),
        ('MRV+Degree', 'degree'),
        ('MRV+Degree+LCV', 'lcv')
    ]
    
    for name, heuristic in heuristics:
        times = []
        for _ in range(runs_per_puzzle):
            csp = SudokuCSP(puzzle)
            start = time.time()
            if heuristic:
                backtracking_with_inference(csp, heuristic)
            else:
                backtracking_search(csp)
            times.append(time.time() - start)
        
        results.append({
            'Algorithm': name,
            'Avg Time': sum(times) / len(times),
            'Min Time': min(times),
            'Max Time': max(times)
        })
    
    return results

# Helper functions
def _backtrack(assignment: Dict[str, int], csp: SudokuCSP) -> Optional[Dict[str, int]]:
    """Helper function for basic backtracking"""
    if len(assignment) == len(csp.squares):
        return assignment
    var = _select_unassigned_variable(assignment, csp)
    for value in _order_domain_values(var, assignment, csp):
        if _is_consistent(var, value, assignment, csp):
            assignment[var] = value
            result = _backtrack(assignment, csp)
            if result:
                return result
            assignment.pop(var)
    return None

def _backtrack_fc(assignment: Dict[str, int], csp: SudokuCSP) -> Optional[Dict[str, int]]:
    """Helper function for backtracking with forward checking"""
    # ... implementation similar to _backtrack but with forward checking ...
    pass

def _backtrack_ac3(assignment: Dict[str, int], csp: SudokuCSP) -> Optional[Dict[str, int]]:
    """Helper function for backtracking with AC3"""
    # ... implementation similar to _backtrack but with AC3 ...
    pass

def _select_unassigned_variable(assignment: Dict[str, int], csp: SudokuCSP) -> str:
    """Select an unassigned variable - MRV heuristic"""
    unassigned = [var for var in csp.squares if var not in assignment]
    return min(unassigned, key=lambda var: len(csp.domains[var]))

def _order_domain_values(var: str, assignment: Dict[str, int], csp: SudokuCSP) -> List[int]:
    """Order domain values - LCV heuristic"""
    return sorted(csp.domains[var])

def _is_consistent(var: str, value: int, assignment: Dict[str, int], csp: SudokuCSP) -> bool:
    """Check if assignment is consistent"""
    for peer in csp.peers[var]:
        if peer in assignment and assignment[peer] == value:
            return False
    return True
