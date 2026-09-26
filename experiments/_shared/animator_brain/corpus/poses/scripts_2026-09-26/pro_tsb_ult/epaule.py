import sys,pickle,numpy as np
sys.path.insert(0,'.'); sys.path.insert(0, "/home/user/Jeux/experiments/_shared/animator_brain/outils")
import geo_pose as G
C1={'Right Arm':np.array([-0.5,0.5,0]),'Left Arm':np.array([0.5,0.5,0]),'Right Leg':np.array([0.5,1,0]),'Left Leg':np.array([-0.5,1,0])}
NOM={'Right Arm':np.array([1,0.5,0]),'Left Arm':np.array([-1,0.5,0]),'Right Leg':np.array([1,-1,0]),'Left Leg':np.array([-1,-1,0])}
def decalage(w,part):
    """décalage du pivot (épaule/hanche) par rapport au pivot nominal, axes du torse, (droite, haut, AVANT)."""
    Rt,pt=w['Torso']; R,p=w[part]
    piv=Rt.T@(R@C1[part]+p-pt)
    d=piv-NOM[part]
    return np.round([d[0],d[1],-d[2]],2)
def local_torse(w,v):
    Rt,pt=w['Torso']; l=Rt.T@(v-pt); return np.round([l[0],l[1],-l[2]],2)  # (droite, haut, avant)
if __name__=='__main__':
    D=pickle.load(open('mondes_corriges.pkl','rb'))
    for n,fr in D.items():
        mags={p:[np.linalg.norm(decalage(w,p)) for t,w in fr] for p in C1}
        print(n, {p:(round(float(np.max(m)),2), round(float(np.median(m)),2)) for p,m in mags.items()})
    for n,f in [('Ultimate1',0),('Ultimate1',300),('Ultimate1',432),('Ultimate1',496),('Ultimate2',93),('Ultimate2',101),('Ultimate2',109),('Collateral Ruin',48),('Collateral Ruin',60),('Collateral Ruin',77),('Stoic Bomb',150),('Stoic Bomb',216)]:
        w=D[n][f][1]
        print(n,f,'RA piv', decalage(w,'Right Arm'),'LA piv',decalage(w,'Left Arm'),'| poingD torse(dr,ht,av)',local_torse(w,G.bout(w,'Right Arm')),'hautD',local_torse(w,G.haut(w,'Right Arm')),'| poingG',local_torse(w,G.bout(w,'Left Arm')),'hautG',local_torse(w,G.haut(w,'Left Arm')))
