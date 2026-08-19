extends Node2D
class_name GueuleVide
## Invocation "Gueule Vide" — cast unique de 42 ticks (0,7s @ 60/s), pas
## une entité persistante (contrairement à un totem) : formation ->
## gueule ouverte/préparation -> morsure (RELEASE+IMPACT) -> désintégration
## (RECOVERY), conventions doc §6.1. Une seule attaque, jamais de
## répétition, `queue_free()` à la fin de son propre cast.
##
## Le recul (recoil) sur la cible touchée est OBLIGATOIRE à l'impact et
## porté par Enemy.take_damage() — "pas une primitive de la recette",
## data/recipes/power.gueule_vide.cast.json, note. Cette scène ne pilote
## QUE : son propre sprite (tick-exact, jamais la lecture fps autonome
## d'AnimatedSprite2D — même discipline que le combo de Player, "les
## ticks sont la seule autorité") et la couche visuelle VFX via
## VfxRecipeRegistry.play() ; le dégât/recul restent ici, pas dans la
## recette.

const RECIPE_ID := "power.gueule_vide.cast"

## docs/recipes/power.gueule_vide.cast.json, "notes" — bornes des 4
## phases (§6.1) et tick de contact (sfx_markers, tick=20, "morsure").
## TOTAL_TICKS reste sous le plafond de sécurité "lifecycle.
## max_lifetime_ticks" (48, "42 + marge") de la recette — seule cette
## classe incrémente _tick, aucun système de pause/étourdissement
## n'existe encore côté gameplay qui pourrait le dépasser.
const FORMATION_END_TICK := 9
const PREP_END_TICK := 15
const BITE_END_TICK := 21
const TOTAL_TICKS := 42
const CONTACT_TICK := 20

## Fiche de référence (INVOCATION : GUEULE VIDE, "COMPORTEMENT") :
## "Zone d'attaque : ~1,5m devant la créature" -> 48px, GameConstants.
## PX_PER_METER (même échelle que le combo de Player, ATTACK_RANGE_PX).
## Dégâts non chiffrés par la fiche (contrairement au combo, 10.0) —
## valeur par défaut alignée sur le dégât combo, à faire trancher par Milan.
const ATTACK_RANGE_PX := 48.0
const ATTACK_DAMAGE := 10.0

## Addendum A, §A.5 : "aucune source de hasard non seedée dans le chemin
## VFX" — l'horloge murale (Time.get_ticks_usec(), l'ancien code d'ici)
## rend compare_reference.py inutilisable et casse le gate "seed fixe ->
## même sortie" (§13.4 du v3). Valeur fixe en attendant un vrai système
## de seed de run côté gameplay (compteur d'événement, seed de run...).
const CAST_SEED := 44103

## 6 frames pose-to-pose (mandat : "4-6 frames") couvrant les 4 phases :
## formation (2 frames), préparation (1), morsure (1), désintégration
## (2). Bornes cumulées en ticks — jamais la fps autonome
## d'AnimatedSprite2D (qui ne peut pas exprimer des phases de durées
## inégales avec le pas fps uniforme de build_sprite_frames.py).
const FRAME_TICK_BOUNDS: Array[int] = [5, 9, 15, 21, 32, 42]

@onready var _sprite: AnimatedSprite2D = $AnimatedSprite2D

var _tick: int = 0
var _recipe_run_id: int = 0
var _contact_resolved: bool = false
var _natural_end: bool = false
var _owner_stats: Stats = null


func _ready() -> void:
	_sprite.play("cast")
	_sprite.pause()
	_sprite.frame = 0
	_recipe_run_id = VfxRecipeRegistry.play(RECIPE_ID, {
		"origin": global_position,
		"seed": CAST_SEED,
		"direction": Vector2.RIGHT,
	})


## Addendum A, §A.4, "owner_death_policy". À appeler juste après avoir
## ajouté cette scène à l'arbre (voir Player._cast_gueule_vide()) — la
## créature observe la mort de son invocateur sans lui être asservie.
func set_owner_stats(stats: Stats) -> void:
	_owner_stats = stats
	if _owner_stats != null and not _owner_stats.died.is_connected(_on_owner_died):
		_owner_stats.died.connect(_on_owner_died)


## "owner_death_policy": "finish_core_then_stop_secondary" — "la
## créature termine sa morsure même si le joueur meurt (elle a été
## arrachée au monde, elle n'est pas liée à lui)". La créature (ce
## script) continue donc sa propre timeline normalement ; seules les
## couches VFX dégradables de la recette (A.1) sont coupées net, les
## protégées vont au bout de leur vie.
func _on_owner_died() -> void:
	VfxRecipeRegistry.cancel(_recipe_run_id, true)


## "cancellable_before": "release" — annulable jusqu'à la fin de la
## préparation (avant PREP_END_TICK, la morsure), plus après. Rien ne
## l'appelle encore (aucun système d'interruption/étourdissement
## n'existe côté gameplay) — la brique est posée pour quand ce sera le
## cas, sans en construire l'usage maintenant (§16.1).
func can_cancel() -> bool:
	return _tick < PREP_END_TICK


func cancel_cast() -> bool:
	if not can_cancel():
		return false
	VfxRecipeRegistry.cancel(_recipe_run_id, false)
	_natural_end = false
	queue_free()
	return true


func _physics_process(_delta: float) -> void:
	if CombatFeedback.is_frozen():
		return
	_tick += 1
	_sprite.frame = _frame_for_tick(_tick)

	if not _contact_resolved and _tick >= CONTACT_TICK:
		_contact_resolved = true
		_resolve_contact()

	if _tick >= TOTAL_TICKS:
		_natural_end = true
		queue_free()


## "scene_change_policy": "stop_immediately" — quitte l'arbre pour
## n'importe quelle raison AUTRE que sa propre fin naturelle (changement
## de scène qui libère toute la branche, libération externe) => aucune
## couche VFX de cette recette ne doit lui survivre. La fin naturelle
## (timeout, TOTAL_TICKS) n'a pas besoin de ce nettoyage forcé : chaque
## couche s'éteint déjà proprement via sa propre lifetime_ticks.
func _exit_tree() -> void:
	if not _natural_end:
		VfxRecipeRegistry.cancel(_recipe_run_id, false)


func _frame_for_tick(tick: int) -> int:
	for i in FRAME_TICK_BOUNDS.size():
		if tick <= FRAME_TICK_BOUNDS[i]:
			return i
	return FRAME_TICK_BOUNDS.size() - 1


## "Recul obligatoire sur la cible touchée à l'impact, porté par
## Enemy.take_damage() comme pour le combo, pas une primitive de la
## recette" — mandat Gueule Vide. Même schéma que Player._try_hit().
func _resolve_contact() -> void:
	var target: Node = Targeting.nearest_enemy_in_radius(get_tree(), global_position, ATTACK_RANGE_PX)
	if target == null:
		return
	target.take_damage(ATTACK_DAMAGE, global_position)


## Tick courant du cast — utile aux tests/captures (même contrat que
## VfxDirector.get_current_tick() et Player._combo_tick).
func get_current_tick() -> int:
	return _tick


func is_finished() -> bool:
	return _tick >= TOTAL_TICKS
