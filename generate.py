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
HAAS = "Neue Haas Grotesk Display Pro"   # tipografia real (Light + Medium)
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


# ─────────────────────────────────────────────────────────────────────
# Template E — Foto producto + ficha técnica resumida
# ─────────────────────────────────────────────────────────────────────
def product_sheet(filename, photo, modelo, funcion, specs):
    """ specs: list of (label, value) — 4 items recomendado. """
    img = FOTOS / photo
    b64 = base64.b64encode(img.read_bytes()).decode()
    img_uri = f"data:image/jpeg;base64,{b64}"

    # Bloque info: parte inferior verde Genstone
    INFO_TOP = 760
    # Distribución de 4 specs en 2 columnas
    col_x = [80, W/2 + 20]
    spec_svg = ""
    for i, (k, v) in enumerate(specs):
        col = i % 2
        row = i // 2
        x = col_x[col]
        y = 1010 + row*150
        spec_svg += f'''
        <text x="{x}" y="{y}" font-family="{FONT}" font-weight="400" font-size="22"
              fill="{VERDE_ENERGIA}" letter-spacing="0.18em">{k.upper()}</text>
        <text x="{x}" y="{y+50}" font-family="{FONT}" font-weight="700" font-size="38"
              fill="{BLANCO}" letter-spacing="{TRACKING}">{v}</text>'''

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="{BLANCO}"/>
  <image href="{img_uri}" x="0" y="0" width="{W}" height="{INFO_TOP}" preserveAspectRatio="xMidYMid slice"/>
  <text x="60" y="80" font-family="{FONT}" font-weight="500" font-size="22"
        fill="{GRIS_MINERAL}" letter-spacing="0.18em">&lt; FICHA TÉCNICA &gt;</text>

  <rect x="0" y="{INFO_TOP}" width="{W}" height="{H-INFO_TOP}" fill="{VERDE_GENSTONE}"/>
  <text x="80" y="{INFO_TOP+150}" font-family="{FONT}" font-weight="900" font-size="180"
        fill="{VERDE_ENERGIA}" letter-spacing="{TRACKING}">{modelo}</text>
  <text x="80" y="{INFO_TOP+200}" font-family="{FONT}" font-weight="400" font-size="28"
        fill="{BLANCO}" letter-spacing="{TRACKING}">{funcion}</text>
  <line x1="80" y1="{INFO_TOP+225}" x2="{W-80}" y2="{INFO_TOP+225}" stroke="{VERDE_ENERGIA}" stroke-opacity="0.4" stroke-width="1"/>

  {spec_svg}

  <g transform="translate({W-260},{H-90})">
    <rect x="0" y="-32" width="200" height="56" rx="6" fill="{VERDE_ENERGIA}"/>
    <text x="100" y="9" font-family="{FONT}" font-weight="900" font-size="28"
          fill="{VERDE_GENSTONE}" text-anchor="middle" letter-spacing="-0.02em">GENSTONE</text>
  </g>
</svg>'''
    write(filename, svg)


# ─────────────────────────────────────────────────────────────────────
# Template F — Card de producto estilo web (foto + chips)
# ─────────────────────────────────────────────────────────────────────
def web_card(filename, photo, modelo, descripcion, chips):
    """ Replica del card de genstone.com.ar/productos.
        chips: list of (label, value) — 3 chips. """
    img = FOTOS / photo
    b64 = base64.b64encode(img.read_bytes()).decode()
    img_uri = f"data:image/jpeg;base64,{b64}"

    PHOTO_H = 780
    PAD = 70

    # Descripción wrap manual (2 líneas máx, ya viene corta)
    desc_svg = ""
    for i, ln in enumerate(descripcion):
        desc_svg += f'''
        <text x="{PAD}" y="{PHOTO_H + 200 + i*44}" font-family="{FONT}" font-weight="400"
              font-size="30" fill="{GRIS_MINERAL}" letter-spacing="{TRACKING}">{ln}</text>'''

    # 3 chips horizontales
    chips_y = PHOTO_H + 320
    chip_h = 120
    gap = 16
    chip_w = (W - 2*PAD - 2*gap) / 3
    chips_svg = ""
    for i, (k, v) in enumerate(chips):
        x = PAD + i*(chip_w + gap)
        chips_svg += f'''
        <rect x="{x}" y="{chips_y}" width="{chip_w}" height="{chip_h}" rx="10"
              fill="none" stroke="{GRIS_CLARO}" stroke-width="1.5"/>
        <text x="{x + chip_w/2}" y="{chips_y + 40}" font-family="{FONT}" font-weight="300"
              font-size="20" fill="{GRIS_MINERAL}" text-anchor="middle"
              letter-spacing="0.1em">{k.upper()}</text>
        <text x="{x + chip_w/2}" y="{chips_y + 86}" font-family="{FONT}" font-weight="500"
              font-size="34" fill="{VERDE_GENSTONE}" text-anchor="middle"
              letter-spacing="{TRACKING}">{v}</text>'''

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="#FFFFFF"/>
  <rect x="0" y="0" width="{W}" height="{PHOTO_H}" fill="{BLANCO}"/>
  <image href="{img_uri}" x="0" y="0" width="{W}" height="{PHOTO_H}" preserveAspectRatio="xMidYMid slice"/>

  <text x="{PAD}" y="{PHOTO_H + 130}" font-family="{FONT}" font-weight="500"
        font-size="100" fill="{VERDE_GENSTONE}" letter-spacing="{TRACKING}">{modelo}</text>

  {desc_svg}
  {chips_svg}
</svg>'''
    write(filename, svg)


# ─────────────────────────────────────────────────────────────────────
# Template G — Consultanos (card "+ otro modelo")
# ─────────────────────────────────────────────────────────────────────
def consult_card(filename, eyebrow, title, descripcion, cta):
    PHOTO_H = 780
    PAD = 70
    desc_svg = ""
    for i, ln in enumerate(descripcion):
        desc_svg += f'''
        <text x="{PAD}" y="{PHOTO_H + 290 + i*44}" font-family="{FONT}" font-weight="400"
              font-size="30" fill="{GRIS_MINERAL}" letter-spacing="{TRACKING}">{ln}</text>'''
    title_svg = ""
    for i, ln in enumerate(title):
        title_svg += f'''
        <text x="{PAD}" y="{PHOTO_H + 140 + i*70}" font-family="{FONT}" font-weight="500"
              font-size="58" fill="{VERDE_GENSTONE}" letter-spacing="{TRACKING}">{ln}</text>'''

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="#FFFFFF"/>
  <rect x="0" y="0" width="{W}" height="{PHOTO_H}" fill="{BLANCO}"/>

  <!-- Plus signo -->
  <g stroke="{VERDE_ENERGIA}" stroke-width="22" stroke-linecap="square">
    <line x1="{W/2-110}" y1="{PHOTO_H/2}" x2="{W/2+110}" y2="{PHOTO_H/2}"/>
    <line x1="{W/2}" y1="{PHOTO_H/2-110}" x2="{W/2}" y2="{PHOTO_H/2+110}"/>
  </g>

  <text x="{PAD}" y="{PHOTO_H + 60}" font-family="{FONT}" font-weight="500"
        font-size="26" fill="{GRIS_MINERAL}" letter-spacing="0.18em">{eyebrow.upper()}</text>

  {title_svg}
  {desc_svg}

  <text x="{PAD}" y="{H - 70}" font-family="{FONT}" font-weight="500"
        font-size="32" fill="{VERDE_ENERGIA}" letter-spacing="{TRACKING}">{cta} →</text>
</svg>'''
    write(filename, svg)


# ─────────────────────────────────────────────────────────────────────
# Template H — FAQ carrusel (Neue Haas Display)
# Pregunta grande y bold arriba, respuesta abajo. Centrado, sin lineas.
# ─────────────────────────────────────────────────────────────────────
def faq_slide(filename, idx, total, question, answer_lines):
    indicator = f"{idx:02d} / {total:02d}"

    # Pregunta — centrada, bold, grande
    q_size = 96
    q_svg = ""
    q_block_h = len(question) * 110
    q_start_y = 480 - q_block_h/2 + 80
    for i, ln in enumerate(question):
        q_svg += f'''
        <text x="{W/2}" y="{q_start_y + i*110}" font-family="{HAAS}" font-weight="500"
              font-size="{q_size}" fill="{VERDE_GENSTONE}" text-anchor="middle"
              letter-spacing="-0.02em">{ln}</text>'''

    # Respuesta — centrada, light
    a_svg = ""
    a_start_y = 880
    for i, ln in enumerate(answer_lines):
        a_svg += f'''
        <text x="{W/2}" y="{a_start_y + i*54}" font-family="{HAAS}" font-weight="300"
              font-size="36" fill="{GRIS_MINERAL}" text-anchor="middle"
              letter-spacing="0">{ln}</text>'''

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="#FFFFFF"/>

  <text x="{W/2}" y="180" font-family="{HAAS}" font-weight="500"
        font-size="24" fill="{VERDE_ENERGIA}" text-anchor="middle"
        letter-spacing="0.22em">PREGUNTAS FRECUENTES — {indicator}</text>

  {q_svg}

  {a_svg}
</svg>'''
    write(filename, svg)


# ─────────────────────────────────────────────────────────────────────
# Slide FAQ 03 — Ruido con comparación visual (centrado, sin lineas)
# ─────────────────────────────────────────────────────────────────────
def faq_ruido(filename):
    idx, total = 3, 6

    # Pregunta centrada arriba
    q_lines = ["¿Hace mucho", "ruido?"]
    q_svg = ""
    for i, ln in enumerate(q_lines):
        q_svg += f'''
        <text x="{W/2}" y="{370 + i*110}" font-family="{HAAS}" font-weight="500"
              font-size="96" fill="{VERDE_GENSTONE}" text-anchor="middle"
              letter-spacing="-0.02em">{ln}</text>'''

    # Comparación — eyebrow + 3 filas centradas
    comp_y = 660
    rows = [
        ("65 dB(A)", "Una conversación normal.", True),
        ("80 dB(A)", "Tráfico intenso.", False),
        ("90 dB(A)", "Generadores comunes.", False),
    ]
    rows_svg = ""
    row_h = 88
    base = comp_y + 60
    for i, (db, label, highlight) in enumerate(rows):
        y = base + i*row_h
        db_color = VERDE_ENERGIA if highlight else GRIS_CLARO
        label_color = VERDE_GENSTONE if highlight else GRIS_MINERAL
        label_weight = "500" if highlight else "300"
        rows_svg += f'''
        <text x="{W/2}" y="{y}" font-family="{HAAS}" font-weight="500"
              font-size="46" fill="{db_color}" text-anchor="middle"
              letter-spacing="-0.015em">{db}<tspan font-weight="300" font-size="32" fill="{label_color}" dx="20">= {label}</tspan></text>'''

    # Implicación
    impl_y = base + 3*row_h + 80

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="#FFFFFF"/>

  <text x="{W/2}" y="180" font-family="{HAAS}" font-weight="500"
        font-size="24" fill="{VERDE_ENERGIA}" text-anchor="middle"
        letter-spacing="0.22em">PREGUNTAS FRECUENTES — {idx:02d} / {total:02d}</text>

  {q_svg}

  <text x="{W/2}" y="{comp_y}" font-family="{HAAS}" font-weight="500"
        font-size="26" fill="{GRIS_MINERAL}" text-anchor="middle"
        letter-spacing="0.22em">COMPARACIÓN</text>

  {rows_svg}

  <text x="{W/2}" y="{impl_y}" font-family="{HAAS}" font-weight="500"
        font-size="26" fill="{GRIS_MINERAL}" text-anchor="middle"
        letter-spacing="0.22em">IMPLICACIÓN</text>
  <text x="{W/2}" y="{impl_y+58}" font-family="{HAAS}" font-weight="500"
        font-size="38" fill="{VERDE_GENSTONE}" text-anchor="middle"
        letter-spacing="-0.015em">Genstone funciona al lado tuyo</text>
  <text x="{W/2}" y="{impl_y+108}" font-family="{HAAS}" font-weight="500"
        font-size="38" fill="{VERDE_GENSTONE}" text-anchor="middle"
        letter-spacing="-0.015em">sin molestarte.</text>
</svg>'''
    write(filename, svg)


# ─────────────────────────────────────────────────────────────────────
# Cover de carrusel FAQ
# ─────────────────────────────────────────────────────────────────────
def faq_cover(filename):
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="{VERDE_GENSTONE}"/>
  <text x="{W/2}" y="160" font-family="{HAAS}" font-weight="500"
        font-size="22" fill="{VERDE_ENERGIA}" text-anchor="middle"
        letter-spacing="0.18em">&lt; ENERGÍA QUE NO FALLA &gt;</text>

  <text x="{W/2}" y="600" font-family="{HAAS}" font-weight="500"
        font-size="160" fill="{BLANCO}" stroke="{BLANCO}" stroke-width="4"
        text-anchor="middle"
        letter-spacing="-0.025em">Preguntas</text>
  <text x="{W/2}" y="780" font-family="{HAAS}" font-weight="500"
        font-size="160" fill="{VERDE_ENERGIA}" stroke="{VERDE_ENERGIA}" stroke-width="4"
        text-anchor="middle"
        letter-spacing="-0.025em">Frecuentes</text>

  <text x="{W/2}" y="960" font-family="{HAAS}" font-weight="300"
        font-size="32" fill="{BLANCO}" text-anchor="middle"
        letter-spacing="0">Todo lo que necesitás saber</text>
  <text x="{W/2}" y="1004" font-family="{HAAS}" font-weight="300"
        font-size="32" fill="{BLANCO}" text-anchor="middle"
        letter-spacing="0">antes de elegir tu generador.</text>

  <text x="{W/2}" y="1250" font-family="{HAAS}" font-weight="500"
        font-size="30" fill="{VERDE_ENERGIA}" text-anchor="middle"
        letter-spacing="0">Deslizá →</text>
</svg>'''
    write(filename, svg)


# ─────────────────────────────────────────────────────────────────────
# Cierre del carrusel FAQ — mismo lenguaje que la cover
# ─────────────────────────────────────────────────────────────────────
def faq_outro(filename):
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="{VERDE_GENSTONE}"/>
  <text x="{W/2}" y="160" font-family="{HAAS}" font-weight="500"
        font-size="22" fill="{VERDE_ENERGIA}" text-anchor="middle"
        letter-spacing="0.18em">&lt; ENERGÍA QUE NO FALLA &gt;</text>

  <text x="{W/2}" y="600" font-family="{HAAS}" font-weight="500"
        font-size="160" fill="{BLANCO}" stroke="{BLANCO}" stroke-width="4"
        text-anchor="middle"
        letter-spacing="-0.025em">¿Tenés</text>
  <text x="{W/2}" y="780" font-family="{HAAS}" font-weight="500"
        font-size="160" fill="{VERDE_ENERGIA}" stroke="{VERDE_ENERGIA}" stroke-width="4"
        text-anchor="middle"
        letter-spacing="-0.025em">más dudas?</text>

  <text x="{W/2}" y="960" font-family="{HAAS}" font-weight="300"
        font-size="32" fill="{BLANCO}" text-anchor="middle"
        letter-spacing="0">Asesorate en nuestra web o escribinos.</text>
  <text x="{W/2}" y="1004" font-family="{HAAS}" font-weight="300"
        font-size="32" fill="{BLANCO}" text-anchor="middle"
        letter-spacing="0">Te ayudamos a elegir el generador ideal.</text>

  <text x="{W/2}" y="1250" font-family="{HAAS}" font-weight="500"
        font-size="36" fill="{VERDE_ENERGIA}" text-anchor="middle"
        letter-spacing="0">genstone.com.ar →</text>
</svg>'''
    write(filename, svg)


# ─────────────────────────────────────────────────────────────────────
# Carruseles temáticos — slides genéricas reutilizables
# ─────────────────────────────────────────────────────────────────────
def carousel_cover(filename, eyebrow, title_white, title_green, sub_lines, cta="Deslizá →"):
    """Cover verde Genstone: titulo en 2 lineas, segunda en verde energia."""
    sub_svg = ""
    for i, ln in enumerate(sub_lines):
        sub_svg += f'''
        <text x="{W/2}" y="{960 + i*44}" font-family="{HAAS}" font-weight="300"
              font-size="32" fill="{BLANCO}" text-anchor="middle"
              letter-spacing="0">{ln}</text>'''
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="{VERDE_GENSTONE}"/>
  <text x="{W/2}" y="160" font-family="{HAAS}" font-weight="500"
        font-size="22" fill="{VERDE_ENERGIA}" text-anchor="middle"
        letter-spacing="0.18em">&lt; {eyebrow.upper()} &gt;</text>

  <text x="{W/2}" y="600" font-family="{HAAS}" font-weight="500"
        font-size="160" fill="{BLANCO}" stroke="{BLANCO}" stroke-width="4"
        text-anchor="middle" letter-spacing="-0.025em">{title_white}</text>
  <text x="{W/2}" y="780" font-family="{HAAS}" font-weight="500"
        font-size="160" fill="{VERDE_ENERGIA}" stroke="{VERDE_ENERGIA}" stroke-width="4"
        text-anchor="middle" letter-spacing="-0.025em">{title_green}</text>

  {sub_svg}

  <text x="{W/2}" y="1250" font-family="{HAAS}" font-weight="500"
        font-size="30" fill="{VERDE_ENERGIA}" text-anchor="middle"
        letter-spacing="0">{cta}</text>
</svg>'''
    write(filename, svg)


def carousel_outro(filename, eyebrow, title_white, title_green, sub_lines, cta):
    """Outro verde Genstone: mismo lenguaje que cover."""
    sub_svg = ""
    for i, ln in enumerate(sub_lines):
        sub_svg += f'''
        <text x="{W/2}" y="{960 + i*44}" font-family="{HAAS}" font-weight="300"
              font-size="32" fill="{BLANCO}" text-anchor="middle"
              letter-spacing="0">{ln}</text>'''
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="{VERDE_GENSTONE}"/>
  <text x="{W/2}" y="160" font-family="{HAAS}" font-weight="500"
        font-size="22" fill="{VERDE_ENERGIA}" text-anchor="middle"
        letter-spacing="0.18em">&lt; {eyebrow.upper()} &gt;</text>

  <text x="{W/2}" y="600" font-family="{HAAS}" font-weight="500"
        font-size="160" fill="{BLANCO}" stroke="{BLANCO}" stroke-width="4"
        text-anchor="middle" letter-spacing="-0.025em">{title_white}</text>
  <text x="{W/2}" y="780" font-family="{HAAS}" font-weight="500"
        font-size="160" fill="{VERDE_ENERGIA}" stroke="{VERDE_ENERGIA}" stroke-width="4"
        text-anchor="middle" letter-spacing="-0.025em">{title_green}</text>

  {sub_svg}

  <text x="{W/2}" y="1250" font-family="{HAAS}" font-weight="500"
        font-size="36" fill="{VERDE_ENERGIA}" text-anchor="middle"
        letter-spacing="0">{cta}</text>
</svg>'''
    write(filename, svg)


def content_slide(filename, eyebrow, headline, body_lines, idx=None, total=None):
    """Slide blanca centrada: headline grande Medium + body Light."""
    eb = eyebrow.upper()
    if idx and total:
        eb = f"{eb} — {idx:02d} / {total:02d}"

    # Headline (max 2 lineas)
    h_svg = ""
    for i, ln in enumerate(headline):
        h_svg += f'''
        <text x="{W/2}" y="{380 + i*110}" font-family="{HAAS}" font-weight="500"
              font-size="92" fill="{VERDE_GENSTONE}" text-anchor="middle"
              letter-spacing="-0.02em">{ln}</text>'''

    # Body
    body_svg = ""
    base_y = 380 + len(headline)*110 + 80
    for i, ln in enumerate(body_lines):
        body_svg += f'''
        <text x="{W/2}" y="{base_y + i*54}" font-family="{HAAS}" font-weight="300"
              font-size="36" fill="{GRIS_MINERAL}" text-anchor="middle"
              letter-spacing="0">{ln}</text>'''

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="#FFFFFF"/>
  <text x="{W/2}" y="180" font-family="{HAAS}" font-weight="500"
        font-size="24" fill="{VERDE_ENERGIA}" text-anchor="middle"
        letter-spacing="0.22em">{eb}</text>
  {h_svg}
  {body_svg}
</svg>'''
    write(filename, svg)


def steps_slide(filename, eyebrow, headline, steps, idx=None, total=None):
    """Slide blanca con lista numerada centrada."""
    eb = eyebrow.upper()
    if idx and total:
        eb = f"{eb} — {idx:02d} / {total:02d}"

    # Headline
    h_svg = f'''
    <text x="{W/2}" y="340" font-family="{HAAS}" font-weight="500"
          font-size="68" fill="{VERDE_GENSTONE}" text-anchor="middle"
          letter-spacing="-0.02em">{headline}</text>'''

    # Steps
    base_y = 480
    step_h = 110
    steps_svg = ""
    for i, txt in enumerate(steps):
        y = base_y + i*step_h
        steps_svg += f'''
        <text x="{W/2 - 360}" y="{y}" font-family="{HAAS}" font-weight="500"
              font-size="60" fill="{VERDE_ENERGIA}" text-anchor="end"
              letter-spacing="-0.02em">{i+1}</text>
        <text x="{W/2 - 320}" y="{y}" font-family="{HAAS}" font-weight="300"
              font-size="32" fill="{GRIS_MINERAL}" text-anchor="start"
              letter-spacing="0">{txt}</text>'''

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="#FFFFFF"/>
  <text x="{W/2}" y="180" font-family="{HAAS}" font-weight="500"
        font-size="24" fill="{VERDE_ENERGIA}" text-anchor="middle"
        letter-spacing="0.22em">{eb}</text>
  {h_svg}
  {steps_svg}
</svg>'''
    write(filename, svg)


def bullets_slide(filename, eyebrow, headline, bullets, idx=None, total=None):
    """Slide blanca con N bullets centrados (label + valor)."""
    eb = eyebrow.upper()
    if idx and total:
        eb = f"{eb} — {idx:02d} / {total:02d}"

    h_svg = f'''
    <text x="{W/2}" y="340" font-family="{HAAS}" font-weight="500"
          font-size="68" fill="{VERDE_GENSTONE}" text-anchor="middle"
          letter-spacing="-0.02em">{headline}</text>'''

    base_y = 540
    row_h = 150
    bullets_svg = ""
    for i, (label, value) in enumerate(bullets):
        y = base_y + i*row_h
        bullets_svg += f'''
        <text x="{W/2}" y="{y}" font-family="{HAAS}" font-weight="500"
              font-size="24" fill="{VERDE_ENERGIA}" text-anchor="middle"
              letter-spacing="0.22em">{label.upper()}</text>
        <text x="{W/2}" y="{y+58}" font-family="{HAAS}" font-weight="500"
              font-size="46" fill="{VERDE_GENSTONE}" text-anchor="middle"
              letter-spacing="-0.02em">{value}</text>'''

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="#FFFFFF"/>
  <text x="{W/2}" y="180" font-family="{HAAS}" font-weight="500"
        font-size="24" fill="{VERDE_ENERGIA}" text-anchor="middle"
        letter-spacing="0.22em">{eb}</text>
  {h_svg}
  {bullets_svg}
</svg>'''
    write(filename, svg)


def big_stat_slide(filename, eyebrow, stat, sub_lines, idx=None, total=None):
    """Slide verde Genstone con estadistica gigante."""
    eb = eyebrow.upper()
    if idx and total:
        eb = f"{eb} — {idx:02d} / {total:02d}"

    sub_svg = ""
    for i, ln in enumerate(sub_lines):
        sub_svg += f'''
        <text x="{W/2}" y="{1000 + i*48}" font-family="{HAAS}" font-weight="300"
              font-size="36" fill="{BLANCO}" text-anchor="middle"
              letter-spacing="0">{ln}</text>'''

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="{VERDE_GENSTONE}"/>
  <text x="{W/2}" y="180" font-family="{HAAS}" font-weight="500"
        font-size="24" fill="{VERDE_ENERGIA}" text-anchor="middle"
        letter-spacing="0.22em">{eb}</text>

  <text x="{W/2}" y="700" font-family="{HAAS}" font-weight="500"
        font-size="220" fill="{VERDE_ENERGIA}" stroke="{VERDE_ENERGIA}" stroke-width="5"
        text-anchor="middle" letter-spacing="-0.03em">{stat}</text>

  {sub_svg}
</svg>'''
    write(filename, svg)


# ─────────────────────────────────────────────────────────────────────
# v2 — Layouts con mas impacto visual
# ─────────────────────────────────────────────────────────────────────

def _corners(color, inset=60, size=32, thick=2):
    """Marcas de registro en las 4 esquinas."""
    return f'''
    <g stroke="{color}" stroke-width="{thick}" fill="none">
      <polyline points="{inset},{inset+size} {inset},{inset} {inset+size},{inset}"/>
      <polyline points="{W-inset-size},{inset} {W-inset},{inset} {W-inset},{inset+size}"/>
      <polyline points="{inset},{H-inset-size} {inset},{H-inset} {inset+size},{H-inset}"/>
      <polyline points="{W-inset-size},{H-inset} {W-inset},{H-inset} {W-inset},{H-inset-size}"/>
    </g>'''


def _eyebrow(text, color, y=100, with_brackets=False):
    body = text.upper()
    if with_brackets:
        body = f"&lt; {body} &gt;"
    return f'''
    <text x="{W/2}" y="{y}" font-family="{HAAS}" font-weight="500"
          font-size="22" fill="{color}" text-anchor="middle"
          letter-spacing="0.22em">{body}</text>'''


def _footer(text, color, y=None):
    if y is None: y = H - 80
    return f'''
    <text x="{W/2}" y="{y}" font-family="{HAAS}" font-weight="500"
          font-size="22" fill="{color}" text-anchor="middle"
          letter-spacing="0.22em">{text.upper()}</text>'''


# Cover v2 — corners + tipo gigante
def cover_v2(filename, eyebrow, title_white, title_green, sub_lines, cta="Deslizá →"):
    sub_svg = ""
    for i, ln in enumerate(sub_lines):
        sub_svg += f'''
        <text x="{W/2}" y="{1010 + i*44}" font-family="{HAAS}" font-weight="300"
              font-size="32" fill="{BLANCO}" text-anchor="middle"
              letter-spacing="0">{ln}</text>'''
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="{VERDE_GENSTONE}"/>
  {_corners(VERDE_ENERGIA)}
  {_eyebrow(eyebrow, VERDE_ENERGIA, y=140, with_brackets=True)}

  <text x="{W/2}" y="600" font-family="{HAAS}" font-weight="500"
        font-size="180" fill="{BLANCO}" stroke="{BLANCO}" stroke-width="5"
        text-anchor="middle" letter-spacing="-0.03em">{title_white}</text>
  <text x="{W/2}" y="800" font-family="{HAAS}" font-weight="500"
        font-size="180" fill="{VERDE_ENERGIA}" stroke="{VERDE_ENERGIA}" stroke-width="5"
        text-anchor="middle" letter-spacing="-0.03em">{title_green}</text>

  {sub_svg}

  <text x="{W/2}" y="1280" font-family="{HAAS}" font-weight="500"
        font-size="32" fill="{VERDE_ENERGIA}" text-anchor="middle"
        letter-spacing="0">{cta}</text>
</svg>'''
    write(filename, svg)


def outro_v2(filename, eyebrow, title_white, title_green, sub_lines, cta):
    sub_svg = ""
    for i, ln in enumerate(sub_lines):
        sub_svg += f'''
        <text x="{W/2}" y="{1010 + i*44}" font-family="{HAAS}" font-weight="300"
              font-size="32" fill="{BLANCO}" text-anchor="middle"
              letter-spacing="0">{ln}</text>'''
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="{VERDE_GENSTONE}"/>
  {_corners(VERDE_ENERGIA)}
  {_eyebrow(eyebrow, VERDE_ENERGIA, y=140, with_brackets=True)}

  <text x="{W/2}" y="600" font-family="{HAAS}" font-weight="500"
        font-size="180" fill="{BLANCO}" stroke="{BLANCO}" stroke-width="5"
        text-anchor="middle" letter-spacing="-0.03em">{title_white}</text>
  <text x="{W/2}" y="800" font-family="{HAAS}" font-weight="500"
        font-size="180" fill="{VERDE_ENERGIA}" stroke="{VERDE_ENERGIA}" stroke-width="5"
        text-anchor="middle" letter-spacing="-0.03em">{title_green}</text>

  {sub_svg}

  <text x="{W/2}" y="1280" font-family="{HAAS}" font-weight="500"
        font-size="36" fill="{VERDE_ENERGIA}" text-anchor="middle"
        letter-spacing="0">{cta}</text>
</svg>'''
    write(filename, svg)


def hero_statement(filename, eyebrow, label, lines, accent_idx=None, bg="dark",
                   indicator=None):
    """Slide-manifiesto: tipografia gigante centrada vertical/horizontalmente.
       bg='dark' verde Genstone | bg='energy' verde energia | bg='light' blanco."""
    if bg == "dark":
        bg_col = VERDE_GENSTONE
        default_col = BLANCO
        accent_col = VERDE_ENERGIA
        eb_col = VERDE_ENERGIA
    elif bg == "energy":
        bg_col = VERDE_ENERGIA
        default_col = VERDE_GENSTONE
        accent_col = BLANCO
        eb_col = VERDE_GENSTONE
    else:
        bg_col = BLANCO
        default_col = VERDE_GENSTONE
        accent_col = VERDE_ENERGIA
        eb_col = VERDE_ENERGIA

    n = len(lines)
    size = 160 if n <= 2 else (130 if n == 3 else 110)
    line_h = size * 1.0
    block_h = n * line_h
    start_y = H/2 - block_h/2 + size*0.85

    txt_svg = ""
    for i, ln in enumerate(lines):
        col = accent_col if i == accent_idx else default_col
        y = start_y + i*line_h
        txt_svg += f'''
        <text x="{W/2}" y="{y}" font-family="{HAAS}" font-weight="500"
              font-size="{size}" fill="{col}" stroke="{col}" stroke-width="4"
              text-anchor="middle" letter-spacing="-0.03em">{ln}</text>'''

    eb_text = label.upper()
    if indicator:
        eb_text = f"{eb_text}  ·  {indicator}"

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="{bg_col}"/>
  {_corners(eb_col)}
  {_eyebrow(eyebrow, eb_col, y=140)}
  {txt_svg}
  {_footer(label, eb_col, y=H-100)}
</svg>'''
    write(filename, svg)


def numbered_v2(filename, eyebrow, headline, steps, indicator=None, bg="dark"):
    """Lista numerada: numeros gigantes en verde energia + steps a la derecha."""
    if bg == "dark":
        bg_col = VERDE_GENSTONE
        text_col = BLANCO
        accent_col = VERDE_ENERGIA
    else:
        bg_col = BLANCO
        text_col = VERDE_GENSTONE
        accent_col = VERDE_ENERGIA

    h_svg = f'''
    <text x="{W/2}" y="290" font-family="{HAAS}" font-weight="500"
          font-size="90" fill="{text_col}" stroke="{text_col}" stroke-width="3"
          text-anchor="middle" letter-spacing="-0.025em">{headline}</text>'''

    n = len(steps)
    base_y = 460
    row_h = 130 if n <= 5 else 110
    rows = ""
    for i, txt in enumerate(steps):
        y = base_y + i*row_h
        rows += f'''
        <text x="{W/2 - 50}" y="{y+30}" font-family="{HAAS}" font-weight="500"
              font-size="120" fill="{accent_col}" stroke="{accent_col}" stroke-width="3"
              text-anchor="end" letter-spacing="-0.03em">{i+1}</text>
        <text x="{W/2 + 20}" y="{y}" font-family="{HAAS}" font-weight="300"
              font-size="32" fill="{text_col}" text-anchor="start"
              letter-spacing="0">{txt}</text>'''

    eb = eyebrow.upper()
    if indicator:
        eb = f"{eb}  ·  {indicator}"

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="{bg_col}"/>
  {_corners(accent_col)}
  {_eyebrow(eb, accent_col, y=140)}
  {h_svg}
  {rows}
</svg>'''
    write(filename, svg)


def stripes_slide(filename, eyebrow, headline, items, indicator=None):
    """Bloques horizontales alternando colores: cada item es una stripe.
       items: [(label, value), ...] (3 items)."""
    h_svg = f'''
    <text x="{W/2}" y="280" font-family="{HAAS}" font-weight="500"
          font-size="90" fill="{VERDE_GENSTONE}" stroke="{VERDE_GENSTONE}" stroke-width="3"
          text-anchor="middle" letter-spacing="-0.025em">{headline}</text>'''

    n = len(items)
    # 3 stripes ocupan el resto del canvas
    stripes_top = 380
    stripes_bot = H - 120
    stripe_h = (stripes_bot - stripes_top) / n
    stripes_svg = ""
    bgs = [VERDE_GENSTONE, VERDE_ENERGIA, VERDE_GENSTONE]
    text_cols = [BLANCO, VERDE_GENSTONE, BLANCO]
    accent_cols = [VERDE_ENERGIA, VERDE_GENSTONE, VERDE_ENERGIA]
    for i, (label, value) in enumerate(items):
        y_top = stripes_top + i*stripe_h
        cy = y_top + stripe_h/2
        stripes_svg += f'''
        <rect x="60" y="{y_top}" width="{W-120}" height="{stripe_h}" fill="{bgs[i]}" rx="12"/>
        <text x="{W/2}" y="{cy - 18}" font-family="{HAAS}" font-weight="500"
              font-size="22" fill="{accent_cols[i]}" text-anchor="middle"
              letter-spacing="0.22em">{label.upper()}</text>
        <text x="{W/2}" y="{cy + 38}" font-family="{HAAS}" font-weight="500"
              font-size="50" fill="{text_cols[i]}"
              stroke="{text_cols[i]}" stroke-width="2"
              text-anchor="middle" letter-spacing="-0.02em">{value}</text>'''

    eb = eyebrow.upper()
    if indicator:
        eb = f"{eb}  ·  {indicator}"

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="#FFFFFF"/>
  {_eyebrow(eb, VERDE_ENERGIA, y=140)}
  {h_svg}
  {stripes_svg}
</svg>'''
    write(filename, svg)


def stat_hero(filename, eyebrow, stat, sub_lines, indicator=None):
    """Stat gigante full-bleed con cross marks decorativos."""
    sub_svg = ""
    for i, ln in enumerate(sub_lines):
        sub_svg += f'''
        <text x="{W/2}" y="{1080 + i*48}" font-family="{HAAS}" font-weight="300"
              font-size="36" fill="{BLANCO}" text-anchor="middle"
              letter-spacing="0">{ln}</text>'''

    eb = eyebrow.upper()
    if indicator:
        eb = f"{eb}  ·  {indicator}"

    # crosses decorativos
    def cross(cx, cy, s=14):
        return f'<g stroke="{VERDE_ENERGIA}" stroke-width="2"><line x1="{cx-s}" y1="{cy}" x2="{cx+s}" y2="{cy}"/><line x1="{cx}" y1="{cy-s}" x2="{cx}" y2="{cy+s}"/></g>'

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="{VERDE_GENSTONE}"/>
  {_corners(VERDE_ENERGIA)}
  {_eyebrow(eb, VERDE_ENERGIA, y=140)}

  {cross(140, 600)}
  {cross(W-140, 600)}
  {cross(140, 820)}
  {cross(W-140, 820)}

  <text x="{W/2}" y="780" font-family="{HAAS}" font-weight="500"
        font-size="260" fill="{VERDE_ENERGIA}" stroke="{VERDE_ENERGIA}" stroke-width="6"
        text-anchor="middle" letter-spacing="-0.04em">{stat}</text>

  {sub_svg}
</svg>'''
    write(filename, svg)


def manifesto_slide(filename, eyebrow, title_white, title_green, body_lines, footer=None):
    """Slide manifiesto: frase heroica arriba + parrafo abajo, centrado."""
    body_svg = ""
    n = len(body_lines)
    body_start = 1330 - 90 - 60 - n*46
    for i, ln in enumerate(body_lines):
        body_svg += f'''
        <text x="{W/2}" y="{body_start + i*46}" font-family="{HAAS}" font-weight="300"
              font-size="30" fill="{BLANCO}" text-anchor="middle"
              letter-spacing="0">{ln}</text>'''

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="{VERDE_GENSTONE}"/>
  {_corners(VERDE_ENERGIA)}
  {_eyebrow(eyebrow, VERDE_ENERGIA, y=140, with_brackets=True)}

  <text x="{W/2}" y="470" font-family="{HAAS}" font-weight="500"
        font-size="160" fill="{BLANCO}" stroke="{BLANCO}" stroke-width="5"
        text-anchor="middle" letter-spacing="-0.03em">{title_white}</text>
  <text x="{W/2}" y="640" font-family="{HAAS}" font-weight="500"
        font-size="160" fill="{VERDE_ENERGIA}" stroke="{VERDE_ENERGIA}" stroke-width="5"
        text-anchor="middle" letter-spacing="-0.03em">{title_green}</text>

  {body_svg}

  <text x="{W/2}" y="{H-70}" font-family="{HAAS}" font-weight="500"
        font-size="22" fill="{VERDE_ENERGIA}" text-anchor="middle"
        letter-spacing="0.22em">{(footer or '').upper()}</text>
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

    # ─── Carrusel Preguntas Frecuentes ───
    faq_cover("faq_00_cover")

    faq_slide("faq_01_kw", 1, 6,
        ["¿Cuántos kW necesito", "para mi casa?"],
        ["Depende de tu consumo. Para departamentos y casas",
         "chicas (heladera, luces, WiFi, TV + un aire) alcanza",
         "con GS12. Para 3-4 ambientes con varios aires y",
         "lavarropas, GS15. Para una casa grande funcionando",
         "sin restricciones, GS17 o superior.",
         "",
         "Consultanos y te ayudamos a elegir."])

    faq_slide("faq_02_combustible", 2, 6,
        ["¿Qué combustible", "usa?"],
        ["Funciona con GLP (gas envasado) o Gas Natural",
         "de red. Elegís el que ya tenés disponible en tu",
         "casa, sin obras adicionales.",
         "",
         "Misma performance en cualquiera de los dos."])

    faq_ruido("faq_03_ruido")

    faq_slide("faq_04_depto", 4, 6,
        ["¿Se puede instalar", "en un departamento?"],
        ["Sí. Genstone GS12 está pensado para departamentos",
         "y espacios reducidos.",
         "",
         "Requiere ventilación adecuada, conexión a gas y",
         "una instalación eléctrica autorizada por un",
         "matriculado. Nuestro equipo te asesora."])

    faq_slide("faq_05_ats", 5, 6,
        ["¿Cómo funciona la", "transferencia automática?"],
        ["El sistema ATS monitorea la red 24/7. Cuando",
         "detecta un corte, arranca el generador en",
         "milisegundos y transfiere la carga automáticamente.",
         "",
         "Cuando vuelve la energía, transfiere de vuelta y",
         "apaga el motor. Sin que tengas que tocar nada."])

    faq_slide("faq_06_mantenimiento", 6, 6,
        ["¿Qué mantenimiento", "necesita?"],
        ["Mantenimiento programado: cambio de aceite, filtro",
         "de aire y bujías según horas de uso.",
         "",
         "El monitoreo 24/7 te avisa cuando toca cada",
         "servicio. Nuestra red técnica se encarga del",
         "resto, en todo el país."])

    faq_outro("faq_07_outro")

    # ─── Quiénes somos (single slide) ───
    manifesto_slide("quienes_somos",
        "Quiénes somos",
        "Lo esencial,", "bien hecho.",
        ["Empresa argentina de respaldo energético",
         "para el hogar. Generadores premium-accesibles",
         "a gas natural y GLP.",
         "",
         "Depósito propio en Parque Industrial DT4,",
         "logística y soporte técnico en todo el país.",
         "Garantía de fábrica de 1 año + posventa."],
        footer="genstone.com.ar")

    # ─── Carrusel ATS: Transferencia automática (v2) ───
    EB1 = "TRANSFERENCIA AUTOMÁTICA"
    T1 = 6

    cover_v2("ats_00_cover", EB1,
        "¿Cómo", "funciona?",
        ["La transferencia automática que mantiene",
         "tu energía sin que tengas que tocar nada."])

    hero_statement("ats_01_tecnologia", EB1, f"01 / {T1}",
        ["ATS.", "El cerebro", "del sistema."],
        accent_idx=0, bg="dark", indicator=None)

    numbered_v2("ats_02_proceso", EB1,
        "Así funciona.",
        ["Monitorea la red eléctrica.",
         "Detecta caída en milisegundos.",
         "Ordena al motor arrancar.",
         "Cambia a alimentación Genstone.",
         "Tu casa no se queda sin energía."],
        indicator=f"02 / {T1}", bg="dark")

    stat_hero("ats_03_velocidad", EB1,
        "0.0001s",
        ["Más rápido que parpadear.",
         "Más rápido de lo que tu casa se da cuenta."],
        indicator=f"03 / {T1}")

    stripes_slide("ats_04_seguridad", EB1,
        "Seguridad total.",
        [("Sin cortocircuitos", "Aislación garantizada."),
         ("Sin daños", "No afecta tus aparatos."),
         ("Sin interrupciones", "Transferencia invisible.")],
        indicator=f"04 / {T1}")

    outro_v2("ats_05_cierre", EB1,
        "Vos ni", "te enterás.",
        ["Mientras el barrio se queda a oscuras,",
         "tu casa sigue funcionando como siempre."],
        cta="genstone.com.ar →")

    # ─── Carrusel Respaldo: Promesa + Evidencia (v2) ───
    EB2 = "RESPALDO QUE NO FALLA"
    T2 = 6

    cover_v2("res_00_cover", EB2,
        "Respaldo", "estable.",
        ["Respaldo eficiente que mantiene",
         "todo en marcha."])

    hero_statement("res_01_escenarios", EB2, f"01 / {T2}",
        ["Incluso", "en los", "escenarios", "más exigentes."],
        accent_idx=3, bg="energy")

    stripes_slide("res_02_cortes", EB2,
        "Lo que significa.",
        [("Corte de 1 hora", "Tu casa funciona normalmente."),
         ("Corte de 8 horas", "Tu vida no se detiene."),
         ("Corte de 2 días", "Seguís igual que siempre.")],
        indicator=f"02 / {T2}")

    stripes_slide("res_03_como", EB2,
        "Cómo lo hace.",
        [("Automático", "Arranca solo."),
         ("Eficiente", "Consume inteligente."),
         ("Estable", "Energía limpia y constante.")],
        indicator=f"03 / {T2}")

    hero_statement("res_04_conclusion", EB2, f"04 / {T2}",
        ["No es", "un plan B.", "Es tu plan A."],
        accent_idx=2, bg="dark")

    outro_v2("res_05_cierre", EB2,
        "Lo que", "necesitás,",
        ["sigue en marcha.",
         "Cualquier día, cualquier hora, cualquier corte."],
        cta="genstone.com.ar →")

    # ─── Cards estilo web (genstone.com.ar/productos) ───
    web_card("web_01_gs12", "genstone-02.jpg", "GS12",
        ["Departamentos y casas chicas. Respalda heladera,",
         "luces, WiFi, TV y un aire acondicionado."],
        [("GLP", "11 kW"), ("GAS NATURAL", "10 kW"), ("FASE", "Monofásico")])

    web_card("web_02_gs15", "genstone-02.jpg", "GS15",
        ["Casas de 3-4 ambientes. Aires, microondas,",
         "lavarropas. Respaldo total ante cortes."],
        [("GLP", "15 kW"), ("GAS NATURAL", "14 kW"), ("FASE", "Monofásico")])

    web_card("web_03_gs17", "genstone-02.jpg", "GS17",
        ["Casas grandes. Toda la casa funcionando sin",
         "restricciones, incluso en cortes largos."],
        [("GLP", "17 kW"), ("GAS NATURAL", "15 kW"), ("FASE", "Monofásico")])

    web_card("web_04_gs18", "genstone-02.jpg", "GS18",
        ["Residencia grande / consumo alto."],
        [("GLP", "18 kW"), ("GAS NATURAL", "16 kW"), ("FASE", "Monofásico")])

    web_card("web_05_gs20", "genstone-02.jpg", "GS20",
        ["Casa grande con quincho/pileta o comercio chico."],
        [("GLP", "20 kW"), ("GAS NATURAL", "18 kW"), ("FASE", "Monofásico")])

    consult_card("web_06_consultanos",
        "Consultanos",
        ["¿Necesitás un generador", "más grande?"],
        ["Para potencias mayores consultanos por más",
         "modelos disponibles."],
        "Hablar por WhatsApp")

    # 11 — Ficha resumida GS12 (foto + info)
    product_sheet("11_ficha_gs12", "genstone-01.jpg", "GS12",
        "Respaldo automático esencial.",
        [("POTENCIA", "11 kW GLP · 10 kW GN"),
         ("NIVEL SONORO", "≤ 65 dB(A)"),
         ("MOTOR", "GB750 · 750 cc"),
         ("PESO NETO", "289 kg")])

    # 12 — Ficha resumida GS15
    product_sheet("12_ficha_gs15", "genstone-02.jpg", "GS15",
        "Respaldo automático de mayor capacidad.",
        [("POTENCIA", "15 kW GLP · 14 kW GN"),
         ("NIVEL SONORO", "≤ 65 dB(A)"),
         ("MOTOR", "GB1000 · 999 cc"),
         ("PESO NETO", "305 kg")])

    # 13 — Ficha resumida GS17
    product_sheet("13_ficha_gs17", "genstone-03.jpg", "GS17",
        "Respaldo automático de potencia avanzada.",
        [("POTENCIA", "17 kW GLP · 15 kW GN"),
         ("NIVEL SONORO", "≤ 65 dB(A)"),
         ("MOTOR", "GB1000 · 999 cc"),
         ("PESO NETO", "306 kg")])

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
