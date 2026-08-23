"""MANDAT MIGRATION CENDRE - pilote. Rend le combo de base 3 coups en
haute densite depuis le GLB rigge+anime (Meshy Punch_Combo, action_id
198) + une retouche manuelle (coup 3, os poses a la main) - meme
technique que pose_walk_brute.py/pose_walk_crawler.py (rotation de
bones nommes, capture Cycles CPU headless par frame).

Coup1 (croix, mocap Punch_Combo) et coup2 (uppercut, mocap Punch_Combo)
viennent du mouvement de bibliotheque Meshy tel quel (aucune retouche
de pose, seulement un echantillonnage non-uniforme du temps : dense a
l'anticipation, 2 frames au contact, etale a la recuperation - regle
de la Bible d'animation). Coup3 (crochet gauche, finisher) n'existe pas
dans Punch_Combo (qui ne contient que 2 frappes distinctes, verifie par
scout render avant tout rendu final - voir docs/worklog.md) : pose a la
main sur le meme squelette (bones LeftArm/LeftForeArm/Spine), amorcee
depuis la pose de garde reelle du mocap (frame 49, quasi-bind-pose) pour
que la coupure mocap->pose-a-la-main soit invisible.

Usage:
    blender --background --factory-startup --python render_combo_cendre.py -- \
        --glb=<combo.glb> --out_dir=<dir> [--res=512] [--samples=32]
"""
import bpy
import sys
import os
import math
import mathutils


def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    result = {}
    for arg in argv:
        if arg.startswith("--") and "=" in arg:
            k, v = arg[2:].split("=", 1)
            result[k] = v
    return result


args = parse_args()
glb_path = args["glb"]
out_dir = args["out_dir"]
res = int(args.get("res", "512"))
samples = int(args.get("samples", "32"))
cam_size = float(args.get("cam_size", "2.2"))
yaw_deg = float(args.get("yaw_deg", "10"))

os.makedirs(out_dir, exist_ok=True)

# ---------------------------------------------------------------- import
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=glb_path)

armature = None
for obj in bpy.context.scene.objects:
    if obj.type == "ARMATURE":
        armature = obj
        break
assert armature is not None
action = bpy.data.actions[0]
if armature.animation_data is None:
    armature.animation_data_create()
armature.animation_data.action = action

# ---------------------------------------------------------------- camera/light (memes reglages que capture_pose.py/rig_final_*.py)
IGNORE_MESH_NAMES = {"icosphere"}


def compute_bbox(objects, depsgraph):
    mins = [math.inf, math.inf, math.inf]
    maxs = [-math.inf, -math.inf, -math.inf]
    for obj in objects:
        if obj.type != "MESH" or obj.name.lower() in IGNORE_MESH_NAMES:
            continue
        eval_obj = obj.evaluated_get(depsgraph)
        mesh = eval_obj.to_mesh()
        for vert in mesh.vertices:
            world = eval_obj.matrix_world @ vert.co
            for i in range(3):
                mins[i] = min(mins[i], world[i])
                maxs[i] = max(maxs[i], world[i])
        eval_obj.to_mesh_clear()
    center = mathutils.Vector(((mins[0] + maxs[0]) / 2, (mins[1] + maxs[1]) / 2, (mins[2] + maxs[2]) / 2))
    return center, mathutils.Vector(mins), mathutils.Vector(maxs)


scene = bpy.context.scene
cam_data = bpy.data.cameras.new("Cam")
cam_data.type = "ORTHO"
cam_data.ortho_scale = cam_size
cam_obj = bpy.data.objects.new("Cam", cam_data)
scene.collection.objects.link(cam_obj)
yaw, pitch = math.radians(yaw_deg), math.radians(18)
direction = mathutils.Vector((math.sin(yaw) * math.cos(pitch), -math.cos(yaw) * math.cos(pitch), math.sin(pitch)))
scene.camera = cam_obj

light_data = bpy.data.lights.new("L", type="SUN")
light_data.energy = 3.0
light_obj = bpy.data.objects.new("L", light_data)
light_obj.rotation_euler = (math.radians(55), 0.0, math.radians(-30))
scene.collection.objects.link(light_obj)

if scene.world is None:
    scene.world = bpy.data.worlds.new("World")
scene.world.use_nodes = True
bg = scene.world.node_tree.nodes.get("Background")
if bg is not None:
    bg.inputs[0].default_value = (0.55, 0.55, 0.57, 1.0)
    bg.inputs[1].default_value = 1.1

scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = samples
scene.cycles.use_denoising = False
scene.view_layers[0].cycles.use_denoising = False
scene.render.film_transparent = True
scene.render.resolution_x = res
scene.render.resolution_y = res
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"

# Cadrage a echelle commune (meme logique que rig_final_brute.py) : Z
# du sol calcule une fois sur la bind pose, tenu fixe pour toutes les
# frames pour eviter tout jitter de camera entre poses.
scene.frame_set(1)
bpy.context.view_layer.update()
depsgraph = bpy.context.evaluated_depsgraph_get()
depsgraph.update()
_, mins0, maxs0 = compute_bbox(bpy.context.scene.objects, depsgraph)
target_z = mins0.z + cam_size * 0.42


def render_current_pose(tag):
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()
    center, mins, maxs = compute_bbox(bpy.context.scene.objects, dg)
    center.z = target_z
    cam_obj.location = center + direction * 10.0
    cam_obj.rotation_euler = (center - cam_obj.location).to_track_quat("-Z", "Y").to_euler()
    out_path = os.path.join(out_dir, f"{tag}.png")
    scene.render.filepath = out_path
    bpy.ops.render.render(write_still=True)
    print("FRAME_RENDERED", tag, out_path)
    return out_path


manifest = []

# ---------------------------------------------------------------- coup1 (croix, mocap pur)
COUP1 = {
    "anticipation": [2, 4, 6, 8, 10, 11, 12, 13],
    "contact": [16, 18],
    "recovery": [20, 22, 24],
}
for phase, frames in COUP1.items():
    for i, f in enumerate(frames):
        scene.frame_set(f)
        tag = f"coup1_{phase}_{i:02d}_mocapframe{f}"
        render_current_pose(tag)
        manifest.append({"coup": 1, "phase": phase, "source": "mocap_punch_combo", "mocap_frame": f, "tag": tag})

# ---------------------------------------------------------------- transition 1->2 (mocap pur, zone de fondu)
TRANSITION_1_2 = [25, 27, 29]
for i, f in enumerate(TRANSITION_1_2):
    scene.frame_set(f)
    tag = f"transition_1to2_{i:02d}_mocapframe{f}"
    render_current_pose(tag)
    manifest.append({"coup": "transition_1to2", "phase": "transition", "source": "mocap_punch_combo", "mocap_frame": f, "tag": tag})

# ---------------------------------------------------------------- coup2 (uppercut, mocap pur - anticipation propre + les 3 frames de transition ci-dessus lui appartiennent aussi narrativement)
COUP2 = {
    "anticipation": [26, 28, 30, 31, 32],
    "contact": [34, 35],
    "recovery": [37, 39, 41],
}
for phase, frames in COUP2.items():
    for i, f in enumerate(frames):
        scene.frame_set(f)
        tag = f"coup2_{phase}_{i:02d}_mocapframe{f}"
        render_current_pose(tag)
        manifest.append({"coup": 2, "phase": phase, "source": "mocap_punch_combo", "mocap_frame": f, "tag": tag})

# ---------------------------------------------------------------- transition 2->3 (mocap pur, queue de garde qui sert de pont vers la pose a la main)
TRANSITION_2_3 = [43, 46, 49]
for i, f in enumerate(TRANSITION_2_3):
    scene.frame_set(f)
    tag = f"transition_2to3_{i:02d}_mocapframe{f}"
    render_current_pose(tag)
    manifest.append({"coup": "transition_2to3", "phase": "transition", "source": "mocap_punch_combo", "mocap_frame": f, "tag": tag})

# ---------------------------------------------------------------- coup3 (crochet gauche, pose a la main - retouche Blender)
# Punch_Combo (verifie par scout render avant ce rendu final, voir
# docs/worklog.md) ne contient que 2 frappes distinctes (croix + uppercut) ;
# le 3e coup du combo de base n'existe pas dans le mouvement de
# bibliotheque. Pose a la main a partir de la derniere frame mocap (49,
# quasi-bind-pose de garde) pour que la coupure soit invisible : action
# detachee a ce point precis, la pose courante devient la nouvelle base,
# puis LeftArm/LeftForeArm/Spine sont pilotes directement (meme technique
# que pose_walk_brute.py/pose_walk_crawler.py). Calibration des axes
# effectuee au prealable par rendus-test isoles (rx=-90 sur LeftArm =
# bras leve devant soi, confirme visuellement avant tout rendu final).
scene.frame_set(49)
bpy.context.view_layer.update()
armature.animation_data.action = None  # la pose courante (frame 49) devient la base figee

bpy.context.view_layer.objects.active = armature
armature.select_set(True)
bpy.ops.object.mode_set(mode="POSE")


def set_bone_euler(name, euler_deg):
    pb = armature.pose.bones[name]
    pb.rotation_mode = "XYZ"
    pb.rotation_euler = tuple(math.radians(d) for d in euler_deg)


# Amplitude au contact (calibree empiriquement) : bras leve devant/vers
# le haut, avant-bras replie, leger contre-buste dans le coup.
PEAK_RX, PEAK_FRX, PEAK_SPINE_RZ = -90.0, -60.0, -12.0

COUP3_FRACTIONS = {
    "anticipation": [0.05, 0.15, 0.28, 0.42, 0.58, 0.72, 0.85],
    "contact": [1.0, 1.0],
    "recovery": [0.75, 0.5, 0.28, 0.08],
}
for phase, fracs in COUP3_FRACTIONS.items():
    for i, frac in enumerate(fracs):
        set_bone_euler("LeftArm", (PEAK_RX * frac, 0, 0))
        set_bone_euler("LeftForeArm", (PEAK_FRX * frac, 0, 0))
        set_bone_euler("Spine", (0, 0, PEAK_SPINE_RZ * frac))
        bpy.ops.object.mode_set(mode="OBJECT")
        tag = f"coup3_{phase}_{i:02d}_frac{frac:.2f}"
        render_current_pose(tag)
        manifest.append({"coup": 3, "phase": phase, "source": "hand_posed_blender_script", "pose_fraction": frac, "tag": tag})
        bpy.context.view_layer.objects.active = armature
        armature.select_set(True)
        bpy.ops.object.mode_set(mode="POSE")

bpy.ops.object.mode_set(mode="OBJECT")

import json
with open(os.path.join(out_dir, "manifest.json"), "w") as fh:
    json.dump(manifest, fh, indent=2)

print("RENDER_COMBO_DONE", len(manifest), "frames")
