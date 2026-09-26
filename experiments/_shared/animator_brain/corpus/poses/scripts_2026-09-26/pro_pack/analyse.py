import sys, pickle, json, numpy as np
sys.path.insert(0, "/home/user/Jeux/experiments/_shared/animator_brain/outils")
import geo_pose as G
M=pickle.load(open("mondes.pkl","rb"))
ARM={"RA":"Right Arm","LA":"Left Arm"}
# (anim, bras, armé, début lâcher, contact, début préparation)
STRIKES=[
 ("[2] M1_1","RA",10,10,15,0),
 ("[2] M1_2","LA",4,5,11,0),
 ("[2] M1_3","LA",9,10,15,0),
 ("[2] M1_4","RA",6,7,16,0),
 ("[3] Uppercut","RA",14,14,21,0),
 ("[3] Downslam V1","RA+LA",14,15,25,0),
 ("[3] Downslam V2","RA",13,13,15,0),
]
def fist(w,k): return G.bout(w,ARM[k])
res=[]
for anim,bras,fw,fr_,fc,f0 in STRIKES:
    ws=[w for t,w in M[anim]]
    ks=["RA","LA"] if bras=="RA+LA" else [bras]
    wc=ws[fc]; tc=wc["Torso"][1]
    fc_pos=np.mean([fist(wc,k) for k in ks],axis=0)
    v=fc_pos-tc; v[1]=0
    avant=tuple(np.round(v/np.linalg.norm(v),4))
    ang=np.degrees(np.arctan2(v[0],-v[2]))  # + = vers sa droite
    dW=G.descripteurs(ws[fw],avant); dC=G.descripteurs(ws[fc],avant)
    f,r=G.repere(avant)
    # trajet du poing
    out={"anim":anim,"bras":bras,"f_arme":fw,"f_lacher":fr_,"f_contact":fc,
         "avant":[float(x) for x in avant],"avant_angle_deg_droite":round(float(ang),1),
         "desc_arme":dW,"desc_contact":dC}
    paths={}
    for k in ks:
        pts=[]
        for i in range(fw,fc+1):
            w=ws[i]; p=fist(w,k)
            pts.append([float(p@f),float(p@r),float(p[1])])  # repère du coup, origine = racine fixe
        P=np.array(pts)
        seg=np.linalg.norm(np.diff(P,axis=0),axis=1); L=seg.sum(); ch=np.linalg.norm(P[-1]-P[0])
        u=(P[-1]-P[0])/ch
        dev=max(np.linalg.norm((p-P[0])-((p-P[0])@u)*u) for p in P)
        # angle balayé autour de l'axe vertical passant par le centre du torse (moyenné)
        tcs=np.array([[ws[i]["Torso"][1]@f, ws[i]["Torso"][1]@r] for i in range(fw,fc+1)])
        hz=P[:,:2]-tcs
        a=np.degrees(np.unwrap(np.arctan2(hz[:,1],hz[:,0])))
        dWk=dW["bras"][k]; dCk=dC["bras"][k]
        paths[k]={"pts_fwd_right_up_monde":[[round(x,2) for x in p] for p in pts],
          "longueur":round(float(L),2),"corde":round(float(ch),2),"rectitude":round(float(ch/L),2),
          "ecart_max_a_la_corde":round(float(dev),2),
          "angle_balaye_autour_du_torse_deg":round(float(a[-1]-a[0]),0),
          "rayon_horiz_min_max":[round(float(np.linalg.norm(hz,axis=1).min()),2),round(float(np.linalg.norm(hz,axis=1).max()),2)],
          "dz_vertical":round(float(P[-1,2]-P[0,2]),2),
          "d_lacet":round(dC["buste"]["lacet"]-dW["buste"]["lacet"],1),
          "d_penche":round(dC["buste"]["penche_avant"]-dW["buste"]["penche_avant"],1),
          "d_bras_az_torse":round(dCk["torse"][0]-dWk["torse"][0],1),
          "d_bras_el_torse":round(dCk["torse"][1]-dWk["torse"][1],1),
          "d_bras_az_coup":round(((dCk["coup"][0]-dWk["coup"][0]+180)%360)-180,1),
          "d_bras_el_coup":round(dCk["coup"][1]-dWk["coup"][1],1),
          "torse_translation_avant":round(float((wc["Torso"][1]-ws[fw]["Torso"][1])@f),2),
          "torse_dy":round(float(wc["Torso"][1][1]-ws[fw]["Torso"][1][1]),2)}
    out["trajet"]=paths
    # vitesse
    for k in ks:
        Pp=np.array([fist(w,k) for w in ws]); vv=np.r_[0,np.linalg.norm(np.diff(Pp,axis=0),axis=1)*60]
        out.setdefault("vitesse_poing",{})[k]=[round(float(x)) for x in vv]
        out.setdefault("vitesse_max",{})[k]=[int(np.argmax(vv[fr_:fc+2])+fr_), round(float(vv[fr_:fc+2].max()))]
    res.append(out)
    print("=====",anim,bras,"armé",fw,"lâcher",fr_,"contact",fc,"avant",avant,f"({ang:+.0f}° à sa droite)")
    print(" ARMÉ   :",G.resume(dW)); print("         pieds",dW["pieds"],"tete",dW.get("tete"))
    print(" CONTACT:",G.resume(dC)); print("         pieds",dC["pieds"],"tete",dC.get("tete"))
    for k,p in paths.items():
        print(" ",k,{kk:vv for kk,vv in p.items() if kk!="pts_fwd_right_up_monde"})
        print("   pts:",p["pts_fwd_right_up_monde"])
json.dump(res,open("analyse.json","w"),indent=1,ensure_ascii=False)
