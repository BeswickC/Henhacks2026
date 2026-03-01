FocusBar- Real-Time Student Focus Tracker
--------------------------------------------------------------------------------------
Focus bar is a productivity tracking tool aimed to assist students in more efficient 
studying by giving them live statiscs about how productive they are while studying. 
It uses a webcam and computer vision to estimate if the student is productive, 
distracted, or in a neutral state during their study session, displaying the feedback
through a Windows style widget.
--------------------------------------------------------------------------------------
Features-
- Real-time vision analysis using a custom YOLO model
- Detects productive actions(ex. Pen interacting with notebook)
- Detects distracting actions(ex. Using phone, doing rubiks cube)
- Accurate time based scoring
- Widget with live data and statistics
- History tab to view previous sessions and a cumulative averages
 --------------------------------------------------------------------------------------
 How It Works
 1. Vision (vison.py)
    - Captures webcam frames using OpenCv and run Yolo object detection
    - Gets the bounding boxes and class IDs of objects
    - Sends a string of the state of the user
 2. Logic (logic.py)
    - Based on deteecteed objects, it decides the focus state
    - Could be productive, distracted, neutral
 3. Scoring (scoring.py)
    - Tracks the amount of time in each state
    -  has functions that start, pause, resume, and restart the time
 4. UI (ui.py)
    - Is responsible for live progress bars
    - Has start, pause, resume, restart controls
 5. Main thread (main.py)
    - Launches the vision seperatly from the UI
    - Controls threading 
