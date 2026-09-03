"""
rule_engine.py
==============
Fall-detection rule engine — 6-state machine + DANGER (lying still) detector.

NEW IN THIS VERSION
-------------------
FEATURE: DANGER detection — person lying still for DANGER_SEC seconds.
  If a person is in the Lying posture and has not moved (movement < INACTIVITY_PX)
  for at least DANGER_SEC continuous seconds, the engine marks danger=True.
  This is SEPARATE from the fall state machine and fires even if no fall
  transition was detected (e.g. person sat/lay down gradually).

BUG FIXES PRESERVED FROM PREVIOUS VERSION
------------------------------------------
BUG 1 — False fall when lying person moves limbs:
  Guard: currently_lying (angle > LYING_GUARD_ANGLE) blocks PRE_FALL entry.

BUG 2 — Stale state bleeds into second fall cycle:
  On RECOVERY → NORMAL all _fall_time, _pre_fall_count, _last_upright_t
  are cleared.
"""

import time
from enum import Enum


# ── State definitions ────────────────────────────────────────────────
class FallState(Enum):
    NORMAL         = "NORMAL"
    PRE_FALL       = "PRE_FALL"
    FALLING        = "FALLING"
    POSSIBLE_FALL  = "POSSIBLE_FALL"
    FALL_CONFIRMED = "FALL_CONFIRMED"
    RECOVERY       = "RECOVERY"


# ── Posture / angle thresholds ───────────────────────────────────────
UPRIGHT_ANGLE      = 35    # angle < 35° → person is upright / standing
HORIZONTAL_ANGLE   = 55    # angle > 55° → person is lying / horizontal
LYING_GUARD_ANGLE  = 50    # if already lying, suppress fall state machine

# ── Motion thresholds ────────────────────────────────────────────────
ANG_VEL_FALL       = 60    # deg/s — active fall rotation
ANG_VEL_PREFAIL    = 30    # deg/s — possible pre-fall
RATIO_LYING        = 1.5   # bbox height/width below this = lying
MOVEMENT_SPIKE     = 1.4   # relative movement spike multiplier
INACTIVITY_PX      = 6     # px/frame — below this = "not moving"

# ── Timing thresholds ────────────────────────────────────────────────
INACTIVITY_SEC     = 1.5   # seconds of stillness to confirm fall
CONFIRM_SEC        = 2.0   # seconds for risk score inactivity signal
UPRIGHT_WINDOW     = 3.0   # look-back window for "was upright recently"
RECOVERY_ANGLE     = 40    # angle < 40° → recovering to upright
RECOVERY_SEC       = 1.5   # seconds upright → full recovery
COOLDOWN_SEC       = 8.0   # min seconds between alerts for same person

# ── DANGER threshold ─────────────────────────────────────────────────
DANGER_SEC         = 5.0   # seconds lying still → DANGER
DANGER_MOVEMENT_PX = 4      # px/frame threshold for "still" in danger check

# ── Risk score weights (must sum to 1.0) ─────────────────────────────
W_ANG_VEL     = 0.35
W_TRANSITION  = 0.25
W_INACTIVITY  = 0.20
W_MOV_SPIKE   = 0.12
W_HORIZ_RATIO = 0.08


class RuleEngine:
    def __init__(self, cooldown_sec=COOLDOWN_SEC):
        self.cooldown_sec      = cooldown_sec
        self._state            = {}   # id → FallState
        self._state_entry_time = {}   # id → timestamp entered current state
        self._last_upright_t   = {}   # id → last time angle < UPRIGHT_ANGLE
        self._fall_time        = {}   # id → timestamp of "possible fall" start
        self._last_alert_t     = {}   # id → last confirmed alert timestamp
        self._pre_fall_count   = {}   # id → consecutive PRE_FALL frames

        # DANGER tracking
        self._lying_since      = {}   # id → timestamp person first became lying
        self._danger_fired     = {}   # id → bool, prevents repeated DANGER logs

    # ── Public accessor ──────────────────────────────────────────────
    def get_state(self, object_id):
        return self._state.get(object_id, FallState.NORMAL)

    # ── Main entry point ─────────────────────────────────────────────
    def process(self, object_id, buffer, feature_extractor=None):
        """
        Run the full state machine + DANGER check for one tracked person.

        Parameters
        ----------
        object_id        : int
        buffer           : list of (timestamp, features_dict)
        feature_extractor: FeatureExtractor instance (for posture history)

        Returns
        -------
        dict:
            state           – current FallState
            fall_confirmed  – bool, True if alert should fire this frame
            risk_score      – float 0–1
            reason          – str description
            is_lying_moving – bool, True if lying but actively moving limbs
            danger          – bool, True if lying still for DANGER_SEC seconds
        """
        now   = time.time()
        state = self._state.get(object_id, FallState.NORMAL)

        if len(buffer) < 2:
            return self._result(state, False, 0.0,
                                "Insufficient buffer", False, False)

        latest_t, latest_f = buffer[-1]
        current_angle = latest_f["angle"]
        ang_vel       = latest_f.get("angular_velocity", 0.0)
        posture       = latest_f.get("posture", "Standing")

        # ── Track last upright time ──────────────────────────────────
        for t, f in buffer:
            if f["angle"] < UPRIGHT_ANGLE:
                self._last_upright_t[object_id] = t

        last_up              = self._last_upright_t.get(object_id, 0)
        was_upright_recently = (now - last_up) <= UPRIGHT_WINDOW

        # ── BUG-1 guard: already lying? ──────────────────────────────
        currently_lying = current_angle > LYING_GUARD_ANGLE

        # ── Compute risk score ───────────────────────────────────────
        risk = self._compute_risk_score(object_id, buffer, feature_extractor)

        # ── DANGER CHECK ─────────────────────────────────────────────
        # Independent of the fall state machine.
        # Fires when person is in Lying posture AND has been still for
        # DANGER_SEC seconds — even if they just lay down normally.
        danger = self._check_danger(object_id, buffer, posture, now)

        # ── State machine ────────────────────────────────────────────
        next_state = state

        if state == FallState.NORMAL:
            if (was_upright_recently
                    and ang_vel >= ANG_VEL_PREFAIL
                    and not currently_lying):
                next_state = FallState.PRE_FALL
                self._pre_fall_count[object_id] = 1

        elif state == FallState.PRE_FALL:
            if currently_lying:
                next_state = FallState.NORMAL
            elif ang_vel >= ANG_VEL_FALL and was_upright_recently:
                next_state = FallState.FALLING
            elif ang_vel < ANG_VEL_PREFAIL * 0.5:
                next_state = FallState.NORMAL

        elif state == FallState.FALLING:
            is_horiz   = (current_angle > HORIZONTAL_ANGLE
                          and latest_f["ratio"] < RATIO_LYING)
            transition = latest_f.get("standing_to_lying_transition", False)
            if is_horiz or transition:
                next_state = FallState.POSSIBLE_FALL
                self._fall_time[object_id] = now
            elif current_angle < UPRIGHT_ANGLE:
                next_state = FallState.NORMAL

        elif state == FallState.POSSIBLE_FALL:
            fall_t    = self._fall_time.get(object_id, now)
            post      = [b for b in buffer if b[0] >= fall_t]
            still     = [b for b in post
                         if b[1]["movement"] < INACTIVITY_PX]
            still_dur = (still[-1][0] - still[0][0]) if len(still) >= 2 else 0.0

            if still_dur >= INACTIVITY_SEC:
                next_state = FallState.FALL_CONFIRMED
            elif current_angle < UPRIGHT_ANGLE:
                next_state = FallState.RECOVERY

        elif state == FallState.FALL_CONFIRMED:
            if self._check_recovery(object_id, buffer, now):
                next_state = FallState.RECOVERY

        elif state == FallState.RECOVERY:
            if (current_angle < UPRIGHT_ANGLE
                    and latest_f["ratio"] > 1.5):
                next_state = FallState.NORMAL
                # BUG-2 fix: clear all stale fall-cycle state
                self._fall_time.pop(object_id, None)
                self._pre_fall_count.pop(object_id, None)
                self._last_upright_t.pop(object_id, None)

        # ── Apply state transition ───────────────────────────────────
        if next_state != state:
            self._state[object_id]            = next_state
            self._state_entry_time[object_id] = now
            print(f"[STATE] ID {object_id}: {state.value} → "
                  f"{next_state.value} | risk={risk:.2f}")

        # ── Lying-moving display flag ────────────────────────────────
        is_lying_moving = (
            currently_lying
            and latest_f.get("movement", 0) > 3.0
            and self._state.get(object_id, FallState.NORMAL)
                in (FallState.NORMAL, FallState.PRE_FALL)
        )

        # ── Alert fire check ─────────────────────────────────────────
        current_state  = self._state.get(object_id, FallState.NORMAL)
        fall_confirmed = False

        if current_state == FallState.FALL_CONFIRMED:
            last_alert = self._last_alert_t.get(object_id, 0)
            if now - last_alert >= self.cooldown_sec:
                fall_confirmed = True
                self._last_alert_t[object_id] = now

        return self._result(current_state, fall_confirmed, risk,
                            f"State={current_state.value}",
                            is_lying_moving, danger)

    # ── DANGER check ─────────────────────────────────────────────────
    def _check_danger(self, object_id, buffer, posture, now):
        """
        Returns True when:
          1. Current posture is Lying.
          2. Every frame in the last DANGER_SEC seconds shows Lying posture
             AND movement below DANGER_MOVEMENT_PX.

        Tracks _lying_since to measure continuous lying duration.
        Resets if person stands/sits or moves significantly.
        """
        is_lying = (posture == "Lying")

        if not is_lying:
            # Person is not lying — reset tracking
            self._lying_since.pop(object_id, None)
            self._danger_fired[object_id] = False
            return False

        # Person is lying — look at recent window
        window = [
            (t, f) for t, f in buffer
            if now - t <= DANGER_SEC
        ]

        if len(window) < 3:
            # Not enough history yet
            if object_id not in self._lying_since:
                self._lying_since[object_id] = now
            return False

        # Check if all frames in the window are Lying AND still
        all_lying_still = all(
            f.get("posture", "") == "Lying"
            and f.get("movement", 999) < DANGER_MOVEMENT_PX
            for _, f in window
        )

        if not all_lying_still:
            # Person moved or changed posture in the window → reset
            self._lying_since[object_id] = now
            self._danger_fired[object_id] = False
            return False

        # All frames are lying + still — check duration
        if object_id not in self._lying_since:
            self._lying_since[object_id] = window[0][0]

        lying_duration = now - self._lying_since[object_id]

        if lying_duration >= DANGER_SEC:
            return True

        return False

    # ── Risk score ───────────────────────────────────────────────────
    def _compute_risk_score(self, object_id, buffer, feature_extractor):
        if len(buffer) < 2:
            return 0.0

        latest_t, latest_f = buffer[-1]

        # If body already lying and NOT in a confirmed fall state,
        # cap risk low so the risk bar is not misleading
        if latest_f["angle"] > LYING_GUARD_ANGLE:
            in_fall_state = self._state.get(object_id, FallState.NORMAL) in (
                FallState.POSSIBLE_FALL, FallState.FALL_CONFIRMED
            )
            if not in_fall_state:
                return round(
                    min(0.30, self._raw_risk(
                        object_id, buffer, feature_extractor)), 3)

        return round(
            min(self._raw_risk(object_id, buffer, feature_extractor), 1.0), 3)

    def _raw_risk(self, object_id, buffer, feature_extractor):
        latest_t, latest_f = buffer[-1]

        # S1: Angular velocity
        ang_vel = latest_f.get("angular_velocity", 0.0)
        s1 = min(ang_vel / ANG_VEL_FALL, 1.0)

        # S2: Posture transition (Standing → Lying)
        s2 = 0.0
        if feature_extractor is not None:
            try:
                if feature_extractor.detect_standing_to_lying(object_id):
                    s2 = 1.0
            except Exception:
                pass

        # S3: Inactivity duration after horizontal
        horiz_buf = [b for b in buffer
                     if b[1]["angle"] > HORIZONTAL_ANGLE
                     and b[1]["ratio"] < RATIO_LYING]
        inactivity_dur = 0.0
        if len(horiz_buf) >= 2:
            still = [b for b in horiz_buf
                     if b[1]["movement"] < INACTIVITY_PX]
            if len(still) >= 2:
                inactivity_dur = still[-1][0] - still[0][0]
        s3 = min(inactivity_dur / CONFIRM_SEC, 1.0)

        # S4: Movement spike
        s4 = 0.0
        if len(buffer) >= 4:
            movements = [b[1]["movement"] for b in buffer]
            avg_early = sum(movements[:-2]) / max(1, len(movements) - 2)
            peak      = max(movements[-3:])
            if avg_early > 0:
                s4 = max(0.0, min(
                    (peak / avg_early - 1.0) / (MOVEMENT_SPIKE - 1.0), 1.0))

        # S5: Horizontal bbox ratio
        s5 = 1.0 if (latest_f["angle"] > HORIZONTAL_ANGLE
                     and latest_f["ratio"] < RATIO_LYING) else 0.0

        return (W_ANG_VEL     * s1
              + W_TRANSITION  * s2
              + W_INACTIVITY  * s3
              + W_MOV_SPIKE   * s4
              + W_HORIZ_RATIO * s5)

    # ── Recovery check ───────────────────────────────────────────────
    def _check_recovery(self, object_id, buffer, now):
        fall_t = self._fall_time.get(object_id, now)
        post   = [b for b in buffer if b[0] > fall_t]
        if not post:
            return False
        upright = [b for b in post if b[1]["angle"] < RECOVERY_ANGLE]
        if len(upright) < 2:
            return False
        return (upright[-1][0] - upright[0][0]) >= RECOVERY_SEC

    # ── Helper ───────────────────────────────────────────────────────
    @staticmethod
    def _result(state, fall_confirmed, risk, reason,
                is_lying_moving=False, danger=False):
        return {
            "state":           state,
            "fall_confirmed":  fall_confirmed,
            "risk_score":      risk,
            "reason":          reason,
            "is_lying_moving": is_lying_moving,
            "danger":          danger,
        }

    # ── Legacy wrappers ──────────────────────────────────────────────
    def check_fall(self, object_id, buffer):
        res = self.process(object_id, buffer)
        is_possible = res["state"] in (
            FallState.FALLING,
            FallState.POSSIBLE_FALL,
            FallState.FALL_CONFIRMED,
        )
        return is_possible, res["reason"]

    def confirm_fall(self, object_id, buffer):
        return self.get_state(object_id) == FallState.FALL_CONFIRMED
