extends Node2D
## Vérification de correction pour VfxRecipeRegistry (Phase 1.5) — pas une
## capture visuelle. Même discipline que tools/smoke_test_gameplay.gd :
## assert-based, sonde l'état réel via `_wait_until`, jamais un compte
## d'`await physics_frame` à l'aveugle (course déjà trouvée en Phase 0).
##
## Fixture volontaire : `power.totem_du_vide.attack` + palette
## `totem_du_vide` — les DEUX fichiers déjà présents dans le dépôt et
## indépendants de Gueule Vide (dont la palette manque encore au moment
## d'écrire ce test, voir docs/worklog.md). Ce test prouve le MÉCANISME
## générique de la registry, pas une recette précise.

var _checks: Array[Dictionary] = []


func _ready() -> void:
	await _check_unknown_recipe()
	await _check_timeline_and_cleanup()
	await _check_palette_resolution()
	await _check_fallback_no_match()

	var all_pass: bool = true
	for c in _checks:
		if not c["pass"]:
			all_pass = false
	print("SMOKE_TEST_RESULT ", JSON.stringify({"all_pass": all_pass, "checks": _checks}))
	get_tree().quit(0 if all_pass else 1)


func _wait_until(predicate: Callable, max_ticks: int = 400) -> bool:
	var waited := 0
	while not predicate.call():
		if waited >= max_ticks:
			return false
		await get_tree().physics_frame
		waited += 1
	return true


func _check_unknown_recipe() -> void:
	var run_id := VfxRecipeRegistry.play("power.does_not_exist", {"origin": Vector2(320, 180)})
	_checks.append({
		"name": "play_unknown_recipe_returns_zero",
		"pass": run_id == 0,
		"detail": {"run_id": run_id},
	})


func _check_timeline_and_cleanup() -> void:
	VfxDirector.clear_log()
	var run_id := VfxRecipeRegistry.play("power.totem_du_vide.attack", {
		"origin": Vector2(320, 180), "seed": 44102, "direction": Vector2.RIGHT,
	})
	var started := run_id != 0 and VfxRecipeRegistry.is_running(run_id)

	# La recette a end_tick max = 6 (fractureLine 0-6, impactFlashFrame 4-6).
	# Les deux couches doivent apparaître dans le spawn_log AVANT la fin.
	var both_spawned := await _wait_until(func():
		var names := {}
		for entry in VfxDirector.spawn_log:
			names[entry["primitive"]] = true
		return names.has("fractureLine") and names.has("impactFlashFrame")
	, 10)

	# Le run doit se terminer peu après end_tick=6 (jamais rester actif
	# indéfiniment — sinon une fuite de runs s'accumule à chaque cast).
	var finished := await _wait_until(func(): return not VfxRecipeRegistry.is_running(run_id), 20)

	_checks.append({
		"name": "recipe_run_starts_spawns_both_layers_then_finishes",
		"pass": started and both_spawned and finished,
		"detail": {"started": started, "both_spawned": both_spawned, "finished": finished},
	})


func _check_palette_resolution() -> void:
	# fractureLine -> role "signature 2 (matière Ink)" (noir d'encre,
	# value_percent=24) dans data/palettes/totem_du_vide.json — son champ
	# `usage` mentionne "fractureLine" explicitement.
	var color := VfxRecipeRegistry._resolve_color("power.totem_du_vide.attack", "totem_du_vide", "fractureLine")
	_checks.append({
		"name": "palette_resolution_matches_usage_text",
		"pass": is_equal_approx(color.get("value_percent", -1.0), 24.0),
		"detail": color,
	})


func _check_fallback_no_match() -> void:
	# Primitive qui n'apparaît dans AUCUN `usage` de la palette -> repli
	# gris neutre 50%, jamais un crash ni une valeur hors bande VFX.
	var color := VfxRecipeRegistry._resolve_color("power.totem_du_vide.attack", "totem_du_vide", "thisPrimitiveDoesNotExist")
	_checks.append({
		"name": "unresolved_primitive_falls_back_to_neutral_gray",
		"pass": is_equal_approx(color.get("value_percent", -1.0), 50.0) and is_equal_approx(color.get("saturation_percent", -1.0), 0.0),
		"detail": color,
	})
