extends CharacterBody2D
class_name Enemy
## Ennemi Phase 1 (G, GDD §10/§21 : "Crawler, Brute, Ranged... HitResponse
## natif"). `take_damage()`/le recul subi/`_visual` restent ceux de la
## Phase 1.2 tels quels — G n'ajoute QUE la capacité d'agir (détecter,
## approcher, télégraphier, frapper), jamais une réécriture de la
## réaction à un coup encaissé.
##
## Un seul script pour les 3 archétypes, pas 3 classes : Crawler et Brute
## partagent la MÊME logique de contact (MELEE), seuls les chiffres
## `@export` changent (vitesse/portée/dégâts/télégraphe) — cohérent avec
## la discipline "pas de variation que le runtime peut dériver d'une
## configuration existante" (Stats.gd). Seul Ranged bifurque réellement
## (garde ses distances, tire un projectile au lieu d'un contact).

enum Archetype { MELEE, RANGED }
enum State { IDLE, CHASE, TELEGRAPH, RECOVER }

const ProjectileScene := preload("res://scenes/gameplay/projectile.tscn")

@export var stats: Stats = Stats.new()
@export var archetype: Archetype = Archetype.MELEE

## Portées/tempo — GDD §10 ne chiffre aucun de ces archétypes (noms de
## travail, "Crawler : petit, rapide, harcèlement", "Brute : lent, lourd,
## grosses attaques télégraphiées", "Ranged : pression à distance").
## Valeurs de départ TUNABLE (même discipline que D, §1.3), à ajuster une
## fois testées en jeu réel — les 3 scènes variantes (enemy_crawler/
## enemy_brute/enemy_ranged.tscn) n'exportent que CES chiffres (+ `stats`
## pour HP/vitesse, voir plus bas), jamais de code dupliqué. La vitesse
## de déplacement vit sur `stats.move_speed_px` (Stats.gd), pas un second
## champ ici — Player l'utilise déjà, aucune raison qu'Enemy en
## réimplémente un distinct.
##
## `enemy.tscn` (le fichier générique, pas les 3 variantes) force
## `aggro_radius_px = 0.0` : il reste le mannequin d'entraînement
## STATIONNAIRE de Phase 1.2, réutilisé tel quel par ~10 checks de
## `smoke_test_gameplay.gd` qui supposent un ennemi immobile à une
## position connue (targeting, combo, Bras-Faux...). Casser ces checks
## pour leur donner une IA qu'ils n'ont jamais demandée aurait été une
## régression, pas une amélioration — l'IA réelle vit dans les 3 scènes
## d'archétype ci-dessous, jamais dans le mannequin générique.
@export var aggro_radius_px: float = 220.0
@export var attack_range_px: float = 40.0  ## MELEE : portée de contact. Ignoré par RANGED (voir preferred_range_px).
@export var telegraph_ticks: int = 18
@export var attack_recover_ticks: int = 14
@export var attack_cooldown_ticks: int = 40
@export var contact_damage: float = 8.0
@export var contact_recoil_px: float = 20.0
@export var hitstop_profile: String = "light"
@export var shake_profile: String = ""  ## "" = pas de shake (CombatFeedback n'a pas de profil "none" pour trigger_shake).

## Phase R4 (retour croisé Gemini/ChatGPT, MANDAT SUITE v2 : "recul par
## poids d'ennemi") — multiplie le `recoil_strength_px` que l'ATTAQUANT
## demande dans `take_damage()`, indépendamment de quel pouvoir/coup a
## frappé (combo/Bras-Faux/Poing Belluaire/Poing Tellurique/Gueule Vide
## passent tous des valeurs différentes sans connaître le poids de la
## cible — ce multiplicateur est ce qui reste constant CÔTÉ CIBLE).
## Jamais 0.0 : "le retour doit toujours être visible, même minime"
## (Milan) — un ennemi lourd résiste au recul, il n'y est jamais immun.
@export var recoil_multiplier: float = 1.0

## RANGED seulement — maintient la distance au lieu de foncer au contact.
@export var preferred_range_px: float = 170.0
@export var range_tolerance_px: float = 24.0
@export var projectile_damage: float = 6.0
@export var projectile_speed_px_s: float = 240.0

## Phase 1.3 (MANDAT SUITE v2) : bob procédural qui simule un déplacement
## sans cycle de marche animé (Crawler/Brute n'ont qu'idle+attaque —
## docs/worklog.md Phase 1.1, "no hand-animated walk cycle, trop coûteux
## pour le prototype"). Glisse la pose idle + une légère oscillation
## verticale pendant CHASE seulement, jamais pendant TELEGRAPH/RECOVER
## (l'ennemi y est immobile par design).
const BOB_AMPLITUDE_PX := 2.0
const BOB_PERIOD_TICKS := 20
var _move_tick: int = 0

## H1 (GDD §20/§21 : "combats -> XP/loot/maîtrise") — TUNABLE, roughly
## proportionnel au HP/difficulté de chaque archétype (Brute > Ranged >
## Crawler, mêmes valeurs que les .tscn variantes).
@export var xp_reward: float = 10.0

## Phase R4 (game feel Milan, "knockback_return_curve: easeOut") : recul en
## courbe de POSITION ease-out (AnimationComposer.ease_out_step_px(), même
## technique que Player._advance_dash()/MOVE) plutôt qu'une vitesse qui
## décroît linéairement — _recoil_tick compte les ticks déjà consommés
## (1-indexé), _recoil_total_ticks/_recoil_total_distance_px/_recoil_direction
## sont figés au moment de l'impact.
var _recoil_tick: int = 0
var _recoil_total_ticks: int = 0
var _recoil_total_distance_px: float = 0.0
var _recoil_direction: Vector2 = Vector2.ZERO

## CHANTIER C (production v1, "Monstres : animations d'interaction") —
## HitResponse directionnel/chancellement/projection, côté ENNEMI cette
## fois (le HitResponse autoload existant ne fait que flash/chiffre/mort,
## générique aux 3 archétypes — §4 GDD ; la sélection de LA bonne
## réaction selon la direction/l'enchaînement/le poids est propre à
## chaque cible, donc portée ici, sur Enemy, même choix d'architecture
## que _recoil_tick/_slow_multiplier ci-dessus).
##
## Direction (4 minimum, GDD Chantier C) : classée sur l'axe dominant du
## vecteur "vers l'attaquant" (voir _select_directional_reaction()) —
## gauche/droite (miroir via flip_h, UNE seule pose "touche_lateral"
## capturée, même convention que le flip_h déjà utilisé pour le
## déplacement) + avant/arrière (2 poses distinctes, "touche_avant"/
## "touche_arriere" — l'un ne peut pas être un miroir de l'autre).
##
## Chancellement (enchaînement de coups) : STAGGER_TRIGGER_HITS coups
## reçus en moins de STAGGER_WINDOW_TICKS déclenchent State.STAGGER
## (IA suspendue, comme le recul) — pose "chancelle" tenue
## STAGGER_DURATION_TICKS, flip_h alterné à cadence FIXE
## (STAGGER_FLIP_PERIOD_TICKS, jamais le FPS autonome de l'anim — même
## discipline tick-exact que <SKILL>_FRAME_TICK_BOUNDS côté Player) pour
## simuler un vacillement gauche-droite sans frame supplémentaire.
##
## Projection + rebond (monstres LÉGERS uniquement, GDD : "le Crawler est
## projeté" vs "le Brute encaisse sans bouger") : PUREMENT dérivé de la
## présence de l'anim "projete" dans le SpriteFrames de CE monstre
## (Crawler/Ranged en ont une, Brute non — cohérent avec la discipline
## du fichier "pas de variation que le runtime peut dériver d'une
## configuration existante", aucun 2e seuil numérique à synchroniser
## avec recoil_multiplier). La pose d'impact directionnelle tient
## IMPACT_POSE_HOLD_TICKS ticks puis cède la place à "projete" pour le
## reste du recul (déjà mis à l'échelle par recoil_multiplier — un
## Crawler vole plus loin qu'un Ranged, même pose, distance différente),
## puis un rebond procédural (BOUNCE_*, décalage vertical du sprite,
## même technique que _update_visual_bob()/le bob de marche — aucune
## frame supplémentaire nécessaire) avant de rendre la main à l'IA.
const STAGGER_WINDOW_TICKS: int = 50
const STAGGER_TRIGGER_HITS: int = 3
const STAGGER_DURATION_TICKS: int = 24
const STAGGER_FLIP_PERIOD_TICKS: int = 6
const IMPACT_POSE_HOLD_TICKS: int = 2
const BOUNCE_DURATION_TICKS: int = 10
const BOUNCE_HEIGHT_PX: float = 6.0

var _last_hit_tick: int = -1000000
var _consecutive_hits: int = 0
var _pending_projection: bool = false
var _projection_pose_active: bool = false
var _bounce_tick: int = 0
var _bounce_total_ticks: int = 0
var _stagger_tick: int = 0
var _stagger_total_ticks: int = 0
var _pre_stagger_flip_h: bool = false

var _state: int = State.IDLE
var _state_tick: int = 0
var _cooldown_remaining: int = 0
var _base_visual_color: Color = Color.WHITE

## MANDAT AUTONOME v3 Phase 3 (Marée de Sable, GDD Terre §2 : "ralentissant
## et entravant les ennemis touchés") — première source de ralentissement
## du jeu, générique plutôt que spécifique à ce seul pouvoir (n'importe
## quelle future compétence "contrôle" pourra appeler apply_slow() sans
## dupliquer cet état). Un multiplicateur qui EXPIRE par compte de ticks
## (même discipline que _recoil_tick/_cooldown_remaining ci-dessus),
## jamais un Timer — cohérent avec le reste de cette classe, tout en
## ticks physiques comptés à la main.
var _slow_multiplier: float = 1.0
var _slow_ticks_remaining: int = 0

## MANDAT DÉDIÉ MARÉE DE SABLE (polish, 2026-08-23) — écart trouvé : apply_slow()
## ci-dessus changeait bien `stats.move_speed_px` (_chase_velocity le lit), mais
## RIEN à l'écran ne le montrait — un ennemi ralenti était visuellement
## indiscernable d'un ennemi normal tant qu'on ne mesurait pas sa vitesse de
## déplacement à l'œil. Réutilise le SEUL mécanisme de teinte déjà câblé sur ce
## nœud (`self_modulate`/`Polygon2D.color`, `_pulse_telegraph_color()` ci-dessous)
## plutôt que d'inventer un 2e système : teinte ocre clair (data/palettes/
## terre.json, rôle "contact" — même couleur que sandCrest/impactStar, aucune
## couleur nouvelle) mélangée par-dessus la couleur de base, recalculée à
## CHAQUE tick dans _reset_visual_color() pour composer proprement avec le
## pulse blanc du télégraphe (qui doit rester visible même sur un ennemi
## ralenti — l'un ne doit jamais écraser silencieusement l'autre).
const SLOW_TINT_COLOR := Color(0.7, 0.595, 0.385, 1.0)  # HSV(40°, 45%, 70%), palette "terre" rôle "contact"
const SLOW_TINT_STRENGTH := 0.65

signal hit(amount: float)

## Nœud visuel de la cible — `Placeholder` (Polygon2D géométrique) sur le
## mannequin générique `enemy.tscn` (encore utilisé par ~10 checks de
## smoke_test_gameplay.gd, jamais retouché), `Visual` (AnimatedSprite2D,
## Phase 1.3 MANDAT SUITE v2) sur les 3 scènes d'archétype réelles —
## mandat production v1 §4 : "shader sur le sprite de la cible" s'applique
## identiquement aux deux (HitResponse.flash_sprite() prend n'importe quel
## CanvasItem), aucune branche de type nécessaire côté HitResponse.
@onready var _visual: CanvasItem = get_node("Visual") if has_node("Visual") else get_node("Placeholder")


## Phase 2.3 (MANDAT SUITE v2) : outlineSelective (ennemi = rouge), sur les
## vraies scènes d'archétype (AnimatedSprite2D) uniquement — le mannequin
## générique Polygon2D n'a pas de canal alpha à contourer de la même façon,
## et n'a jamais eu besoin de lisibilité supplémentaire (smoke tests).
const OutlineShader := preload("res://src/vfx/shaders/outline_selective.gdshader")


func _ready() -> void:
	add_to_group("enemies")
	if _visual is Polygon2D:
		_base_visual_color = (_visual as Polygon2D).color
	elif _visual is AnimatedSprite2D:
		_base_visual_color = _visual.self_modulate
		var mat := ShaderMaterial.new()
		mat.shader = OutlineShader
		mat.set_shader_parameter("outline_color", Color(0.85, 0.2, 0.18, 1.0))
		_visual.material = mat


func _physics_process(_delta: float) -> void:
	# Phase R4 : hit-stop asymétrique — un ennemi consulte TOUJOURS son
	# propre compteur "enemy", qu'il soit lui-même en train de frapper
	# (attaquant, gel court) ou de se faire toucher (cible, gel long) :
	# register_hit() route déjà les deux compteurs selon
	# `attacker_is_player`, ce nœud n'a qu'à lire celui qui le concerne.
	if CombatFeedback.is_enemy_frozen():
		return
	if _recoil_tick < _recoil_total_ticks:
		_recoil_tick += 1
		# Projection (monstres légers, cf. bloc de doc au-dessus de
		# _pending_projection) : la pose d'impact directionnelle tient
		# IMPACT_POSE_HOLD_TICKS ticks puis cède la place à "projete" pour
		# le reste du vol — swap unique (_projection_pose_active garde
		# l'idempotence, jamais un sprite.play() répété à chaque tick qui
		# relancerait la pose en boucle).
		if _pending_projection and not _projection_pose_active and _recoil_tick >= IMPACT_POSE_HOLD_TICKS:
			_projection_pose_active = true
			_apply_hit_reaction("projete", _visual is AnimatedSprite2D and (_visual as AnimatedSprite2D).flip_h)
		var step_px: float = AnimationComposer.ease_out_step_px(_recoil_tick, _recoil_total_ticks, _recoil_total_distance_px)
		velocity = _recoil_direction * (step_px * Engine.physics_ticks_per_second)
		move_and_slide()
		if _recoil_tick >= _recoil_total_ticks and _pending_projection:
			# Recul terminé sur un monstre léger : enchaîne directement sur
			# le rebond procédural (aucune frame supplémentaire — même
			# technique que le bob de marche, _update_visual_bob()).
			_pending_projection = false
			_projection_pose_active = false
			_bounce_tick = 0
			_bounce_total_ticks = BOUNCE_DURATION_TICKS
		return
	if _bounce_tick < _bounce_total_ticks:
		_bounce_tick += 1
		_advance_bounce()
		return
	if _stagger_tick < _stagger_total_ticks:
		_stagger_tick += 1
		_advance_stagger()
		return
	if is_dead():
		return
	if _cooldown_remaining > 0:
		_cooldown_remaining -= 1
	if _slow_ticks_remaining > 0:
		_slow_ticks_remaining -= 1
		if _slow_ticks_remaining <= 0:
			_slow_multiplier = 1.0
	_run_ai()
	_update_visual_bob()
	# Retour visuel du ralentissement (cf. _reset_visual_color()) : appelé
	# chaque tick HORS TELEGRAPH, qui a déjà sa propre couleur par tick via
	# _pulse_telegraph_color() (appelée depuis _run_ai() ci-dessus) — les deux
	# sites ne se marchent jamais dessus, un seul écrit self_modulate/color
	# par tick selon l'état.
	if _state != State.TELEGRAPH:
		_reset_visual_color()
	# `move_and_slide()` UNIQUEMENT si un vrai déplacement est demandé (pas
	# à chaque tick inconditionnellement) : appelé même à vélocité nulle,
	# il dépénètre les CharacterBody2D déjà en collision (deux ennemis
	# posés proches l'un de l'autre, ou d'un ennemi contre le joueur) et
	# les pousse hors de leur position exacte — la Phase 1.2 ne l'appelait
	# QUE pendant le recul, jamais au repos ; cassait silencieusement
	# `bras_faux_hits_all_enemies_in_arc_spares_enemy_outside` (3 ennemis
	# posés à 30px les uns des autres pour le test) avant ce garde-fou.
	if velocity != Vector2.ZERO:
		move_and_slide()


func is_dead() -> bool:
	return stats.is_dead()


## Ralentissement temporaire (Marée de Sable) — écrase toujours l'effet en
## cours par le plus récent (jamais cumulatif, jamais un stack de
## multiplicateurs qui pourrait s'approcher de 0 après 2 vagues) : un
## contrôle qui s'additionnerait sans limite serait un piège de boucle
## infinie, pas un choix de design demandé par la bible.
func apply_slow(multiplier: float, duration_ticks: int) -> void:
	_slow_multiplier = clampf(multiplier, 0.0, 1.0)
	_slow_ticks_remaining = duration_ticks


## `source_position` sert à orienter le recul (toujours opposé à l'attaque,
## jamais isotrope — §4 : "jamais un bruit isotrope"). `damage` peut être 0
## pour un recul sans dégâts (pas de cas connu aujourd'hui, mais la
## signature reste correcte pour ça).
##
## Phase R4 (game feel Milan, bac à sable sur UN impact isolé :
## knockback_distance_px=27) : proche de l'ancien défaut (24.0, déjà le
## défaut générique des 3 take_damage() du jeu) plutôt que des grandes
## valeurs déjà tunées par site (Poing Belluaire 40, boss 26-70) —
## interprété comme LA VALEUR DE RÉFÉRENCE "défaut non spécifié", pas
## comme le coup le plus lourd (contrairement à hitstop_freeze_ms) : les
## attaques déjà tunées explicitement gardent leur propre valeur, seul ce
## défaut change (24.0 -> 27.0), même choix sur les 3 take_damage().
func take_damage(amount: float, source_position: Vector2, recoil_strength_px: float = 27.0, recoil_ticks: int = 6) -> void:
	if is_dead():
		return
	stats.apply_damage(amount)
	hit.emit(amount)
	var away: Vector2 = (global_position - source_position)
	if away.length_squared() < 0.0001:
		away = Vector2.RIGHT
	away = away.normalized()
	# Phase R4 : `recoil_multiplier` (poids de CET ennemi) module le
	# recul demandé par l'attaquant — jamais l'inverse, l'attaquant ne
	# connaît pas le poids de sa cible.
	_recoil_direction = away
	_recoil_total_distance_px = recoil_strength_px * recoil_multiplier
	_recoil_total_ticks = recoil_ticks
	_recoil_tick = 0

	# HitResponse (mandat production v1 §4) : flash + chiffre de dégâts sur
	# TOUT coup qui touche, avant le early-return de mort ci-dessous — la
	# cible qui meurt doit quand même flasher/afficher son dernier chiffre,
	# jamais les sauter silencieusement.
	HitResponse.flash_sprite(_visual)
	HitResponse.spawn_damage_number(amount, global_position, get_parent())

	if not is_dead():
		# CHANTIER C : réaction directionnelle/chancellement/projection —
		# seulement sur un coup qui ne tue pas (la mort a sa propre
		# animation "mort" côté Ranged, _die() ci-dessous — jamais les deux
		# à la fois sur le même impact).
		_on_hit_reaction(away)

		# MANDAT DÉDIÉ RECUL RÉEL (Milan, playtest build web 2026-08-26 :
		# "les monstres ne sont pas repoussés, le joueur ne peut jamais
		# créer de distance, se fait enchaîner"). Root cause confirmée par
		# reproduction en combat réel (Player+Enemy chasant vraiment l'un
		# l'autre, PAS un take_damage() isolé sur un mannequin/ennemi hors
		# d'aggro comme les checks existants ci-dessous) : le recul lui-même
		# déplace bien `global_position` (aucun bug là), mais dès que
		# `_recoil_tick` atteint `_recoil_total_ticks`, `_physics_process`
		# retombe DIRECTEMENT dans `_run_ai()` sans transition — si l'état
		# d'avant le coup était CHASE (le cas normal en combat), l'IA
		# relance IMMÉDIATEMENT `move_speed_px` plein régime vers le
		# joueur et referme en 2-3 ticks les quelques px que le recul
		# venait de créer (4-22px selon le tier de combo, contre 150px/s
		# de vitesse de poursuite Crawler) — invisible à l'écran. Player a
		# déjà exactement ce garde-fou côté lui : `_action_lock`/
		# `_hurt_phase` (voir Player.take_damage()/_advance_hurt()) bloque
		# tout mouvement volontaire pendant SON propre recul ; rien
		# d'équivalent n'existait ici pour empêcher la PROPRE IA de
		# l'ennemi de reprendre aussi sec. Fix : armer State.RECOVER
		# (immobile, `_run_ai()` ne fait plus rien avancer) pour la même
		# durée que sa propre récupération d'attaque — pas un chiffre
		# inventé, `attack_recover_ticks`/`attack_cooldown_ticks` sont déjà
		# tunés par archétype (Crawler léger et court, Brute long) et
		# encaisser un coup casse tout autant l'élan d'attaque de CET
		# ennemi que sa position. Posé ICI (pas dans _physics_process) :
		# `_run_ai()` ne tourne de toute façon pas tant que recul/bounce/
		# stagger n'ont pas fini (gates en tête de _physics_process), donc
		# cet état attend simplement d'être consulté, quelle que soit la
		# séquence de réaction qui précède.
		_state = State.RECOVER
		_state_tick = 0

	if is_dead():
		# H1 (GDD §20 : "combats -> XP/loot/maîtrise") — avant _die(),
		# jamais après (Targeting.get_player() ne dépend pas de CET ennemi).
		var player: Node = Targeting.get_player(get_tree())
		if player != null:
			player.stats.add_xp(xp_reward)
		HitResponse.spawn_death_response(global_position, away, get_parent())
		_die()


## Phase 1.2/1.3 (MANDAT SUITE v2) : Ranged a une vraie animation de mort
## (bibliothèque Meshy, 6 frames — docs/worklog.md Phase 1.2) ; Crawler/
## Brute n'en ont pas (scope Phase 1.1 réduit à idle+attaque). `_die()`
## joue "mort" si elle existe (désactive IA/collision, libère au dernier
## frame via animation_finished) et retombe sur le queue_free() immédiat
## d'avant sinon — jamais de régression pour les 2 sans animation dédiée.
func _die() -> void:
	set_physics_process(false)
	Sfx.play("death")
	var collision: CollisionShape2D = get_node_or_null("CollisionShape2D")
	if collision != null:
		collision.set_deferred("disabled", true)
	if _visual is AnimatedSprite2D:
		var sprite: AnimatedSprite2D = _visual
		if sprite.sprite_frames != null and sprite.sprite_frames.has_animation("mort"):
			sprite.play("mort")
			sprite.animation_finished.connect(queue_free, CONNECT_ONE_SHOT)
			return
	queue_free()


## État minimal : IDLE/CHASE (pas d'aggro ou en approche) -> TELEGRAPH
## (immobile, pulse visuel) -> exécution du coup au dernier tick ->
## RECOVER (immobile, pose le cooldown) -> retour CHASE/IDLE selon
## distance. Pas de state ATTACK séparé : le coup se résout en un seul
## tick à la fin de TELEGRAPH, jamais étalé sur plusieurs (mêmes
## garanties de contact qu'un coup joueur — root motion mis à part, hors
## scope ici, aucun ennemi n'a de root motion GDD-spécifié).
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
			_pulse_telegraph_color(float(_state_tick) / float(max(1, telegraph_ticks)))
			_state_tick += 1
			if _state_tick >= telegraph_ticks:
				_execute_attack(player, to_player)
		State.RECOVER:
			velocity = Vector2.ZERO
			_state_tick += 1
			if _state_tick >= attack_recover_ticks:
				_state = State.CHASE
				_state_tick = 0
				_cooldown_remaining = attack_cooldown_ticks
				_play_visual_animation("idle")
		_:  # IDLE, CHASE
			if dist > aggro_radius_px:
				_state = State.IDLE
				velocity = Vector2.ZERO
				return
			_state = State.CHASE
			if _cooldown_remaining <= 0 and _in_attack_window(dist):
				_state = State.TELEGRAPH
				_state_tick = 0
				velocity = Vector2.ZERO
				_play_visual_animation("attaque")
				return
			velocity = _chase_velocity(to_player, dist)


## RANGED : n'ouvre PAS le tir tant que le joueur est trop proche (dans sa
## propre zone de recul) — sinon "garde ses distances" ne serait qu'un
## mot, jamais un vrai comportement : un joueur qui rush au contact
## déclencherait quand même un tir immobile point-blank, indiscernable
## d'un ennemi de mêlée sans le contact. Doit d'abord reculer
## (_chase_velocity ci-dessous) jusqu'à sortir de la bande de tolérance
## avant d'être de nouveau éligible au télégraphe.
func _in_attack_window(dist: float) -> bool:
	if archetype == Archetype.RANGED:
		return dist <= aggro_radius_px and dist >= preferred_range_px - range_tolerance_px
	return dist <= attack_range_px


## MELEE fonce toujours droit dessus. RANGED "garde ses distances" (GDD
## §10) : approche si trop loin pour tirer, recule si le joueur est
## rentré dans sa zone de confort, tient sa position dans la bande de
## tolérance entre les deux — jamais un simple chase qui le ferait finir
## au contact comme un ennemi de mêlée.
func _chase_velocity(to_player: Vector2, dist: float) -> Vector2:
	if dist < 0.0001:
		return Vector2.ZERO
	var dir: Vector2 = to_player / dist
	var speed: float = stats.move_speed_px * _slow_multiplier
	if archetype == Archetype.RANGED:
		if dist > preferred_range_px + range_tolerance_px:
			return dir * speed
		if dist < preferred_range_px - range_tolerance_px:
			return -dir * speed
		return Vector2.ZERO
	return dir * speed


## Lisibilité du télégraphe (GDD §10, "grosses attaques télégraphiées" —
## exigé explicitement pour Brute, appliqué uniformément aux 3 archétypes
## par simplicité/cohérence) : la cible blanchit progressivement jusqu'au
## moment du coup, déterministe (fonction du tick, jamais un Tween en
## temps réel qui désynchroniserait de la simulation à 60 ticks/s).
##
## Phase R4 (retour croisé Gemini/ChatGPT sur clip réel, MANDAT SUITE
## v2) : ce pulse ne s'appliquait QU'à `Polygon2D` (le mannequin
## générique) — sur les 3 scènes d'archétype réelles (Crawler/Brute/
## Ranged, `_visual` en `AnimatedSprite2D`), rien ne se voyait à l'écran
## pendant tout le TELEGRAPH au-delà du changement d'animation ponctuel
## vers "attaque" en tout DÉBUT de fenêtre — même diagnostic que les
## bugs précédents (Poing Tellurique, outline joueur) : la logique
## existait (`_state_tick`/`telegraph_ticks` gate bien le coup), le
## rendu manquait. Étendu via `self_modulate` (teinte progressive vers
## blanc, même formule que Polygon2D.color) — s'applique PAR-DESSUS le
## shader d'outline déjà posé sur ces sprites (le modulate Godot
## multiplie la sortie du shader, aucun conflit).
func _pulse_telegraph_color(progress: float) -> void:
	# Part de la couleur "de repos" (base, ou teintée sable si ralenti — cf.
	# _slow_tinted_color()) plutôt que toujours _base_visual_color brut : un
	# ennemi ralenti QUI télégraphie un coup doit rester lisible comme
	# "ralenti" jusqu'à ce que le flash blanc du télégraphe monte, jamais un
	# blanc qui efface silencieusement le retour visuel du contrôle en cours.
	var lerped: Color = _slow_tinted_color().lerp(Color(1.0, 1.0, 1.0, 1.0), clampf(progress, 0.0, 1.0))
	if _visual is Polygon2D:
		(_visual as Polygon2D).color = lerped
	elif _visual is AnimatedSprite2D:
		_visual.self_modulate = lerped


## Ralentissement (Marée de Sable, apply_slow() ci-dessus) — teinte ocre clair
## (SLOW_TINT_COLOR) mélangée par-dessus la couleur de base tant que
## `_slow_ticks_remaining > 0`, sinon la couleur de base telle quelle. Recalculé
## à chaque appel plutôt que mémorisé : suit `_slow_ticks_remaining` sans état
## supplémentaire à synchroniser (même discipline que _slow_multiplier, qui
## expire de la même façon par décompte de ticks, jamais un Tween).
func _slow_tinted_color() -> Color:
	if _slow_ticks_remaining > 0:
		return _base_visual_color.lerp(SLOW_TINT_COLOR, SLOW_TINT_STRENGTH)
	return _base_visual_color


## Appelée UNE FOIS au moment où le télégraphe cède la place au coup exécuté
## (_execute_attack(), sortie immédiate du blanc de pulse) ET, depuis le
## correctif MANDAT DÉDIÉ MARÉE DE SABLE, à CHAQUE tick hors TELEGRAPH
## (_physics_process ci-dessus) — c'est ce 2e site d'appel qui donne au
## ralentissement un retour visuel réel : sans lui, la teinte ne se voyait
## qu'à l'instant précis d'un _execute_attack(), jamais en IDLE/CHASE/RECOVER
## où un ennemi ralenti passe l'essentiel de sa durée de ralentissement.
func _reset_visual_color() -> void:
	var color: Color = _slow_tinted_color()
	if _visual is Polygon2D:
		(_visual as Polygon2D).color = color
	elif _visual is AnimatedSprite2D:
		_visual.self_modulate = color


## `_visual` en `AnimatedSprite2D` uniquement (Crawler/Brute/Ranged, Phase
## 1.3) — ignoré sans effet sur le mannequin générique (Polygon2D) et sur
## tout SpriteFrames qui n'aurait pas encore l'anim demandée (aucun crash,
## juste pas de changement visuel, même discipline que les checks
## `is Polygon2D` ci-dessus).
func _play_visual_animation(anim_name: String) -> void:
	if _visual is AnimatedSprite2D:
		var sprite: AnimatedSprite2D = _visual
		if sprite.sprite_frames != null and sprite.sprite_frames.has_animation(anim_name):
			sprite.play(anim_name)


## CHANTIER C — point d'entrée appelé par take_damage() sur tout coup
## NON mortel. `incoming` : direction du coup qui vient d'être encaissé
## (vers l'ATTAQUANT, donc l'opposé de `away`/`_recoil_direction` qui
## pointe vers OÙ l'ennemi est repoussé — les deux sont bien distincts,
## jamais interchangés).
##
## Ordre de décision (jamais les deux à la fois sur le même coup) :
##  1. Enchaînement détecté (STAGGER_TRIGGER_HITS coups en moins de
##     STAGGER_WINDOW_TICKS) -> arme le chancellement, qui prendra le
##     relais APRÈS que le recul (+ projection/rebond éventuels) de CE
##     coup se soit terminé (cf. _physics_process) — jamais à la place,
##     l'impact de ce coup précis reste visible avant le vacillement.
##  2. Sinon, pose d'impact directionnelle immédiate (les 4 directions
##     minimum du mandat) ; si ce monstre a une anim "projete"
##     (monstre LÉGER, cf. doc au-dessus de _pending_projection), elle
##     prendra le relais après IMPACT_POSE_HOLD_TICKS, gérée par
##     _physics_process — jamais posée ici directement, elle dépend du
##     déroulé du recul qui vient tout juste d'être armé par
##     take_damage() au-dessus de cet appel.
func _on_hit_reaction(away: Vector2) -> void:
	var incoming: Vector2 = -away
	var now_tick: int = Engine.get_physics_frames()
	if now_tick - _last_hit_tick <= STAGGER_WINDOW_TICKS:
		_consecutive_hits += 1
	else:
		_consecutive_hits = 1
	_last_hit_tick = now_tick

	var reaction: Dictionary = _select_directional_reaction(incoming)
	_apply_hit_reaction(reaction["anim"], reaction["flip"])

	if _visual is AnimatedSprite2D:
		var sprite: AnimatedSprite2D = _visual
		_pending_projection = sprite.sprite_frames != null and sprite.sprite_frames.has_animation("projete")
	_projection_pose_active = false

	if _consecutive_hits >= STAGGER_TRIGGER_HITS:
		_consecutive_hits = 0
		if _visual is AnimatedSprite2D:
			var sprite2: AnimatedSprite2D = _visual
			if sprite2.sprite_frames != null and sprite2.sprite_frames.has_animation("chancelle"):
				# Armé tout de suite MAIS consommé seulement une fois le
				# recul (+ rebond éventuel) de CE coup écoulé — le gate de
				# _physics_process vérifie le recul et le rebond AVANT le
				# chancellement (ordre des `if`/`return` ci-dessus), donc
				# _stagger_tick ne commence à avancer qu'après, jamais en
				# coupant la pose d'impact/projection de ce même coup.
				_pre_stagger_flip_h = sprite2.flip_h
				_stagger_tick = 0
				_stagger_total_ticks = STAGGER_DURATION_TICKS


## Sélectionne la réaction directionnelle (4 directions minimum, GDD
## Chantier C) selon l'axe DOMINANT de `incoming` (direction vers
## l'attaquant) : latéral (gauche/droite, un seul pose "touche_lateral"
## + flip_h — canonique = coup venu de la DROITE, non-flippé) sinon
## avant/arrière. "Avant" = l'attaquant est du côté caméra (Y+, plus
## proche du joueur qui regarde l'écran) — "arrière" = à l'opposé (Y-) ;
## convention arbitraire mais fixée UNE fois ici, jamais réinterprétée
## ailleurs.
func _select_directional_reaction(incoming: Vector2) -> Dictionary:
	if absf(incoming.x) >= absf(incoming.y):
		return {"anim": "touche_lateral", "flip": incoming.x < 0.0}
	if incoming.y < 0.0:
		return {"anim": "touche_arriere", "flip": _visual is AnimatedSprite2D and (_visual as AnimatedSprite2D).flip_h}
	return {"anim": "touche_avant", "flip": _visual is AnimatedSprite2D and (_visual as AnimatedSprite2D).flip_h}


## Joue `anim_name` immédiatement si ce monstre l'a dans son SpriteFrames
## (silencieux sinon, même discipline que _play_visual_animation()) —
## une seule frame par réaction (idle/attaque/mort le sont déjà dans ce
## pipeline), donc `sprite.play()` seul suffit pour un affichage
## tick-exact : rien à faire avancer, aucune FPS autonome à contourner.
func _apply_hit_reaction(anim_name: String, flip: bool) -> void:
	if not (_visual is AnimatedSprite2D):
		return
	var sprite: AnimatedSprite2D = _visual
	if sprite.sprite_frames == null or not sprite.sprite_frames.has_animation(anim_name):
		return
	sprite.flip_h = flip
	sprite.play(anim_name)


## Rebond procédural post-projection (monstres légers) — décalage
## vertical du sprite en cloche (sin, pic à mi-parcours), même technique
## que le bob de marche (_update_visual_bob()) : aucune frame
## supplémentaire, piloté tick par tick (jamais un Tween en temps réel,
## même discipline que le reste de ce fichier).
func _advance_bounce() -> void:
	if not (_visual is AnimatedSprite2D):
		return
	var sprite: AnimatedSprite2D = _visual
	var t: float = float(_bounce_tick) / float(BOUNCE_DURATION_TICKS)
	sprite.position.y = -sin(PI * t) * BOUNCE_HEIGHT_PX
	if _bounce_tick >= _bounce_total_ticks:
		sprite.position.y = 0.0
		if sprite.sprite_frames != null and sprite.sprite_frames.has_animation("chancelle") and _stagger_total_ticks > 0 and _stagger_tick == 0:
			pass  # le chancellement (déjà armé par _on_hit_reaction) prend le relais au tick suivant, via le gate de _physics_process
		else:
			_play_visual_animation("idle")


## Chancellement (enchaînement de coups) — pose "chancelle" tenue tout le
## long, flip_h basculé à cadence FIXE (STAGGER_FLIP_PERIOD_TICKS,
## jamais le FPS autonome — même discipline tick-exact que
## <SKILL>_FRAME_TICK_BOUNDS côté Player) pour simuler un vacillement
## gauche-droite sans frame supplémentaire. Restaure le flip_h
## pré-chancellement en sortie (sinon un ennemi immobile resterait
## flippé au hasard jusqu'à son prochain déplacement, _update_visual_bob()
## ne touchant flip_h qu'en State.CHASE).
func _advance_stagger() -> void:
	if not (_visual is AnimatedSprite2D):
		return
	var sprite: AnimatedSprite2D = _visual
	if sprite.sprite_frames == null or not sprite.sprite_frames.has_animation("chancelle"):
		_stagger_tick = 0
		_stagger_total_ticks = 0
		return
	if sprite.animation != &"chancelle":
		sprite.play("chancelle")
	var phase: int = (_stagger_tick / STAGGER_FLIP_PERIOD_TICKS) % 2
	sprite.flip_h = _pre_stagger_flip_h != (phase == 1)
	if _stagger_tick >= _stagger_total_ticks:
		sprite.flip_h = _pre_stagger_flip_h
		_stagger_tick = 0
		_stagger_total_ticks = 0
		_play_visual_animation("idle")


## MANDAT AUTONOME v3 Phase 2 (Meshy/Blender) : les 3 archétypes ont
## maintenant une vraie animation "marche" (Ranged : marche+course
## incluses gratuitement dans son rig Meshy déjà payé ; Crawler/Brute :
## 4 poses clés à la main sur leur rig manuel déjà validé, aucun
## crédit). Le bob procédural devient un repli, jamais supprimé — un
## futur archétype sans "marche" dans son SpriteFrames continue de
## bouger visiblement au lieu de rester figé, même discipline que
## `_play_visual_animation()`.
func _update_visual_bob() -> void:
	if not (_visual is AnimatedSprite2D):
		return
	var sprite: AnimatedSprite2D = _visual
	var has_walk_anim: bool = sprite.sprite_frames != null and sprite.sprite_frames.has_animation("marche")
	if _state == State.CHASE and velocity != Vector2.ZERO:
		if has_walk_anim:
			if sprite.animation != &"marche":
				sprite.play("marche")
			sprite.position.y = 0.0
		else:
			_move_tick += 1
			sprite.position.y = sin(float(_move_tick) / BOB_PERIOD_TICKS * TAU) * BOB_AMPLITUDE_PX
		if absf(velocity.x) > 0.0001:
			sprite.flip_h = velocity.x < 0.0
	else:
		_move_tick = 0
		sprite.position.y = 0.0
		if has_walk_anim and sprite.animation == &"marche":
			sprite.play("idle")
		sprite.position.y = 0.0


## MELEE : contact direct sur le joueur, même schéma que Player._try_hit()
## (take_damage + hit-stop/shake symétriques, jamais un 2e système de
## feedback dupliqué). Marge de 1.5x sur attack_range_px : le joueur a pu
## bouger pendant l'anticipation (dash/esquive) — un léger débordement
## reste un contact valide, une fuite complète non (pas de "swing à
## vide" chiffré séparément ici, contrairement au combo joueur — hors
## scope de cette brique).
## RANGED : instancie un projectile en ligne droite vers la position du
## joueur AU MOMENT du tir (pas de homing — même discipline "jamais un
## bruit isotrope", une trajectoire prévisible est ce qui rend un
## ennemi à distance lisible/évitable).
func _execute_attack(player: Node, to_player: Vector2) -> void:
	_reset_visual_color()
	var dir: Vector2 = to_player.normalized() if to_player.length_squared() > 0.0001 else Vector2.RIGHT
	match archetype:
		Archetype.MELEE:
			if global_position.distance_to(player.global_position) <= attack_range_px * 1.5:
				player.take_damage(contact_damage, global_position, contact_recoil_px)
				# Phase R4 : point d'entrée unique register_hit() — même
				# seuil que Player._try_hit() pour SFX/camera-punch
				# ("light" vs le reste), et camera-punch ENFIN présent sur
				# les coups ennemis (trou confirmé par audit : AUCUNE
				# attaque ennemie ne zoomait la caméra jusqu'ici, seules
				# les attaques du joueur le faisaient).
				CombatFeedback.register_hit(
					hitstop_profile, false,
					"light_impact" if hitstop_profile == "light" else "heavy_impact",
					shake_profile, dir,
					hitstop_profile != "light" and hitstop_profile != "none")
		Archetype.RANGED:
			_spawn_projectile(dir)
	_state = State.RECOVER
	_state_tick = 0


func _spawn_projectile(direction: Vector2) -> void:
	var proj: Node2D = ProjectileScene.instantiate()
	get_parent().add_child(proj)
	proj.global_position = global_position
	proj.configure(direction, projectile_speed_px_s, projectile_damage, hitstop_profile, shake_profile)
