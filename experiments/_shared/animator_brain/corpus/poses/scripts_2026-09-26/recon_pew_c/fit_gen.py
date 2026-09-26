"""python3 fit_gen.py <spec.json> : ajustement générique (spec JSON)."""
import sys, json
sys.path.insert(0, ".")
import numpy as np
import fit as F
sp = json.load(open(sys.argv[1]))
spec = dict(sp)
spec["vars"] = [tuple(v) for v in sp["vars"]]
spec["prior"] = [tuple(v) for v in sp["prior"]]
spec["marks"] = {k: (tuple(v[0]), v[1]) for k, v in sp["marks"].items()}
spec["bbox"] = {k: (tuple(v[0]), v[1]) for k, v in sp.get("bbox", {}).items()}
spec["dirs"] = [tuple(v) for v in sp.get("dirs", [])]
if "masque" in sp:
    spec["masque"] = F.prep_masque(sp["masque"]["t"], sp["masque"]["excl"], sp["masque"]["care_excl"])
best = F.run(spec, restarts=sp.get("restarts", 4))
e, det = F.cost(best[0], spec, detail=True)
pose, cam = F.build(best[0], spec)
print("cout", round(e, 1)); print(json.dumps({k: [round(x, 1) for x in v] if isinstance(v, (list, tuple)) else v for k, v in pose.items()}))
print({k: round(v, 2) if isinstance(v, float) else v for k, v in cam.items()})
for k, v in det.items(): print(" ", k, v)
json.dump({"pose": pose, "cam": cam}, open(sp["out"], "w"))
