from h import *
V = {}
for lac in (0, 40, 80):
    V["01_lacet%d" % lac] = ({"hanche": 2.5, "buste": (lac, 5, 0), "tete": (-lac * 0.6, 0), "RA": (lac, -3), "LA": (-120, -40),
        "RL": ("pied", (0.9, 0, 1.3)), "LL": ("pied", (-0.9, 0, -1.4))}, (-160, 8, 5.5, 60), (-1.5, 2.6, -3.0))
noms = []
for k in V:
    p, cam, cib = V[k]
    essai2("05.93", "r593_" + k, p, cam, cible=np.array(cib)); noms.append("r593_" + k)
planche(noms, "r593_01_planche.png")
