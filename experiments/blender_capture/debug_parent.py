import bpy

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath='experiments/monsters_nuit/meshy_output_v2/crawler_remeshed.glb')
mesh_obj = None
for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        mesh_obj = obj
        break
print('MESH_NAME', mesh_obj.name, 'verts', len(mesh_obj.data.vertices))

arm_data = bpy.data.armatures.new('A')
arm_obj = bpy.data.objects.new('A', arm_data)
bpy.context.scene.collection.objects.link(arm_obj)
bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='EDIT')
eb = arm_data.edit_bones
b1 = eb.new('front_L_upper')
b1.head = (-0.30, -0.55, 0.50)
b1.tail = (-0.45, -0.80, 0.25)
bpy.ops.object.mode_set(mode='OBJECT')

bpy.ops.object.select_all(action='DESELECT')
mesh_obj.select_set(True)
arm_obj.select_set(True)
bpy.context.view_layer.objects.active = arm_obj
print('BEFORE parent_set, mesh modifiers:', list(mesh_obj.modifiers.keys()))
try:
    result = bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    print('parent_set result:', result)
except Exception as e:
    print('PARENT_SET_EXCEPTION', repr(e))
print('AFTER parent_set, mesh modifiers:', list(mesh_obj.modifiers.keys()))
print('mesh parent:', mesh_obj.parent)
print('vertex groups:', [vg.name for vg in mesh_obj.vertex_groups])
