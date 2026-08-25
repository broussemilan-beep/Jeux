"""CHANTIER C (Monstres : animations d'interaction) - reactions au coup
Ranged : rig auto-Meshy reussi (posture debout standard, cf. data/
meshy_usage.jsonl entree "rigging" du 2026-08-21), squelette Mixamo-like
(Hips/Spine*/LeftArm-RightArm/LeftUpLeg-RightUpLeg/neck/Head). Meme
technique de pose a la main que les 2 autres monstres (rig deja paye,
aucun credit Meshy supplementaire) plutot qu'un meshy_animate - le
convertisseur Meshy n'a pas de convention d'axe documentee (gotcha deja
note sur le pilote Cendre, meme famille de rig : LeftArm/RightArm PAS
symetriques en signe), verifie ici par rendu-test avant de figer les
poses finales. Cadrage identique a idle/attaque/marche (cam_size=2.6,
target_z=1.092).

5 poses (Ranged = monstre LEGER, recoil_multiplier=1.4 dans
enemy_ranged.tscn - recoit la pose "projete" comme Crawler) :
  touche_lateral / touche_avant / touche_arriere / chancelle / projete.
"""

import bpy
import sys
import os
import math

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
with_normals = args.get("with_normals", "0") == "1"
only = args.get("only")  # nom de pose unique, pour calibration rapide

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
    import mathutils
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


# Gotcha deja documente (pilote Cendre, meme famille de rig) : LeftArm
# leve avec rx=-90, RightArm leve avec rx=+90 - PAS symetrique en
# signe. Verifie empiriquement sur ce rig (voir note worklog) avant de
# figer les poses ci-dessous : meme asymetrie confirmee ici.
POSES = {
    "touche_lateral": {  # canonique : coup venu de la droite, recul vers la gauche
        "Spine": (0, 0, -16), "Spine01": (0, 0, -10), "neck": (0, 0, 14), "Head": (0, 0, 8),
        "RightArm": (30, 0, -20), "RightForeArm": (25, 0, 0),
        "LeftArm": (-15, 0, 12),
        "Hips": (0, 0, -8),
    },
    "touche_avant": {  # coup de face, recule (Hips vers l'arriere, buste part en arriere)
        "Spine": (14, 0, 0), "Spine01": (10, 0, 0), "neck": (-10, 0, 0), "Head": (-6, 0, 0),
        "LeftArm": (30, 0, 10), "RightArm": (-30, 0, -10),
        "LeftUpLeg": (-10, 0, 0), "RightUpLeg": (-10, 0, 0),
    },
    "touche_arriere": {  # coup de dos, part en avant
        "Spine": (-14, 0, 0), "Spine01": (-9, 0, 0), "neck": (9, 0, 0), "Head": (6, 0, 0),
        "LeftArm": (-20, 0, -6), "RightArm": (20, 0, 6),
        "LeftUpLeg": (10, 0, 0), "RightUpLeg": (10, 0, 0),
    },
    "chancelle": {  # chancellement (enchainement de coups), asymetrie deliberee
        "Spine": (0, 0, -13), "Hips": (0, 0, 9),
        "LeftArm": (-22, 0, 16), "RightArm": (26, 0, -14),
        "LeftUpLeg": (8, 0, 0), "RightUpLeg": (-6, 0, 0),
        "neck": (0, 0, 12), "Head": (0, 0, 8),
    },
    "projete": {  # aerien/desequilibre - debut d'un recul de projection (leger)
        "Hips": (18, 0, 0), "Spine": (-20, 0, 0), "Spine01": (-14, 0, 0),
        "neck": (-14, 0, 0), "Head": (-10, 0, 0),
        "LeftArm": (60, 0, 20), "RightArm": (55, 0, -20),
        "LeftForeArm": (30, 0, 0), "RightForeArm": (30, 0, 0),
        "LeftUpLeg": (-30, 0, 0), "RightUpLeg": (-25, 0, 0),
        "LeftLeg": (35, 0, 0), "RightLeg": (30, 0, 0),
    },
}

os.makedirs(out_dir, exist_ok=True)
active_poses = {only: POSES[only]} if only else POSES
for pose_name, bones in active_poses.items():
    reset_pose()
    for bone_name, euler_deg in bones.items():
        set_bone(bone_name, euler_deg)
    bpy.context.view_layer.update()
    raw_path = os.path.join(out_dir, f"{pose_name}_raw.png")
    setup_render(raw_path)
    print("FRAME_RENDERED", pose_name, raw_path)
    if with_normals:
        normal_path = os.path.join(out_dir, f"{pose_name}_normal.png")
        render_normal_pass(bpy.context.scene, normal_path)
        print("FRAME_NORMAL_RENDERED", pose_name, normal_path)

reset_pose()
bpy.ops.object.mode_set(mode="OBJECT")
print("HIT_REACTIONS_RENDER_DONE", len(active_poses))
