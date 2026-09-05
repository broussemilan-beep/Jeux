"""
Calcule la trajectoire MONDE de la roche (position + angle de rotation
autour d'un axe de tumbling, par echantillon) pendant toute la scene --
meme principe que r6_divine_orb/scripts/orb_track.py : ce n'est PAS
anime via des Motor6D (la roche n'est pas un membre du rig), la
trajectoire est SCRIPTEE (des points choisis pour la lecture, pas
derives d'une simulation physique -- ce depot n'a pas de moteur physique,
voir la note de orb_track.py sur ce choix).

Quatre phases, exactement les 4 phases de la demande utilisateur :
  1. t < STRIKE_T             : "repos" -- la roche est posee devant le
     personnage (position fixe, voir choreography.KICK_CONTACT_POINT).
  2. STRIKE_T..FOLLOWUP_STRIKE_T : "lancee" -- propulsee vers le CENTRE
     calcule (choreography.FOLLOWUP_ROCK_CENTER) tel que le point EXACT
     ou le poing de la frappe de suivi va la toucher
     (FOLLOWUP_CONTACT_POINT, mesure par cinematique directe, pas choisi
     a l'oeil) tombe sur SA SURFACE, jamais sur son centre -- arc vers
     le haut (un objet lance, pas une ligne droite), rotation qui
     s'accelere.
  3. FOLLOWUP_STRIKE_T..IMPACT_T : "redirigee" -- la frappe de suivi la
     renvoie plus fort et plus plat vers WORLD_TARGET_POS (un point
     choisi, loin -- voir la note gameplay : "la competence doit rester
     fonctionnelle sans cible, la roche poursuit sa trajectoire et
     termine par un impact environnemental" -- ce point represente ce
     mur/sol lointain, pas un adversaire precis).
  4. t >= IMPACT_T            : "impact" -- plus de position utile, le
     lecteur bascule sur les VFX d'impact a cet instant.
"""
import json

import numpy as np

from choreography import (STRIKE_T, FOLLOWUP_STRIKE_T, ROCK_X0, ROCK_Z0, ROCK_REST_Y,
                           ROCK_RADIUS, FOLLOWUP_CONTACT_POINT, FOLLOWUP_ROCK_CENTER, TOTAL_DURATION)

SAMPLE_HZ = 30

REST_POS = np.array([ROCK_X0, ROCK_REST_Y, ROCK_Z0])

# -- vol redirige, apres la frappe de suivi -- but choisi (pas mesure
# sur un adversaire) : loin devant et legerement de cote, au niveau du
# sol -- "un mur/le sol lointain", pas une cible. La competence reste
# fonctionnelle sans adversaire touche : voir docstring de module.
WORLD_TARGET_POS = np.array([3.5, 0.4, -34.0])

REDIRECT_FLIGHT_S = 1.35   # duree du deuxieme segment, choisie pour une trajectoire lisible, pas mesuree
IMPACT_T = FOLLOWUP_STRIKE_T + REDIRECT_FLIGHT_S


def _ease_out(f):
    """Depart rapide (le lacher d'un coup de pied est un SNAP, pas une
    acceleration progressive), ralentit ensuite -- inverse de l'ease-in
    utilise par orb_track.py pour une charge qui grossit."""
    return 1.0 - (1.0 - f) * (1.0 - f)


def rock_position(t):
    """Position MONDE (np.array) + angle de spin (deg, autour d'un axe
    tumbling fixe) + phase, pour un instant t. Utilise directement par
    calibrate.py (verification des raccords) et par dump_scene_data.py
    (echantillonnage pour le lecteur)."""
    if t < STRIKE_T:
        return REST_POS.copy(), 0.0, "repos"
    if t < FOLLOWUP_STRIKE_T:
        frac = (t - STRIKE_T) / (FOLLOWUP_STRIKE_T - STRIKE_T)
        f = _ease_out(min(1.0, frac))
        # -- cible : le CENTRE de la roche tel que son point de contact
        # avec le poing (FOLLOWUP_CONTACT_POINT) tombe sur sa surface,
        # jamais le point de contact lui-meme (voir choreography.
        # sphere_center_for_surface_contact_3d).
        base = REST_POS + (FOLLOWUP_ROCK_CENTER - REST_POS) * f
        arc = np.array([0.0, 1.4 * np.sin(np.pi * f), 0.0])   # lancee vers le haut par le coup de pied
        spin = 260.0 * f   # tumbling rapide -- un coup de pied, pas un lancer soigne
        return base + arc, spin, "lancee"
    if t < IMPACT_T:
        frac = (t - FOLLOWUP_STRIKE_T) / (IMPACT_T - FOLLOWUP_STRIKE_T)
        f = _ease_out(min(1.0, frac))
        base = FOLLOWUP_ROCK_CENTER + (WORLD_TARGET_POS - FOLLOWUP_ROCK_CENTER) * f
        arc = np.array([0.0, 2.2 * np.sin(np.pi * f * 0.85), 0.0])  # trajectoire plus plate/rapide que le premier segment -- frappee plus fort
        spin = 260.0 + 520.0 * f
        return base + arc, spin, "redirigee"
    return None, 0.0, "impact"


def main():
    n = int(round(IMPACT_T * SAMPLE_HZ)) + 1
    track = []
    for i in range(n):
        t = i / SAMPLE_HZ
        pos, spin, phase = rock_position(t)
        track.append({
            "t": round(t, 4), "phase": phase,
            "pos": [round(float(v), 4) for v in pos] if pos is not None else None,
            "spin_deg": round(float(spin), 2),
        })

    out = {
        "sample_hz": SAMPLE_HZ,
        "rock_radius": float(ROCK_RADIUS),
        "strike_t": STRIKE_T,
        "followup_strike_t": FOLLOWUP_STRIKE_T,
        "impact_t": IMPACT_T,
        "char_duration": TOTAL_DURATION,
        "world_target_pos": [float(v) for v in WORLD_TARGET_POS],
        "rest_pos": [float(v) for v in REST_POS],
        "followup_contact_point": [float(v) for v in FOLLOWUP_CONTACT_POINT],
        "note": ("Trajectoire monde de la roche. A appliquer via un script "
                 "(CFrame direct), PAS via l'Animator -- meme principe que "
                 "orb_track.py de r6_divine_orb."),
        "track": track,
    }
    path = "../output/rock_track.json"
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print(f"ecrit {path}, {len(track)} echantillons, impact a t={IMPACT_T:.3f}s")

    # -- verification : pas de saut de position aux deux raccords de
    # phase (repos->lancee a STRIKE_T, lancee->redirigee a
    # FOLLOWUP_STRIKE_T) -- la position doit coincider exactement des
    # deux cotes de chaque frontiere.
    for label, t_boundary in (("repos->lancee", STRIKE_T), ("lancee->redirigee", FOLLOWUP_STRIKE_T)):
        i = round(t_boundary * SAMPLE_HZ)
        p_before = np.array(track[i - 1]["pos"])
        p_after = np.array(track[i]["pos"])
        gap = np.linalg.norm(p_after - p_before)
        print(f"  raccord {label} (t={t_boundary:.3f}s) : saut={gap:.4f} stud")


if __name__ == "__main__":
    main()
