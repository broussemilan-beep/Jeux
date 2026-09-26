import sys, json
sys.path.insert(0, ".")
import numpy as np
import fit as F
import geo_pose as G
spec = {
 "pose0": {"hanche": 2.4, "buste": [205, 15, -20], "RA": [40, -20], "LA": [-50, -20], "RL": [0, -60], "LL": [0, -90]},
 "cam0": {"L": 18.5, "pitch": 15.6, "roll": 1.1, "fov": 60, "d": 5.6, "beta": 7, "h": 3.9},
 "vars": [("cam", "d", 0), ("cam", "beta", 0), ("cam", "h", 0),
          ("pose", "buste", 0), ("pose", "buste", 1), ("pose", "buste", 2),
          ("pose", "RA", 0), ("pose", "RA", 1), ("pose", "LA", 0), ("pose", "LA", 1)],
 "x0": [5.6, 7, 3.9, 205, 15, -20, 40, -20, -50, -20],
 "step": [0.5, 3, 0.3, 15, 10, 10, 20, 15, 20, 15],
 "prior": [(5.5, 3), (7, 20), (4, 2), (205, 90), (10, 40), (0, 40), (0, 120), (0, 90), (0, 120), (0, 90)],
 "marks": {"RA_tip": ((242, 298), 1), "RA_gant": ((290, 272), 0.7), "LA_tip": ((568, 345), 1), "LA_gant": ((530, 322), 0.5),
           "T_bas_D_av": ((339, 383), 1), "T_bas_G_av": ((505, 362), 0.7), "T_av": ((435, 300), 0.3), "Tete": ((445, 200), 0.3)},
}
best = F.run(spec, restarts=6)
e, det = F.cost(best[0], spec, detail=True)
pose, cam = F.build(best[0], spec)
print("cout", round(e, 1)); print(json.dumps(pose)); print(cam)
for k, v in det.items(): print(k, v)
json.dump({"pose": pose, "cam": cam}, open("fit_460.json", "w"))
