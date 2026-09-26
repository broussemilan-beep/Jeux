"""
VFX des deux noyaux solaires -- PAS un objet monde independant comme
rock_track.py/orb_track.py (il n'y a pas de projectile dans cette
competence, c'est un corps-a-corps) : les noyaux sont ATTACHES aux mains
tant que le personnage les porte (le lecteur les positionne directement
sur les world_pos deja echantillonnes de "Right Arm"/"Left Arm" par le
moteur d'animation -- inutile de dupliquer cette cinematique ici).

Ce module ne scripte QUE ce qui n'est PAS une simple attache a un os :
  1. La FUSION des deux noyaux au sommet du finisher (FIN_COIL_HOLD_T)
     jusqu'a l'impact (FIN_STRIKE_T) -- les deux mains convergent
     physiquement (l'animation elle-meme les rapproche), mais le noyau
     VISUEL doit se lire comme UNE SEULE source d'energie qui grossit,
     pas deux halos qui se chevauchent -- merged_core_position()
     interpole entre le point mesure ou les deux poings se rejoignent
     (choreography.CORE_MERGE_POINT) et le point de contact final
     mesure (choreography.FIN_CONTACT_POINT), avec la MEME courbure que
     la descente du corps (FIN_MID_F, lent puis accelere -- R1/R2, voir
     docstring de choreography.py) : le noyau ne doit jamais sembler
     "en avance" ou "en retard" sur les mains qui le portent.
  2. Le recipe des particules ASPIREES pendant la charge (R3 -- distinct
     de tout ce qui existe dans ce depot jusqu'ici, qui n'a que des
     bursts SORTANTS) : inward_particle_spawn() donne, pour une
     particule i parmi N, son rayon de depart (aleatoire, seed fixe) et
     sa position a l'instant t -- elle nait loin du noyau et converge
     vers lui, jamais l'inverse.
  3. Les parametres du burst d'impact final (rayon/duree/couleur).
"""
import math
import random

import numpy as np

from choreography import (OPEN_T, CHARGE_T, CHARGE_HOLD_T,
                           STRIKE1_T, STRIKE2_T, FIN_COIL_T, FIN_COIL_HOLD_T,
                           FIN_MID_T, FIN_STRIKE_T, FIN_MID_F,
                           CORE_SPAWN_RIGHT, CORE_SPAWN_LEFT,
                           CORE_MERGE_POINT, FIN_CONTACT_POINT)

# -- couleurs (RGB 0-255) -- coeur blanc-jaune tres chaud (pas orange
# terne) pour lire comme une concentration solaire, pas une simple
# boule de feu -- distinct de la palette ROCK_STONE/DEBRIS_STONE des
# prototypes precedents.
CORE_COLOR_HOT = (255, 244, 200)
CORE_COLOR_RIM = (255, 176, 40)
FLASH_COLOR = (255, 255, 255)

# -- rayon des noyaux individuels pendant charge/combo (grossit
# progressivement pendant CHARGE_T..CHARGE_HOLD_T, reste stable ensuite
# jusqu'a la fusion).
CORE_RADIUS_SEED = 0.05    # a CHARGE_T (a peine visible, vient de naitre)
CORE_RADIUS_GROWN = 0.55   # a CHARGE_HOLD_T (pleinement charge)

# -- rayon du noyau FUSIONNE pendant la descente finale -- plus gros que
# la somme des deux noyaux individuels (ils se renforcent, pas juste
# s'additionnent) et EXPLICITEMENT plus grand que tout ce qui existe
# dans r6_directional_punch (VFX de "Poing scintillant"-like le plus
# proche deja construit dans ce depot -- voir README "Recherche").
MERGED_RADIUS_COIL = 0.85
MERGED_RADIUS_STRIKE = 1.35

# -- burst d'impact final.
IMPACT_FLASH_S = 0.10
IMPACT_SHOCKWAVE_S = 0.55
IMPACT_MAX_RADIUS = 9.0


def _ease_in(f):
    return f * f


def core_radius(t):
    """Rayon d'un noyau INDIVIDUEL (avant fusion) a l'instant t -- None
    avant CHARGE_T (le noyau n'existe pas encore), grossit jusqu'a
    CHARGE_HOLD_T puis reste stable jusqu'a FIN_COIL_T (porte tel quel
    pendant tout le combo -- "les mains restent chargees" est plus
    lisible qu'un noyau qui semble s'eteindre entre 2 coups)."""
    if t < CHARGE_T:
        return None
    if t < CHARGE_HOLD_T:
        f = (t - CHARGE_T) / (CHARGE_HOLD_T - CHARGE_T)
        return CORE_RADIUS_SEED + (CORE_RADIUS_GROWN - CORE_RADIUS_SEED) * _ease_in(min(1.0, f))
    if t < FIN_COIL_T:
        return CORE_RADIUS_GROWN
    return None   # a partir de FIN_COIL_T, le noyau FUSIONNE prend le relais


def merged_core_position(t):
    """Position MONDE (np.array) du noyau FUSIONNE entre le sommet du
    coil final et l'impact -- None en dehors de cette fenetre (avant :
    2 noyaux separes sur les mains: apres : flash/burst, plus de noyau
    a suivre). Meme courbure que le corps (FIN_MID_F, voir docstring de
    module) : PAS une interpolation lineaire, le noyau doit sembler
    porte par les mains, pas animé independamment."""
    if t < FIN_COIL_T or t > FIN_STRIKE_T:
        return None, None, "absent"
    if t <= FIN_COIL_HOLD_T:
        # -- montee/hold : les 2 noyaux se rapprochent deja l'un de
        # l'autre au sommet, mais restent 2 sources distinctes jusqu'a
        # FIN_COIL_HOLD_T (la fusion visuelle commence a partir de la).
        return None, None, "distincts"
    # -- fusion + descente : meme repartition temporelle non-lineaire
    # que le corps (lent au debut, accelere vers l'impact).
    if t <= FIN_MID_T:
        frac = (t - FIN_COIL_HOLD_T) / (FIN_MID_T - FIN_COIL_HOLD_T) * FIN_MID_F
    else:
        frac = FIN_MID_F + (t - FIN_MID_T) / (FIN_STRIKE_T - FIN_MID_T) * (1.0 - FIN_MID_F)
    f = min(1.0, max(0.0, frac))
    pos = CORE_MERGE_POINT + (np.array(FIN_CONTACT_POINT) - CORE_MERGE_POINT) * f
    radius = MERGED_RADIUS_COIL + (MERGED_RADIUS_STRIKE - MERGED_RADIUS_COIL) * f
    return pos, radius, "fusion"


def inward_particle_spawn(n=24, seed=31, max_start_radius=2.2):
    """Recipe des particules ASPIREES (R3) : pour chaque particule i,
    une direction/rayon de depart ALEATOIRE (seed fixe -- voir CLAUDE.md
    sur la reproductibilite) autour du noyau, et sa fraction de vie a
    laquelle elle doit avoir atteint le centre (echelonnee -- pas toutes
    au meme instant, sinon ca lit comme un seul anneau qui se contracte
    plutot que des particules individuelles). Position relative au
    noyau (a additionner a la position MONDE du noyau, main ou fusion) :
    start(i) * (1 - ease_in(local_f)) ou local_f = clamp((t-t0)/(vie*i), 0, 1).
    """
    rng = random.Random(seed)
    particles = []
    for i in range(n):
        theta = rng.uniform(0, 2 * math.pi)
        phi = rng.uniform(0.2, math.pi - 0.2)
        r0 = rng.uniform(max_start_radius * 0.4, max_start_radius)
        start = np.array([
            r0 * math.sin(phi) * math.cos(theta),
            r0 * math.cos(phi) * 0.6,   # aplati verticalement -- lit mieux autour d'une main
            r0 * math.sin(phi) * math.sin(theta),
        ])
        phase_offset = rng.uniform(0.0, 0.6)   # echelonnement -- pas toutes synchrones
        particles.append({"start": start.tolist(), "phase_offset": round(phase_offset, 3)})
    return particles


def main():
    import json

    print("=== fenetres VFX (design, verifie par le calcul) ===")
    print(f"  ouverture       : [{OPEN_T:.3f}s .. {CHARGE_T:.3f}s] (bras s'ecartent)")
    print(f"  charge          : [{CHARGE_T:.3f}s .. {CHARGE_HOLD_T:.3f}s] (noyaux naissent, particules aspirees)")
    print(f"  combo           : coup1={STRIKE1_T:.3f}s  coup2={STRIKE2_T:.3f}s (noyaux portes, stables)")
    print(f"  fusion          : [{FIN_COIL_HOLD_T:.3f}s .. {FIN_STRIKE_T:.3f}s] (2 noyaux -> 1, meme courbure que le corps)")
    print(f"  impact          : t={FIN_STRIKE_T:.3f}s  flash={IMPACT_FLASH_S:.2f}s  onde={IMPACT_SHOCKWAVE_S:.2f}s  rayon_max={IMPACT_MAX_RADIUS}")

    # -- verification : la fusion demarre et finit exactement aux points
    # mesures par choreography.py (jamais choisis a l'oeil).
    p0, r0, ph0 = merged_core_position(FIN_COIL_HOLD_T + 0.001)
    p1, r1, ph1 = merged_core_position(FIN_STRIKE_T)
    print(f"\n  debut fusion (t~{FIN_COIL_HOLD_T:.3f}s) : pos={np.round(p0, 3).tolist()} (doit ~= CORE_MERGE_POINT={np.round(CORE_MERGE_POINT, 3).tolist()})")
    print(f"  fin fusion   (t={FIN_STRIKE_T:.3f}s) : pos={np.round(p1, 3).tolist()} (doit ~= FIN_CONTACT_POINT={np.round(np.array(FIN_CONTACT_POINT), 3).tolist()})")

    out = {
        "core_color_hot": CORE_COLOR_HOT, "core_color_rim": CORE_COLOR_RIM, "flash_color": FLASH_COLOR,
        "core_radius_seed": CORE_RADIUS_SEED, "core_radius_grown": CORE_RADIUS_GROWN,
        "merged_radius_coil": MERGED_RADIUS_COIL, "merged_radius_strike": MERGED_RADIUS_STRIKE,
        "impact_flash_s": IMPACT_FLASH_S, "impact_shockwave_s": IMPACT_SHOCKWAVE_S, "impact_max_radius": IMPACT_MAX_RADIUS,
        "core_spawn_right": [float(v) for v in CORE_SPAWN_RIGHT], "core_spawn_left": [float(v) for v in CORE_SPAWN_LEFT],
        "core_merge_point": [float(v) for v in CORE_MERGE_POINT], "fin_contact_point": [float(v) for v in FIN_CONTACT_POINT],
        "open_t": OPEN_T, "charge_t": CHARGE_T, "charge_hold_t": CHARGE_HOLD_T,
        "strike1_t": STRIKE1_T, "strike2_t": STRIKE2_T,
        "fin_coil_t": FIN_COIL_T, "fin_coil_hold_t": FIN_COIL_HOLD_T, "fin_mid_t": FIN_MID_T, "fin_strike_t": FIN_STRIKE_T,
        "inward_particles": inward_particle_spawn(),
    }
    path = "../output/solar_track.json"
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print(f"\necrit {path}")


if __name__ == "__main__":
    main()
