import bpy, sys
argv = sys.argv
argv = argv[argv.index('--')+1:] if '--' in argv else []
glb_path, out_path = argv[0], argv[1]
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=glb_path)
img = bpy.data.images['texture_0']
img.filepath_raw = out_path
img.file_format = 'PNG'
img.save()
print('SAVED_TEXTURE', out_path)
