import sys, pickle, numpy as np
sys.path.insert(0,'.')
import lecteur as L, geo_pose as G
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
D=pickle.load(open('mondes_corriges.pkl','rb'))
fig,axs=plt.subplots(len(D),1,figsize=(18,4*len(D)))
for ax,(n,fr) in zip(axs,D.items()):
    R=np.array([G.bout(w,'Right Arm') for t,w in fr]); Lf=np.array([G.bout(w,'Left Arm') for t,w in fr])
    RL=np.array([G.bout(w,'Right Leg') for t,w in fr]); LL=np.array([G.bout(w,'Left Leg') for t,w in fr])
    v=lambda P: np.r_[0,np.linalg.norm(np.diff(P,axis=0),axis=1)*60]
    ds=[G.descripteurs(w) for t,w in fr]
    lac=np.array([d['buste']['lacet'] for d in ds]); pen=np.array([d['buste']['penche_avant'] for d in ds]); han=np.array([d['hanche'] for d in ds])
    x=np.arange(len(fr))
    ax.plot(x,v(R),'g',label='vPoingD'); ax.plot(x,v(Lf),'b',label='vPoingG')
    ax.plot(x,v(RL),'y',lw=.8,label='vPiedD'); ax.plot(x,v(LL),color='orange',lw=.8,label='vPiedG')
    ax2=ax.twinx(); ax2.plot(x,lac,'r--',label='lacet'); ax2.plot(x,pen,'m:',label='penche'); ax2.plot(x,han*30,'k-.',lw=.6,label='hanche*30')
    ax.set_title(n); ax.set_xticks(np.arange(0,len(fr),10)); ax.tick_params(axis='x',labelsize=6); ax.grid(alpha=.3)
    ax.legend(loc='upper left',fontsize=7); ax2.legend(loc='upper right',fontsize=7)
plt.tight_layout(); plt.savefig('courbes.png',dpi=70)
