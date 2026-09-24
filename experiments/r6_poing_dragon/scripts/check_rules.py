"""
Passe les REGLES apprises par le cerveau (animator_brain/rules.py, LECONS.md)
sur la production telle qu'exportee : fichiers .rbxmx relus + staging.json.

Usage : python3 check_rules.py [etiquette]   ->   ../output/regles_<etiquette>.json
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "output")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "_shared"))

import staging as ST  # noqa: E402
from animator_brain import rules as R  # noqa: E402


def main(tag="courant"):
    scene = json.load(open(os.path.join(OUT, "scene.json")))
    st = json.load(open(os.path.join(OUT, "staging.json")))
    aw, vw = ST.tracks()
    hits = [h[0] for h in scene["hits"]]
    rafale_end = hits[-1] + 12
    # 1. posture pendant la rafale (frames au sol)
    ty = [aw[f]["Torso"][1][1] for f in range(0, rafale_end)]
    checks = [R.check_affaissement(ty, "frappe_legere")]
    # 2. escalade : hitstop, recul de la victime (torse, 12 f apres le contact), secousse
    impacts = {e["frame"]: e for e in st["events"] if e["kind"] == "impact"}
    hs = [impacts[h]["hitstop"] for h in hits if h in impacts]
    shake = [impacts[h]["shake"] for h in hits if h in impacts]
    recoil = [float(np.linalg.norm(vw[min(h + 12, len(vw) - 1)]["Torso"][1] - vw[h]["Torso"][1])) for h in hits]
    checks += [R.check_escalade(hs, "hitstop"), R.check_escalade(recoil, "recul de la victime (studs)"),
               R.check_escalade(shake, "secousse camera")]
    checks.append(R.check_variete_camera(st["camera"], hits))
    # 3. impact final visible, plongee lisible
    overlays = [e["frames"][0] for e in st["events"] if e["kind"] in ("manga", "white")]
    checks.append(R.check_impact_visible(scene["impact_f"], min(overlays)))
    checks.append(R.check_plan_lisible(st["camera"], scene["strike_f"] - 22, scene["impact_f"]))
    rep = R.report(checks)
    json.dump(rep, open(os.path.join(OUT, f"regles_{tag}.json"), "w"), indent=1, ensure_ascii=False)
    print(f"regles apprises : {rep['ok']}/{rep['total']}")
    for c in checks:
        print(("  OK   " if c["ok"] else "  ECHEC") + f" {c['regle']:52s} valeur={c['valeur']}  seuil={c['seuil']}")
    return rep


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "courant")
