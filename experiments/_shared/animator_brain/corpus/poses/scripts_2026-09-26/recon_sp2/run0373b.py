exec(open('fit.py').read())
import json, time
T='03.73'
lab=masque_ref2(REFD+f'sp2/t_{T}.png')
ZB=(140,95,430,335); z=zone_box(ZB)
kp={'tete':(281,152),'mainG':(200,197),'piedG':(254,282)}
L=[n for n in NOMS if n not in ('lac','roll')]
res=[]; t0=time.time()
starts=[]
for az in (-165,-135,-105):
  for pen in (15,45,70):
    for ra in ((-140,10),(160,40),(40,-40)):
      starts.append({'az':az,'el':30,'dist':7.0,'dx':-30,'dy':30,'roll':0,'hanche':2.0,'pen':pen,'cote':0,'RAaz':ra[0],'RAel':ra[1],'LAaz':-60,'LAel':5,'RLaz':20,'RLel':-60,'LLaz':-40,'LLel':-60,'tl':-40,'tt':10,'cape':15,'cy':2.0})
for i,x0 in enumerate(starts):
    x,s=optimise2(x0,lab,z,L,kp=kp,graine=i)
    res.append((s,x))
res.sort(key=lambda t:-t[0])
print('temps',round(time.time()-t0))
for s,x in res[:8]:
    print(round(s,4),{k:round(v,1) for k,v in x.items() if k not in ('cy','roll')})
json.dump(res,open(f'r/fit{T}b.json','w'))
for i in range(3):
    montre(res[i][1],T,f'fitb_top{i}',box=(120,60,480,340))
debug(res[0][1],T,'fitb_top0',ZB)
