"""
phase3_test.py
==============

SANJEEVANI AI — PHASE 3 TEST

PHASE 1 (unchanged, reused as-is):

    LYING
    LYING + MOVEMENT
    NOT LYING

PHASE 2 (unchanged, reused as-is):

    NORMAL
    DANGER      — RESULT stayed exactly "LYING" for
                  LYING_DANGER_SECONDS (20s) continuously.
    RECOVERY    — sustained non-LYING evidence for RECOVERY_SECONDS
                  while in DANGER clears it. Reverting to plain
                  "LYING" mid-recovery cancels the countdown and
                  returns straight to DANGER.

PHASE 3 (new, this file): ESCALATION

    While danger is True, an escalation clock runs from the moment
    danger started (danger_started_at) — NOT reset by a cancelled
    recovery attempt, since danger never actually cleared during
    one. Three levels fire once each, in order, and stack (firing
    Level 2 does not undo Level 1 — the check-in stays active):

        Level 1 (t=0s,  i.e. immediately when danger starts)
        Speaks "Are you okay?" (pyttsx3) and listens for a verbal
        answer (speech_recognition) for up to
        LEVEL1_LISTEN_TIMEOUT_SECONDS.
            "yes"           -> danger fully cleared immediately
                               (stronger evidence than movement, so
                               skips Phase 2's normal 10s movement-
                               recovery countdown), then a
                               LEVEL1_GRACE_PERIOD_SECONDS grace
                               period starts during which danger
                               will NOT re-trigger even if the
                               person stays lying — avoids nagging
                               "Are you okay?" every 20s during a
                               normal nap.
            "no" or silence -> Level 2 fires immediately, skipping
                               the normal 20s wait.
        Runs in a background thread so the video loop doesn't
        freeze for up to 10s. Falls back to a plain printed message
        (old behavior, normal 20s/60s timers apply) if pyttsx3 /
        speech_recognition / a working mic+speaker aren't
        available — the rest of the pipeline still runs either way.

        Install with: pip install pyttsx3 SpeechRecognition
        sounddevice numpy
        (sounddevice instead of PyAudio — no C compiler needed,
        ships a prebuilt PortAudio binary in the wheel on Windows)
    Level 2 (t=20s of sustained danger, or immediately on a "no"/
             silence verbal response to Level 1)
        Simulated caregiver notification.
    Level 3 (t=60s of sustained danger)
        Simulated emergency escalation.

    When danger clears (RECOVERY CONFIRMED), escalation fully
    resets to 0 for the next episode. Alerts already fired are not
    retracted.

    This is a TEST HARNESS — Level 2/3 "notifications" are
    simulated (printed/logged), not real, since alert_system.py is
    off-limits for now.

This file does NOT modify the existing Sanjeevani source files,
and does NOT modify phase1_test.py / phase2_test.py — the
posture-stabilization and danger/recovery functions below are
carried over unchanged; only the main loop adds the Phase 3
escalation layer on top of the Phase 2 label.

DO NOT TOUCH:
    main.py
    feature_extraction.py
    rule_engine.py
    pose_estimation.py
    tracking.py
    alert_system.py

NOT YET IMPLEMENTED (later phases):
    FALL CONFIRMATION (fall-signature detection, bed-zone bypass)
    Real ALERTS (SMS / caregiver notification / emergency integration)
    Multi-person tracking

VOICE CHECK-IN (Level 1):
    Level 1 now speaks "Are you okay?" (pyttsx3, offline TTS) and
    listens for a spoken answer (SpeechRecognition + microphone,
    via Google's free recognizer — needs internet on your machine
    at runtime) for VOICE_LISTEN_TIMEOUT_SECONDS (10s):

        "yes" (or similar)  -> danger clears immediately (stronger
                                signal than movement, skips Phase
                                2's normal recovery countdown), and
                                a GRACE_PERIOD_SECONDS (5 min)
                                window starts where danger won't
                                re-trigger even if still lying —
                                otherwise a resting person would
                                get re-asked every 20s.
        "no" / silence      -> Level 2 fires immediately, skipping
                                the rest of its normal wait.

    Runs in a background thread so the camera loop keeps
    processing frames (and could still detect a real emergency)
    while waiting on TTS/STT, which are blocking calls.

    Requires pyaudio (and system portaudio) for microphone input.
    If pyttsx3/speech_recognition/pyaudio aren't installed, voice
    check-in is automatically disabled and Level 1 falls back to
    print-only (old behavior) — the script still runs either way.
"""

import cv2
import time
import threading
import numpy as np
from collections import deque

try:

    import pyttsx3

    import speech_recognition as sr

    import sounddevice as sd

    VOICE_AVAILABLE = True

except ImportError:

    VOICE_AVAILABLE = False

    print(
        "[INFO] pyttsx3 / speech_recognition / sounddevice not "
        "available — Level 1 voice check-in disabled, falling "
        "back to print-only."
    )

from modules.person_detection import PersonDetector
from modules.tracking import CentroidTracker
from modules.pose_estimation import PoseEstimator
from modules.feature_extraction import FeatureExtractor


# ================================================================
# CONFIGURATION
# ================================================================

MODEL_PATH = "fall_detection/models/yolov8n.pt"


# ================================================================
# VIDEO SOURCE
# ================================================================

# Webcam
VIDEO_SOURCE = 0

# For video testing, use:
# VIDEO_SOURCE = "your_video.avi"


# ================================================================
# MOVEMENT SETTINGS
# ================================================================

MOVEMENT_OBSERVATION_THRESHOLD = 2.0

MOVEMENT_WINDOW_FRAMES = 5

MOVEMENT_REQUIRED_FRAMES = 2

MOVEMENT_RELEASE_REQUIRED_FRAMES = 3


# ================================================================
# INITIAL POSTURE SETTINGS
# ================================================================

# Number of consecutive frames required to establish
# the first stable posture.

POSTURE_CONFIRM_FRAMES = 3

# Window (in frames) used to vote on a posture change.
#
# A posture is confirmed once it wins POSTURE_CONFIRM_FRAMES votes
# within the last POSTURE_VOTE_WINDOW frames — the votes do NOT
# need to be consecutive.
#
# This is what makes lock-in robust to single-frame pose jitter
# (common when a person is lying still and the pose is borderline
# between Lying/Sitting) without requiring an unbroken streak,
# which is easy to get when there's visible movement but hard to
# get when perfectly still.

POSTURE_VOTE_WINDOW = 6


# ================================================================
# LYING -> NOT LYING SETTINGS
# ================================================================

# Once the system is in LYING state, it will not immediately
# switch to NOT LYING because of one noisy Sitting/Standing frame.
#
# This is a WINDOWED VOTE (like POSTURE_VOTE_WINDOW above), not a
# consecutive-frame streak: LYING_EXIT_FRAMES non-Lying readings
# must appear somewhere within the last LYING_EXIT_VOTE_WINDOW
# frames before leaving LYING.
#
# NOTE: an earlier version of this required a strictly UNBROKEN
# consecutive run of non-Lying frames, and reset to zero on any
# single raw=Lying reading. That failed badly in testing: while
# the person was genuinely sitting for many seconds, an occasional
# stray raw=Lying frame (pose/angle noise) kept resetting the
# streak to zero, so it could get stuck reporting "Lying" long
# after the person had sat up. The windowed vote fixes that — a
# lone contrary frame no longer erases all prior evidence.

LYING_EXIT_VOTE_WINDOW = 25

LYING_EXIT_FRAMES = 15


# ================================================================
# PHASE 2 CONFIGURATION — DANGER / RECOVERY
# ================================================================

# How many continuous seconds of RESULT == "LYING" (no movement)
# before raising danger.
#
# Uses wall-clock time (time.time()), not a frame count, so it
# stays correct regardless of camera FPS or dropped frames.
#
# A single frame where RESULT != "LYING" resets this timer to
# zero — no partial credit. RESULT is already Phase 1's debounced
# output (its own windowed votes have already filtered raw noise),
# so an interruption here reflects a real change, not jitter.

LYING_DANGER_SECONDS = 20.0

# How many continuous seconds of recovery evidence (RESULT !=
# "LYING", OR the person is not detected at all) are required
# while in DANGER before danger is cleared.
#
# If RESULT reverts to plain "LYING" at any point during this
# countdown, recovery is cancelled immediately and we return
# straight to DANGER — no re-run of LYING_DANGER_SECONDS, since
# we already have grounds for concern.

RECOVERY_SECONDS = 10.0


# ================================================================
# PHASE 3 CONFIGURATION — ESCALATION
# ================================================================

# How many seconds into a sustained danger episode each level
# fires, measured from when danger first became True
# (danger_started_at). Each fires once; levels stack (a higher
# level does not cancel a lower one already fired).
#
# 0s   -> Level 1 fires the instant danger starts. Cheap/local
#         action (a check-in), so there's no reason to delay it —
#         Phase 2's own LYING_DANGER_SECONDS is already the "wait
#         and see" period before danger even becomes True.
# 20s  -> Level 2. Real-world cost (would notify a caregiver), so
#         it waits for sustained danger past Level 1.
# 60s  -> Level 3. Highest cost (would be a real emergency
#         escalation), so it waits longest.

LEVEL_1_SECONDS = 0.0

LEVEL_2_SECONDS = 20.0

LEVEL_3_SECONDS = 60.0


# ================================================================
# PHASE 3 CONFIGURATION — VOICE CHECK-IN (Level 1)
# ================================================================

# How long to listen for a spoken answer after asking "Are you
# okay?" before treating it as silence (-> escalate like "no").

VOICE_LISTEN_TIMEOUT_SECONDS = 10.0

# How long, after a "yes" answer, danger will NOT re-trigger even
# if the person is still lying still. Without this, a resting
# person who answers "yes" would get re-asked every
# LYING_DANGER_SECONDS (20s) forever.

GRACE_PERIOD_SECONDS = 300.0  # 5 minutes

# Simple keyword matching on the recognized speech text (already
# lowercased before checking). Listed roughly most-specific-first;
# checked in order, first match wins. Kept simple and easy to
# extend — no need to be exhaustive, ambiguous/unmatched speech
# falls through to the "no" side (silence) deliberately, since an
# unclear answer during a possible fall is not a safe answer.

YES_KEYWORDS = [
    "yes",
    "yeah",
    "yep",
    "i'm okay",
    "im okay",
    "i'm fine",
    "im fine",
    "fine",
    "okay",
]

NO_KEYWORDS = [
    "no",
    "not okay",
    "not fine",
    "help",
]


# ================================================================
# PER-PERSON MOVEMENT HISTORY
# ================================================================

movement_history = {}

movement_state = {}


# ================================================================
# PER-PERSON POSTURE STATE
# ================================================================

# Current stable posture:
#
# object_id -> "Lying"
# object_id -> "Sitting"
# object_id -> "Standing"

stable_posture = {}


# Sliding window of recent raw_posture readings, used to vote on
# whether a posture change is real or just single-frame jitter.
#
# object_id -> deque[str] of the last POSTURE_VOTE_WINDOW raw
# posture labels.

posture_history = {}


# ================================================================
# LYING EXIT HISTORY
# ================================================================

# Sliding window of recent raw_posture readings collected while
# stable posture is "Lying", used to vote on whether there's
# enough non-Lying evidence to exit — see LYING_EXIT_VOTE_WINDOW /
# LYING_EXIT_FRAMES above.

lying_exit_history = {}


# ================================================================
# GET MOVEMENT HISTORY
# ================================================================

def get_movement_history(object_id):

    if object_id not in movement_history:

        movement_history[object_id] = deque(
            maxlen=MOVEMENT_WINDOW_FRAMES
        )

    return movement_history[object_id]


# ================================================================
# GET POSTURE VOTE HISTORY
# ================================================================

def get_posture_history(object_id):

    if object_id not in posture_history:

        posture_history[object_id] = deque(
            maxlen=POSTURE_VOTE_WINDOW
        )

    return posture_history[object_id]


def posture_votes(object_id, label):

    history = get_posture_history(
        object_id
    )

    return sum(
        1
        for entry in history
        if entry == label
    )


def get_lying_exit_history(object_id):

    if object_id not in lying_exit_history:

        lying_exit_history[object_id] = deque(
            maxlen=LYING_EXIT_VOTE_WINDOW
        )

    return lying_exit_history[object_id]


# ================================================================
# MOVEMENT CLASSIFIER
# ================================================================

def classify_lying_movement(object_id, movement):

    history = get_movement_history(
        object_id
    )


    # ------------------------------------------------------------
    # Determine movement in current frame
    # ------------------------------------------------------------

    is_moving_frame = (
        movement >= MOVEMENT_OBSERVATION_THRESHOLD
    )


    history.append(
        is_moving_frame
    )


    # ------------------------------------------------------------
    # Number of movement observations
    # ------------------------------------------------------------

    moving_frames = sum(
        history
    )


    currently_moving = movement_state.get(
        object_id,
        False
    )


    # ============================================================
    # CURRENTLY NOT MOVING
    # ============================================================

    if not currently_moving:

        if (
            moving_frames
            >= MOVEMENT_REQUIRED_FRAMES
        ):

            movement_state[object_id] = True

            return True


        return False


    # ============================================================
    # CURRENTLY MOVING
    # ============================================================

    non_moving_frames = (
        len(history)
        - moving_frames
    )


    if (
        non_moving_frames
        >= MOVEMENT_RELEASE_REQUIRED_FRAMES
    ):

        movement_state[object_id] = False

        return False


    return True


# ================================================================
# INITIAL POSTURE ESTABLISHMENT
# ================================================================

def establish_initial_posture(
    object_id,
    raw_posture
):

    current_posture = stable_posture.get(
        object_id,
        None
    )


    # ------------------------------------------------------------
    # Already established
    # ------------------------------------------------------------

    if current_posture is not None:

        return current_posture


    # ------------------------------------------------------------
    # Cast a vote for this frame's raw posture.
    #
    # NOTE: votes do not need to be consecutive. A single noisy
    # frame (e.g. a person lying still whose pose reads as
    # "Sitting" for one frame due to landmark jitter) no longer
    # wipes out progress the way a strict streak counter did.
    # ------------------------------------------------------------

    history = get_posture_history(
        object_id
    )

    history.append(
        raw_posture
    )

    votes = posture_votes(
        object_id,
        raw_posture
    )


    # ------------------------------------------------------------
    # Confirm initial posture
    # ------------------------------------------------------------

    if votes >= POSTURE_CONFIRM_FRAMES:

        stable_posture[object_id] = (
            raw_posture
        )

        posture_history.pop(
            object_id,
            None
        )

        return raw_posture


    return None


# ================================================================
# PHASE 1 POSTURE STABILIZATION
# ================================================================

def stabilize_phase1_posture(
    object_id,
    raw_posture,
    angle,
    ratio
):

    current_posture = stable_posture.get(
        object_id,
        None
    )


    # ============================================================
    # INITIAL STATE
    # ============================================================

    if current_posture is None:

        return establish_initial_posture(
            object_id,
            raw_posture
        )


    # ============================================================
    # CURRENT STATE = LYING
    # ============================================================

    if current_posture == "Lying":

        # --------------------------------------------------------
        # Cast a vote for this frame's raw posture into a window.
        #
        # IMPORTANT: unlike the old version, a single raw=Lying
        # frame does NOT wipe out prior non-Lying evidence. It's
        # just one more vote in the window. A person who has
        # genuinely sat up can still occasionally get a stray
        # raw=Lying reading (pose/angle noise) without resetting
        # the exit countdown back to zero every time.
        # --------------------------------------------------------

        history = get_lying_exit_history(
            object_id
        )

        history.append(
            raw_posture
        )

        non_lying_votes = sum(
            1
            for p in history
            if p != "Lying"
        )


        # --------------------------------------------------------
        # Confirm genuine posture change
        # --------------------------------------------------------

        if non_lying_votes >= LYING_EXIT_FRAMES:

            # ----------------------------------------------------
            # Pick Sitting vs Standing by majority vote within the
            # window (not just this frame's raw_posture, which may
            # itself be a stray Lying reading).
            # ----------------------------------------------------

            standing_votes = sum(
                1
                for p in history
                if p == "Standing"
            )

            sitting_votes = sum(
                1
                for p in history
                if p == "Sitting"
            )

            if standing_votes > sitting_votes:

                stable_posture[object_id] = (
                    "Standing"
                )

            else:

                stable_posture[object_id] = (
                    "Sitting"
                )


            # Reset for next time.

            lying_exit_history.pop(
                object_id,
                None
            )


            # ----------------------------------------------------
            # Clear movement state.
            #
            # Movement is only relevant while lying.
            # ----------------------------------------------------

            movement_history.pop(
                object_id,
                None
            )

            movement_state.pop(
                object_id,
                None
            )


            return stable_posture[object_id]


        # --------------------------------------------------------
        # Not enough non-Lying evidence yet.
        #
        # IMPORTANT:
        # Keep stable state = Lying.
        # --------------------------------------------------------

        return "Lying"


    # ============================================================
    # CURRENT STATE = SITTING / STANDING
    # ============================================================

    # ------------------------------------------------------------
    # If raw posture is Lying, start Lying confirmation.
    # ------------------------------------------------------------

    # ------------------------------------------------------------
    # RAW POSTURE AGREES WITH CURRENT STATE
    #
    # Checked first: no transition in progress, so clear any
    # stale votes from an earlier flicker that never confirmed.
    # ------------------------------------------------------------

    if raw_posture == current_posture:

        posture_history.pop(
            object_id,
            None
        )


        return current_posture


    # ------------------------------------------------------------
    # raw_posture differs from current_posture (Lying, or a
    # different Sitting/Standing reading). Cast a vote for it.
    #
    # Votes need not be consecutive, so a single noisy frame
    # (common while lying still, near the Lying/Sitting boundary)
    # no longer resets progress to zero the way a strict
    # consecutive-streak counter did.
    # ------------------------------------------------------------

    history = get_posture_history(
        object_id
    )

    history.append(
        raw_posture
    )

    votes = posture_votes(
        object_id,
        raw_posture
    )


    # ------------------------------------------------------------
    # Confirm new posture
    # ------------------------------------------------------------

    if votes >= POSTURE_CONFIRM_FRAMES:

        stable_posture[object_id] = (
            raw_posture
        )

        posture_history.pop(
            object_id,
            None
        )


        if raw_posture == "Lying":

            lying_exit_history.pop(
                object_id,
                None
            )


        return raw_posture


    # --------------------------------------------------------
    # Not yet confirmed — keep previous stable state.
    # --------------------------------------------------------

    return current_posture


# ================================================================
# CLEANUP PERSON
# ================================================================

def cleanup_person(object_id):

    movement_history.pop(
        object_id,
        None
    )

    movement_state.pop(
        object_id,
        None
    )

    stable_posture.pop(
        object_id,
        None
    )

    posture_history.pop(
        object_id,
        None
    )

    lying_exit_history.pop(
        object_id,
        None
    )


# ================================================================
# PHASE 2 STATE — DANGER / RECOVERY
# ================================================================
#
# Single person only (no per-object_id dict here, unlike Phase 1's
# state above — matches the current scope of Phase 2).
#
#     danger          : bool — True while in DANGER or
#                        RECOVERY_WATCH; False in NORMAL.
#     lying_since      : timestamp (time.time()) when the current
#                        unbroken run of RESULT == "LYING" started,
#                        while danger is False. None when not
#                        currently accumulating (RESULT != "LYING",
#                        or danger is True).
#     recovery_since   : timestamp when the current recovery
#                        countdown started, while danger is True.
#                        None means danger is True but no recovery
#                        evidence has appeared yet (plain DANGER,
#                        not RECOVERY_WATCH).

danger = False

lying_since = None

recovery_since = None


def update_phase2_state(phase1_result):
    """
    Advances the Phase 2 state machine by one frame.

    phase1_result should be one of:
        "LYING", "LYING + MOVEMENT", "NOT LYING",
        "DETECTING POSTURE", or "NO_PERSON"
    (the last two — no confirmed posture yet, or no person visible
    at all this frame — are treated the same as any non-"LYING"
    reading: they reset the NORMAL-state timer, and count as
    recovery evidence during DANGER/RECOVERY_WATCH.)

    Returns the current Phase 2 label to display/log:
        "NORMAL", "DANGER", or "RECOVERY"
    """

    global danger, lying_since, recovery_since, grace_until

    now = time.time()


    # ------------------------------------------------------------
    # STATE: NORMAL (danger == False)
    # ------------------------------------------------------------

    if not danger:

        # --------------------------------------------------------
        # Grace period active (set after a verbal "yes") — suppress
        # danger re-triggering even if RESULT stays "LYING", so a
        # resting person who already answered "yes" doesn't get
        # re-asked "Are you okay?" every LYING_DANGER_SECONDS.
        # --------------------------------------------------------

        if grace_until is not None:

            if now < grace_until:

                lying_since = None

                return "NORMAL"

            else:

                grace_until = None

                print(
                    "[PHASE-2] Grace period ended — "
                    "resuming normal monitoring"
                )


        if phase1_result == "LYING":

            if lying_since is None:

                lying_since = now

            elif (now - lying_since) >= LYING_DANGER_SECONDS:

                danger = True

                lying_since = None

                print()

                print(
                    ">>> [PHASE-2] DANGER DETECTED "
                    f"(lying still for "
                    f"{LYING_DANGER_SECONDS:.0f}s) <<<"
                )

        else:

            # Any non-LYING reading (including DETECTING POSTURE
            # or NO_PERSON) resets the timer — no partial credit.

            lying_since = None


        return "DANGER" if danger else "NORMAL"


    # ------------------------------------------------------------
    # STATE: DANGER or RECOVERY_WATCH (danger == True)
    # ------------------------------------------------------------

    if recovery_since is None:

        # ----------------------------------------------------
        # STATE: DANGER (no recovery countdown running yet)
        # ----------------------------------------------------

        if phase1_result != "LYING":

            recovery_since = now

            print(
                "[PHASE-2] Recovery evidence seen — "
                "starting recovery countdown"
            )

        return "DANGER"


    # ------------------------------------------------------------
    # STATE: RECOVERY_WATCH
    # ------------------------------------------------------------

    if phase1_result == "LYING":

        # Reverted to plain LYING — cancel recovery, back to
        # DANGER. Danger stays True; we do NOT re-run
        # LYING_DANGER_SECONDS.

        recovery_since = None

        print(
            "[PHASE-2] Recovery cancelled — "
            "back to plain LYING"
        )

        return "DANGER"


    if (now - recovery_since) >= RECOVERY_SECONDS:

        danger = False

        lying_since = None

        recovery_since = None

        print(
            "[PHASE-2] RECOVERY CONFIRMED — "
            "danger cleared"
        )

        return "NORMAL"


    return "RECOVERY"


# ================================================================
# PHASE 3 VOICE CHECK-IN (Level 1)
# ================================================================
#
#     voice_checkin_active : True while the background thread is
#                             running (speaking + listening). Guards
#                             against starting a second thread while
#                             one is already in progress.
#     grace_until           : timestamp until which danger should
#                             NOT re-trigger, set after a "yes"
#                             answer. None means no grace period is
#                             active. Checked by Phase 2's NORMAL
#                             state before it starts counting toward
#                             LYING_DANGER_SECONDS.
#     current_episode_id    : incremented each time a new danger
#                             episode starts (see update_phase3_state).
#                             The check-in thread captures this at
#                             spawn time and checks it still matches
#                             before applying its answer — otherwise
#                             the episode already ended a different
#                             way (e.g. physical-movement recovery
#                             completed while the mic was still
#                             listening) and the stale answer must be
#                             discarded rather than re-triggering
#                             escalation on an episode that's over.

voice_checkin_active = False

grace_until = None

current_episode_id = 0


def speak_text(text):
    """
    Speaks `text` aloud (blocking). No-op (just prints) if voice
    libraries aren't available.
    """

    print(
        f"[VOICE] Speaking: \"{text}\""
    )

    if not VOICE_AVAILABLE:

        return


    try:

        engine = pyttsx3.init()

        engine.say(
            text
        )

        engine.runAndWait()

    except Exception as error:

        print(
            f"[VOICE] TTS failed: {error}"
        )


def classify_answer(text):
    """
    Classifies recognized speech text as "yes", "no", or None
    (unmatched — treated the same as silence by the caller).
    """

    text = text.lower()


    for keyword in NO_KEYWORDS:

        if keyword in text:

            return "no"


    for keyword in YES_KEYWORDS:

        if keyword in text:

            return "yes"


    return None


def record_audio(duration_seconds, samplerate=16000):
    """
    Records `duration_seconds` of mono 16-bit audio via sounddevice
    (no PyAudio needed) and returns (raw_pcm_bytes, samplerate).
    Returns (None, None) on any recording error (no mic, device
    busy, etc.).

    Note: unlike sr.Microphone().listen(), this always records the
    full fixed duration rather than stopping early once speech
    ends — simpler, and fine for a short yes/no answer, just means
    the mic stays "listening" for the whole window even after the
    person finishes talking.
    """

    try:

        recording = sd.rec(
            int(duration_seconds * samplerate),
            samplerate=samplerate,
            channels=1,
            dtype="int16"
        )

        sd.wait()

        return recording.tobytes(), samplerate

    except Exception as error:

        print(
            f"[VOICE] Recording error: {error}"
        )

        return None, None


def listen_for_answer():
    """
    Records up to VOICE_LISTEN_TIMEOUT_SECONDS from the microphone
    and returns "yes", "no", or "silence" (covers: no speech
    detected, unrecognized speech, recognition service error, no
    microphone, or voice libraries unavailable — all treated the
    same way, matching the "unclear answer during a possible fall
    is not a safe answer" rule above).
    """

    if not VOICE_AVAILABLE:

        return "silence"


    raw_audio, samplerate = record_audio(
        VOICE_LISTEN_TIMEOUT_SECONDS
    )

    if raw_audio is None:

        return "silence"


    recognizer = sr.Recognizer()

    # sample_width=2 -> 2 bytes/sample, matching dtype="int16"
    # above. This AudioData object needs no PyAudio at all — it's
    # built directly from the PCM bytes sounddevice recorded.

    audio = sr.AudioData(
        raw_audio,
        samplerate,
        2
    )


    try:

        text = recognizer.recognize_google(
            audio
        )

        print(
            f"[VOICE] Heard: \"{text}\""
        )

    except sr.UnknownValueError:

        print(
            "[VOICE] Could not understand speech"
        )

        return "silence"

    except Exception as error:

        print(
            f"[VOICE] Recognition failed: {error}"
        )

        return "silence"


    answer = classify_answer(
        text
    )

    if answer is None:

        print(
            f"[VOICE] Unmatched answer "
            f"(\"{text}\") — treating as silence"
        )

        return "silence"


    return answer


def run_checkin(episode_id):
    """
    Background-thread worker: speak the check-in prompt, listen
    for an answer, then act on it — unless the episode has already
    ended a different way (e.g. physical-movement recovery) by the
    time the answer comes back, in which case the answer is stale
    and discarded.

    Runs in its own thread (started by start_checkin) so the main
    camera loop keeps processing frames — and could still detect
    a worsening situation, or a recovery, — while TTS/STT block
    this thread.
    """

    global danger, lying_since, recovery_since
    global danger_started_at, escalation_level, grace_until
    global voice_checkin_active

    try:

        speak_text(
            "Are you okay?"
        )

        answer = listen_for_answer()


        # ----------------------------------------------------
        # Staleness check: has this danger episode already ended
        # (by ID mismatch) or already been cleared (danger is
        # False) since this thread started? If so, the episode
        # this answer was about is over — applying it now would
        # incorrectly re-trigger escalation on a closed episode.
        # ----------------------------------------------------

        if episode_id != current_episode_id or not danger:

            print(
                "[VOICE] Answer arrived after the episode "
                "already ended — discarding"
            )

            return


        if answer == "yes":

            print(
                "[VOICE] Answer: YES — "
                "clearing danger, starting grace period "
                f"({GRACE_PERIOD_SECONDS:.0f}s)"
            )

            # Fully clear both Phase 2 and Phase 3 state — a
            # verbal "yes" is stronger evidence than movement, so
            # this skips Phase 2's normal 10s recovery countdown
            # rather than routing through RECOVERY_WATCH.

            danger = False

            lying_since = None

            recovery_since = None

            danger_started_at = None

            escalation_level = 0

            grace_until = (
                time.time() + GRACE_PERIOD_SECONDS
            )


        else:

            # "no" or "silence" — both escalate immediately.

            print(
                f"[VOICE] Answer: {answer.upper()} — "
                "escalating to Level 2 immediately"
            )

            if escalation_level < 2:

                escalation_level = 2

                print(
                    ">>> [PHASE-3] LEVEL 2 — Caregiver "
                    "notification sent (simulated) <<<"
                )

    finally:

        voice_checkin_active = False


def start_checkin(episode_id):
    """
    Starts the background check-in thread, if one isn't already
    running. Called once per danger episode, from the Level 1
    branch of update_phase3_state, which passes the current
    episode's ID so the thread can detect staleness later.
    """

    global voice_checkin_active

    if voice_checkin_active:

        return


    voice_checkin_active = True

    thread = threading.Thread(
        target=run_checkin,
        args=(episode_id,),
        daemon=True
    )

    thread.start()


# ================================================================
# PHASE 3 STATE — ESCALATION
# ================================================================
#
# Single person only, matching Phase 2's scope.
#
#     danger_started_at : timestamp when the CURRENT danger episode
#                          began (set once, when danger flips
#                          False -> True). None when danger is
#                          False. Deliberately NOT touched by a
#                          cancelled recovery attempt (Phase 2's
#                          "back to DANGER" path) — danger never
#                          actually cleared during one, so the
#                          episode — and this clock — is the same
#                          one that started at the original fall.
#     escalation_level   : 0 = nothing fired yet this episode.
#                          1/2/3 = highest level fired so far.
#                          Only ever increases within an episode;
#                          reset to 0 only when danger clears.
#     was_danger         : previous frame's danger value, used
#                          only to detect the False->True and
#                          True->False edges.

danger_started_at = None

escalation_level = 0

was_danger = False


def update_phase3_state(danger_now):
    """
    Advances the Phase 3 escalation state by one frame.

    danger_now is Phase 2's current `danger` bool for this frame.

    Returns escalation_level (0-3) after this frame's update, and
    prints a log line the moment any new level fires.
    """

    global danger_started_at, escalation_level, was_danger
    global current_episode_id

    now = time.time()


    # ------------------------------------------------------------
    # EDGE: danger just became True — new episode starts.
    # ------------------------------------------------------------

    if danger_now and not was_danger:

        danger_started_at = now

        escalation_level = 0

        current_episode_id += 1


    # ------------------------------------------------------------
    # EDGE: danger just became False — episode over, full reset.
    #
    # Alerts already fired this episode are NOT retracted (nothing
    # to retract here — this is a test harness; a real system
    # would send an "all clear" separately, out of scope for now).
    # ------------------------------------------------------------

    if not danger_now and was_danger:

        danger_started_at = None

        escalation_level = 0

        print(
            "[PHASE-3] Danger episode ended — "
            "escalation reset"
        )


    was_danger = danger_now


    # ------------------------------------------------------------
    # While danger is active, check each level in order. Each
    # fires at most once per episode (guarded by escalation_level).
    # ------------------------------------------------------------

    if danger_now and danger_started_at is not None:

        elapsed = now - danger_started_at


        if (
            elapsed >= LEVEL_1_SECONDS
            and escalation_level < 1
        ):

            escalation_level = 1

            print()

            print(
                ">>> [PHASE-3] LEVEL 1 — Check-in triggered <<<"
            )

            if VOICE_AVAILABLE:

                start_checkin(current_episode_id)

            else:

                print(
                    "[PHASE-3] Voice unavailable — "
                    "printed-only check-in, normal L2/L3 "
                    "timers apply"
                )


        if (
            elapsed >= LEVEL_2_SECONDS
            and escalation_level < 2
        ):

            escalation_level = 2

            print(
                ">>> [PHASE-3] LEVEL 2 — Caregiver notification "
                "sent (simulated) <<<"
            )


        if (
            elapsed >= LEVEL_3_SECONDS
            and escalation_level < 3
        ):

            escalation_level = 3

            print(
                ">>> [PHASE-3] LEVEL 3 — Emergency escalation "
                "triggered (simulated) <<<"
            )


    return escalation_level


# ================================================================
# INITIALIZE SANJEEVANI MODULES
# ================================================================

detector = PersonDetector(
    MODEL_PATH
)

tracker = CentroidTracker()

pose_estimator = PoseEstimator()

feature_extractor = FeatureExtractor()


# ================================================================
# OPEN VIDEO
# ================================================================

cap = cv2.VideoCapture(
    VIDEO_SOURCE
)


if not cap.isOpened():

    print(
        "[ERROR] Could not open video source."
    )

    print(
        f"[INFO] VIDEO_SOURCE = {VIDEO_SOURCE}"
    )

    raise SystemExit


# ================================================================
# FULLSCREEN WINDOW
# ================================================================

window_name = (
    "Sanjeevani - Phase 3 Escalation Test"
)


cv2.namedWindow(
    window_name,
    cv2.WINDOW_NORMAL
)


cv2.setWindowProperty(
    window_name,
    cv2.WND_PROP_FULLSCREEN,
    cv2.WINDOW_FULLSCREEN
)


# ================================================================
# START MESSAGE
# ================================================================

print("=" * 90)

print(
    "SANJEEVANI AI - PHASE 3"
)

print(
    "ESCALATION TEST (single person)"
)

print("=" * 90)

print()

print(
    "PHASE 1 OUTPUT (unchanged):"
)

print(
    "    LYING"
)

print(
    "    LYING + MOVEMENT"
)

print(
    "    NOT LYING"
)

print()

print(
    "PHASE 2 OUTPUT (unchanged):"
)

print(
    "    NORMAL"
)

print(
    "    DANGER"
)

print(
    "    RECOVERY"
)

print()

print(
    "PHASE 3 OUTPUT (new):"
)

print(
    "    LEVEL 1 — Check-in (local, immediate)"
)

print(
    "    LEVEL 2 — Caregiver notification (simulated)"
)

print(
    "    LEVEL 3 — Emergency escalation (simulated)"
)

print()

print(
    f"DANGER       : ENABLED "
    f"({LYING_DANGER_SECONDS:.0f}s lying still)"
)

print(
    f"RECOVERY     : ENABLED "
    f"({RECOVERY_SECONDS:.0f}s sustained recovery)"
)

print(
    f"ESCALATION   : ENABLED "
    f"(L1={LEVEL_1_SECONDS:.0f}s, "
    f"L2={LEVEL_2_SECONDS:.0f}s, "
    f"L3={LEVEL_3_SECONDS:.0f}s)"
)

if VOICE_AVAILABLE:

    print(
        f"VOICE CHECK-IN : ENABLED "
        f"(listen {VOICE_LISTEN_TIMEOUT_SECONDS:.0f}s, "
        f"grace {GRACE_PERIOD_SECONDS / 60:.0f}min after 'yes')"
    )

else:

    print(
        "VOICE CHECK-IN : UNAVAILABLE "
        "(pyttsx3/SpeechRecognition not installed — "
        "Level 1 will print only, normal L2/L3 timers apply)"
    )

print(
    "FALL         : DISABLED (later phase)"
)

print(
    "REAL ALERTS  : DISABLED (simulated/logged only)"
)

print()

print(
    f"Movement threshold       : "
    f"{MOVEMENT_OBSERVATION_THRESHOLD:.1f}px"
)

print(
    f"Movement window          : "
    f"{MOVEMENT_WINDOW_FRAMES} frames"
)

print(
    f"Movement ON evidence    : "
    f"{MOVEMENT_REQUIRED_FRAMES} frames"
)

print(
    f"Movement OFF evidence   : "
    f"{MOVEMENT_RELEASE_REQUIRED_FRAMES} frames"
)

print()

print(
    f"Initial posture confirm : "
    f"{POSTURE_CONFIRM_FRAMES} frames"
)

print(
    f"Lying exit confirmation : "
    f"{LYING_EXIT_FRAMES} frames"
)

print()

print(
    "Press Q to quit."
)

print("=" * 90)


# ================================================================
# MAIN LOOP
# ================================================================

while True:

    ret, frame = cap.read()


    if not ret:

        print(
            "[INFO] Video ended or frame could not be read."
        )

        break


    display = frame.copy()


    # ============================================================
    # 1. MEDIAPIPE POSE
    # ============================================================

    pose_data = (
        pose_estimator.detect_full_frame(
            frame
        )
    )


    if pose_data is not None:

        pose_estimator.draw_pose(
            display,
            pose_data["all_landmarks"]
        )


    # ============================================================
    # 2. YOLO PERSON DETECTION
    # ============================================================

    boxes = detector.detect(
        frame
    )


    # ============================================================
    # 3. TRACKING
    # ============================================================

    tracked = tracker.update(
        boxes
    )


    # ============================================================
    # 4. CLEANUP LOST PERSON IDS
    # ============================================================

    active_ids = set(
        tracked.keys()
    )


    all_known_ids = (
        set(movement_history.keys())
        |
        set(stable_posture.keys())
        |
        set(lying_exit_history.keys())
    )


    for object_id in list(
        all_known_ids
    ):

        if object_id not in active_ids:

            cleanup_person(
                object_id
            )


    # ============================================================
    # 5. PROCESS EACH PERSON
    # ============================================================

    # Phase 2 input for this frame. Defaults to NO_PERSON — stays
    # this way if `tracked` is empty, or if the one tracked person
    # has no pose/features this frame (both `continue` before
    # phase1_result is computed below). Overwritten with the real
    # phase1_result as soon as it's known. Single person only, so
    # one variable is enough.

    frame_phase1_result = "NO_PERSON"


    for object_id, obj in tracked.items():

        bbox = obj["bbox"]


        # ========================================================
        # GET POSE FOR PERSON
        # ========================================================

        pose = (
            pose_estimator.get_pose_for_bbox(
                pose_data,
                bbox
            )
        )


        if pose is None:

            x1, y1, x2, y2 = bbox


            cv2.putText(
                display,
                f"ID {object_id}: POSE NOT FOUND",
                (
                    x1,
                    max(
                        30,
                        y1 - 15
                    )
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (128, 128, 128),
                2
            )

            continue


        # ========================================================
        # FEATURE EXTRACTION
        # ========================================================

        features = (
            feature_extractor.extract(
                object_id,
                bbox,
                pose
            )
        )


        if features is None:

            continue


        # ========================================================
        # READ FEATURES
        # ========================================================

        raw_posture = features.get(
            "posture",
            "Unknown"
        )


        movement = features.get(
            "movement",
            0.0
        )


        angle = features.get(
            "angle",
            0.0
        )


        ratio = features.get(
            "ratio",
            0.0
        )


        angular_velocity = features.get(
            "angular_velocity",
            0.0
        )


        # ========================================================
        # STABILIZE POSTURE
        # ========================================================

        stable = stabilize_phase1_posture(
            object_id,
            raw_posture,
            angle,
            ratio
        )


        # ========================================================
        # POSTURE NOT YET CONFIRMED
        # ========================================================

        if stable is None:

            phase1_result = (
                "DETECTING POSTURE"
            )

            movement_evidence = 0

            history_string = ""


        # ========================================================
        # STABLE LYING
        # ========================================================

        elif stable == "Lying":

            temporal_movement = (
                classify_lying_movement(
                    object_id,
                    movement
                )
            )


            if temporal_movement:

                phase1_result = (
                    "LYING + MOVEMENT"
                )

            else:

                phase1_result = (
                    "LYING"
                )


            # ----------------------------------------------------
            # Movement debug
            # ----------------------------------------------------

            history = movement_history.get(
                object_id,
                deque()
            )


            movement_evidence = sum(
                history
            )


            history_string = "".join(
                "1"
                if value
                else "0"
                for value in history
            )


        # ========================================================
        # STABLE SITTING / STANDING
        # ========================================================

        else:

            phase1_result = (
                "NOT LYING"
            )


            movement_evidence = 0

            history_string = ""


            # ----------------------------------------------------
            # Movement is irrelevant when not lying.
            # ----------------------------------------------------

            movement_history.pop(
                object_id,
                None
            )

            movement_state.pop(
                object_id,
                None
            )


        # ========================================================
        # PHASE 2 INPUT
        # ========================================================
        #
        # phase1_result is now finalized for this frame (whichever
        # branch above ran). Feed it to Phase 2 — single person,
        # so this just overwrites the frame-level default.

        frame_phase1_result = phase1_result


        # ========================================================
        # DEBUG STATE
        # ========================================================

        exit_history = lying_exit_history.get(
            object_id,
            deque()
        )

        exit_count = sum(
            1
            for p in exit_history
            if p != "Lying"
        )


        # Candidate/vote count are derived from the vote window
        # rather than tracked separately — there's nothing to show
        # once a posture is already the confirmed "stable" state.

        if raw_posture == stable:

            candidate = None

            candidate_count = 0

        else:

            candidate = raw_posture

            candidate_count = posture_votes(
                object_id,
                raw_posture
            )


        # ========================================================
        # TERMINAL OUTPUT
        # ========================================================

        print(
            f"[PHASE-1] "
            f"ID={object_id} | "
            f"raw={raw_posture} | "
            f"stable={stable} | "
            f"candidate={candidate} | "
            f"candidate_count={candidate_count} | "
            f"movement={movement:.2f}px | "
            f"angle={angle:.2f}° | "
            f"ratio={ratio:.2f} | "
            f"ang_vel={angular_velocity:.2f}°/s | "
            f"move_window={history_string} | "
            f"move_evidence={movement_evidence} | "
            f"lying_exit={exit_count}/{LYING_EXIT_FRAMES} | "
            f"RESULT={phase1_result}"
        )


        # ========================================================
        # BOUNDING BOX COLOR
        # ========================================================

        if phase1_result == "LYING":

            box_color = (
                0,
                165,
                255
            )


        elif phase1_result == "LYING + MOVEMENT":

            box_color = (
                255,
                255,
                0
            )


        elif phase1_result == "NOT LYING":

            box_color = (
                0,
                255,
                0
            )


        else:

            box_color = (
                255,
                255,
                255
            )


        # ========================================================
        # DRAW BOUNDING BOX
        # ========================================================

        x1, y1, x2, y2 = bbox


        cv2.rectangle(
            display,
            (x1, y1),
            (x2, y2),
            box_color,
            2
        )


        # ========================================================
        # MAIN RESULT
        # ========================================================

        cv2.putText(
            display,
            phase1_result,
            (
                x1,
                max(
                    35,
                    y1 - 35
                )
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            box_color,
            2
        )


        # ========================================================
        # POSTURE DEBUG
        # ========================================================

        posture_debug = (
            f"Raw: {raw_posture}"
            f" | Stable: {stable}"
        )


        cv2.putText(
            display,
            posture_debug,
            (
                x1,
                y2 + 20
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1
        )


        # ========================================================
        # MOVEMENT DEBUG
        # ========================================================

        movement_debug = (
            f"Movement: {movement:.1f}px"
            f" | Evidence: "
            f"{movement_evidence}/"
            f"{MOVEMENT_WINDOW_FRAMES}"
        )


        cv2.putText(
            display,
            movement_debug,
            (
                x1,
                y2 + 40
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1
        )


        # ========================================================
        # GEOMETRY DEBUG
        # ========================================================

        geometry_debug = (
            f"Angle: {angle:.1f}"
            f" | Ratio: {ratio:.2f}"
        )


        cv2.putText(
            display,
            geometry_debug,
            (
                x1,
                y2 + 60
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1
        )


        # ========================================================
        # LYING EXIT DEBUG
        # ========================================================

        if stable == "Lying":

            exit_debug = (
                f"Non-Lying evidence: "
                f"{exit_count}/"
                f"{LYING_EXIT_FRAMES}"
            )


            cv2.putText(
                display,
                exit_debug,
                (
                    x1,
                    y2 + 80
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1
            )


    # ============================================================
    # 6. PHASE 2 — DANGER / RECOVERY
    # ============================================================
    #
    # Runs once per frame (single person), using whatever
    # phase1_result was finalized above — or "NO_PERSON" if no
    # one was tracked / pose or features were unavailable.

    phase2_label = update_phase2_state(
        frame_phase1_result
    )


    if lying_since is not None:

        lying_elapsed = (
            time.time() - lying_since
        )

    else:

        lying_elapsed = 0.0


    if recovery_since is not None:

        recovery_elapsed = (
            time.time() - recovery_since
        )

    else:

        recovery_elapsed = 0.0


    print(
        f"[PHASE-2] "
        f"input={frame_phase1_result} | "
        f"danger={danger} | "
        f"state={phase2_label} | "
        f"lying_timer={lying_elapsed:.1f}/"
        f"{LYING_DANGER_SECONDS:.0f}s | "
        f"recovery_timer={recovery_elapsed:.1f}/"
        f"{RECOVERY_SECONDS:.0f}s"
    )


    # ============================================================
    # 7. PHASE 3 — ESCALATION
    # ============================================================
    #
    # Runs once per frame, fed by Phase 2's `danger` bool (not by
    # phase2_label — RECOVERY_WATCH still counts as danger==True,
    # matching the "don't reset the escalation clock on a
    # cancelled recovery attempt" design).

    escalation_level = update_phase3_state(
        danger
    )


    if danger_started_at is not None:

        danger_elapsed = (
            time.time() - danger_started_at
        )

    else:

        danger_elapsed = 0.0


    print(
        f"[PHASE-3] "
        f"danger_elapsed={danger_elapsed:.1f}s | "
        f"escalation_level={escalation_level}"
    )


    # ------------------------------------------------------------
    # BANNER OVERLAY
    # ------------------------------------------------------------

    if phase2_label == "DANGER":

        banner_text = "DANGER"

        banner_color = (0, 0, 255)

    elif phase2_label == "RECOVERY":

        banner_text = (
            f"RECOVERY "
            f"({recovery_elapsed:.0f}/"
            f"{RECOVERY_SECONDS:.0f}s)"
        )

        banner_color = (0, 165, 255)

    else:

        banner_text = None

        banner_color = None


    if banner_text is not None:

        cv2.putText(
            display,
            banner_text,
            (
                30,
                70
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.4,
            banner_color,
            4
        )


    # ------------------------------------------------------------
    # ESCALATION OVERLAY
    #
    # Stacked — shows every level fired so far this episode, not
    # just the highest one, since lower levels stay "active"
    # (e.g. the check-in prompt doesn't go away when Level 2 fires).
    # ------------------------------------------------------------

    escalation_lines = []


    if escalation_level >= 1:

        escalation_lines.append(
            (
                "LEVEL 1: ARE YOU OKAY? (check-in)",
                (0, 255, 255)
            )
        )

    if escalation_level >= 1 and voice_checkin_active:

        escalation_lines.append(
            (
                "  Listening for response...",
                (0, 255, 255)
            )
        )

    if escalation_level >= 2:

        escalation_lines.append(
            (
                "LEVEL 2: CAREGIVER NOTIFIED (simulated)",
                (0, 165, 255)
            )
        )

    if escalation_level >= 3:

        escalation_lines.append(
            (
                "LEVEL 3: EMERGENCY ESCALATION (simulated)",
                (0, 0, 255)
            )
        )


    for line_index, (line_text, line_color) in enumerate(
        escalation_lines
    ):

        cv2.putText(
            display,
            line_text,
            (
                30,
                120 + (line_index * 35)
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            line_color,
            2
        )


    # ============================================================
    # DISPLAY
    # ============================================================

    cv2.imshow(
        window_name,
        display
    )


    # ============================================================
    # KEYBOARD
    # ============================================================

    key = (
        cv2.waitKey(1) & 0xFF
    )


    if key == ord("q"):

        break


# ================================================================
# CLEANUP
# ================================================================

cap.release()

cv2.destroyAllWindows()


print()

print("=" * 90)

print(
    "PHASE 3 TEST FINISHED"             
)

print("=" * 90)