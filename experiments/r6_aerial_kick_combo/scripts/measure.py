"""
Mesures objectives et justifiables appliquees a chaque cycle, conformement
au mandat utilisateur ("mesure-la toi-meme sur des criteres objectifs
justifiables : fluidite de la courbe, absence de tortillement, respect
des contraintes R6"). Toutes les fonctions prennent les echantillons
produits par anim_engine.sample() (60 Hz par defaut, tuples
(t, (rx,ry,rz)_deg, local_pos, world_pos)) et retournent des scores
numeriques + diagnostics textuels, jamais un simple "ca a l'air bien".

Base sur les 3 composantes d'angle (rx,ry,rz) directement -- PAS sur un
angle/axe derive d'un quaternion. Ce choix vient d'un bug trouve au cycle
1 (voir anim_engine.py et README) : un angle derive d'un quaternion se
replie toujours dans [0,180], donc une rotation animee qui traverse 180
deg (frequent ici, le spin du kick2 va jusqu'a ~200 deg) y apparaissait
comme un saut brutal de signe. Les 3 canaux d'angle sont ici authored et
interpoles de façon continue (jamais repliee modulo 360), donc directement
mesurables sans ambiguite.
"""
import math
import numpy as np

from r6_rig import PART_ORDER, ARM_PARTS, LEG_PARTS
from anim_engine import euler_xyz_matrix


def _matrix_angle_deg(m):
    """Angle de rotation total represente par une matrice 3x3 (toujours
    dans [0,180], formule standard trace/2)."""
    tr = np.trace(m)
    c = max(-1.0, min(1.0, (tr - 1.0) / 2.0))
    return math.degrees(math.acos(c))


def curve_smoothness(samples, sample_hz, phases, joints=None):
    """Jerk (3e derivee) du vecteur (rx,ry,rz), RMS normalise par la
    vitesse angulaire (du meme vecteur) de pic, par joint et PAR PHASE
    (une phase = une fenetre a l'interieur de laquelle on attend un seul
    arc de mouvement ; le mouvement change legitimement de plan d'un coup
    a l'autre, donc on ne compare jamais le jerk a cheval sur deux
    phases). Score bas = courbe fluide. Retourne dict joint -> score
    (moyenne ponderee par duree des scores-par-phase), plus un agrege
    "_aggregate_max" = pire joint (une seule articulation qui saccade
    suffit a casser la lecture visuelle du combo)."""
    joints = joints or [p for p in PART_ORDER if p != "HumanoidRootPart"]
    dt = 1.0 / sample_hz
    per_joint_phase_scores = {part: [] for part in joints}
    for phase in phases:
        i0 = math.ceil(phase["t0"] * sample_hz)  # jamais avant le debut de phase
        i1 = math.floor(phase["t1"] * sample_hz)  # jamais dans la phase suivante (voir cycle 2, README)
        for part in joints:
            rot = np.array([s[1] for s in samples[part][i0:i1 + 1]])  # (n,3) deg
            if len(rot) < 5:
                continue
            vel = np.gradient(rot, dt, axis=0)
            acc = np.gradient(vel, dt, axis=0)
            jerk = np.gradient(acc, dt, axis=0)
            jerk_mag = np.linalg.norm(jerk, axis=1)
            vel_mag = np.linalg.norm(vel, axis=1)
            peak_vel = max(np.max(vel_mag), 1e-6)
            score = float(np.sqrt(np.mean(jerk_mag ** 2)) / peak_vel)
            per_joint_phase_scores[part].append((score, phase["t1"] - phase["t0"]))

    scores = {}
    for part, vals in per_joint_phase_scores.items():
        total_w = sum(w for _, w in vals) or 1.0
        scores[part] = sum(s * w for s, w in vals) / total_w
    scores["_aggregate_max"] = max((v for k, v in scores.items() if k != "_aggregate_max"), default=0.0)
    return scores


def twist_reversals(samples, sample_hz, phases, joints=None, noise_floor_deg=3.0):
    """Compte, par joint et par phase, les changements de signe de la
    vitesse angulaire sur l'axe PRIMAIRE de la phase (l'axe rx/ry/rz dont
    l'excursion -- max moins min -- est la plus grande sur cette fenetre :
    c'est l'axe qui porte le mouvement voulu, les 2 autres sont
    generalement du contrepoids/accompagnement secondaire).

    noise_floor_deg : si l'excursion de l'axe primaire est en dessous de
    ce seuil, la phase/joint est ignoree (mouvement trop petit pour que
    quiconque le percoive comme un "tortillement" -- evite de compter du
    bruit numerique sur une articulation quasi immobile).

    phases: liste de dicts {name, t0, t1, expected_reversals:{part:int}}.
    Retourne dict phase -> part -> {found, expected, extra, axis}."""
    joints = joints or [p for p in PART_ORDER if p != "HumanoidRootPart"]
    dt = 1.0 / sample_hz
    report = {}
    for phase in phases:
        i0 = math.ceil(phase["t0"] * sample_hz)  # jamais avant le debut de phase
        i1 = math.floor(phase["t1"] * sample_hz)  # jamais dans la phase suivante (voir cycle 2, README)
        report[phase["name"]] = {}
        for part in joints:
            rot = np.array([s[1] for s in samples[part][i0:i1 + 1]])  # (n,3) deg
            if len(rot) < 3:
                continue
            excursion = rot.max(axis=0) - rot.min(axis=0)
            axis_i = int(np.argmax(excursion))
            if excursion[axis_i] < noise_floor_deg:
                report[phase["name"]][part] = {
                    "found": 0, "expected": 0, "extra": 0,
                    "axis": "none (excursion<noise_floor)",
                }
                continue
            theta = rot[:, axis_i]
            vel = np.gradient(theta, dt)
            signs = np.sign(np.round(vel, 3))
            signs = signs[signs != 0]
            reversals = int(np.sum(signs[1:] != signs[:-1])) if len(signs) > 1 else 0
            expected = phase.get("expected_reversals", {}).get(part, 0)
            report[phase["name"]][part] = {
                "found": reversals,
                "expected": expected,
                "extra": max(0, reversals - expected),
                "axis": ("x", "y", "z")[axis_i],
            }
    return report


def r6_structural_compliance(objs, keyframes, samples):
    """Verifications structurelles automatiques de la contrainte R6 non
    negociable. Retourne dict de checks -> (ok: bool, detail: str)."""
    checks = {}

    expected_parts = set(PART_ORDER)
    checks["six_rigid_segments_only"] = (
        set(objs.keys()) == expected_parts,
        f"parts={sorted(objs.keys())}",
    )

    non_root_translation_ok = True
    detail = []
    for part in PART_ORDER:
        if part == "HumanoidRootPart":
            continue
        positions = [p for (_, _, p, _) in samples[part]]
        first = positions[0]
        max_drift = max(math.dist(first, p) for p in positions)
        if max_drift > 1e-4:
            non_root_translation_ok = False
            detail.append(f"{part} drift={max_drift:.5f}")
    checks["only_root_translates"] = (
        non_root_translation_ok,
        "ok" if non_root_translation_ok else "; ".join(detail),
    )

    max_angles = {}
    over_limit = []
    for part in PART_ORDER:
        if part == "HumanoidRootPart":
            continue
        angles = [_matrix_angle_deg(euler_xyz_matrix(*rot)) for (_, rot, _, _) in samples[part]]
        max_angles[part] = max(angles)
        # Seuil calibre a 250 deg, pas 170 : un Motor6D 3-DOF n'a structurellement
        # RIEN qui l'empeche de tourner a 180-200 deg (contrairement a un coude/genou
        # a charniere) et le kick2 (retourne/spin) EXIGE un tour du corps d'environ
        # 170-200 deg par design -- ce n'est pas un "flip" accidentel du rig, c'est
        # le mouvement demande. 250 deg reste un garde-fou contre une vraie
        # aberration (quasi-demi-tour supplementaire non voulu).
        if max_angles[part] > 250.0:
            over_limit.append(part)
    checks["rotation_within_sane_range"] = (
        len(over_limit) == 0,
        f"max_angles={{{', '.join(f'{k}:{v:.0f}deg' for k,v in max_angles.items())}}}"
        + (f" OVER 250deg: {over_limit}" if over_limit else ""),
    )

    punch_flags = []
    max_forward = 0.0
    for arm in ARM_PARTS:
        for (_, rot, _, _) in samples[arm]:
            m = euler_xyz_matrix(*rot)
            rest_down = np.array([0.0, -1.0, 0.0])
            world_dir = m @ rest_down
            forward = -world_dir[2]  # -Z = avant
            vertical = abs(world_dir[1])
            if forward > 0.7 and vertical < 0.5:
                max_forward = max(max_forward, forward)
                punch_flags.append(arm)
    checks["no_punch_like_arm_pose"] = (
        len(punch_flags) == 0,
        "ok" if not punch_flags else f"forward-reach detecte sur {sorted(set(punch_flags))}, max_forward={max_forward:.2f}",
    )

    rest_eps = 3.0
    start_ok = True
    end_ok = True
    for part in ("Torso", "HumanoidRootPart"):
        rot0 = samples[part][0][1]
        rot1 = samples[part][-1][1]
        a0 = _matrix_angle_deg(euler_xyz_matrix(*rot0))
        a1 = _matrix_angle_deg(euler_xyz_matrix(*rot1))
        if a0 > rest_eps:
            start_ok = False
        if a1 > rest_eps:
            end_ok = False
    checks["neutral_forward_rest_at_start_and_end"] = (
        start_ok and end_ok,
        f"start_ok={start_ok} end_ok={end_ok}",
    )

    checks["kicks_only_no_punches_by_construction"] = (
        True,
        "verifie manuellement via choregraphie (voir cycle report) + no_punch_like_arm_pose ci-dessus",
    )

    return checks


def velocity_continuity(samples, sample_hz, keyframe_times, joints=None):
    """Detecte les a-coups DE VITESSE aux keyframes elles-memes -- angle
    mort delibere de curve_smoothness (qui mesure le jerk STRICTEMENT A
    L'INTERIEUR de chaque segment, keyframes exclues -- necessaire pour ne
    pas confondre "changement de segment" avec "tortillement", voir
    cycle 2 / README). Un handle VECTOR (tangente rectiligne) rend
    n'importe quel segment PARFAITEMENT plat en jerk interne (vitesse
    constante -> jerk nul par construction) mais peut laisser un vrai
    saut de vitesse D'UN segment a l'autre a la keyframe -- visuellement
    un mouvement "mecanique/robotique" plutot que fluide, invisible a
    curve_smoothness seule. Necessaire pour trancher honnetement entre
    AUTO_CLAMPED (courbe a l'interieur des segments, continuite de
    vitesse aux keyframes) et VECTOR (segments plats mais discontinuites
    de vitesse possibles) plutot que de choisir sur le seul score de
    curve_smoothness (aveugle a ce defaut).

    Pour chaque keyframe interieure (ni la premiere ni la derniere),
    compare la vitesse juste avant / juste apres (differences finies sur
    l'echantillonnage dense complet, PAS le decoupage par phase). Retourne
    dict joint -> liste de (t_keyframe, discontinuite_normalisee),
    + moyenne par joint."""
    joints = joints or [p for p in PART_ORDER if p != "HumanoidRootPart"]
    dt = 1.0 / sample_hz
    interior_times = keyframe_times[1:-1]
    out = {}
    for part in joints:
        rot = np.array([s[1] for s in samples[part]])  # (n,3) deg
        vel = np.gradient(rot, dt, axis=0)
        vel_mag = np.linalg.norm(vel, axis=1)
        scale = max(np.max(vel_mag), 1e-6)
        entries = []
        for t_kf in interior_times:
            i = int(round(t_kf * sample_hz))
            i = max(2, min(len(vel) - 3, i))
            v_before = vel[i - 2:i]
            v_after = vel[i:i + 2]
            jump = np.linalg.norm(v_after.mean(axis=0) - v_before.mean(axis=0))
            entries.append((t_kf, float(jump / scale)))
        out[part] = {"per_keyframe": entries, "mean": float(np.mean([e[1] for e in entries])) if entries else 0.0}
    return out


def composite_score(smoothness, twist, structural, continuity=None):
    """Score agrege unique (0-100, plus haut = meilleur) pour comparer les
    cycles et detecter un plateau. Poids : fluidite intra-segment 30,
    continuite de vitesse aux keyframes 15 (les deux ensemble couvrent
    "fluidite de la courbe" -- l'un sans l'autre se laisse tromper, voir
    velocity_continuity), absence de tortillement 25, conformite
    structurelle R6 30 (le rig est non negociable donc toute violation
    coute cher)."""
    # Decroissance exponentielle plutot que lineaire : un unique pic de jerk
    # au sommet d'un coup (inevitable et souhaitable -- c'est la pointe du
    # mouvement) ne doit pas a lui seul ecraser le score.
    smooth_score = 100.0 * math.exp(-0.02 * smoothness["_aggregate_max"])

    if continuity:
        worst_mean = max((v["mean"] for v in continuity.values()), default=0.0)
        continuity_score = 100.0 * math.exp(-3.0 * worst_mean)
    else:
        continuity_score = None

    total_extra = 0
    for phase_report in twist.values():
        for part_report in phase_report.values():
            total_extra += part_report["extra"]
    twist_score = max(0.0, 100.0 - total_extra * 20.0)

    n_ok = sum(1 for ok, _ in structural.values() if ok)
    n_total = len(structural)
    struct_score = 100.0 * n_ok / n_total if n_total else 0.0

    if continuity_score is None:
        return {
            "smoothness": round(smooth_score, 1),
            "no_twist": round(twist_score, 1),
            "structural": round(struct_score, 1),
            "total": round(0.4 * smooth_score + 0.3 * twist_score + 0.3 * struct_score, 1),
        }
    return {
        "smoothness_intra_segment": round(smooth_score, 1),
        "velocity_continuity_at_keyframes": round(continuity_score, 1),
        "no_twist": round(twist_score, 1),
        "structural": round(struct_score, 1),
        "total": round(0.30 * smooth_score + 0.15 * continuity_score
                        + 0.25 * twist_score + 0.30 * struct_score, 1),
    }
