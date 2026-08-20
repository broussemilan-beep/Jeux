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

## Esquive (mandat production v1 §1.3, décision Milan : "Dash ET esquive —
## deux actions séparées") — roulade/pas d'évitement avec i-frames, DISTINCTE
## du dash (pas un renommage). Même construction en 3 phases que le dash
## ci-dessus (anticipation -> déplacement ease-out -> recovery qui glisse),
## mais des proportions différentes : anticipation minimale (l'esquive doit
## répondre vite, c'est une réaction au danger), fenêtre active plus longue
## que le MOVE du dash (le joueur "paie" pour l'invincibilité par une
## recovery un peu plus engagée qu'un simple déplacement), distance plus
## courte que le dash (un "pas d'évitement", pas un sprint). Valeurs de
## départ TUNABLE (mandat §1.3 : "cooldown éventuel TUNABLE"), à ajuster
## une fois testées en jeu réel, jamais un dogme.
const DODGE_ANTICIPATION_TICKS := 2
const DODGE_ACTIVE_TICKS := 8
const DODGE_RECOVERY_TICKS := 6
const DODGE_DISTANCE_PX := 56.0
## Même schéma que DASH_RECOVERY_INITIAL_SPEED_PX_S, à l'échelle de la
## distance plus courte de l'esquive.
const DODGE_RECOVERY_INITIAL_SPEED_PX_S := 150.0
## Cooldown avant de pouvoir ré-esquiver — évite un spam d'i-frames en
## boucle (aucun combat réel n'exerce encore ce garde-fou, mais mieux vaut
## le poser maintenant que devoir le retrofitter une fois que G y branche
## de vraies attaques ennemies).
const DODGE_COOLDOWN_TICKS := 30

## Traînée (mandat B4/J2 : "opacité ~50% puis ~20%") — ce n'est PAS une
## primitive VfxDirector (contrat seed/configure générique, §7.1) : une
## after-image lit la texture/frame COURANTE du sprite du joueur, une
## donnée que seul Player possède, pas quelque chose qu'une recette JSON
## peut décrire (voir _spawn_afterimage() plus bas ; QUAND spawner, en
## revanche, est bien data-driven — _apply_afterimages() ci-dessus).
## Durée de fondu d'une after-image (Tween, temps réel — cohérent avec
## _spawn_afterimage() ci-dessous, un effet purement cosmétique, pas un
## système de combat qui doit rester en ticks purs). Le TIMING de
## déclenchement (quels ticks, combien, avec quelle opacité de départ)
## est lui data-driven depuis data/animation_composer/cendre.json (J2,
## mandat production v1 §4) — migré depuis les anciennes constantes
## DASH_AFTERIMAGE_TICKS/OPACITIES codées en dur, source unique désormais,
## et réutilisé par le combo (coup3) en plus du dash.
const AFTERIMAGE_FADE_SEC := 0.15

const GueuleVideScene := preload("res://scenes/gameplay/powers/gueule_vide.tscn")

## Invocation "Gueule Vide" (INVOCATEUR, data/recipes/power.gueule_vide.cast.json) :
## "Portée d'invocation : 4m". La créature apparaît à une distance fixe
## (3m) dans l'axe du regard (facing), laissant sa propre zone d'attaque
## (~1,5m) porter le reste de la portée totale sans la dépasser.
## "Cooldown suggéré : 6s" -> 360 ticks @ 60/s.
const POWER1_SPAWN_DISTANCE_PX := 96.0  # GameConstants.meters_to_px(3.0)
const POWER1_COOLDOWN_TICKS := 360  # 6s @ 60/s

## Bras-Faux (GDD §7.1, Parasite) — archétype de cast "frappe de zone"
## (mandat production v1 §5) : EXÉCUTÉ PAR LE JOUEUR (contrairement à
## Gueule Vide, une entité invoquée séparée), un seul balayage qui touche
## potentiellement plusieurs ennemis dans un cône, jamais une entité qui
## vit sa propre vie après le cast. "Portée ~1,5m, arc ~90°, durée
## ~0,5-0,7s, une frappe, aucun déplacement automatique" — 40 ticks
## (0,667s) : 14 anticipation (le membre se transforme) / 4 release
## (le balayage, contact au 1er tick comme le combo) / 22 recovery (le
## parasite se rétracte). Dégâts non chiffrés par la fiche (même statut
## que Gueule Vide, ATTACK_DAMAGE ci-dessus) : alignés sur le combo par
## défaut, à faire trancher par Milan. Cooldown NON chiffré par le GDD
## (contrairement à Gueule Vide, "cooldown suggéré 6s") — valeur de
## départ TUNABLE, plus courte que Gueule Vide (compétence de mêlée plus
## légère qu'une invocation), à ajuster une fois testée en jeu réel.
const BRAS_FAUX_ANTICIPATION_TICKS := 14
const BRAS_FAUX_RELEASE_TICKS := 4
const BRAS_FAUX_RECOVERY_TICKS := 22
const BRAS_FAUX_RANGE_PX := 48.0  # ~1.5m, GameConstants.PX_PER_METER
const BRAS_FAUX_HALF_ANGLE_DEG := 45.0  # arc total ~90°
const BRAS_FAUX_DAMAGE := 10.0
const BRAS_FAUX_COOLDOWN_TICKS := 180  # 3s @ 60/s, TUNABLE (non chiffré par le GDD)
const BrasFauxRecipeId := "power.bras_faux.cast"
const BRAS_FAUX_CAST_SEED := 51001  # Addendum A §A.5 : jamais l'horloge murale, même discipline que GueuleVide.CAST_SEED.

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

## Même rôle que _combo_step_absolute_tick : continu sur toute la
## timeline ANTICIPATION+MOVE+RECOVERY du dash (0 au premier tick),
## indépendant des remises à zéro de `_dash_tick` par phase — squash/lean/
## afterimages du dash (J2) s'expriment sur cette timeline continue.
var _dash_step_absolute_tick: int = 0

## Même discipline que DashPhase : NONE = pas d'esquive en cours. ACTIVE est
## la SEULE phase où is_invincible() renvoie true — l'anticipation et la
## recovery n'accordent aucun i-frame (mandat §1.3 : "roulade... avec
## frames d'invincibilité", pas une invincibilité de bout en bout de
## l'action).
enum DodgePhase { NONE, ANTICIPATION, ACTIVE, RECOVERY }
var _dodge_phase: int = DodgePhase.NONE
var _dodge_tick: int = 0
var _dodge_direction: Vector2 = Vector2.ZERO
var _dodge_recovery_velocity: Vector2 = Vector2.ZERO
var _dodge_step_absolute_tick: int = 0
var _dodge_cooldown_remaining: int = 0

## Gueule Vide n'utilise PAS _action_lock : l'invocation (0,7s) n'immobilise
## pas le joueur (rien dans le mandat ne l'exige, contrairement au combo/
## dash) — seul un cooldown la borne dans le temps.
var _power1_cooldown_remaining: int = 0

## Bras-Faux — même discipline de timeline que le combo/dash/esquive
## (ANTICIPATION/RELEASE/RECOVERY, _action_lock pendant toute l'action :
## contrairement à Gueule Vide, "aucun déplacement automatique" du GDD
## implique que le joueur reste engagé dans son geste, pas libre de
## bouger pendant qu'il balaie).
enum BrasFauxPhase { NONE, ANTICIPATION, RELEASE, RECOVERY }
var _bras_faux_phase: int = BrasFauxPhase.NONE
var _bras_faux_tick: int = 0
var _bras_faux_hit_applied: bool = false
var _bras_faux_cooldown_remaining: int = 0

## Recul du joueur sous un coup ennemi (G, GDD §10 — voir take_damage()
## ci-dessous) : même construction qu'Enemy._recoil_ticks_remaining, mais
## portée par sa propre timeline (ACTIVE/NONE) au lieu d'une simple
## variable de compte à rebours, pour ne pas se faire écraser par
## _handle_movement() au tick suivant (§16.3, même piège que dash/dodge —
## voir le commentaire historique sur take_damage() plus bas).
enum HurtPhase { NONE, ACTIVE }
var _hurt_phase: int = HurtPhase.NONE
var _hurt_ticks_remaining: int = 0
var _hurt_recoil_velocity: Vector2 = Vector2.ZERO

@onready var _sprite: AnimatedSprite2D = $AnimatedSprite2D
@onready var _camera: Camera2D = $Camera2D


func _ready() -> void:
	add_to_group("player")
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
	# Le shake ET le punch-zoom continuent de s'appliquer PENDANT un
	# hit-stop (c'est en partie ce qui vend l'impact) — lus avant le
	# retour anticipé ci-dessous, jamais après. Lookahead (mandat
	# production v1 §4, CameraDirector, J2) : direction du dash en cours
	# uniquement, Vector2.ZERO sinon (get_lookahead_offset() le gère déjà).
	var lookahead: Vector2 = CameraDirector.get_lookahead_offset(
		_dash_direction if _dash_phase != DashPhase.NONE else Vector2.ZERO)
	_camera.offset = CombatFeedback.get_shake_offset() + lookahead
	_camera.zoom = CameraDirector.get_punch_zoom()
	if CombatFeedback.is_frozen():
		return

	if _power1_cooldown_remaining > 0:
		_power1_cooldown_remaining -= 1
	if _dodge_cooldown_remaining > 0:
		_dodge_cooldown_remaining -= 1
	if _bras_faux_cooldown_remaining > 0:
		_bras_faux_cooldown_remaining -= 1

	if Input.is_action_just_pressed("attack"):
		_attack_queued = true

	if Input.is_action_just_pressed("power1") and not stats.is_dead() and _power1_cooldown_remaining <= 0:
		_cast_gueule_vide()

	if Input.is_action_just_pressed("power2"):
		_start_bras_faux()

	if Input.is_action_just_pressed("dash"):
		play_dash()

	if Input.is_action_just_pressed("dodge"):
		play_dodge()

	if _dash_phase != DashPhase.NONE:
		_advance_dash()
	elif _dodge_phase != DodgePhase.NONE:
		_advance_dodge()
	elif _bras_faux_phase != BrasFauxPhase.NONE:
		_advance_bras_faux()
	elif _combo_step > 0:
		_advance_combo()
	elif _hurt_phase != HurtPhase.NONE:
		_advance_hurt()
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

	if not _action_lock and not stats.is_dead():
		# E (mandat production v1 §6) : art réel par direction pour idle/
		# déplacement (8 rotations PixelLab, plus de flip_h ici — contrairement
		# au combo/dash/esquive qui restent "sud" seul + flip_h, hors scope
		# de cette brique, §6 "dash/combo/esquive si budget PixelLab, sinon
		# flag"). flip_h à false explicitement : sans ça la valeur laissée
		# par la dernière attaque (_start_attack, qui se flip elle-même
		# indépendamment depuis ce fix) doublerait le miroir sur un art
		# ouest déjà dessiné tel quel.
		_sprite.flip_h = false
		var suffix := _direction_suffix(facing)
		_sprite.play(("deplacement_" if input_dir.length_squared() > 0.0001 else "idle_") + suffix)


## Snappe une direction sur le compas à 8 branches le plus proche, dans la
## même convention que les rotations PixelLab (south/south_east/east/...) —
## Y+ = bas = sud (convention écran Godot, cohérente avec DodgeDirection/
## facing par défaut = Vector2.DOWN = "south").
static func _direction_suffix(dir: Vector2) -> String:
	if dir.length_squared() < 0.0001:
		return "south"
	const SUFFIXES := ["east", "south_east", "south", "south_west", "west", "north_west", "north", "north_east"]
	var octant: int = int(round(rad_to_deg(dir.angle()) / 45.0)) % 8
	if octant < 0:
		octant += 8
	return SUFFIXES[octant]


func _start_attack(step: int) -> void:
	_combo_step = step
	_combo_phase = ComboPhase.ANTICIPATION
	_combo_tick = 0
	_combo_step_absolute_tick = 0
	_hit_applied_this_release = false
	_action_lock = true
	# Auto-contenu (comme play_dash()/play_dodge()) plutôt que de dépendre du
	# flip_h laissé par le dernier _handle_movement() : depuis E (§6), ce
	# dernier remet flip_h à false à CHAQUE tick de mouvement (l'art
	# idle/déplacement est maintenant dessiné par direction, plus par
	# miroir) — le combo, encore art "sud" seul, doit se flipper lui-même
	# pour rester correct face à l'ouest.
	if facing.x != 0.0:
		_sprite.flip_h = facing.x < 0.0
	_sprite.play(AttackAnimName[step - 1])


## Timeline déclarative du coup courant — ANTICIPATION -> RELEASE (frappe
## au premier tick) -> RECOVERY (fenêtre de chaînage sur les derniers
## CHAIN_WINDOW_TICKS). Ne dépend jamais de la durée réelle de lecture du
## sprite, uniquement des compteurs de ticks ci-dessous — sinon changer la
## fps d'une anim de coup déréglerait silencieusement le combat.
func _advance_combo() -> void:
	_combo_tick += 1
	_combo_step_absolute_tick += 1
	var anim_data: Dictionary = {}
	if _combo_step >= 1 and _combo_step <= AttackAnimName.size():
		anim_data = _animation_composer_data.get(AttackAnimName[_combo_step - 1], {})
	_apply_combo_root_motion(anim_data, _combo_step_absolute_tick)
	_apply_squash_lean_afterimages(anim_data, _combo_step_absolute_tick)
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
func _apply_combo_root_motion(anim_data: Dictionary, abs_tick: int) -> void:
	velocity = Vector2.ZERO
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


## AnimationComposer (mandat production v1 §4/J2) : squash (impulsion
## d'échelle, aussi utilisée comme "smear" mandat J2 pour coup3, voir
## _squash_notes du JSON) + lean (bascule de rotation, réutilise la même
## fenêtre que root_motion — le lean accompagne le même engagement dans
## le coup) + afterimages (traînée, réservée à coup3 pour l'instant).
## `sprite.scale`/`rotation_degrees` sont remis à leur valeur neutre par
## AnimationComposer lui-même quand `anim_data` est vide ou hors fenêtre —
## jamais besoin de les réinitialiser ici en plus.
func _apply_squash_lean_afterimages(anim_data: Dictionary, abs_tick: int) -> void:
	AnimationComposer.apply_squash(_sprite, anim_data.get("squash", []), abs_tick)
	var rm: Dictionary = anim_data.get("root_motion", {})
	AnimationComposer.apply_lean(_sprite, float(anim_data.get("lean_deg", 0.0)), facing,
		int(rm.get("start_tick", 0)), int(rm.get("end_tick", 0)), abs_tick)
	_apply_afterimages(anim_data, abs_tick)


## `afterimages` (data/animation_composer/cendre.json, _afterimages_notes) :
## { count, start_tick, spacing_ticks, opacities } — spawn un fantôme à
## chaque tick start_tick + i*spacing_ticks pour i in [0, count).
func _apply_afterimages(anim_data: Dictionary, abs_tick: int) -> void:
	var ai: Dictionary = anim_data.get("afterimages", {})
	if ai.is_empty():
		return
	var count: int = int(ai.get("count", 0))
	var start_tick: int = int(ai.get("start_tick", 0))
	var spacing: int = maxi(1, int(ai.get("spacing_ticks", 1)))
	var opacities: Array = ai.get("opacities", [])
	for i in count:
		if abs_tick == start_tick + i * spacing:
			var opacity: float = float(opacities[i]) if i < opacities.size() else 0.3
			_spawn_afterimage(opacity)
			return


func _end_combo() -> void:
	_combo_step = 0
	_combo_phase = ComboPhase.NONE
	_combo_tick = 0
	_attack_queued = false
	_action_lock = false
	# Garde-fou : squash/lean (J2) devraient déjà être retombés à neutre
	# avant la fin de la timeline (fenêtres toujours closes bien avant
	# RECOVERY_TICKS dans data/animation_composer/cendre.json), mais un
	# oubli de configuration future ne doit jamais laisser le sprite figé
	# étiré/penché en idle.
	_sprite.scale = Vector2.ONE
	_sprite.rotation_degrees = 0.0


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

	# CameraDirector (mandat production v1 §4/J2) : punch-zoom sur les
	# impacts "medium+" — mêmes seuils que le hit-stop existant (jamais un
	# 2e système de seuils dupliqué), "light" exclu.
	if tier["hitstop"] != "light" and tier["hitstop"] != "none":
		CameraDirector.trigger_punch()

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


## Bras-Faux (GDD §7.1) — archétype "frappe de zone" : contrairement à
## _cast_gueule_vide() (une entité séparée qui vit sa propre timeline),
## le joueur EST l'exécutant, sur sa propre timeline de ticks (même
## discipline que _start_attack()/play_dash()/play_dodge()). Rejette la
## même façon que ces autres actions verrouillées : mort, déjà engagé
## dans une autre action, ou cooldown.
##
## Placeholder visuel : réutilise l'anim "coup2" (le balayage tournant
## existant est visuellement le plus proche d'un "seul balayage" avec
## bras tendu — mandat §5 : "asset dédié seulement pour... une
## transformation corporelle [Bras-Faux]", l'art dédié reste à générer,
## pas dans le scope recette+logique de cette brique).
func _start_bras_faux() -> void:
	if stats.is_dead() or _action_lock or _bras_faux_cooldown_remaining > 0:
		return
	_action_lock = true
	_bras_faux_phase = BrasFauxPhase.ANTICIPATION
	_bras_faux_tick = 0
	_bras_faux_hit_applied = false
	_sprite.play("coup2")

	var dir := facing
	if dir.length_squared() < 0.0001:
		dir = Vector2.DOWN
	dir = dir.normalized()
	VfxRecipeRegistry.play(BrasFauxRecipeId, {
		"origin": global_position,
		"seed": BRAS_FAUX_CAST_SEED,
		"direction": dir,
	})


## Timeline déclarative (ANTICIPATION -> RELEASE, contact au 1er tick,
## même convention que _advance_combo() -> RECOVERY) — jamais dépendante
## de la durée réelle de lecture du sprite ("coup2" a sa propre fps,
## potentiellement désynchronisée des bornes ci-dessous, comme documenté
## pour le combo).
func _advance_bras_faux() -> void:
	_bras_faux_tick += 1
	velocity = Vector2.ZERO  # "aucun déplacement automatique" (GDD §7.1) — jamais de root motion ici.
	match _bras_faux_phase:
		BrasFauxPhase.ANTICIPATION:
			if _bras_faux_tick >= BRAS_FAUX_ANTICIPATION_TICKS:
				_bras_faux_phase = BrasFauxPhase.RELEASE
				_bras_faux_tick = 0
		BrasFauxPhase.RELEASE:
			if _bras_faux_tick == 1 and not _bras_faux_hit_applied:
				_try_hit_bras_faux()
				_bras_faux_hit_applied = true
			if _bras_faux_tick >= BRAS_FAUX_RELEASE_TICKS:
				_bras_faux_phase = BrasFauxPhase.RECOVERY
				_bras_faux_tick = 0
		BrasFauxPhase.RECOVERY:
			if _bras_faux_tick >= BRAS_FAUX_RECOVERY_TICKS:
				_end_bras_faux()


func _end_bras_faux() -> void:
	_bras_faux_phase = BrasFauxPhase.NONE
	_bras_faux_tick = 0
	_action_lock = false
	_bras_faux_cooldown_remaining = BRAS_FAUX_COOLDOWN_TICKS


## "Frappe de zone" : TOUS les ennemis vivants dans l'arc, pas un seul
## (Targeting.enemies_in_arc(), pas nearest_enemy_in_radius()) — la
## distinction qui fait l'identité de cet archétype face au combo/Gueule
## Vide (une seule cible chacun). Recul individuel sur CHAQUE cible
## touchée (GDD §7.1 : "chaque coup qui touche impose un recul visible"),
## via Enemy.take_damage() comme pour le combo — jamais une primitive de
## la recette (data/recipes/power.bras_faux.cast.json, notes).
func _try_hit_bras_faux() -> void:
	var dir := facing
	if dir.length_squared() < 0.0001:
		dir = Vector2.DOWN
	dir = dir.normalized()
	var targets: Array = Targeting.enemies_in_arc(get_tree(), global_position, dir, BRAS_FAUX_RANGE_PX, BRAS_FAUX_HALF_ANGLE_DEG)
	if targets.is_empty():
		return
	for target in targets:
		target.take_damage(BRAS_FAUX_DAMAGE, global_position)

	# Même tier que Gueule Vide (tous deux importance_tier 2/6, feedback
	# "medium" dans les deux recettes) — pas un second barème de hit-stop.
	CombatFeedback.trigger_hitstop("medium")
	CameraDirector.trigger_punch()


func is_dead() -> bool:
	return stats.is_dead()


## Mandat production v1 §1.3 : "roulade... avec frames d'invincibilité (i-
## frames) dans la logique de dégâts." Vrai UNIQUEMENT pendant DodgePhase.
## ACTIVE — jamais pendant l'anticipation (le joueur n'a pas encore bougé)
## ni la recovery (il "paie" sa fenêtre d'invincibilité en restant
## vulnérable le temps de se relever).
func is_invincible() -> bool:
	return _dodge_phase == DodgePhase.ACTIVE


## Réaction à un coup subi. Même signature qu'Enemy.take_damage() (source_
## position + recoil_strength_px/recoil_ticks pour orienter le recul,
## cohérence entre les deux entités qui peuvent encaisser un coup) —
## appelée pour de vrai depuis G (Crawler/Brute/Ranged, GDD §10) : le
## recul manquait jusqu'ici (voir _advance_hurt() ci-dessous, qui règle
## le piège documenté par le commentaire historique — _handle_movement()
## écraserait `velocity` au tick suivant sans sa propre timeline).
##
## Si le joueur est DÉJÀ engagé dans une autre timeline (combo/dash/
## esquive/Bras-Faux — `_action_lock` déjà vrai), les dégâts/flash/
## chiffre/mort s'appliquent quand même, mais SANS superposer un recul
## cosmétique par-dessus une timeline en cours (le corrompre est pire que
## l'omettre) — scope volontairement limité pour cette brique G, à
## reconsidérer si Milan le juge insuffisant en jeu réel.
func take_damage(amount: float, source_position: Vector2, recoil_strength_px: float = 24.0, recoil_ticks: int = 6) -> void:
	if stats.is_dead() or is_invincible():
		return
	stats.apply_damage(amount)
	HitResponse.flash_sprite(_sprite)
	HitResponse.spawn_damage_number(amount, global_position, get_parent())
	if stats.is_dead():
		die()
		return
	if _action_lock:
		return
	var away: Vector2 = (global_position - source_position)
	if away.length_squared() < 0.0001:
		away = Vector2.RIGHT
	away = away.normalized()
	_hurt_recoil_velocity = away * (recoil_strength_px * Engine.physics_ticks_per_second / max(1, recoil_ticks))
	_hurt_ticks_remaining = recoil_ticks
	_hurt_phase = HurtPhase.ACTIVE
	play_hurt()


## Réaction à un coup subi — pose juste l'animation/le verrou ; le recul
## lui-même vit dans _advance_hurt() (timeline dédiée, comme dash/dodge).
func play_hurt() -> void:
	if stats.is_dead():
		return
	_action_lock = true
	_sprite.play("hurt")


## Timeline de recul (G) — même construction que le recul d'Enemy
## (_recoil_ticks_remaining) : `move_toward` linéaire vers zéro sur les
## ticks restants, mais posée comme phase à part (ACTIVE/NONE) pour être
## consultée par le if/elif de _physics_process() AVANT _handle_movement(),
## qui écraserait sinon `velocity` dès ce même tick si une touche de
## mouvement est tenue.
func _advance_hurt() -> void:
	if _hurt_ticks_remaining > 0:
		velocity = _hurt_recoil_velocity
		_hurt_recoil_velocity = _hurt_recoil_velocity.move_toward(Vector2.ZERO, _hurt_recoil_velocity.length() / max(1, _hurt_ticks_remaining))
		_hurt_ticks_remaining -= 1
	if _hurt_ticks_remaining <= 0:
		_end_hurt()


func _end_hurt() -> void:
	_hurt_phase = HurtPhase.NONE
	_hurt_ticks_remaining = 0
	velocity = Vector2.ZERO
	_action_lock = false


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
	_dash_step_absolute_tick = 0
	_sprite.play("dash")
	if _dash_direction.x != 0.0:
		_sprite.flip_h = _dash_direction.x < 0.0

	# "shake light dès le premier tick, axe opposé au déplacement" —
	# déclenché ici, au tout premier tick de l'action (l'anticipation),
	# pas seulement au moment où le déplacement démarre.
	CombatFeedback.trigger_shake("light", _dash_direction)


## Même règle de direction que play_dash() (input courant sinon facing,
## jamais nul) — l'esquive DOIT pouvoir se diriger, c'est tout son intérêt
## défensif (s'écarter d'une attaque, pas juste "avancer plus vite").
##
## Placeholder visuel (mandat §1.3 : "le squelette logique... se code
## immédiatement avec un placeholder visuel ; l'animation dédiée se génère
## avec le lot v3") : réutilise l'anim "dash" ET les données squash/lean/
## afterimages de "dash" dans data/animation_composer/cendre.json — l'
## esquive est visuellement un dash pour l'instant, mais logiquement une
## action séparée (sa propre timeline de ticks, son propre cooldown, ses
## propres i-frames). Remplacer par une vraie anim "esquive" dédiée reste
## à faire une fois le lot v3 régénéré (pas dans le scope de cette brique).
func play_dodge() -> void:
	if stats.is_dead() or _action_lock or _dodge_cooldown_remaining > 0:
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
	_dodge_direction = dir.normalized()

	_action_lock = true
	_dodge_phase = DodgePhase.ANTICIPATION
	_dodge_tick = 0
	_dodge_step_absolute_tick = 0
	_sprite.play("dash")
	if _dodge_direction.x != 0.0:
		_sprite.flip_h = _dodge_direction.x < 0.0


## Timeline déclarative du dash (B4) — ANTICIPATION (bref arrêt, buste
## "planté" avant le départ) -> MOVE (burst avec ease-out, DASH_DISTANCE_PX
## répartis sur DASH_MOVE_TICKS, pas une téléportation en un seul tick)
## -> RECOVERY (glissade qui décélère au sol, jamais un arrêt nul). Même
## discipline que _advance_combo() : ne dépend jamais de la durée réelle
## de lecture du sprite.
func _advance_dash() -> void:
	_dash_tick += 1
	_dash_step_absolute_tick += 1
	var dash_data: Dictionary = _animation_composer_data.get("dash", {})
	AnimationComposer.apply_squash(_sprite, dash_data.get("squash", []), _dash_step_absolute_tick)
	AnimationComposer.apply_lean(_sprite, float(dash_data.get("lean_deg", 0.0)), _dash_direction,
		int(dash_data.get("lean_start_tick", 0)), int(dash_data.get("lean_end_tick", 0)), _dash_step_absolute_tick)
	_apply_afterimages(dash_data, _dash_step_absolute_tick)
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
	# Même garde-fou que _end_combo() ci-dessus.
	_sprite.scale = Vector2.ONE
	_sprite.rotation_degrees = 0.0


## Timeline déclarative de l'esquive — même construction en 3 phases que
## _advance_dash() (anticipation plantée -> déplacement ease-out -> recovery
## qui glisse), mais SANS la moindre fenêtre d'i-frames en dehors de la
## phase ACTIVE (is_invincible() ci-dessus ne consulte que _dodge_phase).
## Réutilise les données squash/lean/afterimages de "dash" dans
## data/animation_composer/cendre.json (placeholder visuel, voir
## play_dodge()) — pas une nouvelle entrée JSON dupliquée pour l'instant.
func _advance_dodge() -> void:
	_dodge_tick += 1
	_dodge_step_absolute_tick += 1
	var dash_data: Dictionary = _animation_composer_data.get("dash", {})
	AnimationComposer.apply_squash(_sprite, dash_data.get("squash", []), _dodge_step_absolute_tick)
	AnimationComposer.apply_lean(_sprite, float(dash_data.get("lean_deg", 0.0)), _dodge_direction,
		int(dash_data.get("lean_start_tick", 0)), int(dash_data.get("lean_end_tick", 0)), _dodge_step_absolute_tick)
	_apply_afterimages(dash_data, _dodge_step_absolute_tick)
	match _dodge_phase:
		DodgePhase.ANTICIPATION:
			velocity = Vector2.ZERO
			if _dodge_tick >= DODGE_ANTICIPATION_TICKS:
				_dodge_phase = DodgePhase.ACTIVE
				_dodge_tick = 0
		DodgePhase.ACTIVE:
			var progress_before: float = _ease_out_quad(float(_dodge_tick - 1) / DODGE_ACTIVE_TICKS)
			var progress_after: float = _ease_out_quad(float(_dodge_tick) / DODGE_ACTIVE_TICKS)
			var step_px: float = (progress_after - progress_before) * DODGE_DISTANCE_PX
			velocity = _dodge_direction * (step_px * Engine.physics_ticks_per_second)
			if _dodge_tick >= DODGE_ACTIVE_TICKS:
				_dodge_phase = DodgePhase.RECOVERY
				_dodge_tick = 0
				_dodge_recovery_velocity = _dodge_direction * DODGE_RECOVERY_INITIAL_SPEED_PX_S
		DodgePhase.RECOVERY:
			velocity = _dodge_recovery_velocity
			_dodge_recovery_velocity = _dodge_recovery_velocity.move_toward(
				Vector2.ZERO, DODGE_RECOVERY_INITIAL_SPEED_PX_S / DODGE_RECOVERY_TICKS)
			if _dodge_tick >= DODGE_RECOVERY_TICKS:
				_end_dodge()


func _end_dodge() -> void:
	_dodge_phase = DodgePhase.NONE
	_dodge_tick = 0
	velocity = Vector2.ZERO
	_action_lock = false
	_dodge_cooldown_remaining = DODGE_COOLDOWN_TICKS
	# Même garde-fou que _end_combo()/_end_dash() ci-dessus.
	_sprite.scale = Vector2.ONE
	_sprite.rotation_degrees = 0.0


## Fantôme de traînée (B4, généralisé au combo en J2 — voir
## _apply_afterimages()) — PAS une primitive VfxDirector (§7.1, contrat
## seed/configure générique) : copie la texture/frame COURANTE du sprite
## du joueur, une donnée que seul Player possède. `Sprite2D` autonome,
## parenté au même parent que Player (jamais à Player lui-même, sinon il
## suivrait son mouvement au lieu de rester "planté" derrière lui) —
## s'éteint tout seul via un Tween sur son opacité, jamais géré par
## VfxDirector/VfxBudget (ce n'est pas dans leur périmètre, §8.2).
func _spawn_afterimage(opacity: float) -> void:
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
	tween.tween_property(ghost, "modulate:a", 0.0, AFTERIMAGE_FADE_SEC)
	tween.finished.connect(ghost.queue_free)


func _on_sprite_animation_finished() -> void:
	if _combo_step > 0:
		return  # le combo gère son propre verrou via sa timeline de ticks (_end_combo())
	if _dash_phase != DashPhase.NONE:
		return  # le dash gère son propre verrou via sa timeline de ticks (_end_dash())
	if _dodge_phase != DodgePhase.NONE:
		return  # l'esquive gère son propre verrou via sa timeline de ticks (_end_dodge())
	if _bras_faux_phase != BrasFauxPhase.NONE:
		return  # Bras-Faux gère son propre verrou via sa timeline de ticks (_end_bras_faux())
	if _hurt_phase != HurtPhase.NONE:
		return  # le recul gère son propre verrou via sa timeline de ticks (_end_hurt())
	if _sprite.animation == "mort":
		return  # reste sur la dernière frame, jamais reverrouillé sur idle
	_action_lock = false


func die() -> void:
	stats.hp = 0.0
	_combo_step = 0
	_combo_phase = ComboPhase.NONE
	_attack_queued = false
	_hurt_phase = HurtPhase.NONE
	_dash_phase = DashPhase.NONE
	_dodge_phase = DodgePhase.NONE
	_bras_faux_phase = BrasFauxPhase.NONE
	_action_lock = true
	_sprite.play("mort")
