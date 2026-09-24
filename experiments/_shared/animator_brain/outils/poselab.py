"""Labo de poses R6 : place les 6 blocs par rotations monde (articulations R6
standard), pieds au sol. Pour croquer des cles AVANT de les animer."""
import numpy as np
def Rx(a): a=np.radians(a); c,s=np.cos(a),np.sin(a); return np.array([[1,0,0],[0,c,-s],[0,s,c]])
def Ry(a): a=np.radians(a); c,s=np.cos(a),np.sin(a); return np.array([[c,0,s],[0,1,0],[-s,0,c]])
def Rz(a): a=np.radians(a); c,s=np.cos(a),np.sin(a); return np.array([[c,-s,0],[s,c,0],[0,0,1]])
def pose(torso, head, ra, la, rl, ll, ground=True):
    """Toutes les rotations en repere MONDE (perso regarde -Z, x = sa droite)."""
    T=np.zeros(3); w={'Torso':(torso,T)}
    piv=lambda off: T+torso@np.array(off,float)
    w['Head']=(head, piv((0,1,0))+head@np.array([0,0.5,0.0]))
    w['Right Arm']=(ra, piv((1,0.5,0))+ra@np.array([0.5,-0.5,0.0]))
    w['Left Arm']=(la, piv((-1,0.5,0))+la@np.array([-0.5,-0.5,0.0]))
    w['Right Leg']=(rl, piv((1,-1,0))+rl@np.array([-0.5,-1,0.0]))
    w['Left Leg']=(ll, piv((-1,-1,0))+ll@np.array([0.5,-1,0.0]))
    if ground:
        low=min((p+r@np.array([sx,sy,sz]))[1] for n,(r,p) in w.items() if 'Leg' in n for sx in(-.5,.5) for sy in(-1,1) for sz in(-.5,.5))
        w={k:(r,p-np.array([0,low,0])) for k,(r,p) in w.items()}
    return w
def aim(d, roll=0.0):
    """Rotation monde qui envoie l'axe -Y local (epaule -> main) sur d."""
    d=np.array(d,float); d/=np.linalg.norm(d); y=-d
    ref=np.array([0,0,-1.0]) if abs(y[2])<0.9 else np.array([1.0,0,0])
    x=np.cross(y,ref); x/=np.linalg.norm(x); z=np.cross(x,y)
    R=np.stack([x,y,z],axis=1)
    return R@Ry(roll)
