from h import *
V = {
 "05": ({"hanche": 2.4, "buste": (80, 5, 0), "tete": (-50, 0), "RA": (80, -8), "LA": (-120, -40),
        "RL": ("pied", (0.9, 0, 1.3)), "LL": ("pied", (-0.9, 0, -1.4))}, (-8, 3, 5.0, 45), (0.8, 2.9, -0.6)),
}
for k in V:
    p, cam, cib = V[k]
    w, d = essai2("05.87", "r587_" + k, p, cam, cible=np.array(cib))
    c = cam_de(w, cam, np.array(cib)); print("   RA", bbox(w, "Right Arm", c), "Head", bbox(w, "Head", c), "T", bbox(w, "Torso", c))
