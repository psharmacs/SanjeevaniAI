"""
alert_system.py
===============
Manages fall alerts with:

1. COOLDOWN TIMER     — same person cannot trigger again within cooldown_sec.
2. RECOVERY TRACKING  — records when a person recovers after a fall.
3. SPAM PREVENTION    — alert() returns False if cooldown not elapsed.
4. ALERT LOG          — in-memory history of all alerts (id, time, type).
5. DANGER LOGGING     — logs "DANGER" to terminal AND output/logs.txt
                         when person is lying still for >= 5 seconds.
6. VOICE EMERGENCY    — NEW: logs voice-triggered emergency separately from
                         camera-detected DANGER events so they are clearly
                         distinguishable in the log and in the alert_log list.
                         Uses its own cooldown (_voice_cooldown) and its own
                         last-logged tracker (_voice_logged) so it never
                         interferes with notify_danger() or alert().

LOG FILE
--------
All events are appended to:    output/logs.txt
Events written:
    [HH:MM:SS] FALL DETECTED   — Person {id} | risk={score}
    [HH:MM:SS] RECOVERY        — Person {id}
    [HH:MM:SS] ⚠ DANGER        — Person {id} | lying still >= 5 s
    [HH:MM:SS] 🎙 VOICE EMERGENCY — command=...
"""

import os
import time


# Path to log file — created automatically if it doesn't exist
LOG_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "output", "logs.txt"
)


def _ensure_log_dir():
    """Create output/ directory if it doesn't exist."""
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)


def _write_log(line: str):
    """Append one line to output/logs.txt."""
    _ensure_log_dir()
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


class AlertSystem:
    def __init__(self, cooldown_sec=8):
        """
        Parameters
        ----------
        cooldown_sec : int
            Minimum seconds between consecutive FALL alerts for the same person.
        """
        self.cooldown_sec  = cooldown_sec
        self.last_alert    = {}   # id → timestamp of last fired alert
        self.alert_log     = []   # list of event dicts
        self.recovery_log  = {}   # id → timestamp of last recovery

        # DANGER tracking — avoid spamming repeated DANGER messages
        self._danger_logged   = {}    # id → timestamp last danger was logged
        self._danger_cooldown = 10.0  # seconds between repeated DANGER logs

        # VOICE EMERGENCY tracking — completely separate from notify_danger()
        # so that voice alerts and camera danger alerts never interfere with
        # each other's cooldown timers or log entries.
        self._voice_logged   = 0.0   # timestamp of last voice emergency logged
        self._voice_cooldown = 10.0  # seconds between repeated voice logs

    # ── Fall alert ───────────────────────────────────────────────────
    def alert(self, object_id, risk_score=1.0):
        """
        Fire a fall alert for `object_id`.

        Returns True if alert was fired (cooldown elapsed).
        Returns False if cooldown is still active (spam prevention).
        """
        now  = time.time()
        last = self.last_alert.get(object_id, 0)

        if now - last < self.cooldown_sec:
            return False

        self.last_alert[object_id] = now
        self.alert_log.append({
            "id":         object_id,
            "time":       now,
            "type":       "FALL",
            "risk_score": round(risk_score, 3),
        })

        ts  = time.strftime("%H:%M:%S", time.localtime(now))
        msg = (
            f"[ALERT] ⚠️  FALL DETECTED — Person {object_id} "
            f"| risk={risk_score:.2f} | time={ts}"
        )
        print(msg)
        _write_log(f"[{ts}] FALL DETECTED — Person {object_id} | risk={risk_score:.2f}")
        return True

    # ── Recovery notification ────────────────────────────────────────
    def notify_recovery(self, object_id):
        """Call when the rule engine transitions to RECOVERY state."""
        now = time.time()
        self.recovery_log[object_id] = now
        self.alert_log.append({
            "id":         object_id,
            "time":       now,
            "type":       "RECOVERY",
            "risk_score": 0.0,
        })
        ts  = time.strftime("%H:%M:%S", time.localtime(now))
        msg = f"[ALERT] ✅ RECOVERY — Person {object_id} | time={ts}"
        print(msg)
        _write_log(f"[{ts}] RECOVERY — Person {object_id}")

    # ── DANGER notification ──────────────────────────────────────────
    def notify_danger(self, object_id):
        """
        Call when a person has been lying still for >= DANGER_SEC seconds.

        Prints to terminal AND writes to output/logs.txt.
        Suppressed if the same danger was logged within _danger_cooldown seconds
        (prevents log spam at video framerate).

        Returns True if the danger message was actually written.
        """
        now  = time.time()
        last = self._danger_logged.get(object_id, 0)

        if now - last < self._danger_cooldown:
            return False

        self._danger_logged[object_id] = now
        self.alert_log.append({
            "id":         object_id,
            "time":       now,
            "type":       "DANGER",
            "risk_score": 0.0,
        })

        ts  = time.strftime("%H:%M:%S", time.localtime(now))
        msg = (
            f"[DANGER] 🚨 Person {object_id} is in DANGER — "
            f"lying still for >= 5 seconds | time={ts}"
        )
        print(msg)
        _write_log(
            f"[{ts}] ⚠ DANGER — Person {object_id} | lying still >= 5 s"
        )
        return True

    # ── VOICE EMERGENCY notification ─────────────────────────────────
    def notify_voice_emergency(self, object_id, voice_cmd: str):
        """
        Call when the voice assistant detects the wake word + emergency keyword.

        This is intentionally separate from notify_danger() because:
          - A voice emergency is triggered by the person speaking, not by
            camera/pose analysis. The event type is different and should be
            clearly labelled in the log.
          - object_id is always -1 for voice events (no camera-tracked person).
          - Using notify_danger(-1) would conflate voice alerts with camera
            DANGER events, making the log ambiguous.
          - This function has its own cooldown (_voice_logged, _voice_cooldown)
            so it never resets or interferes with the camera DANGER cooldowns.

        Prints to terminal:
            [SANJEEVANI] 🎙 VOICE EMERGENCY — command='...' | time=HH:MM:SS

        Writes to output/logs.txt:
            [HH:MM:SS] 🎙 VOICE EMERGENCY — command=...

        Appends to alert_log with type "VOICE_EMERGENCY".

        Returns True  if the message was actually written (cooldown elapsed).
        Returns False if still within the voice cooldown window.

        Parameters
        ----------
        object_id  : int  Tracking ID — always -1 for voice-triggered events.
        voice_cmd  : str  The full transcribed command that triggered the alert.
        """
        now = time.time()

        # ── Cooldown guard — uses _voice_logged, not _danger_logged ──
        if now - self._voice_logged < self._voice_cooldown:
            return False

        self._voice_logged = now

        # ── Append to in-memory alert log ────────────────────────────
        self.alert_log.append({
            "id":         object_id,
            "time":       now,
            "type":       "VOICE_EMERGENCY",
            "risk_score": 0.0,
            "command":    voice_cmd,
        })

        ts = time.strftime("%H:%M:%S", time.localtime(now))

        # ── Terminal output ───────────────────────────────────────────
        print(
            f"[SANJEEVANI] 🎙 VOICE EMERGENCY — "
            f"command='{voice_cmd}' | time={ts}"
        )

        # ── Log file output ───────────────────────────────────────────
        _write_log(
            f"[{ts}] 🎙 VOICE EMERGENCY — command={voice_cmd}"
        )

        return True

    # ── Cooldown status ──────────────────────────────────────────────
    def in_cooldown(self, object_id):
        """Returns True if still within the alert cooldown period."""
        last = self.last_alert.get(object_id, 0)
        return (time.time() - last) < self.cooldown_sec

    def cooldown_remaining(self, object_id):
        """Returns seconds remaining in cooldown (0 if not in cooldown)."""
        last = self.last_alert.get(object_id, 0)
        return max(0.0, self.cooldown_sec - (time.time() - last))

    # ── Log access ───────────────────────────────────────────────────
    def get_log(self):
        """Return full alert history list."""
        return list(self.alert_log)

    def get_fall_count(self, object_id=None):
        """Return number of fall alerts (optionally filtered by person)."""
        falls = [e for e in self.alert_log if e["type"] == "FALL"]
        if object_id is not None:
            falls = [e for e in falls if e["id"] == object_id]
        return len(falls)