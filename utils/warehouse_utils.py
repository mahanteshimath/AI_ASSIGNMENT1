import numpy as np
from queue import PriorityQueue

def get_cell_content(cell):
    """Safely parse cell content and return type and number."""
    if isinstance(cell, str):
        if cell == '.':
            return ('empty', None)
        elif cell == 'O':
            return ('obstacle', None)
        elif cell.startswith('P'):
            return ('package', cell[1:])
        elif cell.startswith('D'):
            return ('dropoff', cell[1:])
    return ('unknown', None)

def get_cell_display(cell):
    """Get the display representation of a cell."""
    cell_type, number = get_cell_content(cell)
    if cell_type == 'empty':
        return '.'
    elif cell_type == 'obstacle':
        return 'O'
    elif cell_type == 'package':
        return f'P{number}'
    elif cell_type == 'dropoff':
        return f'D{number}'
    return str(cell)

def setup_warehouse(N=8, M=8, P=4, O=5):
    """Initialize warehouse grid with packages, drop-off points, and obstacles."""
    # Validate input parameters
    if N <= 0 or M <= 0:
        raise ValueError("Grid dimensions must be positive")
    if P <= 0:
        raise ValueError("Number of packages must be positive")
    if O < 0:
        raise ValueError("Number of obstacles cannot be negative")
    if P + O >= N * M:
        raise ValueError("Too many packages and obstacles for grid size")

    # Initialize empty warehouse
    warehouse = np.full((N, M), '.')
    package_locations, dropoff_locations, obstacle_locations = [], [], []
    
    # Place packages and drop-off points with maximum retry attempts
    max_attempts = 100
    for i in range(P):
        attempts = 0
        while attempts < max_attempts:
            package = (np.random.randint(0, N), np.random.randint(0, M))
            dropoff = (np.random.randint(0, N), np.random.randint(0, M))
            if (package != dropoff and 
                package not in package_locations and 
                dropoff not in dropoff_locations and
                warehouse[package[0]][package[1]] == '.' and
                warehouse[dropoff[0]][dropoff[1]] == '.'):
                package_locations.append(package)
                dropoff_locations.append(dropoff)
                warehouse[package[0]][package[1]] = f'P{i+1}'
                warehouse[dropoff[0]][dropoff[1]] = f'D{i+1}'
                break
            attempts += 1
        if attempts >= max_attempts:
            raise RuntimeError("Could not place packages and drop-off points")

    # Place obstacles with validation
    obstacles_placed = 0
    attempts = 0
    while obstacles_placed < O and attempts < max_attempts:
        obstacle = (np.random.randint(0, N), np.random.randint(0, M))
        if warehouse[obstacle[0]][obstacle[1]] == '.':
            warehouse[obstacle[0]][obstacle[1]] = 'O'
            obstacle_locations.append(obstacle)
            obstacles_placed += 1
        attempts += 1
    
    if obstacles_placed < O:
        raise RuntimeError("Could not place all obstacles")

    # When setting cell values, use get_cell_display:
    for idx, (x, y) in enumerate(package_locations):
        warehouse[x][y] = get_cell_display(f'P{idx+1}')
    
    for idx, (x, y) in enumerate(dropoff_locations):
        warehouse[x][y] = get_cell_display(f'D{idx+1}')
    
    for x, y in obstacle_locations:
        warehouse[x][y] = get_cell_display('O')

    return warehouse, package_locations, dropoff_locations, obstacle_locations

def ucs(start, goal, grid, N, M):
    """Uniform Cost Search implementation."""
    frontier = PriorityQueue()
    frontier.put((0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}
    directions = [(-1,0), (1,0), (0,-1), (0,1)]
    
    while not frontier.empty():
        cost, current = frontier.get()
        if current == goal:
            break
            
        for d in directions:
            next_pos = (current[0] + d[0], current[1] + d[1])
            if 0 <= next_pos[0] < N and 0 <= next_pos[1] < M:
                if grid[next_pos[0]][next_pos[1]] == 'O':
                    continue
                new_cost = cost + 1
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    frontier.put((new_cost, next_pos))
                    came_from[next_pos] = current
    
    if goal in cost_so_far:
        path = []
        cur = goal
        while cur is not None:
            path.append(cur)
            cur = came_from[cur]
        path.reverse()
        return path, cost_so_far[goal]
    return None, None

def run_agent_simulation(warehouse, package_locations, dropoff_locations, start=(0,0)):
    """Simulate the agent delivering all packages."""
    if not package_locations or not dropoff_locations:
        raise ValueError("No packages or drop-off points provided")
    if len(package_locations) != len(dropoff_locations):
        raise ValueError("Mismatch in number of packages and drop-off points")
    
    N, M = warehouse.shape
    if not (0 <= start[0] < N and 0 <= start[1] < M):
        raise ValueError("Invalid start position")

    total_cost = 0
    total_reward = 0
    paths = []
    current_position = start
    
    for i in range(len(package_locations)):
        package = package_locations[i]
        dropoff = dropoff_locations[i]
        
        # Find path to package
        path_to_package, cost_to_package = ucs(current_position, package, warehouse, N, M)
        if path_to_package is None:
            return None, None, None, None  # No valid path found
            
        # Find path from package to drop-off
        path_to_dropoff, cost_to_dropoff = ucs(package, dropoff, warehouse, N, M)
        if path_to_dropoff is None:
            return None, None, None, None  # No valid path found
            
        total_cost += (cost_to_package + cost_to_dropoff)
        total_reward += 10  # Delivery reward
        
        paths.append({
            "package": package,
            "path_to_package": path_to_package,
            "cost_to_package": cost_to_package,
            "dropoff": dropoff,
            "path_to_dropoff": path_to_dropoff,
            "cost_to_dropoff": cost_to_dropoff
        })
        
        current_position = dropoff
    
    final_reward = total_reward - total_cost
    return total_cost, total_reward, final_reward, paths
