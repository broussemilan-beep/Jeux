from h import *
V = {
 "04": ({"hanche": 2.4, "buste": (70, 5, 0), "tete": (-40, 0), "RA": (70, -8), "LA": (-120, -40),
        "RL": ("pied", (0.9, 0, 1.3)), "LL": ("pied", (-0.9, 0, -1.4))}, (-20, 3, 5.0, 45), (1.1, 2.9, -0.6)),
 "04_alt_bras_croise_sans_rotation": ({"hanche": 2.4, "buste": (0, 5, 0), "tete": (0, 0), "RA": (-35, -8), "LA": (-120, -40),
        "RL": ("pied", (0.9, 0, 1.3)), "LL": ("pied", (-0.9, 0, -1.4))}, (-20, 3, 5.0, 45), (0.6, 2.9, -0.6)),
}
noms = []
for k in V:
    p, cam, cib = V[k]
    essai2("05.87", "r587_" + k, p, cam, cible=np.array(cib)); noms.append("r587_" + k)
planche(noms, "r587_04_planche.png")
