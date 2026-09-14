import random
import time
from datetime import datetime


class HeartRateSimulator:
    """
    Synthetic wearable-style heart-rate simulator for
    Sanjeevani AI Bed Monitoring.

    Supported situations:
        - Bed lying
        - Bed sitting
        - Lying -> Sitting
        - Sitting -> Lying
        - Sleeping
        - Sustained unusual HR
        - Sensor artifact
        - Missing data

    IMPORTANT:
    This generates synthetic data for software testing only.
    It is NOT medical data and must not be used for diagnosis.
    """

    def __init__(self, resting_hr=72):
        self.resting_hr = float(resting_hr)
        self.current_hr = float(resting_hr)

    # =========================================================
    # INTERNAL HR MOVEMENT
    # =========================================================

    def _move_towards(self, target, max_change=1.5):
        """
        Gradually move current HR toward target.

        This prevents unrealistic jumps during normal
        physiological changes.
        """

        difference = target - self.current_hr

        if abs(difference) <= max_change:
            self.current_hr = target

        elif difference > 0:
            self.current_hr += max_change

        else:
            self.current_hr -= max_change

        # Small natural variation
        self.current_hr += random.uniform(-0.5, 0.5)

        # Keep result within a reasonable simulation range
        self.current_hr = max(40, min(self.current_hr, 140))

        return round(self.current_hr)

    # =========================================================
    # 1. PERSON LYING ON BED
    # =========================================================

    def generate_bed_lying(self):
        """
        Person is lying awake and resting on the bed.

        Synthetic target region:
        approximately 65-80 BPM.
        """

        target = random.uniform(65, 78)

        return self._move_towards(
            target=target,
            max_change=1.2
        )

    # =========================================================
    # 2. PERSON SITTING ON BED
    # =========================================================

    def generate_bed_sitting(self):
        """
        Person is sitting calmly on the bed.

        Synthetic target region:
        approximately 68-84 BPM.
        """

        target = random.uniform(68, 84)

        return self._move_towards(
            target=target,
            max_change=1.5
        )

    # =========================================================
    # 3. LYING -> SITTING
    # =========================================================

    def generate_lying_to_sitting(self):
        """
        Simulates the person changing from lying
        to sitting on the bed.

        HR gradually increases.
        """

        target = random.uniform(78, 88)

        return self._move_towards(
            target=target,
            max_change=2.0
        )

    # =========================================================
    # 4. SITTING -> LYING
    # =========================================================

    def generate_sitting_to_lying(self):
        """
        Simulates the person changing from sitting
        to lying on the bed.

        HR gradually decreases.
        """

        target = random.uniform(65, 74)

        return self._move_towards(
            target=target,
            max_change=2.0
        )

    # =========================================================
    # 5. SLEEPING
    # =========================================================

    def generate_sleeping(self):
        """
        Simulates sleeping while lying on the bed.

        Synthetic target region:
        approximately 55-70 BPM.
        """

        target = random.uniform(55, 70)

        return self._move_towards(
            target=target,
            max_change=0.8
        )

    # =========================================================
    # 6. SUSTAINED UNUSUAL HR
    # =========================================================

    def generate_unusual_hr(self):
        """
        Generates sustained elevated HR for software testing.

        This is NOT a medical diagnosis.
        """

        target = random.uniform(100, 115)

        return self._move_towards(
            target=target,
            max_change=2.0
        )

    # =========================================================
    # 7. SENSOR ARTIFACT
    # =========================================================

    def generate_artifact(self):
        """
        Simulates one suspicious sensor measurement.

        Used later to test whether our validator can
        identify an isolated abnormal reading.
        """

        return random.randint(120, 150)

    # =========================================================
    # 8. MISSING DATA
    # =========================================================

    def generate_missing(self):
        """
        Simulates temporary loss of heart-rate data.
        """

        return None

    # =========================================================
    # MAIN READING FUNCTION
    # =========================================================

    def get_reading(self, mode="bed_lying"):
        """
        Generate one timestamped HR reading.
        """

        if mode == "bed_lying":

            hr = self.generate_bed_lying()

        elif mode == "bed_sitting":

            hr = self.generate_bed_sitting()

        elif mode == "lying_to_sitting":

            hr = self.generate_lying_to_sitting()

        elif mode == "sitting_to_lying":

            hr = self.generate_sitting_to_lying()

        elif mode == "sleeping":

            hr = self.generate_sleeping()

        elif mode == "unusual":

            hr = self.generate_unusual_hr()

        elif mode == "artifact":

            hr = self.generate_artifact()

        elif mode == "missing":

            hr = self.generate_missing()

        else:

            raise ValueError(
                "\nInvalid mode.\n\n"
                "Available modes:\n"
                "  bed_lying\n"
                "  bed_sitting\n"
                "  lying_to_sitting\n"
                "  sitting_to_lying\n"
                "  sleeping\n"
                "  unusual\n"
                "  artifact\n"
                "  missing\n"
            )

        return {
            "timestamp": datetime.now().isoformat(
                timespec="seconds"
            ),
            "heart_rate": hr
        }


# =============================================================
# MAIN TEST
# =============================================================

if __name__ == "__main__":

    simulator = HeartRateSimulator(
        resting_hr=72
    )

    # ---------------------------------------------------------
    # CHANGE ONLY THIS VALUE TO TEST DIFFERENT SCENARIOS
    # ---------------------------------------------------------

    MODE = "bed_sitting"

    # Available:
    #
    # "bed_lying"
    # "bed_sitting"
    # "lying_to_sitting"
    # "sitting_to_lying"
    # "sleeping"
    # "unusual"
    # "artifact"
    # "missing"

    # ---------------------------------------------------------

    print("=" * 60)
    print("❤️  SANJEEVANI AI")
    print("    BED HEART RATE SIMULATOR")
    print("=" * 60)

    print(f"\nMode: {MODE.upper()}")
    print("Sampling interval: 5 seconds")
    print("Press CTRL+C to stop.\n")

    try:

        while True:

            reading = simulator.get_reading(
                mode=MODE
            )

            timestamp = reading["timestamp"]
            heart_rate = reading["heart_rate"]

            if heart_rate is None:

                print(
                    f"{timestamp} | "
                    "HR: MISSING"
                )

            else:

                print(
                    f"{timestamp} | "
                    f"HR: {heart_rate} BPM"
                )

            time.sleep(5)

    except KeyboardInterrupt:

        print("\n\nSimulator stopped.")