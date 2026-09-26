"""
Assemble le JSON du lecteur HTML de la scene complete de combat + trone :
deux rigs R6 INDEPENDANTS ET ACTIFS (Hero/Rival, echantillonnes DIRECTEMENT
par le moteur -- ae.build_rig()/apply_choreography()/sample(), meme chemin
que calibrate_battle.py, PAS un aller-retour par un .rbxmx exporte comme
r6_hit_combo/r6_throne_crown : ce prototype n'exporte pas de KeyframeSequence
intermediaire, la choregraphie de choreography.py va directement au
lecteur), le decor statique (trone+escalier, pilier intact/debris), la
trajectoire de la couronne (meme principe que compute_crown_track.py,
recalculee ici sur la grille du personnage -- voir crown_frames_at()), et
les instants-cles (impacts, telegraphes, bornes de beats) pour la mise en
scene camera/VFX du lecteur.

compute_crown_track.py n'est PAS importe tel quel : ses propres imports de
module (`from calibrate import ...`, `from choreography import full_scene,
FULL_PICKUP_T, ...`) supposent le repere autonome de r6_throne_crown (un
seul personnage, scene qui commence a t=0) -- ni son module `calibrate`
n'existe ici (voir calibrate_battle.py, meme fonctions), ni son
`choreography.full_scene`/`FULL_PICKUP_T` (le choreography.py de CE
prototype est le combat complet, `full_scene`/`climb_stairs`/
`sit_and_crown` vivent dans throne_sequence.py, decales par BEAT5_END).
Isolation entre prototypes oblige (voir CLAUDE.md/consigne de tache) : la
MEME recette (bande suit coussin -> main -> tete, rebond d'atterrissage)
est reimplementee ci-dessous avec les MEMES constantes LANDING_* (valeurs
copiees telles quelles, jamais redevinees) et les fonctions tip_world/
world_rotations de calibrate_battle.py (code identique a calibrate.py de
r6_throne_crown), sur la grille de temps DECALEE par
BEAT5_END + throne_sequence.CLIMB_T -- exactement le decalage que
choreography.hero_track() applique deja a sit_kf.
"""
import json
import math
import os

import numpy as np

import anim_engine as ae
import choreography as bc
import props
import props_battle as pb
import punch_combo as pc
import throne_sequence as ts
from calibrate_battle import tip_world, world_rotations
from r6_rig import PART_ORDER, PART_SIZES

OUT_HZ = 30

# -- copiees telles quelles depuis r6_throne_crown/scripts/
#    compute_crown_track.py (voir docstring de module : son fichier n'est
#    pas importable ici, ces valeurs le sont).
LANDING_DUR = 0.40
LANDING_AMPLITUDE = 0.05
LANDING_FREQ_HZ = 5.0
LANDING_TAU = 0.11

CUSHION_POS = props.cushion_top_pos()

# Instants d'assise/couronnement, decales dans le repere ABSOLU de la
# scene complete -- meme decalage que choreography.hero_track() applique
# a sit_kf (BEAT5_END + ts.CLIMB_T), applique ici a PICKUP_T/PLACED_T
# (relatifs a sit_and_crown() seule, voir throne_sequence.py).
_SIT_SHIFT = bc.BEAT5_END + ts.CLIMB_T
PICKUP_T_ABS = ts.PICKUP_T + _SIT_SHIFT
PLACED_T_ABS = ts.PLACED_T + _SIT_SHIFT

# Sous-phases de sit_and_crown() (approche/assise/couronnement/pose_finale),
# lues directement depuis throne_sequence.py (jamais redevinees) -- servent
# de bornes EXACTES aux plans camera "empruntes" a throne_crown_viewer.html
# (memes valeurs az/el/echelle/cible, voir le template : le repere monde du
# trone/personnage assis est identique, seul le decalage temporel change).
_, _sit_phases, _, _ = ts.sit_and_crown()


def _static_parts_json(parts):
    out = []
    for spec in parts:
        out.append({
            "name": spec["name"], "size": list(spec["size"]),
            "pos": list(spec["pos"]),
            "rot": spec.get("rot", [[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
            "color": spec["color_rgb"], "shape": spec.get("shape", "1"),
            "material": spec.get("material", "Plastic"),
        })
    return out


def _run_track(track_fn, duration_s, secondary_motion=None):
    keyframes, phases, preview_times, engine_opts = track_fn()
    objs = ae.build_rig()
    ae.apply_choreography(objs, keyframes, **engine_opts)
    samples = ae.sample(objs, duration_s=duration_s, sample_hz=OUT_HZ,
                         secondary_motion=secondary_motion)
    return samples, phases


def _frames_from_samples(samples):
    """Meme forme de sortie que resolve_rbxmx.resolve_to_frames() (utilise
    par les deux prototypes de reference), pour que le lecteur HTML puisse
    reutiliser exactement le meme sampleChar()/frameAt() JS -- construit
    ici a partir de samples d'anim_engine.sample() (t, rot_locale,
    pos_locale, pos_monde) plutot que d'un .rbxmx resolu, mais le champ
    monde attendu par le lecteur ("p": position monde, "r": rotation
    monde 3x3 a plat) est identique."""
    n = len(samples["Torso"])
    out = []
    for i in range(n):
        t = samples["Torso"][i][0]
        rot_all = world_rotations(samples, i)   # une seule fois par frame, pas par part
        f = {"t": round(t, 4)}
        for part in PART_ORDER:
            pos = samples[part][i][3]
            rot = rot_all[part]
            f[part] = {
                "p": [round(float(v), 4) for v in pos],
                "r": [round(float(v), 5) for row in np.array(rot) for v in row],
            }
        out.append(f)
    return out


def crown_frames_at(hero_samples):
    """Meme algorithme que compute_crown_track.py (voir docstring de
    module) : coussin statique -> suit la main droite -> suit la tete
    (avec rebond d'atterrissage), mais REUTILISE directement les samples
    DEJA calcules pour Hero (meme rig, meme grille de temps) plutot que
    de rejouer une seconde simulation independante -- garantit que la
    couronne reste exactement synchronisee avec la main/tete de Hero tels
    que rendus, quelle que soit l'option de secondary motion utilisee."""
    local_parts = props.crown_parts()
    n = len(hero_samples["Torso"])
    out = []
    for i in range(n):
        t = hero_samples["Torso"][i][0]
        if t < PICKUP_T_ABS:
            c_pos, c_rot = np.array(CUSHION_POS), np.eye(3)
        elif t < PLACED_T_ABS:
            c_pos, c_rot = tip_world(hero_samples, "Right Arm", i, "bottom"), np.eye(3)
        else:
            c_pos = tip_world(hero_samples, "Head", i, "top")
            c_rot = world_rotations(hero_samples, i)["Head"]
            age = t - PLACED_T_ABS
            if age < LANDING_DUR:
                bounce = (LANDING_AMPLITUDE * math.exp(-age / LANDING_TAU)
                          * math.cos(2 * math.pi * LANDING_FREQ_HZ * age))
                c_pos = c_pos + np.array([0.0, bounce, 0.0])

        frame = {"t": round(float(t), 4)}
        for spec in local_parts:
            lp = np.array(spec["pos"])
            lr = np.array(spec.get("rot", [[1, 0, 0], [0, 1, 0], [0, 0, 1]]))
            wp = c_pos + c_rot @ lp
            wr = c_rot @ lr
            frame[spec["name"]] = {
                "p": [round(float(v), 4) for v in wp],
                "r": [round(float(v), 5) for row in wr for v in row],
            }
        out.append(frame)
    return out


def main():
    duration = bc.TOTAL_SCENE_DURATION

    # -- Hero : secondary motion (retard/depassement du buste, voir
    # anim_engine._spring_chase) UNIQUEMENT sur la portion assise/
    # couronnement -- meme reglage que throne_sequence.SECONDARY_MOTION
    # (stiffness/damping_ratio inchanges), t_min DECALE de _SIT_SHIFT pour
    # que l'effet ne demarre qu'au debut de l'assise dans le repere
    # ABSOLU de la scene complete (sinon il demarrerait pendant le combat,
    # a t=ts.CLIMB_T~3.85s, jamais l'intention de throne_sequence.py).
    hero_secondary = {
        "Torso": {**ts.SECONDARY_MOTION["Torso"], "t_min": ts.SECONDARY_MOTION["Torso"]["t_min"] + _SIT_SHIFT},
    }
    hero_samples, hero_phases = _run_track(bc.hero_track, duration, secondary_motion=hero_secondary)
    # -- Rival : tient sa pose de KO jusqu'a la fin (extrapolation
    # CONSTANT par defaut des F-curves Blender au-dela de la derniere
    # keyframe, verifie -- voir le worklog) -- jamais de secondary motion
    # (Rival ne bouge plus, encaisse tel quel).
    rival_samples, rival_phases = _run_track(bc.rival_track, duration)

    hero_frames = _frames_from_samples(hero_samples)
    rival_frames = _frames_from_samples(rival_samples)
    crown_frames = crown_frames_at(hero_samples)

    static_parts = props.staircase_parts() + props.throne_parts()
    pillar_intact = pb.pillar_parts(bc.PILLAR_POS)
    pillar_debris = pb.pillar_debris_parts(bc.PILLAR_POS)

    # -- instants-cles pour la camera/VFX du lecteur, calcules EXACTEMENT
    # comme calibrate_battle.py (aucune valeur redevinee) : Beat1 (jab
    # d'ouverture de Rival, reflete), Beat2 (combo complet de Hero,
    # translate), Beat3 (haymaker/esquive/kick/pilier), Beat4 (finisher),
    # Beat5 (victoire/demi-tour/marche), montee/assise du trone.
    instants = {
        "t0_end": bc.T0_END,
        "rival_jab_windup": bc.BEAT1_START + pc.JAB_WINDUP_T,
        "rival_jab": bc.BEAT1_START + pc.JAB_T,
        "beat1_end": bc.BEAT1_END,
        "hero_jab_windup": bc.BEAT2_START + pc.JAB_WINDUP_T,
        "hero_jab": bc.BEAT2_START + pc.JAB_T,
        "hero_cross_windup": bc.BEAT2_START + pc.CROSS_WINDUP_T,
        "hero_cross": bc.BEAT2_START + pc.CROSS_T,
        "hero_hook_windup": bc.BEAT2_START + pc.HOOK_WINDUP_T,
        "hero_hook": bc.BEAT2_START + pc.HOOK_T,
        "beat2_end": bc.BEAT2_END,
        "regroup_start": bc.REGROUP_START,
        "beat3_start": bc.BEAT3_START,
        "haymaker_windup": bc.HM_WINDUP_T,
        "haymaker_coil": bc.HM_COIL_T,
        "haymaker_hold": bc.HM_HOLD_T,
        "haymaker_strike": bc.HM_STRIKE_T,
        "dodge_start": bc.DODGE_START_T,
        "dodge_hold": bc.DODGE_HOLD_T,
        "dodge_recover": bc.DODGE_RECOVER_T,
        "kick_windup": bc.KICK_WINDUP_T,
        "kick_hold": bc.KICK_HOLD_T,
        "kick_strike": bc.KICK_STRIKE_T,
        "pillar_hit": bc.PILLAR_HIT_T,
        "beat3_end": bc.BEAT3_END,
        "beat4_start": bc.BEAT4_START,
        "stumble": bc.STUMBLE_T,
        "finish_windup": bc.FINISH_WINDUP_T,
        "finish_coil": bc.FINISH_COIL_T,
        "finish_hold": bc.FINISH_HOLD_T,
        "finish_hipdrive": bc.FINISH_HIPDRIVE_T,
        "finish_strike": bc.FINISH_STRIKE_T,
        "beat4_end": bc.BEAT4_END,
        "breath": bc.BREATH_T,
        "settle": bc.SETTLE_T,
        "flex": bc.FLEX_T,
        "flex_hold": bc.FLEX_HOLD_T,
        "turn_start": bc.TURN_START,
        "turn_end": bc.TURN_END,
        "walk_start": bc.WALK_START,
        "walk_end": bc.WALK_END,
        "beat5_end": bc.BEAT5_END,
        "climb_montee_end": bc.BEAT5_END + ts.STAIRS_T,
        "climb_end": bc.BEAT5_END + ts.CLIMB_T,
        "sit_approche_end": _SIT_SHIFT + _sit_phases[0]["t1"],
        "sit_assise_end": _SIT_SHIFT + _sit_phases[1]["t1"],
        "sit_couronnement_end": _SIT_SHIFT + _sit_phases[2]["t1"],
        "sit_pose_finale_end": _SIT_SHIFT + _sit_phases[3]["t1"],
        "pickup_t": PICKUP_T_ABS,
        "placed_t": PLACED_T_ABS,
        "scene_end": duration,
    }

    out = {
        "fps": OUT_HZ,
        "duration": duration,
        "part_sizes": {p: list(PART_SIZES[p]) for p in PART_ORDER},
        "part_order": PART_ORDER,
        "hero_frames": hero_frames,
        "rival_frames": rival_frames,
        "hero_phases": [{"name": p["name"], "t0": p["t0"], "t1": min(p["t1"], duration)} for p in hero_phases],
        "rival_phases": [{"name": p["name"], "t0": p["t0"], "t1": min(p["t1"], duration)} for p in rival_phases],
        "instants": instants,
        "static_parts": _static_parts_json(static_parts),
        "pillar_parts": _static_parts_json(pillar_intact),
        "pillar_debris_parts": _static_parts_json(pillar_debris),
        "pillar_hit_t": bc.PILLAR_HIT_T,
        "pillar_pos": list(bc.PILLAR_POS),
        "crown_part_names": [s["name"] for s in props.crown_parts()],
        "crown_part_specs": {
            s["name"]: {"size": list(s["size"]), "shape": s.get("shape", "1"),
                        "color": s["color_rgb"], "material": s.get("material", "Plastic")}
            for s in props.crown_parts()
        },
        "crown_frames": crown_frames,
        "pickup_t": PICKUP_T_ABS,
        "placed_t": PLACED_T_ABS,
    }
    path = os.environ.get("SCENE_OUT", "/tmp/battle_throne_scene_data.json")
    with open(path, "w") as f:
        json.dump(out, f, separators=(",", ":"))
    print(f"ecrit {path}, {os.path.getsize(path)} octets, "
          f"{len(hero_frames)} frames hero, {len(rival_frames)} frames rival, "
          f"duree {duration:.2f}s")


if __name__ == "__main__":
    main()
