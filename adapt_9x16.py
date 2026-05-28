#!/usr/bin/env python3
"""
Adapta piezas 4:5 (1080x1350) a 9:16 (1080x1920) preservando el arte original.
Estrategia: detecta color de fondo del corner top-left, escala a 1080 ancho y
extiende vertical con ese color hasta 1920.
"""
import subprocess
from pathlib import Path

SRC = Path("/tmp/adapt")
OUT = Path("/home/user/GENSTONE_SOCIAL-MEDIA/output_9x16")
OUT.mkdir(exist_ok=True)

TW, TH = 1080, 1920

# slug helpers
def slug(p: Path) -> str:
    s = p.stem.lower()
    s = s.replace(" ", "_").replace("'", "").replace("á","a").replace("é","e")
    return s

def detect_bg(img: Path) -> str:
    """Devuelve color HEX del pixel (5,5) — corner top-left."""
    out = subprocess.check_output(
        ["convert", str(img), "-format", "%[pixel:p{5,5}]", "info:"]).decode().strip()
    # 'srgb(23,59,46)' -> #173B2E
    if "srgb" in out:
        nums = out[out.index("(")+1:out.index(")")].split(",")
        r, g, b = [int(n) for n in nums[:3]]
        return f"#{r:02X}{g:02X}{b:02X}"
    return "#FFFFFF"

def adapt(src: Path):
    bg = detect_bg(src)
    name = slug(src)
    dst = OUT / f"{name}.jpg"
    # Resize ancho a 1080 (alto = 1350 si era 4:5), luego extent a 1080x1920 con bg
    subprocess.run([
        "convert", str(src),
        "-resize", "1080x",
        "-background", bg,
        "-gravity", "center",
        "-extent", f"{TW}x{TH}",
        "-colorspace", "sRGB",
        "-quality", "92",
        "-strip",
        str(dst)
    ], check=True)
    print(f"OK  {dst.name}  (bg={bg})")

def main():
    files = []
    for ext in ("*.jpg", "*.jpeg"):
        files += list(SRC.rglob(ext))
    files = [f for f in files if "__MACOSX" not in str(f)]
    for f in sorted(files):
        adapt(f)

if __name__ == "__main__":
    main()
