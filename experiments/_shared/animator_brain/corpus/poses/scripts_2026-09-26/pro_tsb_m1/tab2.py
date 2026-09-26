import sys; sys.path.insert(0, "/home/user/Jeux/experiments/_shared/animator_brain/outils"); import geo_pose as G
import numpy as np, charge as K
n = sys.argv[1]; a = int(sys.argv[2]) if len(sys.argv)>2 else 0; b = int(sys.argv[3]) if len(sys.argv)>3 else 10**6
mw = K.mondes(n)
prev = {}
for i,(t,w) in enumerate(mw):
    sp=[]
    for part in ('Right Arm','Left Arm','Right Leg','Left Leg'):
        bb = G.bout(w, part); v = np.linalg.norm(bb-prev[part])*60 if part in prev else 0; prev[part]=bb; sp.append(v)
    if not (a <= i <= b): continue
    d = G.descripteurs(w)
    pd = d['pieds']
    print(f"{i:3d} vR{sp[0]:5.1f} vL{sp[1]:5.1f} vRL{sp[2]:5.1f} vLL{sp[3]:5.1f} | " + G.resume(d) + f" | pieds RL {pd['RL']} LL {pd['LL']}")
