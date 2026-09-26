"""
Planche de profil au contact : 2 M1 du pack pro contre nos coups de la rafale.
Trait rouge = ecart entre le pivot d'epaule du torse et celui du bras
(translation du Motor6D) ; cercle = poing. Sert de preuve a LECONS.md 6-7.

Usage : python3 profile_contact.py <pack.rbxm> <sortie.png> [etiquette, ex. v3]
"""
import sys, json, numpy as np
import os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "_shared"))
sys.path.insert(0, HERE)
from animator_brain import corpus as C
import staging as ST
SIZES = {"Torso": (2, 2, 1), "Head": (1.25, 1.25, 1.25), "Right Arm": (1, 2, 1), "Left Arm": (1, 2, 1), "Right Leg": (1, 2, 1), "Left Leg": (1, 2, 1)}
COL = {"Torso": "#2b6cb0", "Head": "#e2b714", "Right Arm": "#e2b714", "Left Arm": "#c9a20f", "Right Leg": "#38a169", "Left Leg": "#2f855a"}
def tip(w, p): r, c = w[p]; return c + r @ np.array([0, -1.0, 0])
from PIL import Image, ImageDraw, ImageFont
def hull(P):
    P = sorted(map(tuple, P))
    def cross(o, a, b): return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lo, up = [], []
    for p in P:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0: lo.pop()
        lo.append(p)
    for p in reversed(P):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0: up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]
S, PW, PH = 70, 440, 470
def draw(img, ox, w, title, hand, z0):
    d = ImageDraw.Draw(img)
    X = lambda u, v: (ox + 150 + u * S, PH - 30 - v * S)
    d.line([X(-2, 0), X(4, 0)], fill="black", width=2)
    d.line([X(-2, 3.5), X(4, 3.5)], fill=(150, 150, 150), width=1)
    d.text(X(-1.9, 3.8), "epaule au repos (3,5)", fill=(120, 120, 120))
    for p in ["Left Arm", "Left Leg", "Torso", "Head", "Right Leg", "Right Arm"]:
        r, c = w[p]; h = np.array(SIZES[p]) / 2
        pts = [c + r @ (h * [x, y, z]) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
        H = hull([(-(q[2] - z0), q[1]) for q in pts])
        col = tuple(int(COL[p][i:i + 2], 16) for i in (1, 3, 5))
        d.polygon([X(*q) for q in H], fill=col, outline="black")
    for sx, arm in ((1, "Right Arm"), (-1, "Left Arm")):
        a = w["Torso"][1] + w["Torso"][0] @ np.array([sx * 1, 0.5, 0]); b = w[arm][1] + w[arm][0] @ np.array([-sx * 0.5, 0.5, 0])
        d.line([X(-(a[2] - z0), a[1]), X(-(b[2] - z0), b[1])], fill="red", width=4)
        pa = X(-(a[2] - z0), a[1]); d.ellipse([pa[0] - 5, pa[1] - 5, pa[0] + 5, pa[1] + 5], fill="red")
    t = tip(w, hand); pt = X(-(t[2] - z0), t[1]); d.ellipse([pt[0] - 7, pt[1] - 7, pt[0] + 7, pt[1] + 7], outline="black", width=3)
    d.text((ox + 10, 8), title, fill="black")
    d.text((ox + 10, 24), f"poing a {t[1]:.2f} stud du sol", fill="black")
pack = sys.argv[1]
TAG = sys.argv[3] if len(sys.argv) > 3 else ""
pro = {}
for s in C.load_rbxm_sequences(pack):
    if s["name"].endswith(("M1_1", "M1_3")):
        wf = C.resolve_world(s["frames"])
        best = min(((tip(w, h)[2], i, h) for i, (_t, w) in enumerate(wf) for h in ("Right Arm", "Left Arm")))
        pro[s["name"]] = (wf[best[1]][1], best[2])
aw, vw = ST.tracks()
sc = json.load(open(os.path.join(HERE, "..", "output", "scene.json")))
n_hits = len(sc["hits"])
img = Image.new("RGB", (PW * (2 + n_hits), PH + 40), "white")
for k, (n, (w, h)) in enumerate(sorted(pro.items())):
    draw(img, k * PW, w, f"PRO {n}, au contact", h, w["Torso"][1][2])
for k, (c, s_, kind) in enumerate(sc["hits"]):
    w = aw[c]; h = "Right Arm" if s_ == "R" else "Left Arm"
    draw(img, (k + 2) * PW, w, f"NOUS {TAG}, coup f{c} ({kind}), au contact", h, w["Torso"][1][2])
ImageDraw.Draw(img).text((10, PH + 12), "Profil, avant = droite. Trait rouge = epaule du torse -> epaule du bras : les pros la BAISSENT (descend). Cercle = poing.", fill="black")
img.save(sys.argv[2])
