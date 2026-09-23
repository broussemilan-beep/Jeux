"""
Verifie par le calcul (pas a l'oeil) : que le placement des pieds reste
plausible AU SOL (jamais un pied qui flotte/s'enfonce sans raison) et
qu'il est bien AERIEN (jamais un pied qui traverse le sol) pendant la
levitation -- 2 modes de check distincts, voir docstring de
choreography.py sur pourquoi ce prototype en a besoin (aucun predecesseur
ne quittait le sol) -- que la structure des deux rigs reste rigide/finie
partout, et que le script VFX (black_hole_track.py) reste numeriquement
sain (pas de NaN, coeur jamais plus grand que le disque, tous les
fragments avales avant l'atterrissage) -- meme discipline que
r6_solar_smite/calibrate.py.
"""
import numpy as np

import anim_engine as ae
import choreography as ch
import black_hole_track as bh
from r6_rig import PART_ORDER, PART_SIZES

TOLERANCE = 0.05  # stud -- meme seuil resserre que r6_solar_smite (voir son README pour la justification/source)


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


def _run():
    keyframes, phases, preview_times, engine_opts = ch.character_track()
    duration = max(k["time"] for k in keyframes)
    objs = ae.build_rig()
    ae.apply_choreography(objs, keyframes, **engine_opts)
    samples = ae.sample(objs, duration_s=duration, sample_hz=60, secondary_motion=ch.SECONDARY_MOTION)
    return samples, duration


def idx_at(t, hz=60):
    return round(t * hz)


def main():
    samples, duration = _run()

    print("=== placement des pieds -- 2 modes (sol / aerien), tolerance", TOLERANCE, "stud ===")
    print("(AIRBORNE_WINDOW =", ch.AIRBORNE_WINDOW, "-- avant/apres : verifie au sol par le")
    print(" modele a 3 cas (calage jambe seule / compromis equilibre, voir r6_solar_smite) ;")
    print(" pendant : verifie qu'AUCUN pied ne traverse le sol -- pas de check de contact.)")
    keyframes, _, _, _ = ch.character_track()
    kf_by_time = {}
    for k in keyframes:
        kf_by_time.setdefault(round(k["time"], 6), k)
    EPS_MATCH = 0.01
    problems = []
    clipping = []
    for t in sorted(kf_by_time):
        kf = kf_by_time[t]
        i = min(round(t * 60), len(samples["Left Leg"]) - 1)
        ly = tip_world(samples, "Left Leg", i, "bottom")[1]
        ry = tip_world(samples, "Right Leg", i, "bottom")[1]
        airborne = ch.AIRBORNE_WINDOW["t0"] <= t <= ch.AIRBORNE_WINDOW["t1"]
        if airborne:
            worst_below = min(ly, ry)  # negatif = traverse le sol
            flag = ""
            if worst_below < -TOLERANCE:
                flag = "  <-- CLIPPING (pied sous le sol pendant la levitation)"
                clipping.append((t, ly, ry))
            print(f"  t={t:6.3f}  LeftFootY={ly:7.3f}  RightFootY={ry:7.3f}  [AERIEN]{flag}")
            continue
        worst = max(abs(ly), abs(ry))
        flag = ""
        if worst > TOLERANCE:
            torso = samples["Torso"][i][1]
            left_leg, right_leg = kf["Left Leg"], kf["Right Leg"]
            y_left_only = ch.grounded_root_y(torso, left_leg, "Left Leg")
            y_right_only = ch.grounded_root_y(torso, right_leg, "Right Leg")
            root_y_used = kf["root_pos"][1]
            if abs(root_y_used - y_left_only) < EPS_MATCH and abs(ry) > TOLERANCE and abs(ly) <= TOLERANCE:
                flag = "  (explique : calage jambe gauche seule)"
            elif abs(root_y_used - y_right_only) < EPS_MATCH and abs(ly) > TOLERANCE and abs(ry) <= TOLERANCE:
                flag = "  (explique : calage jambe droite seule)"
            elif abs(root_y_used - (y_left_only + y_right_only) / 2.0) < EPS_MATCH:
                expected_split = abs(y_left_only - y_right_only) / 2.0
                if abs(worst - expected_split) < EPS_MATCH:
                    flag = f"  (explique : compromis equilibre, ecart attendu={expected_split:.3f})"
                else:
                    flag = "  <-- ANOMALIE NON EXPLIQUEE (compromis equilibre mais residu ne correspond pas au calcul)"
                    problems.append((t, ly, ry))
            else:
                flag = "  <-- ANOMALIE NON EXPLIQUEE"
                problems.append((t, ly, ry))
        print(f"  t={t:6.3f}  LeftFootY={ly:7.3f}  RightFootY={ry:7.3f}{flag}")

    print(f"\n{'aucune anomalie' if not problems else str(len(problems)) + ' anomalie(s)'} de placement au sol non expliquee(s)")
    print(f"{'aucun clipping' if not clipping else str(len(clipping)) + ' clipping(s)'} pendant la levitation")

    print("\n=== clearance mesuree aux instants-cles de la levitation (stud au-dessus du sol) ===")
    for name, t in (("RISE (decollage)", ch.RISE_T), ("CLIMAX", ch.CLIMAX_T), ("RELEASE", ch.RELEASE_T)):
        i = idx_at(t)
        ly = tip_world(samples, "Left Leg", i, "bottom")[1]
        ry = tip_world(samples, "Right Leg", i, "bottom")[1]
        print(f"  {name:20s} t={t:.3f}  clearance min={min(ly, ry):.3f} stud")

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

    print(f"\nDuree totale : {ch.TOTAL_DURATION:.3f}s (echantillonnee : {duration:.3f}s)")

    # =====================================================================
    # VFX (black_hole_track.py) -- verifie numeriquement, pas juste relu :
    # pas de NaN/inf sur toute la timeline, coeur JAMAIS plus grand que le
    # disque (l'occulteur ne doit jamais depasser son propre halo), tous
    # les fragments avales (scale=0, invisible) avant l'atterrissage --
    # sinon un debris resterait fige en l'air une fois le sol de nouveau
    # visible, incoherence immediatement visible a l'ecran.
    # =====================================================================
    print("\n=== VFX (black_hole_track.py) : sante numerique ===")
    ts = np.linspace(0.0, ch.TOTAL_DURATION, 500)
    nonfinite = 0
    core_gt_disk = 0
    max_jump = {}
    prev = {}
    for t in ts:
        r, c = bh.disk_radius(t), bh.core_radius(t)
        if c > r + 1e-9:
            core_gt_disk += 1
        for i in range(bh.N_DEBRIS):
            pos, scale, vis = bh.debris_state(i, t)
            if not np.all(np.isfinite(pos)):
                nonfinite += 1
                continue
            if i in prev and vis and prev[i][1]:
                max_jump[i] = max(max_jump.get(i, 0.0), float(np.linalg.norm(pos - prev[i][0])))
            prev[i] = (pos, vis)
    still_visible_at_land = sum(
        1 for i in range(bh.N_DEBRIS)
        if bh.debris_state(i, ch.LAND_T)[2] and bh.debris_state(i, ch.LAND_T)[1] > 0.01
    )
    print(f"  positions non-finies : {nonfinite}")
    print(f"  coeur > disque (violations) : {core_gt_disk}")
    print(f"  fragments encore visibles a LAND_T ({ch.LAND_T:.3f}s) : {still_visible_at_land} / {bh.N_DEBRIS}")
    print(f"  plus gros saut inter-echantillon (dt~{ts[1]-ts[0]:.4f}s) : {max(max_jump.values()) if max_jump else 0.0:.3f} stud")
    vfx_ok = nonfinite == 0 and core_gt_disk == 0 and still_visible_at_land == 0
    print("  VFX OK" if vfx_ok else "  VFX KO -- voir details ci-dessus")

    # -- coherence timeline : le VFX doit finir (collapse) avant ou pile a
    # l'atterrissage, pas apres (sinon un fragment/le disque resteraient
    # visibles alors que le personnage a deja les pieds au sol).
    collapse_end = ch.VFX_EVENTS["collapse"]["t1"]
    print(f"\n  collapse['t1']={collapse_end:.3f}s  vs  LAND_T={ch.LAND_T:.3f}s  "
          f"({'OK, VFX fini avant atterrissage' if collapse_end <= ch.LAND_T + 1e-6 else 'KO -- VFX deborde sur l atterrissage'})")


if __name__ == "__main__":
    main()
