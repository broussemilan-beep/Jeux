"""
« Poing du Dragon » : technique ultime sur deux rigs V2.22, 60 fps.

Brief et decoupage : experiments/_shared/animator_brain/SCENE_POING_DU_DRAGON.md.
Timing tire des references mesurees (corpus/REFERENCES_VIDEO.md), amplitudes
et durees des coups jugees contre le corpus pro (audit.calibrated_verdict).

Tout est ecrit en repere ROBLOX (x droite, y haut, z arriere de l'attaquant ;
l'attaquant regarde -Z). Une pose cle = un dict :
  root   : MasterControl (location en repere du perso x/y/z-arriere, rotation deg)
  pelvis : LowerTorso-FK (location, rotation (tangage+ = en arriere, lacet+ =
           tourner a gauche, roulis))
  chest  : UpperTorso-IKTarget (location ; y+ = poitrine en avant)
  head   : rotation de la tete (victime ; l'attaquant suit `look`)
  look   : point MONDE que l'attaquant regarde (Track Object)
  hands / feet : {"R"|"L": ("w", point monde) -> IK resolu, ou ("c", loc) ->
           valeur brute du controle IK (membre en l'air)}
  arms_fk: {"R"|"L": rotation FK} (victime : bras en FK)
Les cles sont des poses COMPLETES (travail pose a pose, comme la video Moon
Animator) ; les reactions de la victime et les coups de l'attaquant ont
chacun leur propre rythme.

Usage : python3 dragon_clip.py /chemin/Blender_R6.blend
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "output")
sys.path.insert(0, os.path.join(HERE, "..", "..", "_shared"))

from animator_brain import v222_rig as V  # noqa: E402

FPS = 60
D = 3.3                     # distance initiale victime (studs), le long de -Z
END_F = 526                 # 8,77 s

# beats (frames) -- voir SCENE_POING_DU_DRAGON.md
# v2 (retour de Milan : enchainement, puissance) : 4 coups VARIES qui MONTENT
# en force (jab, direct, crochet, coup au corps qui souleve), un pas a chaque
# coup, ecarts 26/24/26 f puis une respiration avant l'uppercut.
HITS = [  # (frame de contact, main, cible sur la victime)
    # v3 : tout dans le corps, a bout portant (refs Black Flash, LECONS.md 6)
    (14, "L", "chest"), (40, "R", "plexus"), (64, "L", "ribs"), (90, "R", "body"),
]
# escalade (rules.check_escalade) : hitstop, secousse, taille des effets
HIT_HITSTOP = [0.03, 0.045, 0.06, 0.085]
HIT_SHAKE = [0.14, 0.22, 0.3, 0.42]
HIT_SCALE = [0.6, 0.78, 0.95, 1.15]
UPPER_F = 150               # uppercut
TAKEOFF_F = 170
APEX_F = 200
SUSPEND_END_F = 256
STRIKE_F = 278              # le poing touche la victime en l'air
IMPACT_F = 288              # ecrasement au sol : impact frames
# v2 (LECONS.md 3) : l'impact au sol reste VISIBLE 10 f (+ hitstop) avant
# les planches manga (298-304), puis blanc et brouillard
MANGA_F = 298
WHITE_F = (304, 334)        # ecran blanc puis brouillard
REVEAL_F = 334
RISE_F = (490, 526)

MARKERS = [("activation", 0)] + [(f"hit{i + 1}", f) for i, (f, _h, _t) in enumerate(HITS)] + [
    ("coup_charge", UPPER_F), ("takeoff", TAKEOFF_F), ("suspend", APEX_F), ("dive", SUSPEND_END_F),
    ("strike", STRIKE_F), ("impact", IMPACT_F), ("manga", MANGA_F), ("white", WHITE_F[0]), ("reveal", REVEAL_F)]

FOOT_Y = 0.065              # bout du pied (limb_tip) au repos, sol a y = 0


def r2b(v):
    return np.array([v[0], -v[2], v[1]])


# ---------------------------------------------------------------------
# outils rig

def world_bone_head(rig, bone):
    """Tete d'un os de controle, repere Roblox."""
    b = rig.primary.pose.bones[bone]
    p = rig.primary.matrix_world @ b.head
    return np.array([p.x, p.z, -p.y])


def solve_point_control(rig, bone, target):
    """Controle a translation pure (ex. LookToPoint) : la position monde de
    sa tete est affine en sa location -> 4 evaluations, solution exacte."""
    import bpy
    pb = rig.primary.pose.bones[bone]
    pb.location = (0.0, 0.0, 0.0)
    bpy.context.view_layer.update()
    b0 = world_bone_head(rig, bone)
    A = np.zeros((3, 3))
    for k in range(3):
        l = [0.0, 0.0, 0.0]
        l[k] = 1.0
        pb.location = tuple(l)
        bpy.context.view_layer.update()
        A[:, k] = world_bone_head(rig, bone) - b0
    loc = np.linalg.solve(A, np.asarray(target, float) - b0)
    pb.location = tuple(loc)
    bpy.context.view_layer.update()
    return tuple(float(x) for x in loc)


IK = {"R": ("RightArm-IK", "Right Arm"), "L": ("LeftArm-IK", "Left Arm")}
LEG = {"R": ("RightLeg-IK", "Right Leg"), "L": ("LeftLeg-IK", "Left Leg")}
FK_ARM = {"R": "RightArm_FK", "L": "LeftArm_FK"}


def body_controls(p):
    c = {}
    if "root" in p:
        c["MasterControl"] = {"location": p["root"][0], "rotation_euler": p["root"][1]}
    if "pelvis" in p:
        c["LowerTorso-FK"] = {"location": p["pelvis"][0], "rotation_euler": p["pelvis"][1]}
    if "chest" in p:
        c["UpperTorso-IKTarget"] = {"location": p["chest"]}
    if "head" in p:
        c["Head"] = {"rotation_euler": p["head"]}
    for s, rot in p.get("arms_fk", {}).items():
        c[FK_ARM[s]] = {"rotation_euler": rot}
    return c


SIZES = {"Torso": (2, 2, 1), "Head": (1.25, 1.25, 1.25), "Right Arm": (1, 2, 1), "Left Arm": (1, 2, 1),
         "Right Leg": (1, 2, 1), "Left Leg": (1, 2, 1)}


def box_lowest(world, part):
    r, c = world[part]
    h = np.array(SIZES[part]) / 2
    return min(float((c + r @ (h * [x, y, z]))[1]) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1))


def shoulder(world, side):
    r, p = world["Right Arm" if side == "R" else "Left Arm"]
    return p + r @ np.array([0.0, 0.75, 0.0])


def torso_pivot(world, side):
    """Pivot d'epaule R6 (C0 du Motor6D : Torso * (+-1, 0,5, 0))."""
    r, p = world["Torso"]
    return p + r @ np.array([1.0 if side == "R" else -1.0, 0.5, 0.0])


def arm_point(world, side, az, el, dist):
    """v3 (LECONS.md 6) : point de main defini depuis le pivot d'epaule --
    azimut (deg, + = vers la droite du perso, 0 = devant le torse, 180 =
    derriere), elevation (deg, - = sous l'horizontale), distance (studs).
    Sonde de l'IK du V2.22 (2026-09-24) : main a < 1,7 stud du pivot ->
    l'IK HAUSSE l'epaule (+0,1 a +0,5) ; a 1,9-2,3 stud sous l'horizontale
    -> il la BAISSE (-0,2 a -0,85), comme les M1 pro."""
    f = world["Torso"][0] @ np.array([0.0, 0.0, -1.0])
    fh = np.array([f[0], 0.0, f[2]])
    fh /= np.linalg.norm(fh)
    right = np.cross(fh, [0.0, 1.0, 0.0])
    a, e = np.radians(az), np.radians(el)
    d = np.cos(e) * (np.cos(a) * fh + np.sin(a) * right) + np.sin(e) * np.array([0.0, 1.0, 0.0])
    return torso_pivot(world, side) + dist * d


def robust_tip(rig, ctrl, part, v):
    """Gauss-Newton du controle IK depuis plusieurs departs : sur certaines
    poses il diverge (controle du pied parti a 6 studs, v3). Garde le
    meilleur residu."""
    best = None
    for seed in ((0.0, 0.0, 0.0), (0.0, 0.3, 0.0), (0.0, -0.3, 0.0), (0.2, 0.0, 0.2), (-0.2, 0.0, 0.2)):
        V.set_controls({ctrl: {"location": seed}}, rig=rig)
        loc, r = V.solve_control_for_tip(ctrl, part, v, rig=rig, iters=25)
        if best is None or r < best[1]:
            best = (loc, r)
        if r < 0.005:
            break
    V.set_controls({ctrl: {"location": best[0]}}, rig=rig)
    return best


def solve_pose(rig, p):
    """v3 : `auto_low` -- si un pied n'atteint pas le sol (appui trop
    etire pour une jambe R6 d'un bloc), baisse le bassin du strict
    necessaire, et seulement de ca (LECONS.md 1)."""
    if not p.get("auto_low"):
        return _solve_pose_once(rig, p)
    p = dict(p)
    y0 = p["pelvis"][0][1]
    best = None
    for _ in range(6):
        c, res = _solve_pose_once(rig, p)
        planted = [f"feet.{side}" for side, (mode, _v) in p.get("feet", {}).items() if mode in ("g", "rg")]
        miss = max([res.get(k, 0.0) for k in planted] + [0.0])
        if best is None or miss < best[0] - 1e-4:
            best = (miss, p["pelvis"])
        else:
            break                       # baisser n'aide plus (pied trop PRES, pas trop loin)
        if miss < 0.012:
            break
        (x, y, z), rot = p["pelvis"]
        if y - miss - 0.004 < y0 - 0.2:
            break                       # jamais plus de 0,2 stud (LECONS.md 1)
        p["pelvis"] = ((x, y - miss - 0.004, z), rot)
    if best[1] is not p["pelvis"]:
        p["pelvis"] = best[1]
        c, res = _solve_pose_once(rig, p)
    return c, res


def _solve_pose_once(rig, p):
    """Passe 1 : pose le corps, resout pieds puis mains puis regard.
    `fit` = (cote, cible, decalage, masque) : translate le MasterControl pour
    que l'epaule tombe a cible + decalage (axes du masque seulement) -- le
    corps se place d'apres le coup, pas l'inverse.
    Pieds/mains ("rw", decalage) : point monde = root + decalage.
    Retourne (controles complets, residus)."""
    c = body_controls(p)
    V.set_controls(c, rig=rig)
    if "fit" in p:
        side, tgt, off, mask = p["fit"]
        sh = shoulder(V.current_parts(rig), side)
        delta = (np.asarray(tgt) + np.asarray(off) - sh) * np.asarray(mask, float)
        loc = np.asarray(c["MasterControl"]["location"]) + delta   # attaquant : repere local = monde
        c["MasterControl"]["location"] = tuple(float(x) for x in loc)
        V.set_controls({"MasterControl": c["MasterControl"]}, rig=rig)
    if "fitp" in p:
        # v3 : le corps se place pour que le pivot d'epaule soit a `dist` du
        # point de contact (IK qui BAISSE l'epaule), bras vers `az` (deg,
        # repere monde, 0 = -Z) ; hauteur du corps inchangee
        side, tgt, dist, az = p["fitp"]
        tgt = np.asarray(tgt, float)
        sh = torso_pivot(V.current_parts(rig), side)
        hd = float(np.sqrt(max(dist ** 2 - (tgt[1] - sh[1]) ** 2, 0.04)))
        a = np.radians(az)
        want = tgt - hd * np.array([np.sin(a), 0.0, -np.cos(a)])
        loc = np.asarray(c["MasterControl"]["location"]) + np.array([want[0] - sh[0], 0.0, want[2] - sh[2]])
        c["MasterControl"]["location"] = tuple(float(x) for x in loc)
        V.set_controls({"MasterControl": c["MasterControl"]}, rig=rig)
    if p.get("ground_root"):
        w = V.current_parts(rig)
        low = min(box_lowest(w, part) for part in SIZES)
        loc = np.asarray(c["MasterControl"]["location"]) + np.array([0.0, 0.02 - low, 0.0])
        c["MasterControl"]["location"] = tuple(float(x) for x in loc)
        V.set_controls({"MasterControl": c["MasterControl"]}, rig=rig)
    root = np.asarray(c.get("MasterControl", {"location": (0, 0, 0)})["location"])
    res = {}
    for table, key in ((LEG, "feet"), (IK, "hands")):
        for s, (mode, v) in p.get(key, {}).items():
            ctrl, part = table[s]
            if mode == "a":
                v = arm_point(V.current_parts(rig), s, *v)
                mode = "w"
            if mode in ("w", "rw", "g", "rg"):
                if mode == "rw":
                    v = root + np.asarray(v)
                if mode == "rg":
                    v = (root[0] + v[0], root[2] + v[1])
                    mode = "g"
                if mode == "g":
                    v = np.array([v[0], FOOT_Y, v[1]])
                loc, r = robust_tip(rig, ctrl, part, v)
                if mode == "g":
                    # une jambe R6 est UNE boite : inclinee, son coin passe sous
                    # le sol meme bout du pied pose -> on remonte la cible
                    best = None
                    for _ in range(6):
                        low = box_lowest(V.current_parts(rig), part)
                        if best is None or abs(low) < best[0]:
                            best = (abs(low), loc, r, v)
                        if abs(low) < 0.01:
                            break
                        v = v + np.array([0.0, -low, 0.0])
                        loc, r = robust_tip(rig, ctrl, part, v)
                    _low, loc, r, v = best
                    V.set_controls({ctrl: {"location": loc}}, rig=rig)
                    if _low > 0.05:
                        res[f"{key}.{s}.sol"] = round(-_low, 3)
                res[f"{key}.{s}"] = round(r, 4)
            else:
                loc = tuple(v)
                V.set_controls({ctrl: {"location": loc}}, rig=rig)
            c[ctrl] = {"location": loc}
    if "look" in p:
        c["LookToPoint"] = {"location": solve_point_control(rig, "LookToPoint", p["look"])}
    return c, res


def key_pose(rig, frame, c, interp="BEZIER", easing=None):
    V.key_controls(frame, c, interpolation=interp, rig=rig, easing=easing)


def bake_world(rig, f0, f1):
    """{frame: {part: (R, p)}} en repere Roblox."""
    import bpy
    S = bpy.context.scene
    out = {}
    for f in range(f0, f1 + 1):
        S.frame_set(f)
        out[f] = V.current_parts(rig)
    return out


# ---------------------------------------------------------------------
# VICTIME (placee a (0, 0, -D), tournee vers l'attaquant). Son repere local :
# x_local = -x monde, z_local (arriere) = -z monde.

def v_world(local):
    return np.array([-local[0], local[1], -D - local[2]])


def v_stand_feet(back, spread=0.5):
    pr, pl = v_world((spread, FOOT_Y, back)), v_world((-spread, FOOT_Y, back))
    return {"R": ("g", (pr[0], pr[2])), "L": ("g", (pl[0], pl[2]))}


def victim_pose(back, y=0.0, rootrot=(0, 0, 0), pelvis=((0, -0.02, 0), (0, 0, 0)), chest=(0, 0, 0),
                head=(0, 0, 0), arms=((8, 0, 0), (8, 0, 0)), feet=None, ground=False):
    """feet=None -> pieds plantes sous le corps ; sinon dict brut.
    ground=True -> corps pose au sol (couche)."""
    p = {"root": ((0.0, y, back), rootrot), "pelvis": pelvis, "chest": chest, "head": head,
         "arms_fk": {"R": arms[0], "L": arms[1]}, "ground_root": ground}
    p["feet"] = feet if feet is not None else v_stand_feet(back)
    return p


AIR_LEGS = {"R": ("c", (0.0, 0.25, 0.55)), "L": ("c", (0.0, -0.1, 0.35))}      # jambes pendantes, genoux fleches
TUMBLE_LEGS = {"R": ("c", (0.1, 0.5, 0.9)), "L": ("c", (-0.1, 0.1, 0.5))}
LIE_LEGS = {"R": ("c", (0.25, 0.0, 0.1)), "L": ("c", (-0.3, 0.1, 0.25))}
LIE_Y = -1.86   # MasterControl en rotation X 90 (couche sur le dos) : bas du corps au sol


def victim_keys():
    """(frame, pose, interpolation). Chaque coup : la tete CLAQUE en 2-3 f
    (mesure pro : 3 f), retour ~10-12 f ; recul progressif ; le 5e coup
    decolle, le 6e juggle, l'uppercut lance haut."""
    K = []
    add = lambda f, p, i="BEZIER": K.append((f, p, i))  # noqa: E731
    def stand(back, feet_back=None, **kw):
        return victim_pose(back, feet=(v_stand_feet(feet_back) if feet_back is not None else None), **kw)
    add(0, stand(0.0))
    # v2 : reactions calibrees sur le corpus (tete au pic en 1-2 f, torse ~27 deg,
    # bras peu agites, AUCUN affaissement) et qui MONTENT d'un coup a l'autre.
    # Les pieds restent plantes au pic puis rattrapent le corps (pas de glisse).
    # v3 : coups DANS LE CORPS (Black Flash) -> la victime se PLIE autour du
    # poing (tangage -), au lieu de claquer la tete en arriere.
    # H1 f14 : jab gauche a la poitrine : buste repousse, tete qui suit
    add(14, stand(0.0), "LINEAR")
    add(15, stand(0.14, feet_back=0.0, head=(14, 8, 0), pelvis=((0, 0, 0), (9, 5, 0)), arms=((-10, 0, 0), (-8, 0, 0))))
    add(26, stand(0.25, head=(2, 2, 0), pelvis=((0, 0, 0), (2, 1, 0))))
    # H2 f40 : direct droit au plexus : se plie en avant, souffle coupe
    add(40, stand(0.25, head=(1, 1, 0)), "LINEAR")
    add(42, stand(0.8, feet_back=0.3, head=(-16, -6, 0), pelvis=((0, 0, 0), (-24, -8, 0)), chest=(0, 0.2, 0),
                  arms=((30, 0, -8), (26, 0, 8))))
    add(53, stand(0.95, head=(-10, -4, 0), pelvis=((0, 0, 0), (-16, -5, 0)), chest=(0, 0.15, 0),
                  arms=((24, 0, -6), (20, 0, 6))))
    # H3 f64 : crochet gauche aux cotes : plie de cote, vers le coup
    add(64, stand(0.95, head=(-8, -3, 0), pelvis=((0, 0, 0), (-14, -4, 0)), chest=(0, 0.12, 0),
                  arms=((22, 0, -6), (18, 0, 6))), "LINEAR")
    add(66, stand(1.3, feet_back=1.05, head=(-12, 16, -12), pelvis=((0, 0, 0), (-18, 14, -10)), chest=(0, 0.2, 0),
                  arms=((10, 0, 0), (34, 0, 22))))
    add(78, stand(1.55, head=(-8, 8, -6), pelvis=((0, 0, 0), (-14, 10, -7)), chest=(0, 0.15, 0),
                  arms=((16, 0, 0), (24, 0, 10))))
    # H4 f90 : coup au corps montant -> plie autour du poing et DECOLLE
    add(90, stand(1.55, head=(-6, 6, -3), pelvis=((0, 0, 0), (-12, 6, -4)), chest=(0, 0.12, 0),
                  arms=((18, 0, 0), (20, 0, 6))), "LINEAR")
    add(93, victim_pose(1.95, y=0.55, head=(-26, 0, 0), pelvis=((0, 0, 0), (-34, 0, 0)), chest=(0, 0.3, 0),
                        arms=((35, 0, 0), (30, 0, 0)), feet=AIR_LEGS))
    add(104, victim_pose(2.4, y=1.3, head=(-16, 0, 0), pelvis=((0, 0, 0), (-24, 0, 0)), chest=(0, 0.2, 0),
                         arms=((40, 0, 0), (34, 0, 0)), feet=TUMBLE_LEGS))
    # v5 : sonnee mais moins affaissee (-0,4 au lieu de -0,75) : le coup charge
    # arrive a plat, a hauteur d'epaule
    add(118, stand(2.6, head=(-16, 0, 0), pelvis=((0, -0.45, 0), (-24, 0, 4)), chest=(0, 0.25, 0),
                   arms=((22, 0, 0), (18, 0, 0))))
    add(126, stand(2.6, head=(-15, 2, 0), pelvis=((0, -0.42, 0), (-22, 1, 5)), chest=(0, 0.24, 0),
                   arms=((21, 0, 0), (17, 0, 0))))
    # sonnee, affaissee, pendant l'anticipation
    add(146, stand(2.6, head=(-12, 4, 0), pelvis=((0, -0.4, 0), (-18, 3, 6)), chest=(0, 0.2, 0),
                   arms=((18, 0, 0), (14, 0, 0))), "LINEAR")
    # v5 COUP CHARGE f150 (droit, a plat) -> ejectee en DIAGONALE (arriere
    # puis haut), et non plus lancee a la verticale par un uppercut
    add(UPPER_F, stand(2.6, head=(-10, 4, 0), pelvis=((0, -0.4, 0), (-16, 3, 6)), arms=((18, 0, 0), (14, 0, 0))),
        "LINEAR")
    add(154, victim_pose(3.4, y=1.2, rootrot=(14, 0, 0), head=(40, 0, 0), pelvis=((0, 0, 0), (-20, 0, 0)),
                         arms=((-70, 0, 0), (-65, 0, 0)), feet=AIR_LEGS), ("QUAD", "EASE_OUT"))
    add(APEX_F, victim_pose(4.2, y=10.5, rootrot=(62, 0, 8), head=(24, 10, 0), pelvis=((0, 0, 0), (12, 0, 0)),
                            arms=((-95, 0, 25), (-85, 0, -30)), feet=TUMBLE_LEGS))
    # temps suspendu : derive lente
    add(SUSPEND_END_F, victim_pose(4.4, y=11.1, rootrot=(74, 0, 10), head=(18, 14, 0), pelvis=((0, 0, 0), (8, 0, 0)),
                                   arms=((-100, 0, 30), (-92, 0, -34)), feet=TUMBLE_LEGS))
    add(STRIKE_F, victim_pose(4.45, y=11.0, rootrot=(80, 0, 8), head=(16, 12, 0), pelvis=((0, 0, 0), (6, 0, 0)),
                              arms=((-102, 0, 30), (-94, 0, -34)), feet=TUMBLE_LEGS), "LINEAR")
    # poing -> plie en V autour du poing, ecrase au sol
    add(281, victim_pose(4.5, y=9.6, rootrot=(84, 0, 4), head=(-30, 0, 0), pelvis=((0, 0, 0), (-34, 0, 0)),
                         chest=(0, 0.4, 0), arms=((-40, 0, 20), (-40, 0, -20)), feet=TUMBLE_LEGS), "LINEAR")
    add(IMPACT_F, victim_pose(4.5, y=LIE_Y + 0.05, rootrot=(90, 0, 0), head=(-18, 0, 0), pelvis=((0, 0, 0), (-18, 0, 0)),
                              chest=(0, 0.25, 0), arms=((-80, 0, 40), (-80, 0, -40)), feet=LIE_LEGS, ground=True))
    add(298, victim_pose(4.5, y=LIE_Y + 0.05, rootrot=(90, 0, 0), head=(-14, 0, 0), pelvis=((0, 0, 0), (-12, 0, 0)),
                         chest=(0, 0.2, 0), arms=((-85, 0, 45), (-85, 0, -45)), feet=LIE_LEGS, ground=True))
    # dans le blanc : rebond et ejection au loin (degage des 291 : le poing
    # de l'attaquant descend au sol derriere elle)
    add(301, victim_pose(5.0, y=LIE_Y + 0.9, rootrot=(98, 0, 6), head=(-6, 0, 0), arms=((-95, 0, 40), (-95, 0, -40)),
                         feet=TUMBLE_LEGS))
    add(310, victim_pose(8.0, y=LIE_Y + 2.6, rootrot=(128, 0, 20), head=(20, 0, 0), arms=((-120, 0, 40), (-110, 0, -50)),
                         feet=TUMBLE_LEGS))
    add(326, victim_pose(15.2, y=LIE_Y + 0.05, rootrot=(90, 0, 6), head=(0, 28, 0), pelvis=((0, 0, 0), (-4, 0, 6)),
                         arms=((-150, 0, 50), (-20, 0, -60)), feet=LIE_LEGS, ground=True))
    add(334, victim_pose(15.6, y=LIE_Y, rootrot=(90, 0, 4), head=(0, 32, 0), pelvis=((0, 0, 0), (-2, 0, 5)),
                         arms=((-155, 0, 52), (-18, 0, -62)), feet=LIE_LEGS, ground=True))
    add(END_F, victim_pose(15.6, y=LIE_Y, rootrot=(90, 0, 4), head=(0, 34, 0), pelvis=((0, 0, 0), (-2, 0, 5)),
                           arms=((-155, 0, 52), (-18, 0, -62)), feet=LIE_LEGS, ground=True))
    return K


# ---------------------------------------------------------------------
# ATTAQUANT (origine, regarde -Z). z negatif = en avant.

def _pivot(x, dz, yaw_deg):
    """offset (x, dz) tourne de yaw autour du bassin (lacet + = a gauche)."""
    t = np.radians(yaw_deg)
    return x * np.cos(t) + dz * np.sin(t), -x * np.sin(t) + dz * np.cos(t)


def a_feet(z, lf=(-0.55, -0.45), rf=(0.6, 0.35), pivot=0.0):
    """pieds plantes : gauche devant, droit derriere (garde orthodoxe).
    v2 : appui SERRE -- une jambe R6 droite (2 studs) ecartee de d abaisse la
    hanche de 2 - sqrt(4 - d^2) : ecarter a 0,85 devant / 0,6 derriere
    obligeait a s'accroupir (v1). Pieds presque sous les hanches, comme les pros."""
    (lx, lz), (rx, rz) = _pivot(*lf, pivot), _pivot(*rf, pivot)
    return {"L": ("g", (lx, z + lz)), "R": ("g", (rx, z + rz))}


def a_stance(z, low=0.08, yaw=-18, lean=-8, look=None, hands=None, feet=None, chest=(0, 0.1, 0)):
    p = {"root": ((0.0, 0.0, z), (0, 0, 0)), "pelvis": ((0, -low, 0), (lean, yaw, 0)), "chest": chest,
         "feet": feet or a_feet(z)}
    p["hands"] = hands or {"L": ("w", (-0.45, 3.45 - low, z - 1.35)), "R": ("w", (0.5, 3.2 - low, z - 0.85))}
    if look is not None:
        p["look"] = look
    return p


def attacker_keys(vw, rig):
    """vw : {frame: parts monde de la victime}. Les cibles de contact sont lues
    sur la victime cuite (contact exact, meme principe que le M1)."""
    def head(f):
        return vw[f]["Head"][1]

    def target(f, kind):
        parts = vw[f]
        if kind == "face":
            r, p = parts["Head"]
            return p + r @ np.array([0, -0.1, -0.62])
        if kind == "chin":
            r, p = parts["Head"]
            return p + r @ np.array([0, -0.55, -0.55])
        r, p = parts["Torso"]
        if kind == "plexus":
            return p + r @ np.array([0, -0.1, -0.55])
        if kind == "ribs":                                 # cotes cote droit de la victime (gauche de l'attaquant)
            return p + r @ np.array([0.5, -0.3, -0.55])
        if kind == "body":
            return p + r @ np.array([0, -0.35, -0.52])
        return p + r @ np.array([0, 0.2, -0.55])         # "chest" : face avant du torse

    K = []
    add = lambda f, p, i="BEZIER": K.append((f, p, i))  # noqa: E731
    # activation : garde (v3 : mains basses et loin du pivot -> epaules basses)
    # v3 (retour de Milan sur la v2 : « bras trop hauts, accroupi, pas de
    # transfert de poids » ; LECONS.md 6-7 ; refs Black Flash) :
    # - coups DANS LE CORPS a bout portant (poitrine, plexus, cotes, foie),
    #   la victime se plie ; poing 2,6-3,2 studs du sol (pro 2,5-3,6) ;
    # - le corps se place d'apres le contact (fitp) : pivot d'epaule a
    #   ~2,1 studs du point touche, bras sous l'horizontale -> l'IK baisse
    #   l'epaule au lieu de la hausser ;
    # - pieds PLANTES de l'armement a la recuperation ; le torse recule
    #   au-dessus du pied arriere a l'armement puis passe devant le pied
    #   avant au contact (transfert ~0,6 stud) ; le pas se fait APRES le
    #   coup, pendant la recuperation, jamais pendant la frappe.
    # v4 (retour de Milan sur la v3b : « les coups partent du bas » ; ses 5
    # exemples, corpus/REFERENCES_VIDEO.md ; LECONS.md 11) : garde MAINS
    # DEVANT LA POITRINE ; le poing arme A HAUTEUR D'EPAULE (en arriere ou sur
    # le cote, jamais a la hanche) et voyage A PLAT. Sonde IK : arme a 0/+15
    # deg et 2-2,1 studs du pivot, l'epaule ne monte pas.
    GUARD = lambda: {"L": ("a", (12, -28, 2.2)), "R": ("a", (-22, -34, 2.15))}  # noqa: E731
    # garde haute de l'autre bras pendant le coup : a hauteur de poitrine
    # (au visage, l'IK du V2.22 hausserait l'epaule -- sonde LECONS.md 11)
    FACE = {"L": ("a", (18, -16, 2.3)), "R": ("a", (-18, -16, 2.3))}
    # le controle IK de la main est interpole EN LIGNE DROITE entre deux cles :
    # de derriere a devant, il frolerait l'epaule (qui remonte). On passe
    # donc par des cles en ARC autour du pivot (cote, bras bas).
    side = lambda h, az, el=-60, d=2.1: ("a", (az if h == "R" else -az, el, d))  # noqa: E731
    # v3b (retour de Milan sur la v3 : « tu donnes des coups vers le bas » ;
    # sa reference « Pro », 17-52-55, t = 4,25 s) : au contact le bras est
    # HORIZONTAL (pro : mediane -3 deg). Pour frapper plus bas, c'est le CORPS
    # qui descend (fente, pied avant qui avance), jamais le bras qui plonge.
    # La cible est donc prise sur la victime A LA HAUTEUR DE L'EPAULE.
    PLAN = {  # kind: (dist pivot->contact, azimut monde, lacet arme, lacet contact, penche contact, bassin, x local cible)
        "chest": (2.3, 12, 18, -32, -10, 0.03, 0.0),     # jab G
        "plexus": (2.3, -12, -55, 40, -12, 0.12, 0.0),   # direct D : torse presque dos a la cible a l'armement
        "ribs": (2.3, 35, 45, -48, -12, 0.12, 0.5),      # crochet G : arc horizontal
        "body": (2.28, -8, -70, 42, -16, 0.62, 0.0),     # final : armement manga, fente profonde (ref Pro)
    }
    BACK, MID = 0.42, 0.15         # torse en retrait a l'armement / a mi-course (studs)

    def target_h(f, y, xl=0.0):
        """Point de la face avant du torse de la victime a la hauteur monde y
        (borne au torse : si l'epaule est trop haute, le point est plus haut
        que la cible voulue et le corps doit descendre)."""
        r, p = vw[f]["Torso"]
        t = (y - p[1] - r[1, 0] * xl - r[1, 2] * -0.55) / max(r[1, 1], 0.3)
        t = float(np.clip(t, -0.85, 0.85))
        return p + r @ np.array([xl, t, -0.55])

    def presolve(pose):
        """Racine du corps reellement obtenue (fitp resolu sur le rig)."""
        c, _res = solve_pose(rig, pose)
        return np.asarray(c["MasterControl"]["location"], float)

    plans = []
    for i, (c, s, kind) in enumerate(HITS):
        dist, az, wind, yaw, lean, low, xl = PLAN[kind]
        o = "L" if s == "R" else "R"
        # hauteur du pivot d'epaule dans la posture de contact -> cible a cette
        # hauteur (bras a -2 a -3 deg, comme les pros)
        probe = {"root": ((0.0, 0.0, 0.0), (0, 0, 0)), "pelvis": ((0, -low, 0), (lean, yaw, 0)), "chest": (0, 0.15, 0)}
        solve_pose(rig, probe)
        y_sh = float(torso_pivot(V.current_parts(rig), s)[1])
        tgt = target_h(c, y_sh - 0.1, xl)
        contact = {"root": ((0.0, 0.0, 0.0), (0, 0, 0)), "pelvis": ((0, -low, 0), (lean, yaw, 0)),
                   "chest": (0, 0.15, 0), "fitp": (s, tuple(tgt), dist, az), "look": head(c),
                   "hands": {s: ("w", tuple(tgt)), o: (("a", (150 if o == "R" else -150, -25, 2.1)) if kind == "chest"
                                                        else FACE[o])}}
        croot = presolve(contact)
        # appuis : pied avant (G) sous/juste derriere le bassin au contact, pied
        # arriere (D) 0,8 derriere ; tournes de la moitie du lacet de contact.
        # Fente (coup au corps) : appuis larges, pied avant DEVANT le bassin
        if kind == "body":
            lx, lz = _pivot(-0.6, -0.7, 0.5 * yaw)
            rx, rz = _pivot(0.6, 1.3, 0.5 * yaw)
        else:
            lx, lz = _pivot(-0.5, 0.12, 0.5 * yaw)
            rx, rz = _pivot(0.55, 0.8, 0.5 * yaw)
        feet = {"L": ("g", (croot[0] + lx, croot[2] + lz)), "R": ("g", (croot[0] + rx, croot[2] + rz))}
        contact["feet"] = feet
        contact["auto_low"] = True
        plans.append((c, s, o, kind, tgt, croot, feet, contact, yaw, wind, lean, low))

    def body(root, low, yaw, lean, f, hands, feet, chest=(0, 0.1, 0)):
        return {"root": (tuple(float(x) for x in root), (0, 0, 0)), "pelvis": ((0, -low, 0), (lean, yaw, 0)),
                "chest": chest, "look": head(f), "hands": hands, "feet": feet, "auto_low": True}

    back = lambda r, d: np.asarray(r) + np.array([0.0, 0.0, d])  # noqa: E731
    c0, _s0, _o0, _k0, _t0, r0, feet0, *_r = plans[0]
    add(0, body(back(r0, 0.3), 0.03, 0, -4, 0, GUARD(), feet0))
    add(3, body(back(r0, 0.4), 0.03, 0.5 * plans[0][9], -1, 3, {"L": side("L", 80, -18, 2.05), "R": GUARD()["R"]}, feet0))
    prev = None
    for i, (c, s, o, kind, tgt, croot, feet, contact, yaw, wind, lean, low) in enumerate(plans):
        lunge = kind == "body"
        # FORME du coup (mains, en azimut/elevation/distance depuis l'epaule) :
        # arme = pose tenue ; a5 / a3 = arc a hauteur d'epaule ; l'autre bras :
        # contre-rotation (jab), vise la cible (direct, final), garde au visage
        aim = {o: ("a", (wind, -12, 2.2))}
        if kind == "chest":        # jab : court, le bras vient du cote
            chamber = {s: side(s, 55, 0, 2.05), o: GUARD()[o]}
            a5 = {s: side(s, 45, 0, 2.1), o: GUARD()[o]}
            a3 = {s: side(s, 22, -2, 2.2), o: side(o, 95, -30, 2.05)}
        elif kind == "plexus":     # direct : arme en arriere, l'autre bras vise
            chamber = {s: side(s, 140, 5, 2.05), **aim}
            a5 = {s: side(s, 95, 2, 2.1), **aim}
            a3 = {s: side(s, 30, -2, 2.2), o: FACE[o]}
        elif kind == "ribs":       # crochet : sur le cote, arc horizontal
            chamber = {s: side(s, 105, 5, 2.05), o: FACE[o]}
            a5 = {s: side(s, 85, 0, 2.1), o: FACE[o]}
            a3 = {s: side(s, 45, -2, 2.2), o: FACE[o]}
        else:                      # final : poing arme haut derriere la tete (manga)
            chamber = {s: side(s, 150, 22, 2.0), **aim}
            a5 = {s: side(s, 110, 8, 2.05), **aim}
            a3 = {s: side(s, 35, -3, 2.2), o: FACE[o]}
        # de la garde (devant) a l'armement (derriere) : cle intermediaire sur
        # le cote, sinon le controle IK traverse le corps
        mid_arm = {s: side(s, 75, -25, 2.15), o: GUARD()[o]}
        # fente : le pied avant part en l'air pendant l'armement et se pose
        # juste avant le contact (pas d'entree, ref Pro 3,75 -> 4,25 s)
        (_m, (fx1, fz1)) = feet["L"]
        if prev is not None:
            pc, pfeet, proot = prev
            (_m, (fx0, fz0)) = pfeet["L"]
            (_m, (bx0, bz0)), (_m2, (bx1, bz1)) = pfeet["R"], feet["R"]
        if lunge:
            # pied arriere d'abord (pendant la recuperation), puis armement sur
            # le pied arriere, pied avant leve
            add(c - 13, body(0.5 * (back(proot, 0.3) + back(croot, 0.95)), 0.1, 0.3 * wind, -2, c - 13, mid_arm,
                             {"L": pfeet["L"], "R": ("w", (0.5 * (bx0 + bx1), 0.45, 0.5 * (bz0 + bz1)))}))
            lifted = {"L": ("w", (0.5 * (fx0 + fx1), 0.4, 0.5 * (fz0 + fz1))), "R": feet["R"]}
            add(c - 9, body(back(croot, 0.95), 0.25, wind, 3, c - 9, chamber,
                            {"L": ("w", (0.7 * fx0 + 0.3 * fx1, 0.3, 0.7 * fz0 + 0.3 * fz1)), "R": feet["R"]}))
            add(c - 5, body(back(croot, 0.6), 0.38, 0.7 * wind + 0.3 * yaw, 0.2 * lean, c - 5, a5, lifted))
            add(c - 2, body(back(croot, 0.15), 0.5, 0.25 * wind + 0.75 * yaw, 0.7 * lean, c - 2, a3, feet))
        else:
            if prev is not None:
                # le PAS, pendant la recuperation du coup precedent : pied avant
                # leve a mi-chemin, puis pied arriere qui suit, reposes avant l'armement
                mid_root = 0.5 * (back(proot, 0.3) + back(croot, BACK))
                add(c - 13, body(mid_root, 0.03, 0.5 * wind, -3, c - 13, mid_arm,
                                 {"L": ("w", (0.5 * (fx0 + fx1), 0.32, 0.5 * (fz0 + fz1))), "R": pfeet["R"]}))
                add(c - 10, body(back(croot, BACK), 0.03, 0.85 * wind, 2, c - 10, chamber,
                                 {"L": feet["L"], "R": ("w", (0.5 * (bx0 + bx1), 0.5, 0.5 * (bz0 + bz1)))}))
            # armement : torse au-dessus du pied arriere, TENU
            add(c - 7, body(back(croot, BACK), 0.03, wind, 3, c - 7, chamber, feet))
            # la hanche et le torse partent, la main suit en arc (cote puis devant),
            # et finit a L'HORIZONTALE
            add(c - 5, body(back(croot, 0.4), 0.5 * low, 0.7 * wind + 0.3 * yaw, 0.2 * lean, c - 5, a5, feet))
            add(c - 3, body(back(croot, MID), 0.8 * low, 0.35 * wind + 0.65 * yaw, 0.6 * lean, c - 3, a3, feet))
        add(c, contact, "LINEAR")
        # poussee : le poing accompagne la victime qui recule, le corps aussi
        t3 = target(c + 3, kind)
        push = np.clip(t3 - tgt, -0.18, 0.18)
        push[1] = 0.0
        # (le poing suit le CORPS, pas la victime : si elle recule plus loin
        # que la poussee, le bras resterait tendu hors de portee -> epaule haussee)
        # et si la victime se plie VERS le poing (plexus), le poing recule
        # avec sa surface au lieu d'y entrer
        fist3 = tgt + push
        surf3 = target_h(c + 3, float(tgt[1]), PLAN[kind][6])
        if surf3[2] > fist3[2] - 0.02:
            # ... et le corps recule d'autant : bras a la meme distance de
            # l'epaule (sinon main trop pres -> l'IK hausse l'epaule)
            fist3 = surf3 + np.array([0.0, 0.0, 0.04])
            push = fist3 - tgt
            push[1] = 0.0
        add(c + 3, body(croot + push, low, 1.1 * yaw, 1.1 * lean, c + 3,
                        {s: ("w", tuple(fist3)), o: contact["hands"][o]}, feet))
        # recuperation : torse revient entre les appuis, garde basse ; le bras
        # arriere repasse par le cote
        # extension TENUE (refs : le coup part en 2-3 f, l'extension dure)
        add(c + 6, body(croot + push, 0.9 * low, 1.05 * yaw, lean, c + 6,
                        {s: ("w", tuple(fist3)), o: contact["hands"][o]}, feet))
        add(c + 8, body(back(croot, 0.1), 0.8 * low, 0.7 * yaw, 0.5 * lean, c + 8,
                        {s: side(s, 30, -15, 2.15), o: side(o, 90, -35, 2.15) if kind == "chest" else GUARD()[o]}, feet))
        add(c + 10, body(back(croot, 0.3), max(0.03, 0.5 * low), 0.35 * yaw, -4, c + 10, GUARD(), feet))
        prev = (c, feet, croot)
    add(108, body(back(plans[-1][5], 0.3), 0.3, -12, -5, 108, GUARD(), plans[-1][6]))

    # v5 COUP CHARGE f118-170 (piste Saitama de Milan ; cerveau v2 :
    # ANGLES_MORTS.md 1, CERVEAU_V2.md). Remplace la boule accroupie
    # (f125-146, torse a 1,4 stud) et l'uppercut qui montait de 4 studs : c'est
    # ce que Milan voyait « partir d'en bas ». Ici :
    # - on se replace en 2 pas, appuis larges, genoux souples (pas de boule) ;
    # - ENROULEMENT : buste tourne dos a la cible, poing arme A HAUTEUR
    #   D'EPAULE derriere, l'autre bras vise ; tenue VIVANTE de 18 f (le buste
    #   continue de s'enrouler un peu : tension, pas gel) ;
    # - DEPART en 4 f : hanche puis buste puis bras, trajet A PLAT ;
    # - extension TENUE, l'autre bras tire en arriere (contre-rotation).
    s_, o_ = "R", "L"
    dist, az, wind, yaw, lean, low = 2.25, -8, -80, 45, -14, 0.3
    probe = {"root": ((0.0, 0.0, 0.0), (0, 0, 0)), "pelvis": ((0, -low, 0), (lean, yaw, 0)), "chest": (0, 0.15, 0)}
    solve_pose(rig, probe)
    y_sh = float(torso_pivot(V.current_parts(rig), s_)[1])
    tgt = target_h(UPPER_F, y_sh - 0.1)
    contact = {"root": ((0.0, 0.0, 0.0), (0, 0, 0)), "pelvis": ((0, -low, 0), (lean, yaw, 0)), "chest": (0, 0.15, 0),
               "fitp": (s_, tuple(tgt), dist, az), "look": head(UPPER_F),
               "hands": {s_: ("w", tuple(tgt)), o_: FACE[o_]}}
    croot = presolve(contact)
    lx, lz = _pivot(-0.6, -0.55, 0.5 * yaw)
    rx, rz = _pivot(0.65, 1.2, 0.5 * yaw)
    cfeet = {"L": ("g", (croot[0] + lx, croot[2] + lz)), "R": ("g", (croot[0] + rx, croot[2] + rz))}
    contact["feet"] = cfeet
    contact["auto_low"] = True
    aim = {o_: ("a", (wind, -12, 2.2))}
    pr, pf = plans[-1][5], plans[-1][6]
    (_m, (fx0, fz0)), (_m, (bx0, bz0)) = pf["L"], pf["R"]
    (_m, (fx1, fz1)), (_m, (bx1, bz1)) = cfeet["L"], cfeet["R"]
    # 2 pas pour se replacer (la victime a recule d'environ 1 stud)
    add(113, body(0.5 * (back(pr, 0.3) + back(croot, 0.6)), 0.15, -10, -4, 113, GUARD(),
                  {"L": ("w", (0.5 * (fx0 + fx1), 0.35, 0.5 * (fz0 + fz1))), "R": pf["R"]}))
    add(117, body(back(croot, 0.6), 0.18, 0.3 * wind, -2, 117, {s_: side(s_, 75, -25, 2.15), o_: GUARD()[o_]},
                  {"L": cfeet["L"], "R": ("w", (0.5 * (bx0 + bx1), 0.4, 0.5 * (bz0 + bz1)))}))
    # enroulement : le poing passe par le cote (arc) puis derriere l'epaule
    add(121, body(back(croot, 0.58), 0.24, 0.7 * wind, 2, 121, {s_: side(s_, 120, 3, 2.05), **aim}, cfeet))
    add(126, body(back(croot, 0.6), 0.3, wind, 4, 126, {s_: side(s_, 150, 5, 2.0), **aim}, cfeet))
    # tenue vivante : le buste continue de s'enrouler, le corps se ramasse un peu
    add(144, body(back(croot, 0.66), 0.34, wind - 7, 5, 144, {s_: side(s_, 156, 6, 2.0), **aim}, cfeet))
    # DEPART (4 f) : hanche et buste d'abord, le bras suit a plat
    add(146, body(back(croot, 0.45), 0.33, 0.55 * wind + 0.45 * yaw, 0.3 * lean, 146,
                  {s_: side(s_, 110, 3, 2.05), **aim}, cfeet))
    add(148, body(back(croot, 0.15), 0.31, 0.15 * wind + 0.85 * yaw, 0.75 * lean, 148,
                  {s_: side(s_, 35, -2, 2.2), o_: FACE[o_]}, cfeet))
    add(UPPER_F, contact, "LINEAR")
    # extension TENUE : le poing continue un peu devant, l'autre bras tire en arriere
    fwd = tgt - (croot + np.array([0.0, float(tgt[1] - croot[1]), 0.0]))
    fwd = fwd / max(1e-6, np.linalg.norm(fwd))
    ext = tgt + 0.12 * fwd
    add(153, body(croot + 0.12 * fwd, low, 1.1 * yaw, 1.1 * lean, 153,
                  {s_: ("w", tuple(ext)), o_: side(o_, 120, -30, 2.1)}, cfeet))
    add(158, body(croot + 0.12 * fwd, 0.9 * low, 1.05 * yaw, lean, 158,
                  {s_: ("w", tuple(ext)), o_: side(o_, 115, -30, 2.1)}, cfeet))
    zc = float(croot[2]) + 0.7
    # ACCROUPI de 8 f (reference : 8 f a 30 i/s) puis DECOLLAGE
    # v5 : on garde les appuis du coup charge (sinon le pied arriere glisse de 0,85 en 4 f)
    add(162, {"root": ((float(croot[0]), 0.0, zc - 0.8), (0, 0, 0)), "pelvis": ((0, -0.85, 0), (-24, 0, 0)), "chest": (0, 0.3, 0),
              "feet": cfeet, "look": head(162),
              "hands": {"R": ("w", (0.9, 1.5, zc - 0.1)), "L": ("w", (-0.9, 1.5, zc - 0.1))}})
    add(TAKEOFF_F - 2, {"root": ((float(croot[0]), 0.0, zc - 0.8), (0, 0, 0)), "pelvis": ((0, -0.9, 0), (-26, 0, 0)), "chest": (0, 0.32, 0),
                        "feet": cfeet, "look": head(TAKEOFF_F - 2),
                        "hands": {"R": ("w", (0.95, 1.45, zc + 0.1)), "L": ("w", (-0.95, 1.45, zc + 0.1))}}, "LINEAR")
    add(TAKEOFF_F + 4, {"root": ((0.0, 2.6, zc - 1.2), (0, 0, 0)), "pelvis": ((0, 0.0, 0), (8, 0, 0)), "chest": (0, 0, 0),
                        "feet": {"L": ("c", (0.0, -0.2, -0.05)), "R": ("c", (0.0, -0.3, -0.05))}, "look": head(TAKEOFF_F + 4),
                        "hands": {"R": ("c", (0.0, 0.0, 0.0)), "L": ("c", (0.0, 0.0, 0.0))}}, ("QUAD", "EASE_OUT"))
    # APEX et TEMPS SUSPENDU : au-dessus et en retrait de la victime,
    # poing arme loin derriere, genou leve, bras gauche qui vise vers le bas
    va = vw[APEX_F]["Torso"][1]
    ax_z = va[2] + 1.6
    # v2 (test de lisibilite de silhouette, build_manga) : la v1 se lisait
    # comme un bloc -> poing plus haut et plus loin derriere, bras avant
    # TENDU vers la cible, jambes en ciseau (genou haut devant, jambe arriere
    # tendue) : une silhouette en X qui se lit de profil
    def cocked(f, y, twist, lean, back, k=1.0):
        return {"root": ((0.0, y, ax_z), (0, 0, 0)), "pelvis": ((0, 0, 0), (lean, twist, -8)), "chest": (0, 0.2, 0),
                "feet": {"L": ("c", (0.0, 0.95 * k, 1.35 * k)), "R": ("c", (0.1, -1.15 * k, 0.55 * k))},
                "look": head(f),
                "hands": {"R": ("w", (1.2, y + 4.5 + 0.2 * k, ax_z + back)), "L": ("w", (-0.55, y + 1.6, ax_z - 2.5))}}
    add(APEX_F, cocked(APEX_F, 13.2, -40, 4, 1.9, 0.85))
    add(SUSPEND_END_F, cocked(SUSPEND_END_F, 13.7, -55, 8, 2.3, 1.0), "BEZIER")
    # PLONGEE : bascule en avant, poing vers le bas, contact en l'air
    tgt = target(STRIKE_F, "chest")
    add(266, {"root": ((0.0, 12.4, ax_z - 0.4), (-45, 0, 0)), "fit": ("R", tgt, (0.3, 3.2, 1.6), (1, 1, 1)), "pelvis": ((0, 0, 0), (-10, -20, 0)), "chest": (0, 0.3, 0),
              "feet": {"L": ("c", (0.0, 0.2, 0.6)), "R": ("c", (0.0, -0.5, 0.3))}, "look": head(266),
              "hands": {"R": ("rw", (1.15, 1.9, 1.5)), "L": ("rw", (-1.2, 2.7, 0.5))}})
    add(STRIKE_F, {"root": ((0.0, tgt[1] + 1.2, tgt[2] + 1.6), (-68, 0, 0)), "pelvis": ((0, 0, 0), (-8, 26, 0)),
                   "fit": ("R", tgt, (0.35, 1.55, 0.95), (1, 1, 1)),
                   "chest": (0, 0.2, 0), "feet": {"L": ("c", (0.0, -0.3, 0.2)), "R": ("c", (0.0, -0.6, 0.0))},
                   "look": head(STRIKE_F),
                   "hands": {"R": ("w", tuple(tgt)), "L": ("w", (-1.3, tgt[1] + 3.2, tgt[2] + 3.0))}}, "LINEAR")
    for f, rot, off in ((280, -62, (0.38, 1.7, 0.7)), (281, -59, (0.39, 1.75, 0.6)), (282, -55, (0.4, 1.8, 0.5)),
                        (285, -42, (0.45, 1.65, 0.6))):
        tg = target(f, "chest")
        add(f, {"root": ((0.0, tg[1] + 1.0, tg[2] + 1.5), (rot, 0, 0)), "pelvis": ((0, 0, 0), (-12, 22, 0)),
                "fit": ("R", tg, off, (1, 1, 1)), "chest": (0, 0.25, 0),
                "feet": {"L": ("c", (0.0, 0.0, 0.3)), "R": ("c", (0.0, -0.4, 0.1))}, "look": tuple(tg),
                "hands": {"R": ("w", tuple(tg)), "L": ("rw", (-1.4, 2.4, 0.6))}}, "LINEAR")
    # ECRASEMENT : atterrissage en garde basse, poing sur la victime au sol
    tg = target(IMPACT_F, "chest")
    zc2 = tg[2] + 1.35
    land = lambda f, low, fist_y, lean=-30: {  # noqa: E731
        "root": ((0.0, 0.0, zc2), (0, 0, 0)), "pelvis": ((0, -low, 0), (lean, 12, 0)), "chest": (0, 0.35, 0),
        "fit": ("R", (tg[0], fist_y, tg[2]), (0.55, 1.35, 0.75), (1, 0, 1)),
        "feet": {"L": ("rg", (-0.75, -0.95)), "R": ("rg", (0.75, 1.85))},
        "look": (tg[0], 0.4, tg[2] - 1.0) if f <= 306 else vw[f]["Head"][1],
        "hands": {"R": ("w", (tg[0], fist_y, tg[2])), "L": ("rw", (-1.7, 2.0 - (low - 1.1), -0.1))}}
    add(IMPACT_F, land(IMPACT_F, 0.95, tg[1]), "LINEAR")
    add(298, land(298, 0.98, float(target(298, "chest")[1])))
    add(301, land(301, 0.99, float(target(301, "chest")[1])))
    add(306, land(306, 1.02, 0.3))
    add(REVEAL_F, land(REVEAL_F, 1.0, 0.3))
    add(400, land(400, 0.94, 0.3, lean=-28))
    add(RISE_F[0], land(RISE_F[0], 1.0, 0.3))
    # RETOUR : se releve, garde relachee, regarde la victime au loin
    add(RISE_F[1], a_stance(zc2, low=0.2, yaw=-8, lean=-4, look=vw[RISE_F[1]]["Head"][1],
                            feet=a_feet(zc2, lf=(-0.6, -0.6), rf=(0.65, 0.5)),
                            hands={"L": ("w", (-1.3, 2.2, zc2 - 0.3)), "R": ("w", (1.35, 2.15, zc2 - 0.2))}))
    return K


# ---------------------------------------------------------------------

def build(blend):
    a = V.open_rig(blend)
    b = V.append_rig(blend, "Victime")
    for s in ("Right Arm", "Left Arm"):
        V.set_setting(s, "IK/FK", 1.0, rig=a)
        V.set_setting(s, "IK/FK", 0.0, rig=b)
    V.set_setting("Head", "Track Object", 1.0, rig=a)
    V.place(b, (0.0, D, 0.0), 180.0)
    return a, b


def interp_args(i):
    return (i, None) if isinstance(i, str) else i


# v5 (cerveau v2 : fluidite, ANGLES_MORTS.md 2) : Blender pose des poignees
# AUTO_CLAMPED, qui aplatissent la tangente a chaque cle ou un canal change de
# sens -> le membre s'arrete a chaque pose cle (rafale 9-12 traits/s contre 4-6
# chez les pros). Poignees AUTO sur les BRAS, le TORSE et la tete ; les PIEDS
# gardent AUTO_CLAMPED (un depassement ferait glisser un pied plante).
# Seulement AVANT le decollage : l'aerien et la fin, que Milan aime et qui
# sont deja fluides (3,5 traits/s), ne bougent pas (et y relacher les
# poignees faisait passer le poing sous le sol pendant l'atterrissage).
# DESACTIVE le 2026-09-24 : essaye sur la v5, il haussait l'epaule dans la
# rafale (0,33 stud, la main depassait vers le pivot et l'IK montait
# l'epaule) et la mesure de fluidite qui le justifiait s'est revelee
# confondue avec le tempo (hypotheses.json, fluidite). Outil garde.
RELAX_HANDLES = None
RELAX_UNTIL_F = TAKEOFF_F
# les cles qui ENCADRENT une tenue d'anticipation restent bridees : relachees,
# la courbe depassait pendant la tenue du coup charge (jambe avant sous le sol)
HOLD_KEYS = {126, 144}


def relax_handles(rig, kind=RELAX_HANDLES, until=RELAX_UNTIL_F, keep=HOLD_KEYS):
    if not kind:
        return
    arm = V._rig(rig).primary
    act = arm.animation_data.action if arm.animation_data else None
    if act is None:
        return
    for fc in V._fcurves(act):
        if "Leg" in fc.data_path or "Foot" in fc.data_path:
            continue
        for kp in fc.keyframe_points:
            if kp.interpolation == "BEZIER" and kp.co[0] < until and int(round(kp.co[0])) not in keep:
                kp.handle_left_type = kind
                kp.handle_right_type = kind
        fc.update()


def animate(a, b, keys_fn=None):
    import bpy
    S = bpy.context.scene
    S.render.fps = FPS
    S.frame_start, S.frame_end = 0, END_F
    report = {"victime": [], "attaquant": []}
    solved = []
    for f, p, i in victim_keys():
        c, res = solve_pose(b, p)
        solved.append((f, c, i))
        report["victime"].append((f, res))
    for f, c, i in solved:
        key_pose(b, f, c, *interp_args(i))
    relax_handles(b)
    vw = bake_world(b, 0, END_F)
    solved = []
    for f, p, i in attacker_keys(vw, a):
        c, res = solve_pose(a, p)
        solved.append((f, c, i))
        report["attaquant"].append((f, res))
    for f, c, i in solved:
        key_pose(a, f, c, *interp_args(i))
    relax_handles(a)
    aw = bake_world(a, 0, END_F)
    return aw, vw, report


def main(blend):
    a, b = build(blend)
    aw, vw, report = animate(a, b)
    worst = max((r for side in report.values() for _f, res in side for r in res.values()), default=0)
    print("residu IK max :", round(worst, 3), "stud")
    for side, rows in report.items():
        for f, res in rows:
            bad = {k: v for k, v in res.items() if v > 0.05}
            if bad:
                print(f"  {side} f{f}: {bad}")
    json.dump({"distance": D, "fps": FPS, "end_f": END_F, "markers": MARKERS, "impact_f": IMPACT_F,
               "strike_f": STRIKE_F, "hits": HITS, "upper_f": UPPER_F, "final_f": UPPER_F, "final_side": "R", "white": WHITE_F, "reveal_f": REVEAL_F,
               "manga_f": MANGA_F, "hit_hitstop": HIT_HITSTOP, "hit_shake": HIT_SHAKE, "hit_scale": HIT_SCALE,
               "residus": report}, open(os.path.join(OUT, "scene.json"), "w"), indent=1)
    return a, b, aw, vw


if __name__ == "__main__":
    main(sys.argv[1])
