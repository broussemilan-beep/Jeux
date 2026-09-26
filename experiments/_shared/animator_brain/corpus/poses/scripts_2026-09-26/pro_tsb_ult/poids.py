import sys, numpy as np
sys.path.insert(0,'/home/user/Jeux/experiments/_shared'); sys.path.insert(0,'/home/user/Jeux/experiments/_shared/animator_brain/outils')
import rbxm_reader as R
P='/root/.claude/uploads/4796ac9e-8e41-51f7-91c4-7b92a6a187d0/b64ecce0-tsb_anim.rbxm'
_v,_nt,_ni,ch=R.read_chunks(P)
cl=R.parse_inst_chunks(ch)
props={}
for cls,pn,_dt,vals in R.parse_prop_chunks(ch,cl): props[(cls,pn)]=vals
print(sorted(k for k in props if k[0] in ('Pose','Keyframe','KeyframeSequence')))
ext=R.parse_prop_extended(ch,cl,{("Pose","CFrame"):"cframe"})
cfr=ext[("Pose","CFrame")]
parent=R.parse_prnt_chunk(ch)
seqn=props[("KeyframeSequence","Name")]
kft=props[("Keyframe","Time")]
pn=props[("Pose","Name")]; pw=props.get(("Pose","Weight"),{})
es=props.get(("Pose","EasingStyle"),{}); ed=props.get(("Pose","EasingDirection"),{})
def anc(ref,table):
    while ref in parent:
        ref=parent[ref]
        if ref in table: return ref
    return None
target=sys.argv[1]
rows=[]
for pr,nm in pn.items():
    kf=anc(pr,kft); s=anc(kf,seqn) if kf is not None else None
    if s is None or seqn[s]!=target: continue
    pos,rot,_=cfr[pr]
    rot=np.array(rot).reshape(3,3)
    ang=np.degrees(np.arccos(np.clip((np.trace(rot)-1)/2,-1,1)))
    rows.append((kft[kf],nm,pw.get(pr),es.get(pr),ed.get(pr),np.round(pos,2),round(ang,1)))
rows.sort(key=lambda r:(r[0],r[1]))
for r in rows:
    if r[1] in (sys.argv[2:] or ['Torso']): print(f"{r[0]*60:6.1f} {r[1]:12s} w={r[2]} es={r[3]} ed={r[4]} pos={r[5]} rotdeg={r[6]}")
