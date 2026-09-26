import sys, pickle, numpy as np
sys.path.insert(0,'.')
import lecteur as L, geo_pose as G
D=pickle.load(open('mondes_corriges.pkl','rb'))
for n,fr in D.items():
    print('=====',n,len(fr))
    for part in ('Right Arm','Left Arm','Right Leg','Left Leg'):
        P=np.array([G.bout(w,part) for t,w in fr]); v=np.r_[0,np.linalg.norm(np.diff(P,axis=0),axis=1)*60]
        # segments above 25 studs/s
        thr=25; on=v>thr; segs=[]; i=0
        while i<len(v):
            if on[i]:
                j=i
                while j<len(v) and on[j]: j+=1
                k=i+int(np.argmax(v[i:j])); segs.append((i,j-1,k,round(v[k],1)))
                i=j
            else: i+=1
        print(' ',part, segs)
