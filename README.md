# AI Assignment 1 - IITJ

# Click bellow to start running code 

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/mahanteshimath/AI_ASSIGNMENT1?quickstart=1)

## Overview
This application implements four AI search problems:
1. Warehouse Logistics Optimization 
2. City Meetup Search
3. Sudoku Solver
4. N-Queens Problem Solver

## Installation
```bash
pip install -r requirements.txt
```

## Running the Application
```bash
streamlit run 🏠_Home.py
```

## Features
- **Warehouse Logistics:**
  - Dynamic goal-based agent
  - Package delivery optimization
  - Obstacle avoidance
  - UCS (Uniform Cost Search) implementation
  - Real-time path visualization
  - Interactive grid configuration

- **City Meetup:**
  - A* and Greedy Best-First Search
  - Real Indian cities data
  - Interactive map visualization
  - Distance-based heuristics
  - State-wise city filtering
  - Real-time path updates

- **Sudoku Solver:**
  - CSP (Constraint Satisfaction Problem) implementation
  - Multiple solving strategies
  - Variable heuristics selection
  - Interactive grid input
  - Step-by-step solution tracking
  - Visual constraint propagation

- **N-Queens Solver:**
  - Simulated Annealing implementation
  - Hill Climbing with random restart
  - Dynamic board size (4-20)
  - Temperature control analysis
  - Energy visualization
  - Interactive board display

## Technical Stack
- Python 3.8+
- Streamlit for web interface
- NumPy for numerical computations
- Plotly for interactive visualizations
- Matplotlib for plotting
- Pandas for data handling

## File Details

### Core Files
- **🏠_Home.py**: Landing page with problem explanations and navigation
  - Navigation interface
  - Problem descriptions
  - Visual guides
  - Footer with author info

### Problem Implementations
- **pages/1_📦_Warehouse_Logistics.py**:
  - Grid-based environment
  - Package/obstacle placement
  - Path visualization
  - Performance metrics

- **pages/2_🤝_City_Meetup.py**:
  - Interactive map interface
  - City selection by state
  - Path visualization
  - Distance calculations
  - Search algorithm comparison

- **pages/3_🎮_Sudoku_Solver.py**:
  - Grid input interface
  - Solution visualization
  - Algorithm selection
  - Performance tracking
  - Step tracking

- **pages/4_👑_N_Queens_Solver.py**:
  - Board size configuration
  - Algorithm selection
  - Temperature control
  - Solution visualization
  - Performance graphs

### Utility Modules
- **utils/warehouse_utils.py**:
  - Grid management
  - Path finding algorithms
  - State space handling
  - Cost calculations

- **utils/meetup_utils.py**:
  - City data processing
  - Distance calculations
  - Search implementations
  - Path optimization

- **utils/sudoku_utils.py**:
  - CSP implementation
  - Constraint checking
  - Solution validation
  - Domain filtering

- **utils/queens_utils.py**:
  - Board state management
  - Algorithm implementations
  - Temperature scheduling
  - Move generation

### Data and Configuration
- **data/india_states_districts_cities_coordinates.csv**:
  - City coordinates
  - State/district mapping
  - Distance data
  - Geographic information

- **requirements.txt**: Dependencies including
  ```
  streamlit>=1.8.0
  numpy>=1.21.0
  pandas>=1.3.0
  plotly>=5.3.0
  matplotlib>=3.4.0
  folium>=0.12.0
  streamlit-folium>=0.6.0
  ```

- **.streamlit/config.toml**:
  - Page configuration
  - Theme settings
  - Display options
  - Performance settings

## Development

### Local Setup
1. Clone the repository
```bash
git clone https://github.com/mahanteshimath/AI_ASSIGNMENT1.git
cd AI_ASSIGNMENT1
```

2. Create virtual environment (optional)
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Run the application
```bash
streamlit run 🏠_Home.py
```

### Code Structure
- Modular design with separate utility modules
- Object-oriented implementation of algorithms
- Interactive web interface using Streamlit
- Visualization using Plotly and Matplotlib

## Author
Mahantesh Hiremath - G24AIT2178

## GitHub Repository
[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/mahanteshimath/AI_ASSIGNMENT1)