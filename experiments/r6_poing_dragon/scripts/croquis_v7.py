"""
Croquis v7 du coup chargé, révisés après l'étude des tutos vidéo (2026-09-24).
On dessine les poses clés au labo de poses R6 (blocs rigides) AVANT de les
animer dans le rig V2.22, et on les compare à la v6 sur les mêmes vues.

- charge : torse détourné ~85° de la cible, poing armé HAUT derrière
  l'épaule, bras avant qui vise, genou levé. C'est la pose ✓ « Serious
  Punch » de la planche de Xoaterz, et la charge du tuto punch. C'est
  l'opposé de la croix ✗ de face de la v6.
- contact E : lacet +70° (soit ~155° de rotation depuis la charge), penché
  de 40° vers la cible, bras horizontal, bras libre ramené à la hanche,
  jambe arrière dans l'axe du torse, qui traîne en l'air : une ligne
  « jetée ».
- contact G : version plus sage (lacet 55°, penché de 35°).

Contrainte R6 trouvée en croquant : le torse R6 est aussi le bassin. Un
torse de profil penché vers la cible fait donc basculer la ligne des
hanches. Au-delà de ~30°, les deux pieds ne peuvent plus rester au sol
sans un grand écart, avec la jambe avant à l'horizontale (on dirait alors
un perso assis). La ligne jetée se fait donc pied arrière en l'air, comme
une fente lancée : c'est l'idiome anime (ligne hors d'équilibre), pas un
défaut. On vérifiera dans le rig V2.22 (jambes en IK) avant d'animer.

Usage : python3 croquis_v7.py sortie.png
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "_shared"))
sys.path.insert(0, os.path.join(HERE, "..", "..", "_shared", "animator_brain", "outils"))
import draw as D  # noqa: E402
import poselab as L  # noqa: E402
from animator_brain import perception as P  # noqa: E402

Ry, Rx, aim = L.Ry, L.Rx, L.aim


def leg(a, back=False, x=0.05):
    a = np.radians(a)
    return aim((x, -np.cos(a), (1 if back else -1) * np.sin(a)))


def charge():
    # rotations MONDE : lacet puis tangage vers la cible (-Z) => Rx(-a) @ Ry(lacet)
    # bascule 25° + bras avant replié bas et vers l'intérieur : silhouette compacte.
    # Avec 12° et un bras avant tendu, le croquis ne sortait de la « croix » que
    # de justesse (seuil de bascule : 10°).
    return L.pose(Rx(-25) @ Ry(-85), Rx(-15) @ Ry(-35),
                  aim((0.25, 0.55, 0.8)),     # poing armé haut derrière l'épaule
                  aim((-0.35, -0.55, -0.75)), # bras avant replié, qui vise bas
                  aim((0.05, -1, 0.1)),       # jambe d'appui verticale
                  aim((-0.1, -0.45, -0.9)))   # genou levé vers la cible


def contact(lacet, pench, phi):
    te = Rx(-pench) @ Ry(lacet)
    up = te @ np.array([0, 1.0, 0])
    return L.pose(te, Rx(-pench + 8) @ Ry(lacet * 0.6),
                  aim((0, -0.02, -1)),                              # bras de frappe horizontal
                  aim((0.3, -0.5, 0.8)),                            # bras libre ramené à la hanche
                  leg(phi),                                         # jambe avant
                  aim(-up + np.array([-0.05, -0.15, 0])))           # jambe arrière dans l'axe du torse


def main(out):
    w = P.load_production(os.path.join(HERE, "..", "output", "dragon_attaquant.rbxmx"))
    cols = [("v6 charge f140", w[140]), ("v6 contact f150", w[150]), ("v7 charge", charge()),
            ("v7 contact E (ligne jetee)", contact(70, 40, 25)), ("v7 contact G (sage)", contact(55, 35, 20))]
    rows = [[D.draw(v, vw, title=f"{t} - {vw}") for t, v in cols] for vw in ("profil", "face34", "jeu")]
    D.sheet(rows, out)


if __name__ == "__main__":
    main(sys.argv[1])
