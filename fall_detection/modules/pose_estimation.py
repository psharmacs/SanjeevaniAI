import cv2
import numpy as np
import mediapipe as mp

POSE_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 7),
    (0, 4), (4, 5), (5, 6), (6, 8),
    (9, 10),
    (11, 12), (11, 13), (13, 15), (15, 17), (15, 19), (15, 21),
    (17, 19), (12, 14), (14, 16), (16, 18), (16, 20), (16, 22), (18, 20),
    (11, 23), (12, 24), (23, 24), (23, 25), (24, 26), (25, 27), (26, 28),
    (27, 29), (28, 30), (29, 31), (30, 32),
]


class PoseEstimator:

    def __init__(self):
        from mediapipe.tasks.python.vision import PoseLandmarker, PoseLandmarkerOptions
        from mediapipe.tasks.python.vision.core.vision_task_running_mode import VisionTaskRunningMode

        model_path = "fall_detection/models/pose_landmarker_lite.task"
        options = PoseLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=model_path),
            running_mode=VisionTaskRunningMode.IMAGE,
            min_pose_detection_confidence=0.5,
            min_pose_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self.pose = PoseLandmarker.create_from_options(options)

    def detect_full_frame(self, frame):
        """
        Run MediaPipe PoseLandmarker on the full frame (once per frame).

        Returns dict:
            left_shoulder, right_shoulder, left_hip, right_hip -> (x,y) px
            all_landmarks -> list of 33 (x,y) pixel coords
        Returns None if no pose detected.
        """
        rgb = frame[..., ::-1].copy() if frame.shape[2] == 3 else frame
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result   = self.pose.detect(mp_image)

        if not result.pose_landmarks:
            return None

        try:
            lm   = result.pose_landmarks[0]
            h, w = frame.shape[:2]

            def to_px(landmark):
                return (int(landmark.x * w), int(landmark.y * h))

            return {
                "left_shoulder":  to_px(lm[11]),
                "right_shoulder": to_px(lm[12]),
                "left_hip":       to_px(lm[23]),
                "right_hip":      to_px(lm[24]),
                "all_landmarks":  [to_px(l) for l in lm],
            }
        except Exception:
            return None

    def get_pose_for_bbox(self, pose_data, bbox):
        """
        Match global pose result to a tracked person's bounding box.

        Returns dict with individual keypoints + midpoints, or None.
        Uses adaptive distance threshold (0.45 × max bbox dimension)
        so lying persons (wide bbox) are correctly matched.
        """
        if pose_data is None:
            return None

        required = ("left_shoulder", "right_shoulder", "left_hip", "right_hip")
        if not all(k in pose_data for k in required):
            return None

        x1, y1, x2, y2 = bbox

        ls = pose_data["left_shoulder"]
        rs = pose_data["right_shoulder"]
        lh = pose_data["left_hip"]
        rh = pose_data["right_hip"]

        shoulder_mid = ((ls[0] + rs[0]) // 2, (ls[1] + rs[1]) // 2)
        hip_mid      = ((lh[0] + rh[0]) // 2, (lh[1] + rh[1]) // 2)

        sx, sy = shoulder_mid

        # Check 1: shoulder midpoint inside bbox
        if x1 <= sx <= x2 and y1 <= sy <= y2:
            return self._build_pose_dict(ls, rs, lh, rh, shoulder_mid, hip_mid)

        # Check 2: adaptive distance threshold
        bbox_w    = max(x2 - x1, 1)
        bbox_h    = max(y2 - y1, 1)
        threshold = 0.45 * max(bbox_w, bbox_h)

        dist = np.linalg.norm(
            np.array([(x1 + x2) / 2.0, (y1 + y2) / 2.0])
            - np.array(shoulder_mid, dtype=float)
        )

        if dist < threshold:
            return self._build_pose_dict(ls, rs, lh, rh, shoulder_mid, hip_mid)

        return None

    def _build_pose_dict(self, ls, rs, lh, rh, shoulder_mid, hip_mid):
        return {
            "left_shoulder":  ls,
            "right_shoulder": rs,
            "left_hip":       lh,
            "right_hip":      rh,
            "shoulder":       shoulder_mid,
            "hip":            hip_mid,
        }

    def draw_pose(self, frame, landmarks):
        """Draw BlazePose skeleton on frame in-place."""
        if not landmarks or len(landmarks) < 25:
            return frame
        for start_idx, end_idx in POSE_CONNECTIONS:
            if start_idx < len(landmarks) and end_idx < len(landmarks):
                cv2.line(frame,
                         tuple(map(int, landmarks[start_idx])),
                         tuple(map(int, landmarks[end_idx])),
                         (0, 0, 255), 2)
        for x, y in landmarks:
            cv2.circle(frame, (int(x), int(y)), 3, (0, 255, 0), -1)
        return frame
