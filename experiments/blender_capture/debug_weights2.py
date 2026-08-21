import bpy
import mathutils

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath='experiments/monsters_nuit/meshy_output_v2/crawler_remeshed.glb')
mesh_obj = None
for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        mesh_obj = obj
        break

# Nettoyage mesh avant heat-weighting (merge doubles + recalc normals) --
bpy.context.view_layer.objects.active = mesh_obj
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
before = len(mesh_obj.data.vertices)
bpy.ops.mesh.remove_doubles(threshold=0.0001)
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')
after = len(mesh_obj.data.vertices)
print('MERGE_DOUBLES', before, '->', after)

# Compte non-manifold edges pour diagnostic ------------------------------
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.mesh.select_non_manifold()
bpy.ops.object.mode_set(mode='OBJECT')
nonmanifold_count = sum(1 for v in mesh_obj.data.vertices if v.select)
print('NONMANIFOLD_VERTS', nonmanifold_count, '/', len(mesh_obj.data.vertices))

arm_data = bpy.data.armatures.new('A')
arm_obj = bpy.data.objects.new('A', arm_data)
bpy.context.scene.collection.objects.link(arm_obj)
bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='EDIT')
eb = arm_data.edit_bones


def add_bone(name, head, tail, parent=None):
    b = eb.new(name)
    b.head = mathutils.Vector(head)
    b.tail = mathutils.Vector(tail)
    if parent is not None:
        b.parent = parent
        b.use_connect = False
    return b


pelvis = add_bone("pelvis", (0, 0.55, 0.40), (0, 0.15, 0.55))
chest = add_bone("chest", (0, 0.15, 0.55), (0, -0.45, 0.55), parent=pelvis)
neck = add_bone("neck", (0, -0.45, 0.55), (0, -0.85, 0.40), parent=chest)
head = add_bone("head", (0, -0.85, 0.40), (0, -1.29, 0.26), parent=neck)
tail = add_bone("tail", (0, 0.55, 0.40), (0, 1.29, 0.11), parent=pelvis)
for side, sx in (("L", -1), ("R", 1)):
    hip = add_bone(f"front_{side}_upper", (sx * 0.30, -0.55, 0.50), (sx * 0.45, -0.80, 0.25), parent=chest)
    add_bone(f"front_{side}_lower", (sx * 0.45, -0.80, 0.25), (sx * 0.55, -1.00, 0.0), parent=hip)
for side, sx in (("L", -1), ("R", 1)):
    hip = add_bone(f"back_{side}_upper", (sx * 0.25, 0.55, 0.45), (sx * 0.35, 0.75, 0.20), parent=pelvis)
    add_bone(f"back_{side}_lower", (sx * 0.35, 0.75, 0.20), (sx * 0.35, 0.85, 0.0), parent=hip)
bpy.ops.object.mode_set(mode='OBJECT')

bpy.ops.object.select_all(action='DESELECT')
mesh_obj.select_set(True)
arm_obj.select_set(True)
bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.parent_set(type='ARMATURE_AUTO')

total_strong = 0
for vg in mesh_obj.vertex_groups:
    count_strong = 0
    max_w = 0.0
    for v in mesh_obj.data.vertices:
        for g in v.groups:
            if g.group == vg.index:
                if g.weight > 0.3:
                    count_strong += 1
                if g.weight > max_w:
                    max_w = g.weight
    total_strong += count_strong
    print(f"GROUP {vg.name}: strong_verts={count_strong} max_weight={max_w:.3f}")
print("TOTAL_STRONG_AFTER_CLEANUP", total_strong)
