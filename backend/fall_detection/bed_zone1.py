import cv2
from ultralytics import YOLO


class BedZoneDetector:
    """
    Detects a person and determines whether the person
    is inside or outside the configured bed zone.

    This module only handles:
        Person detection
        Bed-zone detection

    It does NOT detect falls or posture yet.
    """

    def __init__(
        self,
        model_path="yolov8s.pt",
        bed_zone=None,
        confidence=0.25,
        miss_tolerance=10,
        confirm_frames=3
    ):

        # -----------------------------------------------------
        # LOAD YOLO MODEL
        # -----------------------------------------------------

        self.model = YOLO(model_path)

        self.confidence = confidence

        # -----------------------------------------------------
        # BED ZONE
        #
        # Format:
        # (x1, y1, x2, y2)
        # -----------------------------------------------------

        self.bed_zone = bed_zone

        # -----------------------------------------------------
        # TEMPORAL SMOOTHING (DEBOUNCE)
        #
        # YOLO confidence for a lying-down person can hover
        # right around the confidence threshold, causing the
        # detection to flicker on/off between frames even
        # though the person hasn't moved.
        #
        # miss_tolerance:
        #   number of consecutive missed frames allowed
        #   before we actually report "NOT DETECTED"
        #
        # confirm_frames:
        #   number of consecutive consistent readings needed
        #   before we flip the reported zone status
        #   (INSIDE BED <-> OUTSIDE BED)
        # -----------------------------------------------------

        self.miss_tolerance = miss_tolerance
        self.confirm_frames = confirm_frames

        self.miss_counter = 0
        self.last_confirmed_detected = False

        self.pending_zone_status = None
        self.pending_zone_count = 0
        self.confirmed_zone_status = "OUTSIDE BED"

    # =========================================================
    # SET BED ZONE
    # =========================================================

    def set_bed_zone(self, x1, y1, x2, y2):

        self.bed_zone = (
            x1,
            y1,
            x2,
            y2
        )

    # =========================================================
    # CHECK PERSON INSIDE BED
    # =========================================================

    def is_inside_bed(
        self,
        person_x1,
        person_y1,
        person_x2,
        person_y2
    ):

        if self.bed_zone is None:
            return False

        bed_x1, bed_y1, bed_x2, bed_y2 = self.bed_zone

        # -----------------------------------------------------
        # CALCULATE INTERSECTION
        # -----------------------------------------------------

        intersection_x1 = max(
            person_x1,
            bed_x1
        )

        intersection_y1 = max(
            person_y1,
            bed_y1
        )

        intersection_x2 = min(
            person_x2,
            bed_x2
        )

        intersection_y2 = min(
            person_y2,
            bed_y2
        )

        # -----------------------------------------------------
        # NO INTERSECTION
        # -----------------------------------------------------

        if (
            intersection_x2 <= intersection_x1
            or
            intersection_y2 <= intersection_y1
        ):

            return False

        # -----------------------------------------------------
        # INTERSECTION AREA
        # -----------------------------------------------------

        intersection_width = (
            intersection_x2 - intersection_x1
        )

        intersection_height = (
            intersection_y2 - intersection_y1
        )

        intersection_area = (
            intersection_width
            *
            intersection_height
        )

        # -----------------------------------------------------
        # PERSON BOX AREA
        # -----------------------------------------------------

        person_width = (
            person_x2 - person_x1
        )

        person_height = (
            person_y2 - person_y1
        )

        person_area = (
            person_width
            *
            person_height
        )

        if person_area <= 0:

            return False

        # -----------------------------------------------------
        # HOW MUCH OF PERSON IS INSIDE BED?
        # -----------------------------------------------------

        overlap_ratio = (
            intersection_area
            /
            person_area
        )

        # -----------------------------------------------------
        # BED CHECK
        #
        # 20% overlap is enough.
        #
        # This is useful when a person is lying down because
        # the bounding box can extend outside the bed zone.
        # -----------------------------------------------------

        return overlap_ratio >= 0.20

    # =========================================================
    # PROCESS ONE FRAME
    # =========================================================

    def process_frame(self, frame):

        results = self.model.predict(
            frame,

            # Lower confidence helps detect lying people
            conf=self.confidence,

            # Person class only
            classes=[0],

            # 640 balances accuracy vs CPU speed
            # (960 was too slow on CPU-only hardware and caused
            # the live video to lag behind real time)
            imgsz=640,

            verbose=False
        )

        person_detected = False

        raw_inside_bed = False

        annotated_frame = frame.copy()

        # =====================================================
        # DRAW BED ZONE
        # =====================================================

        if self.bed_zone is not None:

            bed_x1, bed_y1, bed_x2, bed_y2 = self.bed_zone

            # -------------------------------------------------
            # BLUE BED RECTANGLE
            # -------------------------------------------------

            cv2.rectangle(
                annotated_frame,
                (bed_x1, bed_y1),
                (bed_x2, bed_y2),
                (255, 0, 0),
                3
            )

            # -------------------------------------------------
            # BED ZONE LABEL
            # -------------------------------------------------

            label_y = max(
                bed_y1 - 12,
                30
            )

            cv2.putText(
                annotated_frame,
                "BED ZONE",
                (bed_x1, label_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.75,
                (255, 0, 0),
                2
            )

        # =====================================================
        # PROCESS YOLO DETECTIONS
        # =====================================================

        for result in results:

            boxes = result.boxes

            for box in boxes:

                # -------------------------------------------------
                # PERSON CONFIDENCE
                # -------------------------------------------------

                confidence = float(
                    box.conf[0]
                )

                # -------------------------------------------------
                # PERSON COORDINATES
                # -------------------------------------------------

                coordinates = (
                    box.xyxy[0]
                    .cpu()
                    .numpy()
                )

                x1, y1, x2, y2 = map(
                    int,
                    coordinates
                )

                # -------------------------------------------------
                # PERSON CENTER
                # -------------------------------------------------

                center_x = int(
                    (x1 + x2) / 2
                )

                center_y = int(
                    (y1 + y2) / 2
                )

                person_detected = True

                # =================================================
                # BED ZONE CHECK
                # =================================================

                raw_inside_bed = self.is_inside_bed(
                    x1,
                    y1,
                    x2,
                    y2
                )

                # -------------------------------------------------
                # INSIDE BED
                # -------------------------------------------------

                if raw_inside_bed:

                    zone_status = "INSIDE BED"

                    box_color = (
                        0,
                        255,
                        0
                    )

                # -------------------------------------------------
                # OUTSIDE BED
                # -------------------------------------------------

                else:

                    zone_status = "OUTSIDE BED"

                    box_color = (
                        0,
                        0,
                        255
                    )

                # =================================================
                # DRAW PERSON BOX
                # =================================================

                cv2.rectangle(
                    annotated_frame,
                    (x1, y1),
                    (x2, y2),
                    box_color,
                    2
                )

                # =================================================
                # DRAW PERSON CENTER
                # =================================================

                cv2.circle(
                    annotated_frame,
                    (center_x, center_y),
                    6,
                    box_color,
                    -1
                )

                # =================================================
                # PERSON LABEL
                # =================================================

                person_label = (
                    f"{zone_status} "
                    f"{confidence:.2f}"
                )

                label_y = y1 - 10

                if label_y < 25:

                    label_y = y1 + 25

                cv2.putText(
                    annotated_frame,
                    person_label,
                    (x1, label_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    box_color,
                    2
                )

                # -------------------------------------------------
                # PROCESS FIRST PERSON ONLY
                # -------------------------------------------------

                break

            if person_detected:

                break

        # =====================================================
        # TEMPORAL SMOOTHING (FIXES FLICKER)
        #
        # A single missed frame no longer flips the status to
        # NOT DETECTED. A single noisy overlap reading no
        # longer flips INSIDE BED <-> OUTSIDE BED. Both require
        # several consecutive consistent frames first.
        # =====================================================

        if person_detected:

            self.miss_counter = 0

            self.last_confirmed_detected = True

            raw_zone = "INSIDE BED" if raw_inside_bed else "OUTSIDE BED"

            if raw_zone == self.pending_zone_status:

                self.pending_zone_count += 1

            else:

                self.pending_zone_status = raw_zone

                self.pending_zone_count = 1

            if self.pending_zone_count >= self.confirm_frames:

                self.confirmed_zone_status = raw_zone

        else:

            self.miss_counter += 1

            if self.miss_counter >= self.miss_tolerance:

                self.last_confirmed_detected = False

            # else: bridge the gap, keep last confirmed state

        if self.last_confirmed_detected:

            person_status = (
                f"PERSON: DETECTED | "
                f"{self.confirmed_zone_status}"
            )

        else:

            person_status = "PERSON: NOT DETECTED"

        # =====================================================
        # TOP STATUS BAR
        # =====================================================

        cv2.rectangle(
            annotated_frame,
            (10, 10),
            (510, 60),
            (0, 0, 0),
            -1
        )

        cv2.putText(
            annotated_frame,
            person_status,
            (20, 43),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2
        )

        # =====================================================
        # RETURN
        # =====================================================

        return (
            annotated_frame,
            self.last_confirmed_detected,
            person_status
        )


# =============================================================
# MAIN CAMERA TEST
# =============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("❤️ SANJEEVANI AI")
    print("   BED ZONE DETECTION")
    print("=" * 70)

    print()
    print("Starting camera...")
    print("Press Q to stop.")
    print()

    # =========================================================
    # CAMERA
    # =========================================================

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():

        print("ERROR: Could not open camera.")

        exit()

    # =========================================================
    # CAMERA RESOLUTION
    # =========================================================

    camera.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        1280
    )

    camera.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        720
    )

    # =========================================================
    # CREATE DETECTOR
    #
    # YOUR SAVED BED ZONE
    # =========================================================

    detector = BedZoneDetector(
        model_path="yolov8s.pt",

        bed_zone=(
            556,
            295,
            1083,
            518
        ),

        confidence=0.25,

        miss_tolerance=10,

        confirm_frames=3
    )

    # =========================================================
    # CAMERA LOOP
    # =========================================================

    while True:

        # =====================================================
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
        # =====================================================

        for _ in range(2):

            camera.grab()

        success, frame = camera.read()

        if not success:

            print(
                "ERROR: Could not read camera frame."
            )

            break

        # =====================================================
        # PROCESS FRAME
        # =====================================================

        (
            output_frame,
            person_detected,
            status
        ) = detector.process_frame(
            frame
        )

        # =====================================================
        # DISPLAY
        # =====================================================

        cv2.imshow(
            "Sanjeevani AI - Bed Zone",
            output_frame
        )

        # =====================================================
        # KEYBOARD
        # =====================================================

        key = cv2.waitKey(1) & 0xFF

        # -----------------------------------------------------
        # QUIT
        # -----------------------------------------------------

        if key == ord("q"):

            break

    # =========================================================
    # CLEANUP
    # =========================================================

    camera.release()

    cv2.destroyAllWindows()

    print()
    print("=" * 70)
    print("BED ZONE DETECTION STOPPED")
    print("=" * 70)