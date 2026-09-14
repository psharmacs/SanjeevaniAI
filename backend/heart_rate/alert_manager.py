from datetime import datetime


class HeartRateAlertManager:
    """
    Converts analyzer results into system actions.

    Status:
        NORMAL
        WATCH
        ALERT

    This is a software alert layer.
    It does NOT provide a medical diagnosis.
    """

    def __init__(self, cooldown_seconds=30):

        self.cooldown_seconds = cooldown_seconds

        self.last_alert_time = None

        self.alert_count = 0
        self.watch_count = 0

    # =========================================================
    # CHECK ALERT COOLDOWN
    # =========================================================

    def _can_send_alert(self):

        if self.last_alert_time is None:
            return True

        current_time = datetime.now()

        elapsed = (
            current_time - self.last_alert_time
        ).total_seconds()

        return elapsed >= self.cooldown_seconds

    # =========================================================
    # NORMAL
    # =========================================================

    def _handle_normal(self, result):

        return {
            "action": "NO_ACTION",
            "priority": "LOW",
            "message": (
                "Heart rate is within the "
                "current monitoring pattern"
            ),
            "notification": False
        }

    # =========================================================
    # WATCH
    # =========================================================

    def _handle_watch(self, result):

        self.watch_count += 1

        return {
            "action": "CONTINUE_MONITORING",
            "priority": "MEDIUM",
            "message": result.get(
                "reason",
                "Heart-rate pattern requires monitoring"
            ),
            "notification": False
        }

    # =========================================================
    # ALERT
    # =========================================================

    def _handle_alert(self, result):

        if not self._can_send_alert():

            return {
                "action": "ALERT_SUPPRESSED",
                "priority": "HIGH",
                "message": (
                    "Alert condition persists, "
                    "but notification is in cooldown"
                ),
                "notification": False
            }

        self.last_alert_time = datetime.now()

        self.alert_count += 1

        return {
            "action": "GENERATE_ALERT",
            "priority": "HIGH",
            "message": result.get(
                "reason",
                "Abnormal heart-rate pattern detected"
            ),
            "notification": True
        }

    # =========================================================
    # MAIN HANDLER
    # =========================================================

    def handle(self, analyzer_result):

        if not analyzer_result:

            return {
                "action": "NO_ACTION",
                "priority": "LOW",
                "message": "No analyzer result available",
                "notification": False
            }

        status = analyzer_result.get(
            "status"
        )

        # -----------------------------------------------------
        # NORMAL
        # -----------------------------------------------------

        if status == "NORMAL":

            return self._handle_normal(
                analyzer_result
            )

        # -----------------------------------------------------
        # WATCH
        # -----------------------------------------------------

        if status == "WATCH":

            return self._handle_watch(
                analyzer_result
            )

        # -----------------------------------------------------
        # ALERT
        # -----------------------------------------------------

        if status == "ALERT":

            return self._handle_alert(
                analyzer_result
            )

        # -----------------------------------------------------
        # NO DATA
        # -----------------------------------------------------

        if status == "NO_DATA":

            return {
                "action": "DATA_UNAVAILABLE",
                "priority": "MEDIUM",
                "message": (
                    "Heart-rate data is unavailable"
                ),
                "notification": False
            }

        # -----------------------------------------------------
        # UNKNOWN STATUS
        # -----------------------------------------------------

        return {
            "action": "NO_ACTION",
            "priority": "LOW",
            "message": (
                f"Unknown analyzer status: {status}"
            ),
            "notification": False
        }

    # =========================================================
    # SUMMARY
    # =========================================================

    def get_summary(self):

        return {
            "watch_events": self.watch_count,
            "alerts_generated": self.alert_count
        }


# =============================================================
# TEST
# =============================================================

if __name__ == "__main__":

    print("=" * 65)
    print("❤️ SANJEEVANI AI")
    print("   HEART RATE ALERT MANAGER")
    print("=" * 65)

    manager = HeartRateAlertManager(
        cooldown_seconds=30
    )

    # ---------------------------------------------------------
    # TEST 1: NORMAL
    # ---------------------------------------------------------

    print("\nTEST 1: NORMAL")
    print("-" * 65)

    normal_result = {
        "status": "NORMAL",
        "reason": (
            "No unusual heart-rate pattern detected"
        )
    }

    response = manager.handle(
        normal_result
    )

    print(
        f"Status: NORMAL"
    )

    print(
        f"Action: {response['action']}"
    )

    print(
        f"Priority: {response['priority']}"
    )

    print(
        f"Message: {response['message']}"
    )

    print(
        f"Notification: {response['notification']}"
    )

    # ---------------------------------------------------------
    # TEST 2: WATCH
    # ---------------------------------------------------------

    print("\nTEST 2: WATCH")
    print("-" * 65)

    watch_result = {
        "status": "WATCH",
        "reason": (
            "Heart rate shows a consistent "
            "increasing trend"
        )
    }

    response = manager.handle(
        watch_result
    )

    print(
        f"Status: WATCH"
    )

    print(
        f"Action: {response['action']}"
    )

    print(
        f"Priority: {response['priority']}"
    )

    print(
        f"Message: {response['message']}"
    )

    print(
        f"Notification: {response['notification']}"
    )

    # ---------------------------------------------------------
    # TEST 3: ALERT
    # ---------------------------------------------------------

    print("\nTEST 3: ALERT")
    print("-" * 65)

    alert_result = {
        "status": "ALERT",
        "reason": (
            "Sustained elevated heart-rate "
            "pattern detected"
        )
    }

    response = manager.handle(
        alert_result
    )

    print(
        f"Status: ALERT"
    )

    print(
        f"Action: {response['action']}"
    )

    print(
        f"Priority: {response['priority']}"
    )

    print(
        f"Message: {response['message']}"
    )

    print(
        f"Notification: {response['notification']}"
    )

    # ---------------------------------------------------------
    # TEST 4: SECOND ALERT
    # ---------------------------------------------------------

    print("\nTEST 4: REPEATED ALERT")
    print("-" * 65)

    response = manager.handle(
        alert_result
    )

    print(
        f"Status: ALERT"
    )

    print(
        f"Action: {response['action']}"
    )

    print(
        f"Priority: {response['priority']}"
    )

    print(
        f"Message: {response['message']}"
    )

    print(
        f"Notification: {response['notification']}"
    )

    # ---------------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------------

    print("\nSYSTEM SUMMARY")
    print("-" * 65)

    summary = manager.get_summary()

    print(
        f"Watch events: "
        f"{summary['watch_events']}"
    )

    print(
        f"Alerts generated: "
        f"{summary['alerts_generated']}"
    )