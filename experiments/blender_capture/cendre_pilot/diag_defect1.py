"""Diagnostic defaut 1 (bavure aux articulations, coup1 contact) - MANDAT
CORRECTION PILOTE CENDRE. Isole la cause par test, comme le diagnostic
Roll_Dodge (docs/worklog-archive-2026-08-18-a-2026-08-21.md) : rendu
comparatif d'une meme frame avant/apres chaque hypothese.

Usage:
    blender --background --factory-startup --python diag_defect1.py -- \
        --glb=cendre_combo.glb --out_dir=diag_defect1 \
        --mode=baseline|smooth|dupcheck \
        --frame=16 [--res=512] [--samples=32] \
        [--smooth_factor=0.5] [--smooth_iter=3] [--limit_total=4]

mode=baseline   : rend la frame telle quelle (aucune modif de poids).
mode=smooth     : applique vertex_group_limit_total puis
                   vertex_group_smooth sur TOUS les groupes de sommets
                   du mesh, puis rend la meme frame. Rapporte aussi le
                   nombre de sommets a >limit_total influences AVANT
                   correction (mesure objective du probleme, pas une
                   supposition).
mode=dupcheck   : compte les sommets avant/apres un remove_doubles de
                   test (sur une COPIE du mesh, ne modifie rien dans la
                   scene rendue) pour trancher l'hypothese "sommets
                   dupliques non fusionnes" sans imposer un remesh.
mode=rebind     : fusionne reellement les doublons (remove_doubles sur
                   le mesh) puis reparente ARMATURE_AUTO sur
                   l'armature existante (poids recalcules a neuf),
                   pose de bind forcee (REST) pour le heat-weight, puis
                   rend la meme frame.
"""
import bpy
import sys
import os
import math
import mathutils
import bmesh


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
mode = args.get("mode", "baseline")
frame = int(args.get("frame", "16"))
res = int(args.get("res", "512"))
samples = int(args.get("samples", "32"))
cam_size = float(args.get("cam_size", "2.2"))
yaw_deg = float(args.get("yaw_deg", "10"))
smooth_factor = float(args.get("smooth_factor", "0.5"))
smooth_iter = int(args.get("smooth_iter", "3"))
limit_total = int(args.get("limit_total", "4"))

os.makedirs(out_dir, exist_ok=True)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=glb_path)

armature = None
mesh_obj = None
for obj in bpy.context.scene.objects:
    if obj.type == "ARMATURE":
        armature = obj
    if obj.type == "MESH" and obj.name.lower() != "icosphere":
        # char1 (corps skinne) vs Icosphere (marqueur 42 sommets, non
        # skinne, deja ignore du bbox par IGNORE_MESH_NAMES plus bas) -
        # on prend le mesh avec le plus de sommets pour eviter de
        # tomber sur le mauvais objet si l'ordre d'iteration varie.
        if mesh_obj is None or len(obj.data.vertices) > len(mesh_obj.data.vertices):
            mesh_obj = obj
assert armature is not None
assert mesh_obj is not None
action = bpy.data.actions[0]
if armature.animation_data is None:
    armature.animation_data_create()
armature.animation_data.action = action

print("MESH_NAME", mesh_obj.name, "VERT_COUNT", len(mesh_obj.data.vertices))
print("VERTEX_GROUPS", [vg.name for vg in mesh_obj.vertex_groups])

# ---------------------------------------------------------------- dupcheck
if mode == "dupcheck":
    bm = bmesh.new()
    bm.from_mesh(mesh_obj.data)
    before = len(bm.verts)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
    after = len(bm.verts)
    bm.free()
    print(f"DUPCHECK before={before} after={after} removed={before - after} "
          f"pct_removed={100.0 * (before - after) / before:.3f}%")
    sys.exit(0)

# ---------------------------------------------------------------- influence report (toujours affiche, avant toute correction)
max_influences = 0
verts_over_limit = 0
total_influences = 0
for v in mesh_obj.data.vertices:
    n = len(v.groups)
    total_influences += n
    if n > max_influences:
        max_influences = n
    if n > limit_total:
        verts_over_limit += 1
print(f"INFLUENCE_REPORT max_influences_per_vertex={max_influences} "
      f"verts_over_limit_{limit_total}={verts_over_limit}/{len(mesh_obj.data.vertices)} "
      f"avg_influences={total_influences / len(mesh_obj.data.vertices):.2f}")

# ---------------------------------------------------------------- smooth (mode=smooth uniquement)
if mode == "smooth":
    bpy.context.view_layer.objects.active = mesh_obj
    bpy.ops.object.select_all(action="DESELECT")
    mesh_obj.select_set(True)
    bpy.ops.object.mode_set(mode="WEIGHT_PAINT")
    bpy.ops.object.vertex_group_limit_total(group_select_mode="ALL", limit=limit_total)
    bpy.ops.object.vertex_group_smooth(group_select_mode="ALL", factor=smooth_factor, repeat=smooth_iter, expand=0.0)
    bpy.ops.object.mode_set(mode="OBJECT")
    print(f"SMOOTH_APPLIED limit_total={limit_total} factor={smooth_factor} repeat={smooth_iter}")

# ---------------------------------------------------------------- rebind (mode=rebind uniquement)
# Hypothese "sommets dupliques non fusionnes" (piege Meshy deja rencontre,
# voir mandat) : fusion reelle des doublons (bpy.ops.mesh.remove_doubles,
# meme technique que rig_final_brute.py/rig_final_crawler.py) PUIS
# reparentage ARMATURE_AUTO sur l'armature EXISTANTE (celle qui porte deja
# l'action Punch_Combo, pas une armature reconstruite a la main - les noms
# d'os RightArm/LeftArm/etc. doivent rester identiques pour que l'action
# continue de s'appliquer) pour recalculer les poids a neuf sur la
# topologie nettoyee.
if mode == "rebind":
    before_verts = len(mesh_obj.data.vertices)

    # Le GLB Meshy encode le squelette dans un espace local demesure
    # (os a ~100 unites, cf. list_bones.py) compense par
    # matrix_parent_inverse sur le mesh - re-parenter ecrase cette
    # matrice et fait exploser l'echelle visuelle (mesure : bbox x100).
    # On capture l'original pour le restaurer APRES coup : parent_set
    # ne sert ici qu'a recalculer les POIDS (vertex groups), pas la
    # transform.
    orig_parent_inverse = mesh_obj.matrix_parent_inverse.copy()

    armature.data.pose_position = "REST"  # pose de bind pour un heat-weight correct, independant de la frame courante
    bpy.context.view_layer.update()

    bpy.context.view_layer.objects.active = mesh_obj
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.remove_doubles(threshold=0.0001)
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT")
    after_verts = len(mesh_obj.data.vertices)
    print(f"REBIND_REMOVE_DOUBLES before={before_verts} after={after_verts} removed={before_verts - after_verts}")

    bpy.ops.object.select_all(action="DESELECT")
    mesh_obj.select_set(True)
    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.parent_set(type="ARMATURE_AUTO")
    print("REBIND_ARMATURE_AUTO_DONE new_vgroups=", [vg.name for vg in mesh_obj.vertex_groups])

    mesh_obj.matrix_parent_inverse = orig_parent_inverse
    print("REBIND_PARENT_INVERSE_RESTORED")

    armature.data.pose_position = "POSE"
    bpy.context.view_layer.update()

# ---------------------------------------------------------------- rebind_abducted (mode=rebind_abducted uniquement)
# Cause reelle identifiee (voir inspect_shard_weights.py) : en VRAIE pose
# de repos (bras le long du corps), la main droite touche/frole l'ourlet
# de la tunique dechiree a hauteur de hanche -> le heat-weighting
# (proximite 3D) a colle ~950 sommets de l'ourlet a l'os RightHand
# (poids ~0.96-0.98) au lieu de Hips/RightUpLeg. Fix standard de
# rigging : recalculer les poids automatiques pendant que le bras est
# ECARTE du corps (le contact disparait, le heat-weighting retombe sur
# le bon os), PUIS remettre le bras a 0 (repos reel inchange) - la
# pose utilisee pour le calcul n'affecte que la QUALITE du calcul, pas
# les matrices de repos de l'armature.
if mode == "rebind_abducted":
    before_verts = len(mesh_obj.data.vertices)
    orig_parent_inverse = mesh_obj.matrix_parent_inverse.copy()

    armature.data.pose_position = "POSE"
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.select_all(action="DESELECT")
    armature.select_set(True)
    bpy.ops.object.mode_set(mode="POSE")
    for pb_name, euler_deg in (("RightArm", (90.0, 0.0, 0.0)), ("LeftArm", (-90.0, 0.0, 0.0))):
        pb = armature.pose.bones[pb_name]
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = tuple(math.radians(d) for d in euler_deg)
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.context.view_layer.update()
    print("REBIND_ABDUCTED_POSE_APPLIED RightArm=(90,0,0) LeftArm=(-90,0,0)")

    bpy.context.view_layer.objects.active = mesh_obj
    bpy.ops.object.select_all(action="DESELECT")
    mesh_obj.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.remove_doubles(threshold=0.0001)
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT")
    after_verts = len(mesh_obj.data.vertices)
    print(f"REBIND_ABDUCTED_REMOVE_DOUBLES before={before_verts} after={after_verts} removed={before_verts - after_verts}")

    bpy.ops.object.select_all(action="DESELECT")
    mesh_obj.select_set(True)
    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.parent_set(type="ARMATURE_AUTO")
    print("REBIND_ABDUCTED_ARMATURE_AUTO_DONE new_vgroups=", [vg.name for vg in mesh_obj.vertex_groups])

    mesh_obj.matrix_parent_inverse = orig_parent_inverse

    # Retour a la pose de repos reelle (0,0,0) - seul le CALCUL des
    # poids a utilise la pose ecartee, l'armature/l'action reprennent
    # leur etat normal.
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.select_all(action="DESELECT")
    armature.select_set(True)
    bpy.ops.object.mode_set(mode="POSE")
    for pb_name in ("RightArm", "LeftArm"):
        pb = armature.pose.bones[pb_name]
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = (0.0, 0.0, 0.0)
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.context.view_layer.update()
    print("REBIND_ABDUCTED_POSE_RESET")

# ---------------------------------------------------------------- camera/light (identique a render_combo_cendre.py)
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

scene.frame_set(1)
bpy.context.view_layer.update()
depsgraph = bpy.context.evaluated_depsgraph_get()
depsgraph.update()
_, mins0, maxs0 = compute_bbox(bpy.context.scene.objects, depsgraph)
target_z = mins0.z + cam_size * 0.42
print("BBOX_FRAME1", "mins=", tuple(mins0), "maxs=", tuple(maxs0), "target_z=", target_z)

scene.frame_set(frame)
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
dg.update()
center, mins, maxs = compute_bbox(bpy.context.scene.objects, dg)
print("BBOX_RENDER_FRAME", frame, "center=", tuple(center), "mins=", tuple(mins), "maxs=", tuple(maxs))
center.z = target_z
cam_obj.location = center + direction * 10.0
cam_obj.rotation_euler = (center - cam_obj.location).to_track_quat("-Z", "Y").to_euler()
print("CAM_LOCATION", tuple(cam_obj.location))

tag = f"frame{frame}_{mode}"
out_path = os.path.join(out_dir, f"{tag}.png")
scene.render.filepath = out_path
bpy.ops.render.render(write_still=True)
print("FRAME_RENDERED", tag, out_path)
