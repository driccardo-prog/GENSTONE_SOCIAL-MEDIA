#!/usr/bin/env python3
"""
Genstone — Generador de posteos 1080x1350 para Instagram/META.

Sistema visual basado en GENSTONE_GUIDELINES.pdf:
  Verde Energía  #68D38E   (acento)
  Verde Genstone #173B2E   (primario)
  Gris Mineral   #282B2A
  Gris Claro     #B6B6B6
  Blanco Puro    #EFEFEF
  Tipografía:    Helvetica Neue (Inter como render fallback), tracking -25

Pipeline:
  - Genera SVG por pieza segun layout
  - rsvg-convert -> PNG 1080x1350
  - magick PNG -> JPG sRGB calidad 92
"""
from pathlib import Path
import subprocess
import shutil
import base64

ROOT   = Path(__file__).parent
POSTS  = ROOT / "posts"
OUT    = ROOT / "output"
FOTOS  = ROOT / "assets" / "fotos"
POSTS.mkdir(exist_ok=True)
OUT.mkdir(exist_ok=True)

W, H = 1080, 1350

# Paleta
VERDE_ENERGIA  = "#68D38E"
VERDE_GENSTONE = "#173B2E"
GRIS_MINERAL   = "#282B2A"
GRIS_CLARO     = "#B6B6B6"
BLANCO         = "#EFEFEF"

FONT = "Inter"   # stand-in para Helvetica Neue
TRACKING = "-0.025em"   # tracking -25 ≈ -0.025em


def logo_chip(cx, cy, scale=1.0):
    """Pill GENSTONE: pastilla verde con texto verde oscuro."""
    w = 240 * scale
    h = 64 * scale
    x = cx - w / 2
    y = cy - h / 2
    fs = 32 * scale
    return f'''
    <g>
      <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" ry="6" fill="{VERDE_ENERGIA}"/>
      <text x="{cx}" y="{cy + fs*0.36}" font-family="{FONT}" font-weight="900"
            font-size="{fs}" fill="{VERDE_GENSTONE}" text-anchor="middle"
            letter-spacing="-0.02em">GENSTONE</text>
    </g>
    '''


def eyebrow(text, y, color):
    return f'''
    <text x="{W/2}" y="{y}" font-family="{FONT}" font-weight="500"
          font-size="22" fill="{color}" text-anchor="middle"
          letter-spacing="0.18em">&lt; {text} &gt;</text>
    '''


def chevrons(cy, color):
    r = 22
    return f'''
    <g fill="none" stroke="{color}" stroke-width="2">
      <circle cx="100" cy="{cy}" r="{r}"/>
      <polyline points="106,{cy-7} 96,{cy} 106,{cy+7}"/>
      <circle cx="{W-100}" cy="{cy}" r="{r}"/>
      <polyline points="{W-106},{cy-7} {W-96},{cy} {W-106},{cy+7}"/>
    </g>
    '''


# ─────────────────────────────────────────────────────────────────────
# Template A — Big stat sobre verde Genstone
# ─────────────────────────────────────────────────────────────────────
def big_stat(filename, stat, sub_lines, eyebrow_txt="ENERGÍA QUE NO FALLA",
             stat_size=380):
    sub_svg = ""
    base = 950
    for i, ln in enumerate(sub_lines):
        sub_svg += f'''
        <text x="{W/2}" y="{base + i*44}" font-family="{FONT}" font-weight="300"
              font-size="34" fill="{BLANCO}" text-anchor="middle"
              letter-spacing="{TRACKING}">{ln}</text>'''

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="{VERDE_GENSTONE}"/>
  {eyebrow(eyebrow_txt, 110, BLANCO)}
  <text x="{W/2}" y="{H/2 + stat_size*0.18}" font-family="{FONT}" font-weight="900"
        font-size="{stat_size}" fill="{VERDE_ENERGIA}" text-anchor="middle"
        letter-spacing="{TRACKING}">{stat}</text>
  {chevrons(H/2, VERDE_ENERGIA)}
  {sub_svg}
  {logo_chip(W/2, H-110)}
</svg>'''
    write(filename, svg)


# ─────────────────────────────────────────────────────────────────────
# Template A2 — Stat multi-linea (24/7 vertical)
# ─────────────────────────────────────────────────────────────────────
def big_stat_split(filename, top, bottom, sub_lines,
                   eyebrow_txt="ENERGÍA QUE NO FALLA", size=380):
    sub_svg = ""
    base = 1020
    for i, ln in enumerate(sub_lines):
        sub_svg += f'''
        <text x="{W/2}" y="{base + i*44}" font-family="{FONT}" font-weight="300"
              font-size="34" fill="{BLANCO}" text-anchor="middle"
              letter-spacing="{TRACKING}">{ln}</text>'''
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="{VERDE_GENSTONE}"/>
  {eyebrow(eyebrow_txt, 110, BLANCO)}
  <text x="{W/2}" y="500" font-family="{FONT}" font-weight="900"
        font-size="{size}" fill="{VERDE_ENERGIA}" text-anchor="middle"
        letter-spacing="{TRACKING}">{top}</text>
  <text x="{W/2}" y="850" font-family="{FONT}" font-weight="900"
        font-size="{size}" fill="{VERDE_ENERGIA}" text-anchor="middle"
        letter-spacing="{TRACKING}">{bottom}</text>
  {chevrons(680, VERDE_ENERGIA)}
  {sub_svg}
  {logo_chip(W/2, H-110)}
</svg>'''
    write(filename, svg)


# ─────────────────────────────────────────────────────────────────────
# Template B — Frase grande sobre gris claro
# ─────────────────────────────────────────────────────────────────────
def quote_card(filename, lines, sub_lines, footer="LO QUE NECESITÁS SIGUE EN MARCHA",
               accent_idx=None, size=120):
    """ lines: list[str] (1-4 lineas).  accent_idx: indice de la linea verde. """
    n = len(lines)
    line_h = size * 1.0
    block_h = n * line_h
    start_y = H/2 - block_h/2 - 100 + size*0.85
    txt = ""
    for i, ln in enumerate(lines):
        c = VERDE_ENERGIA if i == accent_idx else VERDE_GENSTONE
        y = start_y + i*line_h
        txt += f'''
        <text x="{W/2}" y="{y}" font-family="{FONT}" font-weight="800"
              font-size="{size}" fill="{c}" text-anchor="middle"
              letter-spacing="{TRACKING}">{ln}</text>'''
    sub_svg = ""
    sub_start = start_y + n*line_h + 60
    for i, ln in enumerate(sub_lines):
        sub_svg += f'''
        <text x="{W/2}" y="{sub_start + i*44}" font-family="{FONT}" font-weight="400"
              font-size="32" fill="{GRIS_MINERAL}" text-anchor="middle"
              letter-spacing="{TRACKING}">{ln}</text>'''
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="{BLANCO}"/>
  {txt}
  {sub_svg}
  {eyebrow(footer, H-100, GRIS_MINERAL)}
</svg>'''
    write(filename, svg)


# ─────────────────────────────────────────────────────────────────────
# Template C — Foto + texto + chip
# ─────────────────────────────────────────────────────────────────────
def photo_card(filename, photo, lines, eyebrow_txt=None,
               text_color=BLANCO, dark_overlay=0.55, size=84):
    img = FOTOS / photo
    b64 = base64.b64encode(img.read_bytes()).decode()
    img_uri = f"data:image/jpeg;base64,{b64}"
    n = len(lines)
    line_h = size * 1.08
    start_y = H - 360 + size*0.85 - (n-1)*line_h/2
    txt = ""
    for i, ln in enumerate(lines):
        y = start_y + i*line_h
        txt += f'''
        <text x="80" y="{y}" font-family="{FONT}" font-weight="800"
              font-size="{size}" fill="{text_color}"
              letter-spacing="{TRACKING}">{ln}</text>'''
    eb = ""
    if eyebrow_txt:
        eb = f'''
        <text x="80" y="120" font-family="{FONT}" font-weight="500"
              font-size="22" fill="{text_color}" letter-spacing="0.18em">&lt; {eyebrow_txt} &gt;</text>'''
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#000" stop-opacity="0.0"/>
      <stop offset="0.55" stop-color="#000" stop-opacity="0.15"/>
      <stop offset="1" stop-color="#000" stop-opacity="{dark_overlay}"/>
    </linearGradient>
  </defs>
  <image href="{img_uri}" x="0" y="0" width="{W}" height="{H}" preserveAspectRatio="xMidYMid slice"/>
  <rect width="{W}" height="{H}" fill="url(#g)"/>
  {eb}
  {txt}
  <g transform="translate({W-300},{H-110})">
    <rect x="0" y="-32" width="240" height="64" rx="6" fill="{VERDE_ENERGIA}"/>
    <text x="120" y="12" font-family="{FONT}" font-weight="900" font-size="32"
          fill="{VERDE_GENSTONE}" text-anchor="middle" letter-spacing="-0.02em">GENSTONE</text>
  </g>
</svg>'''
    write(filename, svg)


# ─────────────────────────────────────────────────────────────────────
# Template D — Producto: especificaciones (GS12/15/17)
# ─────────────────────────────────────────────────────────────────────
def product_card(filename, modelo, headline, specs, photo=None):
    rows = ""
    base = 660
    for i, (k, v) in enumerate(specs):
        y = base + i*90
        rows += f'''
        <text x="80" y="{y}" font-family="{FONT}" font-weight="400" font-size="28"
              fill="{GRIS_CLARO}" letter-spacing="{TRACKING}">{k}</text>
        <text x="{W-80}" y="{y}" font-family="{FONT}" font-weight="700" font-size="32"
              fill="{BLANCO}" text-anchor="end" letter-spacing="{TRACKING}">{v}</text>
        <line x1="80" y1="{y+18}" x2="{W-80}" y2="{y+18}" stroke="{VERDE_ENERGIA}" stroke-opacity="0.25" stroke-width="1"/>'''
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="{VERDE_GENSTONE}"/>
  {eyebrow("ENERGÍA QUE NO FALLA", 110, BLANCO)}
  <text x="80" y="320" font-family="{FONT}" font-weight="900" font-size="240"
        fill="{VERDE_ENERGIA}" letter-spacing="{TRACKING}">{modelo}</text>
  <text x="80" y="430" font-family="{FONT}" font-weight="400" font-size="44"
        fill="{BLANCO}" letter-spacing="{TRACKING}">{headline}</text>
  <line x1="80" y1="500" x2="{W-80}" y2="500" stroke="{VERDE_ENERGIA}" stroke-width="2"/>
  <text x="80" y="570" font-family="{FONT}" font-weight="300" font-size="26"
        fill="{GRIS_CLARO}" letter-spacing="0.18em">ESPECIFICACIONES</text>
  {rows}
  {logo_chip(W/2, H-110)}
</svg>'''
    write(filename, svg)


def write(name, svg):
    (POSTS / f"{name}.svg").write_text(svg)


# ─────────────────────────────────────────────────────────────────────
#  PIEZAS
# ─────────────────────────────────────────────────────────────────────
def build_all():
    # 01 — Presentación de marca
    quote_card("01_hola_somos_genstone",
        ["Hola.", "Somos", "Genstone."],
        ["Generadores de respaldo automático",
         "premium accesibles."],
        accent_idx=2, size=180)

    # 02 — Mantené activa tu rutina (replica template B literal)
    quote_card("02_mantene_activa_tu_rutina",
        ["Mantené", "activa tu", "rutina."],
        ["Protegemos tu ritmo,",
         "protegemos tus tiempos,",
         "protegemos tu comodidad."],
        accent_idx=1, size=170)

    # 03 — 24/7
    big_stat_split("03_24_7", "24", "/7",
        ["acompañándote y",
         "monitoreando el sistema."])

    # 04 — 100%
    big_stat("04_100_porciento", "100%",
        ["de autonomía", "energética."])

    # 05 — +20 años
    big_stat("05_mas_20", "+20",
        ["años de vida",
         "útil del sistema."])

    # 06 — ≤65 dB(A)
    big_stat("06_65db", "≤65dB",
        ["energía silenciosa.",
         "más bajo que una conversación."],
        stat_size=260)

    # 07 — Promesa de marca (texto sobre claro)
    quote_card("07_promesa",
        ["Lo que", "necesitás,", "sigue en", "marcha."],
        ["Eficiencia. Continuidad. Solidez."],
        accent_idx=3, size=150, footer="GENSTONE — ENERGÍA QUE NO FALLA")

    # 08 — Estamos cuando hace falta (foto generador)
    photo_card("08_estamos_cuando_hace_falta", "genstone-01.jpg",
        ["Estamos", "cuando", "hace falta."],
        eyebrow_txt="ENERGÍA QUE NO FALLA",
        text_color=BLANCO, dark_overlay=0.6, size=92)

    # 09 — Monitoreo 24/7 (foto celular)
    photo_card("09_monitoreo_247", "celular.jpg",
        ["Genstone no", "duerme.",  "Tu energía", "tampoco."],
        eyebrow_txt="MONITOREO 24/7",
        text_color=GRIS_MINERAL, dark_overlay=0.0, size=72)

    # 10 — GS12 producto
    product_card("10_gs12", "GS12", "Respaldo esencial.",
        [("POTENCIA GLP", "12 kW"),
         ("POTENCIA GAS NATURAL", "10 kW"),
         ("NIVEL SONORO", "≤65 dB(A)"),
         ("MOTOR", "GB750 750cc"),
         ("PESO", "289 kg")])


# ─────────────────────────────────────────────────────────────────────
#  RENDER
# ─────────────────────────────────────────────────────────────────────
def render():
    svgs = sorted(POSTS.glob("*.svg"))
    for svg in svgs:
        png = OUT / (svg.stem + ".png")
        jpg = OUT / (svg.stem + ".jpg")
        subprocess.run([
            "rsvg-convert", "-w", str(W), "-h", str(H),
            "-o", str(png), str(svg)
        ], check=True)
        subprocess.run([
            "convert", str(png),
            "-colorspace", "sRGB",
            "-quality", "92",
            "-strip",
            str(jpg)
        ], check=True)
        png.unlink()
        print(f"OK  {jpg.name}")


if __name__ == "__main__":
    build_all()
    render()
