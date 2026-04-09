
from pathlib import Path


# Reference Object: Standard ID / Credit Card (ISO/IEC 7810 ID-1 spec)

REF_WIDTH_MM  = 85.60   # card width  in millimetres — do not change
REF_HEIGHT_MM = 53.98   # card height in millimetres — do not change
REF_ASPECT_RATIO = REF_WIDTH_MM / REF_HEIGHT_MM   # ≈ 1.585

# How forgiving are we when matching the card's aspect ratio?
# 0.15 means ±15 % — handles mild perspective tilt gracefully.
REF_ASPECT_TOLERANCE = 0.08


# Camera

CAMERA_INDEX  = 1      # 0 = built-in webcam; try 1 if you have an external cam
FRAME_WIDTH   = 1280
FRAME_HEIGHT  = 720

# Output paths  (auto-created on first import)

BASE_DIR        = Path(__file__).parent
OUTPUT_DIR      = BASE_DIR / "output"
SCREENSHOTS_DIR = OUTPUT_DIR / "screenshots"
LOGS_DIR        = OUTPUT_DIR / "logs"

for _dir in (SCREENSHOTS_DIR, LOGS_DIR):
    _dir.mkdir(parents=True, exist_ok=True)

# Contour detection tuning

#MIN_CONTOUR_AREA = 1500
MIN_CONTOUR_AREA = 1000
# px² — smaller blobs (dust, noise) are ignored
GAUSSIAN_BLUR    = (7, 7)  # kernel size for smoothing; increase if noisy background
#CANNY_THRESH1    = 40      # lower = detects more edges (including faint ones)
#CANNY_THRESH2    = 120     # upper = only strong, confident edges
CANNY_THRESH1    = 20      # (Dropped from 40)
CANNY_THRESH2    = 80      # (Dropped from 120)


# Perspective correction (birds-eye warp output size, at ~96 dpi A4 portrait)

WARP_WIDTH  = 794
WARP_HEIGHT = 1123
