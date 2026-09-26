exec(open('run_frame.py').read())
import json
LAB["Cap"]=3
T='04.20'
lab=masque_ref2(REFD+f'sp2/t_{T}.png'); ZB=(160,40,480,345); z=zone_box(ZB)
kp={'tete':(318,118)}
x0=json.load(open('r/fit_0420_cont.json'))[0][1]
out=[]
for la in [(-87,55),(-60,0),(-40,-30),(-20,-60),(-70,-30),(0,-40),(-100,-20)]:
    x=dict(x0); x['LAaz'],x['LAel']=la
    x2,s2=optimise3(x,lab,z,['az','el','dist','dx','dy','LAaz','LAel','pen','cote','RLaz','RLel','LLaz','LLel','RAaz','RAel'],kp=kp,graine=1,echelle=0.4)
    out.append((s2,x2,la))
    print(la,'->',round(s2,4),{k:round(v,1) for k,v in x2.items() if k in ('az','el','dist','pen','cote','RAaz','RAel','LAaz','LAel','RLaz','RLel','LLaz','LLel')})
out.sort(key=lambda t:-t[0])
json.dump([(a,b) for a,b,_ in out],open('r/fit_0420_LA.json','w'))
print(montre3(out[0][1],T,'LA_top0'))
