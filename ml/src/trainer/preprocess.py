"""Turning input into the array the piece classifier sees.

- load_image: piece image file → array. Used by evaluate.py and train.py.
- strokes_to_image: browser strokes → the same kind of array. The engine's
  internal/recognize/preprocess.go must produce the *exact same* image;
  make_test_cases.py writes out/preprocess_cases.json and the engine's Go test checks it.
  Stroke format: defined in engine/api/engine.yaml.
"""
from __future__ import annotations

from pathlib import Path

IMAGE_SIZE = 64


def load_image(path: str | Path, size: int = IMAGE_SIZE):
    """Image file → float32 array (1, size, size), values 0..1, white background = 1.0.

    Grayscale, scaled to fit (aspect ratio kept), centred on a white square.
    """
    import numpy as np
    from PIL import Image

    img = Image.open(path).convert("L")
    img.thumbnail((size, size), Image.Resampling.LANCZOS)
    canvas = Image.new("L", (size, size), 255)
    canvas.paste(img, ((size - img.width) // 2, (size - img.height) // 2))
    return (np.asarray(canvas, dtype=np.float32) / 255.0)[None, :, :]


def strokes_to_image(strokes, size: int = IMAGE_SIZE):
    raise NotImplementedError
