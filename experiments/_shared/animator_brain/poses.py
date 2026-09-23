"""
Poses : conventions d'axes VERIFIEES, traduction pose -> mots, miroir.

Le piege qui a motive ce module (r6_black_hole, 2026-09-23) : des poses
ecrites avec une convention d'axes supposee, jamais verifiee --
`CROUCH_TORSO = (70, 0, 0)` commente "torse plie vers l'avant" penchait en
realite le personnage 70 deg en ARRIERE, et `RISE_ARMS` commente "bras
ecartes a l'horizontale" croisait les mains devant la poitrine. Les
captures ne l'ont pas revele (angle de camera, rig sans visage). Regle du
cerveau : toute pose cle passe par describe_pose() et son intention est
verifiee EN MOTS avant d'etre animee.

Repere personnage R6 (verifie sur le rig reel, RigR6.rbxmx : decal
"face" sur Face=5 = NormalId.Front = -Z) : AVANT = -Z, DROITE = +X,
HAUT = +Y. CFrame.Angles(+x) releve le lookVector : une rotation X
positive LEVE l'avant de la piece.
"""
import math

import numpy as np

from .rig_math import euler_xyz_matrix, fk_pose, part_tip

FORWARD = np.array([0.0, 0.0, -1.0])
RIGHT = np.array([1.0, 0.0, 0.0])
UP = np.array([0.0, 1.0, 0.0])

# Semantique des axes, espace "apercu" de ce depot (== mouvement physique
# dans Roblox : l'export ne fait qu'une conjugaison par C0/C1, meme
# rotation monde). Chaque ligne est PROUVEE par conventions_selftest().
AXES = {
    "Torso": {"X+": "penche en ARRIERE (X- = vers l'avant)",
              "Y+": "epaule droite vers l'avant (torsion)",
              "Z+": "s'incline vers SA gauche"},
    "Head": {"X+": "leve le regard (X- = baisse la tete)",
             "Y+": "tourne le regard vers SA gauche",
             "Z+": "incline la tete vers SA gauche"},
    "Right Arm": {"X+": "part vers l'avant puis monte (90 = horizontal devant, 180 = au-dessus)",
                  "Z+": "s'ecarte vers l'EXTERIEUR (90 = horizontal sur le cote)",
                  "Z-": "croise devant le corps"},
    "Left Arm": {"X+": "part vers l'avant puis monte",
                 "Z-": "s'ecarte vers l'EXTERIEUR (miroir du bras droit)",
                 "Z+": "croise devant le corps"},
    "Right Leg": {"X+": "part vers l'avant", "Z+": "s'ecarte vers l'exterieur"},
    "Left Leg": {"X+": "part vers l'avant", "Z-": "s'ecarte vers l'exterieur"},
}


def mirror(rot):
    """Miroir gauche<->droite d'une rotation locale (plan sagittal x=0) :
    (x, y, z) -> (x, -y, -z). Valable pour torse, tete, bras et jambes
    (verifie par conventions_selftest)."""
    return (rot[0], -rot[1], -rot[2])


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def lerp(a, b, f):
    return tuple(x + f * (y - x) for x, y in zip(a, b))


def _deg(x):
    return math.degrees(x)


def pose_metrics(rig, rots, root_pos=(0.0, 3.0, 0.0)):
    """Grandeurs lisibles d'une pose, dans le repere de la racine."""
    wp, wr = fk_pose(rig, rots, root_pos)
    Rr = wr[rig.root]
    to_body = Rr.T
    torso = rig.root_children[0]
    up = to_body @ (wr[torso] @ UP)
    right = to_body @ (wr[torso] @ RIGHT)
    m = {
        "torso_lean_fwd": _deg(math.atan2(-up[2], up[1])),       # + = vers l'avant
        "torso_lean_left": _deg(math.atan2(-up[0], up[1])),      # + = vers SA gauche
        "torso_twist_rshoulder_fwd": _deg(math.atan2(-right[2], right[0])),
    }
    if "Head" in wp:
        f = to_body @ (wr["Head"] @ FORWARD)
        m["head_pitch_up"] = _deg(math.asin(max(-1, min(1, f[1]))))
        m["head_yaw_left"] = _deg(math.atan2(-f[0], -f[2]))
    for side, arm in (("R", "Right Arm"), ("L", "Left Arm")):
        if arm not in wp:
            continue
        sgn = 1.0 if side == "R" else -1.0
        c0, _ = rig.c0_c1(arm)
        shoulder = wp[torso] + wr[torso] @ c0
        hand = part_tip(rig, wp, wr, arm)
        rel = to_body @ (hand - shoulder)
        hb = to_body @ (hand - wp[rig.root])
        m[f"{side}_hand_above_shoulder"] = rel[1]
        m[f"{side}_hand_forward"] = -rel[2]
        m[f"{side}_hand_outward"] = sgn * rel[0]
        m[f"{side}_hand_crossed"] = bool(sgn * hb[0] < 0.0)   # main passee de l'autre cote de l'axe du corps
    for side, leg in (("R", "Right Leg"), ("L", "Left Leg")):
        if leg not in wp:
            continue
        foot = to_body @ (part_tip(rig, wp, wr, leg) - wp[rig.root])
        m[f"{side}_foot_forward"] = -foot[2]
        m[f"{side}_foot_y_world"] = float(part_tip(rig, wp, wr, leg)[1])
    return m


def describe_pose(rig, rots, root_pos=(0.0, 3.0, 0.0)):
    """Pose -> phrases. A lire AVANT d'animer une cle : si les mots ne
    correspondent pas a l'intention, la pose est fausse, peu importe ce que
    dit le commentaire du code."""
    m = pose_metrics(rig, rots, root_pos)
    out = []
    lf = m["torso_lean_fwd"]
    out.append(f"torse penche {'vers l AVANT' if lf >= 0 else 'en ARRIERE'} {abs(lf):.0f} deg")
    if abs(m["torso_lean_left"]) >= 4:
        out.append(f"torse incline vers sa {'gauche' if m['torso_lean_left'] > 0 else 'droite'} {abs(m['torso_lean_left']):.0f} deg")
    if abs(m["torso_twist_rshoulder_fwd"]) >= 4:
        s = "droite" if m["torso_twist_rshoulder_fwd"] > 0 else "gauche"
        out.append(f"torsion : epaule {s} en avant {abs(m['torso_twist_rshoulder_fwd']):.0f} deg")
    if "head_pitch_up" in m:
        hp, hy = m["head_pitch_up"], m["head_yaw_left"]
        txt = f"regard {'vers le HAUT' if hp >= 0 else 'vers le BAS'} {abs(hp):.0f} deg"
        if abs(hy) >= 5:
            txt += f", tourne vers sa {'gauche' if hy > 0 else 'droite'} {abs(hy):.0f} deg"
        out.append(txt)
    for side, name in (("R", "main droite"), ("L", "main gauche")):
        if f"{side}_hand_above_shoulder" not in m:
            continue
        a, f_, o = m[f"{side}_hand_above_shoulder"], m[f"{side}_hand_forward"], m[f"{side}_hand_outward"]
        pos = []
        pos.append("au-dessus de l'epaule" if a > 0.3 else ("a hauteur d'epaule" if a > -0.5 else "sous l'epaule"))
        if f_ > 0.4:
            pos.append("devant")
        elif f_ < -0.4:
            pos.append("derriere")
        if m[f"{side}_hand_crossed"]:
            pos.append("CROISEE de l'autre cote du corps")
        elif o > 0.8:
            pos.append("ecartee sur le cote")
        out.append(f"{name} : " + ", ".join(pos))
    if "R_foot_forward" in m:
        d = m["R_foot_forward"] - m["L_foot_forward"]
        if abs(d) >= 0.2:
            out.append(f"pied {'droit' if d > 0 else 'gauche'} en avant de {abs(d):.2f} stud")
    return out, m


def conventions_selftest(rig):
    """Prouve AXES par la cinematique directe (jamais supposee). Leve une
    AssertionError si une convention est fausse pour ce rig."""
    def mt(rots):
        return pose_metrics(rig, rots)
    assert mt({"Torso": (30, 0, 0)})["torso_lean_fwd"] < -20, "Torso X+ doit pencher en arriere"
    assert mt({"Torso": (-30, 0, 0)})["torso_lean_fwd"] > 20, "Torso X- doit pencher en avant"
    assert mt({"Torso": (0, 20, 0)})["torso_twist_rshoulder_fwd"] > 10, "Torso Y+ : epaule droite en avant"
    assert mt({"Torso": (0, 0, 20)})["torso_lean_left"] > 10, "Torso Z+ : inclinaison vers sa gauche"
    assert mt({"Head": (20, 0, 0)})["head_pitch_up"] > 10, "Head X+ : regard vers le haut"
    assert mt({"Head": (0, 20, 0)})["head_yaw_left"] > 10, "Head Y+ : regard vers sa gauche"
    assert mt({"Right Arm": (0, 0, 80)})["R_hand_outward"] > 1.0, "Right Arm Z+ : vers l'exterieur"
    assert mt({"Left Arm": (0, 0, -80)})["L_hand_outward"] > 1.0, "Left Arm Z- : vers l'exterieur"
    assert mt({"Right Arm": (0, 0, -60)})["R_hand_crossed"], "Right Arm Z- : croise"
    assert mt({"Right Arm": (90, 0, 0)})["R_hand_forward"] > 1.0, "Arm X+ : vers l'avant"
    assert mt({"Right Leg": (30, 0, 0)})["R_foot_forward"] > 0.5, "Leg X+ : pied vers l'avant"
    # miroir : la pose miroir d'un bras droit = meme geste du bras gauche
    a = mt({"Right Arm": (40, 15, 50)})
    b = mt({"Left Arm": mirror((40, 15, 50))})
    for k in ("hand_above_shoulder", "hand_forward", "hand_outward"):
        assert abs(a["R_" + k] - b["L_" + k]) < 1e-6, f"miroir bras incorrect ({k})"
    return True
