#!/usr/bin/env python3
"""Phase 2.2 (MANDAT SUITE v2) : downscale d'une passe Normal brute vers
la meme grille 64x64 que le diffuse deja quantifie par quantize.py -
reutilise LA MEME fonction `pixelate_block_center` (echantillonnage du
CENTRE de bloc, pas une moyenne) pour garantir un alignement pixel-a-
pixel exact entre normal_texture et diffuse_texture (CanvasTexture,
Godot) : les deux images source partagent la meme resolution/cadrage
camera, donc les memes coordonnees de bloc tombent sur le meme texel
des deux cotes.

AUCUNE des etapes de quantize.py (HSV/palette/dithering/contour) ne
s'applique ici - ce sont des transformations de COULEUR, un normal map
encode des vecteurs, les deformer casserait l'eclairage. Seul le
point-sampling geometrique est reutilise.
"""

import argparse
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from quantize import pixelate_block_center


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--in", dest="in_path", required=True)
    p.add_argument("--out", dest="out_path", required=True)
    p.add_argument("--target_pixels", type=int, default=64)
    args = p.parse_args()

    im = Image.open(args.in_path).convert("RGBA")
    arr = np.array(im)
    rgb = arr[..., :3]
    alpha = arr[..., 3]

    rgb_block = pixelate_block_center(rgb, args.target_pixels)
    alpha_block = pixelate_block_center(alpha[..., None], args.target_pixels)[..., 0]

    out = np.dstack([rgb_block, alpha_block]).astype(np.uint8)
    Image.fromarray(out, "RGBA").save(args.out_path)
    print("NORMAL_QUANTIZE_RESULT", "out=" + args.out_path, "size=" + str(out.shape[:2]))


if __name__ == "__main__":
    main()
