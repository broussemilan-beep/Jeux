import sys, json, numpy as np
sys.path.insert(0, "/home/user/Jeux/experiments/_shared/animator_brain/outils"); import geo_pose as G
import moon as M
SRC="/home/user/Jeux/experiments/r6_un_seul_coup/output/"
W=G.mondes_rbxmx(SRC+"usc_attaquant.rbxmx")
V=G.mondes_rbxmx(SRC+"usc_victime.rbxmx")
ST=json.load(open(SRC+"staging.json"))
CAM=ST["camera"]
def cam_at(f):
    ks=CAM
    for i in range(len(ks)-1):
        k,n=ks[i],ks[i+1]
        if k[0]<=f<n[0]:
            if n[4]=="cut": return (np.array(k[1]),np.array(k[2]),k[3])
            u=(f-k[0])/(n[0]-k[0])
            return (np.array(k[1])+(np.array(n[1])-np.array(k[1]))*u, np.array(k[2])+(np.array(n[2])-np.array(k[2]))*u, k[3]+(n[3]-k[3])*u)
    k=ks[-1]; return (np.array(k[1]),np.array(k[2]),k[3])
if __name__=="__main__":
    print(len(W), W[214]["Torso"][1], V[214]["Torso"][1] if len(V)>214 else None)
