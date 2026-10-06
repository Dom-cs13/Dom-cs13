#!/usr/bin/env python3
"""
Prepare the portrait photo for clean ASCII conversion:
  1. remove the background (rembg) so the subject is isolated
  2. bilateral-smooth away paper/skin noise while keeping drawn edges sharp
  3. stretch tones so skin/background lands near white and hair/lines stay dark
  4. darken line work with difference-of-gaussians
  5. composite onto white and crop square around the subject

Output: source-prepped.png (grayscale), consumed by make_ascii_svg.py.
"""
from __future__ import annotations

import os
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import remove

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_INP = os.path.join(HERE, "..", "source-photo.png")
DEFAULT_OUT = os.path.join(HERE, "..", "source-prepped.png")

LINE_WEIGHT = 0.6


def prep_image(input_path: str, output_path: str) -> None:
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # 1. cut out the subject
    print(f"Removing background from {input_path}...")
    img = Image.open(input_path).convert("RGBA")
    cut = remove(img)
    rgb = np.array(cut.convert("RGB"))
    alpha = np.array(cut.split()[-1])
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

    # 2. smooth texture, keep edges
    smooth = gray
    for _ in range(3):
        smooth = cv2.bilateralFilter(smooth, 9, 40, 9)

    # 3. tone stretch over the subject only
    fg_mask = alpha > 128
    if np.any(fg_mask):
        lo, hi = np.percentile(smooth[fg_mask], [2, 92])
        if hi > lo:
            tone = np.clip((smooth.astype(np.float32) - lo) / (hi - lo), 0, 1)
        else:
            tone = smooth.astype(np.float32) / 255.0
    else:
        tone = smooth.astype(np.float32) / 255.0

    # 4. dark-on-light ridges -> darken lines
    fine = cv2.GaussianBlur(smooth, (0, 0), 1.5).astype(np.float32)
    coarse = cv2.GaussianBlur(smooth, (0, 0), 6.0).astype(np.float32)
    lines = np.clip((coarse - fine) / 40.0, 0, 1)
    out = np.clip(tone - LINE_WEIGHT * lines, 0, 1) * 255.0

    # 5. paste onto white
    mask = cv2.GaussianBlur(alpha.astype(np.float32) / 255.0, (0, 0), 1.0)
    out = out * mask + 255.0 * (1.0 - mask)

    ys, xs = np.where(alpha > 20)
    if len(xs) > 0 and len(ys) > 0:
        side = max(xs.max() - xs.min(), ys.max() - ys.min()) + 60
        cx, cy = (xs.min() + xs.max()) // 2, (ys.min() + ys.max()) // 2
        canvas = np.full((side, side), 255, np.uint8)
        x0, y0 = cx - side // 2, cy - side // 2
        sx0, sy0 = max(x0, 0), max(y0, 0)
        sx1, sy1 = min(x0 + side, out.shape[1]), min(y0 + side, out.shape[0])
        canvas[sy0 - y0 : sy1 - y0, sx0 - x0 : sx1 - x0] = out[sy0:sy1, sx0:sx1].astype(np.uint8)
    else:
        canvas = out.astype(np.uint8)

    Image.fromarray(canvas, mode="L").save(output_path)
    print(f"Wrote {output_path} ({canvas.shape[1]}x{canvas.shape[0]})")


if __name__ == "__main__":
    inp = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_INP
    out = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUT
    prep_image(inp, out)
