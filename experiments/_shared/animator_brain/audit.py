"""
Audit de mouvement -- mesure CHIFFREE de ce qui fait qu'une animation se
lit "mecanique" au lieu de vivante. Ne regarde jamais une image fixe : que
des courbes dans le temps (c'est la que le defaut vit -- une pose peut etre
parfaite et le mouvement entre deux poses robotique).

Chaque metrique correspond a UN principe d'animation viole (voir
README.md, section "Principes -> metriques") :

  overlap        chevauchement / "successive breaking of joints" : un membre
                 enfant doit culminer APRES son parent (retard > 0), jamais
                 pile en meme temps que lui.
  stop_clusters  "pose-to-pose robot" : quand toutes les articulations
                 s'arretent a la MEME frame (typique de cles posees sur
                 tout le corps au meme instant).
  symmetry       "twinning" : bras/jambes gauche et droite en miroir exact
                 (meme pose, meme timing).
  planarity      colonne/tete qui ne tournent que sur UN axe (pitch pur,
                 aucune torsion/inclinaison laterale).
  loops          boucles metronome : cycles d'attente/vol a periode et
                 amplitude parfaitement constantes (sinus pur).
  contacts       pieds qui glissent/s'enfoncent pendant un appui.
  frozen         "hold mort" : tout le corps parfaitement immobile (le
                 principe du "moving hold" demande qu'un hold respire).

Seuils (`TARGETS`) : heuristiques documentees tirees des principes, PAS
calibrees sur un corpus d'animations pro -- prochaine etape identifiee
(README) : les recalibrer sur les rotations fiables du pack
battleground_animation_pack (voir _shared/rbxm_reader.py).

Unite de temps rapportee : frames a 30 fps (convention de ce depot, _fr()),
meme si l'echantillonnage d'entree est plus fin.
"""
import json
import math

import numpy as np

from .rig_math import SampledClip

FPS_REPORT = 30.0


# ---------------------------------------------------------------------
# Outils signal (numpy pur -- pas de scipy dans ce bac a sable)
def smooth(x, k):
    if k <= 1:
        return np.asarray(x, dtype=float)
    k = int(k) | 1
    pad = k // 2
    xp = np.pad(np.asarray(x, dtype=float), pad, mode="edge")
    return np.convolve(xp, np.ones(k) / k, mode="valid")


def find_peaks(x, min_prominence):
    """Maxima locaux de proeminence >= min_prominence (definition
    topographique standard : on descend de chaque cote jusqu'a un point
    plus haut ou le bord, la proeminence = hauteur - le plus haut des deux
    creux rencontres). Plateaux : un seul pic, au milieu du plateau."""
    x = np.asarray(x, dtype=float)
    n = len(x)
    peaks = []
    i = 1
    while i < n - 1:
        if x[i] > x[i - 1]:
            j = i
            while j + 1 < n and x[j + 1] == x[i]:
                j += 1
            if j + 1 < n and x[j + 1] < x[i]:
                mid = (i + j) // 2
                h = x[i]
                l = i - 1
                lmin = x[i]
                while l >= 0 and x[l] <= h:
                    lmin = min(lmin, x[l])
                    l -= 1
                r = j + 1
                rmin = x[i]
                while r < n and x[r] <= h:
                    rmin = min(rmin, x[r])
                    r += 1
                prom = h - max(lmin, rmin)
                if prom >= min_prominence:
                    peaks.append(mid)
            i = j + 1
        else:
            i += 1
    return np.array(peaks, dtype=int)


def _frames(seconds):
    return seconds * FPS_REPORT


def _window_mask(clip, windows):
    if not windows:
        return np.ones(len(clip), dtype=bool)
    m = np.zeros(len(clip), dtype=bool)
    for (a, b) in windows:
        m |= (clip.t >= a) & (clip.t <= b)
    return m


# ---------------------------------------------------------------------
# 1. Overlap : retard des pics de vitesse enfant vs parent
def peak_lags(clip, driver, child, max_lag_s=0.4, prom_frac=0.15, mask=None, smooth_k=3):
    d = smooth(driver, smooth_k)
    c = smooth(child, smooth_k)
    if d.max() <= 1e-6 or c.max() <= 1e-6:
        return []
    pd = find_peaks(d, prom_frac * d.max())
    pc = find_peaks(c, prom_frac * c.max())
    if len(pd) == 0 or len(pc) == 0:
        return []
    lags = []
    for i in pd:
        if mask is not None and not mask[i]:
            continue
        dt = clip.t[pc] - clip.t[i]
        k = int(np.argmin(np.abs(dt)))
        if abs(dt[k]) <= max_lag_s:
            lags.append(float(dt[k]))
    return lags


def _lag_summary(lags):
    if not lags:
        return {"n": 0}
    f = np.array([_frames(l) for l in lags])
    return {
        "n": int(len(f)),
        "median_frames": round(float(np.median(f)), 2),
        "mean_abs_frames": round(float(np.mean(np.abs(f))), 2),
        # "synchrone" = pic dans la meme demi-frame a 30 fps que le parent
        "sync_fraction": round(float(np.mean(np.abs(f) < 0.5)), 3),
    }


def overlap_report(clip, chain=None, windows=None, child_windows=None):
    """chain : liste de (enfant, parent) -- parent peut etre "root" (vitesse
    lineaire de la racine). Par defaut, la chaine R6 : racine -> torse ->
    tete/bras/jambes. child_windows : fenetres propres a un enfant (ex.
    jambes mesurees seulement EN L'AIR : une jambe d'appui est pilotee par
    le contact, elle bouge avec le bassin par physique -- l'overlap est un
    principe des membres LIBRES)."""
    child_windows = child_windows or {}
    root = clip.rig.root
    torso = next((p for p in clip.rig.root_children), None)
    if chain is None:
        chain = [(torso, "root")] + [(p, torso) for p in clip.parts
                                     if clip.rig.parent.get(p) == torso]
    mask = _window_mask(clip, windows)
    sig = {"root": clip.linear_speed(root)}
    for p in clip.parts:
        if p != root:
            sig[p] = clip.local_angular_speed(p)
    rep = {}
    for child, par in chain:
        m = _window_mask(clip, child_windows[child]) if child in child_windows else mask
        rep[f"{child} <- {par}"] = _lag_summary(peak_lags(clip, sig[par], sig[child], mask=m))
    return rep, sig


# ---------------------------------------------------------------------
# 2. Arrets simultanes ("robot hits")
def stop_clusters(clip, sig, parts, stop_frac=0.12, coincide_frames=1.0, min_others=3, windows=None):
    mask = _window_mask(clip, windows)
    stops = {}
    for p in parts:
        s = smooth(sig[p], 3)
        ref = np.percentile(s, 95)
        if ref <= 1e-6:
            stops[p] = np.array([], dtype=int)
            continue
        mins = find_peaks(-s, 0.2 * ref)  # creux marques
        stops[p] = np.array([i for i in mins if s[i] < stop_frac * ref and mask[i]], dtype=int)
    tol = coincide_frames / FPS_REPORT
    total, clustered = 0, 0
    for p in parts:
        for i in stops[p]:
            total += 1
            others = 0
            for q in parts:
                if q == p or len(stops[q]) == 0:
                    continue
                if np.min(np.abs(clip.t[stops[q]] - clip.t[i])) <= tol:
                    others += 1
            if others >= min_others:
                clustered += 1
    return {"stops": int(total), "clustered": int(clustered),
            "clustered_fraction": round(clustered / total, 3) if total else None}


# ---------------------------------------------------------------------
# 3. Symetrie gauche/droite (poses ET timing)
def symmetry_report(clip, sig, pairs=(("Right Arm", "Left Arm"), ("Right Leg", "Left Leg")), windows=None,
                    pair_windows=None):
    """pair_windows : fenetres propres a une paire (jambes : en l'air
    seulement, meme raison que pour l'overlap -- deux jambes d'appui qui
    portent le meme bassin ont des vitesses correlees par physique)."""
    mask = _window_mask(clip, windows)
    ax = clip.rig.lateral_axis
    rep = {}
    pair_windows = pair_windows or {}
    for r, l in pairs:
        if r not in clip.parts or l not in clip.parts:
            continue
        if r in pair_windows:
            mask = _window_mask(clip, pair_windows[r])
        tr = clip.in_root_frame(clip.tip(r))
        tl = clip.in_root_frame(clip.tip(l))
        tl_m = tl.copy()
        tl_m[:, ax] *= -1.0
        d = np.linalg.norm(tr - tl_m, axis=1)[mask]
        sr, sl = smooth(sig[r], 3)[mask], smooth(sig[l], 3)[mask]
        corr = float(np.corrcoef(sr, sl)[0, 1]) if sr.std() > 1e-6 and sl.std() > 1e-6 else 1.0
        lr = _lag_summary(peak_lags(clip, sig[r], sig[l], mask=mask))
        mask = _window_mask(clip, windows)
        rep[f"{r}/{l}"] = {
            "mirror_dist_mean_studs": round(float(d.mean()), 3),
            "mirror_near_fraction": round(float(np.mean(d < 0.12)), 3),  # temps passe en miroir quasi exact
            "speed_corr": round(corr, 3),
            "peak_lag_LR": lr,
        }
    return rep


# ---------------------------------------------------------------------
# 4. Planarite de la colonne/tete (rotation sur un seul axe ?)
def planarity(clip, part, windows=None):
    mask = _window_mask(clip, windows)
    R = clip.local_rot[part]
    inc = []
    for i in range(1, len(R)):
        if not mask[i]:
            continue
        d = R[i - 1].T @ R[i]
        w = np.array([d[2, 1] - d[1, 2], d[0, 2] - d[2, 0], d[1, 0] - d[0, 1]]) / 2.0  # ~ theta*axe (petits pas)
        inc.append(w)
    if not inc:
        return None
    W = np.array(inc)
    S = W.T @ W
    tr = float(np.trace(S))
    if tr <= 1e-12:
        return {"dominant_axis_share": None, "note": "immobile"}
    ev, evec = np.linalg.eigh(S)
    return {"dominant_axis_share": round(float(ev[-1] / tr), 3),
            "dominant_axis": [round(float(v), 2) for v in evec[:, -1]]}


# ---------------------------------------------------------------------
# 5. Boucles metronome
def loop_regularity(clip, sig, window, parts=("Right Arm", "Left Arm")):
    a, b = window
    m = (clip.t >= a) & (clip.t <= b)
    if m.sum() < 8:
        return None
    out = {}
    y = clip.world_pos[clip.rig.root][m, 1]
    series = {"root_y": y - y.mean()}
    for p in parts:
        if p in sig:
            series[f"{p} speed"] = sig[p][m]
    for name, s in series.items():
        s = smooth(s, 3)
        rng = s.max() - s.min()
        if rng <= 1e-6:
            out[name] = {"note": "plat"}
            continue
        pk = find_peaks(s, 0.15 * rng)
        entry = {"peaks": int(len(pk))}
        if len(pk) >= 3:
            iv = np.diff(clip.t[m][pk])
            amp = s[pk]
            entry["interval_cv"] = round(float(iv.std() / iv.mean()), 3)
            entry["amplitude_cv"] = round(float(amp.std() / (abs(amp.mean()) + 1e-9)), 3)
        spec = np.abs(np.fft.rfft(s - s.mean())) ** 2
        if spec.sum() > 0 and len(spec) > 3:
            k = int(np.argmax(spec[1:]) + 1)
            # k = nombre de cycles de la composante dominante dans la
            # fenetre. La purete somme les bins k-1..k+1 : pour k <= 2 cela
            # couvre les bins 1..3, soit quasiment TOUTE l'energie de
            # n'importe quel signal lent sur une fenetre courte -> la mesure
            # ne distingue plus un sinus d'un mouvement organique. Valide a
            # partir de 3 cycles ; sinon declaree non applicable plutot que
            # de juger du bruit (meme regle appliquee a l'avant et a l'apres).
            entry["dominant_cycles_in_window"] = k
            if k >= 3:
                share = spec[max(1, k - 1):k + 2].sum() / spec[1:].sum()
                entry["dominant_freq_share"] = round(float(share), 3)
            else:
                entry["note"] = "fenetre < 3 cycles : purete non applicable"
        out[name] = entry
    return out


# ---------------------------------------------------------------------
# 6. Contacts pieds : glissement horizontal + enfoncement
def contact_report(clip, feet=("Right Leg", "Left Leg"), contact_eps=0.02, vy_eps=0.5, up_axis=1):
    """Glissement = deplacement horizontal d'un pied PLANTE : au sol a
    `contact_eps` pres ET sans vitesse verticale notable (definition
    standard du "foot skating"). Un pied a 5 cm du sol qui descend est en
    train d'ATTERRIR, pas de glisser -- la premiere version de ce metrique
    (seuil 6 cm, sans condition de vitesse) comptait l'approche et le
    decollage comme du glissement."""
    rep = {}
    for f in feet:
        if f not in clip.parts:
            continue
        tip = clip.tip(f)
        y = tip[:, up_axis]
        vy = np.gradient(y, clip.dt)
        horiz = np.delete(tip, up_axis, axis=1)
        c = (y < contact_eps) & (np.abs(vy) < vy_eps)
        runs, i, n = [], 0, len(c)
        while i < n:
            if c[i]:
                j = i
                while j + 1 < n and c[j + 1]:
                    j += 1
                if j > i:
                    disp = np.linalg.norm(horiz[i:j + 1] - horiz[i], axis=1).max()
                    runs.append({"t0": round(float(clip.t[i]), 3), "t1": round(float(clip.t[j]), 3),
                                 "skate_max_studs": round(float(disp), 3)})
                i = j + 1
            else:
                i += 1
        rep[f] = {
            "contacts": len(runs),
            "worst_skate_studs": max((r["skate_max_studs"] for r in runs), default=0.0),
            "min_height_studs": round(float(y.min()), 3),
            "runs": runs,
        }
    return rep


# ---------------------------------------------------------------------
# 6b. Equilibre : centre de masse au-dessus de la base d'appui
def convex_hull(pts):
    pts = sorted(set(map(tuple, np.round(pts, 6))))
    if len(pts) <= 2:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def outside_distance(poly, q):
    """0 si q est dans le polygone convexe, sinon distance au bord."""
    n = len(poly)
    if n < 3:
        return float(min(np.linalg.norm(np.array(p) - q) for p in poly))
    inside = True
    for i in range(n):
        a, b = np.array(poly[i]), np.array(poly[(i + 1) % n])
        if (b[0] - a[0]) * (q[1] - a[1]) - (b[1] - a[1]) * (q[0] - a[0]) < 0:
            inside = False
            break
    if inside:
        return 0.0
    best = 1e9
    for i in range(n):
        a, b = np.array(poly[i]), np.array(poly[(i + 1) % n])
        ab = b - a
        u = np.clip(np.dot(q - a, ab) / (np.dot(ab, ab) + 1e-12), 0, 1)
        best = min(best, float(np.linalg.norm(a + u * ab - q)))
    return best


def balance_report(clip, feet=("Right Leg", "Left Leg"), contact_eps=0.06, foot_half=0.5, tol=0.25):
    """Fraction du temps AU SOL ou la projection du centre de masse sort
    de la base d'appui (enveloppe convexe des semelles au sol) de plus de
    `tol` studs. Une pose statique hors equilibre se lit "fausse" meme si
    personne ne sait dire pourquoi ; un elan dynamique (depart de saut)
    peut legitimement en sortir brievement -- d'ou une fraction, pas un
    interdit absolu."""
    parts = [p for p in clip.parts if p != clip.rig.root]
    mass = {p: float(np.prod(clip.rig.part_sizes[p])) for p in parts}
    M = sum(mass.values())
    com = sum(mass[p] * clip.world_pos[p] for p in parts) / M
    tips = {f: clip.tip(f) for f in feet if f in clip.parts}
    grounded, outside, worst = 0, 0, 0.0
    for i in range(len(clip)):
        corners = []
        for f, tp in tips.items():
            if tp[i, 1] < contact_eps:
                x, z = tp[i, 0], tp[i, 2]
                corners += [(x - foot_half, z - foot_half), (x + foot_half, z - foot_half),
                            (x - foot_half, z + foot_half), (x + foot_half, z + foot_half)]
        if not corners:
            continue
        grounded += 1
        dist = outside_distance(convex_hull(np.array(corners)), np.array([com[i, 0], com[i, 2]]))
        worst = max(worst, dist)
        if dist > tol:
            outside += 1
    return {"grounded_samples": grounded,
            "outside_fraction": round(outside / grounded, 3) if grounded else None,
            "worst_outside_studs": round(worst, 3)}


# ---------------------------------------------------------------------
# 6c. "Pops" : a-coups (acceleration anormale sur 1-2 echantillons) -- la
# signature d'une discontinuite de vitesse (fin de contrainte brutale,
# cle en double, ressort relance...). Un snap VOULU (impact) en produit
# aussi : on rapporte les instants pour relecture, le verdict ne compte
# que ceux qui depassent nettement l'enveloppe du reste du clip.
def pops_report(clip, sig, factor=4.0, max_width_s=0.034):
    out = {}
    series = {"root (lin.)": clip.world_pos[clip.rig.root]}
    for name, p in series.items():
        v = np.gradient(p, clip.dt, axis=0)
        a = np.linalg.norm(np.gradient(v, clip.dt, axis=0), axis=1)
        out[name] = a
    for p in clip.parts:
        if p == clip.rig.root:
            continue
        out[p] = np.abs(np.gradient(sig[p], clip.dt))
    rep = {}
    for name, a in out.items():
        a_s = smooth(a, 1)
        ref = np.percentile(a_s, 90) + 1e-9
        idx = [i for i in find_peaks(a_s, 0.0) if a_s[i] > factor * ref]
        # DISCONTINUITE vs MOUVEMENT RAPIDE VOULU : une cassure de vitesse
        # donne un pic d'acceleration de 1-2 echantillons ; un geste vif
        # mais lisse (lancer, ouverture, coup d'oeil) donne une bosse
        # large. Largeur a mi-hauteur <= max_width_s -> "pop".
        pops, fast = [], []
        for i in idx:
            half = a_s[i] / 2.0
            l = i
            while l > 0 and a_s[l - 1] >= half:
                l -= 1
            r = i
            while r < len(a_s) - 1 and a_s[r + 1] >= half:
                r += 1
            width = (r - l + 1) * clip.dt
            (pops if width <= max_width_s else fast).append((round(float(clip.t[i]), 3), round(width * 1000)))
        rep[name] = {"pops": pops, "fast_moves": fast[:8], "worst_ratio": round(float(a_s.max() / ref), 2)}
    return rep


# ---------------------------------------------------------------------
# 7. Holds morts
def frozen_fraction(clip, sig, ang_eps=3.0, lin_eps=0.05, windows=None):
    mask = _window_mask(clip, windows)
    still = np.ones(len(clip), dtype=bool)
    for p, s in sig.items():
        eps = lin_eps if p == "root" else ang_eps
        still &= smooth(s, 3) < eps
    return round(float(np.mean(still[mask])), 3)


# ---------------------------------------------------------------------
TARGETS = {
    # (description, fonction de verdict sur la valeur) -- voir README
    # ATTENTION (2026-09-24) : seuils NON calibres, ecrits pour la cinematique
    # du trou noir. Le corpus pro (build_corpus.py) les contredit pour le
    # combat de jeu : tete synchrone ou en avance du torse, torse et tete sur
    # un axe dominant (planarite ~0,96), pics souvent synchrones. Pour une
    # categorie du corpus, utiliser calibrated_verdict().
    "overlap_sync_fraction_max": 0.35,   # au plus ~1/3 des pics enfants pile synchrones du parent
    "overlap_head_lag_frames": (1.0, 4.0),
    "overlap_limb_lag_frames": (1.0, 6.0),
    "stop_clustered_fraction_max": 0.30,
    "mirror_near_fraction_max": 0.50,    # pas plus de la moitie du temps en miroir exact
    "lr_speed_corr_max": 0.90,
    "planarity_max": 0.85,               # colonne : au moins ~15 % de l'energie hors de l'axe principal
    "loop_dominant_freq_share_max": 0.80,
    "loop_interval_cv_min": 0.06,
    "skate_max_studs": 0.10,
    "balance_outside_fraction_max": 0.10,
    "frozen_fraction_max": 0.05,
}


def verdict(report):
    """Liste de (metrique, valeur, cible, ok) -- lisible, jamais un score
    unique opaque : chaque ligne dit QUEL principe est viole et ou."""
    T = TARGETS
    rows = []
    for k, v in report["overlap"].items():
        if v.get("n", 0) == 0:
            continue
        child = k.split(" <- ")[0]
        rows.append((f"overlap sync {k}", v["sync_fraction"], f"<= {T['overlap_sync_fraction_max']}",
                     v["sync_fraction"] <= T["overlap_sync_fraction_max"]))
        lo, hi = T["overlap_head_lag_frames"] if child == "Head" else T["overlap_limb_lag_frames"]
        if child != "Torso":
            rows.append((f"overlap retard median {k}", v["median_frames"], f"[{lo}, {hi}] frames",
                         lo <= v["median_frames"] <= hi))
    sc = report["stop_clusters"]["clustered_fraction"]
    if sc is not None:
        rows.append(("arrets simultanes", sc, f"<= {T['stop_clustered_fraction_max']}", sc <= T["stop_clustered_fraction_max"]))
    for k, v in report["symmetry"].items():
        rows.append((f"miroir quasi exact {k}", v["mirror_near_fraction"], f"<= {T['mirror_near_fraction_max']}",
                     v["mirror_near_fraction"] <= T["mirror_near_fraction_max"]))
        rows.append((f"correlation vitesses G/D {k}", v["speed_corr"], f"<= {T['lr_speed_corr_max']}",
                     v["speed_corr"] <= T["lr_speed_corr_max"]))
    for k, v in report["planarity"].items():
        if v and v.get("dominant_axis_share") is not None:
            rows.append((f"planarite {k}", v["dominant_axis_share"], f"<= {T['planarity_max']}",
                         v["dominant_axis_share"] <= T["planarity_max"]))
    for wname, w in report["loops"].items():
        if not w:
            continue
        for sname, e in w.items():
            if "dominant_freq_share" in e:
                rows.append((f"boucle {wname} {sname} purete freq", e["dominant_freq_share"],
                             f"<= {T['loop_dominant_freq_share_max']}",
                             e["dominant_freq_share"] <= T["loop_dominant_freq_share_max"]))
            if "interval_cv" in e:
                rows.append((f"boucle {wname} {sname} CV intervalles", e["interval_cv"],
                             f">= {T['loop_interval_cv_min']}", e["interval_cv"] >= T["loop_interval_cv_min"]))
    for f, v in report["contacts"].items():
        rows.append((f"glissement pied {f}", v["worst_skate_studs"], f"<= {T['skate_max_studs']}",
                     v["worst_skate_studs"] <= T["skate_max_studs"]))
    snaps = report.get("intended_snaps") or []

    def _declared(t):
        return any(a <= t <= b for a, b in snaps)
    n_pops = sum(1 for v in report.get("pops", {}).values() for (t, _) in v["pops"] if not _declared(t))
    rows.append(("discontinuites de vitesse hors snaps declares", n_pops, "== 0", n_pops == 0))
    bal = report.get("balance", {}).get("outside_fraction")
    if bal is not None:
        rows.append(("desequilibre (CdM hors appui)", bal, f"<= {T['balance_outside_fraction_max']}",
                     bal <= T["balance_outside_fraction_max"]))
    rows.append(("holds morts", report["frozen_fraction"], f"<= {T['frozen_fraction_max']}",
                 report["frozen_fraction"] <= T["frozen_fraction_max"]))
    return rows


def audit(samples, rig, loop_windows=None, grounded_windows=None, free_leg_windows=None, intended_snaps=None):
    """intended_snaps : fenetres (t0, t1) ou l'animateur DECLARE un snap
    voulu (impact, explosion en 1-2 frames) -- les discontinuites qui y
    tombent sont rapportees mais ne comptent pas comme defaut ; toute
    autre discontinuite est un defaut."""
    """Point d'entree. loop_windows : dict nom -> (t0, t1) des cycles
    d'attente/vol a examiner. grounded_windows : fenetres ou les pieds sont
    censes etre au sol (restreint la mesure de glissement -- les contacts
    detectes hors de ces fenetres sont quand meme rapportes)."""
    clip = SampledClip(samples, rig)
    legs = [p for p in ("Right Leg", "Left Leg") if p in clip.parts]
    cw = {p: free_leg_windows for p in legs} if free_leg_windows else None
    ov, sig = overlap_report(clip, child_windows=cw)
    limbs = [p for p in clip.parts if p != rig.root]
    report = {
        "duration_s": round(float(clip.t[-1] - clip.t[0]), 3),
        "sample_hz": round(clip.hz, 2),
        "overlap": ov,
        "stop_clusters": stop_clusters(clip, sig, limbs),
        "symmetry": symmetry_report(clip, sig, pair_windows=({"Right Leg": free_leg_windows}
                                                             if free_leg_windows else None)),
        "planarity": {p: planarity(clip, p) for p in limbs if p in ("Torso", "Head")},
        "loops": {name: loop_regularity(clip, sig, w) for name, w in (loop_windows or {}).items()},
        "contacts": contact_report(clip),
        "balance": balance_report(clip),
        "pops": pops_report(clip, sig),
        "frozen_fraction": frozen_fraction(clip, sig),
        "intended_snaps": [list(w) for w in (intended_snaps or [])],
    }
    report["verdict"] = [
        {"metric": m, "value": v, "target": tgt, "ok": bool(ok)} for (m, v, tgt, ok) in verdict(report)
    ]
    report["score"] = {"ok": sum(1 for r in report["verdict"] if r["ok"]), "total": len(report["verdict"])}
    return report, clip, sig


def format_report(report):
    lines = [f"Audit mouvement -- {report['duration_s']}s @ {report['sample_hz']} Hz "
             f"-- {report['score']['ok']}/{report['score']['total']} criteres OK"]
    for r in report["verdict"]:
        mark = "OK " if r["ok"] else "XX "
        lines.append(f"  {mark} {r['metric']:<52s} {str(r['value']):>8s}   cible {r['target']}")
    return "\n".join(lines)


def save_json(report, path):
    with open(path, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------
# Verdict CALIBRE par categorie (corpus/categories.json, build_corpus.py)

def calibrated_verdict(report_or_values, category, stats=None, slack=0.1):
    """Compare chaque mesure a la plage [min, max] des animations PRO de la
    meme categorie, elargie de `slack` x |mediane|. Remplace les seuils
    fixes de TARGETS pour toute categorie du corpus : le 2026-09-24, les 19
    animations du pack premium ont echoue a TARGETS (7 a 14 criteres sur 21-22),
    preuve que ces seuils, ecrits pour une cinematique « organique »,
    ne valent pas pour du combat de jeu. Retourne [(mesure, valeur, plage,
    statut)] avec statut "dans_la_plage" / "hors_plage" / "fragile" (moins
    de taxonomy.MIN_EXAMPLES exemples)."""
    import json
    import os
    if stats is None:
        stats = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "corpus", "categories.json")))
    cat = stats.get(category)
    if cat is None:
        return [("categorie", category, "absente du corpus", "fragile")]
    if isinstance(report_or_values, dict) and "verdict" in report_or_values:
        values = {"audit." + r["metric"]: r["value"] for r in report_or_values["verdict"]}
    else:
        values = report_or_values
    rows = []
    for k, v in values.items():
        ref = cat["mesures"].get(k)
        if ref is None or not isinstance(v, (int, float)):
            continue
        pad = slack * abs(ref["mediane"])
        lo, hi = ref["min"] - pad, ref["max"] + pad
        status = "fragile" if cat["fragile"] else ("dans_la_plage" if lo <= v <= hi else "hors_plage")
        rows.append((k, v, (round(lo, 3), round(hi, 3), ref["mediane"]), status))
    return rows
