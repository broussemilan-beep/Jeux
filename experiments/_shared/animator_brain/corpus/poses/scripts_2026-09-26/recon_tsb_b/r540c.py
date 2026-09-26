from h import *
import sys
base = {"hanche": 2.3, "buste": (0, 20, 0), "tete": (30, 10), "LA": (-95, -15),
        "RL": ("pied", (0.9, 0, 1.5)), "LL": ("pied", (-0.9, 0, -1.5))}
V = {"08a": ((0, -20), (0, 8, 5.0, 45), (0.6, 1.8, 0)),
     "08b": ((20, -20), (0, 8, 5.0, 45), (0.6, 1.8, 0)),
     "08c": ((40, -20), (0, 8, 5.0, 45), (0.6, 1.8, 0))}
noms = []
for k, (ra, cam, cib) in V.items():
    p = dict(base); p["RA"] = ra
    essai2("05.40", "r540_" + k, p, cam, cible=np.array(cib)); noms.append("r540_" + k)
    w = pose2(p); print("   bbox RA", bbox(w, "Right Arm", cam_de(w, cam, np.array(cib))), "T", bbox(w, "Torso", cam_de(w, cam, np.array(cib))))
planche(noms, "r540_08_planche.png")
