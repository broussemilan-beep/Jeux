extends CharacterBody2D
class_name Player
## Personnage jouable — mouvement 8 directions + stats + animations de
## base (Phase 1.3) + combo léger 3 coups (Phase 1.4). `AnimatedSprite2D`
## + `SpriteFrames` cuits par scripts/cook_character_frames.py, direction
## sud uniquement pour l'instant — voir docs/worklog.md.
##
## Entrée : actions UI par défaut de Godot (ui_left/right/up/down) pour le
## mouvement — aucune exigence de contrôles réels dans le mandat Phase 1.
## Une action dédiée "attack" existe dans project.godot (espace + clic
## gauche) car le combo, lui, a besoin d'un input propre à détecter au
## tick près (just_pressed), ce que les actions ui_* génériques ne
## garantissent pas aussi proprement pour du timing de combat.

const AttackAnimName := ["coup1", "coup2", "coup3"]

## Timeline d'un coup, en ticks (60/s) — §6.2 du doc VFX donne des
## fourchettes pour les VFX/animations premium (anticipation 25-40%,
## release 5-12%, recovery 35-55%) ; ces chiffres respectent ces
## proportions pour un coup léger rapide (26 ticks ≈ 0,43s/coup).
const ANTICIPATION_TICKS := 8
const RELEASE_TICKS := 4
const RECOVERY_TICKS := 14
## Fenêtre de chaînage (mandat Phase 1.4 : "fenêtre de chaînage sur les
## derniers ticks de chaque RECOVERY") — dernier tiers de la recovery.
const CHAIN_WINDOW_TICKS := 6

const ATTACK_RANGE_PX := 48.0  # ~1.5m, GameConstants.PX_PER_METER
const ATTACK_DAMAGE := 10.0

const GueuleVideScene := preload("res://scenes/gameplay/powers/gueule_vide.tscn")

## Invocation "Gueule Vide" (INVOCATEUR, data/recipes/power.gueule_vide.cast.json) :
## "Portée d'invocation : 4m". La créature apparaît à une distance fixe
## (3m) dans l'axe du regard (facing), laissant sa propre zone d'attaque
## (~1,5m) porter le reste de la portée totale sans la dépasser.
## "Cooldown suggéré : 6s" -> 360 ticks @ 60/s.
const POWER1_SPAWN_DISTANCE_PX := 96.0  # GameConstants.meters_to_px(3.0)
const POWER1_COOLDOWN_TICKS := 360  # 6s @ 60/s

@export var stats: Stats = Stats.new()

## Direction de face courante (8 valeurs), utile aux futures frames
## directionnelles PixelLab (Phase 1.3+, 7 directions restantes) — mis à
## jour uniquement quand il y a un mouvement réel, jamais remis à zéro à
## l'arrêt (le perso garde sa dernière orientation).
var facing: Vector2 = Vector2.DOWN

## Verrouille l'animation de mouvement (idle/déplacement) pendant qu'une
## action ponctuelle (hurt/dash/mort/combo) joue — sinon _physics_process
## écraserait la pose dès la frame suivante. Pour hurt/dash, levé par
## _on_sprite_animation_finished(). Pour le combo, la timeline en ticks
## ci-dessus est SEULE responsable du verrou (_end_combo()) — le combo ne
## doit jamais dépendre du timing de lecture du sprite, qui est une
## horloge séparée (§16.3 : ne pas fusionner deux minuteries distinctes).
var _action_lock: bool = false

## 0 = pas d'attaque en cours. 1-3 = quel coup du combo joue actuellement.
var _combo_step: int = 0
enum ComboPhase { NONE, ANTICIPATION, RELEASE, RECOVERY }
var _combo_phase: int = ComboPhase.NONE
var _combo_tick: int = 0
var _attack_queued: bool = false
var _hit_applied_this_release: bool = false

## Gueule Vide n'utilise PAS _action_lock : l'invocation (0,7s) n'immobilise
## pas le joueur (rien dans le mandat ne l'exige, contrairement au combo/
## dash) — seul un cooldown la borne dans le temps.
var _power1_cooldown_remaining: int = 0

@onready var _sprite: AnimatedSprite2D = $AnimatedSprite2D


func _ready() -> void:
	_sprite.animation_finished.connect(_on_sprite_animation_finished)


func _physics_process(_delta: float) -> void:
	if _power1_cooldown_remaining > 0:
		_power1_cooldown_remaining -= 1

	if Input.is_action_just_pressed("attack"):
		_attack_queued = true

	if Input.is_action_just_pressed("power1") and not stats.is_dead() and _power1_cooldown_remaining <= 0:
		_cast_gueule_vide()

	if _combo_step > 0:
		velocity = Vector2.ZERO
		_advance_combo()
	elif _attack_queued and not stats.is_dead() and not _action_lock:
		_attack_queued = false
		velocity = Vector2.ZERO
		_start_attack(1)
	else:
		_handle_movement()

	move_and_slide()


func _handle_movement() -> void:
	var input_dir := Vector2(
		Input.get_action_strength("ui_right") - Input.get_action_strength("ui_left"),
		Input.get_action_strength("ui_down") - Input.get_action_strength("ui_up")
	)
	if input_dir.length_squared() > 1.0:
		input_dir = input_dir.normalized()

	velocity = input_dir * stats.move_speed_px
	if input_dir.length_squared() > 0.0001:
		facing = input_dir.normalized()

	if not _action_lock and not stats.is_dead():
		_sprite.play("deplacement" if input_dir.length_squared() > 0.0001 else "idle")


func _start_attack(step: int) -> void:
	_combo_step = step
	_combo_phase = ComboPhase.ANTICIPATION
	_combo_tick = 0
	_hit_applied_this_release = false
	_action_lock = true
	_sprite.play(AttackAnimName[step - 1])


## Timeline déclarative du coup courant — ANTICIPATION -> RELEASE (frappe
## au premier tick) -> RECOVERY (fenêtre de chaînage sur les derniers
## CHAIN_WINDOW_TICKS). Ne dépend jamais de la durée réelle de lecture du
## sprite, uniquement des compteurs de ticks ci-dessous — sinon changer la
## fps d'une anim de coup déréglerait silencieusement le combat.
func _advance_combo() -> void:
	_combo_tick += 1
	match _combo_phase:
		ComboPhase.ANTICIPATION:
			if _combo_tick >= ANTICIPATION_TICKS:
				_combo_phase = ComboPhase.RELEASE
				_combo_tick = 0
		ComboPhase.RELEASE:
			if _combo_tick == 1 and not _hit_applied_this_release:
				_try_hit()
				_hit_applied_this_release = true
			if _combo_tick >= RELEASE_TICKS:
				_combo_phase = ComboPhase.RECOVERY
				_combo_tick = 0
		ComboPhase.RECOVERY:
			var chain_window_start := RECOVERY_TICKS - CHAIN_WINDOW_TICKS
			if _combo_tick >= chain_window_start and _combo_step < AttackAnimName.size() and _attack_queued:
				_attack_queued = false
				_start_attack(_combo_step + 1)
				return
			if _combo_tick >= RECOVERY_TICKS:
				_end_combo()


func _end_combo() -> void:
	_combo_step = 0
	_combo_phase = ComboPhase.NONE
	_combo_tick = 0
	_attack_queued = false
	_action_lock = false


## Un seul coup = une seule cible (mandat : "combo léger", pas une
## attaque en zone — ça, c'est le Totem). Réutilise Targeting, déjà
## éprouvé par le Totem/smoke test, plutôt que d'inventer une seconde
## recherche de cible.
func _try_hit() -> void:
	var target: Node = Targeting.nearest_enemy_in_radius(get_tree(), global_position, ATTACK_RANGE_PX)
	if target == null:
		return
	target.take_damage(ATTACK_DAMAGE, global_position)
	# impactFlashFrame + recoil sur chaque coup (mandat Phase 1.4). Le
	# recoil est déjà porté par Enemy.take_damage() (§4 : réaction de la
	# cible, jamais une primitive de l'attaquant) — ici on ne pose QUE le
	# flash d'impact, seule primitive qui appartient au coup lui-même.
	VfxDirector.spawn("impactFlashFrame", {
		"seed": 0,
		"origin": target.global_position,
		"lifetime_ticks": 2,
		"overdraw_cost": 12.0,
	})


## Invocation "Gueule Vide" — instancie la créature en avant du joueur
## (facing), démarre son cast (42 ticks, autonome — voir gueule_vide.gd),
## pose le cooldown. N'appelle pas VfxRecipeRegistry directement : c'est
## la créature elle-même qui joue sa recette, ce script ne fait qu'un
## spawn de gameplay, comme Player._try_hit() spawne juste
## impactFlashFrame sans piloter le reste du VFX.
func _cast_gueule_vide() -> void:
	_power1_cooldown_remaining = POWER1_COOLDOWN_TICKS
	var dir := facing
	if dir.length_squared() < 0.0001:
		dir = Vector2.DOWN
	dir = dir.normalized()

	var creature: Node2D = GueuleVideScene.instantiate()
	creature.global_position = global_position + dir * POWER1_SPAWN_DISTANCE_PX
	get_parent().add_child(creature)


func is_dead() -> bool:
	return stats.is_dead()


## Réaction à un coup subi — pas encore appelée par du vrai gameplay dans
## cette tranche verticale (aucun ennemi n'attaque le joueur, hors scope
## Phase 1), mais l'animation existe et le hook est prêt pour quand le
## combat réel arrivera.
func play_hurt() -> void:
	if stats.is_dead():
		return
	_action_lock = true
	_sprite.play("hurt")


func play_dash() -> void:
	if stats.is_dead() or _action_lock:
		return
	_action_lock = true
	_sprite.play("dash")


func _on_sprite_animation_finished() -> void:
	if _combo_step > 0:
		return  # le combo gère son propre verrou via sa timeline de ticks (_end_combo())
	if _sprite.animation == "mort":
		return  # reste sur la dernière frame, jamais reverrouillé sur idle
	_action_lock = false


func die() -> void:
	stats.hp = 0.0
	_combo_step = 0
	_combo_phase = ComboPhase.NONE
	_attack_queued = false
	_action_lock = true
	_sprite.play("mort")
