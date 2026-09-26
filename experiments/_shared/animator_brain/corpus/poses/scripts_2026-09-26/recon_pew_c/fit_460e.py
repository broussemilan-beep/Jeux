import sys, json, time
sys.path.insert(0, ".")
import numpy as np
import fit as F
teapot = [(345, 120), (570, 120), (570, 290), (470, 300), (400, 290), (345, 235)]
ciel = [(0, 0), (960, 0), (960, 200), (0, 200)]
x0 = json.loads(sys.argv[1]) if len(sys.argv) > 1 else [5.6, 7, 3.9, 205, 15, -20, 40, -20, -50, -20]
tag = sys.argv[2] if len(sys.argv) > 2 else "d"
spec = {
 "pose0": {"hanche": 2.4, "buste": [205, 15, -20], "RA": [40, -20], "LA": [-50, -20], "RL": [0, -60], "LL": [0, -90]},
 "cam0": {"L": 18.5, "pitch": 15.6, "roll": 1.1, "fov": 60, "d": 5.6, "beta": 7, "h": 3.9},
 "vars": [("cam", "d", 0), ("cam", "beta", 0), ("cam", "h", 0),
          ("pose", "buste", 0), ("pose", "buste", 1), ("pose", "buste", 2),
          ("pose", "RA", 0), ("pose", "RA", 1), ("pose", "LA", 0), ("pose", "LA", 1)],
 "x0": x0,
 "step": [0.5, 3, 0.3, 15, 10, 10, 20, 15, 20, 15],
 "prior": [(5.5, 3), (7, 20), (4, 2), (205, 90), (10, 40), (0, 40), (0, 120), (0, 90), (0, 120), (0, 90)],
 "marks": {"RA_tip": ((249, 291), 1), "LA_tip": ((555, 338), 1),
           "T_bas_D_av": ((339, 383), 1.5), "T_bas_G_av": ((505, 362), 1.0), "Tete": ((455, 222), 0.4)},
 "bbox": {"RA": ((198, 240, 300, 342), 1), "LA": ((521, 299, 589, 376), 0.6)},
 "masque": F.prep_masque("04.60", [ciel, teapot], [teapot]),
 "w_iou": 4000,
}
t0 = time.time()
best = F.run(spec, restarts=3)
e, det = F.cost(best[0], spec, detail=True)
pose, cam = F.build(best[0], spec)
print("cout", round(e, 1), "temps", round(time.time() - t0)); print(json.dumps(pose)); print(cam)
for k, v in det.items(): print(k, v)
json.dump({"pose": pose, "cam": cam}, open(f"fit_460{tag}.json", "w"))
json.dump([float(v) for v in best[0]], open(f"fit_460{tag}_x.json", "w"))
