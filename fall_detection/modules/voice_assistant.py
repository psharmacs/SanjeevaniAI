"""
voice_assistant.py
==================
Standalone voice assistant module — "Sanjeevani".

PURPOSE
-------
Continuously listens through the laptop microphone in a background thread.
Detects the wake word "sanjeevani" followed by an emergency keyword.
Sets an internal emergency flag that the caller can poll via consume_emergency().

DESIGN PRINCIPLES
-----------------
1. Runs entirely in a daemon background thread — never blocks the camera loop,
   YOLO, MediaPipe, rule_engine, feature_extraction, or cv2.imshow().
2. Failure-safe — if the microphone, sounddevice, or speech_recognition
   library is unavailable, the module prints a warning and silently disables
   itself.  The fall detection pipeline continues normally.
3. Cooldown — repeated emergency triggers for the same phrase are suppressed
   within cooldown_sec seconds.
4. consume_emergency() is the ONLY public interface the caller needs.
   It is thread-safe (uses threading.Lock).

WHY NO PyAudio / sr.Microphone()
---------------------------------
sr.Microphone() is a SpeechRecognition convenience wrapper around PyAudio.
PyAudio requires a C extension (PortAudio) that:
  - Does NOT ship a pre-built wheel for Python 3.14 on Windows.
  - Fails at `pip install pyaudio` with compiler errors on most Windows setups.

SOLUTION: record audio directly with sounddevice (pure Python, no C compile
needed) and convert the raw PCM array into sr.AudioData so the existing
Google STT recognizer can be used without any other changes.

HOW SOUNDDEVICE REPLACES PyAudio
---------------------------------
  import sounddevice as sd
  import numpy as np

  # Record LISTEN_PHRASE_SEC seconds of 16 kHz mono audio
  raw = sd.rec(
      int(SAMPLE_RATE * LISTEN_PHRASE_SEC),
      samplerate=SAMPLE_RATE,
      channels=1,
      dtype="int16",
  )
  sd.wait()                              # block until recording is done
                                         # (inside daemon thread — safe)

  # Convert numpy int16 array → raw PCM bytes
  pcm_bytes = raw.tobytes()

  # Wrap in sr.AudioData so recognizer.recognize_google() can accept it
  audio_data = sr.AudioData(pcm_bytes, SAMPLE_RATE, 2)  # 2 bytes per sample

  # Pass to Google STT exactly as before
  text = recognizer.recognize_google(audio_data)

REQUIRED LIBRARIES
------------------
Install with pip (Python 3.14 compatible, NO PyAudio needed):

    pip install SpeechRecognition sounddevice numpy

SpeechRecognition — high-level speech-to-text wrapper (Google STT).
sounddevice       — cross-platform audio I/O via PortAudio bindings
                    that ship as a pre-built wheel for Python 3.14 Windows.
numpy             — converts sounddevice int16 array to bytes for AudioData.

HOW IT WORKS (step by step)
----------------------------
1. __init__  — stores wake word, cooldown, and initialises all state.
2. start()   — imports libraries, tests microphone, launches daemon thread.
3. _listen_loop() — infinite loop:
      a. Records a fixed-length audio chunk using sounddevice.
      b. Converts numpy array → PCM bytes → sr.AudioData.
      c. Sends AudioData to Google STT via recognizer.recognize_google().
      d. Converts result to lowercase text.
      e. Checks for wake word variations:
         "sanjeevani", "sanjivani", "sanjeevni", etc.
      f. Checks for any emergency keyword in the text.
      g. If both present AND cooldown elapsed → sets _emergency_flag + text.
4. consume_emergency() — thread-safe read-and-reset of the emergency flag.
5. stop()    — signals the loop to exit cleanly.

THREAD SAFETY
-------------
_emergency_flag and _emergency_text are protected by _lock (threading.Lock).
All reads and writes go through the lock.
"""

import time
import threading
import logging

# ── Module-level logger ──────────────────────────────────────────────
logger = logging.getLogger(__name__)


# ── Wake words ───────────────────────────────────────────────────────
# Google speech recognition may spell "Sanjeevani" differently.
# Example from your test:
#   You said: "Sanjeevani need help"
#   Recognized: "Sanjivani need help"
#
# So we accept multiple common transcription variations.
DEFAULT_WAKE_WORD = "sanjeevani"

WAKE_WORDS = [
    "sanjeevani",
    "sanjivani",
    "sanjeevni",
    "sanjivni",
    "sanjeevan",
    "sanjivan",
    "sanjivini",
    "sanjeevini",
]


# ── Emergency keywords ───────────────────────────────────────────────
# Any of these phrases/words, appearing alongside the wake word, triggers
# an alert.  Multi-word phrases are matched as substrings in the transcript.
EMERGENCY_KEYWORDS = [
    "need help",    # multi-word first so substring match catches it
    "call help",
    "call family",
    "save me",
    "help",
    "emergency",
    "injured",
    "pain",
    "fallen",
    "hurt",
    "danger",
]

# ── Audio recording parameters ────────────────────────────────────────
# 16 kHz mono int16 is the format expected by Google Web Speech API.
SAMPLE_RATE       = 16000   # Hz — standard for speech recognition
LISTEN_PHRASE_SEC = 6       # seconds of audio captured per recognition chunk
                            # Shorter = more responsive; longer = catches slow speech

# Seconds the background thread sleeps after a library/network failure
# before attempting the next recording cycle.
RETRY_SLEEP_SEC = 3


class VoiceAssistant:
    """
    Wake-word voice assistant named "Sanjeevani".

    Runs in a background daemon thread.
    Does NOT import audio libraries at module load time — imports are
    deferred to start() so that an import failure disables the assistant
    without crashing the fall detection pipeline.

    Parameters
    ----------
    wake_word    : str   Wake word to listen for (default: "sanjeevani").
    cooldown_sec : float Minimum seconds between consecutive emergency alerts.
    """

    def __init__(self, wake_word: str = DEFAULT_WAKE_WORD,
                 cooldown_sec: float = 10.0):

        # ── Configuration ────────────────────────────────────────────
        self.wake_word    = wake_word.lower().strip()
        self.cooldown_sec = cooldown_sec

        # ── Internal state ───────────────────────────────────────────
        self._lock           = threading.Lock()   # protects flag + text
        self._emergency_flag = False              # True when emergency detected
        self._emergency_text = ""                 # captured command text

        self._last_trigger_t = 0.0   # timestamp of last triggered alert
        self._running        = False  # controls the listen loop
        self._thread         = None  # background thread reference

        # ── Availability flag ────────────────────────────────────────
        # Set to False if libraries or microphone are unavailable.
        # The fall detection system checks this to skip integration calls.
        self.available = False   # will be set True in start() if OK

    # ────────────────────────────────────────────────────────────────
    # Public API
    # ────────────────────────────────────────────────────────────────

    def start(self):
        """
        Start the background listening thread.

        Attempts to import SpeechRecognition, sounddevice, and numpy.
        If any import fails, prints a warning and returns without
        starting the thread (self.available remains False).

        Also performs a small test recording with sounddevice to
        verify that the microphone hardware is accessible.

        This method is safe to call from main() before the camera loop.
        """
        # ── Step 1: try importing required libraries ─────────────────
        try:
            import speech_recognition as sr   # noqa: F401
            import sounddevice as sd          # noqa: F401
            import numpy as np                # noqa: F401
        except ImportError as exc:
            print(
                f"[SANJEEVANI] ⚠ Voice assistant disabled — "
                f"missing library: {exc}\n"
                f"  Install with: "
                f"pip install SpeechRecognition sounddevice numpy"
            )
            return   # assistant stays disabled; pipeline continues normally

        # ── Step 2: test microphone access via sounddevice ───────────
        # Record 1 sample — just verifies the device opens without error.
        # This is intentionally PyAudio-free: we never call sr.Microphone().
        try:
            import sounddevice as sd
            sd.rec(1, samplerate=SAMPLE_RATE, channels=1, dtype="int16")
            sd.wait()
        except Exception as exc:
            print(
                f"[SANJEEVANI] ⚠ Voice assistant disabled — "
                f"sounddevice microphone test failed: {exc}"
            )
            return   # assistant stays disabled

        # ── Step 3: all checks passed — mark as available ────────────
        self.available = True
        self._running  = True

        # ── Step 4: launch background daemon thread ──────────────────
        # daemon=True ensures the thread does not block program exit.
        self._thread = threading.Thread(
            target=self._listen_loop,
            name="SanjeevaniVoiceThread",
            daemon=True,
        )
        self._thread.start()

        print(
            f"[SANJEEVANI] ✅ Voice assistant started — "
            f"wake word: '{self.wake_word}' | "
            f"cooldown: {self.cooldown_sec}s"
        )

    def stop(self):
        """
        Signal the background thread to stop and wait for it to finish.

        Safe to call even if the assistant was never started or is disabled.
        """
        self._running = False

        if self._thread is not None and self._thread.is_alive():
            # Thread checks _running at the top of each loop iteration.
            self._thread.join(timeout=5.0)

        print("[SANJEEVANI] Voice assistant stopped.")

    def consume_emergency(self):
        """
        Thread-safe read-and-reset of the emergency flag.

        Returns
        -------
        (True,  command_text)  — emergency was detected; flag is reset.
        (False, "")            — no emergency pending.

        Calling this repeatedly after a single detection returns
        (False, "") until the next emergency occurs (auto-reset behaviour).
        """
        with self._lock:
            if self._emergency_flag:
                # Reset immediately so the same event isn't consumed twice.
                self._emergency_flag = False
                text = self._emergency_text
                self._emergency_text = ""
                return True, text

        return False, ""

    # ────────────────────────────────────────────────────────────────
    # Background listen loop (runs in daemon thread)
    # ────────────────────────────────────────────────────────────────

    def _listen_loop(self):
        """
        Infinite loop that:
          1. Records an audio chunk from the microphone using sounddevice.
          2. Converts the numpy PCM array to sr.AudioData (no PyAudio needed).
          3. Converts AudioData to text via Google STT.
          4. Detects wake word variation + emergency keyword.
          5. Sets the emergency flag if conditions are met.

        Each iteration is fully wrapped in try/except — any error is logged
        and the loop continues so the fall detection pipeline is never affected.
        """
        # ── Import here (already verified in start()) ────────────────
        # Deferred import so module-level import never raises ImportError.
        import speech_recognition as sr
        import sounddevice as sd
        import numpy as np

        recognizer = sr.Recognizer()

        print("[SANJEEVANI] Listening for wake word…")

        # ── Main listen loop ─────────────────────────────────────────
        while self._running:
            try:
                # ── Step A: record audio chunk with sounddevice ──────
                # sd.rec() is non-blocking by default; sd.wait() blocks
                # until recording is complete. This happens inside the
                # daemon thread and does NOT affect the main thread.
                #
                # dtype="int16" gives 16-bit PCM — what Google STT expects.
                # channels=1   = mono (speech recognition works on mono).
                num_samples = int(SAMPLE_RATE * LISTEN_PHRASE_SEC)

                raw_array = sd.rec(
                    num_samples,
                    samplerate=SAMPLE_RATE,
                    channels=1,
                    dtype="int16",
                )
                sd.wait()   # blocks daemon thread only — main thread is free

                # ── Step B: convert numpy array → PCM bytes → AudioData
                pcm_bytes = raw_array.tobytes()

                # sr.AudioData(frame_data, sample_rate, sample_width)
                # sample_width = 2 because int16 = 2 bytes per sample.
                # This is the ONLY SpeechRecognition class we use — no
                # sr.Microphone() and therefore no PyAudio dependency.
                audio_data = sr.AudioData(pcm_bytes, SAMPLE_RATE, 2)

                # ── Step C: convert audio to text (Google STT) ───────
                # Uses the free Google Web Speech API (no API key needed).
                # Replace with recognizer.recognize_vosk(audio_data) for
                # fully offline recognition (requires vosk package).
                try:
                    raw_text = recognizer.recognize_google(audio_data)
                except sr.UnknownValueError:
                    # Audio was captured but speech could not be understood.
                    # Common during silence or background noise — not an error.
                    continue
                except sr.RequestError as exc:
                    # Network error or Google API unavailable.
                    print(f"[SANJEEVANI] ⚠ STT request error: {exc}")
                    time.sleep(RETRY_SLEEP_SEC)
                    continue

                # ── Step D: normalise to lowercase for matching ───────
                text = raw_text.lower().strip()
                print(f"[SANJEEVANI] Heard: '{text}'")

                # ── Step E: check for wake word ──────────────────────
                # Wake word must be present anywhere in the transcription.
                # We check multiple spelling variations because Google may
                # transcribe "Sanjeevani" as "Sanjivani", "Sanjeevni", etc.
                wake_detected = any(wake in text for wake in WAKE_WORDS)

                if not wake_detected:
                    # Not addressed to Sanjeevani — ignore silently.
                    continue

                # ── Step F: check for emergency keyword ─────────────
                detected_keyword = None
                for keyword in EMERGENCY_KEYWORDS:
                    if keyword in text:
                        detected_keyword = keyword
                        break

                if detected_keyword is None:
                    # Wake word heard but no emergency content — acknowledge only.
                    print(
                        f"[SANJEEVANI] Wake word detected but no "
                        f"emergency keyword in: '{text}'"
                    )
                    continue

                # ── Step G: cooldown check ───────────────────────────
                now = time.time()
                if now - self._last_trigger_t < self.cooldown_sec:
                    remaining = self.cooldown_sec - (now - self._last_trigger_t)
                    print(
                        f"[SANJEEVANI] Emergency suppressed — "
                        f"cooldown active ({remaining:.1f}s remaining)"
                    )
                    continue

                # ── Step H: set emergency flag (thread-safe) ─────────
                self._last_trigger_t = now

                with self._lock:
                    self._emergency_flag = True
                    self._emergency_text = text   # full transcribed command

                print(
                    f"[SANJEEVANI] 🚨 EMERGENCY DETECTED — "
                    f"command: '{text}' | keyword: '{detected_keyword}'"
                )

            except Exception as exc:
                # Catch-all: any unexpected error in one iteration must NOT
                # crash the thread or the fall detection pipeline.
                logger.warning("[SANJEEVANI] Unexpected error: %s", exc)
                print(f"[SANJEEVANI] ⚠ Unexpected error in listen loop: {exc}")
                time.sleep(RETRY_SLEEP_SEC)

        # Loop exited cleanly (self._running set to False by stop())
        print("[SANJEEVANI] Listen loop exited.")

    # ────────────────────────────────────────────────────────────────
    # Helpers
    # ────────────────────────────────────────────────────────────────

    def is_available(self) -> bool:
        """
        Returns True if the voice assistant started successfully.
        Use this in main.py to decide whether to call consume_emergency().
        """
        return self.available

    def __repr__(self) -> str:
        return (
            f"VoiceAssistant("
            f"wake_word='{self.wake_word}', "
            f"available={self.available}, "
            f"running={self._running})"
        )