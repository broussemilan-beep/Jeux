from h import *
import sys
base = {"hanche": 2.4, "buste": (0, 10, 0), "tete": (0, 10), "RA": (0, 0), "LA": (-60, -40),
        "RL": ("pied", (0.9, 0, 1.3)), "LL": ("pied", (-0.9, 0, -1.4))}
noms = []
for k, cam in {"01_camAz-30": (-30, 5, 5.0, 45), "01_camAz0": (0, 5, 5.0, 45), "01_camAz+30": (30, 5, 5.0, 45)}.items():
    essai2("05.87", "r587_" + k, base, cam, cible=np.array((0.5, 3.0, 0))); noms.append("r587_" + k)
planche(noms, "r587_01_planche.png")
