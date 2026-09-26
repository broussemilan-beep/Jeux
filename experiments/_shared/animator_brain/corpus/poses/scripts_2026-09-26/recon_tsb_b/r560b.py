from h import *
import sys
# repère caméra-relatif : cam az 0 = la caméra de ce plan ; on convertira ensuite.
L = {"RL": ("pied", (0.9, 0, 1.5)), "LL": ("pied", (-0.9, 0, -1.5)), "LA": (-95, -35), "tete": (30, 10)}
V = {
 "02": ({"hanche": 2.3, "buste": (15, 20, -10), "RA": (15, -15)}, (0, 8, 5.0, 45), (0.6, 1.8, 0)),
 "03": ({"hanche": 2.3, "buste": (30, 20, -15), "RA": (30, -5)}, (0, 8, 5.0, 45), (0.6, 1.8, 0)),
 "04": ({"hanche": 2.3, "buste": (30, 25, -15), "RA": (20, -20)}, (0, 8, 4.2, 50), (0.6, 1.8, 0)),
 "05": ({"hanche": 2.3, "buste": (25, 25, -15), "RA": (15, -35)}, (0, 8, 5.0, 45), (0.6, 1.8, 0)),
 "06": ({"hanche": 2.3, "buste": (35, 25, -15), "RA": (25, -30)}, (0, 8, 4.5, 48), (0.6, 1.8, 0)),
 "07": ({"hanche": 2.3, "buste": (35, 25, -15), "RA": (35, -40, 20)}, (0, 8, 4.5, 48), (0.6, 1.8, 0)),
 "08_alt_lacet0": ({"hanche": 2.3, "buste": (0, 25, -15), "RA": (-5, -30)}, (0, 8, 4.5, 48), (0.6, 1.8, 0)),
 "08_alt_lacet65": ({"hanche": 2.3, "buste": (65, 25, -15), "RA": (55, -30)}, (0, 8, 4.5, 48), (0.6, 1.8, 0)),
}
noms = []
for k in sys.argv[1:]:
    p, cam, cib = V[k]; q = dict(L); q.update(p)
    w, d = essai2("05.60", "r560_" + k, q, cam, cible=np.array(cib)); noms.append("r560_" + k)
    c = cam_de(w, cam, np.array(cib)); print("   RA", bbox(w, "Right Arm", c), "T", bbox(w, "Torso", c))
planche(noms, "r560_" + "_".join(sys.argv[1:]) + "_planche.png")
