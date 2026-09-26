import sys, pickle, numpy as np
sys.path.insert(0,'.')
import lecteur as L, geo_pose as G
D={n:L.mondes(n) for n in L.NOMS}
pickle.dump(D,open('mondes_corriges.pkl','wb'))
for n,fr in D.items():
    with open(f'dump_{n.replace(" ","_")}.txt','w') as f:
        pr=None; pl=None
        for i,(t,w) in enumerate(fr):
            r=G.bout(w,'Right Arm'); l=G.bout(w,'Left Arm')
            vr=0 if pr is None else np.linalg.norm(r-pr)*60; vl=0 if pl is None else np.linalg.norm(l-pl)*60
            pr,pl=r,l
            d=G.descripteurs(w)
            f.write(f"{i:4d} vR {vr:5.1f} vL {vl:5.1f} | tors {np.round(w['Torso'][1],2)} | "+G.resume(d)+f" | pieds {d['pieds']}\n")
