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
HITS = [  # (frame de contact, main, cible sur la victime)
    (10, "R", "face"), (40, "L", "face"), (60, "R", "body"),
    (74, "L", "face"), (88, "R", "chin"), (108, "L", "body"),
]
UPPER_F = 150               # uppercut
TAKEOFF_F = 170
APEX_F = 200
SUSPEND_END_F = 256
STRIKE_F = 278              # le poing touche la victime en l'air
IMPACT_F = 288              # ecrasement au sol : impact frames
WHITE_F = (294, 322)        # ecran blanc puis brouillard
REVEAL_F = 322
RISE_F = (490, 526)

MARKERS = [("activation", 0)] + [(f"hit{i + 1}", f) for i, (f, _h, _t) in enumerate(HITS)] + [
    ("uppercut", UPPER_F), ("takeoff", TAKEOFF_F), ("suspend", APEX_F), ("dive", SUSPEND_END_F),
    ("strike", STRIKE_F), ("impact", IMPACT_F), ("white", WHITE_F[0]), ("reveal", REVEAL_F)]

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


def solve_pose(rig, p):
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
            if mode in ("w", "rw", "g", "rg"):
                if mode == "rw":
                    v = root + np.asarray(v)
                if mode == "rg":
                    v = (root[0] + v[0], root[2] + v[1])
                    mode = "g"
                if mode == "g":
                    v = np.array([v[0], FOOT_Y, v[1]])
                V.set_controls({ctrl: {"location": (0.0, 0.0, 0.0)}}, rig=rig)
                loc, r = V.solve_control_for_tip(ctrl, part, v, rig=rig, iters=25)
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
                        loc, r = V.solve_control_for_tip(ctrl, part, v, rig=rig, iters=25)
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


def victim_pose(back, y=0.0, rootrot=(0, 0, 0), pelvis=((0, -0.12, 0), (0, 0, 0)), chest=(0, 0, 0),
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
    stand = lambda back, **kw: victim_pose(back, **kw)  # noqa: E731
    add(0, stand(0.0))
    # H1 f10 : direct du droit au visage -> tete vers la gauche de l'attaquant
    add(10, stand(0.0), "LINEAR")
    add(13, stand(0.22, head=(24, -32, 6), pelvis=((0, -0.2, 0), (20, -16, 5)), arms=((-20, 0, 0), (-12, 0, 0))))
    add(24, stand(0.3, head=(6, -8, 0), pelvis=((0, -0.18, 0), (4, -4, 0))))
    # H2 f40 : crochet gauche au visage -> tete vers la droite
    add(40, stand(0.3, head=(2, -2, 0)), "LINEAR")
    add(43, stand(0.55, head=(18, 38, -8), pelvis=((0, -0.22, 0), (17, 22, -6)), arms=((-9, 0, 0), (-22, 0, 0))))
    add(54, stand(0.62, head=(4, 10, 0), pelvis=((0, -0.2, 0), (3, 4, 0))))
    # H3 f60 : corps -> se plie en avant, genoux qui cedent
    add(60, stand(0.62, head=(2, 6, 0)), "LINEAR")
    add(63, stand(1.1, head=(-22, 0, 0), pelvis=((0, -0.55, 0), (-32, 0, 0)), chest=(0, 0.25, 0),
                  arms=((30, 0, 0), (26, 0, 0))))
    add(72, stand(1.12, head=(-14, 0, 0), pelvis=((0, -0.5, 0), (-22, 0, 0)), chest=(0, 0.2, 0),
                  arms=((30, 0, 0), (30, 0, 0))))
    # H4 f74 : direct gauche -> la tete remonte d'un coup
    add(74, stand(1.12, head=(-12, 0, 0), pelvis=((0, -0.5, 0), (-20, 0, 0)), arms=((28, 0, 0), (28, 0, 0))), "LINEAR")
    add(77, stand(1.35, head=(34, 6, 0), pelvis=((0, -0.3, 0), (14, 0, 0)), arms=((-15, 0, 0), (-18, 0, 0))))
    add(86, stand(1.4, head=(10, 2, 0), pelvis=((0, -0.25, 0), (2, 0, 0))))
    # H5 f88 : coup montant au menton -> decolle
    add(88, stand(1.4, head=(8, 0, 0)), "LINEAR")
    add(91, victim_pose(1.6, y=0.55, head=(42, 0, 0), pelvis=((0, 0, 0), (22, 0, 0)), arms=((-60, 0, 0), (-55, 0, 0)),
                        feet=AIR_LEGS))
    add(100, victim_pose(1.85, y=1.15, head=(26, 0, 0), pelvis=((0, 0, 0), (16, 0, 0)), arms=((-40, 0, 0), (-45, 0, 0)),
                         feet=AIR_LEGS))
    # H6 f108 : au corps en l'air (juggle)
    add(108, victim_pose(1.95, y=1.2, head=(18, 0, 0), pelvis=((0, 0, 0), (10, 0, 0)), arms=((-30, 0, 0), (-35, 0, 0)),
                         feet=AIR_LEGS), "LINEAR")
    add(111, victim_pose(2.45, y=1.4, head=(-24, 0, 0), pelvis=((0, 0, 0), (-32, 0, 0)), chest=(0, 0.3, 0),
                         arms=((50, 0, 0), (45, 0, 0)), feet=TUMBLE_LEGS))
    add(126, stand(2.6, head=(-16, 0, 0), pelvis=((0, -0.75, 0), (-24, 0, 4)), chest=(0, 0.25, 0),
                   arms=((22, 0, 0), (18, 0, 0))), "BEZIER")
    # sonnee, affaissee, pendant l'anticipation
    add(146, stand(2.6, head=(-12, 4, 0), pelvis=((0, -0.7, 0), (-18, 3, 6)), chest=(0, 0.2, 0),
                   arms=((18, 0, 0), (14, 0, 0))), "LINEAR")
    # UPPERCUT f150 -> lancee en l'air, bascule en arriere
    add(UPPER_F, stand(2.6, head=(-10, 4, 0), pelvis=((0, -0.7, 0), (-16, 3, 6)), arms=((18, 0, 0), (14, 0, 0))),
        "LINEAR")
    add(154, victim_pose(2.9, y=1.6, rootrot=(22, 0, 0), head=(48, 0, 0), pelvis=((0, 0, 0), (20, 0, 0)),
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
    # dans le blanc : rebond et ejection au loin (degage des 291 : le poing
    # de l'attaquant descend au sol derriere elle)
    add(291, victim_pose(5.0, y=LIE_Y + 0.9, rootrot=(98, 0, 6), head=(-6, 0, 0), arms=((-95, 0, 40), (-95, 0, -40)),
                         feet=TUMBLE_LEGS))
    add(298, victim_pose(8.0, y=LIE_Y + 2.6, rootrot=(128, 0, 20), head=(20, 0, 0), arms=((-120, 0, 40), (-110, 0, -50)),
                         feet=TUMBLE_LEGS))
    add(314, victim_pose(15.2, y=LIE_Y + 0.05, rootrot=(90, 0, 6), head=(0, 28, 0), pelvis=((0, 0, 0), (-4, 0, 6)),
                         arms=((-150, 0, 50), (-20, 0, -60)), feet=LIE_LEGS, ground=True))
    add(322, victim_pose(15.6, y=LIE_Y, rootrot=(90, 0, 4), head=(0, 32, 0), pelvis=((0, 0, 0), (-2, 0, 5)),
                         arms=((-155, 0, 52), (-18, 0, -62)), feet=LIE_LEGS, ground=True))
    add(END_F, victim_pose(15.6, y=LIE_Y, rootrot=(90, 0, 4), head=(0, 34, 0), pelvis=((0, 0, 0), (-2, 0, 5)),
                           arms=((-155, 0, 52), (-18, 0, -62)), feet=LIE_LEGS, ground=True))
    return K


# ---------------------------------------------------------------------
# ATTAQUANT (origine, regarde -Z). z negatif = en avant.

def a_feet(z, lf=(-0.62, -0.85), rf=(0.72, 0.6)):
    """pieds plantes : gauche devant, droit derriere (garde orthodoxe)."""
    return {"L": ("g", (lf[0], z + lf[1])), "R": ("g", (rf[0], z + rf[1]))}


def a_stance(z, low=0.45, yaw=-18, lean=-10, look=None, hands=None, feet=None, chest=(0, 0.1, 0)):
    p = {"root": ((0.0, 0.0, z), (0, 0, 0)), "pelvis": ((0, -low, 0), (lean, yaw, 0)), "chest": chest,
         "feet": feet or a_feet(z)}
    p["hands"] = hands or {"L": ("w", (-0.45, 3.45 - low, z - 1.35)), "R": ("w", (0.5, 3.2 - low, z - 0.85))}
    if look is not None:
        p["look"] = look
    return p


def attacker_keys(vw):
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
        if kind == "body":
            return p + r @ np.array([0, -0.35, -0.52])
        return p + r @ np.array([0, 0.2, -0.55])         # "chest" : face avant du torse

    K = []
    add = lambda f, p, i="BEZIER": K.append((f, p, i))  # noqa: E731
    # activation : garde, flash blanc
    add(0, a_stance(0.0, look=head(0)))
    for i, (c, s, kind) in enumerate(HITS):
        tgt = target(c, kind)
        z = float(tgt[2]) + (2.25 if kind != "body" else 2.05)
        lowc = 0.55 if kind != "chin" else 0.35
        if s == "R":
            wind_yaw, hit_yaw = -55, 45
            chamber = ("w", (0.95, 3.05 - lowc, z + 0.3))
            other_c = ("w", (-0.45, 3.4 - lowc, z - 1.1))
            other_hit = ("w", (-0.85, 3.1 - lowc, z + 0.7))
        else:
            wind_yaw, hit_yaw = 35, -45
            chamber = ("w", (-0.95, 3.05 - lowc, z + 0.2))
            other_c = ("w", (0.5, 3.3 - lowc, z - 0.8))
            other_hit = ("w", (0.9, 3.1 - lowc, z + 0.65))
        o = "L" if s == "R" else "R"
        mid = 0.45 * np.asarray(tgt) + 0.55 * np.asarray(chamber[1])
        # verdict corpus v1 : coups trop secs (bras 4 200 deg/s contre 2 100
        # max chez le pro, action 6 f contre 8-19) et torse trop peu tourne
        # (43 deg contre 67-131) -> armement a c-10, tenu, action de 7 f
        # armement qui claque puis se TIENT (la main recule, le torse s'enroule)
        if c - 10 > 0:
            add(c - 10, a_stance(z + 0.1, low=lowc - 0.05, yaw=wind_yaw * 0.85, lean=-6, look=head(c - 10),
                                 hands={s: chamber, o: other_c}))
        add(c - 7, a_stance(z + 0.12, low=lowc - 0.02, yaw=wind_yaw, lean=-7, look=head(c - 7),
                            hands={s: chamber, o: other_c}))
        # la main MENE (deja a mi-trajet quand le torse commence a peine)
        add(c - 3, a_stance(z, low=lowc, yaw=wind_yaw * 0.35 + hit_yaw * 0.65 * 0.4, lean=-12, look=head(c - 3),
                            hands={s: ("w", tuple(mid)), o: other_c}))
        # contact : l'autre bras tire en arriere
        add(c, a_stance(z - 0.05, low=lowc + 0.05, yaw=hit_yaw, lean=-16, look=head(c),
                        hands={s: ("w", tuple(tgt)), o: other_hit}), "LINEAR")
        # suite : 2 f sur la cible (la victime recule), puis retour en garde
        # au corps, la victime se plie VERS le poing : on le retire
        tg2 = np.asarray(tgt) + (np.array([0, 0.05, 0.3]) if kind == "body" else np.array([0, 0, -0.1]))
        add(c + 2, a_stance(z - 0.05, low=lowc + 0.05, yaw=hit_yaw + 6, lean=-17, look=head(c + 2),
                            hands={s: ("w", tuple(tg2)), o: other_hit}))
        nxt = HITS[i + 1][0] - 10 if i + 1 < len(HITS) else 118
        if nxt - (c + 2) > 10:
            add(c + 9, a_stance(z - 0.1, low=0.5, yaw=hit_yaw * 0.4 - 10, lean=-11, look=head(c + 9)))

    # ANTICIPATION 118-146 : fente tres basse, poing arme a la hanche, glisse
    zc = -2.0
    lunge_feet = lambda z: a_feet(z, lf=(-0.75, -1.35), rf=(0.95, 1.25))  # noqa: E731
    add(118, a_stance(zc + 0.05, low=0.5, yaw=-20, lean=-12, look=head(118)))
    add(126, {"root": ((0.0, 0.0, zc - 0.2), (0, 0, 0)), "pelvis": ((0, -1.35, 0), (-24, -52, -4)), "chest": (0, 0.3, 0),
              "feet": lunge_feet(zc - 0.2), "look": head(126),
              "hands": {"R": ("w", (0.95, 1.55, zc + 0.05)), "L": ("w", (-0.55, 2.35, zc - 1.75))}})
    add(144, {"root": ((0.0, 0.0, zc - 0.45), (0, 0, 0)), "pelvis": ((0, -1.42, 0), (-26, -58, -5)), "chest": (0, 0.32, 0),
              "feet": lunge_feet(zc - 0.45), "look": head(144),
              "hands": {"R": ("w", (1.0, 1.45, zc - 0.25)), "L": ("w", (-0.6, 2.3, zc - 2.0))}}, "LINEAR")
    # UPPERCUT : snap 4 f, le corps se deplie de bas en haut
    tgt = target(UPPER_F, "chin")
    add(146, {"root": ((0.0, 0.0, zc - 0.5), (0, 0, 0)), "pelvis": ((0, -1.3, 0), (-22, -45, -4)), "chest": (0, 0.3, 0),
              "feet": lunge_feet(zc - 0.45), "look": head(146),
              "hands": {"R": ("w", (1.0, 1.55, zc - 0.4)), "L": ("w", (-0.65, 2.35, zc - 1.9))}})
    add(148, {"root": ((0.0, 0.0, zc - 0.6), (0, 0, 0)), "pelvis": ((0, -0.9, 0), (-8, -8, 0)), "chest": (0, 0.2, 0),
              "feet": lunge_feet(zc - 0.45), "look": head(148),
              "hands": {"R": ("w", tuple(0.55 * tgt + 0.45 * np.array([1.0, 1.45, zc - 0.25]))),
                        "L": ("w", (-0.8, 2.6, zc - 1.0))}})
    add(UPPER_F, {"root": ((0.0, 0.0, zc - 0.7), (0, 0, 0)), "pelvis": ((0, -0.6, 0), (10, 28, 4)), "chest": (0, 0.0, 0),
                  "feet": a_feet(zc - 0.6, lf=(-0.7, -0.95), rf=(0.85, 0.85)), "look": head(UPPER_F),
                  "hands": {"R": ("w", tuple(tgt)), "L": ("w", (-0.95, 3.0, zc + 0.1))}}, "LINEAR")
    # suite : sur la pointe des pieds, poing au ciel
    add(157, {"root": ((0.0, 0.25, zc - 0.75), (0, 0, 0)), "pelvis": ((0, 0.0, 0), (16, 38, 6)), "chest": (0, -0.1, 0),
              "feet": {"L": ("c", (0.0, 0.1, 0.1)), "R": ("c", (0.0, -0.2, 0.25))}, "look": head(UPPER_F) + np.array([0, 1.5, 0]),
              "hands": {"R": ("w", (0.4, 6.4, zc - 1.3)), "L": ("w", (-1.1, 3.0, zc + 0.2))}})
    # ACCROUPI de 8 f (reference : 8 f a 30 i/s) puis DECOLLAGE
    add(162, {"root": ((0.0, 0.0, zc - 0.8), (0, 0, 0)), "pelvis": ((0, -0.85, 0), (-24, 0, 0)), "chest": (0, 0.3, 0),
              "feet": a_feet(zc - 0.8, lf=(-0.6, -0.7), rf=(0.6, 0.6)), "look": head(162),
              "hands": {"R": ("w", (0.9, 1.5, zc - 0.1)), "L": ("w", (-0.9, 1.5, zc - 0.1))}})
    add(TAKEOFF_F - 2, {"root": ((0.0, 0.0, zc - 0.8), (0, 0, 0)), "pelvis": ((0, -0.9, 0), (-26, 0, 0)), "chest": (0, 0.32, 0),
                        "feet": a_feet(zc - 0.8, lf=(-0.6, -0.7), rf=(0.6, 0.6)), "look": head(TAKEOFF_F - 2),
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
        "look": (tg[0], 0.4, tg[2] - 1.0) if f <= 296 else vw[f]["Head"][1],
        "hands": {"R": ("w", (tg[0], fist_y, tg[2])), "L": ("rw", (-1.7, 2.0 - (low - 1.1), -0.1))}}
    add(IMPACT_F, land(IMPACT_F, 0.95, tg[1]), "LINEAR")
    add(291, land(291, 0.98, float(target(291, "chest")[1])))
    add(296, land(296, 1.02, 0.3))
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
    vw = bake_world(b, 0, END_F)
    solved = []
    for f, p, i in attacker_keys(vw):
        c, res = solve_pose(a, p)
        solved.append((f, c, i))
        report["attaquant"].append((f, res))
    for f, c, i in solved:
        key_pose(a, f, c, *interp_args(i))
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
               "strike_f": STRIKE_F, "hits": HITS, "upper_f": UPPER_F, "white": WHITE_F, "reveal_f": REVEAL_F,
               "residus": report}, open(os.path.join(OUT, "scene.json"), "w"), indent=1)
    return a, b, aw, vw


if __name__ == "__main__":
    main(sys.argv[1])
