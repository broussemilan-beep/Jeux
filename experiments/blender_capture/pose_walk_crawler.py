"""MANDAT AUTONOME v3 Phase 2 - marche Crawler : le rig manuel Crawler
(13 os, deja valide en Phase 1.1 / rig_final_crawler.py) est repris tel
quel depuis le GLB rigge final (bind pose, aucune animation dedans) -
AUCUN nouveau rig, seulement 4 poses de marche cles a la main (meme
technique que la pose d'attaque deja approuvee : rotation manuelle de
quelques os nommes, pas d'estimation Meshy - un quadrupede reste hors
de ce que l'auto-rig sait faire, gotcha deja documente). Cadrage
identique a idle/attaque (cam_size=2.6, target_z=1.0878)."""

import bpy
import sys
import os
import math
import mathutils

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from normal_pass import render_normal_pass


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
cam_size = float(args.get("cam_size", "2.6"))
target_z = float(args.get("target_z", "1.0878"))
with_normals = args.get("with_normals", "1") == "1"

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=glb_path)

arm_obj = None
for obj in bpy.context.scene.objects:
    if obj.type == "ARMATURE":
        arm_obj = obj
        break
assert arm_obj is not None


def setup_render(out_path, res=512, samples=32):
    scene = bpy.context.scene
    for cam in [o for o in scene.objects if o.type == "CAMERA"]:
        bpy.data.objects.remove(cam, do_unlink=True)
    for light in [o for o in scene.objects if o.type == "LIGHT"]:
        bpy.data.objects.remove(light, do_unlink=True)

    cam_data = bpy.data.cameras.new("Cam")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = cam_size
    cam_obj = bpy.data.objects.new("Cam", cam_data)
    scene.collection.objects.link(cam_obj)
    yaw, pitch = math.radians(35), math.radians(18)
    direction = mathutils.Vector((math.sin(yaw) * math.cos(pitch), -math.cos(yaw) * math.cos(pitch), math.sin(pitch)))
    center = mathutils.Vector((0, 0, target_z))
    cam_obj.location = center + direction * 10.0
    cam_obj.rotation_euler = (center - cam_obj.location).to_track_quat("-Z", "Y").to_euler()
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
    scene.render.filepath = out_path
    bpy.ops.render.render(write_still=True)


bpy.ops.object.select_all(action="DESELECT")
bpy.context.view_layer.objects.active = arm_obj
arm_obj.select_set(True)
bpy.ops.object.mode_set(mode="POSE")


def reset_pose():
    for b in arm_obj.pose.bones:
        b.rotation_mode = "XYZ"
        b.rotation_euler = (0, 0, 0)


def set_bone(name, euler_deg):
    pb = arm_obj.pose.bones[name]
    pb.rotation_mode = "XYZ"
    pb.rotation_euler = tuple(math.radians(d) for d in euler_deg)


# Trot diagonal (front_L+back_R avancent ensemble, front_R+back_L
# reculent - meme gait qu'un vrai quadrupede) : 4 poses, deux contacts
# et deux passages, meme convention d'axe X que la pose d'attaque deja
# approuvee (rig_final_crawler.py, front_*_upper/lower rotation X).
POSES = {
    "walk_0": {  # contact : front_L + back_R avant
        "front_L_upper": (-28, 0, 0), "front_L_lower": (18, 0, 0),
        "front_R_upper": (24, 0, 0), "front_R_lower": (-22, 0, 0),
        "back_L_upper": (22, 0, 0), "back_L_lower": (-18, 0, 0),
        "back_R_upper": (-26, 0, 0), "back_R_lower": (16, 0, 0),
        "pelvis": (2, 0, 0), "neck": (3, 0, 0), "tail": (-8, 0, 6),
    },
    "walk_1": {  # passage (neutre, leger abaissement du corps)
        "front_L_upper": (-6, 0, 0), "front_R_upper": (6, 0, 0),
        "back_L_upper": (6, 0, 0), "back_R_upper": (-6, 0, 0),
        "pelvis": (0, 0, 0), "neck": (0, 0, 0), "tail": (0, 0, -4),
    },
    "walk_2": {  # contact : front_R + back_L avant (miroir de walk_0)
        "front_R_upper": (-28, 0, 0), "front_R_lower": (18, 0, 0),
        "front_L_upper": (24, 0, 0), "front_L_lower": (-22, 0, 0),
        "back_R_upper": (22, 0, 0), "back_R_lower": (-18, 0, 0),
        "back_L_upper": (-26, 0, 0), "back_L_lower": (16, 0, 0),
        "pelvis": (-2, 0, 0), "neck": (-3, 0, 0), "tail": (8, 0, 6),
    },
    "walk_3": {  # passage (miroir de walk_1)
        "front_R_upper": (-6, 0, 0), "front_L_upper": (6, 0, 0),
        "back_R_upper": (6, 0, 0), "back_L_upper": (-6, 0, 0),
        "pelvis": (0, 0, 0), "neck": (0, 0, 0), "tail": (0, 0, -4),
    },
}

os.makedirs(out_dir, exist_ok=True)
for i, (pose_name, bones) in enumerate(POSES.items()):
    reset_pose()
    for bone_name, euler_deg in bones.items():
        set_bone(bone_name, euler_deg)
    bpy.context.view_layer.update()
    raw_path = os.path.join(out_dir, f"walk_raw_{i}.png")
    setup_render(raw_path)
    print("FRAME_RENDERED", i, pose_name, raw_path)
    if with_normals:
        normal_path = os.path.join(out_dir, f"walk_normal_{i}.png")
        render_normal_pass(bpy.context.scene, normal_path)
        print("FRAME_NORMAL_RENDERED", i, normal_path)

reset_pose()
bpy.ops.object.mode_set(mode="OBJECT")
print("WALK_POSE_RENDER_DONE", len(POSES))
