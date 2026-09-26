import sys, pickle, numpy as np
sys.path.insert(0,'.')
import lecteur as L, geo_pose as G
D=pickle.load(open('mondes_corriges.pkl','rb'))
n=sys.argv[1]; step=int(sys.argv[2]); a=int(sys.argv[3]) if len(sys.argv)>3 else 0; b=int(sys.argv[4]) if len(sys.argv)>4 else 10**9
fr=D[n]
def rel(w,part): return G.bout(w,part)-w['Torso'][1]
print(' f  vRrel vLrel | lac  pen cote hanc | RA_t az  el | LA_t az  el | poingR f,r,u | poingL f,r,u | tete_t')
for i in range(max(a,0),min(b,len(fr)),step):
    w=fr[i][1]; d=G.descripteurs(w)
    vr=np.linalg.norm(rel(w,'Right Arm')-rel(fr[i-1][1],'Right Arm'))*60 if i>0 else 0
    vl=np.linalg.norm(rel(w,'Left Arm')-rel(fr[i-1][1],'Left Arm'))*60 if i>0 else 0
    B=d['buste']; ra=d['bras']['RA']['torse']; la=d['bras']['LA']['torse']
    print(f"{i:4d} {vr:5.1f} {vl:5.1f} | {B['lacet']:+5.0f} {B['penche_avant']:+4.0f} {B['penche_cote']:+4.0f} {d['hanche']:4.2f} | {ra[0]:+5.0f} {ra[1]:+4.0f} | {la[0]:+5.0f} {la[1]:+4.0f} | {d['poing']['RA'][0]:+5.2f} {d['poing']['RA'][1]:+5.2f} {d['poing']['RA'][2]:+5.2f} | {d['poing']['LA'][0]:+5.2f} {d['poing']['LA'][1]:+5.2f} {d['poing']['LA'][2]:+5.2f} | {d['tete']['torse'][0]:+4.0f} {d['tete']['torse'][1]:+4.0f}")
