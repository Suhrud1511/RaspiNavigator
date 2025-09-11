"""
Highly optimized A* pathfinding for edge devices
Uses Euclidean and penalty heuristics, fast heapq, and memory-efficient structures
"""
import heapq
from db.graph_db import Node, Edge, GraphDB

def euclidean(n1: Node, n2: Node):
    return ((n1.x - n2.x)**2 + (n1.y - n2.y)**2) ** 0.5

def heuristic(n1: Node, n2: Node):
    spatial_dist = euclidean(n1, n2)
    building_penalty = 50 if n1.building != n2.building else 0
    floor_penalty = abs(n1.floor - n2.floor) * 15
    type_penalty = 5 if n1.node_type == "room" else 0
    return spatial_dist + building_penalty + floor_penalty + type_penalty

def find_path_astar(graph: GraphDB, start_code: str, end_code: str):
    if start_code not in graph.lookup or end_code not in graph.lookup:
        return {"success": False, "error": "Room not found"}
    start_id = graph.lookup[start_code]
    end_id = graph.lookup[end_code]
    open_heap = [(0, start_id)]
    came_from = {}
    g_score = {start_id: 0}
    f_score = {start_id: heuristic(graph.nodes[start_id], graph.nodes[end_id])}
    closed_set = set()
    while open_heap:
        current_f, current_id = heapq.heappop(open_heap)
        if current_id in closed_set:
            continue
        if current_id == end_id:
            return reconstruct_path(graph, came_from, current_id, start_id)
        closed_set.add(current_id)
        for edge in graph.adjacency[current_id]:
            neighbor_id = edge.to_id
            if neighbor_id in closed_set:
                continue
            tentative_g = g_score[current_id] + edge.weight
            if neighbor_id not in g_score or tentative_g < g_score[neighbor_id]:
                came_from[neighbor_id] = (current_id, edge)
                g_score[neighbor_id] = tentative_g
                f_score[neighbor_id] = tentative_g + heuristic(graph.nodes[neighbor_id], graph.nodes[end_id])
                heapq.heappush(open_heap, (f_score[neighbor_id], neighbor_id))
    return {"success": False, "error": "No path found"}

def reconstruct_path(graph, came_from, current_id, start_id):
    path = []
    edges = []
    while current_id in came_from:
        path.append(current_id)
        parent_id, edge = came_from[current_id]
        edges.append(edge)
        current_id = parent_id
    path.append(start_id)
    path.reverse()
    edges.reverse()
    instructions = []
    total_distance = 0
    for i, edge in enumerate(edges):
        from_node = graph.nodes[path[i]]
        to_node = graph.nodes[path[i + 1]]
        turn_direction = calculate_turn_direction(edges[i-1].bearing if i > 0 else 0, edge.bearing)
        instruction = generate_instruction(from_node, to_node, turn_direction, edge.weight)
        instructions.append({
            "step": i + 1,
            "from_node": from_node,
            "to_node": to_node,
            "distance": int(edge.weight),
            "bearing": edge.bearing,
            "turn_direction": turn_direction,
            "instruction": instruction,
            "time": max(3, int(edge.weight / 1.4))
        })
        total_distance += edge.weight
    return {
        "success": True,
        "start_room": graph.nodes[path[0]],
        "end_room": graph.nodes[path[-1]],
        "total_distance": int(total_distance),
        "total_time": sum(inst["time"] for inst in instructions),
        "instructions": instructions
    }

def calculate_turn_direction(prev_bearing, current_bearing):
    angle_diff = (current_bearing - prev_bearing + 360) % 360
    if angle_diff < 30 or angle_diff > 330:
        return "straight"
    elif 30 <= angle_diff <= 150:
        return "right"
    elif 210 <= angle_diff <= 330:
        return "left"
    else:
        return "u_turn"

def generate_instruction(from_node, to_node, turn_direction, distance):
    if to_node.node_type == "stairs":
        if to_node.floor > from_node.floor:
            return "Take stairs up"
        elif to_node.floor < from_node.floor:
            return "Take stairs down"
        else:
            return "Take stairs"
    action_map = {
        "straight": "Continue straight",
        "left": "Turn left",
        "right": "Turn right",
        "u_turn": "Turn around"
    }
    action = action_map.get(turn_direction, "Walk")
    if to_node.node_type == "room":
        return f"{action} to {to_node.name}"
    elif to_node.node_type == "corridor":
        return f"{action} along corridor"
    elif to_node.node_type == "entrance":
        return f"{action} to {to_node.name}"
    return f"{action} toward {to_node.name}"
