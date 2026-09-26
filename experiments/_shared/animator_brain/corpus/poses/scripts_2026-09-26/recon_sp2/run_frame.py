import sys, json, time, random
exec(open('fit.py').read())
CFG = {
 '03.73': dict(zone=(140,95,430,335), kp={'tete':(282,156),'mainG':(200,197),'piedG':(254,282)}, fov=False,
               base=dict(az=-140,el=30,dist=8.0,dx=-25,dy=30,hanche=2.2,pen=25,cote=0,LAaz=-60,LAel=25,RLaz=20,RLel=-40,LLaz=-30,LLel=-40,tl=-50,tt=5,cape=10,fov=70)),
}
def lance(T, cfg, starts_ra, nomfich, contraintes=None, extra_starts=None, n_az=(-165,-135,-105), n_pen=(15,45)):
    lab = masque_ref2(REFD + f'sp2/t_{T}.png')
    z = zone_box(cfg['zone'])
    L = [n for n in NOMS3 if n not in ('lac', 'roll') and (cfg['fov'] or n != 'fov')]
    res = []
    i = 0
    for az in n_az:
        for pen in n_pen:
            for ra in starts_ra:
                x0 = dict(cfg['base']); x0.update(az=az, pen=pen, RAaz=ra[0], RAel=ra[1], roll=0)
                if extra_starts: x0.update(extra_starts)
                x, s = optimise3(x0, lab, z, L, kp=cfg['kp'], graine=i, contraintes=contraintes); i += 1
                res.append((s, x))
    res.sort(key=lambda t: -t[0])
    json.dump(res, open(f'r/{nomfich}.json', 'w'))
    return res
