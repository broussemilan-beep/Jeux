import sys; sys.path.insert(0, "/home/user/Jeux/experiments/_shared/animator_brain/outils"); import geo_pose as G
import numpy as np
P='/root/.claude/uploads/4796ac9e-8e41-51f7-91c4-7b92a6a187d0/b64ecce0-tsb_anim.rbxm'
n = sys.argv[1]
import charge as K
mw = K.mondes(n)
prev = {}
for i,(t,w) in enumerate(mw):
    d = G.descripteurs(w)
    line = f"{i:3d} t{t:.3f} "
    sp = []
    for part in ('Right Arm','Left Arm'):
        b = G.bout(w, part)
        v = np.linalg.norm(b - prev[part])*60 if part in prev else 0
        prev[part] = b
        sp.append(v)
    tp = w['Torso'][1]
    hrp = w['HumanoidRootPart'][1]
    line += f"vR {sp[0]:5.1f} vL {sp[1]:5.1f} | torso ({tp[0]:+.2f},{tp[1]:.2f},{tp[2]:+.2f}) | " + G.resume(d)
    print(line)
