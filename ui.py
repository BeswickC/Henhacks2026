import tkinter as tk
from tkinter import ttk
import time


class Smoother:
    def __init__(self):
        self.stable_state = "neutral"
        self.suspected = None
        self.suspected_start = None

        self.hold_time = {
            "distracted": 0.4,
            "productive": 0.7,
            "neutral": 0.8
            }

    def update(self, state):
        now = time.time()

        if state == self.stable_state:
            self.suspected = None
            self.suspected_start = None
            return self.stable_state
        
        if self.suspected != state:
            self.suspected = state
            self.suspected_start = now
            return self.stable_state
        
        elapsed = now - self.suspected_start

        if elapsed >= self.hold_time.get(state, 0.6):
            self.stable_state = state
            self.suspected = None
            self.suspected_start = None

        return self.stable_state
    
def format_time(seconds):
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds & 3600) // 60
    seconds = seconds % 60

    return f"{hours:02}:{minutes:02}:{seconds:02}"

class App:
    def __init__(self, state_queue, scoring, shutdown):
        self.state_queue = state_queue
        self.scoring = scoring
        self.shutdown = shutdown

        self.root = tk.Tk()
        self.root.title("FocusBar")
        self.root.geometry("420x260")
        self.root.resizable(False, False)

        self.root.potocol("WM_DELETE_WINDOW", self.on_close)

        self.smoother = Smoother()

        self.latest_state = "neutral"
        self.latest_stable = "neutral"

        self.past_sessions = []
        self._build_ui()

        self.root.after(100, self.update_loop)

    def _build_ui(self):
        self.notebook == ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)