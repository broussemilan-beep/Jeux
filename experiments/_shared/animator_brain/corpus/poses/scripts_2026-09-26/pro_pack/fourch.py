import json
A={s["anim"]:s for s in json.load(open("analyse.json"))}
def norm(s,key):
    d=s[key]; k=s["bras"] if s["bras"]!="RA+LA" else "RA"; o="LA" if k=="RA" else "RA"
    m=-1 if k=="LA" else 1
    b=d["bras"][k]["torse"]; ob=d["bras"][o]["torse"]; p=d["poing"][k]; op=d["poing"][o]
    return {"lacet":m*d["buste"]["lacet"],"penche_avant":d["buste"]["penche_avant"],"penche_cote":m*d["buste"]["penche_cote"],
            "bras_torse":(m*b[0],b[1]),"autre_bras_torse":(m*ob[0],ob[1]),"poing":(p[0],m*p[1],p[2]),"autre_poing":(op[0],m*op[1],op[2]),
            "recul_epaule_frappeuse":m*d["epaules"]["recul_droite"],"hanche":d["hanche"],"tete_coup":(m*d["tete"]["coup"][0],d["tete"]["coup"][1]),"tete_torse":(m*d["tete"]["torse"][0],d["tete"]["torse"][1])}
out={}
for n in A:
    out[n]={"arme":norm(A[n],"desc_arme"),"contact":norm(A[n],"desc_contact")}
for n,v in out.items():
    print(n); print("  armé   ",v["arme"]); print("  contact",v["contact"])
json.dump(out,open("normalise_droitier.json","w"),indent=1)
