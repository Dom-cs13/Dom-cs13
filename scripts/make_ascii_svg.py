#!/usr/bin/env python3
"""
Convert a prepared portrait photo into a clean, monochrome ASCII-art SVG that
types itself in line-by-line using pure SMIL animations.
"""
from __future__ import annotations

import html
import os
import sys
from typing import List
from PIL import Image, ImageEnhance, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SRC = os.path.join(HERE, "..", "source-prepped.png")
DEFAULT_OUT = os.path.join(HERE, "..", "dom-ascii.svg")

RAMP = " .`:-=+*cs#%@"
BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
TITLE_TEXT = "#7d8590"
INK = "#c9d1d9"
CURSOR = "#c9d1d9"


def image_to_ascii_grid(
    src_path: str,
    cols: int = 180,
    rows: int = 96,
    contrast: float = 1.05,
    brightness: float = 1.0,
    gamma: float = 1.18,
    white_floor: float = 0.80,
    sharpen: bool = False,
) -> List[str]:
    im = Image.open(src_path).convert("L")
    if sharpen:
        im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=140, threshold=2))
    im = ImageEnhance.Brightness(im).enhance(brightness)
    im = ImageEnhance.Contrast(im).enhance(contrast)
    im = im.resize((cols, rows), Image.LANCZOS)
    px = im.load()

    rows_txt: List[str] = []
    ramp_len = len(RAMP)
    for y in range(rows):
        chars: List[str] = []
        for x in range(cols):
            lum = px[x, y] / 255.0
            lum = pow(lum, gamma)
            if lum >= white_floor:
                chars.append(" ")
                continue
            idx = int((1.0 - lum) * (ramp_len - 1) + 0.5)
            idx = max(0, min(ramp_len - 1, idx))
            chars.append(RAMP[idx])
        rows_txt.append("".join(chars))
    return rows_txt


def generate_ascii_svg(
    rows_txt: List[str],
    cols: int = 180,
    rows_count: int = 96,
    art_w_target: float = 800.0,
    title: str = "dom@github: ~$ ./portrait.sh",
    name: str = "Dominique Contreras",
    static: bool = False,
) -> str:
    cell_w = art_w_target / cols
    cell_h = cell_w * 15 / 8
    pad = 20
    titlebar_h = 30
    status_h = 30
    art_w = cols * cell_w
    art_h = rows_count * cell_h
    canvas_w = int(art_w + pad * 2)
    canvas_h = int(titlebar_h + art_h + status_h + pad)

    row_dur = 5.8 / max(rows_count, 1)
    stagger = row_dur
    art_top = titlebar_h + pad * 0.35

    parts: List[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
        f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, '
        f'Menlo, Consolas, monospace">',
        '<defs>',
        f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">',
        f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>',
        '</linearGradient></defs>',
        f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="url(#bg)"/>',
        f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" '
        f'fill="none" stroke="{FRAME}" stroke-width="1"/>',
        f'<line x1="0" y1="{titlebar_h}" x2="{canvas_w}" y2="{titlebar_h}" stroke="{FRAME}"/>',
    ]

    for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{pad + i*16}" cy="{titlebar_h/2}" r="5" fill="{dotcol}"/>')

    parts.append(
        f'<text x="{canvas_w/2}" y="{titlebar_h/2 + 4}" fill="{TITLE_TEXT}" font-size="12" '
        f'text-anchor="middle">{html.escape(title)}</text>'
    )

    font_size = cell_h * 0.86
    for ry, line in enumerate(rows_txt):
        y = art_top + ry * cell_h + cell_h * 0.74
        row_y = art_top + ry * cell_h
        delay = ry * stagger
        safe = html.escape(line)
        text = (
            f'<text xml:space="preserve" x="{pad}" y="{y:.1f}" fill="{INK}" '
            f'font-size="{font_size:.1f}" textLength="{art_w}" lengthAdjust="spacing">{safe}</text>'
        )

        if static:
            parts.append(text)
            continue

        parts.append(
            f'<clipPath id="r{ry}"><rect x="{pad}" y="{row_y:.1f}" height="{cell_h}" width="0">'
            f'<animate attributeName="width" from="0" to="{art_w}" begin="{delay:.3f}s" '
            f'dur="{row_dur:.2f}s" fill="freeze"/></rect></clipPath>'
        )
        parts.append(f'<g clip-path="url(#r{ry})">{text}</g>')
        parts.append(
            f'<rect y="{row_y+1:.1f}" width="{cell_w}" height="{cell_h-2}" fill="{CURSOR}" opacity="0">'
            f'<animate attributeName="x" from="{pad}" to="{pad+art_w}" begin="{delay:.3f}s" '
            f'dur="{row_dur:.2f}s" fill="freeze"/>'
            f'<set attributeName="opacity" to="0.85" begin="{delay:.3f}s"/>'
            f'<set attributeName="opacity" to="0" begin="{delay+row_dur:.3f}s"/></rect>'
        )

    status_line_y = titlebar_h + art_h + pad * 0.35
    status_y = status_line_y + 19
    parts.append(f'<line x1="0" y1="{status_line_y:.1f}" x2="{canvas_w}" y2="{status_line_y:.1f}" stroke="{FRAME}"/>')
    safe_name = html.escape(name)
    parts.append(
        f'<text x="{pad}" y="{status_y:.1f}" fill="{TITLE_TEXT}" font-size="13">'
        f'dom@github:~$ whoami <tspan fill="{INK}">{safe_name}</tspan></text>'
    )
    status_chars = len(f"dom@github:~$ whoami {name} ")
    cursor_x = pad + status_chars * 13 * 0.6
    parts.append(
        f'<rect x="{cursor_x:.1f}" y="{status_y-12:.1f}" width="8" height="14" fill="{INK}">'
        f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" '
        f'dur="1s" repeatCount="indefinite"/></rect>'
    )
    parts.append("</svg>")
    return "".join(parts)


def main() -> None:
    src = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SRC
    out = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUT

    cols = int(os.environ.get("COLS", 180))
    rows = round(cols * 8 / 15)
    static = bool(os.environ.get("STATIC"))
    user = os.environ.get("GH_PROFILE_USER", "Dom-cs13")
    name = os.environ.get("GH_PROFILE_NAME", "Dominique Contreras")

    print(f"Generating ASCII SVG from {src} to {out} ({cols}x{rows})...")
    rows_txt = image_to_ascii_grid(src, cols=cols, rows=rows)
    svg = generate_ascii_svg(
        rows_txt,
        cols=cols,
        rows_count=rows,
        title=f"{user.lower()}@github: ~$ ./portrait.sh",
        name=name,
        static=static,
    )

    with open(out, "w", encoding="utf-8") as f:
        f.write(svg)

    # If output is dom-ascii.svg, also keep avi-ascii.svg for compatibility with the plan
    alt_out = os.path.join(os.path.dirname(os.path.abspath(out)), "avi-ascii.svg")
    with open(alt_out, "w", encoding="utf-8") as f:
        f.write(svg)

    print(f"Wrote {out} and {alt_out} ({len(svg)} bytes)")


if __name__ == "__main__":
    main()
