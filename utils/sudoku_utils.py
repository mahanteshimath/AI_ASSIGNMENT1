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

def backtracking_search(csp: SudokuCSP) -> Optional[Tuple[Dict[str, int], int]]:
    """Basic backtracking search"""
    iterations = 0
    def backtrack(assignment: Dict[str, int]) -> Optional[Dict[str, int]]:
        nonlocal iterations
        iterations += 1
        if len(assignment) == len(csp.squares):
            return assignment
        var = _select_unassigned_variable(assignment, csp)
        for value in _order_domain_values(var, assignment, csp):
            if _is_consistent(var, value, assignment, csp):
                assignment[var] = value
                result = backtrack(assignment)
                if result:
                    return result
                assignment.pop(var)
        return None
    
    result = backtrack({})
    if result:
        return (result, iterations)  # Return tuple of solution and iterations
    return None  # Return None if no solution found

def backtracking_with_inference(csp: SudokuCSP, inference: str = 'forward_checking') -> Optional[Tuple[Dict[str, int], int]]:
    """Backtracking search with inference"""
    iterations = 0
    def backtrack(assignment: Dict[str, int]) -> Optional[Dict[str, int]]:
        nonlocal iterations
        iterations += 1
        if len(assignment) == len(csp.squares):
            return assignment
        
        # Apply appropriate variable selection heuristic
        if inference == 'mrv':
            var = _select_mrv(assignment, csp)
        elif inference == 'degree':
            var = _select_mrv_degree(assignment, csp)
        elif inference == 'lcv':
            var = _select_mrv_degree(assignment, csp)
            values = _order_domain_values_lcv(var, assignment, csp)
        else:
            var = _select_unassigned_variable(assignment, csp)
            values = _order_domain_values(var, assignment, csp)
        
        # Use LCV for value ordering if specified
        values = _order_domain_values_lcv(var, assignment, csp) if inference == 'lcv' else _order_domain_values(var, assignment, csp)
        
        for value in values:
            if _is_consistent(var, value, assignment, csp):
                assignment[var] = value
                result = backtrack(assignment)
                if result:
                    return result
                assignment.pop(var)
        return None
    
    result = backtrack({})
    if result:
        return (result, iterations)
    return None

def _select_mrv(assignment: Dict[str, int], csp: SudokuCSP) -> str:
    """Select unassigned variable with minimum remaining values"""
    unassigned = [var for var in csp.squares if var not in assignment]
    return min(unassigned, key=lambda var: len(csp.domains[var]))

def _select_mrv_degree(assignment: Dict[str, int], csp: SudokuCSP) -> str:
    """Select variable using MRV with degree heuristic as tie-breaker"""
    unassigned = [var for var in csp.squares if var not in assignment]
    # First apply MRV
    min_remaining = min(len(csp.domains[var]) for var in unassigned)
    min_vars = [var for var in unassigned if len(csp.domains[var]) == min_remaining]
    
    if len(min_vars) == 1:
        return min_vars[0]
    
    # Use degree heuristic as tie-breaker
    return max(min_vars, key=lambda var: sum(1 for peer in csp.peers[var] if peer not in assignment))

def _order_domain_values_lcv(var: str, assignment: Dict[str, int], csp: SudokuCSP) -> List[int]:
    """Order domain values using Least Constraining Value heuristic"""
    def count_conflicts(value):
        count = 0
        for peer in csp.peers[var]:
            if peer not in assignment and value in csp.domains[peer]:
                count += 1
        return count
    
    return sorted(csp.domains[var], key=count_conflicts)

def evaluate_heuristics(puzzles: List[str], runs_per_puzzle: int = 3) -> List[Dict]:
    """Evaluate different heuristic combinations"""
    results = []
    heuristics = [
        ('Basic', None),
        ('MRV', 'mrv'),
        ('MRV+Degree', 'degree'),
        ('MRV+Degree+LCV', 'lcv')
    ]
    
    for name, heuristic in heuristics:
        total_times = []
        total_iterations = []
        total_successes = 0
        total_runs = len(puzzles) * runs_per_puzzle
        
        for puzzle in puzzles:
            for _ in range(runs_per_puzzle):
                csp = SudokuCSP(puzzle)
                start = time.time()
                if heuristic:
                    result = backtracking_with_inference(csp, inference=heuristic)
                else:
                    result = backtracking_search(csp)
                total_times.append(time.time() - start)
                
                if result:
                    total_successes += 1
                    total_iterations.append(result[1])
                else:
                    total_iterations.append(0)
        
        success_rate = (total_successes / total_runs) * 100
        avg_iterations = sum(total_iterations) / len(total_iterations) if total_iterations else 0
        
        results.append({
            'Algorithm': name,
            'Avg Time': sum(total_times) / len(total_times),
            'Min Time': min(total_times),
            'Max Time': max(total_times),
            'Avg Iterations': avg_iterations,
            'Success Rate': success_rate
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
    """Backtracking with forward checking"""
    if len(assignment) == len(csp.squares):
        return assignment
    
    var = _select_unassigned_variable(assignment, csp)
    for value in _order_domain_values(var, assignment, csp):
        if _is_consistent(var, value, assignment, csp):
            # Save current domains
            saved_domains = {k: v.copy() for k, v in csp.domains.items()}
            
            # Make assignment and update domains
            assignment[var] = value
            csp.domains[var] = {value}
            
            # Forward check
            failure = False
            for peer in csp.peers[var]:
                if peer not in assignment and value in csp.domains[peer]:
                    csp.domains[peer] = csp.domains[peer] - {value}
                    if not csp.domains[peer]:  # Domain wipeout
                        failure = True
                        break
            
            if not failure:
                result = _backtrack_fc(assignment, csp)
                if result:
                    return result
            
            # Restore domains and remove assignment
            csp.domains = saved_domains
            assignment.pop(var)
            
    return None

def _backtrack_ac3(assignment: Dict[str, int], csp: SudokuCSP) -> Optional[Dict[str, int]]:
    """Backtracking with AC3"""
    if len(assignment) == len(csp.squares):
        return assignment
    
    var = _select_unassigned_variable(assignment, csp)
    for value in _order_domain_values(var, assignment, csp):
        if _is_consistent(var, value, assignment, csp):
            # Save current domains
            saved_domains = {k: v.copy() for k, v in csp.domains.items()}
            
            # Make assignment and update domains
            assignment[var] = value
            csp.domains[var] = {value}
            
            # Run AC3
            queue = [(peer, var) for peer in csp.peers[var] if peer not in assignment]
            failure = not _ac3(queue, csp)
            
            if not failure:
                result = _backtrack_ac3(assignment, csp)
                if result:
                    return result
            
            # Restore domains and remove assignment
            csp.domains = saved_domains
            assignment.pop(var)
    
    return None

def _ac3(queue: List[Tuple[str, str]], csp: SudokuCSP) -> bool:
    """AC3 algorithm for constraint propagation"""
    while queue:
        (xi, xj) = queue.pop(0)
        if _revise(xi, xj, csp):
            if not csp.domains[xi]:
                return False
            # Add neighbors for further constraint propagation
            for xk in csp.peers[xi]:
                if xk != xj:
                    queue.append((xk, xi))
    return True

def _revise(xi: str, xj: str, csp: SudokuCSP) -> bool:
    """Revise the domain of xi with respect to xj"""
    revised = False
    for x in list(csp.domains[xi]):  # Make a copy since we'll modify domain
        # If no value in xj's domain satisfies the constraint with x
        if not any(y != x for y in csp.domains[xj]):
            csp.domains[xi].remove(x)
            revised = True
    return revised

def _select_unassigned_variable(assignment: Dict[str, int], csp: SudokuCSP) -> str:
    """Select an unassigned variable - MRV heuristic"""    unassigned = [var for var in csp.squares if var not in assignment]
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
