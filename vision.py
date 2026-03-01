import cv2
from ultralytics import YOLO
from logic import evaluate_state
from queue import Empty


def vision_loop(state_queue, model_path="best.pt", cam_index=1, conf=.25, stop_flag=None, show_preview=True):
    model = YOLO(model_path)
    cap = cv2.VideoCapture(cam_index)

    if not cap.isOpened():
        state_queue.put("error:camera_not_opened")
        return

    while True:
        if stop_flag is not None and stop_flag():
            break

        ret, frame = cap.read()
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
                    "confidence": obj_c,
                    "bbox": [x1, y1, x2, y2]
                })

                if show_preview:
                    label = model.names.get(cls, str(cls))
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, f"{label} {obj_c:.2f}",
                                (x1, max(20, y1 - 10)),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.5,
                                (0, 255, 0), 2)

        state = evaluate_state(detections)

        if state["distracted"]:
            current_state = "distracted"
        elif state["productive"]:
            current_state = "productive"
        else:
            current_state = "neutral"

        try:
            while True:
                state_queue.get_nowait()
        except Empty:
            pass

        state_queue.put(current_state)

        if show_preview:
            cv2.putText(frame, f"STATE: {current_state.upper()}",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.9,
                        (255, 255, 255), 2)

            cv2.imshow("FocusBar - Vision", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC closes preview AND stops vision loop
                break
            if key == ord('q'):  # Q just hides preview window
                cv2.destroyWindow("FocusBar - Vision")
                show_preview = False

    cap.release()
    cv2.destroyAllWindows()