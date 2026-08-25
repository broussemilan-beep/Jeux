extends Node2D
class_name CorbeauPale
## Invocation "Corbeau Pâle" (Invocateur, Tier 2/5, docs/references/
## invocateur/corbeau_pale.png, "PROJECTILE RAPIDE") — cast unique de 46
## ticks, PAS une entité persistante (même discipline que GueuleVide),
## mais contrairement à elle CETTE créature TRANSLATE réellement sa
## position pendant sa phase "chasse" (planche, temps 3) : "un corbeau
## d'encre jaillit et fonce à ras du sol sur une ligne droite", plusieurs
## cibles possibles sur son passage (pas une seule morsure ciblée comme
## Gueule Vide). Cette scène pilote SON PROPRE sprite (tick-exact,
## FRAME_TICK_BOUNDS — jamais la fps autonome d'AnimatedSprite2D) et SA
## PROPRE position (translation en ligne droite pendant CHASSE) ; le
## dégât/le ciblage restent ici (Targeting.enemies_in_line), jamais une
## primitive de la recette (data/recipes/power.corbeau_pale.cast.json).

const RECIPE_ID := "power.corbeau_pale.cast"

## 4 temps de la planche (labels planche : Préparation/Invocation/Chasse/
## Disparition) mappés sur les ticks de CETTE créature (la Préparation
## côté Cendre lui-même est portée par Player.gd, CORBEAU_PALE_
## GESTURE_TICKS — cette créature couvre Invocation->Chasse->Disparition,
## avec une courte formation qui recouvre la fin de la Préparation de
## Cendre plutôt que d'attendre qu'elle finisse, exactement comme
## GueuleVide.GUEULE_VIDE_GESTURE_TICKS/GueuleVide.TOTAL_TICKS se
## chevauchent déjà sans être synchronisés tick pour tick).
const FORMATION_END_TICK := 8   # 0-8 : éclaboussure d'encre, le corbeau se forme (temps 2, Invocation)
const PREP_END_TICK := 14       # 8-14 : forme complète, tendu au lancement
const CHASSE_END_TICK := 34     # 14-34 : vol/chasse (temps 3) — 20 ticks de translation réelle
const TOTAL_TICKS := 46         # 34-46 : dissipation (temps 4)
const CHASSE_START_TICK := PREP_END_TICK

## "fonce à ras du sol sur une ligne droite" — portée modérée (pas un tir
## qui traverse l'écran, cohérente avec l'échelle des autres compétences
## dédiées déjà en jeu, ex. Marée de Sable 90px) mais explicitement plus
## longue qu'une frappe de mêlée (Gueule Vide 48px) : c'est un PROJECTILE,
## pas un corps-à-corps. TUNABLE, non chiffré par une fiche bible (aucune
## section GDD dédiée à Corbeau Pâle, contrairement à Serpent Creux §6.2).
const RANGE_PX := 140.0
const HALF_WIDTH_PX := 18.0
const DAMAGE := 10.0  # même ordre que Gueule Vide (même Tier 2/5), la différence tient au multi-cible, pas aux dégâts par cible.

## Addendum A §A.5 : jamais l'horloge murale — voir GueuleVide.CAST_SEED.
## Suite de la séquence 51001 (Bras-Faux) .. 51004 (Marée de Sable).
const CAST_SEED := 51005

## 6 frames pose-à-pose sur les 46 ticks ci-dessus — bornes cumulées,
## jamais la fps autonome d'AnimatedSprite2D (même discipline que
## GueuleVide.FRAME_TICK_BOUNDS). frame2/frame3 couvrent la fenêtre de
## chasse/contact (14-34), frame4/5 la dissipation.
const FRAME_TICK_BOUNDS: Array[int] = [6, 14, 24, 34, 40, 46]

@onready var _sprite: AnimatedSprite2D = $AnimatedSprite2D

## Fixée par l'appelant (Player._cast_corbeau_pale()) juste après
## instantiate(), AVANT add_child() — même convention que
## `creature.global_position = ...` déjà utilisée par GueuleVide, pour
## que _ready() la lise déjà correctement positionnée.
var travel_direction: Vector2 = Vector2.RIGHT

var _tick: int = 0
var _recipe_run_id: int = 0
var _natural_end: bool = false
var _owner_stats: Stats = null
var _spawn_origin: Vector2 = Vector2.ZERO
var _hit_enemies: Array = []


func _ready() -> void:
	_sprite.play("cast")
	_sprite.pause()
	_sprite.frame = 0
	Sfx.play("spawn")
	if travel_direction.length_squared() < 0.0001:
		travel_direction = Vector2.RIGHT
	travel_direction = travel_direction.normalized()
	_spawn_origin = global_position
	_recipe_run_id = VfxRecipeRegistry.play(RECIPE_ID, {
		"origin": global_position,
		"seed": CAST_SEED,
		"direction": travel_direction,
	})


func set_owner_stats(stats: Stats) -> void:
	_owner_stats = stats
	if _owner_stats != null and not _owner_stats.died.is_connected(_on_owner_died):
		_owner_stats.died.connect(_on_owner_died)


## "owner_death_policy": "finish_core_then_stop_secondary" — même
## contrat que GueuleVide._on_owner_died().
func _on_owner_died() -> void:
	VfxRecipeRegistry.cancel(_recipe_run_id, true)


## Annulable jusqu'à la fin de la formation (avant que le corbeau ne
## parte réellement chasser) — même contrat que GueuleVide.can_cancel().
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

	if _tick > CHASSE_START_TICK and _tick <= CHASSE_END_TICK:
		var chasse_t: float = float(_tick - CHASSE_START_TICK) / float(CHASSE_END_TICK - CHASSE_START_TICK)
		global_position = _spawn_origin + travel_direction * (RANGE_PX * chasse_t)
		_resolve_contact_along_path(RANGE_PX * chasse_t)

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


## "Plusieurs cibles possibles" (fiche planche, temps 3 "Chasse") —
## Targeting.enemies_in_line() depuis l'origine du spawn, longueur =
## distance déjà parcourue CE tick (grandit à chaque appel : la ligne
## "avance" avec le corbeau). `_hit_enemies` évite qu'un ennemi déjà
## traversé ne reprenne un dégât à chaque tick suivant — une seule
## morsure par ennemi sur tout le trajet, jamais un dégât par tick.
func _resolve_contact_along_path(traveled_px: float) -> void:
	var targets: Array = Targeting.enemies_in_line(get_tree(), _spawn_origin, travel_direction, traveled_px, HALF_WIDTH_PX)
	for target in targets:
		if _hit_enemies.has(target):
			continue
		_hit_enemies.append(target)
		target.take_damage(DAMAGE, global_position)
		CombatFeedback.register_hit("light", true, "light_impact", "light", travel_direction, false)


func get_current_tick() -> int:
	return _tick


func is_finished() -> bool:
	return _tick >= TOTAL_TICKS
