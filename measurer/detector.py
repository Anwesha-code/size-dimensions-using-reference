"""
measurer/detector.py — The measurement brain
============================================
Pipeline:
  1. Preprocess the frame into clean edges (grayscale → blur → Canny)
  2. Find all closed contours (shapes) in the scene
  3. Sort them left-to-right so the card is always processed first
  4. Identify the ID card by its aspect ratio → compute Pixels Per Millimetre
  5. Measure every other detected object using that PPM ratio
  6. Return a list of Detection dataclasses — ready for drawing and logging
"""

import cv2
import numpy as np
from dataclasses import dataclass
from typing import Optional

from config import (
    REF_WIDTH_MM, REF_HEIGHT_MM, REF_ASPECT_RATIO, REF_ASPECT_TOLERANCE,
    MIN_CONTOUR_AREA, GAUSSIAN_BLUR, CANNY_THRESH1, CANNY_THRESH2,
)


# Data model


@dataclass
class Detection:
    """
    Everything we know about one detected object in a frame.
    Passed to the visualizer for drawing and to the logger for saving.
    """
    label: str
    box_points: np.ndarray      # 4 corner points of the rotated bounding rect
    width_mm: float
    height_mm: float
    center: tuple               # (cx, cy) in pixels — used for label placement
    is_reference: bool = False  # True if this is the ID card


# Preprocessing


def preprocess(frame: np.ndarray) -> np.ndarray:
    """
    Turn a colour frame into a crisp edge map.

    Why each step:
      - Grayscale   : colour adds noise, not signal, for shape detection
      - Gaussian    : smooths out minor texture (fabric grain, desk wood)
      - Canny       : finds the sharp brightness cliffs = real object edges
      - Dilate      : closes tiny gaps in contours so they're fully closed loops
    """
    gray    = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, GAUSSIAN_BLUR, 0)
    edges   = cv2.Canny(blurred, CANNY_THRESH1, CANNY_THRESH2)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    edges  = cv2.dilate(edges, kernel, iterations=1)
    return edges


# Contour helpers


def _fit_bounding_box(contour: np.ndarray) -> Optional[tuple]:
    """
    Fit a minimum-area rectangle to a contour.

    cv2.minAreaRect gives us a rotated rectangle (handles objects that aren't
    perfectly axis-aligned). We always return width >= height for consistency.

    Returns (box_points, width_px, height_px, center) or None if too small.
    """
    if cv2.contourArea(contour) < MIN_CONTOUR_AREA:
        return None

    rect                     = cv2.minAreaRect(contour)
    box                      = cv2.boxPoints(rect).astype(np.intp)
    (cx, cy), (w_px, h_px), _ = rect

    # Normalise so width is always the longer side
    if w_px < h_px:
        w_px, h_px = h_px, w_px

    return box, float(w_px), float(h_px), (int(cx), int(cy))


def _looks_like_id_card(w_px: float, h_px: float) -> bool:
    """
    Does this rectangle's aspect ratio match an ID card (within tolerance)?

    We check aspect ratio rather than absolute pixel size because the card
    could be anywhere in the frame and at any distance to the camera.
    """
    if h_px < 1:
        return False
    aspect = w_px / h_px
    deviation = abs(aspect - REF_ASPECT_RATIO) / REF_ASPECT_RATIO
    return deviation <= REF_ASPECT_TOLERANCE


# Main pipeline


def measure_frame(frame: np.ndarray) -> list[Detection]:
    """
    Analyse one frame and return a list of Detection objects.

    The first rectangle whose aspect ratio matches an ID card becomes the
    reference; every subsequent shape is measured using the PPM ratio derived
    from that card.

    If no card is found, we return an empty list — the HUD will show a warning.
    """
    edges = preprocess(frame)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Sort contours left-to-right — ensures the leftmost card-shaped rectangle
    # is processed before any objects we want to measure
    contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[0])

    ppm: Optional[float] = None   # pixels per millimetre — unknown until card found
    detections: list     = []
    ref_found            = False
    obj_index            = 1

    for contour in contours:
        result = _fit_bounding_box(contour)
        if result is None:
            continue

        box, w_px, h_px, center = result

        if not ref_found and _looks_like_id_card(w_px, h_px):
            # ---- Found the ID card: calibrate PPM ----
            # PPM = card's pixel width ÷ card's real width in mm
            ppm       = w_px / REF_WIDTH_MM
            ref_found = True

            detections.append(Detection(
                label        = "ID Card (Reference)",
                box_points   = box,
                width_mm     = REF_WIDTH_MM,
                height_mm    = REF_HEIGHT_MM,
                center       = center,
                is_reference = True,
            ))

        elif ppm is not None:
            # ---- Measure a regular object using calibrated PPM ----
            w_mm = round(w_px / ppm, 1)
            h_mm = round(h_px / ppm, 1)

            detections.append(Detection(
                label      = f"Object {obj_index}",
                box_points = box,
                width_mm   = w_mm,
                height_mm  = h_mm,
                center     = center,
            ))
            obj_index += 1

    return detections
