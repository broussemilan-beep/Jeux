"""CHANTIER C (Monstres : animations d'interaction) - reactions au coup
Brute : meme technique que pose_walk_brute.py (rig manuel 12 os deja
valide, poses a la main, aucun credit Meshy). Cadrage identique a
idle/attaque/marche (cam_size=2.6, target_z=1.092).

4 poses (Brute = monstre LOURD, recoil_multiplier=0.35 dans
enemy_brute.tscn - "encaisse sans bouger" : AUCUNE pose "projete", et
les 3 poses "touche_*" utilisent des amplitudes de rotation reduites
d'environ moitie par rapport a Crawler/Ranged - la difference de poids
doit se voir aussi dans l'ampleur de la pose, pas seulement dans le
recul physique deja pilote par recoil_multiplier) :
  - touche_lateral : canonique = coup venu de la DROITE (recoil vers la
    gauche) - enemy.gd applique flip_h pour le coup venu de la gauche.
  - touche_avant : coup venu de face - encaisse, buste recule un peu.
  - touche_arriere : coup venu de dos - encaisse, buste avance un peu.
  - chancelle : pose de chancellement (enchainement de coups) - enemy.gd
    fait alterner flip_h a cadence fixe pendant State.STAGGER.
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


POSES = {
    "touche_lateral": {  # canonique : coup venu de la droite, recul vers la gauche (amplitude reduite - lourd)
        "pelvis": (0, 0, 9), "chest": (0, 0, 12), "neck": (4, 0, -10), "head": (0, 0, -6),
        "arm_R_upper": (-14, 0, 12), "arm_R_lower": (10, 0, 0),
        "leg_R_upper": (-8, 0, 0),
    },
    "touche_avant": {  # coup de face, encaisse en reculant a peine
        "chest": (-9, 0, 0), "neck": (9, 0, 0), "head": (5, 0, 0),
        "arm_L_upper": (-11, 0, 6), "arm_R_upper": (-11, 0, -6),
        "leg_L_upper": (-7, 0, 0), "leg_R_upper": (-7, 0, 0),
        "pelvis": (7, 0, 0),
    },
    "touche_arriere": {  # coup de dos, encaisse en avancant a peine
        "chest": (10, 0, 0), "neck": (-8, 0, 0), "head": (-5, 0, 0),
        "arm_L_upper": (7, 0, 4), "arm_R_upper": (7, 0, -4),
        "leg_L_upper": (6, 0, 0), "leg_R_upper": (6, 0, 0),
        "pelvis": (-6, 0, 0),
    },
    "chancelle": {  # chancellement (enchainement de coups) - plus marque qu'un seul coup encaisse
        "chest": (0, 0, 14), "pelvis": (0, 0, -9),
        "arm_L_upper": (-16, 0, 6), "arm_R_upper": (18, 0, -6),
        "leg_L_upper": (9, 0, 0), "leg_R_upper": (-6, 0, 0),
        "neck": (10, 0, 9), "head": (4, 0, 6),
    },
}

os.makedirs(out_dir, exist_ok=True)
for pose_name, bones in POSES.items():
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
print("HIT_REACTIONS_RENDER_DONE", len(POSES))
