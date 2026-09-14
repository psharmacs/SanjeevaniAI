import numpy as np
from collections import OrderedDict


class CentroidTracker:
    def __init__(self, max_disappeared=30, max_distance=120):
        self.next_id = 0

        self.objects = OrderedDict()      # id -> centroid (x, y)
        self.bboxes = OrderedDict()       # id -> (x1, y1, x2, y2)
        self.disappeared = OrderedDict()  # id -> frames since last seen

        self.max_disappeared = max_disappeared
        self.max_distance = max_distance

    def _register(self, centroid, bbox):
        """
        Register a new person.
        """

        # ---------------------------------------------------------
        # Sanjeevani AI monitors only ONE person.
        # Remove any existing person before registering a new one.
        # ---------------------------------------------------------
        if len(self.objects) > 0:
            for oid in list(self.objects.keys()):
                self._deregister(oid)

        self.objects[self.next_id] = centroid
        self.bboxes[self.next_id] = bbox
        self.disappeared[self.next_id] = 0

        self.next_id += 1

    def _deregister(self, object_id):
        """
        Remove a tracked person.
        """

        if object_id in self.objects:
            del self.objects[object_id]

        if object_id in self.bboxes:
            del self.bboxes[object_id]

        if object_id in self.disappeared:
            del self.disappeared[object_id]

    def update(self, detections):
        """
        Parameters
        ----------
        detections : list of (x1, y1, x2, y2) from YOLO

        Returns
        -------
        dict
            {
                object_id:
                {
                    "bbox": (x1, y1, x2, y2),
                    "centroid": (cx, cy)
                }
            }
        """

        # =========================================================
        # CASE 1: No person detected
        # =========================================================

        if len(detections) == 0:

            for oid in list(self.disappeared.keys()):

                self.disappeared[oid] += 1

                if self.disappeared[oid] > self.max_disappeared:
                    self._deregister(oid)

            return self._build_output()

        # =========================================================
        # IMPORTANT:
        # Only use ONE detection.
        #
        # person_detection.py already returns the largest person,
        # but this provides an additional safety layer.
        # =========================================================

        if len(detections) > 1:

            def box_area(bbox):
                x1, y1, x2, y2 = bbox

                width = max(0, x2 - x1)
                height = max(0, y2 - y1)

                return width * height

            largest_detection = max(
                detections,
                key=box_area
            )

            detections = [largest_detection]

        # =========================================================
        # Calculate centroid
        # =========================================================

        x1, y1, x2, y2 = detections[0]

        input_centroid = np.array(
            [
                (x1 + x2) // 2,
                (y1 + y2) // 2
            ],
            dtype="float"
        )

        # =========================================================
        # CASE 2: No existing tracked person
        # =========================================================

        if len(self.objects) == 0:

            self._register(
                input_centroid,
                detections[0]
            )

            return self._build_output()

        # =========================================================
        # Existing person
        # =========================================================

        object_id = list(self.objects.keys())[0]

        object_centroid = np.array(
            self.objects[object_id],
            dtype="float"
        )

        # Distance between old and new centroid
        distance = np.linalg.norm(
            object_centroid - input_centroid
        )

        # =========================================================
        # CASE 3: Person movement is within allowed distance
        # =========================================================

        if distance <= self.max_distance:

            self.objects[object_id] = input_centroid

            self.bboxes[object_id] = detections[0]

            self.disappeared[object_id] = 0

        # =========================================================
        # CASE 4: Detection moved too far
        # =========================================================

        else:

            self.disappeared[object_id] += 1

            if self.disappeared[object_id] > self.max_disappeared:

                self._deregister(object_id)

                self._register(
                    input_centroid,
                    detections[0]
                )

        return self._build_output()

    def _build_output(self):
        """
        Build tracker output.
        """

        return {
            oid: {
                "bbox": self.bboxes[oid],
                "centroid": self.objects[oid]
            }
            for oid in self.objects
        }