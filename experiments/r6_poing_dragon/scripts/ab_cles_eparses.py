"""
A/B « clés éparses » (étude TSB, 2026-09-24, corpus/ETUDE_TSB.md).

TSB pose une clé toutes les ~4 f et laisse le moteur interpoler en Linear.
Le poing passe alors à pleine vitesse en 1 image et file en palier. Nous
exportons chaque image cuite depuis des courbes Bézier : la frappe monte en
triangle.

Variante B : les MÊMES poses, mais sur la fenêtre choisie, l'export ne garde
que les poses clés posées à la main (les images clées dans Blender). Roblox
interpole linéairement entre elles, comme TSB. Hors de la fenêtre, rien ne
change. Une seule variable change : c'est ce qui rend l'avis de Milan
attribuable.

Sortie : ../output/ab_cles_eparses/ (rbxmx attaquant B, victime inchangée,
scene/verification/planches copiées), plus un lecteur construit dessus
(DRAGON_OUT).

Usage : python3 ab_cles_eparses.py /chemin/Blender_R6.blend [f0 f1]
"""
import json
import os
import shutil
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dragon_clip as M  # noqa: E402
import verify_export as VE  # noqa: E402
from animator_brain import perception as P  # noqa: E402
from animator_brain import roblox_export as X  # noqa: E402

OUT_B = os.path.join(M.OUT, "ab_cles_eparses")


def authored_frames(rig):
    """Images clées à la main dans Blender (toutes courbes confondues)."""
    fr = set()
    for o in [rig.primary, rig.internal] + list(rig.holders.values()):
        ad = getattr(o, "animation_data", None)
        if ad and ad.action:
            fr |= {int(round(k.co[0])) for fc in M.V._fcurves(ad.action) for k in fc.keyframe_points}
    return sorted(fr)


def main(blend, f0=108, f1=170):
    a, b, aw, vw = M.main(blend)
    keys = [f for f in authored_frames(a) if f0 <= f <= f1]
    att = [(f / M.FPS, aw[f]) for f in range(0, M.END_F + 1)]
    vic = [(f / M.FPS, vw[f]) for f in range(0, M.END_F + 1)]
    keep = [f / M.FPS for _n, f in M.MARKERS] + [c / M.FPS for c, _s, _k in M.HITS]
    att_a = X.reduce_keyframes(att, keep_times=keep)
    vic_r = X.reduce_keyframes(vic, keep_times=keep)
    # B : hors fenêtre = export A ; dans la fenêtre = poses clés seules
    fr = lambda t: int(round(t * M.FPS))  # noqa: E731
    att_b = [(t, w) for t, w in att_a if not (f0 < fr(t) < f1)]
    att_b += [(f / M.FPS, aw[f]) for f in keys if f0 < f < f1]
    att_b.sort(key=lambda x: x[0])
    os.makedirs(OUT_B, exist_ok=True)
    marks = [(f / M.FPS, name, name) for name, f in M.MARKERS]
    X.write_kfseq(att_b, os.path.join(OUT_B, "dragon_attaquant.rbxmx"), "PoingDuDragon_Attaquant", priority=4, markers=marks)
    X.write_kfseq(vic_r, os.path.join(OUT_B, "dragon_victime.rbxmx"), "PoingDuDragon_Victime", priority=4)
    for f in ["scene.json", "verification.json"] + [f"manga_{i}.png" for i in (1, 2, 3)] + [f"carte_{i}.png" for i in (1, 2, 3)]:
        shutil.copy(os.path.join(M.OUT, f), OUT_B)
    # mesure : le profil de frappe du coup chargé, A contre B, relu dans les fichiers
    res = {"fenetre": [f0, f1], "cles_main": keys,
           "cles_dans_fenetre": {"A": sum(f0 < fr(t) < f1 for t, _ in att_a), "B": sum(f0 < fr(t) < f1 for t, _ in att_b)}}
    for lab, path in (("A", os.path.join(M.OUT, "dragon_attaquant.rbxmx")), ("B", os.path.join(OUT_B, "dragon_attaquant.rbxmx"))):
        w = P.load_production(path)
        res[lab] = P.profil_frappe(w, M.UPPER_F, "Right Arm")
    # contact : distance poing / torse victime inchangée à f150 (les clés B passent PAR les poses)
    res["contact_B_poing_f150"] = [round(float(x), 3) for x in P.tip(P.load_production(os.path.join(OUT_B, "dragon_attaquant.rbxmx"))[M.UPPER_F], "Right Arm")]
    res["contact_A_poing_f150"] = [round(float(x), 3) for x in P.tip(aw[M.UPPER_F], "Right Arm")]
    json.dump(res, open(os.path.join(OUT_B, "ab.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))
    return res


if __name__ == "__main__":
    args = sys.argv[1:]
    main(args[0], *(int(x) for x in args[1:3]))
