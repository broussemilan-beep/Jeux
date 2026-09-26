import json
import numpy as np
import charge as K, geo_pose as G
from PIL import Image
R = {r['id']: r for r in json.load(open('frappes_tsb.json'))}
v5 = G.mondes_rbxmx('/home/user/Jeux/experiments/r6_un_seul_coup/output/usc_attaquant.rbxmx')
r = R['M2']; m2 = K.mondes('M2'); av2 = tuple(r['avant_vecteur'])
lignes = [('TSB M2 ARME f0', m2[0][1], av2), ('TSB M2 DEPART f7', m2[7][1], av2), ('TSB M2 CONTACT f10', m2[10][1], av2),
          ('v5 TENUE f240', v5[240], (0, 0, -1)), ('v5 DEPART f270', v5[270], (0, 0, -1)), ('v5 CONTACT f283', v5[283], (0, 0, -1))]
CAMS = [(0, 5, 'face'), (90, 5, 'sa droite'), (45, 30, '45/30'), (180, 10, 'dos')]
tw = th = 260
im = Image.new('RGB', (tw * 4, th * len(lignes)), (0, 0, 0))
for i, (nm, w, av) in enumerate(lignes):
    c = w['Torso'][1].copy(); c[1] = 2.2
    for k, (az, el, cn) in enumerate(CAMS):
        cam = G.camera_orbite(c, az, el, 8.5, 50, avant=av)
        im.paste(G.rendre(w, cam, (tw, th), f'{nm} {cn}'), (k * tw, i * th))
im.save('compare_TSB_M2_vs_v5.png'); print(im.size)
