"""
Verifie et exporte le Poing du Dragon (dragon_clip.py), en une passe :

1. contacts : distance signee poing / boite de la partie visee a CHAQUE coup
   (4 coups de la rafale, coup charge (v5, ex-uppercut), frappe en l'air, ecrasement au sol), et
   penetration dans les 10 frames qui suivent ;
2. sol : aucun coin de partie sous le sol (> 0,1 stud) ;
3. tete jamais decalee (regle du corpus pro) ;
4. export des deux KeyframeSequences a 60 Hz avec les markers, aller-retour
   par l'equation du moteur ;
5. SENS en repere Roblox, relu dans les fichiers ;
6. verdict calibre par SEGMENT : chaque coup de la rafale en frappe_legere,
   l'uppercut en frappe_lourde, chaque reaction en reaction.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "_shared"))

import dragon_clip as M  # noqa: E402
from animator_brain import audit as A  # noqa: E402
from animator_brain import corpus as C  # noqa: E402
from animator_brain import roblox_export as X  # noqa: E402
from animator_brain import v222_rig as V  # noqa: E402
from animator_brain.build_corpus import flatten  # noqa: E402

LEGS = ("Right Leg", "Left Leg")
HALF = {"Torso": np.array([1.0, 1.0, 0.5]), "Head": np.array([0.62, 0.62, 0.62])}
SIZES = {"Torso": (2, 2, 1), "Head": (1.25, 1.25, 1.25), "Right Arm": (1, 2, 1), "Left Arm": (1, 2, 1),
         "Right Leg": (1, 2, 1), "Left Leg": (1, 2, 1)}


def sdist(pt, part):
    r, c = part[0], part[1]
    return lambda half: _box(pt, r, c, half)


def _box(pt, rot, center, half):
    q = rot.T @ (np.asarray(pt) - center)
    d = np.abs(q) - half
    return float(np.linalg.norm(np.maximum(d, 0.0)) + min(max(d[0], max(d[1], d[2])), 0.0))


def lowest(world):
    lo = 1e9
    for p, s in SIZES.items():
        r, c = world[p]
        h = np.array(s) / 2
        for sx in (-1, 1):
            for sy in (-1, 1):
                for sz in (-1, 1):
                    lo = min(lo, float((c + r @ (h * [sx, sy, sz]))[1]))
    return lo


def contact_checks(aw, vw):
    rows = []
    events = [(c, s, k) for c, s, k in M.HITS] + [(M.UPPER_F, "R", "chest"), (M.STRIKE_F, "R", "chest"),
                                                   (M.IMPACT_F, "R", "chest")]
    for c, s, kind in events:
        arm = "Right Arm" if s == "R" else "Left Arm"
        part = "Head" if kind in ("face", "chin") else "Torso"

        def sd(f):
            return _box(V.limb_tip(aw[f], arm), vw[f][part][0], vw[f][part][1], HALF[part])
        after = [sd(f) for f in range(c + 1, min(c + 11, M.END_F))]
        rows.append({"frame": c, "main": s, "cible": part, "distance_au_contact": round(sd(c), 3),
                     "penetration_max_apres": round(-min(0.0, min(after)), 3)})
    return rows


def resample(keys, t):
    """Pose du moteur a l'instant t : Lerp/slerp entre les deux cles."""
    ts = [k[0] for k in keys]
    i = max(0, min(len(ts) - 2, int(np.searchsorted(ts, t, side="right")) - 1))
    u = min(1.0, max(0.0, (t - ts[i]) / (ts[i + 1] - ts[i])))
    out = {}
    for p in keys[i][1]:
        (ra, pa), (rb, pb) = keys[i][1][p], keys[i + 1][1][p]
        out[p] = (X._slerp_rot(ra, rb, u), pa + (pb - pa) * u)
    return out


def reduction_error(path, full, root):
    """Ecart max (studs, centres des parts) entre l'animation lue dans le
    fichier reduit et rejouee par le moteur, et la cuisson image par image."""
    keys = X.read_kfseq(path)
    worst = 0.0
    for t, w in full:
        ws = X.solve(resample(keys, t), root=root)
        wf = X.solve({p: X.joint_transform(p, w) for p in ws if p != "HumanoidRootPart"}, root=root)
        worst = max(worst, max(float(np.linalg.norm(ws[p][1] - wf[p][1])) for p in ws))
    return worst


def segment_verdict(frames, cat, strike):
    tp = C.timing_profile(frames, False, LEGS, strike=strike)
    vals = {"timing." + k: v for k, v in flatten(tp).items()}
    rows = A.calibrated_verdict(vals, cat)
    ok = sum(r[3] == "dans_la_plage" for r in rows)
    return ok, len(rows), [(r[0], r[1], r[2]) for r in rows if r[3] == "hors_plage"]


def main(blend):
    a, b, aw, vw = M.main(blend)
    rep = {}
    rep["contacts"] = contact_checks(aw, vw)
    rep["sol"] = {"plus_bas_attaquant": round(min(lowest(aw[f]) for f in aw), 3),
                  "plus_bas_victime": round(min(lowest(vw[f]) for f in vw), 3)}
    rep["translation_tete_max"] = round(max(float(np.linalg.norm(X.joint_transform("Head", w)[1]))
                                            for w in list(aw.values()) + list(vw.values())), 5)
    # export
    att = [(f / M.FPS, aw[f]) for f in range(0, M.END_F + 1)]
    vic = [(f / M.FPS, vw[f]) for f in range(0, M.END_F + 1)]
    pa = os.path.join(M.OUT, "dragon_attaquant.rbxmx")
    pv = os.path.join(M.OUT, "dragon_victime.rbxmx")
    marks = [(f / M.FPS, name, name) for name, f in M.MARKERS]
    keep = [f / M.FPS for _n, f in M.MARKERS] + [c / M.FPS for c, _s, _k in M.HITS]
    att_r = X.reduce_keyframes(att, keep_times=keep)
    vic_r = X.reduce_keyframes(vic, keep_times=keep)
    if M.RAFALE.get("eparse"):
        # v8 : dans la fenêtre de la rafale, on n'exporte que les poses posées
        # (clé toutes les 2-5 f, Linear dans Roblox), comme TSB (CARNET §2.1c)
        f0, f1 = M.RAFALE["eparse"]
        posees = set()
        for o in [a.primary, a.internal] + list(a.holders.values()):
            ad = getattr(o, "animation_data", None)
            if ad and ad.action:
                posees |= {int(round(k.co[0])) for fc in M.V._fcurves(ad.action) for k in fc.keyframe_points}
        fr = lambda t: int(round(t * M.FPS))  # noqa: E731
        att_r = [(t, w) for t, w in att_r if not (f0 < fr(t) < f1)] + [(f / M.FPS, aw[f]) for f in sorted(posees)
                                                                       if f0 < f < f1]
        att_r.sort(key=lambda x: x[0])
        rep["rafale_cles_posees"] = sorted(f for f in posees if f0 < f < f1)
    X.write_kfseq(att_r, pa, "PoingDuDragon_Attaquant", priority=4, markers=marks)
    X.write_kfseq(vic_r, pv, "PoingDuDragon_Victime", priority=4)
    rep["aller_retour_max"] = max(max(v[0] for v in X.roundtrip_error(p, fr).values())
                                  for p, fr in ((pa, att_r), (pv, vic_r)))
    rep["cles"] = {"attaquant": len(att_r), "victime": len(vic_r), "frames": len(att)}
    rep["ecart_max_reduction_studs"] = round(max(reduction_error(p, fr, root) for p, fr, root in (
        (pa, att, (np.eye(3), np.array([0.0, 3.0, 0.0]))),
        (pv, vic, (np.diag([-1.0, 1.0, -1.0]), np.array([0.0, 3.0, -M.D]))))), 4)
    rep["taille_fichiers_ko"] = [os.path.getsize(p) // 1024 for p in (pa, pv)]
    # SENS, relu dans les fichiers, victime placee comme en jeu
    ry = np.array([[-1.0, 0, 0], [0, 1.0, 0], [0, 0, -1.0]])
    ha, hv = (np.eye(3), np.array([0.0, 3.0, 0.0])), (ry, np.array([0.0, 3.0, -M.D]))
    fa, fv = X.read_kfseq(pa), X.read_kfseq(pv)
    wa = lambda f: X.solve(resample(fa, f / M.FPS), root=ha)  # noqa: E731
    wv = lambda f: X.solve(resample(fv, f / M.FPS), root=hv)  # noqa: E731
    look = lambda w, p="Torso": -w[p][0][:, 2]  # noqa: E731
    h1 = M.HITS[0][0]
    sens = {
        "attaquant_regarde_moins_z": bool(look(wa(0))[2] < -0.9),
        "victime_face_a_l_attaquant": bool(look(wv(0))[2] > 0.9),
        "poing_H1_devant": bool(V.limb_tip(wa(h1), "Right Arm" if M.HITS[0][1] == "R" else "Left Arm")[2] < -1.5),
        "victime_recule_vers_moins_z": bool(wv(126)["Torso"][1][2] < wv(0)["Torso"][1][2] - 2.0),
        "victime_en_l_air_a_l_apex": bool(wv(M.APEX_F)["Torso"][1][1] > 9.0),
        "attaquant_au_dessus_a_l_apex": bool(wa(M.APEX_F)["Torso"][1][1] > wv(M.APEX_F)["Torso"][1][1] + 2.0),
        "poing_vers_le_bas_au_contact_air": bool(
            (V.limb_tip(wa(M.STRIKE_F), "Right Arm") - wa(M.STRIKE_F)["Right Arm"][1])[1] < -0.5),
        "victime_ejectee_loin_devant": bool(wv(M.END_F)["Torso"][1][2] < -15.0),
        "victime_couchee_a_la_fin": bool(abs(look(wv(M.END_F))[1]) > 0.9),
    }
    # interpolation : chaque Pose en Linear (Enum.PoseEasingStyle.Linear = 0).
    # 1 = Constant : en jeu, pose figee puis saut a la cle suivante. Tous nos
    # exports l'ont ete jusqu'au 2026-09-24 sans qu'aucun controle le voie (le
    # lecteur HTML interpole lineairement quoi qu'il arrive).
    import re as _re
    for nom in ("dragon_attaquant.rbxmx", "dragon_victime.rbxmx"):
        styles = set(_re.findall(r'<token name="EasingStyle">(\d+)</token>', open(os.path.join(M.OUT, nom)).read()))
        sens[f"interpolation_lineaire_{nom.split('_')[1].split('.')[0]}"] = styles == {"0"}
    rep["sens_roblox"] = sens
    if not all(sens.values()):
        raise SystemExit(f"SENS FAUX : {sens}")
    # verdicts par segment
    seg = {}
    for i, (c, s, kind) in enumerate(M.HITS):
        seg[f"coup{i + 1}_{s}_{kind}"] = ("frappe_legere",) + segment_verdict(att[c - 10:c + 15], "frappe_legere", True)
        seg[f"reaction{i + 1}"] = ("reaction",) + segment_verdict(vic[c:c + 15], "reaction", False)
    seg["coup_charge"] = ("frappe_lourde",) + segment_verdict(att[118:171], "frappe_lourde", True)
    seg["plongee_ecrasement"] = ("frappe_lourde",) + segment_verdict(att[240:300], "frappe_lourde", True)
    rep["verdicts"] = {k: {"categorie": v[0], "dans_la_plage": v[1], "total": v[2], "hors_plage": v[3]}
                       for k, v in seg.items()}
    json.dump(rep, open(os.path.join(M.OUT, "verification.json"), "w"), indent=1, ensure_ascii=False, default=float)
    print(json.dumps({k: rep[k] for k in ("sol", "translation_tete_max", "aller_retour_max", "cles",
                                          "ecart_max_reduction_studs", "taille_fichiers_ko",
                                          "sens_roblox")}, ensure_ascii=False))
    for r in rep["contacts"]:
        print("  contact", r)
    for k, v in rep["verdicts"].items():
        print(f"  {k:28s} {v['categorie']:14s} {v['dans_la_plage']}/{v['total']}")
    return rep, a, b, aw, vw


if __name__ == "__main__":
    main(sys.argv[1])
