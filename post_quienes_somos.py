#!/usr/bin/env python3
"""
Post IG 1080x1350 con el top del flyer (header + iconos) + frase de cierre.
"""
import subprocess, base64
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "output"
POSTS = ROOT / "posts"
TOP = Path("/tmp/top_section.jpg")

W, H = 1080, 1350

VERDE_ENERGIA  = "#68D38E"
VERDE_GENSTONE = "#173B2E"
GRIS_MINERAL   = "#282B2A"
BLANCO         = "#EFEFEF"

HAAS = "Neue Haas Grotesk Display Pro"

b64 = base64.b64encode(TOP.read_bytes()).decode()
top_uri = f"data:image/jpeg;base64,{b64}"

svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="#FFFFFF"/>
  <image href="{top_uri}" x="0" y="0" width="{W}" height="1140"/>

  <!-- Frase de cierre -->
  <text x="{W/2}" y="1230" font-family="{HAAS}" font-weight="500"
        font-size="40" fill="{VERDE_GENSTONE}" stroke="{VERDE_GENSTONE}" stroke-width="2"
        text-anchor="middle" letter-spacing="-0.025em">Lo que necesitás,</text>
  <text x="{W/2}" y="1278" font-family="{HAAS}" font-weight="500"
        font-size="40" fill="{VERDE_ENERGIA}" stroke="{VERDE_ENERGIA}" stroke-width="2"
        text-anchor="middle" letter-spacing="-0.025em">sigue en marcha.</text>
</svg>
'''
(POSTS / "post_quienes_somos.svg").write_text(svg)

png = OUT / "post_quienes_somos.png"
jpg = OUT / "post_quienes_somos.jpg"
subprocess.run(["rsvg-convert", "-w", str(W), "-h", str(H),
                "-o", str(png), str(POSTS / "post_quienes_somos.svg")], check=True)
subprocess.run(["convert", str(png), "-colorspace", "sRGB", "-quality", "96",
                "-sampling-factor", "1x1", "-strip", str(jpg)], check=True)
png.unlink()
print(f"OK  {jpg.name}")
