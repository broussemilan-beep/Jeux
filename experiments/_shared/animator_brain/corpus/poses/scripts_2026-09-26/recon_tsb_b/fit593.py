from h import *
import itertools
dummy = pose2({"hanche": 3.0, "z": -14.0, "buste": (180, 0, 0)})
# cibles mesurées sur la ref (panneau 520x360)
T = {"Head": (150, 72, 225, 150), "RA": (135, 150, 300, 262), "dummy_c": (276, 122)}
def err(w, cam):
    e = 0
    bh = bbox(w, "Head", cam); e += sum(abs(a - b) for a, b in zip(bh, T["Head"]))
    br = bbox(w, "Right Arm", cam); e += sum(abs(a - b) for a, b in zip(br, T["RA"]))
    bd = bbox(dummy, "Torso", cam); cx, cy = (bd[0] + bd[2]) / 2, (bd[1] + bd[3]) / 2
    e += 2 * (abs(cx - T["dummy_c"][0]) + abs(cy - T["dummy_c"][1]))
    return e
best = []
for lac in (0, 20, 40, 60, 80):
    for ra_az_coup in (-20, 0, 20):
        p = {"hanche": 2.5, "buste": (lac, 5, 0), "tete": (-lac * 0.6, 0), "RA": (lac + ra_az_coup, -3), "LA": (-120, -40),
             "RL": ("pied", (0.9, 0, 1.3)), "LL": ("pied", (-0.9, 0, -1.4))}
        w = pose2(p)
        for ex, ey, ez, fov in itertools.product((-3, -2, -1, 0), (3.0, 3.6, 4.2), (3, 5, 7), (40, 55, 70)):
            eye = np.array([ex, ey, ez], float)
            # la caméra regarde un point entre le perso et le mannequin : on cherche la direction
            for tx in (0, 1.5, 3):
                cam = (eye, np.array([tx, 2.6, -8.0]), fov)
                try:
                    e = err(w, cam)
                except Exception:
                    continue
                best.append((e, lac, ra_az_coup, ex, ey, ez, fov, tx))
best.sort()
for b in best[:12]:
    print(b)
# meilleur par lacet
for lac in (0, 20, 40, 60, 80):
    print("lacet", lac, min(b for b in best if b[1] == lac))
