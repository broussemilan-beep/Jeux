import sys, json, time
sys.path.insert(0, ".")
import numpy as np
import fit as F
x0 = json.loads(sys.argv[1]) if len(sys.argv) > 1 else [5.6, 7, 4.0, 225, 10, -10]
tag = sys.argv[2] if len(sys.argv) > 2 else "T1"
spec = {
 "pose0": {"hanche": 2.4, "buste": [205, 15, -20], "RA": [90, -90], "LA": [-90, -90], "RL": [0, -90], "LL": [0, -90]},
 "cam0": {"L": 18.5, "pitch": 15.6, "roll": 1.1, "fov": 60, "d": 5.6, "beta": 7, "h": 3.9},
 "vars": [("cam", "d", 0), ("cam", "beta", 0), ("cam", "h", 0),
          ("pose", "buste", 0), ("pose", "buste", 1), ("pose", "buste", 2)],
 "x0": x0, "step": [0.5, 3, 0.3, 20, 10, 10],
 "prior": [(5.5, 3), (7, 20), (4, 2), (205, 180), (10, 60), (0, 60)],
 "marks": {"@Torso:0.45,-1,-0.5": ((362, 379), 1), "@Torso:0,-1,-0.5": ((423, 367), 1), "@Torso:-0.45,-1,-0.5": ((460, 347), 1),
           "@Torso:0,0.6,-0.5": ((440, 280), 0.3)},
 "dirs": [("@Torso:0.45,-1,-0.5", "@Torso:0.45,0,-0.5", 14, 0.5), ("@Torso:0,-1,-0.5", "@Torso:0,0,-0.5", 10, 0.5),
          ("@Torso:-0.45,-1,-0.5", "@Torso:-0.45,0,-0.5", 17, 0.5)],
}
best = F.run(spec, restarts=4)
e, det = F.cost(best[0], spec, detail=True)
pose, cam = F.build(best[0], spec)
print("cout", round(e, 1)); print(json.dumps(pose)); print(cam)
for k, v in det.items(): print(k, v)
json.dump({"pose": pose, "cam": cam}, open(f"fit_460{tag}.json", "w"))
