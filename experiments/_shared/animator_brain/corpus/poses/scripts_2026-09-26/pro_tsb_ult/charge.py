import sys, pickle, numpy as np
sys.path.insert(0, "/home/user/Jeux/experiments/_shared/animator_brain/outils"); import geo_pose as G
sys.path.insert(0,'/home/user/Jeux/experiments/_shared')
from animator_brain import corpus as C
P='/root/.claude/uploads/4796ac9e-8e41-51f7-91c4-7b92a6a187d0/b64ecce0-tsb_anim.rbxm'
NOMS=['Ultimate1','Ultimate2','Stoic Bomb','Collateral Ruin','Swift Sweep']
def load():
    out={}
    for n in NOMS:
        out[n]=G.mondes_rbxm(P,n)
    return out
if __name__=='__main__':
    D=load()
    pickle.dump(D, open('mondes.pkl','wb'))
    seqs={s['name']:s for s in C.load_rbxm_sequences(P)}
    for n in NOMS:
        s=seqs[n]
        print('==',n, 'nframes60', len(D[n]), 'priority', s['priority'], 'loop', s['loop'], 'poids_nul', s['poids_nul_fraction'])
        for t,poses in s['frames']:
            print(f"  kf t={t:.3f} f60={t*60:.1f} parts={sorted(poses.keys())}")
