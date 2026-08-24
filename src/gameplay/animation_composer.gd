extends RefCounted
class_name AnimationComposer
## Applique squash/lean depuis les données déclaratives de
## data/animation_composer/<perso>.json (mandat production v1 §4/J2) — pur,
## sans état interne : Player (ou toute future entité) possède le tick
## courant et le sprite, ce module se contente de calculer/appliquer sur
## commande, à CHAQUE tick de l'action en cours (jamais un Tween en temps
## réel — mêmes ticks purs que tout le reste du combat).
##
## afterimages n'est PAS géré ici : contrairement à squash/lean (des
## transformations pures du sprite), une after-image doit COPIER la
## texture/frame courante dans un nouveau nœud (Player._spawn_afterimage())
## — une donnée que seul l'appelant possède, cohérent avec la même
## distinction déjà posée pour root_motion (§7.1, "seul Player possède
## cette donnée"). Ce module se limite aux deux transformations qui
## peuvent être appliquées EN PLACE sur le sprite existant.

## Durée (en ticks) de la montée ET de la descente d'une impulsion
## squash/lean — même valeur pour les deux, pas une coïncidence : les deux
## suivent la même philosophie "exagérer puis redescendre" (matrice
## d'autonomie du mandat, section 3).
const EASE_TICKS := 3


static func ease_out_quad(x: float) -> float:
	var c: float = clampf(x, 0.0, 1.0)
	return 1.0 - (1.0 - c) * (1.0 - c)


## Sandbox de Milan ("knockback_return_curve: easeOut") : le recul devient
## une COURBE DE POSITION ease-out (vite puis qui s'adoucit) plutôt qu'une
## simple décroissance linéaire de vitesse (`move_toward` vers 0) — même
## technique que Player._advance_dash() (MOVE), la seule référence déjà
## éprouvée d'un déplacement en ticks purs qui suit ease_out_quad(),
## partagée ici pour ne pas la retaper 3 fois (Player.take_damage(),
## Enemy.take_damage(), BossGateMaw.take_damage()). `tick` = le tick qui
## VIENT d'être consommé (1-indexé, comme _dash_tick après incrémentation).
## Retourne la distance à parcourir CE tick (pas une vitesse) — l'appelant
## la convertit en vitesse via `* Engine.physics_ticks_per_second` pour
## rester compatible avec `velocity` + `move_and_slide()`.
static func ease_out_step_px(tick: int, total_ticks: int, total_distance_px: float) -> float:
	if total_ticks <= 0:
		return 0.0
	var progress_before: float = ease_out_quad(float(tick - 1) / float(total_ticks))
	var progress_after: float = ease_out_quad(float(tick) / float(total_ticks))
	return (progress_after - progress_before) * total_distance_px


## `keyframes` : la liste "squash" d'une animation (voir data/
## animation_composer/cendre.json, _squash_notes). Remet `sprite.scale` à
## (1,1) par défaut puis applique le PREMIER keyframe dont la fenêtre
## [tick-EASE_TICKS, tick+hold+EASE_TICKS] couvre `abs_tick` — un seul
## keyframe actif à la fois pour l'instant (aucune superposition gérée,
## suffisant tant qu'aucune donnée n'en définit plus d'un par animation).
static func apply_squash(sprite: Node2D, keyframes: Array, abs_tick: int) -> void:
	sprite.scale = Vector2.ONE
	for kf_variant in keyframes:
		var kf: Dictionary = kf_variant
		var peak_tick: int = int(kf.get("tick", 0))
		var hold: int = maxi(1, int(kf.get("hold", 1)))
		var target := Vector2(float(kf.get("x", 1.0)), float(kf.get("y", 1.0)))
		var in_start: int = peak_tick - EASE_TICKS
		var hold_end: int = peak_tick + hold
		var out_end: int = hold_end + EASE_TICKS
		if abs_tick < in_start or abs_tick > out_end:
			continue
		var t: float
		if abs_tick <= peak_tick:
			t = ease_out_quad(float(abs_tick - in_start) / EASE_TICKS)
		elif abs_tick <= hold_end:
			t = 1.0
		else:
			t = 1.0 - ease_out_quad(float(abs_tick - hold_end) / EASE_TICKS)
		sprite.scale = Vector2.ONE.lerp(target, t)
		return


## Smear procédural (mandat "fluidité", Partie 2, "smear frames
## procédurales") — étirement le long de l'axe du mouvement sur les
## déplacements rapides (dash/esquive), calculé à CHAQUE tick depuis la
## VITESSE RÉELLE du joueur, PAS depuis des keyframes pré-autorées comme
## `apply_squash` ci-dessus. Distinction volontaire entre les deux couches :
## `apply_squash` reste un beat ANIMÉ à la main (anticipation/impact posés
## dans data/animation_composer/<perso>.json), le smear est une fonction
## PURE de la vitesse instantanée — la même distinction qu'en animation
## traditionnelle entre une pose d'anticipation dessinée et une traînée de
## mouvement générée. Remplace, pour le dash/l'esquive, l'ancienne
## impulsion squash figée du JSON (x=1.3/y=0.75) qui étirait toujours
## l'axe HORIZONTAL peu importe la direction réelle du dash — juste pour
## un dash est/ouest, fausse dès qu'on quitte l'axe horizontal (un dash
## vers le nord s'étirait quand même en largeur). Zéro coût de génération
## (aucun asset dédié), juste une fonction du vecteur vitesse.
##
## Approximation par AXE DOMINANT (horizontal vs vertical) plutôt qu'une
## vraie rotation+scale+dérotation dans le repère du mouvement : plus
## simple, zéro conflit avec `apply_lean` (qui écrit `rotation_degrees`
## juste après dans l'appelant), et suffisant ici — l'art de Cendre pour
## dash/esquive reste dessiné "sud + flip_h" (jamais une vraie rotation
## vers la direction visée), donc étirer dans le repère LOCAL du sprite
## (pas un repère tourné vers `velocity`) garde le smear aligné avec la
## silhouette réellement affichée à l'écran plutôt qu'avec un repère que
## l'art ne suit pas.
const SMEAR_MAX_STRETCH := 0.35  # +35% dans l'axe dominant au pic de vitesse
const SMEAR_REFERENCE_SPEED_PX_S := 900.0  # vitesse à laquelle le smear plafonne (pic du dash, voir Player._advance_dash())

## `velocity` : vitesse RÉELLE du joueur pour CE tick (px/s, même valeur
## que `Player.velocity` juste après le calcul de la phase MOVE/ACTIVE).
## Ne touche PAS `sprite.scale` si la vitesse est quasi nulle — laisse la
## valeur déjà posée par `apply_squash()` (appelé avant, dans l'ordre où
## l'appelant les enchaîne) plutôt que de la forcer à IDENTITY : le smear
## est un effet ADDITIF sur les phases où le joueur bouge vraiment, pas un
## reset inconditionnel comme `apply_squash`/`apply_lean`.
static func apply_motion_smear(sprite: Node2D, velocity: Vector2) -> void:
	var speed: float = velocity.length()
	if speed < 1.0:
		return
	var t: float = clampf(speed / SMEAR_REFERENCE_SPEED_PX_S, 0.0, 1.0)
	var stretch: float = 1.0 + SMEAR_MAX_STRETCH * t
	# Compression légère de l'axe perpendiculaire (~moitié de l'étirement) —
	# approximation de conservation de volume, moins agressive que
	# l'étirement pour ne jamais donner l'impression d'un sprite qui
	# rétrécit plus qu'il ne s'étire.
	var squeeze: float = 1.0 - SMEAR_MAX_STRETCH * 0.5 * t
	if absf(velocity.x) >= absf(velocity.y):
		sprite.scale = Vector2(stretch, squeeze)
	else:
		sprite.scale = Vector2(squeeze, stretch)


## `lean_deg` : amplitude max (voir _lean_notes du JSON). Rampe symétrique
## sur [start_tick, end_tick] — monte jusqu'au milieu de la fenêtre, puis
## redescend. `facing` donne le signe (bascule dans le sens du mouvement/
## coup). Remet `sprite.rotation_degrees` à 0 par défaut.
static func apply_lean(sprite: Node2D, lean_deg: float, facing: Vector2, start_tick: int, end_tick: int, abs_tick: int) -> void:
	sprite.rotation_degrees = 0.0
	if lean_deg == 0.0 or end_tick <= start_tick:
		return
	if abs_tick < start_tick or abs_tick > end_tick:
		return
	var span: float = float(end_tick - start_tick)
	var mid: float = start_tick + span / 2.0
	var t: float
	if float(abs_tick) <= mid:
		t = ease_out_quad(float(abs_tick - start_tick) / maxf(1.0, mid - start_tick))
	else:
		t = 1.0 - ease_out_quad((float(abs_tick) - mid) / maxf(1.0, end_tick - mid))
	var sign: float = 1.0 if facing.x >= 0.0 else -1.0
	sprite.rotation_degrees = lean_deg * t * sign
