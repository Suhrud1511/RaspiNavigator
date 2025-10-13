import heapq
from db.graph_db import GraphDB, Node

def heuristic(n1: Node, n2: Node):
    dx = n1.x - n2.x
    dy = n1.y - n2.y
    spatial = (dx * dx + dy * dy) ** 0.5
    building = 50 if n1.building != n2.building else 0
    floor = abs(n1.floor - n2.floor) * 15
    t = 5 if n1.node_type == "room" else 0
    return spatial + building + floor + t

def find_path_astar(graph: GraphDB, start_code: str, end_code: str):
    if start_code not in graph.lookup or end_code not in graph.lookup:
        return {"success": False, "error": "Room not found"}
    start_id = graph.lookup[start_code]
    end_id = graph.lookup[end_code]
    start_node = graph.nodes[start_id]
    end_node = graph.nodes[end_id]
    open_heap = [(heuristic(start_node, end_node), 0, start_id)]
    open_set = {start_id}
    came_from = {}
    g_score = {start_id: 0}
    closed = set()
    while open_heap:
        _, g, current = heapq.heappop(open_heap)
        if current == end_id:
            return reconstruct_path(graph, came_from, current, start_id)
        open_set.discard(current)
        closed.add(current)
        for edge in graph.adjacency[current]:
            neighbor = edge.to_id
            if neighbor in closed:
                continue
            tentative_g = g_score[current] + edge.weight
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = (current, edge)
                g_score[neighbor] = tentative_g
                if neighbor not in open_set:
                    heapq.heappush(open_heap, (tentative_g + heuristic(graph.nodes[neighbor], end_node), tentative_g, neighbor))
                    open_set.add(neighbor)
    return {"success": False, "error": "No path found"}

def find_path_bidirectional_astar(graph: GraphDB, start_code: str, end_code: str):
    if start_code not in graph.lookup or end_code not in graph.lookup:
        return {"success": False, "error": "Room not found"}
    start_id = graph.lookup[start_code]
    end_id = graph.lookup[end_code]
    f_heap = [(heuristic(graph.nodes[start_id], graph.nodes[end_id]), 0, start_id)]
    b_heap = [(heuristic(graph.nodes[end_id], graph.nodes[start_id]), 0, end_id)]
    f_set, b_set = {start_id}, {end_id}
    f_g, b_g = {start_id: 0}, {end_id: 0}
    f_came, b_came = {}, {}
    f_closed, b_closed = set(), set()
    best, meet = float('inf'), None
    while f_heap and b_heap:
        if f_heap:
            _, g, curr = heapq.heappop(f_heap)
            f_set.discard(curr)
            f_closed.add(curr)
            if curr in b_closed:
                total = f_g[curr] + b_g[curr]
                if total < best:
                    best = total
                    meet = curr
            for edge in graph.adjacency[curr]:
                n = edge.to_id
                if n in f_closed:
                    continue
                tg = f_g[curr] + edge.weight
                if n not in f_g or tg < f_g[n]:
                    f_came[n] = (curr, edge)
                    f_g[n] = tg
                    if n not in f_set:
                        heapq.heappush(f_heap, (tg + heuristic(graph.nodes[n], graph.nodes[end_id]), tg, n))
                        f_set.add(n)
        if b_heap:
            _, g, curr = heapq.heappop(b_heap)
            b_set.discard(curr)
            b_closed.add(curr)
            if curr in f_closed:
                total = f_g[curr] + b_g[curr]
                if total < best:
                    best = total
                    meet = curr
            for edge in graph.adjacency[curr]:
                n = edge.to_id
                if n in b_closed:
                    continue
                tg = b_g[curr] + edge.weight
                if n not in b_g or tg < b_g[n]:
                    b_came[n] = (curr, edge)
                    b_g[n] = tg
                    if n not in b_set:
                        heapq.heappush(b_heap, (tg + heuristic(graph.nodes[n], graph.nodes[start_id]), tg, n))
                        b_set.add(n)
        if meet is not None:
            f_path, f_edges = [], []
            n = meet
            while n in f_came:
                f_path.append(n)
                p, e = f_came[n]
                f_edges.append(e)
                n = p
            f_path.append(start_id)
            f_path.reverse()
            f_edges.reverse()
            b_path, b_edges = [], []
            n = meet
            while n in b_came:
                b_path.append(n)
                p, e = b_came[n]
                b_edges.append(e)
                n = p
            b_path = b_path[1:]
            full_path = f_path + b_path
            full_edges = f_edges + b_edges
            if len(full_edges) != len(full_path) - 1:
                m = min(len(full_edges), len(full_path) - 1)
                full_edges = full_edges[:m]
                full_path = full_path[:m+1]
            return build_instructions(graph, full_path, full_edges)
    return {"success": False, "error": "No path found"}

def reconstruct_path(graph, came_from, current_id, start_id):
    path, edges = [], []
    while current_id in came_from:
        path.append(current_id)
        parent_id, edge = came_from[current_id]
        edges.append(edge)
        current_id = parent_id
    path.append(start_id)
    path.reverse()
    edges.reverse()
    return build_instructions(graph, path, edges)

def build_instructions(graph, path, edges):
    instructions = []
    total_distance = 0
    for i, edge in enumerate(edges):
        from_node = graph.nodes[path[i]]
        to_node = graph.nodes[path[i + 1]]
        prev_bearing = edges[i-1].bearing if i > 0 else 0
        turn = calculate_turn_direction(prev_bearing, edge.bearing)
        instr = generate_instruction(from_node, to_node, turn, edge.weight)
        instructions.append({
            "step": i + 1,
            "from_node": from_node,
            "to_node": to_node,
            "distance": int(edge.weight),
            "bearing": edge.bearing,
            "turn_direction": turn,
            "instruction": instr,
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
    angle = (current_bearing - prev_bearing + 360) % 360
    if angle < 30 or angle > 330:
        return "straight"
    if 30 <= angle <= 150:
        return "right"
    if 210 <= angle <= 330:
        return "left"
    return "u_turn"

def generate_instruction(from_node, to_node, turn_direction, distance):
    if to_node.node_type == "stairs":
        if to_node.floor > from_node.floor:
            return "Take stairs up"
        if to_node.floor < from_node.floor:
            return "Take stairs down"
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
    if to_node.node_type == "corridor":
        return f"{action} along corridor"
    if to_node.node_type == "entrance":
        return f"{action} to {to_node.name}"
    return f"{action} toward {to_node.name}"
