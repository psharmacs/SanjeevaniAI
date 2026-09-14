from processor import HeartRateProcessor


class HeartRateAnalyzer:
    """
    Analyzes CLEAN heart-rate data produced by HeartRateProcessor.

    Status:

        NORMAL
        WATCH
        ALERT
        NO_DATA

    The analyzer detects patterns only.
    It does NOT provide a medical diagnosis.
    """

    def __init__(
        self,
        watch_threshold=90,
        alert_threshold=100,
        low_alert_threshold=50,
        sustained_readings=4,
        trend_window=4,
        trend_change_threshold=2
    ):

        self.watch_threshold = watch_threshold

        self.alert_threshold = alert_threshold

        self.low_alert_threshold = low_alert_threshold

        self.sustained_readings = sustained_readings

        self.trend_window = trend_window

        self.trend_change_threshold = trend_change_threshold

    # =========================================================
    # SUSTAINED HIGH HR
    # =========================================================

    def _is_sustained_high(self, history):

        if len(history) < self.sustained_readings:
            return False

        recent = history[
            -self.sustained_readings:
        ]

        return all(
            hr >= self.alert_threshold
            for hr in recent
        )

    # =========================================================
    # SUSTAINED LOW HR
    # =========================================================

    def _is_sustained_low(self, history):

        if len(history) < self.sustained_readings:
            return False

        recent = history[
            -self.sustained_readings:
        ]

        return all(
            hr <= self.low_alert_threshold
            for hr in recent
        )

    # =========================================================
    # INCREASING TREND
    # =========================================================

    def _is_increasing_trend(self, history):

        if len(history) < self.trend_window:
            return False

        recent = history[
            -self.trend_window:
        ]

        increases = 0

        for i in range(1, len(recent)):

            difference = (
                recent[i] -
                recent[i - 1]
            )

            if difference >= self.trend_change_threshold:

                increases += 1

        return (
            increases >=
            self.trend_window - 1
        )

    # =========================================================
    # DECREASING TREND
    # =========================================================

    def _is_decreasing_trend(self, history):

        if len(history) < self.trend_window:
            return False

        recent = history[
            -self.trend_window:
        ]

        decreases = 0

        for i in range(1, len(recent)):

            difference = (
                recent[i] -
                recent[i - 1]
            )

            if difference <= -self.trend_change_threshold:

                decreases += 1

        return (
            decreases >=
            self.trend_window - 1
        )

    # =========================================================
    # MAIN ANALYSIS
    # =========================================================

    def analyze(self, processed_data):

        heart_rate = processed_data.get(
            "heart_rate"
        )

        accepted = processed_data.get(
            "accepted",
            True
        )

        artifact = processed_data.get(
            "artifact",
            False
        )

        smoothed_hr = processed_data.get(
            "smoothed_hr"
        )

        history = processed_data.get(
            "history",
            []
        )

        # =====================================================
        # NO DATA
        # =====================================================

        if heart_rate is None:

            return {
                "status": "NO_DATA",
                "reason": (
                    "Heart-rate reading unavailable"
                )
            }

        # =====================================================
        # SENSOR ARTIFACT
        # =====================================================

        if artifact and not accepted:

            return {
                "status": "WATCH",
                "reason": (
                    "Possible sensor artifact detected; "
                    "monitoring continues"
                )
            }

        # =====================================================
        # READING NOT ACCEPTED
        # =====================================================

        if not accepted:

            return {
                "status": "WATCH",
                "reason": (
                    "Heart-rate reading was not accepted "
                    "for analysis"
                )
            }

        # =====================================================
        # INSUFFICIENT HISTORY
        # =====================================================

        if len(history) < 3:

            return {
                "status": "NORMAL",
                "reason": (
                    "Collecting more heart-rate history"
                )
            }

        # =====================================================
        # SUSTAINED HIGH
        # =====================================================

        if self._is_sustained_high(history):

            return {
                "status": "ALERT",
                "reason": (
                    "Sustained elevated heart-rate "
                    "pattern detected"
                )
            }

        # =====================================================
        # SUSTAINED LOW
        # =====================================================

        if self._is_sustained_low(history):

            return {
                "status": "ALERT",
                "reason": (
                    "Sustained low heart-rate "
                    "pattern detected"
                )
            }

        # =====================================================
        # INCREASING TREND
        # =====================================================

        if self._is_increasing_trend(history):

            return {
                "status": "WATCH",
                "reason": (
                    "Heart rate shows a consistent "
                    "increasing trend"
                )
            }

        # =====================================================
        # DECREASING TREND
        # =====================================================

        if self._is_decreasing_trend(history):

            return {
                "status": "WATCH",
                "reason": (
                    "Heart rate shows a consistent "
                    "decreasing trend"
                )
            }

        # =====================================================
        # ELEVATED SMOOTHED HR
        # =====================================================

        if (
            smoothed_hr is not None
            and
            smoothed_hr >= self.watch_threshold
        ):

            return {
                "status": "WATCH",
                "reason": (
                    "Smoothed heart rate is elevated"
                )
            }

        # =====================================================
        # LOW SMOOTHED HR
        # =====================================================

        if (
            smoothed_hr is not None
            and
            smoothed_hr <= self.low_alert_threshold
        ):

            return {
                "status": "WATCH",
                "reason": (
                    "Smoothed heart rate is low; "
                    "continued monitoring recommended"
                )
            }

        # =====================================================
        # NORMAL
        # =====================================================

        return {
            "status": "NORMAL",
            "reason": (
                "No unusual heart-rate pattern detected"
            )
        }


# =============================================================
# TEST HELPER
# =============================================================

def run_test(title, values):

    print("\n")
    print("=" * 70)
    print(title)
    print("=" * 70)

    processor = HeartRateProcessor(
        history_size=12,
        artifact_jump=25
    )

    analyzer = HeartRateAnalyzer(
        watch_threshold=90,
        alert_threshold=100,
        low_alert_threshold=50,
        sustained_readings=4,
        trend_window=4,
        trend_change_threshold=2
    )

    result = None

    for hr in values:

        processed = processor.process(hr)

        result = analyzer.analyze(
            processed
        )

        print(
            f"HR: {hr} | "
            f"Accepted: {processed['accepted']} | "
            f"Artifact: {processed['artifact']} | "
            f"Smoothed: {processed['smoothed_hr']} | "
            f"Trend: {processed['trend']} | "
            f"Status: {result['status']}"
        )

    print()

    print(
        "Final History:",
        processor.get_history()
    )

    print(
        "Final Status:",
        result["status"]
    )

    print(
        "Reason:",
        result["reason"]
    )


# =============================================================
# TESTS
# =============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("❤️ SANJEEVANI AI")
    print("   HEART RATE ANALYZER")
    print("=" * 70)

    # =========================================================
    # TEST A
    # NORMAL
    # =========================================================

    run_test(
        "TEST A → NORMAL",
        [
            72,
            73,
            71,
            74,
            72,
            75,
            73,
            72,
            74,
            73
        ]
    )

    # =========================================================
    # TEST B
    # INCREASING
    # =========================================================

    run_test(
        "TEST B → INCREASING",
        [
            72,
            75,
            78,
            81,
            84,
            87,
            90,
            93
        ]
    )

    # =========================================================
    # TEST C
    # DECREASING
    # =========================================================

    run_test(
        "TEST C → DECREASING",
        [
            95,
            92,
            89,
            86,
            83,
            80,
            77,
            74
        ]
    )

    # =========================================================
    # TEST D
    # SUSTAINED HIGH
    # =========================================================

    run_test(
        "TEST D → SUSTAINED HIGH → ALERT",
        [
            96,
            98,
            101,
            104,
            106,
            108,
            107,
            109
        ]
    )

    # =========================================================
    # TEST E
    # SUSTAINED LOW
    # =========================================================

    run_test(
        "TEST E → SUSTAINED LOW → ALERT",
        [
            58,
            54,
            51,
            48,
            47,
            49,
            46,
            48
        ]
    )

    # =========================================================
    # TEST F
    # SENSOR SPIKE
    # =========================================================

    run_test(
        "TEST F → SENSOR SPIKE → IGNORE",
        [
            72,
            73,
            74,
            145,
            74,
            73,
            72,
            74
        ]
    )

    # =========================================================
    # TEST G
    # RECOVERY
    # =========================================================

    run_test(
        "TEST G → RECOVERY → NORMAL",
        [
            108,
            104,
            100,
            96,
            91,
            86,
            81,
            77,
            74,
            72,
            73,
            72
        ]
    )

    print()
    print("=" * 70)
    print("ALL ANALYZER TESTS COMPLETE")
    print("=" * 70)