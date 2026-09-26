from h import *
base = {"hanche": 2.3, "buste": (0, 20, 0), "tete": (30, 10), "LA": (-95, -35),
        "RL": ("pied", (0.9, 0, 1.5)), "LL": ("pied", (-0.9, 0, -1.5))}
V = {"09": ((0, -28), (0, 8, 5.0, 45), (0.6, 1.8, 0)),
     "09_altD_bras_derriere": ((180, -30), (0, 8, 5.0, 45), (0.6, 1.8, 0)),
     "09_altE_bras_travers": ((-45, -30), (0, 8, 5.0, 45), (0.6, 1.8, 0))}
noms = []
for k, (ra, cam, cib) in V.items():
    p = dict(base); p["RA"] = ra
    essai2("05.40", "r540_" + k, p, cam, cible=np.array(cib)); noms.append("r540_" + k)
planche(noms, "r540_09_planche.png")
