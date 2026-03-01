import threading
from queue import Queue

from vision import vision_loop
from scoring import ScoringEngine
from ui import App

#
def main():
    state_queue = Queue(1)
    scoring = ScoringEngine
    running = True

    def stop_flag():
        return not running
    
    vision_thread = threading.Thread(target=vision_loop, args=(state_queue,), kwargs={
            "model_path": "best.pt",
            "cam_index": 1,
            "conf": 0.25,
            "stop_flag": stop_flag
        }, daemon = True)
    
    vision_thread.start()

    def shutdown():
        running["value"] = False

    app = App(state_queue, scoring, shutdown)
    app.run()
    shutdown()
    vision_thread.join(2)


if __name__ == "__main__":
    main()
