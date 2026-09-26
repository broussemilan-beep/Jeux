import sys, pickle, numpy as np
sys.path.insert(0, "/home/user/Jeux/experiments/_shared/animator_brain/outils")
import geo_pose as G
M=pickle.load(open("mondes.pkl","rb"))
for n,fr in M.items():
    print("=====",n, len(fr))
    ws=[w for t,w in fr]
    for arm in ("Right Arm","Left Arm"):
        P=np.array([G.bout(w,arm) for w in ws])
        v=np.linalg.norm(np.diff(P,axis=0),axis=1)*60
        print(arm,"speed:", " ".join(f"{x:.0f}" for x in v))
    Tp=np.array([w["Torso"][1] for w in ws]); print("torso pos first/last", Tp[0].round(2), Tp[-1].round(2), "HRP", ws[0]["HumanoidRootPart"][1].round(2), ws[-1]["HumanoidRootPart"][1].round(2))
    for i,w in enumerate(ws):
        d=G.descripteurs(w)
        print(i, G.resume(d))
