#!/usr/bin/env python3
"""
Flyer WhatsApp 1080x2400 — version scrolleable.
Header + Quienes somos (con iconos) + Lista de precios + Footer.
"""
import subprocess, base64
from pathlib import Path

ROOT = Path(__file__).parent
FOTOS = ROOT / "assets" / "fotos"
OUT = ROOT / "output"
POSTS = ROOT / "posts"

W, H = 1080, 2900

VERDE_ENERGIA  = "#68D38E"
VERDE_GENSTONE = "#173B2E"
GRIS_MINERAL   = "#282B2A"
GRIS_CLARO     = "#B6B6B6"
BLANCO         = "#EFEFEF"

HAAS = "Neue Haas Grotesk Display Pro"


def img_data(path: Path) -> str:
    b64 = base64.b64encode(path.read_bytes()).decode()
    return f"data:image/jpeg;base64,{b64}"


def logo_genstone(cx, cy, scale=1.0):
    """Logo GENSTONE: tabletilla verde con bordes superior/inferior ondulados,
       'GENSTONE' en verde Genstone con peso heavy (stroke + fill)."""
    w = 360 * scale
    h = 110 * scale
    x = cx - w / 2
    y = cy - h / 2
    # Curva sutil arriba y abajo (estilo brand wordmark)
    bulge = 12 * scale
    path = (f"M {x} {y+bulge} "
            f"Q {x + w/2} {y - bulge}, {x + w} {y + bulge} "
            f"L {x + w} {y + h - bulge} "
            f"Q {x + w/2} {y + h + bulge}, {x} {y + h - bulge} "
            f"Z")
    fs = 64 * scale
    return f'''
    <path d="{path}" fill="{VERDE_ENERGIA}"/>
    <text x="{cx}" y="{cy + fs*0.36}" font-family="{HAAS}" font-weight="500"
          font-size="{fs}" fill="{VERDE_GENSTONE}"
          stroke="{VERDE_GENSTONE}" stroke-width="3.5"
          text-anchor="middle" letter-spacing="-0.04em">GENSTONE</text>
    '''


# ─── Iconos SVG, 80x80, en verde energía ────────────────────────────
def icon_pin(cx, cy):
    """Pin de ubicacion."""
    x, y = cx - 40, cy - 40
    return f'''<g transform="translate({x},{y})" stroke="{VERDE_ENERGIA}" stroke-width="4"
        fill="none" stroke-linecap="round" stroke-linejoin="round">
      <path d="M 40 8 C 24 8 12 20 12 36 C 12 56 40 74 40 74 C 40 74 68 56 68 36 C 68 20 56 8 40 8 Z"/>
      <circle cx="40" cy="34" r="8"/>
    </g>'''


def icon_shield(cx, cy):
    """Escudo con check."""
    x, y = cx - 40, cy - 40
    return f'''<g transform="translate({x},{y})" stroke="{VERDE_ENERGIA}" stroke-width="4"
        fill="none" stroke-linecap="round" stroke-linejoin="round">
      <path d="M 40 8 L 68 18 L 68 38 C 68 54 40 72 40 72 C 40 72 12 54 12 38 L 12 18 Z"/>
      <polyline points="26,40 36,50 54,30"/>
    </g>'''


def icon_truck(cx, cy):
    """Camion delivery."""
    x, y = cx - 40, cy - 40
    return f'''<g transform="translate({x},{y})" stroke="{VERDE_ENERGIA}" stroke-width="4"
        fill="none" stroke-linecap="round" stroke-linejoin="round">
      <rect x="6" y="26" width="38" height="26" rx="2"/>
      <path d="M 44 32 L 56 32 L 70 44 L 70 52 L 44 52 Z"/>
      <circle cx="20" cy="58" r="6"/>
      <circle cx="56" cy="58" r="6"/>
    </g>'''


def icon_tile(cx, y, icon_fn, title, sub_lines):
    """Tile con icono arriba + titulo + subtitulo."""
    icon = icon_fn(cx, y + 50)
    title_svg = f'''<text x="{cx}" y="{y + 175}" font-family="{HAAS}" font-weight="500"
        font-size="28" fill="{VERDE_GENSTONE}" text-anchor="middle"
        letter-spacing="-0.015em">{title}</text>'''
    sub_svg = ""
    for i, ln in enumerate(sub_lines):
        sub_svg += f'''
        <text x="{cx}" y="{y + 215 + i*32}" font-family="{HAAS}" font-weight="300"
              font-size="22" fill="{GRIS_MINERAL}" text-anchor="middle"
              letter-spacing="0">{ln}</text>'''
    return icon + title_svg + sub_svg


def product_card(y, modelo, descripcion, chips, precio):
    """Card 1080 x 420: foto + info + precio."""
    foto = img_data(FOTOS / "genstone-02.jpg")

    PHOTO_X, PHOTO_W, PHOTO_H = 60, 340, 340
    INFO_X = PHOTO_X + PHOTO_W + 50   # 470
    INFO_RIGHT = W - 60

    desc = ""
    for i, ln in enumerate(descripcion):
        desc += f'''
        <text x="{INFO_X}" y="{y + 170 + i*38}" font-family="{HAAS}" font-weight="300"
              font-size="24" fill="{GRIS_MINERAL}" letter-spacing="0">{ln}</text>'''

    chips_svg = ""
    chip_y = y + 250
    chip_h = 70
    gap = 10
    chip_w = (INFO_RIGHT - INFO_X - 2*gap) / 3
    for i, (k, v) in enumerate(chips):
        cx = INFO_X + i*(chip_w + gap)
        chips_svg += f'''
        <rect x="{cx}" y="{chip_y}" width="{chip_w}" height="{chip_h}" rx="8"
              fill="none" stroke="{GRIS_CLARO}" stroke-width="1.5"/>
        <text x="{cx + chip_w/2}" y="{chip_y + 26}" font-family="{HAAS}" font-weight="300"
              font-size="14" fill="{GRIS_MINERAL}" text-anchor="middle"
              letter-spacing="0.12em">{k.upper()}</text>
        <text x="{cx + chip_w/2}" y="{chip_y + 54}" font-family="{HAAS}" font-weight="500"
              font-size="22" fill="{VERDE_GENSTONE}" text-anchor="middle"
              letter-spacing="-0.02em">{v}</text>'''

    return f'''
    <image href="{foto}" x="{PHOTO_X}" y="{y + 20}" width="{PHOTO_W}" height="{PHOTO_H}"
           preserveAspectRatio="xMidYMid slice"/>
    <text x="{INFO_X}" y="{y + 110}" font-family="{HAAS}" font-weight="500"
          font-size="100" fill="{VERDE_GENSTONE}" letter-spacing="-0.025em">{modelo}</text>
    {desc}
    {chips_svg}
    <!-- precio destacado -->
    <rect x="{INFO_X}" y="{y + 350}" width="{INFO_RIGHT - INFO_X}" height="60"
          fill="{VERDE_GENSTONE}" rx="8"/>
    <text x="{INFO_X + 24}" y="{y + 390}" font-family="{HAAS}" font-weight="500"
          font-size="18" fill="{VERDE_ENERGIA}" letter-spacing="0.2em">PRECIO</text>
    <text x="{INFO_RIGHT - 24}" y="{y + 392}" font-family="{HAAS}" font-weight="500"
          font-size="36" fill="{BLANCO}" text-anchor="end"
          letter-spacing="-0.02em">{precio}</text>
    '''


def _corners_top(color, inset=40, size=28, thick=2):
    """Solo brackets superiores (header dark green)."""
    return f'''
    <g stroke="{color}" stroke-width="{thick}" fill="none">
      <polyline points="{inset},{inset+size} {inset},{inset} {inset+size},{inset}"/>
      <polyline points="{W-inset-size},{inset} {W-inset},{inset} {W-inset},{inset+size}"/>
    </g>'''


def _corners_bottom(color, y_bottom, inset=40, size=28, thick=2):
    """Brackets inferiores en y_bottom (footer dark green)."""
    return f'''
    <g stroke="{color}" stroke-width="{thick}" fill="none">
      <polyline points="{inset},{y_bottom-size} {inset},{y_bottom} {inset+size},{y_bottom}"/>
      <polyline points="{W-inset-size},{y_bottom} {W-inset},{y_bottom} {W-inset},{y_bottom-size}"/>
    </g>'''


def build_flyer():
    # ─── Quiénes somos: 3 tiles (icon + título + subtitle) ───────
    tile_y = 800
    tiles = (
        icon_tile(W * 0.18, tile_y, icon_pin,
                  "Hecho en Argentina",
                  ["Depósito en Parque", "Industrial DT4."])
        + icon_tile(W * 0.50, tile_y, icon_shield,
                    "Garantía 1 año",
                    ["Respaldo de fábrica", "+ posventa."])
        + icon_tile(W * 0.82, tile_y, icon_truck,
                    "Logística nacional",
                    ["Llegamos a todo", "el país."])
    )

    # ─── Lista de precios: 3 cards ───────────────────────────────
    cards_y_start = 1340
    products = [
        ("GS12", ["Departamentos y casas chicas.",
                  "Heladera, luces, WiFi, TV y un AC."],
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
    cards = ""
    for i, (modelo, desc, chips, precio) in enumerate(products):
        cards += product_card(cards_y_start + i * 420, modelo, desc, chips, precio)

    footer_y = cards_y_start + 3 * 420 + 110

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect width="{W}" height="{H}" fill="#FFFFFF"/>

  <!-- ═══ HEADER ════════════════════════════════════════════════ -->
  <rect x="0" y="0" width="{W}" height="380" fill="{VERDE_GENSTONE}"/>
  {_corners_top(VERDE_ENERGIA)}

  <text x="{W/2}" y="150" font-family="{HAAS}" font-weight="500"
        font-size="22" fill="{VERDE_ENERGIA}" text-anchor="middle"
        letter-spacing="0.22em">&lt; ENERGÍA QUE NO FALLA &gt;</text>

  <text x="{W/2}" y="260" font-family="{HAAS}" font-weight="500"
        font-size="80" fill="{BLANCO}" stroke="{BLANCO}" stroke-width="3"
        text-anchor="middle" letter-spacing="-0.025em">Lo esencial,</text>
  <text x="{W/2}" y="350" font-family="{HAAS}" font-weight="500"
        font-size="80" fill="{VERDE_ENERGIA}" stroke="{VERDE_ENERGIA}" stroke-width="3"
        text-anchor="middle" letter-spacing="-0.025em">bien hecho.</text>

  <!-- ═══ QUIENES SOMOS ═══════════════════════════════════════ -->
  <text x="{W/2}" y="510" font-family="{HAAS}" font-weight="500"
        font-size="22" fill="{VERDE_ENERGIA}" text-anchor="middle"
        letter-spacing="0.22em">&lt; SOBRE GENSTONE &gt;</text>

  <text x="{W/2}" y="600" font-family="{HAAS}" font-weight="500"
        font-size="48" fill="{VERDE_GENSTONE}" stroke="{VERDE_GENSTONE}" stroke-width="2"
        text-anchor="middle" letter-spacing="-0.025em">Empresa argentina de respaldo</text>
  <text x="{W/2}" y="654" font-family="{HAAS}" font-weight="500"
        font-size="48" fill="{VERDE_GENSTONE}" stroke="{VERDE_GENSTONE}" stroke-width="2"
        text-anchor="middle" letter-spacing="-0.025em">energético para el hogar.</text>

  <text x="{W/2}" y="720" font-family="{HAAS}" font-weight="300"
        font-size="26" fill="{GRIS_MINERAL}" text-anchor="middle"
        letter-spacing="0">Generadores premium-accesibles a gas natural y GLP.</text>

  {tiles}

  <!-- Divider -->
  <line x1="60" y1="1140" x2="{W-60}" y2="1140" stroke="{VERDE_ENERGIA}" stroke-width="1.5"/>

  <!-- ═══ LISTA DE PRECIOS ═══════════════════════════════════ -->
  <text x="{W/2}" y="1200" font-family="{HAAS}" font-weight="500"
        font-size="22" fill="{VERDE_ENERGIA}" text-anchor="middle"
        letter-spacing="0.22em">&lt; LÍNEA GS &gt;</text>

  <text x="{W/2}" y="1280" font-family="{HAAS}" font-weight="500"
        font-size="68" fill="{VERDE_GENSTONE}" stroke="{VERDE_GENSTONE}" stroke-width="3"
        text-anchor="middle" letter-spacing="-0.025em">Lista de precios</text>

  {cards}

  <!-- ═══ FOOTER ═══════════════════════════════════════════ -->
  <rect x="0" y="{footer_y - 30}" width="{W}" height="{H - (footer_y - 30)}" fill="{VERDE_GENSTONE}"/>
  {_corners_bottom(VERDE_ENERGIA, H - 40)}
  <text x="{W/2}" y="{footer_y + 40}" font-family="{HAAS}" font-weight="500"
        font-size="22" fill="{VERDE_ENERGIA}" text-anchor="middle"
        letter-spacing="0.22em">&lt; CONSULTANOS &gt;</text>

  <!-- Web (linkeable) -->
  <a href="https://genstone.com.ar" target="_blank">
    <text x="{W/2}" y="{footer_y + 100}" font-family="{HAAS}" font-weight="500"
          font-size="42" fill="{BLANCO}" text-anchor="middle"
          letter-spacing="-0.02em">genstone.com.ar</text>
  </a>

  <!-- Instagram (linkeable) -->
  <a href="https://instagram.com/genstonegroup" target="_blank">
    <text x="{W/2}" y="{footer_y + 150}" font-family="{HAAS}" font-weight="500"
          font-size="30" fill="{VERDE_ENERGIA}" text-anchor="middle"
          letter-spacing="-0.02em">@genstonegroup</text>
  </a>

  <text x="{W/2}" y="{footer_y + 185}" font-family="{HAAS}" font-weight="300"
        font-size="19" fill="{GRIS_CLARO}" text-anchor="middle"
        letter-spacing="0">Precios sujetos a modificación sin previo aviso.</text>
</svg>
'''
    (POSTS / "flyer_lista_precios.svg").write_text(svg)


def render():
    svg = POSTS / "flyer_lista_precios.svg"
    png = OUT / "flyer_lista_precios.png"
    jpg = OUT / "flyer_lista_precios.jpg"
    subprocess.run(["rsvg-convert", "-w", str(W), "-h", str(H),
                    "-o", str(png), str(svg)], check=True)
    subprocess.run(["convert", str(png), "-colorspace", "sRGB",
                    "-quality", "96", "-sampling-factor", "1x1",
                    "-strip", str(jpg)], check=True)
    png.unlink()
    print(f"OK  {jpg.name}  ({W}x{H})")


if __name__ == "__main__":
    build_flyer()
    render()
