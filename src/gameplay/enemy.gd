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
		var step_px: float = AnimationComposer.ease_out_step_px(_recoil_tick, _recoil_total_ticks, _recoil_total_distance_px)
		velocity = _recoil_direction * (step_px * Engine.physics_ticks_per_second)
		move_and_slide()
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
	var lerped: Color = _base_visual_color.lerp(Color(1.0, 1.0, 1.0, 1.0), clampf(progress, 0.0, 1.0))
	if _visual is Polygon2D:
		(_visual as Polygon2D).color = lerped
	elif _visual is AnimatedSprite2D:
		_visual.self_modulate = lerped


func _reset_visual_color() -> void:
	if _visual is Polygon2D:
		(_visual as Polygon2D).color = _base_visual_color
	elif _visual is AnimatedSprite2D:
		_visual.self_modulate = _base_visual_color


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
