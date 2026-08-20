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
