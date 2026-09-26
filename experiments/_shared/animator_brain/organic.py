"""
Cycles organiques -- remplace les boucles metronome (un sinus pur a
periode fixe, bras gauche = -bras droit) par ce que fait un animateur a la
main sur un "moving hold" : un mouvement lent qui ne se repete jamais tout
a fait, chaque membre sur son propre rythme.

Construction (deterministe, graine fixe -- jamais d'alea non reproductible) :
  - somme de 3 sinusoides a rapports de frequence IRRATIONNELS (1, phi,
    e) : le signal ne boucle jamais exactement, mais reste lisse et borne ;
  - phases tirees d'une graine PAR MEMBRE : gauche et droite ne sont plus
    en miroir ni en phase ;
  - enveloppe (smoothstep) aux bords : le cycle part de la pose cle et y
    revient sans a-coup ;
  - cles posees aux EXTREMA du signal (la ou un animateur les poserait :
    positions extremes, jamais une grille reguliere), tangentes laissees
    au moteur (Bezier AUTO_CLAMPED -> pente nulle aux extremes).

Mesure de controle : audit.loop_regularity (purete de frequence, CV des
intervalles entre pics) -- un sinus pur donne ~0.99 de purete, un cycle
organique < 0.8.
"""
import math

import numpy as np

PHI = (1 + 5 ** 0.5) / 2
DETUNE = (1.0, PHI, math.e)
WEIGHTS = (0.62, 0.28, 0.10)


def organic_wave(t, freq, seed):
    rng = np.random.RandomState(seed)
    ph = rng.uniform(0, 2 * math.pi, len(DETUNE))
    t = np.asarray(t, dtype=float)
    return sum(w * np.sin(2 * math.pi * freq * d * t + p) for w, d, p in zip(WEIGHTS, DETUNE, ph))


def _envelope(t, t0, t1, ramp):
    t = np.asarray(t, dtype=float)
    a = np.clip((t - t0) / ramp, 0, 1) if ramp > 0 else np.ones_like(t)
    b = np.clip((t1 - t) / ramp, 0, 1) if ramp > 0 else np.ones_like(t)
    s = lambda x: x * x * (3 - 2 * x)
    return s(a) * s(b)


def organic_keys(t0, t1, base, channels, seed, ramp_s=0.3, min_gap_s=2 / 30, dense_hz=240,
                 base_end=None):
    """base : valeur (3-uplet) au debut ; base_end : valeur a la fin (par
    defaut = base) -- la derive lente entre les deux est lineaire, le cycle
    s'y superpose. channels : 3 entrees {"amp", "freq"} ou None (canal fixe).
    Retourne [(t, (a, b, c)), ...] avec des cles aux extrema."""
    base = np.asarray(base, dtype=float)
    base_end = base if base_end is None else np.asarray(base_end, dtype=float)
    n = max(8, int((t1 - t0) * dense_hz))
    ts = np.linspace(t0, t1, n)
    env = _envelope(ts, t0, t1, ramp_s)
    drift = base[None, :] + ((ts - t0) / (t1 - t0))[:, None] * (base_end - base)[None, :]
    vals = drift.copy()
    key_t = {t0, t1}
    for c, spec in enumerate(channels):
        if not spec or spec.get("amp", 0) == 0:
            continue
        w = spec["amp"] * env * organic_wave(ts - t0, spec["freq"], seed * 7 + c * 131)
        vals[:, c] += w
        dw = np.diff(w)
        for i in range(1, len(dw)):
            if dw[i - 1] * dw[i] < 0:
                key_t.add(float(ts[i]))
    ks = sorted(key_t)
    merged = [ks[0]]
    for k in ks[1:]:
        if k - merged[-1] >= min_gap_s:
            merged.append(k)
    if merged[-1] != t1:
        merged[-1] = t1
    out = []
    for k in merged:
        i = int(round((k - t0) / (t1 - t0) * (n - 1)))
        out.append((float(k), tuple(float(v) for v in vals[i])))
    return out
