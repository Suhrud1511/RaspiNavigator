import queue
import json
import os
import re
from typing import Optional, Tuple, Iterable, Set

import sounddevice as sd
from vosk import Model, KaldiRecognizer

from db.graph_db import GraphDB

BASE_DIR = os.path.dirname(__file__)
DEFAULT_MODEL = os.path.join(BASE_DIR, "vosk-model-small-en-us-0.15")

NUM_MAP = {
    'zero': '0', 'oh': '0', 'o': '0',
    'one': '1', 'two': '2', 'three': '3', 'four': '4',
    'five': '5', 'six': '6', 'seven': '7', 'eight': '8', 'nine': '9'
}


class VoiceInput:
    def __init__(self, model_path: str = DEFAULT_MODEL, samplerate: int = 16000):
        if not os.path.exists(model_path):
            raise RuntimeError(f"Vosk model not found at {model_path}. Download and extract the model.")
        self.model = Model(model_path)
        self.samplerate = samplerate
        self.q: queue.Queue = queue.Queue()
        self._stream = None

    def listen(self, prompt: str = "Speak (e.g. 'guide me from 100101 to 40101'):", grammar: Optional[Iterable[str]] = None) -> str:
        print(prompt)
        recognizer = KaldiRecognizer(self.model, self.samplerate, json.dumps(list(grammar)) if grammar else None)
        with sd.RawInputStream(samplerate=self.samplerate, blocksize=8000, dtype='int16', channels=1, callback=self._callback):
            while True:
                data = self.q.get()
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    text = result.get("text", "").strip()
                    if text:
                        return text
                else:
                    partial = json.loads(recognizer.PartialResult()).get("partial", "")
                    if partial:
                        print(f"Heard (partial): {partial}", end="\r")

    def _callback(self, indata, frames, time, status):
        self.q.put(bytes(indata))


def _words_to_digits(words: Iterable[str]) -> str:
    out = []
    for w in words:
        w = w.lower()
        if w in NUM_MAP:
            out.append(NUM_MAP[w])
        elif re.fullmatch(r"\d+", w):
            out.append(w)
    return ''.join(out)


def _find_candidate_codes_from_text(text: str, valid_codes: Optional[Set[str]] = None) -> Tuple[Optional[str], Optional[str]]:
    tokens = re.findall(r"\w+", text.lower())
    digit_tokens = []
    for t in tokens:
        if t in NUM_MAP or re.fullmatch(r"\d+", t):
            digit_tokens.append(t)
    candidates = []
    for i in range(len(digit_tokens)):
        for j in range(i + 1, min(i + 7, len(digit_tokens)) + 1):
            code = _words_to_digits(digit_tokens[i:j])
            if not code:
                continue
            if valid_codes is None or code in valid_codes:
                candidates.append(code)
    candidates = sorted(set(candidates), key=len, reverse=True)
    if len(candidates) >= 2:
        return candidates[0], candidates[1]
    if len(candidates) == 1:
        return candidates[0], None
    return None, None


def extract_rooms_from_text(text: str, graph: Optional[GraphDB] = None) -> Tuple[Optional[str], Optional[str]]:
    if graph is None:
        graph = GraphDB()
    valid_codes = {n.code for n in graph.nodes}

    m = re.search(r"(?:from\s+)?(?:room\s+)?(\w+)[^\w]+(?:to\s+)?(?:room\s+)?(\w+)", text, flags=re.I)
    if m:
        s, e = m.group(1).lower(), m.group(2).lower()
        if s in valid_codes and e in valid_codes:
            return s, e

    s, e = _find_candidate_codes_from_text(text, valid_codes)
    return s, e
