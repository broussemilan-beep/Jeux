import sys, pickle, numpy as np
sys.path.insert(0, "/home/user/Jeux/experiments/_shared/animator_brain/outils")
import geo_pose as G
M=pickle.load(open("mondes.pkl","rb"))
names=sys.argv[1:] or list(M)
for n in names:
    fr=M[n]; ws=[w for t,w in fr]
    print("=====",n)
    P={a:np.array([G.bout(w,a) for w in ws]) for a in ("Right Arm","Left Arm")}
    V={a:np.r_[0,np.linalg.norm(np.diff(P[a],axis=0),axis=1)*60] for a in P}
    print(" f  hanc lac  pen cot | RAaz RAel  RAf   RAr   RAu  vR  reachR| LAaz LAel  LAf   LAr   LAu  vL reachL| recD  RLf RLr LLf LLr")
    for i,w in enumerate(ws):
        d=G.descripteurs(w); b=d["buste"]
        tc=w["Torso"][1]
        rr=np.linalg.norm((P["Right Arm"][i]-tc)[[0,2]]); rl=np.linalg.norm((P["Left Arm"][i]-tc)[[0,2]])
        ra=d["bras"]["RA"]["torse"]; la=d["bras"]["LA"]["torse"]; pr=d["poing"]["RA"]; pl=d["poing"]["LA"]
        print(f"{i:2d} {d['hanche']:.2f} {b['lacet']:+4.0f} {b['penche_avant']:+3.0f} {b['penche_cote']:+3.0f} | {ra[0]:+4.0f} {ra[1]:+4.0f} {pr[0]:+5.2f} {pr[1]:+5.2f} {pr[2]:+5.2f} {V['Right Arm'][i]:3.0f} {rr:4.2f} | {la[0]:+4.0f} {la[1]:+4.0f} {pl[0]:+5.2f} {pl[1]:+5.2f} {pl[2]:+5.2f} {V['Left Arm'][i]:3.0f} {rl:4.2f} | {d['epaules']['recul_droite']:+5.2f} {d['pieds']['RL'][0]:+.2f} {d['pieds']['RL'][1]:+.2f} {d['pieds']['LL'][0]:+.2f} {d['pieds']['LL'][1]:+.2f}")
