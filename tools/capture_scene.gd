extends Node2D
## Scène de capture headless — docs/ARCHITECTURE_VFX_v3.md §13.3.
##
## "Scène de capture dédiée tools/capture_scene.tscn : charge une
## recette/animation, seed fixée, joue, exporte les frames en PNG
## (get_viewport().get_texture().get_image().save_png()) [...] Lancée par
## scripts/capture_headless.sh."
##
## Trois modes, un seul point d'entrée (jamais deux scènes de capture qui
## dupliqueraient la technique pause+3×process_frame ci-dessous) :
##
## --mode=primitive (par défaut, Phase 0) : capture UNE primitive nommée
##   à UN tick donné.
##   --primitive=impactFlashFrame   nom de primitive (VfxDirector._registry)
##   --seed=44102                   seed déterministe (traçabilité replay)
##   --tick=1                       tick physique auquel capturer
##   --lifetime_ticks=2             durée de vie donnée à la primitive (def. 2,
##                                  §4 "1-2 ticks" d'impactFlashFrame) — augmenter
##                                  pour capturer un tick significatif d'une
##                                  primitive à la durée de vie naturellement plus
##                                  longue (D, tranche 3 : spiral/orbital/etc.),
##                                  sinon le director la libère avant --tick.
##   --out=/chemin/absolu/sortie.png
##
## --mode=character (Phase 1.3+) : instancie le Player, joue une
##   animation nommée, capture une frame précise de cette animation.
##   --anim=idle_south               nom d'animation (SpriteFrames du Player) —
##                                  idle/déplacement sont désormais 8 rotations
##                                  réelles (E, mandat §6) : idle_south,
##                                  idle_north, idle_east, idle_west,
##                                  idle_south_east, idle_south_west,
##                                  idle_north_east, idle_north_west (et
##                                  déplacement_<même liste>) — coup1/2/3,
##                                  dash, hurt, mort restent "sud" seul.
##   --frame=0                      index de frame à capturer dans cette animation
##   --out=/chemin/absolu/sortie.png
##   --background=neutral|loaded    §13.2 "fond neutre + fond chargé" (def. neutral)
##   --scale=1|2|4                  §13.2 "1×/2×/4×" (def. 1), upscale NEAREST post-capture
##   Pas de RNG ici (frames PixelLab pré-cuites, pas de primitive
##   procédurale) donc --seed n'a pas de sens ; la traçabilité vient du
##   character_id/animation_group_id loggés dans data/pixellab_usage.jsonl.
##
##   "fond chargé" (§13.2) : aucun décor de jeu réel n'existe encore en
##   Phase 1 (pas de tuiles/salle) — matérialisé ici par un damier de test
##   généré procéduralement (_make_loaded_background), pas un asset final.
##   À remplacer par un vrai décor quand Phase 2+ apportera des tuiles.
##
## --mode=power (Phase 1.5+) : instancie une scène de pouvoir
##   (res://scenes/gameplay/powers/<power>.tscn), laisse la physique RÉELLE
##   tourner jusqu'à un tick donné (la créature pilote son propre cast en
##   autonome, contrairement au mode character qui pose juste une frame
##   figée), gèle puis capture — nécessaire ici car le mode character ne
##   gère pas une entité qui se détruit elle-même (queue_free) en fin de vie.
##   --power=gueule_vide            nom de la scène (scenes/gameplay/powers/<power>.tscn)
##   --tick=2                       tick physique auquel capturer (< durée totale du cast)
##   --background=neutral|loaded, --scale=1|2|4  mêmes conventions que character.
##   --out=/chemin/absolu/sortie.png
##
## --mode=player_action (D, Bras-Faux) : instancie le Player RÉEL (pas une
##   scène de pouvoir séparée) et simule une pression d'input via
##   Input.action_press/release — nécessaire pour toute action portée par
##   player.gd lui-même (Bras-Faux, esquive, dash, combo) plutôt que par
##   une scène de créature autonome comme Gueule Vide. Place aussi 2
##   ennemis (front + côté, mêmes offsets que _check_bras_faux() du smoke
##   test) pour rendre visible le recul multi-cible, pas juste le VFX seul.
##   --action=power2                 nom de l'InputMap action à presser 1 frame
##   --tick=16                       tick physique auquel capturer (compté
##                                    depuis la pression, pas depuis _ready())
##   --background=neutral|loaded, --scale=1|2|4  mêmes conventions que character.
##   --out=/chemin/absolu/sortie.png
##
## Voir CLAUDE.md "Environnement de capture — écart documenté" : cette
## scène elle-même ne sait rien de xvfb/Vulkan logiciel — c'est
## scripts/capture_headless.sh qui choisit COMMENT lancer Godot. Ce
## fichier reste portable vers un vrai `--headless` le jour où ça
## fonctionnera dans l'environnement d'exécution.

const PlayerScene := preload("res://scenes/gameplay/player.tscn")
const EnemyScene := preload("res://scenes/gameplay/enemy.tscn")


func _ready() -> void:
	var args := _parse_args()
	var mode: String = args.get("mode", "primitive")
	if mode == "character":
		await _run_character_capture(args)
	elif mode == "power":
		await _run_power_capture(args)
	elif mode == "player_action":
		await _run_player_action_capture(args)
	elif mode == "scene":
		await _run_scene_capture(args)
	else:
		await _run_primitive_capture(args)


## --mode=scene (Chantier B, vérification décor) : instancie une scène
## RÉELLE quelconque (res://scenes/...) via une Camera2D positionnée à la
## demande, laisse tourner quelques ticks si besoin, capture — pour
## vérifier un décor (TileMapLayer, props) sans dépendre d'un mode dédié
## par écran. Pas un remplacement des modes existants (character/power/
## player_action restent la référence pour le personnage/les pouvoirs) :
## seulement pour des scènes qui n'ont pas encore de mode spécifique.
##   --scene_path=res://scenes/gameplay/gate_premiere.tscn
##   --cam_x=640 --cam_y=300 --cam_zoom=1.0
##   --wait_ticks=1                 ticks physiques avant capture (def. 1)
##   --background=neutral|loaded, --scale=1|2|4  mêmes conventions qu'ailleurs.
##   --use_scene_camera=1           Phase R4 (BASE_ZOOM permanent) : n'injecte
##                                  PAS de Camera2D — laisse la caméra RÉELLE
##                                  de la scène (celle de Player, pilotée par
##                                  CameraDirector.get_zoom() à chaque tick)
##                                  rester active, pour vérifier le zoom de
##                                  base EN JEU RÉEL plutôt qu'un cam_zoom
##                                  choisi à la main qui l'écraserait. --cam_x/
##                                  y/zoom ignorés dans ce mode (def. 0/off).
##   --out=/chemin/absolu/sortie.png
func _run_scene_capture(args: Dictionary) -> void:
	var scene_path: String = args.get("scene_path", "")
	var out_path: String = args.get("out", "")
	var cam_x: float = float(args.get("cam_x", "320"))
	var cam_y: float = float(args.get("cam_y", "180"))
	var cam_zoom: float = float(args.get("cam_zoom", "1.0"))
	var wait_ticks: int = int(args.get("wait_ticks", "1"))
	var scale: int = int(args.get("scale", "1"))
	var use_scene_camera: bool = args.get("use_scene_camera", "0") == "1"
	if scene_path == "" or out_path == "":
		push_error("capture_scene[scene]: --scene_path et --out sont requis.")
		get_tree().quit(1)
		return
	if not ResourceLoader.exists(scene_path):
		push_error("capture_scene[scene]: scène introuvable '%s'." % scene_path)
		get_tree().quit(1)
		return

	var packed: PackedScene = load(scene_path)
	var instance: Node = packed.instantiate()
	add_child(instance)

	if not use_scene_camera:
		var cam := Camera2D.new()
		cam.position = Vector2(cam_x, cam_y)
		cam.zoom = Vector2(cam_zoom, cam_zoom)
		add_child(cam)
		cam.make_current()

	for i in range(wait_ticks):
		await get_tree().physics_frame

	await _freeze_and_wait_render()

	var img: Image = get_viewport().get_texture().get_image()
	if scale > 1:
		img.resize(img.get_width() * scale, img.get_height() * scale, Image.INTERPOLATE_NEAREST)
	var err := _save_png(img, out_path)

	var report := {
		"save_err": err, "out_path": out_path, "size": [img.get_width(), img.get_height()],
		"mode": "scene", "scene_path": scene_path, "use_scene_camera": use_scene_camera,
		"cam": [cam_x, cam_y, cam_zoom], "wait_ticks": wait_ticks, "scale": scale,
	}
	print("CAPTURE_RESULT ", JSON.stringify(report))
	get_tree().quit(0 if err == OK else 1)


func _run_player_action_capture(args: Dictionary) -> void:
	var action_name: String = args.get("action", "")
	var target_tick: int = int(args.get("tick", "16"))
	var out_path: String = args.get("out", "")
	var background: String = args.get("background", "neutral")
	var scale: int = int(args.get("scale", "1"))
	if action_name == "" or out_path == "":
		push_error("capture_scene[player_action]: --action et --out sont requis.")
		get_tree().quit(1)
		return
	if not InputMap.has_action(action_name):
		push_error("capture_scene[player_action]: action InputMap introuvable '%s'." % action_name)
		get_tree().quit(1)
		return

	if background == "loaded":
		add_child(_make_loaded_background())

	var player := PlayerScene.instantiate()
	player.global_position = Vector2(320, 200)
	player.facing = Vector2.RIGHT
	add_child(player)

	# Mêmes offsets que _check_bras_faux() (tools/smoke_test_gameplay.gd) :
	# un ennemi devant (0°, dans l'arc) et un sur le côté (30°, dans l'arc)
	# pour que le recul multi-cible soit visible dans la capture, pas
	# seulement le VFX seul sur une salle vide.
	var enemy_front := EnemyScene.instantiate()
	enemy_front.global_position = player.global_position + Vector2(30, 0)
	add_child(enemy_front)

	var enemy_side := EnemyScene.instantiate()
	var side_dir := Vector2.RIGHT.rotated(deg_to_rad(30.0))
	enemy_side.global_position = player.global_position + side_dir * 30.0
	add_child(enemy_side)

	await get_tree().physics_frame

	Input.action_press(action_name)
	await get_tree().physics_frame
	Input.action_release(action_name)

	# Compté depuis la pression (pas depuis _ready()) — même sonde par
	# comptage de physics_frame que le smoke test (_wait_until), la
	# physique RÉELLE du Player pilote son propre état, aucune horloge
	# externe à interroger comme VfxDirector.get_current_tick() en mode
	# primitive.
	var ticks_waited := 0
	while ticks_waited < target_tick:
		await get_tree().physics_frame
		ticks_waited += 1

	await _freeze_and_wait_render()

	var img: Image = get_viewport().get_texture().get_image()
	if scale > 1:
		img.resize(img.get_width() * scale, img.get_height() * scale, Image.INTERPOLATE_NEAREST)
	var err := _save_png(img, out_path)

	var report := {
		"save_err": err,
		"out_path": out_path,
		"size": [img.get_width(), img.get_height()],
		"mode": "player_action",
		"action": action_name,
		"tick": target_tick,
		"background": background,
		"scale": scale,
	}
	print("CAPTURE_RESULT ", JSON.stringify(report))
	get_tree().quit(0 if err == OK else 1)


func _run_power_capture(args: Dictionary) -> void:
	var power_name: String = args.get("power", "")
	var target_tick: int = int(args.get("tick", "2"))
	var out_path: String = args.get("out", "")
	var background: String = args.get("background", "neutral")
	var scale: int = int(args.get("scale", "1"))
	if power_name == "" or out_path == "":
		push_error("capture_scene[power]: --power et --out sont requis.")
		get_tree().quit(1)
		return

	var scene_path := "res://scenes/gameplay/powers/%s.tscn" % power_name
	if not ResourceLoader.exists(scene_path):
		push_error("capture_scene[power]: scène introuvable '%s'." % scene_path)
		get_tree().quit(1)
		return

	if background == "loaded":
		add_child(_make_loaded_background())

	var power_scene: PackedScene = load(scene_path)
	var instance: Node2D = power_scene.instantiate()
	instance.global_position = Vector2(320, 260)
	add_child(instance)

	# Physique RÉELLE (pas de pause avant le tick cible) : la créature
	# avance sa propre horloge en autonome — même sondage que
	# _run_primitive_capture() pour VfxDirector.get_current_tick(), avec
	# la même course déjà trouvée en Phase 0 (l'ordre entre la reprise
	# d'un `await physics_frame` et le `_physics_process` d'un AUTRE nœud
	# pour ce même pas n'est pas garanti).
	while is_instance_valid(instance) and instance.get_current_tick() < target_tick:
		await get_tree().physics_frame

	if not is_instance_valid(instance):
		push_warning("capture_scene[power]: '%s' s'est libéré avant le tick %d (durée de vie trop courte)." % [power_name, target_tick])

	await _freeze_and_wait_render()

	var img: Image = get_viewport().get_texture().get_image()
	if scale > 1:
		img.resize(img.get_width() * scale, img.get_height() * scale, Image.INTERPOLATE_NEAREST)
	var err := _save_png(img, out_path)

	var report := {
		"save_err": err,
		"out_path": out_path,
		"size": [img.get_width(), img.get_height()],
		"mode": "power",
		"power": power_name,
		"tick": target_tick,
		"background": background,
		"scale": scale,
	}
	print("CAPTURE_RESULT ", JSON.stringify(report))
	get_tree().quit(0 if err == OK else 1)


func _run_character_capture(args: Dictionary) -> void:
	var anim_name: String = args.get("anim", "idle_south")
	var frame_index: int = int(args.get("frame", "0"))
	var out_path: String = args.get("out", "")
	var background: String = args.get("background", "neutral")
	var scale: int = int(args.get("scale", "1"))
	if out_path == "":
		push_error("capture_scene[character]: --out manquant, rien à écrire.")
		get_tree().quit(1)
		return

	if background == "loaded":
		add_child(_make_loaded_background())

	var player := PlayerScene.instantiate()
	player.global_position = Vector2(320, 260)
	add_child(player)

	var sprite: AnimatedSprite2D = player.get_node("AnimatedSprite2D")
	sprite.play(anim_name)
	sprite.frame = frame_index
	sprite.pause()  # fige sur cette frame précise, jamais une capture "au hasard" du timing

	# PAS d'await physics_frame ici, volontairement : Player._physics_process
	# bascule automatiquement idle/deplacement selon le mouvement (aucune
	# entrée pressée pendant une capture) — le laisser tourner ne serait-ce
	# qu'un pas physique écraserait silencieusement l'anim demandée
	# (hurt/dash/mort) en la remettant sur "idle". L'état déjà posé
	# ci-dessus (frame gelée) est rendu correctement par les process_frame
	# de _freeze_and_wait_render() sans qu'aucune physique n'ait besoin de
	# tourner.
	await _freeze_and_wait_render()

	var img: Image = get_viewport().get_texture().get_image()
	if scale > 1:
		img.resize(img.get_width() * scale, img.get_height() * scale, Image.INTERPOLATE_NEAREST)
	var err := _save_png(img, out_path)

	var report := {
		"save_err": err,
		"out_path": out_path,
		"size": [img.get_width(), img.get_height()],
		"mode": "character",
		"anim": anim_name,
		"frame": frame_index,
		"frame_count": sprite.sprite_frames.get_frame_count(anim_name),
		"background": background,
		"scale": scale,
	}
	print("CAPTURE_RESULT ", JSON.stringify(report))
	get_tree().quit(0 if err == OK else 1)


## "fond chargé" (§13.2) : damier de test généré procéduralement — aucun
## décor de jeu réel n'existe encore en Phase 1 (voir note de tête de
## fichier). Motif déterministe (aucun RNG), deux tons neutres proches de
## la bande "decor" (data/palettes/value_bands.json) pour rester dans
## l'esprit d'un fond de jeu sans prétendre en être un.
func _make_loaded_background() -> Sprite2D:
	var vw: int = ProjectSettings.get_setting("display/window/size/viewport_width", 640)
	var vh: int = ProjectSettings.get_setting("display/window/size/viewport_height", 360)
	var img := Image.create(vw, vh, false, Image.FORMAT_RGBA8)
	const CELL := 16
	var tone_a := Color8(58, 56, 62, 255)
	var tone_b := Color8(84, 80, 74, 255)
	for y in range(vh):
		for x in range(vw):
			var cell_index := (x / CELL) + (y / CELL)
			img.set_pixel(x, y, tone_a if cell_index % 2 == 0 else tone_b)
	var sprite := Sprite2D.new()
	sprite.centered = false
	sprite.position = Vector2.ZERO
	sprite.texture = ImageTexture.create_from_image(img)
	return sprite


func _run_primitive_capture(args: Dictionary) -> void:
	var primitive_name: String = args.get("primitive", "impactFlashFrame")
	var seed_val: int = int(args.get("seed", "0"))
	var target_tick: int = int(args.get("tick", "1"))
	var out_path: String = args.get("out", "")
	# Défaut historique (2) gardé tel quel pour ne rien changer aux appels
	# existants — certaines primitives (D, tranche 3) ont une durée de vie
	# naturelle bien plus longue ; --lifetime_ticks permet de capturer un
	# tick significatif de LEUR propre timeline plutôt que de les figer
	# artificiellement à 2, ce qui les libérerait avant --tick demandé.
	var lifetime_ticks: int = int(args.get("lifetime_ticks", "2"))

	if out_path == "":
		push_error("capture_scene: --out manquant, rien à écrire.")
		get_tree().quit(1)
		return

	# Centre du viewport logique 640×360 (§0) — origine par défaut d'un
	# test isolé, aucun perso/salle n'existe encore en Phase 0.
	var origin := Vector2(320, 180)

	VfxDirector.clear_log()
	var node := VfxDirector.spawn(primitive_name, {
		"seed": seed_val,
		"origin": origin,
		"lifetime_ticks": lifetime_ticks,
		"overdraw_cost": 12.0,
	})
	if node == null:
		push_error("capture_scene: spawn refusé pour '%s' (budget ou primitive inconnue) — voir logs ci-dessus." % primitive_name)
		get_tree().quit(1)
		return

	# Avance jusqu'au tick demandé via le vrai pas physique (60/s, §0) —
	# jamais un délai réel (create_timer), qui dérive sous charge hôte.
	# EN SONDANT VfxDirector.get_current_tick(), pas en comptant les
	# `await physics_frame` un par un : trouvé pendant la validation
	# Phase 0 (docs/worklog.md) que le signal `physics_frame` peut
	# réveiller ce coroutine AVANT que VfxDirector._physics_process ait
	# fini de tourner pour ce même pas (ordre non garanti entre la
	# reprise d'un `await` et le traitement physique des autres nœuds).
	# Compter les réveils du signal comme s'ils valaient chacun un tick
	# VfxDirector était donc faux d'un cran, silencieusement — sonder
	# l'état RÉEL du compteur élimine la course au lieu de la masquer.
	while VfxDirector.get_current_tick() < target_tick:
		await get_tree().physics_frame

	# GÈLE la simulation avant d'attendre le rendu. Trouvé pendant la
	# validation Phase 0 (docs/worklog.md) : le pipeline de rendu de
	# Godot bufferise plusieurs images — un seul process_frame après le
	# tick cible capture une image pas encore rasterisée (fond par défaut
	# seul, VFX absent), mais attendre plusieurs process_frame SANS geler
	# laisse la physique continuer d'avancer (1 tick/frame avec
	# max_physics_steps_per_frame=1, project.godot) et tuait la primitive
	# de test (durée de vie 1-2 ticks, §4) avant même la capture. Geler
	# arrête net l'avancement des ticks (VfxDirector, un autoload,
	# n'échappe pas à la pause par défaut) SANS arrêter le rendu — la
	# redraw déjà posée par le dernier tick(...) continue d'être
	# rasterisée normalement pendant qu'on attend.
	await _freeze_and_wait_render()

	var img: Image = get_viewport().get_texture().get_image()
	var err := _save_png(img, out_path)

	var log_entry: Dictionary = VfxDirector.spawn_log[0] if VfxDirector.spawn_log.size() > 0 else {}
	var report := {
		"save_err": err,
		"out_path": out_path,
		"size": [img.get_width(), img.get_height()],
		"primitive": primitive_name,
		"seed": seed_val,
		"tick": target_tick,
		"spawn_log_entry": log_entry,
		"active_count": VfxDirector.get_active_count(),
		"current_tick": VfxDirector.get_current_tick(),
		"engine_max_physics_steps": Engine.get_max_physics_steps_per_frame(),
		"engine_physics_ticks": Engine.physics_ticks_per_second,
		"pixel_at_origin": var_to_str(img.get_pixel(int(origin.x), int(origin.y))),
		"pixel_corner": var_to_str(img.get_pixel(10, 10)),
	}
	print("CAPTURE_RESULT ", JSON.stringify(report))

	get_tree().quit(0 if err == OK else 1)


## Gèle la simulation puis attend 3 process_frame avant de lire le
## viewport — technique prouvée en Phase 0 (docs/worklog.md) : le pipeline
## de rendu de Godot bufferise plusieurs images, un seul process_frame
## après avoir posé l'état voulu capture parfois une image pas encore
## rasterisée. Geler (get_tree().paused = true) arrête net toute
## simulation (physique, autoloads) SANS arrêter le rendu, donc la
## dernière redraw posée continue d'être rasterisée normalement pendant
## qu'on attend — utilisé tel quel par les deux modes de capture.
func _freeze_and_wait_render() -> void:
	get_tree().paused = true
	await get_tree().process_frame
	await get_tree().process_frame
	await get_tree().process_frame


func _save_png(img: Image, out_path: String) -> Error:
	var dir_path := out_path.get_base_dir()
	if dir_path != "" and not DirAccess.dir_exists_absolute(dir_path):
		DirAccess.make_dir_recursive_absolute(dir_path)
	return img.save_png(out_path)


func _parse_args() -> Dictionary:
	var result := {}
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--") and arg.contains("="):
			var kv := arg.substr(2).split("=", true, 1)
			result[kv[0]] = kv[1]
	return result
