"""
Lecteur jouable (page HTML autonome) du Poing du Dragon, a partir des
FICHIERS EXPORTES : chaque frame vient des KeyframeSequences relues et
rejouees par l'equation du moteur (staging.tracks), avec la victime placee
comme en jeu. Camera, effets et hitstops : staging.json, la meme source que
le module Roblox. Three.js est en Y haut / -Z avant comme Roblox.

Usage : python3 build_player.py   ->   ../output/dragon_player.html
"""
import base64
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("DRAGON_OUT") or os.path.join(HERE, "..", "output")  # DRAGON_OUT : variante A/B
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "_shared"))

import staging as ST  # noqa: E402
from animator_brain import roblox_export as X  # noqa: E402

PARTS = ["Torso", "Head", "Left Arm", "Right Arm", "Left Leg", "Right Leg"]


def quat(r):
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
    q = np.array([x, y, z, w])
    return q / np.linalg.norm(q)


def pack(track):
    """Tableau plat par frame : pour chaque part, x y z qx qy qz qw (3 decimales)."""
    out = []
    prev = {}
    for w in track:
        row = []
        for p in PARTS:
            r, pos = w[p]
            q = quat(r)
            if p in prev and np.dot(prev[p], q) < 0:      # continuite pour le slerp
                q = -q
            prev[p] = q
            row += [round(float(v), 3) for v in pos] + [round(float(v), 4) for v in q]
        out.append(row)
    return out


def data_uri(path):
    return "data:image/png;base64," + base64.b64encode(open(path, "rb").read()).decode()


def main():
    staging, aw, vw = ST.main()
    ver = json.load(open(os.path.join(OUT, "verification.json")))
    data = {
        "fps": staging["fps"], "end": staging["end_f"], "parts": PARTS,
        "att": pack(aw), "vic": pack(vw),
        "camera": staging["camera"], "events": staging["events"], "palette": staging["palette"],
        "markers": staging["markers"], "cinema_dose": staging.get("cinema_dose", 1),
        "sizes": X.RIG["part_sizes"],
        "manga": [data_uri(os.path.join(OUT, f"manga_{i}.png")) for i in (1, 2, 3)],
        "cartes": [data_uri(os.path.join(OUT, f"carte_{i}.png")) for i in (1, 2, 3)],
        # v13 : planches plein écran (build_planches.py)
        "planches": {os.path.splitext(n)[0]: data_uri(os.path.join(OUT, "planches", n))
                     for n in sorted(os.listdir(os.path.join(OUT, "planches")))} if os.path.isdir(os.path.join(OUT, "planches")) else {},
        "verif": {"cles": ver["cles"], "aller_retour": ver["aller_retour_max"],
                  "sens": all(ver["sens_roblox"].values()), "reduction": ver["ecart_max_reduction_studs"]},
    }
    # studio VFX : moteur + textures + meshes + sons (vfx_studio/)
    vs = os.path.join(HERE, "..", "..", "_shared", "vfx_studio")
    cat = json.load(open(os.path.join(vs, "textures", "catalogue.json")))["textures"]
    b64 = lambda path, mime: f"data:{mime};base64," + base64.b64encode(open(path, "rb").read()).decode()  # noqa: E731
    variantes = {}
    for t in cat:
        if t.get("variante_de"):
            variantes[t["variante_de"]] = variantes.get(t["variante_de"], 0) + 1
    cs = json.load(open(os.path.join(vs, "sons", "catalogue.json")))["sons"]
    data["vfx"] = {
        "textures": {t["nom"]: b64(os.path.join(vs, "textures", t["fichier"]), "image/png") for t in cat if not t.get("variante_de")},
        "variantes": variantes,
        "meshes": json.load(open(os.path.join(vs, "meshes", "meshes.json"))),
        "sons": {x["nom"]: b64(os.path.join(vs, "sons", x["fichier"]), "audio/wav") for x in cs},
        "modeles": {"dragon": json.load(open(os.path.join(vs, "modeles", "dragon.json")))},
    }
    data["vfx"]["textures"]["dragon_atlas"] = b64(os.path.join(vs, "modeles", "dragon_atlas.png"), "image/png")
    html = open(os.path.join(HERE, "player_template.html")).read()
    html = html.replace("/*__MOTEUR_VFX__*/", open(os.path.join(vs, "lab", "moteur.js")).read())
    html = html.replace("/*__DATA__*/null", json.dumps(data, separators=(",", ":")))
    path = os.path.join(OUT, "dragon_player.html")
    open(path, "w").write(html)
    print(path, len(html) // 1024, "Ko")
    return path


if __name__ == "__main__":
    main()
