"""
bed_zone.py
===========
Manual Bed Zone module for Sanjeevani AI.

Purpose:
1. Load saved bed zone points from output/bed_zone.json
2. Save bed zone points
3. Draw bed zone on frame
4. Check whether a point is inside bed zone
5. Check whether person bbox center is inside bed zone
6. Return person bbox center for visual debugging

This module only handles bed area.
It does NOT handle sleep monitoring.
It does NOT change fall detection logic.
"""

import os
import json
import cv2
import numpy as np


# Bed zone points will be saved here:
# fall_detection/output/bed_zone.json
BED_ZONE_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "output",
    "bed_zone.json"
)


class BedZone:
    def __init__(self):
        self.points = []
        self.loaded = False
        self.load()

    # ── Load saved bed zone ─────────────────────────────────────────
    def load(self):
        """Load bed zone points from output/bed_zone.json."""
        if not os.path.exists(BED_ZONE_FILE):
            print("[BED_ZONE] No saved bed zone found.")
            self.points = []
            self.loaded = False
            return False

        try:
            with open(BED_ZONE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.points = data.get("points", [])

            if len(self.points) >= 3:
                self.loaded = True
                print(f"[BED_ZONE] Loaded bed zone: {self.points}")
                return True

        except Exception as e:
            print(f"[BED_ZONE] Failed to load bed zone: {e}")

        self.points = []
        self.loaded = False
        return False

    # ── Save bed zone ───────────────────────────────────────────────
    def save(self, points):
        """Save bed zone points to output/bed_zone.json."""
        os.makedirs(os.path.dirname(BED_ZONE_FILE), exist_ok=True)

        # Convert tuples to lists and values to int for clean JSON saving
        self.points = [[int(x), int(y)] for x, y in points]
        self.loaded = len(self.points) >= 3

        with open(BED_ZONE_FILE, "w", encoding="utf-8") as f:
            json.dump({"points": self.points}, f, indent=4)

        print(f"[BED_ZONE] Saved bed zone: {self.points}")

    # ── Draw bed zone ───────────────────────────────────────────────
    def draw(self, frame):
        """Draw bed zone polygon on frame."""
        if not self.loaded or len(self.points) < 3:
            return frame

        pts = np.array(self.points, dtype=np.int32)

        # Transparent fill
        overlay = frame.copy()
        cv2.fillPoly(overlay, [pts], color=(255, 0, 255))
        cv2.addWeighted(overlay, 0.20, frame, 0.80, 0, frame)

        # Polygon border
        cv2.polylines(
            frame,
            [pts],
            isClosed=True,
            color=(255, 0, 255),
            thickness=2
        )

        # Draw corner points for debugging
        for i, (x, y) in enumerate(self.points):
            cv2.circle(frame, (int(x), int(y)), 5, (0, 0, 255), -1)
            cv2.putText(
                frame,
                f"P{i + 1}",
                (int(x) + 8, int(y) - 8),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 255),
                2
            )

        # Label
        x, y = self.points[0]
        cv2.putText(
            frame,
            "BED ZONE",
            (int(x), int(y) - 15),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 0, 255),
            2
        )

        return frame

    # ── Check point inside bed zone ─────────────────────────────────
    def contains_point(self, x, y):
        """
        Check whether point (x, y) is inside bed zone.

        Returns:
            True  → point is inside bed zone
            False → point is outside bed zone
        """
        if not self.loaded or len(self.points) < 3:
            return False

        pts = np.array(self.points, dtype=np.int32)

        result = cv2.pointPolygonTest(
            pts,
            (float(x), float(y)),
            False
        )

        return result >= 0

    # ── Check person bbox center inside bed zone ────────────────────
    def contains_bbox_center(self, bbox):
        """
        Check whether person bounding box center is inside bed zone.

        bbox format:
            (x1, y1, x2, y2)
        """
        if bbox is None:
            return False

        x1, y1, x2, y2 = bbox

        cx = (x1 + x2) / 2.0
        cy = (y1 + y2) / 2.0

        return self.contains_point(cx, cy)

    # ── Get bbox center ─────────────────────────────────────────────
    def get_bbox_center(self, bbox):
        """
        Return center point of person bounding box.

        bbox format:
            (x1, y1, x2, y2)

        Returns:
            cx, cy
        """
        x1, y1, x2, y2 = bbox

        cx = int((x1 + x2) / 2.0)
        cy = int((y1 + y2) / 2.0)

        return cx, cy