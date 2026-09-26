import sys, pickle, json, numpy as np
sys.path.insert(0, "/home/user/Jeux/experiments/_shared/animator_brain/outils")
import geo_pose as G
M=pickle.load(open("mondes.pkl","rb"))
A=json.load(open("analyse.json"))
ARM={"RA":"Right Arm","LA":"Left Arm"}
for s in A:
    ws=[w for t,w in M[s["anim"]]]; f,r=G.repere(tuple(s["avant"]))
    k=list(s["trajet"])[0]
    P=np.array([G.bout(w,ARM[k]) for w in ws]); v=np.r_[0,np.linalg.norm(np.diff(P,axis=0),axis=1)*60]
    fw,fr_,fc=s["f_arme"],s["f_lacher"],s["f_contact"]
    seg=np.linalg.norm(np.diff(P[fw:fc+1],axis=0),axis=1); L=seg.sum()
    last2=seg[-2:].sum()/L; last1=seg[-1]/L
    # settle after contact
    st=next((i for i in range(fc+1,len(ws)) if v[i]<5),None)
    Tz=np.array([w["Torso"][1]@f for w in ws]); Ty=np.array([w["Torso"][1][1] for w in ws])
    iback=int(np.argmin(Tz[:fc+1]))
    lac=[G.descripteurs(w,tuple(s["avant"]))["buste"]["lacet"] for w in ws]
    print(f"{s['anim']:16s} {k} armé f{fw} lâcher f{fr_} contact f{fc} | vitesses lâcher→contact+2: {[int(x) for x in v[fr_:fc+3]]}")
    print(f"   part du trajet dans la dernière image {last1:.0%}, 2 dernières {last2:.0%} | vmax {v[fr_:fc+1].max():.0f} à f{fr_+int(np.argmax(v[fr_:fc+1]))} | poing immobile (<5 st/s) dès f{st} ; fin f{len(ws)-1}")
    print(f"   torse avance (repère coup): f0 {Tz[0]:+.2f}, recul max f{iback} {Tz[iback]:+.2f}, armé {Tz[fw]:+.2f}, contact {Tz[fc]:+.2f} -> fente {Tz[fc]-Tz[iback]:+.2f} ; hanche min {Ty[:fc+1].min():.2f} à f{int(np.argmin(Ty[:fc+1]))}")
    print(f"   lacet par image armé→contact: {[round(x) for x in lac[fw:fc+1]]}")
