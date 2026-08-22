extends Node2D
class_name Projectile
## Projectile d'ennemi RANGED (G, GDD §10 : "pression à distance") —
## trajectoire rectiligne déterministe, fixée une seule fois à `configure()`
## (pas de homing, voir enemy.gd _execute_attack() : une trajectoire
## prévisible est ce qui rend un ennemi à distance lisible/évitable).
## Contact = distance simple au joueur, pas de CollisionShape/Area2D —
## cohérent avec le placeholder géométrique minimal déjà utilisé par Enemy
## et avec la discipline "hitboxes toujours géométriques".

const CONTACT_RADIUS_PX := 10.0
const MAX_LIFETIME_TICKS := 120  ## 2s @ 60/s — filet de sécurité si la cible meurt/quitte l'arène en vol.

var _direction: Vector2 = Vector2.RIGHT
var _speed_px_s: float = 240.0
var _damage: float = 6.0
var _ticks_remaining: int = MAX_LIFETIME_TICKS

## Phase R4 (retour croisé Gemini/ChatGPT, MANDAT SUITE v2) : audit a
## confirmé que ces deux valeurs étaient hardcodées "light"/"" ici,
## ignorant totalement les exports `hitstop_profile`/`shake_profile` de
## l'ennemi RANGED qui a tiré (morte-code — un futur Ranged plus lourd
## aurait eu beau régler `hitstop_profile = "medium"`, le projectile ne
## l'aurait jamais lu). `configure()` les reçoit maintenant de
## `enemy.gd::_spawn_projectile()`, même source de vérité que le contact
## MELEE.
var _hitstop_profile: String = "light"
var _shake_profile: String = ""


func configure(direction: Vector2, speed_px_s: float, damage: float, hitstop_profile: String = "light", shake_profile: String = "") -> void:
	_direction = direction.normalized() if direction.length_squared() > 0.0001 else Vector2.RIGHT
	_speed_px_s = speed_px_s
	_damage = damage
	_hitstop_profile = hitstop_profile
	_shake_profile = shake_profile


func _physics_process(_delta: float) -> void:
	# Un projectile ennemi est une entité côté ennemi (Phase R4, hit-stop
	# asymétrique) — is_enemy_frozen(), pas le générique is_frozen().
	if CombatFeedback.is_enemy_frozen():
		return
	_ticks_remaining -= 1
	if _ticks_remaining <= 0:
		queue_free()
		return
	global_position += _direction * (_speed_px_s / Engine.physics_ticks_per_second)

	var player: Node = Targeting.get_player(get_tree())
	if player == null:
		return
	if global_position.distance_to(player.global_position) <= CONTACT_RADIUS_PX:
		player.take_damage(_damage, global_position)
		# Point d'entrée unique register_hit() (Phase R4) — même seuil
		# SFX/camera-punch que le contact MELEE d'Enemy._execute_attack().
		CombatFeedback.register_hit(
			_hitstop_profile, false,
			"light_impact" if _hitstop_profile == "light" else "heavy_impact",
			_shake_profile, _direction,
			_hitstop_profile != "light" and _hitstop_profile != "none")
		queue_free()
