import sys, pickle, json, numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, "/home/user/Jeux/experiments/_shared/animator_brain/outils")
import geo_pose as G
import moon as MO
M=pickle.load(open("mondes.pkl","rb"))
A=json.load(open("analyse.json"))
ARM={"RA":"Right Arm","LA":"Left Arm"}
T=(240,220)
cams=[("face",0,8),("sa droite",90,8),("3/4 haut",45,30)]
rows=[]
for s in A:
    ws=[w for t,w in M[s["anim"]]]
    av=tuple(s["avant"]); ks=list(s["trajet"].keys())
    row=[]
    for lab,f in (("ARME",s["f_arme"]),("CONTACT",s["f_contact"])):
        w=ws[f]; tc=w["Torso"][1].copy(); tc[1]=max(1.8,tc[1]-0.3)
        for cn,az,el in cams:
            cam=G.camera_orbite(tc,az,el,11,50,avant=av)
            row.append(G.rendre([w],cam,T,f"{s['anim'][4:]} {lab} f{f} {cn}"))
    # trajet vu de dessus (et 3/4) : pelure d'oignon bras frappeur + polyligne du poing
    for cn,az,el in (("dessus",0,85),("trajet 3/4",60,25)):
        worlds=[ws[s["f_arme"]]]+[{ARM[k]:ws[i][ARM[k]] for k in ks} for i in range(s["f_arme"]+1,s["f_contact"])]+[ws[s["f_contact"]]]
        pts={k:[G.bout(ws[i],ARM[k]) for i in range(s["f_arme"],s["f_contact"]+1)] for k in ks}
        tc=ws[s["f_arme"]]["Torso"][1]
        def extra(d,proj,pts=pts,tc=tc,av=av):
            for k,P in pts.items():
                q=[proj(p)[0] for p in P]
                d.line(q,fill=(255,0,200),width=3)
                for j,x in enumerate(q):
                    d.ellipse([x[0]-3,x[1]-3,x[0]+3,x[1]+3],fill=(255,255,0) if j==0 else ((255,60,60) if j==len(q)-1 else (255,0,200)))
            a=np.array(av); o=np.array([tc[0],0.05,tc[2]])
            p0=proj(o)[0]; p1=proj(o+3.5*a)[0]
            d.line([p0,p1],fill=(0,0,0),width=2); d.ellipse([p1[0]-4,p1[1]-4,p1[0]+4,p1[1]+4],fill=(0,0,0))
        cam=G.camera_orbite((tc[0],1.5,tc[2]),az,el,13,50,avant=av)
        row.append(MO.render(worlds,cam[0],cam[1],cam[2],T,title=f"{cn} f{s['f_arme']}->{s['f_contact']}",sky=(200,205,215),extra=extra))
    rows.append(row)
nc=len(rows[0])
sheet=Image.new("RGB",(T[0]*nc+ (nc-1)*2, T[1]*len(rows)+(len(rows)-1)*2+24),(0,0,0))
d=ImageDraw.Draw(sheet)
hdr=["ARME face","ARME sa droite","ARME 3/4 haut","CONTACT face","CONTACT sa droite","CONTACT 3/4 haut","TRAJET dessus (cible=pt noir)","TRAJET 3/4"]
for j,h in enumerate(hdr): d.text((j*(T[0]+2)+6,6),h,fill=(255,255,255))
for i,row in enumerate(rows):
    for j,im in enumerate(row):
        sheet.paste(im,(j*(T[0]+2),24+i*(T[1]+2)))
sheet.save("planche_pro_pack.png")
# moitiés pour lecture
w,h=sheet.size
sheet.crop((0,0,w//2+1,h)).save("planche_gauche.png"); sheet.crop((w//2,0,w,h)).save("planche_droite.png")
for i in range(0,len(rows),2):
    sheet.crop((0,24+i*(T[1]+2),w,24+min(len(rows),i+2)*(T[1]+2))).save(f"planche_lignes_{i}.png")
print(sheet.size)
