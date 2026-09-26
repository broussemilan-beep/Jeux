import sys, pickle, json, numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, "/home/user/Jeux/experiments/_shared/animator_brain/outils")
import geo_pose as G
M=pickle.load(open("mondes.pkl","rb"))
A={s["anim"]:s for s in json.load(open("analyse.json"))}
T=(380,340)
sel=[("[2] M1_4","f_arme"),("[2] M1_4","f_contact"),("[2] M1_1","f_arme"),("[2] M1_2","f_arme")]
cams=[("face",0,5),("sa droite",90,5),("derriere",180,10),("3/4 haut",45,30)]
sheet=Image.new("RGB",(T[0]*4+6,T[1]*len(sel)+2*(len(sel)-1)),(0,0,0))
for i,(n,key) in enumerate(sel):
    s=A[n]; f=s[key]; w=[w for t,w in M[n]][f]; av=tuple(s["avant"])
    tc=w["Torso"][1].copy(); tc[1]=2.2
    for j,(cn,az,el) in enumerate(cams):
        cam=G.camera_orbite(tc,az,el,9.5,50,avant=av)
        sheet.paste(G.rendre([w],cam,T,f"{n[4:]} {key[2:]} f{f} {cn}"),(j*(T[0]+2),i*(T[1]+2)))
sheet.save("zoom_armes.png")
