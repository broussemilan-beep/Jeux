import sys, json, pickle, numpy as np
sys.path.insert(0,'.'); sys.path.insert(0, "/home/user/Jeux/experiments/_shared/animator_brain/outils")
import geo_pose as G
from PIL import Image, ImageDraw
D=pickle.load(open('mondes_corriges.pkl','rb'))
C=json.load(open('coups.json'))
CAMS=[(0,0,'face az0'),(90,0,'sa droite az90'),(45,30,'3/4 az45 el30')]
T=(300,300)
def cellule(ws, w0, az, el, titre, av, dist=11):
    t=w0['Torso'][1]; cam=G.camera_orbite((t[0],t[1]-0.3,t[2]),az,el,dist,50,avant=av)
    return G.rendre(ws,cam,T,titre)
def ligne(ims):
    r=Image.new('RGB',(T[0]*len(ims)+4*(len(ims)-1),T[1]),(0,0,0))
    for k,im in enumerate(ims): r.paste(im,(k*(T[0]+4),0))
    return r
tout=[]
for cid,c in C.items():
    fr=D[c['anim']]; av=tuple(c['avant']); a=c['temps']['arme']; k=c['temps']['contact']
    rows=[]
    for f,lab in ((a,'ARME'),(k,'CONTACT')):
        w=fr[f][1]; rows.append(ligne([cellule([w],w,az,el,f"{cid} f{f} {lab} | {nm}",av) for az,el,nm in CAMS]))
    idx=np.linspace(a,k,6).astype(int); ws=[fr[i][1] for i in idx]
    rows.append(ligne([cellule(ws,fr[k][1],0,85,f"pelure {idx.tolist()} | dessus (avant=haut img?)",av,13),
                       cellule(ws,fr[k][1],45,30,"pelure | 3/4",av,13),
                       cellule(ws,fr[k][1],180,20,"pelure | de dos az180",av,13)]))
    out=Image.new('RGB',(rows[0].width,sum(r.height+4 for r in rows)),(0,0,0)); y=0
    for r in rows: out.paste(r,(0,y)); y+=r.height+4
    out.save(f'planche_{cid}.png'); tout.append(out)
    print('ok',cid)
# planche globale armé/contact seulement, 3/4 + face
