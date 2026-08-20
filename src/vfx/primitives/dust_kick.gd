extends Node2D
## Primitive "dustKick" — docs/ARCHITECTURE_VFX_v3.md §7.1 : "poussière au
## contact sol". Distincte de smokePuff (résidu qui traîne après coup,
## CONSEQUENCE) : ceci est le contact LUI-MÊME — un pied, un roulé, un
## atterrissage qui touche le sol MAINTENANT (dash/esquive/atterrissage).
## Bref, bas, anguleux (des éclats de poussière, pas un nuage) et
## directionnel — projeté à l'OPPOSÉ du mouvement (§4 : "recul de la
## cible... jamais un bruit isotrope", même logique appliquée ici au
## sol). Couche CONTACT (§4).

const MIN_VALUE_HSV := 0.20
const MAX_VALUE_HSV := 0.92
const KICK_COUNT := 5
const CONE_HALF_ANGLE := PI / 4.0  # 45° de part et d'autre de l'opposé du mouvement

var seed_val: int = 0
var lifetime_ticks: int = 7
var scale_px: float = 10.0
var origin: Vector2 = Vector2.ZERO
## Direction du DÉPLACEMENT qui a causé le contact — la poussière part à
## l'opposé, jamais dans le sens du mouvement.
var direction: Vector2 = Vector2.RIGHT
var _color: Color = Color.from_hsv(0.0, 0.0, 0.45, 1.0)

var _ticks_elapsed: int = 0
var _rng := RandomNumberGenerator.new()
var _kick_dirs: Array[Vector2] = []
var _kick_speeds: Array[float] = []
var _kick_sizes: Array[float] = []


func configure(params: Dictionary) -> void:
	seed_val = params.get("seed", 0)
	lifetime_ticks = maxi(1, int(params.get("lifetime_ticks", 7)))
	scale_px = params.get("scale_px", 10.0)
	origin = params.get("origin", Vector2.ZERO)
	position = origin
	direction = params.get("direction", Vector2.RIGHT)
	if direction.length_squared() < 0.0001:
		direction = Vector2.RIGHT
	direction = direction.normalized()
	z_index = 91  # CONTACT : au-dessus de fractureLine (90), sous ribbonTrail (94) — bas, discret, jamais dominant.

	var value_pct: float = clampf(params.get("value_percent", 45.0), 0.0, 100.0) / 100.0
	var hue_deg: float = params.get("hue_deg", 0.0)
	var sat_pct: float = clampf(params.get("saturation_percent", 0.0), 0.0, 100.0) / 100.0
	var v: float = clampf(value_pct, MIN_VALUE_HSV, MAX_VALUE_HSV)
	_color = Color.from_hsv(hue_deg / 360.0, sat_pct, v, 1.0)

	_rng.seed = seed_val
	var opposite: Vector2 = -direction
	_kick_dirs.clear()
	_kick_speeds.clear()
	_kick_sizes.clear()
	for i in KICK_COUNT:
		var a: float = (_rng.randf() * 2.0 - 1.0) * CONE_HALF_ANGLE
		_kick_dirs.append(opposite.rotated(a))
		_kick_speeds.append(scale_px * (0.5 + _rng.randf() * 0.5))
		_kick_sizes.append(1.5 + _rng.randf() * 1.5)


func tick(ticks_elapsed: int) -> void:
	_ticks_elapsed = ticks_elapsed
	queue_redraw()


func _draw() -> void:
	var t: float = clampf(float(_ticks_elapsed) / float(lifetime_ticks), 0.0, 1.0)
	var alpha: float = 1.0 - clampf((t - 0.5) / 0.5, 0.0, 1.0)
	if alpha <= 0.0:
		return
	var col := Color(_color.r, _color.g, _color.b, alpha)
	for i in KICK_COUNT:
		# Ease-out : rapide au contact, ralentit vite — un éclat de
		# poussière projeté, pas une translation à vitesse constante.
		var eased: float = 1.0 - (1.0 - t) * (1.0 - t)
		var p: Vector2 = _kick_dirs[i] * _kick_speeds[i] * eased
		draw_circle(p, _kick_sizes[i] * (1.0 - t * 0.4), col)
