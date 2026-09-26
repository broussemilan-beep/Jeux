import sys, json, numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, ".")
from charge import W, V, G, M, cam_at
from mesure_cam import aires, lisibilite, cadrage, proj_fn, orbite_de
S=(852,480)
def cible_corps(w): return w["Torso"][1]+np.array([0,-0.35,0])
def trajet_poing(cam, f0=270, f1=282):
    P,_=proj_fn(cam,S); pts=[P(G.bout(W[f],"Right Arm"))[0] for f in range(f0,f1+1)]
    d=np.linalg.norm(pts[-1]-pts[0])*100/S[1]
    dedans=np.mean([(0<=p[0]<=S[0] and 0<=p[1]<=S[1]) for p in pts])
    return round(float(d),1), int(round(100*dedans))
C={}
t250=cible_corps(W[250])
C["v5_reelle_charge"]=cam_at(250)
C["A_etab_large_az75_el30"]=G.camera_orbite(t250,75,30,13.0,40)
C["A2_etab_large_az120_el30"]=G.camera_orbite(t250,120,30,13.0,40)
C["B_tenue_moyen_az75_el20"]=G.camera_orbite(t250,75,20,7.4,40)
C["B2_tenue_moyen_az120_el20"]=G.camera_orbite(t250,120,20,7.4,40)
C["B3_tenue_moyen_az0_el20(face)"]=G.camera_orbite(t250,0,20,7.4,40)
t276=cible_corps(W[276])
C["v5_reelle_depart"]=cam_at(276)
C["D_depart_az60_el8"]=G.camera_orbite(t276+np.array([0,0.5,0]),60,8,6.0,45)
C["D2_depart_az-118_el8"]=G.camera_orbite(t276+np.array([0,0.5,0]),-118,8,6.0,45)
rows={}
for k,cam in C.items():
    f=276 if "depart" in k else 250
    r={"orbite(az,el,dist,fov)":orbite_de(cam, W[f]["Torso"][1]),"cadrage":cadrage(W[f],cam,S),"aires":aires(W[f],cam,S),
       "lisib":lisibilite(W[250],W[173],cam,S),"trajet_poing_270_282(%haut,%dans_cadre)":trajet_poing(cam)}
    rows[k]=r; print(k, json.dumps(r,ensure_ascii=False))
json.dump(rows,open("candidats_mesures.json","w"),indent=1,ensure_ascii=False)
# planche 1 : même pose v5 (f250), caméra v5 vs candidates
L=["v5_reelle_charge","A_etab_large_az75_el30","A2_etab_large_az120_el30","B_tenue_moyen_az75_el20","B2_tenue_moyen_az120_el20","B3_tenue_moyen_az0_el20(face)"]
ims=[G.rendre([W[250]],C[k],(426,240),k.replace("_"," ")[:48]) for k in L]
sh=Image.new("RGB",(426*3,240*2)); [sh.paste(im,((i%3)*426,(i//3)*240)) for i,im in enumerate(ims)]; sh.save("rendus/meme_pose_f250_cameras.png")
# planche 2 : départ du coup f270..282 en pelure (5 poses) depuis v5 réelle / D / D2
def pelure(cam, titre):
    ws=[W[f] for f in (270,274,277,280,282)]
    return G.rendre(ws,cam,(426,240),titre)
ims=[pelure(C["v5_reelle_depart"],"v5 reelle depart f272-278 (az47 el-13)"),pelure(C["D_depart_az60_el8"],"D depart az60 el8"),pelure(C["D2_depart_az-118_el8"],"D2 depart az-118 el8")]
sh=Image.new("RGB",(426*3,240)); [sh.paste(im,(i*426,0)) for i,im in enumerate(ims)]; sh.save("rendus/depart_pelure_cameras.png")
