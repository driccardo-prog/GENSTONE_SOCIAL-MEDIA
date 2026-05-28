#!/usr/bin/env python3
"""
Adapta piezas 4:5 -> 9:16 (1080x1920) preservando el arte original.

Approach: detecta los GAPS verticales (filas vacias) y le inserta filas
adicionales de bg puro dentro de cada gap. El contenido nunca se corta
ni se reposiciona internamente — solo se separan los bloques.
"""
from pathlib import Path
from PIL import Image
import numpy as np

SRC = Path("/tmp/adapt")
OUT = Path("/home/user/GENSTONE_SOCIAL-MEDIA/output_9x16")
OUT.mkdir(exist_ok=True)

TW, TH = 1080, 1920


def slug(p: Path) -> str:
    s = p.stem.lower()
    return s.replace(" ", "_").replace("'", "").replace("á","a").replace("é","e")


def sample_bg(img: Image.Image):
    """Media de pixels en las 4 esquinas (60x60 cada una)."""
    arr = np.asarray(img.convert("RGB"))
    h, w = arr.shape[:2]
    s = 60
    corners = [arr[0:s, 0:s], arr[0:s, w-s:w], arr[h-s:h, 0:s], arr[h-s:h, w-s:w]]
    stack = np.concatenate([c.reshape(-1, 3) for c in corners])
    return tuple(int(x) for x in np.median(stack, axis=0))


def find_gaps(arr, bg, tol=18, min_gap_rows=20):
    """Devuelve [(y0, y1)] de regiones-gap (filas casi enteramente bg)
       que tengan al menos min_gap_rows filas consecutivas."""
    diff = np.abs(arr.astype(np.int16) - np.array(bg, dtype=np.int16)).max(axis=2)
    row_is_bg = (diff <= tol).mean(axis=1) > 0.99
    h = len(row_is_bg)

    gaps = []
    y = 0
    while y < h:
        if row_is_bg[y]:
            start = y
            while y < h and row_is_bg[y]:
                y += 1
            if y - start >= min_gap_rows:
                gaps.append((start, y))
        else:
            y += 1
    return gaps


def expand(src: Path, dst: Path):
    img = Image.open(src).convert("RGB")
    w0, h0 = img.size
    new_h = int(h0 * TW / w0)
    img = img.resize((TW, new_h), Image.LANCZOS)
    arr = np.asarray(img)
    bg = sample_bg(img)
    bg_hex = "#{:02X}{:02X}{:02X}".format(*bg)

    extra_total = TH - new_h
    if extra_total <= 0:
        img.crop((0, 0, TW, TH)).save(dst, "JPEG", quality=92)
        print(f"OK  {dst.name}  (sin expansion necesaria)")
        return

    gaps = find_gaps(arr, bg)
    # Filtrar gaps que tocan el borde (top/bottom) — solo gaps internos
    internal_gaps = [g for g in gaps if g[0] > 5 and g[1] < new_h - 5]

    if not internal_gaps:
        # Sin gaps internos: agregar margenes top/bottom usando filas-edge
        # del original para evitar costura JPEG
        canvas = Image.new("RGB", (TW, TH), bg)
        canvas.paste(img, (0, extra_total // 2))
        canvas.save(dst, "JPEG", quality=92)
        print(f"OK  {dst.name}  (sin gaps internos)")
        return

    # Distribuir extra_total proporcional al tamaño de cada gap interno
    sizes = [g[1] - g[0] for g in internal_gaps]
    total = sum(sizes)
    extra_per = [int(extra_total * s / total) for s in sizes]
    diff = extra_total - sum(extra_per)
    if diff != 0:
        idx = sizes.index(max(sizes))
        extra_per[idx] += diff

    # Construir canvas:
    #   - copia solo bloques de contenido (sin incluir las filas-gap del original)
    #   - cada gap original lo reemplazamos por bg promedio limpio de (gap + extra)
    canvas = Image.new("RGB", (TW, TH), bg)
    y_canvas = 0
    y_src = 0
    PAD = 8  # rows extra para preservar descenders (p, g, y, etc.)
    for i, (g0, g1) in enumerate(internal_gaps):
        # Extender content hasta g0 + PAD para incluir descenders
        content_end = min(g0 + PAD, g1)
        content_h = content_end - y_src
        if content_h > 0:
            block = img.crop((0, y_src, TW, content_end))
            canvas.paste(block, (0, y_canvas))
            y_canvas += content_h
        # Reemplazar lo que queda del gap por color limpio + extra
        gap_h = (g1 - content_end) + extra_per[i]
        gap_pixels = arr[content_end:g1].reshape(-1, 3) if g1 > content_end else arr[g0:g1].reshape(-1, 3)
        gap_color = tuple(int(c) for c in np.median(gap_pixels, axis=0))
        fill = Image.new("RGB", (TW, gap_h), gap_color)
        canvas.paste(fill, (0, y_canvas))
        y_canvas += gap_h
        y_src = g1

    # Copiar resto del original (despues del ultimo gap interno)
    if y_src < new_h:
        block = img.crop((0, y_src, TW, new_h))
        canvas.paste(block, (0, y_canvas))

    canvas.save(dst, "JPEG", quality=92, optimize=True)
    print(f"OK  {dst.name}  bg={bg_hex}  gaps_internos={len(internal_gaps)}")


def main():
    files = []
    for ext in ("*.jpg", "*.jpeg"):
        files += list(SRC.rglob(ext))
    files = [f for f in files if "__MACOSX" not in str(f)]
    for f in sorted(files):
        dst = OUT / f"{slug(f)}.jpg"
        expand(f, dst)


if __name__ == "__main__":
    main()
