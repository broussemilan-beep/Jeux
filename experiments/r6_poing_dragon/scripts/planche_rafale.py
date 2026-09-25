"""
Planche des POSES de la rafale (attaquant + victime), lues dans les
KeyframeSequences exportées : pour chaque coup, armé / départ / contact /
extension / retour, sous 3 vues (3/4 avant, profil, caméra de jeu).
Sert à juger les poses et le placement à l'œil (CARNET §1.5, §1.7), pas
seulement le timing.

Usage : python3 planche_rafale.py <dossier_output> <sortie.png> [titre]
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "_shared", "animator_brain", "outils"))
import moon as M  # noqa: E402
import vues as V  # noqa: E402

TENUE = {"Torso": (28, 28, 30), "Head": (234, 184, 146), "Right Arm": (234, 184, 146),
         "Left Arm": (234, 184, 146), "Right Leg": (58, 58, 62), "Left Leg": (58, 58, 62)}
VICT = {"Torso": (245, 205, 40), "Head": (245, 205, 40), "Right Arm": (245, 205, 40),
        "Left Arm": (245, 205, 40), "Right Leg": (60, 150, 70), "Left Leg": (60, 150, 70)}
S = (300, 220)


def charger(out):
    sc = json.load(open(os.path.join(out, "scene.json")))
    d = sc["distance"]
    A = V.lire_kfseq(os.path.join(out, "dragon_attaquant.rbxmx"))
    B = V.lire_kfseq(os.path.join(out, "dragon_victime.rbxmx"), root=(M.Ry(180), np.array([0.0, 3.0, -d])))
    return sc, A, B


def rendu2(wa, wb, eye, tgt, fov, titre):
    # couleurs distinctes : on préfixe les parts de la victime
    ww = {("V_" + k): v for k, v in wb.items()}
    col = dict(TENUE)
    col.update({("V_" + k): v for k, v in VICT.items()})
    sizes = dict(M.SIZES)
    M.SIZES.update({("V_" + k): v for k, v in sizes.items()})
    try:
        return M.render([wa, ww], eye, tgt, fov, S, title=titre, sky=(236, 238, 242), couleurs=col)
    finally:
        for k in list(M.SIZES):
            if k.startswith("V_"):
                del M.SIZES[k]


def main(out, sortie, titre=""):
    sc, A, B = charger(out)
    hits = [h[0] for h in sc["hits"]][:4]
    moments = [("arme", -7), ("depart", -3), ("contact", 0), ("ext", 5), ("retour", 10)]
    rows = []
    for c in hits:
        tiles = []
        for nom, df in moments:
            f = c + df
            wa, wb = A[f], B[f]
            mid = 0.5 * (wa["Torso"][1] + wb["Torso"][1])
            v34 = rendu2(wa, wb, mid + np.array([6.5, 2.2, 4.5]), mid + np.array([0, -0.4, 0]), 42, f"h f{c}{df:+d} {nom} 3/4")
            prof = rendu2(wa, wb, mid + np.array([9.5, 0.8, 0]), mid + np.array([0, -0.4, 0]), 38, "profil")
            a = wa["Torso"][1]; sx = 0.3 * a[0] + 1.75
            jeu = rendu2(wa, wb, np.array([sx, max(4.5, a[1] + 1.8), a[2] + 10]), np.array([sx, a[1] + 0.2, a[2] - 4]), 34, "jeu (serre)")
            t = Image.new("RGB", (S[0], S[1] * 3), "white")
            t.paste(v34, (0, 0)); t.paste(prof, (0, S[1])); t.paste(jeu, (0, 2 * S[1]))
            tiles.append(t)
        row = Image.new("RGB", (S[0] * len(tiles), S[1] * 3), "white")
        for k, t in enumerate(tiles):
            row.paste(t, (k * S[0], 0))
        rows.append(row)
    P = Image.new("RGB", (rows[0].size[0], sum(r.size[1] for r in rows) + 20), "white")
    ImageDraw.Draw(P).text((4, 4), titre, fill=(0, 0, 0))
    y = 20
    for r in rows:
        P.paste(r, (0, y)); y += r.size[1]
    P.save(sortie)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "")
