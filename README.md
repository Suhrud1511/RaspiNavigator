# RaspiNavigator

A sophisticated indoor navigation system designed for Raspberry Pi, featuring efficient pathfinding algorithms and an intuitive interface with voice input and LED display capabilities.

## Features

### 1. Advanced Pathfinding
- **Standard A\* Algorithm**: Optimized for indoor navigation with custom heuristics
- **Bidirectional A\* Search**: Faster pathfinding by running simultaneous searches from start and end points
- **Multi-Floor Navigation**: Seamlessly handles vertical navigation between floors

### 2. Smart Campus Modeling
- **Comprehensive Graph Database**: Represents buildings with rooms, corridors, stairs, and entrances
- **Automatic Connection System**: 
  - Rooms connect to nearest corridors
  - Stairs link different floors
  - Buildings connect through central corridors
  - Entrances integrate with building network
- **Spatial Indexing**: Efficient node lookup using grid-based spatial partitioning

### 3. Hardware Integration
- **Sense HAT Support**: 
  - LED Matrix display for directional guidance
  - Fallback to emulator when hardware isn't available
- **Voice Input**: Natural language processing for room selection
- **User Interface**: Command-line interface with voice and display feedback

## Technical Architecture

### GraphDB
```
Node(id, code, name, building, floor, x, y, node_type)
Edge(to_id, weight, bearing)
```

The database provides:
- Automatic spatial relationship generation
- Bidirectional connections between nodes
- Efficient node lookup and neighbor access
- Grid-based spatial indexing

### Navigation Engine
- Cost-based pathfinding with penalties for:
  - Floor changes
  - Building transitions
  - Distance traveled
- Turn-by-turn navigation instructions
- Distance and time estimation

## Installation

1. Clone the repository
```bash
git clone https://github.com/Suhrud1511/RaspiNavigator.git
```

2. Create and activate virtual environment
```bash
python -m venv env
source env/bin/activate  # On Unix or MacOS
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

## Usage

1. Start the navigation system:
```bash
python pathfinding/pathfinder.py
```

2. Use voice commands or text input to specify start and end locations

3. Follow the LED display for directions

## Project Structure

```
RaspiNavigator/
├── pathfinding/
│   ├── algorithms/
│   │   └── astar.py          # A* implementations
│   ├── db/
│   │   └── graph_db.py       # Graph database
│   ├── display/
│   │   └── led_matrix.py     # LED display interface
│   ├── navigation/
│   │   ├── cli.py           # Command interface
│   │   └── voice_utils.py   # Voice processing
│   └── pathfinder.py        # Main entry point
└── env/                     # Virtual environment
```

## License

This project is licensed under the [LICENSE](LICENSE) - see the LICENSE file for details.
