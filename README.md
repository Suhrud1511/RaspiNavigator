# RaspiNavigator

## Algorithms

This project provides standard and bidirectional A* pathfinding algorithms for indoor navigation. The algorithms are designed to efficiently find routes in multi-floor building layouts.

- **A***: Finds the shortest path using a heuristic (distance plus penalties for floor/building changes).
- **Bidirectional A***: Runs two A* searches from start and end, meeting in the middle for faster results.

---

## GraphDB

The `GraphDB` class represents the building as a graph of rooms, corridors, stairs, and entrances.

- **Nodes**: Each room, corridor, or stair is a node with spatial and type information.
- **Edges**: Connections between nodes, with distance and direction.
- **Automatic Connections**: Rooms connect to corridors, stairs connect floors, and entrances connect to the building.

---

See the code in `pathfinding/algorithms/astar.py` and `pathfinding/db/graph_db.py` for details.