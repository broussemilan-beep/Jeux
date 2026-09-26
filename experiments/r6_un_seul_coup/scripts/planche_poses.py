"""
Planche des poses clés (revue avant tout le reste) : chaque clé vue de
profil (côté +x) et de 3/4 face, les deux persos, sol visible.
Usage : python3 planche_poses.py <blend> <sortie.png> [frames...]
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "_shared", "animator_brain", "outils"))
import coup_clip as C  # noqa: E402
import moon  # noqa: E402

FRAMES = [186, 200, 208, 214, 250, 266, 271, 275, 279, 281, 283]


def main(blend, out, frames=FRAMES):
    a, b, aw, vw = C.main(blend)
    W, H = 380, 300
    S = Image.new("RGB", (W * 2, H * len(frames) // 1), (20, 20, 20))
    rows = []
    for f in frames:
        c = aw[f]["Torso"][1]
        w = [aw[f]]
        side = moon.render(w, eye=c + np.array([9.0, 0.0, 0.0]), target=c + np.array([0, -0.8, 0.0]), fov=45,
                           size=(W, H), title=f"f{f} profil")
        tq = moon.render(w, eye=c + np.array([5.0, 0.0, -7.0]), target=c + np.array([0, -0.6, 0]), fov=45,
                         size=(W, H), title=f"f{f} 3/4 face")
        rows.append((side, tq))
    cols = 3
    n = len(rows)
    S = Image.new("RGB", (W * 2 * cols, H * ((n + cols - 1) // cols)), (20, 20, 20))
    for i, (s, t) in enumerate(rows):
        x, y = (i % cols) * 2 * W, (i // cols) * H
        S.paste(s, (x, y))
        S.paste(t, (x + W, y))
    S.save(out)
    print(out)


if __name__ == "__main__":
    fr = [int(x) for x in sys.argv[3:]] or FRAMES
    main(sys.argv[1], sys.argv[2], fr)
