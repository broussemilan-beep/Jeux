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
	# Mandat critique probabiliste : zéro pour TOUTE la suite sauf
	# _check_critical_hit() (qui force sa propre valeur puis restaure
	# celle-ci) — sans ça, un crit qui roule au hasard pendant un check
	# de dégâts/hitstop exacts le ferait échouer de façon intermittente.
	# Pas de RNG à seeder : la chance elle-même est la variable de test.
	_player._combo_crit_chance_percent = 0.0

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
	await _check_critical_hit()
	await _check_dash()
	await _check_gueule_vide()
	await _check_gueule_vide_hits_enemy_at_realistic_melee_range()
	await _check_gueule_vide_owner_death_policy()
	await _check_hit_response()
	await _check_animation_composer_and_camera()
	await _check_dodge()
	await _check_bras_faux()
	await _check_poing_belluaire()
	await _check_poing_tellurique()
	await _check_maree_de_sable()
	await _check_machoire()
	await _check_forme_bestiale()
	await _check_pattes_de_chasse()
	await _check_corbeau_pale()
	await _check_poing_du_colosse()
	await _check_oeil_sans_regard()
	await _check_serpent_creux()
	await _check_carapace()
	await _check_effondrement()
	await _check_fissure_eruptive()
	await _check_input_buffer_fires_at_cancel_window()
	await _check_input_buffer_expires_when_never_consumed()
	await _check_power_slot_gating()
	await _check_player_recoils_on_taking_damage()
	await _check_crawler_chases_and_hits_player()
	await _check_brute_telegraphs_before_hitting()
	await _check_ranged_keeps_distance_and_fires_projectile()
	await _check_enemy_faces_chase_direction_in_multiple_directions()
	await _check_enemy_directional_hit_reaction()
	await _check_enemy_stagger_on_consecutive_hits()
	await _check_weight_differentiates_projection_vs_planted()
	await _check_enemy_recoil_holds_real_separation_during_active_chase()
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
	await _check_player_death_restart_flow()

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


## Mandat "critique probabiliste" (verrouillé par Milan, nom de travail
## interne "Black Flash" — jamais exposé au joueur) : (A) un coup forcé
## à rouler critique applique x1.5 aux dégâts + le palier de feedback
## "critical" (flash plein écran + shake au-dessus de "heavy", jamais
## atteint par un coup normal) ; (B) la mécanique de streak — +3% par
## combo propre à 3 coups, un coup subi remet à 5% NET (jamais une
## décroissance). Piloté par manipulation directe de
## `_combo_crit_chance_percent` (forcé à 0.0 pour tout le reste de cette
## suite, voir _ready()) plutôt qu'un seed RNG à contrôler — la chance
## elle-même est la variable de test, pas le tirage.
func _check_critical_hit() -> void:
	await _wait_until(func(): return not _player._action_lock, Player.COMBO_TIER_RECOVERY_TICKS[2] + 10)

	# Réutilise l'ennemi déjà posé par _check_combo_tier_feedback() (même
	# position, encore bien vivant après 3 coups de combo léger) plutôt
	# que d'en spawner un second au même endroit — évite toute ambiguïté
	# de ciblage (voir le commentaire sur "EnemyForCombo" plus haut dans
	# ce fichier).
	var enemy: Enemy = get_node("EnemyForTierFeedback")

	# --- Partie A : un coup forcé à 100% doit appliquer x1.5 + le palier
	# de feedback "critical" ---
	_player._combo_crit_chance_percent = 100.0
	var hp_before: float = enemy.stats.hp
	Input.action_press("attack")
	await get_tree().physics_frame
	Input.action_release("attack")
	await _wait_until(func(): return _player._combo_step == 1, 10)
	var hit_landed: bool = await _wait_until(
		func(): return enemy.stats.hp < hp_before,
		Player.ANTICIPATION_TICKS + Player.RELEASE_TICKS + 5)
	var damage_dealt: float = hp_before - enemy.stats.hp
	var screen_flash_alpha: float = CombatFeedback.get_screen_flash_color().a
	var shake_amplitude: float = CombatFeedback._shake_amplitude_px

	_checks.append({
		"name": "critical_hit_applies_1_5x_damage",
		"pass": hit_landed and is_equal_approx(damage_dealt, Player.ATTACK_DAMAGE * Player.CRIT_DAMAGE_MULT),
		"detail": {
			"hit_landed": hit_landed, "damage_dealt": damage_dealt,
			"expected": Player.ATTACK_DAMAGE * Player.CRIT_DAMAGE_MULT,
		},
	})
	_checks.append({
		"name": "critical_hit_triggers_distinct_screen_flash_and_shake",
		"pass": screen_flash_alpha > 0.0 and is_equal_approx(shake_amplitude, 9.0),
		"detail": {"screen_flash_alpha": screen_flash_alpha, "shake_amplitude": shake_amplitude},
	})

	# Laisser ce combo (un seul coup, pas chaîné) retomber jusqu'à idle
	# avant la partie B — sinon le premier "attack" de la partie B
	# chaînerait vers coup2 au lieu de démarrer un combo neuf.
	await _wait_until(
		func(): return _player._combo_step == 0,
		Player.RELEASE_TICKS + Player.COMBO_TIER_RECOVERY_TICKS[0] + 10)

	# --- Partie B : streak — combo propre à 3 coups ajoute +3%, un coup
	# subi remet net à 5% ---
	_player._combo_crit_chance_percent = Player.CRIT_BASE_CHANCE_PERCENT
	var chain_window_start: int = Player.RECOVERY_TICKS - Player.CHAIN_WINDOW_TICKS

	Input.action_press("attack")
	await get_tree().physics_frame
	Input.action_release("attack")
	await _wait_until(func(): return _player._combo_step == 1, 10)
	await _wait_until(
		func(): return _player._combo_step == 1 and _player._combo_phase == Player.ComboPhase.RECOVERY and _player._combo_tick >= chain_window_start,
		Player.RECOVERY_TICKS + 5)
	Input.action_press("attack")
	await get_tree().physics_frame
	Input.action_release("attack")
	await _wait_until(func(): return _player._combo_step == 2, 10)
	await _wait_until(
		func(): return _player._combo_step == 2 and _player._combo_phase == Player.ComboPhase.RECOVERY and _player._combo_tick >= chain_window_start,
		Player.RECOVERY_TICKS + 5)
	Input.action_press("attack")
	await get_tree().physics_frame
	Input.action_release("attack")
	await _wait_until(func(): return _player._combo_step == 3, 10)
	await _wait_until(
		func(): return _player._combo_step == 0,
		Player.COMBO_TIER_ANTICIPATION_TICKS[2] + Player.RELEASE_TICKS + Player.COMBO_TIER_RECOVERY_TICKS[2] + 10)

	var chance_after_clean_combo: float = _player._combo_crit_chance_percent
	_checks.append({
		"name": "critical_streak_bonus_added_after_clean_3_hit_combo",
		"pass": is_equal_approx(chance_after_clean_combo, Player.CRIT_BASE_CHANCE_PERCENT + Player.CRIT_STREAK_BONUS_PERCENT),
		"detail": {"chance_after_clean_combo": chance_after_clean_combo},
	})

	# Un coup subi (à tout moment, pas seulement pendant un combo) doit
	# remettre net à 5%, jamais une décroissance progressive.
	_player.take_damage(1.0, _player.global_position + Vector2(-10, 0))
	var chance_after_taking_damage: float = _player._combo_crit_chance_percent
	_checks.append({
		"name": "taking_damage_resets_crit_chance_to_base",
		"pass": is_equal_approx(chance_after_taking_damage, Player.CRIT_BASE_CHANCE_PERCENT),
		"detail": {"chance_after_taking_damage": chance_after_taking_damage},
	})

	# Rétablit l'état test-safe (0%, voir _ready()) pour le reste de la suite.
	_player._combo_crit_chance_percent = 0.0
	enemy.queue_free()
	await get_tree().physics_frame


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


## MANDAT RETOURS DE PLAYTEST RÉEL, point 4 ("Gueule Vide imperceptible en
## jeu réel") — diagnostic AVANT hypothèse (discipline demandée) : la
## créature ne se déplace jamais (aucun code de mouvement dans
## gueule_vide.gd), elle mord dans un rayon ATTACK_RANGE_PX (48px) centré
## sur SA PROPRE position, elle-même à POWER1_SPAWN_DISTANCE_PX (96px) du
## joueur. Elle ne peut donc toucher qu'un ennemi situé entre 48px et
## 144px du joueur (bande centrée sur elle) — un ennemi DÉJÀ EN TRAIN
## D'ATTAQUER le joueur au corps-à-corps (le moment le plus probable pour
## lancer une invocation "de contre") est lui, par construction, à sa
## propre portée de contact (`attack_range_px` côté Enemy — 28px pour
## Crawler, `scenes/gameplay/enemy_crawler.tscn`), donc DANS l'angle mort
## entre le joueur et la créature, hors du rayon de morsure. Ce check
## reproduit ce scénario réaliste (ennemi à portée de contact Crawler, pas
## la position artificiellement commode du check `_check_gueule_vide()`
## ci-dessus) pour vérifier si le coup part vraiment dans les conditions
## de jeu les plus courantes.
func _check_gueule_vide_hits_enemy_at_realistic_melee_range() -> void:
	RunState.active_power = "invocateur"
	_player.facing = Vector2.RIGHT

	# _check_gueule_vide() juste avant a déjà consommé le cooldown de
	# power1 (6s = 360 ticks) — sans attendre qu'il retombe ici, la
	# pression ci-dessous ne spawnerait RIEN et ce check "réussirait" pour
	# la mauvaise raison (aucun cast, donc aucun dégât, jamais un hit
	# manqué détecté). Attendre le retour à 0 AVANT de presser, pas après.
	await _wait_until(func(): return _player._power1_cooldown_remaining <= 0, Player.POWER1_COOLDOWN_TICKS + 10)

	var enemy := EnemyCrawlerScene.instantiate()
	enemy.name = "EnemyMeleeRangeForGueuleVide"
	# Crawler.attack_range_px = 28px — distance à laquelle il s'arrête pour
	# mordre le joueur en vrai combat (scenes/gameplay/enemy_crawler.tscn).
	enemy.global_position = _player.global_position + Vector2.RIGHT * 28.0
	add_child(enemy)
	await get_tree().physics_frame

	var hp_before: float = enemy.stats.hp

	Input.action_press("power1")
	await get_tree().physics_frame
	Input.action_release("power1")

	# Recherche AVEC nouvelle tentative après le hit, pas une seule lecture
	# immédiate après le relâchement : le _physics_process() de Player qui
	# instancie la créature (Player._cast_gueule_vide()) tourne au tick
	# PHYSIQUE suivant la pression, pas de façon synchrone à l'intérieur de
	# ce même appel — une recherche one-shot juste après release() peut donc
	# rater la créature alors qu'elle apparaît bien une frame plus tard
	# (constaté : `get_children()` ne la contenait pas encore à cet instant
	# précis lors de la mise au point de ce check).
	var creature: GueuleVide = null
	for child in get_children():
		if child is GueuleVide:
			creature = child
			break

	var hit_landed: bool = await _wait_until(func(): return enemy.stats.hp < hp_before, GueuleVide.TOTAL_TICKS + 10)
	if creature == null:
		for child in get_children():
			if child is GueuleVide:
				creature = child
				break

	_checks.append({
		"name": "gueule_vide_hits_enemy_at_realistic_melee_contact_range",
		"pass": hit_landed,
		"detail": {"hit_landed": hit_landed, "enemy_distance_from_player_px": 28.0},
	})

	enemy.queue_free()
	# Attendre que CETTE créature termine réellement son cast (jusqu'à son
	# shardBurst de désintégration, ticks 27-42) avant de rendre la main —
	# sinon elle continue de tourner en arrière-plan pendant le check
	# SUIVANT (_check_gueule_vide_owner_death_policy(), qui vide puis
	# relit VfxDirector.spawn_log pour SA PROPRE créature) et peut y faire
	# fuiter un "shardBurst" qui n'a rien à voir avec ce que ce check-là
	# vérifie — même bug de non-isolation inter-check que documenté au-
	# dessus pour "EnemyForGueuleVide" resté dans le groupe "enemies".
	if creature != null:
		await _wait_until(func(): return not is_instance_valid(creature), GueuleVide.TOTAL_TICKS + 10)

	# Cette morsure a déclenché son propre hit-stop + punch-zoom caméra
	# (CombatFeedback.register_hit(), même mécanisme que le combo — voir
	# gueule_vide.gd::_resolve_contact()). Sans attendre leur retour à
	# l'état neutre ICI, un check ULTÉRIEUR qui suppose une caméra/un
	# hit-stop au repos (ex. camera_punch_zoom_triggers_on_medium_hit_
	# not_light, qui lit CameraDirector.get_punch_zoom() juste après un
	# coup "light" et attend Vector2.ONE) peut lire un résidu qui n'a rien
	# à voir avec CE qu'il teste — même famille de bug de non-isolation
	# inter-check que le commentaire "Phase R4" de
	# src/vfx/vfx_recipe_registry.gd (_physics_process) documente déjà
	# pour VfxDirector.spawn_log.
	await _wait_until(func():
		return not CombatFeedback.is_frozen() and CameraDirector.get_punch_zoom() == Vector2.ONE
	, CameraDirector.PUNCH_ZOOM_TICKS + 20)
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
		"name": "bras_faux_input_starts_state_and_plays_dedicated_anim",
		"pass": started and anim_during == "bras_faux",
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
		"name": "poing_belluaire_input_starts_state_and_plays_dedicated_anim",
		"pass": started and anim_during == "poing_belluaire",
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
		"name": "poing_tellurique_input_starts_state_and_plays_dedicated_anim",
		"pass": started and anim_during == "poing_tellurique",
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


## MANDAT AUTONOME v3 Phase 3 — Marée de Sable (Terre, tier 2, palier
## niveau 3, slot "power2" comme Bras-Faux/tier 2 de Monstrification).
## Vérifie la forme LIGNE (pas un cône comme Bras-Faux/Poing Tellurique) :
## un ennemi dans l'axe est touché, un ennemi decalé lateralement au-dela
## de la demi-largeur est epargne, un ennemi au-dela de la portee est
## epargne — 3 angles distincts de enemies_in_arc(). Verifie aussi le
## ralentissement (apply_slow(), Enemy.gd) sur la cible touchee.
func _check_maree_de_sable() -> void:
	await _wait_until(func(): return not _player._action_lock, Player.MAREE_DE_SABLE_RECOVERY_TICKS + 5)

	RunState.active_power = "terre"
	_player.stats.level = 3  # palier de Marée de Sable (tier 2)

	_player.global_position = Vector2(200, 2300)
	_player.velocity = Vector2.ZERO
	_player.facing = Vector2.RIGHT
	var sprite: AnimatedSprite2D = _player.get_node("AnimatedSprite2D")

	var enemy_in_line := EnemyScene.instantiate()
	enemy_in_line.name = "MareeDeSableInLine"
	enemy_in_line.global_position = _player.global_position + Vector2(60, 0)  # forward 60 <= 90, lateral 0 <= 15
	add_child(enemy_in_line)

	var enemy_lateral_outside := EnemyScene.instantiate()
	enemy_lateral_outside.name = "MareeDeSableLateralOutside"
	enemy_lateral_outside.global_position = _player.global_position + Vector2(60, 30)  # forward 60, lateral 30 > 15
	add_child(enemy_lateral_outside)

	var enemy_beyond_range := EnemyScene.instantiate()
	enemy_beyond_range.name = "MareeDeSableBeyondRange"
	enemy_beyond_range.global_position = _player.global_position + Vector2(150, 0)  # forward 150 > 90
	add_child(enemy_beyond_range)

	await get_tree().physics_frame

	var hp_in_line_before: float = enemy_in_line.stats.hp
	var hp_lateral_outside_before: float = enemy_lateral_outside.stats.hp
	var hp_beyond_range_before: float = enemy_beyond_range.stats.hp

	Input.action_press("power2")
	await get_tree().physics_frame
	Input.action_release("power2")
	var started: bool = await _wait_until(func(): return _player._maree_de_sable_phase != Player.MareeDeSablePhase.NONE, 5)
	var anim_during: String = sprite.animation

	await _wait_until(
		func(): return enemy_in_line.stats.hp < hp_in_line_before,
		Player.MAREE_DE_SABLE_ANTICIPATION_TICKS + Player.MAREE_DE_SABLE_RELEASE_TICKS + 5)
	var hp_in_line_after: float = enemy_in_line.stats.hp
	var hp_lateral_outside_after: float = enemy_lateral_outside.stats.hp
	var hp_beyond_range_after: float = enemy_beyond_range.stats.hp
	var in_line_slowed: bool = enemy_in_line._slow_multiplier < 1.0 and enemy_in_line._slow_ticks_remaining > 0
	var lateral_outside_not_slowed: bool = enemy_lateral_outside._slow_multiplier == 1.0

	# MANDAT DÉDIÉ MARÉE DE SABLE (polish, 2026-08-23) — écart trouvé : le
	# ralentissement (apply_slow() ci-dessus) changeait bien la vitesse mais
	# rien à l'écran ne le montrait (Enemy._reset_visual_color() ne
	# connaissait pas _slow_ticks_remaining avant ce correctif). Marge de 12
	# ticks physiques (PAS 1 seul) avant de lire self_modulate/Polygon2D.color :
	# juste après take_damage(), Enemy._physics_process() retourne tôt
	# plusieurs ticks de suite (hit-stop "medium" ~4 ticks via
	# CombatFeedback.is_enemy_frozen(), PUIS recul ~6 ticks via
	# _recoil_tick < _recoil_total_ticks) AVANT d'atteindre le code qui
	# applique la teinte — un seul tick de marge échouait systématiquement
	# ici (in_line_color restait au magenta de base), pas un bug de la
	# teinte elle-même mais un test qui la lisait trop tôt.
	for _i in 12:
		await get_tree().physics_frame
	var in_line_color: Color = enemy_in_line._visual.self_modulate if enemy_in_line._visual is AnimatedSprite2D else (enemy_in_line._visual as Polygon2D).color
	var lateral_outside_color: Color = enemy_lateral_outside._visual.self_modulate if enemy_lateral_outside._visual is AnimatedSprite2D else (enemy_lateral_outside._visual as Polygon2D).color
	var in_line_visually_tinted: bool = in_line_color != enemy_in_line._base_visual_color
	var lateral_outside_not_tinted: bool = lateral_outside_color == enemy_lateral_outside._base_visual_color

	var ended: bool = await _wait_until(
		func(): return _player._maree_de_sable_phase == Player.MareeDeSablePhase.NONE,
		Player.MAREE_DE_SABLE_RELEASE_TICKS + Player.MAREE_DE_SABLE_RECOVERY_TICKS + 5)
	var action_unlocked_after: bool = not _player._action_lock

	Input.action_press("power2")
	await get_tree().physics_frame
	Input.action_release("power2")
	var maree_de_sable_started_during_cooldown: bool = _player._maree_de_sable_phase != Player.MareeDeSablePhase.NONE

	_checks.append({
		"name": "maree_de_sable_input_starts_state_and_plays_dedicated_anim",
		"pass": started and anim_during == "maree_de_sable",
		"detail": {"started": started, "anim": anim_during},
	})
	_checks.append({
		"name": "maree_de_sable_hits_line_spares_lateral_and_beyond_range",
		"pass": hp_in_line_after < hp_in_line_before and hp_lateral_outside_after == hp_lateral_outside_before and hp_beyond_range_after == hp_beyond_range_before,
		"detail": {
			"hp_in_line_before": hp_in_line_before, "hp_in_line_after": hp_in_line_after,
			"hp_lateral_outside_before": hp_lateral_outside_before, "hp_lateral_outside_after": hp_lateral_outside_after,
			"hp_beyond_range_before": hp_beyond_range_before, "hp_beyond_range_after": hp_beyond_range_after,
		},
	})
	_checks.append({
		"name": "maree_de_sable_slows_target_hit_only",
		"pass": in_line_slowed and lateral_outside_not_slowed,
		"detail": {"in_line_slowed": in_line_slowed, "lateral_outside_not_slowed": lateral_outside_not_slowed},
	})
	_checks.append({
		"name": "maree_de_sable_slow_has_visible_tint_on_hit_target_only",
		"pass": in_line_visually_tinted and lateral_outside_not_tinted,
		"detail": {
			"in_line_color": in_line_color, "in_line_base_color": enemy_in_line._base_visual_color,
			"lateral_outside_color": lateral_outside_color, "lateral_outside_base_color": enemy_lateral_outside._base_visual_color,
		},
	})
	_checks.append({
		"name": "maree_de_sable_ends_and_unlocks_then_cooldown_blocks_second_cast",
		"pass": ended and action_unlocked_after and not maree_de_sable_started_during_cooldown,
		"detail": {
			"ended": ended, "action_unlocked_after": action_unlocked_after,
			"maree_de_sable_started_during_cooldown": maree_de_sable_started_during_cooldown,
		},
	})

	enemy_in_line.queue_free()
	enemy_lateral_outside.queue_free()
	enemy_beyond_range.queue_free()
	await get_tree().physics_frame


## CHANTIER A (2026-08-24, agent dédié Terre, plan de production v1) —
## Carapace (tier 3, DÉFENSIF, slot "power3"). Structurellement différent
## des 4 autres compétences Terre (voir Player.CarapacePhase/CARAPACE_* et
## power.carapace.cast.json) : pas de _try_hit — vérifie l'activation, le
## passage en phase ACTIVE (buff is_carapace_active() + réduction de
## dégâts mesurée), la phase RECOVERY, puis que le multiplicateur ne
## persiste PAS après _end_carapace(). Avance directement au bout de
## l'ACTIVE en manipulant _carapace_tick (CARAPACE_ACTIVE_TICKS=180 —
## attendre ces ticks un par un serait inutilement long, même discipline
## que les autres checks qui réinitialisent directement l'état interne,
## ex. *_cooldown_remaining = 0 plus bas).
func _check_carapace() -> void:
	await _wait_until(func(): return not _player._action_lock, Player.CARAPACE_RECOVERY_TICKS + 5)

	RunState.active_power = "terre"
	_player.stats.level = 6  # palier de Carapace (tier 3, data/pouvoirs/terre.json)

	_player.global_position = Vector2(200, 2500)
	_player.velocity = Vector2.ZERO
	_player.facing = Vector2.RIGHT
	var sprite: AnimatedSprite2D = _player.get_node("AnimatedSprite2D")

	Input.action_press("power3")
	await get_tree().physics_frame
	Input.action_release("power3")
	var started: bool = await _wait_until(func(): return _player._carapace_phase != Player.CarapacePhase.NONE, 5)
	var anim_during_activation: String = sprite.animation

	var reached_active: bool = await _wait_until(
		func(): return _player._carapace_phase == Player.CarapacePhase.ACTIVE,
		Player.CARAPACE_ACTIVATION_TICKS + 5)
	var anim_during_active: String = sprite.animation
	var buff_active_flag: bool = _player.is_carapace_active()

	var hp_before_hit: float = _player.stats.hp
	_player.take_damage(20.0, _player.global_position + Vector2(-10, 0))
	var damage_taken_during_active: float = hp_before_hit - _player.stats.hp

	_player._carapace_tick = Player.CARAPACE_ACTIVE_TICKS
	var reached_recovery: bool = await _wait_until(
		func(): return _player._carapace_phase == Player.CarapacePhase.RECOVERY, 5)
	var anim_during_recovery: String = sprite.animation

	var ended: bool = await _wait_until(
		func(): return _player._carapace_phase == Player.CarapacePhase.NONE,
		Player.CARAPACE_RECOVERY_TICKS + 5)
	var action_unlocked_after: bool = not _player._action_lock
	var buff_inactive_after_end: bool = not _player.is_carapace_active()

	var hp_before_hit2: float = _player.stats.hp
	_player.take_damage(20.0, _player.global_position + Vector2(-10, 0))
	var damage_taken_after_end: float = hp_before_hit2 - _player.stats.hp

	Input.action_press("power3")
	await get_tree().physics_frame
	Input.action_release("power3")
	var carapace_started_during_cooldown: bool = _player._carapace_phase != Player.CarapacePhase.NONE

	_checks.append({
		"name": "carapace_input_starts_activation_and_plays_dedicated_anim",
		"pass": started and anim_during_activation == "carapace_activation",
		"detail": {"started": started, "anim": anim_during_activation},
	})
	_checks.append({
		"name": "carapace_reaches_active_phase_and_plays_looping_anim",
		"pass": reached_active and anim_during_active == "carapace_active" and buff_active_flag,
		"detail": {"reached_active": reached_active, "anim": anim_during_active, "buff_active_flag": buff_active_flag},
	})
	_checks.append({
		"name": "carapace_active_reduces_damage_taken_by_configured_multiplier",
		"pass": is_equal_approx(damage_taken_during_active, 20.0 * Player.CARAPACE_DAMAGE_MULTIPLIER),
		"detail": {"damage_taken_during_active": damage_taken_during_active, "expected": 20.0 * Player.CARAPACE_DAMAGE_MULTIPLIER},
	})
	_checks.append({
		"name": "carapace_reaches_recovery_then_ends_and_unlocks_then_cooldown_blocks_second_cast",
		"pass": reached_recovery and anim_during_recovery == "carapace_fin" and ended and action_unlocked_after and buff_inactive_after_end and not carapace_started_during_cooldown,
		"detail": {
			"reached_recovery": reached_recovery, "anim_during_recovery": anim_during_recovery,
			"ended": ended, "action_unlocked_after": action_unlocked_after,
			"buff_inactive_after_end": buff_inactive_after_end,
			"carapace_started_during_cooldown": carapace_started_during_cooldown,
		},
	})
	_checks.append({
		"name": "carapace_damage_reduction_does_not_persist_after_buff_ends",
		"pass": is_equal_approx(damage_taken_after_end, 20.0),
		"detail": {"damage_taken_after_end": damage_taken_after_end, "expected": 20.0},
	})

	# Chauffe anti-fuite d'input (constatée empiriquement, cf. capture_scene.gd
	# "ordre non garanti entre la reprise d'un `await` et le traitement
	# physique des autres nœuds") : la pression power3 juste au-dessus est
	# bloquée par le cooldown au moment où elle est traitée, MAIS sous
	# llvmpipe/xvfb le just_pressed correspondant peut être vu une seconde
	# fois, en retard, quelques ticks plus tard — sans conséquence tant que
	# le cooldown est encore > 0 (blocage silencieux, idempotent). Ces
	# quelques ticks laissent cette éventuelle 2e détection se dissiper
	# PENDANT que le cooldown est encore plein, avant de le remettre à 0
	# juste en dessous — sinon un power3 fantôme, retrouvant le cooldown à
	# 0, peut se mettre en file (si _action_lock est vrai à cet instant pour
	# une tout autre raison) et se déclencher pour de bon pendant le check
	# suivant (_check_effondrement), qui ne presse jamais lui-même power3.
	for i in range(4):
		await get_tree().physics_frame
	_player._carapace_cooldown_remaining = 0


## Effondrement (tier 4, ZONE/IMPACT MAJEUR, slot "power4"). Vérifie la
## forme CERCLE (half_angle_deg=180 dans _try_hit_effondrement(), pas un
## cône comme Poing Tellurique/Bras-Faux) : un ennemi DEVANT et un ennemi
## DERRIÈRE le lanceur sont TOUS LES DEUX touchés (preuve que ce n'est pas
## un cône frontal), un ennemi au-delà du rayon est épargné.
func _check_effondrement() -> void:
	await _wait_until(func(): return not _player._action_lock, Player.EFFONDREMENT_RECOVERY_TICKS + 5)

	RunState.active_power = "terre"
	_player.stats.level = 10  # palier d'Effondrement (tier 4)

	_player.global_position = Vector2(200, 2700)
	_player.velocity = Vector2.ZERO
	_player.facing = Vector2.RIGHT
	var sprite: AnimatedSprite2D = _player.get_node("AnimatedSprite2D")

	var enemy_front := EnemyScene.instantiate()
	enemy_front.name = "EffondrementFront"
	enemy_front.global_position = _player.global_position + Vector2(50, 0)  # devant, dans le rayon 70
	add_child(enemy_front)

	var enemy_behind := EnemyScene.instantiate()
	enemy_behind.name = "EffondrementBehind"
	enemy_behind.global_position = _player.global_position + Vector2(-50, 0)  # DERRIÈRE — hors d'un cône frontal, dans un cercle
	add_child(enemy_behind)

	var enemy_beyond_radius := EnemyScene.instantiate()
	enemy_beyond_radius.name = "EffondrementBeyondRadius"
	enemy_beyond_radius.global_position = _player.global_position + Vector2(0, 120)  # 120 > 70
	add_child(enemy_beyond_radius)

	await get_tree().physics_frame

	var hp_front_before: float = enemy_front.stats.hp
	var hp_behind_before: float = enemy_behind.stats.hp
	var hp_beyond_radius_before: float = enemy_beyond_radius.stats.hp

	Input.action_press("power4")
	await get_tree().physics_frame
	Input.action_release("power4")
	var started: bool = await _wait_until(func(): return _player._effondrement_phase != Player.EffondrementPhase.NONE, 5)
	var anim_during: String = sprite.animation

	await _wait_until(
		func(): return enemy_front.stats.hp < hp_front_before,
		Player.EFFONDREMENT_ANTICIPATION_TICKS + Player.EFFONDREMENT_RELEASE_TICKS + 5)
	var hp_front_after: float = enemy_front.stats.hp
	var hp_behind_after: float = enemy_behind.stats.hp
	var hp_beyond_radius_after: float = enemy_beyond_radius.stats.hp

	# Marge élargie (+25, pas le +5 habituel) — constaté empiriquement (agent
	# Terre, CHANTIER A) : sous xvfb/llvmpipe, Input.is_action_just_pressed()
	# peut voir un "power4" retardé de plusieurs dizaines de ticks après
	# l'appui synthétique du haut de cette fonction (même famille de
	# décalage physics/render déjà documentée pour capture_scene.gd) — sur
	# ANTICIPATION+RELEASE aussi longs qu'Effondrement (36 ticks), cet écho
	# tombe parfois DANS la fenêtre d'annulation de sa propre RECOVERY,
	# consommé comme un input en file légitime (comportement CORRECT du
	# système d'annulation généralisé face à ce qu'il reçoit) et termine le
	# cast un peu plus tôt que les 26 ticks nominaux — la marge de +5 des
	# autres compétences Terre (bien plus courtes) ne suffit pas toujours à
	# voir cette fin anticipée avant expiration du budget de ce `_wait_until`.
	var ended: bool = await _wait_until(
		func(): return _player._effondrement_phase == Player.EffondrementPhase.NONE,
		Player.EFFONDREMENT_RECOVERY_TICKS + 25)
	var action_unlocked_after: bool = not _player._action_lock

	Input.action_press("power4")
	await get_tree().physics_frame
	Input.action_release("power4")
	var effondrement_started_during_cooldown: bool = _player._effondrement_phase != Player.EffondrementPhase.NONE

	_checks.append({
		"name": "effondrement_input_starts_state_and_plays_dedicated_anim",
		"pass": started and anim_during == "effondrement",
		"detail": {"started": started, "anim": anim_during},
	})
	_checks.append({
		"name": "effondrement_hits_full_circle_front_and_behind_spares_beyond_radius",
		"pass": hp_front_after < hp_front_before and hp_behind_after < hp_behind_before and hp_beyond_radius_after == hp_beyond_radius_before,
		"detail": {
			"hp_front_before": hp_front_before, "hp_front_after": hp_front_after,
			"hp_behind_before": hp_behind_before, "hp_behind_after": hp_behind_after,
			"hp_beyond_radius_before": hp_beyond_radius_before, "hp_beyond_radius_after": hp_beyond_radius_after,
		},
	})
	_checks.append({
		"name": "effondrement_ends_and_unlocks_then_cooldown_blocks_second_cast",
		"pass": ended and action_unlocked_after and not effondrement_started_during_cooldown,
		"detail": {
			"ended": ended, "action_unlocked_after": action_unlocked_after,
			"effondrement_started_during_cooldown": effondrement_started_during_cooldown,
		},
	})

	enemy_front.queue_free()
	enemy_behind.queue_free()
	enemy_beyond_radius.queue_free()
	await get_tree().physics_frame


## Fissure Éruptive (tier 5, dernière compétence Terre, slot "power5").
## Vérifie que l'impact tombe À DISTANCE (FISSURE_ERUPTIVE_RANGE_PX devant
## le lanceur), PAS sur le lanceur lui-même comme Effondrement : un ennemi
## AU POINT D'IMPACT est touché, un ennemi PRÈS DU LANCEUR (mais pas au
## point d'impact) et un ennemi AU-DELÀ du petit rayon d'impact sont
## épargnés tous les deux.
func _check_fissure_eruptive() -> void:
	await _wait_until(func(): return not _player._action_lock, Player.FISSURE_ERUPTIVE_RECOVERY_TICKS + 5)

	RunState.active_power = "terre"
	_player.stats.level = 15  # palier de Fissure Éruptive (tier 5)

	_player.global_position = Vector2(200, 2900)
	_player.velocity = Vector2.ZERO
	_player.facing = Vector2.RIGHT
	var sprite: AnimatedSprite2D = _player.get_node("AnimatedSprite2D")

	var enemy_at_impact := EnemyScene.instantiate()
	enemy_at_impact.name = "FissureEruptiveAtImpact"
	enemy_at_impact.global_position = _player.global_position + Vector2(Player.FISSURE_ERUPTIVE_RANGE_PX, 0)
	add_child(enemy_at_impact)

	var enemy_near_caster := EnemyScene.instantiate()
	enemy_near_caster.name = "FissureEruptiveNearCaster"
	enemy_near_caster.global_position = _player.global_position + Vector2(20, 0)
	add_child(enemy_near_caster)

	var enemy_beyond_impact := EnemyScene.instantiate()
	enemy_beyond_impact.name = "FissureEruptiveBeyondImpact"
	enemy_beyond_impact.global_position = _player.global_position + Vector2(Player.FISSURE_ERUPTIVE_RANGE_PX + 80, 0)
	add_child(enemy_beyond_impact)

	await get_tree().physics_frame

	var hp_at_impact_before: float = enemy_at_impact.stats.hp
	var hp_near_caster_before: float = enemy_near_caster.stats.hp
	var hp_beyond_impact_before: float = enemy_beyond_impact.stats.hp

	Input.action_press("power5")
	await get_tree().physics_frame
	Input.action_release("power5")
	var started: bool = await _wait_until(func(): return _player._fissure_eruptive_phase != Player.FissureEruptivePhase.NONE, 5)
	var anim_during: String = sprite.animation

	await _wait_until(
		func(): return enemy_at_impact.stats.hp < hp_at_impact_before,
		Player.FISSURE_ERUPTIVE_ANTICIPATION_TICKS + Player.FISSURE_ERUPTIVE_RELEASE_TICKS + 5)
	var hp_at_impact_after: float = enemy_at_impact.stats.hp
	var hp_near_caster_after: float = enemy_near_caster.stats.hp
	var hp_beyond_impact_after: float = enemy_beyond_impact.stats.hp

	# Marge élargie (+25) — même remarque que _check_effondrement() juste
	# au-dessus : ANTICIPATION+RELEASE=28 ticks laisse le temps à un écho
	# tardif de "power5" (xvfb/llvmpipe) de retomber dans la fenêtre
	# d'annulation de la RECOVERY et d'y être consommé légitimement, un peu
	# avant les 30 ticks nominaux.
	var ended: bool = await _wait_until(
		func(): return _player._fissure_eruptive_phase == Player.FissureEruptivePhase.NONE,
		Player.FISSURE_ERUPTIVE_RECOVERY_TICKS + 25)
	var action_unlocked_after: bool = not _player._action_lock

	Input.action_press("power5")
	await get_tree().physics_frame
	Input.action_release("power5")
	var fissure_eruptive_started_during_cooldown: bool = _player._fissure_eruptive_phase != Player.FissureEruptivePhase.NONE

	_checks.append({
		"name": "fissure_eruptive_input_starts_state_and_plays_dedicated_anim",
		"pass": started and anim_during == "fissure_eruptive",
		"detail": {"started": started, "anim": anim_during},
	})
	_checks.append({
		"name": "fissure_eruptive_hits_only_at_ranged_impact_point_spares_caster_vicinity_and_beyond",
		"pass": hp_at_impact_after < hp_at_impact_before and hp_near_caster_after == hp_near_caster_before and hp_beyond_impact_after == hp_beyond_impact_before,
		"detail": {
			"hp_at_impact_before": hp_at_impact_before, "hp_at_impact_after": hp_at_impact_after,
			"hp_near_caster_before": hp_near_caster_before, "hp_near_caster_after": hp_near_caster_after,
			"hp_beyond_impact_before": hp_beyond_impact_before, "hp_beyond_impact_after": hp_beyond_impact_after,
		},
	})
	_checks.append({
		"name": "fissure_eruptive_ends_and_unlocks_then_cooldown_blocks_second_cast",
		"pass": ended and action_unlocked_after and not fissure_eruptive_started_during_cooldown,
		"detail": {
			"ended": ended, "action_unlocked_after": action_unlocked_after,
			"fissure_eruptive_started_during_cooldown": fissure_eruptive_started_during_cooldown,
		},
	})

	enemy_at_impact.queue_free()
	enemy_near_caster.queue_free()
	enemy_beyond_impact.queue_free()
	await get_tree().physics_frame


## CHANTIER A — agent Invocateur, les 4 compétences restantes (Corbeau
## Pâle T2, Poing du Colosse T3, Œil Sans Regard T4, Serpent Creux T5,
## data/pouvoirs/invocateur.json). Construction différente des 5
## compétences dédiées ci-dessus (Bras-Faux etc., qui restent sur la
## timeline du JOUEUR) : ces 4 suivent le patron de Gueule Vide
## (_check_gueule_vide()) — une créature SÉPARÉE (scenes/gameplay/
## powers/<skill>.tscn) qui pilote sa propre timeline de ticks/son propre
## sprite (FRAME_TICK_BOUNDS), avec le dégât/ciblage résolus DANS la
## créature, jamais dans player.gd. Note délibérée sur ce qui N'EST PAS
## testé ici : contrairement à Gueule Vide (dont le cooldown s'arme DÈS
## le cast, cf. _cast_gueule_vide()), ces 4 compétences arment leur
## cooldown seulement en fin de RECOVERY (_end_corbeau_pale() etc., même
## patron que _end_bras_faux()) — un second appui PENDANT le cast est
## donc mis en FILE par le buffer généralisé (_queued_power_slot), pas
## bloqué net, et peut légitimement relancer la MÊME compétence une fois
## sa propre fenêtre d'annulation ouverte ("dernier appui gagne", déjà
## exhaustivement vérifié pour ce mécanisme générique par
## _check_input_buffer_fires_at_cancel_window()/_check_input_buffer_expires_when_never_consumed()
## sur Bras-Faux/Poing Belluaire) — pas re-testé ici pour éviter de
## dupliquer ce scénario et de le faire courir contre le cooldown réel de
## CES 4 compétences.
##
## Corbeau Pâle — même construction que Gueule Vide mais la créature
## TRANSLATE réellement en ligne droite pendant sa phase de "chasse" (voir
## corbeau_pale.gd) : multi-cible en ligne (Targeting.enemies_in_line),
## pas une seule morsure ciblée.
func _check_corbeau_pale() -> void:
	await _wait_until(func(): return not _player._action_lock, 60)

	# Amendement GDD Pouvoir/déblocage : Corbeau Pâle est tier 2 de
	# l'Invocateur (data/pouvoirs/invocateur.json, palier niveau 3), slot
	# "power2" — voir get_unlocked_skill_for_slot().
	RunState.active_power = "invocateur"
	_player.stats.level = 3  # palier de Corbeau Pâle (tier 2, unlock_level 3)

	_player.global_position = Vector2(200, 3400)
	_player.velocity = Vector2.ZERO
	_player.facing = Vector2.RIGHT
	var sprite: AnimatedSprite2D = _player.get_node("AnimatedSprite2D")
	var spawn_origin: Vector2 = _player.global_position + Vector2.RIGHT * Player.CORBEAU_PALE_SPAWN_DISTANCE_PX

	var enemy_in_line := EnemyScene.instantiate()
	enemy_in_line.name = "CorbeauPaleInLine"
	enemy_in_line.global_position = spawn_origin + Vector2(60, 0)  # dans l'axe, 60px < RANGE_PX (140)
	add_child(enemy_in_line)

	var enemy_lateral_outside := EnemyScene.instantiate()
	enemy_lateral_outside.name = "CorbeauPaleLateralOutside"
	enemy_lateral_outside.global_position = spawn_origin + Vector2(60, 30)  # lateral 30 > HALF_WIDTH_PX (18)
	add_child(enemy_lateral_outside)

	var enemy_beyond_range := EnemyScene.instantiate()
	enemy_beyond_range.name = "CorbeauPaleBeyondRange"
	enemy_beyond_range.global_position = spawn_origin + Vector2(200, 0)  # 200px > RANGE_PX (140)
	add_child(enemy_beyond_range)

	await get_tree().physics_frame

	var hp_in_line_before: float = enemy_in_line.stats.hp
	var hp_lateral_outside_before: float = enemy_lateral_outside.stats.hp
	var hp_beyond_range_before: float = enemy_beyond_range.stats.hp

	Input.action_press("power2")
	await get_tree().physics_frame
	Input.action_release("power2")

	var creature: CorbeauPale = null
	var spawned: bool = await _wait_until(func():
		for child in get_children():
			if child is CorbeauPale:
				creature = child
				return true
		return false
	, Player.CORBEAU_PALE_ANTICIPATION_TICKS + 5)
	var anim_during: String = sprite.animation

	var hit_landed: bool = await _wait_until(func(): return enemy_in_line.stats.hp < hp_in_line_before, CorbeauPale.TOTAL_TICKS + 10)
	var hp_in_line_after: float = enemy_in_line.stats.hp
	var hp_lateral_outside_after: float = enemy_lateral_outside.stats.hp
	var hp_beyond_range_after: float = enemy_beyond_range.stats.hp

	var creature_finished: bool = await _wait_until(func(): return spawned and not is_instance_valid(creature), CorbeauPale.TOTAL_TICKS + 15)
	var action_unlocked_after: bool = await _wait_until(func(): return not _player._action_lock, 10)
	var cooldown_armed_after_cast: bool = _player._corbeau_pale_cooldown_remaining > 0

	Input.action_press("power2")
	await get_tree().physics_frame
	Input.action_release("power2")
	var creature_count_after_cooldown_press := 0
	for child in get_children():
		if child is CorbeauPale:
			creature_count_after_cooldown_press += 1

	_checks.append({
		"name": "corbeau_pale_input_spawns_creature_and_plays_dedicated_gesture",
		"pass": spawned and anim_during == "invocation_corbeau_pale",
		"detail": {"spawned": spawned, "anim": anim_during},
	})
	_checks.append({
		"name": "corbeau_pale_hits_enemy_in_line_spares_lateral_outside_and_beyond_range",
		"pass": hit_landed and hp_lateral_outside_after == hp_lateral_outside_before and hp_beyond_range_after == hp_beyond_range_before,
		"detail": {
			"hit_landed": hit_landed,
			"hp_in_line_before": hp_in_line_before, "hp_in_line_after": hp_in_line_after,
			"hp_lateral_outside_before": hp_lateral_outside_before, "hp_lateral_outside_after": hp_lateral_outside_after,
			"hp_beyond_range_before": hp_beyond_range_before, "hp_beyond_range_after": hp_beyond_range_after,
		},
	})
	_checks.append({
		"name": "corbeau_pale_ends_and_unlocks_then_cooldown_blocks_a_new_cast",
		"pass": creature_finished and action_unlocked_after and cooldown_armed_after_cast and creature_count_after_cooldown_press == 1,
		"detail": {
			"creature_finished": creature_finished, "action_unlocked_after": action_unlocked_after,
			"cooldown_armed_after_cast": cooldown_armed_after_cast,
			"creature_count_after_cooldown_press": creature_count_after_cooldown_press,
		},
	})

	enemy_in_line.queue_free()
	enemy_lateral_outside.queue_free()
	enemy_beyond_range.queue_free()
	await get_tree().physics_frame


## Poing du Colosse (INVOCATEUR, tier 3/5, palier niveau 6, slot "power3")
## — créature STATIONNAIRE (comme Gueule Vide) mais impact en ZONE (AoE,
## Targeting.enemies_in_arc en cercle complet, half_angle_deg=180 — voir
## poing_du_colosse.gd) : un ennemi proche de l'impact est touché QUELLE
## QUE SOIT sa direction, un ennemi hors du rayon est épargné.
func _check_poing_du_colosse() -> void:
	await _wait_until(func(): return not _player._action_lock, 60)

	RunState.active_power = "invocateur"
	_player.stats.level = 6  # palier de Poing du Colosse (tier 3, unlock_level 6)

	_player.global_position = Vector2(200, 3600)
	_player.velocity = Vector2.ZERO
	_player.facing = Vector2.RIGHT
	var sprite: AnimatedSprite2D = _player.get_node("AnimatedSprite2D")
	var spawn_origin: Vector2 = _player.global_position + Vector2.RIGHT * Player.POING_DU_COLOSSE_SPAWN_DISTANCE_PX

	var enemy_within_radius := EnemyScene.instantiate()
	enemy_within_radius.name = "PoingDuColosseWithinRadius"
	enemy_within_radius.global_position = spawn_origin + Vector2(0, 30)  # 30px < RADIUS_PX (56), AoE : la direction n'a aucun effet
	add_child(enemy_within_radius)

	var enemy_beyond_radius := EnemyScene.instantiate()
	enemy_beyond_radius.name = "PoingDuColosseBeyondRadius"
	enemy_beyond_radius.global_position = spawn_origin + Vector2(100, 0)  # 100px > RADIUS_PX (56)
	add_child(enemy_beyond_radius)

	await get_tree().physics_frame

	var hp_within_radius_before: float = enemy_within_radius.stats.hp
	var hp_beyond_radius_before: float = enemy_beyond_radius.stats.hp

	Input.action_press("power3")
	await get_tree().physics_frame
	Input.action_release("power3")

	var creature: PoingDuColosse = null
	var spawned: bool = await _wait_until(func():
		for child in get_children():
			if child is PoingDuColosse:
				creature = child
				return true
		return false
	, Player.POING_DU_COLOSSE_ANTICIPATION_TICKS + 5)
	var anim_during: String = sprite.animation

	var hit_landed: bool = await _wait_until(func(): return enemy_within_radius.stats.hp < hp_within_radius_before, PoingDuColosse.TOTAL_TICKS + 10)
	var hp_within_radius_after: float = enemy_within_radius.stats.hp
	var hp_beyond_radius_after: float = enemy_beyond_radius.stats.hp

	var creature_finished: bool = await _wait_until(func(): return spawned and not is_instance_valid(creature), PoingDuColosse.TOTAL_TICKS + 15)
	var action_unlocked_after: bool = await _wait_until(func(): return not _player._action_lock, 10)
	var cooldown_armed_after_cast: bool = _player._poing_du_colosse_cooldown_remaining > 0

	Input.action_press("power3")
	await get_tree().physics_frame
	Input.action_release("power3")
	var creature_count_after_cooldown_press := 0
	for child in get_children():
		if child is PoingDuColosse:
			creature_count_after_cooldown_press += 1

	_checks.append({
		"name": "poing_du_colosse_input_spawns_creature_and_plays_dedicated_gesture",
		"pass": spawned and anim_during == "invocation_poing_du_colosse",
		"detail": {"spawned": spawned, "anim": anim_during},
	})
	_checks.append({
		"name": "poing_du_colosse_hits_all_enemies_in_radius_spares_enemy_beyond_it",
		"pass": hit_landed and hp_beyond_radius_after == hp_beyond_radius_before,
		"detail": {
			"hit_landed": hit_landed,
			"hp_within_radius_before": hp_within_radius_before, "hp_within_radius_after": hp_within_radius_after,
			"hp_beyond_radius_before": hp_beyond_radius_before, "hp_beyond_radius_after": hp_beyond_radius_after,
		},
	})
	_checks.append({
		"name": "poing_du_colosse_ends_and_unlocks_then_cooldown_blocks_a_new_cast",
		"pass": creature_finished and action_unlocked_after and cooldown_armed_after_cast and creature_count_after_cooldown_press == 1,
		"detail": {
			"creature_finished": creature_finished, "action_unlocked_after": action_unlocked_after,
			"cooldown_armed_after_cast": cooldown_armed_after_cast,
			"creature_count_after_cooldown_press": creature_count_after_cooldown_press,
		},
	})

	enemy_within_radius.queue_free()
	enemy_beyond_radius.queue_free()
	await get_tree().physics_frame


## Œil Sans Regard (INVOCATEUR, tier 4/5, palier niveau 10, slot "power4")
## — créature STATIONNAIRE flottante (offset vertical au spawn), rayon
## PERCE en ligne résolu INSTANTANÉMENT à BEAM_TICK (pas une translation
## tick par tick comme Corbeau Pâle/Serpent Creux) : Targeting.
## enemies_in_line sur toute BEAM_LENGTH_PX, multi-cible.
func _check_oeil_sans_regard() -> void:
	await _wait_until(func(): return not _player._action_lock, 60)

	RunState.active_power = "invocateur"
	_player.stats.level = 10  # palier de Œil Sans Regard (tier 4, unlock_level 10)

	_player.global_position = Vector2(200, 3800)
	_player.velocity = Vector2.ZERO
	_player.facing = Vector2.RIGHT
	var sprite: AnimatedSprite2D = _player.get_node("AnimatedSprite2D")
	var spawn_origin: Vector2 = (
		_player.global_position
		+ Vector2.RIGHT * Player.OEIL_SANS_REGARD_SPAWN_DISTANCE_PX
		+ Vector2(0, Player.OEIL_SANS_REGARD_SPAWN_HEIGHT_OFFSET_PX)
	)

	var enemy_in_line := EnemyScene.instantiate()
	enemy_in_line.name = "OeilSansRegardInLine"
	enemy_in_line.global_position = spawn_origin + Vector2(60, 0)  # dans l'axe, 60px < BEAM_LENGTH_PX (128)
	add_child(enemy_in_line)

	var enemy_lateral_outside := EnemyScene.instantiate()
	enemy_lateral_outside.name = "OeilSansRegardLateralOutside"
	enemy_lateral_outside.global_position = spawn_origin + Vector2(60, 25)  # lateral 25 > BEAM_HALF_WIDTH_PX (12)
	add_child(enemy_lateral_outside)

	var enemy_beyond_range := EnemyScene.instantiate()
	enemy_beyond_range.name = "OeilSansRegardBeyondRange"
	enemy_beyond_range.global_position = spawn_origin + Vector2(200, 0)  # 200px > BEAM_LENGTH_PX (128)
	add_child(enemy_beyond_range)

	await get_tree().physics_frame

	var hp_in_line_before: float = enemy_in_line.stats.hp
	var hp_lateral_outside_before: float = enemy_lateral_outside.stats.hp
	var hp_beyond_range_before: float = enemy_beyond_range.stats.hp

	Input.action_press("power4")
	await get_tree().physics_frame
	Input.action_release("power4")

	var creature: OeilSansRegard = null
	var spawned: bool = await _wait_until(func():
		for child in get_children():
			if child is OeilSansRegard:
				creature = child
				return true
		return false
	, Player.OEIL_SANS_REGARD_ANTICIPATION_TICKS + 5)
	var anim_during: String = sprite.animation

	var hit_landed: bool = await _wait_until(func(): return enemy_in_line.stats.hp < hp_in_line_before, OeilSansRegard.TOTAL_TICKS + 10)
	var hp_in_line_after: float = enemy_in_line.stats.hp
	var hp_lateral_outside_after: float = enemy_lateral_outside.stats.hp
	var hp_beyond_range_after: float = enemy_beyond_range.stats.hp

	var creature_finished: bool = await _wait_until(func(): return spawned and not is_instance_valid(creature), OeilSansRegard.TOTAL_TICKS + 15)
	var action_unlocked_after: bool = await _wait_until(func(): return not _player._action_lock, 10)
	var cooldown_armed_after_cast: bool = _player._oeil_sans_regard_cooldown_remaining > 0

	Input.action_press("power4")
	await get_tree().physics_frame
	Input.action_release("power4")
	var creature_count_after_cooldown_press := 0
	for child in get_children():
		if child is OeilSansRegard:
			creature_count_after_cooldown_press += 1

	_checks.append({
		"name": "oeil_sans_regard_input_spawns_creature_and_plays_dedicated_gesture",
		"pass": spawned and anim_during == "invocation_oeil_sans_regard",
		"detail": {"spawned": spawned, "anim": anim_during},
	})
	_checks.append({
		"name": "oeil_sans_regard_beam_hits_enemy_in_line_spares_lateral_outside_and_beyond_range",
		"pass": hit_landed and hp_lateral_outside_after == hp_lateral_outside_before and hp_beyond_range_after == hp_beyond_range_before,
		"detail": {
			"hit_landed": hit_landed,
			"hp_in_line_before": hp_in_line_before, "hp_in_line_after": hp_in_line_after,
			"hp_lateral_outside_before": hp_lateral_outside_before, "hp_lateral_outside_after": hp_lateral_outside_after,
			"hp_beyond_range_before": hp_beyond_range_before, "hp_beyond_range_after": hp_beyond_range_after,
		},
	})
	_checks.append({
		"name": "oeil_sans_regard_ends_and_unlocks_then_cooldown_blocks_a_new_cast",
		"pass": creature_finished and action_unlocked_after and cooldown_armed_after_cast and creature_count_after_cooldown_press == 1,
		"detail": {
			"creature_finished": creature_finished, "action_unlocked_after": action_unlocked_after,
			"cooldown_armed_after_cast": cooldown_armed_after_cast,
			"creature_count_after_cooldown_press": creature_count_after_cooldown_press,
		},
	})

	enemy_in_line.queue_free()
	enemy_lateral_outside.queue_free()
	enemy_beyond_range.queue_free()
	await get_tree().physics_frame


## Serpent Creux (INVOCATEUR, tier 5/5, palier niveau 15, l'ultime, slot
## "power5", GDD §6.2) — même construction que Corbeau Pâle (créature qui
## translate réellement en ligne pendant sa phase d'attaque), portée
## strictement supérieure à Gueule Vide comme l'exige la fiche (voir
## serpent_creux.gd, commentaire RANGE_PX) — non re-testé chiffre pour
## chiffre ici (déjà démontré par construction dans le commentaire du
## script), seulement le comportement gameplay (spawn, multi-cible en
## ligne, cooldown, fin de vie).
func _check_serpent_creux() -> void:
	await _wait_until(func(): return not _player._action_lock, 60)

	RunState.active_power = "invocateur"
	_player.stats.level = 15  # palier de Serpent Creux (tier 5, unlock_level 15)

	_player.global_position = Vector2(200, 4000)
	_player.velocity = Vector2.ZERO
	_player.facing = Vector2.RIGHT
	var sprite: AnimatedSprite2D = _player.get_node("AnimatedSprite2D")
	var spawn_origin: Vector2 = _player.global_position + Vector2.RIGHT * Player.SERPENT_CREUX_SPAWN_DISTANCE_PX

	var enemy_in_line := EnemyScene.instantiate()
	enemy_in_line.name = "SerpentCreuxInLine"
	enemy_in_line.global_position = spawn_origin + Vector2(80, 0)  # dans l'axe, 80px < RANGE_PX (170)
	add_child(enemy_in_line)

	var enemy_lateral_outside := EnemyScene.instantiate()
	enemy_lateral_outside.name = "SerpentCreuxLateralOutside"
	enemy_lateral_outside.global_position = spawn_origin + Vector2(80, 30)  # lateral 30 > HALF_WIDTH_PX (16)
	add_child(enemy_lateral_outside)

	var enemy_beyond_range := EnemyScene.instantiate()
	enemy_beyond_range.name = "SerpentCreuxBeyondRange"
	enemy_beyond_range.global_position = spawn_origin + Vector2(220, 0)  # 220px > RANGE_PX (170)
	add_child(enemy_beyond_range)

	await get_tree().physics_frame

	var hp_in_line_before: float = enemy_in_line.stats.hp
	var hp_lateral_outside_before: float = enemy_lateral_outside.stats.hp
	var hp_beyond_range_before: float = enemy_beyond_range.stats.hp

	Input.action_press("power5")
	await get_tree().physics_frame
	Input.action_release("power5")

	var creature: SerpentCreux = null
	var spawned: bool = await _wait_until(func():
		for child in get_children():
			if child is SerpentCreux:
				creature = child
				return true
		return false
	, Player.SERPENT_CREUX_ANTICIPATION_TICKS + 5)
	var anim_during: String = sprite.animation

	var hit_landed: bool = await _wait_until(func(): return enemy_in_line.stats.hp < hp_in_line_before, SerpentCreux.TOTAL_TICKS + 10)
	var hp_in_line_after: float = enemy_in_line.stats.hp
	var hp_lateral_outside_after: float = enemy_lateral_outside.stats.hp
	var hp_beyond_range_after: float = enemy_beyond_range.stats.hp

	var creature_finished: bool = await _wait_until(func(): return spawned and not is_instance_valid(creature), SerpentCreux.TOTAL_TICKS + 15)
	var action_unlocked_after: bool = await _wait_until(func(): return not _player._action_lock, 10)
	var cooldown_armed_after_cast: bool = _player._serpent_creux_cooldown_remaining > 0

	Input.action_press("power5")
	await get_tree().physics_frame
	Input.action_release("power5")
	var creature_count_after_cooldown_press := 0
	for child in get_children():
		if child is SerpentCreux:
			creature_count_after_cooldown_press += 1

	_checks.append({
		"name": "serpent_creux_input_spawns_creature_and_plays_dedicated_gesture",
		"pass": spawned and anim_during == "invocation_serpent_creux",
		"detail": {"spawned": spawned, "anim": anim_during},
	})
	_checks.append({
		"name": "serpent_creux_hits_enemy_in_line_spares_lateral_outside_and_beyond_range",
		"pass": hit_landed and hp_lateral_outside_after == hp_lateral_outside_before and hp_beyond_range_after == hp_beyond_range_before,
		"detail": {
			"hit_landed": hit_landed,
			"hp_in_line_before": hp_in_line_before, "hp_in_line_after": hp_in_line_after,
			"hp_lateral_outside_before": hp_lateral_outside_before, "hp_lateral_outside_after": hp_lateral_outside_after,
			"hp_beyond_range_before": hp_beyond_range_before, "hp_beyond_range_after": hp_beyond_range_after,
		},
	})
	_checks.append({
		"name": "serpent_creux_ends_and_unlocks_then_cooldown_blocks_a_new_cast",
		"pass": creature_finished and action_unlocked_after and cooldown_armed_after_cast and creature_count_after_cooldown_press == 1,
		"detail": {
			"creature_finished": creature_finished, "action_unlocked_after": action_unlocked_after,
			"cooldown_armed_after_cast": cooldown_armed_after_cast,
			"creature_count_after_cooldown_press": creature_count_after_cooldown_press,
		},
	})

	enemy_in_line.queue_free()
	enemy_lateral_outside.queue_free()
	enemy_beyond_range.queue_free()
	await get_tree().physics_frame


## MANDAT PLAN DE PRODUCTION, Chantier A — agent Monstrification, les 3
## compétences restantes (Mâchoire T3, Forme Bestiale T4, Pattes de Chasse
## T5). Mâchoire — même construction que _check_bras_faux()/
## _check_poing_belluaire() ci-dessus (archétype "melee_impact", slot3 =
## tier3 de monstrification.json).
func _check_machoire() -> void:
	await _wait_until(func(): return not _player._action_lock, Player.MACHOIRE_RECOVERY_TICKS + 5)

	RunState.active_power = "monstrification"
	_player.stats.level = 6  # palier de Mâchoire (tier 3, unlock_level 6)

	_player.global_position = Vector2(200, 2600)
	_player.velocity = Vector2.ZERO
	_player.facing = Vector2.RIGHT
	var sprite: AnimatedSprite2D = _player.get_node("AnimatedSprite2D")

	var enemy_front := EnemyScene.instantiate()
	enemy_front.name = "MachoireFront"
	enemy_front.global_position = _player.global_position + Vector2(30, 0)  # 0° — dans l'arc
	add_child(enemy_front)

	var enemy_side := EnemyScene.instantiate()
	enemy_side.name = "MachoireSide"
	var side_dir := Vector2.RIGHT.rotated(deg_to_rad(25.0))
	enemy_side.global_position = _player.global_position + side_dir * 30.0  # 25° — dans l'arc (demi-angle 40°)
	add_child(enemy_side)

	var enemy_outside := EnemyScene.instantiate()
	enemy_outside.name = "MachoireOutside"
	var outside_dir := Vector2.RIGHT.rotated(deg_to_rad(90.0))
	enemy_outside.global_position = _player.global_position + outside_dir * 30.0  # 90° — hors arc
	add_child(enemy_outside)

	await get_tree().physics_frame

	var hp_front_before: float = enemy_front.stats.hp
	var hp_side_before: float = enemy_side.stats.hp
	var hp_outside_before: float = enemy_outside.stats.hp

	Input.action_press("power3")
	await get_tree().physics_frame
	Input.action_release("power3")
	var started: bool = await _wait_until(func(): return _player._machoire_phase != Player.MachoirePhase.NONE, 5)
	var anim_during: String = sprite.animation

	await _wait_until(
		func(): return enemy_front.stats.hp < hp_front_before,
		Player.MACHOIRE_ANTICIPATION_TICKS + Player.MACHOIRE_RELEASE_TICKS + 5)
	var hp_front_after: float = enemy_front.stats.hp
	var hp_side_after: float = enemy_side.stats.hp
	var hp_outside_after: float = enemy_outside.stats.hp

	var ended: bool = await _wait_until(
		func(): return _player._machoire_phase == Player.MachoirePhase.NONE, Player.MACHOIRE_RECOVERY_TICKS + 5)
	var action_unlocked_after: bool = not _player._action_lock

	Input.action_press("power3")
	await get_tree().physics_frame
	Input.action_release("power3")
	var machoire_started_during_cooldown: bool = _player._machoire_phase != Player.MachoirePhase.NONE

	_checks.append({
		"name": "machoire_input_starts_state_and_plays_dedicated_anim",
		"pass": started and anim_during == "machoire",
		"detail": {"started": started, "anim": anim_during},
	})
	_checks.append({
		"name": "machoire_hits_all_enemies_in_arc_spares_enemy_outside",
		"pass": hp_front_after < hp_front_before and hp_side_after < hp_side_before and hp_outside_after == hp_outside_before,
		"detail": {
			"hp_front_before": hp_front_before, "hp_front_after": hp_front_after,
			"hp_side_before": hp_side_before, "hp_side_after": hp_side_after,
			"hp_outside_before": hp_outside_before, "hp_outside_after": hp_outside_after,
		},
	})
	_checks.append({
		"name": "machoire_ends_and_unlocks_then_cooldown_blocks_second_cast",
		"pass": ended and action_unlocked_after and not machoire_started_during_cooldown,
		"detail": {
			"ended": ended, "action_unlocked_after": action_unlocked_after,
			"machoire_started_during_cooldown": machoire_started_during_cooldown,
		},
	})

	enemy_front.queue_free()
	enemy_side.queue_free()
	enemy_outside.queue_free()
	await get_tree().physics_frame


## Forme Bestiale — même construction, arc le plus large de la Classe
## (FORME_BESTIALE_HALF_ANGLE_DEG=70°, slot4 = tier4, unlock_level 14).
func _check_forme_bestiale() -> void:
	await _wait_until(func(): return not _player._action_lock, Player.FORME_BESTIALE_RECOVERY_TICKS + 5)

	RunState.active_power = "monstrification"
	_player.stats.level = 14  # palier de Forme Bestiale (tier 4, unlock_level 14)

	_player.global_position = Vector2(200, 2900)
	_player.velocity = Vector2.ZERO
	_player.facing = Vector2.RIGHT
	var sprite: AnimatedSprite2D = _player.get_node("AnimatedSprite2D")

	var enemy_front := EnemyScene.instantiate()
	enemy_front.name = "FormeBestialeFront"
	enemy_front.global_position = _player.global_position + Vector2(40, 0)  # 0° — dans l'arc
	add_child(enemy_front)

	var enemy_wide := EnemyScene.instantiate()
	enemy_wide.name = "FormeBestialeWide"
	var wide_dir := Vector2.RIGHT.rotated(deg_to_rad(60.0))
	enemy_wide.global_position = _player.global_position + wide_dir * 40.0  # 60° — dans l'arc large (demi-angle 70°)
	add_child(enemy_wide)

	var enemy_outside := EnemyScene.instantiate()
	enemy_outside.name = "FormeBestialeOutside"
	var outside_dir := Vector2.RIGHT.rotated(deg_to_rad(150.0))
	enemy_outside.global_position = _player.global_position + outside_dir * 40.0  # 150° — hors arc même large
	add_child(enemy_outside)

	await get_tree().physics_frame

	var hp_front_before: float = enemy_front.stats.hp
	var hp_wide_before: float = enemy_wide.stats.hp
	var hp_outside_before: float = enemy_outside.stats.hp

	Input.action_press("power4")
	await get_tree().physics_frame
	Input.action_release("power4")
	var started: bool = await _wait_until(func(): return _player._forme_bestiale_phase != Player.FormeBestialePhase.NONE, 5)
	var anim_during: String = sprite.animation

	await _wait_until(
		func(): return enemy_front.stats.hp < hp_front_before,
		Player.FORME_BESTIALE_ANTICIPATION_TICKS + Player.FORME_BESTIALE_RELEASE_TICKS + 5)
	var hp_front_after: float = enemy_front.stats.hp
	var hp_wide_after: float = enemy_wide.stats.hp
	var hp_outside_after: float = enemy_outside.stats.hp

	var ended: bool = await _wait_until(
		func(): return _player._forme_bestiale_phase == Player.FormeBestialePhase.NONE,
		Player.FORME_BESTIALE_RELEASE_TICKS + Player.FORME_BESTIALE_RECOVERY_TICKS + 5)
	var action_unlocked_after: bool = not _player._action_lock

	Input.action_press("power4")
	await get_tree().physics_frame
	Input.action_release("power4")
	var forme_bestiale_started_during_cooldown: bool = _player._forme_bestiale_phase != Player.FormeBestialePhase.NONE

	_checks.append({
		"name": "forme_bestiale_input_starts_state_and_plays_dedicated_anim",
		"pass": started and anim_during == "forme_bestiale",
		"detail": {"started": started, "anim": anim_during},
	})
	_checks.append({
		"name": "forme_bestiale_hits_all_enemies_in_wide_arc_spares_enemy_outside",
		"pass": hp_front_after < hp_front_before and hp_wide_after < hp_wide_before and hp_outside_after == hp_outside_before,
		"detail": {
			"hp_front_before": hp_front_before, "hp_front_after": hp_front_after,
			"hp_wide_before": hp_wide_before, "hp_wide_after": hp_wide_after,
			"hp_outside_before": hp_outside_before, "hp_outside_after": hp_outside_after,
		},
	})
	_checks.append({
		"name": "forme_bestiale_ends_and_unlocks_then_cooldown_blocks_second_cast",
		"pass": ended and action_unlocked_after and not forme_bestiale_started_during_cooldown,
		"detail": {
			"ended": ended, "action_unlocked_after": action_unlocked_after,
			"forme_bestiale_started_during_cooldown": forme_bestiale_started_during_cooldown,
		},
	})

	enemy_front.queue_free()
	enemy_wide.queue_free()
	enemy_outside.queue_free()
	await get_tree().physics_frame


## Pattes de Chasse — SEUL pouvoir de Monstrification avec un déplacement
## automatique (voir Player.PATTES_DE_CHASSE_* / _advance_pattes_de_chasse()) :
## vérifie à la fois le déplacement (comme _check_dash()) ET le jet de
## dégâts en ligne au tick de frappe (comme _check_maree_de_sable(), mais
## Targeting.enemies_in_line() depuis la position ATTEINTE au tick de
## frappe, pas la position de départ — slot5 = tier5, unlock_level 18).
func _check_pattes_de_chasse() -> void:
	await _wait_until(func(): return not _player._action_lock, Player.PATTES_DE_CHASSE_RECOVERY_TICKS + 5)

	RunState.active_power = "monstrification"
	_player.stats.level = 18  # palier de Pattes de Chasse (tier 5, unlock_level 18)

	_player.global_position = Vector2(200, 3200)
	_player.velocity = Vector2.ZERO
	_player.facing = Vector2.RIGHT
	var sprite: AnimatedSprite2D = _player.get_node("AnimatedSprite2D")
	var pos_before: Vector2 = _player.global_position

	# Position atteinte au tick de frappe ≈ pos_before + DISTANCE * (STRIKE_TICK/MOVE_TICKS)
	# (progression ease-out, donc une sous-estimation prudente — placé bien
	# en-deça pour rester robuste à la courbe réelle).
	var strike_progress_estimate: float = float(Player.PATTES_DE_CHASSE_STRIKE_TICK) / float(Player.PATTES_DE_CHASSE_MOVE_TICKS)
	var strike_x_estimate: float = pos_before.x + Player.PATTES_DE_CHASSE_DISTANCE_PX * strike_progress_estimate

	var enemy_in_line := EnemyScene.instantiate()
	enemy_in_line.name = "PattesDeChasseInLine"
	enemy_in_line.global_position = Vector2(strike_x_estimate + 10.0, pos_before.y)  # devant la position de frappe, dans la bande
	add_child(enemy_in_line)

	var enemy_lateral_outside := EnemyScene.instantiate()
	enemy_lateral_outside.name = "PattesDeChasseLateralOutside"
	enemy_lateral_outside.global_position = Vector2(strike_x_estimate + 10.0, pos_before.y + 40.0)  # lateral 40 > half_width 18
	add_child(enemy_lateral_outside)

	await get_tree().physics_frame

	var hp_in_line_before: float = enemy_in_line.stats.hp
	var hp_lateral_outside_before: float = enemy_lateral_outside.stats.hp

	Input.action_press("power5")
	await get_tree().physics_frame
	Input.action_release("power5")
	var started: bool = await _wait_until(func(): return _player._pattes_de_chasse_phase != Player.PattesDeChassePhase.NONE, 5)
	var anim_during: String = sprite.animation

	var moved_during_move: bool = await _wait_until(
		func(): return _player._pattes_de_chasse_phase == Player.PattesDeChassePhase.MOVE and _player.global_position.x > pos_before.x + 5.0,
		Player.PATTES_DE_CHASSE_ANTICIPATION_TICKS + 5)

	var hit_landed: bool = await _wait_until(
		func(): return enemy_in_line.stats.hp < hp_in_line_before,
		Player.PATTES_DE_CHASSE_ANTICIPATION_TICKS + Player.PATTES_DE_CHASSE_MOVE_TICKS + 5)
	var hp_in_line_after: float = enemy_in_line.stats.hp
	var hp_lateral_outside_after: float = enemy_lateral_outside.stats.hp

	var ended: bool = await _wait_until(
		func(): return _player._pattes_de_chasse_phase == Player.PattesDeChassePhase.NONE,
		Player.PATTES_DE_CHASSE_MOVE_TICKS + Player.PATTES_DE_CHASSE_RECOVERY_TICKS + 5)
	var pos_after: Vector2 = _player.global_position
	var action_unlocked_after: bool = not _player._action_lock
	var displaced_forward: bool = pos_after.x > pos_before.x + Player.PATTES_DE_CHASSE_DISTANCE_PX * 0.5

	Input.action_press("power5")
	await get_tree().physics_frame
	Input.action_release("power5")
	var pattes_de_chasse_started_during_cooldown: bool = _player._pattes_de_chasse_phase != Player.PattesDeChassePhase.NONE

	_checks.append({
		"name": "pattes_de_chasse_input_starts_state_and_plays_dedicated_anim",
		"pass": started and anim_during == "pattes_de_chasse",
		"detail": {"started": started, "anim": anim_during},
	})
	_checks.append({
		"name": "pattes_de_chasse_moves_player_forward_during_move_phase",
		"pass": moved_during_move,
		"detail": {"moved_during_move": moved_during_move},
	})
	_checks.append({
		"name": "pattes_de_chasse_hits_enemy_in_line_spares_lateral_outside",
		"pass": hit_landed and hp_in_line_after < hp_in_line_before and hp_lateral_outside_after == hp_lateral_outside_before,
		"detail": {
			"hit_landed": hit_landed,
			"hp_in_line_before": hp_in_line_before, "hp_in_line_after": hp_in_line_after,
			"hp_lateral_outside_before": hp_lateral_outside_before, "hp_lateral_outside_after": hp_lateral_outside_after,
		},
	})
	_checks.append({
		"name": "pattes_de_chasse_ends_displaced_and_unlocks_then_cooldown_blocks_second_cast",
		"pass": ended and displaced_forward and action_unlocked_after and not pattes_de_chasse_started_during_cooldown,
		"detail": {
			"ended": ended, "pos_before": pos_before, "pos_after": pos_after,
			"displaced_forward": displaced_forward, "action_unlocked_after": action_unlocked_after,
			"pattes_de_chasse_started_during_cooldown": pattes_de_chasse_started_during_cooldown,
		},
	})

	enemy_in_line.queue_free()
	enemy_lateral_outside.queue_free()
	await get_tree().physics_frame


## MANDAT "fluidité" (Partie 2, couche code) — généralisation du buffer
## d'input + fenêtre d'annulation aux 5 compétences dédiées
## (Player._try_activate_power_slot()/_queued_power_slot/
## _try_consume_queued_input()). Scénario : le joueur presse Bras-Faux
## (power2, tier2 Monstrification), PUIS presse Poing Belluaire (power1,
## tier1 Monstrification) alors qu'il est encore verrouillé dans Bras-Faux
## — AVANT ce mandat, ce second appui était perdu en silence
## (`_start_poing_belluaire()` retournait tôt sur `_action_lock`). Vérifie
## trois choses : (1) l'appui ne démarre RIEN tant que la fenêtre
## d'annulation de Bras-Faux (BRAS_FAUX_CANCEL_WINDOW_TICKS) n'est pas
## ouverte — pas de déclenchement immédiat, pas un bug de double-input ;
## (2) dès que cette fenêtre s'ouvre, Poing Belluaire démarre tout SEUL
## (sans second appui) et Bras-Faux se termine PLUS TÔT que sa RECOVERY
## complète (22 ticks) — "se déclenche dès que possible" ; (3) Bras-Faux
## paie quand même son cooldown, comme une fin normale.
func _check_input_buffer_fires_at_cancel_window() -> void:
	await _wait_until(func(): return not _player._action_lock, 60)

	RunState.active_power = "monstrification"
	_player.stats.level = 3  # débloque poing_belluaire (tier1) ET bras_faux (tier2)
	# Les DEUX compétences ont déjà été exercées par leurs propres checks
	# plus haut (_check_bras_faux()/_check_poing_belluaire()) — reset direct
	# des cooldowns plutôt que de compter sur le nombre de ticks écoulés
	# depuis (fragile, dépendrait de l'ordre/durée des checks intercalés).
	_player._bras_faux_cooldown_remaining = 0
	_player._poing_belluaire_cooldown_remaining = 0

	_player.global_position = Vector2(200, 2500)
	_player.velocity = Vector2.ZERO
	_player.facing = Vector2.RIGHT

	Input.action_press("power2")
	await get_tree().physics_frame
	Input.action_release("power2")
	var bras_faux_started: bool = await _wait_until(
		func(): return _player._bras_faux_phase != Player.BrasFauxPhase.NONE, 5)

	# RECOVERY-relatif : tick d'ouverture de la fenêtre d'annulation.
	var cancel_window_start: int = Player.BRAS_FAUX_RECOVERY_TICKS - Player.BRAS_FAUX_CANCEL_WINDOW_TICKS

	# Attend d'être 3 ticks (RELATIFS à RECOVERY) avant l'ouverture — via le
	# compteur AUTORITATIF `_bras_faux_tick`, jamais un compte d'`await`
	# manuel (l'ordre entre la reprise d'un `await physics_frame` et le
	# `_physics_process` d'un nœud n'est pas garanti au tick près, même
	# réserve documentée ailleurs dans ce fichier) — largement à
	# l'intérieur d'INPUT_BUFFER_TICKS (10) pour que le buffer survive
	# jusqu'à l'ouverture.
	await _wait_until(
		func(): return (_player._bras_faux_phase == Player.BrasFauxPhase.RECOVERY
			and _player._bras_faux_tick >= cancel_window_start - 3),
		Player.BRAS_FAUX_ANTICIPATION_TICKS + Player.BRAS_FAUX_RELEASE_TICKS + cancel_window_start + 5)

	Input.action_press("power1")
	await get_tree().physics_frame
	Input.action_release("power1")
	var queued_immediately: bool = await _wait_until(func(): return _player._queued_power_slot == 1, 3)

	# Toujours strictement AVANT l'ouverture (tick relatif < cancel_window_start) :
	# rien ne doit encore avoir démarré — preuve que c'est la fenêtre
	# d'annulation qui gate le déclenchement, pas juste "le prochain input
	# marche tout de suite".
	var still_locked_in_bras_faux: bool = _player._bras_faux_phase == Player.BrasFauxPhase.RECOVERY \
		and _player._bras_faux_tick < cancel_window_start \
		and _player._poing_belluaire_phase == Player.PoingBelluairePhase.NONE

	# Ouverture de la fenêtre d'annulation : Poing Belluaire doit démarrer
	# TOUT SEUL (aucun second appui n'a été envoyé depuis "power1" ci-dessus).
	var poing_belluaire_started: bool = await _wait_until(
		func(): return _player._poing_belluaire_phase != Player.PoingBelluairePhase.NONE, 8)
	var bras_faux_ended: bool = _player._bras_faux_phase == Player.BrasFauxPhase.NONE
	var bras_faux_paid_cooldown: bool = _player._bras_faux_cooldown_remaining > 0
	var queue_cleared_after_fire: bool = _player._queued_power_slot == 0

	# Laisse Poing Belluaire terminer naturellement depuis SON tout début
	# (ANTICIPATION+RELEASE+RECOVERY, pas juste RECOVERY : contrairement à
	# _check_poing_belluaire() qui démarre son attente une fois déjà en
	# RELEASE/RECOVERY, ici l'attente commence dès le tout premier tick) —
	# vérifie que la transition n'a rien corrompu (pas de verrou fantôme).
	var poing_belluaire_ended: bool = await _wait_until(
		func(): return _player._poing_belluaire_phase == Player.PoingBelluairePhase.NONE,
		Player.POING_BELLUAIRE_ANTICIPATION_TICKS + Player.POING_BELLUAIRE_RELEASE_TICKS
			+ Player.POING_BELLUAIRE_RECOVERY_TICKS + 12)
	var action_unlocked_after: bool = not _player._action_lock

	_checks.append({
		"name": "queued_power_does_not_fire_before_cancel_window_opens",
		"pass": bras_faux_started and queued_immediately and still_locked_in_bras_faux,
		"detail": {
			"bras_faux_started": bras_faux_started, "queued_immediately": queued_immediately,
			"still_locked_in_bras_faux": still_locked_in_bras_faux,
		},
	})
	_checks.append({
		"name": "queued_power_fires_on_its_own_when_cancel_window_opens_and_ends_current_action_early",
		"pass": poing_belluaire_started and bras_faux_ended and bras_faux_paid_cooldown and queue_cleared_after_fire,
		"detail": {
			"poing_belluaire_started": poing_belluaire_started, "bras_faux_ended": bras_faux_ended,
			"bras_faux_paid_cooldown": bras_faux_paid_cooldown, "queue_cleared_after_fire": queue_cleared_after_fire,
		},
	})
	_checks.append({
		"name": "power_fired_from_cancel_window_still_completes_and_unlocks_normally",
		"pass": poing_belluaire_ended and action_unlocked_after,
		"detail": {"poing_belluaire_ended": poing_belluaire_ended, "action_unlocked_after": action_unlocked_after},
	})


## Même mandat que ci-dessus — vérifie l'autre moitié du contrat : le
## buffer est une fenêtre COURTE (INPUT_BUFFER_TICKS), pas une file
## d'attente illimitée. Presse Marée de Sable (power2, tier2 Terre) tout
## au DÉBUT de l'anticipation de Poing Tellurique (power1, tier1 Terre,
## fenêtre d'annulation ouverte seulement au tick relatif 8 de sa RECOVERY,
## bien après l'expiration du buffer) — l'input doit avoir expiré avant que
## la fenêtre d'annulation ne s'ouvre, donc Poing Tellurique va au bout de
## sa RECOVERY complète et Marée de Sable ne démarre jamais tout seul.
func _check_input_buffer_expires_when_never_consumed() -> void:
	await _wait_until(func(): return not _player._action_lock, 60)

	RunState.active_power = "terre"
	_player.stats.level = 3  # débloque poing_tellurique (tier1) ET maree_de_sable (tier2)
	# Même précaution que _check_input_buffer_fires_at_cancel_window() —
	# les deux ont déjà été exercées par leurs propres checks plus haut.
	_player._poing_tellurique_cooldown_remaining = 0
	_player._maree_de_sable_cooldown_remaining = 0

	_player.global_position = Vector2(200, 2500)
	_player.velocity = Vector2.ZERO
	_player.facing = Vector2.RIGHT

	Input.action_press("power1")
	await get_tree().physics_frame
	Input.action_release("power1")
	var poing_tellurique_started: bool = await _wait_until(
		func(): return _player._poing_tellurique_phase != Player.PoingTelluriquePhase.NONE, 5)

	# Appui TRÈS tôt (tick ~2 d'ANTICIPATION, qui dure 18 ticks) — beaucoup
	# plus tôt que INPUT_BUFFER_TICKS (10) avant l'ouverture de la fenêtre
	# d'annulation (tick relatif 8 de RECOVERY, soit tick absolu 18+4+8=30).
	Input.action_press("power2")
	await get_tree().physics_frame
	Input.action_release("power2")
	var queued_right_after_press: bool = await _wait_until(func(): return _player._queued_power_slot == 2, 3)

	# Attend au-delà d'INPUT_BUFFER_TICKS (10) depuis l'appui ci-dessus —
	# le buffer doit avoir expiré tout seul, sans jamais avoir été consommé.
	var expired: bool = await _wait_until(func(): return _player._queued_power_slot == 0, Player.INPUT_BUFFER_TICKS + 3)

	# Poing Tellurique doit continuer sa RECOVERY NORMALEMENT (rien à
	# annuler puisque le buffer a expiré) jusqu'à sa fin NATURELLE complète.
	var ended_naturally: bool = await _wait_until(
		func(): return _player._poing_tellurique_phase == Player.PoingTelluriquePhase.NONE,
		Player.POING_TELLURIQUE_ANTICIPATION_TICKS + Player.POING_TELLURIQUE_RELEASE_TICKS
			+ Player.POING_TELLURIQUE_RECOVERY_TICKS + 10)
	var maree_de_sable_never_started: bool = _player._maree_de_sable_phase == Player.MareeDeSablePhase.NONE
	var action_unlocked_after: bool = not _player._action_lock

	_checks.append({
		"name": "queued_power_input_expires_after_input_buffer_ticks_if_never_consumed",
		"pass": poing_tellurique_started and queued_right_after_press and expired,
		"detail": {
			"poing_tellurique_started": poing_tellurique_started,
			"queued_right_after_press": queued_right_after_press, "expired": expired,
		},
	})
	_checks.append({
		"name": "expired_buffer_lets_current_action_run_its_full_recovery_uninterrupted",
		"pass": ended_naturally and action_unlocked_after and maree_de_sable_never_started,
		"detail": {
			"ended_naturally": ended_naturally, "action_unlocked_after": action_unlocked_after,
			"maree_de_sable_never_started": maree_de_sable_never_started,
		},
	})


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


## MANDAT PLAYTEST RÉEL (retour Milan, build web déployé, 2026-08-26) : "les 3
## monstres restent TOUS orientés dans la même direction en jeu réel — ils
## devraient se tourner vers le joueur ou vers leur direction de déplacement,
## mais ne le font jamais." Reproduction en conditions de jeu réelles (pas une
## capture isolée à un instant T, comme exigé par le mandat) : chacun des 3
## archétypes (Crawler/Brute/Ranged — "les 3 monstres", pas seulement un
## échantillon) chassé successivement vers +x PUIS vers -x (le joueur déplacé
## de l'autre côté en cours de route, comme un joueur qui contourne le
## monstre) doit voir son `Visual.flip_h` suivre le signe de sa vitesse RÉELLE
## de poursuite dans les DEUX cas, pas seulement au premier contact — sinon
## `_update_visual_bob()` (src/gameplay/enemy.gd, PARTAGÉE par les 3 scènes
## d'archétype) ne fait illusion qu'une fois puis se fige, ce qu'une capture à
## un seul instant ne peut pas distinguer d'un comportement correct.
##
## `offset_px` par archétype : > `attack_range_px` (jamais un contact
## immédiat, sinon le monstre irait direct en TELEGRAPH sans jamais bouger
## visuellement) ET assez sous `aggro_radius_px` pour absorber le
## déplacement du monstre DURANT `wait_ticks` sans jamais en sortir (RANGED :
## aussi > preferred_range_px+range_tolerance_px, sinon il resterait immobile
## dans sa bande de tolérance au lieu de vraiment chasser/s'orienter).
func _check_enemy_faces_chase_direction_in_multiple_directions() -> void:
	var configs: Array[Dictionary] = [
		{"name": "crawler", "scene": EnemyCrawlerScene, "offset_px": 200.0, "wait_ticks": 30},
		{"name": "brute", "scene": EnemyBruteScene, "offset_px": 150.0, "wait_ticks": 40},
		{"name": "ranged", "scene": EnemyRangedScene, "offset_px": 210.0, "wait_ticks": 30},
	]
	var per_monster: Dictionary = {}
	var all_pass := true

	for cfg in configs:
		var enemy: Enemy = cfg["scene"].instantiate()
		enemy.name = "FacingCheck_%s" % cfg["name"]
		enemy.global_position = Vector2(1200, 1200)  # zone isolée, aucun autre check n'y pose rien
		add_child(enemy)
		await get_tree().physics_frame

		var sprite: AnimatedSprite2D = enemy.get_node("Visual")
		var offset_px: float = cfg["offset_px"]
		var wait_ticks: int = cfg["wait_ticks"]

		# --- Poursuite vers +x (joueur posé à droite) ---
		_player.global_position = enemy.global_position + Vector2(offset_px, 0)
		var chasing_right: bool = await _wait_until(
			func(): return enemy._state == Enemy.State.CHASE and enemy.velocity.x > 0.0, 60)
		# Quelques ticks de plus : _update_visual_bob() tourne APRÈS _run_ai()
		# dans le même _physics_process, laisser une marge pour que flip_h se
		# soit bien mis à jour avant de le lire.
		for i in range(wait_ticks):
			await get_tree().physics_frame
		var flip_while_chasing_right: bool = sprite.flip_h

		# --- Le joueur contourne le monstre : posé à gauche de la position
		# COURANTE (déjà avancée vers +x ci-dessus, jamais la position de
		# départ figée — sinon `offset_px` cumulé à la distance déjà
		# parcourue risquerait de dépasser `aggro_radius_px` et de faire
		# retomber le monstre en IDLE au lieu de renverser son cap) — le
		# monstre doit inverser son cap ET son orientation, pas rester figé
		# sur flip_h du premier passage. ---
		_player.global_position = enemy.global_position + Vector2(-offset_px, 0)
		var chasing_left: bool = await _wait_until(
			func(): return enemy._state == Enemy.State.CHASE and enemy.velocity.x < 0.0, 60)
		for i in range(wait_ticks):
			await get_tree().physics_frame
		var flip_while_chasing_left: bool = sprite.flip_h

		var this_pass: bool = chasing_right and not flip_while_chasing_right and chasing_left and flip_while_chasing_left
		all_pass = all_pass and this_pass
		per_monster[cfg["name"]] = {
			"pass": this_pass,
			"chasing_right": chasing_right, "flip_while_chasing_right": flip_while_chasing_right,
			"chasing_left": chasing_left, "flip_while_chasing_left": flip_while_chasing_left,
		}
		enemy.queue_free()
		await get_tree().physics_frame

	_checks.append({
		"name": "enemy_flips_to_face_actual_chase_direction_both_ways",
		"pass": all_pass,
		"detail": per_monster,
	})


## CHANTIER C (production v1, "Monstres : animations d'interaction") —
## 4 directions minimum : latéral (droite non-flippé/gauche flippé, une
## seule pose "touche_lateral" en miroir — même convention que le flip_h
## déjà utilisé pour le déplacement) + avant/arrière (2 poses distinctes).
## Une instance FRAÎCHE de Crawler par direction (jamais la même,
## évite toute contamination de _consecutive_hits/_stagger_* entre les
## 4 mesures — même discipline d'isolation que les autres checks
## d'ennemis de ce fichier).
func _check_enemy_directional_hit_reaction() -> void:
	var results: Dictionary = {}
	var offsets: Dictionary = {
		"right": Vector2(50, 0), "left": Vector2(-50, 0),
		"front": Vector2(0, 50), "back": Vector2(0, -50),
	}
	for dir_name in offsets.keys():
		var crawler := EnemyCrawlerScene.instantiate()
		crawler.name = "CrawlerDir_%s" % dir_name
		crawler.global_position = Vector2(700, 700)
		add_child(crawler)
		await get_tree().physics_frame
		var sprite: AnimatedSprite2D = crawler.get_node("Visual")
		crawler.take_damage(5.0, crawler.global_position + offsets[dir_name])
		results[dir_name] = {"anim": str(sprite.animation), "flip_h": sprite.flip_h}
		crawler.queue_free()
		await get_tree().physics_frame

	var pass_directional: bool = (
		results["right"]["anim"] == "touche_lateral" and not results["right"]["flip_h"]
		and results["left"]["anim"] == "touche_lateral" and results["left"]["flip_h"]
		and results["front"]["anim"] == "touche_avant"
		and results["back"]["anim"] == "touche_arriere"
	)
	_checks.append({
		"name": "crawler_hit_reaction_differs_by_incoming_direction",
		"pass": pass_directional,
		"detail": results,
	})


## Chancellement (enchaînement de coups) : STAGGER_TRIGGER_HITS (3) coups
## dans STAGGER_WINDOW_TICKS n'arment PAS le chancellement avant le 3e
## (2 coups seuls = simple encaissement répété, pas encore un
## "enchaînement"), puis la pose "chancelle" doit effectivement jouer une
## fois le recul du 3e coup écoulé — Brute (lourd, sans "projete") choisi
## ici pour vérifier que le chancellement ne dépend PAS de la présence de
## la pose de projection (mécanisme générique aux 3 archétypes).
func _check_enemy_stagger_on_consecutive_hits() -> void:
	var brute := EnemyBruteScene.instantiate()
	brute.name = "BruteStagger"
	brute.global_position = Vector2(750, 750)
	add_child(brute)
	await get_tree().physics_frame
	var sprite: AnimatedSprite2D = brute.get_node("Visual")
	var source: Vector2 = brute.global_position + Vector2(50, 0)

	brute.take_damage(5.0, source)
	await get_tree().physics_frame
	brute.take_damage(5.0, source)
	var stagger_armed_after_two: bool = brute._stagger_total_ticks > 0
	brute.take_damage(5.0, source)
	var stagger_armed_after_three: bool = brute._stagger_total_ticks > 0

	var chancelle_played: bool = await _wait_until(func(): return sprite.animation == &"chancelle", 20)

	brute.queue_free()
	await get_tree().physics_frame
	_checks.append({
		"name": "brute_staggers_after_three_consecutive_hits_in_window_not_before",
		"pass": (not stagger_armed_after_two) and stagger_armed_after_three and chancelle_played,
		"detail": {
			"stagger_armed_after_two": stagger_armed_after_two,
			"stagger_armed_after_three": stagger_armed_after_three,
			"chancelle_played": chancelle_played,
		},
	})


## Réaction différenciée par poids (GDD Chantier C : "le Brute encaisse
## sans bouger, le Crawler est projeté" — recoil_multiplier existait déjà
## en code, cette passe n'ajoute QUE l'animation). Crawler (léger,
## recoil_multiplier=1.6, a la pose "projete") doit traverser un état
## "projete" puis un rebond procédural, et finir déplacé nettement plus
## loin que Brute (lourd, recoil_multiplier=0.35, PAS de pose "projete"
## dans son SpriteFrames — donc jamais de rebond non plus, cf.
## _pending_projection dans enemy.gd).
func _check_weight_differentiates_projection_vs_planted() -> void:
	var crawler := EnemyCrawlerScene.instantiate()
	crawler.name = "CrawlerProjection"
	crawler.global_position = Vector2(800, 800)
	add_child(crawler)
	await get_tree().physics_frame
	var crawler_sprite: AnimatedSprite2D = crawler.get_node("Visual")
	var crawler_pos_before: Vector2 = crawler.global_position
	crawler.take_damage(5.0, crawler_pos_before + Vector2(-50, 0))
	var saw_projete: bool = await _wait_until(func(): return crawler_sprite.animation == &"projete", 10)
	await _wait_until(func(): return crawler._recoil_tick >= crawler._recoil_total_ticks and crawler._bounce_total_ticks > 0, 20)
	var crawler_bounced: bool = crawler._bounce_total_ticks > 0
	await _wait_until(func(): return crawler._bounce_tick >= crawler._bounce_total_ticks, 20)
	var crawler_displacement: float = crawler_pos_before.distance_to(crawler.global_position)
	crawler.queue_free()
	await get_tree().physics_frame

	var brute := EnemyBruteScene.instantiate()
	brute.name = "BruteNoProjection"
	brute.global_position = Vector2(850, 800)
	add_child(brute)
	await get_tree().physics_frame
	var brute_sprite: AnimatedSprite2D = brute.get_node("Visual")
	var brute_has_projete_anim: bool = brute_sprite.sprite_frames.has_animation("projete")
	var brute_pos_before: Vector2 = brute.global_position
	brute.take_damage(5.0, brute_pos_before + Vector2(-50, 0))
	await _wait_until(func(): return brute._recoil_tick >= brute._recoil_total_ticks, 20)
	var brute_displacement: float = brute_pos_before.distance_to(brute.global_position)
	var brute_bounce_total: int = brute._bounce_total_ticks
	brute.queue_free()
	await get_tree().physics_frame

	_checks.append({
		"name": "crawler_is_projected_and_bounces_brute_stays_planted",
		"pass": (
			saw_projete and crawler_bounced and not brute_has_projete_anim
			and brute_bounce_total == 0 and crawler_displacement > brute_displacement * 2.0
		),
		"detail": {
			"saw_projete": saw_projete, "crawler_bounced": crawler_bounced,
			"crawler_displacement_px": crawler_displacement, "brute_displacement_px": brute_displacement,
			"brute_has_projete_anim": brute_has_projete_anim, "brute_bounce_total": brute_bounce_total,
		},
	})


## MANDAT DÉDIÉ RECUL RÉEL (Milan, playtest build web, 2026-08-26) : "les
## monstres ne sont pas repoussés en jeu réel, le joueur ne peut jamais
## créer de distance, se fait enchaîner." Le check ci-dessus
## (`_check_weight_differentiates_projection_vs_planted`) et les autres
## checks recul de ce fichier (`combo_hit_applies_recoil_to_enemy`,
## `gueule_vide_contact_applies_recoil_to_enemy`) NE PEUVENT PAS attraper
## ce bug : ils posent l'ennemi hors d'aggro ou lisent `enemy.tscn`
## générique (`aggro_radius_px = 0.0`), donc `_run_ai()` n'y relance
## JAMAIS de CHASE après le recul. Ce check pose au contraire un Crawler
## en poursuite active RÉELLE (hors de SON PROPRE attack_range_px, donc
## en CHASE à vitesse pleine) au moment précis où le joueur riposte —
## reproduction en conditions de combat réel, pas une capture isolée à un
## instant T.
##
## Root cause (confirmée par reproduction AVANT ce fix, cf. docs/
## worklog.md) : le recul déplaçait déjà bien `global_position` (aucun
## bug côté `_recoil_tick`/`take_damage()` eux-mêmes), mais rien
## n'empêchait `_run_ai()` de relancer la CHASE à pleine vitesse
## (`move_speed_px`) DÈS le tick suivant la fin du recul — un Crawler
## (150px/s) refermait en 2-3 ticks les quelques px qu'un coup de tier1
## (4px × recoil_multiplier) venait de créer, invisible à l'écran. Fixé
## en armant `State.RECOVER` dans `Enemy.take_damage()` (voir enemy.gd) :
## même principe que `Player._action_lock`/`_hurt_phase`
## (`_advance_hurt()`), qui bloque déjà tout mouvement volontaire du
## joueur pendant SON propre recul — ici appliqué à la PROPRE IA de
## l'ennemi.
##
## N'utilise AUCUN chiffre codé en dur pour la fenêtre de tenue : dérivé
## de `_recoil_total_ticks`/`attack_recover_ticks` (déjà exportés/tunés
## par archétype), pour ne jamais désynchroniser ce check d'un futur
## retuning de ces valeurs.
func _check_enemy_recoil_holds_real_separation_during_active_chase() -> void:
	await _wait_until(func(): return not _player._action_lock, 60)
	_player.global_position = Vector2(200, 2300)
	_player.velocity = Vector2.ZERO
	_player.stats.hp = 100.0
	# Déterminisme (même discipline que _ready()) : un critique roulé ici
	# ne changerait pas le recul (dérivé du tier, pas du critique), mais
	# éviter toute variance non seedée superflue sur ce check précis.
	_player._combo_crit_chance_percent = 0.0

	var crawler := EnemyCrawlerScene.instantiate()
	crawler.name = "CrawlerRecoilHold"
	# 60px : hors de son propre attack_range_px (28px) — il CHASE donc
	# activement, à vraie vitesse, PAS un mannequin immobile — mais assez
	# près pour entrer dans l'ATTACK_RANGE_PX (48px) du joueur en
	# quelques ticks de fermeture, comme un vrai corps-à-corps.
	crawler.global_position = _player.global_position + Vector2(60, 0)
	add_child(crawler)
	await get_tree().physics_frame

	var chasing: bool = await _wait_until(func(): return crawler._state == Enemy.State.CHASE, 60)

	var hp_before: float = crawler.stats.hp
	Input.action_press("attack")
	await get_tree().physics_frame
	Input.action_release("attack")
	var hit_landed: bool = await _wait_until(func(): return crawler.stats.hp < hp_before, 30)
	var dist_at_hit: float = _player.global_position.distance_to(crawler.global_position)

	# Fenêtre garantie sans reprise de poursuite (recul + State.RECOVER,
	# armés ensemble par take_damage()) — mesurée 2 ticks AVANT sa fin
	# théorique (marge pour l'arrondi ease-out et un éventuel hit-stop
	# résiduel), jamais après : au-delà, on mesurerait la reprise de
	# CHASE elle-même, pas la tenue du recul.
	var hold_ticks: int = maxi(1, crawler._recoil_total_ticks + crawler.attack_recover_ticks - 2)
	for i in range(hold_ticks):
		await get_tree().physics_frame
	var dist_during_hold: float = _player.global_position.distance_to(crawler.global_position)

	# Garde-fou symétrique : l'IA doit bien reprendre APRÈS cette fenêtre
	# (pas un blocage permanent) — un recul qui "tient" pour toujours
	# serait un bug tout aussi faux que celui corrigé ici.
	var resumed_chase: bool = await _wait_until(
		func(): return (
			crawler._state == Enemy.State.CHASE
			and _player.global_position.distance_to(crawler.global_position) < dist_during_hold - 1.0),
		60)

	_checks.append({
		"name": "enemy_recoil_holds_real_separation_during_active_chase_then_resumes",
		"pass": chasing and hit_landed and dist_during_hold >= dist_at_hit - 0.5 and resumed_chase,
		"detail": {
			"chasing": chasing, "hit_landed": hit_landed,
			"dist_at_hit": dist_at_hit, "dist_during_hold": dist_during_hold,
			"hold_ticks": hold_ticks, "resumed_chase": resumed_chase,
		},
	})
	crawler.queue_free()
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


## MANDAT "retours de playtest réel" (point 1, PRIORITÉ ABSOLUE) — softlock
## confirmé par Milan en jeu réel : `die()` verrouillait tout et rien nulle
## part ne permettait d'en sortir (aucun new_run()/restart() dans tout le
## dépôt). DERNIER check de toute la suite, volontairement : au-delà du
## seuil, un appui "attack" appelle pour de vrai `RunState.start_new_run()`,
## qui appelle `change_scene_to_file()` — un changement de scène réel qui
## remplace CE nœud de test lui-même. Testé empiriquement (traces de
## debug temporaires, retirées après coup) : `_process_death_restart()`
## se déclenche bien exactement au tick attendu et `RunState.player_stats`
## change bien d'objet — mais AUCUN `await get_tree().physics_frame`
## postérieur à ce tick ne reprend jamais dans ce fichier (le nœud qui
## attend est celui que `change_scene_to_file()` vient de remplacer) :
## plusieurs variantes testées (lecture immédiate, tick supplémentaire,
## `_wait_until()`) font toutes stagner le process indéfiniment dès que le
## tick déclencheur a réellement eu lieu. Ce dernier check s'arrête donc
## volontairement AVANT le tick qui franchit le seuil — il vérifie tout ce
## qui est observable en toute sécurité depuis ce nœud (verrouillage à la
## mort, délai anti-appui-accidentel) ; le déclenchement réel au-delà du
## seuil est vérifié par lecture directe de `_process_death_restart()`/
## `RunState.start_new_run()` (voir leurs commentaires) plutôt que rejoué
## ici, pour ne pas rendre toute la suite de smoke test fragile à un
## changement de scène réel au milieu de son exécution.
func _check_player_death_restart_flow() -> void:
	var stats_before_death: Stats = _player.stats
	_player.take_damage(999999.0, _player.global_position + Vector2(-10, 0))
	var died_flag: bool = _player.stats.is_dead()
	var anim_after_death: String = _player._sprite.animation
	var action_lock_after_death: bool = _player._action_lock
	var death_ticks_reset: bool = _player._death_ticks == 0

	# Avant le seuil (DEATH_RESTART_INPUT_ENABLED_TICKS - 1 ticks, "attack"
	# tenu à chaque tick) : aucune relance ne doit se déclencher — le délai
	# est volontaire (voir le commentaire de la constante dans player.gd),
	# contre un appui accidentel juste après la mort. S'arrête volontairement
	# UN tick avant le seuil (voir le commentaire de fonction ci-dessus).
	for i in range(Player.DEATH_RESTART_INPUT_ENABLED_TICKS - 1):
		Input.action_press("attack")
		await get_tree().physics_frame
		Input.action_release("attack")

	var scene_unchanged_before_threshold: bool = (
		is_instance_valid(_player) and RunState.player_stats == stats_before_death)

	_checks.append({
		"name": "player_death_locks_action_plays_mort_and_resets_death_ticks",
		"pass": died_flag and anim_after_death == "mort" and action_lock_after_death and death_ticks_reset,
		"detail": {
			"died_flag": died_flag, "anim_after_death": anim_after_death,
			"action_lock_after_death": action_lock_after_death, "death_ticks_reset": death_ticks_reset,
		},
	})
	_checks.append({
		"name": "death_restart_input_is_ignored_before_threshold_ticks",
		"pass": scene_unchanged_before_threshold,
		"detail": {"scene_unchanged_before_threshold": scene_unchanged_before_threshold},
	})


func _report() -> void:
	var all_pass := true
	for c in _checks:
		if not c["pass"]:
			all_pass = false
	print("SMOKE_TEST_RESULT ", JSON.stringify({"all_pass": all_pass, "checks": _checks}))
	get_tree().quit(0 if all_pass else 1)
