extends CharacterBody2D
class_name BossGateMaw
## Gate Maw (H2, GDD §15 : "boss tutoriel, masse organique de Gate avec
## grande gueule ; morsure, charge, projection, frappe au sol, phase
## énervée"). Silhouette unique (§15), pas un archétype générique comme
## Enemy.gd — Crawler/Brute/Ranged partagent un seul script parce qu'ils
## SONT interchangeables au-delà des chiffres ; un boss ne l'est pas :
## rotation fixe de 4 attaques distinctes, jamais un seul contact répété.
##
## Rotation DÉTERMINISTE [Morsure, Charge, Frappe au sol, Projection],
## jamais un tirage aléatoire : un "boss tutoriel" doit montrer chaque
## attaque dans un ordre prévisible pour que le joueur les apprenne une
## par une — et le garde-fou "seed toujours déterministe" (mandat §9)
## s'applique aussi bien à une décision de combat qu'à un chemin VFX ; le
## plus sûr pour le respecter ici est de ne tirer aucun nombre du tout.
##
## `take_damage()`/le recul subi/`_visual` reprennent Enemy.gd tels
## quels (même contrat HitResponse) — seule la couche décision change.

enum Attack { BITE, CHARGE, SLAM, PROJECTION }
enum State { IDLE, CHASE, TELEGRAPH, CHARGE_DASH, RECOVER }

const ATTACK_ROTATION := [Attack.BITE, Attack.CHARGE, Attack.SLAM, Attack.PROJECTION]
const SLAM_TELEGRAPH_SEED := 71001  ## Addendum A §A.5 : jamais l'horloge murale, même discipline que Player.BRAS_FAUX_CAST_SEED.

@export var stats: Stats = Stats.new()
@export var xp_reward: float = 120.0  ## H1 (GDD §20) — récompense de fin de Gate, nettement au-dessus des ennemis normaux (G).

@export var aggro_radius_px: float = 320.0

## Morsure — contact court, la plus rapide des 4, sert de première prise
## de contact quand le joueur approche.
@export var bite_range_px: float = 55.0
@export var bite_telegraph_ticks: int = 20
@export var bite_damage: float = 16.0
@export var bite_recoil_px: float = 26.0

## Charge — seule attaque qui couvre la distance elle-même (trigger_range
## large, contrairement aux 3 autres qui exigent déjà le contact).
@export var charge_trigger_range_px: float = 260.0
@export var charge_telegraph_ticks: int = 30
@export var charge_dash_ticks: int = 14
@export var charge_dash_distance_px: float = 220.0
## > rayon de collision du boss (30px) + celui du joueur (10px) = 40px —
## une marge trop juste : les deux corps se bloquent physiquement en
## contact à ~40px (move_and_slide() ne laisse jamais deux capsules se
## chevaucher), donc un seuil ÉGAL à cette distance échoue en permanence
## dès que le boss a déjà rejoint le joueur avant même de charger (ce
## qui arrive dès que le cooldown expire pendant qu'il le talonne déjà
## en CHASE) — trouvé par boss_attack_rotation_hits_player_with_all_four_attacks,
## pas en relisant le code : Charge ratait son coup à chaque fois.
@export var charge_contact_radius_px: float = 60.0
@export var charge_damage: float = 24.0
@export var charge_recoil_px: float = 40.0

## Frappe au sol — AOE autour du boss, télégraphée par un `groundRing`
## (primitive VFX existante, jamais dupliquée) : le joueur voit le
## rayon exact avant l'impact, la contre-mesure est de sortir du cercle.
@export var slam_telegraph_ticks: int = 34
@export var slam_radius_px: float = 100.0
@export var slam_damage: float = 26.0
@export var slam_recoil_px: float = 36.0

## Projection — dégâts bruts plus faibles que Frappe au sol, mais le
## PLUS gros recul des 4 : sa signature est de repousser, pas de punir.
@export var projection_range_px: float = 60.0
@export var projection_telegraph_ticks: int = 26
@export var projection_damage: float = 14.0
@export var projection_recoil_px: float = 70.0

@export var attack_cooldown_ticks: int = 70
@export var attack_recover_ticks: int = 16

## Phase énervée (GDD §15) — bascule UNE fois, jamais réversible, au
## seuil de PV. Cooldown/recovery resserrés + vitesse accrue ; teinte de
## base décalée vers le rouge chaud en permanence (tell lisible même
## hors télégraphe) — voir _enraged_tint().
@export var enrage_hp_ratio: float = 0.4
@export var enrage_cooldown_ticks: int = 40
@export var enrage_recover_ticks: int = 10
@export var enrage_speed_multiplier: float = 1.25

var _recoil_ticks_remaining: int = 0
var _recoil_velocity: Vector2 = Vector2.ZERO

var _state: int = State.IDLE
var _state_tick: int = 0
var _attack_index: int = 0
var _current_attack: int = Attack.BITE
var _cooldown_remaining: int = 0
var _base_visual_color: Color = Color.WHITE
var _base_move_speed_px: float = 0.0
var _enraged: bool = false

var _charge_direction: Vector2 = Vector2.RIGHT
var _charge_hit_applied: bool = false

signal hit(amount: float)
signal enraged

@onready var _visual: CanvasItem = $Placeholder


func _ready() -> void:
	add_to_group("enemies")
	if _visual is Polygon2D:
		_base_visual_color = (_visual as Polygon2D).color
	_base_move_speed_px = stats.move_speed_px


func _physics_process(_delta: float) -> void:
	if CombatFeedback.is_frozen():
		return
	if _recoil_ticks_remaining > 0:
		_recoil_ticks_remaining -= 1
		velocity = _recoil_velocity
		_recoil_velocity = _recoil_velocity.move_toward(Vector2.ZERO, _recoil_velocity.length() / max(1, _recoil_ticks_remaining + 1))
		move_and_slide()
		return
	if is_dead():
		return
	_check_enrage()
	if _cooldown_remaining > 0:
		_cooldown_remaining -= 1
	_run_ai()
	# Même garde-fou que G (Enemy.gd) : move_and_slide() UNIQUEMENT si un
	# vrai déplacement est demandé, jamais à chaque tick inconditionnellement.
	if velocity != Vector2.ZERO:
		move_and_slide()


func is_dead() -> bool:
	return stats.is_dead()


func _check_enrage() -> void:
	if _enraged or stats.max_hp <= 0.0:
		return
	if stats.hp / stats.max_hp <= enrage_hp_ratio:
		_enraged = true
		stats.move_speed_px = _base_move_speed_px * enrage_speed_multiplier
		enraged.emit()


## Même contrat qu'Enemy.take_damage() (source_position/recoil pour le
## recul subi), + crédite xp_reward au joueur à la mort comme G/H1.
func take_damage(amount: float, source_position: Vector2, recoil_strength_px: float = 24.0, recoil_ticks: int = 6) -> void:
	if is_dead():
		return
	stats.apply_damage(amount)
	hit.emit(amount)
	var away: Vector2 = (global_position - source_position)
	if away.length_squared() < 0.0001:
		away = Vector2.RIGHT
	away = away.normalized()
	_recoil_velocity = away * (recoil_strength_px * Engine.physics_ticks_per_second / max(1, recoil_ticks))
	_recoil_ticks_remaining = recoil_ticks

	HitResponse.flash_sprite(_visual)
	HitResponse.spawn_damage_number(amount, global_position, get_parent())

	if is_dead():
		var player: Node = Targeting.get_player(get_tree())
		if player != null:
			player.stats.add_xp(xp_reward)
		HitResponse.spawn_death_response(global_position, away, get_parent())
		queue_free()


func _run_ai() -> void:
	var player: Node = Targeting.get_player(get_tree())
	if player == null:
		velocity = Vector2.ZERO
		_state = State.IDLE
		_state_tick = 0
		return

	var to_player: Vector2 = player.global_position - global_position
	var dist: float = to_player.length()

	match _state:
		State.TELEGRAPH:
			velocity = Vector2.ZERO
			_advance_telegraph()
		State.CHARGE_DASH:
			_advance_charge_dash(player)
		State.RECOVER:
			velocity = Vector2.ZERO
			_state_tick += 1
			if _state_tick >= _current_recover_ticks():
				_state = State.CHASE
				_state_tick = 0
				_cooldown_remaining = _current_cooldown_ticks()
		_:  # IDLE, CHASE
			if dist > aggro_radius_px:
				_state = State.IDLE
				velocity = Vector2.ZERO
				return
			_state = State.CHASE
			if _cooldown_remaining <= 0 and _next_attack_ready(dist):
				_start_telegraph(to_player)
				return
			velocity = (to_player / dist) * stats.move_speed_px if dist > 0.0001 else Vector2.ZERO


## SLAM se déclenche sur une zone plus large que son propre rayon
## (×1.5) : le boss n'a pas besoin d'être collé au joueur pour LANCER
## l'attaque, seulement d'être raisonnablement proche — la vérification
## de contact réelle, elle, se refait en fin de télégraphe avec le rayon
## exact (le joueur a pu sortir du cercle entre-temps, c'est le point).
func _next_attack_ready(dist: float) -> bool:
	match ATTACK_ROTATION[_attack_index]:
		Attack.BITE:
			return dist <= bite_range_px
		Attack.CHARGE:
			return dist <= charge_trigger_range_px
		Attack.SLAM:
			return dist <= slam_radius_px * 1.5
		Attack.PROJECTION:
			return dist <= projection_range_px
	return false


func _start_telegraph(to_player: Vector2) -> void:
	_current_attack = ATTACK_ROTATION[_attack_index]
	_state = State.TELEGRAPH
	_state_tick = 0
	velocity = Vector2.ZERO
	if _current_attack == Attack.CHARGE:
		_charge_direction = to_player.normalized() if to_player.length_squared() > 0.0001 else Vector2.RIGHT
	elif _current_attack == Attack.SLAM:
		VfxDirector.spawn("groundRing", {
			"seed": SLAM_TELEGRAPH_SEED,
			"origin": global_position,
			"lifetime_ticks": slam_telegraph_ticks,
			"scale_px": slam_radius_px,
			"hue_deg": 12.0,
			"saturation_percent": 65.0,
			"value_percent": 55.0,
			"degradable": false,
		})


func _advance_telegraph() -> void:
	var total: int = _telegraph_ticks_for(_current_attack)
	_pulse_telegraph_color(float(_state_tick) / float(max(1, total)))
	_state_tick += 1
	if _state_tick >= total:
		_execute_attack()


func _telegraph_ticks_for(attack: int) -> int:
	match attack:
		Attack.BITE:
			return bite_telegraph_ticks
		Attack.CHARGE:
			return charge_telegraph_ticks
		Attack.SLAM:
			return slam_telegraph_ticks
		Attack.PROJECTION:
			return projection_telegraph_ticks
	return bite_telegraph_ticks


## BITE/SLAM/PROJECTION se résolvent en un seul tick, distance recalculée
## fraîche (le joueur a pu bouger pendant tout le télégraphe). CHARGE, à
## l'inverse, n'inflige rien ici : elle bascule vers CHARGE_DASH, une
## timeline à part avec sa propre fenêtre de contact.
func _execute_attack() -> void:
	_reset_visual_color()
	var player: Node = Targeting.get_player(get_tree())
	match _current_attack:
		Attack.BITE:
			if player != null and global_position.distance_to(player.global_position) <= bite_range_px * 1.4:
				player.take_damage(bite_damage, global_position, bite_recoil_px)
				CombatFeedback.trigger_hitstop("light")
			_advance_rotation_to_recover()
		Attack.PROJECTION:
			if player != null and global_position.distance_to(player.global_position) <= projection_range_px * 1.4:
				player.take_damage(projection_damage, global_position, projection_recoil_px)
				CombatFeedback.trigger_hitstop("light")
				CombatFeedback.trigger_shake("light", player.global_position - global_position)
			_advance_rotation_to_recover()
		Attack.SLAM:
			if player != null and global_position.distance_to(player.global_position) <= slam_radius_px:
				player.take_damage(slam_damage, global_position, slam_recoil_px)
				CombatFeedback.trigger_hitstop("medium")
				CombatFeedback.trigger_shake("medium", Vector2.ZERO)
			_advance_rotation_to_recover()
		Attack.CHARGE:
			_state = State.CHARGE_DASH
			_state_tick = 0
			_charge_hit_applied = false


func _advance_charge_dash(player: Node) -> void:
	if not _charge_hit_applied and player != null and global_position.distance_to(player.global_position) <= charge_contact_radius_px:
		player.take_damage(charge_damage, global_position, charge_recoil_px)
		CombatFeedback.trigger_hitstop("medium")
		CombatFeedback.trigger_shake("light", _charge_direction)
		_charge_hit_applied = true

	var progress_before: float = float(_state_tick) / float(charge_dash_ticks)
	var progress_after: float = float(_state_tick + 1) / float(charge_dash_ticks)
	var step_px: float = (minf(progress_after, 1.0) - minf(progress_before, 1.0)) * charge_dash_distance_px
	velocity = _charge_direction * (step_px * Engine.physics_ticks_per_second)

	_state_tick += 1
	if _state_tick >= charge_dash_ticks:
		_advance_rotation_to_recover()


func _advance_rotation_to_recover() -> void:
	_attack_index = (_attack_index + 1) % ATTACK_ROTATION.size()
	_state = State.RECOVER
	_state_tick = 0


func _current_cooldown_ticks() -> int:
	return enrage_cooldown_ticks if _enraged else attack_cooldown_ticks


func _current_recover_ticks() -> int:
	return enrage_recover_ticks if _enraged else attack_recover_ticks


## Même lisibilité de télégraphe que G (Enemy._pulse_telegraph_color) —
## fonction du tick, jamais un Tween temps réel — mais teinte chaude
## (orange-rouge) distincte du blanc générique des ennemis normaux : un
## boss doit se lire comme plus dangereux, pas comme un Crawler de plus.
func _pulse_telegraph_color(progress: float) -> void:
	if _visual is Polygon2D:
		var base: Color = _enraged_tint(_base_visual_color)
		(_visual as Polygon2D).color = base.lerp(Color(1.0, 0.3, 0.1, 1.0), clampf(progress, 0.0, 1.0))


func _reset_visual_color() -> void:
	if _visual is Polygon2D:
		(_visual as Polygon2D).color = _enraged_tint(_base_visual_color)


func _enraged_tint(base: Color) -> Color:
	if not _enraged:
		return base
	return base.lerp(Color(1.0, 0.15, 0.05, 1.0), 0.35)
