extends Node
## Autoload "VfxDirector" — docs/ARCHITECTURE_VFX_v3.md §8.2.
##
## Contrat d'appel (§7.1) :
##   VfxDirector.spawn("impactFlashFrame", {
##       "seed": 44102, "origin": Vector2(320, 180), "lifetime_ticks": 2,
##       "particles": 0, "overdraw_cost": 12.0,
##   })
##
## Rôles du director (§8.2, verbatim) :
##   - résout recette + palette + seed ;
##   - impose des budgets de particules/sprites/overdraw par action ET
##     par zone d'écran (délégué à VfxBudget) ;
##   - centralise le cleanup (timeout, mort, changement de scène) ;
##   - journalise seed + recette de chaque spawn pour replay et capture ;
##   - expose un mode debug par couche.
##
## Phase 0 (§15) : seulement "spawn, seed, cleanup, budgets simples" — pas
## encore de résolution de recette JSON multi-couches (ça, c'est
## vfx_recipe_registry.gd, Phase 1+, une fois qu'une vraie recette existe
## à résoudre). Ici : une primitive nommée directement, un contrat clair,
## prouvé de bout en bout par la capture headless.
##
## Contrat d'une primitive (src/vfx/primitives/*.gd) :
##   - extends Node2D, autonome (un fichier = une primitive, §7) ;
##   - func configure(params: Dictionary) -> void, appelée une fois avant
##     l'ajout à la scène ;
##   - func tick(ticks_elapsed: int) -> void, OPTIONNELLE — appelée par ce
##     director à chaque pas physique (60/s) tant que l'instance est
##     vivante. Le director avance les ticks, jamais la primitive en
##     autonome, pour garantir un ordre déterministe entre couches d'une
##     même recette (nécessaire pour la reproductibilité seed, §13.4).

var _container: Node2D
var _tick_counter: int = 0

## instance_id (int, Node.get_instance_id()) -> { node, primitive, lifetime_ticks, ticks_elapsed, zone_idx }
var _active: Dictionary = {}

## Nom de primitive -> chemin de script. Enrichi à mesure que les
## primitives du §7.1 sont écrites — jamais une primitive référencée ici
## sans fichier réel derrière (pas de placeholder).
var _registry: Dictionary = {
	"impactFlashFrame": "res://src/vfx/primitives/impact_flash_frame.gd",
	"groundRing": "res://src/vfx/primitives/ground_ring.gd",
	"runicStamp": "res://src/vfx/primitives/runic_stamp.gd",
	"fractureLine": "res://src/vfx/primitives/fracture_line.gd",
	"shardBurst": "res://src/vfx/primitives/shard_burst.gd",
}

## Journal en mémoire de chaque spawn — §8.2 "journalise seed + recette
## de chaque spawn pour replay et capture". La scène de capture
## (tools/capture_scene.tscn) lit ceci pour nommer/tracer ses exports.
var spawn_log: Array[Dictionary] = []


func _ready() -> void:
	_container = Node2D.new()
	_container.name = "VfxActive"
	add_child(_container)


func _physics_process(_delta: float) -> void:
	_tick_counter += 1
	# Copie des clés : _free_spawn() mute _active pendant l'itération,
	# itérer directement sur _active.keys() en live serait indéfini.
	for instance_id in _active.keys().duplicate():
		var entry: Dictionary = _active.get(instance_id)
		if entry == null:
			continue  # déjà libéré par un autre chemin cette même frame
		entry["ticks_elapsed"] += 1

		# Libérer UN PAS APRÈS le dernier tick visible, jamais dans le
		# même appel que lui. Trouvé pendant la validation Phase 0
		# (docs/worklog.md) : queue_free() retire le nœud de l'arbre de
		# rendu avant que le tick final ait eu l'occasion d'être
		# rasterisé — une capture pile sur le tick terminal d'une durée
		# de vie de 2 ticks tombait sur un écran vide. Avec ce garde,
		# lifetime_ticks=2 reste visible et capturable aux ticks 1 ET 2,
		# la libération n'arrive qu'au tick 3 (jamais dessiné).
		if entry["ticks_elapsed"] > entry["lifetime_ticks"]:
			_free_spawn(instance_id)
			continue

		var node: Node = entry["node"]
		if is_instance_valid(node) and node.has_method("tick"):
			node.tick(entry["ticks_elapsed"])


## Retourne le nœud spawné, ou null si le budget refuse ou si la
## primitive est inconnue — jamais d'exception, jamais de spawn partiel.
## `params` attendus (voir docstring de fichier) : seed, origin,
## lifetime_ticks, et le coût déclaré par l'appelant — soit directement
## `particles`/`overdraw_cost`, soit `size_px`/`opacity`/`layers` pour
## que VfxBudget calcule l'overdraw lui-même (§8.2).
func spawn(primitive_name: String, params: Dictionary) -> Node:
	if not _registry.has(primitive_name):
		push_error("VfxDirector.spawn: primitive inconnue '%s' — l'ajouter à _registry après avoir écrit son fichier, jamais avant." % primitive_name)
		return null

	var origin: Vector2 = params.get("origin", Vector2.ZERO)
	var zone_idx: int = VfxBudget.zone_index_for(origin)
	var overdraw_cost: float = params.get("overdraw_cost", 0.0)
	if overdraw_cost <= 0.0 and params.has("size_px"):
		overdraw_cost = VfxBudget.estimate_overdraw_cost(
			params.get("size_px", 0.0), params.get("opacity", 1.0), params.get("layers", 1))

	var cost := {
		"particles": params.get("particles", 0),
		"overdraw": overdraw_cost,
		"zone_idx": zone_idx,
		"degradable": params.get("degradable", true),
	}
	var verdict: Dictionary = VfxBudget.can_spawn(cost)
	if not verdict["ok"]:
		push_warning("VfxDirector.spawn: budget refusé pour '%s' — %s" % [primitive_name, verdict["reason"]])
		return null

	var script: GDScript = load(_registry[primitive_name])
	var node: Node2D = script.new()
	_container.add_child(node)
	node.configure(params)

	var instance_id: int = node.get_instance_id()
	VfxBudget.register_spawn(instance_id, cost)
	_active[instance_id] = {
		"node": node,
		"primitive": primitive_name,
		"lifetime_ticks": max(1, int(params.get("lifetime_ticks", 1))),
		"ticks_elapsed": 0,
		"zone_idx": zone_idx,
		# run_id=0 : spawn direct hors recette (ex. Player._try_hit()),
		# jamais un vrai run_id de VfxRecipeRegistry (celle-ci commence à
		# 1) — aucune collision possible avec cleanup_run()/A.4.
		"run_id": int(params.get("run_id", 0)),
		"degradable": bool(params.get("degradable", true)),
	}

	spawn_log.append({
		"tick": _tick_counter,
		"primitive": primitive_name,
		"seed": params.get("seed", 0),
		"origin": origin,
		"zone_idx": zone_idx,
	})

	return node


func _free_spawn(instance_id: int) -> void:
	var entry: Dictionary = _active.get(instance_id)
	if entry == null:
		return
	var node: Node = entry["node"]
	if is_instance_valid(node):
		node.queue_free()
	VfxBudget.release(instance_id)
	_active.erase(instance_id)


## §13.4 "cleanup : destruction au timeout, à la mort, au changement de
## scène" — appelé explicitement par le jeu (pas automatique ici, ce
## director ne sait pas quand une scène change ou un joueur meurt, c'est
## à l'appelant de le dire).
func cleanup_all() -> void:
	for instance_id in _active.keys().duplicate():
		_free_spawn(instance_id)


## Addendum A, §A.4 — nettoyage forcé scopé à UN run de recette (jamais
## tout le VFX en cours comme cleanup_all(), qui tuerait aussi les
## couches d'autres pouvoirs actifs). `only_degradable=true` : ne libère
## que les couches marquées `degradable` (A.1) — utilisé pour
## "owner_death_policy: finish_core_then_stop_secondary" (les couches
## protégées vont au bout de leur propre durée de vie). `false` : tout
## libérer sans distinction — "scene_change_policy: stop_immediately" et
## une annulation complète avant "release" (cancellable_before).
func cleanup_run(run_id: int, only_degradable: bool = false) -> void:
	for instance_id in _active.keys().duplicate():
		var entry: Dictionary = _active.get(instance_id)
		if entry == null or int(entry.get("run_id", 0)) != run_id:
			continue
		if only_degradable and not bool(entry.get("degradable", true)):
			continue
		_free_spawn(instance_id)


func get_active_count() -> int:
	return _active.size()


func clear_log() -> void:
	spawn_log.clear()


## Tick logique courant (60/s, physics_process) — utile aux scripts de
## capture pour attendre "jusqu'au tick N" de façon déterministe plutôt
## qu'un nombre de frames rendues (qui peut varier).
func get_current_tick() -> int:
	return _tick_counter
