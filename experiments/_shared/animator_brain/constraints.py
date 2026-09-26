"""
Contraintes d'animateur resolues par le calcul : pieds plantes (IK de jambe
RIGIDE R6) et regard (la tete vise un point du monde).

Pourquoi c'est vital en R6 : pas de genou. Une jambe est un segment rigide
de longueur fixe L (articulation de hanche -> milieu de la semelle). Pour
baisser le bassin avec les deux pieds au sol, il n'y a qu'une solution
geometrique : les jambes s'inclinent ET le bassin recule/avance pour que
chaque pied reste exactement a distance L de sa hanche. Poser les angles
de jambe "a l'oeil" avec le bassin fixe en x/z fait glisser les pieds --
mesure sur r6_black_hole avant correction : 2.96 studs de glissade au
crouch, jamais vue parce que calibrate.py ne verifiait que la HAUTEUR des
pieds (voir README, section "Contacts").

Deux niveaux d'usage (comme un animateur avec des jambes en IK) :
  - plant_pose()      : a la POSE CLE -- on donne torse + bassin souhaite
                        + cibles des pieds, on recoit le bassin corrige et
                        les angles de jambes exacts.
  - foot_lock_pass()  : sur les ECHANTILLONS -- entre deux cles, les
                        courbes Bezier interpolent angles et bassin
                        independamment, ce qui refait glisser les pieds ;
                        la passe re-resout chaque echantillon pendant les
                        fenetres d'appui (avec fondu d'entree/sortie).

Convention FK : identique a anim_engine._world_positions / fk_pose (espace
apercu : rotations C0/C1 ignorees, conversion au repere du joint faite a
l'export) -- donc ce qui est resolu ici est exactement ce qui est rendu et
exporte.
"""
import math

import numpy as np

from .rig_math import euler_xyz_matrix, fk_pose, part_tip


# ---------------------------------------------------------------------
# Geometrie d'une jambe
def _leg_vec(rig, leg):
    """v = vecteur articulation->semelle dans le repere de la jambe au
    repos (-c1 + (0, -h/2, 0)). |v| = longueur utile L."""
    _, c1 = rig.c0_c1(leg)
    h = rig.part_sizes[leg][1]
    return -c1 + np.array([0.0, -h / 2.0, 0.0])


def _torso_frame(rig, root_pos, root_rot, torso_rot):
    torso = rig.root_children[0]
    c0, c1 = rig.c0_c1(torso)
    Rr = euler_xyz_matrix(*root_rot)
    Rt = euler_xyz_matrix(*torso_rot)
    tw = np.array(root_pos, dtype=float) + Rr @ (c0 - Rt @ c1)
    return tw, Rr @ Rt


def _hip_joint(rig, leg, torso_w, R_tw):
    c0, _ = rig.c0_c1(leg)
    return torso_w + R_tw @ c0


# ---------------------------------------------------------------------
# Resolution du bassin : plus petit deplacement delta tel que chaque pied
# plante reste a distance L_i de sa hanche (intersection de spheres).
def root_offset_for_feet(centers, radii):
    """centers[i] = F_i - J_i (cible du pied moins hanche AVANT correction) ;
    on cherche delta de norme minimale avec |centers[i] - delta| = radii[i].
    1 pied : point de la sphere le plus proche de 0. 2 pieds : point du
    cercle d'intersection le plus proche de 0. Retourne (delta, exact)."""
    c = [np.asarray(x, dtype=float) for x in centers]
    r = list(radii)
    if len(c) == 1:
        n = np.linalg.norm(c[0])
        if n < 1e-9:
            return np.array([0.0, -r[0], 0.0]), True
        return c[0] * (1.0 - r[0] / n), True
    c1, c2 = c[0], c[1]
    r1, r2 = r[0], r[1]
    dvec = c2 - c1
    d = np.linalg.norm(dvec)
    if d < 1e-9 or d > r1 + r2 or d < abs(r1 - r2):
        # pas d'intersection exacte : moindres carres (Gauss-Newton) --
        # pieds trop ecartes pour la longueur de jambe, signale a l'appelant
        delta = np.zeros(3)
        for _ in range(30):
            res, J = [], []
            for ci, ri in zip(c, r):
                v = delta - ci
                nv = np.linalg.norm(v) + 1e-12
                res.append(nv - ri)
                J.append(v / nv)
            res, J = np.array(res), np.array(J)
            A = J.T @ J + 1e-6 * np.eye(3)
            step = np.linalg.solve(A, J.T @ res + 1e-6 * delta)
            delta -= step
            if np.linalg.norm(step) < 1e-9:
                break
        return delta, False
    n = dvec / d
    a = (d * d + r1 * r1 - r2 * r2) / (2 * d)
    m = c1 + a * n
    rho = math.sqrt(max(0.0, r1 * r1 - a * a))
    q = np.dot(m, n) * n            # projection de l'origine sur le plan du cercle
    e = q - m
    ne = np.linalg.norm(e)
    if ne < 1e-9:                   # origine sur l'axe : n'importe quelle direction du plan
        e = np.cross(n, [0.0, 1.0, 0.0])
        if np.linalg.norm(e) < 1e-9:
            e = np.cross(n, [1.0, 0.0, 0.0])
        ne = np.linalg.norm(e)
    return m + rho * e / ne, True


# ---------------------------------------------------------------------
# IK d'une jambe rigide : angles (rx, rz) -- torsion ry conservee -- qui
# pointent la semelle vers la cible.
def leg_angles_toward(rig, leg, R_tw, J, F, guess):
    v = _leg_vec(rig, leg)
    u = R_tw.T @ (np.asarray(F, dtype=float) - J)
    nu = np.linalg.norm(u)
    if nu < 1e-9:
        return tuple(guess)
    u = u * (np.linalg.norm(v) / nu)   # direction seule (la longueur est garantie par le bassin)
    rx, ry, rz = guess
    x = np.array([rx, rz], dtype=float)

    def f(p):
        return euler_xyz_matrix(p[0], ry, p[1]) @ v - u
    for _ in range(40):
        r0 = f(x)
        if np.linalg.norm(r0) < 1e-7:
            break
        Jm = np.zeros((3, 2))
        for k in range(2):
            dp = np.zeros(2)
            dp[k] = 1e-3
            Jm[:, k] = (f(x + dp) - r0) / 1e-3
        step = np.linalg.lstsq(Jm, -r0, rcond=None)[0]
        step = np.clip(step, -25, 25)
        x = x + step
        if np.linalg.norm(step) < 1e-6:
            break
    return (float(x[0]), float(ry), float(x[1]))


def plant_pose(rig, torso_rot, root_pos, feet, leg_guess, root_rot=(0.0, 0.0, 0.0)):
    """Pose cle, pieds plantes. feet : dict leg -> cible monde de la
    semelle (x, y, z). leg_guess : dict leg -> (rx, ry, rz) de depart (fixe
    la torsion ry et la branche de solution). Retourne (root_pos corrige,
    dict leg -> angles, info)."""
    tw, Rtw = _torso_frame(rig, root_pos, root_rot, torso_rot)
    legs = list(feet.keys())
    Js = {l: _hip_joint(rig, l, tw, Rtw) for l in legs}
    centers = [np.asarray(feet[l], dtype=float) - Js[l] for l in legs]
    radii = [np.linalg.norm(_leg_vec(rig, l)) for l in legs]
    delta, exact = root_offset_for_feet(centers, radii)
    new_root = np.asarray(root_pos, dtype=float) + delta
    angles = {l: leg_angles_toward(rig, l, Rtw, Js[l] + delta, feet[l], leg_guess[l]) for l in legs}
    # verification par FK complete (jamais supposee)
    rots = {rig.root: root_rot, rig.root_children[0]: torso_rot, **angles}
    wp, wr = fk_pose(rig, rots, new_root)
    err = {l: float(np.linalg.norm(part_tip(rig, wp, wr, l) - np.asarray(feet[l]))) for l in legs}
    return tuple(float(v) for v in new_root), angles, {"root_shift": delta.round(4).tolist(), "exact": exact,
                                                        "foot_error": err}


def plant_pose_at_height(rig, torso_rot, root_y, root_xz_guess, feet, leg_guess, root_rot=(0.0, 0.0, 0.0)):
    """Controle "animateur" du crouch : on impose la HAUTEUR du bassin
    (profondeur de l'accroupissement), les pieds restent plantes, et le
    solveur trouve OU le bassin doit se placer horizontalement (recule
    derriere les talons ou avance) -- exactement ce que fait un rig a
    jambes IK quand on baisse le controleur de hanche.

    Pourquoi pas plant_pose() : son critere "plus petit deplacement" est
    mal pose quand le bassin demande est loin du lieu atteignable (cercle
    de ~2 studs de rayon autour : n'importe quel point du cercle est "le
    plus proche" -- trouve en reglant le crouch de r6_black_hole, le
    bassin partait de 1.7 stud sur le cote).

    Geometrie : torse fixe => chaque hanche = bassin + a_i (constant) ;
    |F_i - (p + a_i)| = L_i avec p_y impose => deux cercles dans le plan
    horizontal y = root_y ; on prend l'intersection la plus proche de
    root_xz_guess (choisit la branche : bassin en arriere ou en avant).
    Retourne (root_pos, legs, info) -- info["feasible"] False si la
    hauteur est inatteignable avec cet ecart de pieds (bassin trop haut ou
    trop bas pour la longueur de jambe)."""
    tw0, Rtw = _torso_frame(rig, (0.0, 0.0, 0.0), root_rot, torso_rot)
    legs = list(feet.keys())
    circles = []
    feasible = True
    for l in legs:
        a = _hip_joint(rig, l, tw0, Rtw)          # hanche quand bassin = origine
        g = np.asarray(feet[l], dtype=float) - a  # bassin qui mettrait la hanche PILE sur le pied
        L = np.linalg.norm(_leg_vec(rig, l))
        dy = g[1] - root_y
        if abs(dy) > L:
            feasible = False
            r = 0.0
        else:
            r = math.sqrt(L * L - dy * dy)
        circles.append((np.array([g[0], g[2]]), r))
    gx = np.asarray(root_xz_guess, dtype=float)
    if len(circles) == 1:
        c, r = circles[0]
        v = gx - c
        nv = np.linalg.norm(v)
        p = c + (v / nv * r if nv > 1e-9 else np.array([0.0, r]))
    else:
        (c1, r1), (c2, r2) = circles
        dv = c2 - c1
        d = np.linalg.norm(dv)
        if d < 1e-9 or d > r1 + r2 or d < abs(r1 - r2):
            feasible = False
            # meilleur compromis : point du segment des centres pondere
            p = c1 + dv * (r1 / (r1 + r2 + 1e-9)) if d > 1e-9 else c1
        else:
            a_ = (d * d + r1 * r1 - r2 * r2) / (2 * d)
            h = math.sqrt(max(0.0, r1 * r1 - a_ * a_))
            m = c1 + a_ * dv / d
            perp = np.array([-dv[1], dv[0]]) / d
            cand = [m + h * perp, m - h * perp]
            p = min(cand, key=lambda q: np.linalg.norm(q - gx))
    root = np.array([p[0], root_y, p[1]])
    tw, _ = _torso_frame(rig, root, root_rot, torso_rot)
    angles = {l: leg_angles_toward(rig, l, Rtw, _hip_joint(rig, l, tw, Rtw), feet[l], leg_guess[l]) for l in legs}
    rots = {rig.root: root_rot, rig.root_children[0]: torso_rot, **angles}
    wp, wr = fk_pose(rig, rots, root)
    err = {l: float(np.linalg.norm(part_tip(rig, wp, wr, l) - np.asarray(feet[l]))) for l in legs}
    return tuple(float(v) for v in root), angles, {"feasible": feasible, "foot_error": err}


def balance_margin(rig, rots, root_pos, contact_legs, foot_half=0.5, ground_eps=0.06):
    """Distance (studs) du centre de masse a la base d'appui (enveloppe des
    semelles au sol, projection horizontale) : 0 = en equilibre. Une pose
    cle au sol hors equilibre est refusee par les choregraphies construites
    avec ce cerveau (voir r6_black_hole/choreography._grounded)."""
    from .audit import convex_hull, outside_distance
    from .rig_math import center_of_mass
    wp, wr = fk_pose(rig, rots, root_pos)
    corners = []
    for l in contact_legs:
        tip = part_tip(rig, wp, wr, l)
        if tip[1] < ground_eps:
            for sx in (-foot_half, foot_half):
                for sz in (-foot_half, foot_half):
                    corners.append((tip[0] + sx, tip[2] + sz))
    if not corners:
        return None
    com = center_of_mass(rig, wp)
    return outside_distance(convex_hull(np.array(corners)), np.array([com[0], com[2]]))


def pelvis_height_range(rig, torso_rot, feet, y_min=0.3, y_max=4.0, step=0.01, root_rot=(0.0, 0.0, 0.0)):
    """Hauteurs de bassin atteignables (pieds plantes, torse donne) --
    renvoie (y_bas, y_haut) de la plus grande plage continue, ou None.
    A consulter AVANT de choisir la profondeur d'un crouch : avec des
    jambes rigides, torsion du bassin et ecart des pieds changent
    fortement ce qui est possible (trouve en reglant r6_black_hole : un
    crouch tordu de -10 deg a y=1.9 etait infaisable)."""
    ok = []
    for y in np.arange(y_min, y_max + 1e-9, step):
        _, _, info = plant_pose_at_height(rig, torso_rot, float(y), (0.0, 0.0), feet,
                                          {l: (0.0, 0.0, 0.0) for l in feet}, root_rot)
        ok.append((float(y), info["feasible"] and max(info["foot_error"].values()) < 1e-4))
    best, cur = None, None
    for y, f in ok:
        if f:
            cur = (cur[0], y) if cur else (y, y)
            if best is None or cur[1] - cur[0] > best[1] - best[0]:
                best = cur
        else:
            cur = None
    return best


# ---------------------------------------------------------------------
# Passe sur echantillons (format anim_engine : part -> [(t, rot, pos)])
def _weight(t, t0, t1, blend):
    if t < t0 - blend or t > t1 + blend:
        return 0.0
    if t < t0:
        x = (t - (t0 - blend)) / blend
    elif t > t1:
        x = ((t1 + blend) - t) / blend
    else:
        return 1.0
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


# Decollage : les pieds partent quand la demi-corde des cercles d'appui
# passe sous TOE_OFF_CHORD (jambes a ~95 % d'extension). Pres de la pleine
# extension, le probleme devient SINGULIER : cercles quasi tangents, leur
# intersection file a l'horizontale pour un rien de hauteur (mesure :
# 21.9 puis 40 studs/s la frame avant le decollage ; melanger vers la
# solution 3D "plus petit deplacement" empirait -- elle est elle-meme mal
# posee la). Physiquement juste : les pieds quittent le sol JUSTE AVANT
# que les jambes se verrouillent tendues.
TOE_OFF_CHORD = 0.35


def _weight2(t, t0, t1, bin_, bout):
    """Poids d'un appui : fondu d'ENTREE (le pied arrive) et de SORTIE
    (le pied part) reglables separement. Un decollage a blend_out=0 : une
    fois la jambe tendue le pied quitte le sol net -- un fondu de sortie y
    retiendrait le bassin pendant que la cle le propulse (pop mesure :
    0.85 stud de correction a la frame suivante)."""
    if t < t0:
        if bin_ <= 0 or t < t0 - bin_:
            return 0.0
        x = (t - (t0 - bin_)) / bin_
    elif t > t1:
        if bout <= 0 or t > t1 + bout:
            return 0.0
        x = ((t1 + bout) - t) / bout
    else:
        return 1.0
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def _horizontal_offset_at_height(rig, legs, targets, hip_offsets, rp, prev_xz):
    """Deplacement HORIZONTAL (dy = 0) du bassin qui remet chaque pied
    plante a distance L de sa hanche, a hauteur de bassin inchangee. Deux
    pieds : intersection de deux cercles dans le plan y = bassin, branche la
    plus proche de la solution de l'echantillon precedent (continuite --
    jamais de saut de branche). None si inatteignable a cette hauteur."""
    circles = []
    for l in legs:
        g = np.asarray(targets[l], dtype=float) - hip_offsets[l]
        L = np.linalg.norm(_leg_vec(rig, l))
        dy = g[1] - rp[1]
        if abs(dy) > L:
            return None
        circles.append((np.array([g[0], g[2]]), math.sqrt(L * L - dy * dy)))
    ref = np.array(prev_xz if prev_xz is not None else (rp[0], rp[2]), dtype=float)
    if len(circles) == 1:
        c, r = circles[0]
        v = ref - c
        nv = np.linalg.norm(v)
        p = c + (v / nv * r if nv > 1e-9 else np.array([0.0, r]))
        cond = r
    else:
        (c1, r1), (c2, r2) = circles
        dv = c2 - c1
        d = np.linalg.norm(dv)
        if d < 1e-9 or d > r1 + r2 or d < abs(r1 - r2):
            return None
        a = (d * d + r1 * r1 - r2 * r2) / (2 * d)
        h = math.sqrt(max(0.0, r1 * r1 - a * a))
        m = c1 + a * dv / d
        perp = np.array([-dv[1], dv[0]]) / d
        p = min((m + h * perp, m - h * perp), key=lambda q: np.linalg.norm(q - ref))
        cond = h
    return np.array([p[0] - rp[0], 0.0, p[1] - rp[2]]), cond


def foot_lock_pass(local_samples, rig, contacts, ground_y=0.0, blend_s=3 / 30, release_eps=0.02,
                   preserve_height=True):
    """contacts : liste de {"leg", "t0", "t1", "target": (x,y,z) | None,
    optionnel "blend_in"/"blend_out" (s)}.
    target None = position de la semelle a t0 (dans les echantillons
    d'entree), y force au sol. Modifie local_samples en place ; retourne un
    journal (deplacement max du bassin, erreur residuelle max)."""
    root = rig.root
    torso = rig.root_children[0]
    n = len(local_samples[root])
    times = [s[0] for s in local_samples[root]]

    def pose_at(i):
        return {p: local_samples[p][i][1] for p in local_samples}, local_samples[root][i][2]

    targets = []
    for c in contacts:
        tgt = c.get("target")
        if tgt is None:
            i0 = min(range(n), key=lambda k: abs(times[k] - c["t0"]))
            rots, rp = pose_at(i0)
            wp, wr = fk_pose(rig, rots, rp)
            tip = part_tip(rig, wp, wr, c["leg"])
            tgt = (float(tip[0]), ground_y, float(tip[2]))
        targets.append(np.array(tgt, dtype=float))

    log = {"max_root_shift": 0.0, "t_max_root_shift": None, "max_residual": 0.0, "inexact_samples": 0,
           "auto_toe_off": {}}
    released = [False] * len(contacts)
    prev_xz = None
    for i in range(n):
        t = times[i]
        rots, rp = pose_at(i)
        tw, Rtw = _torso_frame(rig, rp, rots[root], rots[torso])
        # DECOLLAGE AUTOMATIQUE (contact avec "release_after") : des que la
        # jambe est a pleine extension -- le bassin cle est trop haut pour
        # que le pied touche encore, l'IK devrait le TIRER VERS LE BAS -- le
        # pied quitte le sol a CET echantillon. Programmer le decollage a
        # une date fixe bloquait le bassin a pleine extension en attendant
        # la date, puis le relachait d'un coup (mesure r6_black_hole :
        # vitesse du bassin 9.5 -> 1 -> 29 studs/s, "double pompe").
        cand = [k for k, c in enumerate(contacts)
                if c.get("release_after") is not None and not released[k]
                and c["release_after"] <= t <= c["t1"] + c.get("blend_out", blend_s)]
        if cand:
            # critere VERTICAL : garder ces pieds au sol exigerait de
            # TIRER LE BASSIN VERS LE BAS (delta_y < 0) -> les jambes sont a
            # pleine extension, les pieds partent. Un simple "pied hors de
            # portee" confondait extension et derive laterale du bassin
            # entre deux cles (premier essai : decollage 1 frame apres le
            # debut de la poussee, jambes encore pliees).
            legs_c = [contacts[k]["leg"] for k in cand]
            Js = [_hip_joint(rig, l, tw, Rtw) for l in legs_c]
            d, _ = root_offset_for_feet([targets[k] - J for k, J in zip(cand, Js)],
                                        [np.linalg.norm(_leg_vec(rig, l)) for l in legs_c])
            res = _horizontal_offset_at_height(rig, legs_c, {l: targets[k] for k, l in zip(cand, legs_c)},
                                               {l: J - np.asarray(rp) for l, J in zip(legs_c, Js)},
                                               np.asarray(rp), prev_xz)
            near_singular = res is None or res[1] < TOE_OFF_CHORD
            if d[1] < -release_eps or near_singular:
                for k in cand:
                    released[k] = True
                    log["auto_toe_off"][contacts[k]["leg"]] = round(float(t), 3)
        active = []
        for k, (c, tgt) in enumerate(zip(contacts, targets)):
            if released[k]:
                continue
            w = _weight2(t, c["t0"], c["t1"], c.get("blend_in", blend_s), c.get("blend_out", blend_s))
            if w > 0:
                active.append((c["leg"], tgt, w))
        if not active:
            prev_xz = None   # nouvel appui = nouvelle continuite de branche
            continue
        # une seule cible par jambe (la plus ponderee)
        by_leg = {}
        for leg, tgt, w in active:
            if leg not in by_leg or w > by_leg[leg][1]:
                by_leg[leg] = (tgt, w)
        legs = list(by_leg)
        Js = {l: _hip_joint(rig, l, tw, Rtw) for l in legs}
        # SEULS LES PIEDS PORTEURS (poids plein) placent le bassin ; un pied
        # qui est en train d'arriver (fondu d'entree) ne fait que ramener SA
        # jambe vers le sol. Sinon le bassin sautait pour satisfaire un pied
        # pas encore pose (mesure : pic a 16 studs/s a l'atterrissage).
        hard = [l for l in legs if by_leg[l][1] >= 0.999]
        solve_legs = hard if hard else [max(legs, key=lambda l: by_leg[l][1])]
        delta, exact = root_offset_for_feet([by_leg[l][0] - Js[l] for l in solve_legs],
                                            [np.linalg.norm(_leg_vec(rig, l)) for l in solve_legs])
        # HAUTEUR PRESERVEE (defaut) : la hauteur du bassin est l'intention
        # de l'animateur (profondeur du crouch, montee de la poussee) ; les
        # pieds ne decident que de sa position HORIZONTALE -- comme un
        # controleur de hanche avec jambes en IK. La correction 3D "plus
        # petit deplacement" modifiait aussi la hauteur, donc la courbe de
        # vitesse verticale cle (mesure : bosse de +0.08 stud la frame avant
        # le decollage -> a-coup de vitesse). Repli 3D si la hauteur est
        # inatteignable.
        def _solve(ls, d3, ex):
            if preserve_height:
                res = _horizontal_offset_at_height(rig, ls, {l: by_leg[l][0] for l in ls},
                                                   {l: Js[l] - np.asarray(rp) for l in ls}, np.asarray(rp),
                                                   prev_xz)
                if res is not None:
                    return res[0], True
            return d3, ex
        delta, exact = _solve(solve_legs, delta, exact)
        # TRANSFERT DE POIDS progressif : un pied qui arrive (fondu
        # d'entree) fait glisser la solution du bassin de "appui simple" a
        # "double appui" au rythme de son poids -- sans ca, le bassin
        # sautait d'une solution a l'autre a la frame ou le pied devenait
        # porteur (mesure : 15.6 studs/s sur une frame).
        partial = [l for l in legs if l not in solve_legs]
        if partial and hard:
            w_p = max(by_leg[l][1] for l in partial)
            d3_all, ex_all = root_offset_for_feet([by_leg[l][0] - Js[l] for l in legs],
                                                  [np.linalg.norm(_leg_vec(rig, l)) for l in legs])
            d_all, _ = _solve(legs, d3_all, ex_all)
            delta = delta + w_p * (d_all - delta)
        wmax = max(by_leg[l][1] for l in solve_legs)
        delta = delta * wmax
        prev_xz = (rp[0] + delta[0], rp[2] + delta[2])
        if not exact:
            log["inexact_samples"] += 1
        new_rp = tuple(float(a + b) for a, b in zip(rp, delta))
        t_, r_, _ = local_samples[root][i]
        local_samples[root][i] = (t_, r_, new_rp)
        if float(np.linalg.norm(delta)) > log["max_root_shift"]:
            log["max_root_shift"] = float(np.linalg.norm(delta))
            log["t_max_root_shift"] = round(float(t), 3)
        for l in legs:
            tgt, w = by_leg[l]
            cur = local_samples[l][i][1]
            ik = leg_angles_toward(rig, l, Rtw, Js[l] + delta, tgt, cur)
            blended = tuple(a + w * (b - a) for a, b in zip(cur, ik))
            if w < 0.999:
                # pied qui arrive : il ne doit JAMAIS passer sous le sol
                # pendant son fondu (le bassin descend plus vite que le
                # fondu ne le remonte -- mesure : -6 cm a l'atterrissage) ;
                # s'il le ferait, il est verrouille des maintenant.
                rots_b = {p: local_samples[p][i][1] for p in local_samples}
                rots_b[l] = blended
                rp_b = tuple(float(a + b) for a, b in zip(rp, delta))
                wpb, wrb = fk_pose(rig, rots_b, rp_b)
                if part_tip(rig, wpb, wrb, l)[1] < ground_y - 0.002:
                    blended = ik
            tl, _, pl = local_samples[l][i]
            local_samples[l][i] = (tl, blended, pl)
        # residu apres correction (FK complete)
        rots2, rp2 = pose_at(i)
        wp, wr = fk_pose(rig, rots2, rp2)
        for l in legs:
            tgt, w = by_leg[l]
            if w >= 0.999:
                log["max_residual"] = max(log["max_residual"],
                                          float(np.linalg.norm(part_tip(rig, wp, wr, l) - tgt)))
    # PASSE DE RELACHEMENT DES JAMBES : a la fin d'un appui (decollage), le
    # bassin est libre immediatement, mais la JAMBE passe en douceur de son
    # angle IK (au dernier echantillon d'appui) a sa courbe cle -- la courbe
    # cle de la jambe peut etre en retard volontaire (overlap) et differer de
    # l'IK a cet instant (mesure : pic d'acceleration 10x la norme sur les
    # jambes au decollage).
    for c in contacts:
        rb = c.get("leg_release_blend")
        if not rb:
            continue
        leg = c["leg"]
        t_end = c["t1"]
        i_end = max((k for k in range(n) if times[k] <= t_end), default=None)
        if i_end is None:
            continue
        a0 = np.array(local_samples[leg][i_end][1], dtype=float)
        for k in range(i_end + 1, n):
            x = (times[k] - times[i_end]) / rb
            if x >= 1.0:
                break
            w = 1.0 - x * x * (3 - 2 * x)
            tl, cur, pl = local_samples[leg][k]
            cur = np.array(cur, dtype=float)
            local_samples[leg][k] = (tl, tuple(float(v) for v in cur + w * (a0 - cur)), pl)
    log = {k: (round(v, 4) if isinstance(v, float) else v) for k, v in log.items()}
    return log


# ---------------------------------------------------------------------
# Regard : la tete vise un point du monde (les yeux menent l'action).
def head_look_angles(rig, head, R_parent_w, head_w, target, current, limits=(55.0, 70.0)):
    """Angles locaux (rx, ry, rz) de la tete qui orientent sa face (-Z
    local) vers `target`, roulis rz conserve, bornes |rx|<=limits[0],
    |ry|<=limits[1] (une tete qui "casse" le cou au-dela se lit fausse)."""
    d = np.asarray(target, dtype=float) - np.asarray(head_w, dtype=float)
    nd = np.linalg.norm(d)
    if nd < 1e-6:
        return tuple(current)
    dl = R_parent_w.T @ (d / nd)
    # 1) direction BORNEE dans le cone atteignable (lacet puis elevation),
    #    AVANT toute resolution -- une cible derriere la tete ne fait plus
    #    basculer la solution d'un cote a l'autre d'une frame a l'autre
    #    (trouve par l'audit : pic d'acceleration 29x la norme sur la tete).
    yaw = math.degrees(math.atan2(-dl[0], -dl[2]))
    # cible quasi DERRIERE (|lacet| > 150) : gauche ou droite n'est decide
    # que par le bruit d'arrondi -> on garde le cote vers lequel la tete
    # tourne deja (hysteresis). Trouve par l'audit : lacet +23.5 -> -18.8
    # deg en UN echantillon (2581 deg/s) sur le coup d'oeil final.
    if abs(yaw) > 150.0 and current[1] != 0.0 and (yaw > 0) != (current[1] > 0):
        yaw = -yaw
    yaw = max(-limits[1], min(limits[1], yaw))
    elev = math.degrees(math.atan2(dl[1], math.hypot(dl[0], dl[2])))
    elev = max(-limits[0], min(limits[0], elev))
    cy, sy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    ce, se = math.cos(math.radians(elev)), math.sin(math.radians(elev))
    dc = np.array([-sy * ce, se, -cy * ce])
    # 2) inversion exacte de forward = Rx(p) Ry(y) (0,0,-1)
    #    = (-sin y, sin p cos y, -cos p cos y)  (Rz ne change pas l'axe Z)
    ry = math.degrees(math.asin(max(-1.0, min(1.0, -dc[0]))))
    rx = math.degrees(math.atan2(dc[1], -dc[2]))
    return (float(rx), float(ry), float(current[2]))


def look_at_pass(local_samples, rig, windows, head="Head", blend_s=6 / 30):
    """windows : liste de {"t0","t1","target": (x,y,z) ou callable(t),
    "weight": 0..1}. Melange (poids) le regard par-dessus la tete cle : la
    tete garde son jeu (et son retard d'overlap) mais son regard est
    stabilise sur la cible -- c'est ce qui evite la tete "posee sur un
    manche" qui suit le corps comme un bloc."""
    root = rig.root
    parent = rig.parent[head]
    n = len(local_samples[root])
    for i in range(n):
        t = local_samples[root][i][0]
        wsum, tgt = 0.0, None
        for w in windows:
            wt = _weight(t, w["t0"], w["t1"], blend_s) * w.get("weight", 1.0)
            if wt > wsum:
                wsum = wt
                tgt = w["target"](t) if callable(w["target"]) else w["target"]
        if wsum <= 0:
            continue
        rots = {p: local_samples[p][i][1] for p in local_samples}
        rp = local_samples[root][i][2]
        wp, wr = fk_pose(rig, rots, rp)
        cur = rots[head]
        la = head_look_angles(rig, head, wr[parent], wp[head], tgt, cur)
        blended = tuple(a + wsum * (b - a) for a, b in zip(cur, la))
        th, _, ph = local_samples[head][i]
        local_samples[head][i] = (th, blended, ph)
