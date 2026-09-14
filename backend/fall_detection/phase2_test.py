"""
phase2_test.py
==============

SANJEEVANI AI — PHASE 2 TEST

PHASE 1 (unchanged, reused as-is):

    LYING
    LYING + MOVEMENT
    NOT LYING

PHASE 2 (new, this file):

    DANGER      — RESULT stayed exactly "LYING" (no movement) for
                  LYING_DANGER_SECONDS continuously.
    RECOVERY    — while in DANGER, RESULT became "LYING + MOVEMENT",
                  "NOT LYING", or the person left frame/pose was
                  lost. Counts up for RECOVERY_SECONDS; reaching it
                  clears danger. Reverting to plain "LYING" during
                  the countdown cancels recovery and returns
                  straight to DANGER (no re-run of the original
                  detection timer).

Single person only. No per-object_id danger tracking.

This file does NOT modify the existing Sanjeevani source files,
and does NOT modify phase1_test.py — the posture-stabilization
functions below (stabilize_phase1_posture, classify_lying_movement,
establish_initial_posture, etc.) are carried over unchanged from
phase1_test.py; only the main loop adds the Phase 2 layer on top
of phase1_result.

DO NOT TOUCH:
    main.py
    feature_extraction.py
    rule_engine.py
    pose_estimation.py
    tracking.py
    alert_system.py

NOT YET IMPLEMENTED (later phases):
    FALL CONFIRMATION (fall-signature detection, bed-zone bypass)
    Escalating/repeat alerts
    ALERTS (voice / notification)
    Multi-person danger tracking
"""

import cv2
import time
from collections import deque

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

    global danger, lying_since, recovery_since

    now = time.time()


    # ------------------------------------------------------------
    # STATE: NORMAL (danger == False)
    # ------------------------------------------------------------

    if not danger:

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
    "Sanjeevani - Phase 2 Danger/Recovery Test"
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
    "SANJEEVANI AI - PHASE 2"
)

print(
    "DANGER / RECOVERY TEST (single person)"
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
    "PHASE 2 OUTPUT (new):"
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
    f"DANGER       : ENABLED "
    f"({LYING_DANGER_SECONDS:.0f}s lying still)"
)

print(
    f"RECOVERY     : ENABLED "
    f"({RECOVERY_SECONDS:.0f}s sustained recovery)"
)

print(
    "FALL         : DISABLED (later phase)"
)

print(
    "ALERT SYSTEM : DISABLED (later phase)"
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
    "PHASE 2 TEST FINISHED"
)

print("=" * 90)