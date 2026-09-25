"""
Avant d'appeler « défaut » ce qu'une vue de jugement montre, on mesure la
MÊME chose sur la référence, dans la MÊME caméra (ici la caméra de jeu de
dos du lecteur, recadrée).

1. Part du bras qui frappe HORS du tronc au moment d'extension max
   (test de silhouette de Disney). Résultat 2026-09-25 : caché aussi chez
   TSB, donc pas un défaut propre à la v7 (fausse alerte évitée).
2. Part de l'image du perso prise par le bras LIBRE.
3. Contraste de vitesse du poing : vitesse max à la frappe / vitesse max
   pendant la préparation (fenêtre f-18..f-5), en 3D et à l'écran
   (Williams : « the slow against the fast »).

Le fichier TSB (fourni par Milan) n'est jamais versionné : on passe son
chemin en argument ; seules les mesures dérivées sortent.
Usage : python3 regard_v7_vs_tsb.py <tsb_anim.rbxm> <sortie.json>
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "_shared"))
sys.path.insert(0, os.path.join(HERE, "..", "..", "_shared", "animator_brain", "outils"))
from animator_brain import corpus as C  # noqa: E402
from animator_brain import perception as P  # noqa: E402
import vues as V  # noqa: E402

AV = np.array([0, 0, -1.0])
BRAS = ("Right Arm", "Left Arm")


def cam(w, fov=24.0):
    a = w["Torso"][1]
    sx = 0.3 * a[0] + 1.75
    return (np.array([sx, max(4.5, a[1] + 1.8), a[2] + 10]), np.array([sx, a[1] + 0.2, a[2] - 4]), fov)


def bras_avant(w):
    return max(BRAS, key=lambda h: (P.tip(w, h) - w["Torso"][1]) @ AV)


def part_libre(w, h):
    libre = BRAS[1] if h == BRAS[0] else BRAS[0]
    tout = V._masque(w, tuple(V.M.SIZES), *cam(w), (480, 270)).sum()
    return float(V._masque(w, (libre,), *cam(w), (480, 270)).sum() / max(tout, 1))


def contraste(vit, f):
    fast = max(vit[max(0, f - 4):f + 2])
    lo = max(0, f - 18)
    prep = max(vit[lo:max(lo + 1, f - 5)])
    return round(fast / max(prep, 1e-3), 2)


def mesurer(w, f, h):
    v3 = [0.0] + [float(np.linalg.norm(P.tip(b, h) - P.tip(a, h))) for a, b in zip(w, w[1:])]
    ve = V.espacement(w, h, [cam(x, 70.0) for x in w])
    return {"frame": f, "bras": h, "hors_tronc": V.hors_silhouette(w[f], *cam(w[f]))[h],
            "part_bras_libre": round(part_libre(w[f], h), 2),
            "contraste_3d": contraste(v3, f), "contraste_ecran": contraste(ve, f)}


def main(tsb, out):
    res = {"tsb": {}, "v7": {}}
    for s in C.load_rbxm_sequences(tsb):
        w = [x[1] for x in C.resample_linear(s["frames"])]
        reach = [max((P.tip(x, h) - x["Torso"][1]) @ AV for h in BRAS) for x in w]
        f = int(np.argmax(reach))
        res["tsb"][s["name"]] = mesurer(w, f, bras_avant(w[f]))
    W = V.lire_kfseq(os.path.join(HERE, "..", "output", "dragon_attaquant.rbxmx"))
    for nom, f in (("h1", 14), ("h2", 40), ("h3", 64), ("h4", 90), ("coup_charge", 150)):
        res["v7"][nom] = mesurer(W, f, "Right Arm" if nom == "coup_charge" else bras_avant(W[f]))
    json.dump(res, open(out, "w"), indent=1, ensure_ascii=False)
    for g in res:
        for k, v in res[g].items():
            print(g, k, v)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
