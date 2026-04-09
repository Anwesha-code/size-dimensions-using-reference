"""
measurer/perspective.py — Birds-eye-view perspective correction
===============================================================
Problem this solves:
  When your laptop camera is angled (not perfectly overhead), objects further
  from the camera look slightly smaller than identical objects near it.
  This breaks the "one PPM for the whole frame" assumption.

Solution:
  Place a white A4 sheet as your workspace mat.
  This module detects its four corners, then warps the image so it looks
  like the camera is looking straight down — a flat, undistorted view.

How to use:
  Toggle on/off with the [P] key in the main loop.
  When ON, place your A4 paper flat on the desk and ensure all four edges
  are visible in frame. Lay your ID card and objects on top of the paper.
"""

import cv2
import numpy as np
from typing import Optional

from config import GAUSSIAN_BLUR, CANNY_THRESH1, CANNY_THRESH2, WARP_WIDTH, WARP_HEIGHT


# Corner ordering helper


def _order_corners(pts: np.ndarray) -> np.ndarray:
    """
    Sort 4 corner points into a consistent order:
      [top-left, top-right, bottom-right, bottom-left]

    This is critical for getPerspectiveTransform — if the corners are in
    the wrong order, the warp will flip or rotate the image unexpectedly.

    Trick: top-left has the smallest (x+y); bottom-right has the largest.
           top-right has the smallest (x-y); bottom-left has the largest.
    """
    rect = np.zeros((4, 2), dtype=np.float32)
    s    = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)

    rect[0] = pts[np.argmin(s)]     # top-left
    rect[2] = pts[np.argmax(s)]     # bottom-right
    rect[1] = pts[np.argmin(diff)]  # top-right
    rect[3] = pts[np.argmax(diff)]  # bottom-left
    return rect

# Paper/workspace detection


def _find_largest_rectangle(frame: np.ndarray) -> Optional[np.ndarray]:
    """
    Find the largest 4-sided contour in the frame — assumed to be the A4 mat.

    We check only the top-5 largest contours for speed; the paper is almost
    always the biggest thing in a tidy desk scene.

    Returns 4 corner points as float32, or None if nothing suitable found.
    """
    gray    = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, GAUSSIAN_BLUR, 0)
    edges   = cv2.Canny(blurred, CANNY_THRESH1, CANNY_THRESH2)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours     = sorted(contours, key=cv2.contourArea, reverse=True)

    for contour in contours[:5]:
        perimeter  = cv2.arcLength(contour, closed=True)
        approx     = cv2.approxPolyDP(contour, 0.02 * perimeter, closed=True)

        if len(approx) == 4:
            return approx.reshape(4, 2).astype(np.float32)

    return None


# Public API


def warp_to_birds_eye(frame: np.ndarray) -> tuple[np.ndarray, Optional[np.ndarray]]:
    """
    Attempt to warp the frame into a flat, top-down birds-eye view.

    Steps:
      1. Find the four corners of the A4 mat
      2. Map those corners to the four corners of a fixed output canvas
      3. Apply the perspective transform

    Returns:
      (warped_frame, transform_matrix)

    If no rectangle is found (e.g. the paper isn't fully visible), the
    original frame is returned unchanged and matrix is None — so the caller
    can degrade gracefully without crashing.
    """
    corners = _find_largest_rectangle(frame)

    if corners is None:
        return frame, None   # graceful fallback

    # Source points: the detected corners in the original frame
    src = _order_corners(corners)

    # Destination points: the four corners of our output canvas
    dst = np.array([
        [0,            0           ],
        [WARP_WIDTH-1, 0           ],
        [WARP_WIDTH-1, WARP_HEIGHT-1],
        [0,            WARP_HEIGHT-1],
    ], dtype=np.float32)

    matrix = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(frame, matrix, (WARP_WIDTH, WARP_HEIGHT))

    return warped, matrix
