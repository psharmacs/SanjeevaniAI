"""
main1.py
========
Bed Zone Testing Pipeline for Sanjeevani AI.

Purpose:
This file is only for testing Manual Bed Zone.

It does ONLY these things:
1. Opens camera
2. Detects person using YOLO
3. Picks only the largest detected person
4. Loads and draws saved Bed Zone
5. Shows ON BED / OFF BED label
6. Writes ON BED / OFF BED status with time in fall_detection/bed.txt

Important:
This file does NOT:
- save recording
- write output/logs.txt
- run voice assistant
- trigger fall alert
- trigger danger alert
- change rule_engine.py
- change alert_system.py
- change original main.py

Original main.py remains safe.
"""

import cv2
import os
import time

from modules.video_capture    import VideoCapture
from modules.person_detection import PersonDetector
from modules.bed_zone         import BedZone
from utils.helpers            import draw_bbox


MODEL_PATH = "fall_detection/models/yolov8n.pt"

# ── bed.txt path ────────────────────────────────────────────────────
# This file stores ON BED / OFF BED status with timestamp.
BED_LOG_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "bed.txt"
)

# ── Stability setting ───────────────────────────────────────────────
# Status must remain same for these many frames before writing to bed.txt.
# This prevents ON BED / OFF BED flickering.
STABLE_FRAMES_REQUIRED = 5


# ── Colors (BGR) ────────────────────────────────────────────────────
COLOR_ON_BED   = (255, 0, 255)    # magenta
COLOR_OFF_BED  = (0, 0, 255)      # red
COLOR_NO_ZONE  = (128, 128, 128)  # grey


def write_bed_log(bed_status):
    """
    Write bed status into fall_detection/bed.txt.

    Example:
        [19:52:10] Main Person is ON BED
        [19:53:20] Main Person is OFF BED
    """
    now = time.time()
    ts = time.strftime("%H:%M:%S", time.localtime(now))

    line = f"[{ts}] Main Person is {bed_status}"

    with open(BED_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

    print(f"[BED_LOG] {line}")


def get_largest_bbox(boxes):
    """
    Pick only the largest detected person bbox.

    Why?
    During testing there is only one real person.
    Tracker may create many IDs when detection is lost/recreated.
    So we ignore tracker and use largest bbox only.
    """
    if not boxes:
        return None

    largest_box = None
    largest_area = 0

    for bbox in boxes:
        x1, y1, x2, y2 = bbox
        area = max(0, x2 - x1) * max(0, y2 - y1)

        if area > largest_area:
            largest_area = area
            largest_box = bbox

    return largest_box


def main():
    # ── Core modules ────────────────────────────────────────────────
    video    = VideoCapture()
    detector = PersonDetector(MODEL_PATH)

    # ── Bed Zone module ─────────────────────────────────────────────
    # Loads manually selected bed area from output/bed_zone.json.
    bed_zone = BedZone()

    # ── Status tracking ─────────────────────────────────────────────
    # confirmed_status is what has already been written to bed.txt.
    confirmed_status = None

    # candidate_status is the latest raw status waiting to become stable.
    candidate_status = None
    candidate_count = 0

    # ── Fullscreen window ───────────────────────────────────────────
    cv2.namedWindow("Bed Zone Test", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(
        "Bed Zone Test",
        cv2.WND_PROP_FULLSCREEN,
        cv2.WINDOW_FULLSCREEN
    )

    print(f"[BED_LOG] Bed status will be saved in: {BED_LOG_FILE}")

    while True:
        ret, frame, fps = video.read()
        if not ret:
            break

        display = frame.copy()
        frame_h, frame_w = frame.shape[:2]

        # ── Draw saved bed zone on screen ───────────────────────────
        if bed_zone.loaded:
            bed_zone.draw(display)
        else:
            cv2.putText(
                display,
                "BED ZONE NOT FOUND - Run select_bed_zone.py first",
                (30, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.75,
                COLOR_NO_ZONE,
                2
            )

        # ── YOLO person detection ───────────────────────────────────
        boxes = detector.detect(frame)

        # ── Pick only largest person bbox ───────────────────────────
        bbox = get_largest_bbox(boxes)

        if bbox is not None:
            x1, y1, x2, y2 = bbox

            # Check whether person bbox center is inside bed zone
            person_on_bed = bed_zone.contains_bbox_center(bbox)

            # Get center point for visual debugging
            cx, cy = bed_zone.get_bbox_center(bbox)

            if bed_zone.loaded:
                if person_on_bed:
                    raw_status = "ON BED"
                    color = COLOR_ON_BED
                else:
                    raw_status = "OFF BED"
                    color = COLOR_OFF_BED
            else:
                raw_status = "NO BED ZONE"
                color = COLOR_NO_ZONE

            # ── Stability filter ────────────────────────────────────
            # If same raw status continues for STABLE_FRAMES_REQUIRED frames,
            # then we confirm it and write to bed.txt only once.
            if raw_status == candidate_status:
                candidate_count += 1
            else:
                candidate_status = raw_status
                candidate_count = 1

            if (
                candidate_count >= STABLE_FRAMES_REQUIRED
                and candidate_status != confirmed_status
                and candidate_status in ("ON BED", "OFF BED")
            ):
                confirmed_status = candidate_status
                write_bed_log(confirmed_status)

            # Draw person bounding box
            draw_bbox(display, bbox, 0, False, color=color)

            # Draw center point of person bbox
            cv2.circle(display, (cx, cy), 6, color, -1)

            # Show ON BED / OFF BED label
            cv2.putText(
                display,
                f"MAIN PERSON: {raw_status}",
                (x1, y1 - 12),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                color,
                2
            )

        else:
            cv2.putText(
                display,
                "NO PERSON DETECTED",
                (30, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.75,
                COLOR_NO_ZONE,
                2
            )

        # ── FPS overlay ─────────────────────────────────────────────
        cv2.putText(
            display,
            f"FPS: {fps:.1f}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 0),
            2
        )

        # ── Help text ───────────────────────────────────────────────
        cv2.putText(
            display,
            "Bed Zone Test: Largest person only",
            (10, frame_h - 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2
        )

        cv2.putText(
            display,
            "ON BED / OFF BED saved in fall_detection/bed.txt",
            (10, frame_h - 45),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2
        )

        cv2.putText(
            display,
            "Press q to quit",
            (10, frame_h - 15),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2
        )

        cv2.imshow("Bed Zone Test", display)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    video.release()


if __name__ == "__main__":
    main()