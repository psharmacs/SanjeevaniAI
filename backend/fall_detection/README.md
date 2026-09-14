# Fall Detection System

A real-time, multi-person fall detection system using OpenCV, Ultralytics YOLOv8, and MediaPipe Pose.

## Features
- Real-time webcam input
- Multi-person detection and tracking
- Pose estimation and feature extraction
- Rule-based, time-aware fall detection
- Alert system with cooldown

## Project Structure
```
fall_detection/
├── main.py
├── modules/
│   ├── video_capture.py
│   ├── person_detection.py
│   ├── tracking.py
│   ├── pose_estimation.py
│   ├── feature_extraction.py
│   ├── temporal_buffer.py
│   ├── rule_engine.py
│   ├── alert_system.py
├── models/
│   └── yolov8n.pt
├── utils/
│   └── helpers.py
├── outputs/
│   └── logs.txt
├── requirements.txt
└── README.md
```

## Usage
1. Place `yolov8n.pt` in the `models/` directory.
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python main.py`
