"""
« Un seul coup » (Serious Punch) : cinématique sur deux rigs V2.22, 60 fps.

Conception : animator_brain/corpus/fiches/UN_SEUL_COUP.md (Serious Punch TSB,
Serious Punch 2 et Serious Punch de Pew relus à 0,1 s ; fiche COUP_CHARGE.md).
Réutilise les solveurs de pose du Poing du Dragon (dragon_clip.py : même
grammaire de pose, même repère Roblox : x droite, y haut, l'attaquant regarde
-Z ; la victime est à DV studs devant lui, tournée vers lui).

Découpage (frames, 60 i/s) :
  0-78     entrée : de dos, debout, bras ballants
  78-156   CALME : debout face à la victime, presque rien
  156-183  départ : il se ramasse, part
  183-234  approche : glissade en fente très basse, torse presque horizontal
  234-261  armé : se relève en tordant le buste, poing à la hanche, genou haut ; tenue qui tremble
  261-283  frappe : le pied avant se plante, le bassin tourne, le poing part droit
  283      contact (sauté à l'écran : 2 images inversées, blanc)
  283-630  fente basse TENUE, poing tendu (conséquence)
  630-750  il se redresse lentement, main à la hanche, regarde au loin

Usage : python3 coup_clip.py /chemin/Blender_R6.blend
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("USC_OUT") or os.path.join(HERE, "..", "output")
DRAGON = os.path.join(HERE, "..", "..", "r6_poing_dragon", "scripts")
sys.path.insert(0, DRAGON)
sys.path.insert(0, os.path.join(HERE, "..", "..", "_shared"))

import dragon_clip as M  # noqa: E402  (solveurs de pose, repère, victime)
from animator_brain import v222_rig as V  # noqa: E402

FPS = 60
DV = 16.0                   # distance initiale de la victime (studs, le long de -Z)
M.D = DV                    # victim_pose / v_world de dragon_clip lisent ce global
END_F = 750                 # 12,5 s
CALME_F = 78
DEPART_F = 156              # il se ramasse (plan serré sur ses jambes)
LANCE_F = 170               # il PART : le sol casse sous lui, il est là-bas en 3 images
ARRIVEE_F = 173
CHARGE_F = 186              # coupe : il est déjà devant la victime et CHARGE son poing
TENUE_F = 222               # buste enroulé, poing au plus loin derrière ; tenue qui tremble
FRAPPE_F = 271              # départ du coup
CONTACT_F = 283
INVERSE_F = (283, 291)      # 2 images inversées (2 x 4 i)
BLANC_F = (291, 321)        # blanc 0,2 s puis dissolution 0,3 s
CONSEQ_F = (321, 516, 618)  # 3 plans de conséquence
REDRESSE_F = (630, 705)
MARKERS = [("activation", 0), ("calme", CALME_F), ("depart", DEPART_F), ("lance", LANCE_F),
           ("charge", CHARGE_F), ("frappe", FRAPPE_F), ("contact", CONTACT_F), ("blanc", BLANC_F[0]),
           ("consequence", CONSEQ_F[0]), ("redresse", REDRESSE_F[0])]


def world_parts_head(vw, f):
    return np.asarray(vw[f]["Head"][1], float)


# ---------------------------------------------------------------------
# VICTIME (repère local de dragon_clip : back = recul le long de -Z monde)

GUARD = ((-72, 0, -14), (-84, 0, 16))           # garde : avant-bras levés devant le torse (FK)


def victim_keys():
    K = []
    add = lambda f, p, i="BEZIER": K.append((f, p, i))  # noqa: E731
    vp = M.victim_pose
    # garde qui respire (vivante, jamais figée) ; DEBOUT : sa poitrine doit
    # être à hauteur d'épaule de l'attaquant (v1 : garde accroupie -0,2 +
    # attaquant penché 40° -> le poing tapait le bas-ventre, « vers le bas »)
    for f, k in ((0, 0), (46, 1), (96, 0), (146, 1), (ARRIVEE_F, 0)):
        add(f, vp(0.0, pelvis=((0, -0.06 - 0.015 * k, 0), (-4 - k, 0, 0)), chest=(0, 0.08, 0), head=(-3 + k, 0, 0),
                  arms=((GUARD[0][0] - 3 * k, 0, GUARD[0][2]), (GUARD[1][0] - 3 * k, 0, GUARD[1][2]))))
    # il apparaît d'un coup devant elle : sursaut (4 i), puis figée, elle tremble
    add(ARRIVEE_F + 4, vp(0.25, pelvis=((0, -0.02, 0), (10, 0, 0)), chest=(0, -0.08, 0), head=(12, 0, 0),
                          arms=((-122, 0, -20), (-128, 0, 22))), "LINEAR")
    for f, k in ((200, 1), (228, -1), (252, 1), (270, -1)):
        add(f, vp(0.25, pelvis=((0, -0.04, 0), (7 + 0.6 * k, 0.4 * k, 0)), chest=(0, -0.05, 0), head=(8 + k, 0.8 * k, 0),
                  arms=((-114 - 2 * k, 0, -14), (-120 + 2 * k, 0, 16))))
    add(CONTACT_F, vp(0.25, pelvis=((0, -0.04, 0), (6, 0, 0)), chest=(0, -0.05, 0), head=(7, 0, 0),
                      arms=((-112, 0, -12), (-118, 0, 14))), "LINEAR")
    # le coup : pliée autour du poing, puis ÉJECTÉE le long de -Z (pendant le
    # blanc) ; elle file vers l'horizon en tournant (un point au loin)
    add(CONTACT_F + 2, vp(0.9, y=0.2, rootrot=(-18, 0, 0), head=(-30, 0, 0), pelvis=((0, 0, 0), (-34, 0, 0)),
                          chest=(0, 0.35, 0), arms=((-40, 0, 10), (-40, 0, -10)), feet=M.AIR_LEGS), "LINEAR")
    add(292, vp(9.0, y=1.4, rootrot=(-30, 0, 6), head=(-20, 0, 0), pelvis=((0, 0, 0), (-30, 0, 0)),
                chest=(0, 0.3, 0), arms=((30, 0, 20), (30, 0, -20)), feet=M.AIR_LEGS), "LINEAR")
    add(310, vp(34.0, y=3.2, rootrot=(-90, 0, 20), head=(10, 0, 0), arms=((80, 0, 40), (70, 0, -40)),
                feet=M.TUMBLE_LEGS), "LINEAR")
    add(340, vp(68.0, y=4.6, rootrot=(-200, 0, 40), head=(20, 0, 0), arms=((100, 0, 60), (60, 0, -50)),
                feet=M.TUMBLE_LEGS), "LINEAR")
    add(400, vp(125.0, y=5.4, rootrot=(-380, 0, 70), arms=((120, 0, 60), (40, 0, -60)), feet=M.TUMBLE_LEGS), "LINEAR")
    add(470, vp(180.0, y=4.0, rootrot=(-540, 0, 90), arms=((120, 0, 60), (40, 0, -60)), feet=M.TUMBLE_LEGS), "LINEAR")
    add(END_F, vp(205.0, y=3.2, rootrot=(-600, 0, 100), arms=((120, 0, 60), (40, 0, -60)), feet=M.TUMBLE_LEGS))
    return K


# ---------------------------------------------------------------------
# ATTAQUANT (origine, regarde -Z)

def feet_at(z, lx=-0.5, lz=-0.1, rx=0.55, rz=0.2):
    return {"L": ("g", (lx, z + lz)), "R": ("g", (rx, z + rz))}


HANG = {"R": ("d", ((0.24, -1.0, 0.06), 1.9)), "L": ("d", ((-0.24, -1.0, 0.06), 1.9))}


def attacker_keys(vw, rig):
    """v2 (retour de Milan sur la v1, 2026-09-26) :
    - « la scène où le perso réduit la distance : il doit aller ultra vite,
      tu casses le sol de son point de départ, puis la scène apparaît avec le
      moment où il charge son poing et frappe » -> plus de glissade : il part
      en 3 images, le sol casse, coupe sur la CHARGE devant la victime ;
    - « le perso frappait vers le bas (comme dans le Poing du Dragon) ; il
      charge son poing, il l'arme en le ramenant à l'arrière et en tournant
      son buste » (refs : Gon accroupi poing à la hanche, Saitama manga, poing
      rouge) -> mesuré sur la v1 : buste penché 40°, poing à 2,5 studs du sol
      (bas-ventre), bras à -25° pendant l'armé. Ici : appuis larges, buste
      presque droit (12-16°), buste qui TOURNE (épaule droite en arrière,
      jusqu'à -66°), poing ramené derrière à hauteur de hanche/poitrine, puis
      coup À PLAT, épaule en avant, poing à hauteur de poitrine (COUP_CHARGE
      §1 : « tourner son buste vers la droite pour charger son poing droit,
      plier les jambes, le 2e bras placé, et boum il envoie »)."""
    K = []
    add = lambda f, p, i="BEZIER": K.append((f, p, i))  # noqa: E731
    head = lambda f: tuple(world_parts_head(vw, f))  # noqa: E731

    def idle(f, z, k):
        """debout, bras ballants, visage plat ; k = phase de respiration (-1..1)"""
        return {"root": ((0.0, 0.0, z), (0, 0, 0)), "pelvis": ((0, -0.03 + 0.012 * k, 0), (1 + 0.6 * k, 0, 0)),
                "chest": (0, 0.05 + 0.012 * k, 0), "feet": feet_at(0.0), "hands": HANG, "look": head(f)}
    # ENTRÉE + CALME : presque rien ; la respiration est lente (1,3 s)
    for f, k in ((0, 0), (39, 1), (78, 0), (117, 1), (DEPART_F, 0)):
        add(f, idle(f, 0.0, k))
    # DÉPART : il se ramasse, TRÈS bas (le sol va casser sous cette poussée)
    add(LANCE_F, {"root": ((0.0, 0.0, 0.1), (0, 0, 0)), "pelvis": ((0, -0.8, 0), (-26, -8, 0)), "chest": (0, 0.3, 0),
                  "feet": feet_at(0.0, lx=-0.6, lz=-0.3, rx=0.65, rz=0.45), "look": head(LANCE_F), "auto_low": True,
                  "hands": {"R": ("d", ((0.35, -0.7, 0.65), 1.9)), "L": ("d", ((-0.35, -0.7, 0.6), 1.9))}}, "LINEAR")

    # LA CHARGE, devant la victime. Pose de base : appuis larges (pied gauche
    # devant, droit derrière), jambes pliées, buste presque droit qui TOURNE.
    za = -11.3
    chest_v = lambda f: np.asarray(vw[f]["Torso"][1], float) + np.array([0.0, 0.3, 0.55])  # noqa: E731
    stance = {"L": ("g", (-0.75, za - 0.95)), "R": ("g", (0.85, za + 1.0))}

    def charge(f, twist, fist_back, low=0.48, lean=-9, wig=(0.0, 0.0), i="BEZIER"):
        # poing ramené DERRIÈRE, à hauteur de hanche / bas de poitrine
        fist = np.array([0.55, -0.22, fist_back]) + np.array([wig[0], wig[1], 0.0]) * 0.035
        return {"root": ((0.0, 0.0, za), (0, 0, 0)), "pelvis": ((0, -low, 0), (lean, twist, 0)), "chest": (0, 0.08, 0),
                "feet": stance, "auto_low": True,
                "hands": {"R": ("d", (tuple(fist), 1.95)), "L": ("a", (-12, -18, 1.95))},
                "look": head(f)}
    # arrivée (3 images de voyage : le corps file, les membres traînent)
    add(ARRIVEE_F, charge(ARRIVEE_F, -18, 0.4, low=0.62, lean=-18), "LINEAR")
    # le buste s'ENROULE : l'épaule droite part en arrière, le poing avec
    add(CHARGE_F, charge(CHARGE_F, -32, 0.65, low=0.55, lean=-16))
    add(200, charge(200, -48, 0.85))
    add(TENUE_F, charge(TENUE_F, -62, 1.0, low=0.52))
    # tenue qui TREMBLE, la torsion monte encore un peu (la tension, pas un gel)
    for f, w, tw in ((232, (3, 2), -63), (242, (-2, 3), -64), (252, (2, -2), -65), (262, (-3, -1), -66)):
        add(f, charge(f, tw, 1.0, low=0.53, wig=w))
    add(FRAPPE_F, charge(FRAPPE_F, -66, 1.02, low=0.54), "LINEAR")

    # FRAPPE : le bassin et le buste tournent d'abord (le poing traîne,
    # fouet), l'épaule droite passe DEVANT, le bras part à PLAT ; contact
    # exact sur la POITRINE, à hauteur d'épaule
    s_ = "R"
    low, lean, yaw = 0.22, -5, 42
    probe = {"root": ((0.0, 0.0, 0.0), (0, 0, 0)), "pelvis": ((0, -low, 0), (lean, yaw, 0)), "chest": (0, 0.06, 0)}
    M.solve_pose(rig, probe)
    y_sh = float(M.torso_pivot(V.current_parts(rig), s_)[1])
    r, p = vw[CONTACT_F]["Torso"]
    t = float(np.clip((y_sh + 0.1 - p[1] - r[1, 2] * -0.55) / max(r[1, 1], 0.3), -0.75, 0.75))
    tgt = p + r @ np.array([0.0, t, -0.55])
    hikite = ("a", (-150, -30, 2.0))
    contact = {"root": ((0.0, 0.0, 0.0), (0, 0, 0)), "pelvis": ((0, -low, 0), (lean, yaw, 0)), "chest": (0, 0.06, 0),
               "fitp": (s_, tuple(tgt), 2.15, -4), "look": tuple(tgt + np.array([0.0, 0.5, -2.0])),
               "hands": {s_: ("w", tuple(tgt)), "L": hikite}}
    c, _res = M.solve_pose(rig, contact)
    croot = np.asarray(c["MasterControl"]["location"], float)
    lx, lz = M._pivot(-0.75, -0.9, 0.4 * yaw)
    rx, rz = M._pivot(0.85, 1.25, 0.4 * yaw)
    cfeet = {"L": ("g", (croot[0] + lx, croot[2] + lz)), "R": ("g", (croot[0] + rx, croot[2] + rz))}
    contact["feet"] = cfeet
    contact["auto_low"] = True
    # le bassin part, le poing reste derrière
    add(275, {"root": ((0.0, 0.0, 0.5 * (za + croot[2])), (0, 0, 0)), "pelvis": ((0, -0.44, 0), (-9, -40, 0)),
              "chest": (0, 0.08, 0), "feet": cfeet, "auto_low": True,
              "hands": {"R": ("d", ((0.6, -0.2, 0.9), 1.95)), "L": ("a", (-40, -25, 1.95))},
              "look": head(275)}, "LINEAR")
    # buste de face, le poing passe à la hanche (à plat)
    add(279, {"root": ((0.0, 0.0, croot[2] + 0.15), (0, 0, 0)), "pelvis": ((0, -0.38, 0), (-8, 5, 0)),
              "chest": (0, 0.08, 0), "feet": cfeet, "auto_low": True,
              "hands": {"R": ("a", (70, -8, 2.05)), "L": ("a", (-120, -30, 2.0))}, "look": tuple(tgt)}, "LINEAR")
    add(281, {"root": ((0.0, 0.0, croot[2] + 0.05), (0, 0, 0)), "pelvis": ((0, -0.33, 0), (-6, 28, 0)),
              "chest": (0, 0.07, 0), "feet": cfeet, "auto_low": True,
              "hands": {"R": ("d", ((-0.05, 0.0, -1.0), 2.05)), "L": hikite}, "look": tuple(tgt)}, "LINEAR")
    add(CONTACT_F, contact, "LINEAR")
    # suite : l'épaule passe encore un peu devant, puis l'EXTENSION est TENUE,
    # bras à plat vers l'horizon (la victime est partie)
    ext = tgt + np.array([0.0, 0.0, -0.15])

    def tenue(f, k=0.0, lowk=0.0):
        p_ = dict(contact)
        p_["root"] = ((float(croot[0]), float(croot[1]), float(croot[2]) - 0.08), (0, 0, 0))
        p_.pop("fitp", None)
        p_["pelvis"] = ((0, -(low + lowk) + 0.012 * k, 0), (lean - 2 + 0.5 * k, yaw + 4, 0))
        # bras À PLAT vers l'horizon (direction, pas point : le corps se
        # tasse un peu, un point fixe devenait hors d'atteinte de 0,4 stud)
        p_["hands"] = {s_: ("d", ((-0.03, 0.2 + 0.004 * k, -1.0), 2.05)), "L": ("a", (-152, -32, 2.0))}
        p_["look"] = tuple(tgt + np.array([0.0, 0.3, -30.0]))
        return p_
    add(CONTACT_F + 3, tenue(CONTACT_F + 3, 0, 0.04))
    add(300, tenue(300, 0, 0.06))
    for f, k in ((380, 1), (460, -1), (540, 1), (REDRESSE_F[0], 0)):
        add(f, tenue(f, k, 0.06))
    # REDRESSEMENT : lent ; le bras tendu retombe, pied arrière ramené,
    # main à la hanche (« dans la poche »), il regarde au loin
    zr = float(croot[2]) - 0.08
    far = (0.0, 3.4, zr - 250.0)
    add(660, {"root": ((float(croot[0]), 0.0, zr), (0, 0, 0)), "pelvis": ((0, -0.3, 0), (-8, 24, 0)), "chest": (0, 0.1, 0),
              "feet": cfeet, "auto_low": True, "look": far,
              "hands": {"R": ("d", ((0.1, -0.55, -0.85), 1.95)), "L": ("d", ((-0.3, -0.9, 0.3), 1.9))}})
    zf = zr + 0.9
    feet_f = {"L": ("g", (float(croot[0]) - 0.6, zf - 0.55)), "R": ("g", (float(croot[0]) + 0.55, zf + 0.35))}
    add(684, {"root": ((float(croot[0]) - 0.1, 0.0, zf - 0.2), (0, 8, 0)), "pelvis": ((0, -0.2, 0), (-4, 14, 0)),
              "chest": (0, 0.08, 0), "look": far,
              "feet": {"L": feet_f["L"], "R": ("w", (float(croot[0]) + 0.6, 0.45, zf + 0.6))},
              "hands": {"R": ("d", ((0.2, -1.0, 0.25), 1.9)), "L": ("d", ((-0.25, -1.0, 0.1), 1.9))}})
    add(REDRESSE_F[1], {"root": ((float(croot[0]) - 0.15, 0.0, zf - 0.25), (0, 10, 0)), "pelvis": ((0, -0.04, 0), (0, 8, 0)),
                        "chest": (0, 0.04, 0), "look": far, "feet": feet_f,
                        "hands": {"R": ("d", ((0.16, -1.0, 0.3), 1.85)), "L": ("d", ((-0.24, -1.0, 0.08), 1.9))}})
    add(END_F, {"root": ((float(croot[0]) - 0.15, 0.0, zf - 0.25), (0, 10, 0)), "pelvis": ((0, -0.03, 0), (1, 8, 0)),
                "chest": (0, 0.05, 0), "look": far, "feet": feet_f,
                "hands": {"R": ("d", ((0.16, -1.0, 0.3), 1.85)), "L": ("d", ((-0.24, -1.0, 0.08), 1.9))}})
    return K, {"contact_tgt": tgt, "croot": croot}


# ---------------------------------------------------------------------

def build(blend):
    a = V.open_rig(blend)
    b = V.append_rig(blend, "Victime")
    for s in ("Right Arm", "Left Arm"):
        V.set_setting(s, "IK/FK", 1.0, rig=a)
        V.set_setting(s, "IK/FK", 0.0, rig=b)
    V.set_setting("Head", "Track Object", 1.0, rig=a)
    V.place(b, (0.0, DV, 0.0), 180.0)
    return a, b


def animate(a, b):
    import bpy
    S = bpy.context.scene
    S.render.fps = FPS
    S.frame_start, S.frame_end = 0, END_F
    report = {"victime": [], "attaquant": []}
    solved = []
    for f, p, i in victim_keys():
        c, res = M.solve_pose(b, p)
        solved.append((f, c, i))
        report["victime"].append((f, res))
    for f, c, i in solved:
        M.key_pose(b, f, c, *M.interp_args(i))
    vw = M.bake_world(b, 0, END_F)
    keys, info = attacker_keys(vw, a)
    solved = []
    for f, p, i in keys:
        c, res = M.solve_pose(a, p)
        solved.append((f, c, i))
        report["attaquant"].append((f, res))
    for f, c, i in solved:
        M.key_pose(a, f, c, *M.interp_args(i))
    aw = M.bake_world(a, 0, END_F)
    return aw, vw, report, info


def main(blend):
    os.makedirs(OUT, exist_ok=True)
    a, b = build(blend)
    aw, vw, report, info = animate(a, b)
    worst = max((r for side in report.values() for _f, res in side for r in res.values()), default=0)
    print("residu IK max :", round(worst, 3), "stud")
    for side, rows in report.items():
        for f, res in rows:
            bad = {k: v for k, v in res.items() if abs(v) > 0.05}
            if bad:
                print(f"  {side} f{f}: {bad}")
    json.dump({"distance": DV, "fps": FPS, "end_f": END_F, "markers": MARKERS, "contact_f": CONTACT_F,
               "inverse": INVERSE_F, "blanc": BLANC_F, "consequence": CONSEQ_F, "redresse": REDRESSE_F,
               "contact_tgt": [float(x) for x in info["contact_tgt"]], "residus": report},
              open(os.path.join(OUT, "scene.json"), "w"), indent=1)
    return a, b, aw, vw


if __name__ == "__main__":
    main(sys.argv[1])
