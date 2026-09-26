import sys, pickle, numpy as np
sys.path.insert(0,'.'); sys.path.insert(0, "/home/user/Jeux/experiments/_shared/animator_brain/outils")
import geo_pose as G
D=pickle.load(open('mondes_corriges.pkl','rb'))
n=sys.argv[1]; a=int(sys.argv[2]); b=int(sys.argv[3]); arm=sys.argv[4] if len(sys.argv)>4 else 'RA'
part={'RA':'Right Arm','LA':'Left Arm'}[arm]
fr=D[n]
print(f'{n} {arm}: f | vmonde vrel | lacet pen cote hanche | bras torse az el | bras coup az el | poing(f,r,u) | az_poing_horiz dist_h | recul_D')
for i in range(a,b+1):
    w=fr[i][1]; d=G.descripteurs(w)
    p=G.bout(w,part); pp=G.bout(fr[i-1][1],part)
    t=w['Torso'][1]; tp=fr[i-1][1]['Torso'][1]
    v=np.linalg.norm(p-pp)*60; vr=np.linalg.norm((p-t)-(pp-tp))*60
    po=d['poing'][arm]; azp=np.degrees(np.arctan2(po[1],po[0])); dh=np.hypot(po[0],po[1])
    B=d['buste']; bt=d['bras'][arm]['torse']; bc=d['bras'][arm]['coup']
    print(f"{i:4d} | {v:6.1f} {vr:6.1f} | {B['lacet']:+5.0f} {B['penche_avant']:+4.0f} {B['penche_cote']:+4.0f} {d['hanche']:4.2f} | {bt[0]:+5.0f} {bt[1]:+4.0f} | {bc[0]:+5.0f} {bc[1]:+4.0f} | {po[0]:+5.2f} {po[1]:+5.2f} {po[2]:+5.2f} | {azp:+5.0f} {dh:4.2f} | {d['epaules']['recul_droite']:+5.2f}")
