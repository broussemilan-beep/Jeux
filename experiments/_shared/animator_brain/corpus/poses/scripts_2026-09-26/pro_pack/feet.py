import sys, pickle, numpy as np
sys.path.insert(0, "/home/user/Jeux/experiments/_shared/animator_brain/outils")
import geo_pose as G
M=pickle.load(open("mondes.pkl","rb"))
for n,fs in [("[2] M1_1",[0,5,10,13,15,18,25]),("[2] M1_2",[0,4,8,11,20]),("[2] M1_4",[0,6,9,12,16,25]),("[3] Uppercut",[0,14,18,21,25]),("[3] Downslam V1",[0,14,20,25]),("[3] Downslam V2",[0,13,15,20])]:
    ws=[w for t,w in M[n]]
    print("==",n)
    for f in fs:
        w=ws[f]
        s=[]
        for p in ("Right Leg","Left Leg"):
            b=G.bout(w,p); R=w[p][0]; 
            # leg yaw: direction of leg's -Z (front face) horizontal
            fz=R@np.array([0,0,-1.0]); yaw=np.degrees(np.arctan2(fz[0],-fz[2]))
            s.append(f"{p[0]}: x{b[0]:+.2f} z{b[2]:+.2f} y{b[1]:+.2f} yawPied{yaw:+.0f}")
        T=w["Torso"][1]
        print(f" f{f:2d} torse x{T[0]:+.2f} z{T[2]:+.2f} y{T[1]:.2f} | "+" | ".join(s))
