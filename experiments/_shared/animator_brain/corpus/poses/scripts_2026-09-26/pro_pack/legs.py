import sys, pickle, numpy as np
sys.path.insert(0, "/home/user/Jeux/experiments/_shared/animator_brain/outils")
import geo_pose as G
M=pickle.load(open("mondes.pkl","rb"))
for n,fr in M.items():
    ws=[w for t,w in fr]
    print("==",n)
    for p in ("Right Leg","Left Leg","Head"):
        P=np.array([G.bout(w,p) for w in ws])
        v=np.r_[0,np.linalg.norm(np.diff(P,axis=0),axis=1)*60]
        print(p, "v:", " ".join(f"{x:.0f}" for x in v))
    T=np.array([w["Torso"][1] for w in ws]); print("torso xyz:", " ".join(f"({a:.2f},{b:.2f},{c:.2f})" for a,b,c in T[::3]))
