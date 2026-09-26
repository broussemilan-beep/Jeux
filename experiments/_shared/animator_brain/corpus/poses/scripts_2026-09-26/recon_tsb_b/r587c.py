from h import *
V = {
 "03_camAz-20": ({"hanche": 2.4, "buste": (70, 10, 0), "tete": (-40, 10), "RA": (70, 0), "LA": (-120, -40),
        "RL": ("pied", (0.9, 0, 1.3)), "LL": ("pied", (-0.9, 0, -1.4))}, (-20, 5, 5.0, 45), (0.3, 3.0, 0)),
 "03_camAz-35_lacet80": ({"hanche": 2.4, "buste": (80, 10, 0), "tete": (-50, 10), "RA": (80, 0), "LA": (-120, -40),
        "RL": ("pied", (0.9, 0, 1.3)), "LL": ("pied", (-0.9, 0, -1.4))}, (-35, 5, 5.0, 45), (0.3, 3.0, 0)),
}
noms = []
for k in V:
    p, cam, cib = V[k]
    essai2("05.87", "r587_" + k, p, cam, cible=np.array(cib)); noms.append("r587_" + k)
planche(noms, "r587_03_planche.png")
