"""
VFX du trou noir -- fragments de sol arraches, disque d'accretion, coeur
noir, trainees radiales, vignette. Rien de tout ça n'est un os du rig
(contrairement a r6_solar_smite ou les noyaux etaient attaches aux
mains) : c'est un decor procedural independant, synchronise sur
`choreography.VFX_EVENTS`/`choreography.BLACK_HOLE_CENTER`, jamais
improvise cote viewer.

Base sur l'analyse frame-par-frame de la reference video envoyee par
l'utilisateur ("Black Hole Ability", voir choreography.py + README) :
  - Les fragments sont ARRACHES du sol (pas nes en l'air) : ils partent
    d'une position au sol, dispersee en anneau autour du personnage
    (frame ~5-6.25s de la reference), montent, puis ORBITENT en spirale
    VERS le centre -- pas une simple ligne droite (frame ~7.5s : l'amas
    tourne visiblement sur lui-meme).
  - Le disque d'accretion + le coeur noir apparaissent PENDANT que les
    fragments sont deja en train de converger, pas avant (chevauchement
    volontaire, voir VFX_EVENTS["disk_form"]).
  - Trainees blanches en spirale (motion blur radial) qui semblent
    "tomber" vers l'anneau (frame ~9-11s) -- vocabulaire visuel neuf
    pour ce depot (distinct des particules aspirees en ligne droite de
    r6_solar_smite : ici c'est une VRAIE spirale, angle + rayon changent
    tous les deux).
  - Fond de scene qui s'assombrit fortement des la formation du disque
    (vignette quasi totale au climax) -- PAS une opacite plein ecran qui
    cache l'action (voir experiments/_shared/vfx_craft_checklist.md) :
    seul le FOND s'assombrit, le disque/coeur/personnage restent lisibles
    par contraste, exactement l'inverse d'un voile qui masquerait tout.
"""
import math
import random

import numpy as np

from choreography import (BLACK_HOLE_CENTER, VFX_EVENTS, RISE_T, LAND_T)

# -- couleurs (RGB 0-255) -- disque chaud blanc-or, coeur pur noir (PAS
# un simple halo sombre -- occulteur veritable dans le viewer), distinct
# de la palette CORE_COLOR_HOT/CORE_COLOR_RIM (blanc-jaune chaleur
# solaire) de r6_solar_smite : ici le rim est plus dore/ambre, plus
# proche de l'or fondu que du soleil blanc.
DISK_COLOR_HOT = (255, 246, 214)
DISK_COLOR_RIM = (255, 196, 64)
CORE_COLOR = (4, 3, 2)          # quasi-noir pur, jamais totalement (0,0,0) pour rester dans une palette de rendu HDR-friendly
STREAK_COLOR = (255, 252, 240)

N_DEBRIS = 16
N_STREAKS = 22

_rng = random.Random(20260923)  # seed fixe -- reproductible (meme discipline que rock_track/orb_track/solar_track)

# =======================================================================
# Fragments de sol -- points de depart dissemines en anneau autour du
# personnage (pas un cercle parfait : rayon + angle randomises, seed
# fixe, pour lire comme un VRAI sol dechire, pas un pattern regulier).
# =======================================================================
_DEBRIS_SPAWN = []
_DEBRIS_ORBIT_R = []
_DEBRIS_ORBIT_Y = []
_DEBRIS_ANGLE0 = []
_DEBRIS_STAGGER = []
_DEBRIS_SIZE = []
for _i in range(N_DEBRIS):
    ang = _rng.uniform(0, 2 * math.pi)
    rad = _rng.uniform(2.4, 8.0)
    _DEBRIS_SPAWN.append(np.array([rad * math.cos(ang), 0.0, rad * math.sin(ang)]))
    _DEBRIS_ORBIT_R.append(_rng.uniform(2.6, 5.2))
    _DEBRIS_ORBIT_Y.append(_rng.uniform(-1.0, 1.6))
    _DEBRIS_ANGLE0.append(_rng.uniform(0, 2 * math.pi))
    _DEBRIS_STAGGER.append(_rng.uniform(0.0, 1.0))
    _DEBRIS_SIZE.append(_rng.uniform(0.35, 0.95))

CONSUME_RADIUS = 0.35   # rayon d'orbite en dessous duquel un fragment est considere "avale" (disparait)


def _ease_out(f):
    return 1.0 - (1.0 - f) ** 2


def _ease_in(f):
    return f * f


def _clamp01(f):
    return max(0.0, min(1.0, f))


def debris_state(i, t):
    """Retourne (position np.array, scale 0..1, visible bool) pour le
    fragment i a l'instant t. Trois etapes, chacune bornee par les memes
    fenetres que VFX_EVENTS (rien de reinvente au niveau du timing) :
      1. immobile au sol avant son tour de depart (echelonne -- STAGGER).
      2. lancement : sol -> point d'orbite (ease-out, "arrache").
      3. orbite en spirale : angle tourne, rayon retrecit progressivement
         (vitesse angulaire qui AUGMENTE en approchant le centre --
         orbite qui se resserre, pas une vitesse constante) jusqu'a
         CONSUME_RADIUS -> disparait (scale -> 0)."""
    launch = VFX_EVENTS["debris_launch"]
    gather = VFX_EVENTS["debris_gather"]
    stagger = _DEBRIS_STAGGER[i]
    t_launch0 = launch["t0"] + stagger * 0.5 * (launch["t1"] - launch["t0"])
    t_launch1 = t_launch0 + (launch["t1"] - launch["t0"]) * 0.5
    t_gather1 = gather["t1"] - (1.0 - stagger) * 0.6  # certains fragments sont avales plus tot que d'autres -- pas tous pile a HOLD_END_T

    spawn = _DEBRIS_SPAWN[i]
    orbit_r0 = _DEBRIS_ORBIT_R[i]
    orbit_y = _DEBRIS_ORBIT_Y[i]
    angle0 = _DEBRIS_ANGLE0[i]
    size = _DEBRIS_SIZE[i]

    if t < t_launch0:
        return spawn.copy(), size, True

    orbit_point0 = BLACK_HOLE_CENTER + np.array([orbit_r0 * math.cos(angle0), orbit_y, orbit_r0 * math.sin(angle0)])

    if t < t_launch1:
        f = _ease_out(_clamp01((t - t_launch0) / max(1e-6, t_launch1 - t_launch0)))
        pos = spawn + f * (orbit_point0 - spawn)
        return pos, size, True

    if t >= t_gather1:
        return BLACK_HOLE_CENTER.copy(), 0.0, False

    f = _ease_in(_clamp01((t - t_launch1) / max(1e-6, t_gather1 - t_launch1)))
    radius = orbit_r0 + f * (CONSUME_RADIUS - orbit_r0)
    # vitesse angulaire croissante en approchant le centre (orbite qui
    # se resserre) : integrale approximee par un terme en 1/(1-f*0.85),
    # borne (jamais de division par 0 -- f<1 strictement dans cette
    # branche).
    angle = angle0 + 5.5 * f + 3.0 * f * f
    y = orbit_y * (1.0 - 0.4 * f)  # se rapproche legerement du plan du disque en spiralant
    pos = BLACK_HOLE_CENTER + np.array([radius * math.cos(angle), y, radius * math.sin(angle)])
    scale = size * (1.0 - 0.5 * f)  # retrecit visiblement en approchant (pas juste teleporte a taille pleine jusqu'au bout)
    return pos, scale, True


def all_debris_states(t):
    return [debris_state(i, t) for i in range(N_DEBRIS)]


# =======================================================================
# Disque d'accretion + coeur noir -- grossissent pendant disk_form,
# pleine intensite pendant hold/climax, s'effondrent pendant collapse.
# =======================================================================
DISK_RADIUS_MAX = 4.6
DISK_THICKNESS = 0.55
CORE_RADIUS_MAX = 1.15


def disk_radius(t):
    form = VFX_EVENTS["disk_form"]
    collapse = VFX_EVENTS["collapse"]
    if t < form["t0"]:
        return 0.0
    if t < form["t1"]:
        f = _ease_out(_clamp01((t - form["t0"]) / (form["t1"] - form["t0"])))
        return DISK_RADIUS_MAX * f
    if t < collapse["t0"]:
        return DISK_RADIUS_MAX
    if t < collapse["t1"]:
        f = _clamp01((t - collapse["t0"]) / (collapse["t1"] - collapse["t0"]))
        return DISK_RADIUS_MAX * (1.0 - _ease_in(f))
    return 0.0


def core_radius(t):
    r = disk_radius(t)
    return CORE_RADIUS_MAX * min(1.0, r / DISK_RADIUS_MAX) if DISK_RADIUS_MAX else 0.0


def disk_opacity(t):
    """Distinct du rayon : le disque atteint son rayon max avant
    d'atteindre sa pleine opacite (il se forme "flou" puis se durcit),
    et pendant climax son opacite PULSE legerement (pas un plateau
    plat -- l'energie qui monte doit se voir)."""
    climax = VFX_EVENTS["climax"]
    r = disk_radius(t)
    if r <= 0.0:
        return 0.0
    base = min(1.0, r / DISK_RADIUS_MAX) ** 0.5
    if climax["t0"] <= t <= climax["t1"] + 0.4:
        pulse = 0.12 * math.sin((t - climax["t0"]) * 18.0)
        base = _clamp01(base + pulse)
    return base


def vignette_level(t):
    """0 = scene normale, 1 = fond quasi noir (le personnage/disque
    restent visibles par contraste -- voir docstring de module, jamais
    une opacite plein ecran qui cacherait l'action)."""
    form = VFX_EVENTS["disk_form"]
    collapse = VFX_EVENTS["collapse"]
    if t < form["t0"]:
        return 0.0
    if t < form["t1"]:
        f = _clamp01((t - form["t0"]) / (form["t1"] - form["t0"]))
        return 0.75 * _ease_out(f)
    if t < collapse["t0"]:
        return 0.75
    if t < collapse["t1"]:
        f = _clamp01((t - collapse["t0"]) / (collapse["t1"] - collapse["t0"]))
        return 0.75 * (1.0 - f) + 1.0 * _ease_in(f)  # pic bref a la toute fin (flash d'engloutissement) avant de retomber (gere cote viewer, post-collapse)
    return 0.0  # apres collapse : le viewer refait remonter la lumiere vers l'atterrissage (decision de mise en scene, voir choreography.py)


# =======================================================================
# Trainees radiales -- spiralent VERS le disque (pas depuis le centre
# vers l'exterieur comme un burst classique). Chaque trainee i a un
# rayon de depart / angle / vitesse propres (seed fixe).
# =======================================================================
_STREAK_R0 = []
_STREAK_ANGLE0 = []
_STREAK_SPEED = []
_STREAK_TILT = []
for _i in range(N_STREAKS):
    _STREAK_R0.append(_rng.uniform(3.0, 7.5))
    _STREAK_ANGLE0.append(_rng.uniform(0, 2 * math.pi))
    _STREAK_SPEED.append(_rng.uniform(0.7, 1.6))
    _STREAK_TILT.append(_rng.uniform(-0.6, 0.6))


def export_config():
    """Tout ce dont le lecteur JS a besoin pour REIMPLEMENTER exactement
    debris_state()/disk_radius()/core_radius()/disk_opacity()/
    vignette_level()/streak_state() cote JS -- valeurs STATIQUES
    (seeds/parametres), jamais une trajectoire pre-calculee frame par
    frame (meme convention que r6_solar_smite/solar_track.py : le
    lecteur recalcule la courbe lui-meme a partir des memes formules,
    il ne rejoue pas une liste figee)."""
    return {
        "n_debris": N_DEBRIS,
        "n_streaks": N_STREAKS,
        "consume_radius": CONSUME_RADIUS,
        "disk_radius_max": DISK_RADIUS_MAX,
        "disk_thickness": DISK_THICKNESS,
        "core_radius_max": CORE_RADIUS_MAX,
        "black_hole_center": [float(v) for v in BLACK_HOLE_CENTER],
        "vfx_events": VFX_EVENTS,
        "colors": {
            "disk_hot": DISK_COLOR_HOT, "disk_rim": DISK_COLOR_RIM,
            "core": CORE_COLOR, "streak": STREAK_COLOR,
        },
        "debris": [
            {
                "spawn": [float(v) for v in _DEBRIS_SPAWN[i]],
                "orbit_r": _DEBRIS_ORBIT_R[i],
                "orbit_y": _DEBRIS_ORBIT_Y[i],
                "angle0": _DEBRIS_ANGLE0[i],
                "stagger": _DEBRIS_STAGGER[i],
                "size": _DEBRIS_SIZE[i],
            }
            for i in range(N_DEBRIS)
        ],
        "streaks": [
            {
                "r0": _STREAK_R0[i], "angle0": _STREAK_ANGLE0[i],
                "speed": _STREAK_SPEED[i], "tilt": _STREAK_TILT[i],
            }
            for i in range(N_STREAKS)
        ],
    }


def streak_state(i, t):
    """Position + progression (0..1, pour l'alpha/la longueur du trait
    dans le viewer) d'une trainee, active uniquement pendant
    disk_form..collapse (elle n'a de sens qu'une fois le disque
    forme)."""
    form = VFX_EVENTS["disk_form"]
    collapse = VFX_EVENTS["collapse"]
    t0, t1 = form["t0"], collapse["t1"]
    if t < t0 or t > t1:
        return None
    speed = _STREAK_SPEED[i]
    cycle = (t - t0) * speed
    f = cycle % 1.0
    r = _STREAK_R0[i] * (1.0 - _ease_in(f))
    angle = _STREAK_ANGLE0[i] + 6.0 * f
    y = _STREAK_TILT[i] * (1.0 - f)
    pos = BLACK_HOLE_CENTER + np.array([r * math.cos(angle), y, r * math.sin(angle)])
    return pos, f
