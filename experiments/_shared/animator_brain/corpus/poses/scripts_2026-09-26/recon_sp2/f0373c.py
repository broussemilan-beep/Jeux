exec(open('run_frame.py').read())
import json
T='03.73'; cfg=CFG[T]
lab=masque_ref2(REFD+f'sp2/t_{T}.png'); z=zone_box(cfg['zone'])
def main_visible(x,w):
    eye,tgt,fov=camera(vers_cam3(x),(0,x['hanche'],0))
    d=G.bout(w,'Right Arm')-G.haut(w,'Right Arm'); d/=np.linalg.norm(d)
    v=eye-G.bout(w,'Right Arm'); v/=np.linalg.norm(v)
    ang=math.degrees(math.acos(np.clip(d@v,-1,1)))
    return 0.004*max(0,ang-75)
res=lance(T,cfg,[(-170,0),(160,20),(-140,10)],'f0373_mainvisible',contraintes=main_visible,n_az=(-150,-125),n_pen=(35,50))
for s,x in res[:4]: print('MAIN_VISIBLE',round(s,4),{k:round(v,1) for k,v in x.items() if k in ('az','el','dist','fov','pen','cote','RAaz','RAel','LAaz','LAel','RLaz','RLel','LLaz','LLel','cape','hanche','tl','tt')})
x=res[0][1]
print(montre3(x,T,'H3_mainvisible_top0',box=(120,60,480,340)))
print(geo_cote(x,T,'H3_mainvisible_top0'))
d=G.descripteurs(G.pose({k:v for k,v in vers_q(x).items() if k!='cape'}))
print(G.resume(d)); print(d['pieds'], d.get('tete'))
