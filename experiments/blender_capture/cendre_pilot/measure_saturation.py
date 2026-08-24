#!/usr/bin/env python3
"""Point de vigilance identite (MANDAT MIGRATION CENDRE) : mesure
objective de saturation, pas une affirmation visuelle. Compare la
saturation moyenne (HSV, pixels non-transparents) du rendu Meshy brut,
du rendu quantifie (target_saturation=0.10 applique par quantize.py) et
des frames PixelLab existantes de Cendre, pour verifier honnetement que
la migration ne recolore pas le personnage."""
import sys
import numpy as np
from PIL import Image


def mean_saturation(path):
    im = Image.open(path).convert("RGBA")
    arr = np.asarray(im).astype(np.float32) / 255.0
    rgb = arr[..., :3]
    alpha = arr[..., 3]
    mask = alpha > 0.1
    if mask.sum() == 0:
        return None, 0
    maxc = rgb.max(axis=-1)
    minc = rgb.min(axis=-1)
    sat = np.where(maxc > 1e-6, (maxc - minc) / np.maximum(maxc, 1e-6), 0.0)
    return float(sat[mask].mean()), int(mask.sum())


if __name__ == "__main__":
    for p in sys.argv[1:]:
        s, n = mean_saturation(p)
        print(f"{p}\tmean_saturation={s:.4f}\tnonzero_alpha_px={n}" if s is not None else f"{p}\tEMPTY")
