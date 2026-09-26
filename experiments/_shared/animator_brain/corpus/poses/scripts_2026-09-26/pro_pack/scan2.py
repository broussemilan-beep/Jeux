import sys, numpy as np, pickle
sys.path.insert(0, "/home/user/Jeux/experiments/_shared/animator_brain/outils"); import geo_pose as G
D=pickle.load(open("mondes.pkl","rb"))
for n,fr in D.items():
    print("=====",n)
    prev=None
    for i,(t,w) in enumerate(fr):
        tor=w["Torso"][1]
        tips={k:G.bout(w,p) for k,p in [("RA","Right Arm"),("LA","Left Arm"),("RL","Right Leg"),("LL","Left Leg")]}
        v={k:(0 if prev is None else np.linalg.norm(tips[k]-prev[k])*60) for k in tips}
        prev=tips
        s=f"{i:3d} " + " ".join(f"v{k}={v[k]:5.1f}" for k in tips) + " | RL " + str(np.round(tips['RL']-tor,2))+" LL "+str(np.round(tips['LL']-tor,2)) + f" torsoY {tor[1]:.2f} z {tor[2]:+.2f}"
        print(s)
