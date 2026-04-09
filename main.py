"""
main.py — Object Size Measurement Tool
=======================================
Turns your webcam into a real-time digital ruler using your ID card
as the calibration reference.

Quick start
-----------
  1.  pip install opencv-contrib-python numpy
  2.  python main.py
  3.  Place your ID card on the left side of the frame
  4.  Put any object next to it — dimensions appear instantly

Controls
--------
  S   Save annotated screenshot  +  append to today's CSV log
  P   Toggle birds-eye perspective correction (needs A4 paper as mat)
  Q   Quit

Output
------
  Screenshots  →  output/screenshots/measurement_YYYYMMDD_HHMMSS.png
  CSV log      →  output/logs/measurements_YYYY-MM-DD.csv
"""

import sys
import cv2

from config           import CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT
from measurer.detector    import measure_frame
from measurer.perspective import warp_to_birds_eye
from measurer.visualizer  import draw_detections, draw_hud
from utils.logger         import log_measurements
from utils.saver          import save_screenshot


# Camera initialisation


def open_camera(index: int) -> cv2.VideoCapture:
    """
    Open the webcam and set the desired resolution.
    Exits with a clear message if the camera can't be reached — much better
    than an obscure OpenCV segfault.
    """
    cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)  # CAP_DSHOW = faster on Windows
    if not cap.isOpened():
        sys.exit(
            f"\n[ERROR] Could not open camera at index {index}.\n"
            "  - Make sure no other app (Teams, Zoom) is using the camera.\n"
            "  - Try changing CAMERA_INDEX in config.py (0, 1, 2 ...).\n"
        )

    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)   # let the camera autofocus

    # Read back actual resolution (camera might cap at a lower value)
    actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"[Camera] Opened at {actual_w}x{actual_h}  (index {index})")
    return cap


# Main loop

def run() -> None:
    cap            = open_camera(CAMERA_INDEX)
    perspective_on = False

    print("\nObject Measurer is running.")
    print("  Place your ID card on the LEFT side of the frame to calibrate.\n")

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            # A dropped frame is normal; just skip it
            continue

        
        # 1. (Optional) Warp to birds-eye view for better accuracy
       
        working = frame.copy()
        if perspective_on:
            working, matrix = warp_to_birds_eye(working)
            if matrix is None:
                # Paper not detected — show a hint on the raw frame instead
                cv2.putText(working,
                            "Perspective ON: show A4 paper fully in frame",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                            (0, 220, 220), 1, cv2.LINE_AA)

        # 2. Detect objects and measure them
        detections  = measure_frame(working)
        ref_found   = any(d.is_reference for d in detections)
        obj_count   = sum(1 for d in detections if not d.is_reference)

        # 3. Draw everything on the frame
        draw_detections(working, detections)
        draw_hud(working, perspective_on, ref_found, obj_count)

        cv2.imshow("Object Measurer  —  S: Save  |  P: Perspective  |  Q: Quit", working)

        # 4. Handle keypresses
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            print("\nQuitting.")
            break

        elif key == ord("s"):
            save_screenshot(working)
            log_measurements(detections)

        elif key == ord("p"):
            perspective_on = not perspective_on
            state = "ON  (lay A4 paper flat in view)" if perspective_on else "OFF"
            print(f"[Perspective] {state}")

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run()
