import sys, numpy as np, pickle, json
sys.path.insert(0, "/home/user/Jeux/experiments/_shared/animator_brain/outils"); import geo_pose as G
D=pickle.load(open("mondes.pkl","rb"))
for n,i in [('[3] Downslam V2',0),('[3] Downslam V2',10),('[3] Downslam V2',13),('[3] Downslam V2',15)]:
    t,w=D[n][i]
    d=G.descripteurs(w)
    print(n,i,json.dumps(d))
    Rt,pt=w["Torso"]
    print(" torso up", np.round(Rt@np.array([0,1,0]),2), "fwd", np.round(Rt@np.array([0,0,-1]),2), "right",np.round(Rt@np.array([1,0,0]),2))
    for p in ["Right Arm","Left Arm"]:
        R,pp=w[p]; print(" ",p,"center rel",np.round(pp-pt,2),"dir",np.round(R@np.array([0,-1,0]),2),"top",np.round(G.haut(w,p)-pt,2))
