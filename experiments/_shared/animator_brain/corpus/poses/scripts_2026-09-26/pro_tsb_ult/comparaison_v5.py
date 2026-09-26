import sys, pickle, numpy as np
sys.path.insert(0,'.'); sys.path.insert(0, "/home/user/Jeux/experiments/_shared/animator_brain/outils")
import geo_pose as G
from PIL import Image, ImageDraw
D=pickle.load(open('mondes_corriges.pkl','rb'))
# v5 f240 (tenue) reconstruit depuis ses descripteurs (jambes NON reproduites : neutres)
v5=G.pose({"hanche":2.37,"buste":(-64,28,0),"RA":(11,-6),"LA":(-116,-36)})
print('v5 recon :',G.resume(G.descripteurs(v5)))
items=[('v5 f240 (recon, jambes neutres)',v5),('TSB U1 f432 poing a la hanche',D['Ultimate1'][432][1]),('TSB U2 f93 revers arme',D['Ultimate2'][93][1]),('TSB CR f60 deux mains',D['Collateral Ruin'][60][1]),('TSB SB f150 bras en X',D['Stoic Bomb'][150][1])]
CAMS=[(0,0,'face'),(90,0,'sa droite'),(45,30,'3/4 haut'),(0,85,'dessus')]
T=(240,240)
rows=[]
for lab,w in items:
    t=w['Torso'][1]; ims=[]
    for az,el,nm in CAMS:
        cam=G.camera_orbite((t[0],t[1]-0.3,t[2]),az,el,11,50); ims.append(G.rendre([w],cam,T,f"{lab} | {nm}"))
    r=Image.new('RGB',(T[0]*4+12,T[1]),(0,0,0))
    for k,im in enumerate(ims): r.paste(im,(k*(T[0]+4),0))
    rows.append(r)
out=Image.new('RGB',(rows[0].width,sum(r.height+4 for r in rows)),(0,0,0)); y=0
for r in rows: out.paste(r,(0,y)); y+=r.height+4
out.save('comparaison_armes_v5_vs_tsb.png'); print(out.size)
