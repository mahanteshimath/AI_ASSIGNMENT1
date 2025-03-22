# AI Assignment 1 - IITJ

## Overview
This application implements two AI search problems:
1. Warehouse Logistics Optimization
2. City Meetup Search

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

- **City Meetup:**
  - A* and Greedy Best-First Search
  - Real Indian cities data
  - Interactive map visualization

## Project Structure
```
.
├── 🏠_Home.py
├── pages/
│   ├── 1_📦_Warehouse_Logistics.py
│   └── 2_🤝_City_Meetup.py
├── utils/
│   ├── warehouse_utils.py
│   └── meetup_utils.py
├── data/
│   └── india_states_districts_cities_coordinates.csv
├── requirements.txt
└── .streamlit/
    └── config.toml
```

### File Descriptions

- **🏠_Home.py**: The main entry point for the Streamlit application. Provides navigation to different sections.
- **pages/1_📦_Warehouse_Logistics.py**: Implements the warehouse logistics optimization problem.
- **pages/2_🤝_City_Meetup.py**: Implements the city meetup search problem.
- **utils/warehouse_utils.py**: Contains utility functions for the warehouse logistics problem.
- **utils/meetup_utils.py**: Contains utility functions for the city meetup search problem.
- **data/india_states_districts_cities_coordinates.csv**: CSV file containing coordinates of Indian cities.
- **requirements.txt**: Lists the Python dependencies required to run the application.
- **.streamlit/config.toml**: Configuration file for Streamlit settings.

## Author
Mahantesh Hiremath - G24AIT2178

## GitHub Repository
[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/your-repo-link)