import numpy as np, glob
from vp_run2 import analyse
fs = sorted(glob.glob('fr640/f*.png'))
F = 300.0
rows = []
for i, p in enumerate(fs):
    t = 3.5 + i/30
    try:
        r = analyse(p, out=p.replace('fr640/', 'vpt_'))
    except Exception as e:
        print(round(t,3), 'fail', e); continue
    vps = [v for v in r['vp'] if v is not None]
    if len(vps) < 2:
        print(round(t,3), 'vps', vps); continue
    (x1,y1),(x2,y2) = vps
    # horizon through the two vps -> pitch
    sl = (y2-y1)/(x2-x1) if x2!=x1 else 0
    yc = y1 + sl*(320-x1)
    pitch = np.degrees(np.arctan((180-yc)/F))
    roll = np.degrees(np.arctan(sl))
    cp = np.cos(np.radians(pitch))
    a1 = np.degrees(np.arctan((x1-320)*cp/F)); a2 = np.degrees(np.arctan((x2-320)*cp/F))
    # canonical grid angle mod 90 in [0,90)
    g = [a % 90 for a in (a1, a2)]
    fest = r['f']
    rows.append((t, pitch, roll, a1, a2, fest))
    print(f"{t:.3f} pitch {pitch:5.1f} roll {roll:5.1f} axes {a1:6.1f} {a2:6.1f} sum|| {abs(a1-a2):5.1f} f {fest if fest is None else round(fest)}")
