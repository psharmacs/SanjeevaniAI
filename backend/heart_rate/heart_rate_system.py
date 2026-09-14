import time

from validator import HeartRateValidator
from processor import HeartRateProcessor
from analyzer import HeartRateAnalyzer
from alert_manager import HeartRateAlertManager
from simulator import HeartRateSimulator


class HeartRateSystem:
    """
    End-to-end Sanjeevani AI heart-rate monitoring system.

    Pipeline:

        Simulator
            ↓
        Validator
            ↓
        Processor
            ↓
        Analyzer
            ↓
        Alert Manager
    """

    def __init__(self):

        # =====================================================
        # VALIDATOR
        # =====================================================

        self.validator = HeartRateValidator()

        # =====================================================
        # PROCESSOR
        # =====================================================

        self.processor = HeartRateProcessor(
            history_size=12,
            artifact_jump=25
        )

        # =====================================================
        # ANALYZER
        # =====================================================

        self.analyzer = HeartRateAnalyzer(
            watch_threshold=90,
            alert_threshold=100,
            sustained_readings=4,
            trend_window=4,
            trend_change_threshold=2
        )

        # =====================================================
        # ALERT MANAGER
        # =====================================================

        self.alert_manager = HeartRateAlertManager(
            cooldown_seconds=30
        )

    # =========================================================
    # PROCESS ONE READING
    # =========================================================

    def process_reading(
        self,
        heart_rate,
        timestamp
    ):

        # -----------------------------------------------------
        # CREATE READING
        # -----------------------------------------------------

        reading = {
            "timestamp": timestamp,
            "heart_rate": heart_rate
        }

        # -----------------------------------------------------
        # VALIDATION
        # -----------------------------------------------------

        validation = self.validator.validate_reading(
            reading
        )

        # -----------------------------------------------------
        # INVALID READING
        # -----------------------------------------------------

        if not validation["valid"]:

            analyzer_result = {
                "status": "NO_DATA",
                "reason": validation["reason"]
            }

            alert_result = self.alert_manager.handle(
                analyzer_result
            )

            return {
                "reading": reading,
                "validation": validation,
                "processor": None,
                "analyzer": analyzer_result,
                "alert": alert_result
            }

        # -----------------------------------------------------
        # PROCESSOR
        # -----------------------------------------------------

        processed = self.processor.process(
            heart_rate
        )

        # -----------------------------------------------------
        # ANALYZER
        # -----------------------------------------------------

        analysis = self.analyzer.analyze(
            processed
        )

        # -----------------------------------------------------
        # ALERT MANAGER
        # -----------------------------------------------------

        alert = self.alert_manager.handle(
            analysis
        )

        # -----------------------------------------------------
        # FINAL RESULT
        # -----------------------------------------------------

        return {
            "reading": reading,
            "validation": validation,
            "processor": processed,
            "analyzer": analysis,
            "alert": alert
        }

    # =========================================================
    # DISPLAY RESULT
    # =========================================================

    def display_result(self, result):

        print()
        print("-" * 75)

        reading = result["reading"]

        print(
            f"Time: {reading['timestamp']}"
        )

        print(
            f"HR: {reading['heart_rate']} BPM"
        )

        # -----------------------------------------------------
        # VALIDATION
        # -----------------------------------------------------

        validation = result["validation"]

        print(
            f"Validation: "
            f"{validation['valid']}"
        )

        print(
            f"Validation Reason: "
            f"{validation['reason']}"
        )

        # -----------------------------------------------------
        # PROCESSOR
        # -----------------------------------------------------

        processor = result["processor"]

        if processor is not None:

            print(
                f"Accepted: "
                f"{processor['accepted']}"
            )

            print(
                f"Artifact: "
                f"{processor['artifact']}"
            )

            print(
                f"Smoothed HR: "
                f"{processor['smoothed_hr']} BPM"
            )

            print(
                f"Average HR: "
                f"{processor['average_hr']} BPM"
            )

            print(
                f"Trend: "
                f"{processor['trend']}"
            )

        # -----------------------------------------------------
        # ANALYZER
        # -----------------------------------------------------

        analyzer = result["analyzer"]

        print(
            f"Status: "
            f"{analyzer['status']}"
        )

        print(
            f"Reason: "
            f"{analyzer['reason']}"
        )

        # -----------------------------------------------------
        # ALERT MANAGER
        # -----------------------------------------------------

        alert = result["alert"]

        print(
            f"Action: "
            f"{alert['action']}"
        )

        print(
            f"Priority: "
            f"{alert['priority']}"
        )

        print(
            f"Notification: "
            f"{alert['notification']}"
        )

    # =========================================================
    # RUN CONTINUOUS MONITORING
    # =========================================================

    def run(self, simulator):

        print("=" * 75)
        print("❤️ SANJEEVANI AI")
        print("   END-TO-END HEART RATE MONITORING SYSTEM")
        print("=" * 75)

        print()

        print("Pipeline:")
        print(
            "Simulator → Validator → Processor → "
            "Analyzer → Alert Manager"
        )

        print()

        print("Starting system...")
        print("Press CTRL+C to stop.")

        try:

            for reading in simulator.stream():

                result = self.process_reading(
                    reading["heart_rate"],
                    reading["timestamp"]
                )

                self.display_result(
                    result
                )

        except KeyboardInterrupt:

            print()
            print("=" * 75)
            print("SYSTEM STOPPED")
            print("=" * 75)

            self.display_summary()

    # =========================================================
    # SUMMARY
    # =========================================================

    def display_summary(self):

        summary = self.alert_manager.get_summary()

        print()
        print("=" * 75)
        print("FINAL SYSTEM SUMMARY")
        print("=" * 75)

        print(
            f"Watch events: "
            f"{summary['watch_events']}"
        )

        print(
            f"Alerts generated: "
            f"{summary['alerts_generated']}"
        )

        print(
            f"Clean HR history: "
            f"{self.processor.get_history()}"
        )


# =============================================================
# MAIN
# =============================================================

if __name__ == "__main__":

    simulator = HeartRateSimulator(
        interval=1
    )

    system = HeartRateSystem()

    system.run(
        simulator
    )