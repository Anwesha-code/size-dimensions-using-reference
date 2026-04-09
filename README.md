# Object Size Measurement  📏
> Turn your laptop webcam into a real-time digital ruler using an ID card as reference.

---

## How it works

1. You place your **ID card on the left side** of the camera's view
2. The script detects the card by its known aspect ratio (85.6 × 54 mm)
3. It computes a **Pixels-Per-Millimetre (PPM)** ratio from the card's pixel width
4. Every other shape in the frame is measured using that ratio
5. Dimensions are overlaid live on the video feed

---

## Setup (one-time)

```bash
# 1. Create a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate        # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the project
python main.py
```

---

## Controls

| Key | Action |
|-----|--------|
| `S` | Save annotated screenshot + append measurements to CSV log |
| `P` | Toggle birds-eye perspective correction (needs A4 paper flat in frame) |
| `Q` | Quit |

---

## Output files

```
output/
├── screenshots/
│   └── measurement_20250618_143022.png   ← annotated frame
└── logs/
    └── measurements_2025-06-18.csv       ← one row per detected object
```

The timestamp in the screenshot filename matches the rows in the CSV so you
can trace every measurement back to its source image.

---

## Tips for best results

- **Lighting**: Even, diffuse light (no harsh shadows). Natural daylight is ideal.
- **Background**: A solid-colour surface — dark desk or white paper — gives the clearest edges.
- **Card placement**: Put the ID card on the **left side** of the frame, flat and unobstructed.
- **Perspective mode**: Place an A4 sheet flat as a mat, lay card + objects on top, press `P`.
- **Camera distance**: About 30–50 cm overhead is ideal for objects roughly palm-sized.

---

## Project structure

```
object_measurer/
├── main.py                  ← entry point & main loop
├── config.py                ← all tuneable constants
├── requirements.txt
├── measurer/
│   ├── detector.py          ← contour detection + PPM maths
│   ├── perspective.py       ← birds-eye warp transform
│   └── visualizer.py        ← bounding boxes, labels, HUD
└── utils/
    ├── logger.py             ← CSV measurement logging
    └── saver.py              ← screenshot saving
```

---

## Tweaking detection

Edit **`config.py`** if the detection is too noisy or missing objects:

| Variable | Effect |
|----------|--------|
| `MIN_CONTOUR_AREA` | Increase to ignore small noise blobs |
| `CANNY_THRESH1/2` | Lower values detect more (faint) edges |
| `GAUSSIAN_BLUR` | Larger kernel = more smoothing (try `(9,9)` on a textured surface) |
| `REF_ASPECT_TOLERANCE` | Increase if card isn't being detected at a steep angle |
