from datetime import datetime


class HeartRateValidator:
    """
    Validates raw heart-rate readings before they are
    passed to the processing and analysis stages.

    This module does NOT determine whether a person's
    heart rate is medically normal or abnormal.
    """

    def __init__(self, minimum_hr=30, maximum_hr=220):
        self.minimum_hr = minimum_hr
        self.maximum_hr = maximum_hr

    # =========================================================
    # CHECK HEART RATE VALUE
    # =========================================================

    def validate_heart_rate(self, heart_rate):
        """
        Validate the heart-rate value.

        Returns:
            True  -> value can be processed
            False -> value should not be processed
        """

        # Missing value
        if heart_rate is None:
            return False

        # Check numeric type
        if not isinstance(heart_rate, (int, float)):
            return False

        # Check valid numerical range
        if heart_rate < self.minimum_hr:
            return False

        if heart_rate > self.maximum_hr:
            return False

        return True

    # =========================================================
    # CHECK COMPLETE READING
    # =========================================================

    def validate_reading(self, reading):
        """
        Validate a complete HR reading.

        Expected format:

        {
            "timestamp": "...",
            "heart_rate": 72
        }
        """

        # Check that reading is a dictionary
        if not isinstance(reading, dict):
            return {
                "valid": False,
                "reason": "Invalid reading format"
            }

        # Check timestamp
        timestamp = reading.get("timestamp")

        if timestamp is None:
            return {
                "valid": False,
                "reason": "Missing timestamp"
            }

        # Check timestamp format
        try:
            datetime.fromisoformat(timestamp)

        except (ValueError, TypeError):
            return {
                "valid": False,
                "reason": "Invalid timestamp"
            }

        # Get HR
        heart_rate = reading.get("heart_rate")

        # Missing HR
        if heart_rate is None:
            return {
                "valid": False,
                "reason": "Heart rate missing"
            }

        # Validate HR
        if not isinstance(heart_rate, (int, float)):
            return {
                "valid": False,
                "reason": "Heart rate is not numeric"
            }

        # Check HR range
        if heart_rate < self.minimum_hr:
            return {
                "valid": False,
                "reason": "Heart rate below sensor validation range"
            }

        if heart_rate > self.maximum_hr:
            return {
                "valid": False,
                "reason": "Heart rate above sensor validation range"
            }

        # Everything is valid
        return {
            "valid": True,
            "reason": "Valid reading"
        }


# =============================================================
# TEST
# =============================================================

if __name__ == "__main__":

    validator = HeartRateValidator()

    test_readings = [

        {
            "timestamp": "2026-08-30T15:50:00",
            "heart_rate": 72
        },

        {
            "timestamp": "2026-08-30T15:50:05",
            "heart_rate": 78
        },

        {
            "timestamp": "2026-08-30T15:50:10",
            "heart_rate": None
        },

        {
            "timestamp": "2026-08-30T15:50:15",
            "heart_rate": 250
        },

        {
            "timestamp": "2026-08-30T15:50:20",
            "heart_rate": "72"
        },

        {
            "timestamp": "wrong-time",
            "heart_rate": 75
        }
    ]

    print("=" * 60)
    print("❤️ SANJEEVANI AI")
    print("   HEART RATE DATA VALIDATOR")
    print("=" * 60)

    print()

    for reading in test_readings:

        result = validator.validate_reading(reading)

        print(
            f"HR: {reading.get('heart_rate')} | "
            f"Valid: {result['valid']} | "
            f"Reason: {result['reason']}"
        )