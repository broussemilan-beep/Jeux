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

## Addendum A, §A.5 — fixture réelle (pas totem_du_vide) car le bug
## corrigé était spécifique à ce script : la seed venait de
## Time.get_ticks_usec(), l'horloge murale, cassant le gate "seed fixe ->
## même sortie" (§13.4 du v3).
const GueuleVideScene := preload("res://scenes/gameplay/powers/gueule_vide.tscn")

var _checks: Array[Dictionary] = []


func _ready() -> void:
	await _check_unknown_recipe()
	await _check_timeline_and_cleanup()
	await _check_palette_resolution()
	await _check_fallback_no_match()
	await _check_recipe_registry_seed_is_deterministic()
	await _check_gueule_vide_seed_is_fixed_not_wallclock()
	_check_budget_degrades_decorative_layer()
	_check_budget_never_refuses_protected_layer()
	await _check_all_primitives_spawn_tick_and_cleanup()

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


## Addendum A, §A.5 : "aucune source de hasard non seedée dans le chemin
## VFX". Preuve de bout en bout registry -> director -> primitives :
## deux runs de la MÊME recette avec la MÊME seed explicite doivent
## produire le même spawn_log (mêmes primitives, mêmes seeds, même
## ordre) — le mécanisme générique, indépendant de Gueule Vide.
func _check_recipe_registry_seed_is_deterministic() -> void:
	VfxDirector.clear_log()
	VfxRecipeRegistry.play("power.totem_du_vide.attack", {
		"origin": Vector2(320, 180), "seed": 7777, "direction": Vector2.RIGHT,
	})
	await _wait_until(func(): return VfxDirector.spawn_log.size() >= 2, 10)
	var log1: Array = _log_signature(VfxDirector.spawn_log)

	VfxDirector.clear_log()
	VfxRecipeRegistry.play("power.totem_du_vide.attack", {
		"origin": Vector2(320, 180), "seed": 7777, "direction": Vector2.RIGHT,
	})
	await _wait_until(func(): return VfxDirector.spawn_log.size() >= 2, 10)
	var log2: Array = _log_signature(VfxDirector.spawn_log)

	_checks.append({
		"name": "recipe_registry_same_seed_produces_identical_spawn_log",
		"pass": log1.size() >= 2 and log1 == log2,
		"detail": {"log1": log1, "log2": log2},
	})


## Addendum A, §A.5 : régression ciblée sur le bug réel — gueule_vide.gd
## passait Time.get_ticks_usec() comme seed. Deux invocations séparées
## par un vrai écart de ticks physiques (donc de temps réel) doivent
## produire la MÊME seed dans le spawn_log ; si l'horloge murale revenait,
## cet écart suffirait à les rendre différentes.
func _check_gueule_vide_seed_is_fixed_not_wallclock() -> void:
	VfxDirector.clear_log()
	var cast1: Node2D = GueuleVideScene.instantiate()
	add_child(cast1)
	await _wait_until(func(): return VfxDirector.spawn_log.size() >= 2, 10)
	var seeds1: Array = _log_signature(VfxDirector.spawn_log)
	if is_instance_valid(cast1):
		cast1.queue_free()

	for i in range(15):
		await get_tree().physics_frame

	VfxDirector.clear_log()
	var cast2: Node2D = GueuleVideScene.instantiate()
	add_child(cast2)
	await _wait_until(func(): return VfxDirector.spawn_log.size() >= 2, 10)
	var seeds2: Array = _log_signature(VfxDirector.spawn_log)
	if is_instance_valid(cast2):
		cast2.queue_free()

	_checks.append({
		"name": "gueule_vide_seed_is_fixed_not_wallclock",
		"pass": seeds1.size() >= 2 and seeds1 == seeds2,
		"detail": {"seeds_cast1": seeds1, "seeds_cast2": seeds2},
	})


## (primitive, seed) par entrée, dans l'ordre — assez pour comparer deux
## exécutions sans dépendre de champs non déterministes par nature
## (origin/zone_idx dépendent de la position, pas de la seed).
func _log_signature(log: Array[Dictionary]) -> Array:
	var sig: Array = []
	for entry in log:
		sig.append([entry["primitive"], entry["seed"]])
	return sig


## Addendum A, §A.2 : ordre de dégradation — une couche DÉGRADABLE qui
## dépasse le plafond souple d'overdraw d'une zone est refusée (retirée
## entièrement, faute de primitive capable d'un rendu "à moitié").
## Zone 11 (coin bas-droit, x:480-640/y:240-360) — inutilisée par les
## autres checks de ce fichier, aucune contamination d'état.
func _check_budget_degrades_decorative_layer() -> void:
	var verdict: Dictionary = VfxBudget.can_spawn({
		"particles": 0, "overdraw": 999.0, "zone_idx": 11, "degradable": true,
	})
	_checks.append({
		"name": "budget_refuses_degradable_layer_over_soft_cap",
		"pass": verdict["ok"] == false,
		"detail": verdict,
	})


## D, tranche 3 (primitives 6->15) : couverture générique plutôt que 8
## checks quasi-identiques copiés-collés — chaque primitive ENREGISTRÉE
## dans VfxDirector._registry (les 15 du §7.1, pas seulement les 8
## nouvelles) doit spawn, tourner quelques ticks sans erreur, puis se
## libérer d'elle-même via le timeout standard du director — la même
## preuve que _check_timeline_and_cleanup() mais balayée sur tout le
## registre en une passe, jamais un test par fichier qui dériverait du
## registre réel (une primitive ajoutée à _registry sans être couverte
## ici passerait inaperçue).
func _check_all_primitives_spawn_tick_and_cleanup() -> void:
	var failures: Array = []
	var primitive_names: Array = VfxDirector._registry.keys()
	for primitive_name in primitive_names:
		VfxDirector.clear_log()
		var node: Node = VfxDirector.spawn(primitive_name, {
			"seed": 12345, "origin": Vector2(320, 180), "direction": Vector2.RIGHT,
			"lifetime_ticks": 3, "overdraw_cost": 1.0,
		})
		if node == null:
			failures.append({"primitive": primitive_name, "reason": "spawn_refused"})
			continue
		var freed := await _wait_until(func(): return VfxDirector.get_active_count() == 0, 10)
		if not freed:
			failures.append({"primitive": primitive_name, "reason": "did_not_cleanup"})

	_checks.append({
		"name": "all_registered_primitives_spawn_tick_and_cleanup",
		"pass": failures.is_empty(),
		"detail": {"failures": failures, "primitive_count": primitive_names.size()},
	})


## Même zone, même overdraw excessif, mais couche PROTÉGÉE — "plancher
## intouchable" (étape 7) : ne doit JAMAIS être refusée pour ce plafond
## souple, contrairement à avant l'Addendum A où can_spawn() ne
## distinguait pas protégé/dégradable et pouvait refuser les deux.
func _check_budget_never_refuses_protected_layer() -> void:
	var verdict: Dictionary = VfxBudget.can_spawn({
		"particles": 0, "overdraw": 999.0, "zone_idx": 11, "degradable": false,
	})
	_checks.append({
		"name": "budget_never_refuses_protected_layer_over_soft_cap",
		"pass": verdict["ok"] == true,
		"detail": verdict,
	})
