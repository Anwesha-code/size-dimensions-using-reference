"""
utils/saver.py — Annotated screenshot saving
=============================================
Saves the current frame (with bounding boxes and labels already drawn)
as a PNG with a human-readable timestamp in the filename.

Save location:  output/screenshots/measurement_YYYYMMDD_HHMMSS.png

This is the file you'll attach to your project submission or demo slides.
"""

import cv2
import numpy as np
from datetime import datetime
from pathlib import Path

from config import SCREENSHOTS_DIR


def save_screenshot(frame: np.ndarray) -> Path:
    """
    Write an annotated frame to the screenshots folder.

    The timestamp in the filename makes it easy to match screenshots
    against the corresponding rows in the CSV log.

    Returns the full path of the saved file.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = SCREENSHOTS_DIR / f"measurement_{timestamp}.png"

    success = cv2.imwrite(str(file_path), frame)

    if success:
        print(f"[Saver] Screenshot saved  -->  {file_path}")
    else:
        print(f"[Saver] ERROR: Could not write to {file_path}")

    return file_path
