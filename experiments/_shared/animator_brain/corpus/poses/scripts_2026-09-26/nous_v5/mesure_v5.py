"""Mesure géométrique de NOTRE v5 (usc_attaquant.rbxmx), images 172-300."""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, "/home/user/Jeux/experiments/_shared/animator_brain/outils")
import geo_pose as G  # noqa: E402

OUT = os.path.dirname(os.path.abspath(__file__))
SRC = "/home/user/Jeux/experiments/r6_un_seul_coup/output/usc_attaquant.rbxmx"
W = G.mondes_rbxmx(SRC)
F0, F1 = 172, 300
f_, r_ = G.repere((0, 0, -1))
Y = np.array([0, 1.0, 0])


def P(v):  # monde -> (avant, droite, haut) du coup
    v = np.asarray(v, float)
    return np.array([v @ f_, v @ r_, v @ Y])


rows = {}
for i in range(F0, F1 + 1):
    w = W[i]
    d = G.descripteurs(w)
    Rt, pt = w["Torso"]
    fist_w = G.bout(w, "Right Arm")
    sh_w = G.haut(w, "Right Arm")          # haut du bras (≈ épaule)
    lfist_w = G.bout(w, "Left Arm")
    head_w = w["Head"][1]
    d["_monde"] = {"torse": P(pt).round(3).tolist(), "poingD": P(fist_w).round(3).tolist(),
                   "hautBrasD": P(sh_w).round(3).tolist(), "poingG": P(lfist_w).round(3).tolist(),
                   "tete": P(head_w).round(3).tolist()}
    rows[i] = d

with open(os.path.join(OUT, "v5_descripteurs_172_300.json"), "w") as fh:
    json.dump(rows, fh, indent=0)

# ------------------------------------------------ table lisible, chaque image
lines = []
prev = None
cum = 0.0
for i in range(F0, F1 + 1):
    d = rows[i]
    m = d["_monde"]
    pf = np.array(m["poingD"])
    v = 0.0 if prev is None else float(np.linalg.norm(pf - prev))
    cum += v
    prev = pf
    d["_vit"] = round(v, 3)
    lines.append(f"{i} {G.resume(d)} | pieds {d['pieds']} | poingD monde(av,dr,ht) {np.round(pf,2).tolist()} v={v:.3f} cum={cum:.2f}")
open(os.path.join(OUT, "v5_table_172_300.txt"), "w").write("\n".join(lines) + "\n")

# ------------------------------------------------ détection des phases (vitesse de pose)
def pose_vec(i):
    d = rows[i]
    b = d["buste"]
    return np.array([d["hanche"] * 20, b["lacet"], b["penche_avant"], b["penche_cote"],
                     *d["bras"]["RA"]["torse"], *d["bras"]["LA"]["torse"]])


act = []
for i in range(F0 + 1, F1 + 1):
    act.append((i, float(np.abs(pose_vec(i) - pose_vec(i - 1)).max())))
open(os.path.join(OUT, "v5_activite.txt"), "w").write(
    "# max |Δ| par image (deg, hanche x20) : 0 = figé\n" + "\n".join(f"{i} {a:.2f}" for i, a in act) + "\n")

# ------------------------------------------------ la détente : décomposition
def detente(a, b):
    da, db = rows[a], rows[b]
    ma, mb = da["_monde"], db["_monde"]
    fa, fb = np.array(ma["poingD"]), np.array(mb["poingD"])
    ta, tb = np.array(ma["torse"]), np.array(mb["torse"])
    sa, sb = np.array(ma["hautBrasD"]), np.array(mb["hautBrasD"])
    path = sum(np.linalg.norm(np.array(rows[k + 1]["_monde"]["poingD"]) - np.array(rows[k]["_monde"]["poingD"]))
               for k in range(a, b))
    chord = np.linalg.norm(fb - fa)
    # écart max à la corde
    dev = 0.0
    u = (fb - fa) / max(chord, 1e-9)
    for k in range(a, b + 1):
        p = np.array(rows[k]["_monde"]["poingD"]) - fa
        dev = max(dev, float(np.linalg.norm(p - (p @ u) * u)))
    return {
        "images": [a, b], "duree_i": b - a,
        "lacet_buste": [da["buste"]["lacet"], db["buste"]["lacet"], round(db["buste"]["lacet"] - da["buste"]["lacet"], 1)],
        "penche_avant": [da["buste"]["penche_avant"], db["buste"]["penche_avant"]],
        "hanche": [da["hanche"], db["hanche"]],
        "RA_az_torse": [da["bras"]["RA"]["torse"][0], db["bras"]["RA"]["torse"][0],
                        round(db["bras"]["RA"]["torse"][0] - da["bras"]["RA"]["torse"][0], 1)],
        "RA_el_torse": [da["bras"]["RA"]["torse"][1], db["bras"]["RA"]["torse"][1]],
        "RA_az_coup": [da["bras"]["RA"]["coup"][0], db["bras"]["RA"]["coup"][0],
                       round(db["bras"]["RA"]["coup"][0] - da["bras"]["RA"]["coup"][0], 1)],
        "poing_monde_depart": fa.round(2).tolist(), "poing_monde_arrivee": fb.round(2).tolist(),
        "deplacement_poing": (fb - fa).round(2).tolist(),
        "part_torse_translation": (tb - ta).round(2).tolist(),
        "part_epaule_rotation_buste": ((sb - tb) - (sa - ta)).round(2).tolist(),
        "part_bras_rotation": ((fb - sb) - (fa - sa)).round(2).tolist(),
        "longueur_chemin": round(float(path), 2), "corde": round(float(chord), 2),
        "rectitude_corde_sur_chemin": round(float(chord / max(path, 1e-9)), 3),
        "ecart_max_a_la_corde": round(dev, 2),
        "vitesse_moy_studs_par_image": round(float(path / (b - a)), 3),
    }


dec = {"detente_270_283": detente(270, 283), "detente_271_283": detente(271, 283),
       "arc_186_214": detente(186, 214), "tenue_214_266": detente(214, 266),
       "compression_260_271": detente(260, 271)}
vit = {i: rows[i]["_vit"] for i in range(265, 292)}
dec["vitesse_poing_par_image_265_291"] = vit
# par image : lacet, az bras, poing relatif torse
dec["detail_detente"] = {i: {"lacet": rows[i]["buste"]["lacet"], "RA_torse": rows[i]["bras"]["RA"]["torse"],
                             "RA_coup": rows[i]["bras"]["RA"]["coup"], "poing_rel": rows[i]["poing"]["RA"],
                             "poing_monde": rows[i]["_monde"]["poingD"], "torse_monde": rows[i]["_monde"]["torse"],
                             "v": rows[i]["_vit"]} for i in range(266, 292)}
json.dump(dec, open(os.path.join(OUT, "v5_detente.json"), "w"), indent=1)

# ------------------------------------------------ planches de rendu
KEYS = [173, 200, 214, 250, 271, 275, 279, 281, 283, 290]
CAMS = [(0, 10, "face (victime)"), (45, 15, "3/4 avant-droit"), (90, 5, "profil droit"), (200, 20, "dos-gauche")]
TW, TH = 320, 240


def recentre(w, off):
    return {k: (R, p - off) for k, (R, p) in w.items()}


off = np.array([W[271]["Torso"][1][0], 0.0, W[271]["Torso"][1][2]])  # sol visible
for ci, (az, el, nom) in enumerate(CAMS):
    sheet = Image.new("RGB", (5 * TW, 2 * TH), (0, 0, 0))
    for k, fr in enumerate(KEYS):
        w = recentre(W[fr], off)
        cam = G.camera_orbite(w["Torso"][1], az, el, 9, 50)
        im = G.rendre(w, cam, (TW, TH), f"{fr} cam az{az} el{el}")
        sheet.paste(im, ((k % 5) * TW, (k // 5) * TH))
    sheet.save(os.path.join(OUT, f"planche_cam{ci}_az{az}_el{el}.png"))

# une planche par image clé (4 caméras côte à côte) pour les regarder en détail
for fr in KEYS:
    row = Image.new("RGB", (4 * TW, TH), (0, 0, 0))
    w = recentre(W[fr], off)
    for ci, (az, el, nom) in enumerate(CAMS):
        cam = G.camera_orbite(w["Torso"][1], az, el, 9, 50)
        row.paste(G.rendre(w, cam, (TW, TH), f"{fr} {nom}"), (ci * TW, 0))
    row.save(os.path.join(OUT, f"cle_{fr}.png"))

# ------------------------------------------------ trajectoire du poing (onion skin)
onion = [recentre(W[i], off) for i in (266, 271, 274, 277, 279, 281, 283)]
tgt = np.array(onion[3]["Torso"][1])
for az, el, tag in [(0, 89, "dessus"), (90, 5, "profil"), (0, 10, "face"), (200, 20, "dos")]:
    cam = G.camera_orbite(tgt, az, el, 11 if el > 80 else 9, 50)
    G.rendre(onion, cam, (640, 480), f"onion 266/271/274/277/279/281/283 {tag}").save(
        os.path.join(OUT, f"onion_detente_{tag}.png"))

# plan de dessus dessiné (PIL) : chemin du poing D, épaule, orientation du torse
S = 60  # px par stud
img = Image.new("RGB", (720, 720), (245, 245, 245))
dr = ImageDraw.Draw(img)
t271 = np.array(rows[271]["_monde"]["torse"])


def px(p):  # (avant, droite) relatif au torse de 271 -> px ; avant = haut de l'image
    return (360 + S * (p[1] - t271[1]), 480 - S * (p[0] - t271[0]))


for g in range(-6, 7):
    dr.line([px((g + t271[0], -6 + t271[1])), px((g + t271[0], 6 + t271[1]))], fill=(225, 225, 225))
    dr.line([px((-6 + t271[0], g + t271[1])), px((6 + t271[0], g + t271[1]))], fill=(225, 225, 225))
pts = [px(rows[i]["_monde"]["poingD"]) for i in range(186, 292)]
for i in range(186, 291):
    col = (0, 150, 0) if i < 214 else (150, 150, 150) if i < 266 else (230, 120, 0) if i < 271 else (220, 0, 0) if i < 283 else (0, 0, 220)
    dr.line([px(rows[i]["_monde"]["poingD"]), px(rows[i + 1]["_monde"]["poingD"])], fill=col, width=3)
for i in (186, 200, 214, 266, 271, 274, 277, 279, 281, 283, 290):
    m = rows[i]["_monde"]
    fp, sp, tp = px(m["poingD"]), px(m["hautBrasD"]), px(m["torse"])
    dr.ellipse([fp[0] - 4, fp[1] - 4, fp[0] + 4, fp[1] + 4], outline=(0, 0, 0))
    dr.text((fp[0] + 5, fp[1] - 6), str(i), fill=(0, 0, 0))
    dr.line([sp, fp], fill=(0, 160, 0), width=1)
    # axe des épaules (torse) : droite du torse
    lac = np.radians(rows[i]["buste"]["lacet"])
    fwd = np.array([np.cos(lac), -np.sin(lac)])  # (avant, droite) : lacet + = tourné vers sa gauche
    rgt = np.array([np.sin(lac), np.cos(lac)])
    c = np.array(m["torse"][:2])
    if i in (186, 214, 271, 277, 283):
        dr.line([px(c - rgt), px(c + rgt)], fill=(200, 0, 0), width=2)
        dr.line([px(c), px(c + 0.8 * fwd)], fill=(120, 0, 0), width=1)
dr.text((10, 10), "v5 vu de DESSUS (haut = vers la victime, droite = sa droite), 1 case = 1 stud", fill=(0, 0, 0))
dr.text((10, 26), "poing D : vert=arc 186-214, gris=tenue, orange=compression 266-271, ROUGE=detente 271-283, bleu=apres", fill=(0, 0, 0))
dr.text((10, 42), "trait rouge epais = axe des epaules (186,214,271,277,283) ; trait vert fin = epaule->poing", fill=(0, 0, 0))
img.save(os.path.join(OUT, "plan_dessus_poing.png"))

# profil (avant vs haut) du poing
img = Image.new("RGB", (720, 480), (245, 245, 245))
dr = ImageDraw.Draw(img)


def px2(p):
    return (200 + S * (p[0] - t271[0]), 440 - S * p[2])


dr.line([px2((t271[0] - 4, 0, 0)), px2((t271[0] + 8, 0, 0))], fill=(0, 0, 0))
for i in range(186, 291):
    col = (0, 150, 0) if i < 214 else (150, 150, 150) if i < 266 else (230, 120, 0) if i < 271 else (220, 0, 0) if i < 283 else (0, 0, 220)
    dr.line([px2(rows[i]["_monde"]["poingD"]), px2(rows[i + 1]["_monde"]["poingD"])], fill=col, width=3)
for i in (186, 214, 271, 277, 283):
    p = px2(rows[i]["_monde"]["poingD"])
    dr.text((p[0] + 4, p[1] - 12), str(i), fill=(0, 0, 0))
    q = px2(rows[i]["_monde"]["hautBrasD"])
    dr.ellipse([q[0] - 3, q[1] - 3, q[0] + 3, q[1] + 3], fill=(0, 120, 0))
cp = px2((-15.865 * -1, 0, 3.369))  # cible contact : z=-15.865 -> avant +15.865
dr.ellipse([cp[0] - 5, cp[1] - 5, cp[0] + 5, cp[1] + 5], outline=(255, 0, 255), width=2)
dr.text((10, 10), "v5 de PROFIL (droite = vers la victime, haut = hauteur), poing D ; rond magenta = cible contact", fill=(0, 0, 0))
img.save(os.path.join(OUT, "profil_poing.png"))
print("ok")
