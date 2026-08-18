extends Node
## Autoload "VfxRecipeRegistry" — docs/ARCHITECTURE_VFX_v3.md §8.1/§8.2.
##
## Résout une recette JSON (data/recipes/<id>.json) en un timeline de
## spawns VfxDirector, tick-driven (chaque layer respecte son PROPRE
## start_tick/end_tick relatif au début du run — jamais un burst
## instantané de tous les layers à t=0, §8.1 : "start_tick": 0 est la
## toute première couche, pas toutes les couches).
##
## Usage :
##   var run_id := VfxRecipeRegistry.play("power.gueule_vide.cast", {
##       "origin": Vector2(320, 180), "seed": 44102, "direction": Vector2.RIGHT,
##   })
##   VfxRecipeRegistry.is_running(run_id) -> bool
##
## Ce que cette registry NE fait PAS (délibérément, §8.1 notes des
## recettes) : dégâts, recul, animation du lanceur/créature, SFX. Tout ça
## reste côté script gameplay de l'entité qui joue le pouvoir (ex.
## gueule_vide.gd), sur SA PROPRE boucle de ticks synchronisée — "pas une
## primitive de la recette" pour le recul (doc VFX §4), même logique pour
## le reste : cette registry ne pilote QUE les couches visuelles.
##
## Résolution palette (§8.1 : `palette_id` par recette) : chaque rôle de
## data/palettes/<palette_id>.json porte un champ `usage` en texte libre
## qui NOMME les primitives qu'il colore (convention déjà en place dans
## data/palettes/totem_du_vide.json, ex. "groundRing (spawn), fine
## bordure du totem"). Cette registry fait correspondre chaque layer à
## son rôle en cherchant le nom de la primitive DANS le texte `usage` de
## chaque rôle (recherche insensible à la casse) — aucune modification du
## schéma recette/palette pour ajouter un champ de mapping qui n'existe
## pas aujourd'hui. Aucun rôle ne correspond -> couleur de repli neutre
## (gris moyen 50% V, désaturé), un avertissement loggué une seule fois
## par (recipe_id, primitive) manquant, jamais en boucle par tick.

var _recipe_cache: Dictionary = {}   # recipe_id -> Dictionary
var _palette_cache: Dictionary = {}  # palette_id -> Dictionary
var _warned_missing_role: Dictionary = {}  # "<recipe_id>/<primitive>" -> true

## run_id (int) -> { recipe, palette_id, origin, seed, direction, elapsed_ticks,
##                    spawned: Dictionary[int, true], end_tick: int }
var _active: Dictionary = {}
var _next_run_id: int = 1


func _physics_process(_delta: float) -> void:
	for run_id in _active.keys().duplicate():
		var run: Dictionary = _active.get(run_id)
		if run == null:
			continue
		run["elapsed_ticks"] += 1
		_spawn_due_layers(run)
		if run["elapsed_ticks"] > run["end_tick"]:
			_active.erase(run_id)


## Démarre une recette. `params` : origin (Vector2, requis), seed (int),
## direction (Vector2, défaut RIGHT). Retourne un run_id (jamais 0 —
## réservé comme "aucun run"). Retourne 0 si la recette est introuvable.
func play(recipe_id: String, params: Dictionary) -> int:
	var recipe: Dictionary = _load_recipe(recipe_id)
	if recipe.is_empty():
		push_error("VfxRecipeRegistry.play: recette introuvable '%s' (data/recipes/%s.json)." % [recipe_id, recipe_id])
		return 0

	var run_id := _next_run_id
	_next_run_id += 1

	var layers: Array = recipe.get("layers", [])
	var max_end_tick := 0
	for layer in layers:
		max_end_tick = maxi(max_end_tick, int(layer.get("end_tick", layer.get("start_tick", 0))))
	var limits: Dictionary = recipe.get("limits", {})
	var end_tick: int = int(limits.get("persistent_ticks", max_end_tick))
	end_tick = maxi(end_tick, max_end_tick)

	var run := {
		"recipe_id": recipe_id,
		"recipe": recipe,
		"palette_id": recipe.get("palette_id", ""),
		"origin": params.get("origin", Vector2.ZERO),
		"seed": params.get("seed", 0),
		"direction": params.get("direction", Vector2.RIGHT),
		"elapsed_ticks": 0,
		"spawned": {},
		"end_tick": end_tick,
	}
	_active[run_id] = run
	_spawn_due_layers(run)  # couches à start_tick == 0 : spawn immédiat, pas d'attente d'un tick physique.
	return run_id


func is_running(run_id: int) -> bool:
	return _active.has(run_id)


func get_elapsed_ticks(run_id: int) -> int:
	var run: Dictionary = _active.get(run_id, {})
	return run.get("elapsed_ticks", -1)


## Arrête la PLANIFICATION de nouvelles couches (les primitives déjà
## spawnées gardent leur propre durée de vie via VfxDirector — ce n'est
## pas un cleanup forcé, cf. VfxDirector.cleanup_all() pour ça).
func stop(run_id: int) -> void:
	_active.erase(run_id)


func _spawn_due_layers(run: Dictionary) -> void:
	var elapsed: int = run["elapsed_ticks"]
	var layers: Array = run["recipe"].get("layers", [])
	for i in layers.size():
		if run["spawned"].has(i):
			continue
		var layer: Dictionary = layers[i]
		var start_tick: int = int(layer.get("start_tick", 0))
		if start_tick != elapsed:
			continue
		run["spawned"][i] = true
		var end_tick: int = int(layer.get("end_tick", start_tick + 1))
		var lifetime: int = maxi(1, end_tick - start_tick)
		var primitive_name: String = layer.get("primitive", "")
		var color_params: Dictionary = _resolve_color(run["recipe_id"], run["palette_id"], primitive_name)

		var spawn_params := {
			"seed": run["seed"],
			"origin": run["origin"],
			"direction": run["direction"],
			"lifetime_ticks": lifetime,
		}
		spawn_params.merge(color_params)
		VfxDirector.spawn(primitive_name, spawn_params)


## Cherche, dans la palette résolue, le rôle dont le texte `usage`
## mentionne `primitive_name` (insensible à la casse). Retourne les
## params de couleur prêts à fusionner dans un appel spawn() ; gris
## moyen désaturé si rien ne correspond (jamais un crash, jamais une
## couleur hors bande VFX 20-92%, §3).
func _resolve_color(recipe_id: String, palette_id: String, primitive_name: String) -> Dictionary:
	var fallback := {"value_percent": 50.0, "hue_deg": 0.0, "saturation_percent": 0.0}
	if palette_id == "":
		return fallback
	var palette: Dictionary = _load_palette(palette_id)
	if palette.is_empty():
		return fallback

	var needle: String = primitive_name.to_lower()
	for role in palette.get("roles", []):
		var usage: String = str(role.get("usage", "")).to_lower()
		if needle != "" and usage.contains(needle):
			return {
				"value_percent": float(role.get("value_percent", 50.0)),
				"hue_deg": float(role.get("hue_deg", 0.0)),
				"saturation_percent": float(role.get("saturation_percent", 0.0)),
			}

	var warn_key := "%s/%s" % [recipe_id, primitive_name]
	if not _warned_missing_role.has(warn_key):
		_warned_missing_role[warn_key] = true
		push_warning("VfxRecipeRegistry: aucun rôle de palette '%s' ne mentionne la primitive '%s' (recette '%s') — repli gris neutre." % [palette_id, primitive_name, recipe_id])
	return fallback


func _load_recipe(recipe_id: String) -> Dictionary:
	if _recipe_cache.has(recipe_id):
		return _recipe_cache[recipe_id]
	var path := "res://data/recipes/%s.json" % recipe_id
	var data := _load_json(path)
	_recipe_cache[recipe_id] = data
	return data


func _load_palette(palette_id: String) -> Dictionary:
	if _palette_cache.has(palette_id):
		return _palette_cache[palette_id]
	var path := "res://data/palettes/%s.json" % palette_id
	var data := _load_json(path)
	_palette_cache[palette_id] = data
	return data


func _load_json(path: String) -> Dictionary:
	if not FileAccess.file_exists(path):
		return {}
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return {}
	var text := f.get_as_text()
	var parsed = JSON.parse_string(text)
	if parsed == null or typeof(parsed) != TYPE_DICTIONARY:
		return {}
	return parsed
