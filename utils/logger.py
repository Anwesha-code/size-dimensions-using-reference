"""
utils/logger.py — Measurement logging to CSV
============================================
Every time you press [S], all detections in the current frame are appended
to a CSV log file (one file per calendar day, so logs stay manageable).

Log location:  output/logs/measurements_YYYY-MM-DD.csv

CSV columns:
  timestamp      — when the measurement was taken
  label          — "ID Card (Reference)" or "Object N"
  width_mm       — measured width in millimetres
  height_mm      — measured height in millimetres
  is_reference   — True/False
"""

import csv
from datetime import datetime
from pathlib import Path

from config import LOGS_DIR
from measurer.detector import Detection


_CSV_FIELDS = ["timestamp", "label", "width_mm", "height_mm", "is_reference"]


def _today_log_path() -> Path:
    """One CSV file per day.  output/logs/measurements_2025-06-18.csv"""
    date_tag = datetime.now().strftime("%Y-%m-%d")
    return LOGS_DIR / f"measurements_{date_tag}.csv"


def log_measurements(detections: list[Detection]) -> Path | None:
    """
    Append all detections from one frame to today's CSV.

    - If the file doesn't exist yet, a header row is written first.
    - If detections is empty (no card found, nothing measured), we skip
      writing rather than appending a blank row.

    Returns the log path on success, None if nothing was written.
    """
    if not detections:
        print("[Logger] Nothing to log — no detections in this frame.")
        return None

    log_path     = _today_log_path()
    write_header = not log_path.exists()
    timestamp    = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(log_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_CSV_FIELDS)

        if write_header:
            writer.writeheader()

        for d in detections:
            writer.writerow({
                "timestamp"   : timestamp,
                "label"       : d.label,
                "width_mm"    : d.width_mm,
                "height_mm"   : d.height_mm,
                "is_reference": d.is_reference,
            })

    print(f"[Logger] {len(detections)} row(s) saved  -->  {log_path}")
    return log_path
