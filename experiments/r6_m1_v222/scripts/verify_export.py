"""
Verifie et exporte le clip M1 + reaction (m1_clip.py), en une passe :

1. contact : distance signee poing / boite du torse de la victime, frame
   par frame (le poing touche a l'impact, ne traverse pas ensuite) ;
2. articulations attachees : translation des Motor6D (hors RootJoint) ~0 ;
3. export des deux KeyframeSequences (jambes a poids nul, marker "hit"),
   aller-retour par l'equation du moteur ;
4. verdict CALIBRE par categorie (frappe_legere / reaction) ;
5. rapport JSON + texte dans ../output/.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "_shared"))

import m1_clip as M  # noqa: E402
from animator_brain import audit as A  # noqa: E402
from animator_brain import corpus as C  # noqa: E402
from animator_brain import roblox_export as X  # noqa: E402
from animator_brain.build_corpus import flatten  # noqa: E402

LEGS = ("Right Leg", "Left Leg")


def main(blend):
    a, b, wa, wb, d = M.main(blend)
    rep = {"distance_studs": round(d, 4)}
    # 1. contact
    sd = []
    for (t, fa), (_t, fb) in zip(wa, wb):
        r, c = fb["Torso"]
        sd.append(M.box_signed_distance(M.fist_tip(fa), r, c, np.array([1.0, 1.0, 0.5])))
    sd = np.array(sd)
    rep["contact"] = {"impact_f": M.IMPACT_F, "distance_signee_a_l_impact": round(float(sd[M.IMPACT_F]), 4),
                      "penetration_max": round(float(-min(0.0, sd.min())), 4),
                      "frames_en_penetration": [int(i) for i in np.where(sd < -0.05)[0]]}
    # 2. articulations : la TETE ne se decale jamais (pack pro : 0 partout) ;
    # les membres, eux, se decalent chez les pros (faux coude) -- juges par
    # la plage de la categorie dans le verdict calibre ci-dessous
    rep["translation_tete_max"] = round(max(float(np.linalg.norm(X.joint_transform("Head", w)[1]))
                                            for _t, w in wa + wb), 5)
    # 3. export
    att = [(f / M.FPS, w) for f, (_t, w) in enumerate(wa)]
    vic = [((f - M.VIC_START_F) / M.FPS, wb[f][1]) for f in range(M.VIC_START_F, M.VIC_END_F + 1)]
    pa = os.path.join(M.OUT, "m1_attaquant.rbxmx")
    pv = os.path.join(M.OUT, "m1_victime_reaction.rbxmx")
    X.write_kfseq(att, pa, "M1_Attaquant", priority=3, markers=[(M.IMPACT_F / M.FPS, "hit", "right_fist")],
                  zero_weight=LEGS)
    X.write_kfseq(vic, pv, "M1_Victime_Reaction", priority=3, zero_weight=LEGS)
    rt = max(max(v[0] for v in X.roundtrip_error(p, fr).values()) for p, fr in ((pa, att), (pv, vic)))
    rep["aller_retour_max_studs"] = rt
    # 4. verdict calibre
    for key, frames, cat in (("attaquant", att, "frappe_legere"), ("victime", vic, "reaction")):
        tp = C.timing_profile(frames, False, LEGS, strike=(cat == "frappe_legere"))
        vals = {"timing." + k: v for k, v in flatten(tp).items()}
        rows = A.calibrated_verdict(vals, cat)
        rep[key] = {"categorie": cat, "timing": tp,
                    "verdict": {"dans_la_plage": sum(r[3] == "dans_la_plage" for r in rows),
                                "total": len(rows),
                                "hors_plage": [(r[0], r[1], r[2]) for r in rows if r[3] == "hors_plage"]}}
    json.dump(rep, open(os.path.join(M.OUT, "verification.json"), "w"), indent=1, ensure_ascii=False, default=float)
    print(json.dumps({k: v for k, v in rep.items() if k not in ("attaquant", "victime")}, ensure_ascii=False))
    for key in ("attaquant", "victime"):
        v = rep[key]["verdict"]
        print(f"{key} ({rep[key]['categorie']}) : {v['dans_la_plage']}/{v['total']} mesures dans la plage pro")
        for h in v["hors_plage"]:
            print("   hors plage :", h)
        print("   phases :", rep[key]["timing"].get("phases"))
    return rep


if __name__ == "__main__":
    main(sys.argv[1])
