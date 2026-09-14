import cv2


# ============================================================
# CAMERA SETTINGS
# ============================================================

CAMERA_INDEX = 0

FRAME_WIDTH = 1280
FRAME_HEIGHT = 720


# ============================================================
# CAMERA
# ============================================================

cap = cv2.VideoCapture(CAMERA_INDEX)

if not cap.isOpened():

    print("ERROR: Could not open camera.")
    exit()


# ============================================================
# FORCE SAME RESOLUTION AS BED_ZONE1.PY
# ============================================================

cap.set(
    cv2.CAP_PROP_FRAME_WIDTH,
    FRAME_WIDTH
)

cap.set(
    cv2.CAP_PROP_FRAME_HEIGHT,
    FRAME_HEIGHT
)


# ============================================================
# CHECK ACTUAL RESOLUTION
# ============================================================

actual_width = int(
    cap.get(cv2.CAP_PROP_FRAME_WIDTH)
)

actual_height = int(
    cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
)

print("=" * 70)
print("SANJEEVANI AI")
print("BED ZONE SELECTOR")
print("=" * 70)

print()
print(
    f"Camera resolution: "
    f"{actual_width} x {actual_height}"
)

print()


# ============================================================
# GLOBAL VARIABLES
# ============================================================

drawing = False
moving = False

start_x = 0
start_y = 0

x1 = 0
y1 = 0
x2 = 0
y2 = 0

offset_x = 0
offset_y = 0

has_zone = False


# ============================================================
# MOUSE CALLBACK
# ============================================================

def mouse_callback(event, x, y, flags, param):

    global drawing
    global moving

    global start_x
    global start_y

    global x1
    global y1
    global x2
    global y2

    global offset_x
    global offset_y

    global has_zone

    # --------------------------------------------------------
    # LEFT BUTTON DOWN
    # --------------------------------------------------------

    if event == cv2.EVENT_LBUTTONDOWN:

        # Existing rectangle
        if has_zone:

            if (
                x1 <= x <= x2
                and
                y1 <= y <= y2
            ):

                moving = True

                offset_x = x - x1
                offset_y = y - y1

                return

        # Create new rectangle
        drawing = True

        start_x = x
        start_y = y

        x1 = x
        y1 = y

        x2 = x
        y2 = y

        has_zone = False


    # --------------------------------------------------------
    # MOUSE MOVE
    # --------------------------------------------------------

    elif event == cv2.EVENT_MOUSEMOVE:

        # Creating rectangle
        if drawing:

            x2 = x
            y2 = y


        # Moving rectangle
        elif moving:

            width = x2 - x1
            height = y2 - y1

            x1 = x - offset_x
            y1 = y - offset_y

            x2 = x1 + width
            y2 = y1 + height

            # Keep rectangle inside frame

            if x1 < 0:

                x1 = 0
                x2 = width

            if y1 < 0:

                y1 = 0
                y2 = height

            if x2 > actual_width:

                x2 = actual_width
                x1 = x2 - width

            if y2 > actual_height:

                y2 = actual_height
                y1 = y2 - height


    # --------------------------------------------------------
    # LEFT BUTTON UP
    # --------------------------------------------------------

    elif event == cv2.EVENT_LBUTTONUP:

        if drawing:

            drawing = False

            # Normalize coordinates

            x1 = min(
                start_x,
                x
            )

            y1 = min(
                start_y,
                y
            )

            x2 = max(
                start_x,
                x
            )

            y2 = max(
                start_y,
                y
            )

            has_zone = True

        elif moving:

            moving = False


# ============================================================
# CREATE WINDOW
# ============================================================

window_name = "Sanjeevani AI - Bed Zone Selector"

cv2.namedWindow(
    window_name,
    cv2.WINDOW_NORMAL
)

cv2.resizeWindow(
    window_name,
    FRAME_WIDTH,
    FRAME_HEIGHT
)

cv2.setMouseCallback(
    window_name,
    mouse_callback
)


# ============================================================
# MAIN LOOP
# ============================================================

while True:

    ret, frame = cap.read()

    if not ret:

        print(
            "ERROR: Could not read camera frame."
        )

        break


    # --------------------------------------------------------
    # MAKE SURE FRAME HAS EXPECTED SIZE
    # --------------------------------------------------------

    if (
        frame.shape[1] != FRAME_WIDTH
        or
        frame.shape[0] != FRAME_HEIGHT
    ):

        frame = cv2.resize(
            frame,
            (
                FRAME_WIDTH,
                FRAME_HEIGHT
            )
        )


    display = frame.copy()


    # ========================================================
    # DRAW BED ZONE
    # ========================================================

    if has_zone:

        cv2.rectangle(
            display,
            (x1, y1),
            (x2, y2),
            (255, 0, 0),
            3
        )


        cv2.putText(
            display,
            "BED ZONE",
            (
                x1,
                max(
                    y1 - 10,
                    30
                )
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 0, 0),
            2
        )


        # ----------------------------------------------------
        # COORDINATES
        # ----------------------------------------------------

        coordinate_text = (
            f"({x1}, {y1}) -> "
            f"({x2}, {y2})"
        )


        cv2.putText(
            display,
            coordinate_text,
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )


    # ========================================================
    # INSTRUCTIONS
    # ========================================================

    cv2.rectangle(
        display,
        (
            10,
            FRAME_HEIGHT - 70
        ),
        (
            FRAME_WIDTH - 10,
            FRAME_HEIGHT - 10
        ),
        (0, 0, 0),
        -1
    )


    cv2.putText(
        display,
        "Drag = Create | "
        "Drag inside = Move | "
        "R = Reset | "
        "S = Save | "
        "Q = Quit",
        (
            20,
            FRAME_HEIGHT - 35
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2
    )


    # ========================================================
    # DISPLAY
    # ========================================================

    cv2.imshow(
        window_name,
        display
    )


    key = cv2.waitKey(1) & 0xFF


    # ========================================================
    # RESET
    # ========================================================

    if key == ord("r"):

        has_zone = False

        x1 = 0
        y1 = 0
        x2 = 0
        y2 = 0

        print(
            "Bed zone reset."
        )


    # ========================================================
    # SAVE
    # ========================================================

    elif key == ord("s"):

        if has_zone:

            with open(
                "bed.txt",
                "w"
            ) as file:

                file.write(
                    f"{x1},{y1},{x2},{y2}"
                )


            print()
            print("=" * 70)
            print("BED ZONE SAVED")
            print("=" * 70)

            print(
                f"BED_ZONE = "
                f"({x1}, {y1}, {x2}, {y2})"
            )

            print(
                "Saved to: bed.txt"
            )

            print("=" * 70)


        else:

            print(
                "Please create a bed zone first."
            )


    # ========================================================
    # QUIT
    # ========================================================

    elif key == ord("q"):

        break


# ============================================================
# CLEANUP
# ============================================================

cap.release()

cv2.destroyAllWindows()


print()
print("=" * 70)
print("BED ZONE SELECTOR STOPPED")
print("=" * 70)