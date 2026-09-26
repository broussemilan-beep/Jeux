"""
Piste 1 -- exageration algorithmique post-hoc, appliquee CANAL PAR CANAL
sur les courbes d'angle Motor6D deja produites (cycle 5).

Deux filtres, cascadables, tous deux issus de SIGGRAPH 2006 :

1. Cartoon Animation Filter (Wang, Drucker, Agrawala, Cohen) :
       x*(t) = x(t) - k . G(x''(t))
   soit : soustraire une version lissee (convolution gaussienne) de
   l'acceleration du signal. Le signe fait tout le travail -- quand le
   mouvement ACCELERE (x'' > 0, debut de geste), on soustrait du positif,
   donc la courbe part LEGEREMENT A L'ENVERS avant de partir :
   anticipation. Quand il DECELERE (x'' < 0, fin de geste), on soustrait
   du negatif, donc la courbe DEPASSE la pose cible avant d'y revenir :
   follow-through / overshoot. Aucune reconstruction de mouvement, aucune
   hypothese sur le squelette : le filtre ne voit qu'un signal scalaire,
   donc il est nativement compatible R6 (on l'applique 3 fois par
   Motor6D, une par axe d'Euler).

   Cas particulier utile ici : les segments du cycle 5 sont RECTILIGNES
   (tangentes VECTOR), donc x'' est un train d'impulsions situees
   exactement aux keyframes. La gaussienne transforme chaque impulsion en
   un lobe lisse centre sur la keyframe -- anticipation avant la pose et
   depassement apres, en un seul lobe symetrique par pose. C'est
   exactement l'effet recherche, et c'est pour cela que le filtre se
   marie bien avec des segments lineaires plutot qu'avec des tangentes
   deja adoucies.

2. Slow In / Slow Out (Kwon & van de Panne) : reparametrage TEMPOREL qui
   concentre le mouvement autour des poses cles (approche et depart
   ralentis). Implemente ici comme un time-warp par segment de keyframes,
   d'intensite alpha : u' = (1-alpha).u + alpha.smoothstep(u). A alpha=0
   on retrouve exactement le cycle 5 ; a alpha=1 la vitesse s'annule a
   chaque pose. Ce filtre ne change AUCUNE valeur de pose -- seulement la
   distribution du temps entre elles.

Ordre de cascade retenu : SISO d'abord (il cree les accelerations en
creusant les ease in/out), Cartoon ensuite (il exagere ces accelerations).
L'inverse marche aussi mais donne moins de matiere au second filtre.

Garde-fou : le filtre est FONDU A ZERO (taper) sur les premieres et
dernieres fractions de seconde, pour que l'animation commence et finisse
exactement sur la pose neutre -- sinon une anticipation ajoutee a t=0
casserait le blend d'entree cote Roblox et ferait echouer le check
structurel neutral_forward_rest_at_start_and_end.
"""
import numpy as np


def _gaussian_kernel(sigma_samples, truncate=4.0):
    radius = max(1, int(truncate * sigma_samples + 0.5))
    x = np.arange(-radius, radius + 1, dtype=float)
    k = np.exp(-(x ** 2) / (2.0 * sigma_samples ** 2))
    return k / k.sum()


def _smooth(signal, sigma_samples):
    kernel = _gaussian_kernel(sigma_samples)
    pad = len(kernel) // 2
    padded = np.pad(signal, pad, mode="edge")
    return np.convolve(padded, kernel, mode="valid")


def _taper(n, dt, taper_s):
    """Fenetre 0 -> 1 -> 0 (cosinus), pour annuler l'effet du filtre aux
    deux extremites de l'animation."""
    w = np.ones(n)
    ramp = max(1, int(round(taper_s / dt)))
    if 2 * ramp >= n:
        ramp = max(1, n // 4)
    ease = 0.5 - 0.5 * np.cos(np.linspace(0.0, np.pi, ramp))
    w[:ramp] = ease
    w[-ramp:] = ease[::-1]
    return w


def cartoon_filter(signal, dt, k_gain, sigma_s, taper_s=0.08):
    """x*(t) = x(t) - k . G(x''(t)). k_gain est en s^2 (il multiplie une
    acceleration en deg/s^2 pour produire des degres)."""
    x = np.asarray(signal, dtype=float)
    if len(x) < 5 or k_gain == 0.0:
        return x.copy(), np.zeros_like(x)
    vel = np.gradient(x, dt)
    acc = np.gradient(vel, dt)
    sigma_samples = max(0.75, sigma_s / dt)
    delta = -k_gain * _smooth(acc, sigma_samples)
    delta *= _taper(len(x), dt, taper_s)
    return x + delta, delta


def siso_retime(times, values, keyframe_times, alpha):
    """Re-echantillonne values(times) a des temps deformes par segment de
    keyframes : u' = (1-alpha).u + alpha.smoothstep(u). Ne modifie pas les
    valeurs aux keyframes, seulement le rythme entre elles."""
    t = np.asarray(times, dtype=float)
    v = np.asarray(values, dtype=float)
    if alpha == 0.0:
        return v.copy()
    kts = np.asarray(sorted(keyframe_times), dtype=float)
    idx = np.clip(np.searchsorted(kts, t, side="right") - 1, 0, len(kts) - 2)
    t0 = kts[idx]
    t1 = kts[idx + 1]
    span = np.where(t1 > t0, t1 - t0, 1.0)
    u = np.clip((t - t0) / span, 0.0, 1.0)
    smooth_u = 3.0 * u ** 2 - 2.0 * u ** 3
    u2 = (1.0 - alpha) * u + alpha * smooth_u
    t_warp = t0 + u2 * span
    return np.interp(t_warp, t, v)


def apply_to_samples(samples, sample_hz, keyframe_times, k_gain, sigma_s,
                     alpha=0.0, taper_s=0.08, filter_root_position=True):
    """Applique SISO puis le Cartoon Filter a TOUS les canaux scalaires :
    les 3 angles d'Euler de chaque part, et (optionnellement) les 3
    composantes de position du HumanoidRootPart -- la seule part autorisee
    a translater sur ce rig, donc le seul canal de position filtre
    (filtrer une position de membre violerait la contrainte R6 de segment
    rigide sans translation interne).

    samples : dict part -> [(t, (rx,ry,rz), local_pos, world_pos), ...]
    Retourne (local_samples_filtres, deltas) au format attendu par
    anim_engine._world_positions, deltas gardant la contribution pure du
    filtre par part/canal (pour la mesure de reponse)."""
    dt = 1.0 / sample_hz
    parts = list(samples.keys())
    times = np.array([s[0] for s in samples[parts[0]]], dtype=float)

    filtered = {}
    deltas = {}
    for part in parts:
        rot = np.array([s[1] for s in samples[part]], dtype=float)  # (n,3)
        pos = np.array([s[2] for s in samples[part]], dtype=float)  # (n,3)

        rot_out = np.empty_like(rot)
        rot_delta = np.zeros_like(rot)
        for axis in range(3):
            channel = siso_retime(times, rot[:, axis], keyframe_times, alpha)
            filt, delta = cartoon_filter(channel, dt, k_gain, sigma_s, taper_s)
            rot_out[:, axis] = filt
            # delta mesure par rapport au signal ORIGINAL (avant SISO
            # aussi), c'est la contribution totale du post-traitement.
            rot_delta[:, axis] = filt - rot[:, axis]

        pos_out = pos.copy()
        if filter_root_position and part == "HumanoidRootPart":
            for axis in range(3):
                channel = siso_retime(times, pos[:, axis], keyframe_times, alpha)
                filt, _ = cartoon_filter(channel, dt, k_gain, sigma_s, taper_s)
                pos_out[:, axis] = filt

        filtered[part] = [
            (float(times[i]), tuple(rot_out[i]), tuple(pos_out[i]))
            for i in range(len(times))
        ]
        deltas[part] = rot_delta

    return filtered, deltas
