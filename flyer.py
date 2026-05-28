#!/usr/bin/env python3
"""
Flyer WhatsApp 1080x1920 — Linea GS (GS12 / GS15 / GS17)
Foto + modelo + descripcion + chips + precio en cada card.
"""
import subprocess, base64
from pathlib import Path

ROOT = Path(__file__).parent
FOTOS = ROOT / "assets" / "fotos"
OUT = ROOT / "output"
POSTS = ROOT / "posts"

W, H = 1080, 1920

VERDE_ENERGIA  = "#68D38E"
VERDE_GENSTONE = "#173B2E"
GRIS_MINERAL   = "#282B2A"
GRIS_CLARO     = "#B6B6B6"
BLANCO         = "#EFEFEF"

HAAS = "Neue Haas Grotesk Display Pro"
FALLBACK = "Inter"

def img_data(path: Path) -> str:
    b64 = base64.b64encode(path.read_bytes()).decode()
    return f"data:image/jpeg;base64,{b64}"


def product_card(y, modelo, descripcion, chips, precio):
    """Una card 1080 x 480: foto izquierda + info derecha + precio."""
    foto = img_data(FOTOS / "genstone-02.jpg")

    PHOTO_X, PHOTO_W, PHOTO_H = 50, 380, 380
    INFO_X = PHOTO_X + PHOTO_W + 40   # 470
    INFO_RIGHT = W - 50               # 1030

    desc = ""
    for i, ln in enumerate(descripcion):
        desc += f'''
        <text x="{INFO_X}" y="{y + 180 + i*38}" font-family="{HAAS}" font-weight="300"
              font-size="24" fill="{GRIS_MINERAL}" letter-spacing="0">{ln}</text>'''

    chips_svg = ""
    chip_y = y + 270
    chip_h = 76
    gap = 10
    chip_w = (INFO_RIGHT - INFO_X - 2*gap) / 3
    for i, (k, v) in enumerate(chips):
        cx = INFO_X + i*(chip_w + gap)
        chips_svg += f'''
        <rect x="{cx}" y="{chip_y}" width="{chip_w}" height="{chip_h}" rx="8"
              fill="none" stroke="{GRIS_CLARO}" stroke-width="1.5"/>
        <text x="{cx + chip_w/2}" y="{chip_y + 28}" font-family="{HAAS}" font-weight="300"
              font-size="15" fill="{GRIS_MINERAL}" text-anchor="middle"
              letter-spacing="0.12em">{k.upper()}</text>
        <text x="{cx + chip_w/2}" y="{chip_y + 58}" font-family="{HAAS}" font-weight="500"
              font-size="22" fill="{VERDE_GENSTONE}" text-anchor="middle"
              letter-spacing="-0.02em">{v}</text>'''

    precio_y = y + 410
    return f'''
    <rect x="{PHOTO_X}" y="{y + 20}" width="{PHOTO_W}" height="{PHOTO_H}" fill="{BLANCO}" rx="12"/>
    <image href="{foto}" x="{PHOTO_X}" y="{y + 20}" width="{PHOTO_W}" height="{PHOTO_H}"
           preserveAspectRatio="xMidYMid slice" clip-path="inset(0 round 12px)"/>
    <text x="{INFO_X}" y="{y + 115}" font-family="{HAAS}" font-weight="500"
          font-size="92" fill="{VERDE_GENSTONE}" letter-spacing="-0.025em">{modelo}</text>
    {desc}
    {chips_svg}
    <text x="{INFO_X}" y="{precio_y}" font-family="{HAAS}" font-weight="500"
          font-size="18" fill="{GRIS_MINERAL}" letter-spacing="0.2em">PRECIO</text>
    <text x="{INFO_RIGHT}" y="{precio_y}" font-family="{HAAS}" font-weight="500"
          font-size="44" fill="{VERDE_GENSTONE}" text-anchor="end"
          letter-spacing="-0.02em">{precio}</text>
    <line x1="50" y1="{y + 460}" x2="{W-50}" y2="{y + 460}"
          stroke="{VERDE_ENERGIA}" stroke-opacity="0.35" stroke-width="1"/>
    '''


def build_flyer():
    HEADER_H = 230
    INTRO_H = 200
    cards = ""
    products = [
        ("GS12", ["Departamentos y casas chicas.",
                  "Respalda heladera, luces, WiFi, TV y un AC."],
         [("GLP", "11 kW"), ("GAS NATURAL", "10 kW"), ("FASE", "Monofásico")],
         "USD 5.500"),
        ("GS15", ["Casas de 3-4 ambientes. Aires,",
                  "microondas, lavarropas. Respaldo total."],
         [("GLP", "15 kW"), ("GAS NATURAL", "14 kW"), ("FASE", "Monofásico")],
         "USD 7.800"),
        ("GS17", ["Casas grandes. Toda la casa funcionando",
                  "sin restricciones, incluso en cortes largos."],
         [("GLP", "17 kW"), ("GAS NATURAL", "15 kW"), ("FASE", "Monofásico")],
         "USD 9.800"),
    ]
    for i, (modelo, desc, chips, precio) in enumerate(products):
        y = HEADER_H + INTRO_H + i * 450
        cards += product_card(y, modelo, desc, chips, precio)

    footer_y = HEADER_H + INTRO_H + 3 * 450 + 30

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="#FFFFFF"/>

  <!-- Header -->
  <!-- Logo chip GENSTONE -->
  <g transform="translate({W/2 - 110}, 70)">
    <rect x="0" y="0" width="220" height="56" rx="6" fill="{VERDE_ENERGIA}"/>
    <text x="110" y="38" font-family="{HAAS}" font-weight="500" font-size="28"
          fill="{VERDE_GENSTONE}" text-anchor="middle" letter-spacing="-0.02em">GENSTONE</text>
  </g>

  <text x="{W/2}" y="170" font-family="{HAAS}" font-weight="500"
        font-size="22" fill="{VERDE_ENERGIA}" text-anchor="middle"
        letter-spacing="0.22em">&lt; NUESTROS PRODUCTOS &gt;</text>

  <text x="{W/2}" y="225" font-family="{HAAS}" font-weight="500"
        font-size="44" fill="{VERDE_GENSTONE}" text-anchor="middle"
        letter-spacing="-0.025em">Línea GS — Lista de precios</text>

  <!-- Intro: quienes somos / donde estamos -->
  <text x="{W/2}" y="300" font-family="{HAAS}" font-weight="500"
        font-size="20" fill="{VERDE_ENERGIA}" text-anchor="middle"
        letter-spacing="0.22em">SOBRE GENSTONE</text>
  <text x="{W/2}" y="350" font-family="{HAAS}" font-weight="500"
        font-size="34" fill="{VERDE_GENSTONE}" text-anchor="middle"
        letter-spacing="-0.025em">Empresa argentina de respaldo energético</text>
  <text x="{W/2}" y="392" font-family="{HAAS}" font-weight="500"
        font-size="34" fill="{VERDE_GENSTONE}" text-anchor="middle"
        letter-spacing="-0.025em">premium-accesible para el hogar.</text>
  <text x="{W/2}" y="438" font-family="{HAAS}" font-weight="300"
        font-size="24" fill="{GRIS_MINERAL}" text-anchor="middle"
        letter-spacing="0">Depósito propio en Parque Industrial DT4 · llegamos a todo el país.</text>

  <!-- Cards -->
  {cards}

  <!-- Footer -->
  <text x="{W/2}" y="{footer_y}" font-family="{HAAS}" font-weight="500"
        font-size="22" fill="{VERDE_ENERGIA}" text-anchor="middle"
        letter-spacing="0.22em">&lt; ENERGÍA QUE NO FALLA &gt;</text>
  <text x="{W/2}" y="{footer_y + 50}" font-family="{HAAS}" font-weight="300"
        font-size="24" fill="{GRIS_MINERAL}" text-anchor="middle"
        letter-spacing="0">Garantía de fábrica 1 año + posventa  ·  genstone.com.ar</text>
    '''
    # Cerrar SVG
    svg += "\n</svg>\n"
    (POSTS / "flyer_lista_precios.svg").write_text(svg)


def render():
    svg = POSTS / "flyer_lista_precios.svg"
    png = OUT / "flyer_lista_precios.png"
    jpg = OUT / "flyer_lista_precios.jpg"
    subprocess.run(["rsvg-convert", "-w", str(W), "-h", str(H),
                    "-o", str(png), str(svg)], check=True)
    subprocess.run(["convert", str(png), "-colorspace", "sRGB",
                    "-quality", "92", "-strip", str(jpg)], check=True)
    png.unlink()
    print(f"OK  {jpg.name}")


if __name__ == "__main__":
    build_flyer()
    render()
