"""
measurer/visualizer.py — Everything visual that overlays on the frame
=====================================================================
Responsibilities:
  - draw_detections : coloured rotated bounding boxes + dimension labels
  - draw_hud        : top-left status panel (mode, controls, card status)

Colour scheme (BGR):
  Green   → reference ID card
  Blue    → measured objects
  Yellow  → status text highlights
  White   → neutral HUD text
"""

import cv2
import numpy as np
from measurer.detector import Detection


# ---- Colours (BGR order for OpenCV) ----
GREEN  = (34,  197, 94 )
BLUE   = (235, 130, 59 )
WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0  )
YELLOW = (0,   220, 220)
RED    = (60,  60,  220)

# Label drawing


def _draw_label(frame: np.ndarray,
                text: str,
                anchor: tuple,
                color: tuple) -> None:
    """
    Draw text with a semi-transparent dark pill background so it's readable
    over any surface — white desk, dark wood, whatever.

    anchor = (x, y) is the bottom-centre of the label.
    """
    font       = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.52
    thickness  = 1
    pad        = 5

    (tw, th), _ = cv2.getTextSize(text, font, font_scale, thickness)
    ax, ay = anchor

    # Pill background
    x1, y1 = ax - tw // 2 - pad, ay - th - pad * 2
    x2, y2 = ax + tw // 2 + pad, ay + pad

    overlay = frame.copy()
    cv2.rectangle(overlay, (x1, y1), (x2, y2), BLACK, -1)
    cv2.addWeighted(overlay, 0.55, frame, 0.45, 0, frame)  # semi-transparent

    # Text
    cv2.putText(frame, text,
                (ax - tw // 2, ay - pad),
                font, font_scale, color, thickness, cv2.LINE_AA)



# Detections overlay


def draw_detections(frame: np.ndarray, detections: list[Detection]) -> None:
    """
    For each detection, draw:
      - A rotated bounding box (coloured by type)
      - A small dot at the centre point
      - A dimension label: "Width x Height mm"
    """
    for d in detections:
        color = GREEN if d.is_reference else BLUE

        # Rotated bounding box
        cv2.drawContours(frame, [d.box_points], contourIdx=0,
                         color=color, thickness=2, lineType=cv2.LINE_AA)

        # Centre dot
        cv2.circle(frame, d.center, radius=4, color=color, thickness=-1)

        # Dimension string
        if d.is_reference:
            label = f"REF: {d.width_mm:.1f} x {d.height_mm:.1f} mm"
        else:
            label = f"{d.label}  {d.width_mm:.1f} x {d.height_mm:.1f} mm"

        # Place label 30px above the centre so it clears the box edge
        lx, ly = d.center
        _draw_label(frame, label, anchor=(lx, ly - 30), color=color)



# HUD (heads-up display)


def draw_hud(frame: np.ndarray,
             perspective_on: bool,
             ref_found: bool,
             object_count: int) -> None:
    """
    Draw a clean status panel in the top-left corner showing:
      - Whether the ID card was found and PPM is calibrated
      - How many objects are currently being measured
      - Whether perspective correction is active
      - Keyboard shortcuts
    """
    # Semi-transparent background for the whole HUD panel
    panel_h = 145
    panel_w = 260
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (panel_w, panel_h), BLACK, -1)
    cv2.addWeighted(overlay, 0.45, frame, 0.55, 0, frame)

    font       = cv2.FONT_HERSHEY_SIMPLEX
    font_small = 0.46
    line_gap   = 22
    x, y       = 10, 20

    # Card / calibration status
    card_status = "ID Card: FOUND  (calibrated)" if ref_found \
                  else "ID Card: NOT FOUND  <-- place card"
    card_color  = GREEN if ref_found else RED
    cv2.putText(frame, card_status, (x, y), font, font_small,
                card_color, 1, cv2.LINE_AA)
    y += line_gap

    # Object count
    cv2.putText(frame, f"Objects measured: {object_count}", (x, y),
                font, font_small, WHITE, 1, cv2.LINE_AA)
    y += line_gap

    # Perspective mode
    persp_text  = f"Perspective: {'ON  (A4 mat mode)' if perspective_on else 'OFF (raw camera)'}"
    persp_color = YELLOW if perspective_on else WHITE
    cv2.putText(frame, persp_text, (x, y), font, font_small,
                persp_color, 1, cv2.LINE_AA)
    y += line_gap + 4

    # Divider line
    cv2.line(frame, (x, y), (panel_w - 10, y), WHITE, 1)
    y += 10

    # Controls
    for shortcut in ["[S] Save screenshot + log", "[P] Toggle perspective", "[Q] Quit"]:
        cv2.putText(frame, shortcut, (x, y), font, font_small,
                    WHITE, 1, cv2.LINE_AA)
        y += line_gap
