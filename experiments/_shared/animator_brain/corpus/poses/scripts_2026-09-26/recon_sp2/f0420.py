exec(open('run_frame.py').read())
import json
LAB["Cap"]=3
T='04.20'
lab=masque_ref2(REFD+f'sp2/t_{T}.png'); ZB=(160,40,480,345); z=zone_box(ZB)
kp={'tete':(318,118)}
x373=json.load(open('r/f0373_mainvisible.json'))[0][1]
res=[]
i=0
for az in (-125,-110,-95,-80):
    for dist in (4.0,5.0):
        x0=dict(x373); x0.update(az=az,dist=dist,dx=0,dy=0)
        # 1) caméra seule
        x,s=optimise3(x0,lab,z,['az','el','dist','dx','dy'],kp=kp,graine=i); i+=1
        # 2) pose libre ensuite, petits pas
        x2,s2=optimise3(x,lab,z,[n for n in NOMS3 if n not in ('lac','roll','fov')],kp=kp,graine=i,echelle=0.5); i+=1
        res.append((s2,x2,s,x))
res.sort(key=lambda t:-t[0])
for s2,x2,s,x in res[:5]:
    print(round(s,4),'->',round(s2,4),{k:round(v,1) for k,v in x2.items() if k in ('az','el','dist','dx','dy','hanche','pen','cote','RAaz','RAel','LAaz','LAel','RLaz','RLel','LLaz','LLel','tl','tt')})
json.dump([(a,b) for a,b,_,_ in res],open('r/fit_0420_cont.json','w'))
print(montre3(res[0][1],T,'cont_top0'))
print(montre3(res[0][3],T,'cont_top0_poseFigee'))
