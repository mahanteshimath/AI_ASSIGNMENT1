import time
import random
from typing import Dict, Set, List, Tuple, Optional
import numpy as np

class SudokuCSP:
    def __init__(self, grid_string: str):
        self.squares = [r + c for r in 'ABCDEFGHI' for c in '123456789']
        self.digits = '123456789'
        self.rows = 'ABCDEFGHI'
        self.cols = '123456789'
        
        # Parse grid
        self.grid = self._parse_grid(grid_string)
        self.domains = self._get_domains()
        
        # Create unit lists and peers
        self.unitlist = (
            [self._cross(self.rows, c) for c in self.cols] +           # rows
            [self._cross(r, self.cols) for r in self.rows] +           # columns
            [self._cross(rs, cs) for rs in ('ABC','DEF','GHI') 
             for cs in ('123','456','789')]                            # boxes
        )
        self.units = {s: [u for u in self.unitlist if s in u] for s in self.squares}
        self.peers = {s: set(sum(self.units[s],[]))-{s} for s in self.squares}

    def _cross(self, A: str, B: str) -> List[str]:
        return [a + b for a in A for b in B]

    def _parse_grid(self, grid_string: str) -> Dict[str, int]:
        """Convert grid string into {square: digit} dict with 0 for empties."""
        chars = [c for c in grid_string if c in '0123456789.']
        assert len(chars) == 81, f"Grid must be 81 chars, got {len(chars)}"
        return {s: int(d) if d != '.' else 0 
                for s, d in zip(self.squares, chars)}

    def _get_domains(self) -> Dict[str, Set[str]]:
        """Get initial domains for all squares."""
        domains = {}
        for s in self.squares:
            if self.grid[s] == 0:
                domains[s] = set(self.digits)
            else:
                domains[s] = {str(self.grid[s])}
        return domains

def backtracking_search(csp: SudokuCSP) -> Optional[Tuple[Dict[str, int], int]]:
    """Basic backtracking search."""
    def backtrack(assignment: Dict[str, int], iterations: int = 0) -> Optional[Tuple[Dict[str, int], int]]:
        if len(assignment) == len(csp.squares):
            return assignment, iterations
            
        var = select_unassigned_variable(assignment, csp)
        for value in csp.domains[var]:
            if is_consistent(var, int(value), assignment, csp):
                assignment[var] = int(value)
                result = backtrack(assignment, iterations + 1)
                if result:
                    return result
                del assignment[var]
        return None
        
    return backtrack({s: csp.grid[s] for s in csp.squares if csp.grid[s] != 0})

def backtracking_with_inference(csp: SudokuCSP, inference: str = 'forward_checking') -> Optional[Tuple[Dict[str, int], int]]:
    """Backtracking with inference (Forward Checking or AC3)."""
    def forward_checking(var: str, value: int, domains: Dict[str, Set[str]], assignment: Dict[str, int]) -> Optional[Dict[str, Set[str]]]:
        domains = domains.copy()
        domains[var] = {str(value)}
        
        for peer in csp.peers[var]:
            if peer not in assignment:
                domains[peer] = domains[peer] - {str(value)}
                if not domains[peer]:
                    return None
        return domains

    def backtrack(assignment: Dict[str, int], domains: Dict[str, Set[str]], iterations: int = 0) -> Optional[Tuple[Dict[str, int], int]]:
        if len(assignment) == len(csp.squares):
            return assignment, iterations
        
        var = select_unassigned_variable(assignment, csp)
        # Sort values by least constraining value
        values = sorted(domains[var], key=lambda x: sum(1 for p in csp.peers[var] if x in domains[p]))
        
        for value in values:
            if is_consistent(var, int(value), assignment, csp):
                assignment[var] = int(value)
                
                # Make a copy of domains for inference
                curr_domains = {k: set(v) for k, v in domains.items()}
                
                if inference == 'forward_checking':
                    new_domains = forward_checking(var, int(value), curr_domains, assignment)
                else:  # AC3
                    new_domains = ac3(csp, var, int(value), curr_domains)
                
                if new_domains is not None:
                    result = backtrack(assignment, new_domains, iterations + 1)
                    if result:
                        return result
                
                del assignment[var]
        
        return None
    
    return backtrack({s: csp.grid[s] for s in csp.squares if csp.grid[s] != 0}, csp.domains.copy())

def select_unassigned_variable(assignment: Dict[str, int], csp: SudokuCSP) -> str:
    """Select an unassigned variable - MRV heuristic"""
    unassigned = [var for var in csp.squares if var not in assignment]
    return min(unassigned, key=lambda var: len(csp.domains[var]))

def is_consistent(var: str, value: int, assignment: Dict[str, int], csp: SudokuCSP) -> bool:
    """Check if assignment is consistent."""
    for peer in csp.peers[var]:
        if peer in assignment and assignment[peer] == value:
            return False
    return True

def ac3(csp: SudokuCSP, var: str, value: int, domains: Dict[str, Set[str]]) -> Optional[Dict[str, Set[str]]]:
    """AC3 algorithm for constraint propagation."""
    # Create a deep copy of domains to avoid modifying original
    domains = {k: set(v) for k, v in domains.items()}
    domains[var] = {str(value)}
    
    # Initialize queue with all arcs between var and its peers
    queue = []
    for peer in csp.peers[var]:
        queue.append((peer, var))  # Add arc from peer to var
        # Also add arcs between peers to maintain consistency
        for other_peer in csp.peers[peer]:
            if other_peer != var:
                queue.append((peer, other_peer))
    
    while queue:
        (x1, x2) = queue.pop(0)
        if revise(csp, x1, x2, domains):
            if not domains[x1]:
                return None  # No solution exists
            # Add all neighbors of x1 except x2 to queue
            for peer in csp.peers[x1] - {x2}:
                queue.append((peer, x1))
    
    return domains

def revise(csp: SudokuCSP, x1: str, x2: str, domains: Dict[str, Set[str]]) -> bool:
    """Revise domains - return True if domain of x1 was changed."""
    revised = False
    
    # Make copy of domain to avoid modifying during iteration
    x1_domain = set(domains[x1])
    
    for d1 in x1_domain:
        # Check if there's any value in x2's domain that allows d1
        valid = False
        for d2 in domains[x2]:
            if d1 != d2:  # Different values satisfy the constraint
                valid = True
                break
        
        if not valid:
            domains[x1].remove(d1)
            revised = True
    
    return revised

def evaluate_heuristics(puzzles: List[str], runs_per_puzzle: int = 1) -> List[dict]:
    """Evaluate different heuristic combinations."""
    results = []
    
    for puzzle in puzzles:
        # Test different heuristic combinations
        algorithms = [
            ("Basic Backtracking", lambda: backtracking_search(SudokuCSP(puzzle))),
            ("MRV Only", lambda: backtracking_with_inference(SudokuCSP(puzzle), 'mrv_only')),
            ("MRV + Degree", lambda: backtracking_with_inference(SudokuCSP(puzzle), 'mrv_degree')),
            ("MRV + Degree + LCV", lambda: backtracking_with_inference(SudokuCSP(puzzle), 'all_heuristics'))
        ]
        
        for name, algo in algorithms:
            times = []
            iterations = []
            successes = 0
            
            for _ in range(runs_per_puzzle):
                start_time = time.time()
                result = algo()
                end_time = time.time()
                
                if result:
                    solution, iters = result
                    times.append(end_time - start_time)
                    iterations.append(iters)
                    successes += 1
            
            if times:
                results.append({
                    'Algorithm': name,
                    'Avg Time': sum(times) / len(times),
                    'Avg Iterations': sum(iterations) / len(iterations),
                    'Success Rate': successes / runs_per_puzzle,
                    'Std Dev Time': np.std(times),
                    'Peak Memory': max(iterations) * 81  # Rough estimate of peak memory usage
                })
            
    return results
