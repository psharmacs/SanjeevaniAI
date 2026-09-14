import cv2
import sys
import time
from pathlib import Path


# ============================================================
# PROJECT PATH SETUP
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent

FALL_DETECTION_PATH = PROJECT_ROOT / "fall_detection"

HEART_RATE_PATH = PROJECT_ROOT / "heart_rate"


# Add project root
if str(PROJECT_ROOT) not in sys.path:

    sys.path.insert(
        0,
        str(PROJECT_ROOT)
    )


# Add heart_rate folder
#
# Your heart_rate_system.py uses imports such as:
#
# from validator import HeartRateValidator
# from processor import HeartRateProcessor
# from analyzer import HeartRateAnalyzer
# from alert_manager import HeartRateAlertManager
#
# Therefore heart_rate must be in sys.path.
#
if str(HEART_RATE_PATH) not in sys.path:

    sys.path.insert(
        0,
        str(HEART_RATE_PATH)
    )


# ============================================================
# IMPORT BED ZONE
# ============================================================

from fall_detection.bed_zone1 import BedZoneDetector


# ============================================================
# IMPORT HEART RATE
# ============================================================

from heart_rate.heart_rate_system import HeartRateSystem

from heart_rate.simulator import HeartRateSimulator


# ============================================================
# CONFIGURATION
# ============================================================

CAMERA_INDEX = 0

# ------------------------------------------------------------
# YOLO MODEL
#
# FIXED: this was "yolov8n.pt" (nano), which overrode
# bed_zone1.py's own default of "yolov8s.pt" because it's
# passed explicitly below. The nano model gives much weaker,
# borderline confidence on lying-down poses, which is why
# this integrated script failed to detect "inside bed" even
# though bed_zone1.py worked fine standalone.
# ------------------------------------------------------------

YOLO_MODEL = "yolov8s.pt"

# ------------------------------------------------------------
# YOUR SAVED BED ZONE
# ------------------------------------------------------------

BED_ZONE = (
    556,
    295,
    1083,
    518
)

# ------------------------------------------------------------
# YOLO CONFIDENCE
# ------------------------------------------------------------

YOLO_CONFIDENCE = 0.25

# ------------------------------------------------------------
# TEMPORAL SMOOTHING (DEBOUNCE)
#
# bed_zone1.py supports these too - pass them explicitly here
# so the integrated system gets the same flicker-smoothing
# behavior as the standalone script.
# ------------------------------------------------------------

MISS_TOLERANCE = 10

CONFIRM_FRAMES = 3

# ------------------------------------------------------------
# HEART RATE INTERVAL
# ------------------------------------------------------------

HR_INTERVAL = 1.0


# ============================================================
# CREATE NEW HEART RATE SYSTEM
# ============================================================

def create_heart_rate_system():

    return HeartRateSystem()


# ============================================================
# GET HEART RATE READING
# ============================================================
#
# Different versions of your simulator have used:
#
# 1. generate_reading()
#
# 2. get_next_reading()
#
# This function supports both.
#
# ============================================================

def get_heart_rate_reading(simulator):

    # --------------------------------------------------------
    # CURRENT SIMULATOR
    # --------------------------------------------------------

    if hasattr(
        simulator,
        "generate_reading"
    ):

        reading = simulator.generate_reading()

        return (
            reading["heart_rate"],
            reading["timestamp"]
        )


    # --------------------------------------------------------
    # OLDER SIMULATOR
    # --------------------------------------------------------

    elif hasattr(
        simulator,
        "get_next_reading"
    ):

        heart_rate = (
            simulator.get_next_reading()
        )

        timestamp = time.strftime(
            "%Y-%m-%dT%H:%M:%S"
        )

        return (
            heart_rate,
            timestamp
        )


    # --------------------------------------------------------
    # NO VALID METHOD
    # --------------------------------------------------------

    else:

        raise AttributeError(
            "HeartRateSimulator does not have "
            "generate_reading() or "
            "get_next_reading()."
        )


# ============================================================
# DRAW INTEGRATED STATUS
# ============================================================

def draw_integrated_status(
    frame,
    person_detected,
    inside_bed,
    hr_result
):

    # ========================================================
    # PERSON STATUS
    # ========================================================

    if not person_detected:

        person_text = (
            "PERSON: NOT DETECTED"
        )

    elif inside_bed:

        person_text = (
            "PERSON: INSIDE BED"
        )

    else:

        person_text = (
            "PERSON: OUTSIDE BED"
        )


    # ========================================================
    # PERSON STATUS BOX
    # ========================================================

    cv2.rectangle(
        frame,
        (10, 10),
        (560, 65),
        (0, 0, 0),
        -1
    )

    cv2.putText(
        frame,
        person_text,
        (20, 48),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        (255, 255, 255),
        2
    )


    # ========================================================
    # HEART RATE STATUS
    # ========================================================

    # --------------------------------------------------------
    # PERSON NOT DETECTED
    # --------------------------------------------------------

    if not person_detected:

        hr_text = (
            "HEART RATE: OFF"
        )

        hr_color = (
            0,
            0,
            255
        )


    # --------------------------------------------------------
    # PERSON OUTSIDE BED
    # --------------------------------------------------------

    elif not inside_bed:

        hr_text = (
            "HEART RATE: OFF"
        )

        hr_color = (
            0,
            165,
            255
        )


    # --------------------------------------------------------
    # PERSON INSIDE BED
    # --------------------------------------------------------

    else:

        # ----------------------------------------------------
        # HR SYSTEM STARTING
        # ----------------------------------------------------

        if hr_result is None:

            hr_text = (
                "HEART RATE: STARTING"
            )

            hr_color = (
                0,
                255,
                255
            )

        else:

            # =================================================
            # GET RESULT
            # =================================================

            reading = hr_result.get(
                "reading",
                {}
            )

            processor = hr_result.get(
                "processor"
            )

            analyzer = hr_result.get(
                "analyzer",
                {}
            )

            # -------------------------------------------------
            # HEART RATE
            # -------------------------------------------------

            heart_rate = reading.get(
                "heart_rate"
            )

            # -------------------------------------------------
            # ANALYZER STATUS
            # -------------------------------------------------

            status = analyzer.get(
                "status",
                "NO_DATA"
            )

            # -------------------------------------------------
            # SMOOTHED HR
            # -------------------------------------------------

            smoothed_hr = None

            if processor is not None:

                smoothed_hr = processor.get(
                    "smoothed_hr"
                )


            # =================================================
            # CREATE HR TEXT
            # =================================================

            # -------------------------------------------------
            # REASON
            #
            # e.g. "Heart rate rising rapidly",
            #      "Heart rate dropping",
            #      etc. Comes from your analyzer.
            # -------------------------------------------------

            reason = analyzer.get(
                "reason"
            )

            if heart_rate is not None:

                if smoothed_hr is not None:

                    hr_text = (
                        f"HR: {heart_rate} BPM | "
                        f"SMOOTHED: {smoothed_hr} | "
                        f"{status}"
                    )

                else:

                    hr_text = (
                        f"HR: {heart_rate} BPM | "
                        f"{status}"
                    )

                if reason:

                    hr_text += (
                        f" | {reason}"
                    )

            else:

                hr_text = (
                    "HEART RATE: NO DATA | "
                    f"{status}"
                )


            # =================================================
            # HR COLOR
            # =================================================

            if status == "ALERT":

                hr_color = (
                    0,
                    0,
                    255
                )

            elif status == "WATCH":

                hr_color = (
                    0,
                    165,
                    255
                )

            else:

                hr_color = (
                    0,
                    255,
                    0
                )


    # ========================================================
    # DRAW HEART RATE BOX
    # ========================================================

    cv2.rectangle(
        frame,
        (10, 75),
        (1000, 130),
        (0, 0, 0),
        -1
    )

    cv2.putText(
        frame,
        hr_text,
        (20, 110),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        hr_color,
        2
    )


    # ========================================================
    # DANGER ALERT BANNER
    #
    # This is only drawn on frames where the analyzer status
    # is "ALERT". It is rebuilt fresh every frame from the
    # current status, so it disappears on its own the moment
    # the alert clears - no separate "hide" logic needed.
    # ========================================================

    if (
        person_detected
        and
        inside_bed
        and
        hr_result is not None
    ):

        analyzer = hr_result.get(
            "analyzer",
            {}
        )

        status = analyzer.get(
            "status"
        )

        if status == "ALERT":

            reason = analyzer.get(
                "reason"
            )

            danger_text = (
                "⚠ DANGER: "
                f"{reason}"
                if reason else
                "⚠ DANGER: HEART RATE ALERT"
            )

            frame_height, frame_width = (
                frame.shape[0],
                frame.shape[1]
            )

            banner_y1 = 140

            banner_y2 = 195

            cv2.rectangle(
                frame,
                (10, banner_y1),
                (min(frame_width - 10, 1000), banner_y2),
                (0, 0, 255),
                -1
            )

            cv2.putText(
                frame,
                danger_text,
                (20, banner_y1 + 38),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2
            )


    return frame


# ============================================================
# PRINT HEART RATE RESULT
# ============================================================

def print_heart_rate_result(
    result
):

    if result is None:

        return


    # ========================================================
    # READING
    # ========================================================

    reading = result.get(
        "reading",
        {}
    )


    # ========================================================
    # PROCESSOR
    # ========================================================

    processor = result.get(
        "processor"
    )


    # ========================================================
    # ANALYZER
    # ========================================================

    analyzer = result.get(
        "analyzer",
        {}
    )


    # ========================================================
    # ALERT
    # ========================================================

    alert = result.get(
        "alert",
        {}
    )


    print()

    print(
        "-" * 75
    )


    # ========================================================
    # BASIC READING
    # ========================================================

    print(
        f"Time: "
        f"{reading.get('timestamp')}"
    )

    print(
        f"HR: "
        f"{reading.get('heart_rate')} BPM"
    )


    # ========================================================
    # PROCESSOR
    # ========================================================

    if processor is not None:

        print(
            f"Smoothed HR: "
            f"{processor.get('smoothed_hr')}"
        )

        print(
            f"Average HR: "
            f"{processor.get('average_hr')}"
        )

        print(
            f"Trend: "
            f"{processor.get('trend')}"
        )

        print(
            f"Artifact: "
            f"{processor.get('artifact')}"
        )


    # ========================================================
    # ANALYZER
    # ========================================================

    print(
        f"HR Status: "
        f"{analyzer.get('status')}"
    )

    print(
        f"Reason: "
        f"{analyzer.get('reason')}"
    )


    # ========================================================
    # ALERT MANAGER
    # ========================================================

    print(
        f"Alert Action: "
        f"{alert.get('action')}"
    )

    print(
        f"Priority: "
        f"{alert.get('priority')}"
    )

    print(
        f"Notification: "
        f"{alert.get('notification')}"
    )


    print(
        "-" * 75
    )


# ============================================================
# MAIN
# ============================================================

def main():

    # ========================================================
    # HEADER
    # ========================================================

    print(
        "=" * 75
    )

    print(
        "❤️ SANJEEVANI AI"
    )

    print(
        "   INTEGRATED BED + HEART RATE MONITORING"
    )

    print(
        "=" * 75
    )


    # ========================================================
    # CONFIGURATION DISPLAY
    # ========================================================

    print()

    print(
        "Bed Zone:"
    )

    print(
        f"  {BED_ZONE}"
    )

    print()

    print(
        "YOLO Model:"
    )

    print(
        f"  {YOLO_MODEL}"
    )

    print()

    print(
        "YOLO Confidence:"
    )

    print(
        f"  {YOLO_CONFIDENCE}"
    )

    print()


    # ========================================================
    # SYSTEM LOGIC
    # ========================================================

    print(
        "System Logic:"
    )

    print(
        "  Person INSIDE BED  → Heart Rate ON"
    )

    print(
        "  Person OUTSIDE BED → Heart Rate OFF"
    )

    print(
        "  Person NOT FOUND   → Heart Rate OFF"
    )

    print()

    print(
        "Press Q to stop."
    )

    print()


    # ========================================================
    # CAMERA
    # ========================================================

    camera = cv2.VideoCapture(
        CAMERA_INDEX
    )


    if not camera.isOpened():

        print(
            "ERROR: Could not open camera."
        )

        return


    # ========================================================
    # CAMERA RESOLUTION
    # ========================================================

    camera.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        1280
    )

    camera.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        720
    )


    # ========================================================
    # BED ZONE DETECTOR
    # ========================================================

    detector = BedZoneDetector(
        model_path=YOLO_MODEL,

        bed_zone=BED_ZONE,

        confidence=YOLO_CONFIDENCE,

        miss_tolerance=MISS_TOLERANCE,

        confirm_frames=CONFIRM_FRAMES
    )


    # ========================================================
    # HEART RATE SIMULATOR
    # ========================================================
    #
    # This is currently TEST data.
    #
    # Later this can be replaced with the real
    # heart-rate sensor.
    #
    # ========================================================

    simulator = HeartRateSimulator(
        interval=HR_INTERVAL
    )


    # ========================================================
    # HEART RATE SYSTEM
    # ========================================================

    heart_rate_system = (
        create_heart_rate_system()
    )


    # ========================================================
    # STATE VARIABLES
    # ========================================================

    heart_rate_active = False

    last_hr_result = None

    last_hr_time = 0


    # ========================================================
    # CAMERA LOOP
    # ========================================================

    while True:

        # ====================================================
        # FLUSH STALE FRAMES
        #
        # On CPU-only hardware, YOLO can be slower than the
        # camera's frame rate. If we don't drain the buffer,
        # OpenCV queues up old frames and the display
        # increasingly lags behind real time.
        #
        # grab() just discards a frame without decoding it,
        # so this is cheap. We grab a couple extra times to
        # skip ahead to the newest frame before we actually
        # read (retrieve + decode) one.
        # ====================================================

        for _ in range(2):

            camera.grab()


        # ====================================================
        # READ CAMERA
        # ====================================================

        success, frame = camera.read()


        if not success:

            print(
                "ERROR: Could not read camera frame."
            )

            break


        # ====================================================
        # BED ZONE DETECTION
        # ====================================================

        (
            output_frame,
            person_detected,
            person_status
        ) = detector.process_frame(
            frame
        )


        # ====================================================
        # DETERMINE BED STATUS
        # ====================================================

        inside_bed = False


        if person_detected:

            if "INSIDE BED" in person_status:

                inside_bed = True


        # ====================================================
        # CASE 1
        # PERSON NOT DETECTED
        # ====================================================

        if not person_detected:

            # ------------------------------------------------
            # HEART RATE WAS ACTIVE
            # ------------------------------------------------

            if heart_rate_active:

                print()

                print(
                    "=" * 75
                )

                print(
                    "PERSON NOT DETECTED"
                )

                print(
                    "HEART RATE MONITORING OFF"
                )

                print(
                    "=" * 75
                )


            # ------------------------------------------------
            # TURN OFF
            # ------------------------------------------------

            heart_rate_active = False

            last_hr_result = None


            # ------------------------------------------------
            # RESET HR SYSTEM
            #
            # This clears previous HR history.
            # ------------------------------------------------

            heart_rate_system = (
                create_heart_rate_system()
            )


        # ====================================================
        # CASE 2
        # PERSON OUTSIDE BED
        # ====================================================

        elif not inside_bed:

            # ------------------------------------------------
            # HEART RATE WAS ACTIVE
            # ------------------------------------------------

            if heart_rate_active:

                print()

                print(
                    "=" * 75
                )

                print(
                    "PERSON OUTSIDE BED"
                )

                print(
                    "HEART RATE MONITORING OFF"
                )

                print(
                    "=" * 75
                )


            # ------------------------------------------------
            # TURN OFF
            # ------------------------------------------------

            heart_rate_active = False

            last_hr_result = None


            # ------------------------------------------------
            # RESET HR SYSTEM
            # ------------------------------------------------

            heart_rate_system = (
                create_heart_rate_system()
            )


        # ====================================================
        # CASE 3
        # PERSON INSIDE BED
        # ====================================================

        else:

            # ------------------------------------------------
            # PERSON JUST ENTERED BED
            # ------------------------------------------------

            if not heart_rate_active:

                print()

                print(
                    "=" * 75
                )

                print(
                    "PERSON INSIDE BED"
                )

                print(
                    "HEART RATE MONITORING ON"
                )

                print(
                    "=" * 75
                )


                # --------------------------------------------
                # CREATE FRESH HR SYSTEM
                # --------------------------------------------

                heart_rate_system = (
                    create_heart_rate_system()
                )


                heart_rate_active = True

                last_hr_result = None

                last_hr_time = 0


            # =================================================
            # HEART RATE PROCESSING
            # =================================================

            current_time = time.time()


            if (
                current_time - last_hr_time
                >= HR_INTERVAL
            ):

                try:

                    # ----------------------------------------
                    # GET HR READING
                    # ----------------------------------------

                    (
                        heart_rate,
                        timestamp
                    ) = get_heart_rate_reading(
                        simulator
                    )


                    # ----------------------------------------
                    # SEND READING TO HR SYSTEM
                    # ----------------------------------------

                    last_hr_result = (
                        heart_rate_system.process_reading(
                            heart_rate,
                            timestamp
                        )
                    )


                    # ----------------------------------------
                    # PRINT RESULT
                    # ----------------------------------------

                    print_heart_rate_result(
                        last_hr_result
                    )


                    # ----------------------------------------
                    # UPDATE TIMER
                    # ----------------------------------------

                    last_hr_time = current_time


                except Exception as error:

                    print()

                    print(
                        "HEART RATE ERROR:"
                    )

                    print(
                        error
                    )


        # ====================================================
        # DRAW FINAL STATUS
        # ====================================================

        output_frame = draw_integrated_status(
            output_frame,
            person_detected,
            inside_bed,
            last_hr_result
        )


        # ====================================================
        # DISPLAY
        # ====================================================

        cv2.imshow(
            "Sanjeevani AI - Integrated System",
            output_frame
        )


        # ====================================================
        # KEYBOARD
        # ====================================================

        key = cv2.waitKey(1) & 0xFF


        # ----------------------------------------------------
        # QUIT
        # ----------------------------------------------------

        if key == ord("q"):

            break


    # ========================================================
    # CLEANUP
    # ========================================================

    camera.release()

    cv2.destroyAllWindows()


    # ========================================================
    # STOP MESSAGE
    # ========================================================

    print()

    print(
        "=" * 75
    )

    print(
        "SANJEEVANI AI INTEGRATED SYSTEM STOPPED"
    )

    print(
        "=" * 75
    )


# ============================================================
# PROGRAM ENTRY
# ============================================================

if __name__ == "__main__":

    main()