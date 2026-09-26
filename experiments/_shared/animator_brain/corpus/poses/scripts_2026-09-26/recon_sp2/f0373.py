exec(open('run_frame.py').read())
T='03.73'; cfg=CFG[T]
import math
# H1 : bras droit libre (départs variés)
res=lance(T,cfg,[(-160,15),(160,40),(90,0),(30,-40)],'f0373_libre')
for s,x in res[:5]: print('LIBRE',round(s,4),{k:round(v,1) for k,v in x.items() if k in ('az','el','dist','pen','cote','RAaz','RAel','LAaz','LAel','cape','hanche')})
# H2 : bras droit contraint vers l'AVANT du torse (|az|<70)
def avant(x,w):
    a=((x['RAaz']+180)%360)-180
    return 0.01*max(0,abs(a)-70)
res2=lance(T,cfg,[(30,-30),(0,0),(45,20),(-30,-40)],'f0373_RAavant',contraintes=avant)
for s,x in res2[:3]: print('RA_AVANT',round(s,4),{k:round(v,1) for k,v in x.items() if k in ('az','el','dist','pen','cote','RAaz','RAel','LAaz','LAel','cape','hanche')})
montre3(res[0][1],T,'H1_libre_top0',box=(120,60,480,340))
montre3(res2[0][1],T,'H2_RAavant_top0',box=(120,60,480,340))
