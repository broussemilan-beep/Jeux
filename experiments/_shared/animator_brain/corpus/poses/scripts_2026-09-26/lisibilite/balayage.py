import sys, json, numpy as np
sys.path.insert(0, ".")
from charge import W, V, G, M
from mesure_cam import aires, lisibilite, cadrage, proj_fn
f=250; w=W[f]; g=W[173]
t=w["Torso"][1]
cible=t+np.array([0,-0.4,0])   # un peu sous le centre du torse : le corps entier
res=[]
for el in (-12,5,15,25,35):
    for az in range(-180,180,15):
        cam=G.camera_orbite(cible,az,el,9.0,40)
        a=aires(w,cam,(426,240)); L=lisibilite(w,g,cam,(426,240)); c=cadrage(w,cam,(426,240))
        # le devant du torse regarde-t-il la caméra ? (+1 face, -1 dos)
        Rt=w["Torso"][0]; avant_torse=Rt@np.array([0,0,-1.0]); vers_cam=(cam[0]-t)/np.linalg.norm(cam[0]-t)
        res.append(dict(az=az,el=el,ratio_brasD_sur_G=round(a["brasD_pct"]/max(a["brasG_pct"],0.05),2),brasD=a["brasD_pct"],brasG=a["brasG_pct"],
            epaule_ecran=L["deplacement_epaule_ecran_pct"],poing_ecran=L["deplacement_poing_ecran_pct"],axe_coup=L["axe_du_coup_visible"],
            ligne_ep=L["ligne_epaules_visible"],brasD_long=L["bras_D_visible_longueur"],torse_face=round(float(avant_torse@vers_cam),2)))
json.dump(res,open("balayage_v5_f250.json","w"),indent=0)
print("az el | brasD/G | poing_ecran% epaule_ecran% | axe_coup ligne_ep brasD_long | torse_face")
for r in res:
    if r["el"] in (-12,25):
        print(f'{r["az"]:5d} {r["el"]:3d} | {r["ratio_brasD_sur_G"]:5.2f} ({r["brasD"]:.1f}/{r["brasG"]:.1f}) | {r["poing_ecran"]:5.1f} {r["epaule_ecran"]:5.1f} | {r["axe_coup"]:.2f} {r["ligne_ep"]:.2f} {r["brasD_long"]:.2f} | {r["torse_face"]:+.2f}')
