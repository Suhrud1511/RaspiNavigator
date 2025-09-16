"""
Navigation CLI: User interface for pathfinding
"""
from db.graph_db import GraphDB
from display.led_matrix import LEDMatrix
from algorithms.astar import find_path_bidirectional_astar

class NavigationSystem:
    def __init__(self):
        print("Initializing navigation system...")
        self.graph = GraphDB()
        self.display = LEDMatrix()
        print(f"Ready. {len(self.graph.nodes)} nodes, {sum(len(adj) for adj in self.graph.adjacency)} connections")
    def run(self):
        while True:
            print("\n1. Navigate")
            print("2. List rooms")
            print("3. Exit")
            choice = input("Choose: ").strip()
            if choice == "1":
                self._navigate()
            elif choice == "2":
                self._list_rooms()
            elif choice == "3":
                break
    def _navigate(self):
        start = input("Start room: ").strip()
        end = input("End room: ").strip()
        if not start or not end:
            print("Invalid input")
            return
        result = find_path_bidirectional_astar(self.graph, start, end)
        if not result["success"]:
            print(f"Error: {result['error']}")
            return
        print(f"\nRoute: {result['start_room'].name} → {result['end_room'].name}")
        print(f"Distance: {result['total_distance']}m")
        print(f"Time: {result['total_time']}s")
        print(f"Steps: {len(result['instructions'])}")
        if input("\nStart navigation? (y/N): ").lower() == 'y':
            self._step_navigation(result["instructions"])
    def _step_navigation(self, instructions):
        for i, instruction in enumerate(instructions):
            print(f"\nStep {i+1}/{len(instructions)}")
            print(f"Instruction: {instruction['instruction']}")
            print(f"Distance: {instruction['distance']}m")
            self.display.display_step(instruction)
            if input("\nPress ENTER (q to quit): ").lower() == 'q':
                break
        print("\nNavigation complete!")
    def _list_rooms(self):
        rooms = [(n.code, n.name, n.building, n.floor) for n in self.graph.nodes if n.node_type == "room"]
        for building in sorted(set(r[2] for r in rooms)):
            print(f"\nBuilding {building}:")
            building_rooms = [r for r in rooms if r[2] == building]
            for code, name, _, floor in sorted(building_rooms):
                print(f"  {code}: {name} (Floor {floor})")

def main():
    nav = NavigationSystem()
    nav.run()

if __name__ == "__main__":
    main()
