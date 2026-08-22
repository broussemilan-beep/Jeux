"""MANDAT AUTONOME v3 Phase 2 - marche Brute : meme technique que
pose_walk_crawler.py (rig manuel 10 os deja valide, 4 poses de marche
a la main, aucune animation Meshy - le rig auto avait echoue sur cette
posture accroupie, gotcha deja documente). Cadrage identique a
idle/attaque (cam_size=2.6, target_z=1.092)."""

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
target_z = float(args.get("target_z", "1.092"))
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


# Marche bipede, bras/jambe opposes (contralateral swing standard) : 4
# poses, memes bones que la pose d'attaque deja approuvee
# (arm_{L,R}_upper/lower, leg_{L,R}_upper/lower, chest).
POSES = {
    "walk_0": {  # contact : leg_L avant, arm_R avant
        "leg_L_upper": (-22, 0, 0), "leg_L_lower": (14, 0, 0),
        "leg_R_upper": (20, 0, 0), "leg_R_lower": (-16, 0, 0),
        "arm_R_upper": (-18, 0, 0), "arm_L_upper": (16, 0, 0),
        "chest": (0, 0, 3), "pelvis": (0, 0, 2),
    },
    "walk_1": {  # passage
        "leg_L_upper": (-5, 0, 0), "leg_R_upper": (5, 0, 0),
        "arm_R_upper": (-4, 0, 0), "arm_L_upper": (4, 0, 0),
        "chest": (0, 0, 0), "pelvis": (0, 0, 0),
    },
    "walk_2": {  # contact : leg_R avant, arm_L avant (miroir)
        "leg_R_upper": (-22, 0, 0), "leg_R_lower": (14, 0, 0),
        "leg_L_upper": (20, 0, 0), "leg_L_lower": (-16, 0, 0),
        "arm_L_upper": (-18, 0, 0), "arm_R_upper": (16, 0, 0),
        "chest": (0, 0, -3), "pelvis": (0, 0, -2),
    },
    "walk_3": {  # passage (miroir)
        "leg_R_upper": (-5, 0, 0), "leg_L_upper": (5, 0, 0),
        "arm_L_upper": (-4, 0, 0), "arm_R_upper": (4, 0, 0),
        "chest": (0, 0, 0), "pelvis": (0, 0, 0),
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
