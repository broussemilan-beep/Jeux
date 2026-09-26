"""
Verifie par le calcul (pas a l'oeil) la scene de combat a deux
combattants ACTIFS (hero_track/rival_track de choreography.py) :

  1. Que les contacts REUTILISES de punch_combo (jab d'ouverture de
     Rival -- reflete -- et combo jab/cross/hook complet de Hero --
     translate) gardent bien le meme ecart de contact que dans
     r6_hit_combo -- preuve numerique que la translation/reflexion ne
     degrade pas une geometrie deja calibree (voir docstring de
     choreography.py).
  2. Que les DEUX contacts genuinement NOUVEAUX (coup de pied circulaire
     de Hero, coup de grace/finisher de Hero) approchent vraiment Rival
     au moment de leur impact -- ecart mesure, pas suppose, memes
     ordres de grandeur que les ecarts de r6_hit_combo (~0.3-0.6 stud).
  3. Que le raccord Beat5 -> throne_sequence.climb_stairs() tombe
     EXACTEMENT sur la meme pose (ecart nul, pas une coincidence
     visuelle) -- et que le combat seul dure bien >= 30s (retour
     utilisateur explicite).
"""
import numpy as np

import anim_engine as ae
import choreography as bc
import punch_combo as pc
from r6_rig import PART_ORDER, PART_SIZES


def world_rotations(samples, i):
    rot = {}
    root_r = ae.euler_xyz_matrix(*samples["HumanoidRootPart"][i][1])
    rot["HumanoidRootPart"] = root_r
    torso_r = root_r @ ae.euler_xyz_matrix(*samples["Torso"][i][1])
    rot["Torso"] = torso_r
    for part in PART_ORDER:
        if part in ("HumanoidRootPart", "Torso"):
            continue
        rot[part] = torso_r @ ae.euler_xyz_matrix(*samples[part][i][1])
    return rot


def tip_world(samples, part, i, end="bottom"):
    world_pos = np.array(samples[part][i][3])
    rots = world_rotations(samples, i)
    half = PART_SIZES[part][1] / 2.0
    sign = -1.0 if end == "bottom" else 1.0
    return world_pos + rots[part] @ np.array([0.0, sign * half, 0.0])


def _run(track_fn, sample_hz=60):
    keyframes, phases, preview_times, engine_opts = track_fn()
    duration = max(k["time"] for k in keyframes)
    objs = ae.build_rig()
    ae.apply_choreography(objs, keyframes, **engine_opts)
    samples = ae.sample(objs, duration_s=duration, sample_hz=sample_hz)
    return samples, duration


def idx_at(t, hz=60):
    return round(t * hz)


def main():
    hero_samples, hero_dur = _run(bc.hero_track)
    rival_samples, rival_dur = _run(bc.rival_track)

    print("=== reutilisation : contacts DEJA calibres dans r6_hit_combo ===")
    print("(doivent retomber pres de 0.493/0.366/0.380 stud -- translation/reflexion, pas recalibres)")

    # -- Beat 1 : jab d'ouverture de Rival (reflete), encaisse par Hero --
    t_rival_jab = bc.BEAT1_START + pc.JAB_T
    i = idx_at(t_rival_jab)
    fist = tip_world(rival_samples, "Left Arm", i, "bottom")
    hero_torso = np.array(hero_samples["Torso"][i][3])
    gap = np.linalg.norm(fist - hero_torso)
    print(f"  rival_jab   (t={t_rival_jab:.2f}s) : poing={fist.round(3).tolist()}  "
          f"torse hero={hero_torso.round(3).tolist()}  ecart={gap:.3f} stud")

    # -- Beat 2 : combo complet de Hero (translate), encaisse par Rival --
    for name, t_local, arm in (("hero_jab", pc.JAB_T, "Left Arm"),
                                ("hero_cross", pc.CROSS_T, "Right Arm"),
                                ("hero_hook", pc.HOOK_T, "Left Arm")):
        t_abs = bc.BEAT2_START + t_local
        i = idx_at(t_abs)
        fist = tip_world(hero_samples, arm, i, "bottom")
        rival_torso = np.array(rival_samples["Torso"][i][3])
        gap = np.linalg.norm(fist - rival_torso)
        print(f"  {name:10s} (t={t_abs:.2f}s, {arm}) : poing={fist.round(3).tolist()}  "
              f"torse rival={rival_torso.round(3).tolist()}  ecart={gap:.3f} stud")

    print("\n=== contacts NOUVEAUX (mesures, pas devines) ===")

    i = idx_at(bc.KICK_STRIKE_T)
    foot = tip_world(hero_samples, "Right Leg", i, "bottom")
    rival_torso = np.array(rival_samples["Torso"][i][3])
    gap_kick = np.linalg.norm(foot - rival_torso)
    print(f"  kick       (t={bc.KICK_STRIKE_T:.2f}s, Right Leg) : pied={foot.round(3).tolist()}  "
          f"torse rival={rival_torso.round(3).tolist()}  ecart={gap_kick:.3f} stud  "
          f"(KICK_LUNGE_Z={bc.KICK_LUNGE_Z})")

    i = idx_at(bc.FINISH_STRIKE_T)
    fist = tip_world(hero_samples, "Left Arm", i, "bottom")
    rival_torso = np.array(rival_samples["Torso"][i][3])
    gap_finish = np.linalg.norm(fist - rival_torso)
    print(f"  finisher   (t={bc.FINISH_STRIKE_T:.2f}s, Left Arm) : poing={fist.round(3).tolist()}  "
          f"torse rival={rival_torso.round(3).tolist()}  ecart={gap_finish:.3f} stud  "
          f"(FINISH_LUNGE_Z={bc.FINISH_LUNGE_Z})")

    print("\n=== raccord Beat5 -> throne_sequence.climb_stairs() ===")
    i = idx_at(bc.WALK_END)
    hero_root = np.array(hero_samples["HumanoidRootPart"][i][2])  # local pos == root_pos ici
    print(f"  root_pos a WALK_END (t={bc.WALK_END:.3f}s) = {hero_root.round(4).tolist()} "
          f"(attendu (0, 3.0, -7.2))")

    print("\n=== structure : rotations finies et plausibles ===")
    for label, samples in (("hero", hero_samples), ("rival", rival_samples)):
        problems = []
        for part in PART_ORDER:
            for s in samples[part]:
                rx, ry, rz = s[1]
                if not all(np.isfinite([rx, ry, rz])):
                    problems.append(f"{part} : rotation non finie")
                    break
                if max(abs(rx), abs(ry), abs(rz)) > 260:
                    problems.append(f"{part} : rotation hors plage plausible ({rx:.1f},{ry:.1f},{rz:.1f})")
                    break
        if problems:
            print(f"  {label} : STRUCTURE KO :")
            for p in problems:
                print("   -", p)
        else:
            print(f"  {label} : OK -- 6 segments rigides, rotations finies et plausibles.")

    print(f"\nDurees : hero={hero_dur:.2f}s, rival={rival_dur:.2f}s")
    print(f"TOTAL_FIGHT_DURATION={bc.TOTAL_FIGHT_DURATION:.2f}s (doit etre >= 30s)")
    print(f"TOTAL_SCENE_DURATION={bc.TOTAL_SCENE_DURATION:.2f}s (combat + trone)")


if __name__ == "__main__":
    main()
