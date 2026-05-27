# Genstone — Posteos Instagram / META

Generador de piezas 1080×1350 a partir del sistema visual de Genstone.

## Sistema visual

| Color | HEX | Uso |
| --- | --- | --- |
| Verde Energía | `#68D38E` | acento / números |
| Verde Genstone | `#173B2E` | primario / fondos |
| Gris Mineral | `#282B2A` | texto |
| Gris Claro | `#B6B6B6` | secundarios |
| Blanco Puro | `#EFEFEF` | fondos claros |

**Tipografía:** Helvetica Neue · tracking −25 (en este render: Inter como stand-in, `letter-spacing: -0.025em`).

## Templates

- **A — Big stat sobre verde**: número grande verde + bajada blanca + chip GENSTONE (`03–06`).
- **B — Frase sobre claro**: titulares en verde Genstone con palabra/línea acento en verde energía (`01, 02, 07`).
- **C — Foto + overlay**: foto + degradado + texto + chip (`08, 09`).
- **D — Producto**: modelo + headline + tabla de specs (`10`).

## Piezas generadas

| # | Archivo | Concepto |
| --- | --- | --- |
| 01 | `output/01_hola_somos_genstone.jpg` | Hola. Somos Genstone. |
| 02 | `output/02_mantene_activa_tu_rutina.jpg` | Mantené activa tu rutina. |
| 03 | `output/03_24_7.jpg` | 24/7 monitoreo |
| 04 | `output/04_100_porciento.jpg` | 100% de autonomía |
| 05 | `output/05_mas_20.jpg` | +20 años de vida útil |
| 06 | `output/06_65db.jpg` | ≤65 dB(A) energía silenciosa |
| 07 | `output/07_promesa.jpg` | Lo que necesitás, sigue en marcha. |
| 08 | `output/08_estamos_cuando_hace_falta.jpg` | Estamos cuando hace falta. |
| 09 | `output/09_monitoreo_247.jpg` | Monitoreo 24/7 (foto celular) |
| 10 | `output/10_gs12.jpg` | GS12 — ficha técnica |

## Cómo generar

```bash
python3 generate.py
```

Pipeline: SVG → `rsvg-convert` → PNG 1080×1350 → `convert` → JPG sRGB calidad 92.

Para agregar piezas: editar `build_all()` en `generate.py`.
