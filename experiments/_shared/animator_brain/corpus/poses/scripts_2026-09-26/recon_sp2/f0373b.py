exec(open('run_frame.py').read())
import json
T='03.73'; cfg=CFG[T]
lab=masque_ref2(REFD+f'sp2/t_{T}.png'); z=zone_box(cfg['zone'])
res=json.load(open('r/f0373_libre.json'))
# pour les 6 meilleurs : direction caméra dans les axes du torse, et score si RA pointe exactement vers la caméra / exactement à l'opposé
for s,x in res[:6]:
    q=vers_q(x); w=G.pose({k:v for k,v in q.items() if k!='cape'})
    eye,tgt,fov=camera(vers_cam3(x),(0,x['hanche'],0))
    Rt,pt=w['Torso']; sh=pt+Rt@np.array([1.5,0.5,0])
    v=eye-sh; v/=np.linalg.norm(v)
    azc,elc=G._dir_az_el(Rt.T@v,np.array([0,0,-1.0]),np.array([1.0,0,0]))
    y=dict(x); y['RAaz'],y['RAel']=azc,elc; s1=evalue3(y,lab,z,cfg['kp'])
    y2=dict(x); y2['RAaz'],y2['RAel']=((azc+360)%360)-180,-elc; s2=evalue3(y2,lab,z,cfg['kp'])
    print(round(s,4),'RA',round(x['RAaz']),round(x['RAel']),'| cam dans axes torse',azc,elc,'| RA->cam',round(s1,4),'| RA<-cam',round(s2,4))
