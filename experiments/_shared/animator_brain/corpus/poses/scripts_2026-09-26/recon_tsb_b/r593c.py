from h import *
dummy = pose2({"hanche": 3.0, "z": -14.0, "buste": (180, 0, 0)})
def P(lac, raz):
    return {"hanche": 2.5, "buste": (lac, 5, 0), "tete": (-lac * 0.6, 0), "RA": (lac + raz, -3), "LA": (-120, -40),
            "RL": ("pied", (0.9, 0, 1.3)), "LL": ("pied", (-0.9, 0, -1.4))}
noms = []
for k, (lac, raz, eye, tx, fov) in {"03_lacet0": (0, -20, (0, 3.0, 7), 3, 55),
                                  "03_lacet60": (60, -20, (0, 4.2, 7), 1.5, 40),
                                  "03_lacet80": (80, -20, (0, 3.6, 5), 1.5, 55)}.items():
    essai3("05.93", "r593_" + k, P(lac, raz), oeil=eye, cible=(tx, 2.6, -8.0), fov=fov, extra=[dummy]); noms.append("r593_" + k)
planche(noms, "r593_03_planche.png")
