import sys; sys.path.insert(0, ".")
import numpy as np, json, cv2
import bras_grille as B
import fit as F
teapot = [(345, 120), (570, 120), (570, 290), (470, 300), (400, 290), (345, 235)]
ciel = [(0, 0), (960, 0), (960, 200), (0, 200)]
m, care = F.prep_masque("04.60", [ciel, teapot], [teapot])
zone = np.zeros_like(care); zone[100:185, 90:180] = True   # zone du bras droit (demi-échelle): x 180-360, y 200-370
zone &= care
res = {}
for bras, tip, bb, z in (("RA", (249, 291), (198, 240, 300, 342), zone), ("LA", (555, 338), (521, 299, 589, 376), None)):
    azs, els, C = B.carte("fit_460T1.json", bras, np.array(tip), np.array(bb), zone=z, masque=m if z is not None else None,
                          w_iou=6000 if z is not None else 0)
    a, e = B.dessin(azs, els, C, f"carte_{bras}_460.png", f"4.6 s {bras} : coût de la direction du bras")
    np.save(f"carte_{bras}_460.npy", C)
    # minima locaux distincts
    flat = [(C[i, j], azs[j], els[i]) for i in range(len(els)) for j in range(len(azs))]
    flat.sort()
    picks = []
    for c, az, el in flat:
        if all(abs(((az - pa + 180) % 360) - 180) > 30 or abs(el - pe) > 25 for _, pa, pe in picks):
            picks.append((c, az, el))
        if len(picks) >= 4: break
    print(bras, "meilleur", a, e, "| minima distincts:", [(round(c), az, el) for c, az, el in picks])
    res[bras] = [(float(c), float(az), float(el)) for c, az, el in picks]
json.dump(res, open("minima_460.json", "w"))
