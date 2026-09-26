"""python3 essai.py <t> <sortie> '<params python dict>' '<cam dict>' [avant]"""
import sys, json, ast
import numpy as np
sys.path.insert(0, "/tmp/claude-0/-home-user-Jeux/4796ac9e-8e41-51f7-91c4-7b92a6a187d0/scratchpad/poing/wf/recon_pew_c")
import rendu as R
import geo_pose as G
t, out, ps, cs = sys.argv[1:5]
avant = ast.literal_eval(sys.argv[5]) if len(sys.argv) > 5 else (0, 0, -1)
p = ast.literal_eval(ps); c = ast.literal_eval(cs)
w = G.pose(p)
tc = w["Torso"][1]
cible = c.pop("cible", tuple(tc))
cam = R.camera(cible, avant=avant, **c)
R.compare(f"/tmp/claude-0/-home-user-Jeux/4796ac9e-8e41-51f7-91c4-7b92a6a187d0/scratchpad/poing/refs/pew/t_{t}.png" if not t.startswith('/') else t, w, cam, out, titre=out.split('/')[-1])
d = G.descripteurs(w, avant)
print(G.resume(d))
print("pieds", d["pieds"], "tete", d.get("tete"))
