from datetime import datetime
"""
main.py
=======
Fall Detection Pipeline — main entry point.

CHANGES IN THIS VERSION
-----------------------
1. DANGER detection: if person is Lying AND not moving for >= 5 s,
   prints "⚠ DANGER" to terminal and writes to output/logs.txt.

2. Posture display is now driven purely by feature_extractor posture
   classification (Standing / Sitting / Lying), not inferred from
   state machine state. This makes the posture label always correct.

3. is_lying_moving flag shown as "Lying (moving)" with cyan box.
   Distinct from static Lying (orange) and DANGER (red flashing label).

4. Danger label shown in red above the bounding box when danger=True.

5. FALL RECORDING:
   When fall is confirmed, recording starts automatically and saves
   the video inside output/recording/.

6. VOICE ASSISTANT — Sanjeevani:
   Runs in a background thread. Listens for wake word "sanjeevani"
   followed by an emergency keyword (help, emergency, injured, etc.).
   On detection, fires alert_system.notify_voice_emergency(-1, voice_cmd)
   and writes to output/logs.txt. Does NOT affect camera, YOLO, or MediaPipe
   in any way. If microphone or libraries are unavailable, pipeline continues
   normally.

7. VOICE EMERGENCY OVERLAY:
   "VOICE EMERGENCY DETECTED" text is shown for 3–5 seconds (not just 1 frame)
   so the operator has time to read it. Controlled by voice_overlay_until
   timestamp — the overlay is drawn on every frame until the timer expires.

8. MIC STATUS OVERLAY:
   "MIC: ON"  (green)  — voice assistant started successfully.
   "MIC: OFF" (grey)   — sounddevice/SpeechRecognition unavailable or mic error.

9. EMERGENCY RECORDING TRIGGERS:
   Recording starts when:
       fall_confirmed OR danger OR voice_emergency

COLOR REFERENCE
---------------
Green   = Standing
Yellow  = Sitting
Orange  = Lying (static / resting)
Cyan    = Lying (moving — limb movement while already on ground)
Amber   = Pre-Fall
Red     = Fall Confirmed / DANGER
"""

import cv2
import numpy as np
import os
import time
from pathlib import Path

from modules.video_capture      import VideoCapture
from modules.person_detection   import PersonDetector
from modules.tracking           import CentroidTracker
from modules.pose_estimation    import PoseEstimator
from modules.feature_extraction import FeatureExtractor
from modules.temporal_buffer    import TemporalBuffer
from modules.rule_engine        import RuleEngine, FallState
from modules.alert_system       import AlertSystem
from modules.voice_assistant    import VoiceAssistant          # ← INTEGRATION 1
from utils.helpers              import draw_bbox

MODEL_PATH = "fall_detection/models/yolov8n.pt"

# Ensure output directory exists at startup
os.makedirs("output", exist_ok=True)

# ── Recording directory ─────────────────────────────────────────────
RECORDING_DIR = "output/recording"
os.makedirs(RECORDING_DIR, exist_ok=True)

# Recording duration after confirmed fall / danger / voice emergency
RECORD_DURATION = 15   # seconds

# ── Voice overlay duration ───────────────────────────────────────────
# How many seconds the "VOICE EMERGENCY DETECTED" text stays visible on screen.
# Previously this was 1 frame only; now it persists so the operator can read it.
VOICE_OVERLAY_SEC = 4   # seconds (adjust between 3–5 as preferred)

# ── Colour palette (BGR) ─────────────────────────────────────────────
COLOR_STANDING      = (0,   255,   0)    # green
COLOR_SITTING       = (0,   255, 255)    # yellow
COLOR_LYING         = (0,   165, 255)    # orange
COLOR_LYING_MOVING  = (255, 255,   0)    # cyan
COLOR_PREFALL       = (0,   140, 255)    # amber
COLOR_FALLING       = (0,    80, 255)    # dark orange
COLOR_FALL          = (0,     0, 255)    # red
COLOR_RECOVERY      = (255, 200,   0)    # teal
COLOR_DANGER        = (0,     0, 200)    # dark red
COLOR_NO_POSE       = (128, 128, 128)    # grey


def _state_color(state, posture, is_lying_moving, danger):
    """Map FSM state + posture + flags to BGR colour."""
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
    """Horizontal risk bar: green (0.0) → red (1.0)."""
    cv2.rectangle(frame, (x, y), (x + width, y + height), (50, 50, 50), -1)
    bar_w = int(width * risk_score)
    r     = int(255 * risk_score)
    g     = int(255 * (1.0 - risk_score))
    cv2.rectangle(frame, (x, y), (x + bar_w, y + height), (0, g, r), -1)
    cv2.rectangle(frame, (x, y), (x + width, y + height), (200, 200, 200), 1)


def _build_label(object_id, state, posture, is_lying_moving,
                 fall_confirmed, danger):
    """
    Compose the display label for a tracked person.

    Priority (highest first):
        1. DANGER — person lying still >= 5 s
        2. FALL DETECTED — confirmed fall
        3. FALLING! — active fall motion
        4. Pre-Fall — pre-fall state
        5. Recovery
        6. Lying (moving) — lying but moving limbs
        7. Lying — stationary lying
        8. Sitting
        9. Standing  (default)
    """
    if danger:
        return f"ID:{object_id} ⚠ DANGER — lying still"
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


def _recording_timestamp():
    """Return a readable local date/time for recording terminal logs."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _start_recording_if_needed(recording, video_writer, object_id,
                               frame_w, frame_h, event_type):
    """
    Start recording if recording is not already active.

    Used for:
        FALL   → fall_confirmed
        DANGER → lying still danger
        VOICE  → Sanjeevani voice emergency

    Returns
    -------
    recording, video_writer, record_start_time, current_recording_path

    If recording is already active:
        record_start_time and current_recording_path return as None
        so caller keeps old values unchanged.
    """
    if recording:
        return recording, video_writer, None, None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Keep filename readable and safe.
    safe_object_id = str(object_id).replace("-", "minus")
    event_name = event_type.lower()

    recording_path = os.path.join(
        RECORDING_DIR,
        f"{event_name}_person_{safe_object_id}_{timestamp}.avi"
    )

    # Using .avi + XVID because it is more reliable
    # on Windows OpenCV than .mp4 + mp4v.
    fourcc = cv2.VideoWriter_fourcc(*"XVID")

    video_writer = cv2.VideoWriter(
        recording_path,
        fourcc,
        20.0,
        (frame_w, frame_h)
    )

    # Check if VideoWriter opened successfully
    if not video_writer.isOpened():
        print("[ERROR] VideoWriter failed to open")
        video_writer = None
        return False, None, None, None

    print(f"[RECORDING] Started ({event_type}): {recording_path}")

    return True, video_writer, time.time(), recording_path


def main():
    video             = VideoCapture()
    detector          = PersonDetector(MODEL_PATH)
    tracker           = CentroidTracker()
    pose_estimator    = PoseEstimator()
    feature_extractor = FeatureExtractor()
    buffer            = TemporalBuffer(buffer_time=6.0)   # 6 s covers DANGER window
    rule_engine       = RuleEngine()
    alert_system      = AlertSystem()

    # ── INTEGRATION 2: create and start voice assistant ──────────────
    # Started BEFORE the camera loop so microphone calibration (~1 s)
    # happens during pipeline warm-up, not during live detection.
    # If libraries or microphone are missing, va.available = False and
    # the pipeline continues completely unaffected.
    va = VoiceAssistant(wake_word="sanjeevani", cooldown_sec=10)
    va.start()
    # ─────────────────────────────────────────────────────────────────

    # ── Fullscreen window ───────────────────────────────────────────
    cv2.namedWindow("Fall Detection", cv2.WINDOW_NORMAL)

    cv2.setWindowProperty(
        "Fall Detection",
        cv2.WND_PROP_FULLSCREEN,
        cv2.WINDOW_FULLSCREEN
    )

    prev_states = {}   # track state transitions for recovery notification

    # ── Recording state ─────────────────────────────────────────────
    recording = False
    video_writer = None
    record_start_time = None
    current_recording_path = None

    # Track what caused the current recording.
    # DANGER recordings stop when the person moves/changes posture/disappears.
    recording_event_type = None
    recording_object_id = None

    # One recording is allowed per continuous DANGER event.
    danger_event_recorded = False

    # ── Voice overlay state ──────────────────────────────────────────
    # voice_overlay_until stores the time.time() value until which the
    # "VOICE EMERGENCY DETECTED" overlay should remain on screen.
    # Initialised to 0 so no overlay is drawn at startup.
    # When a voice emergency is consumed, this is set to:
    #     time.time() + VOICE_OVERLAY_SEC
    # Every frame checks: if time.time() < voice_overlay_until → draw overlay.
    voice_overlay_until = 0.0

    while True:
        ret, frame, fps = video.read()
        if not ret:
            break

        display = frame.copy()

        # DANGER recording is latched after it starts.
        # We do NOT require `danger=True` on every frame because the
        # RuleEngine's 5-second danger window can fluctuate.
        danger_recording_should_stop = False
        danger_recording_stop_reason = None

        # Frame size used for saving recording
        frame_h, frame_w = frame.shape[:2]

        # ── 1. MediaPipe pose — once per frame ────────────────────────
        pose_data = pose_estimator.detect_full_frame(frame)
        if pose_data is not None:
            pose_estimator.draw_pose(display, pose_data["all_landmarks"])

        # ── 2. YOLO detection ──────────────────────────────────────────
        boxes = detector.detect(frame)

        # ── 3. Centroid tracker ────────────────────────────────────────
        tracked = tracker.update(boxes)

        # ── 4. Per-person processing ───────────────────────────────────
        for object_id, obj in tracked.items():
            bbox = obj["bbox"]

            pose = (
                pose_estimator.get_pose_for_bbox(pose_data, bbox)
                if pose_data is not None else None
            )

            # No pose detected → draw grey box and skip
            if pose is None:
                cv2.rectangle(display,
                              (bbox[0], bbox[1]), (bbox[2], bbox[3]),
                              COLOR_NO_POSE, 1)
                cv2.putText(display, f"ID:{object_id} (no pose)",
                            (bbox[0], bbox[1] - 8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, COLOR_NO_POSE, 1)
                continue

            features = feature_extractor.extract(object_id, bbox, pose)
            if features is None:
                continue

            buffer.update(object_id, features)
            buf = buffer.get(object_id)

            # ── Run state machine ─────────────────────────────────────
            result          = rule_engine.process(
                object_id, buf, feature_extractor=feature_extractor
            )
            state           = result["state"]
            fall_confirmed  = result["fall_confirmed"]
            risk_score      = result["risk_score"]
            is_lying_moving = result["is_lying_moving"]
            danger          = result["danger"]

            # ── DANGER recording control ──────────────────────────────
            # Once DANGER recording starts, do not use the RuleEngine's
            # `danger` flag to keep it alive. That flag is based on the
            # rolling 5-second danger window and can become False even
            # while the person is still lying.
            #
            # Instead, stop only when:
            #   1. the tracked person disappears,
            #   2. posture is no longer Lying, or
            #   3. clear movement is detected.
            if (
                recording
                and recording_event_type == "DANGER"
                and object_id == recording_object_id
            ):
                current_posture = features.get("posture", "")
                current_movement = features.get("movement", 0)

                if current_posture != "Lying":
                    danger_recording_should_stop = True
                    danger_recording_stop_reason = (
                        "person changed posture"
                    )
                elif current_movement >= 8:
                    danger_recording_should_stop = True
                    danger_recording_stop_reason = (
                        f"person moved (movement={current_movement:.1f}px)"
                    )

            # ── Recovery notification ─────────────────────────────────
            prev_st = prev_states.get(object_id)
            if (prev_st == FallState.FALL_CONFIRMED
                    and state == FallState.RECOVERY):
                alert_system.notify_recovery(object_id)
            prev_states[object_id] = state

            # ── Fall alert ────────────────────────────────────────────
            if fall_confirmed:
                alert_system.alert(object_id, risk_score=risk_score)

                # ── Start recording on confirmed fall ───────────────
                recording, video_writer, new_start_time, new_path = (
                    _start_recording_if_needed(
                        recording,
                        video_writer,
                        object_id,
                        frame_w,
                        frame_h,
                        "FALL"
                    )
                )

                if new_start_time is not None:
                    record_start_time = new_start_time
                    current_recording_path = new_path
                    recording_event_type = "FALL"
                    recording_object_id = object_id

            # ── DANGER alert ──────────────────────────────────────────
            # Fires when person is Lying and not moving for >= 5 s.
            # alert_system.notify_danger() handles its own cooldown so it
            # won't write hundreds of identical lines per second.
            if danger:
                alert_system.notify_danger(object_id)

                # ── Start only ONE recording for this DANGER event ──
                if not danger_event_recorded:
                    recording, video_writer, new_start_time, new_path = (
                        _start_recording_if_needed(
                            recording,
                            video_writer,
                            object_id,
                            frame_w,
                            frame_h,
                            "DANGER"
                        )
                    )

                    if new_start_time is not None:
                        record_start_time = new_start_time
                        current_recording_path = new_path
                        recording_event_type = "DANGER"
                        recording_object_id = object_id
                        danger_event_recorded = True

            # Reset the one-recording lock only after the current
            # DANGER event has ended. This prevents back-to-back 15-second
            # recordings while the same danger condition remains active.
            if not danger:
                danger_event_recorded = False

            # ── Label ─────────────────────────────────────────────────
            posture = features["posture"]
            color   = _state_color(state, posture, is_lying_moving, danger)
            label   = _build_label(
                object_id, state, posture, is_lying_moving,
                fall_confirmed, danger
            )

            # ── Draw bounding box ─────────────────────────────────────
            draw_bbox(display, bbox, object_id, fall_confirmed, color=color)

            # Main label (posture / state)
            cv2.putText(display, label,
                        (bbox[0], bbox[1] - 28),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, color, 2)

            # Sub-label (angular velocity + state name)
            ang_vel = features.get("angular_velocity", 0.0)
            cv2.putText(display,
                        f"{ang_vel:.0f}°/s | {state.value}",
                        (bbox[0], bbox[1] - 12),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.42, color, 1)

            # Risk bar
            _draw_risk_bar(display,
                           bbox[0], bbox[3] + 4,
                           risk_score, width=bbox[2] - bbox[0])

            cv2.putText(display,
                        f"risk:{risk_score:.2f}",
                        (bbox[0], bbox[3] + 22),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.42, color, 1)

        # ── INTEGRATION 3: poll voice assistant once per frame ────────
        # consume_emergency() is non-blocking — returns instantly.
        # Uses object_id = -1 to distinguish voice triggers from camera
        # detections in the log file (e.g. "Person -1" = voice alert).
        # The check is guarded by va.available so it is completely skipped
        # (zero cost) if the voice assistant failed to start.
        #
        # notify_voice_emergency() is used instead of notify_danger(-1)
        # because:
        #   - Voice emergencies have a different event type ("VOICE_EMERGENCY")
        #     vs camera-detected danger ("DANGER") — makes logs unambiguous.
        #   - notify_voice_emergency() has its own independent cooldown
        #     (_voice_logged) so it never resets camera DANGER cooldowns.
        #   - The terminal message clearly shows the spoken command text.
        if va.available:
            voice_triggered, voice_cmd = va.consume_emergency()
            if voice_triggered:
                # Route through the dedicated voice emergency handler so the
                # log entry, terminal message, and alert_log type are all
                # correctly labelled as VOICE_EMERGENCY.
                alert_system.notify_voice_emergency(-1, voice_cmd)

                # ── Start recording on voice emergency ──────────────
                recording, video_writer, new_start_time, new_path = (
                    _start_recording_if_needed(
                        recording,
                        video_writer,
                        -1,
                        frame_w,
                        frame_h,
                        "VOICE"
                    )
                )

                if new_start_time is not None:
                    record_start_time = new_start_time
                    current_recording_path = new_path
                    recording_event_type = "VOICE"
                    recording_object_id = -1

                # Set the overlay timer so "VOICE EMERGENCY DETECTED" stays
                # visible for VOICE_OVERLAY_SEC seconds (default 4 s).
                # Previously this was drawn for only 1 frame; now it persists
                # so the operator on screen can clearly read the alert.
                voice_overlay_until = time.time() + VOICE_OVERLAY_SEC

        # ── Voice overlay (drawn every frame until timer expires) ─────
        # Checked unconditionally (even if va.available is False) because
        # voice_overlay_until starts at 0.0 and will never be set when
        # the assistant is disabled — so the condition is always False.
        if time.time() < voice_overlay_until:
            cv2.putText(
                display,
                "VOICE EMERGENCY DETECTED",
                (frame_w // 2 - 280, frame_h // 2),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.2,
                COLOR_FALL,
                3,
            )
        # ─────────────────────────────────────────────────────────────

        # ── 5. Overlays ───────────────────────────────────────────────
        cv2.putText(display, f"FPS: {fps:.1f}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

        # ── MIC status overlay (top-right corner) ─────────────────────
        # Shows "MIC: ON" in green if voice assistant started successfully,
        # or "MIC: OFF" in grey if sounddevice/SpeechRecognition is missing
        # or the microphone was not accessible at startup.
        va_status     = "MIC: ON"  if va.available else "MIC: OFF"
        va_status_col = (0, 255, 0) if va.available else (100, 100, 100)
        cv2.putText(
            display,
            va_status,
            (frame_w - 160, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            va_status_col,
            2,
        )

        legends = [
            ("Standing",       COLOR_STANDING),
            ("Sitting",        COLOR_SITTING),
            ("Lying",          COLOR_LYING),
            ("Lying (moving)", COLOR_LYING_MOVING),
            ("Pre-Fall",       COLOR_PREFALL),
            ("Falling",        COLOR_FALLING),
            ("FALL",           COLOR_FALL),
            ("Recovery",       COLOR_RECOVERY),
            ("DANGER",         COLOR_DANGER),
        ]
        for i, (txt, col) in enumerate(legends):
            cv2.putText(display, f"■ {txt}",
                        (10, 60 + i * 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, col, 1)

        # ── Recording writer ─────────────────────────────────────────
        if recording and video_writer is not None:

            # =========================================================
            # DANGER RECORDING
            # =========================================================
            # A DANGER recording continues only while the person who
            # triggered it remains lying and still.
            if recording_event_type == "DANGER":

                # Person disappeared from the tracker.
                if recording_object_id not in tracked:
                    danger_recording_should_stop = True
                    danger_recording_stop_reason = "person disappeared"

                if danger_recording_should_stop:
                    stop_time = _recording_timestamp()
                    incomplete_path = current_recording_path

                    # Finalize the writer first.
                    video_writer.release()
                    video_writer = None
                    recording = False

                    print(
                        f"[RECORDING] STOPPED at {stop_time} — "
                        f"{danger_recording_stop_reason}."
                    )

                    # Do NOT save an incomplete recording.
                    if incomplete_path is not None:
                        try:
                            incomplete_file = Path(incomplete_path)
                            if incomplete_file.exists():
                                incomplete_file.unlink()
                        except Exception as e:
                            print(
                                f"[RECORDING] Could not delete incomplete "
                                f"recording: {e}"
                            )

                    print(
                        "[RECORDING] NOT SAVED — "
                        "15-second duration was not completed."
                    )

                    current_recording_path = None
                    record_start_time = None
                    recording_event_type = None
                    recording_object_id = None

            # =========================================================
            # WRITE FRAME / NORMAL 15-SECOND RECORDING
            # =========================================================
            if recording and video_writer is not None:

                # Show REC indicator and elapsed recording time.
                elapsed_recording = time.time() - record_start_time

                cv2.putText(
                    display,
                    "REC",
                    (frame_w - 150, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    3
                )

                cv2.putText(
                    display,
                    f"{min(elapsed_recording, RECORD_DURATION):04.1f}s / {RECORD_DURATION}s",
                    (frame_w - 260, 68),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (0, 0, 255),
                    2
                )

                # Write current displayed frame into video file
                video_writer.write(display)

                # FALL and VOICE recordings use the normal 15-second
                # duration. DANGER recordings are allowed to stop early
                # when the danger condition ends, but also have the
                # 15-second maximum as a safety limit.
                if time.time() - record_start_time >= RECORD_DURATION:

                    completed_path = current_recording_path
                    completed_event = recording_event_type

                    # 15 seconds are complete, so finalize the video first.
                    video_writer.release()
                    video_writer = None
                    recording = False

                    stop_time = _recording_timestamp()

                    print(
                        f"[RECORDING] STOPPED at {stop_time} — "
                        f"{completed_event} recording reached 15 seconds."
                    )

                    print(
                        f"[RECORDING] SAVED COMPLETELY at {stop_time}: "
                        f"{completed_path}"
                    )

                    current_recording_path = None
                    record_start_time = None
                    recording_event_type = None
                    recording_object_id = None

        cv2.imshow("Fall Detection", display)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # ── Safe recording cleanup ─────────────────────────────────────
    if video_writer is not None:
        incomplete_path = current_recording_path

        video_writer.release()
        video_writer = None
        recording = False

        # Do not leave a partial event recording when the program exits.
        if incomplete_path is not None:
            try:
                incomplete_file = Path(incomplete_path)
                if incomplete_file.exists():
                    incomplete_file.unlink()
                    print(
                        "[RECORDING] NOT SAVED — "
                        "program stopped before 15-second duration."
                    )
            except Exception as e:
                print(
                    f"[RECORDING] Could not delete incomplete "
                    f"recording: {e}"
                )

    # ── INTEGRATION 4: stop voice assistant cleanly on exit ──────────
    # Called after the camera loop exits (q pressed or camera lost).
    # Safe to call even if va never started (va.available = False).
    va.stop()
    # ─────────────────────────────────────────────────────────────────

    video.release()


if __name__ == "__main__":
    main()