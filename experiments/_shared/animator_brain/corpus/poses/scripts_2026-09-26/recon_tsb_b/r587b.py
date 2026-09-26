from h import *
import sys
V = {
 "02_lacet70": ({"hanche": 2.4, "buste": (70, 10, 0), "tete": (-40, 10), "RA": (70, 0), "LA": (-120, -40),
        "RL": ("pied", (0.9, 0, 1.3)), "LL": ("pied", (-0.9, 0, -1.4))}, (0, 5, 5.0, 45), (0.3, 3.0, 0)),
 "02_lacet45": ({"hanche": 2.4, "buste": (45, 10, 0), "tete": (-30, 10), "RA": (45, 0), "LA": (-120, -40),
        "RL": ("pied", (0.9, 0, 1.3)), "LL": ("pied", (-0.9, 0, -1.4))}, (0, 5, 5.0, 45), (0.3, 3.0, 0)),
 "02_lacet90": ({"hanche": 2.4, "buste": (90, 10, 0), "tete": (-60, 10), "RA": (90, 0), "LA": (-120, -40),
        "RL": ("pied", (0.9, 0, 1.3)), "LL": ("pied", (-0.9, 0, -1.4))}, (0, 5, 5.0, 45), (0.3, 3.0, 0)),
}
noms = []
for k in V:
    p, cam, cib = V[k]
    essai2("05.87", "r587_" + k, p, cam, cible=np.array(cib)); noms.append("r587_" + k)
planche(noms, "r587_02_planche.png")
