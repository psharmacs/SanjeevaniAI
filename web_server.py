import sys
import cv2
import numpy as np
import os
import time
import json
import asyncio
import threading
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Append fall_detection to sys.path to resolve internal modules correctly
sys.path.append(os.path.join(os.path.dirname(__file__), "fall_detection"))

from modules.video_capture      import VideoCapture
from modules.person_detection   import PersonDetector
from modules.tracking           import CentroidTracker
from modules.pose_estimation    import PoseEstimator
from modules.feature_extraction import FeatureExtractor
from modules.temporal_buffer    import TemporalBuffer
from modules.rule_engine        import RuleEngine, FallState
from modules.alert_system       import AlertSystem
from modules.voice_assistant    import VoiceAssistant
from utils.helpers              import draw_bbox

MODEL_PATH = "fall_detection/models/yolov8n.pt"

# Global states
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

latest_frame = None
latest_state_json = "{}"
clients = set()
running = True
privacy_mode = False

from pydantic import BaseModel
class PrivacyRequest(BaseModel):
    enabled: bool

@app.post("/api/privacy")
async def toggle_privacy(req: PrivacyRequest):
    global privacy_mode
    privacy_mode = req.enabled
    return {"status": "success", "privacy_mode": privacy_mode}

# Original color palette
COLOR_STANDING      = (0,   255,   0)
COLOR_SITTING       = (0,   255, 255)
COLOR_LYING         = (0,   165, 255)
COLOR_LYING_MOVING  = (255, 255,   0)
COLOR_PREFALL       = (0,   140, 255)
COLOR_FALLING       = (0,    80, 255)
COLOR_FALL          = (0,     0, 255)
COLOR_RECOVERY      = (255, 200,   0)
COLOR_DANGER        = (0,     0, 200)
COLOR_NO_POSE       = (128, 128, 128)

def _state_color(state, posture, is_lying_moving, danger):
    if danger:                                 return COLOR_DANGER
    if state == FallState.FALL_CONFIRMED:      return COLOR_FALL
    if state == FallState.FALLING:             return COLOR_FALLING
    if state == FallState.PRE_FALL:            return COLOR_PREFALL
    if state == FallState.RECOVERY:            return COLOR_RECOVERY
    if is_lying_moving:                        return COLOR_LYING_MOVING
    if posture == "Lying":                     return COLOR_LYING
    if posture == "Sitting":                   return COLOR_SITTING
    return COLOR_STANDING

def _draw_risk_bar(frame, x, y, risk_score, width=80, height=8):
    cv2.rectangle(frame, (x, y), (x + width, y + height), (50, 50, 50), -1)
    bar_w = int(width * risk_score)
    r     = int(255 * risk_score)
    g     = int(255 * (1.0 - risk_score))
    cv2.rectangle(frame, (x, y), (x + bar_w, y + height), (0, g, r), -1)
    cv2.rectangle(frame, (x, y), (x + width, y + height), (200, 200, 200), 1)

def _build_label(object_id, state, posture, is_lying_moving, fall_confirmed, danger):
    if danger:
        return f"ID:{object_id} DANGER - lying still"
    if fall_confirmed or state == FallState.FALL_CONFIRMED:
        return f"ID:{object_id} FALL DETECTED"
    if state == FallState.FALLING:
        return f"ID:{object_id} FALLING!"
    if state == FallState.PRE_FALL:
        return f"ID:{object_id} Pre-Fall"
    if state == FallState.RECOVERY:
        return f"ID:{object_id} Recovery"
    if is_lying_moving:
        return f"ID:{object_id} Lying (moving)"
    if posture == "Lying":
        return f"ID:{object_id} Lying"
    if posture == "Sitting":
        return f"ID:{object_id} Sitting"
    return f"ID:{object_id} Standing"

def run_ai_pipeline():
    global latest_frame, latest_state_json, running
    
    os.makedirs("output", exist_ok=True)
    RECORDING_DIR = "output/recording"
    os.makedirs(RECORDING_DIR, exist_ok=True)

    video             = VideoCapture()
    detector          = PersonDetector(MODEL_PATH)
    tracker           = CentroidTracker()
    pose_estimator    = PoseEstimator()
    feature_extractor = FeatureExtractor()
    buffer            = TemporalBuffer(buffer_time=6.0)
    rule_engine       = RuleEngine()
    alert_system      = AlertSystem()

    va = VoiceAssistant(wake_word="sanjeevani", cooldown_sec=10)
    va.start()
    
    from collections import deque
    frame_buffer = deque(maxlen=150) # 10 second rolling buffer
    recording_incident = False
    post_fall_frames_left = 0
    incident_frames = []

    prev_states = {}
    voice_overlay_until = 0.0

    while running:
        if privacy_mode:
            state_payload = {
                "fps": 0.0,
                "mic_status": va.available,
                "persons": [],
                "timestamp": time.time(),
                "overall_status": "PRIVACY_MODE",
                "logs": alert_system.get_log()[-10:]
            }
            latest_state_json = json.dumps(state_payload)
            # Generate black frame
            black_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(black_frame, "PRIVACY MODE ENABLED", (120, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 100, 100), 2)
            ret, buffer_img = cv2.imencode('.jpg', black_frame)
            if ret:
                latest_frame = buffer_img.tobytes()
            time.sleep(0.5)
            # Empty out the video buffer so it doesn't queue old frames
            video.read() 
            continue

        ret, frame, fps = video.read()
        if not ret:
            print("Video end.")
            time.sleep(0.1)
            continue

        display = frame.copy()
        frame_h, frame_w = frame.shape[:2]

        pose_data = pose_estimator.detect_full_frame(frame)
        if pose_data is not None:
            pose_estimator.draw_pose(display, pose_data["all_landmarks"])

        boxes = detector.detect(frame)
        tracked = tracker.update(boxes)

        state_payload = {
            "fps": round(fps, 1),
            "mic_status": va.available,
            "persons": [],
            "timestamp": time.time(),
            "overall_status": "SAFE",
            "logs": alert_system.get_log()[-10:] # last 10 events
        }

        any_danger = False
        any_fall = False

        for object_id, obj in tracked.items():
            bbox = obj["bbox"]
            pose = pose_estimator.get_pose_for_bbox(pose_data, bbox) if pose_data is not None else None

            if pose is None:
                # We will still pass pose=None to feature_extractor to allow bounding-box fallback
                cv2.rectangle(display, (bbox[0], bbox[1]), (bbox[2], bbox[3]), COLOR_NO_POSE, 1)
                cv2.putText(display, f"ID:{object_id} (inferring pose)", (bbox[0], bbox[1] - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.45, COLOR_NO_POSE, 1)

            features = feature_extractor.extract(object_id, bbox, pose)
            if features is None:
                continue

            buffer.update(object_id, features)
            buf = buffer.get(object_id)

            result          = rule_engine.process(object_id, buf, feature_extractor=feature_extractor)
            state           = result["state"]
            fall_confirmed  = result["fall_confirmed"]
            risk_score      = result["risk_score"]
            is_lying_moving = result["is_lying_moving"]
            danger          = result["danger"]

            if danger: any_danger = True
            if fall_confirmed: any_fall = True

            prev_st = prev_states.get(object_id)
            if prev_st == FallState.FALL_CONFIRMED and state == FallState.RECOVERY:
                alert_system.notify_recovery(object_id)
            prev_states[object_id] = state

            if fall_confirmed:
                alert_system.alert(object_id, risk_score=risk_score)
            if danger:
                alert_system.notify_danger(object_id)

            posture = features["posture"]
            color   = _state_color(state, posture, is_lying_moving, danger)
            label   = _build_label(object_id, state, posture, is_lying_moving, fall_confirmed, danger)

            draw_bbox(display, bbox, object_id, fall_confirmed, color=color)
            cv2.putText(display, label, (bbox[0], bbox[1] - 28), cv2.FONT_HERSHEY_SIMPLEX, 0.65, color, 2)
            ang_vel = features.get("angular_velocity", 0.0)
            cv2.putText(display, f"{ang_vel:.0f} deg/s | {state.value}", (bbox[0], bbox[1] - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.42, color, 1)
            _draw_risk_bar(display, bbox[0], bbox[3] + 4, risk_score, width=bbox[2] - bbox[0])

            state_payload["persons"].append({
                "id": object_id,
                "bbox": [int(x) for x in bbox],
                "posture": posture,
                "state": state.value,
                "risk_score": risk_score,
                "danger": danger,
                "is_lying_moving": is_lying_moving,
                "angular_velocity": ang_vel,
                "fall_confirmed": fall_confirmed
            })

        if va.available:
            voice_triggered, voice_cmd = va.consume_emergency()
            if voice_triggered:
                alert_system.notify_voice_emergency(-1, voice_cmd)
                voice_overlay_until = time.time() + 4.0

        if time.time() < voice_overlay_until:
            cv2.putText(display, "VOICE EMERGENCY DETECTED", (frame_w // 2 - 280, frame_h // 2), cv2.FONT_HERSHEY_SIMPLEX, 1.2, COLOR_FALL, 3)
            state_payload["voice_emergency"] = True
            any_danger = True
        else:
            state_payload["voice_emergency"] = False

        if any_danger:
            state_payload["overall_status"] = "DANGER"
        elif any_fall:
            state_payload["overall_status"] = "EMERGENCY"
        elif any(p.get("state") in ["PRE_FALL", "FALLING"] for p in state_payload["persons"]):
            state_payload["overall_status"] = "ANALYSING"

        latest_state_json = json.dumps(state_payload)
        
        # JPEG encoding
        ret, buffer_img = cv2.imencode('.jpg', display)
        if ret:
            latest_frame = buffer_img.tobytes()

        # Rolling Buffer Video Recording
        frame_buffer.append(display.copy())
        
        # Start recording if an emergency/danger is detected
        if state_payload["overall_status"] in ["EMERGENCY", "DANGER"] and not recording_incident:
            recording_incident = True
            post_fall_frames_left = 150 # Capture 10 seconds (approx 150 frames) after the event
            incident_frames = list(frame_buffer)
            
        if recording_incident:
            incident_frames.append(display.copy())
            post_fall_frames_left -= 1
            
            if post_fall_frames_left <= 0:
                # Save to disk
                ts = datetime.now().strftime("%I_%M_%S_%p")
                video_filename = os.path.join(RECORDING_DIR, f"Incident_{ts}.mp4")
                h, w = display.shape[:2]
                # Use mp4v codec
                out = cv2.VideoWriter(video_filename, cv2.VideoWriter_fourcc(*'mp4v'), 15.0, (w, h))
                for f in incident_frames:
                    out.write(f)
                out.release()
                print(f"[REC] Saved incident video to {video_filename}")
                
                recording_incident = False
                incident_frames = []

    va.stop()
    video.release()

@app.on_event("startup")
async def startup_event():
    # Start AI loop in background thread
    t = threading.Thread(target=run_ai_pipeline, daemon=True)
    t.start()

@app.on_event("shutdown")
def shutdown_event():
    global running
    running = False

def generate_frames():
    global latest_frame
    while True:
        if latest_frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + latest_frame + b'\r\n')
        time.sleep(0.05) # ~20 fps

@app.get("/video_feed")
async def video_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)
    try:
        while True:
            await websocket.send_text(latest_state_json)
            await asyncio.sleep(0.1) # 10 Hz updates
    except WebSocketDisconnect:
        clients.remove(websocket)

@app.get("/api/logs")
def get_logs():
    logs = []
    log_file = "output/logs.txt"
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines[-50:]: # last 50
                logs.append(line.strip())
    return {"logs": logs}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
