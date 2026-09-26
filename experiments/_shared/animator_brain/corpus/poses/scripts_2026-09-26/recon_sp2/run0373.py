exec(open('fit.py').read())
import json, time
lab=masque_ref(REFD+'sp2/t_03.73.png',sombre=45)
z=zone_box((140,95,430,335))
L=[n for n in NOMS if n not in ('lac','roll')]
res=[]
t0=time.time()
starts=[]
for az in (-160,-130,-100):
  for pen in (20,50):
    for ra in ((-140,10),(160,40),(40,-40)):
      starts.append({'az':az,'el':30,'dist':7.0,'dx':-30,'dy':30,'roll':0,'hanche':2.0,'pen':pen,'cote':0,'RAaz':ra[0],'RAel':ra[1],'LAaz':-60,'LAel':5,'RLaz':20,'RLel':-60,'LLaz':-40,'LLel':-60,'tl':-60,'tt':10,'cape':15,'cy':2.0})
for i,x0 in enumerate(starts):
    x,s=optimise(x0,lab,z,L,tours=12,graine=i)
    res.append((s,x,x0))
res.sort(key=lambda t:-t[0])
print('temps',time.time()-t0)
for s,x,x0 in res[:6]:
    print(round(s,4),{k:round(v,1) for k,v in x.items()})
json.dump([(s,x) for s,x,_ in res],open('r/fit0373.json','w'))
for i in range(3):
    montre(res[i][1],'03.73',f'fit_top{i}',box=(120,60,480,340))
