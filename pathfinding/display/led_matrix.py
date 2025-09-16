"""
LEDMatrix: Display logic for navigation steps
"""
import math

class LEDMatrix:
    def __init__(self):
        self.size = 8
        self.clear()

    def clear(self):
        self.matrix = [[' ' for _ in range(self.size)] for _ in range(self.size)]

    def display_step(self, instruction):
        self.clear()
        turn_direction = instruction["turn_direction"]
        distance = instruction["distance"]
        # Only show a single arrow head for clarity
        center = self.size // 2
        if turn_direction == "straight":
            self.matrix[center-2][center] = '▲'
        elif turn_direction == "left":
            self.matrix[center][center-2] = '◀'
        elif turn_direction == "right":
            self.matrix[center][center+2] = '▶'
        elif "stairs up" in instruction["instruction"].lower():
            # Draw a stair-step pattern up and an arrow
            for i in range(4):
                self.matrix[center+1-i][center-2+i] = '█'
            self.matrix[center-3][center+2] = '▲'
        elif "stairs down" in instruction["instruction"].lower():
            # Draw a stair-step pattern down and an arrow
            for i in range(4):
                self.matrix[center-2+i][center-2+i] = '█'
            self.matrix[center+3][center+2] = '▼'
        else:
            # Default: show a dot in the center
            self.matrix[center][center] = '•'
        self._add_distance(distance)
        self._print()

    def _draw_straight_arrow(self):
        center = self.size // 2
        for y in range(2, 6):
            self.matrix[y][center] = '█'
        self.matrix[1][center] = '▲'

    def _draw_left_turn(self):
        center = self.size // 2
        for x in range(1, center+1):
            self.matrix[center][x] = '█'
        for y in range(center, 6):
            self.matrix[y][1] = '█'
        self.matrix[center][0] = '◀'

    def _draw_right_turn(self):
        center = self.size // 2
        for x in range(center, self.size-1):
            self.matrix[center][x] = '█'
        for y in range(center, 6):
            self.matrix[y][self.size-2] = '█'
        self.matrix[center][self.size-1] = '▶'

    def _draw_stairs_up(self):
        for i in range(4):
            self.matrix[6-i][i+2] = '█'
        self.matrix[1][self.size//2] = '▲'

    def _draw_stairs_down(self):
        for i in range(4):
            self.matrix[1+i][i+2] = '█'
        self.matrix[self.size-2][self.size//2] = '▼'

    def _draw_general_direction(self, bearing):
        center = self.size // 2
        rad = math.radians(bearing)
        dx = math.sin(rad) * 3
        dy = math.cos(rad) * 3
        end_x = int(center + dx)
        end_y = int(center - dy)
        self._draw_line(center, center, end_x, end_y)
        if 0 <= end_x < self.size and 0 <= end_y < self.size:
            self.matrix[end_y][end_x] = '►'

    def _draw_line(self, x0, y0, x1, y1):
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        x, y = x0, y0
        while True:
            if 0 <= x < self.size and 0 <= y < self.size:
                self.matrix[y][x] = '█'
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def _add_distance(self, distance):
        dist_str = f"{distance}m"
        start = max(0, (self.size - len(dist_str)) // 2)
        for i, char in enumerate(dist_str):
            if start + i < self.size:
                self.matrix[self.size-1][start + i] = char

    def _print(self):
        print("┌" + "─" * self.size + "┐")
        for row in self.matrix:
            print("│" + "".join(row) + "│")
        print("└" + "─" * self.size + "┘")
