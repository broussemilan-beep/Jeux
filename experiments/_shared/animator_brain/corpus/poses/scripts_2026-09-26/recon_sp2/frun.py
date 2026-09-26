import sys, json
exec(open('run_frame.py').read())
T = sys.argv[1]
B = dict(az=-120, el=25, dist=4.5, dx=0, dy=0, hanche=2.2, pen=40, cote=0, LAaz=-60, LAel=40, RLaz=20, RLel=-40, LLaz=-20, LLel=-30, tl=0, tt=0, cape=5, fov=70)
C = {
 '04.20': dict(zone=(160,40,480,345), kp={'tete':(318,118)}, fov=False, base=dict(B, dist=4.5),
               ras=[(-160,5),(150,30),(90,10),(40,-30)], azs=(-150,-120,-90), pens=(20,45)),
 '04.53': dict(zone=(230,0,640,330), kp={'tete':(360,70)}, fov=True, base=dict(B, dist=3.5, el=35, pen=45),
               ras=[(-160,5),(150,30),(90,0),(30,-20),(0,0)], azs=(-90,-45,0), pens=(20,50)),
 '04.60': dict(zone=(260,0,640,330), kp={'tete':(405,80)}, fov=True, base=dict(B, dist=3.2, el=35, pen=45),
               ras=[(-160,5),(150,30),(90,0),(30,-20),(0,0)], azs=(-60,-20,20), pens=(20,50)),
 '04.80': dict(zone=(60,0,640,360), kp={'tete':(395,15),'mainD':(215,135)}, fov=True, base=dict(B, dist=3.0, el=5, pen=20),
               ras=[(0,0),(-30,-10),(30,10),(60,0)], azs=(-40,0,40), pens=(0,30)),
}
cfg = C[T]
res = lance(T, cfg, cfg['ras'], 'fit_' + T.replace('.', ''), n_az=cfg['azs'], n_pen=cfg['pens'])
for s, x in res[:6]:
    print(T, round(s, 4), {k: round(v, 1) for k, v in x.items() if k in ('az','el','dist','fov','dx','dy','hanche','pen','cote','RAaz','RAel','LAaz','LAel','RLaz','RLel','LLaz','LLel','tl','tt','cape')})
for i in range(3):
    montre3(res[i][1], T, f'fit_top{i}')
