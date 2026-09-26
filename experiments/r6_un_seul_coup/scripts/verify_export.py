"""
Vérifie et exporte « Un seul coup » (coup_clip.py), en une passe :
1. contact : distance signée poing / boîte du torse de la victime au contact ;
2. sol : aucun coin de partie sous le sol (> 0,1 stud) ;
3. tête jamais décalée (règle du corpus pro) ;
4. export des deux KeyframeSequences à 60 Hz avec les markers, aller-retour
   par l'équation du moteur, écart de la réduction de clés ;
5. SENS en repère Roblox, relu dans les fichiers (victime placée comme en jeu) :
   contrôles TECHNIQUES seulement (orientation, placement, contact devant) ;
6. interpolation Linear partout ;
7. mesures de POSE (geo_pose, repère du coup) aux temps forts, sans verdict :
   à lire à côté des fourchettes des refs, pas des règles.
Usage : python3 verify_export.py /chemin/Blender_R6.blend
"""
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DRAGON = os.path.join(HERE, "..", "..", "r6_poing_dragon", "scripts")
sys.path.insert(0, os.path.join(HERE, "..", "..", "_shared"))
sys.path.insert(0, DRAGON)
sys.path.insert(0, HERE)

import coup_clip as C  # noqa: E402
from animator_brain import roblox_export as X  # noqa: E402
from animator_brain import v222_rig as V  # noqa: E402
sys.path.insert(0, os.path.join(HERE, "..", "..", "_shared", "animator_brain", "outils"))
import geo_pose as G  # noqa: E402
import importlib.util  # noqa: E402


def _dragon(nom):
    """Module du Poing du Dragon chargé par son CHEMIN (mêmes noms de fichiers ici)."""
    spec = importlib.util.spec_from_file_location("dragon_" + nom, os.path.join(DRAGON, nom + ".py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


_VE = _dragon("verify_export")
_box, lowest, resample, HALF = _VE._box, _VE.lowest, _VE.resample, _VE.HALF


def reduction_error(path, full, root):
    keys = X.read_kfseq(path)
    worst = 0.0
    for t, w in full:
        ws = X.solve(resample(keys, t), root=root)
        wf = X.solve({p: X.joint_transform(p, w) for p in ws if p != "HumanoidRootPart"}, root=root)
        worst = max(worst, max(float(np.linalg.norm(ws[p][1] - wf[p][1])) for p in ws))
    return worst


def main(blend):
    a, b, aw, vw = C.main(blend)
    rep = {}
    cf = C.CONTACT_F
    rep["contact"] = round(_box(V.limb_tip(aw[cf], "Right Arm"), vw[cf]["Torso"][0], vw[cf]["Torso"][1], HALF["Torso"]), 3)
    rep["sol"] = {"plus_bas_attaquant": round(min(lowest(aw[f]) for f in aw), 3),
                  "plus_bas_victime": round(min(lowest(vw[f]) for f in vw), 3),
                  "images_attaquant_sous_0.1": [f for f in aw if lowest(aw[f]) < -0.1]}
    rep["translation_tete_max"] = round(max(float(np.linalg.norm(X.joint_transform("Head", w)[1]))
                                            for w in list(aw.values()) + list(vw.values())), 5)
    att = [(f / C.FPS, aw[f]) for f in range(0, C.END_F + 1)]
    vic = [(f / C.FPS, vw[f]) for f in range(0, C.END_F + 1)]
    pa = os.path.join(C.OUT, "usc_attaquant.rbxmx")
    pv = os.path.join(C.OUT, "usc_victime.rbxmx")
    marks = [(f / C.FPS, n, n) for n, f in C.MARKERS]
    keep = [f / C.FPS for _n, f in C.MARKERS]
    att_r = X.reduce_keyframes(att, keep_times=keep)
    vic_r = X.reduce_keyframes(vic, keep_times=keep)
    X.write_kfseq(att_r, pa, "UnSeulCoup_Attaquant", priority=4, markers=marks)
    X.write_kfseq(vic_r, pv, "UnSeulCoup_Victime", priority=4)
    rep["aller_retour_max"] = max(max(v[0] for v in X.roundtrip_error(p, fr).values())
                                  for p, fr in ((pa, att_r), (pv, vic_r)))
    rep["cles"] = {"attaquant": len(att_r), "victime": len(vic_r), "frames": len(att)}
    ha, hv = (np.eye(3), np.array([0.0, 3.0, 0.0])), (np.diag([-1.0, 1.0, -1.0]), np.array([0.0, 3.0, -C.DV]))
    rep["ecart_max_reduction_studs"] = round(max(reduction_error(pa, att, ha), reduction_error(pv, vic, hv)), 4)
    rep["taille_fichiers_ko"] = [os.path.getsize(p) // 1024 for p in (pa, pv)]
    fa, fv = X.read_kfseq(pa), X.read_kfseq(pv)
    wa = lambda f: X.solve(resample(fa, f / C.FPS), root=ha)  # noqa: E731
    wv = lambda f: X.solve(resample(fv, f / C.FPS), root=hv)  # noqa: E731
    look = lambda w, p="Torso": -w[p][0][:, 2]  # noqa: E731
    elev = lambda w: float(np.degrees(np.arcsin((w["Right Arm"][0] @ np.array([0.0, -1.0, 0.0]))[1])))  # noqa: E731
    penche = lambda w: float(np.degrees(np.arccos((w["Torso"][0] @ np.array([0.0, 1.0, 0.0]))[1])))  # noqa: E731
    rep["mesures_coup"] = {"bras_elev_contact": round(elev(wa(C.CONTACT_F)), 1), "buste_penche_contact": round(penche(wa(C.CONTACT_F)), 1),
                           "poing_y_contact": round(float(V.limb_tip(wa(C.CONTACT_F), "Right Arm")[1]), 2),
                           "buste_penche_charge": round(penche(wa(C.TENUE_F)), 1),
                           "bras_elev_tenue": [round(elev(wa(f)), 1) for f in range(C.CONTACT_F + 3, C.REDRESSE_F[0], 40)]}
    # Mesures de POSE, sans verdict (rappel de Milan, 2026-09-26 : « tu
    # apprends et tu te nourris, tu ne crées pas de règles gravées dans la
    # roche »). Jusqu'à la v5, des lectures de style (« poing sur le côté pas
    # derrière », « bras à plat », « buste presque droit »...) étaient ici en
    # vrai/faux et bloquaient l'export : elles venaient de mes lectures en
    # mots, en partie fausses. Ce sont maintenant des NOMBRES (geo_pose, repère
    # du coup) à lire à côté des fourchettes mesurées sur les refs (fiche
    # UN_SEUL_COUP §11) ; seuls les contrôles techniques restent en vrai/faux.
    rep["mesures_pose"] = {nom: G.descripteurs(wa(f)) for nom, f in (
        ("garde", C.ARRIVEE_F), ("debut_charge", C.CHARGE_F), ("tenue", C.TENUE_F), ("detente", C.FRAPPE_F),
        ("contact", C.CONTACT_F), ("tenue_du_coup", C.CONTACT_F + 6))}
    # contrôles TECHNIQUES : orientation des rigs, placement de la scène,
    # contact réellement devant, interpolation exportée
    sens = {
        "attaquant_regarde_moins_z": bool(look(wa(0))[2] < -0.9),
        "victime_face_a_l_attaquant": bool(look(wv(0))[2] > 0.9),
        "attaquant_devant_la_victime_des_la_charge": bool(wa(C.CHARGE_F)["Torso"][1][2] < -9.0),
        "poing_devant_au_contact": bool(V.limb_tip(wa(C.CONTACT_F), "Right Arm")[2] < wa(C.CONTACT_F)["Torso"][1][2] - 1.5),
        "victime_ejectee_loin_devant": bool(wv(C.END_F)["Torso"][1][2] < -150.0),
        "attaquant_debout_a_la_fin": bool(wa(C.END_F)["Torso"][1][1] > 2.8),
    }
    for nom in ("usc_attaquant.rbxmx", "usc_victime.rbxmx"):
        styles = set(re.findall(r'<token name="EasingStyle">(\d+)</token>', open(os.path.join(C.OUT, nom)).read()))
        sens["interpolation_lineaire_" + nom.split("_")[1].split(".")[0]] = styles == {"0"}
    rep["sens_roblox"] = sens
    json.dump(rep, open(os.path.join(C.OUT, "verification.json"), "w"), indent=1, ensure_ascii=False, default=float)
    print(json.dumps(rep, ensure_ascii=False, default=float))
    if not all(sens.values()):
        raise SystemExit(f"SENS FAUX : {sens}")
    return rep, a, b, aw, vw


if __name__ == "__main__":
    main(sys.argv[1])
