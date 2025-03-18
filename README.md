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
- Warehouse Logistics:
  - Dynamic goal-based agent
  - Package delivery optimization
  - Obstacle avoidance

- City Meetup:
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

## Author
Mahantesh Hiremath- G24AIT2178