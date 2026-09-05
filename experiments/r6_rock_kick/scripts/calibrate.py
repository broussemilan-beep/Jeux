"""
Verifie par le calcul (pas a l'oeil) : que le coup de pied ET la frappe
de suivi touchent bien la roche a l'instant exact de leur impact, que
les deux raccords de trajectoire de la roche (rock_track.py) ne sautent
pas, que le placement des pieds reste plausible tout du long (jamais un
pied qui flotte/s'enfonce sans raison -- meme discipline que
r6_battle_throne/scripts/foot_check_battle.py), et que la structure du
rig reste rigide/finie partout.
"""
import numpy as np

import anim_engine as ae
import choreography as ch
import rock_track as rt
from r6_rig import PART_ORDER, PART_SIZES

TOLERANCE = 0.30


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


def foot_y(samples, part, i):
    return tip_world(samples, part, i, "bottom")[1]


def idx_at(t, hz=60):
    return round(t * hz)


def main():
    keyframes, phases, preview_times, engine_opts = ch.striker_track()
    duration = max(k["time"] for k in keyframes)
    objs = ae.build_rig()
    ae.apply_choreography(objs, keyframes, **engine_opts)
    samples = ae.sample(objs, duration_s=duration, sample_hz=60)

    print("=== contacts (mesures, pas devines) ===")
    i = idx_at(ch.STRIKE_T)
    foot = tip_world(samples, "Right Leg", i, "bottom")
    rock_pos, _, _ = rt.rock_position(ch.STRIKE_T)
    gap = np.linalg.norm(foot - rock_pos) - ch.ROCK_RADIUS
    print(f"  coup de pied (t={ch.STRIKE_T:.3f}s) : pied={foot.round(3).tolist()}  "
          f"centre roche={rock_pos.round(3).tolist()}  ecart a la surface={gap:.3f} stud")

    i = idx_at(ch.FOLLOWUP_STRIKE_T)
    fist = tip_world(samples, "Right Arm", i, "bottom")
    rock_pos, _, _ = rt.rock_position(ch.FOLLOWUP_STRIKE_T)
    gap = np.linalg.norm(fist - rock_pos) - ch.ROCK_RADIUS
    print(f"  frappe de suivi (t={ch.FOLLOWUP_STRIKE_T:.3f}s) : poing={fist.round(3).tolist()}  "
          f"centre roche={rock_pos.round(3).tolist()}  ecart a la surface={gap:.3f} stud")

    print("\n=== raccords de trajectoire de la roche (rock_track.py) ===")
    for label, t_boundary in (("repos->lancee", ch.STRIKE_T), ("lancee->redirigee", ch.FOLLOWUP_STRIKE_T)):
        eps = 1.0 / rt.SAMPLE_HZ / 2
        p_before, _, _ = rt.rock_position(t_boundary - eps)
        p_after, _, _ = rt.rock_position(t_boundary + eps)
        print(f"  {label} : saut={np.linalg.norm(p_after - p_before):.4f} stud")

    print("\n=== placement des pieds (sol = Y0.0), tolerance", TOLERANCE, "stud ===")
    problems = []
    for t in sorted(set(round(k["time"], 6) for k in keyframes)):
        i = min(round(t * 60), len(samples["Left Leg"]) - 1)
        ly = foot_y(samples, "Left Leg", i)
        ry = foot_y(samples, "Right Leg", i)
        worst = max(abs(ly), abs(ry))
        flag = ""
        if worst > TOLERANCE:
            # -- attendu : jambe qui frappe en l'air pendant les deux
            # coups (coup de pied ET son chambrage/suite, la jambe droite
            # ne touche jamais le sol dans ces fenetres).
            kick_window = ch.WINDUP_T - 0.01 <= t <= ch.FOLLOWTHROUGH_T + 0.01
            if kick_window and abs(ry) > TOLERANCE and abs(ly) <= TOLERANCE:
                flag = "  (attendu : jambe qui frappe en l'air)"
            else:
                flag = "  <-- ANOMALIE NON EXPLIQUEE"
                problems.append((t, ly, ry))
        print(f"  t={t:6.3f}  LeftFootY={ly:7.3f}  RightFootY={ry:7.3f}{flag}")

    print(f"\n{'aucune anomalie' if not problems else str(len(problems)) + ' anomalie(s)'} de placement des pieds non expliquee(s)")

    print("\n=== structure : rotations finies et plausibles ===")
    bad = []
    for part in PART_ORDER:
        for s in samples[part]:
            rx, ry, rz = s[1]
            if not all(np.isfinite([rx, ry, rz])):
                bad.append(f"{part} : rotation non finie")
                break
            if max(abs(rx), abs(ry), abs(rz)) > 260:
                bad.append(f"{part} : rotation hors plage plausible ({rx:.1f},{ry:.1f},{rz:.1f})")
                break
    print("  OK" if not bad else "  STRUCTURE KO : " + "; ".join(bad))

    print(f"\nDuree animation personnage : {duration:.3f}s")
    print(f"Impact final de la roche (environnemental) : t={rt.IMPACT_T:.3f}s, cible={rt.WORLD_TARGET_POS.tolist()}")


if __name__ == "__main__":
    main()
