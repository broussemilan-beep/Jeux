extends Node2D
## Capture headless d'une pose du Player, pour vérifier À L'ŒIL le pivot
## bas-centre (§6.3) après le passage de scripts/cook_character_frames.py
## — les checks logiques de smoke_test_gameplay.gd prouvent que l'état
## anime bien (idle/déplacement/etc.), pas que les pieds tombent au bon
## endroit visuellement. Mêmes techniques de capture prouvées en Phase 0
## (tools/capture_scene.gd) : pause + 3 process_frame avant lecture du
## viewport.
##
## --anim=idle --out=/chemin/absolu.png

const PlayerScene := preload("res://scenes/gameplay/player.tscn")


func _ready() -> void:
	var args := _parse_args()
	var anim_name: String = args.get("anim", "idle")
	var out_path: String = args.get("out", "")
	if out_path == "":
		push_error("capture_player_pose: --out manquant.")
		get_tree().quit(1)
		return

	var player := PlayerScene.instantiate()
	player.global_position = Vector2(320, 260)
	add_child(player)

	# Repère visuel : ligne horizontale au niveau du sol (y du node Player,
	# donc des pieds si le pivot §6.3 est correct) pour juger l'alignement
	# d'un coup d'œil sur le PNG exporté.
	var ground := Node2D.new()
	add_child(ground)
	ground.z_index = 200
	ground.draw.connect(func():
		ground.draw_line(Vector2(0, 260), Vector2(640, 260), Color.RED, 1.0)
	)
	ground.queue_redraw()

	var sprite: AnimatedSprite2D = player.get_node("AnimatedSprite2D")
	sprite.play(anim_name)

	await get_tree().physics_frame
	await get_tree().physics_frame

	get_tree().paused = true
	await get_tree().process_frame
	await get_tree().process_frame
	await get_tree().process_frame

	var img: Image = get_viewport().get_texture().get_image()
	var dir_path := out_path.get_base_dir()
	if dir_path != "" and not DirAccess.dir_exists_absolute(dir_path):
		DirAccess.make_dir_recursive_absolute(dir_path)
	var err := img.save_png(out_path)
	print("CAPTURE_RESULT ", JSON.stringify({"save_err": err, "out_path": out_path, "anim": anim_name}))
	get_tree().quit(0 if err == OK else 1)


func _parse_args() -> Dictionary:
	var result := {}
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--") and arg.contains("="):
			var kv := arg.substr(2).split("=", true, 1)
			result[kv[0]] = kv[1]
	return result
