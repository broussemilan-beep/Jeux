"""
Calcule la trajectoire MONDE de la roche (position + angle de rotation
autour d'un axe de tumbling, par echantillon) pendant toute la scene --
meme principe que r6_divine_orb/scripts/orb_track.py : ce n'est PAS
anime via des Motor6D (la roche n'est pas un membre du rig), la
trajectoire est SCRIPTEE (des points choisis pour la lecture, pas
derives d'une simulation physique -- ce depot n'a pas de moteur physique,
voir la note de orb_track.py sur ce choix).

Six phases (les 4 de la demande utilisateur, plus la naissance de la
roche elle-meme -- corrigee suite au retour "le perso tape le sol...
fait ressortir une roche du sol", qui exige que la roche N'EXISTE PAS
avant l'impact du stomp, pas seulement qu'elle soit deja posee la) :
  0. t < STOMP_STRIKE_T       : "absente" -- la roche n'existe pas
     encore, rien a afficher (meme convention que orb_track.py avant
     RAISE_T : rayon/existence nulle, pas une position par defaut).
  1. STOMP_STRIKE_T..ERUPTION_END_T : "jaillissement" -- la roche sort
     du sol exactement au point d'impact du stomp
     (choreography.STOMP_POINT, mesure par cinematique directe sur le
     pied, jamais choisi a l'oeil), montee rapide avec un leger
     depassement/rebond (elle jaillit avec force, ne glisse pas
     doucement hors du sol) avant de se stabiliser posee au sol.
  2. ERUPTION_END_T..STRIKE_T : "repos" -- la roche fraichement sortie
     attend, immobile, le temps que le personnage termine son
     chambrage pour le coup de pied.
  3. STRIKE_T..FOLLOWUP_STRIKE_T : "lancee" -- propulsee vers le CENTRE
     calcule (choreography.FOLLOWUP_ROCK_CENTER) tel que le point EXACT
     ou le poing de la frappe de suivi va la toucher
     (FOLLOWUP_CONTACT_POINT, mesure par cinematique directe, pas choisi
     a l'oeil) tombe sur SA SURFACE, jamais sur son centre -- arc vers
     le haut (un objet lance, pas une ligne droite), rotation qui
     s'accelere.
  4. FOLLOWUP_STRIKE_T..IMPACT_T : "redirigee" -- la frappe de suivi la
     renvoie plus fort et plus plat vers WORLD_TARGET_POS (un point
     choisi, loin -- voir la note gameplay : "la competence doit rester
     fonctionnelle sans cible, la roche poursuit sa trajectoire et
     termine par un impact environnemental" -- ce point represente ce
     mur/sol lointain, pas un adversaire precis).
  5. t >= IMPACT_T            : "impact" -- plus de position utile, le
     lecteur bascule sur les VFX d'impact a cet instant.
"""
import json
import math

import numpy as np

from choreography import (STOMP_STRIKE_T, STRIKE_T, FOLLOWUP_STRIKE_T, ROCK_X0, ROCK_Z0, ROCK_REST_Y,
                           ROCK_RADIUS, FOLLOWUP_CONTACT_POINT, FOLLOWUP_ROCK_CENTER, TOTAL_DURATION)

SAMPLE_HZ = 30

REST_POS = np.array([ROCK_X0, ROCK_REST_Y, ROCK_Z0])

# -- duree du jaillissement : assez bref pour lire comme un eclatement
# (pas une roche qui "pousse" lentement), mais laisse le temps a un
# rebond/depassement d'etre visible avant STRIKE_T (0.55s de marge dans
# la chronologie actuelle -- voir choreography.STOMP_STRIKE_T/STRIKE_T).
ERUPTION_S = 0.40
ERUPTION_END_T = STOMP_STRIKE_T + ERUPTION_S
# -- profondeur de depart : la roche part d'assez bas sous le sol pour
# que sa remontee traverse visiblement la surface, pas un simple "pop"
# a fleur de sol.
_ERUPTION_START_Y = -ROCK_RADIUS * 0.85

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


def _ease_in(f):
    """Depart lent, accelere -- copie de orb_track.py : une croissance
    qui accelere se lit mieux qu'une vitesse constante."""
    return f * f


def rock_position(t):
    """Position MONDE (np.array ou None si la roche n'existe pas encore)
    + angle de spin (deg, autour d'un axe tumbling fixe) + phase, pour
    un instant t. Utilise directement par calibrate.py (verification
    des raccords) et par dump_scene_data.py (echantillonnage pour le
    lecteur)."""
    if t < STOMP_STRIKE_T:
        return None, 0.0, "absente"
    if t < ERUPTION_END_T:
        frac = (t - STOMP_STRIKE_T) / ERUPTION_S
        # -- jaillissement avec depassement : monte au-dela de sa
        # hauteur de repos puis retombe s'y stabiliser (amorti par
        # (1-f)) -- lit comme une roche EJECTEE avec force, pas posee
        # doucement en place.
        f = _ease_in(min(1.0, frac))
        overshoot = 0.6 * math.sin(math.pi * f) * (1.0 - f)
        y = _ERUPTION_START_Y + (ROCK_REST_Y - _ERUPTION_START_Y) * f + overshoot
        pos = np.array([ROCK_X0, y, ROCK_Z0])
        spin = 40.0 * f   # tumbling leger pendant l'ejection -- pas encore le tumbling rapide du lancer
        return pos, spin, "jaillissement"
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
        "stomp_strike_t": STOMP_STRIKE_T,
        "eruption_end_t": ERUPTION_END_T,
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

    # -- verification : la roche n'existe pas avant l'impact du stomp
    # (retour utilisateur -- elle doit "sortir du sol", pas etre deja
    # la), et son point de depart est bien au point d'impact mesure.
    i0 = round(STOMP_STRIKE_T * SAMPLE_HZ)
    print(f"  avant le stomp (t={STOMP_STRIKE_T - 1/SAMPLE_HZ:.3f}s) : pos={track[i0 - 1]['pos']} (doit etre None)")
    print(f"  au stomp (t={STOMP_STRIKE_T:.3f}s) : pos={track[i0]['pos']} (doit demarrer a X/Z=[{ROCK_X0:.3f}, {ROCK_Z0:.3f}], sous le sol en Y)")

    # -- pas de saut de position aux raccords de phase restants
    # (jaillissement->repos, repos->lancee, lancee->redirigee) -- la
    # position doit coincider exactement des deux cotes de chaque
    # frontiere.
    for label, t_boundary in (("jaillissement->repos", ERUPTION_END_T),
                               ("repos->lancee", STRIKE_T), ("lancee->redirigee", FOLLOWUP_STRIKE_T)):
        i = round(t_boundary * SAMPLE_HZ)
        p_before = np.array(track[i - 1]["pos"])
        p_after = np.array(track[i]["pos"])
        gap = np.linalg.norm(p_after - p_before)
        print(f"  raccord {label} (t={t_boundary:.3f}s) : saut={gap:.4f} stud")


if __name__ == "__main__":
    main()
