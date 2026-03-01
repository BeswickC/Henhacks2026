import cv2
import time
from ultralytics import YOLO
from logic import evaluate_state

model = YOLO("best.pt")

cap = cv2.VideoCapture(1)

scoring = ScoringEngine()
scoring.start_session()

last_print = time.time()
def vision_loop(state_queue, model_path="best.pt", cam_index=1, conf=.25, stop_flag=None):
    model = YOLO(model_path)
    cap = cv2.VideoCapture(cam_index)
    while True:
        ret, frame = cap.read()
        if stop_flag is not None and stop_flag():
            break
        if not ret:
            state_queue.put("error:framereading")
            break


        results = model(frame, conf=conf)
        detections = []

        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                obj_c = float(box.conf[0])
                cls = int(box.cls[0])
                detections.append({
                    "class_id": cls,
                    "confidence": conf,
                    "bbox": [x1, y1, x2, y2]
                })
        state = evaluate_state(detections)

        if state["distracted"]:
            current_state = "distracted"
        elif state["productive"]:
            current_state = "productive"
        else:
            current_state = "neutral"

        while not state_queue.empty():
            state_queue.get()

        state_queue.put(current_state)



        

    cap.release()
