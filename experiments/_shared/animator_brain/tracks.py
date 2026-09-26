"""
Pistes par articulation + decalage des cles (overlap) -- la "feuille
d'exposition" de l'animateur.

Le format d'origine des prototypes (une liste de keyframes, chacune
posant TOUT le corps au meme instant) fabrique mecaniquement le defaut le
plus visible : toutes les articulations partent, culminent et s'arretent
ensemble (mesure : audit.overlap / stop_clusters). Un animateur ne pose
jamais tout le corps a la meme frame : il decale les cles membre par
membre dans le sens de la chaine de pilotage (le bassin mene, le torse
suit, puis epaules/bras, la tete et les mains arrivent en dernier -- ou
l'inverse quand ce sont les pieds qui menent, a l'atterrissage).

  tracks = {part: [(t, (rx, ry, rz)), ...], ROOT_POS: [(t, (x, y, z)), ...]}

offset_tracks() applique des decalages en FRAMES (30 fps) par fenetre de
temps, garantit que l'ordre des cles de chaque piste est preserve (jamais
une cle qui en double une autre -- ce qui inverserait le mouvement) et
journalise chaque ajustement.
"""
ROOT_POS = "__root_pos__"
FPS = 30.0


def keyframes_to_tracks(keyframes, parts, root="HumanoidRootPart"):
    tracks = {p: [] for p in parts}
    tracks[ROOT_POS] = []
    for kf in sorted(keyframes, key=lambda k: k["time"]):
        t = kf["time"]
        for p in parts:
            tracks[p].append((t, tuple(kf.get(p, (0.0, 0.0, 0.0)))))
        tracks[ROOT_POS].append((t, tuple(kf.get("root_pos", (0.0, 0.0, 0.0)))))
    return tracks


def merge_tracks(base, extra, window=None):
    """Remplace, dans chaque piste de `base`, les cles comprises dans
    `window` (t0, t1) par celles de `extra` (utilise pour inserer un cycle
    organique genere par organic.py au milieu d'une piste posee a la main)."""
    out = {}
    for k in set(base) | set(extra):
        b = list(base.get(k, []))
        e = list(extra.get(k, []))
        if window and e:
            t0, t1 = window
            b = [kv for kv in b if not (t0 <= kv[0] <= t1)]
        out[k] = sorted(b + e, key=lambda kv: kv[0])
    return out


def offset_tracks(tracks, rules, min_gap_frames=1.0, keep_first=True, keep_last=True):
    """rules : liste de {"t0", "t1", "frames": {part: decalage}} ; une cle
    dont l'instant D'ORIGINE tombe dans [t0, t1) est decalee de
    frames[part]/30 s (positif = en retard sur le reste du corps). La
    premiere et la derniere cle de chaque piste restent ancrees (debut et
    fin de clip exacts). Retourne (nouvelles pistes, journal)."""
    gap = min_gap_frames / FPS
    out, log = {}, []
    for part, keys in tracks.items():
        if not keys:
            out[part] = []
            continue
        shifted = []
        for i, (t, v) in enumerate(keys):
            dt = 0.0
            anchored = (keep_first and i == 0) or (keep_last and i == len(keys) - 1)
            if not anchored:
                for r in rules:
                    if r["t0"] <= t < r["t1"]:
                        dt = r["frames"].get(part, 0.0) / FPS
                        break
            shifted.append([t + dt, v, t])
        # ordre preserve : chaque cle au moins `gap` apres la precedente ;
        # si impossible sans depasser la suivante, on la ramene vers son
        # instant d'origine (jamais d'inversion).
        for i in range(1, len(shifted)):
            if shifted[i][0] < shifted[i - 1][0] + gap:
                new_t = shifted[i - 1][0] + gap
                log.append(f"{part}: cle {shifted[i][2]:.3f}s repoussee {shifted[i][0]:.3f}->{new_t:.3f}")
                shifted[i][0] = new_t
        if keep_last and len(shifted) > 1 and shifted[-1][0] < shifted[-2][0] + gap:
            log.append(f"{part}: conflit en fin de piste ({shifted[-2][0]:.3f} >= {shifted[-1][0]:.3f})")
        out[part] = [(t, v) for t, v, _ in shifted]
    return out, log


def track_value(keys, t):
    """Valeur lineaire d'une piste a l'instant t (utilitaire de
    verification -- le rendu reel passe par les courbes Bezier du moteur)."""
    if t <= keys[0][0]:
        return keys[0][1]
    for (ta, va), (tb, vb) in zip(keys, keys[1:]):
        if ta <= t <= tb:
            f = (t - ta) / (tb - ta) if tb > ta else 0.0
            return tuple(a + f * (b - a) for a, b in zip(va, vb))
    return keys[-1][1]
