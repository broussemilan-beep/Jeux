import sys, json, numpy as np
from PIL import Image
sys.path.insert(0, ".")
from charge import W, V, cam_at, G, M
Y=np.array([0,1.0,0])
def orbite_de(cam, cible=None):
    eye,look,fov=cam
    c = look if cible is None else np.asarray(cible)
    v=eye-c; d=np.linalg.norm(v); h=np.hypot(v[0],v[2])
    az=np.degrees(np.arctan2(v[0], -v[2]))   # az0 = côté -Z (devant), +90 = +X (sa droite)
    el=np.degrees(np.arctan2(v[1], h))
    return round(float(az),1), round(float(el),1), round(float(d),2), round(float(fov),1)
def proj_fn(cam, size=(852,480)):
    eye,target,fov=cam; eye=np.asarray(eye,float); target=np.asarray(target,float)
    Wd,H=size; f=target-eye; f/=np.linalg.norm(f); r=np.cross(f,Y); r/=np.linalg.norm(r); u=np.cross(r,f)
    foc=(H/2)/np.tan(np.radians(fov)/2)
    def P(p):
        v=np.asarray(p)-eye; z=v@f
        return np.array([Wd/2+foc*(v@r)/max(z,1e-3), H/2-foc*(v@u)/max(z,1e-3)]), z
    return P, f
def coins(w, part):
    R,c=w[part]; h=np.array(M.SIZES[part])/2
    cs=np.array([[a,b,cc] for a in (-1,1) for b in (-1,1) for cc in (-1,1)])*h
    return (R@cs.T).T+c
PARTS=["Torso","Head","Right Arm","Left Arm","Right Leg","Left Leg"]
def cadrage(w, cam, size=(852,480)):
    P,_=proj_fn(cam,size); Wd,H=size
    pts=[]; inside={}
    for p in PARTS:
        cc=[P(x)[0] for x in coins(w,p)]
        pts+=cc
        inside[p]=np.mean([(0<=q[0]<=Wd and 0<=q[1]<=H) for q in cc])
    pts=np.array(pts)
    ymin,ymax=pts[:,1].min(),pts[:,1].max(); xmin,xmax=pts[:,0].min(),pts[:,0].max()
    # hauteur du perso à l'écran (non coupée) en % de la hauteur d'image
    return {"haut_perso_pct": round(100*(ymax-ymin)/H), "larg_perso_pct": round(100*(xmax-xmin)/Wd),
            "dans_cadre_pct": {k: int(round(100*v)) for k,v in inside.items()},
            "pieds_visibles": bool(inside["Right Leg"]>=0.99 and inside["Left Leg"]>=0.99)}
def aires(w, cam, size=(852,480)):
    col={"Torso":(100,100,100),"Head":(100,100,100),"Right Arm":(0,255,0),"Left Arm":(0,0,255),"Right Leg":(255,255,0),"Left Leg":(255,255,0)}
    im=M.render([w],cam[0],cam[1],cam[2],size,couleurs=col,ombre=False,contour=None,sky=(0,0,0),ground=False)
    a=np.asarray(im).reshape(-1,3)
    n=lambda c:int(((a==np.array(c)).all(1)).sum())
    tot=size[0]*size[1]
    return {"brasD_pct": round(100*n((0,255,0))/tot,1), "brasG_pct": round(100*n((0,0,255))/tot,1),
            "jambes_pct": round(100*n((255,255,0))/tot,1), "torse_tete_pct": round(100*n((100,100,100))/tot,1)}
def lisibilite(w_arme, w_garde, cam, size=(852,480)):
    """Ce que la charge change, projeté à l'écran (en % de la hauteur d'image)."""
    P,f=proj_fn(cam,size); H=size[1]
    fa=G.bout(w_arme,"Right Arm"); fg=G.bout(w_garde,"Right Arm")
    sa=G.haut(w_arme,"Right Arm"); sg=G.haut(w_garde,"Right Arm")
    d_poing=np.linalg.norm(P(fa)[0]-P(fg)[0])*100/H
    d_epaule=np.linalg.norm(P(sa)[0]-P(sg)[0])*100/H
    # raccourci : part du vecteur épaule D -> épaule G (ligne d'épaules) perpendiculaire à l'axe de vue
    def perp(v):
        v=np.asarray(v,float); return float(np.linalg.norm(v-(v@f)*f)/max(np.linalg.norm(v),1e-9))
    bras=fa-sa
    Rt=w_arme["Torso"][0]
    ligne_ep=Rt@np.array([1.0,0,0])
    avant=np.array([0,0,-1.0])
    return {"deplacement_poing_ecran_pct": round(d_poing,1), "deplacement_epaule_ecran_pct": round(d_epaule,1),
            "bras_D_visible_longueur": round(perp(bras),2), "ligne_epaules_visible": round(perp(ligne_ep),2),
            "axe_du_coup_visible": round(perp(avant),2),
            "epaule_recul_3d": round(float((sa-sg)@(-avant)),2), "poing_recul_3d": round(float((fa-fg)@(-avant)),2),
            "poing_depl_3d": round(float(np.linalg.norm(fa-fg)),2)}
if __name__=="__main__":
    out={}
    for f in (186,200,214,250,270):
        cam=cam_at(f); t=W[f]["Torso"][1]
        out[f]={"cam_v5_orbite(az,el,dist,fov)": orbite_de(cam, t), "cadrage": cadrage(W[f],cam), "aires": aires(W[f],cam),
                "lisib_vs_garde173": lisibilite(W[f], W[173], cam)}
    for f in (272,276,278,279,281,282):
        cam=cam_at(f); t=W[f]["Torso"][1]
        out[f]={"cam_v5_orbite(az,el,dist,fov)": orbite_de(cam, t), "cadrage": cadrage(W[f],cam), "aires": aires(W[f],cam)}
    for k,v in out.items(): print(k, json.dumps(v, ensure_ascii=False))
    json.dump(out, open("v5_cadrage_mesures.json","w"), indent=1, ensure_ascii=False)
    # rendus de contrôle à la caméra exacte v5
    ims=[]
    for f in (200,250,270,276,281):
        ims.append(G.rendre([W[f],V[f]], cam_at(f), (426,240), f"v5 f{f} cam exacte"))
    sh=Image.new("RGB",(426*5,240)); [sh.paste(im,(i*426,0)) for i,im in enumerate(ims)]; sh.save("rendus/v5_cam_exacte.png")
