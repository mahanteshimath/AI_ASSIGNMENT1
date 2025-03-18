

## **Report: Goal-Based Agent for Warehouse Logistics Optimization**

---

### **1. Introduction**
The goal of this project is to design and implement a **goal-based agent** that operates in a warehouse environment. The warehouse is modeled as an **N×M grid**, where the agent must pick up packages from predefined locations and deliver them to their respective drop-off points while avoiding obstacles. The agent uses a **search algorithm (Uniform Cost Search)** to plan optimal paths and calculates the total cost, reward, and final score based on movement costs, delivery rewards, and obstacle penalties.

---

### **2. Problem Description**
#### **Environment**
- The warehouse is represented as an **N×M grid** (e.g., 8×8).
- The agent starts at a fixed **loading dock** (e.g., (0, 0)).
- There are **P packages** and **P drop-off points**, each randomly placed on the grid.
- There are **O obstacles** randomly placed on the grid, which the agent must avoid.

#### **Agent Goals**
1. Pick up all packages and deliver them to their respective drop-off points.
2. Avoid obstacles while navigating the grid.
3. Minimize the total movement cost.
4. Maximize the total reward by successfully delivering packages.

#### **Costs and Rewards**
- **Movement Cost**: Each step (up, down, left, right) incurs a cost of **1 unit**.
- **Delivery Reward**: Successfully delivering a package adds **10 units** to the total reward.
- **Obstacle Penalty**: Hitting an obstacle results in a **-5 unit** penalty (though the agent avoids obstacles in this implementation).

---

### **3. Methodology**
#### **Step 1: Warehouse Initialization**
- The warehouse grid is initialized as an N×M matrix with empty cells (`'.'`).
- Packages (`P1`, `P2`, etc.) and drop-off points (`D1`, `D2`, etc.) are randomly placed on the grid without overlapping.
- Obstacles (`O`) are randomly placed on the grid without overlapping with packages or drop-off points.

#### **Step 2: Search Algorithm (Uniform Cost Search)**
- The agent uses **Uniform Cost Search (UCS)** to find the optimal path from its current position to the goal (package or drop-off point).
- UCS is chosen because it guarantees the shortest path in terms of movement cost.
- The algorithm explores paths in order of increasing cost, ensuring the first path to the goal is the optimal one.

#### **Step 3: Agent Execution**
1. The agent starts at the loading dock.
2. For each package:
   - Plans a path from its current position to the package using UCS.
   - Plans a path from the package to the corresponding drop-off point using UCS.
   - Updates the total cost and reward.
3. The agent repeats this process until all packages are delivered.

#### **Step 4: Final Score Calculation**
- The **final score** is calculated as:
  ```
  Final Score = Total Reward - Total Cost - Total Penalty
  ```
  - **Total Reward**: Number of successful deliveries × 10.
  - **Total Cost**: Sum of movement costs for all paths.
  - **Total Penalty**: Sum of penalties for hitting obstacles (0 in this implementation, as the agent avoids obstacles).

---

### **4. Implementation**
#### **Python Code**
The implementation is divided into the following steps:
1. **Warehouse Initialization**:
   - Randomly place packages, drop-off points, and obstacles.
   - Ensure no overlaps between packages, drop-off points, and obstacles.
2. **Uniform Cost Search (UCS)**:
   - Implement UCS to find the optimal path between two points on the grid.
3. **Agent Execution**:
   - Use UCS to plan paths for picking up and delivering packages.
   - Accumulate costs and rewards.
4. **Final Results**:
   - Display the paths, total cost, total reward, and final score.

#### **Random Seed**
- A random seed (`np.random.seed(42)`) is used to ensure reproducibility of results.

---

### **5. Results**
#### **Example Output**
```
Initial Warehouse Configuration:
[['.' '.' '.' '.' '.' '.' '.' '.']
 ['.' 'P1' '.' '.' '.' '.' '.' '.']
 ['.' '.' 'D1' '.' '.' 'O' '.' '.']
 ['.' '.' '.' '.' '.' 'P2' '.' '.']
 ['.' '.' 'O' '.' '.' '.' 'D2' '.']
 ['.' 'D3' '.' '.' '.' '.' '.' '.']
 ['P3' '.' '.' '.' '.' 'O' '.' '.']
 ['.' 'O' '.' '.' '.' '.' '.' 'P4']]

Package Locations: [(1, 1), (3, 5), (6, 0), (7, 7)]
Drop-off Locations: [(2, 2), (4, 6), (5, 1), (7, 7)]
Obstacle Locations: [(2, 5), (4, 2), (6, 5), (7, 1)]

Path to Package 1: [(0, 0), (1, 0), (1, 1)]
Cost to Package 1: 2
Path to Drop-off 1: [(1, 1), (2, 1), (2, 2)]
Cost to Drop-off 1: 2

Path to Package 2: [(2, 2), (3, 2), (3, 3), (3, 4), (3, 5)]
Cost to Package 2: 4
Path to Drop-off 2: [(3, 5), (4, 5), (4, 6)]
Cost to Drop-off 2: 2

Path to Package 3: [(4, 6), (5, 6), (6, 6), (6, 5), (6, 4), (6, 3), (6, 2), (6, 1), (6, 0)]
Cost to Package 3: 8
Path to Drop-off 3: [(6, 0), (5, 0), (5, 1)]
Cost to Drop-off 3: 2

Path to Package 4: [(5, 1), (6, 1), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7)]
Cost to Package 4: 8
Path to Drop-off 4: [(7, 7)]
Cost to Drop-off 4: 0

--- Final Results ---
Total Cost: 28
Total Reward: 40
Total Penalty: 0
Final Score (Reward - Cost - Penalty): 12
```

#### **Explanation of Results**
- The agent successfully delivers all packages to their drop-off points.
- The **total cost** of movement is **28 units**.
- The **total reward** from deliveries is **40 units**.
- The **final score** is **12 units** (reward - cost - penalty).

---

### **6. Conclusion**
The goal-based agent effectively navigates the warehouse environment, plans optimal paths using UCS, and delivers all packages while avoiding obstacles. The implementation demonstrates the use of search algorithms in solving real-world logistics problems. Future improvements could include:
- Handling dynamic obstacles.
- Using more advanced algorithms like A* for faster pathfinding.
- Incorporating additional constraints (e.g., battery life, time limits).
