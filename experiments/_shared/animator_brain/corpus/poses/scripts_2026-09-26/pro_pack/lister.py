import sys; sys.path.insert(0, "/home/user/Jeux/experiments/_shared/animator_brain/outils"); import geo_pose as G
sys.path.insert(0, "/home/user/Jeux/experiments/_shared")
from animator_brain import corpus as C
P="/root/.claude/uploads/4796ac9e-8e41-51f7-91c4-7b92a6a187d0/4b059cba-battleground_animation_pack_v1.0.1.rbxm"
seqs=C.load_rbxm_sequences(P)
for s in seqs:
    ts=[round(t,3) for t,_ in s["frames"]]
    parts=set()
    for t,p in s["frames"]: parts|=set(p.keys())
    print(repr(s["name"]), s["loop"], s["priority"], len(ts), ts[:3], ts[-1], sorted(parts))
