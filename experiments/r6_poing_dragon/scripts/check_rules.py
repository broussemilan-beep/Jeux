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
from animator_brain import roblox_export as X  # noqa: E402
from animator_brain import rules as R  # noqa: E402


def _tip(w, part):
    r, c = w[part]
    return c + r @ np.array([0.0, -1.0, 0.0])


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
    # 4. mecanique du corps pendant la rafale (retour Milan sur la v2)
    shoulders = [float(X.joint_transform(a, aw[f])[1][1]) for f in range(0, rafale_end)
                 for a in ("Right Arm", "Left Arm")]
    checks.append(R.check_epaules(shoulders))
    elev, heights, transfer = [], [], []
    for c, side, _kind in scene["hits"]:
        hand = "Right Arm" if side == "R" else "Left Arm"
        w = aw[c]
        d = _tip(w, hand) - w[hand][1]
        elev.append(float(np.degrees(np.arctan2(d[1], np.hypot(d[0], d[2])))))
        heights.append(float(_tip(w, hand)[1]))
        # avant = -Z (l'attaquant regarde -Z) ; torse relatif au milieu des pieds
        rel = [-(aw[f]["Torso"][1][2] - (_tip(aw[f], "Left Leg")[2] + _tip(aw[f], "Right Leg")[2]) / 2)
               for f in range(max(0, c - 16), c + 1)]
        transfer.append(rel[-1] - min(rel))
    checks.append(R.check_bras_au_contact(elev, heights))
    checks.append(R.check_transfert_poids(transfer, n_power=len(transfer)))
    rep = R.report(checks)
    json.dump(rep, open(os.path.join(OUT, f"regles_{tag}.json"), "w"), indent=1, ensure_ascii=False)
    print(f"regles apprises : {rep['ok']}/{rep['total']}")
    for c in checks:
        print(("  OK   " if c["ok"] else "  ECHEC") + f" {c['regle']:52s} valeur={c['valeur']}  seuil={c['seuil']}")
    return rep


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "courant")
