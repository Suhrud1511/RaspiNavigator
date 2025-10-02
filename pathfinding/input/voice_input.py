import sounddevice as sd
import queue
import sys
import json
from vosk import Model, KaldiRecognizer
from db.graph_db import GraphDB
from display.led_matrix import LEDMatrix
from algorithms.astar import find_path_bidirectional_astar

class VoiceInput:
    def __init__(self):
        print("Initializing navigation system...")
        self.graph = GraphDB()
        self.display = LEDMatrix()
        print(f"Ready. {len(self.graph.nodes)} nodes, {sum(len(adj) for adj in self.graph.adjacency)} connections")
        self.q = queue.Queue()
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
        MODEL_PATH = "vosk-model-small-en-us-0.15"
        q = queue.Queue()
        def callback(indata, frames, time, status):
            if status:
                print(status, file=sys.stderr)
            q.put(bytes(indata))

        model = Model(MODEL_PATH)
        recognizer = KaldiRecognizer(model, 16000)

        print("Say the current room and destination separated by 'and'")
        with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                            channels=1, callback=callback):
            result_text = ""
            while True:
                data = q.get()
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    result_text = result.get("text", "")
                    if result_text:
                        break

        # debug
        print("Your input:", result_text)

        def extract_locations(text):
            words = text.lower().split()
            digit_map = {
                "zero": "0", "oh": "0", "one": "1", "two": "2", "to": "2", "too": "2",
                "three": "3", "four": "4", "for": "4", "five": "5", "six": "6", "seven": "7",
                "eight": "8", "nine": "9"
            }

            if "and" not in words:
                return []

            and_index = words.index("and")
            from_words = words[:and_index]
            to_words = words[and_index + 1:]

            def words_to_number(word_list):
                digits = [digit_map[w] for w in word_list if w in digit_map]
                return "".join(digits)

            from_loc = words_to_number(from_words)
            to_loc = words_to_number(to_words)

            return [from_loc, to_loc]

        locations = extract_locations(result_text)

        if len(locations) == 2:
            from_loc, to_loc = locations
            print(f"From: {from_loc}")
            print(f"To: {to_loc}")
            result = find_path_bidirectional_astar(self.graph, from_loc, to_loc)
            if not result["success"]:
                print(f"Error: {result['error']}")
                return
            print(f"\nRoute: {result['start_room'].name} → {result['end_room'].name}")
            print(f"Distance: {result['total_distance']}m")
            print(f"Time: {result['total_time']}s")
            print(f"Steps: {len(result['instructions'])}")
            if input("\nStart navigation? (y/N): ").lower() == 'y':
                self._step_navigation(result["instructions"])
        else:
            print("Could not detect both locations clearly.")
        if not result["success"]:
            print(f"Error: {result['error']}")
            return
        
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
    nav = VoiceInput()
    nav.run()

if __name__ == "__main__":
    main()
