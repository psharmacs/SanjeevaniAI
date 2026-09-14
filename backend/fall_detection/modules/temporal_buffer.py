"""
temporal_buffer.py
==================
Stores per-person feature history with timestamp-based pruning.

UPGRADES in this version
------------------------
1. get_window(object_id, seconds) — fetch only the last N seconds.
2. get_angle_trend(object_id, seconds) — list of (t, angle) pairs
   for angular-velocity analysis.
3. get_posture_sequence(object_id) — ordered list of recent posture
   labels for transition detection.
4. is_stationary(object_id, seconds, threshold) — True if the person
   has barely moved over the last N seconds (post-fall inactivity check).
"""

import time
from collections import deque


class TemporalBuffer:
    def __init__(self, buffer_time=5.0):
        """
        Parameters
        ----------
        buffer_time : float
            Maximum age (seconds) of entries to retain per person.
            Raised to 5 s (was 3 s) so the state machine has enough
            history to confirm falls that take 2–3 s to develop.
        """
        self.buffer_time = buffer_time
        self.buffers = {}   # {object_id: deque of (timestamp, features_dict)}

    # ── Write ────────────────────────────────────────────────────────
    def update(self, object_id, features):
        """Append (now, features) and prune old entries."""
        now = time.time()
        if object_id not in self.buffers:
            self.buffers[object_id] = deque()
        self.buffers[object_id].append((now, features))
        cutoff = now - self.buffer_time
        while self.buffers[object_id] and self.buffers[object_id][0][0] < cutoff:
            self.buffers[object_id].popleft()

    # ── Read: full buffer ────────────────────────────────────────────
    def get(self, object_id):
        """Return full list of (timestamp, features_dict)."""
        return list(self.buffers.get(object_id, []))

    # ── Read: time-windowed slice ────────────────────────────────────
    def get_window(self, object_id, seconds):
        """
        Return entries from the last `seconds` seconds only.
        Useful for the state machine to inspect recent behaviour.
        """
        cutoff = time.time() - seconds
        return [
            (t, f) for t, f in self.buffers.get(object_id, [])
            if t >= cutoff
        ]

    # ── Read: angle trend ────────────────────────────────────────────
    def get_angle_trend(self, object_id, seconds=1.0):
        """
        Return list of (timestamp, angle) pairs for the last `seconds`.
        Used to compute angular velocity and trend direction.
        """
        return [
            (t, f["angle"])
            for t, f in self.get_window(object_id, seconds)
        ]

    # ── Read: posture sequence ───────────────────────────────────────
    def get_posture_sequence(self, object_id):
        """
        Return ordered list of posture labels from the full buffer.
        Example: ["Standing", "Standing", "Sitting", "Lying"]
        """
        return [f["posture"] for _, f in self.get(object_id)]

    # ── Read: inactivity check ───────────────────────────────────────
    def is_stationary(self, object_id, seconds=2.0, threshold=6):
        """
        Returns True if the person's movement has been below `threshold`
        pixels for the entire last `seconds` window.

        Parameters
        ----------
        threshold : float
            Maximum movement (pixels) per frame to be considered still.
        """
        window = self.get_window(object_id, seconds)
        if len(window) < 3:
            return False
        return all(f["movement"] < threshold for _, f in window)

    # ── Utility ──────────────────────────────────────────────────────
    def remove(self, object_id):
        """Remove a person's buffer (e.g. when they leave frame)."""
        self.buffers.pop(object_id, None)

    def person_ids(self):
        """Return set of all currently tracked person IDs."""
        return set(self.buffers.keys())
