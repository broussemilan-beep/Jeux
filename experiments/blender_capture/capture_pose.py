"""experiments/blender_capture/capture_pose.py

Rendu headless d'un GLB riggé (Blender 4.x, Cycles CPU, zéro Vulkan,
zéro display server) — solution de repli au pipeline Godot
(SubViewport 3D offscreen) resté bloqué dans le conteneur de la
session MANDAT NUIT (voir docs/worklog.md, section "PHASE 3 — 3
monstres Meshy" pour le diagnostic complet). Prend un GLB, une
animation optionnelle + un temps/frame, calcule une caméra
orthographique auto-cadrée sur la bounding box du modèle, et rend un
PNG RGBA (fond transparent, haute résolution). AUCUNE quantification
pixel-art ici — faite séparément en Python pur (Pillow/numpy) par
experiments/blender_capture/quantize.py : ce script ne produit que le
rendu 3D brut.

Cycles/CPU choisi explicitement (pas EEVEE) : EEVEE nécessite un
contexte OpenGL/EGL même en headless, exactement le genre de
dépendance display/driver qui a bloqué le pipeline Godot. Cycles CPU
est un raytracer logiciel pur, aucune dépendance GPU/Vulkan/X11.

Usage :
    blender --background --factory-startup --python capture_pose.py -- \
        --glb=/path/to/model.glb --out=/path/to/out.png \
        [--anim_name=NAME] [--anim_time=SECONDS] [--anim_frame=N] \
        [--list_actions] [--res=512] [--samples=32] \
        [--cam_yaw_deg=35] [--cam_pitch_deg=18] [--cam_size=0]

--list_actions imprime les noms d'action disponibles dans le GLB et
quitte sans rendre (reconnaissance avant de choisir --anim_name).
--cam_size=0 (défaut) calcule automatiquement une taille orthographique
depuis la bounding box du modèle ; passer une valeur positive pour
calibrer manuellement comme sur le pipeline Godot d'origine.
"""

import bpy
import sys
import math
import mathutils


def parse_args() -> dict:
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []
    result = {}
    for arg in argv:
        if arg.startswith("--") and "=" in arg:
            k, v = arg[2:].split("=", 1)
            result[k] = v
        elif arg.startswith("--"):
            result[arg[2:]] = "1"
    return result


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in list(bpy.data.meshes):
        bpy.data.meshes.remove(block)
    for block in list(bpy.data.armatures):
        bpy.data.armatures.remove(block)
    for block in list(bpy.data.actions):
        bpy.data.actions.remove(block)


# Objets rencontrés dans les GLB riggés Meshy qui ne font PAS partie du
# personnage (artefact du pipeline de rig, probablement un gizmo/proxy
# visuel) — repéré sur Crawler : un mesh nommé "Icosphere" (42 sommets,
# span fixe (0,0,-1)-(0,0,1) quelle que soit la pose/l'anim jouée) qui
# gonflait la bbox calculée et rendait TOUTES les poses de Crawler
# identiques en taille (~2.0 unités) indépendamment de la pose réelle
# du personnage. Exclu explicitement du calcul de bbox.
IGNORE_MESH_NAMES = {"icosphere"}


def compute_bbox(objects, depsgraph) -> tuple:
    # IMPORTANT : `obj.bound_box` est la bbox LOCALE de la donnée
    # source, non évaluée — elle ignore la déformation par armature
    # (constaté empiriquement : identique bit-à-bit entre idle et une
    # pose de coup de pied en l'air sur Crawler). Il faut la bbox
    # évaluée (post-modificateurs, post-pose) via le depsgraph pour
    # cadrer une caméra sur la VRAIE silhouette de la pose demandée.
    mins = [math.inf, math.inf, math.inf]
    maxs = [-math.inf, -math.inf, -math.inf]
    for obj in objects:
        if obj.type != "MESH":
            continue
        if obj.name.lower() in IGNORE_MESH_NAMES:
            continue
        eval_obj = obj.evaluated_get(depsgraph)
        mesh = eval_obj.to_mesh()
        for vert in mesh.vertices:
            world = eval_obj.matrix_world @ vert.co
            for i in range(3):
                mins[i] = min(mins[i], world[i])
                maxs[i] = max(maxs[i], world[i])
        eval_obj.to_mesh_clear()
    if mins[0] == math.inf:
        return mathutils.Vector((0.0, 0.0, 0.0)), mathutils.Vector((0.0, 0.0, 0.0))
    center = mathutils.Vector(
        ((mins[0] + maxs[0]) / 2, (mins[1] + maxs[1]) / 2, (mins[2] + maxs[2]) / 2)
    )
    size = mathutils.Vector((maxs[0] - mins[0], maxs[1] - mins[1], maxs[2] - mins[2]))
    return center, size


def main() -> None:
    args = parse_args()
    glb_path = args.get("glb")
    if not glb_path:
        print("ERROR: --glb requis")
        sys.exit(1)
    out_path = args.get("out", "/tmp/blender_capture.png")
    res = int(args.get("res", "512"))
    samples = int(args.get("samples", "32"))
    cam_yaw_deg = float(args.get("cam_yaw_deg", "35"))
    cam_pitch_deg = float(args.get("cam_pitch_deg", "18"))
    cam_size_arg = float(args.get("cam_size", "0"))
    target_z_arg = args.get("target_z")
    anim_name = args.get("anim_name", "")
    anim_time = args.get("anim_time")
    anim_frame = args.get("anim_frame")
    list_actions = args.get("list_actions") == "1"

    clear_scene()

    bpy.ops.import_scene.gltf(filepath=glb_path)

    imported = list(bpy.context.scene.objects)
    armature = None
    for obj in imported:
        if obj.type == "ARMATURE":
            armature = obj
            break

    if list_actions:
        print("ACTIONS:", [a.name for a in bpy.data.actions])
        for a in bpy.data.actions:
            print("  ", a.name, "frame_range=", tuple(a.frame_range))
        return

    scene = bpy.context.scene
    fps = scene.render.fps

    if armature is not None and bpy.data.actions:
        target_action = bpy.data.actions.get(anim_name) if anim_name else bpy.data.actions[0]
        if target_action is not None:
            if armature.animation_data is None:
                armature.animation_data_create()
            armature.animation_data.action = target_action
            if anim_frame is not None:
                frame = float(anim_frame)
            elif anim_time is not None:
                frame = target_action.frame_range[0] + float(anim_time) * fps
            else:
                frame = target_action.frame_range[0]
            scene.frame_set(int(round(frame)))
            # Force l'évaluation du depsgraph sur cette frame AVANT de
            # lire matrix_world (compute_bbox) et avant le rendu — sans
            # ça la pose du squelette reste celle du dernier frame_set
            # implicite (souvent la bind pose), pas celle demandée.
            bpy.context.view_layer.update()

    depsgraph = bpy.context.evaluated_depsgraph_get()
    depsgraph.update()
    center, size = compute_bbox(imported, depsgraph)
    if args.get("debug_bbox", "0") == "1":
        for obj in imported:
            if obj.type != "MESH":
                continue
            eval_obj = obj.evaluated_get(depsgraph)
            mesh = eval_obj.to_mesh()
            if len(mesh.vertices) > 0:
                v0_local = mesh.vertices[0].co.copy()
                v0_world = eval_obj.matrix_world @ v0_local
                print("DEBUG_BBOX", obj.name, "vcount=", len(mesh.vertices),
                      "v0_local=", tuple(v0_local), "v0_world=", tuple(v0_world))
            eval_obj.to_mesh_clear()
    cam_size = cam_size_arg if cam_size_arg > 0 else (max(size.x, size.y, size.z) * 1.3 if max(size) > 0 else 2.0)
    # --target_z permet un cadrage à ÉCHELLE COMMUNE entre plusieurs
    # personnages : au lieu de centrer chaque capture sur SA propre bbox
    # (ce qui efface toute différence de taille réelle entre modèles),
    # on fixe le même point vertical (monde) au même endroit du cadre
    # pour tous — typiquement le sol (Z=0) à une fraction fixe depuis le
    # bas de l'image, indépendante de la taille du personnage.
    if target_z_arg is not None:
        center.z = float(target_z_arg)

    cam_data = bpy.data.cameras.new("CaptureCam")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = cam_size
    cam_obj = bpy.data.objects.new("CaptureCam", cam_data)
    scene.collection.objects.link(cam_obj)

    # Blender = Z up (le glTF importer bascule l'axe à l'import). Le
    # yaw tourne autour de Z (vertical), le pitch incline la caméra
    # vers le haut/bas — même logique de cadrage que
    # experiments/bakeoff_voie_c/capture_idle_glb.gd côté Godot (qui
    # est en Y-up), adaptée à l'axe vertical de Blender.
    yaw = math.radians(cam_yaw_deg)
    pitch = math.radians(cam_pitch_deg)
    distance = 10.0
    direction = mathutils.Vector((
        math.sin(yaw) * math.cos(pitch),
        -math.cos(yaw) * math.cos(pitch),
        math.sin(pitch),
    ))
    cam_obj.location = center + direction * distance
    look_dir = center - cam_obj.location
    cam_obj.rotation_euler = look_dir.to_track_quat("-Z", "Y").to_euler()
    scene.camera = cam_obj

    key_light_data = bpy.data.lights.new("KeyLight", type="SUN")
    key_light_data.energy = 3.0
    key_light_obj = bpy.data.objects.new("KeyLight", key_light_data)
    key_light_obj.rotation_euler = (math.radians(55), 0.0, math.radians(-30))
    scene.collection.objects.link(key_light_obj)

    if scene.world is None:
        scene.world = bpy.data.worlds.new("World")
    scene.world.use_nodes = True
    bg_node = scene.world.node_tree.nodes.get("Background")
    if bg_node is not None:
        bg_node.inputs[0].default_value = (0.55, 0.55, 0.57, 1.0)
        bg_node.inputs[1].default_value = 1.1

    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = samples
    # Ce build Blender (paquet apt) est compilé sans OpenImageDenoiser —
    # le débruitage est activé par défaut sur les nouvelles scènes et
    # fait échouer le rendu ("Build without OpenImageDenoiser") sans lui.
    scene.cycles.use_denoising = False
    scene.view_layers[0].cycles.use_denoising = False
    scene.render.film_transparent = True
    scene.render.resolution_x = res
    scene.render.resolution_y = res
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.filepath = out_path

    bpy.ops.render.render(write_still=True)

    print("CAPTURE_RESULT", {
        "out_path": out_path, "center": tuple(center), "size": tuple(size),
        "cam_size": cam_size, "cam_yaw_deg": cam_yaw_deg, "cam_pitch_deg": cam_pitch_deg,
    })


main()
