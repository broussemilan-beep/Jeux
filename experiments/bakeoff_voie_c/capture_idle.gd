extends Node
## Bake-off Animation, Voie C — capture headless de la pose idle SEULE
## (GARDE-FOU 1 du mandat : rendu de validation avant toute animation).
## Même discipline de capture headless que tools/capture_scene.gd (xvfb +
## rendering-driver vulkan, geler puis attendre plusieurs process_frame
## avant de lire le viewport — voir _freeze_and_wait_render()).
##
## Fond = vrai alpha de SubViewport (transparent_bg), PAS un chroma key.
## Essayé d'abord en vert pur + knockout Python : raté, la désaturation
## du shader (target_saturation) s'applique AUSSI au fond avant qu'on
## puisse le repérer (vert plein -> gris pâle, plus vert du tout). Deux
## SubViewport imbriqués (3D transparent -> TextureRect+shader dans un
## 2D transparent) lus directement via get_texture().get_image() :
## contourne aussi le stretch/aspect fixe 640x360 du viewport racine du
## projet (project.godot), qui letterboxait la capture si on lisait
## get_viewport() de la fenêtre principale à la place.
##
## JETABLE dans son usage (script d'expérience, pas un outil permanent du
## jeu) mais PAS supprimé après coup comme les scripts capture_arena_scratch
## habituels : ce dossier experiments/bakeoff_voie_c/ EST le livrable de
## l'expérience, à garder tant que le comparatif n'est pas tranché.

const CendreLowPolyScript := preload("res://experiments/bakeoff_voie_c/cendre_lowpoly.gd")
const PixelShader := preload("res://experiments/bakeoff_voie_c/pixel_quantize.gdshader")


func _ready() -> void:
	var args := _parse_args()
	var internal_res: int = int(args.get("internal_res", "512"))
	var out_path: String = args.get("out", "/tmp/voie_c_idle_raw.png")
	# Cadrage caméra — voir docs/worklog_bakeoff.md pour la dérivation de
	# ces valeurs par rapport au gabarit réel (idle_south/0.png).
	var cam_size: float = float(args.get("cam_size", "1.55"))
	var cam_yaw_deg: float = float(args.get("cam_yaw_deg", "35"))
	var cam_pitch_deg: float = float(args.get("cam_pitch_deg", "18"))
	var cam_y_offset: float = float(args.get("cam_y_offset", "0.0"))
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

	var character := Node3D.new()
	character.set_script(CendreLowPolyScript)
	world.add_child(character)
	await get_tree().physics_frame  # laisse _ready() du perso peupler total_height

	var total_height: float = character.total_height
	var char_center := Vector3(0.0, total_height * 0.5, 0.0)

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
	if args.get("no_shader", "0") != "1":  # DEBUG isolation — bypasse le shader pour voir la géométrie 3D brute
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
		"total_height": total_height, "cam_size": cam_size,
		"cam_yaw_deg": cam_yaw_deg, "cam_pitch_deg": cam_pitch_deg, "cam_y_offset": cam_y_offset,
	}))
	get_tree().quit(0 if err == OK else 1)


func _parse_args() -> Dictionary:
	var result := {}
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--") and arg.contains("="):
			var kv := arg.substr(2).split("=", true, 1)
			result[kv[0]] = kv[1]
	return result
