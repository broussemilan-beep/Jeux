#!/usr/bin/env python3
"""Phase R4 (retour croisé Gemini/ChatGPT, item 6 restant) : le sol de
gate_premiere/test_arena (assets/processed/sprites/world/
floor_terrain_atlas.png) est confirmé trop saturé/contrasté par capture
réelle (tools/capture_scene.tscn --mode=scene) — absorbe les VFX,
bruit visuel qui écrase la lisibilité du combat. Réduit UNIQUEMENT
saturation + contraste de valeur (HSV), jamais la teinte (§ Addendum C :
"chaud MAIS pas bruyant" — le choix de couleur reste correct, seule son
intensité est en cause). Alpha préservé intact (transparence du
TileSet). Déterministe, pas d'IA de vision, réversible (le PNG original
reste dans git history).
"""
from __future__ import annotations

import colorsys
import sys
from pathlib import Path

from PIL import Image

SATURATION_MULT = 0.62
VALUE_CONTRAST_MULT = 0.80  # resserre la valeur autour de son centre (moins de blancs/noirs extremes)
VALUE_CENTER = 0.55


def process(src: Path, dst: Path) -> None:
    img = Image.open(src).convert("RGBA")
    px = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            hh, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
            s *= SATURATION_MULT
            v = VALUE_CENTER + (v - VALUE_CENTER) * VALUE_CONTRAST_MULT
            v = max(0.0, min(1.0, v))
            s = max(0.0, min(1.0, s))
            nr, ng, nb = colorsys.hsv_to_rgb(hh, s, v)
            px[x, y] = (round(nr * 255), round(ng * 255), round(nb * 255), a)
    img.save(dst)


if __name__ == "__main__":
    src_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        "assets/processed/sprites/world/floor_terrain_atlas.png")
    dst_path = Path(sys.argv[2]) if len(sys.argv) > 2 else src_path
    process(src_path, dst_path)
    print(f"OK: {src_path} -> {dst_path}")
