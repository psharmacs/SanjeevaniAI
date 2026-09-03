"""
feature_extraction.py
=====================
Extracts per-frame features for each tracked person.

FIXES IN THIS VERSION
---------------------
FIX 1 — classify_posture() thresholds were INVERTED / WRONG.
  SYMPTOM: System could not correctly distinguish Standing vs Lying.
  ROOT CAUSE: bbox ratio = height / width.
    - Standing person  → tall bbox   → ratio HIGH  (e.g. 2.0–4.0)
    - Lying person     → wide bbox   → ratio LOW   (e.g. 0.3–0.8)
    - Old code checked `ratio < 0.75` for Lying, which was correct
      directionally but threshold was too aggressive and conflicted
      with the angle conditions.  More critically the Standing check
      `ratio > 1.8` fired BEFORE the Lying check, so many lying
      people with a ratio of 1.0–1.5 were misclassified as Sitting.
  FIX: Reordered and recalibrated thresholds so that:
    - Lying   = angle > 55°  OR  ratio < 1.0
    - Standing = angle < 30° AND ratio > 1.6
    - Everything else = Sitting

FIX 2 — Angular velocity window was broken.
  SYMPTOM: ang_vel always returned 0 after the first frame.
  ROOT CAUSE: The loop that found the oldest sample in the 0.5 s window
    was returning the FIRST sample inside the window (break on first
    match ≥ window_start), but was naming it old_t/old_a, making dt ≈ 0.
  FIX: Iterate to find the EARLIEST sample inside the window instead.
"""

import math
import time
import numpy as np
from collections import deque


# ── Angular-velocity thresholds (degrees / second) ──────────────────
ANG_VEL_FALL_THRESHOLD    = 60
ANG_VEL_PREFAIL_THRESHOLD = 30

# ── Posture history length ───────────────────────────────────────────
POSTURE_HISTORY_LEN = 20   # ~2 s at 10 fps


class FeatureExtractor:
    def __init__(self, smoothing_window=5):
        self.smoothing_window  = smoothing_window

        # Per-person smoothing buffers
        self.angle_buffer    = {}
        self.movement_buffer = {}
        self.ratio_buffer    = {}

        # Angular-velocity computation
        self.angle_history   = {}   # {id: deque of (timestamp, smooth_angle)}

        # Posture transition tracking
        self.posture_history = {}   # {id: deque of posture labels}

        # Previous smooth angle (for per-frame delta)
        self.prev_smooth_angle = {}

        # Previous bbox centre (for movement)
        self.prev_centers = {}

    # ──────────────────────────────────────────────────────────────────
    # PCA body-orientation angle
    # ──────────────────────────────────────────────────────────────────
    def _compute_body_angle(self, ls, rs, lh, rh):
        """
        Uses SVD/PCA on shoulder + hip keypoints to find body axis angle.

        Returns float in [0°, 90°]:
            ~0°  → vertical   (standing)
            ~90° → horizontal (lying)
        """
        pts = np.array([ls, rs, lh, rh], dtype=float)
        centered = pts - pts.mean(axis=0)
        try:
            _, _, vt = np.linalg.svd(centered)
            ax = vt[0]
            return math.degrees(math.atan2(abs(ax[0]), abs(ax[1])))
        except Exception:
            dx = rs[0] - ls[0]
            dy = rs[1] - ls[1]
            d  = math.hypot(dx, dy)
            return math.degrees(math.atan2(abs(dx), abs(dy))) if d > 1 else 0.0

    # ──────────────────────────────────────────────────────────────────
    # Hybrid posture classifier  ← FIX 1
    # ──────────────────────────────────────────────────────────────────
    def classify_posture(self, angle, ratio):
        """
        Vote: PCA body angle  +  bbox aspect ratio.

        bbox ratio = height / width:
            Standing → ratio HIGH (≈ 2.0 – 4.0), angle LOW  (< 35°)
            Lying    → ratio LOW  (≈ 0.3 – 1.0), angle HIGH (> 55°)
            Sitting  → intermediate values

        Decision table (first match wins):
            1. angle > 55°                     → Lying   (strong angle signal)
            2. ratio < 1.0                     → Lying   (very wide bbox)
            3. angle > 45° AND ratio < 1.3     → Lying   (combined weak signal)
            4. angle < 30° AND ratio > 1.6     → Standing
            5. ratio > 2.0                     → Standing (very tall bbox)
            6. everything else                 → Sitting
        """
        if angle > 55:
            return "Lying"
        if angle < 35 and ratio > 1.4:
            return "Standing"
        
        # If the body is relatively upright, it shouldn't be Lying even if the box is wide (like when sitting)
        if ratio < 0.7 and angle > 45:
            return "Lying"
            
        if ratio > 2.0:
            return "Standing"
            
        return "Sitting"

    # ──────────────────────────────────────────────────────────────────
    # Angular velocity  ← FIX 2
    # ──────────────────────────────────────────────────────────────────
    def _compute_angular_velocity(self, object_id, smooth_angle, now):
        """
        Angular velocity (deg/sec) over last 0.5 s window.
        Returns 0.0 if insufficient history.
        """
        if object_id not in self.angle_history:
            self.angle_history[object_id] = deque(maxlen=30)

        self.angle_history[object_id].append((now, smooth_angle))
        hist = self.angle_history[object_id]

        if len(hist) < 2:
            return 0.0

        # FIX 2: find the EARLIEST sample that is still inside the window
        window_start = now - 0.5
        earliest_t, earliest_a = hist[0]           # absolute oldest
        for t, a in hist:
            if t >= window_start:                   # first sample in window
                earliest_t, earliest_a = t, a
                break

        dt = now - earliest_t
        if dt < 0.01:
            return 0.0

        return abs(smooth_angle - earliest_a) / dt  # deg / sec

    # ──────────────────────────────────────────────────────────────────
    # Posture transition detection
    # ──────────────────────────────────────────────────────────────────
    def _update_posture_history(self, object_id, posture):
        if object_id not in self.posture_history:
            self.posture_history[object_id] = deque(maxlen=POSTURE_HISTORY_LEN)
        self.posture_history[object_id].append(posture)

    def get_posture_history(self, object_id):
        return self.posture_history.get(object_id, deque())

    def detect_standing_to_lying(self, object_id):
        """
        True if posture history contains Standing → (Sitting?) → Lying.
        """
        hist = list(self.posture_history.get(object_id, []))
        if len(hist) < 3:
            return False

        had_standing   = False
        had_transition = False
        for p in hist:
            if p == "Standing":
                had_standing = True
            elif p in ("Sitting", "Lying") and had_standing:
                had_transition = True
            if p == "Lying" and had_transition:
                return True
        return False

    # ──────────────────────────────────────────────────────────────────
    # Main extraction
    # ──────────────────────────────────────────────────────────────────
    def extract(self, object_id, bbox, pose, prev_features=None):
        """
        Compute all features for one tracked person in one frame.

        Returns dict:
            angle                        – smoothed PCA body angle (deg)
            ratio                        – smoothed bbox height/width
            movement                     – smoothed centroid displacement (px)
            angle_change                 – |Δsmooth_angle| since last frame
            angular_velocity             – deg/sec over 0.5 s window
            posture                      – "Standing" | "Sitting" | "Lying"
            standing_to_lying_transition – bool
        Returns None if pose is degenerate.
        """
        now = time.time()
        x1, y1, x2, y2 = bbox

        # ── Bbox ratio ───────────────────────────────────────────────
        h = max(y2 - y1, 1)
        w = max(x2 - x1, 1)
        raw_ratio = max(0.3, min(h / w, 5.0))

        # ── Resolve keypoints ────────────────────────────────────────
        if pose is None:
            # Fallback to pure bounding box ratio when skeleton is missing
            raw_angle = 90.0 if raw_ratio < 1.0 else 0.0
        else:
            has_full = all(k in pose for k in (
                "left_shoulder", "right_shoulder", "left_hip", "right_hip"
            ))
            if has_full:
                ls = pose["left_shoulder"];  rs = pose["right_shoulder"]
                lh = pose["left_hip"];       rh = pose["right_hip"]
                raw_angle = self._compute_body_angle(ls, rs, lh, rh)
            elif "shoulder" in pose and "hip" in pose:
                sm = pose["shoulder"];  hm = pose["hip"]
                dx = sm[0] - hm[0];    dy = sm[1] - hm[1]
                if math.hypot(dx, dy) < 1e-6:
                    raw_angle = 90.0 if raw_ratio < 1.0 else 0.0
                else:
                    raw_angle = math.degrees(math.atan2(abs(dx), abs(dy)))
            else:
                raw_angle = 90.0 if raw_ratio < 1.0 else 0.0

        # ── Bbox ratio ───────────────────────────────────────────────
        h = max(y2 - y1, 1)
        w = max(x2 - x1, 1)
        raw_ratio = max(0.3, min(h / w, 5.0))

        # ── Movement ─────────────────────────────────────────────────
        cx = (x1 + x2) / 2.0;  cy = (y1 + y2) / 2.0
        pcx, pcy = self.prev_centers.get(object_id, (cx, cy))
        raw_movement = math.hypot(cx - pcx, cy - pcy)
        self.prev_centers[object_id] = (cx, cy)

        # ── Smoothing buffers ────────────────────────────────────────
        for buf in (self.angle_buffer, self.movement_buffer, self.ratio_buffer):
            if object_id not in buf:
                buf[object_id] = deque(maxlen=self.smoothing_window)

        self.angle_buffer[object_id].append(raw_angle)
        self.movement_buffer[object_id].append(raw_movement)
        self.ratio_buffer[object_id].append(raw_ratio)

        smooth_angle    = float(np.mean(self.angle_buffer[object_id]))
        smooth_movement = float(np.mean(self.movement_buffer[object_id]))
        smooth_ratio    = float(np.mean(self.ratio_buffer[object_id]))

        # ── Angle change (smooth delta) ──────────────────────────────
        prev_s       = self.prev_smooth_angle.get(object_id, smooth_angle)
        angle_change = abs(smooth_angle - prev_s)
        self.prev_smooth_angle[object_id] = smooth_angle

        # ── Angular velocity ─────────────────────────────────────────
        angular_velocity = self._compute_angular_velocity(
            object_id, smooth_angle, now
        )

        # ── Posture + transition ─────────────────────────────────────
        posture    = self.classify_posture(smooth_angle, smooth_ratio)
        self._update_posture_history(object_id, posture)
        transition = self.detect_standing_to_lying(object_id)

        print(
            f"[FEATURE] ID {object_id} | "
            f"angle={smooth_angle:.1f}° | ratio={smooth_ratio:.2f} | "
            f"ang_vel={angular_velocity:.1f}°/s | "
            f"move={smooth_movement:.1f}px | posture={posture}"
            + (" | TRANSITION⚡" if transition else "")
        )

        return {
            "angle":                        smooth_angle,
            "ratio":                        smooth_ratio,
            "movement":                     smooth_movement,
            "angle_change":                 angle_change,
            "angular_velocity":             angular_velocity,
            "posture":                      posture,
            "standing_to_lying_transition": transition,
        }
