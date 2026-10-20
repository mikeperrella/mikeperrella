#!/usr/bin/env python3
"""Generate an animated GitHub-streak SVG (squares light up one by one).
Works standalone; designed to run in a GitHub Action daily to stay live.
Usage: python generate_streak_svg.py [username] [output.svg]
"""
import sys
import json
import datetime
from pathlib import Path
import xml.etree.ElementTree as ET

USER = sys.argv[1] if len(sys.argv) > 1 else "mikeperrella"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).resolve().parent.parent / "contrib-heatmap.svg"
SNAPSHOT = Path(__file__).resolve().parent.parent / "data" / "contributions.json"


def get_data(user):
    # Fail closed rather than silently displaying another user's/stale fixture data.
    if not SNAPSHOT.is_file():
        raise FileNotFoundError(f"Missing {SNAPSHOT}. Run fetch_contributions.py first.")
    with SNAPSHOT.open(encoding="utf-8") as fh:
        snap = json.load(fh)
    if snap.get("username", "").lower() != user.lower():
        raise ValueError("Snapshot username does not match the requested account")
    days = snap.get("days", [])
    if not days:
        raise ValueError("Contribution snapshot has no days")
    dates = [datetime.date.fromisoformat(item["date"]) for item in days]
    if len(dates) != len(set(dates)) or dates != sorted(dates):
        raise ValueError("Snapshot dates are duplicated or out of order")
    if any((b-a).days != 1 for a,b in zip(dates, dates[1:])):
        raise ValueError("Snapshot is missing dates")
    if any(not isinstance(d.get("count"), int) or d["count"] < 0
           or not isinstance(d.get("level"), int) or d["level"] not in range(5)
           for d in days):
        raise ValueError("Snapshot contains invalid contribution counts or levels")
    real_total = sum(day["count"] for day in days)
    if real_total != snap.get("total_contributions"):
        raise ValueError("Snapshot daily total disagrees with reported total")
    return {"contributions": days, "total": {"lastYear": real_total}}


data = get_data(USER)
contribs = data["contributions"]
total = data["total"]["lastYear"]

# ---- layout ----
CELL, GAP, RAD, LEFT, TOP = 13, 3, 2.5, 34, 24
COLORS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
FLASH = "#b4ffaa"
GRAY = "#7d8590"
MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

n = len(contribs)
NW = (n + 6) // 7
W = LEFT + NW*(CELL+GAP) + 6
H = TOP + 7*(CELL+GAP) + 22

# timing (seconds)
REVEAL, DUR = 3.6, 0.55
maxorder = (NW-1) + 6*0.55

rects, labels = [], []
sd = datetime.date.fromisoformat(contribs[0]["date"])
last_m = None
for wk in range(NW):
    d = sd + datetime.timedelta(days=wk*7)
    if d.month != last_m:
        last_m = d.month
        labels.append(f'<text class="lbl" x="{LEFT+wk*(CELL+GAP)}" y="{TOP-8}">{MONTHS[d.month-1]}</text>')
for name, r in [("Mon",1),("Wed",3),("Fri",5)]:
    labels.append(f'<text class="lbl" x="2" y="{TOP+r*(CELL+GAP)+CELL-2}">{name}</text>')

for i, c in enumerate(contribs):
    wk, row, lvl = i//7, i%7, c["level"]
    x = LEFT + wk*(CELL+GAP); y = TOP + row*(CELL+GAP)
    delay = round((wk + row*0.55)/maxorder * REVEAL, 3)
    cls = "c g" if lvl >= 1 else "c e"
    rects.append(
        f'<rect class="{cls}" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="{RAD}" '
        f'fill="{COLORS[lvl]}" style="animation-delay:{delay}s"/>'
    )

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif">
<style>
  text.lbl {{ fill:{GRAY}; font-size:13px; font-weight:600; }}
  text.total {{ fill:#e6edf3; font-size:15px; font-weight:700; }}
  .c {{ transform-box:fill-box; transform-origin:center; opacity:0; animation:pop {DUR}s ease-out both; }}
  .g {{ animation:pop {DUR}s ease-out both, flash {DUR+0.15}s ease-out both; }}
  @keyframes pop {{ 0%{{opacity:0;transform:scale(.2)}} 60%{{opacity:1;transform:scale(1.1)}} 100%{{opacity:1;transform:scale(1)}} }}
  @keyframes flash {{ 0%{{filter:brightness(2.4)}} 45%{{filter:brightness(2.4)}} 100%{{filter:brightness(1)}} }}
  @media (prefers-reduced-motion: reduce) {{ .c {{ opacity:1 !important; animation:none !important; }} }}
</style>
<rect width="{W}" height="{H}" fill="none"/>
{''.join(labels)}
{''.join(rects)}
<text class="total" x="{LEFT}" y="{H-6}">{total:,} contributions in the last year</text>
</svg>'''

OUT.write_text(svg, encoding="utf-8")
ET.fromstring(svg)
print(f"Wrote {OUT}: {n} days, {total:,} contributions, {len(svg)//1024} KB")
