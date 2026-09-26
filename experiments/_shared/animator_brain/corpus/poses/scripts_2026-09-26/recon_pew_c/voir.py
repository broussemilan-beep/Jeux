"""python3 voir.py fit.json t sortie [avant] : rend le résultat d'ajustement"""
import sys, json, ast
sys.path.insert(0, ".")
import numpy as np
import rendu as R
import geo_pose as G
from essai2 import cam_grille
d = json.load(open(sys.argv[1])); t = sys.argv[2]; out = sys.argv[3]
avant = ast.literal_eval(sys.argv[4]) if len(sys.argv) > 4 else (0, 0, -1)
pose = {k: (tuple(v) if isinstance(v, list) else v) for k, v in d["pose"].items()}
w = G.pose(pose)
cam = cam_grille(w["Torso"][1], **d["cam"])
src = t if t.startswith('/') else f"/tmp/claude-0/-home-user-Jeux/4796ac9e-8e41-51f7-91c4-7b92a6a187d0/scratchpad/poing/refs/pew/t_{t}.png"
R.compare(src, w, cam, out, titre=out.split('/')[-1])
print(G.resume(G.descripteurs(w, avant)))
