"""
Lecteur interactif (page HTML autonome) de la technique M1, a partir des
FICHIERS EXPORTES : chaque frame est resolue par l'equation du moteur
(roblox_export.solve) avec les deux personnages places comme en jeu
(attaquant a l'origine regardant -Z, victime = attaquant * CFrame.new(0,0,-d)
* Angles(0,pi,0)). Three.js est en Y haut / -Z avant comme Roblox : aucune
conversion de repere. Hitstop, VFX, recul et secousse : memes parametres que
M1.CONFIG, lus dans le source Luau.

Usage : python3 build_player.py   ->   ../output/m1_player.html
"""
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "output")
sys.path.insert(0, os.path.join(HERE, "..", "..", "_shared"))
from animator_brain import roblox_export as X  # noqa: E402

LUAU = open(os.path.join(HERE, "..", "luau", "M1Technique.luau")).read()
SCENE = json.load(open(os.path.join(OUT, "scene.json")))


def cfg(name):
    return float(re.search(rf"\b{name}\s*=\s*([0-9.]+)", LUAU).group(1))


def cfg_color(name):
    m = re.search(rf"{name}\s*=\s*Color3\.fromRGB\((\d+),\s*(\d+),\s*(\d+)\)", LUAU)
    return "#%02x%02x%02x" % tuple(int(x) for x in m.groups())


def quat(r):
    """matrice de rotation -> quaternion (x, y, z, w)"""
    t = np.trace(r)
    if t > 0:
        s = np.sqrt(t + 1.0) * 2
        w, x, y, z = 0.25 * s, (r[2, 1] - r[1, 2]) / s, (r[0, 2] - r[2, 0]) / s, (r[1, 0] - r[0, 1]) / s
    elif r[0, 0] > r[1, 1] and r[0, 0] > r[2, 2]:
        s = np.sqrt(1.0 + r[0, 0] - r[1, 1] - r[2, 2]) * 2
        w, x, y, z = (r[2, 1] - r[1, 2]) / s, 0.25 * s, (r[0, 1] + r[1, 0]) / s, (r[0, 2] + r[2, 0]) / s
    elif r[1, 1] > r[2, 2]:
        s = np.sqrt(1.0 + r[1, 1] - r[0, 0] - r[2, 2]) * 2
        w, x, y, z = (r[0, 2] - r[2, 0]) / s, (r[0, 1] + r[1, 0]) / s, 0.25 * s, (r[1, 2] + r[2, 1]) / s
    else:
        s = np.sqrt(1.0 + r[2, 2] - r[0, 0] - r[1, 1]) * 2
        w, x, y, z = (r[1, 0] - r[0, 1]) / s, (r[0, 2] + r[2, 0]) / s, (r[1, 2] + r[2, 1]) / s, 0.25 * s
    return [round(float(v), 5) for v in (x, y, z, w)]


def track(path, root):
    frames = []
    for _t, poses in X.read_kfseq(path):
        w = X.solve(poses, root=root)
        frames.append({p: [round(float(v), 4) for v in w[p][1]] + quat(w[p][0]) for p in X.PART_ORDER
                       if p != "HumanoidRootPart"})
    return frames


def main():
    d = SCENE["distance"]
    ry = np.array([[-1.0, 0, 0], [0, 1.0, 0], [0, 0, -1.0]])
    att = track(os.path.join(OUT, "m1_attaquant.rbxmx"), (np.eye(3), np.array([0.0, 3.0, 0.0])))
    vic = track(os.path.join(OUT, "m1_victime_reaction.rbxmx"), (ry, np.array([0.0, 3.0, -d])))
    data = {
        "fps": 60, "att": att, "vic": vic, "distance": round(d, 3),
        "markers": {"trail_on": 10 / 60, "hit": SCENE["impact_f"] / 60, "trail_off": 21 / 60},
        "phases": [["armement", 0, 9 / 60], ["coup", 9 / 60, 21 / 60], ["tenue", 21 / 60, 39 / 60]],
        "cfg": {k: cfg(k) for k in ("HITSTOP", "KNOCKBACK", "KNOCKBACK_TIME", "SHAKE_AMPLITUDE", "SHAKE_DURATION")},
        "colors": {k: cfg_color(k) for k in ("FLASH_COLOR", "SPARK_COLOR", "RING_COLOR", "TRAIL_COLOR")},
        "sizes": X.RIG["part_sizes"],
    }
    html = open(os.path.join(HERE, "player_template.html")).read().replace("/*__DATA__*/null", json.dumps(data, separators=(",", ":")))
    path = os.path.join(OUT, "m1_player.html")
    open(path, "w").write(html)
    print(path, len(html) // 1024, "Ko ;", len(att), "frames attaquant,", len(vic), "frames victime")


if __name__ == "__main__":
    main()
