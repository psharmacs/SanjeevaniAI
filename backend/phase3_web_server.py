import sys
import cv2
import time
import threading
import json
import asyncio
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

latest_frame = None
latest_state_json = '{"overall_status": "SAFE", "fps": 0, "persons": [], "logs": []}'
clients = set()
privacy_mode = False

class PrivacyRequest(BaseModel):
    enabled: bool

@app.post("/api/privacy")
def toggle_privacy(req: PrivacyRequest):
    global privacy_mode, latest_state_json
    privacy_mode = req.enabled
    
    if privacy_mode:
        latest_state_json = json.dumps({
            "overall_status": "PRIVACY_MODE", 
            "fps": 0, 
            "persons": [], 
            "logs": ["Privacy mode activated."]
        })
    return {"status": "success", "privacy_mode": privacy_mode}

# We will intercept cv2.imshow and cv2.waitKey!
original_imshow = cv2.imshow
original_waitkey = cv2.waitKey

def mock_imshow(winname, mat):
    global latest_frame, latest_state_json, privacy_mode
    ret, buffer = cv2.imencode('.jpg', mat)
    if ret:
        latest_frame = buffer.tobytes()
        
    # Send a dummy JSON so the React frontend stays "Online"
    if not privacy_mode:
        latest_state_json = json.dumps({
            "overall_status": "SAFE", 
            "fps": 15, 
            "persons": [], 
            "logs": ["Running Phase 3 Test script..."]
        })

def mock_waitkey(delay):
    # Never return 'q' (which is 113), just return -1 so the loop never breaks
    time.sleep(delay / 1000.0 if delay > 0 else 0.01)
    return -1

cv2.imshow = mock_imshow
cv2.waitKey = mock_waitkey
cv2.namedWindow = lambda *args, **kwargs: None
cv2.setWindowProperty = lambda *args, **kwargs: None

def run_phase3():
    # We execute their 2500-line script exactly as-is, but in our mocked environment!
    print("[SERVER] Starting phase3_test.py wrapper...")
    root_dir = "E:/Sanjeevani_AI2/SanjeevaniAI"
    os.chdir(root_dir)
    if "fall_detection" not in sys.path:
        sys.path.append(os.path.join(root_dir, "fall_detection"))
    
    with open("fall_detection/phase3_test.py", "r", encoding="utf-8") as f:
        code = f.read()
    
    env = globals().copy()
    
    try:
        exec(code, env)
    except Exception as e:
        print(f"[SERVER] Error running phase3_test.py: {e}")

@app.on_event("startup")
def startup():
    t = threading.Thread(target=run_phase3, daemon=True)
    t.start()

def generate_frames():
    global latest_frame
    while True:
        if latest_frame is not None:
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + latest_frame + b'\r\n')
        time.sleep(0.05)

@app.get("/video_feed")
def video_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)
    try:
        while True:
            await websocket.send_text(latest_state_json)
            await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        clients.remove(websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
