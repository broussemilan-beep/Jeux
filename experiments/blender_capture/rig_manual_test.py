"""Test de rig manuel low-tech pour Crawler : construit une armature
simple (colonne+cou+tete, queue, 4 pattes a 2 segments) alignee a la
main sur le maillage remeshe (mesure via inspect_mesh.py), parente en
ARMATURE_AUTO (ponderation automatique de Blender, pas de peinture
manuelle), puis tourne un os de patte pour verifier que la deformation
reste propre. Alternative au rig auto Meshy qui echoue sur ce maillage
(422 Pose estimation failed) a cause de la posture quadrupede/accroupie
fidele a la reference.

Coordonnees bone tirees de inspect_mesh.py sur crawler_remeshed.glb :
  - tete (extremite museau, centree en X) : y=-1.29, z=0.26
  - pattes avant (griffes ecartees) : y=-1.0, x=+-0.65, z=0.0 (sol)
  - pic dorsal (sommet arche) : y=0.19, z=0.90
  - queue/arriere-train bas (extremite arriere, centree en X) : y=1.29, z=0.11
  - pattes arriere (estimees depuis l'elargissement des tranches
    y=0.65-0.9) : y=0.8, x=+-0.35, z=0.0 (sol)
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

# --- Nettoyage mesh AVANT armature ---------------------------------------
# Le remesh Meshy laisse ~50% de sommets dupliques (probablement un
# sous-produit du remesh par shell/face), ce qui fait totalement
# echouer le solveur "Bone Heat Weighting" de Blender (0.000 partout,
# silencieusement, seul un warning console le signale). Merge by
# distance + recalcul des normales avant de parenter resout le probleme
# (verifie : 282419 -> 130118 sommets, poids ensuite corrects sur les 13
# groupes, max ~0.9-1.0 chacun).
bpy.context.view_layer.objects.active = mesh_obj
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.remove_doubles(threshold=0.0001)
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode="OBJECT")

# --- Construction de l'armature ---------------------------------------
arm_data = bpy.data.armatures.new("CrawlerArmature")
arm_obj = bpy.data.objects.new("CrawlerArmature", arm_data)
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


# Colonne : bassin -> epaule/poitrine -> cou -> tete
pelvis = add_bone("pelvis", (0, 0.55, 0.40), (0, 0.15, 0.55))
chest = add_bone("chest", (0, 0.15, 0.55), (0, -0.45, 0.55), parent=pelvis)
neck = add_bone("neck", (0, -0.45, 0.55), (0, -0.85, 0.40), parent=chest)
head = add_bone("head", (0, -0.85, 0.40), (0, -1.29, 0.26), parent=neck)
tail = add_bone("tail", (0, 0.55, 0.40), (0, 1.29, 0.11), parent=pelvis)

# Pattes avant (attachees au chest), 2 segments (cuisse+patte basse)
for side, sx in (("L", -1), ("R", 1)):
    hip = add_bone(f"front_{side}_upper", (sx * 0.30, -0.55, 0.50), (sx * 0.45, -0.80, 0.25), parent=chest)
    add_bone(f"front_{side}_lower", (sx * 0.45, -0.80, 0.25), (sx * 0.55, -1.00, 0.0), parent=hip)

# Pattes arriere (attachees au pelvis), 2 segments
for side, sx in (("L", -1), ("R", 1)):
    hip = add_bone(f"back_{side}_upper", (sx * 0.25, 0.55, 0.45), (sx * 0.35, 0.75, 0.20), parent=pelvis)
    add_bone(f"back_{side}_lower", (sx * 0.35, 0.75, 0.20), (sx * 0.35, 0.85, 0.0), parent=hip)

bpy.ops.object.mode_set(mode="OBJECT")

# --- Parentage avec ponderation automatique -----------------------------
bpy.ops.object.select_all(action="DESELECT")
mesh_obj.select_set(True)
arm_obj.select_set(True)
bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.parent_set(type="ARMATURE_AUTO")

# --- Rendu utilitaire ----------------------------------------------------
def setup_render(out_path, res=512, samples=24):
    scene = bpy.context.scene
    for cam in [o for o in scene.objects if o.type == "CAMERA"]:
        bpy.data.objects.remove(cam, do_unlink=True)
    for light in [o for o in scene.objects if o.type == "LIGHT"]:
        bpy.data.objects.remove(light, do_unlink=True)

    cam_data = bpy.data.cameras.new("TestCam")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 3.2
    cam_obj = bpy.data.objects.new("TestCam", cam_data)
    scene.collection.objects.link(cam_obj)
    yaw, pitch = math.radians(35), math.radians(20)
    direction = mathutils.Vector((math.sin(yaw) * math.cos(pitch), -math.cos(yaw) * math.cos(pitch), math.sin(pitch)))
    center = mathutils.Vector((0, 0, 0.4))
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


# Rendu au repos (bind pose)
setup_render(out_render_rest)
print("RENDER_REST_SAVED", out_render_rest)

# --- Test de deformation : tourner la patte avant gauche ----------------
bpy.ops.object.select_all(action="DESELECT")
bpy.context.view_layer.objects.active = arm_obj
arm_obj.select_set(True)
bpy.ops.object.mode_set(mode="POSE")
pb = arm_obj.pose.bones["front_L_upper"]
pb.rotation_mode = "XYZ"
pb.rotation_euler = (math.radians(70), math.radians(40), math.radians(50))
pb2 = arm_obj.pose.bones["front_L_lower"]
pb2.rotation_mode = "XYZ"
pb2.rotation_euler = (math.radians(-60), math.radians(30), math.radians(20))
bpy.ops.object.mode_set(mode="OBJECT")

setup_render(out_render_posed)
print("RENDER_POSED_SAVED", out_render_posed)

# --- Export GLB (avec armature + skin, bind pose) -----------------------
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
