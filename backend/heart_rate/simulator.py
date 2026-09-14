import random
import time
from datetime import datetime


class HeartRateSimulator:
    """
    Continuous heart-rate simulator for Sanjeevani AI.

    The simulator produces a continuous stream of
    realistic-looking heart-rate readings.

    It deliberately passes through different physiological
    patterns so the monitoring pipeline can be tested:

        NORMAL
        INCREASING
        SUSTAINED HIGH
        RECOVERY
        NORMAL
        DECREASING
        SUSTAINED LOW
        RECOVERY
        NORMAL
        SENSOR SPIKE
        NORMAL
        ...

    This is TEST/SIMULATION data.
    It is NOT real medical sensor data.
    """

    def __init__(self, interval=1.0):

        self.interval = interval

        # Current simulated HR
        self.current_hr = 72.0

        # Current phase
        self.phase = "NORMAL"

        # Number of readings in current phase
        self.phase_readings = 0

        # Random generator
        self.random = random.Random()

        # -----------------------------------------------------
        # Phase sequence
        # -----------------------------------------------------

        self.phases = [

            # Normal resting HR
            ("NORMAL", 15),

            # Gradual increase
            ("INCREASING", 10),

            # Sustained high HR
            ("SUSTAINED_HIGH", 8),

            # Recovery
            ("RECOVERY_FROM_HIGH", 12),

            # Normal
            ("NORMAL", 12),

            # Gradual decrease
            ("DECREASING", 10),

            # Sustained low HR
            ("SUSTAINED_LOW", 8),

            # Recovery
            ("RECOVERY_FROM_LOW", 12),

            # Normal
            ("NORMAL", 12),

            # Sensor spike
            ("SENSOR_SPIKE", 1),

            # Back to normal
            ("NORMAL", 15),
        ]

        self.phase_index = 0

        self.phase = self.phases[0][0]

        self.phase_length = self.phases[0][1]

    # =========================================================
    # MOVE TO NEXT PHASE
    # =========================================================

    def _next_phase(self):

        self.phase_index += 1

        if self.phase_index >= len(self.phases):

            self.phase_index = 0

        self.phase, self.phase_length = (
            self.phases[self.phase_index]
        )

        self.phase_readings = 0

    # =========================================================
    # GENERATE NORMAL HR
    # =========================================================

    def _normal(self):

        target = 72

        change = (
            target - self.current_hr
        ) * 0.25

        noise = self.random.uniform(
            -1.5,
            1.5
        )

        self.current_hr += (
            change + noise
        )

        self.current_hr = max(
            68,
            min(78, self.current_hr)
        )

        return round(
            self.current_hr
        )

    # =========================================================
    # INCREASING HR
    # =========================================================

    def _increasing(self):

        self.current_hr += self.random.uniform(
            2.0,
            4.0
        )

        noise = self.random.uniform(
            -1.0,
            1.0
        )

        self.current_hr += noise

        self.current_hr = min(
            110,
            self.current_hr
        )

        return round(
            self.current_hr
        )

    # =========================================================
    # SUSTAINED HIGH
    # =========================================================

    def _sustained_high(self):

        target = 106

        adjustment = (
            target - self.current_hr
        ) * 0.35

        noise = self.random.uniform(
            -2,
            2
        )

        self.current_hr += (
            adjustment + noise
        )

        self.current_hr = max(
            102,
            min(110, self.current_hr)
        )

        return round(
            self.current_hr
        )

    # =========================================================
    # RECOVERY FROM HIGH
    # =========================================================

    def _recovery_from_high(self):

        target = 74

        change = (
            target - self.current_hr
        ) * 0.20

        noise = self.random.uniform(
            -1.5,
            1.5
        )

        self.current_hr += (
            change + noise
        )

        self.current_hr = max(
            72,
            min(105, self.current_hr)
        )

        return round(
            self.current_hr
        )

    # =========================================================
    # DECREASING HR
    # =========================================================

    def _decreasing(self):

        self.current_hr -= self.random.uniform(
            2.0,
            4.0
        )

        noise = self.random.uniform(
            -1.0,
            1.0
        )

        self.current_hr += noise

        self.current_hr = max(
            42,
            self.current_hr
        )

        return round(
            self.current_hr
        )

    # =========================================================
    # SUSTAINED LOW
    # =========================================================

    def _sustained_low(self):

        target = 47

        adjustment = (
            target - self.current_hr
        ) * 0.35

        noise = self.random.uniform(
            -1.5,
            1.5
        )

        self.current_hr += (
            adjustment + noise
        )

        self.current_hr = max(
            44,
            min(50, self.current_hr)
        )

        return round(
            self.current_hr
        )

    # =========================================================
    # RECOVERY FROM LOW
    # =========================================================

    def _recovery_from_low(self):

        target = 73

        change = (
            target - self.current_hr
        ) * 0.20

        noise = self.random.uniform(
            -1.5,
            1.5
        )

        self.current_hr += (
            change + noise
        )

        self.current_hr = min(
            78,
            max(45, self.current_hr)
        )

        return round(
            self.current_hr
        )

    # =========================================================
    # SENSOR SPIKE
    # =========================================================

    def _sensor_spike(self):

        # Deliberate impossible/sudden measurement jump
        return 145

    # =========================================================
    # GENERATE ONE READING
    # =========================================================

    def generate_reading(self):

        # Move to next phase if necessary
        if self.phase_readings >= self.phase_length:

            self._next_phase()

        # -----------------------------------------------------
        # Generate HR according to phase
        # -----------------------------------------------------

        if self.phase == "NORMAL":

            hr = self._normal()

        elif self.phase == "INCREASING":

            hr = self._increasing()

        elif self.phase == "SUSTAINED_HIGH":

            hr = self._sustained_high()

        elif self.phase == "RECOVERY_FROM_HIGH":

            hr = self._recovery_from_high()

        elif self.phase == "DECREASING":

            hr = self._decreasing()

        elif self.phase == "SUSTAINED_LOW":

            hr = self._sustained_low()

        elif self.phase == "RECOVERY_FROM_LOW":

            hr = self._recovery_from_low()

        elif self.phase == "SENSOR_SPIKE":

            hr = self._sensor_spike()

        else:

            hr = self._normal()

        self.phase_readings += 1

        return {
            "timestamp": datetime.now().strftime(
                "%Y-%m-%dT%H:%M:%S"
            ),
            "heart_rate": hr,
            "simulator_phase": self.phase
        }

    # =========================================================
    # CONTINUOUS GENERATOR
    # =========================================================

    def stream(self):

        while True:

            reading = self.generate_reading()

            yield reading

            time.sleep(
                self.interval
            )


# =============================================================
# TEST SIMULATOR
# =============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("❤️ SANJEEVANI AI")
    print("   CONTINUOUS HEART RATE SIMULATOR")
    print("=" * 70)

    print()

    print(
        "Generating continuous simulated HR data..."
    )

    print(
        "Press CTRL+C to stop."
    )

    print()

    simulator = HeartRateSimulator(
        interval=1
    )

    try:

        for reading in simulator.stream():

            print(
                f"Time: {reading['timestamp']} | "
                f"HR: {reading['heart_rate']} BPM | "
                f"Phase: {reading['simulator_phase']}"
            )

    except KeyboardInterrupt:

        print()
        print("=" * 70)
        print("SIMULATOR STOPPED")
        print("=" * 70)