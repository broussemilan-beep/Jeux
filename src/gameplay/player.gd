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

## Feedback par tier de combo (mandat combat, escalade des 3 coups de
## base — délibérément adoucie sous le "heavy sur coup 3" du diagnostic
## externe : "ce sont des attaques de BASE, si elles tapent déjà en
## heavy il ne reste rien pour les tiers 5-6, contraire au principe
## d'escalade du doc").
##
## Décision de gabarit (à documenter dans docs/worklog.md) : le mandat
## demande "light-medium" pour le hit-stop du coup 2 et le shake du
## coup 3, mais CombatFeedback n'expose que les 5/3 profils discrets du
## doc (§9.1/§9.2) — pas de palier intermédiaire. À 60 ticks/s
## (CombatFeedback.TICK_MS ≈ 16,667 ms), "light" arrondit déjà à 1 tick
## et "medium" à 2 ticks : il n'existe aucune valeur entière DISTINCTE
## entre les deux pour matérialiser un "light-medium" de hit-stop. Choix
## retenu, dans l'esprit même de l'escalade demandée : arrondir vers le
## BAS (jamais vers le haut) sur toute ambiguïté de palier — un tier
## en-dessous de la couverture pleine reste un tier de base, jamais un
## plafond consommé par avance sur les tiers 5-6 futurs.
const COMBO_TIER_FEEDBACK := [
	{"hitstop": "light", "recoil_px": 4.0, "shake": "", "arc_slash": false},
	{"hitstop": "light", "recoil_px": 8.0, "shake": "", "arc_slash": true},
	{"hitstop": "medium", "recoil_px": 14.0, "shake": "light", "arc_slash": false},
]

## Timeline du dash, en ticks (60/s) — mandat combat (B4) : "se lit
## actuellement comme une téléportation : pas de compression avant
## départ, pas de traînée, arrêt trop net." Découpage repris du
## diagnostic externe (2 anticipation / 5 déplacement / 4 recovery,
## 11 ticks ≈ 0,18s) — EXCEPTION EXPLICITE au §6.2 du doc VFX
## (bande "release" attendue 5-12%) : ici le déplacement EST le
## release (5/11 ≈ 45%), pas un simple appui visuel bref pendant qu'une
## autre couche porte le mouvement. Documentée dans docs/worklog.md
## plutôt que passée sous silence, comme demandé.
const DASH_ANTICIPATION_TICKS := 2
const DASH_MOVE_TICKS := 5
const DASH_RECOVERY_TICKS := 4

## Distance totale parcourue pendant DASH_MOVE_TICKS — point de départ à
## ressentir, pas un dogme (même réserve que les autres valeurs de
## tuning de cette session). ~2,5m, un peu court du 3m de portée
## d'invocation (POWER1_SPAWN_DISTANCE_PX) pour rester un déplacement
## d'esquive, pas un remplacement du mouvement normal.
const DASH_DISTANCE_PX := 80.0
## Vitesse de glissade au sol en tout début de RECOVERY, décroît vers 0
## de façon linéaire sur DASH_RECOVERY_TICKS (même schéma que le recul
## d'Enemy._physics_process, réutilisé ici côté joueur).
const DASH_RECOVERY_INITIAL_SPEED_PX_S := 220.0

## Traînée : 2 after-images (mandat : "opacité ~50% puis ~20%"), posées
## à des ticks distincts de la phase MOUVEMENT pour qu'elles apparaissent
## décalées dans l'espace derrière le joueur, pas superposées au même
## endroit. Chaque ghost s'éteint ensuite tout seul (voir
## _spawn_dash_afterimage()) — ce n'est PAS une primitive VfxDirector
## (contrat seed/configure générique, §7.1) : une after-image lit la
## texture/frame COURANTE du sprite du joueur, une donnée que seul
## Player possède, pas quelque chose qu'une recette JSON peut décrire.
const DASH_AFTERIMAGE_TICKS: Array[int] = [1, 3]
const DASH_AFTERIMAGE_OPACITIES: Array[float] = [0.5, 0.2]
const DASH_AFTERIMAGE_FADE_SEC := 0.15

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
## écraserait la pose dès la frame suivante. Pour hurt, levé par
## _on_sprite_animation_finished(). Pour le combo ET le dash (B4), la
## timeline en ticks ci-dessous est SEULE responsable du verrou
## (_end_combo()/_end_dash()) — aucun des deux ne doit dépendre du
## timing de lecture du sprite, qui est une horloge séparée (§16.3 : ne
## pas fusionner deux minuteries distinctes).
var _action_lock: bool = false

## 0 = pas d'attaque en cours. 1-3 = quel coup du combo joue actuellement.
var _combo_step: int = 0
enum ComboPhase { NONE, ANTICIPATION, RELEASE, RECOVERY }
var _combo_phase: int = ComboPhase.NONE
var _combo_tick: int = 0
var _attack_queued: bool = false
var _hit_applied_this_release: bool = false

## Compteur de ticks absolu depuis le DÉBUT du coup courant (0 à la
## première frappe de _advance_combo() après _start_attack()), INDÉPENDANT
## des remises à zéro de `_combo_tick` à chaque transition de phase —
## root_motion (mandat production v1 §4, données dans
## data/animation_composer/cendre.json) s'exprime sur cette timeline
## continue (start_tick/end_tick), pas sur le tick relatif à une seule
## phase.
var _combo_step_absolute_tick: int = 0

## data/animation_composer/cendre.json — root_motion (J1) par nom
## d'animation ; squash/lean/afterimages y sont déjà présents mais pas
## encore lus (J2, mandat production v1 §4/§6). Chargé une fois au
## _ready(), jamais relu par tick.
var _animation_composer_data: Dictionary = {}

## NONE = pas de dash en cours. Timeline déclarative (B4), même
## discipline que le combo ci-dessus.
enum DashPhase { NONE, ANTICIPATION, MOVE, RECOVERY }
var _dash_phase: int = DashPhase.NONE
var _dash_tick: int = 0
var _dash_direction: Vector2 = Vector2.ZERO
var _dash_recovery_velocity: Vector2 = Vector2.ZERO

## Gueule Vide n'utilise PAS _action_lock : l'invocation (0,7s) n'immobilise
## pas le joueur (rien dans le mandat ne l'exige, contrairement au combo/
## dash) — seul un cooldown la borne dans le temps.
var _power1_cooldown_remaining: int = 0

@onready var _sprite: AnimatedSprite2D = $AnimatedSprite2D
@onready var _camera: Camera2D = $Camera2D


func _ready() -> void:
	_sprite.animation_finished.connect(_on_sprite_animation_finished)
	_animation_composer_data = _load_animation_composer_data()


func _load_animation_composer_data() -> Dictionary:
	const PATH := "res://data/animation_composer/cendre.json"
	if not FileAccess.file_exists(PATH):
		return {}
	var text: String = FileAccess.get_file_as_string(PATH)
	var parsed: Variant = JSON.parse_string(text)
	if parsed is Dictionary:
		return parsed
	return {}


func _physics_process(_delta: float) -> void:
	# Le shake continue de s'appliquer PENDANT un hit-stop (c'est en
	# partie ce qui vend l'impact) — lu avant le retour anticipé
	# ci-dessous, jamais après.
	_camera.offset = CombatFeedback.get_shake_offset()
	if CombatFeedback.is_frozen():
		return

	if _power1_cooldown_remaining > 0:
		_power1_cooldown_remaining -= 1

	if Input.is_action_just_pressed("attack"):
		_attack_queued = true

	if Input.is_action_just_pressed("power1") and not stats.is_dead() and _power1_cooldown_remaining <= 0:
		_cast_gueule_vide()

	if Input.is_action_just_pressed("dash"):
		play_dash()

	if _dash_phase != DashPhase.NONE:
		_advance_dash()
	elif _combo_step > 0:
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
		if facing.x != 0.0:
			_sprite.flip_h = facing.x < 0.0

	if not _action_lock and not stats.is_dead():
		_sprite.play("deplacement" if input_dir.length_squared() > 0.0001 else "idle")


func _start_attack(step: int) -> void:
	_combo_step = step
	_combo_phase = ComboPhase.ANTICIPATION
	_combo_tick = 0
	_combo_step_absolute_tick = 0
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
	_combo_step_absolute_tick += 1
	_apply_combo_root_motion(_combo_step_absolute_tick)
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


## Root motion (mandat production v1 §4, "constat fondateur" : "les
## attaques jouaient sur place, `velocity = 0` pendant le combo") — pousse
## le joueur en avant (`facing`) sur la fenêtre [start_tick, end_tick] de
## `data/animation_composer/cendre.json` pour le coup courant, JAMAIS en
## dehors (velocity remise à zéro par défaut). Via `velocity` uniquement
## (murs solides via move_and_slide(), déjà appelé une fois par frame en
## fin de _physics_process — jamais une écriture directe de `position`).
## Même construction ease-out par différence progress_after-progress_before
## que _advance_dash() (MOVE) : réutilise _ease_out_quad(), pas une
## nouvelle courbe dupliquée.
func _apply_combo_root_motion(abs_tick: int) -> void:
	velocity = Vector2.ZERO
	if _combo_step <= 0 or _combo_step > AttackAnimName.size():
		return
	var anim_name: String = AttackAnimName[_combo_step - 1]
	var anim_data: Dictionary = _animation_composer_data.get(anim_name, {})
	var rm: Dictionary = anim_data.get("root_motion", {})
	if rm.is_empty():
		return
	var start_tick: int = int(rm.get("start_tick", 0))
	var end_tick: int = int(rm.get("end_tick", 0))
	var span: int = end_tick - start_tick
	if span <= 0 or abs_tick < start_tick or abs_tick > end_tick:
		return
	var distance_px: float = float(rm.get("distance_px", 0.0))
	var progress_before: float = _ease_out_quad(float(abs_tick - 1 - start_tick) / span)
	var progress_after: float = _ease_out_quad(float(abs_tick - start_tick) / span)
	var step_px: float = (progress_after - progress_before) * distance_px
	velocity = facing * (step_px * Engine.physics_ticks_per_second)


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
	var tier: Dictionary = COMBO_TIER_FEEDBACK[_combo_step - 1]
	target.take_damage(ATTACK_DAMAGE, global_position, tier["recoil_px"])

	# Hit-stop + shake (mandat combat, B1-B3) : local aux nœuds de combat
	# via CombatFeedback (§9.1), jamais Engine.time_scale. Direction du
	# shake = `facing` (l'attaque), CombatFeedback inverse lui-même l'axe.
	CombatFeedback.trigger_hitstop(tier["hitstop"])
	if tier["shake"] != "":
		CombatFeedback.trigger_shake(tier["shake"], facing)

	# impactFlashFrame + recoil sur chaque coup (mandat Phase 1.4). Le
	# recoil est déjà porté par Enemy.take_damage() (§4 : réaction de la
	# cible, jamais une primitive de l'attaquant) — ici on ne pose QUE le
	# flash d'impact, seule primitive qui appartient au coup lui-même.
	VfxDirector.spawn("impactFlashFrame", {
		"seed": 0,
		"origin": target.global_position,
		"lifetime_ticks": 2,
		"overdraw_cost": 12.0,
		# Addendum A §A.1/§A.2 : CONTACT protégée (primaire impactFlashFrame
		# + recul) — ne se sacrifie jamais sous pression de budget.
		"degradable": false,
	})

	# arcSlash sur le coup 2 seulement (mandat : "arc visuel bref sur 2
	# ticks") — trace du geste qui a touché, couche CONTACT protégée au
	# même titre que impactFlashFrame ci-dessus.
	if tier["arc_slash"]:
		VfxDirector.spawn("arcSlash", {
			"seed": 0,
			"origin": target.global_position,
			"direction": facing,
			"lifetime_ticks": 2,
			"scale_px": 28.0,
			"degradable": false,
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
	creature.set_owner_stats(stats)


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


## Direction du dash : l'input courant s'il y en a un (esquive dirigée,
## standard pour ce type d'action), sinon `facing` (dash "en avant" à
## l'arrêt) — jamais une direction nulle.
func play_dash() -> void:
	if stats.is_dead() or _action_lock:
		return
	var input_dir := Vector2(
		Input.get_action_strength("ui_right") - Input.get_action_strength("ui_left"),
		Input.get_action_strength("ui_down") - Input.get_action_strength("ui_up")
	)
	var dir := input_dir
	if dir.length_squared() < 0.0001:
		dir = facing
	if dir.length_squared() < 0.0001:
		dir = Vector2.DOWN
	_dash_direction = dir.normalized()

	_action_lock = true
	_dash_phase = DashPhase.ANTICIPATION
	_dash_tick = 0
	_sprite.play("dash")
	if _dash_direction.x != 0.0:
		_sprite.flip_h = _dash_direction.x < 0.0

	# "shake light dès le premier tick, axe opposé au déplacement" —
	# déclenché ici, au tout premier tick de l'action (l'anticipation),
	# pas seulement au moment où le déplacement démarre.
	CombatFeedback.trigger_shake("light", _dash_direction)


## Timeline déclarative du dash (B4) — ANTICIPATION (bref arrêt, buste
## "planté" avant le départ) -> MOVE (burst avec ease-out, DASH_DISTANCE_PX
## répartis sur DASH_MOVE_TICKS, pas une téléportation en un seul tick)
## -> RECOVERY (glissade qui décélère au sol, jamais un arrêt nul). Même
## discipline que _advance_combo() : ne dépend jamais de la durée réelle
## de lecture du sprite.
func _advance_dash() -> void:
	_dash_tick += 1
	match _dash_phase:
		DashPhase.ANTICIPATION:
			velocity = Vector2.ZERO
			if _dash_tick >= DASH_ANTICIPATION_TICKS:
				_dash_phase = DashPhase.MOVE
				_dash_tick = 0
		DashPhase.MOVE:
			var progress_before: float = _ease_out_quad(float(_dash_tick - 1) / DASH_MOVE_TICKS)
			var progress_after: float = _ease_out_quad(float(_dash_tick) / DASH_MOVE_TICKS)
			var step_px: float = (progress_after - progress_before) * DASH_DISTANCE_PX
			velocity = _dash_direction * (step_px * Engine.physics_ticks_per_second)
			var afterimage_idx := DASH_AFTERIMAGE_TICKS.find(_dash_tick)
			if afterimage_idx != -1:
				_spawn_dash_afterimage(DASH_AFTERIMAGE_OPACITIES[afterimage_idx])
			if _dash_tick >= DASH_MOVE_TICKS:
				_dash_phase = DashPhase.RECOVERY
				_dash_tick = 0
				_dash_recovery_velocity = _dash_direction * DASH_RECOVERY_INITIAL_SPEED_PX_S
		DashPhase.RECOVERY:
			velocity = _dash_recovery_velocity
			_dash_recovery_velocity = _dash_recovery_velocity.move_toward(
				Vector2.ZERO, DASH_RECOVERY_INITIAL_SPEED_PX_S / DASH_RECOVERY_TICKS)
			if _dash_tick >= DASH_RECOVERY_TICKS:
				_end_dash()


## Décélération quadratique (rapide puis qui s'adoucit) — "vitesse max
## avec ease-out" du mandat : plein régime dès le premier tick de MOVE,
## puis chaque tick suivant couvre un peu moins de distance.
func _ease_out_quad(x: float) -> float:
	var c: float = clampf(x, 0.0, 1.0)
	return 1.0 - (1.0 - c) * (1.0 - c)


func _end_dash() -> void:
	_dash_phase = DashPhase.NONE
	_dash_tick = 0
	velocity = Vector2.ZERO
	_action_lock = false


## Fantôme de traînée (B4) — PAS une primitive VfxDirector (§7.1, contrat
## seed/configure générique) : copie la texture/frame COURANTE du sprite
## du joueur, une donnée que seul Player possède. `Sprite2D` autonome,
## parenté au même parent que Player (jamais à Player lui-même, sinon il
## suivrait son mouvement au lieu de rester "planté" derrière lui) —
## s'éteint tout seul via un Tween sur son opacité, jamais géré par
## VfxDirector/VfxBudget (ce n'est pas dans leur périmètre, §8.2).
func _spawn_dash_afterimage(opacity: float) -> void:
	var texture: Texture2D = _sprite.sprite_frames.get_frame_texture(_sprite.animation, _sprite.frame)
	if texture == null:
		return
	var ghost := Sprite2D.new()
	ghost.texture = texture
	ghost.offset = _sprite.offset
	ghost.flip_h = _sprite.flip_h
	ghost.z_index = _sprite.z_index - 1
	ghost.modulate = Color(1.0, 1.0, 1.0, opacity)
	# add_child() AVANT de fixer global_position : le calcul global_position
	# a besoin de la transform du parent, indisponible tant que le nœud
	# n'est pas encore dans l'arbre.
	get_parent().add_child(ghost)
	ghost.global_position = _sprite.global_position
	var tween: Tween = ghost.create_tween()
	tween.tween_property(ghost, "modulate:a", 0.0, DASH_AFTERIMAGE_FADE_SEC)
	tween.finished.connect(ghost.queue_free)


func _on_sprite_animation_finished() -> void:
	if _combo_step > 0:
		return  # le combo gère son propre verrou via sa timeline de ticks (_end_combo())
	if _dash_phase != DashPhase.NONE:
		return  # le dash gère son propre verrou via sa timeline de ticks (_end_dash())
	if _sprite.animation == "mort":
		return  # reste sur la dernière frame, jamais reverrouillé sur idle
	_action_lock = false


func die() -> void:
	stats.hp = 0.0
	_combo_step = 0
	_combo_phase = ComboPhase.NONE
	_attack_queued = false
	_dash_phase = DashPhase.NONE
	_action_lock = true
	_sprite.play("mort")
