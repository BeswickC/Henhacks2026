def intersects(boxA, boxB):
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    if xA < xB and yA < yB:
        return True
    return False


def evaluate_state(detections):
    pen_boxes = []
    notebook_boxes = []
    cube_detected = False
    phone_detected = False

    for det in detections:
        cls = det["class_id"]
        bbox = det["bbox"]

        if cls == 2:
            pen_boxes.append(bbox)
        elif cls == 1:
            notebook_boxes.append(bbox)
        elif cls == 0:
            cube_detected = True
        elif cls == 3:
            phone_detected = True

    pen_touching_notebook = False

    for pen in pen_boxes:
        for notebook in notebook_boxes:
            if intersects(pen, notebook):
                pen_touching_notebook = True
                break

    if phone_detected or cube_detected:
        state = {
            "productive": False,
            "distracted": True,
            "neutral": False
        }
    elif pen_touching_notebook:
        state = {
            "productive": True,
            "distracted": False,
            "neutral": False
        }
    else:
        state = {
            "productive": False,
            "distracted": False,
            "neutral": True
        }
    return state