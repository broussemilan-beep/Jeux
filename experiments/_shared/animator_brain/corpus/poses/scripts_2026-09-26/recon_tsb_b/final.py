from h import *
import json
F = {
 "4.87": ({"hanche": 2.2, "buste": (0, 35, 0), "RA": (170, -30), "LA": (-20, -5), "tete": (0, 0),
           "RL": ("pied", (0.8, 0, 1.8)), "LL": ("pied", (-0.8, 0, -1.2))}, "r487_05_final.png", None),
 "5.13": ({"hanche": 2.2, "buste": (0, 30, 0), "RA": (175, 10), "LA": (-15, 20), "tete": (0, 0),
           "RL": ("pied", (0.8, 0, 1.8)), "LL": ("pied", (-0.8, 0, -1.2))}, "r513_07_final.png", None),
 "5.27": ({"hanche": 2.4, "buste": (-15, 25, -10), "tete": (45, -15), "RA": (180, -5), "LA": (-60, -40),
           "RL": ("pied", (0.9, 0, 1.4)), "LL": ("pied", (-0.9, 0, -1.4))}, "r527_05_final.png", None),
 "5.40": ({"hanche": 2.3, "buste": (0, 20, 0), "tete": (30, 10), "RA": (0, -28), "LA": (-95, -35),
           "RL": ("pied", (0.9, 0, 1.5)), "LL": ("pied", (-0.9, 0, -1.5))}, "r540_09.png", 58),
 "5.60": ({"hanche": 2.3, "buste": (35, 25, -15), "tete": (30, 10), "RA": (25, -30), "LA": (-95, -35),
           "RL": ("pied", (0.9, 0, 1.5)), "LL": ("pied", (-0.9, 0, -1.5))}, "r560_06.png", 38),
 "5.87": ({"hanche": 2.4, "buste": (80, 5, 0), "tete": (-50, 0), "RA": (80, -8), "LA": (-120, -40),
           "RL": ("pied", (0.9, 0, 1.3)), "LL": ("pied", (-0.9, 0, -1.4))}, "r587_05.png", 0),
}
def local_torse(w, p):
    R, c = w["Torso"]; v = R.T @ (np.asarray(p) - c)
    return [round(float(v[0]), 2), round(float(v[1]), 2), round(float(-v[2]), 2)]  # droite, haut, avant (torse)
out = {}
for t, (p, png, rot_h1) in F.items():
    w = pose2(p)
    d_cam = G.descripteurs(w)  # avant = -Z du rendu (repère caméra-relatif / face du buste pour 4.87-5.27)
    loc = local_torse(w, G.bout(w, "Right Arm"))
    locL = local_torse(w, G.bout(w, "Left Arm"))
    r = {"png": png, "params_repere_rendu": {k: v for k, v in p.items()}, "poing_RA_axes_torse(dr,ht,av)": loc,
         "poing_LA_axes_torse(dr,ht,av)": locL, "desc_repere_rendu": d_cam}
    if rot_h1 is not None:
        # H1 : direction du coup = direction du bras à 5.87 ; la caméra de ce plan est à rot_h1 deg à gauche de cette ligne
        # -> on tourne le monde de rot_h1 vers la droite : équivalent à avant = direction tournée de +rot_h1 (vers la droite du perso)
        a = np.radians(rot_h1)
        avant = (np.sin(a), 0.0, -np.cos(a))   # ligne du coup vue dans le repère du rendu
        r["desc_H1"] = G.descripteurs(w, avant)
        r["resume_H1"] = G.resume(r["desc_H1"])
    r["resume_rendu"] = G.resume(d_cam)
    out[t] = r
    print(t, "| poing RA axes torse (dr,ht,av)", loc, "| LA", locL)
    print("   rendu:", r["resume_rendu"])
    if "resume_H1" in r: print("   H1   :", r["resume_H1"])
json.dump(out, open("final.json", "w"), indent=1, ensure_ascii=False, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))
