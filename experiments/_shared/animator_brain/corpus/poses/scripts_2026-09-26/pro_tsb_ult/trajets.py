import sys, json, pickle, numpy as np
sys.path.insert(0,'.'); sys.path.insert(0, "/home/user/Jeux/experiments/_shared/animator_brain/outils")
import geo_pose as G
from PIL import Image, ImageDraw
D=pickle.load(open('mondes_corriges.pkl','rb'))
C=json.load(open('coups.json'))
PART={'RA':'Right Arm','LA':'Left Arm'}
S=60; W=H=420
def dessin(cid,c,marge_av=20,marge_ap=6):
    fr=D[c['anim']]; av=np.array(c['avant']); f_,r_=G.repere(av); part=PART[c['bras']]
    a=c['temps']['arme']; k=c['temps']['contact']
    im=Image.new('RGB',(2*W+10,H+40),(245,245,245)); dr=ImageDraw.Draw(im)
    for ox,titre in ((0,'DESSUS : haut = avant (cible), droite = sa droite'),(W+10,'PROFIL : droite = avant, haut = haut')):
        dr.rectangle([ox,0,ox+W,H],outline=(0,0,0)); dr.text((ox+4,H+4),titre,fill=(0,0,0))
        cx,cy=ox+W//2,H//2
        dr.line([cx-4,cy,cx+4,cy],fill=(0,0,0)); dr.line([cx,cy-4,cx,cy+4],fill=(0,0,0))
        for g in range(-3,4):
            dr.line([cx+g*S,0,cx+g*S,H],fill=(225,225,225)); dr.line([ox,cy+g*S,ox+W,cy+g*S],fill=(225,225,225))
    dr.text((4,H+20),f"{cid}  armé f{a} (bleu) -> contact f{k} (rouge); points gris = avant armé; torse = trait",fill=(0,0,0))
    i0=max(1,a-marge_av); i1=min(len(fr)-1,k+marge_ap)
    for i in range(i0,i1+1):
        w=fr[i][1]; t=w['Torso'][1]; v=G.bout(w,part)-t
        x,y,h=v@f_,v@r_,v[1]
        if i<a: col=(170,170,170)
        elif i<=k: u=(i-a)/max(1,k-a); col=(int(40+215*u),40,int(255-215*u))
        else: col=(255,170,170)
        # dessus
        cx,cy=W//2,H//2; px,py=cx+y*S,cy-x*S; dr.ellipse([px-3,py-3,px+3,py+3],fill=col)
        if i in (a,k) or (a<i<k and (i-a)%max(1,(k-a)//4)==0):
            Rt=w['Torso'][0]; fh=Rt@np.array([0,0,-1.0]); fh[1]=0; fh/=np.linalg.norm(fh)
            ex,ey=fh@f_,fh@r_; dr.line([cx,cy,cx+ey*S*1.2,cy-ex*S*1.2],fill=col,width=3)
            rh=Rt@np.array([1.0,0,0]); dr.line([cx-(rh@r_)*S,cy+(rh@f_)*S,cx+(rh@r_)*S,cy-(rh@f_)*S],fill=col,width=1)
            dr.text((px+4,py-4),str(i),fill=col)
        # profil
        cx2=W+10+W//2; px2,py2=cx2+x*S,H//2-h*S; dr.ellipse([px2-3,py2-3,px2+3,py2+3],fill=col)
        if i in (a,k): dr.text((px2+4,py2-4),str(i),fill=col)
    im.save(f'trajet_{cid}.png'); return im
ims=[dessin(cid,c) for cid,c in C.items()]
out=Image.new('RGB',(ims[0].width,sum(i.height+6 for i in ims)),(0,0,0)); y=0
for i in ims: out.paste(i,(0,y)); y+=i.height+6
out.save('trajets_tous.png'); print(out.size)
