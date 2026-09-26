from kfit import *
nan = np.nan
FR = {
 'L9388': dict(W=2080, H=1170, pitch=13.4, A=45.0, obs=[
    (('Dface', 'Right Arm'), [424, 722, 624, 845], 1.0),
    (('Dface', 'Left Arm'), [1200, 1460, 645, 874], 1.0),
    (('box', 'Left Arm'), [nan, 1460, 642, 1005], 0.7),
    (('box', 'Right Arm'), [424, nan, 608, 850], 0.7),
    (('torso_top_left', None), [772, 580], 1.0),
    (('torso_bot_left', None), [785, 978], 1.0),
    (('torso_bottom', 1144), [944], 1.0)]),
 'L4.0': dict(W=960, H=540, pitch=14.2, A=33.5, obs=[
    (('Dface', 'Right Arm'), [206, 337, 270, 412], 2.17),
    (('Dface', 'Left Arm'), [550, 650, 254, 352], 2.17),
    (('box', 'Left Arm'), [nan, 650, 254, 409], 1.5),
    (('box', 'Right Arm'), [206, nan, 262, 412], 1.5),
    (('torso_top_left', None), [364, 244], 2.17),
    (('torso_bot_left', None), [362, 422], 2.17),
    (('torso_bottom', 509), [400], 2.17)]),
 'L4.4': dict(W=960, H=540, pitch=15.5, A=23.4, obs=[
    (('Dface', 'Right Arm'), [219, 337, 255, 386], 2.17),
    (('box', 'Left Arm'), [510, 598, 250, 352], 1.0),
    (('box', 'Right Arm'), [219, nan, 233, 386], 1.5),
    (('torso_top_left', None), [356, 227], 2.17),
    (('torso_bot_left', None), [359, 389], 2.17),
    (('torso_bottom', 505), [360], 1.0)]),
}
POSE = ['pav', 'pco', 'raz', 'rel', 'laz', 'lel']
CAMP = ['caz', 'cel', 'cd', 'cyo']
def unpack(x, frames):
    pose = dict(zip(POSE, x[:6])); cams = {}
    for i, k in enumerate(frames):
        cams[k] = dict(zip(CAMP, x[6 + 4 * i: 10 + 4 * i]))
    return pose, cams
def jres(x, frames, prior_w, extra=None):
    pose, cams = unpack(x, frames)
    res = []
    for k in frames:
        v = dict(pose); v.update(cams[k])
        spec = {'names': list(v.keys()), 'fixed': {'lacet': 0.0, 'hanche': 2.4, **(extra or {})}}
        fr = FR[k]
        res.extend(residuals(np.array(list(v.values())), spec, fr['obs'], fr['W'], fr['H'], fr['pitch']).tolist())
    # orbit prior: caz difference = -(A_k - A_ref)
    k0 = frames[0]
    for k in frames[1:]:
        pred = -(FR[k]['A'] - FR[k0]['A'])
        res.append(prior_w * ((cams[k]['caz'] - cams[k0]['caz']) - pred))
    return np.array(res)
def jlm(x0, frames, prior_w=3.0, it=300, extra=None):
    x = np.array(x0, float); lam = 1e-2
    f = lambda xx: jres(xx, frames, prior_w, extra)
    r = f(x); cost = r @ r
    for _ in range(it):
        J = np.zeros((len(r), len(x)))
        for i in range(len(x)):
            dx = np.zeros(len(x)); dx[i] = 1e-3 * max(1.0, abs(x[i]))
            J[:, i] = (f(x + dx) - r) / dx[i]
        A = J.T @ J; g = J.T @ r; ok = False
        for _ in range(12):
            step = np.linalg.solve(A + lam * np.diag(np.diag(A) + 1e-6), -g)
            rn = f(x + step); cn = rn @ rn
            if cn < cost:
                x, r, cost = x + step, rn, cn; lam = max(lam / 3, 1e-7); ok = True; break
            lam *= 4
        if not ok or np.abs(step).max() < 1e-4: break
    return x, cost, r
def show(x, frames, tag, extra=None):
    pose, cams = unpack(x, frames)
    for k in frames:
        v = dict(pose); v.update(cams[k]); v.update({'lacet': 0.0, 'hanche': 2.4, **(extra or {})})
        p = {'hanche': v['hanche'], 'buste': (v['lacet'], v['pav'], v['pco']), 'tete': (0, 15),
             'RA': (v['raz'], v['rel'], 0.0), 'LA': (v['laz'], v['lel'], 0.0), 'RL': ('pied', (1.0, 0, -0.6)), 'LL': ('pied', (-1.0, 0, 0.6))}
        w = G.pose(p)
        cam = cam3(w, v['caz'], v['cel'], v['cd'], FR[k]['pitch'], v['cyo'])
        G.cote_a_cote(REFS[k], [w], cam, sortie=OUT + f'{tag}_{k}.png', titre=f'{tag} {k}')
    return pose, cams
if __name__ == "__main__":
    frames = ['L9388', 'L4.0', 'L4.4']
    x9 = np.load('x9388.npy')   # caz cel cd cyo pav pco raz rel laz lel
    x0 = list(x9[4:10]) + [x9[0], x9[1], x9[2], x9[3], x9[0] + 11.5, x9[1], x9[2], x9[3], x9[0] + 21.6, x9[1], x9[2], x9[3]]
    for pw in (3.0, 0.0):
        x, cost, r = jlm(x0, frames, pw)
        pose, cams = unpack(x, frames)
        print('prior', pw, 'rms', round((cost / len(r)) ** 0.5, 2), {k: round(v, 1) for k, v in pose.items()})
        for k in frames: print('   ', k, {kk: round(vv, 2) for kk, vv in cams[k].items()})
        np.save(f'xjoint7_p{int(pw)}.npy', x)
        show(x, frames, f'r7_joint_p{int(pw)}')
