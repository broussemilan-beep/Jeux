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


func _ready() -> void:
	_sprite.play("cast")
	_sprite.pause()
	_sprite.frame = 0
	_recipe_run_id = VfxRecipeRegistry.play(RECIPE_ID, {
		"origin": global_position,
		"seed": Time.get_ticks_usec() % 100000,
		"direction": Vector2.RIGHT,
	})


func _physics_process(_delta: float) -> void:
	_tick += 1
	_sprite.frame = _frame_for_tick(_tick)

	if not _contact_resolved and _tick >= CONTACT_TICK:
		_contact_resolved = true
		_resolve_contact()

	if _tick >= TOTAL_TICKS:
		queue_free()


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
