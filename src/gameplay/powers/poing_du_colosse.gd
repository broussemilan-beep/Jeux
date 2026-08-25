extends Node2D
class_name PoingDuColosse
## Invocation "Poing du Colosse" (Invocateur, Tier 3/5, docs/references/
## invocateur/poing_du_colosse.png, "IMPACT MAJEUR") — cast unique de 54
## ticks, PAS une entité persistante. Structure la plus proche de
## GueuleVide parmi les 4 nouvelles compétences : créature STATIONNAIRE
## (contrairement à Corbeau Pâle/Serpent Creux, qui translatent), un seul
## impact ponctuel en ZONE ("s'abat avec une force écrasante sur la zone
## ciblée" — AoE, pas une cible unique comme la morsure de Gueule Vide).
## Cette scène pilote SON PROPRE sprite (tick-exact, FRAME_TICK_BOUNDS) ;
## le dégât/le ciblage restent ici (Targeting.enemies_in_arc en cercle
## complet), jamais une primitive de la recette (data/recipes/
## power.poing_du_colosse.cast.json).

const RECIPE_ID := "power.poing_du_colosse.cast"

## 4 temps de la planche (labels planche : Préparation/Matérialisation/
## Impact/Dissipation) — la Préparation côté Cendre est portée par
## Player.gd (POING_DU_COLOSSE_GESTURE_TICKS), cette créature couvre
## Matérialisation->Impact->Dissipation, chevauchement volontaire avec le
## geste de Cendre (même discipline que GueuleVide).
const FORMATION_END_TICK := 16   # 0-16 : le poing émerge du sol, encore courbé (temps 2, Matérialisation)
const PREP_END_TICK := 24        # 16-24 : poing dressé, tenu juste avant l'abattage
const IMPACT_END_TICK := 32      # 24-32 : l'abattage + l'impact (temps 3)
const TOTAL_TICKS := 54          # 32-54 : dissipation (temps 4)
const CONTACT_TICK := 26

## "s'abat... sur la zone ciblée" — AoE, TUNABLE (aucune fiche bible pour
## cette compétence, contrairement à Serpent Creux §6.2). Rayon un ton
## au-dessus de la zone de morsure de Gueule Vide (48px/1.5m) — un poing
## géant couvre plus de terrain qu'une petite gueule chétive — et dégâts
## nettement au-dessus des compétences dédiées existantes (Poing
## Belluaire 16, le plus haut jusqu'ici) : "impact majeur", Tier 3/5.
const RADIUS_PX := 56.0
const DAMAGE := 20.0

## Addendum A §A.5 — suite de la séquence CAST_SEED (voir corbeau_pale.gd).
const CAST_SEED := 51006

## 6 frames pose-à-pose sur les 54 ticks ci-dessus. frame3 couvre
## CONTACT_TICK (26, dans la fenêtre 24-32) — même discipline que
## GueuleVide.FRAME_TICK_BOUNDS.
const FRAME_TICK_BOUNDS: Array[int] = [8, 16, 24, 32, 42, 54]

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
	Sfx.play("spawn")
	_recipe_run_id = VfxRecipeRegistry.play(RECIPE_ID, {
		"origin": global_position,
		"seed": CAST_SEED,
		"direction": Vector2.RIGHT,  # AoE symétrique — direction sans effet gameplay, même convention que GueuleVide.
	})


func set_owner_stats(stats: Stats) -> void:
	_owner_stats = stats
	if _owner_stats != null and not _owner_stats.died.is_connected(_on_owner_died):
		_owner_stats.died.connect(_on_owner_died)


func _on_owner_died() -> void:
	VfxRecipeRegistry.cancel(_recipe_run_id, true)


## Annulable jusqu'à la fin de la Matérialisation (avant l'abattage) —
## même contrat que GueuleVide.can_cancel().
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
	if CombatFeedback.is_player_frozen():
		return
	_tick += 1
	_sprite.frame = _frame_for_tick(_tick)

	if not _contact_resolved and _tick >= CONTACT_TICK:
		_contact_resolved = true
		_resolve_contact()

	if _tick >= TOTAL_TICKS:
		_natural_end = true
		queue_free()


func _exit_tree() -> void:
	if not _natural_end:
		VfxRecipeRegistry.cancel(_recipe_run_id, false)


func _frame_for_tick(tick: int) -> int:
	for i in FRAME_TICK_BOUNDS.size():
		if tick <= FRAME_TICK_BOUNDS[i]:
			return i
	return FRAME_TICK_BOUNDS.size() - 1


## AoE : TOUS les ennemis vivants dans RADIUS_PX, pas seulement le plus
## proche (Targeting.enemies_in_arc avec half_angle_deg=180° — un cercle
## complet, "facing" n'a alors aucun effet sur le résultat, astuce
## documentée plutôt qu'une nouvelle fonction Targeting dédiée à
## l'AoE pur). "Force écrasante" -> hit-stop heavy, shake heavy,
## camera-punch (le plus lourd des impacts de cette Classe).
func _resolve_contact() -> void:
	var targets: Array = Targeting.enemies_in_arc(get_tree(), global_position, Vector2.RIGHT, RADIUS_PX, 180.0)
	if targets.is_empty():
		return
	for target in targets:
		target.take_damage(DAMAGE, global_position)
	CombatFeedback.register_hit("heavy", true, "heavy_impact", "heavy", Vector2.DOWN, true)


func get_current_tick() -> int:
	return _tick


func is_finished() -> bool:
	return _tick >= TOTAL_TICKS
