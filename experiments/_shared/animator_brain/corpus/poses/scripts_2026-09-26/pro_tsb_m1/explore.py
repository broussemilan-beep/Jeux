import sys; sys.path.insert(0, "/home/user/Jeux/experiments/_shared/animator_brain/outils"); import geo_pose as G
import numpy as np
from animator_brain import corpus as C
P='/root/.claude/uploads/4796ac9e-8e41-51f7-91c4-7b92a6a187d0/b64ecce0-tsb_anim.rbxm'
seqs = {s['name']: s for s in C.load_rbxm_sequences(P)}
for n in ['M1','M2','M3','M4','WallComboPlayer']:
    s = seqs[n]
    print('==', n, 'nkeys', len(s['frames']))
    for fr in s['frames'][:3]:
        print('  ', type(fr), len(fr), [type(x) for x in fr][:4])
    print('  key times', [round(fr[0],3) for fr in s['frames']])
    mw = G.mondes_rbxm(P, n)
    print('  nframes60', len(mw), 'parts', list(mw[0][1].keys()))
