"""Chargeur local : comme corpus.load_rbxm_sequences mais garde le poids de
chaque Pose, pour pouvoir ignorer les Poses de poids 0 (conteneurs)."""
import sys
sys.path.insert(0, "/home/user/Jeux/experiments/_shared/animator_brain/outils")
import geo_pose as G  # noqa
import numpy as np
from animator_brain import corpus as C
R = C.R
P = '/root/.claude/uploads/4796ac9e-8e41-51f7-91c4-7b92a6a187d0/b64ecce0-tsb_anim.rbxm'


def load_w(path=P):
    _v, _nt, _ni, ch = R.read_chunks(path)
    cl = R.parse_inst_chunks(ch)
    props = {}
    for cls, pn, _dt, vals in R.parse_prop_chunks(ch, cl):
        props[(cls, pn)] = vals
    ext = R.parse_prop_extended(ch, cl, {("Pose", "CFrame"): "cframe"})
    cfr = ext[("Pose", "CFrame")]
    parent = R.parse_prnt_chunk(ch)
    seq_names = props[("KeyframeSequence", "Name")]
    kf_time = props[("Keyframe", "Time")]
    pose_name = props[("Pose", "Name")]
    pose_weight = props.get(("Pose", "Weight"), {})
    easing = props.get(("Pose", "EasingStyle"), {})

    def anc(ref, table):
        while ref in parent:
            ref = parent[ref]
            if ref in table:
                return ref
        return None
    seqs = {s: {} for s in seq_names}
    for kf, t in kf_time.items():
        s = anc(kf, seq_names)
        if s is not None:
            seqs[s][kf] = (t, {})
    for pr, nm in pose_name.items():
        kf = anc(pr, kf_time)
        s = anc(kf, seq_names) if kf is not None else None
        if s is None:
            continue
        pos, rot, _ = cfr[pr]
        seqs[s][kf][1][nm] = (np.array(rot, float).reshape(3, 3), np.array(pos, float),
                               float(pose_weight.get(pr, 1.0)), easing.get(pr))
    out = {}
    for s, kfs in seqs.items():
        out[seq_names[s]] = sorted(kfs.values(), key=lambda f: f[0])
    return out


def mondes(nom, fps=60, ignorer_poids_nul=True):
    raw = load_w()[nom]
    fr = []
    for t, poses in raw:
        d = {}
        for part, (r, p, w, e) in poses.items():
            if ignorer_poids_nul and w == 0.0:
                continue
            d[part] = (r, p)
        fr.append((t, d))
    return C.resample_linear(fr, fps)


if __name__ == "__main__":
    raw = load_w()
    for nom in ['M1', 'M2', 'M3', 'M4', 'WallComboPlayer']:
        print('==', nom)
        for t, poses in raw[nom][:30]:
            print(' ', round(t, 3), {k: (v[2], v[3]) for k, v in poses.items()})
