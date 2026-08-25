"""CHANTIER C (Monstres : animations d'interaction) - reactions au coup
Crawler : meme technique que pose_walk_crawler.py (rig manuel 13 os deja
valide, poses a la main, aucun credit Meshy - un quadrupede reste hors
de ce que l'auto-rig sait faire, gotcha deja documente). Cadrage
identique a idle/attaque/marche (cam_size=2.6, target_z=1.0878).

5 poses (Crawler = monstre LEGER, recoil_multiplier=1.6 dans
enemy_crawler.tscn - seul monstre a recevoir la pose "projete") :
  - touche_lateral : canonique = coup venu de la DROITE (recoil vers la
    gauche) - enemy.gd applique flip_h pour le coup venu de la gauche
    (miroir), meme convention que le flip_h deja utilise pour le
    deplacement.
  - touche_avant : coup venu de face (le joueur est devant, cote "sud"
    de l'ecran) - se cabre en arriere.
  - touche_arriere : coup venu de dos (cote "nord") - bascule en avant.
  - chancelle : pose de chancellement (enchainement de coups) - enemy.gd
    fait alterner flip_h a cadence fixe pendant State.STAGGER pour
    simuler un vacillement gauche-droite sans frame supplementaire.
  - projete : pose aerienne/recroquevillee jouee au debut d'un recul
    de projection (recoil_total_distance_px au-dessus du seuil "leger").
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
target_z = float(args.get("target_z", "1.0878"))
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
    "touche_lateral": {  # canonique : coup venu de la droite, recul vers la gauche
        "pelvis": (0, 0, 20), "chest": (0, 0, 16), "neck": (8, 0, -22), "head": (0, 0, -10),
        "front_R_upper": (-25, 0, 0), "front_R_lower": (35, 0, 0),
        "back_R_upper": (-14, 0, 0),
        "front_L_upper": (10, 0, 0),
        "tail": (0, 0, -26),
    },
    "touche_avant": {  # coup de face, se cabre en arriere
        "neck": (26, 0, 0), "head": (14, 0, 0),
        "front_L_upper": (-32, 0, 0), "front_L_lower": (22, 0, 0),
        "front_R_upper": (-32, 0, 0), "front_R_lower": (22, 0, 0),
        "pelvis": (14, 0, 0), "tail": (18, 0, 0),
    },
    "touche_arriere": {  # coup de dos, bascule en avant
        "neck": (-24, 0, 0), "head": (-12, 0, 0),
        "front_L_upper": (18, 0, 0), "front_L_lower": (-14, 0, 0),
        "front_R_upper": (18, 0, 0), "front_R_lower": (-14, 0, 0),
        "back_L_upper": (-16, 0, 0), "back_R_upper": (-16, 0, 0),
        "pelvis": (-12, 0, 0), "tail": (-16, 0, 0),
    },
    "chancelle": {  # chancellement (enchainement de coups), pose asymetrique deliberee
        "front_L_upper": (-16, 0, 0), "front_R_upper": (22, 0, 0),
        "back_L_upper": (11, 0, 0), "back_R_upper": (-9, 0, 0),
        "neck": (6, 0, 16), "head": (0, 0, 10),
        "pelvis": (0, 0, 8), "tail": (0, 0, -12),
    },
    "projete": {  # aerien/recroqueville - debut d'un recul de projection (leger uniquement)
        "front_L_upper": (42, 0, 0), "front_L_lower": (-42, 0, 0),
        "front_R_upper": (42, 0, 0), "front_R_lower": (-42, 0, 0),
        "back_L_upper": (40, 0, 0), "back_L_lower": (-38, 0, 0),
        "back_R_upper": (40, 0, 0), "back_R_lower": (-38, 0, 0),
        "pelvis": (0, 0, 12), "neck": (-22, 0, 0), "head": (-10, 0, 0),
        "tail": (0, 0, 32),
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
