"""
Trajectoire du poing vue de profil, dans le repere du torse (avant = droite,
hauteur relative au pivot d'epaule), sur les 0,27 s qui precedent le contact :
M1 du pack pro contre nos coups. Sert de preuve a LECONS.md 11.

Usage : python3 fist_path.py <pack.rbxm> <sortie.png> [etiquette]
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "_shared"))
sys.path.insert(0, HERE)
from animator_brain import corpus as C  # noqa: E402
import staging as ST  # noqa: E402


def tip(w, p):
    r, c = w[p]
    return c + r @ np.array([0, -1.0, 0])


def pivot(w, hand):
    r, p = w["Torso"]
    return p + r @ np.array([1.0 if hand == "Right Arm" else -1.0, 0.5, 0])


def path(frames, ci, hand, n=16):
    """(avant, hauteur) du poing relatifs au pivot d'epaule du CONTACT."""
    w0 = frames[ci][1]
    pv = pivot(w0, hand)
    return [(-(tip(frames[i][1], hand)[2] - pv[2]), tip(frames[i][1], hand)[1] - pv[1])
            for i in range(max(0, ci - n), ci + 1)]


def main(pack, out, tag=""):
    curves = []
    for s in C.load_rbxm_sequences(pack):
        if s["name"].endswith(("M1_1", "M1_2", "M1_4")):
            wf = C.resolve_world(s["frames"])
            best = min(((tip(w, h)[2], i, h) for i, (_t, w) in enumerate(wf) for h in ("Right Arm", "Left Arm")))
            curves.append(("PRO " + s["name"].split()[-1], path(wf, best[1], best[2]), (40, 140, 60)))
    aw, _vw = ST.tracks()
    sc = json.load(open(os.path.join(HERE, "..", "output", "scene.json")))
    fr = [(f / 60, aw[f]) for f in range(len(aw))]
    for c, side, kind in sc["hits"]:
        curves.append((f"NOUS {tag} f{c} {kind}", path(fr, c, "Right Arm" if side == "R" else "Left Arm"), (200, 60, 40)))
    PW, PH, S = 330, 300, 60
    img = Image.new("RGB", (PW * len(curves), PH + 40), "white")
    for k, (name, pts, col) in enumerate(curves):
        d = ImageDraw.Draw(img)
        ox = k * PW
        X = lambda u, v: (ox + 100 + u * S, 150 - v * S)  # noqa: E731
        d.line([X(-1.5, 0), X(3.8, 0)], fill=(170, 170, 170))          # hauteur d'epaule
        d.ellipse([X(0, 0)[0] - 5, X(0, 0)[1] - 5, X(0, 0)[0] + 5, X(0, 0)[1] + 5], fill=(0, 0, 0))
        d.text((X(-1.5, 0)[0], X(-1.5, 0)[1] - 13), "epaule", fill=(120, 120, 120))
        for i, (u, v) in enumerate(pts):
            p = X(u, v)
            r = 3 if i < len(pts) - 1 else 7
            d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=col)
            if i:
                d.line([X(*pts[i - 1]), p], fill=col, width=2)
        a = X(*pts[0])
        d.text((a[0] + 5, a[1] - 5), "depart", fill=col)
        d.text((ox + 8, 8), name, fill=(0, 0, 0))
        rise = pts[-1][1] - min(v for _u, v in pts[-7:])
        d.text((ox + 8, 24), f"depart {pts[0][1]:+.2f} / epaule ; montee sur 6 f : {rise:.2f}", fill=(0, 0, 0))
    ImageDraw.Draw(img).text((8, PH + 16), "Poing vu de profil, 16 f avant le contact (gros point), repere du torse : "
                             "avant = droite, trait gris = hauteur d'epaule.", fill=(0, 0, 0))
    img.save(out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "")
