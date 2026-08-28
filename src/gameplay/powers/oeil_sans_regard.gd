extends Node2D
class_name OeilSansRegard
## Invocation "Œil Sans Regard" (Invocateur, Tier 4/5, docs/references/
## invocateur/oeil_sans_regard.png, "RAYON") — cast unique de 48 ticks,
## PAS une entité persistante. Créature STATIONNAIRE (comme Poing du
## Colosse) mais flottant à distance/hauteur de Cendre (voir
## Player._cast_oeil_sans_regard(), offset vertical au spawn) : "un œil
## d'encre s'ouvre dans les airs et projette un rayon d'encre qui perce
## TOUT sur sa trajectoire" — pierce multi-cible en LIGNE (pas un cône
## comme Poing Tellurique, pas un cercle comme Poing du Colosse). Cette
## scène pilote SON PROPRE sprite (tick-exact, FRAME_TICK_BOUNDS) ; le
## dégât/le ciblage restent ici (Targeting.enemies_in_line), jamais une
## primitive de la recette (data/recipes/power.oeil_sans_regard.cast.json).

const RECIPE_ID := "power.oeil_sans_regard.cast"

## 4 temps de la planche (labels planche : Préparation/Ouverture/Rayon/
## Fermeture) — la Préparation côté Cendre est portée par Player.gd
## (OEIL_SANS_REGARD_GESTURE_TICKS), cette créature couvre
## Ouverture->Rayon->Fermeture.
const OPEN_END_TICK := 14    # 0-14 : l'œil se matérialise, encore fermé/entrouvert (temps 2, Ouverture)
const PREP_END_TICK := 20    # 14-20 : pleinement ouvert, tenu juste avant le tir
const BEAM_TICK := 22        # le rayon jaillit (temps 3, Rayon) — dans la fenêtre beamSegment 18-26 de la recette
const TOTAL_TICKS := 48      # 30-48 : fermeture/dissipation (temps 4)

## "perce tout sur sa trajectoire" — portée en ligne, TUNABLE (aucune
## fiche bible pour cette compétence). Même longueur que beamSegment.
## scale_px de la recette (128px) : le rayon visuel et la ligne de
## dégâts doivent couvrir la même distance, sinon un ennemi visuellement
## touché par le rayon ne prendrait pas de dégât (ou l'inverse).
const BEAM_LENGTH_PX := 128.0
const BEAM_HALF_WIDTH_PX := 12.0
const DAMAGE := 12.0  # Tier 4/5, pierce multi-cible — entre Gueule Vide (10, cible unique) et Poing du Colosse (20, AoE lourd).

## Addendum A §A.5 — suite de la séquence CAST_SEED.
const CAST_SEED := 51007

## PASSE DENSITÉ (2026-08-28, MANDAT campagne "densité d'animation +
## richesse visuelle", bible §2, cible 12-18 frames) : régénéré en v3
## PixelLab (même character bac7d236, nouvelle animation "cast_dense" à
## 17 frames sud, frame_count=16+keep_first_frame). Lecture visuelle
## réelle : 0-3 = œil grand ouvert tenu (anticipation) ; 4-7 = paupière
## qui se resserre progressivement (préparation, tension qui monte) ;
## 8-10 = LE clignement/tir, resserrement final rapide en 2-3 frames à
## peine ("beaucoup sur l'anticipation, 2-3 sur le contact") ; 11-16 =
## fermeture complète + gouttes (6 frames, désintégration, richesse
## ajoutée). Répartition non-uniforme : 8 frames sur ouverture+
## préparation (0-20t), 3 SEULEMENT sur le tir (20-30t), 6 sur la
## fermeture/dissipation (30-48t). BEAM_TICK (22, inchangé) tombe pile
## sur la borne exacte frame7/frame8 (même convention que l'ancien
## mandat), soit le tout premier frame du "resserrement final".
const FRAME_TICK_BOUNDS: Array[int] = [3, 7, 11, 14, 15, 17, 18, 20, 22, 25, 30, 34, 38, 41, 44, 46, 48]

@onready var _sprite: AnimatedSprite2D = $AnimatedSprite2D

## Fixée par l'appelant (Player._cast_oeil_sans_regard()) juste après
## instantiate(), AVANT add_child() — même convention que
## CorbeauPale.travel_direction : direction du rayon, indépendante de la
## position de spawn (déjà décalée en hauteur par l'appelant).
var beam_direction: Vector2 = Vector2.RIGHT

var _tick: int = 0
var _recipe_run_id: int = 0
var _beam_resolved: bool = false
var _natural_end: bool = false
var _owner_stats: Stats = null


func _ready() -> void:
	_sprite.play("cast")
	_sprite.pause()
	_sprite.frame = 0
	Sfx.play("spawn")
	if beam_direction.length_squared() < 0.0001:
		beam_direction = Vector2.RIGHT
	beam_direction = beam_direction.normalized()
	# origin = position de L'ŒIL (déjà décalée par l'appelant), pas celle
	# de Cendre — voir notes de la recette, le rayon part de la créature.
	_recipe_run_id = VfxRecipeRegistry.play(RECIPE_ID, {
		"origin": global_position,
		"seed": CAST_SEED,
		"direction": beam_direction,
	})


func set_owner_stats(stats: Stats) -> void:
	_owner_stats = stats
	if _owner_stats != null and not _owner_stats.died.is_connected(_on_owner_died):
		_owner_stats.died.connect(_on_owner_died)


func _on_owner_died() -> void:
	VfxRecipeRegistry.cancel(_recipe_run_id, true)


## Annulable jusqu'à la fin de l'Ouverture (avant que le rayon ne parte).
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

	if not _beam_resolved and _tick >= BEAM_TICK:
		_beam_resolved = true
		_resolve_beam()

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


## "Perce tout sur sa trajectoire" — résolution INSTANTANÉE (contrairement
## à Corbeau Pâle/Serpent Creux qui translatent tick par tick, un rayon
## d'encre n'a pas de temps de trajet perceptible à l'échelle du jeu) :
## un seul appel à Targeting.enemies_in_line() sur toute BEAM_LENGTH_PX,
## TOUS les ennemis dans la ligne prennent le dégât ce même tick.
func _resolve_beam() -> void:
	var targets: Array = Targeting.enemies_in_line(get_tree(), global_position, beam_direction, BEAM_LENGTH_PX, BEAM_HALF_WIDTH_PX)
	if targets.is_empty():
		return
	for target in targets:
		target.take_damage(DAMAGE, global_position)
	CombatFeedback.register_hit("medium", true, "light_impact", "medium", beam_direction, true)


func get_current_tick() -> int:
	return _tick


func is_finished() -> bool:
	return _tick >= TOTAL_TICKS
