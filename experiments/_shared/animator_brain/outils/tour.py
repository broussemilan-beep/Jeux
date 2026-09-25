"""
TOUR d'une pose : la même image vue de 8 caméras tout autour (tous les 45°).

Appris sur le coup final aérien v9 (CARNET §3.8). La 1re pose d'armé était
un tas illisible, et je changeais de caméra au hasard. Le tour montre en
une seule planche depuis où la silhouette est OUVERTE. On choisit alors la
caméra d'après la pose (une pose n'existe que depuis sa caméra, repro
leçon 2), ou on refait la pose.
C'est une aide pour regarder : aucun critère, aucun seuil.

Usage :
  python3 tour.py <dossier_sortie_production> <frame> <sortie.png> [distance]
  (lit dragon_attaquant.rbxmx / dragon_victime.rbxmx du dossier ; az 0 = côté victime, -Z)
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import moon as M  # noqa: E402
import vues as VU  # noqa: E402


def tour(w, autres, dist=9.0, taille=(360, 300)):
    c = w["Torso"][1]
    ims = []
    for az in range(0, 360, 45):
        a = np.radians(az)
        eye = c + np.array([np.sin(a) * dist, -1.5, -np.cos(a) * dist])
        ims.append(M.render([w] + autres, eye=eye, target=c + np.array([0, -0.8, 0]), fov=45, size=taille,
                            ground=False, title=f"az {az}"))
    S = Image.new("RGB", (4 * taille[0], 2 * taille[1]))
    for i, im in enumerate(ims):
        S.paste(im, ((i % 4) * taille[0], (i // 4) * taille[1]))
    return S


def main(d, f, out, dist=9.0):
    A = VU.lire_kfseq(os.path.join(d, "dragon_attaquant.rbxmx"))
    V = VU.lire_kfseq(os.path.join(d, "dragon_victime.rbxmx"),
                      root=(np.diag([-1.0, 1.0, -1.0]), np.array([0.0, 3.0, -3.3])))
    tour(A[f], [V[f]], dist).save(out)


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]), sys.argv[3], float(sys.argv[4]) if len(sys.argv) > 4 else 9.0)
