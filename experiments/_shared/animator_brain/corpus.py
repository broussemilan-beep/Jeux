"""
Corpus du cerveau : lire de VRAIES animations Roblox (packs .rbxm/.rbxmx,
nos propres exports) et en tirer des mesures comparables, rangees par
categorie de technique (taxonomy.py).

Regle (PLAN.md, section 3) : aucun chiffre d'une source n'est copie dans un
prototype. Il passe par ici, devient une distribution par categorie, et
c'est la distribution qu'on consulte. Les fichiers sources ne sont pas
versionnes (licences) : seules les mesures derivees le sont.
"""
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, ".."))

import rbxm_reader as R  # noqa: E402
from . import roblox_export as X  # noqa: E402


def load_rbxm_sequences(path):
    """Toutes les KeyframeSequence d'un .rbxm binaire :
    [{"name", "loop", "priority", "frames": [(t, {part: (T_rot, T_pos)})]}]
    ou T = Pose.CFrame (transformation du Motor6D, repere du joint)."""
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

    def ancestor_in(ref, table):
        while ref in parent:
            ref = parent[ref]
            if ref in table:
                return ref
        return None

    seqs = {s: {"name": n, "loop": bool(props.get(("KeyframeSequence", "Loop"), {}).get(s, False)),
                "priority": props.get(("KeyframeSequence", "Priority"), {}).get(s), "kf": {}}
            for s, n in seq_names.items()}
    for kf, t in kf_time.items():
        s = ancestor_in(kf, seq_names)
        if s is not None:
            seqs[s]["kf"][kf] = (t, {})
    for pr, nm in pose_name.items():
        kf = ancestor_in(pr, kf_time)
        s = ancestor_in(kf, seq_names) if kf is not None else None
        if s is None:
            continue
        pos, rot, _rid = cfr[pr]
        seqs[s]["kf"][kf][1][nm] = (np.array(rot, float).reshape(3, 3), np.array(pos, float))
        seqs[s].setdefault("w", {}).setdefault(nm, []).append(float(pose_weight.get(pr, 1.0)))
    out = []
    for s in seqs.values():
        frames = sorted(s["kf"].values(), key=lambda f: f[0])
        zero = {nm: round(float(np.mean(np.array(ws) == 0.0)), 3) for nm, ws in s.get("w", {}).items()}
        out.append({"name": s["name"], "loop": s["loop"], "priority": s["priority"], "frames": frames,
                    "poids_nul_fraction": zero})
    out.sort(key=lambda d: d["name"])
    return out


def resolve_world(frames, root=(np.eye(3), np.array([0.0, 3.0, 0.0]))):
    """Poses -> CFrames monde par l'equation du moteur. Une part absente
    d'un keyframe est interpolee entre ses keyframes voisins (comme
    l'Animator) -- signale si ca arrive."""
    missing = sum(1 for _t, p in frames for part in X.PART_ORDER[1:] if part not in p)
    if missing:
        raise NotImplementedError(f"{missing} poses absentes : interpolation a implementer")
    return [(t, X.solve(p, root=root)) for t, p in frames]


def euler_xyz_deg(r):
    """Inverse de rig_math.euler_xyz_matrix (Rx @ Ry @ Rz, degres)."""
    b = np.arcsin(np.clip(r[0, 2], -1.0, 1.0))
    a = np.arctan2(-r[1, 2], r[2, 2])
    c = np.arctan2(-r[0, 1], r[0, 0])
    return tuple(np.degrees([a, b, c]))


def to_samples(world_frames):
    """CFrames monde -> format d'echantillons du cerveau
    (samples[part] = [(t, euler_local_deg, None, world_pos)]), pour que
    audit.audit() mesure une animation importee EXACTEMENT comme les notres."""
    samples = {p: [] for p in X.PART_ORDER}
    for t, w in world_frames:
        for p in X.PART_ORDER:
            par = X.PARENT.get(p)
            r = w[p][0] if par is None else w[par][0].T @ w[p][0]
            samples[p].append((t, euler_xyz_deg(r), None, w[p][1]))
    return samples


def brain_rig():
    from .rig_math import Rig
    return Rig(list(X.PART_ORDER), dict(X.PARENT), {k: tuple(v) for k, v in X.RIG["part_sizes"].items()},
               dict(X.RIG["joints"]))


# ---------------------------------------------------------------------
# Mesures de TIMING et d'AMPLITUDE (ce que l'audit de defauts ne mesure pas)

LIMBS = ("Torso", "Head", "Right Arm", "Left Arm", "Right Leg", "Left Leg")


def _smooth(x, k=3):
    if k <= 1:
        return x
    ker = np.ones(k) / k
    return np.convolve(np.pad(x, (k // 2, k // 2), mode="edge"), ker, mode="valid")


def timing_profile(world_frames, loop=False, ignore_parts=(), strike=False):
    """Mesures de timing/espacement/amplitude d'un clip, a partir des CFrames
    monde. Unites : secondes, degres, studs, frames a 60 fps (f60).
    ignore_parts : parts dont les Poses ont un poids nul (en jeu, c'est une
    AUTRE animation qui les mene, ex. jambes d'un M1 laissees a la course) --
    exclues de l'energie, des mouvements et des amplitudes.
    strike : l'action est le mouvement ou la main part le plus vite VERS
    L'AVANT -- l'armement peut etre plus violent que le coup lui-meme
    (mesure sur M1_3) et eloigne lui aussi la main du torse, mais vers
    l'arriere : ni la vitesse brute ni l'extension ne suffisent."""
    t = np.array([f[0] for f in world_frames])
    t = t - t[0]
    n = len(t)
    dt = float(np.median(np.diff(t))) if n > 1 else 1 / 60
    samples = to_samples(world_frames)
    from .rig_math import SampledClip
    clip = SampledClip(samples, brain_rig())
    limbs = [p for p in LIMBS if p not in ignore_parts]
    ang = {p: _smooth(clip.local_angular_speed(p)) for p in limbs}
    # Torso : sa rotation "locale" est relative au HumanoidRootPart, donc c'est
    # bien la rotation du corps entier ; on ajoute sa translation (root motion)
    torso_lin = _smooth(clip.linear_speed("Torso"))
    energy = sum(ang[p] for p in limbs)
    energy_raw = sum(clip.local_angular_speed(p) for p in limbs)
    pk = float(energy.max()) if n else 0.0
    out = {"duree_s": round(float(t[-1]), 3), "n_frames": n, "boucle": bool(loop),
           "parts_ignorees_poids_nul": list(ignore_parts)}
    if pk <= 1e-9:
        out["energie"] = "nulle"
        return out
    out["energie"] = {
        "pic_deg_s": round(pk, 1),
        "mediane_deg_s": round(float(np.median(energy)), 1),
        "contraste_pic_sur_mediane": round(pk / max(1e-9, float(np.median(energy))), 2),
        "fraction_quasi_tenue": round(float(np.mean(energy < 0.15 * pk)), 3),
        "fraction_rapide": round(float(np.mean(energy > 0.5 * pk)), 3),
    }
    # extremes (poses cles lues dans le mouvement) : minima locaux d'energie
    # nettement sous le pic
    e = energy
    mins = [i for i in range(1, n - 1) if e[i] <= e[i - 1] and e[i] < e[i + 1] and e[i] < 0.35 * pk]
    out["poses_cles_par_s"] = round(len(mins) / max(dt, t[-1]), 2)
    # MOUVEMENTS : segments separes par des quasi-arrets (energie < 20 % du
    # pic). Pour chacun : bornes, et l'ORDRE dans lequel les parts culminent
    # (qui mene le geste).
    # decoupage en VALLEES sur l'energie brute (le lissage efface une tenue
    # d'une frame) : un minimum local coupe s'il descend sous la moitie du
    # plus petit des deux pics qui l'encadrent.
    er = energy_raw
    cand = [i for i in range(1, n - 1) if er[i] <= er[i - 1] and er[i] < er[i + 1]]
    cut = [0]
    for j, i in enumerate(cand):
        nxt = cand[j + 1] if j + 1 < len(cand) else n - 1
        left, right = er[cut[-1]:i + 1].max(), er[i:nxt + 1].max()
        if er[i] < 0.5 * min(left, right) and min(left, right) > 0.15 * er.max():
            cut.append(i)
    cut.append(n - 1)
    cut = sorted(set(cut))
    hand_sp = {h: _smooth(np.linalg.norm(np.gradient(clip.tip(h), dt, axis=0), axis=1)) for h in ("Right Arm", "Left Arm")}
    hand = np.maximum(hand_sp["Right Arm"], hand_sp["Left Arm"])
    # vitesse de la main VERS L'AVANT du personnage (-Z du HumanoidRootPart) :
    # un armement eloigne aussi la main du torse, mais vers l'arriere. On ne
    # regarde que la main QUI FRAPPE (celle qui va le plus loin devant le
    # torse) : l'autre main peut elle aussi partir vers l'avant pendant
    # l'armement (bras de visee) et tromper la detection (vu sur notre M1).
    fwd = np.array([clip.world_rot["HumanoidRootPart"][i] @ np.array([0.0, 0.0, -1.0]) for i in range(n)])
    torso_p = clip.world_pos["Torso"]
    reach = {h: float(np.max(np.einsum("ij,ij->i", clip.tip(h) - torso_p, fwd))) for h in ("Right Arm", "Left Arm")}
    punch = max(reach, key=reach.get)
    ext = _smooth(np.einsum("ij,ij->i", np.gradient(clip.tip(punch), dt, axis=0), fwd))
    moves = []
    for a, b in zip(cut[:-1], cut[1:]):
        if b - a < 2:
            continue
        seg = slice(a, b + 1)
        epk = float(e[seg].max())
        if epk < 0.2 * pk:
            continue
        order = sorted(((float(t[a + int(np.argmax(ang[p][seg]))]), p) for p in limbs if ang[p][seg].max() > 0.2 * ang[p].max()))
        live = [i for i in range(a, b + 1) if er[i] > 0.15 * er[seg].max()]
        moves.append({"debut_f60": round(t[a] * 60, 1), "fin_f60": round(t[b] * 60, 1),
                      "fin_active_f60": round(t[live[-1]] * 60, 1) if live else round(t[b] * 60, 1),
                      "main_vers_avant_max_studs_s": round(float(max(0.0, ext[seg].max())), 1),
                      "pic_energie_rel": round(epk / pk, 2), "main_max_studs_s": round(float(hand[seg].max()), 1),
                      "ordre_des_pics": [(p, round((tp - t[a]) * 60, 1)) for tp, p in order]})
    out["mouvements"] = moves
    out["main_qui_frappe"] = punch
    if not loop and moves:
        # l'ACTION = le mouvement ou la main va le plus vite (le coup),
        # sinon celui de plus forte energie
        key = (lambda i: moves[i]["main_vers_avant_max_studs_s"]) if strike else (lambda i: moves[i]["pic_energie_rel"])
        k = max(range(len(moves)), key=key)
        act = moves[k]
        dur60 = t[-1] * 60
        end = act["fin_active_f60"]
        out["phases"] = {
            "anticipation_f60": act["debut_f60"],
            "action_f60": round(end - act["debut_f60"], 1),
            "recuperation_ou_tenue_f60": round(dur60 - end, 1),
            "fraction_anticipation": round(act["debut_f60"] / dur60, 3),
            "fraction_recuperation": round((dur60 - end) / dur60, 3),
            "qui_mene_l_action": [p for p, _f in act["ordre_des_pics"]],
        }
    out["membres"] = {}
    rest = np.eye(3)
    for p in limbs:
        lr = clip.local_rot[p]
        amp_rest = max(np.degrees(np.arccos(np.clip((np.trace(rest.T @ r) - 1) / 2, -1, 1))) for r in lr)
        amp_run = max(np.degrees(np.arccos(np.clip((np.trace(lr[0].T @ r) - 1) / 2, -1, 1))) for r in lr)
        out["membres"][p] = {"vitesse_max_deg_s": round(float(ang[p].max()), 1),
                             "pic_a_s": round(float(t[int(np.argmax(ang[p]))]), 3),
                             "amplitude_vs_repos_deg": round(float(amp_rest), 1),
                             "amplitude_vs_debut_deg": round(float(amp_run), 1)}
    out["mains_vitesse_max_studs_s"] = {h: round(float(v.max()), 1) for h, v in hand_sp.items()}
    # translation des Motor6D (hors RootJoint) : les pros DECALENT les membres
    # (faux coude du rig IK) -- la tete, jamais (mesure du pack, 2026-09-24)
    out["translation_articulation_max_studs"] = {
        p: round(max(float(np.linalg.norm(X.joint_transform(p, w)[1])) for _t, w in world_frames), 3)
        for p in limbs if p != "Torso"}
    tp = clip.world_pos["Torso"]
    out["deplacement_torse_studs"] = {"x": round(float(np.ptp(tp[:, 0])), 2), "y": round(float(np.ptp(tp[:, 1])), 2),
                                     "z": round(float(np.ptp(tp[:, 2])), 2)}
    out["torse_vitesse_max_studs_s"] = round(float(torso_lin.max()), 1)
    # Ajout du 2026-09-24 (retour de Milan sur le Poing du Dragon : « il est
    # accroupi ») : hauteur ABSOLUE du torse sous la position debout (centre
    # du torse a y = 3 au repos). deplacement_torse_studs ne mesure que la
    # VARIATION pendant le clip : un perso accroupi des la frame 0 y passait.
    sag = np.maximum(0.0, 3.0 - tp[:, 1])
    out["affaissement_torse_studs"] = {"max": round(float(sag.max()), 3), "median": round(float(np.median(sag)), 3)}
    # Ajout du 2026-09-24 (retour de Milan sur la v2 : « les bras sont trop
    # hauts, il n'est pas en transfert de poids »). Decalage VERTICAL des
    # epaules (translation du Motor6D, axe haut du torse) : les pros baissent
    # l'epaule (jusqu'a -1,3 stud sur les M1), jamais ne la montent (max
    # +0,04) ; un haussement d'epaule se lit comme des bras trop hauts.
    sh_y = [float(X.joint_transform(a, w)[1][1]) for _t, w in world_frames for a in ("Right Arm", "Left Arm")
            if a in limbs]
    if sh_y:
        out["decalage_epaule_vertical_studs"] = {"haut_max": round(max(sh_y), 3), "bas_max": round(min(sh_y), 3),
                                                 "median": round(float(np.median(sh_y)), 3)}
    if strike:
        out["mecanique_frappe"] = strike_mechanics(clip, punch, fwd)
    return out


def strike_mechanics(clip, hand, fwd):
    """Mecanique du corps au contact (frame ou la main qui frappe est le plus
    loin devant le torse) :
    - bras_elevation_deg : angle epaule->poing au-dessus (+) / sous (-) de
      l'horizontale ;
    - portee_studs : poing devant le torse ;
    - transfert_poids_studs : de combien le torse avance PAR RAPPORT AUX
      PIEDS entre la position la plus reculee (armement) et le contact. Si le
      pied avance avec le torse, le transfert reste nul : c'est le torse qui
      doit passer au-dessus du pied avant."""
    torso = clip.world_pos["Torso"]
    tipp = clip.tip(hand)
    reach = np.einsum("ij,ij->i", tipp - torso, fwd)
    i = int(np.argmax(reach))
    center = clip.world_pos[hand][i]
    d = tipp[i] - center
    elev = float(np.degrees(np.arctan2(d[1], np.hypot(d[0], d[2]))))
    feet = (clip.tip("Right Leg") + clip.tip("Left Leg")) / 2
    rel = np.einsum("ij,ij->i", torso - feet, fwd)     # + = torse devant les pieds
    # Ajout du 2026-09-24 (retour de Milan sur la v3b : « les coups partent du
    # bas ») : trajectoire du poing sur les 0,1 s qui precedent le contact,
    # en hauteur relative au pivot d'epaule du contact. Un direct arme haut et
    # voyage A PLAT ; un uppercut monte.
    sx = 1.0 if hand == "Right Arm" else -1.0
    pivot_y = float((torso[i] + clip.world_rot["Torso"][i] @ np.array([sx, 0.5, 0.0]))[1])
    n = max(2, int(round(0.1 / clip.dt)))
    h = tipp[max(0, i - n): i + 1, 1] - pivot_y
    return {"bras_elevation_deg": round(elev, 1), "portee_studs": round(float(reach[i]), 2),
            "transfert_poids_studs": round(float(rel[i] - rel[: i + 1].min()), 2),
            "poing_hauteur_studs": round(float(tipp[i][1]), 2),
            "poing_montee_finale_studs": round(float(h[-1] - h.min()), 2),
            "poing_hauteur_aller_vs_epaule": round(float(h.mean()), 2)}


def ignored_by_weight(seq, frac=0.9):
    return tuple(p for p, z in seq.get("poids_nul_fraction", {}).items() if z >= frac and p in LIMBS)


def measure(world_frames, loop=False, ignore_parts=(), strike=False):
    """Fiche complete : timing + audit du cerveau (memes fonctions que pour
    nos propres animations)."""
    from . import audit as A
    rep, _clip, _sig = A.audit(to_samples(world_frames), brain_rig())
    return {"timing": timing_profile(world_frames, loop, ignore_parts, strike),
            "audit": {r["metric"]: r["value"] for r in rep["verdict"]},
            "audit_ok": rep["score"]}
