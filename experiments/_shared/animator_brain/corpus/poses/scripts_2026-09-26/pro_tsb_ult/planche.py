import sys, pickle, numpy as np
sys.path.insert(0,'.'); sys.path.insert(0, "/home/user/Jeux/experiments/_shared/animator_brain/outils")
import geo_pose as G
from PIL import Image, ImageDraw
D=pickle.load(open('mondes_corriges.pkl','rb'))
CAMS=[(0,0,'face (az0)'),(90,0,'sa droite (az90)'),(45,30,'3/4 haut (az45 el30)')]
def cell(w, az, el, titre, taille=(300,300), dist=11, avant=(0,0,-1)):
    t=w['Torso'][1]; cible=(t[0], t[1]-0.3, t[2])
    cam=G.camera_orbite(cible, az, el, dist, 50, avant=avant)
    return G.rendre([w], cam, taille, titre)
def planche(items, sortie, taille=(300,300), dist=11):
    """items: [(anim, frame, label, avant)]"""
    rows=[]
    for anim,f,lab,avant in items:
        w=D[anim][f][1]
        ims=[cell(w,az,el,f"{anim} f{f} {lab} | {nm}",taille,dist,avant) for az,el,nm in CAMS]
        row=Image.new('RGB',(taille[0]*3+8,taille[1]),(0,0,0))
        for k,im in enumerate(ims): row.paste(im,(k*(taille[0]+4),0))
        rows.append(row)
    out=Image.new('RGB',(rows[0].width, sum(r.height+4 for r in rows)),(0,0,0))
    y=0
    for r in rows: out.paste(r,(0,y)); y+=r.height+4
    out.save(sortie); return out
if __name__=='__main__':
    anim=sys.argv[1]; frames=[int(x) for x in sys.argv[2].split(',')]; sortie=sys.argv[3]
    planche([(anim,f,'',(0,0,-1)) for f in frames], sortie, (260,260))
