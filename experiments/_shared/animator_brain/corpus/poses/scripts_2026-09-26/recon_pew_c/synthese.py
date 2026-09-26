import sys, json
sys.path.insert(0, ".")
import numpy as np
sys.path.insert(0, "/home/user/Jeux/experiments/_shared/animator_brain/outils")
import rendu
import geo_pose as G
from essai2 import cam_grille, cap
fits = {"4.6": "fit_460d.json", "4.8": "fit_480c.json", "4.9": "fit_490b.json", "5.0": "fit_500b.json"}
W = {}
for t, f in fits.items():
    d = json.load(open(f)); pose = {k: (tuple(v) if isinstance(v, list) else v) for k, v in d["pose"].items()}
    w = G.pose(pose); c = cam_grille(w["Torso"][1], **d["cam"]); W[t] = (w, c, pose, d["cam"])
w49 = W["4.9"][0]
ra = w49["Right Arm"][0] @ np.array([0, -1.0, 0]); av = np.array([ra[0], 0, ra[2]]); av /= np.linalg.norm(av)
print("avant (monde, horizontal du bras droit à 4.9) =", av.round(3))
out = {}
for t, (w, c, pose, cam) in W.items():
    d = G.descripteurs(w, tuple(av))
    tc = w["Torso"][1]; toc = c["eye"] - tc; toc[1] = 0; toc /= np.linalg.norm(toc)
    ang_cam = np.degrees(np.arctan2(np.cross(av, toc)[1], av @ toc))
    Rt = w["Torso"][0]; fwd = Rt @ np.array([0, 0, -1.0]); fwd[1] = 0; fwd /= np.linalg.norm(fwd)
    face_cam = np.degrees(np.arccos(np.clip(fwd @ toc, -1, 1)))
    print(t, G.resume(d)); print("   pieds", d["pieds"], "| caméra à", round(float(ang_cam)), "deg de l'axe du coup ; torse fait", round(float(face_cam)), "deg avec la direction caméra")
    out[t] = {"params": pose, "cam": cam, "descripteurs": d, "cam_vs_coup_deg": round(float(ang_cam)), "torse_vs_cam_deg": round(float(face_cam))}
json.dump(out, open("synthese.json", "w"), indent=1, default=float)
