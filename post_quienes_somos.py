#!/usr/bin/env python3
"""
Post IG 1080x1350 — solo seccion "Sobre Genstone" + iconos del flyer.
Toma directamente del PDF modificado del user.
"""
import subprocess, base64, shutil
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "output"
POSTS = ROOT / "posts"

W, H = 1080, 1350

VERDE_ENERGIA  = "#68D38E"
VERDE_GENSTONE = "#173B2E"

PDF = Path("/root/.claude/uploads/c4d66611-250f-4c93-ad14-7d7799d6d1ff/db5074a1-flyer_lista_precios.pdf")

# Render PDF a 1080 wide (72 dpi)
flyer_jpg = Path("/tmp/flyer_1x-1.jpg")
if not flyer_jpg.exists():
    subprocess.run([
        "pdftoppm", "-r", "72", "-jpeg", "-jpegopt", "quality=98",
        str(PDF), "/tmp/flyer_1x"
    ], check=True)

# Crop: y=380 a y=1135 (justo despues del divider) = 755 tall
SRC_Y, SRC_H = 380, 755
section = "/tmp/section.png"
subprocess.run([
    "convert", str(flyer_jpg),
    "-crop", f"{W}x{SRC_H}+0+{SRC_Y}", "+repage",
    section
], check=True)

# Sample bg color del crop para canvas
bg_raw = subprocess.check_output([
    "convert", section, "-format", "%[pixel:p{5,5}]", "info:"
]).decode().strip()
# 'srgb(250,250,248)' -> '#FAFAF8'
nums = bg_raw[bg_raw.index("(")+1:bg_raw.index(")")].split(",")
r, g, b = [int(float(n)) for n in nums[:3]]
bg = f"#{r:02X}{g:02X}{b:02X}"
print(f"bg: {bg}")

# Compose: centrado en 1080x1350 con el bg color exacto + corner brackets
top_pad = (H - SRC_H) // 2

b64 = base64.b64encode(Path(section).read_bytes()).decode()
section_uri = f"data:image/png;base64,{b64}"

# Corner brackets en las 4 esquinas (verde energia, sutil)
INSET = 50
SIZE = 32
BR = 2
corners = f'''
<g stroke="{VERDE_ENERGIA}" stroke-width="{BR}" fill="none">
  <polyline points="{INSET},{INSET+SIZE} {INSET},{INSET} {INSET+SIZE},{INSET}"/>
  <polyline points="{W-INSET-SIZE},{INSET} {W-INSET},{INSET} {W-INSET},{INSET+SIZE}"/>
  <polyline points="{INSET},{H-INSET-SIZE} {INSET},{H-INSET} {INSET+SIZE},{H-INSET}"/>
  <polyline points="{W-INSET-SIZE},{H-INSET} {W-INSET},{H-INSET} {W-INSET},{H-INSET-SIZE}"/>
</g>'''

svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="{bg}"/>
  {corners}
  <image href="{section_uri}" x="0" y="{top_pad}" width="{W}" height="{SRC_H}"/>
</svg>
'''

svg_path = POSTS / "post_sobre_genstone.svg"
svg_path.write_text(svg)

png = OUT / "post_sobre_genstone.png"
jpg = OUT / "post_sobre_genstone.jpg"
subprocess.run(["rsvg-convert", "-w", str(W), "-h", str(H),
                "-o", str(png), str(svg_path)], check=True)
subprocess.run(["convert", str(png), "-colorspace", "sRGB", "-quality", "96",
                "-sampling-factor", "1x1", "-strip", str(jpg)], check=True)
png.unlink()
print(f"OK  {jpg.name}")
