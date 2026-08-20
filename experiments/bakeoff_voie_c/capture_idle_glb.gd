extends Node
## Bake-off Animation, Voie C — variante de capture_idle.gd qui charge un
## GLB EXTERNE (sortie Meshy AI) au lieu du proxy primitives
## (cendre_lowpoly.gd), pour un comparatif à égalité via le MÊME pipeline
## caméra/pixelisation (GARDE-FOU 1 : rendu de la pose idle SEULE avant
## toute animation). Voir capture_idle.gd pour la discipline de capture
## headless (fond alpha réel, gel avant lecture) — reprise à l'identique
## ici, seule la source du personnage change.

const PixelShader := preload("res://experiments/bakeoff_voie_c/pixel_quantize.gdshader")


func _ready() -> void:
	var args := _parse_args()
	var glb_path: String = args.get("glb", "")
	if glb_path == "":
		push_error("capture_idle_glb: --glb manquant.")
		get_tree().quit(1)
		return
	var internal_res: int = int(args.get("internal_res", "512"))
	var out_path: String = args.get("out", "/tmp/voie_c_glb_idle_raw.png")
	var cam_size: float = float(args.get("cam_size", "1.75"))
	var cam_yaw_deg: float = float(args.get("cam_yaw_deg", "35"))
	var cam_pitch_deg: float = float(args.get("cam_pitch_deg", "18"))
	var cam_y_offset: float = float(args.get("cam_y_offset", "0.0"))
	var model_yaw_deg: float = float(args.get("model_yaw_deg", "0.0"))
	var color_steps: int = int(args.get("color_steps", "8"))
	var dither_amount: float = float(args.get("dither_amount", "0.35"))
	var outline_thickness: float = float(args.get("outline_thickness", "3.0"))
	var target_pixels: int = int(args.get("target_pixels", "64"))

	var sub_viewport := SubViewport.new()
	sub_viewport.size = Vector2i(internal_res, internal_res)
	sub_viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	sub_viewport.own_world_3d = true
	sub_viewport.transparent_bg = true
	add_child(sub_viewport)

	var world := Node3D.new()
	sub_viewport.add_child(world)

	var env := Environment.new()
	env.background_mode = Environment.BG_CLEAR_COLOR
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.55, 0.55, 0.57)
	env.ambient_light_energy = 1.1
	var world_env := WorldEnvironment.new()
	world_env.environment = env
	world.add_child(world_env)

	var key_light := DirectionalLight3D.new()
	key_light.light_energy = 1.0
	key_light.rotation_degrees = Vector3(-55.0, -30.0, 0.0)
	world.add_child(key_light)

	var packed: PackedScene = load(glb_path)
	if packed == null:
		push_error("capture_idle_glb: impossible de charger '%s'." % glb_path)
		get_tree().quit(1)
		return
	var character: Node3D = packed.instantiate()
	character.rotation_degrees.y = model_yaw_deg
	world.add_child(character)
	await get_tree().physics_frame

	# Bounding box réelle du modèle importé (pas de total_height exposé
	# comme sur le proxy primitives) — parcourt tous les MeshInstance3D
	# pour cadrer la caméra de la même façon que cendre_lowpoly.gd. Pour un
	# mesh skinné, `global_transform` du MeshInstance3D ne reflète pas la
	# déformation par le squelette (aabb calculée au repos, potentiellement
	# minuscule si le nœud porteur du skin a une transform quasi-identité
	# pendant que la mise à l'échelle vit dans le Skeleton3D, constaté
	# empiriquement) — --char_center_x/y/z permettent un cadrage manuel de
	# secours si l'aabb calculée ne colle pas.
	if args.get("debug_dump", "0") == "1":
		_dump_tree(character, 0)

	var aabb := _compute_aabb(character)
	var total_height: float = aabb.size.y
	var char_center := Vector3(aabb.position.x + aabb.size.x * 0.5, aabb.position.y + total_height * 0.5, aabb.position.z + aabb.size.z * 0.5)
	if args.has("char_center_y"):
		char_center.y = float(args.get("char_center_y"))
	if args.has("char_center_x"):
		char_center.x = float(args.get("char_center_x"))
	if args.has("char_center_z"):
		char_center.z = float(args.get("char_center_z"))

	var cam := Camera3D.new()
	cam.projection = Camera3D.PROJECTION_ORTHOGONAL
	cam.size = cam_size
	cam.near = 0.05
	cam.far = 20.0
	var distance := 5.0
	var yaw := deg_to_rad(cam_yaw_deg)
	var pitch := deg_to_rad(cam_pitch_deg)
	var dir := Vector3(sin(yaw) * cos(pitch), sin(pitch), cos(yaw) * cos(pitch))
	cam.position = char_center + dir * distance + Vector3(0.0, cam_y_offset, 0.0)
	world.add_child(cam)
	cam.look_at(char_center + Vector3(0.0, cam_y_offset, 0.0), Vector3.UP)

	var shader_mat := ShaderMaterial.new()
	shader_mat.shader = PixelShader
	shader_mat.set_shader_parameter("target_x_pixel_count", target_pixels)
	shader_mat.set_shader_parameter("target_y_pixel_count", target_pixels)
	shader_mat.set_shader_parameter("color_steps", color_steps)
	shader_mat.set_shader_parameter("target_saturation", 0.10)
	shader_mat.set_shader_parameter("dither_amount", dither_amount)
	shader_mat.set_shader_parameter("outline_thickness", outline_thickness)

	var sub_viewport_2d := SubViewport.new()
	sub_viewport_2d.size = Vector2i(internal_res, internal_res)
	sub_viewport_2d.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	sub_viewport_2d.transparent_bg = true
	add_child(sub_viewport_2d)

	var display := TextureRect.new()
	display.texture = sub_viewport.get_texture()
	display.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	display.size = Vector2(internal_res, internal_res)
	if args.get("no_shader", "0") != "1":
		display.material = shader_mat
	sub_viewport_2d.add_child(display)

	for i in range(6):
		await get_tree().physics_frame

	get_tree().paused = true
	await get_tree().process_frame
	await get_tree().process_frame
	await get_tree().process_frame

	var img: Image = sub_viewport_2d.get_texture().get_image()
	var dir_path := out_path.get_base_dir()
	if dir_path != "" and not DirAccess.dir_exists_absolute(dir_path):
		DirAccess.make_dir_recursive_absolute(dir_path)
	var err := img.save_png(out_path)

	print("CAPTURE_RESULT ", JSON.stringify({
		"save_err": err, "out_path": out_path, "internal_res": internal_res,
		"total_height": total_height, "aabb_position": var_to_str(aabb.position), "aabb_size": var_to_str(aabb.size),
		"cam_size": cam_size, "cam_yaw_deg": cam_yaw_deg, "cam_pitch_deg": cam_pitch_deg,
		"model_yaw_deg": model_yaw_deg,
	}))
	get_tree().quit(0 if err == OK else 1)


## Boîte englobante réelle (espace monde) de tous les MeshInstance3D sous
## `node`, fusionnés — pas d'équivalent "total_height" exposé par un GLB
## importé comme sur le proxy primitives (cendre_lowpoly.gd), donc calculé
## ici directement depuis la géométrie pour cadrer la caméra pareil.
func _compute_aabb(node: Node) -> AABB:
	var meshes: Array[MeshInstance3D] = []
	_collect_mesh_instances(node, meshes)
	if meshes.is_empty():
		return AABB()
	var result: AABB = meshes[0].global_transform * meshes[0].get_aabb()
	for i in range(1, meshes.size()):
		result = result.merge(meshes[i].global_transform * meshes[i].get_aabb())
	return result


func _collect_mesh_instances(node: Node, out: Array[MeshInstance3D]) -> void:
	if node is MeshInstance3D and node.mesh != null:
		out.append(node)
	for child in node.get_children():
		_collect_mesh_instances(child, out)


## DEBUG isolation — dump du nœud/transform/aabb pour diagnostiquer une
## échelle inattendue sur un GLB importé (mesh skinné notamment).
func _dump_tree(node: Node, depth: int) -> void:
	var indent := "  ".repeat(depth)
	var extra := ""
	if node is MeshInstance3D:
		extra = " mesh_aabb=%s global_xform_origin=%s global_xform_basis_scale=%s" % [
			node.get_aabb() if node.mesh else "null",
			node.global_transform.origin,
			node.global_transform.basis.get_scale(),
		]
	elif node is Skeleton3D:
		extra = " bone_count=%d global_xform_origin=%s global_xform_basis_scale=%s" % [
			node.get_bone_count(), node.global_transform.origin, node.global_transform.basis.get_scale(),
		]
	print("%s%s (%s)%s" % [indent, node.name, node.get_class(), extra])
	for child in node.get_children():
		_dump_tree(child, depth + 1)


func _parse_args() -> Dictionary:
	var result := {}
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--") and arg.contains("="):
			var kv := arg.substr(2).split("=", true, 1)
			result[kv[0]] = kv[1]
	return result
