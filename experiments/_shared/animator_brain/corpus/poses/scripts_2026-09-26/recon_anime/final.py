from lib import *
import json
F = {}
# --- finals (params before natural roll) ---
F["gon"] = dict(ref=D+"ref_gon.png", avant=(0,0,-1), cam=(172,10,14,25), cible=(0,1.45,0.5),
    p={'hanche':2.2,'buste':(-20,62,-25),'tete':(25,20),'RA':(160,-78),'LA':(45,0),'RL':('pied',(1.6,0,0.85)),'LL':('pied',(-1.6,0,0.85))})
F["saitama_dos"] = dict(ref=D+"ref_saitama_dos.png", avant=(0,0,-1), cam=(195,-27,3.4,85), cible=(0,2.1,0),
    p={'hanche':2.5,'buste':(15,10,-8),'tete':(35,30),'RA':(0,0),'LA':(25,10),'RL':('pied',(0.6,0,-1.0)),'LL':('pied',(-0.5,0,1.4))})
F["manga"] = dict(ref=D+"ref_manga.png", avant=(0,0,-1), cam=(-20,12,4.3,50), cible=(0.7,3.95,-0.6),
    p={'hanche':3.0,'buste':(0,15,0),'tete':(0,25),'RA':(-20,0),'LA':(-150,-60),'RL':('pied',(0.8,0,0.8)),'LL':('pied',(-0.8,0,-0.8))})
F["rouge"] = dict(ref=D+"ref_rouge.png", avant=(0,0,-1), cam=(-10,-10,2.3,65), cible=(0.0,4.1,-1.0),
    p={'hanche':3.0,'buste':(25,10,0),'tete':(-12.5,5),'RA':(25,0),'LA':(-160,-60),'RL':('pied',(0.8,0,-1.2)),'LL':('pied',(-0.8,0,1.0))})
out = {}
for k, f in F.items():
    q = nat(f["p"])
    w = G.pose(q)
    c = G.camera_orbite(f["cible"], *f["cam"], avant=f["avant"])
    G.cote_a_cote(f["ref"], [w], c, sortie=D+f"final_{k}.png", titre=f"final {k}")
    d = G.descripteurs(w, avant=f["avant"])
    out[k] = {"params": {kk: (list(v) if isinstance(v, tuple) else v) for kk, v in q.items()}, "cam": f["cam"], "cible": f["cible"], "descripteurs": d}
    print(k, G.resume(d)); print("   pieds", d["pieds"], "tete", d.get("tete"))
json.dump(out, open(D+"final_params_descripteurs.json","w"), indent=1, default=str)

# --- planche : v5 tenue (f240) vs Gon mesuré vs Gon transposé, 3 caméras ---
v5 = nat({'hanche':2.37,'buste':(-64,28,0),'tete':(0,0),'RA':(11,-6,340),'LA':(-117,-36,300),'RL':('pied',(1.2,0,0.6)),'LL':('pied',(-1.0,0,-1.0))})
gon = nat(F["gon"]["p"])
trans = nat({'hanche':2.45,'buste':(-35,35,-10),'tete':(20,10),'RA':(170,-75),'LA':(40,-10),'RL':('pied',(1.4,0,0.9)),'LL':('pied',(-1.3,0,-0.6))})
for nm, q in (("v5_f240", v5), ("gon_mesure", gon), ("gon_transpose", trans)):
    d = G.descripteurs(G.pose(q)); print(nm, G.resume(d))
ims = []
for nm, q in (("v5_f240", v5), ("gon_mesure", gon), ("gon_transpose", trans)):
    w = G.pose(q); row = []
    for az, el in ((180, 12), (90, 5), (35, 15)):
        c = G.camera_orbite((0, 1.9, 0), az, el, 11, 35)
        row.append(G.rendre([w], c, (360, 300), f"{nm} cam az{az}"))
    ims.append(row)
from PIL import Image as I
planche = I.new("RGB", (3*364, 3*304))
for i, row in enumerate(ims):
    for j, im in enumerate(row):
        planche.paste(im, (j*364, i*304))
planche.save(D+"planche_v5_vs_gon.png")
