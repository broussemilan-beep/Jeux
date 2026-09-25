"""
CORPS ou BRAS : qui porte le mouvement ? Outil de VIGILANCE, à lancer sur
chaque production avant de la montrer.

Retour de Milan sur la v9 (7,7) : « tu as animé que les bras encore une
fois ; tu as manqué de vigilance ». Mesuré sur l'aérien v9 :
- torse figé 24/24 images pendant le calme ;
- torse figé 16/32 images pendant l'armé (la « tenue vivante » ne bougeait
  que le poing) ;
- torse figé 15/22 images pendant la frappe (corps translaté d'un bloc,
  seul le bras agit : bras droit 470° contre torse 116°).
En v8, le torse bougeait sur chaque image de la frappe.

Ce que l'outil sort, par phase : rotation cumulée du torse (monde), des bras,
des jambes et de la tête (par rapport au torse), et le nombre d'images où le
torse est quasi figé (< 0,3°/image).
Ce n'est pas un critère. Un torse figé peut être voulu (une vraie tenue,
un calme). Mais s'il est figé alors que les bras bougent, il faut aller
REGARDER : c'est le signe du « perso qui n'anime que ses bras » (CARNET §2.1d,
repro leçon 3 « corps d'abord »).

Usage : python3 corps_bras.py <attaquant.rbxmx> nom:f0:f1 [nom:f0:f1 ...]
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vues as VU  # noqa: E402


def ang(ra, rb):
    c = (np.trace(ra.T @ rb) - 1) / 2
    return float(np.degrees(np.arccos(np.clip(c, -1, 1))))


def rel(w, part):
    return w["Torso"][0].T @ w[part][0]


def phase(W, a, b, seuil=0.3):
    out = {"images": b - a, "torse": 0.0, "bras_D": 0.0, "bras_G": 0.0, "jambes": 0.0, "tete": 0.0, "torse_fige": 0}
    for f in range(a, b):
        t = ang(W[f]["Torso"][0], W[f + 1]["Torso"][0])
        out["torse"] += t
        out["torse_fige"] += t < seuil
        out["bras_D"] += ang(rel(W[f], "Right Arm"), rel(W[f + 1], "Right Arm"))
        out["bras_G"] += ang(rel(W[f], "Left Arm"), rel(W[f + 1], "Left Arm"))
        out["jambes"] += sum(ang(rel(W[f], p), rel(W[f + 1], p)) for p in ("Left Leg", "Right Leg"))
        out["tete"] += ang(rel(W[f], "Head"), rel(W[f + 1], "Head"))
    return out


def main(path, specs):
    W = VU.lire_kfseq(path)
    for s in specs:
        nom, a, b = s.split(":")
        r = phase(W, int(a), int(b))
        alerte = "  <- torse figé pendant que les bras bougent : REGARDER" if (
            r["torse_fige"] > 0.4 * r["images"] and r["bras_D"] + r["bras_G"] > 3 * r["torse"] + 20) else ""
        print(f"{nom:10s} {r['images']:3d} f | torse {r['torse']:5.0f}° (figé {r['torse_fige']}/{r['images']}) | "
              f"bras D {r['bras_D']:5.0f}° G {r['bras_G']:5.0f}° | jambes {r['jambes']:5.0f}° | tête {r['tete']:4.0f}°{alerte}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
