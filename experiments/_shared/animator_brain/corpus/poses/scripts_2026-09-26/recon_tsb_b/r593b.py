from h import *
# mannequin cible (dummy) : un R6 debout a 14 studs devant (-Z)
dummy = pose2({"hanche": 3.0, "z": -14.0, "buste": (180, 0, 0)})
V = {}
for lac in (0, 40, 80):
    V["02_lacet%d" % lac] = {"hanche": 2.5, "buste": (lac, 5, 0), "tete": (-lac * 0.6, 0), "RA": (lac, -3), "LA": (-120, -40),
        "RL": ("pied", (0.9, 0, 1.3)), "LL": ("pied", (-0.9, 0, -1.4))}
noms = []
for k, p in V.items():
    essai3("05.93", "r593_" + k, p, oeil=(-1.2, 3.4, 3.2), cible=(1.2, 2.6, -8.0), fov=55, extra=[dummy]); noms.append("r593_" + k)
planche(noms, "r593_02_planche.png")
