"""
Assemble le JSON du lecteur HTML : le personnage (UN SEUL rig, jamais la
FK brute -- resolu directement via le moteur d'animation, PAS via un
aller-retour .rbxmx) et la trajectoire monde de la roche
(rock_track.rock_position()), plus la geometrie statique (decor,
cluster de spheres de la roche intacte, debris d'impact) et les instants
cles pour la mise en scene camera/VFX du lecteur.

Difference deliberee avec r6_hit_combo/r6_divine_orb/r6_throne_crown :
ceux-la relisent un .rbxmx deja exporte via resolve_rbxmx.resolve_to_frames()
(equation reelle du moteur, C0/C1 non-identite). Ici, comme calibrate.py
(seule verification deja faite sur ce prototype), on echantillonne
DIRECTEMENT anim_engine.build_rig()/apply_choreography()/sample() --
c'est la convention (C0/C1 de POSITION seulement, rotation locale au
joint) que choreography.py a utilisee pour calculer ROCK_X0/ROCK_Z0/
FOLLOWUP_ROCK_CENTER (voir foot_tip_world()/fist_tip_world()) : relire
un .rbxmx recalculerait les positions avec la VRAIE composition C0.rot/
C1.rot (non-identite, voir r6_rig.py) et desynchroniserait visuellement
le contact deja calibre. Pas de .rbxmx exporte pour ce prototype -- ce
script est la seule etape entre choreography.py et le lecteur.
"""
import json
import os

import numpy as np

import anim_engine as ae
import choreography as ch
import props_rock as pr
import rock_track as rt
from calibrate import world_rotations
from r6_rig import PART_ORDER, PART_SIZES

OUT_HZ = 30
# Duree de queue apres l'impact final de la roche (t=IMPACT_T) pour
# laisser jouer les VFX d'impact (debris/onde/flash) avant la fin de la
# scene -- voir README/CLAUDE.md : la scene ne s'arrete pas a la duree de
# l'animation du personnage (4.0s), la roche continue seule au-dela.
IMPACT_TAIL_S = 1.0


def build_char_frames(out_hz=OUT_HZ):
    """Rejoue striker_track() via le moteur (Empty bpy + F-curves Bezier,
    voir anim_engine.py), echantillonne a out_hz, et met en forme chaque
    frame EXACTEMENT comme resolve_rbxmx.resolve_to_frames() (meme schema
    {t, part: {p:[x,y,z], r:[9 floats monde, row-major]}}) pour que le
    JS du lecteur (copie de r6_hit_combo, sampleChar()/slerpish()) marche
    sans modification."""
    keyframes, phases, preview_times, engine_opts = ch.striker_track()
    duration = max(k["time"] for k in keyframes)
    objs = ae.build_rig()
    ae.apply_choreography(objs, keyframes, **engine_opts)
    samples = ae.sample(objs, duration_s=duration, sample_hz=out_hz)

    n = len(samples["HumanoidRootPart"])
    frames = []
    for i in range(n):
        t = samples["HumanoidRootPart"][i][0]
        rots = world_rotations(samples, i)
        f = {"t": round(t, 4)}
        for part in PART_ORDER:
            if part == "HumanoidRootPart":
                continue
            pos = samples[part][i][3]
            rot = rots[part]
            f[part] = {
                "p": [round(float(v), 4) for v in pos],
                "r": [round(float(v), 5) for row in rot for v in row],
            }
        frames.append(f)
    return frames, duration, phases


def build_rock_track(scene_duration, hz=OUT_HZ):
    """Reechantillonne rock_track.rock_position() (deja verifie par
    calibrate.py -- on ne relit PAS output/rock_track.json, qui s'arrete
    a IMPACT_T a 30Hz sans la queue d'impact) sur toute la duree de la
    scene, meme grille de temps (30Hz) que le personnage pour une
    interpolation JS coherente (frameAt() suppose un pas constant)."""
    n = int(round(scene_duration * hz)) + 1
    track = []
    for i in range(n):
        t = i / hz
        pos, spin, phase = rt.rock_position(t)
        track.append({
            "t": round(t, 4), "phase": phase,
            "pos": [round(float(v), 4) for v in pos] if pos is not None else None,
            "spin_deg": round(float(spin), 2),
        })
    return track


def _spec_out(spec):
    """Reduit un dict Part (voir props_rock.py/export_model.py) aux seuls
    champs dont le lecteur WebGL a besoin (geometrie + couleur), jamais
    les champs specifiques a l'export .rbxmx (material Roblox, mat de
    texture -- ni l'un ni l'autre n'a de PBR genere pour ce prototype,
    voir textures/ : seuls stone_ground/ruin_wall existent, la roche/les
    debris sont donc rendus en couleur pleine, pas texture)."""
    return {
        "name": spec["name"],
        "size": [float(v) for v in spec["size"]],
        "pos": [float(v) for v in spec["pos"]],
        "color": [int(c) for c in spec.get("color_rgb", (120, 120, 130))],
        "shape": spec.get("shape", "1"),
    }


def main():
    char_frames, char_duration, phases = build_char_frames()
    scene_duration = rt.IMPACT_T + IMPACT_TAIL_S
    rock_track = build_rock_track(scene_duration)

    # Roche intacte : cluster local (centre a l'origine) -- le lecteur
    # applique position+rotation (rock_track) comme transform d'un
    # THREE.Group parent, jamais recalcule par piece. Debris : deja
    # positionnes en coordonnees MONDE, au point d'impact reel
    # (rock_track.WORLD_TARGET_POS, pas devine) -- statiques, pas de
    # transform de groupe a leur appliquer.
    rock_parts_local = pr.rock_parts((0.0, 0.0, 0.0), ch.ROCK_RADIUS)
    debris_parts_world = pr.rock_debris_parts(tuple(rt.WORLD_TARGET_POS.tolist()), ch.ROCK_RADIUS)

    out = {
        "fps": OUT_HZ,
        "char_duration": char_duration,
        "scene_duration": scene_duration,
        "part_sizes": {p: list(PART_SIZES[p]) for p in PART_ORDER},
        "part_order": PART_ORDER,
        "char_frames": char_frames,
        "char_z": ch.CHAR_Z,
        "rock_radius": ch.ROCK_RADIUS,
        "rock_rest_pos": [float(v) for v in rt.REST_POS],
        "rock_track": rock_track,
        "rock_parts": [_spec_out(s) for s in rock_parts_local],
        "debris_parts": [_spec_out(s) for s in debris_parts_world],
        "world_target_pos": [float(v) for v in rt.WORLD_TARGET_POS],
        "kick_contact_point": [float(v) for v in ch.KICK_CONTACT_POINT],
        "followup_contact_point": [float(v) for v in ch.FOLLOWUP_CONTACT_POINT],
        "followup_rock_center": [float(v) for v in ch.FOLLOWUP_ROCK_CENTER],
        # -- point d'impact MESURE du stomp (voir choreography.STOMP_POINT) :
        # c'est LA ou la roche jaillit et ou le lecteur doit ancrer le VFX de
        # fissure/poussiere au sol (pas un point choisi a l'oeil cote lecteur).
        "stomp_point": [float(v) for v in ch.STOMP_POINT],
        "key_times": {
            "t0_end": ch.T0_END,
            # -- phase STOMP (voir choreography.py) : bornes exposees pour que
            # le lecteur cale sa camera basse dediee et son VFX de jaillissement
            # dessus, jamais devinees cote JS.
            "stomp_windup_t": ch.STOMP_WINDUP_T,
            "stomp_hold_t": ch.STOMP_HOLD_T,
            "stomp_strike_t": ch.STOMP_STRIKE_T,
            "stomp_recover_t": ch.STOMP_RECOVER_T,
            # -- fin du jaillissement de la roche (voir rock_track.ERUPTION_END_T)
            # -- distinct de stomp_recover_t (le corps recupere plus vite que la
            # roche ne finit de jaillir, voir README/docstring de rock_track.py).
            "eruption_end_t": rt.ERUPTION_END_T,
            "windup_t": ch.WINDUP_T,
            "coil_t": ch.COIL_T,
            "coil_hold_t": ch.COIL_HOLD_T,
            "strike_t": ch.STRIKE_T,
            "followthrough_t": ch.FOLLOWTHROUGH_T,
            "recover_t": ch.RECOVER_T,
            "followup_windup_t": ch.FOLLOWUP_WINDUP_T,
            "followup_coil_t": ch.FOLLOWUP_COIL_T,
            "followup_coil_hold_t": ch.FOLLOWUP_COIL_HOLD_T,
            "followup_strike_t": ch.FOLLOWUP_STRIKE_T,
            "followup_recover_t": ch.FOLLOWUP_RECOVER_T,
            "impact_t": rt.IMPACT_T,
        },
    }
    path = os.environ.get("SCENE_OUT", "/tmp/rock_kick_scene_data.json")
    with open(path, "w") as f:
        json.dump(out, f, separators=(",", ":"))
    print(f"ecrit {path}, {os.path.getsize(path)} octets, {len(char_frames)} frames perso, "
          f"{len(rock_track)} echantillons roche, duree scene {scene_duration:.2f}s "
          f"(perso {char_duration:.2f}s + impact a {rt.IMPACT_T:.2f}s + queue {IMPACT_TAIL_S:.2f}s)")


if __name__ == "__main__":
    main()
