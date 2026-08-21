"""Meme methode que rig_manual_test.py (Crawler), coordonnees
recalibrees pour Brute via inspect_mesh.py sur brute_remeshed.glb :

  - sommet du crane (pic) : y=-0.13, z=2.20
  - menton/machoire (extremite avant basse) : y=-1.16, z=1.31
  - mains/phalanges au sol (bras tres longs, posture "knuckle-walker") :
    x=+-1.37, y=-0.6, z=0.45
  - jambes courtes/reculees, tranches Y 0.20-0.97 : largeur X retrecit
    de 1.19 a 0.14, hauteur moyenne chute de 1.05 a 0.22 -> jambes
    fleachies sous le corps, pieds vers y=0.85-1.0
"""

import bpy
import sys
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
out_glb = args.get("out_glb", "/tmp/rig_test.glb")
out_render_rest = args.get("out_render_rest", "/tmp/rig_test_rest.png")
out_render_posed = args.get("out_render_posed", "/tmp/rig_test_posed.png")

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=glb_path)

mesh_obj = None
for obj in bpy.context.scene.objects:
    if obj.type == "MESH":
        mesh_obj = obj
        break
assert mesh_obj is not None, "aucun mesh trouve dans le GLB"

bpy.context.view_layer.objects.active = mesh_obj
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
before = len(mesh_obj.data.vertices)
bpy.ops.mesh.remove_doubles(threshold=0.0001)
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode="OBJECT")
print("MERGE_DOUBLES", before, "->", len(mesh_obj.data.vertices))

arm_data = bpy.data.armatures.new("BruteArmature")
arm_obj = bpy.data.objects.new("BruteArmature", arm_data)
bpy.context.scene.collection.objects.link(arm_obj)
bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode="EDIT")
eb = arm_data.edit_bones


def add_bone(name, head, tail, parent=None):
    b = eb.new(name)
    b.head = mathutils.Vector(head)
    b.tail = mathutils.Vector(tail)
    if parent is not None:
        b.parent = parent
        b.use_connect = False
    return b


# Colonne : bassin (hanches, y positif = arriere) -> poitrine -> cou -> tete
pelvis = add_bone("pelvis", (0, 0.7, 0.85), (0, 0.3, 1.3))
chest = add_bone("chest", (0, 0.3, 1.3), (0, -0.1, 1.85), parent=pelvis)
neck = add_bone("neck", (0, -0.1, 1.85), (0, -0.6, 1.75), parent=chest)
head = add_bone("head", (0, -0.6, 1.75), (0, -1.1, 1.3), parent=neck)

# Bras (tres longs, attaches a la poitrine, mains au sol)
for side, sx in (("L", -1), ("R", 1)):
    shoulder = add_bone(f"arm_{side}_upper", (sx * 0.6, -0.3, 1.7), (sx * 1.0, -0.5, 1.0), parent=chest)
    add_bone(f"arm_{side}_lower", (sx * 1.0, -0.5, 1.0), (sx * 1.35, -0.6, 0.45), parent=shoulder)

# Jambes (courtes, accroupies, attachees au bassin)
for side, sx in (("L", -1), ("R", 1)):
    hip = add_bone(f"leg_{side}_upper", (sx * 0.4, 0.5, 0.9), (sx * 0.5, 0.7, 0.5), parent=pelvis)
    add_bone(f"leg_{side}_lower", (sx * 0.5, 0.7, 0.5), (sx * 0.45, 0.85, 0.0), parent=hip)

bpy.ops.object.mode_set(mode="OBJECT")

bpy.ops.object.select_all(action="DESELECT")
mesh_obj.select_set(True)
arm_obj.select_set(True)
bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.parent_set(type="ARMATURE_AUTO")


def setup_render(out_path, res=512, samples=24):
    scene = bpy.context.scene
    for cam in [o for o in scene.objects if o.type == "CAMERA"]:
        bpy.data.objects.remove(cam, do_unlink=True)
    for light in [o for o in scene.objects if o.type == "LIGHT"]:
        bpy.data.objects.remove(light, do_unlink=True)

    cam_data = bpy.data.cameras.new("TestCam")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 3.8
    cam_obj = bpy.data.objects.new("TestCam", cam_data)
    scene.collection.objects.link(cam_obj)
    yaw, pitch = math.radians(35), math.radians(20)
    direction = mathutils.Vector((math.sin(yaw) * math.cos(pitch), -math.cos(yaw) * math.cos(pitch), math.sin(pitch)))
    center = mathutils.Vector((0, 0, 0.9))
    cam_obj.location = center + direction * 10.0
    cam_obj.rotation_euler = (center - cam_obj.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = cam_obj

    light_data = bpy.data.lights.new("L", type="SUN")
    light_data.energy = 3.0
    light_obj = bpy.data.objects.new("L", light_data)
    light_obj.rotation_euler = (math.radians(55), 0.0, math.radians(-30))
    scene.collection.objects.link(light_obj)

    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = False
    scene.view_layers[0].cycles.use_denoising = False
    scene.render.film_transparent = True
    scene.render.resolution_x = res
    scene.render.resolution_y = res
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = out_path
    bpy.ops.render.render(write_still=True)


setup_render(out_render_rest)
print("RENDER_REST_SAVED", out_render_rest)

# Test de deformation : tourner le bras gauche (le plus long/complexe)
bpy.ops.object.select_all(action="DESELECT")
bpy.context.view_layer.objects.active = arm_obj
arm_obj.select_set(True)
bpy.ops.object.mode_set(mode="POSE")
pb = arm_obj.pose.bones["arm_L_upper"]
pb.rotation_mode = "XYZ"
pb.rotation_euler = (math.radians(60), math.radians(30), math.radians(-40))
pb2 = arm_obj.pose.bones["arm_L_lower"]
pb2.rotation_mode = "XYZ"
pb2.rotation_euler = (math.radians(-50), math.radians(20), math.radians(30))
bpy.ops.object.mode_set(mode="OBJECT")

setup_render(out_render_posed)
print("RENDER_POSED_SAVED", out_render_posed)

bpy.ops.object.mode_set(mode="POSE")
pb.rotation_euler = (0, 0, 0)
pb2.rotation_euler = (0, 0, 0)
bpy.ops.object.mode_set(mode="OBJECT")
bpy.ops.object.select_all(action="SELECT")
try:
    bpy.ops.export_scene.gltf(filepath=out_glb, use_selection=True, export_animations=False)
    print("GLB_EXPORTED", out_glb)
except Exception as e:
    print("GLB_EXPORT_FAILED", repr(e))
    bpy.ops.wm.save_as_mainfile(filepath=out_glb.rsplit(".", 1)[0] + ".blend")
    print("BLEND_SAVED_INSTEAD", out_glb.rsplit(".", 1)[0] + ".blend")
