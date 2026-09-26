"""
Verifie le placement des pieds au sol (Y=0.0 monde) pour Hero ET Rival, a
chaque instant-cle de la scene de combat -- meme methode que
r6_hit_combo/scripts/foot_check.py (copie du principe, pas du fichier :
ce prototype est independant, voir convention du depot), etendue aux
DEUX combattants actifs. Signale tout ecart au-dela de 0.3 stud (meme
seuil de tolerance documente que le combo de poing, retour "axes des
jambes") -- pas pour interdire tout ecart (certaines poses de projection/
KO l'acceptent explicitement, voir choreography.py), mais pour repondre
par la mesure, pas par l'oeil, si un pied flotte ou s'enfonce sans raison.
"""
import numpy as np

import anim_engine as ae
import choreography as bc
from r6_rig import PART_SIZES

TOLERANCE = 0.30

# -- instants ou un pied hors sol est ATTENDU (vol/projection/KO), donc
# pas signale comme anomalie -- voir la pose correspondante dans
# choreography.py pour la justification.
_HOOK_T_ABS = bc.BEAT2_START + bc.pc.HOOK_T
_CROSS_T_ABS = bc.BEAT2_START + bc.pc.CROSS_T

EXPECTED_AIRBORNE = {
    "rival": [
        # -- encaisse le cross puis le hook : whiplash + projection, memes
        # poses (CROSS_HIT_*/HOOK_HIT_*) que dans r6_hit_combo, jamais
        # verifiees cote pieds la-bas (mannequin statique, jamais scrutine
        # -- voir DAZED_GROUNDED_ROOT_Y plus haut) mais des transitoires
        # BREVES (<0.3s, hold-and-snap : seuls les HOLDS doivent etre bien
        # plantes, pas les instants de lacher/reaction).
        (round(_CROSS_T_ABS, 6), "encaisse le cross -- whiplash"),
        (round(_CROSS_T_ABS + 0.06, 6), "encaisse le cross -- overshoot"),
        (round(_CROSS_T_ABS + 0.20, 6), "encaisse le cross -- tenu bref avant le hook"),
        (round(_HOOK_T_ABS - 0.03, 6), "encaisse le cross -- tenu bref avant le hook"),
        (round(_HOOK_T_ABS, 6), "encaisse le hook -- whiplash"),
        (round(_HOOK_T_ABS + 0.08, 6), "projete par le hook -- vol (HOOK_HOP_Y)"),
        (round(_HOOK_T_ABS + 0.35, 6), "projete par le hook -- retombee"),
        (round(bc.KICK_STRIKE_T, 6), "encaisse le coup de pied -- instant d'impact"),
        (round(bc.KICK_STRIKE_T + 0.10, 6), "vol apres le coup de pied (KICK_HOP_Y)"),
        (round(bc.PILLAR_HIT_T, 6), "affaisse contre le pilier (CRUMPLE_ROOT_Y != 0)"),
        (round(bc.PILLAR_HIT_T + 0.55, 6), "affaisse contre le pilier (tenu)"),
        (round(bc.BEAT4_START, 6), "affaisse contre le pilier (debut beat4)"),
        (round(bc.FINISH_STRIKE_T, 6), "encaisse le finisher -- instant d'impact"),
        (round(bc.FINISH_STRIKE_T + 0.30, 6), "encaisse le finisher -- tenu avant l'effondrement"),
        (round(bc.FINISH_STRIKE_T + 0.60, 6), "effondre, KO (COLLAPSE_ROOT_Y != 0)"),
        (round(bc.WALK_END, 6), "effondre, KO (tenu)"),
    ],
    "hero": [
        (round(bc.KICK_WINDUP_T, 6), "chambrage du coup de pied -- jambe droite levee"),
        (round(bc.KICK_HOLD_T, 6), "chambrage tenu -- jambe droite levee"),
        (round(bc.KICK_STRIKE_T, 6), "extension du coup de pied -- jambe droite en l'air"),
    ],
}


def _world_rotations(samples, i):
    rot = {}
    root_r = ae.euler_xyz_matrix(*samples["HumanoidRootPart"][i][1])
    rot["HumanoidRootPart"] = root_r
    torso_r = root_r @ ae.euler_xyz_matrix(*samples["Torso"][i][1])
    rot["Torso"] = torso_r
    for part in samples:
        if part in ("HumanoidRootPart", "Torso"):
            continue
        rot[part] = torso_r @ ae.euler_xyz_matrix(*samples[part][i][1])
    return rot


def _foot_y(samples, part, i):
    world_pos = np.array(samples[part][i][3])
    rots = _world_rotations(samples, i)
    half = PART_SIZES[part][1] / 2.0
    tip = world_pos + rots[part] @ np.array([0.0, -half, 0.0])
    return tip[1]


def _check(label, track_fn, hz=120, t_max=None):
    keyframes, phases, preview_times, engine_opts = track_fn()
    duration = max(k["time"] for k in keyframes)
    objs = ae.build_rig()
    ae.apply_choreography(objs, keyframes, **engine_opts)
    samples = ae.sample(objs, duration_s=duration, sample_hz=hz, secondary_motion=None)

    expected = dict(EXPECTED_AIRBORNE.get(label, []))
    print(f"=== {label} : hauteur des pieds (sol = Y0.0) a chaque instant-cle ===")
    problems = []
    times = sorted(set(round(k["time"], 6) for k in keyframes))
    if t_max is not None:
        times = [t for t in times if t <= t_max + 1e-6]
    for t in times:
        i = min(round(t * hz), len(samples["Left Leg"]) - 1)
        ly = _foot_y(samples, "Left Leg", i)
        ry = _foot_y(samples, "Right Leg", i)
        root_y = samples["HumanoidRootPart"][i][2][1]
        worst = max(abs(ly), abs(ry))
        flag = ""
        if worst > TOLERANCE:
            note = expected.get(t)
            if note:
                flag = f"  (attendu : {note})"
            else:
                flag = "  <-- ANOMALIE NON EXPLIQUEE"
                problems.append((t, ly, ry))
        print(f"  t={t:7.3f}  rootY={root_y:6.3f}  LeftFootY={ly:7.3f}  RightFootY={ry:7.3f}{flag}")
    if problems:
        print(f"  >>> {len(problems)} anomalie(s) non expliquee(s) pour {label}")
    else:
        print(f"  >>> {label} : aucune anomalie de placement des pieds non expliquee")
    return problems


def main():
    # -- hero_track() ajoute throne_sequence.climb_stairs()/sit_and_crown()
    # au-dela de WALK_END : ces keyframes montent volontairement au-dessus
    # de Y=0 (marches, estrade) et sont deja verifies par le calibrate.py
    # de r6_throne_crown -- hors de portee de ce script (qui suppose un
    # sol plat Y=0), donc explicitement exclus plutot que de generer de
    # faux positifs.
    p_hero = _check("hero", bc.hero_track, t_max=bc.WALK_END)
    print()
    p_rival = _check("rival", bc.rival_track)
    total = len(p_hero) + len(p_rival)
    print(f"\nTotal anomalies non expliquees : {total}")


if __name__ == "__main__":
    main()
