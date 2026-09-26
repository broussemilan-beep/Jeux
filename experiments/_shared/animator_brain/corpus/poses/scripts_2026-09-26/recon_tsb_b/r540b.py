from h import *
base = {"hanche": 2.3, "buste": (0, 20, 0), "tete": (30, 10), "LA": (-95, -15),
        "RL": ("pied", (0.9, 0, 1.5)), "LL": ("pied", (-0.9, 0, -1.5))}
noms=[]
for k,(ra,cam,cib) in {"07a":((10,-28),(10,8,5.0,45),(0.6,1.8,0)),
                  "07b":((20,-25),(10,8,5.0,45),(0.6,1.8,0)),
                  "07c":((5,-35),(10,8,5.0,45),(0.6,1.8,0))}.items():
    p=dict(base); p["RA"]=ra
    essai("05.40","r540_"+k,p,cam,cible=np.array(cib)); noms.append("r540_"+k)
planche(noms,"r540_07_planche.png")
