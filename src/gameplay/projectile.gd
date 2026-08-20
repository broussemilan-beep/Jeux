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


func configure(direction: Vector2, speed_px_s: float, damage: float) -> void:
	_direction = direction.normalized() if direction.length_squared() > 0.0001 else Vector2.RIGHT
	_speed_px_s = speed_px_s
	_damage = damage


func _physics_process(_delta: float) -> void:
	if CombatFeedback.is_frozen():
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
		CombatFeedback.trigger_hitstop("light")
		queue_free()
