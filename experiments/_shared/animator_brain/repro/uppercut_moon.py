"""
REPRODUCTION du tuto « How to animate R6 SMOOTHLY » (uppercut, Moon Animator),
en suivant SA méthode, dans l'ordre où il la montre
(corpus/tutos/etude_complete_uppercut_moon.md) :

  passe 1 : le TORSE seul porte tout le mouvement (départ, anticipation, drag,
            milieu, exagération, plus d'exagération, wiggle) ; on la rejoue
            seule pour vérifier qu'elle se lit (le tuto le montre à 256 s) ;
  passe 2 : bras gauche (peu de mouvement : il suit le torse) ;
  passe 3 : bras droit (l'uppercut) : les MÊMES rôles, avec un drag de bras
            « disloqué » (traîne derrière, translaté) ;
  passe 4 : tête : garde le regard de la 1re image (contre-rotation), exagère
            au milieu, puis suit le torse ;
  passe 5 : jambes en dernier : pieds plantés à leur place de départ.

Clés tous les 5 frames à 60 i/s en Linear, astuce 2 du tuto : la clé du
milieu rapprochée du drag (10 -> 12). Sortie : une image par passe + la vidéo.
Usage : python3 uppercut_moon.py <dossier_sortie>
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "outils"))
import moon as M  # noqa: E402

FOOT_R, FOOT_L = (1.0, 0.0, 1.35), (-0.7, 0.0, -1.6)   # pieds plantés (écartés, pied gauche devant)
LOOK = np.array([0.0, 3.4, -6.0])                          # la cible (regard de départ)

# ---- passe 1 : le torse (hauteur du centre, lacet, tangage, roulis)
TORSO = [  # (frame, rôle, y, yaw, pitch, roll) -- 3e passe : le tuto filme le perso de PROFIL au départ
    (0, "départ", 2.30, 10, -20, 0),            # de profil vers la cible, ramassé, bras rentrés
    (5, "anticipation", 2.10, 35, -28, -6),     # s'enroule loin du coup (épaule droite en arrière)
    (10, "drag", 2.20, 0, -14, 4),              # se déroule, le bras traîne
    (12, "milieu", 2.15, -55, -2, 18),          # le torse s'ouvre VERS la caméra, bras vertical
    (15, "exagération", 2.05, -68, 4, 24),      # dépasse
    (20, "plus d'exagération", 2.00, -60, 0, 20),  # se pose bas, fente avant/arrière
]
HOLD_END = 60


def torso_pose(y, yaw, pitch, roll):
    p = M.neutral(y)
    p["root"] = (np.array([0.0, y, 0.0]), M.E(yaw, pitch, roll))
    return p


def arm_rel(p, d_world, trans_world=(0, 0, 0)):
    rt = p["root"][1]
    return (rt.T @ M.aim(d_world), rt.T @ np.asarray(trans_world, float))


def build(passes=5):
    keys = []
    for f, role, y, yaw, pitch, roll in TORSO:
        p = torso_pose(y, yaw, pitch, roll)
        rt = p["root"][1]
        if passes >= 2:   # bras gauche : relâché, suit le torse, s'ouvre au coup
            d = {"départ": (0.1, -0.5, -0.85), "anticipation": (0.2, -0.6, -0.75), "drag": (-0.4, -0.8, -0.4),
                 "milieu": (0.35, -0.9, 0.35), "exagération": (0.4, -0.85, 0.35), "plus d'exagération": (0.35, -0.9, 0.3)}[role]
            p["Left Arm"] = arm_rel(p, d)
        if passes >= 3:   # bras droit : garde basse -> armé bas derrière -> drag disloqué -> vertical
            d, tr = {"départ": ((-0.1, -0.5, -0.85), (0, 0, 0)),
                     "anticipation": ((0.4, -0.85, 0.35), (0, -0.1, 0.1)),
                     "drag": ((0.25, -0.9, 0.45), (0, -0.3, 0.25)),        # « may look dislocated »
                     "milieu": ((0.1, 1.0, 0.0), (0, 0.25, 0)),
                     "exagération": ((0.0, 1.0, 0.05), (0, 0.35, 0)),
                     "plus d'exagération": ((0.05, 1.0, 0.0), (0, 0.3, 0))}[role]
            p["Right Arm"] = arm_rel(p, d, tr)
        else:
            p["Right Arm"] = arm_rel(p, (0.3, -0.7, -0.6)) if passes >= 2 else p["Right Arm"]
        if passes >= 4:   # tête : regard fixé sur la cible jusqu'au drag, puis exagère avec le torse
            head = p["Torso"] if False else None
            w = M.world(p)
            if True:   # 3e passe : dans la vidéo, la tête garde le regard sur la cible du début à la fin
                fwd = LOOK - w["Head"][1]
                Rw = M.aim(-fwd)                      # -Y local vers l'arrière => regard (-Z) vers la cible
                Rw = M._align(np.array([0, 0, -1.0]), fwd)
                p["Head"] = (rt.T @ Rw, np.zeros(3))
            else:
                p["Head"] = (M.E(0, -8 if role == "milieu" else -4, 8), np.zeros(3))
        if passes >= 5:
            M.plant(p, "Right Leg", FOOT_R)
            M.plant(p, "Left Leg", FOOT_L)
        keys.append((f, p))
    # wiggle : petits cercles qui ralentissent, sur la dernière pose (clés tous les 5)
    last = keys[-1][1]
    for f in range(25, HOLD_END + 1, 5):
        p = M.wiggle(last, "root", f - 20, amp_deg=2.5, period=10, decay=14)
        p = M.wiggle(p, "Right Arm", f - 20, amp_deg=4.0, period=10, decay=14)
        if passes >= 5:
            M.plant(p, "Right Leg", FOOT_R); M.plant(p, "Left Leg", FOOT_L)
        keys.append((f, p))
    return keys


CAM = dict(eye=(8.5, 4.6, -3.5), target=(0.0, 2.0, 0.0), fov=40)   # 3/4 avant-gauche en hauteur, comme le tuto


def main(out):
    os.makedirs(out, exist_ok=True)
    from PIL import Image
    tiles = []
    for n, name in ((1, "passe 1 : torse seul"), (3, "passes 2-3 : + bras"), (5, "passes 4-5 : + tete, pieds")):
        keys = build(n)
        frames = M.sample(keys, HOLD_END + 1)
        for f in (0, 5, 10, 12, 15, 20, 40):
            tiles.append(M.render([M.world(frames[f])], title=f"{name} f{f}", size=(320, 240), **CAM))
    W, H = tiles[0].size
    S = Image.new("RGB", (W * 7, H * 3))
    for i, t in enumerate(tiles):
        S.paste(t, ((i % 7) * W, (i // 7) * H))
    S.save(os.path.join(out, "uppercut_passes.png"))
    frames = M.sample(build(5), HOLD_END + 1)
    fd = os.path.join(out, "frames"); os.makedirs(fd, exist_ok=True)
    for i in range(20):       # 20 frames de pose de départ tenue, comme la boucle du tuto
        M.render([M.world(frames[0])], **CAM).save(os.path.join(fd, f"f{i:04d}.png"))
    for i, fr in enumerate(frames):
        M.render([M.world(fr)], **CAM).save(os.path.join(fd, f"f{i + 20:04d}.png"))
    M.video(fd, os.path.join(out, "uppercut_repro.mp4"))
    return frames


if __name__ == "__main__":
    main(sys.argv[1])
