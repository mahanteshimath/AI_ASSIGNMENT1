import numpy as np
from typing import List, Tuple, Set, Optional
import random

class SudokuSolver:
    def __init__(self, grid: np.ndarray):
        self.grid = grid
        self.domains = self._initialize_domains()
        
    def _initialize_domains(self) -> List[List[Set[int]]]:
        domains = [[set(range(1, 10)) for _ in range(9)] for _ in range(9)]
        for i in range(9):
            for j in range(9):
                if self.grid[i][j] != 0:
                    domains[i][j] = {self.grid[i][j]}
        return domains

    def get_mrv_cell(self) -> Tuple[int, int]:
        min_remaining = float('inf')
        mrv_cell = None
        
        for i in range(9):
            for j in range(9):
                if self.grid[i][j] == 0:
                    remaining = len(self.domains[i][j])
                    if remaining < min_remaining:
                        min_remaining = remaining
                        mrv_cell = (i, j)
        return mrv_cell

    def get_degree_cell(self) -> Tuple[int, int]:
        max_degree = -1
        degree_cell = None
        
        for i in range(9):
            for j in range(9):
                if self.grid[i][j] == 0:
                    degree = self._count_constraints(i, j)
                    if degree > max_degree:
                        max_degree = degree
                        degree_cell = (i, j)
        return degree_cell

    def _count_constraints(self, row: int, col: int) -> int:
        count = 0
        for i in range(9):
            if i != col and self.grid[row][i] == 0:
                count += 1
            if i != row and self.grid[i][col] == 0:
                count += 1
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if i != row and j != col and self.grid[i][j] == 0:
                    count += 1
        return count

def solve_with_backtracking(grid: np.ndarray, heuristic: str) -> np.ndarray:
    solver = SudokuSolver(grid.copy())
    return _backtrack(solver, heuristic)

def solve_with_forward_checking(grid: np.ndarray, heuristic: str) -> np.ndarray:
    solver = SudokuSolver(grid.copy())
    return _forward_check(solver, heuristic)

def solve_with_arc_consistency(grid: np.ndarray, heuristic: str) -> np.ndarray:
    solver = SudokuSolver(grid.copy())
    return _arc_consistency(solver, heuristic)

def _backtrack(solver: SudokuSolver, heuristic: str) -> Optional[np.ndarray]:
    if np.all(solver.grid != 0):
        return solver.grid
    
    row, col = _get_next_cell(solver, heuristic)
    if row is None:
        return None
        
    for value in _get_ordered_values(solver, row, col, heuristic):
        if _is_valid(solver.grid, row, col, value):
            solver.grid[row][col] = value
            result = _backtrack(solver, heuristic)
            if result is not None:
                return result
            solver.grid[row][col] = 0
    
    return None

def _forward_check(solver: SudokuSolver, heuristic: str) -> Optional[np.ndarray]:
    if np.all(solver.grid != 0):
        return solver.grid
    
    row, col = _get_next_cell(solver, heuristic)
    if row is None:
        return None
        
    original_domains = [d.copy() for d in solver.domains]
    
    for value in _get_ordered_values(solver, row, col, heuristic):
        if _is_valid(solver.grid, row, col, value):
            solver.grid[row][col] = value
            if _update_domains(solver, row, col):
                result = _forward_check(solver, heuristic)
                if result is not None:
                    return result
            solver.grid[row][col] = 0
            solver.domains = [d.copy() for d in original_domains]
    
    return None

def _arc_consistency(solver: SudokuSolver, heuristic: str) -> Optional[np.ndarray]:
    if not _ac3(solver):
        return None
    return _forward_check(solver, heuristic)

def _ac3(solver: SudokuSolver) -> bool:
    queue = _get_all_arcs()
    while queue:
        (xi, xj) = queue.pop(0)
        if _revise(solver, xi, xj):
            if len(solver.domains[xi[0]][xi[1]]) == 0:
                return False
            for xk in _get_neighbors(xi):
                queue.append((xk, xi))
    return True

def is_valid_sudoku(grid: np.ndarray) -> bool:
    def has_duplicates(arr):
        seen = set()
        for x in arr:
            if x != 0:
                if x in seen:
                    return True
                seen.add(x)
        return False

    # Check rows and columns
    for i in range(9):
        if has_duplicates(grid[i, :]) or has_duplicates(grid[:, i]):
            return False

    # Check 3x3 boxes
    for box_row in range(0, 9, 3):
        for box_col in range(0, 9, 3):
            box = grid[box_row:box_row+3, box_col:box_col+3].flatten()
            if has_duplicates(box):
                return False

    return True

# Helper functions
def _get_next_cell(solver: SudokuSolver, heuristic: str) -> Tuple[Optional[int], Optional[int]]:
    if heuristic == "MRV":
        return solver.get_mrv_cell()
    elif heuristic == "Degree":
        return solver.get_degree_cell()
    else:
        for i in range(9):
            for j in range(9):
                if solver.grid[i][j] == 0:
                    return (i, j)
    return (None, None)

def _get_ordered_values(solver: SudokuSolver, row: int, col: int, heuristic: str) -> List[int]:
    values = list(solver.domains[row][col])
    if heuristic == "LCV":
        values.sort(key=lambda x: _count_conflicts(solver, row, col, x))
    return values

def _is_valid(grid: np.ndarray, row: int, col: int, value: int) -> bool:
    # Check row
    if value in grid[row, :]:
        return False
    
    # Check column
    if value in grid[:, col]:
        return False
    
    # Check 3x3 box
    box_row, box_col = 3 * (row // 3), 3 * (col // 3)
    if value in grid[box_row:box_row+3, box_col:box_col+3]:
        return False
    
    return True

def _update_domains(solver: SudokuSolver, row: int, col: int) -> bool:
    value = solver.grid[row][col]
    
    # Update row domains
    for j in range(9):
        if j != col and value in solver.domains[row][j]:
            solver.domains[row][j].remove(value)
            if len(solver.domains[row][j]) == 0:
                return False
                
    # Update column domains
    for i in range(9):
        if i != row and value in solver.domains[i][col]:
            solver.domains[i][col].remove(value)
            if len(solver.domains[i][col]) == 0:
                return False
                
    # Update box domains
    box_row, box_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(box_row, box_row + 3):
        for j in range(box_col, box_col + 3):
            if i != row and j != col and value in solver.domains[i][j]:
                solver.domains[i][j].remove(value)
                if len(solver.domains[i][j]) == 0:
                    return False
                    
    return True

def _count_conflicts(solver: SudokuSolver, row: int, col: int, value: int) -> int:
    conflicts = 0
    
    # Count row conflicts
    for j in range(9):
        if j != col and value in solver.domains[row][j]:
            conflicts += 1
            
    # Count column conflicts
    for i in range(9):
        if i != row and value in solver.domains[i][col]:
            conflicts += 1
            
    # Count box conflicts
    box_row, box_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(box_row, box_row + 3):
        for j in range(box_col, box_col + 3):
            if i != row and j != col and value in solver.domains[i][j]:
                conflicts += 1
                
    return conflicts

def _get_all_arcs():
    arcs = []
    for i in range(9):
        for j in range(9):
            for neighbor in _get_neighbors((i, j)):
                arcs.append(((i, j), neighbor))
    return arcs

def _get_neighbors(cell):
    row, col = cell
    neighbors = set()
    
    # Row neighbors
    for j in range(9):
        if j != col:
            neighbors.add((row, j))
            
    # Column neighbors
    for i in range(9):
        if i != row:
            neighbors.add((i, col))
            
    # Box neighbors
    box_row, box_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(box_row, box_row + 3):
        for j in range(box_col, box_col + 3):
            if i != row and j != col:
                neighbors.add((i, j))
                
    return neighbors

def _revise(solver: SudokuSolver, xi: Tuple[int, int], xj: Tuple[int, int]) -> bool:
    revised = False
    for x in list(solver.domains[xi[0]][xi[1]]):
        if not any(y != x for y in solver.domains[xj[0]][xj[1]]):
            solver.domains[xi[0]][xi[1]].remove(x)
            revised = True
    return revised
