from ultralytics import YOLO


class PersonDetector:
    def __init__(self, model_path, conf_thres=0.5):
        self.model = YOLO(model_path)
        self.conf_thres = conf_thres

    def detect(self, frame):
        """
        Run YOLOv8 on frame and return the main detected person.

        For the Sanjeevani AI setup, only the largest detected
        person is returned because the system is designed to
        monitor one elderly person.

        Returns
        -------
        list of (x1, y1, x2, y2) int tuples
        """

        # Run YOLO
        results = self.model(
            frame,
            conf=self.conf_thres,
            classes=[0],
            verbose=False
        )[0]

        boxes = []

        # Process detected boxes
        for box in results.boxes:

            # Class 0 = person
            if int(box.cls[0]) != 0:
                continue

            confidence = float(box.conf[0])

            # Confidence filtering
            if confidence < self.conf_thres:
                continue

            # Bounding box coordinates
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            boxes.append(
                (x1, y1, x2, y2)
            )

        # ---------------------------------------------------------
        # If multiple persons are detected,
        # keep only the largest bounding box.
        # ---------------------------------------------------------
        if len(boxes) > 1:

            def box_area(bbox):
                x1, y1, x2, y2 = bbox

                width = max(0, x2 - x1)
                height = max(0, y2 - y1)

                return width * height

            largest_box = max(
                boxes,
                key=box_area
            )

            boxes = [largest_box]

        return boxes