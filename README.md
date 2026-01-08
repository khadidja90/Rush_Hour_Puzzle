# 🚗 Rush Hour Puzzle Solver – Python
<img src="images/Screenshot 2026-01-08 200722.png" width="600">
## 🧩 Overview
This project implements the **Rush Hour puzzle game** and solves it automatically using
**Artificial Intelligence search algorithms**.

The puzzle is modeled as a **state-space search problem** and solved using:
- **Breadth-First Search (BFS)**
- **A* (A-star) search with heuristics**

The computed solution is then **animated using Pygame**, allowing a clear and visual
demonstration of the steps required to solve the puzzle.

---

## 🎯 Objectives
- Model the Rush Hour game as a search problem
- Implement and compare **uninformed** and **informed** search algorithms
- Design **heuristics** to improve search efficiency
- Visualize the solution through animation

---

## 🛠️ Technologies Used
- **Python 3**
- **Pygame**
- Data structures (Queue, Priority Queue)
- AI search algorithms

---

## 🧠 Algorithms Implemented

### 🔹 Breadth-First Search (BFS)
- Explores the state space level by level
- Guarantees the **shortest solution**
- High memory consumption for complex puzzles

### 🔹 A* Search Algorithm
Uses the evaluation function:
f(n) = g(n) + h(n)
- `g(n)`: cost from the initial state
- `h(n)`: heuristic estimation to the goal
- Faster and more efficient than BFS

---

## 🔍 Heuristics Used (A*)

1. **Blocking Cars Heuristic**
   - Counts the number of vehicles blocking the target car’s path to the exit

2. **Distance to Exit Heuristic**
   - Estimates how far the target car is from the exit

Both heuristics are **admissible**, ensuring optimal solutions.

---

## 🎞️ Animated Solution (Pygame)
- The solution is displayed **step by step**
- Vehicles move smoothly on the grid
- Helps visualize how the puzzle is solved

---

## 📊 Features
- Automatic puzzle solving
- BFS and A* comparison
- Heuristic-based optimization
- Graphical animation
- Clean and modular code

---

## 📌 Educational Value
This project demonstrates:
- State representation
- Search space exploration
- Heuristic design
- AI algorithms applied to games
- Visualization using Pygame

---

## 🚀 Future Improvements
- Add more puzzle configurations
- Compare heuristic performance
- Implement additional algorithms (DFS, IDA*)
- Improve graphical interface

---

## 📷 Demo
<img src="images/Screenshot 2026-01-08 195631.png" width="600">
<img src="images/Screenshot 2026-01-08 195719.png" width="600">
<img src="images/Screenshot 2026-01-08 195759.png" width="600">
<img src="images/Screenshot 2026-01-08 195835.png" width="600">
<img src="images/Screenshot 2026-01-08 195914.png" width="600">
