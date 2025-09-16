"""
GraphDB: Lightweight graph database for edge devices
Includes Node, Edge dataclasses and campus graph construction
"""
import math
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class Node:
    id: int
    code: str
    name: str
    building: int
    floor: int
    x: float
    y: float
    node_type: str

@dataclass
class Edge:
    to_id: int
    weight: float
    bearing: float

class GraphDB:
    def __init__(self):
        self.nodes: List[Node] = []
        self.adjacency: List[List[Edge]] = []
        self.lookup: Dict[str, int] = {}
        self.spatial_index: Dict[Tuple[int, int], List[int]] = {}
        self._build_realistic_campus()
        self._generate_connections()
        self._build_spatial_index()

    def _build_realistic_campus(self):
        campus_data = [
            # Building 10 - Floor 0
            ("100101", "Reception", 10, 0, 50.0, 50.0, "room"),
            ("100102", "Library", 10, 0, 30.0, 50.0, "room"),
            ("100103", "Restaurant", 10, 0, 70.0, 50.0, "room"),
            ("100104", "Makerspace", 10, 0, 20.0, 50.0, "room"),
            ("100105", "Computer Lab", 10, 0, 80.0, 50.0, "room"),
            ("100106", "Meeting Room A", 10, 0, 30.0, 30.0, "room"),
            ("100107", "Meeting Room B", 10, 0, 70.0, 30.0, "room"),
            ("100108", "Auditorium", 10, 0, 50.0, 20.0, "room"),
            ("100109", "Student Services", 10, 0, 20.0, 30.0, "room"),
            ("100110", "IT Support", 10, 0, 80.0, 30.0, "room"),
            # Building 10 - Floor 1
            ("101101", "Classroom 101", 10, 1, 20.0, 20.0, "room"),
            ("101102", "Classroom 102", 10, 1, 30.0, 20.0, "room"),
            ("101103", "Classroom 103", 10, 1, 50.0, 20.0, "room"),
            ("101140", "Lecture Hall 140", 10, 1, 80.0, 20.0, "room"),
            ("101105", "Group Room 1", 10, 1, 20.0, 10.0, "room"),
            ("101106", "Group Room 2", 10, 1, 30.0, 10.0, "room"),
            ("101107", "Group Room 3", 10, 1, 50.0, 10.0, "room"),
            ("101108", "Group Room 4", 10, 1, 70.0, 10.0, "room"),
            ("101109", "Student Kitchen", 10, 1, 80.0, 10.0, "room"),
            ("101110", "Study Area", 10, 1, 70.0, 20.0, "room"),
            # Building 10 - Floor 2
            ("102101", "IT Office 1", 10, 2, 20.0, 5.0, "room"),
            ("102102", "IT Office 2", 10, 2, 30.0, 5.0, "room"),
            ("102103", "IT Office 3", 10, 2, 50.0, 5.0, "room"),
            ("102104", "IT Office 4", 10, 2, 70.0, 5.0, "room"),
            ("102105", "Server Room", 10, 2, 50.0, 0.0, "room"),
            # Building 4 - Floor 0
            ("40101", "Room 4013", 4, 0, 5.0, 20.0, "room"),
            ("40102", "Study Area", 4, 0, 10.0, 50.0, "room"),
            ("40103", "Group Room 1", 4, 0, 10.0, 30.0, "room"),
            ("40104", "Group Room 2", 4, 0, 10.0, 20.0, "room"),
            ("40105", "Group Room 3", 4, 0, 5.0, 30.0, "room"),
            ("40106", "Lab Room A", 4, 0, 0.0, 30.0, "room"),
            ("40107", "Lab Room B", 4, 0, 0.0, 20.0, "room"),
            ("40108", "Student Lounge", 4, 0, 5.0, 10.0, "room"),
            ("40109", "Storage", 4, 0, 0.0, 10.0, "room"),
            ("40110", "Copy Room", 4, 0, 10.0, 10.0, "room"),
            # Building 4 - Floor 1
            ("41101", "Research Office 1", 4, 1, 5.0, 20.0, "room"),
            ("41102", "Research Office 2", 4, 1, 10.0, 20.0, "room"),
            ("41103", "Research Office 3", 4, 1, 5.0, 30.0, "room"),
            ("41104", "Research Office 4", 4, 1, 10.0, 30.0, "room"),
            ("41105", "Conference Room", 4, 1, 0.0, 30.0, "room"),
            # Corridors
            ("H10-C0", "Main Corridor Hus 10 Floor 0", 10, 0, 50.0, 40.0, "corridor"),
            ("H10-C1", "Main Corridor Hus 10 Floor 1", 10, 1, 50.0, 15.0, "corridor"),
            ("H10-C2", "Main Corridor Hus 10 Floor 2", 10, 2, 50.0, 2.5, "corridor"),
            ("H4-C0", "Main Corridor Hus 4 Floor 0", 4, 0, 10.0, 30.0, "corridor"),
            ("H4-C1", "Main Corridor Hus 4 Floor 1", 4, 1, 10.0, 30.0, "corridor"),
            ("CENTRAL", "Central Corridor", 0, 0, 30.0, 50.0, "corridor"),
            # Stairs
            ("H10-S1", "Main Stairwell Hus 10", 10, 0, 60.0, 40.0, "stairs"),
            ("H10-S2", "North Stairwell Hus 10", 10, 0, 50.0, 10.0, "stairs"),
            ("H4-S1", "Main Stairwell Hus 4", 4, 0, 15.0, 30.0, "stairs"),
            # Entrances
            ("H10-E1", "Main Entrance Hus 10", 10, 0, 50.0, 80.0, "entrance"),
            ("H10-E2", "Bus Entrance Hus 10", 10, 0, 80.0, 70.0, "entrance"),
            ("H10-E3", "Garden Entrance Hus 10", 10, 0, 20.0, 70.0, "entrance"),
            ("H4-E1", "Main Entrance Hus 4", 4, 0, 10.0, 70.0, "entrance"),
        ]
        for i, (code, name, building, floor, x, y, node_type) in enumerate(campus_data):
            node = Node(i, code, name, building, floor, x, y, node_type)
            self.nodes.append(node)
            self.lookup[code] = i
            self.adjacency.append([])

    def _generate_connections(self):
        for node in self.nodes:
            if node.node_type == "room":
                self._connect_room_to_corridor(node)
            elif node.node_type == "corridor":
                self._connect_corridor_network(node)
            elif node.node_type == "stairs":
                self._connect_stairs(node)
            elif node.node_type == "entrance":
                self._connect_entrance(node)

    def _connect_room_to_corridor(self, room):
        corridors = [n for n in self.nodes if n.node_type == "corridor" and n.building == room.building and n.floor == room.floor]
        if corridors:
            nearest = min(corridors, key=lambda c: self._euclidean_distance(room, c))
            distance = self._euclidean_distance(room, nearest)
            bearing = self._calculate_bearing(room, nearest)
            self.adjacency[room.id].append(Edge(nearest.id, distance, bearing))
            self.adjacency[nearest.id].append(Edge(room.id, distance, (bearing + 180) % 360))

    def _connect_corridor_network(self, corridor):
        # Connect to stairs on the same floor
        stairs = [n for n in self.nodes if n.node_type == "stairs" and n.building == corridor.building and n.floor == corridor.floor]
        for stair in stairs:
            distance = self._euclidean_distance(corridor, stair)
            if distance < 50:
                bearing = self._calculate_bearing(corridor, stair)
                self.adjacency[corridor.id].append(Edge(stair.id, distance, bearing))
                self.adjacency[stair.id].append(Edge(corridor.id, distance, (bearing + 180) % 360))
        # Only connect to central corridor if on the same floor
        if corridor.building != 0:
            central = next((n for n in self.nodes if n.code == "CENTRAL" and n.floor == corridor.floor), None)
            if central:
                distance = self._euclidean_distance(corridor, central) + 20
                bearing = self._calculate_bearing(corridor, central)
                self.adjacency[corridor.id].append(Edge(central.id, distance, bearing))
                self.adjacency[central.id].append(Edge(corridor.id, distance, (bearing + 180) % 360))

    def _connect_stairs(self, stairs):
        same_building_corridors = [n for n in self.nodes if n.node_type == "corridor" and n.building == stairs.building and n.floor != stairs.floor]
        for corridor in same_building_corridors:
            floor_diff = abs(stairs.floor - corridor.floor)
            distance = 5 + floor_diff * 10
            bearing = 0 if corridor.floor > stairs.floor else 180
            # Connect stairs to corridor
            self.adjacency[stairs.id].append(Edge(corridor.id, distance, bearing))
            # Connect corridor back to stairs (bidirectional)
            reverse_bearing = (bearing + 180) % 360
            self.adjacency[corridor.id].append(Edge(stairs.id, distance, reverse_bearing))

    def _connect_entrance(self, entrance):
        corridors = [n for n in self.nodes if n.node_type == "corridor" and n.building == entrance.building]
        if corridors:
            nearest = min(corridors, key=lambda c: self._euclidean_distance(entrance, c))
            distance = self._euclidean_distance(entrance, nearest)
            bearing = self._calculate_bearing(entrance, nearest)
            self.adjacency[entrance.id].append(Edge(nearest.id, distance, bearing))
            self.adjacency[nearest.id].append(Edge(entrance.id, distance, (bearing + 180) % 360))

    def _euclidean_distance(self, node1, node2):
        return math.sqrt((node1.x - node2.x)**2 + (node1.y - node2.y)**2)

    def _calculate_bearing(self, from_node, to_node):
        dx = to_node.x - from_node.x
        dy = to_node.y - from_node.y
        bearing = math.degrees(math.atan2(dx, dy))
        return (bearing + 360) % 360

    def _build_spatial_index(self):
        for node in self.nodes:
            grid_x = int(node.x // 10)
            grid_y = int(node.y // 10)
            key = (grid_x, grid_y)
            if key not in self.spatial_index:
                self.spatial_index[key] = []
            self.spatial_index[key].append(node.id)

    def neighbors(self, node_id):
        return self.adjacency[node_id]

    def get_node(self, node_id):
        return self.nodes[node_id]

    def all_nodes(self):
        return self.nodes

    def all_edges(self):
        return self.adjacency
