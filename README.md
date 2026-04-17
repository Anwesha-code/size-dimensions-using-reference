# Object Size Measurement 
Using your webcam to a real-time digital ruler using any ID card as a reference.


## How it works

1. Place your **ID card on the left side** of the camera's view
2. The script detects the card by its known aspect ratio (85.6 × 54 mm)
3. It computes a **Pixels-Per-Millimetre (PPM)** ratio from the card's pixel width
4. Every other shape in the frame is measured using that ratio
5. Dimensions are shown live on the video feed

---

## Setup (run one-time)

```bash
# 1. Create a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate        # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the project
python main.py
```

## Controls

| Key | Action |
|-----|--------|
| `S` | Save annotated screenshot + append measurements to CSV log |
| `P` | Toggle birds-eye perspective correction (needs A4 paper flat in frame) |
| `Q` | Quit |


## Output files

```
output/
 - screenshots/
   - measurement_20250618_143022.png  
 -  logs/
    - measurements_2025-06-18.csv       
```

The timestamp in the screenshot filename matches the rows in the CSV so you
can trace every measurement back to its source image.


## Tips for best results

- **Lighting**: Even, diffused light (no harsh shadows should be made). Natural daylight is ideal.
- **Background**: A solid-colour surface gives the clearest edges.
- **Card placement**: Put the ID card on the **left side** of the frame laying flat. 
- **Perspective mode**: Place an A4 sheet flat as a mat, put card + objects on top, press `P`.

## Project structure

```
object_measurer/
- main.py                  ← entry point & main loop
- config.py                ← all tuneable constants
- requirements.txt
- measurer/
   - detector.py          ← contour detection + PPM maths
   - perspective.py       ← birds-eye warp transform
   - visualizer.py        ← bounding boxes, labels, HUD
- utils/
    - logger.py             ← CSV measurement logging
    - saver.py              ← screenshot saving
```

## Tweaking detection

Edit **`config.py`** if the detection is too noisy or missing objects:

| Variable | Effect |
|----------|--------|
| `MIN_CONTOUR_AREA` | Increase to ignore small noise blobs |
| `CANNY_THRESH1/2` | Lower values detect more (faint) edges |
| `GAUSSIAN_BLUR` | Larger kernel = more smoothing (try `(9,9)` on a textured surface) |
| `REF_ASPECT_TOLERANCE` | Increase if card isn't being detected at a steep angle |

Project by: 

Anwesha Singh

B.Tech Computer Science Engineering

Manipal University Jaipur
