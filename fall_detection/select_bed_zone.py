"""
select_bed_zone.py
==================
Tool to manually select bed zone.

How to use:
1. Run this file.
2. Camera window opens in fullscreen / maximum size.
3. Click 4 corners of the bed.
4. Press 's' to save.
5. Press 'r' to reset.
6. Press 'q' to quit.
"""

import cv2
import os
import json


BED_ZONE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "output",
    "bed_zone.json"
)

points = []


def mouse_callback(event, x, y, flags, param):
    global points

    if event == cv2.EVENT_LBUTTONDOWN:
        if len(points) < 4:
            points.append((x, y))
            print(f"[BED_ZONE] Point added: {(x, y)}")

        if len(points) == 4:
            print("[BED_ZONE] 4 points selected. Press 's' to save.")


def save_points():
    os.makedirs(os.path.dirname(BED_ZONE_FILE), exist_ok=True)

    with open(BED_ZONE_FILE, "w", encoding="utf-8") as f:
        json.dump({"points": points}, f, indent=4)

    print(f"[BED_ZONE] Saved to: {BED_ZONE_FILE}")


def main():
    global points

    cap = cv2.VideoCapture(1)

    # ── UPDATED: Try to open camera in higher resolution ─────────────
    # This helps you see the bed clearly and select corners accurately.
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    if not cap.isOpened():
        print("[ERROR] Camera not opened.")
        return

    # ── UPDATED: Open bed selection window in fullscreen ─────────────
    cv2.namedWindow("Select Bed Zone", cv2.WINDOW_NORMAL)

    cv2.setWindowProperty(
        "Select Bed Zone",
        cv2.WND_PROP_FULLSCREEN,
        cv2.WINDOW_FULLSCREEN
    )

    cv2.setMouseCallback("Select Bed Zone", mouse_callback)

    print("\nInstructions:")
    print("1. Click 4 corners of the bed.")
    print("2. Press 's' to save.")
    print("3. Press 'r' to reset.")
    print("4. Press 'q' to quit.\n")

    print("Click order:")
    print("P1 = top-left mattress corner")
    print("P2 = top-right mattress corner")
    print("P3 = bottom-right mattress corner")
    print("P4 = bottom-left mattress corner\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        display = frame.copy()

        # Draw selected points
        for i, p in enumerate(points):
            cv2.circle(display, p, 6, (0, 0, 255), -1)
            cv2.putText(
                display,
                str(i + 1),
                (p[0] + 8, p[1] - 8),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 255),
                2
            )

        # Draw lines between selected points
        if len(points) >= 2:
            for i in range(len(points) - 1):
                cv2.line(
                    display,
                    points[i],
                    points[i + 1],
                    (255, 0, 255),
                    2
                )

        # Close polygon when 4 points selected
        if len(points) == 4:
            cv2.line(
                display,
                points[3],
                points[0],
                (255, 0, 255),
                2
            )

            cv2.putText(
                display,
                "Press 's' to save bed zone",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

        else:
            cv2.putText(
                display,
                f"Click bed corners: {len(points)}/4",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 255),
                2
            )

        # Show help text on screen
        cv2.putText(
            display,
            "s = save | r = reset | q = quit",
            (20, 75),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2
        )

        cv2.imshow("Select Bed Zone", display)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("s"):
            if len(points) == 4:
                save_points()
            else:
                print("[BED_ZONE] Please select exactly 4 points first.")

        elif key == ord("r"):
            points = []
            print("[BED_ZONE] Points reset.")

        elif key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()