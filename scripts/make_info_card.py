#!/usr/bin/env python3
"""
Generate a neofetch-style terminal info card as an SVG.
Features staggered line fade/slide animations, color key-values, and terminal blocks.
"""
from __future__ import annotations

import html
import os
import sys
from typing import Dict, List, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUT = os.path.join(HERE, "..", "info-card.svg")

W, H = 840, 880
PAD = 24
TITLEBAR_H = 30
BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
MUTED = "#7d8590"
TEXT = "#e6edf3"
CYAN = "#38bdf8"
GREEN = "#34d399"
YELLOW = "#fbbf24"
PURPLE = "#c084fc"
RED = "#f87171"
BLUE = "#60a5fa"

PALETTE_COLORS = [
    "#1f2937", "#ef4444", "#10b981", "#f59e0b",
    "#3b82f6", "#8b5cf6", "#06b6d4", "#f3f4f6"
]

PALETTE_BRIGHT = [
    "#4b5563", "#f87171", "#34d399", "#fbbf24",
    "#60a5fa", "#a78bfa", "#22d3ee", "#ffffff"
]


def generate_info_card_svg(info: Dict[str, str], static: bool = False) -> str:
    lines: List[Tuple[str, str, str]] = [
        ("user", info.get("user", "dom@github"), GREEN),
        ("name", info.get("name", "Dominique Contreras"), TEXT),
        ("role", info.get("role", "Developer & Game Creator"), YELLOW),
        ("stack", info.get("stack") or info.get("focus", "Python · JavaScript · HTML"), CYAN),
        ("engines", info.get("engines", "Unity · Unreal Engine"), PURPLE),
        ("status", info.get("status", "Building games & web systems"), TEXT),
        ("repos", info.get("repos", "18 Public Repositories"), BLUE),
        ("github", info.get("github", "github.com/Dom-cs13"), GREEN),
        ("interests", info.get("interests", "Game Dev · Clean Architecture · SOLID"), YELLOW),
        ("terminal", info.get("terminal", "zsh / bash on Linux"), MUTED),
    ]

    ascii_logo = [
        r"      ___           ___     ",
        r"     /\  \         /\  \    ",
        r"    /::\  \       /::\  \   ",
        r"   /:/\:\  \     /:/\:\  \  ",
        r"  /:/  \:\__\   /:/  \:\__\ ",
        r" /:/__/ \:|__| /:/__/ \:|__|",
        r" \:\  \ /:/  / \:\  \ /:/  /",
        r"  \:\  /:/  /   \:\  /:/  / ",
        r"   \:\/:/  /     \:\/:/  /  ",
        r"    \::/__/       \::/__/   ",
        r"     ~~            ~~       ",
    ]

    slide_dur = 0.45
    stagger = 0.12

    css = f"""
    .f {{ opacity: 0; animation: fadeSlide {slide_dur}s cubic-bezier(0.16, 1, 0.3, 1) both; }}
    @keyframes fadeSlide {{
      0% {{ opacity: 0; transform: translateY(12px); }}
      100% {{ opacity: 1; transform: translateY(0); }}
    }}
    @media (prefers-reduced-motion: reduce) {{
      .f {{ opacity: 1 !important; transform: none !important; animation: none !important; }}
    }}
    """.strip()

    parts: List[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        f'<style>{css}</style>',
        '<defs>',
        f'<linearGradient id="ibg" x1="0" y1="0" x2="0" y2="1">',
        f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>',
        '</linearGradient></defs>',
        f'<rect width="{W}" height="{H}" rx="12" fill="url(#ibg)"/>',
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{FRAME}" stroke-width="1"/>',
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
    ]

    for i, dot in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dot}"/>')

    parts.append(
        f'<text x="{W/2}" y="{TITLEBAR_H/2 + 4}" fill="{MUTED}" font-size="12" '
        f'text-anchor="middle">dom@github: ~$ neofetch</text>'
    )

    # Content section
    content_top = TITLEBAR_H + 36

    # Terminal prompt header
    delay = 0.05
    static_attr = "" if not static else ' style="opacity: 1;"'
    dyn_attr = f' class="f" style="animation-delay: {delay:.2f}s"' if not static else static_attr
    parts.append(f'<g{dyn_attr}>')
    parts.append(
        f'<text x="{PAD}" y="{content_top}" font-size="15" fill="{GREEN}">'
        f'dom@github<tspan fill="{MUTED}">:~$</tspan> <tspan fill="{TEXT}">neofetch --stdout</tspan></text>'
    )
    parts.append('</g>')

    # Separator banner line
    banner_y = content_top + 26
    parts.append(
        f'<line x1="{PAD}" y1="{banner_y}" x2="{W-PAD}" y2="{banner_y}" stroke="{FRAME}" stroke-dasharray="4,4"/>'
    )

    # Left column: ASCII Logo
    logo_top = banner_y + 36
    logo_x = PAD + 10
    logo_line_h = 24
    for idx, line in enumerate(ascii_logo):
        delay = 0.15 + idx * 0.04
        dyn_attr = f' class="f" style="animation-delay: {delay:.2f}s"' if not static else static_attr
        parts.append(f'<g{dyn_attr}>')
        safe_l = html.escape(line)
        parts.append(
            f'<text x="{logo_x}" y="{logo_top + idx * logo_line_h}" fill="{CYAN}" font-size="14" '
            f'font-weight="bold" xml:space="preserve">{safe_l}</text>'
        )
        parts.append('</g>')

    # Right column: Key / Value specs
    specs_x = PAD + 250
    specs_top = banner_y + 40
    specs_step = 36

    for idx, (key, val, color) in enumerate(lines):
        delay = 0.25 + idx * stagger
        dyn_attr = f' class="f" style="animation-delay: {delay:.2f}s"' if not static else static_attr
        y = specs_top + idx * specs_step
        parts.append(f'<g{dyn_attr}>')
        # Key in Cyan/Yellow, Value in styled color
        parts.append(
            f'<text x="{specs_x}" y="{y}" font-size="15" fill="{MUTED}" font-weight="600">'
            f'{key.ljust(10)} <tspan fill="{FRAME}">│</tspan> '
            f'<tspan fill="{color}" font-weight="500">{html.escape(val)}</tspan></text>'
        )
        parts.append('</g>')

    # Bottom Terminal Color Palette Blocks (Neofetch signature)
    palette_top = specs_top + len(lines) * specs_step + 40
    parts.append(
        f'<line x1="{PAD}" y1="{palette_top - 18}" x2="{W-PAD}" y2="{palette_top - 18}" stroke="{FRAME}"/>'
    )

    block_w = 40
    block_h = 22
    block_gap = 10
    start_x = (W - (len(PALETTE_COLORS) * (block_w + block_gap))) / 2

    # Normal Palette Row
    pal_delay = 0.25 + len(lines) * stagger + 0.1
    dyn_attr = f' class="f" style="animation-delay: {pal_delay:.2f}s"' if not static else static_attr
    parts.append(f'<g{dyn_attr}>')
    for i, col in enumerate(PALETTE_COLORS):
        bx = start_x + i * (block_w + block_gap)
        parts.append(f'<rect x="{bx}" y="{palette_top}" width="{block_w}" height="{block_h}" rx="4" fill="{col}"/>')
    parts.append('</g>')

    # Bright Palette Row
    pal_bright_delay = pal_delay + 0.1
    dyn_attr = f' class="f" style="animation-delay: {pal_bright_delay:.2f}s"' if not static else static_attr
    parts.append(f'<g{dyn_attr}>')
    for i, col in enumerate(PALETTE_BRIGHT):
        bx = start_x + i * (block_w + block_gap)
        parts.append(f'<rect x="{bx}" y="{palette_top + block_h + 6}" width="{block_w}" height="{block_h}" rx="4" fill="{col}"/>')
    parts.append('</g>')

    # Bottom status quote
    quote_y = palette_top + block_h * 2 + 54
    dyn_attr = f' class="f" style="animation-delay: {pal_bright_delay + 0.1:.2f}s"' if not static else static_attr
    parts.append(f'<g{dyn_attr}>')
    parts.append(
        f'<text x="{W/2}" y="{quote_y}" fill="{MUTED}" font-size="13" font-style="italic" text-anchor="middle">'
        f'"Code with passion. Build worlds with imagination."'
        f'</text>'
    )
    parts.append('</g>')

    parts.append('</svg>')
    return "".join(parts)


def main() -> None:
    out = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUT
    static = bool(os.environ.get("STATIC"))

    info = {
        "user": "dom@github",
        "name": "Dominique Contreras",
        "role": "Developer & Game Creator",
        "focus": "Python · JavaScript · HTML",
        "engines": "Unity · Unreal Engine",
        "status": "Building games & web systems",
        "repos": "18 Public Repositories",
        "github": "github.com/Dom-cs13",
        "interests": "Game Dev · Clean Code · SOLID",
        "terminal": "zsh / bash on Linux",
    }

    svg = generate_info_card_svg(info, static=static)
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Wrote {out} ({len(svg)} bytes; {W}x{H})")


if __name__ == "__main__":
    main()
