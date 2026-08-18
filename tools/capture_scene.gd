extends Node2D
## Scène de capture headless — docs/ARCHITECTURE_VFX_v3.md §13.3.
##
## "Scène de capture dédiée tools/capture_scene.tscn : charge une
## recette/animation, seed fixée, joue, exporte les frames en PNG
## (get_viewport().get_texture().get_image().save_png()) [...] Lancée par
## scripts/capture_headless.sh."
##
## Phase 0 : capture UNE primitive nommée à UN tick donné (pas encore de
## recette JSON multi-couches ni de séquence complète — Phase 1+, une
## fois qu'une vraie recette existe). Arguments passés après "--" sur la
## ligne de commande, format --clef=valeur :
##   --primitive=impactFlashFrame   nom de primitive (VfxDirector._registry)
##   --seed=44102                   seed déterministe (traçabilité replay)
##   --tick=1                       tick physique auquel capturer (1-2 pour impactFlashFrame)
##   --out=/chemin/absolu/sortie.png
##
## Voir CLAUDE.md "Environnement de capture — écart documenté" : cette
## scène elle-même ne sait rien de xvfb/Vulkan logiciel — c'est
## scripts/capture_headless.sh qui choisit COMMENT lancer Godot. Ce
## fichier reste portable vers un vrai `--headless` le jour où ça
## fonctionnera dans l'environnement d'exécution.

func _ready() -> void:
	var args := _parse_args()
	var primitive_name: String = args.get("primitive", "impactFlashFrame")
	var seed_val: int = int(args.get("seed", "0"))
	var target_tick: int = int(args.get("tick", "1"))
	var out_path: String = args.get("out", "")

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
		"lifetime_ticks": 2,
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
	get_tree().paused = true
	await get_tree().process_frame
	await get_tree().process_frame
	await get_tree().process_frame

	var img: Image = get_viewport().get_texture().get_image()
	var dir_path := out_path.get_base_dir()
	if dir_path != "" and not DirAccess.dir_exists_absolute(dir_path):
		DirAccess.make_dir_recursive_absolute(dir_path)
	var err := img.save_png(out_path)

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


func _parse_args() -> Dictionary:
	var result := {}
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--") and arg.contains("="):
			var kv := arg.substr(2).split("=", true, 1)
			result[kv[0]] = kv[1]
	return result
