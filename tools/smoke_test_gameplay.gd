extends Node2D
## Test de correction headless pour le squelette gameplay Phase 1.2 —
## Player/Enemy/Stats/Targeting. Pas une capture visuelle (§13.3, réservée
## aux livrables à verdict Milan) : ici on vérifie juste que la logique
## fait ce qu'elle dit, avant de construire animations/combo/compétence
## par-dessus (§16.3 "vérifier avant de déclarer fini").
##
## Lancé par scripts/run_gameplay_smoke_test.sh, même mécanique headless
## que scripts/capture_headless.sh (xvfb + Vulkan logiciel, voir CLAUDE.md).

const PlayerScene := preload("res://scenes/gameplay/player.tscn")
const EnemyScene := preload("res://scenes/gameplay/enemy.tscn")

var _player: Player
var _enemy_near: Enemy
var _enemy_far: Enemy
var _checks: Array[Dictionary] = []


func _ready() -> void:
	_player = PlayerScene.instantiate()
	_player.global_position = Vector2(200, 180)
	add_child(_player)

	_enemy_near = EnemyScene.instantiate()
	_enemy_near.name = "EnemyNear"
	_enemy_near.global_position = Vector2(260, 180)  # 60px ≈ 1.9m, dans le rayon 3m
	add_child(_enemy_near)

	_enemy_far = EnemyScene.instantiate()
	_enemy_far.name = "EnemyFar"
	_enemy_far.global_position = Vector2(420, 180)  # 220px ≈ 6.9m, hors rayon 3m
	add_child(_enemy_far)

	await get_tree().physics_frame  # laisser les groupes ("enemies") se peupler

	_check_targeting()
	await _check_damage_and_recoil()
	await _check_death()
	await _check_movement()

	_report()


func _check_targeting() -> void:
	var radius_px: float = GameConstants.meters_to_px(3.0)
	var found: Node = Targeting.nearest_enemy_in_radius(get_tree(), _player.global_position, radius_px)
	_checks.append({
		"name": "targeting_nearest_in_radius_picks_near_not_far",
		"pass": found == _enemy_near,
		"detail": {"radius_px": radius_px, "found": str(found)},
	})


func _check_damage_and_recoil() -> void:
	var hp_before: float = _enemy_near.stats.hp
	var pos_before: Vector2 = _enemy_near.global_position
	_enemy_near.take_damage(10.0, _player.global_position)
	var hp_after_hit: float = _enemy_near.stats.hp

	for i in range(4):
		await get_tree().physics_frame

	var pos_after: Vector2 = _enemy_near.global_position
	_checks.append({
		"name": "take_damage_reduces_hp",
		"pass": is_equal_approx(hp_before - hp_after_hit, 10.0),
		"detail": {"hp_before": hp_before, "hp_after": hp_after_hit},
	})
	_checks.append({
		"name": "take_damage_applies_recoil_away_from_source",
		"pass": pos_after.x > pos_before.x + 0.5,  # attaque venait de la gauche (player) -> recul vers +x
		"detail": {"pos_before": str(pos_before), "pos_after": str(pos_after)},
	})


func _check_death() -> void:
	var was_in_group_before: bool = _enemy_near.is_in_group("enemies")
	_enemy_near.take_damage(1000.0, _player.global_position)
	var dead_flag: bool = _enemy_near.is_dead()
	await get_tree().physics_frame
	await get_tree().physics_frame
	_checks.append({
		"name": "lethal_damage_marks_dead_and_frees_node",
		"pass": was_in_group_before and dead_flag and not is_instance_valid(_enemy_near),
		"detail": {"was_in_group_before": was_in_group_before, "dead_flag": dead_flag, "still_valid": is_instance_valid(_enemy_near)},
	})


func _check_movement() -> void:
	var pos_before: Vector2 = _player.global_position
	Input.action_press("ui_right")
	for i in range(6):
		await get_tree().physics_frame
	Input.action_release("ui_right")
	var pos_after: Vector2 = _player.global_position
	_checks.append({
		"name": "player_moves_right_on_input_and_updates_facing",
		"pass": pos_after.x > pos_before.x + 1.0 and _player.facing == Vector2.RIGHT,
		"detail": {"pos_before": str(pos_before), "pos_after": str(pos_after), "facing": str(_player.facing)},
	})


func _report() -> void:
	var all_pass := true
	for c in _checks:
		if not c["pass"]:
			all_pass = false
	print("SMOKE_TEST_RESULT ", JSON.stringify({"all_pass": all_pass, "checks": _checks}))
	get_tree().quit(0 if all_pass else 1)
