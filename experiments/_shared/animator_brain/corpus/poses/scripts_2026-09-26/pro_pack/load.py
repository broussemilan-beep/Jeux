import sys, pickle
sys.path.insert(0, "/home/user/Jeux/experiments/_shared/animator_brain/outils")
import geo_pose as G
sys.path.insert(0, "/home/user/Jeux/experiments/_shared")
from animator_brain import corpus as C
P="/root/.claude/uploads/4796ac9e-8e41-51f7-91c4-7b92a6a187d0/4b059cba-battleground_animation_pack_v1.0.1.rbxm"
seqs=C.load_rbxm_sequences(P)
print([ (s["name"], len(s["frames"])) for s in seqs])
names=['[2] M1_1','[2] M1_2','[2] M1_3','[2] M1_4','[3] Uppercut','[3] Downslam V1','[3] Downslam V2']
out={}
for n in names:
    fr=G.mondes_rbxm(P,n)
    out[n]=fr
    t,w=fr[0]
    print(n, len(fr), fr[-1][0], list(w.keys()))
pickle.dump(out, open("mondes.pkl","wb"))
for s in seqs:
    if s["name"] in names:
        print(s["name"], [round(f[0] if isinstance(f,tuple) else 0,3) for f in s["frames"]][:40] if isinstance(s["frames"][0],tuple) else type(s["frames"][0]))
