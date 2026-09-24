"""
Premier CLIP DE JEU du cerveau (PLAN.md, etape 3) : un M1 (direct du droit)
et la reaction de la victime, sur deux rigs V2.22 dans la meme scene, 60 fps.

Principes tires du corpus (corpus/README.md), PAS de chiffres copies d'un
clip : torse qui balaie un grand arc en lacet, regard verrouille sur la
cible (fonction Track Object du rig), bras tendu tres peu de temps,
armement qui claque en ~3 frames puis se tient, jambes a poids nul (en jeu,
la marche/l'idle les mene ; dans l'apercu elles suivent le torse en FK
neutre, exactement comme en jeu). Victime : tete qui claque en ~3 frames,
retour ~11 frames. Amplitudes choisies DANS la plage pro de la categorie
(audit.calibrated_verdict le verifie a la fin).

Usage : python3 m1_clip.py /chemin/Blender_R6.blend
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "output")
sys.path.insert(0, os.path.join(HERE, "..", "..", "_shared"))

from animator_brain import v222_rig as V  # noqa: E402
from animator_brain import roblox_export as X  # noqa: E402

FPS = 60
IMPACT_F = 17            # frame du contact (scene)
ATT_END_F = 39           # 0,65 s, duree mediane des M1 pro
VIC_START_F, VIC_END_F = IMPACT_F, IMPACT_F + 13

REST_TIP_R = np.array([1.5, 2.0, 0.0])        # bout de la main droite au repos (Roblox)
LOOK_REST_B = np.array([0.0, 4.2, 2.02])       # LookToPoint au repos (Blender)


def r2b(v):
    """Roblox (x, y haut, z arriere) -> Blender (x, y avant, z haut)."""
    return np.array([v[0], -v[2], v[1]])


def look_at(point_r):
    return tuple(r2b(point_r) - LOOK_REST_B)


# ---------------------------------------------------------------------
# Choregraphie. Lacet + = tourner a gauche, tangage + = pencher en arriere
# (LowerTorso-FK : rotation (tangage, lacet, roulis) en degres).

def attacker_keys(victim_chest_r, punch_aim_r):
    """(frame, torse (tangage, lacet, roulis), bassin (x, haut, arriere),
    bout de la main D, bout de la main G (monde Roblox), regard).
    v7 : le bras gauche TIRE franchement en arriere pendant la frappe
    (« chamber », oppose au poing) -- amplitude 71 deg avant, 124-196 chez le pro.
    v6 (chaine des pics vs pro) : a f14 la main est deja presque devant (le
    bras culmine AVANT le torse, comme le pro) ; retour du bras etale jusqu'a
    f33 (sinon 3e pic de vitesse, absent chez le pro).
    v5 (revue visuelle) : a l'armement le bras gauche VISE la cible, tendu
    droit devant a hauteur de poitrine (comme le pro : main ~2,8 studs devant
    le torse, hauteur ~2,9) -- en v4 il pointait vers le haut, monte pour
    faire passer une mesure d'amplitude : chiffre bon, pose illisible.
    v4 : claquement en 3 frames (2 frames : tout culminait des la frame 1,
    hors plage pro), bras gauche de visee plus haut, cle f19 pour que le
    poing ne rentre pas dans la victime pendant que le torse finit l'arc.
    v3 d'apres audit.calibrated_verdict (frappe_legere) : les DEUX bras en IK
    (les pros decalent les deux, 1,3-1,6 stud), armement qui claque en 2
    frames, suite du geste qui ne rentre plus dans la victime."""
    look = look_at(victim_chest_r)
    follow = (np.asarray(punch_aim_r) + np.array([0.0, 0.0, 0.2])).tolist()   # 0,2 stud en deca du contact
    rest_l = [-1.5, 2.0, 0.0]
    return [
        (0,  (0, 0, 0),      (0, 0, 0),         REST_TIP_R.tolist(), rest_l,            look),
        (3,  (-6, -60, 4),   (0, -0.04, 0.08),  [2.0, 4.3, 1.5],     [-0.3, 3.2, -1.7], look),  # l'armement CLAQUE
        (10, (-8, -98, 6),   (0, -0.06, 0.12),  [1.3, 4.4, 1.8],     [0.2, 3.1, -2.0],  look),  # extreme, tenu
        (14, (-12, -35, 2),  (0, -0.08, -0.05), [0.9, 3.5, -2.3],    [-1.0, 3.4, -0.6], look),  # la main MENE : deja presque devant
        (IMPACT_F, (-16, 30, -3), (0, -0.10, -0.25), punch_aim_r,    [-1.1, 3.3, 1.5],  look),  # contact, bras G tire en arriere
        (19, (-18, 42, -4),  (0, -0.10, -0.28), (np.asarray(punch_aim_r) + [0.0, 0.0, 0.12]).tolist(),
         [-1.2, 3.2, 1.6], look),                                                                   # ne rentre pas
        (21, (-20, 52, -4),  (0, -0.10, -0.30), follow,              [-1.3, 3.1, 1.5],  look),  # le torse finit l'arc
        (33, (-21, 47, -4),  (0, -0.10, -0.30), [0.9, 3.2, -1.0],    [-1.5, 3.0, 1.0],  look),  # retour LENT du bras
        (ATT_END_F, (-22, 45, -3), (0, -0.09, -0.28), [0.9, 3.1, -0.9], [-1.5, 3.0, 0.9], look),  # tenue
    ]


def victim_tracks():
    """Pistes SEPAREES par groupe (la tete mene : chez le pro elle culmine
    des la 1re frame), valeurs (tangage, lacet[, roulis]) ou FK X des bras.
    Torse en mode FK : pivot sur SON centre (une reaction pro ne deplace pas
    le torse). Aller en ligne droite, retour QUAD/EASE_OUT (essaye aussi :
    SINE/EASE_IN_OUT -> vallee a l'extreme, 25/38 au lieu de 28) : un seul
    mouvement, sans arret a l'extreme ni longue traine (v4 : EXPO trainait,
    43 % du temps quasi immobile contre 0-7 % chez le pro)."""
    s0, e = VIC_START_F, VIC_END_F
    return {
        "Head": [(s0, (0, 0, 0)), (s0 + 2, (22, 28, 0)), (e, (0, 0, 0))],
        "Torso_FK": [(s0, (0, 0, 0)), (s0 + 3, (13, 20, -5)), (e, (0, 0, 0))],
        "RightArm_FK": [(s0, (0, 0, 0)), (s0 + 2, (-30, 0, 0)), (e, (0, 0, 0))],
        "LeftArm_FK": [(s0, (0, 0, 0)), (s0 + 3, (-26, 0, 0)), (e, (0, 0, 0))],
    }


def build(blend):
    a = V.open_rig(blend)
    b = V.append_rig(blend, "Victime")
    # jambes a poids nul en jeu : dans l'apercu, FK neutre qui suit le torse
    for rig in (a, b):
        for leg in ("Left Leg", "Right Leg"):
            V.set_setting(leg, "IK/FK", 0.0, rig=rig)
            V.set_setting(leg, "Torso Influence", 1.0, rig=rig)
    # main droite en IK, epaule ATTACHEE au torse (Torso Influence = 1).
    # Torso Influence = 0 detache aussi l'epaule (mesure : bras a 1,73 stud
    # du torse) -- la visee en repere monde passe donc par
    # V.solve_control_for_tip, pas par ce reglage.
    V.set_setting("Right Arm", "IK/FK", 1.0, rig=a)
    V.set_setting("Left Arm", "IK/FK", 1.0, rig=a)
    V.set_setting("Head", "Track Object", 1.0, rig=a)
    V.set_setting("Torso", "IK/FK", 0.0, rig=b)   # victime : torse en FK (pivot au centre)
    return a, b


def attacker_controls(key):
    f, torso, pelvis, _tip_r, _tip_l, look = key
    return {"LowerTorso-FK": {"rotation_euler": torso, "location": pelvis},
            "LookToPoint": {"location": look}}


def solve_attacker(a, keys):
    """Passe 1 (rig encore NON anime) : pour chaque cle, pose le corps puis
    resout la main. Retourne [(cle, location IK, residu)]."""
    out = []
    for k in keys:
        V.set_controls(attacker_controls(k), rig=a)
        loc, res = V.solve_control_for_tip("RightArm-IK", "Right Arm", k[3], rig=a)
        loc_l, res_l = V.solve_control_for_tip("LeftArm-IK", "Left Arm", k[4], rig=a)
        out.append((k, (loc, loc_l), max(res, res_l)))
    return out


def key_attacker(a, solved):
    for k, (loc, loc_l), _res in solved:
        c = attacker_controls(k)
        c["RightArm-IK"] = {"location": loc}
        c["LeftArm-IK"] = {"location": loc_l}
        V.key_controls(k[0], c, rig=a)


def key_victim(b):
    for ctrl, track in victim_tracks().items():
        for i, (f, rot) in enumerate(track):
            interp, easing = (("LINEAR", None) if i == 0 else ("QUAD", "EASE_OUT") if i == 1 else ("BEZIER", None))
            V.key_controls(f, {ctrl: {"rotation_euler": rot}}, rig=b, interpolation=interp, easing=easing)


def fist_tip(world):
    return V.limb_tip(world, "Right Arm")


def box_signed_distance(pt, rot, center, half):
    q = rot.T @ (np.asarray(pt) - center)
    d = np.abs(q) - half
    outside = np.linalg.norm(np.maximum(d, 0.0))
    inside = min(max(d[0], max(d[1], d[2])), 0.0)
    return outside + inside


def reach_at_impact(blend):
    """Portee du poing a l'impact : pose d'impact, bras vise TRES loin
    devant (chaine tendue) -> point du poing le plus avance."""
    a, _b = build(blend)
    k = attacker_keys(np.array([0.0, 3.2, -3.0]), [0.0, 3.2, -12.0])[4]
    V.set_controls(attacker_controls(k), rig=a)
    V.solve_control_for_tip("RightArm-IK", "Right Arm", k[3], rig=a)
    V.solve_control_for_tip("LeftArm-IK", "Left Arm", k[4], rig=a)
    return fist_tip(V.current_parts(a))


def main(blend):
    tip = reach_at_impact(blend)
    d = 0.5 - tip[2]            # surface avant du torse de la victime = poing
    contact = tip.tolist()
    print(f"poing a l'impact (bras tendu) : {np.round(tip, 3)} -> victime a {d:.3f} studs")
    a, b = build(blend)
    V.place(b, (0.0, d, 0.0), 180.0)
    chest = np.array([0.0, 3.2, -d])
    keys = attacker_keys(chest, contact)
    solved = solve_attacker(a, keys)
    for k, _loc, res in solved:
        print(f"  cle f{k[0]:2d} : residu main {res:.3f} stud")
    key_attacker(a, solved)
    key_victim(b)
    import bpy
    bpy.context.scene.render.fps = FPS
    wa = V.bake_parts(0, ATT_END_F, rig=a)
    wb = V.bake_parts(0, ATT_END_F, rig=b)
    json.dump({"distance": d, "impact_f": IMPACT_F, "fps": FPS, "att_end_f": ATT_END_F,
               "vic": [VIC_START_F, VIC_END_F], "residus_main": [round(r, 4) for _k, _l, r in solved]},
              open(os.path.join(OUT, "scene.json"), "w"))
    return a, b, wa, wb, d


if __name__ == "__main__":
    main(sys.argv[1])
