import cv2
import time
from ultralytics import YOLO
from logic import evaluate_state
from scoring import ScoringEngine


model = YOLO("best.pt")

cap = cv2.VideoCapture(1)

scoring = ScoringEngine()
scoring.start_session()

last_print = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)

    detections = []

    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            label = model.names[cls]

            detections.append({
                "class_id": cls,
                "confidence": conf,
                "bbox": [x1, y1, x2, y2]
            })

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
            cv2.putText(frame, f"{label} {conf:.2f}",
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0,255,0), 2)

    state = evaluate_state(detections)

    if state["distracted"]:
        current_state = "distracted"
    elif state["productive"]:
        current_state = "productive"
    else:
        current_state = "neutral"

    scoring.update_time(current_state)

    if time.time() - last_print >= 1.0:
        print("state:", current_state, "percents:", scoring.get_percentages())
        last_print = time.time()

    cv2.putText(frame, f"STATE: {current_state.upper()}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255), 2)

    cv2.imshow("YOLO Detection", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()