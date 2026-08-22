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
const GueuleVideScene := preload("res://scenes/gameplay/powers/gueule_vide.tscn")
const EnemyCrawlerScene := preload("res://scenes/gameplay/enemy_crawler.tscn")
const EnemyBruteScene := preload("res://scenes/gameplay/enemy_brute.tscn")
const EnemyRangedScene := preload("res://scenes/gameplay/enemy_ranged.tscn")
const BossGateMawScene := preload("res://scenes/gameplay/boss_gate_maw.tscn")

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

	_check_input_map_has_no_stray_mouse_bindings()
	_check_targeting()
	await _check_damage_and_recoil()
	await _check_death()
	await _check_movement()
	await _check_combo()
	await _check_combo_tier_feedback()
	await _check_dash()
	await _check_gueule_vide()
	await _check_gueule_vide_owner_death_policy()
	await _check_hit_response()
	await _check_animation_composer_and_camera()
	await _check_dodge()
	await _check_bras_faux()
	await _check_poing_belluaire()
	await _check_poing_tellurique()
	await _check_power_slot_gating()
	await _check_player_recoils_on_taking_damage()
	await _check_crawler_chases_and_hits_player()
	await _check_brute_telegraphs_before_hitting()
	await _check_ranged_keeps_distance_and_fires_projectile()
	_check_stats_add_xp_levels_up()
	await _check_enemy_death_awards_xp_to_player()
	await _check_boss_attack_rotation_hits_player_with_all_four_attacks()
	await _check_boss_slam_spares_player_outside_radius_but_hits_inside()
	await _check_boss_enrages_at_hp_threshold()
	await _check_boss_death_awards_xp_reward()
	await _check_gate_room_locks_until_cleared()
	await _check_xp_pickup_grants_xp_and_frees_itself()
	await _check_heal_zone_heals_player_to_full()
	await _check_gate_exit_emits_signal_on_player_contact()
	await _check_run_state_persists_player_stats_across_new_player_instances()
	await _check_gate_entrance_detects_player_once_and_targets_the_gate_scene()
	await _check_gate_premiere_wires_exit_signal_to_a_handler()
	await _check_character_screen_toggles_open_closed_and_shows_class_none()

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


## Phase R1 (retour croisé Gemini/ChatGPT sur clip réel, MANDAT SUITE v2) :
## un InputEventMouseButton sans zone restreinte sur "attack" faisait
## qu'un touché n'importe où sur l'écran déclenchait une attaque sur le
## web export tactile — retiré de project.godot, mais un test headless
## classique (Input.action_press()) ne l'aurait jamais détecté, puisqu'il
## contourne l'InputMap. Vérifie directement la configuration réelle de
## chaque action gameplay plutôt que son effet simulé, pour empêcher ce
## bug précis de revenir silencieusement (ex. un remap futur qui
## réintroduit un binding souris générique).
func _check_input_map_has_no_stray_mouse_bindings() -> void:
	var gameplay_actions := ["attack", "power1", "power2", "power3", "power4", "power5", "dash", "dodge", "character_screen"]
	var offenders: Array[String] = []
	for action_name in gameplay_actions:
		for event in InputMap.action_get_events(action_name):
			if event is InputEventMouseButton:
				offenders.append(action_name)
	_checks.append({
		"name": "gameplay_actions_have_no_mouse_button_bindings",
		"pass": offenders.is_empty(),
		"detail": {"offenders": offenders, "checked": gameplay_actions},
	})


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
		# E (mandat production v1 §6) : art réel par direction depuis
		# cette tranche — "idle"/"deplacement" simples n'existent plus
		# comme noms d'anim, remplacés par idle_<dir>/deplacement_<dir>.
		# facing par défaut = Vector2.DOWN ("south") avant tout mouvement ;
		# une pression "ui_right" fait facing=RIGHT ("east"), qui RESTE
		# est après l'arrêt (facing ne se réinitialise jamais tout seul).
		"name": "sprite_animation_switches_idle_deplacement_idle",
		"pass": anim_before == "idle_south" and anim_during == "deplacement_east" and anim_after_stop == "idle_east",
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
		# facing hérité de _check_movement() (east, jamais retouché ici,
		# aucun input directionnel dans ce check) — E (§6) : "idle_east",
		# plus le simple "idle" d'avant l'art par direction.
		"name": "combo_returns_to_idle_after_full_recovery_without_input",
		"pass": ended and anim_final == "idle_east",
		"detail": {"ended": ended, "combo_step": _player._combo_step, "anim": anim_final},
	})

	# Nettoyage — "EnemyForCombo" survit à ce test (90/80 PV, jamais létal)
	# et RESTAIT dans l'arbre indéfiniment avant ce correctif : inoffensif
	# tant que le joueur ne bougeait jamais pendant une attaque, mais le
	# root motion (mandat production v1 J1) le fait désormais avancer de
	# quelques px vers cet ennemi à CHAQUE coup — sur ce test, assez pour
	# que "EnemyForCombo" finisse par être plus proche du joueur que le
	# nouvel ennemi placé par _check_combo_tier_feedback() (toujours à
	# +30px de la position COURANTE du joueur), et Targeting.
	# nearest_enemy_in_radius() ciblait alors silencieusement le mauvais
	# ennemi — les 3 checks de _check_combo_tier_feedback() lisaient les
	# PV d'un ennemi jamais touché. Bug de test réel trouvé en câblant le
	# root motion, pas une supposition (docs/worklog.md).
	enemy.queue_free()
	await get_tree().physics_frame


## Compte les ticks pendant lesquels CombatFeedback reste gelé À PARTIR
## de maintenant — utile pour distinguer "light" (1 tick, 12ms arrondi)
## de "medium" (2 ticks, 25ms arrondi) sans dépendre d'un accès privé à
## CombatFeedback, seulement de son API publique is_frozen().
func _drain_frozen_ticks() -> int:
	var n := 0
	while CombatFeedback.is_frozen():
		await get_tree().physics_frame
		n += 1
	return n


## B3 : feedback de combat par tier de combo (hit-stop/shake/arcSlash,
## src/gameplay/player.gd, COMBO_TIER_FEEDBACK) — vérifie que l'escalade
## réelle correspond au mandat (coup1 léger sans shake, coup2 avec
## arcSlash, coup3 avec un hit-stop plus long ET un shake visible),
## jamais juste que le code compile. CombatFeedback/VfxDirector sont déjà
## éprouvés par ailleurs (smoke_test_vfx_recipe.gd) — on ne reteste que
## l'intégration combo -> feedback ici.
func _check_combo_tier_feedback() -> void:
	var enemy := EnemyScene.instantiate()
	enemy.name = "EnemyForTierFeedback"
	enemy.global_position = _player.global_position + Vector2(30, 0)
	add_child(enemy)
	await get_tree().physics_frame  # laisser le groupe "enemies" se peupler

	# Coup 1 — hit-stop light (1 tick), pas de shake, pas d'arcSlash.
	var hp_before_1: float = enemy.stats.hp
	Input.action_press("attack")
	await get_tree().physics_frame
	Input.action_release("attack")
	await _wait_until(func(): return _player._combo_step == 1, 10)
	var hit1_landed: bool = await _wait_until(
		func(): return enemy.stats.hp < hp_before_1,
		Player.ANTICIPATION_TICKS + Player.RELEASE_TICKS + 5)
	# Phase R4 : le shake se décompte en ticks RÉELS (CombatFeedback ne se
	# gèle jamais lui-même) tandis que le hit-stop cible est maintenant
	# ASYMÉTRIQUE — sonder le shake ET le gel dans LA MÊME boucle (plutôt
	# que deux boucles séquentielles, dans un ordre ou dans l'autre) :
	# avec un gel "medium" désormais aussi long (4 ticks) que la fenêtre de
	# sonde du shake, mesurer l'un PUIS l'autre fait toujours rater le
	# premier des deux (déjà retombé pendant que le second était sondé).
	var shake_seen_tier1 := false
	var frozen_ticks_1 := 0
	var freeze_done_tier1 := false
	for i in range(6):
		if CombatFeedback.get_shake_offset() != Vector2.ZERO:
			shake_seen_tier1 = true
		if not freeze_done_tier1:
			if CombatFeedback.is_frozen():
				frozen_ticks_1 += 1
			else:
				freeze_done_tier1 = true
		await get_tree().physics_frame

	# Chaîner vers coup 2 dans la fenêtre de chaînage (même mécanique que
	# _check_combo()) — coup2 doit poser une couche arcSlash (2 ticks).
	VfxDirector.clear_log()
	var chain_window_start: int = Player.RECOVERY_TICKS - Player.CHAIN_WINDOW_TICKS
	await _wait_until(
		func(): return _player._combo_step == 1 and _player._combo_phase == Player.ComboPhase.RECOVERY and _player._combo_tick >= chain_window_start,
		Player.RECOVERY_TICKS + 5)
	var hp_before_2: float = enemy.stats.hp
	Input.action_press("attack")
	await get_tree().physics_frame
	Input.action_release("attack")
	await _wait_until(func(): return _player._combo_step == 2, 10)
	var hit2_landed: bool = await _wait_until(
		func(): return enemy.stats.hp < hp_before_2,
		Player.ANTICIPATION_TICKS + Player.RELEASE_TICKS + 5)
	var arc_slash_spawned := false
	for entry in VfxDirector.spawn_log:
		if entry["primitive"] == "arcSlash":
			arc_slash_spawned = true

	# Chaîner vers coup 3 — hit-stop medium (2 ticks, plus long que coup1)
	# ET shake visible (contrairement à coup1).
	await _wait_until(
		func(): return _player._combo_step == 2 and _player._combo_phase == Player.ComboPhase.RECOVERY and _player._combo_tick >= chain_window_start,
		Player.RECOVERY_TICKS + 5)
	var hp_before_3: float = enemy.stats.hp
	Input.action_press("attack")
	await get_tree().physics_frame
	Input.action_release("attack")
	await _wait_until(func(): return _player._combo_step == 3, 10)
	# Phase R4 : tier3 (finisher) a sa PROPRE anticipation, plus longue
	# que tier1/2 (COMBO_TIER_ANTICIPATION_TICKS), pas la constante plate.
	var hit3_landed: bool = await _wait_until(
		func(): return enemy.stats.hp < hp_before_3,
		Player.COMBO_TIER_ANTICIPATION_TICKS[2] + Player.RELEASE_TICKS + 5)
	# Phase R4 : shake et gel sondés dans LA MÊME boucle (voir commentaire
	# identique sur tier1 plus haut).
	var shake_seen_tier3 := false
	var frozen_ticks_3 := 0
	var freeze_done_tier3 := false
	for i in range(6):
		if CombatFeedback.get_shake_offset() != Vector2.ZERO:
			shake_seen_tier3 = true
		if not freeze_done_tier3:
			if CombatFeedback.is_frozen():
				frozen_ticks_3 += 1
			else:
				freeze_done_tier3 = true
		await get_tree().physics_frame

	# Phase R4 : hit-stop désormais ASYMÉTRIQUE (cible plus longue que
	# l'attaquant) — _drain_frozen_ticks() lit CombatFeedback.is_frozen()
	# (OR des deux compteurs), qui reste vrai jusqu'à ce que le PLUS LONG
	# des deux (toujours le compteur CIBLE ici, le joueur étant
	# l'attaquant) retombe à 0. Valeurs recalculées depuis
	# TARGET_HITSTOP_MS (light=31ms->2 ticks, medium=65ms->4 ticks à
	# 60/s) — plus les anciennes valeurs symétriques (1/2 ticks).
	_checks.append({
		"name": "combo_tier1_hitstop_light_no_shake",
		"pass": hit1_landed and frozen_ticks_1 == 2 and not shake_seen_tier1,
		"detail": {"hit_landed": hit1_landed, "frozen_ticks": frozen_ticks_1, "shake_seen": shake_seen_tier1},
	})
	_checks.append({
		"name": "combo_tier2_spawns_arc_slash",
		"pass": hit2_landed and arc_slash_spawned,
		"detail": {"hit_landed": hit2_landed, "arc_slash_spawned": arc_slash_spawned},
	})
	_checks.append({
		"name": "combo_tier3_hitstop_medium_longer_than_tier1_with_shake",
		"pass": hit3_landed and frozen_ticks_3 == 4 and frozen_ticks_3 > frozen_ticks_1 and shake_seen_tier3,
		"detail": {"hit_landed": hit3_landed, "frozen_ticks": frozen_ticks_3, "shake_seen": shake_seen_tier3},
	})


## B4 : refonte du dash (anticipation/ease-out/recovery/traînée/shake) —
## vérifie que le dash déplace réellement le joueur (contrairement à
## l'ancien play_dash(), qui ne faisait que jouer une animation sans
## aucune logique de déplacement — "se lit comme une téléportation"),
## verrouille les autres actions pendant sa timeline, déclenche un shake
## dès les premiers ticks et pose sa traînée de 2 after-images.
func _check_dash() -> void:
	# _check_combo_tier_feedback() ne vide pas le combo jusqu'à idle (elle
	# s'arrête juste après le coup 3, contrairement à _check_combo() qui,
	# elle, attend explicitement le retour à _combo_step == 0) — attendre
	# ici que _action_lock retombe avant de tester le dash, sinon
	# play_dash() se fait rejeter par son propre garde (_action_lock).
	await _wait_until(func(): return not _player._action_lock, Player.RECOVERY_TICKS + 5)

	# y=600, loin des ennemis des checks précédents (tous autour de
	# y=180) — sinon le dash percute leur CollisionShape2D et
	# move_and_slide() l'arrête après quelques pixels, un faux négatif
	# de collision, pas un bug de la timeline de déplacement elle-même.
	_player.global_position = Vector2(200, 600)
	_player.velocity = Vector2.ZERO
	_player.facing = Vector2.RIGHT
	var sprite: AnimatedSprite2D = _player.get_node("AnimatedSprite2D")
	var pos_before: Vector2 = _player.global_position

	var sprite2d_count_before := 0
	for child in _player.get_parent().get_children():
		if child is Sprite2D:
			sprite2d_count_before += 1

	Input.action_press("dash")
	await get_tree().physics_frame
	Input.action_release("dash")
	var started: bool = await _wait_until(func(): return _player._dash_phase != Player.DashPhase.NONE, 5)
	var anim_during: String = sprite.animation

	# Pendant le dash (verrouillé), un appui "attack" ne doit PAS démarrer
	# le combo — le dash garde la priorité, _action_lock bloque l'attaque.
	Input.action_press("attack")
	await get_tree().physics_frame
	Input.action_release("attack")
	var combo_started_during_dash: bool = _player._combo_step > 0

	# Shake actif dès les premiers ticks (mandat : "shake light dès le
	# premier tick") — même mécanique de lecture que
	# _check_combo_tier_feedback().
	var shake_seen := false
	for i in range(3):
		if CombatFeedback.get_shake_offset() != Vector2.ZERO:
			shake_seen = true
		await get_tree().physics_frame

	# Les 2 after-images (mandat) sont posées pendant MOVE — les compter
	# une fois MOVE écoulé (juste avant qu'un Tween de fondu ne commence à
	# en libérer), pas trop tard sinon elles ont déjà pu s'éteindre
	# (DASH_AFTERIMAGE_FADE_SEC ≈ 9 ticks après leur propre spawn).
	await _wait_until(
		func(): return _player._dash_phase == Player.DashPhase.RECOVERY or _player._dash_phase == Player.DashPhase.NONE,
		Player.DASH_ANTICIPATION_TICKS + Player.DASH_MOVE_TICKS + 5)
	var sprite2d_count_mid := 0
	for child in _player.get_parent().get_children():
		if child is Sprite2D:
			sprite2d_count_mid += 1

	var ended: bool = await _wait_until(
		func(): return _player._dash_phase == Player.DashPhase.NONE,
		Player.DASH_RECOVERY_TICKS + 5)
	var pos_after: Vector2 = _player.global_position
	var action_unlocked_after: bool = not _player._action_lock

	_checks.append({
		"name": "dash_input_starts_dash_and_plays_dash_anim",
		"pass": started and anim_during == "dash",
		"detail": {"started": started, "anim": anim_during},
	})
	_checks.append({
		"name": "dash_blocks_attack_input_while_locked",
		"pass": not combo_started_during_dash,
		"detail": {"combo_started_during_dash": combo_started_during_dash},
	})
	_checks.append({
		"name": "dash_shake_visible_from_early_ticks",
		"pass": shake_seen,
		"detail": {"shake_seen": shake_seen},
	})
	_checks.append({
		"name": "dash_spawns_two_afterimage_ghosts",
		"pass": sprite2d_count_mid - sprite2d_count_before == 2,
		"detail": {"before": sprite2d_count_before, "mid": sprite2d_count_mid},
	})
	_checks.append({
		"name": "dash_displaces_player_by_roughly_dash_distance_then_unlocks",
		"pass": ended and action_unlocked_after
			and pos_after.x > pos_before.x + Player.DASH_DISTANCE_PX * 0.9
			and pos_after.x < pos_before.x + Player.DASH_DISTANCE_PX * 1.6,
		"detail": {"pos_before": str(pos_before), "pos_after": str(pos_after), "ended": ended, "action_unlocked_after": action_unlocked_after},
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
	# Amendement GDD Pouvoir/déblocage : "power1" n'est plus lié en dur à
	# Gueule Vide, il faut que le Pouvoir actif de cette run soit
	# Invocateur pour que le slot 1 (tier 1, palier niveau 1, déjà
	# atteint par défaut) résolve vers _cast_gueule_vide().
	RunState.active_power = "invocateur"
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

	# Sans ce nettoyage, "EnemyForGueuleVide" reste dans "enemies" à y=600
	# (même zone que _check_dash()/_check_animation_composer_and_camera()) —
	# bug de non-isolation déjà documenté pour "EnemyForCombo" : un check
	# ultérieur qui spawne SON propre ennemi peut se faire voler sa cible
	# par ce résidu, en silence (le combo avance quand même sur un swing à
	# vide — voir player.gd, "swing à vide" — donc rien ne crashe, juste
	# aucun dégât ne tombe sur le mauvais ennemi visé par le test).
	enemy.queue_free()
	await get_tree().physics_frame


## Addendum A, §A.4 : "owner_death_policy": "finish_core_then_stop_secondary"
## — instance dédiée (pas _player, déjà exercé/mort ailleurs dans cette
## suite) pour isoler ce scénario. Position loin des autres checks pour
## ne pas partager de zone d'écran VfxBudget avec eux.
func _check_gueule_vide_owner_death_policy() -> void:
	VfxDirector.clear_log()
	var owner_stats := Stats.new()
	var creature: Node2D = GueuleVideScene.instantiate()
	creature.global_position = Vector2(500, 260)
	add_child(creature)
	creature.set_owner_stats(owner_stats)

	# Laisser groundRing/runicStamp (start_tick=0, protégées, A.1) spawner
	# avant de tuer le propriétaire.
	var protected_spawned_before_death: bool = await _wait_until(func(): return VfxDirector.spawn_log.size() >= 2, 10)

	owner_stats.apply_damage(owner_stats.max_hp)  # émet `died`
	var freed_immediately: bool = not is_instance_valid(creature)  # NE DOIT PAS arriver

	# Avancer jusqu'après le start_tick=27 (dégradable, shardBurst) sans
	# qu'elle apparaisse dans le spawn_log — "stop_secondary".
	var shard_burst_spawned: bool = await _wait_until(func():
		for entry in VfxDirector.spawn_log:
			if entry["primitive"] == "shardBurst":
				return true
		return false
	, 35)

	# weakref() plutôt qu'une capture directe de `creature` dans ce 3e
	# lambda : GDScript logge une erreur "Lambda capture ... was freed"
	# quand un Object capturé se libère PENDANT que le même Callable est
	# encore rappelé par _wait_until() sur les frames suivantes — inoffensif
	# (le check reste correct) mais bruyant ; weakref().get_ref() évite le
	# problème proprement, c'est l'idiome Godot prévu pour ce cas.
	var creature_ref: WeakRef = weakref(creature)
	var creature_finished: bool = await _wait_until(func(): return creature_ref.get_ref() == null, GueuleVide.TOTAL_TICKS + 10)

	_checks.append({
		"name": "gueule_vide_owner_death_keeps_creature_alive",
		"pass": protected_spawned_before_death and not freed_immediately,
		"detail": {"protected_spawned_before_death": protected_spawned_before_death, "freed_immediately": freed_immediately},
	})
	_checks.append({
		"name": "gueule_vide_owner_death_cancels_degradable_layer",
		"pass": not shard_burst_spawned,
		"detail": {"shard_burst_spawned": shard_burst_spawned},
	})
	_checks.append({
		"name": "gueule_vide_finishes_normally_despite_owner_death",
		"pass": creature_finished,
		"detail": {"creature_finished": creature_finished},
	})


## J1 (mandat production v1 §4/§6, "La réponse au coup") : root motion sur
## les 3 coups + HitResponse (flash/chiffre de dégâts/décal de mort) —
## vérifie l'intégration réelle, pas juste que le code compile. Player
## reste immobile hors des fenêtres root_motion (déjà couvert
## implicitement par _check_combo_tier_feedback, qui n'aurait pas pu
## viser juste sinon) ; ce check-ci se concentre sur ce que
## _check_combo_tier_feedback ne teste pas : le déplacement RÉEL du
## joueur pendant le coup, et le côté CIBLE (flash/chiffre/décal).
func _check_hit_response() -> void:
	# --- Root motion : le joueur avance réellement pendant coup1 ---
	var pos_before_attack: Vector2 = _player.global_position
	Input.action_press("attack")
	await get_tree().physics_frame
	Input.action_release("attack")
	await _wait_until(func(): return _player._combo_step == 1, 10)
	# Laisse passer la fenêtre root_motion de coup1 (start_tick=6..end_tick=10,
	# data/animation_composer/cendre.json) sans qu'un ennemi n'interfère
	# (aucun dans le rayon ici — seul le déplacement est mesuré).
	for i in range(12):
		await get_tree().physics_frame
	var displacement: float = _player.global_position.x - pos_before_attack.x
	await _wait_until(func(): return _player._combo_step == 0, 30)

	_checks.append({
		"name": "root_motion_displaces_player_forward_during_coup1",
		"pass": displacement > 1.0 and displacement <= 10.5,
		"detail": {"displacement_px": displacement, "expected_max_px": 10.0},
	})

	# --- HitResponse côté cible : flash + chiffre + décal de mort ---
	var enemy := EnemyScene.instantiate()
	enemy.name = "EnemyForHitResponse"
	enemy.global_position = _player.global_position + Vector2(30, 0)
	add_child(enemy)
	await get_tree().physics_frame

	var visual: CanvasItem = enemy.get_node("Placeholder")
	var material_before_hit: Material = visual.material
	enemy.take_damage(10.0, _player.global_position, 4.0, 6)
	var flash_active_right_after_hit: bool = visual.material != null and visual.material is ShaderMaterial

	var number_spawned := false
	for n in HitResponse._number_pool:
		if n.is_active():
			number_spawned = true
			break

	# Le flash se lève tout seul après FLASH_TICKS (2) — un tick de plus
	# par sécurité contre l'ordre autoload/nœud de scène (même prudence
	# que partout ailleurs dans ce fichier, voir CombatFeedback en tête
	# de project.godot).
	for i in range(HitResponse.FLASH_TICKS + 1):
		await get_tree().physics_frame
	var flash_cleared_after_ticks: bool = visual.material == material_before_hit

	var zone_idx: int = VfxBudget.zone_index_for(enemy.global_position)
	var residue_before_death: float = VfxBudget.debug_state()["zones"][zone_idx]["residue"]
	enemy.take_damage(1000.0, _player.global_position, 4.0, 6)  # létal
	await get_tree().physics_frame
	var residue_after_death: float = VfxBudget.debug_state()["zones"][zone_idx]["residue"]

	_checks.append({
		"name": "hit_response_flash_applies_then_clears",
		"pass": flash_active_right_after_hit and flash_cleared_after_ticks,
		"detail": {"flash_active_right_after_hit": flash_active_right_after_hit, "flash_cleared_after_ticks": flash_cleared_after_ticks},
	})
	_checks.append({
		"name": "hit_response_spawns_pooled_damage_number",
		"pass": number_spawned,
		"detail": {"number_spawned": number_spawned},
	})
	_checks.append({
		"name": "hit_response_death_registers_ground_decal_residue",
		"pass": residue_after_death > residue_before_death,
		"detail": {"residue_before_death": residue_before_death, "residue_after_death": residue_after_death},
	})


## J2 (mandat production v1 §4/§6, "Le corps en mouvement") : squash/lean
## du dash (data-driven, migré depuis les constantes codées en dur — voir
## AnimationComposer), punch-zoom CameraDirector sur un impact medium+, et
## lookahead pendant un dash. Vérifie l'intégration réelle : le sprite
## bouge/tourne réellement, la caméra zoome réellement, pas juste que le
## code compile.
func _check_animation_composer_and_camera() -> void:
	# --- squash/lean pendant le dash : le sprite change réellement d'échelle/rotation ---
	var scale_before_dash: Vector2 = _player.get_node("AnimatedSprite2D").scale
	Input.action_press("dash")
	await get_tree().physics_frame
	Input.action_release("dash")
	await _wait_until(func(): return _player._dash_phase != Player.DashPhase.NONE, 5)

	var scale_seen_nonidentity := false
	var rotation_seen_nonzero := false
	var sprite: AnimatedSprite2D = _player.get_node("AnimatedSprite2D")
	for i in range(9):  # couvre la fenêtre squash (tick=4) et lean (0..7)
		await get_tree().physics_frame
		if sprite.scale != Vector2.ONE:
			scale_seen_nonidentity = true
		if not is_equal_approx(sprite.rotation_degrees, 0.0):
			rotation_seen_nonzero = true

	# --- lookahead pendant le dash : offset non nul dans la direction du dash ---
	var lookahead_during_dash: Vector2 = CameraDirector.get_lookahead_offset(_player._dash_direction)

	await _wait_until(func(): return _player._dash_phase == Player.DashPhase.NONE, 15)
	var scale_after_dash: Vector2 = sprite.scale
	var rotation_after_dash: float = sprite.rotation_degrees

	_checks.append({
		"name": "dash_applies_squash_and_lean_then_resets",
		"pass": scale_seen_nonidentity and rotation_seen_nonzero
			and scale_after_dash == Vector2.ONE and is_equal_approx(rotation_after_dash, 0.0),
		"detail": {
			"scale_before_dash": str(scale_before_dash), "scale_seen_nonidentity": scale_seen_nonidentity,
			"rotation_seen_nonzero": rotation_seen_nonzero, "scale_after_dash": str(scale_after_dash),
			"rotation_after_dash": rotation_after_dash,
		},
	})
	_checks.append({
		"name": "camera_lookahead_offset_nonzero_during_dash",
		"pass": lookahead_during_dash.length() > 1.0,
		"detail": {"lookahead_during_dash": str(lookahead_during_dash)},
	})

	# --- punch-zoom : un impact tier2 (medium+ exclu "light") déclenche un zoom qui décroît ---
	var enemy := EnemyScene.instantiate()
	enemy.name = "EnemyForCameraDirector"
	enemy.global_position = _player.global_position + Vector2(30, 0)
	add_child(enemy)
	await get_tree().physics_frame

	Input.action_press("attack")
	await get_tree().physics_frame
	Input.action_release("attack")
	await _wait_until(func(): return _player._combo_step == 1, 10)
	var chain_window_start_cd: int = Player.RECOVERY_TICKS - Player.CHAIN_WINDOW_TICKS
	var chain1_open := func(): return _player._combo_step == 1 and _player._combo_phase == Player.ComboPhase.RECOVERY and _player._combo_tick >= chain_window_start_cd
	await _wait_until(chain1_open, Player.RECOVERY_TICKS + 5)
	Input.action_press("attack")
	await get_tree().physics_frame
	Input.action_release("attack")
	await _wait_until(func(): return _player._combo_step == 2, 10)
	# coup2 = tier2 ("light" hitstop mais recoil_px accru et arcSlash) —
	# PAS medium+, donc PAS de punch. Vérifie l'absence pour ne pas se
	# contenter de "un zoom est apparu à un moment", confirmer le bon
	# déclencheur (coup3 seulement, hitstop "medium").
	var zoom_after_tier2: Vector2 = CameraDirector.get_punch_zoom()

	var chain_window_start_cd2: int = Player.RECOVERY_TICKS - Player.CHAIN_WINDOW_TICKS
	var chain2_open := func(): return _player._combo_step == 2 and _player._combo_phase == Player.ComboPhase.RECOVERY and _player._combo_tick >= chain_window_start_cd2
	await _wait_until(chain2_open, Player.RECOVERY_TICKS + 5)
	var hp_before_tier3: float = enemy.stats.hp
	Input.action_press("attack")
	await get_tree().physics_frame
	Input.action_release("attack")
	await _wait_until(func(): return _player._combo_step == 3, 10)
	await _wait_until(func(): return enemy.stats.hp < hp_before_tier3, Player.COMBO_TIER_ANTICIPATION_TICKS[2] + Player.RELEASE_TICKS + 5)
	var zoom_right_after_tier3: Vector2 = CameraDirector.get_punch_zoom()
	# Phase R4 : hit-stop asymétrique — CameraDirector.get_punch_zoom() ne
	# décroît QUE quand CombatFeedback.is_frozen() (OR des deux pools) est
	# faux ; un coup "medium" gèle la cible (l'ennemi, ici) 4 ticks
	# (TARGET_HITSTOP_MS.medium=65ms), plus long que l'ancien gel symétrique
	# (2 ticks) sur lequel cette marge était calée. Attendre le gel le plus
	# long (4) + la décroissance du punch (PUNCH_ZOOM_TICKS=3) + marge (2).
	for i in range(4 + CameraDirector.PUNCH_ZOOM_TICKS + 2):
		await get_tree().physics_frame
	var zoom_after_decay: Vector2 = CameraDirector.get_punch_zoom()

	_checks.append({
		"name": "camera_punch_zoom_triggers_on_medium_hit_not_light",
		"pass": zoom_after_tier2 == Vector2.ONE and zoom_right_after_tier3 != Vector2.ONE and zoom_after_decay == Vector2.ONE,
		"detail": {
			"zoom_after_tier2": str(zoom_after_tier2), "zoom_right_after_tier3": str(zoom_right_after_tier3),
			"zoom_after_decay": str(zoom_after_decay),
		},
	})

	enemy.queue_free()
	await get_tree().physics_frame


## D (mandat production v1 §1.3, "Dash ET esquive — deux actions séparées")
## : squelette logique de l'esquive — état DODGE, i-frames UNIQUEMENT
## pendant la phase ACTIVE, cooldown. Vérifie l'effet réel des i-frames
## (take_damage() annulé pendant la fenêtre, pas juste is_invincible() qui
## pourrait mentir sans jamais être consultée par un vrai coup), pas
## seulement les transitions d'état.
func _check_dodge() -> void:
	# Phase R4 : le check précédent (_check_camera_punch) termine sur un
	# coup3 (finisher) dont l'anticipation ET la récupération sont
	# désormais allongées (COMBO_TIER_ANTICIPATION_TICKS/
	# COMBO_TIER_RECOVERY_TICKS[2]) — attendre la levée de _action_lock du
	# COMBO qui vient de se terminer, pas juste une marge calée sur
	# DODGE_RECOVERY_TICKS (bien trop courte pour couvrir la RECOVERY du
	# finisher, cause du cascade "anim:'coup3'" observé ici).
	await _wait_until(func(): return not _player._action_lock,
		Player.COMBO_TIER_RECOVERY_TICKS[2] + Player.RELEASE_TICKS + 15)

	# y=900, loin de tous les ennemis des checks précédents (y=180/y=600) —
	# même précaution que _check_dash().
	_player.global_position = Vector2(200, 900)
	_player.velocity = Vector2.ZERO
	_player.facing = Vector2.RIGHT
	var sprite: AnimatedSprite2D = _player.get_node("AnimatedSprite2D")
	var pos_before: Vector2 = _player.global_position
	var invincible_before: bool = _player.is_invincible()

	Input.action_press("dodge")
	await get_tree().physics_frame
	Input.action_release("dodge")
	var started: bool = await _wait_until(func(): return _player._dodge_phase != Player.DodgePhase.NONE, 5)
	var anim_during: String = sprite.animation
	var invincible_during_anticipation: bool = _player.is_invincible()

	var reached_active: bool = await _wait_until(
		func(): return _player._dodge_phase == Player.DodgePhase.ACTIVE, Player.DODGE_ANTICIPATION_TICKS + 3)
	var invincible_during_active: bool = _player.is_invincible()
	var hp_before_hit_during_active: float = _player.stats.hp
	_player.take_damage(10.0, _player.global_position + Vector2(-10, 0))
	var hp_after_hit_during_active: float = _player.stats.hp

	var reached_recovery: bool = await _wait_until(
		func(): return _player._dodge_phase == Player.DodgePhase.RECOVERY, Player.DODGE_ACTIVE_TICKS + 3)
	var invincible_during_recovery: bool = _player.is_invincible()

	var ended: bool = await _wait_until(
		func(): return _player._dodge_phase == Player.DodgePhase.NONE, Player.DODGE_RECOVERY_TICKS + 5)
	var pos_after: Vector2 = _player.global_position
	var action_unlocked_after: bool = not _player._action_lock
	var invincible_after: bool = _player.is_invincible()

	var hp_before_hit_after_end: float = _player.stats.hp
	_player.take_damage(10.0, _player.global_position + Vector2(-10, 0))
	var hp_after_hit_after_end: float = _player.stats.hp

	# Cooldown : un second appui immédiat ne doit RIEN déclencher tant que
	# DODGE_COOLDOWN_TICKS n'est pas écoulé (même discipline que le
	# cooldown de Gueule Vide, _check_gueule_vide()).
	Input.action_press("dodge")
	await get_tree().physics_frame
	Input.action_release("dodge")
	# Tick de battement supplémentaire avant de rendre la main (bug réel
	# trouvé et diagnostiqué par instrumentation ciblée, D tranche 3,
	# docs/worklog.md) : sans lui, l'écho "just pressed" de CETTE pression
	# — bloquée ici à raison (DODGE_COOLDOWN_TICKS encore actif) — reste
	# lisible par Player plus tard que prévu et déclenche une VRAIE
	# seconde esquive dès que son propre cooldown s'épuise (~30 ticks plus
	# tard, chronométré au tick près sur plusieurs runs), pile au moment
	# où _check_bras_faux() presse "power2" : Player consommait alors
	# _action_lock pour cette esquive fantôme, bloquant Bras-Faux en plein
	# départ (started=false) un run sur quatre environ. Un pas
	# supplémentaire ici laisse Player lire ET consommer cet écho
	# immédiatement, dans la fenêtre où le blocage est le comportement
	# attendu, plutôt que de le laisser fuiter vers un check ultérieur.
	await get_tree().physics_frame
	var dodge_started_during_cooldown: bool = _player._dodge_phase != Player.DodgePhase.NONE

	_checks.append({
		"name": "dodge_input_starts_dodge_state",
		"pass": started and not invincible_before,
		"detail": {"started": started, "anim": anim_during, "invincible_before": invincible_before},
	})
	_checks.append({
		"name": "dodge_iframes_only_during_active_phase",
		"pass": not invincible_during_anticipation and reached_active and invincible_during_active
			and reached_recovery and not invincible_during_recovery and not invincible_after,
		"detail": {
			"invincible_during_anticipation": invincible_during_anticipation,
			"invincible_during_active": invincible_during_active,
			"invincible_during_recovery": invincible_during_recovery,
			"invincible_after": invincible_after,
		},
	})
	_checks.append({
		"name": "dodge_iframes_negate_damage_only_during_active",
		"pass": hp_after_hit_during_active == hp_before_hit_during_active
			and hp_after_hit_after_end < hp_before_hit_after_end,
		"detail": {
			"hp_before_hit_during_active": hp_before_hit_during_active, "hp_after_hit_during_active": hp_after_hit_during_active,
			"hp_before_hit_after_end": hp_before_hit_after_end, "hp_after_hit_after_end": hp_after_hit_after_end,
		},
	})
	_checks.append({
		"name": "dodge_displaces_player_then_unlocks",
		"pass": ended and action_unlocked_after
			and pos_after.x > pos_before.x + Player.DODGE_DISTANCE_PX * 0.9
			and pos_after.x < pos_before.x + Player.DODGE_DISTANCE_PX * 1.6,
		"detail": {"pos_before": str(pos_before), "pos_after": str(pos_after), "ended": ended, "action_unlocked_after": action_unlocked_after},
	})
	_checks.append({
		"name": "dodge_cooldown_blocks_immediate_second_dodge",
		"pass": not dodge_started_during_cooldown,
		"detail": {"dodge_started_during_cooldown": dodge_started_during_cooldown},
	})


## D, tranche 2 (mandat production v1 §5, "usine à pouvoirs") : Bras-Faux
## (GDD §7.1), premier pouvoir sur l'archétype de cast "frappe de zone" —
## vérifie précisément ce qui distingue cet archétype du combo/Gueule Vide
## (une seule cible chacun) : PLUSIEURS ennemis touchés en un seul
## balayage si tous dans l'arc, un ennemi hors arc épargné. Place 3
## ennemis autour du joueur (deux dans le cône de 90°, un à 90° pile hors
## cône) plutôt que de faire confiance à Targeting.enemies_in_arc() sur
## la seule foi de son code — le smoke test vérifie l'EFFET réel (PV qui
## bougent), pas l'appel de fonction.
func _check_bras_faux() -> void:
	await _wait_until(func(): return not _player._action_lock, Player.BRAS_FAUX_RECOVERY_TICKS + 5)

	# Amendement GDD Pouvoir/déblocage : Bras-Faux est tier 2 de
	# Monstrification (data/pouvoirs/monstrification.json), palier
	# niveau 3 — sans ce niveau, le slot resterait verrouillé et "power2"
	# ne ferait plus rien.
	RunState.active_power = "monstrification"
	_player.stats.level = 3

	_player.global_position = Vector2(200, 1200)
	_player.velocity = Vector2.ZERO
	_player.facing = Vector2.RIGHT
	var sprite: AnimatedSprite2D = _player.get_node("AnimatedSprite2D")

	var enemy_front := EnemyScene.instantiate()
	enemy_front.name = "BrasFauxFront"
	enemy_front.global_position = _player.global_position + Vector2(30, 0)  # 0° — dans l'arc
	add_child(enemy_front)

	var enemy_side := EnemyScene.instantiate()
	enemy_side.name = "BrasFauxSide"
	var side_dir := Vector2.RIGHT.rotated(deg_to_rad(30.0))
	enemy_side.global_position = _player.global_position + side_dir * 30.0  # 30° — dans l'arc (demi-angle 45°)
	add_child(enemy_side)

	var enemy_outside := EnemyScene.instantiate()
	enemy_outside.name = "BrasFauxOutside"
	var outside_dir := Vector2.RIGHT.rotated(deg_to_rad(90.0))
	enemy_outside.global_position = _player.global_position + outside_dir * 30.0  # 90° — hors arc
	add_child(enemy_outside)

	await get_tree().physics_frame  # laisser le groupe "enemies" se peupler

	var hp_front_before: float = enemy_front.stats.hp
	var hp_side_before: float = enemy_side.stats.hp
	var hp_outside_before: float = enemy_outside.stats.hp

	Input.action_press("power2")
	await get_tree().physics_frame
	Input.action_release("power2")
	var started: bool = await _wait_until(func(): return _player._bras_faux_phase != Player.BrasFauxPhase.NONE, 5)
	var anim_during: String = sprite.animation

	await _wait_until(
		func(): return enemy_front.stats.hp < hp_front_before,
		Player.BRAS_FAUX_ANTICIPATION_TICKS + Player.BRAS_FAUX_RELEASE_TICKS + 5)
	var hp_front_after: float = enemy_front.stats.hp
	var hp_side_after: float = enemy_side.stats.hp
	var hp_outside_after: float = enemy_outside.stats.hp

	var ended: bool = await _wait_until(
		func(): return _player._bras_faux_phase == Player.BrasFauxPhase.NONE, Player.BRAS_FAUX_RECOVERY_TICKS + 5)
	var action_unlocked_after: bool = not _player._action_lock

	# Cooldown : un second appui immédiat ne doit RIEN déclencher (même
	# discipline que dodge/Gueule Vide).
	Input.action_press("power2")
	await get_tree().physics_frame
	Input.action_release("power2")
	var bras_faux_started_during_cooldown: bool = _player._bras_faux_phase != Player.BrasFauxPhase.NONE

	_checks.append({
		"name": "bras_faux_input_starts_state_and_plays_placeholder_anim",
		"pass": started and anim_during == "coup2",
		"detail": {"started": started, "anim": anim_during},
	})
	_checks.append({
		"name": "bras_faux_hits_all_enemies_in_arc_spares_enemy_outside",
		"pass": hp_front_after < hp_front_before and hp_side_after < hp_side_before and hp_outside_after == hp_outside_before,
		"detail": {
			"hp_front_before": hp_front_before, "hp_front_after": hp_front_after,
			"hp_side_before": hp_side_before, "hp_side_after": hp_side_after,
			"hp_outside_before": hp_outside_before, "hp_outside_after": hp_outside_after,
		},
	})
	_checks.append({
		"name": "bras_faux_ends_and_unlocks_then_cooldown_blocks_second_cast",
		"pass": ended and action_unlocked_after and not bras_faux_started_during_cooldown,
		"detail": {
			"ended": ended, "action_unlocked_after": action_unlocked_after,
			"bras_faux_started_during_cooldown": bras_faux_started_during_cooldown,
		},
	})

	enemy_front.queue_free()
	enemy_side.queue_free()
	enemy_outside.queue_free()
	await get_tree().physics_frame


## Phase 3 (MANDAT SUITE v2, RANK_ZERO_POWER_SKILL_BIBLE v0.4) : Poing
## Belluaire (Monstrification §2), même construction que _check_bras_faux()
## ci-dessus mais avec le cône plus étroit (30° de demi-angle, "coup
## frontal" pas un balayage) — l'ennemi latéral est placé à 15° (dans le
## cône) au lieu de 30° pour Bras-Faux.
func _check_poing_belluaire() -> void:
	await _wait_until(func(): return not _player._action_lock, Player.POING_BELLUAIRE_RECOVERY_TICKS + 5)

	# Amendement GDD Pouvoir/déblocage : Poing Belluaire est tier 1 de
	# Monstrification (data/pouvoirs/monstrification.json, palier niveau
	# 1) — déjà atteint par défaut, mais on fixe active_power au cas où
	# ce check tournerait seul (ne pas dépendre de l'ordre d'exécution).
	RunState.active_power = "monstrification"

	_player.global_position = Vector2(200, 1800)
	_player.velocity = Vector2.ZERO
	_player.facing = Vector2.RIGHT
	var sprite: AnimatedSprite2D = _player.get_node("AnimatedSprite2D")

	# Distance 30px (même espacement que Bras-Faux, connu sans chevauchement
	# de collision avec le joueur) et angle latéral resserré à 12° (marge de
	# 18° sous le demi-angle 30°) : à 25px/15° le chevauchement de collision
	# au spawn provoquait un léger recalage de position (move_and_slide()
	# résorbant l'interpénétration dès le 1er tick) qui suffisait à faire
	# sortir la cible latérale du cône — corrigé en donnant de la marge des
	# deux côtés plutôt qu'en coupant au plus juste.
	var enemy_front := EnemyScene.instantiate()
	enemy_front.name = "PoingBelluaireFront"
	enemy_front.global_position = _player.global_position + Vector2(30, 0)  # 0° — dans l'arc
	add_child(enemy_front)

	var enemy_side := EnemyScene.instantiate()
	enemy_side.name = "PoingBelluaireSide"
	var side_dir := Vector2.RIGHT.rotated(deg_to_rad(12.0))
	enemy_side.global_position = _player.global_position + side_dir * 30.0  # 12° — dans l'arc (demi-angle 30°)
	add_child(enemy_side)

	var enemy_outside := EnemyScene.instantiate()
	enemy_outside.name = "PoingBelluaireOutside"
	var outside_dir := Vector2.RIGHT.rotated(deg_to_rad(90.0))
	enemy_outside.global_position = _player.global_position + outside_dir * 30.0  # 90° — hors arc
	add_child(enemy_outside)

	await get_tree().physics_frame

	var hp_front_before: float = enemy_front.stats.hp
	var hp_side_before: float = enemy_side.stats.hp
	var hp_outside_before: float = enemy_outside.stats.hp

	# Poing Belluaire est tier 1 de Monstrification (data/pouvoirs/
	# monstrification.json) : le slot résolu est donc "power1", pas
	# "power3" comme dans l'ancien câblage 1:1 (voir RunState.active_power
	# fixé plus haut).
	Input.action_press("power1")
	await get_tree().physics_frame
	Input.action_release("power1")
	var started: bool = await _wait_until(func(): return _player._poing_belluaire_phase != Player.PoingBelluairePhase.NONE, 5)
	var anim_during: String = sprite.animation

	await _wait_until(
		func(): return enemy_front.stats.hp < hp_front_before,
		Player.POING_BELLUAIRE_ANTICIPATION_TICKS + Player.POING_BELLUAIRE_RELEASE_TICKS + 5)
	var hp_front_after: float = enemy_front.stats.hp
	var hp_side_after: float = enemy_side.stats.hp
	var hp_outside_after: float = enemy_outside.stats.hp

	# Phase R4 : Poing Belluaire s'inflige à lui-même un hit-stop "heavy"
	# (register_hit("heavy", true, ...), _try_hit_poing_belluaire()) — tant
	# que CombatFeedback.is_player_frozen() est vrai, TOUT _physics_process
	# du joueur (dont _advance_poing_belluaire()) est court-circuité (garde
	# en tête de fonction), donc la progression de sa propre RECOVERY est
	# elle-même mise en pause quelques ticks après le coup. Marge élargie
	# (au-delà de +5) pour couvrir ce gel côté attaquant (ATTACKER_HITSTOP_
	# MS.heavy), sans quoi la RECOVERY n'a pas fini dans la fenêtre d'attente.
	var ended: bool = await _wait_until(
		func(): return _player._poing_belluaire_phase == Player.PoingBelluairePhase.NONE, Player.POING_BELLUAIRE_RECOVERY_TICKS + 12)
	var action_unlocked_after: bool = not _player._action_lock

	Input.action_press("power1")
	await get_tree().physics_frame
	Input.action_release("power1")
	var poing_belluaire_started_during_cooldown: bool = _player._poing_belluaire_phase != Player.PoingBelluairePhase.NONE

	_checks.append({
		"name": "poing_belluaire_input_starts_state_and_plays_placeholder_anim",
		"pass": started and anim_during == "coup3",
		"detail": {"started": started, "anim": anim_during},
	})
	_checks.append({
		"name": "poing_belluaire_hits_all_enemies_in_arc_spares_enemy_outside",
		"pass": hp_front_after < hp_front_before and hp_side_after < hp_side_before and hp_outside_after == hp_outside_before,
		"detail": {
			"hp_front_before": hp_front_before, "hp_front_after": hp_front_after,
			"hp_side_before": hp_side_before, "hp_side_after": hp_side_after,
			"hp_outside_before": hp_outside_before, "hp_outside_after": hp_outside_after,
		},
	})
	_checks.append({
		"name": "poing_belluaire_ends_and_unlocks_then_cooldown_blocks_second_cast",
		"pass": ended and action_unlocked_after and not poing_belluaire_started_during_cooldown,
		"detail": {
			"ended": ended, "action_unlocked_after": action_unlocked_after,
			"poing_belluaire_started_during_cooldown": poing_belluaire_started_during_cooldown,
		},
	})

	enemy_front.queue_free()
	enemy_side.queue_free()
	enemy_outside.queue_free()
	await get_tree().physics_frame


## Phase 3 (MANDAT SUITE v2) : Poing Tellurique (Terre §1), même
## construction (demi-angle 40°, ennemi latéral à 25°).
func _check_poing_tellurique() -> void:
	await _wait_until(func(): return not _player._action_lock, Player.POING_TELLURIQUE_RECOVERY_TICKS + 5)

	# Amendement GDD Pouvoir/déblocage : Poing Tellurique est tier 1 de
	# Terre (data/pouvoirs/terre.json, palier niveau 1, déjà atteint par
	# défaut) — sans ce Pouvoir actif, "power4" ne ferait plus rien.
	RunState.active_power = "terre"

	_player.global_position = Vector2(200, 2100)
	_player.velocity = Vector2.ZERO
	_player.facing = Vector2.RIGHT
	var sprite: AnimatedSprite2D = _player.get_node("AnimatedSprite2D")

	# Même correctif de marge que Poing Belluaire ci-dessus (distance 30px,
	# angle latéral resserré sous le demi-angle pour absorber le léger
	# recalage de collision au spawn).
	var enemy_front := EnemyScene.instantiate()
	enemy_front.name = "PoingTelluriqueFront"
	enemy_front.global_position = _player.global_position + Vector2(30, 0)  # 0° — dans l'arc
	add_child(enemy_front)

	var enemy_side := EnemyScene.instantiate()
	enemy_side.name = "PoingTelluriqueSide"
	var side_dir := Vector2.RIGHT.rotated(deg_to_rad(18.0))
	enemy_side.global_position = _player.global_position + side_dir * 30.0  # 18° — dans l'arc (demi-angle 40°)
	add_child(enemy_side)

	var enemy_outside := EnemyScene.instantiate()
	enemy_outside.name = "PoingTelluriqueOutside"
	var outside_dir := Vector2.RIGHT.rotated(deg_to_rad(90.0))
	enemy_outside.global_position = _player.global_position + outside_dir * 30.0  # 90° — hors arc
	add_child(enemy_outside)

	await get_tree().physics_frame

	var hp_front_before: float = enemy_front.stats.hp
	var hp_side_before: float = enemy_side.stats.hp
	var hp_outside_before: float = enemy_outside.stats.hp

	# Poing Tellurique est tier 1 de Terre (data/pouvoirs/terre.json) : le
	# slot résolu est donc "power1", pas "power4" comme dans l'ancien
	# câblage 1:1 (voir RunState.active_power fixé plus haut).
	Input.action_press("power1")
	await get_tree().physics_frame
	Input.action_release("power1")
	var started: bool = await _wait_until(func(): return _player._poing_tellurique_phase != Player.PoingTelluriquePhase.NONE, 5)
	var anim_during: String = sprite.animation

	await _wait_until(
		func(): return enemy_front.stats.hp < hp_front_before,
		Player.POING_TELLURIQUE_ANTICIPATION_TICKS + Player.POING_TELLURIQUE_RELEASE_TICKS + 5)
	var hp_front_after: float = enemy_front.stats.hp
	var hp_side_after: float = enemy_side.stats.hp
	var hp_outside_after: float = enemy_outside.stats.hp

	var ended: bool = await _wait_until(
		func(): return _player._poing_tellurique_phase == Player.PoingTelluriquePhase.NONE, Player.POING_TELLURIQUE_RECOVERY_TICKS + 5)
	var action_unlocked_after: bool = not _player._action_lock

	Input.action_press("power1")
	await get_tree().physics_frame
	Input.action_release("power1")
	var poing_tellurique_started_during_cooldown: bool = _player._poing_tellurique_phase != Player.PoingTelluriquePhase.NONE

	_checks.append({
		"name": "poing_tellurique_input_starts_state_and_plays_placeholder_anim",
		"pass": started and anim_during == "coup1",
		"detail": {"started": started, "anim": anim_during},
	})
	_checks.append({
		"name": "poing_tellurique_hits_all_enemies_in_arc_spares_enemy_outside",
		"pass": hp_front_after < hp_front_before and hp_side_after < hp_side_before and hp_outside_after == hp_outside_before,
		"detail": {
			"hp_front_before": hp_front_before, "hp_front_after": hp_front_after,
			"hp_side_before": hp_side_before, "hp_side_after": hp_side_after,
			"hp_outside_before": hp_outside_before, "hp_outside_after": hp_outside_after,
		},
	})
	_checks.append({
		"name": "poing_tellurique_ends_and_unlocks_then_cooldown_blocks_second_cast",
		"pass": ended and action_unlocked_after and not poing_tellurique_started_during_cooldown,
		"detail": {
			"ended": ended, "action_unlocked_after": action_unlocked_after,
			"poing_tellurique_started_during_cooldown": poing_tellurique_started_during_cooldown,
		},
	})

	enemy_front.queue_free()
	enemy_side.queue_free()
	enemy_outside.queue_free()
	await get_tree().physics_frame


## Amendement GDD Pouvoir/déblocage (confirmé par Milan, docs/worklog.md) :
## vérifie le cœur du nouveau mécanisme, pas seulement que les 4
## compétences déjà vivantes n'ont pas régressé. Trois angles : (1) un
## slot débloqué+implémenté est bien exposé (Poing Belluaire, tier 1 de
## Monstrification, palier niveau 1), (2) un slot implémenté mais PAS
## encore débloqué par le niveau reste absent (Bras-Faux, tier 2, palier
## niveau 3, testé à niveau 1), et redevient présent une fois le palier
## atteint, (3) un appui sur ce même slot pendant qu'il est verrouillé
## ne déclenche RIEN côté gameplay (pas juste "le bouton n'existe pas" :
## l'input lui-même doit être un no-op).
func _check_power_slot_gating() -> void:
	await _wait_until(func(): return not _player._action_lock, 60)
	RunState.active_power = "monstrification"
	_player.stats.level = 1

	var slot1_at_level1: Dictionary = _player.get_power_slot_info(1)
	var slot2_at_level1: Dictionary = _player.get_power_slot_info(2)

	# Appui sur le slot verrouillé (Bras-Faux, "power2") : ne doit rien
	# démarrer — même garde que le reste de l'input, pas un bouton absent
	# qui laisserait pourtant l'action passer si pressée au clavier.
	Input.action_press("power2")
	await get_tree().physics_frame
	Input.action_release("power2")
	var bras_faux_started_while_locked: bool = _player._bras_faux_phase != Player.BrasFauxPhase.NONE

	# Capturé AVANT de relever le niveau ci-dessous : au niveau 1 ce slot
	# est encore vide, c'est justement ce que ce ratio doit refléter (0.0,
	# jamais le vrai cooldown de Bras-Faux une fois débloqué).
	var slot2_cooldown_ratio_when_empty: float = _player.get_power_slot_cooldown_ratio(2)

	_player.stats.level = 3
	var slot2_at_level3: Dictionary = _player.get_power_slot_info(2)

	_checks.append({
		"name": "power_slot_unlocked_and_implemented_is_exposed",
		"pass": not slot1_at_level1.is_empty() and slot1_at_level1.get("id", "") == "poing_belluaire",
		"detail": {"slot1_at_level1": slot1_at_level1},
	})
	_checks.append({
		"name": "power_slot_below_unlock_level_stays_absent",
		"pass": slot2_at_level1.is_empty(),
		"detail": {"slot2_at_level1": slot2_at_level1},
	})
	_checks.append({
		"name": "power_slot_becomes_present_once_level_reached",
		"pass": not slot2_at_level3.is_empty() and slot2_at_level3.get("id", "") == "bras_faux",
		"detail": {"slot2_at_level3": slot2_at_level3},
	})
	_checks.append({
		"name": "locked_power_slot_input_is_a_no_op",
		"pass": not bras_faux_started_while_locked,
		"detail": {"bras_faux_started_while_locked": bras_faux_started_while_locked},
	})
	_checks.append({
		"name": "empty_power_slot_cooldown_ratio_is_zero",
		"pass": is_equal_approx(slot2_cooldown_ratio_when_empty, 0.0),
		"detail": {"slot2_cooldown_ratio_when_empty": slot2_cooldown_ratio_when_empty},
	})


## G (GDD §10) : le recul du joueur sous un coup ennemi manquait jusqu'ici
## (voir Player.take_damage()) — vérifie sa propre timeline (_hurt_phase),
## symétrique du recul déjà testé côté Enemy depuis Phase 1.2.
func _check_player_recoils_on_taking_damage() -> void:
	await _wait_until(func(): return not _player._action_lock, 60)
	_player.global_position = Vector2(200, 1500)
	_player.velocity = Vector2.ZERO
	_player.stats.hp = 100.0

	var pos_before: Vector2 = _player.global_position
	_player.take_damage(10.0, pos_before + Vector2(-40, 0), 30.0, 8)
	await get_tree().physics_frame
	var pos_next_tick: Vector2 = _player.global_position

	var ended: bool = await _wait_until(func(): return _player._hurt_phase == Player.HurtPhase.NONE, 20)
	var pos_after: Vector2 = _player.global_position
	var action_unlocked_after: bool = not _player._action_lock

	_checks.append({
		"name": "player_recoils_away_from_attacker_on_taking_damage",
		"pass": pos_next_tick.x > pos_before.x and ended and action_unlocked_after and pos_after.x > pos_before.x,
		"detail": {
			"pos_before": str(pos_before), "pos_next_tick": str(pos_next_tick),
			"pos_after": str(pos_after), "ended": ended, "action_unlocked_after": action_unlocked_after,
		},
	})


## G (GDD §10/§21, "Crawler : petit, rapide, harcèlement") : vérifie le
## comportement de bout en bout (détection -> approche -> contact ->
## dégâts + recul du joueur), pas juste l'appel de fonction — posé hors
## de son rayon de contact mais dans son rayon d'aggro pour forcer une
## vraie approche avant le premier coup.
func _check_crawler_chases_and_hits_player() -> void:
	await _wait_until(func(): return not _player._action_lock, 60)
	_player.global_position = Vector2(200, 1700)
	_player.velocity = Vector2.ZERO
	_player.stats.hp = 100.0

	var crawler := EnemyCrawlerScene.instantiate()
	crawler.name = "CrawlerChase"
	crawler.global_position = _player.global_position + Vector2(120, 0)
	add_child(crawler)
	await get_tree().physics_frame

	var dist_before: float = crawler.global_position.distance_to(_player.global_position)
	var hp_before: float = _player.stats.hp

	var hit: bool = await _wait_until(func(): return _player.stats.hp < hp_before, 300)
	var hp_after: float = _player.stats.hp

	_checks.append({
		"name": "crawler_chases_then_hits_player",
		"pass": hit and dist_before > crawler.attack_range_px and hp_after < hp_before,
		"detail": {"dist_before": dist_before, "attack_range_px": crawler.attack_range_px, "hp_before": hp_before, "hp_after": hp_after, "hit": hit},
	})
	crawler.queue_free()
	await get_tree().physics_frame


## G (GDD §10, "Brute : lent, lourd, grosses attaques télégraphiées") :
## posé DÉJÀ à portée de contact (isole le timing du télégraphe de
## l'approche, déjà couverte par le check Crawler ci-dessus) — aucun
## dégât ne doit tomber avant la fin de `telegraph_ticks`, et le coup qui
## suit doit être le contact_damage exact de Brute (nettement plus lourd
## que Crawler, cohérent avec "grosses attaques").
func _check_brute_telegraphs_before_hitting() -> void:
	await _wait_until(func(): return not _player._action_lock, 60)
	_player.global_position = Vector2(200, 1900)
	_player.velocity = Vector2.ZERO
	_player.stats.hp = 100.0

	var brute := EnemyBruteScene.instantiate()
	brute.name = "BruteTelegraph"
	brute.global_position = _player.global_position + Vector2(40, 0)  # déjà dans attack_range_px (52)
	add_child(brute)
	await get_tree().physics_frame

	var reached_telegraph: bool = await _wait_until(func(): return brute._state == Enemy.State.TELEGRAPH, 20)
	var hp_before: float = _player.stats.hp

	for i in range(brute.telegraph_ticks - 2):
		await get_tree().physics_frame
	var hp_still_telegraphing: float = _player.stats.hp

	var hit: bool = await _wait_until(func(): return _player.stats.hp < hp_before, 20)
	var hp_after: float = _player.stats.hp

	_checks.append({
		"name": "brute_telegraphs_before_landing_a_heavier_hit",
		"pass": reached_telegraph and hp_still_telegraphing == hp_before and hit and is_equal_approx(hp_before - hp_after, brute.contact_damage),
		"detail": {
			"reached_telegraph": reached_telegraph, "hp_before": hp_before,
			"hp_still_telegraphing": hp_still_telegraphing, "hp_after": hp_after,
			"contact_damage": brute.contact_damage,
		},
	})
	brute.queue_free()
	await get_tree().physics_frame


## G (GDD §10, "Ranged : pression à distance") : posé trop proche de sa
## `preferred_range_px` -> doit d'abord reculer (kiting) plutôt que foncer
## au contact comme un ennemi de mêlée, puis toucher le joueur par
## projectile SANS jamais entrer dans sa propre portée de contact
## (attack_range_px, héritée mais inutilisée par RANGED — sert ici de
## seuil de preuve "ce n'était pas un contact").
func _check_ranged_keeps_distance_and_fires_projectile() -> void:
	await _wait_until(func(): return not _player._action_lock, 60)
	_player.global_position = Vector2(200, 2100)
	_player.velocity = Vector2.ZERO
	_player.stats.hp = 100.0

	var ranged := EnemyRangedScene.instantiate()
	ranged.name = "RangedKite"
	ranged.global_position = _player.global_position + Vector2(60, 0)  # < preferred_range_px - range_tolerance_px
	add_child(ranged)
	await get_tree().physics_frame

	var dist_start: float = ranged.global_position.distance_to(_player.global_position)
	for i in range(20):
		await get_tree().physics_frame
	var dist_after_kite: float = ranged.global_position.distance_to(_player.global_position)

	var hp_before: float = _player.stats.hp
	var hit: bool = await _wait_until(func(): return _player.stats.hp < hp_before, 240)
	var hp_after: float = _player.stats.hp
	var dist_when_hit: float = ranged.global_position.distance_to(_player.global_position)

	_checks.append({
		"name": "ranged_retreats_to_preferred_range_then_hits_player_with_projectile",
		"pass": dist_after_kite > dist_start and hit and hp_after < hp_before and dist_when_hit > ranged.attack_range_px,
		"detail": {
			"dist_start": dist_start, "dist_after_kite": dist_after_kite,
			"hp_before": hp_before, "hp_after": hp_after, "dist_when_hit": dist_when_hit, "hit": hit,
		},
	})
	ranged.queue_free()
	await get_tree().physics_frame


## H1 (GDD §17/§20/§21 : "XP, niveau") : logique pure sur Stats, sans
## scène — même esprit que les checks les plus simples de ce fichier.
func _check_stats_add_xp_levels_up() -> void:
	var s := Stats.new()
	var level_ups: Array = []
	s.leveled_up.connect(func(new_level: int): level_ups.append(new_level))

	s.add_xp(50.0)  # exactement xp_to_next_level() au niveau 1 -> une montée
	var level_after_first: int = s.level
	var xp_after_first: float = s.xp
	var max_hp_after_first: float = s.max_hp

	s.add_xp(125.0)  # >= xp_to_next_level() au niveau 2 (100) -> une 2e montée EN BOUCLE, reste 25 d'XP
	var level_after_second: int = s.level
	var xp_after_second: float = s.xp
	var max_hp_after_second: float = s.max_hp
	var int_after_second: float = s.int_stat

	_checks.append({
		"name": "stats_add_xp_levels_up_in_a_loop_and_carries_remainder",
		"pass": level_after_first == 2 and is_equal_approx(xp_after_first, 0.0) and is_equal_approx(max_hp_after_first, 110.0)
			and level_after_second == 3 and is_equal_approx(xp_after_second, 25.0)
			and is_equal_approx(max_hp_after_second, 120.0) and is_equal_approx(int_after_second, 12.0)
			and level_ups == [2, 3],
		"detail": {
			"level_after_first": level_after_first, "xp_after_first": xp_after_first, "max_hp_after_first": max_hp_after_first,
			"level_after_second": level_after_second, "xp_after_second": xp_after_second,
			"max_hp_after_second": max_hp_after_second, "int_after_second": int_after_second,
			"level_ups": level_ups,
		},
	})


## H1 (GDD §20 : "combats -> XP/loot/maîtrise") : la mort d'un ennemi
## doit créditer le joueur, pas juste disparaître.
func _check_enemy_death_awards_xp_to_player() -> void:
	await _wait_until(func(): return not _player._action_lock, 60)
	_player.global_position = Vector2(200, 2300)
	_player.stats.level = 1
	_player.stats.xp = 0.0
	var xp_before: float = _player.stats.xp

	var crawler := EnemyCrawlerScene.instantiate()
	crawler.name = "CrawlerXpReward"
	crawler.global_position = _player.global_position + Vector2(500, 0)  # loin, hors aggro -> pas d'IA parasite
	add_child(crawler)
	await get_tree().physics_frame

	var reward: float = crawler.xp_reward
	crawler.take_damage(9999.0, crawler.global_position + Vector2(-10, 0))
	var xp_after: float = _player.stats.xp
	await get_tree().physics_frame

	_checks.append({
		"name": "enemy_death_awards_xp_to_player",
		"pass": is_equal_approx(xp_after - xp_before, reward),
		"detail": {"xp_before": xp_before, "xp_after": xp_after, "xp_reward": reward},
	})


## H2 (GDD §15 : "morsure, charge, projection, frappe au sol") — le boss
## doit montrer les 4 attaques de sa rotation DANS L'ORDRE, chacune avec
## ses propres dégâts, pas juste "un ennemi qui touche". Le joueur reste
## immobile et proche : le recul entre deux coups (jusqu'à 70px pour
## Projection) ne casse pas le test — le boss retourne en CHASE entre
## deux attaques et referme la distance avant la suivante, tant que ça
## reste dans son rayon d'aggro (320px, large marge).
func _check_boss_attack_rotation_hits_player_with_all_four_attacks() -> void:
	await _wait_until(func(): return not _player._action_lock, 60)
	_player.global_position = Vector2(2800, 200)
	_player.velocity = Vector2.ZERO
	_player.stats.hp = 200.0
	_player.stats.max_hp = 200.0

	var boss := BossGateMawScene.instantiate()
	boss.name = "BossRotationCheck"
	boss.global_position = _player.global_position + Vector2(45, 0)
	add_child(boss)
	await get_tree().physics_frame

	var deltas: Array = []
	var hp_before: float = _player.stats.hp
	for i in range(4):
		var hit: bool = await _wait_until(func(): return _player.stats.hp < hp_before, 400)
		var hp_after: float = _player.stats.hp
		deltas.append(hp_before - hp_after if hit else -1.0)
		hp_before = hp_after

	_checks.append({
		"name": "boss_attack_rotation_hits_player_with_all_four_attacks_in_order",
		"pass": is_equal_approx(deltas[0], boss.bite_damage) and is_equal_approx(deltas[1], boss.charge_damage)
			and is_equal_approx(deltas[2], boss.slam_damage) and is_equal_approx(deltas[3], boss.projection_damage),
		"detail": {
			"deltas": deltas,
			"expected": [boss.bite_damage, boss.charge_damage, boss.slam_damage, boss.projection_damage],
		},
	})
	boss.queue_free()
	await get_tree().physics_frame


## G/H2 : Frappe au sol se déclenche dans une fenêtre large (×1.5 du
## rayon réel) mais ne touche QUE si le joueur est encore dans le rayon
## exact au moment de l'impact — vérifie les deux cas séparément
## (`_attack_index` forcé sur SLAM, même discipline que les tests G qui
## lisent/écrivent directement l'état interne plutôt que de ré-implémenter
## une recherche).
func _check_boss_slam_spares_player_outside_radius_but_hits_inside() -> void:
	await _wait_until(func(): return not _player._action_lock, 60)

	_player.global_position = Vector2(2800, 600)
	_player.velocity = Vector2.ZERO
	_player.stats.hp = 200.0
	_player.stats.max_hp = 200.0
	var boss_outside := BossGateMawScene.instantiate()
	boss_outside.name = "BossSlamOutside"
	boss_outside.global_position = _player.global_position + Vector2(120, 0)  # < slam_radius_px*1.5 (150, déclenche) mais > slam_radius_px (100, épargné)
	boss_outside._attack_index = 2  # Attack.SLAM
	add_child(boss_outside)
	await get_tree().physics_frame
	var hp_before_outside: float = _player.stats.hp
	for i in range(boss_outside.slam_telegraph_ticks + 5):
		await get_tree().physics_frame
	var hp_after_outside: float = _player.stats.hp
	boss_outside.queue_free()
	await get_tree().physics_frame

	_player.global_position = Vector2(2800, 800)
	_player.velocity = Vector2.ZERO
	_player.stats.hp = 200.0
	var boss_inside := BossGateMawScene.instantiate()
	boss_inside.name = "BossSlamInside"
	boss_inside.global_position = _player.global_position + Vector2(50, 0)  # < slam_radius_px -> touche
	boss_inside._attack_index = 2
	add_child(boss_inside)
	await get_tree().physics_frame
	var hp_before_inside: float = _player.stats.hp
	var hit_inside: bool = await _wait_until(func(): return _player.stats.hp < hp_before_inside, boss_inside.slam_telegraph_ticks + 10)
	var hp_after_inside: float = _player.stats.hp
	var boss_inside_slam_damage: float = boss_inside.slam_damage
	boss_inside.queue_free()
	await get_tree().physics_frame

	_checks.append({
		"name": "boss_slam_spares_player_outside_radius_but_hits_inside",
		"pass": is_equal_approx(hp_after_outside, hp_before_outside) and hit_inside
			and is_equal_approx(hp_before_inside - hp_after_inside, boss_inside_slam_damage),
		"detail": {
			"hp_before_outside": hp_before_outside, "hp_after_outside": hp_after_outside,
			"hp_before_inside": hp_before_inside, "hp_after_inside": hp_after_inside, "hit_inside": hit_inside,
		},
	})


## H2 (GDD §15 : "phase énervée") : bascule une fois au seuil de PV,
## resserre le cooldown — pas juste un flag qui ne change rien.
func _check_boss_enrages_at_hp_threshold() -> void:
	var boss := BossGateMawScene.instantiate()
	boss.name = "BossEnrageCheck"
	boss.global_position = Vector2(2800, 1000)
	add_child(boss)
	await get_tree().physics_frame

	var enraged_before: bool = boss._enraged
	var threshold_hp: float = boss.stats.max_hp * boss.enrage_hp_ratio
	boss.take_damage(boss.stats.max_hp - threshold_hp + 1.0, boss.global_position + Vector2(-10, 0))
	# take_damage() pose SON PROPRE recul (_recoil_tick/_recoil_total_ticks,
	# Phase R4 courbe ease-out — défaut 6 ticks) — _check_enrage() est
	# gardée derrière le early-return recul de _physics_process() (comme
	# tout le reste de l'IA), donc un seul physics_frame ne suffit pas : il
	# faut attendre la fin du recul avant que la vérification ait seulement
	# une chance de tourner.
	await _wait_until(func(): return boss._recoil_tick >= boss._recoil_total_ticks, 20)
	await get_tree().physics_frame

	var enraged_after: bool = boss._enraged
	var cooldown_after: int = boss._current_cooldown_ticks()

	_checks.append({
		"name": "boss_enrages_at_hp_threshold_and_shortens_cooldown",
		"pass": not enraged_before and enraged_after and cooldown_after == boss.enrage_cooldown_ticks,
		"detail": {
			"enraged_before": enraged_before, "enraged_after": enraged_after,
			"cooldown_after": cooldown_after, "expected_cooldown": boss.enrage_cooldown_ticks,
		},
	})
	boss.queue_free()
	await get_tree().physics_frame


## H1/H2 : récompense de fin de Gate nettement au-dessus d'un ennemi
## normal (G) — niveau du joueur forcé haut AVANT la mort pour que la
## grosse récompense (120 XP) ne déclenche pas de montée de niveau qui
## consommerait le delta d'XP brut (même piège que la boucle de niveaux,
## vérifié séparément par stats_add_xp_levels_up_in_a_loop_...).
func _check_boss_death_awards_xp_reward() -> void:
	await _wait_until(func(): return not _player._action_lock, 60)
	_player.global_position = Vector2(2800, 1200)
	_player.stats.level = 10
	_player.stats.xp = 0.0
	var xp_before: float = _player.stats.xp

	var boss := BossGateMawScene.instantiate()
	boss.name = "BossXpReward"
	boss.global_position = _player.global_position + Vector2(500, 0)
	add_child(boss)
	await get_tree().physics_frame

	var reward: float = boss.xp_reward
	boss.take_damage(99999.0, boss.global_position + Vector2(-10, 0))
	var xp_after: float = _player.stats.xp
	await get_tree().physics_frame

	_checks.append({
		"name": "boss_death_awards_xp_reward_to_player",
		"pass": is_equal_approx(xp_after - xp_before, reward) and reward > 50.0,
		"detail": {"xp_before": xp_before, "xp_after": xp_after, "xp_reward": reward},
	})


## H3 (GDD §11 : "Entrée → combats → ... → embranchement → Elite →
## repos → boss → ..."). GateRoom.gd n'a pas de scène packagée dédiée —
## construit à la main (Enemies/Door en enfants AVANT d'entrer dans
## l'arbre, pour que _ready() les voie déjà) plutôt que d'ajouter un
## .tscn jetable pour une seule structure de 3 nœuds.
func _check_gate_room_locks_until_cleared() -> void:
	var room := Node2D.new()
	room.name = "GateRoomCheck"
	room.set_script(load("res://src/world/gate_room.gd"))

	var enemies_node := Node2D.new()
	enemies_node.name = "Enemies"
	var crawler := EnemyCrawlerScene.instantiate()
	crawler.global_position = Vector2(2800, 2500)
	enemies_node.add_child(crawler)
	room.add_child(enemies_node)

	var door := Node2D.new()
	door.name = "Door"
	room.add_child(door)

	room.requires_clear = true
	add_child(room)
	await get_tree().physics_frame

	var cleared_before: bool = room.is_cleared()
	var door_present_before: bool = room.has_node("Door")

	crawler.take_damage(9999.0, crawler.global_position + Vector2(-10, 0))
	await get_tree().physics_frame

	var cleared_after: bool = room.is_cleared()
	var door_present_after: bool = room.has_node("Door")

	_checks.append({
		"name": "gate_room_locks_door_until_enemies_cleared_then_opens",
		"pass": not cleared_before and door_present_before and cleared_after and not door_present_after,
		"detail": {
			"cleared_before": cleared_before, "door_present_before": door_present_before,
			"cleared_after": cleared_after, "door_present_after": door_present_after,
		},
	})
	room.queue_free()
	await get_tree().physics_frame


## H3 (GDD §11 : "loot/événement"/"récompense").
func _check_xp_pickup_grants_xp_and_frees_itself() -> void:
	await _wait_until(func(): return not _player._action_lock, 60)
	_player.global_position = Vector2(200, 2700)
	_player.stats.level = 10
	_player.stats.xp = 0.0

	var pickup := Area2D.new()
	pickup.name = "XpPickupCheck"
	pickup.set_script(load("res://src/world/xp_pickup.gd"))
	pickup.xp_amount = 25.0
	var shape := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = Vector2(40, 40)
	shape.shape = rect
	pickup.add_child(shape)
	pickup.global_position = _player.global_position
	add_child(pickup)

	var xp_before: float = _player.stats.xp
	# queue_free() est différé (fin de frame), pas instantané : sonder
	# jusqu'à ce qu'il ait vraiment eu lieu plutôt que fixer un nombre de
	# frames arbitraire, même discipline que _wait_until partout ailleurs.
	await _wait_until(func(): return not is_instance_valid(pickup), 20)
	var xp_after: float = _player.stats.xp
	var pickup_freed: bool = not is_instance_valid(pickup)

	_checks.append({
		"name": "xp_pickup_grants_xp_and_frees_itself_on_player_contact",
		"pass": is_equal_approx(xp_after - xp_before, 25.0) and pickup_freed,
		"detail": {"xp_before": xp_before, "xp_after": xp_after, "pickup_freed": pickup_freed},
	})


## H3 (GDD §11 : salle "repos" — interprétation documentée dans
## HealZone.gd).
func _check_heal_zone_heals_player_to_full() -> void:
	await _wait_until(func(): return not _player._action_lock, 60)
	_player.global_position = Vector2(200, 2900)
	_player.stats.hp = 10.0
	_player.stats.max_hp = 100.0

	var zone := Area2D.new()
	zone.name = "HealZoneCheck"
	zone.set_script(load("res://src/world/heal_zone.gd"))
	var shape := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = Vector2(60, 60)
	shape.shape = rect
	zone.add_child(shape)
	zone.global_position = _player.global_position
	add_child(zone)

	var hp_before: float = _player.stats.hp
	await get_tree().physics_frame
	await get_tree().physics_frame
	var hp_after: float = _player.stats.hp

	_checks.append({
		"name": "heal_zone_heals_player_to_full_on_contact",
		"pass": is_equal_approx(hp_before, 10.0) and is_equal_approx(hp_after, 100.0),
		"detail": {"hp_before": hp_before, "hp_after": hp_after},
	})
	zone.queue_free()
	await get_tree().physics_frame


## H3 (GDD §11/§20 : "sortie" -> signal câblable par H4, voir GateExit.gd).
func _check_gate_exit_emits_signal_on_player_contact() -> void:
	await _wait_until(func(): return not _player._action_lock, 60)
	_player.global_position = Vector2(200, 3100)

	var exit_marker := Area2D.new()
	exit_marker.name = "GateExitCheck"
	exit_marker.set_script(load("res://src/world/gate_exit.gd"))
	var shape := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = Vector2(40, 40)
	shape.shape = rect
	exit_marker.add_child(shape)
	exit_marker.global_position = _player.global_position
	add_child(exit_marker)

	var completed: Array = []
	exit_marker.gate_completed.connect(func(): completed.append(true))

	await get_tree().physics_frame
	await get_tree().physics_frame

	_checks.append({
		"name": "gate_exit_emits_gate_completed_on_player_contact",
		"pass": completed.size() == 1,
		"detail": {"completed_count": completed.size()},
	})
	exit_marker.queue_free()
	await get_tree().physics_frame


## H4 (mandat §6, GDD §20 : progression persiste Hub<->Gate). Deux instances
## Player distinctes doivent partager le MÊME Resource Stats via l'autoload
## RunState — pas une resynchronisation manuelle, l'identité de l'objet
## (voir run_state.gd, Player._ready()).
func _check_run_state_persists_player_stats_across_new_player_instances() -> void:
	var player_a: Player = PlayerScene.instantiate()
	player_a.global_position = Vector2(200, 3300)
	add_child(player_a)
	await get_tree().physics_frame

	var player_b: Player = PlayerScene.instantiate()
	player_b.global_position = Vector2(260, 3300)
	add_child(player_b)
	await get_tree().physics_frame

	var same_stats_object: bool = (
		player_a.stats == RunState.player_stats and player_b.stats == RunState.player_stats
	)

	player_a.stats.hp = 42.0
	var propagates_to_b: bool = is_equal_approx(player_b.stats.hp, 42.0)

	_checks.append({
		"name": "run_state_persists_player_stats_across_new_player_instances",
		"pass": same_stats_object and propagates_to_b,
		"detail": {
			"same_stats_object": same_stats_object, "propagates_to_b": propagates_to_b,
			"hp_a": player_a.stats.hp, "hp_b": player_b.stats.hp,
		},
	})
	player_a.queue_free()
	player_b.queue_free()
	await get_tree().physics_frame


## H4 — testable sans jamais appeler `_on_body_entered()` réel (qui
## invoquerait `get_tree().change_scene_to_file()`, destructeur pour l'arbre
## de scène du test lui-même). `_should_trigger()` est la partie pure,
## séparée exprès pour ça (voir gate_entrance.gd).
func _check_gate_entrance_detects_player_once_and_targets_the_gate_scene() -> void:
	var entrance := Area2D.new()
	entrance.name = "GateEntranceCheck"
	entrance.set_script(load("res://src/world/gate_entrance.gd"))
	add_child(entrance)

	var target_matches: bool = entrance.target_gate_scene == "res://scenes/gameplay/gate_premiere.tscn"
	var triggers_on_player: bool = entrance._should_trigger(_player)

	entrance._triggered = true
	var ignores_after_triggered: bool = not entrance._should_trigger(_player)

	var non_player := Node2D.new()
	add_child(non_player)
	entrance._triggered = false
	var ignores_non_player: bool = not entrance._should_trigger(non_player)

	_checks.append({
		"name": "gate_entrance_detects_player_once_and_targets_the_gate_scene",
		"pass": target_matches and triggers_on_player and ignores_after_triggered and ignores_non_player,
		"detail": {
			"target_matches": target_matches, "triggers_on_player": triggers_on_player,
			"ignores_after_triggered": ignores_after_triggered, "ignores_non_player": ignores_non_player,
		},
	})
	non_player.queue_free()
	entrance.queue_free()
	await get_tree().physics_frame


## H4 — vérifie le câblage GateExit->Outpost sans charger toute la scène
## gate_premiere.tscn (lourd : ennemis, boss, VFX...) ni déclencher un vrai
## change_scene_to_file() : un mock allégé avec juste un enfant "Exit"
## portant gate_exit.gd, sous le script gate_premiere.gd — Godot appelle
## _ready() (donc le .connect()) dès l'ajout à l'arbre.
func _check_gate_premiere_wires_exit_signal_to_a_handler() -> void:
	var mock := Node2D.new()
	mock.name = "GatePremiereCheck"
	mock.set_script(load("res://src/world/gate_premiere.gd"))

	var exit_marker := Area2D.new()
	exit_marker.name = "Exit"
	exit_marker.set_script(load("res://src/world/gate_exit.gd"))
	mock.add_child(exit_marker)

	add_child(mock)
	await get_tree().physics_frame

	var connections: Array = exit_marker.gate_completed.get_connections()
	var wired: bool = connections.size() >= 1

	_checks.append({
		"name": "gate_premiere_wires_exit_signal_to_a_handler",
		"pass": wired,
		"detail": {"connection_count": connections.size()},
	})
	mock.queue_free()
	await get_tree().physics_frame


## H5 (GDD §17 : "Écran personnage : NAME/RANK/LEVEL/FOR/AGI/INT/VIT/
## CLASS/SKILLS/EQUIPMENT... afficher CLASS = NONE"). L'écran lit
## Input.is_action_just_pressed() dans son propre _process() (pas
## _physics_process, voir character_screen.gd) — d'où `await
## process_frame` ici, pas `physics_frame` comme le reste du fichier.
func _check_character_screen_toggles_open_closed_and_shows_class_none() -> void:
	var screen: CharacterScreen = load("res://scenes/ui/character_screen.tscn").instantiate()
	add_child(screen)
	await get_tree().process_frame

	var closed_before: bool = not screen.is_open()

	Input.action_press("character_screen")
	await get_tree().process_frame
	Input.action_release("character_screen")
	var open_after_press: bool = screen.is_open()
	await get_tree().process_frame  # laisse _process() peupler les labels depuis _player

	var stats_text: String = screen.get_node("Panel/StatsLabel").text
	var shows_class_none: bool = stats_text.contains("CLASSE : AUCUNE")
	var shows_name: bool = stats_text.contains("Rank Zero")

	Input.action_press("character_screen")
	await get_tree().process_frame
	Input.action_release("character_screen")
	var closed_after_second_press: bool = not screen.is_open()

	_checks.append({
		"name": "character_screen_toggles_open_closed_and_shows_class_none",
		"pass": (
			closed_before and open_after_press and shows_class_none and shows_name
			and closed_after_second_press
		),
		"detail": {
			"closed_before": closed_before, "open_after_press": open_after_press,
			"shows_class_none": shows_class_none, "shows_name": shows_name,
			"closed_after_second_press": closed_after_second_press, "stats_text": stats_text,
		},
	})
	screen.queue_free()
	await get_tree().process_frame


func _report() -> void:
	var all_pass := true
	for c in _checks:
		if not c["pass"]:
			all_pass = false
	print("SMOKE_TEST_RESULT ", JSON.stringify({"all_pass": all_pass, "checks": _checks}))
	get_tree().quit(0 if all_pass else 1)
