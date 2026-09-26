"""
REPRODUCTION du tuto « Punch tut » (Blender, add-on Rbx Animations) avec SA
timeline finale (corpus/tutos/etude_complete_punch_blender.md) :
clés 0, 20, 30, 60, 61, 62, 63, 66, 90 à 60 i/s.
  0-30 garde -> charge en « K » ; 30-60 charge TENUE (bouge à peine) ;
  60-62 la frappe en 2 f (61 = clé intermédiaire sur le seul bras) ;
  63-66 retrait du bras ; 66-90 pose d'APRÈS tenue : corps plié, couché
  en avant, dos à la caméra. Frappe du bras GAUCHE (comme dans la vidéo).
Usage : python3 punch_blender.py <dossier_sortie>
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "outils"))
import moon as M  # noqa: E402

TARGET = np.array([0.0, 3.2, -4.0])


def pose(y, yaw, pitch, roll, strike, free, feet, head_follow=False, strike_tr=(0, 0, 0)):
    p = M.neutral(y)
    p["root"] = (np.array([0.0, y, 0.0]), M.E(yaw, pitch, roll))
    rt = p["root"][1]
    p["Left Arm"] = (rt.T @ M.aim(strike), rt.T @ np.asarray(strike_tr, float))
    p["Right Arm"] = (rt.T @ M.aim(free), np.zeros(3))
    w = M.world(p)
    fwd = TARGET - w["Head"][1]
    Rw = M._align(np.array([0, 0, -1.0]), fwd)
    p["Head"] = (rt.T @ Rw if not head_follow else M.E(0, -10, 0), np.zeros(3))
    M.plant(p, "Left Leg", feet[0]); M.plant(p, "Right Leg", feet[1])
    return p


FEET = ((-0.6, 0.0, -1.5), (0.8, 0.0, 2.3))     # grand écart avant/arrière, planté tout du long
# 2e passe (comparée à la vidéo) : tout est plus BAS et plus COMPACT que notre 1er essai ;
# la jambe arrière finit presque couchée.
KEYS = [
    (0, pose(2.70, 0, -6, 0, (-0.2, -0.8, -0.5), (0.2, -0.8, -0.5), ((-0.6, 0, -0.9), (0.6, 0, 0.9)))),
    (20, pose(2.20, 45, -16, 0, (-0.3, -0.6, 0.7), (0.2, -0.5, -0.8), FEET)),
    (30, pose(1.95, 88, -26, -6, (-0.15, -0.35, 0.95), (0.1, -0.55, -0.85), FEET)),   # CHARGE compacte, détournée
    (60, pose(1.90, 94, -28, -8, (-0.15, -0.3, 0.95), (0.1, -0.55, -0.85), FEET)),    # tenue « vivante »
    (61, pose(1.70, 20, -40, 0, (-0.6, 0.0, -0.4), (0.3, 0.3, 0.9), FEET)),           # clé intermédiaire
    (62, pose(1.45, -85, -55, 0, (0.0, -0.05, -1.0), (0.5, 0.8, 0.2), FEET, strike_tr=(0, 0, -0.6))),  # CONTACT
    (63, pose(1.40, -90, -56, 0, (0.0, 0.3, -0.9), (0.5, 0.8, 0.2), FEET, strike_tr=(0, 0, -0.3))),
    (66, pose(1.35, -95, -55, 0, (-0.2, 0.9, 0.2), (0.4, 0.7, 0.3), FEET, head_follow=True)),  # retrait
    (90, pose(1.40, -92, -52, 0, (-0.2, 0.9, 0.25), (0.4, 0.6, 0.35), FEET, head_follow=True)),  # APRÈS, tenue
]
CAM = dict(eye=(-7.0, 4.2, -2.5), target=(0.0, 1.6, 0.0), fov=40)   # de côté, comme la boucle finale de la vidéo


def main(out):
    from PIL import Image
    os.makedirs(out, exist_ok=True)
    frames = M.sample(KEYS, 91)
    fd = os.path.join(out, "frames"); os.makedirs(fd, exist_ok=True)
    for i, fr in enumerate(frames):
        M.render([M.world(fr)], **CAM).save(os.path.join(fd, f"f{i:04d}.png"))
    M.video(fd, os.path.join(out, "punch_repro.mp4"))
    tiles = [M.render([M.world(frames[f])], title=f"f{f}", size=(320, 240), **CAM) for f in (0, 20, 30, 45, 60, 61, 62, 63, 66, 90)]
    S = Image.new("RGB", (320 * 5, 240 * 2))
    for i, t in enumerate(tiles):
        S.paste(t, ((i % 5) * 320, (i // 5) * 240))
    S.save(os.path.join(out, "punch_keys.png"))


if __name__ == "__main__":
    main(sys.argv[1])
