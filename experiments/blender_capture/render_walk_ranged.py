"""MANDAT AUTONOME v3 Phase 2 - marche Ranged : la marche est INCLUSE
gratuitement dans le rig Meshy deja paye (rig_task_id=01a024b4-...,
cf. data/meshy_usage.jsonl) - aucun credit supplementaire. Ce script
importe le GLB anime deja telecharge (Animation_Walking_withSkin.glb),
echantillonne N poses regulierement espacees sur le cycle et rend
chacune avec EXACTEMENT le cadrage deja etabli pour idle/attaque
Ranged (cam_size=2.6, target_z=1.092, cf. docs/worklog.md 2026-08-21)."""

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
n_frames = int(args.get("n_frames", "6"))
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
assert arm_obj is not None, "aucune armature trouvee dans le GLB anime"

action = arm_obj.animation_data.action if arm_obj.animation_data else None
assert action is not None, "aucune action trouvee sur l'armature (le GLB n'est pas anime)"
frame_start, frame_end = action.frame_range
print(f"ACTION_RANGE {frame_start} {frame_end}")


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


os.makedirs(out_dir, exist_ok=True)
for i in range(n_frames):
    t = frame_start + (frame_end - frame_start) * (i / n_frames)
    bpy.context.scene.frame_set(int(round(t)))
    bpy.context.view_layer.update()
    raw_path = os.path.join(out_dir, f"walk_raw_{i}.png")
    setup_render(raw_path)
    print("FRAME_RENDERED", i, raw_path)
    if with_normals:
        normal_path = os.path.join(out_dir, f"walk_normal_{i}.png")
        render_normal_pass(bpy.context.scene, normal_path)
        print("FRAME_NORMAL_RENDERED", i, normal_path)

print("WALK_RENDER_DONE", n_frames)
