extends Node2D
class_name SerpentCreux
## Invocation "Serpent Creux" (Invocateur, Tier 5/5, unlock_level 15 — le
## pouvoir ultime de la Classe, docs/RANK_ZERO_MASTER_GDD.md §6.2 +
## docs/references/invocateur/invocation_du_serpent.png) — cast unique de
## 60 ticks, PAS une entité persistante. GDD §6.2 (texte officiel) : "Un
## serpent très fin apparaît brièvement, déjà comprimé, puis détend
## brutalement son corps en ligne droite pour traverser les ennemis avant
## de disparaître. Rôle : portée supérieure à Gueule Vide, attaque
## linéaire, plusieurs cibles possibles." Même famille de construction que
## CorbeauPale (créature qui TRANSLATE réellement pendant sa phase
## d'attaque, contrairement à GueuleVide/PoingDuColosse stationnaires) —
## voir corbeau_pale.gd pour le patron détaillé, adapté ici à une portée/
## des dégâts d'ultime (Tier 5/5) et à une phase de compression
## (converge) avant le relâchement. Le dégât/le ciblage restent ici
## (Targeting.enemies_in_line), jamais une primitive de la recette
## (data/recipes/power.serpent_creux.cast.json).

const RECIPE_ID := "power.serpent_creux.cast"

## 4 temps de la planche (labels planche : Préparation/Invocation/
## Apparition/Attaque) — la Préparation côté Cendre est portée par
## Player.gd (SERPENT_CREUX_GESTURE_TICKS), cette créature couvre
## Invocation->Apparition->Attaque (le temps "Invocation" de la planche
## est un glyphe seul, sans Cendre visible dans le panneau — approximé
## ici par la formation du serpent qui commence AVANT sa propre
## apparition visuelle complète, cohérent avec le chevauchement déjà
## accepté ailleurs entre le geste de Cendre et la créature).
const FORMATION_END_TICK := 18   # 0-18 : le serpent émerge du sol en S (temps 3, Apparition)
const PREP_END_TICK := 26        # 18-26 : pleinement coiled, "déjà comprimé" — converge de la recette
const STRIKE_END_TICK := 46      # 26-46 : le corps se détend et frappe en ligne (temps 4, Attaque) — 20 ticks de translation réelle
const TOTAL_TICKS := 60          # 46-60 : dissipation
const STRIKE_START_TICK := PREP_END_TICK

## "Portée supérieure à Gueule Vide" (GDD §6.2, exigence explicite) :
## portée totale de Gueule Vide depuis le joueur = spawn (POWER1_SPAWN_
## DISTANCE_PX, 96px) + zone de morsure (ATTACK_RANGE_PX, 48px) = 144px.
## Serpent Creux : spawn plus proche (SPAWN_DISTANCE_PX côté Player.gd,
## 48px — "déjà comprimé" tout près de Cendre) + RANGE_PX ci-dessous
## (170px) = 218px de portée totale, strictement supérieure à Gueule
## Vide comme l'exige la fiche, marge confortable plutôt qu'un dépassement
## de quelques pixels difficile à distinguer à l'écran.
const RANGE_PX := 170.0
const HALF_WIDTH_PX := 16.0
const DAMAGE := 18.0  # Tier 5/5, l'ultime — au-dessus de toutes les compétences dédiées existantes (Poing du Colosse 20 reste l'exception AoE/stationnaire, pas un pierce linéaire).

## Addendum A §A.5 — suite de la séquence CAST_SEED.
const CAST_SEED := 51008

## 6 frames pose-à-pose sur les 60 ticks ci-dessus. frame3 couvre le
## début de la frappe (STRIKE_START_TICK=26, borne exacte frame2/frame3).
const FRAME_TICK_BOUNDS: Array[int] = [10, 18, 26, 40, 50, 60]

@onready var _sprite: AnimatedSprite2D = $AnimatedSprite2D

## Fixée par l'appelant (Player._cast_serpent_creux()) juste après
## instantiate(), AVANT add_child() — même convention que
## CorbeauPale.travel_direction.
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


func _on_owner_died() -> void:
	VfxRecipeRegistry.cancel(_recipe_run_id, true)


## Annulable jusqu'à la fin de la compression (avant le relâchement).
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

	if _tick > STRIKE_START_TICK and _tick <= STRIKE_END_TICK:
		var strike_t: float = float(_tick - STRIKE_START_TICK) / float(STRIKE_END_TICK - STRIKE_START_TICK)
		global_position = _spawn_origin + travel_direction * (RANGE_PX * strike_t)
		_resolve_contact_along_path(RANGE_PX * strike_t)

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


## "Traverser les ennemis" (GDD §6.2) — même patron que
## CorbeauPale._resolve_contact_along_path() : ligne qui grandit avec la
## distance parcourue, un seul dégât par ennemi sur tout le trajet.
func _resolve_contact_along_path(traveled_px: float) -> void:
	var targets: Array = Targeting.enemies_in_line(get_tree(), _spawn_origin, travel_direction, traveled_px, HALF_WIDTH_PX)
	for target in targets:
		if _hit_enemies.has(target):
			continue
		_hit_enemies.append(target)
		target.take_damage(DAMAGE, global_position)
		CombatFeedback.register_hit("heavy", true, "heavy_impact", "heavy", travel_direction, true)


func get_current_tick() -> int:
	return _tick


func is_finished() -> bool:
	return _tick >= TOTAL_TICKS
