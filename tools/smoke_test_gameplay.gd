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
	await _check_combo()
	await _check_gueule_vide()

	_report()


## Sonde un état réel dans une boucle plutôt que de compter des
## `await physics_frame` un par un — même discipline que
## tools/capture_scene.gd (docs/worklog.md, Phase 0) : l'ordre entre la
## reprise d'un `await physics_frame` et le `_physics_process` d'un AUTRE
## nœud pour ce même pas n'est pas garanti, compter les réveils comme des
## ticks serait faux d'un cran, silencieusement. Retourne false (jamais
## une boucle infinie) si la condition n'est jamais atteinte.
func _wait_until(predicate: Callable, max_ticks: int = 400) -> bool:
	var n := 0
	while not predicate.call():
		if n >= max_ticks:
			return false
		await get_tree().physics_frame
		n += 1
	return true


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
	var sprite: AnimatedSprite2D = _player.get_node("AnimatedSprite2D")
	var anim_before: String = sprite.animation
	var pos_before: Vector2 = _player.global_position
	Input.action_press("ui_right")
	for i in range(6):
		await get_tree().physics_frame
	var anim_during: String = sprite.animation
	Input.action_release("ui_right")
	await get_tree().physics_frame
	var pos_after: Vector2 = _player.global_position
	var anim_after_stop: String = sprite.animation
	_checks.append({
		"name": "player_moves_right_on_input_and_updates_facing",
		"pass": pos_after.x > pos_before.x + 1.0 and _player.facing == Vector2.RIGHT,
		"detail": {"pos_before": str(pos_before), "pos_after": str(pos_after), "facing": str(_player.facing)},
	})
	_checks.append({
		"name": "sprite_animation_switches_idle_deplacement_idle",
		"pass": anim_before == "idle" and anim_during == "deplacement" and anim_after_stop == "idle",
		"detail": {"anim_before": anim_before, "anim_during": anim_during, "anim_after_stop": anim_after_stop},
	})


## Phase 1.4 : combo léger 3 coups — attack déclenche coup1, la fenêtre
## de chaînage sur les derniers ticks de RECOVERY avance vers coup2 sur
## un second appui, le coup applique dégâts+recul (mandat : "ce n'est pas
## une primitive du coup, c'est la réaction de l'ennemi"), et le combo
## revient seul à idle après une pleine recovery sans nouvel appui —
## Enemy.take_damage() et Targeting sont déjà éprouvés par les checks
## précédents, on ne les reteste pas ici, seulement la timeline du combo.
func _check_combo() -> void:
	var enemy := EnemyScene.instantiate()
	enemy.name = "EnemyForCombo"
	enemy.global_position = _player.global_position + Vector2(30, 0)  # < ATTACK_RANGE_PX (48px)
	add_child(enemy)
	await get_tree().physics_frame  # laisser le groupe "enemies" se peupler

	var sprite: AnimatedSprite2D = _player.get_node("AnimatedSprite2D")
	var hp_before: float = enemy.stats.hp

	Input.action_press("attack")
	await get_tree().physics_frame
	Input.action_release("attack")
	var started: bool = await _wait_until(func(): return _player._combo_step == 1, 10)
	var anim_step1: String = sprite.animation

	var hit_landed: bool = await _wait_until(
		func(): return enemy.stats.hp < hp_before,
		Player.ANTICIPATION_TICKS + Player.RELEASE_TICKS + 5)
	var hp_after_hit: float = enemy.stats.hp
	var enemy_pos_at_hit: Vector2 = enemy.global_position

	# Laisser quelques ticks au recul (Enemy._physics_process) pour
	# bouger visiblement avant de le mesurer.
	for i in range(8):
		await get_tree().physics_frame
	var enemy_pos_after_recoil: Vector2 = enemy.global_position

	var chain_window_start: int = Player.RECOVERY_TICKS - Player.CHAIN_WINDOW_TICKS
	var window_open: bool = await _wait_until(
		func(): return _player._combo_step == 1 and _player._combo_phase == Player.ComboPhase.RECOVERY and _player._combo_tick >= chain_window_start,
		Player.RECOVERY_TICKS + 5)
	Input.action_press("attack")
	await get_tree().physics_frame
	Input.action_release("attack")
	var chained: bool = await _wait_until(func(): return _player._combo_step == 2, 10)
	var anim_step2: String = sprite.animation

	var ended: bool = await _wait_until(
		func(): return _player._combo_step == 0,
		Player.ANTICIPATION_TICKS + Player.RELEASE_TICKS + Player.RECOVERY_TICKS + 10)
	# _end_combo() ne pousse pas l'anim "idle" elle-même — c'est
	# _handle_movement() qui le fait, au PROCHAIN _physics_process une
	# fois _combo_step revenu à 0 (les deux ne peuvent pas courir dans le
	# même appel, la branche est choisie en tête de _physics_process avant
	# que _advance_combo() ne remette _combo_step à 0). Un tick de plus
	# avant de lire l'anim, sinon lecture une frame trop tôt.
	await get_tree().physics_frame
	var anim_final: String = sprite.animation

	_checks.append({
		"name": "attack_input_starts_coup1",
		"pass": started and anim_step1 == "coup1",
		"detail": {"started": started, "anim": anim_step1},
	})
	_checks.append({
		"name": "combo_hit_damages_enemy_in_range",
		"pass": hit_landed and is_equal_approx(hp_before - hp_after_hit, Player.ATTACK_DAMAGE),
		"detail": {"hit_landed": hit_landed, "hp_before": hp_before, "hp_after": hp_after_hit},
	})
	_checks.append({
		"name": "combo_hit_applies_recoil_to_enemy",
		"pass": enemy_pos_after_recoil.x > enemy_pos_at_hit.x + 1.0,
		"detail": {"pos_at_hit": str(enemy_pos_at_hit), "pos_after_recoil": str(enemy_pos_after_recoil)},
	})
	_checks.append({
		"name": "chain_window_press_advances_to_coup2",
		"pass": window_open and chained and anim_step2 == "coup2",
		"detail": {"window_open": window_open, "chained": chained, "anim": anim_step2},
	})
	_checks.append({
		"name": "combo_returns_to_idle_after_full_recovery_without_input",
		"pass": ended and anim_final == "idle",
		"detail": {"ended": ended, "combo_step": _player._combo_step, "anim": anim_final},
	})


## Phase 1.5 : invocation "Gueule Vide" — appui sur "power1" fait
## apparaître la créature (scenes/gameplay/powers/gueule_vide.tscn) devant
## le joueur, elle joue son propre cast (42 ticks) et applique
## dégâts+recul sur la cible en zone au tick de contact — "pas une
## primitive de la recette", porté par Enemy.take_damage() comme le
## combo. Le cooldown (6s = 360 ticks) bloque un second appui immédiat.
## VfxDirector/VfxRecipeRegistry sont déjà éprouvés par
## tools/smoke_test_vfx_recipe.gd, on ne reteste pas leur mécanique ici,
## seulement l'intégration gameplay (spawn, cooldown, dégât/recul, fin de
## vie de la créature).
func _check_gueule_vide() -> void:
	_player.facing = Vector2.RIGHT
	var spawn_pos: Vector2 = _player.global_position + Vector2.RIGHT * Player.POWER1_SPAWN_DISTANCE_PX

	var enemy := EnemyScene.instantiate()
	enemy.name = "EnemyForGueuleVide"
	enemy.global_position = spawn_pos + Vector2(20, 0)  # dans ATTACK_RANGE_PX (48px) de la créature
	add_child(enemy)
	await get_tree().physics_frame  # laisser le groupe "enemies" se peupler

	var hp_before: float = enemy.stats.hp

	Input.action_press("power1")
	await get_tree().physics_frame
	Input.action_release("power1")

	var creature: GueuleVide = null
	var spawned: bool = await _wait_until(func():
		for child in get_children():
			if child is GueuleVide:
				creature = child
				return true
		return false
	, 10)

	var cooldown_armed: bool = _player._power1_cooldown_remaining > 0
	# Un second appui immédiat ne doit RIEN spawner de plus tant que le
	# cooldown court — jamais un deuxième cast gratuit en un tick.
	Input.action_press("power1")
	await get_tree().physics_frame
	Input.action_release("power1")
	var creature_count_after_second_press := 0
	for child in get_children():
		if child is GueuleVide:
			creature_count_after_second_press += 1

	var hit_landed: bool = await _wait_until(func(): return enemy.stats.hp < hp_before, GueuleVide.CONTACT_TICK + 5)
	var hp_after_hit: float = enemy.stats.hp

	for i in range(8):
		await get_tree().physics_frame
	var enemy_pos_after_recoil: Vector2 = enemy.global_position

	var creature_finished: bool = await _wait_until(func(): return spawned and not is_instance_valid(creature), GueuleVide.TOTAL_TICKS + 10)

	_checks.append({
		"name": "power1_input_spawns_gueule_vide_creature",
		"pass": spawned and cooldown_armed,
		"detail": {"spawned": spawned, "cooldown_remaining": _player._power1_cooldown_remaining},
	})
	_checks.append({
		"name": "power1_cooldown_blocks_immediate_second_cast",
		"pass": creature_count_after_second_press == 1,
		"detail": {"creature_count_after_second_press": creature_count_after_second_press},
	})
	_checks.append({
		"name": "gueule_vide_contact_damages_enemy_in_range",
		"pass": hit_landed and is_equal_approx(hp_before - hp_after_hit, GueuleVide.ATTACK_DAMAGE),
		"detail": {"hit_landed": hit_landed, "hp_before": hp_before, "hp_after": hp_after_hit},
	})
	_checks.append({
		"name": "gueule_vide_contact_applies_recoil_to_enemy",
		"pass": enemy_pos_after_recoil.x > spawn_pos.x + 20.0 + 1.0,
		"detail": {"enemy_pos_after_recoil": str(enemy_pos_after_recoil)},
	})
	_checks.append({
		"name": "gueule_vide_creature_frees_itself_after_cast",
		"pass": creature_finished,
		"detail": {"creature_finished": creature_finished},
	})


func _report() -> void:
	var all_pass := true
	for c in _checks:
		if not c["pass"]:
			all_pass = false
	print("SMOKE_TEST_RESULT ", JSON.stringify({"all_pass": all_pass, "checks": _checks}))
	get_tree().quit(0 if all_pass else 1)
