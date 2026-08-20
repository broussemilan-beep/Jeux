#!/usr/bin/env python3
"""Bake-off Animation, Voie C — downscale NEAREST du rendu brut (haute
résolution interne, déjà pixelisé par blocs par pixel_quantize.gdshader)
vers le canevas de jeu réel (64x64, mêmes conventions que
assets/manifests/cendre_frames_cooked.json — out_canvas [64,64]).

Le shader bloque déjà l'UV en paquets de exactement internal_res/64
pixels identiques (target_x/y_pixel_count=64) : un simple NEAREST à ce
facteur EXACT reproduit 1 pixel de sortie par bloc, sans aucun
lissage/moyenne — downscale "gratuit", pas une approximation.

Usage :
    python3 postprocess.py --in out/voie_c_idle_raw.png --out out/voie_c_idle_64.png --canvas 64
"""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--in", dest="in_path", type=Path, required=True)
    p.add_argument("--out", dest="out_path", type=Path, required=True)
    p.add_argument("--canvas", type=int, default=64)
    args = p.parse_args()

    img = Image.open(args.in_path).convert("RGBA")
    if img.width % args.canvas != 0 or img.height % args.canvas != 0:
        raise SystemExit(
            f"résolution brute {img.size} pas un multiple exact de --canvas {args.canvas} "
            "— le blocage du shader (target_x/y_pixel_count) ne correspond plus à ce canevas."
        )
    out = img.resize((args.canvas, args.canvas), Image.NEAREST)
    args.out_path.parent.mkdir(parents=True, exist_ok=True)
    out.save(args.out_path)
    print(f"OK — {args.in_path} ({img.size}) -> {args.out_path} ({out.size})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
