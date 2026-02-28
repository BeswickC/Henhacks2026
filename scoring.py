import time

class ScoringEngine:

    def __init__(self):

        self.productive_time = 0.0
        self.distracted_time = 0.0
        self.neutral_time = 0.0

        self.last_update_time = None

        self._is_running = False


    def start_session(self):
        self.productive_time = 0.0
        self.distracted_time = 0.0
        self.neutral_time = 0.0
        self.last_update_time = time.time()
        self._is_running = True


    def pause_session(self, current_state):
        if not self._is_running:
            return
        self.update_time(current_state)
        self._is_running = False


    def resume_session(self):
        if not self._is_running:
            self.last_update_time = time.time()
            self._is_running = True
    

    def end_session(self, current_state):
        if self._is_running:
            self.pause_session(current_state)

        return {
            "time_breakdown": self.get_time_breakdown(),
            "percentages": self.get_percentages()
        }


    def update_time(self, current_state):

        if not self._is_running or self.last_update_time is None:
            return

        current_time = time.time()
        elapsed_time = current_time - self.last_update_time

        if current_state == "productive":
            self.productive_time += elapsed_time
        elif current_state == "distracted":
            self.distracted_time += elapsed_time
        elif current_state == "neutral":
            self.neutral_time += elapsed_time

        self.last_update_time = current_time


    def get_percentages(self):
        total = self.productive_time + self.distracted_time + self.neutral_time

        if total == 0:
            return {
                "productive": 0,
                "distracted": 0,
                "neutral": 0
            }
        
        return {
            "productive": (self.productive_time / total) * 100,
            "distracted": (self.distracted_time / total) * 100,
            "neutral": (self.neutral_time / total) * 100
        }


    def get_time_breakdown(self):
        total_time = self.productive_time + self.distracted_time + self.neutral_time
        
        return {
            "productive": self.productive_time,
            "distracted": self.distracted_time,
            "neutral": self.neutral_time,
            "total": total_time
        }


    def is_running(self):
        return self._is_running


    def get_session_duration(self, current_state=None):
        if self._is_running and current_state is not None:
            self.update_time(current_state)

        return (
            self.productive_time +
            self.distracted_time +
            self.neutral_time
        )