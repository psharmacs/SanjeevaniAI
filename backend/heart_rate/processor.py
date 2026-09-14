from collections import deque


class HeartRateProcessor:
    """
    Processes heart-rate readings after validation.

    Responsibilities:
    - Detect sudden sensor artifacts
    - Reject isolated unrealistic jumps
    - Recover after an artifact
    - Smooth accepted HR readings
    - Maintain clean HR history
    - Calculate average HR
    - Detect HR trend

    This module does NOT provide a medical diagnosis.
    """

    def __init__(
        self,
        history_size=12,
        artifact_jump=25,
        smoothing_window=5,
        trend_window=4
    ):

        self.history_size = history_size
        self.artifact_jump = artifact_jump
        self.smoothing_window = smoothing_window
        self.trend_window = trend_window

        # -----------------------------------------------------
        # Clean accepted HR history
        # -----------------------------------------------------

        self.history = deque(
            maxlen=history_size
        )

        # -----------------------------------------------------
        # History used for smoothing
        # -----------------------------------------------------

        self.smoothing_history = deque(
            maxlen=smoothing_window
        )

        # -----------------------------------------------------
        # Artifact tracking
        # -----------------------------------------------------

        self.artifact_count = 0

    # =========================================================
    # ARTIFACT DETECTION
    # =========================================================

    def _is_artifact(self, heart_rate):

        # No previous accepted reading
        if not self.history:
            return False

        previous_hr = self.history[-1]

        difference = abs(
            heart_rate - previous_hr
        )

        # -----------------------------------------------------
        # Detect sudden jump
        # -----------------------------------------------------

        if difference > self.artifact_jump:

            # -------------------------------------------------
            # If the previous reading was already identified
            # as an artifact, allow the next plausible reading
            # to become a recovery reading.
            # -------------------------------------------------

            if self.artifact_count > 0:
                return False

            return True

        return False

    # =========================================================
    # SMOOTHING
    # =========================================================

    def _calculate_smoothed_hr(self):

        if not self.smoothing_history:
            return None

        values = list(
            self.smoothing_history
        )

        return round(
            sum(values) / len(values),
            2
        )

    # =========================================================
    # AVERAGE
    # =========================================================

    def _calculate_average_hr(self):

        if not self.history:
            return None

        values = list(
            self.history
        )

        return round(
            sum(values) / len(values),
            2
        )

    # =========================================================
    # TREND DETECTION
    # =========================================================

    def _calculate_trend(self):

        if len(self.history) < 3:
            return "insufficient_data"

        values = list(
            self.history
        )

        recent = values[
            -self.trend_window:
        ]

        if len(recent) < 3:
            return "insufficient_data"

        increasing = 0
        decreasing = 0

        # -----------------------------------------------------
        # Compare consecutive readings
        # -----------------------------------------------------

        for i in range(1, len(recent)):

            difference = (
                recent[i] - recent[i - 1]
            )

            if difference >= 2:

                increasing += 1

            elif difference <= -2:

                decreasing += 1

        # -----------------------------------------------------
        # Increasing
        # -----------------------------------------------------

        if (
            increasing >= 2
            and increasing > decreasing
        ):

            return "increasing"

        # -----------------------------------------------------
        # Decreasing
        # -----------------------------------------------------

        if (
            decreasing >= 2
            and decreasing > increasing
        ):

            return "decreasing"

        # -----------------------------------------------------
        # Stable
        # -----------------------------------------------------

        return "stable"

    # =========================================================
    # MAIN PROCESSING FUNCTION
    # =========================================================

    def process(self, heart_rate):

        # =====================================================
        # MISSING HR
        # =====================================================

        if heart_rate is None:

            return {
                "heart_rate": heart_rate,
                "accepted": False,
                "artifact": False,
                "smoothed_hr": (
                    self._calculate_smoothed_hr()
                ),
                "average_hr": (
                    self._calculate_average_hr()
                ),
                "trend": (
                    self._calculate_trend()
                ),
                "history": self.get_history(),
                "reason": "Heart rate is missing"
            }

        # =====================================================
        # NON-NUMERIC HR
        # =====================================================

        if not isinstance(
            heart_rate,
            (int, float)
        ):

            return {
                "heart_rate": heart_rate,
                "accepted": False,
                "artifact": False,
                "smoothed_hr": (
                    self._calculate_smoothed_hr()
                ),
                "average_hr": (
                    self._calculate_average_hr()
                ),
                "trend": (
                    self._calculate_trend()
                ),
                "history": self.get_history(),
                "reason": "Heart rate is not numeric"
            }

        # =====================================================
        # ARTIFACT CHECK
        # =====================================================

        artifact = self._is_artifact(
            heart_rate
        )

        if artifact:

            self.artifact_count += 1

            return {
                "heart_rate": heart_rate,
                "accepted": False,
                "artifact": True,
                "smoothed_hr": (
                    self._calculate_smoothed_hr()
                ),
                "average_hr": (
                    self._calculate_average_hr()
                ),
                "trend": (
                    self._calculate_trend()
                ),
                "history": self.get_history(),
                "reason": (
                    "Possible sensor artifact detected; "
                    "monitoring continues"
                )
            }

        # =====================================================
        # ACCEPT READING
        # =====================================================

        self.history.append(
            heart_rate
        )

        self.smoothing_history.append(
            heart_rate
        )

        # -----------------------------------------------------
        # A valid reading means the sensor has recovered.
        # -----------------------------------------------------

        self.artifact_count = 0

        # =====================================================
        # CALCULATE PROCESSED VALUES
        # =====================================================

        smoothed_hr = (
            self._calculate_smoothed_hr()
        )

        average_hr = (
            self._calculate_average_hr()
        )

        trend = (
            self._calculate_trend()
        )

        # =====================================================
        # RETURN PROCESSED DATA
        # =====================================================

        return {
            "heart_rate": heart_rate,
            "accepted": True,
            "artifact": False,
            "smoothed_hr": smoothed_hr,
            "average_hr": average_hr,
            "trend": trend,
            "history": self.get_history(),
            "reason": "Reading accepted"
        }

    # =========================================================
    # GET HISTORY
    # =========================================================

    def get_history(self):

        return list(
            self.history
        )

    # =========================================================
    # RESET
    # =========================================================

    def reset(self):

        self.history.clear()

        self.smoothing_history.clear()

        self.artifact_count = 0


# =============================================================
# TEST
# =============================================================

if __name__ == "__main__":

    print("=" * 65)
    print("❤️ SANJEEVANI AI")
    print("   HEART RATE PROCESSOR")
    print("=" * 65)

    processor = HeartRateProcessor(
        history_size=12,
        artifact_jump=25,
        smoothing_window=5,
        trend_window=4
    )

    # =========================================================
    # TEST 1
    # =========================================================

    print("\nTEST 1: NORMAL HEART RATE")
    print("-" * 65)

    normal_data = [
        72,
        73,
        72,
        74,
        73,
        75,
        74,
        73
    ]

    for hr in normal_data:

        result = processor.process(
            hr
        )

        print(
            f"HR: {hr} | "
            f"Accepted: {result['accepted']} | "
            f"Artifact: {result['artifact']} | "
            f"Smoothed: {result['smoothed_hr']} | "
            f"Trend: {result['trend']}"
        )

    # =========================================================
    # TEST 2
    # =========================================================

    print("\nTEST 2: ISOLATED SENSOR SPIKE")
    print("-" * 65)

    processor.reset()

    spike_data = [
        72,
        73,
        74,
        145,
        74,
        73
    ]

    for hr in spike_data:

        result = processor.process(
            hr
        )

        print(
            f"HR: {hr} | "
            f"Accepted: {result['accepted']} | "
            f"Artifact: {result['artifact']} | "
            f"Smoothed: {result['smoothed_hr']} | "
            f"History: {processor.get_history()}"
        )

    # =========================================================
    # TEST 3
    # =========================================================

    print("\nTEST 3: GRADUAL HEART RATE INCREASE")
    print("-" * 65)

    processor.reset()

    increasing_data = [
        72,
        75,
        78,
        81,
        84,
        87,
        90
    ]

    for hr in increasing_data:

        result = processor.process(
            hr
        )

        print(
            f"HR: {hr} | "
            f"Accepted: {result['accepted']} | "
            f"Smoothed: {result['smoothed_hr']} | "
            f"Trend: {result['trend']}"
        )

    # =========================================================
    # TEST 4
    # =========================================================

    print("\nTEST 4: SUSTAINED HIGH HEART RATE")
    print("-" * 65)

    processor.reset()

    high_data = [
        102,
        105,
        108,
        106,
        107,
        109
    ]

    for hr in high_data:

        result = processor.process(
            hr
        )

        print(
            f"HR: {hr} | "
            f"Accepted: {result['accepted']} | "
            f"Artifact: {result['artifact']} | "
            f"Smoothed: {result['smoothed_hr']} | "
            f"Trend: {result['trend']}"
        )

    # =========================================================
    # FINAL HISTORY
    # =========================================================

    print("\nFINAL CLEAN HISTORY")
    print("-" * 65)

    print(
        processor.get_history()
    )