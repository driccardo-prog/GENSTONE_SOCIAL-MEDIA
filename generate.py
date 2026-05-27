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
