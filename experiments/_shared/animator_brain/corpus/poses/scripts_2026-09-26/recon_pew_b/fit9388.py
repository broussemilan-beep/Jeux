from kfit import *
nan = np.nan
OBS = [(('Dface', 'Right Arm'), [424, 722, 624, 845], 1.0),
       (('Dface', 'Left Arm'), [1200, 1460, 645, 874], 1.0),
       (('box', 'Left Arm'), [nan, 1460, 642, 1005], 0.7),
       (('box', 'Right Arm'), [424, nan, 608, 850], 0.7),
       (('torso_left', None), [775, 580, 978], 1.0),
       (('head', None), [1011, 617], 0.3)]
spec = {'names': ['caz', 'cel', 'cd', 'cyo', 'pav', 'pco', 'raz', 'rel', 'laz', 'lel'], 'fixed': {'lacet': 0.0, 'hanche': 2.4}}
best = None
for caz0 in (-30, 0, 30, 60):
    for lel0 in (-20, 30):
        x0 = [caz0, 20, 5.5, 3, 15, 0, caz0 * 0.5, 10, caz0 * 0.5, lel0]
        x, cost, r = lm(x0, spec, OBS, 2080, 1170, 13.4)
        print(caz0, lel0, round(cost ** 0.5 / len(r) ** 0.5, 1), np.round(x, 1))
        if best is None or cost < best[1]:
            best = (x, cost)
x = best[0]
np.save('x9388.npy', x)
p, v = build(x, spec)
w = G.pose(p)
cam = cam3(w, v['caz'], v['cel'], v['cd'], 13.4, v['cyo'])
G.cote_a_cote(REFS['L9388'], [w], cam, sortie=OUT + 'r5_9388_lm.png', titre='r5 LM')
print(p, v)
print(G.resume(G.descripteurs(w)))
