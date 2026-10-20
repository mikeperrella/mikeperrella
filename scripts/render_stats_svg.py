#!/usr/bin/env python3
"""
Render a self-contained terminal dashboard SVG for the GitHub profile README.

The canvas matches the portrait panel (840 x 880) so the two sit side by side
at equal widths. Type is sized for that half-width display (~410 px).

    python scripts/render_stats_svg.py [output.svg]
"""
from __future__ import annotations

import os
import sys
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape as xml_escape

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "stats.svg")

BG = "#0D1117"
BG2 = "#161B22"
FOREST = "#16372C"
GREEN = "#39D353"
INK = "#E6EDF3"
MUTED = "#8B949E"
FRAME = "#30363D"

W, H = 840, 880
PAD = 32
TITLEBAR_H = 32

# motion (seconds) — one-shot; final keyframe holds
HEADER_DELAY = 0.05
SLIDE_DUR = 0.55
SECTION_START = 0.38
SECTION_STAGGER = 0.14
FOOTER_LEAD = 0.18

NAME = "Mike Perrella"
FOCUS = "Cybersecurity / GRC / AI Security"
PROMPT = "mike@github:~$ ./system-info.sh"
FOOTER = "SECURITY × AI × AUTOMATION"

SECTIONS = [
    ("CREDENTIALS", "B.S. CIS (Cybersecurity) · Security+"),
    ("GRC & COMPLIANCE", "SOC 2 · NIST CSF 2.0 · ISO 27001"),
    ("SECURITY ENGINEERING", "IAM · Detection · STRIDE"),
    ("AI & AUTOMATION", "Python · LangGraph · Local LLMs"),
    ("FEATURED PROJECTS", "ALIBI · VIGCAP · Aegis · ARGUS"),
    ("BACKGROUND", "BizAI · IFF · Covington & Burling"),
]


def main() -> None:
    prompt_y = TITLEBAR_H + 44
    name_y = prompt_y + 44
    focus_y = name_y + 38
    rule_y = focus_y + 26

    footer_y = H - 38
    sections_top = rule_y + 24
    sections_bottom = footer_y - 32
    gap = 12
    n = len(SECTIONS)
    tile_h = (sections_bottom - sections_top - gap * (n - 1)) / n
    tile_w = W - PAD * 2
    footer_delay = SECTION_START + SECTION_STAGGER * n + FOOTER_LEAD
    prompt_host, prompt_rest = PROMPT.split(":", 1)

    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="{xml_escape(NAME)} — {xml_escape(FOCUS)}" '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        "<style>"
        f".panel{{opacity:0;animation:rise {SLIDE_DUR}s ease-out both}}"
        "@keyframes rise{"
        "0%{opacity:0;transform:translateY(12px)}"
        "100%{opacity:1;transform:translateY(0)}"
        "}"
        "@media (prefers-reduced-motion: reduce){"
        ".panel{opacity:1!important;transform:none!important;animation:none!important}"
        "}"
        "</style>",
        f'<rect width="{W}" height="{H}" rx="12" fill="{BG}"/>',
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" '
        f'fill="none" stroke="{FRAME}"/>',
        f'<rect width="{W}" height="{TITLEBAR_H}" rx="12" fill="{BG2}"/>',
        f'<rect y="{TITLEBAR_H - 12}" width="{W}" height="12" fill="{BG2}"/>',
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
    ]

    for i, dot in enumerate(("#FF5F56", "#FFBD2E", "#27C93F")):
        parts.append(
            f'<circle cx="{PAD + i * 16}" cy="{TITLEBAR_H / 2}" r="5" fill="{dot}"/>'
        )

    parts.append(
        f'<text x="{W / 2}" y="{TITLEBAR_H / 2 + 5}" fill="{MUTED}" font-size="13" '
        f'text-anchor="middle">system-info.sh</text>'
    )

    # ---- identity header -------------------------------------------------
    parts.append(f'<g class="panel" style="animation-delay:{HEADER_DELAY:.2f}s">')
    parts.append(
        f'<text x="{PAD + 4}" y="{prompt_y}" fill="{MUTED}" font-size="20">'
        f'<tspan fill="{GREEN}">{xml_escape(prompt_host)}</tspan>'
        f'<tspan fill="{MUTED}">{xml_escape(":" + prompt_rest)}</tspan></text>'
    )
    parts.append(
        f'<text x="{PAD + 4}" y="{name_y}" fill="{INK}" font-size="40" '
        f'font-weight="700">{xml_escape(NAME)}</text>'
    )
    parts.append(
        f'<text x="{PAD + 4}" y="{focus_y}" fill="{GREEN}" font-size="22">'
        f"{xml_escape(FOCUS)}</text>"
    )
    parts.append(
        f'<line x1="{PAD}" y1="{rule_y}" x2="{W - PAD}" y2="{rule_y}" '
        f'stroke="{FRAME}"/>'
    )
    parts.append("</g>")

    # ---- information rows ------------------------------------------------
    rail_w = 6
    for i, (label, value) in enumerate(SECTIONS):
        x = PAD
        y = sections_top + i * (tile_h + gap)
        delay = SECTION_START + i * SECTION_STAGGER
        label_y = y + tile_h * 0.38
        value_y = y + tile_h * 0.72

        parts.append(f'<g class="panel" style="animation-delay:{delay:.2f}s">')
        parts.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{tile_w:.1f}" height="{tile_h:.1f}" '
            f'rx="8" fill="{BG2}" stroke="{FRAME}"/>'
        )
        parts.append(
            f'<rect x="{x:.1f}" y="{y + 10:.1f}" width="{rail_w}" '
            f'height="{tile_h - 20:.1f}" rx="2" fill="{FOREST}"/>'
        )
        parts.append(
            f'<text x="{x + 28:.1f}" y="{label_y:.1f}" fill="{MUTED}" font-size="20" '
            f'letter-spacing="1.6">{xml_escape(label)}</text>'
        )
        parts.append(
            f'<text x="{x + 28:.1f}" y="{value_y:.1f}" fill="{INK}" font-size="24">'
            f"{xml_escape(value)}</text>"
        )
        parts.append("</g>")

    # ---- footer ----------------------------------------------------------
    parts.append(f'<g class="panel" style="animation-delay:{footer_delay:.2f}s">')
    parts.append(
        f'<text x="{W / 2}" y="{footer_y}" fill="{MUTED}" font-size="16" '
        f'text-anchor="middle" letter-spacing="2">{xml_escape(FOOTER)}</text>'
    )
    parts.append("</g>")
    parts.append("</svg>")

    svg = "".join(parts)
    out_path = os.path.abspath(OUT)
    with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(svg)

    ET.parse(out_path)
    print(f"wrote {out_path}: {W} x {H}, {len(svg) // 1024} KB")


if __name__ == "__main__":
    main()
