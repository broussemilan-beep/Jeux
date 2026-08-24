"""MANDAT CORRECTION PILOTE ROUND 2, point 2 - diagnostic de l'echarde
residuelle a la hanche. Meme methodologie que inspect_shard_weights.py
(round 1) : deplacement anormal bind->contact, poids de squelette des
sommets les plus deplaces - mais applique APRES le fix round 1
(fix_shoulder_hem_skinning / rebind_abducted), pour diagnostiquer l'etat
ACTUEL du pipeline (celui qui a produit combo_render_v2), pas l'etat
d'avant-fix deja documente.

Usage:
    blender --background --factory-startup --python inspect_hip_shard.py -- \
        <glb_path> <contact_frame>
"""
import bpy
import sys
import math


argv = sys.argv[sys.argv.index("--") + 1:]
glb_path = argv[0]
contact_frame = int(argv[1]) if len(argv) > 1 else 16

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=glb_path)

armature = None
mesh_obj = None
for obj in bpy.context.scene.objects:
    if obj.type == "ARMATURE":
        armature = obj
    if obj.type == "MESH" and obj.name.lower() != "icosphere":
        if mesh_obj is None or len(obj.data.vertices) > len(mesh_obj.data.vertices):
            mesh_obj = obj
assert armature is not None
assert mesh_obj is not None


def fix_shoulder_hem_skinning(armature, mesh_obj):
    """Copie EXACTE de la fonction de meme nom dans render_combo_cendre.py
    (le fix round 1 deja committe / 7421ff1) - pour diagnostiquer l'etat
    du mesh APRES ce fix, pas avant."""
    orig_parent_inverse = mesh_obj.matrix_parent_inverse.copy()

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

    bpy.context.view_layer.objects.active = mesh_obj
    bpy.ops.object.select_all(action="DESELECT")
    mesh_obj.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.remove_doubles(threshold=0.0001)
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT")

    bpy.ops.object.select_all(action="DESELECT")
    mesh_obj.select_set(True)
    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.parent_set(type="ARMATURE_AUTO")

    mesh_obj.matrix_parent_inverse = orig_parent_inverse

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
    print("FIX_SHOULDER_HEM_SKINNING_APPLIED (diagnostic replica)")


fix_shoulder_hem_skinning(armature, mesh_obj)

action = bpy.data.actions[0]
if armature.animation_data is None:
    armature.animation_data_create()
armature.animation_data.action = action

scene = bpy.context.scene


def eval_positions(frame):
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()
    eval_obj = mesh_obj.evaluated_get(dg)
    mesh = eval_obj.to_mesh()
    positions = [eval_obj.matrix_world @ v.co for v in mesh.vertices]
    eval_obj.to_mesh_clear()
    return positions


pos_bind = eval_positions(1)
pos_contact = eval_positions(contact_frame)

vgroups = mesh_obj.vertex_groups
vg_by_index = {vg.index: vg.name for vg in vgroups}

disp = []
for i, (a, b) in enumerate(zip(pos_bind, pos_contact)):
    d = (b - a).length
    disp.append((d, i))

disp.sort(reverse=True)
print("TOP_DISPLACEMENT_VERTS_POST_FIX (frame1 -> frame%d)" % contact_frame)
seen_weight_summary = {}
for d, i in disp[:40]:
    v = mesh_obj.data.vertices[i]
    weights = sorted(
        [(vg_by_index.get(g.group, "?"), round(g.weight, 3)) for g in v.groups],
        key=lambda x: -x[1],
    )
    print(f"  vert={i} displacement={d:.3f} bind_pos={tuple(round(x,3) for x in pos_bind[i])} contact_pos={tuple(round(x,3) for x in pos_contact[i])} weights={weights}")
    for name, w in weights:
        seen_weight_summary[name] = seen_weight_summary.get(name, 0) + 1

print("BONE_FREQUENCY_IN_TOP40", seen_weight_summary)

threshold = 0.5
dominant_bone_count = {}
count_over = 0
for d, i in disp:
    if d < threshold:
        break
    count_over += 1
    v = mesh_obj.data.vertices[i]
    if not v.groups:
        dominant_bone_count["NONE"] = dominant_bone_count.get("NONE", 0) + 1
        continue
    dom = max(v.groups, key=lambda g: g.weight)
    name = vg_by_index.get(dom.group, "?")
    dominant_bone_count[name] = dominant_bone_count.get(name, 0) + 1

print(f"VERTS_OVER_THRESHOLD_{threshold}", count_over)
print("DOMINANT_BONE_DISTRIBUTION", dominant_bone_count)

scene.frame_set(1)
bpy.context.view_layer.update()
for bname in ["Hips", "Spine", "RightUpLeg", "LeftUpLeg", "RightHand", "LeftHand",
              "RightArm", "LeftArm", "RightForeArm", "LeftForeArm"]:
    if bname not in armature.pose.bones:
        continue
    pb = armature.pose.bones[bname]
    head_w = armature.matrix_world @ pb.head
    tail_w = armature.matrix_world @ pb.tail
    print("BONE_WORLD", bname, "head=", tuple(round(x, 3) for x in head_w), "tail=", tuple(round(x, 3) for x in tail_w))

# Vraie pose REST (T/A-pose du squelette) - espace du heat-weighting.
armature.data.pose_position = "REST"
bpy.context.view_layer.update()
dg_rest = bpy.context.evaluated_depsgraph_get()
dg_rest.update()
eval_obj_rest = mesh_obj.evaluated_get(dg_rest)
mesh_rest = eval_obj_rest.to_mesh()
pos_rest = [eval_obj_rest.matrix_world @ v.co for v in mesh_rest.vertices]
eval_obj_rest.to_mesh_clear()

print("FLAGGED_VERTS_TRUE_REST_POSITION (top 10 by displacement)")
for d, i in disp[:10]:
    print(f"  vert={i} rest_pos={tuple(round(x,3) for x in pos_rest[i])}")

for bname in ["Hips", "Spine", "RightUpLeg", "LeftUpLeg", "RightHand", "LeftHand"]:
    if bname not in armature.pose.bones:
        continue
    pb = armature.pose.bones[bname]
    head_w = armature.matrix_world @ pb.head
    print("BONE_TRUE_REST_WORLD", bname, "head=", tuple(round(x, 3) for x in head_w))
armature.data.pose_position = "POSE"
