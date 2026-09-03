"""
recovery.py
===========

Handles the 5-second RECOVERY override after DANGER.

Behavior:
    DANGER
       ↓
    person moves / changes posture
       ↓
    RECOVERY for 5 seconds
       ↓
    normal detection resumes
"""

import time
from datetime import datetime


class DangerRecovery:
    def __init__(self, recovery_duration=10.0):
        self.recovery_duration = recovery_duration

        # object_id -> recovery start time
        self._recovery_start = {}

        # object_id -> whether DANGER was detected
        self._danger_active = {}

    def mark_danger(self, object_id):
        """
        Remember that this person has entered DANGER.
        """
        self._danger_active[object_id] = True

    def should_start_recovery(
        self,
        object_id,
        movement,
        posture,
        state
    ):
        """
        Decide whether DANGER recovery should start.

        Recovery starts only after DANGER has already occurred
        and the person subsequently moves or changes state.
        """

        if not self._danger_active.get(object_id, False):
            return False

        # Already in recovery
        if object_id in self._recovery_start:
            return False

        # Movement of limbs/body
        moved = movement > 3.0

        # Posture changed from lying
        posture_changed = posture in (
            "Sitting",
            "Standing",
        )

        # Existing rule-engine recovery state
        existing_recovery = (
            str(state).upper().endswith("RECOVERY")
        )

        return moved or posture_changed or existing_recovery

    def start_recovery(self, object_id):
        """
        Start the 5-second recovery period.
        """
        if object_id in self._recovery_start:
            return False

        self._recovery_start[object_id] = time.time()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(
            f"[RECOVERY] Person {object_id} entered RECOVERY "
            f"at {timestamp} — duration: 5 seconds."
        )

        return True

    def is_recovering(self, object_id):
        """
        Return True while the 5-second recovery period is active.
        """
        if object_id not in self._recovery_start:
            return False

        elapsed = time.time() - self._recovery_start[object_id]

        if elapsed < self.recovery_duration:
            return True

        self.finish_recovery(object_id)
        return False

    def remaining_seconds(self, object_id):
        """
        Return remaining recovery time.
        """
        if object_id not in self._recovery_start:
            return 0.0

        elapsed = time.time() - self._recovery_start[object_id]
        remaining = self.recovery_duration - elapsed

        return max(0.0, remaining)

    def finish_recovery(self, object_id):
        """
        Finish the recovery period and return to normal detection.
        """
        if object_id not in self._recovery_start:
            return False

        del self._recovery_start[object_id]

        self._danger_active.pop(object_id, None)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(
            f"[RECOVERY] Person {object_id} recovery completed "
            f"at {timestamp} — normal detection resumed."
        )

        return True

    def clear_person(self, object_id):
        """
        Remove all recovery information for a person.
        """
        self._recovery_start.pop(object_id, None)
        self._danger_active.pop(object_id, None)