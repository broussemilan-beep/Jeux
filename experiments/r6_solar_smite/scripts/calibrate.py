"""
Verifie par le calcul (pas a l'oeil) : que chacune des 3 frappes
(combo_1, combo_2, finisher) touche vraiment sa cible au moment exact de
son impact, que le placement des pieds reste plausible tout du long
(jamais un pied qui flotte/s'enfonce sans raison), et que la structure
des deux rigs (attaquant + mannequin) reste rigide/finie partout --
meme discipline que r6_hit_combo/calibrate.py.
"""
import numpy as np

import anim_engine as ae
import choreography as ch
from r6_rig import PART_ORDER, PART_SIZES

TOLERANCE = 0.35


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


def _run(choreo_fn, secondary_motion, sample_hz=60):
    keyframes, phases, preview_times, engine_opts = choreo_fn()
    duration = max(k["time"] for k in keyframes)
    objs = ae.build_rig()
    ae.apply_choreography(objs, keyframes, **engine_opts)
    samples = ae.sample(objs, duration_s=duration, sample_hz=sample_hz, secondary_motion=secondary_motion)
    return samples, duration


def idx_at(t, hz=60):
    return round(t * hz)


def main():
    att_samples, att_dur = _run(ch.attacker_track, ch.ATTACKER_SECONDARY_MOTION)
    dum_samples, dum_dur = _run(ch.dummy_reaction, ch.DUMMY_SECONDARY_MOTION)

    print("=== contacts par coup (mesures, pas devines) ===")
    for name, t, arm, target_part in (
        ("combo_1", ch.STRIKE1_T, "Right Arm", "Torso"),
        ("combo_2", ch.STRIKE2_T, "Left Arm", "Torso"),
    ):
        i = idx_at(t)
        fist = tip_world(att_samples, arm, i, "bottom")
        target = np.array(dum_samples[target_part][i][3])
        gap = np.linalg.norm(fist - target)
        print(f"  {name:8s} (t={t:.3f}s, {arm}) : poing={fist.round(3).tolist()}  "
              f"{target_part} mannequin={target.round(3).tolist()}  ecart={gap:.3f} stud")

    # -- finisher : les DEUX poings, moyenne, vs la TETE du mannequin
    # (coup descendant vers la tete, pas le torse -- voir docstring de
    # choreography.dummy_reaction).
    i = idx_at(ch.FIN_STRIKE_T)
    right_fist = tip_world(att_samples, "Right Arm", i, "bottom")
    left_fist = tip_world(att_samples, "Left Arm", i, "bottom")
    fists_mid = (right_fist + left_fist) / 2.0
    dummy_head = np.array(dum_samples["Head"][i][3])
    gap = np.linalg.norm(fists_mid - dummy_head)
    print(f"  {'finisher':8s} (t={ch.FIN_STRIKE_T:.3f}s, 2 bras) : poings(milieu)={fists_mid.round(3).tolist()}  "
          f"tete mannequin={dummy_head.round(3).tolist()}  ecart={gap:.3f} stud")

    print("\n=== fenetres de hit / knockback (design intent, pas de moteur ici) ===")
    for name, w in ch.HIT_WINDOWS.items():
        print(f"  {name:8s} : [{w['t0']:.3f}s .. {w['t1']:.3f}s] ({(w['t1'] - w['t0']) * 30:.0f} frames)  knockback={w['knockback']}")

    print("\n=== placement des pieds (sol = Y0.0), tolerance", TOLERANCE, "stud ===")
    keyframes, _, _, _ = ch.attacker_track()
    problems = []
    for t in sorted(set(round(k["time"], 6) for k in keyframes)):
        i = min(round(t * 60), len(att_samples["Left Leg"]) - 1)
        ly = tip_world(att_samples, "Left Leg", i, "bottom")[1]
        ry = tip_world(att_samples, "Right Leg", i, "bottom")[1]
        worst = max(abs(ly), abs(ry))
        flag = ""
        if worst > TOLERANCE:
            # -- attendu : jambes larges/en appui pendant le finisher
            # (brace de reception du coup, jamais un pied a plat par
            # construction de la pose) -- fenetre generosement bornee.
            finisher_window = ch.FIN_COIL_T - 0.01 <= t <= ch.FIN_FOLLOWTHROUGH_T + 0.01
            if finisher_window and worst < TOLERANCE * 2.2:
                flag = "  (attendu : brace large du finisher)"
            else:
                flag = "  <-- ANOMALIE NON EXPLIQUEE"
                problems.append((t, ly, ry))
        print(f"  t={t:6.3f}  LeftFootY={ly:7.3f}  RightFootY={ry:7.3f}{flag}")

    print(f"\n{'aucune anomalie' if not problems else str(len(problems)) + ' anomalie(s)'} de placement des pieds non expliquee(s)")

    print("\n=== structure : rotations finies et plausibles ===")
    bad = []
    for label, samples in (("attaquant", att_samples), ("mannequin", dum_samples)):
        for part in PART_ORDER:
            for s in samples[part]:
                rx, ry, rz = s[1]
                if not all(np.isfinite([rx, ry, rz])):
                    bad.append(f"{label}/{part} : rotation non finie")
                    break
                if max(abs(rx), abs(ry), abs(rz)) > 260:
                    bad.append(f"{label}/{part} : rotation hors plage plausible ({rx:.1f},{ry:.1f},{rz:.1f})")
                    break
    print("  OK" if not bad else "  STRUCTURE KO : " + "; ".join(bad))

    print(f"\nDurees : attaquant={att_dur:.3f}s, mannequin={dum_dur:.3f}s (doivent etre egales)")
    print(f"Duree totale : {ch.TOTAL_DURATION:.3f}s")


if __name__ == "__main__":
    main()
