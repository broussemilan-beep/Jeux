"""
Planches d'ETUDE (cerveau v2) : pour qu'un animateur -- moi -- regarde
vraiment les references, image par image, autour des moments qui comptent.

Pour chaque clip : jusqu'a 3 moments (salves de cartes d'impact d'abord,
puis pics d'energie separes d'au moins 1 s). Pour chaque moment, une rangee
de 12 images de -0,5 s a +0,23 s (pas de 3 f a 60 i/s), etiquetees par leur
decalage en frames. Les planches restent LOCALES (images d'oeuvres
protegees : jamais versionnees) ; ce qui est versionne, c'est ce que j'en
tire (corpus/ETUDE_VISUELLE.md).

Usage : python3 planches_etude.py <video> <sortie.png> [--titre ...]
"""
import argparse
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import clip_analyzer as CA  # noqa: E402

OFFS = list(range(-30, 15, 4))       # 12 images : -30 .. +14 f (60 i/s)
TW = 170


def moments(path, k=3):
    w, h, dur = CA._probe(path)
    rgb = CA._decode(path, w, h, CA.GRAY_W)
    g = rgb.mean(axis=3).astype(np.float32)
    white = (g > 235).mean(axis=(1, 2))
    dark = (g < 40).mean(axis=(1, 2))
    card = (white > 0.85) | ((dark > 0.5) & (white > 0.05)) | (dark > 0.9)
    diff = np.r_[0.0, np.abs(np.diff(g, axis=0)).mean(axis=(1, 2))]
    diff[card] = 0
    out = []
    # 1. salves de cartes
    i = 0
    while i < len(card):
        if card[i]:
            out.append(i)
            i += 30
        else:
            i += 1
    # 2. pics d'energie
    e = np.convolve(diff, np.ones(6) / 6, mode="same")
    for j in np.argsort(-e):
        if len(out) >= k:
            break
        if all(abs(j - m) > 60 for m in out) and 30 <= j < len(e) - 15:
            out.append(int(j))
    return sorted(out[:k]), len(g), dur


def frame_at(path, t, w=TW):
    r = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", f"{max(0.0, t):.4f}", "-i", path, "-frames:v", "1",
                        "-vf", f"scale={w}:-2", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True)
    from io import BytesIO
    return Image.open(BytesIO(r.stdout)).convert("RGB") if r.stdout else None


def planche(path, out, titre=""):
    ms, n, dur = moments(path)
    rows = []
    for m in ms:
        ims = [frame_at(path, (m + o) / 60.0) for o in OFFS]
        ims = [im for im in ims if im is not None]
        if ims:
            rows.append((m, ims))
    if not rows:
        return None
    th = max(im.height for _m, ims in rows for im in ims)
    S = Image.new("RGB", (TW * len(OFFS), 16 + len(rows) * (th + 14)), "black")
    d = ImageDraw.Draw(S)
    d.text((4, 2), f"{titre}  ({dur:.1f} s)  -- decalage en frames a 60 i/s autour de chaque moment", fill=(255, 220, 0))
    for r, (m, ims) in enumerate(rows):
        y = 16 + r * (th + 14)
        for c, im in enumerate(ims):
            S.paste(im, (c * TW, y + 12))
            d.text((c * TW + 3, y), f"{'t=' + format(m / 60, '.2f') + 's ' if c == 0 else ''}{OFFS[c]:+d}",
                   fill=(255, 255, 255) if OFFS[c] != -2 else (255, 80, 80))
    S.save(out)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("out")
    ap.add_argument("--titre", default="")
    a = ap.parse_args()
    print(planche(a.video, a.out, a.titre))
