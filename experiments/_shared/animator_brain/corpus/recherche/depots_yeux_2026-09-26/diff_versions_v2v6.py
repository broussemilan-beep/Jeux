"""Ecart ENTRE deux versions, image par image, au cadrage reel (ce qu'AL ne fait pas :
il juxtapose, il ne mesure pas). Sortie : plages de temps ou la difference est visible."""
import cv2, numpy as np, sys
V = "/home/user/Jeux/captures/verification/2026-09-26-un-seul-coup-%s-scene-complete-avec-son.mp4"
def lire(v):
    cap = cv2.VideoCapture(V % v); out = []
    while True:
        ok, f = cap.read()
        if not ok: break
        out.append(cv2.cvtColor(cv2.resize(f, (213, 120), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY).astype(np.float32))
    return out
for a, b in [("v2", "v3"), ("v3", "v4"), ("v4", "v5"), ("v5", "v6")]:
    A, B = lire(a), lire(b)
    part = np.array([(np.abs(x - y) > 25).mean() for x, y in zip(A, B)])  # part de l'image qui change (vignette 213x120)
    vis = part > 0.02
    plages = []; s = None
    for i, x in enumerate(list(vis) + [False]):
        if x and s is None: s = i
        if not x and s is not None: plages.append((s, i - 1)); s = None
    print(f"{a}->{b}: images differentes (>2% de l'ecran) : {int(vis.sum())}/{len(part)} = {vis.sum()/30:.2f} s ; pic {part.max()*100:.0f}% a f{part.argmax()}")
    print("   plages (f, s):", [(p, round(p[0]/30, 2), round((p[1]-p[0]+1)/30, 2)) for p in plages if p[1]-p[0] >= 1][:12])
