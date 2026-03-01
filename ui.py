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
    minutes = (seconds % 3600) // 60
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


        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        style = ttk.Style(self.root)
        style.theme_use("clam")
        base_layout = style.layout("Horizontal.TProgressbar")
        style.layout("Prod.Horizontal.TProgressbar", base_layout)
        style.layout("Dist.Horizontal.TProgressbar", base_layout)
        style.layout("Neut.Horizontal.TProgressbar", base_layout)

        style.configure(
            "Prod.Horizontal.TProgressbar",
            troughcolor="#e5e7eb",
            background="#22c55e"
        )

        style.configure(
            "Dist.Horizontal.TProgressbar",
            troughcolor="#e5e7eb",
            background="#ef4444"
        )

        style.configure(
            "Neut.Horizontal.TProgressbar",
            troughcolor="#e5e7eb",
            background="#9ca3af"
        )
        self.smoother = Smoother()

        self.latest_state = "neutral"
        self.latest_stable = "neutral"

        self.past_sessions = []

        self._build_ui()
        self.update_lifetime_stats()

        self.root.after(100, self.update_loop)


    def _build_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        self.live_tab = ttk.Frame(self.notebook)
        self.history_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.live_tab, text="Current Session")
        self.notebook.add(self.history_tab, text="Past Sessions")

        self._build_live_tab()
        self._build_history_tab()


    def _build_live_tab(self):
        top = ttk.Frame(self.live_tab, padding=10)
        top.pack(fill="x")

        self.state_label = ttk.Label(top, text="STATE: NEUTRAL", font=("Segoe UI", 12, "bold"))
        self.state_label.pack(anchor="w")

        self.timer_label = ttk.Label(top, text="Time: 00:00:00", font=("Segoe UI", 10))
        self.timer_label.pack(anchor="w", pady=(4, 0))

        bars = ttk.Frame(self.live_tab, padding=10)
        bars.pack(fill="x")

        ttk.Label(bars, text="Productive").grid(row=0, column=0, sticky="w")
        self.pb_productive = ttk.Progressbar(bars, orient="horizontal", length=260, mode="determinate", maximum=100,style="Prod.Horizontal.TProgressbar")
        self.pb_productive.grid(row=0, column=1, padx=8)
        self.lbl_productive = ttk.Label(bars, text="0%")
        self.lbl_productive.grid(row=0, column=2, sticky="e")

        ttk.Label(bars, text="Distracted").grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.pb_distracted = ttk.Progressbar(bars, orient="horizontal", length=260, mode="determinate", maximum=100,style="Dist.Horizontal.TProgressbar")
        self.pb_distracted.grid(row=1, column=1, padx=8, pady=(8, 0))
        self.lbl_distracted = ttk.Label(bars, text="0%")
        self.lbl_distracted.grid(row=1, column=2, sticky="e", pady=(8, 0))

        ttk.Label(bars, text="Neutral").grid(row=2, column=0, sticky="w", pady=(8, 0))
        self.pb_neutral = ttk.Progressbar(bars, orient="horizontal", length=260, mode="determinate", maximum=100, style="Neut.Horizontal.TProgressbar")
        self.pb_neutral.grid(row=2, column=1, padx=8, pady=(8, 0))
        self.lbl_neutral = ttk.Label(bars, text="0%")
        self.lbl_neutral.grid(row=2, column=2, sticky="e", pady=(8, 0))

        buttons = ttk.Frame(self.live_tab, padding=10)
        buttons.pack(fill="x")

        self.btn_start = ttk.Button(buttons, text="Start", command=self.on_start)
        self.btn_pause = ttk.Button(buttons, text="Pause", command=self.on_pause)
        self.btn_resume = ttk.Button(buttons, text="Resume", command=self.on_resume)
        self.btn_restart = ttk.Button(buttons, text="Restart", command=self.on_restart)

        self.btn_start.grid(row=0, column=0, padx=4)
        self.btn_pause.grid(row=0, column=1, padx=4)
        self.btn_resume.grid(row=0, column=2, padx=4)
        self.btn_restart.grid(row=0, column=3, padx=4)


    def _build_history_tab(self):
        frame = ttk.Frame(self.history_tab, padding=10)
        frame.pack(fill="both", expand=True)

        stats = ttk.Frame(frame)
        stats.pack(fill="x", pady=(0, 8))

        self.lifetime_label = ttk.Label(stats, text="Lifetime: 0 sessions", font=("Segoe UI", 10, "bold"))
        self.lifetime_label.grid(row=0, column=0, sticky="w")

        self.lifetime_avg_label = ttk.Label(stats, text="Avg: Prod 0% | Dist 0% | Neut 0%")
        self.lifetime_avg_label.grid(row=1, column=0, sticky="w", pady=(2, 0))

        self.lifetime_time_label = ttk.Label(stats, text="Total time: 00:00:00")
        self.lifetime_time_label.grid(row=2, column=0, sticky="w", pady=(2, 0))

        columns = ("time", "productive", "distracted", "neutral")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=7)

        self.tree.heading("time", text="Duration")
        self.tree.heading("productive", text="Prod %")
        self.tree.heading("distracted", text="Dist %")
        self.tree.heading("neutral", text="Neut %")

        self.tree.column("time", width=90, anchor="center")
        self.tree.column("productive", width=80, anchor="center")
        self.tree.column("distracted", width=80, anchor="center")
        self.tree.column("neutral", width=80, anchor="center")

        self.tree.pack(fill="both", expand=True)


    def update_lifetime_stats(self):
        n = len(self.past_sessions)

        if n == 0:
            self.lifetime_label.config(text="Lifetime: 0 sessions")
            self.lifetime_avg_label.config(text="Avg: Prod 0% | Dist 0% | Neut 0%")
            self.lifetime_time_label.config(text="Total time: 00:00:00")
            return

        total_seconds = 0.0
        prod_seconds = 0.0
        dist_seconds = 0.0
        neut_seconds = 0.0

        for s in self.past_sessions:
            tb = s["time_breakdown"]
            total_seconds += tb["total"]
            prod_seconds += tb["productive"]
            dist_seconds += tb["distracted"]
            neut_seconds += tb["neutral"]

        if total_seconds <= 0:
            prod_pct = 0
            dist_pct = 0
            neut_pct = 0
        else:
            prod_pct = int((prod_seconds / total_seconds) * 100)
            dist_pct = int((dist_seconds / total_seconds) * 100)
            neut_pct = int((neut_seconds / total_seconds) * 100)

        self.lifetime_label.config(text=f"Lifetime: {n} sessions")
        self.lifetime_avg_label.config(text=f"Avg: Prod {prod_pct}% | Dist {dist_pct}% | Neut {neut_pct}%")
        self.lifetime_time_label.config(text=f"Total time: {format_time(total_seconds)}")


    def on_start(self):
        self.scoring.start_session()


    def on_pause(self):
        self.scoring.pause_session(self.latest_stable)


    def on_resume(self):
        self.scoring.resume_session()


    def on_restart(self):
        summary = self.scoring.end_session(self.latest_stable)
        self.past_sessions.append(summary)

        self.tree.insert(
            "",
            "end",
            values=(
                format_time(summary["time_breakdown"]["total"]),
                int(summary["percentages"]["productive"]),
                int(summary["percentages"]["distracted"]),
                int(summary["percentages"]["neutral"]),
            )
        )

        self.update_lifetime_stats()
        self.scoring.start_session()


    def update_loop(self):
        while not self.state_queue.empty():
            self.latest_state = self.state_queue.get()

        if isinstance(self.latest_state, str) and self.latest_state.startswith("error:"):
            self.latest_state = "neutral"

        self.latest_stable = self.smoother.update(self.latest_state)

        if self.scoring.is_running():
            self.scoring.update_time(self.latest_stable)

        perc = self.scoring.get_percentages()

        self.pb_productive["value"] = perc["productive"]
        self.pb_distracted["value"] = perc["distracted"]
        self.pb_neutral["value"] = perc["neutral"]

        self.lbl_productive.config(text=f"{int(perc['productive'])}%")
        self.lbl_distracted.config(text=f"{int(perc['distracted'])}%")
        self.lbl_neutral.config(text=f"{int(perc['neutral'])}%")

        self.state_label.config(text=f"STATE: {self.latest_stable.upper()}")

        duration = self.scoring.get_session_duration(self.latest_stable)
        self.timer_label.config(text=f"Time: {format_time(duration)}")

        self.root.after(100, self.update_loop)


    def on_close(self):
        self.shutdown()
        self.root.destroy()


    def run(self):
        self.root.mainloop()