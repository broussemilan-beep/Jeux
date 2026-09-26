"""Lecteur TSB corrigé : ignore les Pose de Weight 0 (conteneurs vides posés
par l'Animation Editor pour porter les enfants ; CFrame identité). Sinon
resample_linear les traite comme des clés et le Torso retombe à l'identité."""
import sys, numpy as np
sys.path.insert(0,'/home/user/Jeux/experiments/_shared'); sys.path.insert(0,'/home/user/Jeux/experiments/_shared/animator_brain/outils')
import rbxm_reader as R
import geo_pose as G
from animator_brain import corpus as C
P='/root/.claude/uploads/4796ac9e-8e41-51f7-91c4-7b92a6a187d0/b64ecce0-tsb_anim.rbxm'
NOMS=['Ultimate1','Ultimate2','Stoic Bomb','Collateral Ruin','Swift Sweep']

def sequences(path=P, garder_poids_nul=False):
    _v,_nt,_ni,ch=R.read_chunks(path)
    cl=R.parse_inst_chunks(ch)
    props={}
    for cls,pn,_dt,vals in R.parse_prop_chunks(ch,cl): props[(cls,pn)]=vals
    ext=R.parse_prop_extended(ch,cl,{("Pose","CFrame"):"cframe"})
    cfr=ext[("Pose","CFrame")]; parent=R.parse_prnt_chunk(ch)
    seqn=props[("KeyframeSequence","Name")]; kft=props[("Keyframe","Time")]
    pn=props[("Pose","Name")]; pw=props.get(("Pose","Weight"),{})
    def anc(ref,table):
        while ref in parent:
            ref=parent[ref]
            if ref in table: return ref
        return None
    seqs={s:{} for s in seqn}
    for kf,t in kft.items():
        s=anc(kf,seqn)
        if s is not None: seqs[s][kf]=(t,{})
    for pr,nm in pn.items():
        kf=anc(pr,kft); s=anc(kf,seqn) if kf is not None else None
        if s is None: continue
        if not garder_poids_nul and float(pw.get(pr,1.0))==0.0: continue
        pos,rot,_=cfr[pr]
        seqs[s][kf][1][nm]=(np.array(rot,float).reshape(3,3),np.array(pos,float))
    return {seqn[s]:sorted(v.values(),key=lambda f:f[0]) for s,v in seqs.items()}

def mondes(nom, path=P, fps=60):
    return C.resample_linear(sequences(path)[nom], fps)
