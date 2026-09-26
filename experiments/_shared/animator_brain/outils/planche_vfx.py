"""
PLANCHE VFX : les moments où les EFFETS culminent dans une référence, vus
image par image à la cadence native.

`planche_ref.py` cherche les tenues et les pics de mouvement du CORPS. Ici,
on cherche ce que font les effets. Un VFX de combat se voit par :
- des pixels très clairs (additif, bloom, flash) ;
- des couleurs saturées (énergie) ;
- un changement brutal d'une image à l'autre (flash, carte, coupe).
Le score par image combine ces trois signaux. On garde les K moments les plus
forts, séparés d'au moins 0,5 s. Pour chacun, une rangée de 10 images
consécutives, de -2 à +7 autour du pic.

C'est une aide pour regarder, pas un critère : le score dit OÙ regarder, pas
si c'est bien.

Usage : python3 planche_vfx.py <video|gif> <sortie.png> [K=3] [largeur=240]
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from planche_ref import cadence_native, extraire  # noqa: E402


def scores(ims):
    out, prev = [], None
    for im in ims:
        a = np.asarray(im.resize((160, max(1, int(160 * im.size[1] / im.size[0])))), dtype=np.float32) / 255.0
        mx, mn = a.max(axis=2), a.min(axis=2)
        clair = float(np.mean(mx > 0.92))                      # part de pixels quasi blancs / saturés clairs
        sat = float(np.mean((mx - mn) * (mx > 0.5)))           # saturation des zones claires
        lum = a.mean(axis=2)
        saut = 0.0 if prev is None else float(np.mean(np.abs(lum - prev)))
        prev = lum
        out.append({"clair": clair, "sat": sat, "saut": saut})
    c = np.array([o["clair"] for o in out]); s = np.array([o["sat"] for o in out]); j = np.array([o["saut"] for o in out])
    z = lambda v: (v - np.median(v)) / (np.std(v) + 1e-6)  # noqa: E731
    return z(c) + z(s) + 1.5 * z(j), out


def moments(sc, fps, k=3, ecart_s=0.5):
    order = np.argsort(-sc)
    pris = []
    for i in order:
        if all(abs(i - p) >= ecart_s * fps for p in pris):
            pris.append(int(i))
        if len(pris) >= k:
            break
    return sorted(pris)


def main(src, sortie, k=3, largeur=240):
    fps = min(30.0, cadence_native(src))
    ims = extraire(src, fps=fps, largeur=largeur)
    sc, _raw = scores(ims)
    ms = moments(sc, fps, k)
    w, h = ims[0].size
    n = 10
    S = Image.new("RGB", (n * w, len(ms) * (h + 18)), (12, 12, 16))
    d = ImageDraw.Draw(S)
    for r, m in enumerate(ms):
        for c in range(n):
            i = m - 2 + c
            if 0 <= i < len(ims):
                S.paste(ims[i], (c * w, r * (h + 18) + 18))
                d.text((c * w + 3, r * (h + 18) + 3), f"{i / fps:.2f}s" + (" *" if i == m else ""), fill=(255, 220, 90))
    S.save(sortie)
    print(os.path.basename(src), f"{fps:.1f} i/s", len(ims), "images ; moments :", [round(m / fps, 2) for m in ms])
    return ms, fps


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 3,
         int(sys.argv[4]) if len(sys.argv) > 4 else 240)
