"""
Moteur d'animation : construit une hierarchie d'Empty Blender (bpy) qui
reproduit exactement la hierarchie de Motor6D du rig R6 (voir r6_rig.py),
pose des keyframes (interpolation Bezier reelle, moteur de courbes de
Blender) a partir d'une chronologie de poses, puis echantillonne le
resultat a frequence fine pour l'export et la mesure.

Choix de conception n1 (documente au README) : Empty plutot qu'os
d'Armature -- un Empty enfant a un repere local qui EST directement le
repere de rotation-relative-au-parent, donc la rotation posee garde
exactement la semantique de Pose.CFrame de Roblox (rotation appliquee au
joint, relative au repos), sans conversion d'axes lies a la convention
interne d'un os.

Choix de conception n2 (trouve au cycle 1, corrige avant le premier
rapport -- voir README "blocages") : on garde `rotation_mode='XYZ'` sur
chaque Empty mais on ne fait JAMAIS confiance a la matrice que Blender
compose lui-meme depuis rotation_euler (verifie experimentalement :
Blender applique sa PROPRE convention interne pour 'XYZ', differente de
Rx*Ry*Rz -- essai numerique, ecart max ~0.67 sur des coefficients de
matrice, donc PAS la meme rotation que CFrame.Angles(x,y,z) de Roblox).
`rotation_euler` sert donc uniquement de support a 3 CANAUX SCALAIRES
independants, chacun garde son propre keyframe/interpolation Bezier
Blender -- exactement ce dont on a besoin (une courbe lissee par
composante). La matrice de rotation EFFECTIVEMENT utilisee (export +
mesure) est TOUJOURS recalculee a la main via euler_xyz_matrix() a partir
des 3 valeurs (rx,ry,rz) echantillonnees, jamais lue depuis Blender.
Ce choix a aussi elimine le probleme de repliement du quaternion
(rotation_quaternion pris independamment par composante ne respecte pas
la norme unitaire entre keyframes eloignes -- observe au cycle 1, sauts
de +170 a -170 deg sur les courbes -- l'abandon du mode QUATERNION
supprime le probleme a la racine plutot que de le corriger a la mesure).
"""
import math
import numpy as np
import bpy

from r6_rig import PART_ORDER, PARENT, JOINTS, local_offset, joint_for_part


def euler_xyz_matrix(rx_deg, ry_deg, rz_deg):
    """Reproduit CFrame.Angles(x,y,z) de Roblox : rotation intrinseque
    Rx puis Ry puis Rz (radians), matrice 3x3 numpy. Definition de
    reference utilisee PARTOUT (export, mesure) -- jamais la composition
    interne de Blender pour rotation_euler, qui est differente."""
    rx, ry, rz = math.radians(rx_deg), math.radians(ry_deg), math.radians(rz_deg)
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Rx @ Ry @ Rz


def build_rig():
    """Construit la hierarchie d'Empty dans la scene bpy courante, un par
    part R6. Position locale = offset au repos par rapport au parent
    (local_offset du joint). Retourne dict part_name -> bpy Object."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    objs = {}
    for part in PART_ORDER:
        bpy.ops.object.empty_add(type="PLAIN_AXES", radius=0.3)
        obj = bpy.context.active_object
        obj.name = part
        obj.rotation_mode = "XYZ"
        parent_name = PARENT.get(part)
        if parent_name is None:
            obj.location = (0.0, 0.0, 0.0)
        else:
            jname = joint_for_part(part)
            offset = local_offset(jname)
            obj.location = offset
            obj.parent = objs[parent_name]
            obj.matrix_parent_inverse = objs[parent_name].matrix_world.inverted()
        objs[part] = obj
    return objs


def apply_choreography(objs, keyframes, fps=30, handle_type="AUTO_CLAMPED", handle_type_per_part=None):
    """handle_type_per_part : dict optionnel part_name -> handle_type qui
    surcharge handle_type pour cette part precise (permet un reglage
    mixte, ex. VECTOR sur les jambes/torse "porteurs du geste", AUTO_CLAMPED
    sur bras/tete "accompagnement secondaire" -- cycle 4)."""
    handle_type_per_part = handle_type_per_part or {}
    """keyframes: liste de dicts avec 'time' (s) + rotations (deg, tuple xyz)
    par part, et optionnellement 'root_pos' (studs) pour HumanoidRootPart.
    Pose des keyframes Bezier (tangentes auto-clamped) sur chaque objet,
    un canal scalaire independant par composante d'angle (voir note de
    module -- on n'utilise PAS la composition rotation_euler de Blender,
    seulement ses 3 canaux comme courbes lissees independantes)."""
    scene = bpy.context.scene
    scene.render.fps = fps
    scene.frame_start = 0
    last_frame = int(round(max(k["time"] for k in keyframes) * fps)) + 1
    scene.frame_end = last_frame

    for part, obj in objs.items():
        obj.animation_data_clear()
        obj.animation_data_create()
        obj.animation_data.action = bpy.data.actions.new(name=f"{part}_action")

    for kf in keyframes:
        frame = kf["time"] * fps
        scene.frame_set(int(round(frame)))
        for part, obj in objs.items():
            rx, ry, rz = kf.get(part, (0.0, 0.0, 0.0))
            obj.rotation_euler = (math.radians(rx), math.radians(ry), math.radians(rz))
            obj.keyframe_insert(data_path="rotation_euler", frame=frame)
            if part == "HumanoidRootPart":
                pos = kf.get("root_pos", (0.0, 0.0, 0.0))
                obj.location = pos
                obj.keyframe_insert(data_path="location", frame=frame)

    # Interpolation Bezier + tangentes auto-clamped (courbe fluide, pas
    # d'overshoot incontrole) sur tous les canaux.
    # Blender >= 4.4 : Action est "layered" (layers -> strips -> slots ->
    # channelbag -> fcurves), il n'y a plus de .fcurves direct sur Action.
    for part, obj in objs.items():
        this_handle_type = handle_type_per_part.get(part, handle_type)
        action = obj.animation_data.action if obj.animation_data else None
        if not action:
            continue
        for layer in action.layers:
            for strip in layer.strips:
                for slot in action.slots:
                    cb = strip.channelbag(slot)
                    if cb is None:
                        continue
                    for fcurve in cb.fcurves:
                        for kp in fcurve.keyframe_points:
                            kp.interpolation = "BEZIER"
                            kp.handle_left_type = this_handle_type
                            kp.handle_right_type = this_handle_type
                        # Piege bpy (trouve au cycle 2) : ecrire
                        # handle_*_type ne recalcule PAS handle_left/
                        # handle_right -- ils restent aux coordonnees
                        # calculees par l'ancien type (ici AUTO_CLAMPED),
                        # donc la courbe ne changeait pas du tout malgre
                        # le changement de type. On recalcule a la main
                        # pour VECTOR (tangente rectiligne vers chaque
                        # voisin immediat, x deja a 1/3 de la distance
                        # par construction Blender).
                        if this_handle_type == "VECTOR":
                            pts = fcurve.keyframe_points
                            n = len(pts)
                            for i, kp in enumerate(pts):
                                if i > 0:
                                    prev_co = pts[i - 1].co
                                    kp.handle_left.y = kp.co.y - (kp.co.y - prev_co.y) / 3.0
                                if i < n - 1:
                                    next_co = pts[i + 1].co
                                    kp.handle_right.y = kp.co.y + (next_co.y - kp.co.y) / 3.0

    return last_frame


def _spring_chase(times, target, stiffness, damping_ratio, t_min=None):
    """Oscillateur amorti qui "poursuit" une courbe cible -- retard +
    depassement + stabilisation naturels, au lieu de suivre la courbe
    Bezier bruteforce. Integration semi-implicite (Euler), pas de
    dependance externe -- c'est la meme idee que le "secondary motion" /
    "auto-physics" d'outils comme Cascadeur, recree ici en local (pas
    d'API, pas de GPU necessaire dans ce sandbox -- voir README).

    t_min : si fourni, la sortie vaut exactement `target` avant t_min
    (aucun effet, la courbe d'origine -- deja travaillee a la main --
    reste intacte, ex. la montee d'escalier/demi-tour de ce prototype),
    et la simulation demarre PILE sur la valeur cible a t_min (vitesse
    nulle) -- aucun saut visible au point de depart de l'effet."""
    n = len(times)
    out = list(target)
    if n == 0:
        return out
    start_i = 0
    if t_min is not None:
        start_i = next((i for i, t in enumerate(times) if t >= t_min), n)
    if start_i >= n:
        return out
    omega = stiffness ** 0.5
    damp = 2.0 * damping_ratio * omega
    pos = target[start_i]
    vel = 0.0
    out[start_i] = pos
    for i in range(start_i + 1, n):
        dt = times[i] - times[i - 1]
        accel = stiffness * (target[i] - pos) - damp * vel
        vel += accel * dt
        pos += vel * dt
        out[i] = pos
    return out


def sample(objs, duration_s, fps=30, sample_hz=60, secondary_motion=None):
    """Echantillonne (rx,ry,rz) [deg, 3 canaux INDEPENDANTS -- voir note de
    module] + location a sample_hz, en avancant la frame de la scene
    (evaluation reelle des F-curves Bezier de Blender). Retourne dict
    part -> liste de (t, euler_xyz_deg, local_pos, world_pos).
    world_pos vient de matrix_world, mais recompose a la main (voir
    _world_positions ci-dessous) a partir de euler_xyz_matrix -- PAS de
    matrix_world.translation de Blender, pour rester coherent avec la
    seule definition de rotation utilisee partout (Roblox CFrame.Angles).

    secondary_motion : dict optionnel part_name -> {"channels": (0,1,2),
    "stiffness", "damping_ratio", "t_min"} -- applique _spring_chase() au
    canal de rotation LOCAL de cette part avant de recalculer les
    positions monde (donc tout ce qui en depend -- y compris un objet
    porte, suivi via tip_world() dans un script appelant -- reste
    coherent avec la courbe lissee, pas avec la courbe brute)."""
    scene = bpy.context.scene
    n = int(round(duration_s * sample_hz)) + 1
    out = {part: [] for part in objs}
    local_samples = {part: [] for part in objs}
    for i in range(n):
        t = i / sample_hz
        frame = t * fps
        scene.frame_set(0)  # force re-eval
        scene.frame_set(int(frame), subframe=frame - int(frame))
        for part, obj in objs.items():
            e = obj.rotation_euler
            rx, ry, rz = math.degrees(e.x), math.degrees(e.y), math.degrees(e.z)
            pos = obj.location
            local_samples[part].append((t, (rx, ry, rz), (pos.x, pos.y, pos.z)))

    if secondary_motion:
        times = [s[0] for s in local_samples[next(iter(local_samples))]]
        for part, cfg in secondary_motion.items():
            channels = cfg.get("channels", (0, 1, 2))
            chased = {}
            for ch in channels:
                target = [s[1][ch] for s in local_samples[part]]
                chased[ch] = _spring_chase(
                    times, target, cfg.get("stiffness", 140.0),
                    cfg.get("damping_ratio", 0.8), cfg.get("t_min"))
            for i in range(n):
                t, rot, pos = local_samples[part][i]
                rot = list(rot)
                for ch in channels:
                    rot[ch] = chased[ch][i]
                local_samples[part][i] = (t, tuple(rot), pos)

    world_positions = _world_positions(local_samples, n)
    for part in objs:
        for i in range(n):
            t, rot, pos = local_samples[part][i]
            out[part].append((t, rot, pos, world_positions[part][i]))
    return out


def _world_positions(local_samples, n):
    """Cinematique directe a la main, alignee sur l'equation du moteur
    Roblox : Part1 = Part0 * C0 * Transform * C1^-1, dont la partie
    translation vaut `c0 - R.c1` et NON `c0 - c1`.

    Corrige apres confrontation avec la resolution reelle du .rbxmx
    (`resolve_rbxmx.py`) : cette fonction utilisait `local_offset()`,
    c'est-a-dire l'ecart de repos `c0 - c1`, CONSTANT quelle que soit la
    rotation. Un membre y tournait donc autour de son propre centre au
    lieu de pivoter autour de son point d'attache -- une jambe qui frappe
    voyait son pied bouger mais le haut de sa cuisse se detacher de la
    hanche. Ecart mesure contre le moteur : jusqu'a 1.74 stud sur la
    jambe droite. Les angles ecrits (donc toutes les mesures et le
    fichier exporte) n'etaient pas touches -- seuls les apercus l'etaient."""
    out = {part: [None] * n for part in local_samples}
    r_world = {part: [None] * n for part in local_samples}
    for i in range(n):
        for part in PART_ORDER:
            _, rot, pos = local_samples[part][i]
            m_local = euler_xyz_matrix(*rot)
            parent = PARENT.get(part)
            if parent is None:
                out[part][i] = pos
                r_world[part][i] = m_local
            else:
                jname = joint_for_part(part)
                c0 = np.array(JOINTS[jname]["C0"]["pos"])
                c1 = np.array(JOINTS[jname]["C1"]["pos"])
                pos = tuple((c0 - m_local @ c1).tolist())
                pw = np.array(out[parent][i])
                rw = r_world[parent][i]
                world = pw + rw @ np.array(pos)
                out[part][i] = tuple(world.tolist())
                r_world[part][i] = rw @ m_local
    return out
