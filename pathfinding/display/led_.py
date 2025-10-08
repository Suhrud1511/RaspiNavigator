from sense_hat import SenseHat
import time as t

# --- Color constants ---
RED = [255, 0, 0]
WHITE = [255, 255, 255]
BLACK = [0, 0, 0]


class DirectionDisplay:
    """Handles direction arrow and number display on Sense HAT"""

    def __init__(self):
        self.sense = SenseHat()
        self.sense.clear()
        self.arrows = self._create_arrows()
        self.numbers = self._create_numbers()

    # -------------------------------
    # Arrow and number pattern setup
    # -------------------------------
    def _create_arrows(self):
        """Define 3-row arrow patterns"""
        return {
            'N': [
                [BLACK, BLACK, RED, RED, RED, BLACK, BLACK, BLACK],
                [BLACK, RED, BLACK, RED, BLACK, RED, BLACK, BLACK],
                [RED, BLACK, BLACK, RED, BLACK, BLACK, RED, BLACK],
            ],
            'S': [
                [RED, BLACK, BLACK, RED, BLACK, BLACK, RED, BLACK],
                [BLACK, RED, BLACK, RED, BLACK, RED, BLACK, BLACK],
                [BLACK, BLACK, RED, RED, RED, BLACK, BLACK, BLACK],
            ],
            'E': [
                [BLACK, BLACK, BLACK,BLACK, RED, RED, RED, BLACK],
                [BLACK, BLACK, BLACK, BLACK,  BLACK, BLACK, BLACK,RED],
                [BLACK, BLACK, BLACK,BLACK, RED, RED, RED,  BLACK],
            ],
            'W': [
                [BLACK, RED, RED, RED, BLACK, BLACK, BLACK, BLACK],
                [RED, BLACK , BLACK, BLACK, BLACK, BLACK, BLACK, BLACK],
                [BLACK, RED, RED, RED, BLACK, BLACK, BLACK, BLACK],
            ],
        }

    def _create_numbers(self):
        """Define 5-row number patterns"""
        return {
            '0': [
                [BLACK, WHITE, WHITE, BLACK],
                [WHITE, BLACK, BLACK, WHITE],
                [WHITE, BLACK, BLACK, WHITE],
                [WHITE, BLACK, BLACK, WHITE],
                [BLACK, WHITE, WHITE, BLACK],
            ],
            '1': [
                [BLACK, WHITE, BLACK, BLACK],
                [WHITE, WHITE, BLACK, BLACK],
                [BLACK, WHITE, BLACK, BLACK],
                [BLACK, WHITE, BLACK, BLACK],
                [WHITE, WHITE, WHITE, BLACK],
            ],
            '2': [
                [WHITE, WHITE, WHITE, BLACK],
                [BLACK, BLACK, WHITE, BLACK],
                [WHITE, WHITE, WHITE, BLACK],
                [WHITE, BLACK, BLACK, BLACK],
                [WHITE, WHITE, WHITE, BLACK],
            ],
            '3': [
                [WHITE, WHITE, WHITE, BLACK],
                [BLACK, BLACK, WHITE, BLACK],
                [WHITE, WHITE, WHITE, BLACK],
                [BLACK, BLACK, WHITE, BLACK],
                [WHITE, WHITE, WHITE, BLACK],
            ],
            '4': [
                [WHITE, BLACK, WHITE, BLACK],
                [WHITE, BLACK, WHITE, BLACK],
                [WHITE, WHITE, WHITE, BLACK],
                [BLACK, BLACK, WHITE, BLACK],
                [BLACK, BLACK, WHITE, BLACK],
            ],
            '5': [
                [WHITE, WHITE, WHITE, WHITE],
                [WHITE, BLACK, BLACK, BLACK],
                [WHITE, WHITE, WHITE, BLACK],
                [BLACK, BLACK, WHITE, BLACK],
                [WHITE, WHITE, WHITE, BLACK],
            ],
            '6': [
                [BLACK, WHITE, WHITE, BLACK],
                [WHITE, BLACK, BLACK, BLACK],
                [WHITE, WHITE, WHITE, BLACK],
                [WHITE, BLACK, BLACK, WHITE],
                [BLACK, WHITE, WHITE, BLACK],
            ],
            '7': [
                [WHITE, WHITE, WHITE, BLACK],
                [BLACK, BLACK, WHITE, BLACK],
                [BLACK, WHITE, BLACK, BLACK],
                [BLACK, WHITE, BLACK, BLACK],
                [BLACK, WHITE, BLACK, BLACK],
            ],
            '8': [
                [BLACK, WHITE, WHITE, BLACK],
                [WHITE, BLACK, BLACK, WHITE],
                [BLACK, WHITE, WHITE, BLACK],
                [WHITE, BLACK, BLACK, WHITE],
                [BLACK, WHITE, WHITE, BLACK],
            ],
            '9': [
                [BLACK, WHITE, WHITE, BLACK],
                [WHITE, BLACK, BLACK, WHITE],
                [BLACK, WHITE, WHITE, WHITE],
                [BLACK, BLACK, BLACK, WHITE],
                [BLACK, WHITE, WHITE, BLACK],
            ],
        }

    # -------------------------------
    # Core display methods
    # -------------------------------
    def clear(self):
        """Clear LED matrix"""
        self.sense.clear()

    def make_number_rows(self, distance):
        """Return a 5-row section for the number(s)"""
        rows = []
        if len(distance) == 1:
            # Center single digit
            num = self.numbers[distance]
            for r in range(5):
                rows.append([BLACK, BLACK, BLACK, num[r][0], num[r][1], num[r][2], num[r][3], BLACK])
        else:
            left, right = self.numbers[distance[0]], self.numbers[distance[1]]
            for r in range(5):
                rows.append(left[r] + right[r])
        return rows

    def build_display(self, direction, distance):
        """Combine arrow + digits into 8x8 pixel grid"""
        display = self.arrows[direction] + self.make_number_rows(distance)
        return [pix for row in display for pix in row]

    def show(self, direction, distance):
        """Display arrow and number on LED"""
        pixels = self.build_display(direction, distance)
        self.sense.set_pixels(pixels)

    def show_green_face(self):
        """Show a green happy face"""
        GREEN = [0, 255, 0]
        BLACK = [0, 0, 0]
        face = [
            BLACK, BLACK, GREEN, GREEN, GREEN, GREEN, BLACK, BLACK,
            BLACK, GREEN, GREEN, GREEN, GREEN, GREEN, GREEN, BLACK,
            GREEN, GREEN, BLACK, GREEN, GREEN, BLACK, GREEN, GREEN,
            GREEN, GREEN, GREEN, GREEN, GREEN, GREEN, GREEN, GREEN,
            GREEN, GREEN, GREEN, GREEN, GREEN, GREEN, GREEN, GREEN,
            GREEN, BLACK, GREEN, GREEN, GREEN, GREEN, BLACK, GREEN,
            BLACK, GREEN, BLACK, BLACK, BLACK, BLACK, GREEN, BLACK,
            BLACK, BLACK, GREEN, GREEN, GREEN, GREEN, BLACK, BLACK,
        ]
        self.sense.set_pixels(face)

    def show_red_face(self):
        """Show a red angry/sad face"""
        RED = [255, 0, 0]
        BLACK = [0, 0, 0]
        face = [
            BLACK, BLACK, RED, RED, RED, RED, BLACK, BLACK,
            BLACK, RED, RED, RED, RED, RED, RED, BLACK,
            RED, RED, BLACK, RED, RED, BLACK, RED, RED,
            RED, RED, RED, RED, RED, RED, RED, RED,
            RED, RED, RED, RED, RED, RED, RED, RED,
            RED, BLACK, RED, RED, RED, RED, BLACK, RED,
            BLACK, RED, BLACK, BLACK, BLACK, BLACK, RED, BLACK,
            BLACK, BLACK, RED, RED, RED, RED, BLACK, BLACK,
        ]
        self.sense.set_pixels(face)

# -------------------------------
# Main Program Loop
# -------------------------------
def main():
    display = DirectionDisplay()
    display.show_green_face()

    t.sleep(5)
    display.show_red_face()


    while True:
        data = input("Enter [from,to,direction,distance] (e.g. Home,Office,N,12): ")
        parts = [x.strip() for x in data.split(",")]

        if len(parts) != 4:
            print("❌ Invalid format! Expected: from,to,direction,distance")
            continue

        direction, distance = parts[2].upper(), parts[3]

        if direction not in display.arrows:
            print("❌ Invalid direction! Use N, S, E, or W.")
            continue
        if not distance.isdigit() or int(distance) > 99:
            print("❌ Distance must be 1–2 digits (0–99).")
            continue

        display.clear()
        display.show(direction, distance)


# Run program
if __name__ == "__main__":
    main()
