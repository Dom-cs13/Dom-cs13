#!/usr/bin/env python3
"""
Generate a neofetch-style terminal info card as an SVG featuring Arch Linux ASCII art.
Features staggered line fade/slide animations, color key-values, and terminal palette.
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
ARCH_BLUE = "#1793d1"
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
        ("user", info.get("user", "dom@arch"), GREEN),
        ("host", info.get("host", "Dominique Contreras"), TEXT),
        ("os", info.get("os", "Arch Linux x86_64"), ARCH_BLUE),
        ("kernel", info.get("kernel", "Linux Zen"), MUTED),
        ("role", info.get("role", "Systems, Backend & Game Dev"), YELLOW),
        ("stack", info.get("stack", ".NET · C# · Kotlin · C/C++ · Python"), CYAN),
        ("backend", info.get("backend", "YARP · Microservices · PostgreSQL"), PURPLE),
        ("gamedev", info.get("gamedev", "Unity · Godot (C#, GDScript)"), GREEN),
        ("mobile", info.get("mobile", "Android Offline-First (Room, MVVM)"), BLUE),
        ("low-level", info.get("low-level", "DSLs · Compilers · Embedded (PIC/ESP32)"), RED),
        ("shell", info.get("shell", "zsh / bash on Linux"), MUTED),
    ]

    arch_logo = [
        r"              /\              ",
        r"             /  \             ",
        r"            /\   \            ",
        r"           /      \           ",
        r"          /   /\   \          ",
        r"         /   /  \   \         ",
        r"        /   / /\ \   \        ",
        r"       /   / /  \ \   \       ",
        r"      /___/ /    \ \___\      ",
        r"      \____/      \____/      ",
    ]

    slide_dur = 0.45
    stagger = 0.10

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
        f'text-anchor="middle">dom@arch: ~$ neofetch</text>'
    )

    content_top = TITLEBAR_H + 34

    delay = 0.05
    static_attr = "" if not static else ' style="opacity: 1;"'
    dyn_attr = f' class="f" style="animation-delay: {delay:.2f}s"' if not static else static_attr
    parts.append(f'<g{dyn_attr}>')
    parts.append(
        f'<text x="{PAD}" y="{content_top}" font-size="15" fill="{GREEN}">'
        f'dom@arch<tspan fill="{MUTED}">:~$</tspan> <tspan fill="{TEXT}">neofetch --stdout</tspan></text>'
    )
    parts.append('</g>')

    banner_y = content_top + 24
    parts.append(
        f'<line x1="{PAD}" y1="{banner_y}" x2="{W-PAD}" y2="{banner_y}" stroke="{FRAME}" stroke-dasharray="4,4"/>'
    )

    # Left column: Arch Linux ASCII Logo
    logo_top = banner_y + 44
    logo_x = PAD + 10
    logo_line_h = 24
    for idx, line in enumerate(arch_logo):
        delay = 0.12 + idx * 0.03
        dyn_attr = f' class="f" style="animation-delay: {delay:.2f}s"' if not static else static_attr
        parts.append(f'<g{dyn_attr}>')
        safe_l = html.escape(line)
        parts.append(
            f'<text x="{logo_x}" y="{logo_top + idx * logo_line_h}" fill="{ARCH_BLUE}" font-size="14" '
            f'font-weight="bold" xml:space="preserve">{safe_l}</text>'
        )
        parts.append('</g>')

    # Right column: Specs
    specs_x = PAD + 270
    specs_top = banner_y + 36
    specs_step = 34

    for idx, (key, val, color) in enumerate(lines):
        delay = 0.15 + idx * stagger
        dyn_attr = f' class="f" style="animation-delay: {delay:.2f}s"' if not static else static_attr
        y = specs_top + idx * specs_step
        parts.append(f'<g{dyn_attr}>')
        parts.append(
            f'<text x="{specs_x}" y="{y}" font-size="14" fill="{MUTED}" font-weight="600">'
            f'{key.ljust(10)} <tspan fill="{FRAME}">│</tspan> '
            f'<tspan fill="{color}" font-weight="500">{html.escape(val)}</tspan></text>'
        )
        parts.append('</g>')

    palette_top = specs_top + len(lines) * specs_step + 36
    parts.append(
        f'<line x1="{PAD}" y1="{palette_top - 16}" x2="{W-PAD}" y2="{palette_top - 16}" stroke="{FRAME}"/>'
    )

    block_w = 40
    block_h = 22
    block_gap = 10
    start_x = (W - (len(PALETTE_COLORS) * (block_w + block_gap))) / 2

    pal_delay = 0.15 + len(lines) * stagger + 0.08
    dyn_attr = f' class="f" style="animation-delay: {pal_delay:.2f}s"' if not static else static_attr
    parts.append(f'<g{dyn_attr}>')
    for i, col in enumerate(PALETTE_COLORS):
        bx = start_x + i * (block_w + block_gap)
        parts.append(f'<rect x="{bx}" y="{palette_top}" width="{block_w}" height="{block_h}" rx="4" fill="{col}"/>')
    parts.append('</g>')

    pal_bright_delay = pal_delay + 0.08
    dyn_attr = f' class="f" style="animation-delay: {pal_bright_delay:.2f}s"' if not static else static_attr
    parts.append(f'<g{dyn_attr}>')
    for i, col in enumerate(PALETTE_BRIGHT):
        bx = start_x + i * (block_w + block_gap)
        parts.append(f'<rect x="{bx}" y="{palette_top + block_h + 6}" width="{block_w}" height="{block_h}" rx="4" fill="{col}"/>')
    parts.append('</g>')

    quote_y = palette_top + block_h * 2 + 50
    dyn_attr = f' class="f" style="animation-delay: {pal_bright_delay + 0.08:.2f}s"' if not static else static_attr
    parts.append(f'<g{dyn_attr}>')
    parts.append(
        f'<text x="{W/2}" y="{quote_y}" fill="{MUTED}" font-size="13" font-style="italic" text-anchor="middle">'
        f'"Engineered for performance. Built on Linux."'
        f'</text>'
    )
    parts.append('</g>')

    parts.append('</svg>')
    return "".join(parts)


def main() -> None:
    out = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUT
    static = bool(os.environ.get("STATIC"))

    info = {
        "user": "dom@arch",
        "host": "Dominique Contreras",
        "os": "Arch Linux x86_64",
        "kernel": "Linux Zen",
        "role": "Systems, Backend & Game Dev",
        "stack": ".NET · C# · Kotlin · C/C++ · Python",
        "backend": "YARP · Microservices · PostgreSQL",
        "gamedev": "Unity · Godot (C#, GDScript)",
        "mobile": "Android Offline-First (Room, MVVM)",
        "low-level": "DSLs · Compilers · Embedded (PIC/ESP32)",
        "shell": "zsh / bash on Linux",
    }

    svg = generate_info_card_svg(info, static=static)
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Wrote {out} ({len(svg)} bytes; {W}x{H})")


if __name__ == "__main__":
    main()
