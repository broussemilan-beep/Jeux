extends Node2D
## Primitive "smokePuff" — docs/ARCHITECTURE_VFX_v3.md §7.1 : "nuage
## stylisé sans transparence floue". §10.2 : "Aucun dissolve par alpha
## fade seul : toujours une logique de retrait (fragments, aspiration,
## cendre, pixels, lignes)." — donc PAS un cercle dont l'alpha descend
## simplement à 0 : un petit nombre de blobs OPAQUES qui disparaissent un
## par un (retrait par comptage), jamais un flou. Couche CONSEQUENCE (§4) :
## résidu qui traîne après un impact ou un déplacement (§9.3 étape 5).

const MIN_VALUE_HSV := 0.20
const MAX_VALUE_HSV := 0.92
const BLOB_COUNT := 5

var seed_val: int = 0
var lifetime_ticks: int = 16
var scale_px: float = 14.0
var origin: Vector2 = Vector2.ZERO
var _color: Color = Color.from_hsv(0.0, 0.0, 0.35, 1.0)

var _ticks_elapsed: int = 0
var _rng := RandomNumberGenerator.new()
var _blob_offsets: Array[Vector2] = []
var _blob_sizes: Array[float] = []
var _blob_rise_speed: Array[float] = []
## Ordre de retrait (index de blob) — un par un, jamais tous en même temps.
var _removal_order: Array[int] = []


func configure(params: Dictionary) -> void:
	seed_val = params.get("seed", 0)
	lifetime_ticks = maxi(BLOB_COUNT, int(params.get("lifetime_ticks", 16)))
	scale_px = params.get("scale_px", 14.0)
	origin = params.get("origin", Vector2.ZERO)
	position = origin
	z_index = 5  # CONSEQUENCE : sous ANTICIPATION (groundRing=10) — un résidu discret, jamais au-dessus de l'action en cours.

	var value_pct: float = clampf(params.get("value_percent", 35.0), 0.0, 100.0) / 100.0
	var hue_deg: float = params.get("hue_deg", 0.0)
	var sat_pct: float = clampf(params.get("saturation_percent", 0.0), 0.0, 100.0) / 100.0
	var v: float = clampf(value_pct, MIN_VALUE_HSV, MAX_VALUE_HSV)
	_color = Color.from_hsv(hue_deg / 360.0, sat_pct, v, 1.0)

	_rng.seed = seed_val
	_blob_offsets.clear()
	_blob_sizes.clear()
	_blob_rise_speed.clear()
	for i in BLOB_COUNT:
		var a: float = _rng.randf() * TAU
		var r: float = scale_px * 0.3 * _rng.randf()
		_blob_offsets.append(Vector2(cos(a), sin(a)) * r)
		_blob_sizes.append(scale_px * (0.4 + _rng.randf() * 0.4))
		_blob_rise_speed.append(0.15 + _rng.randf() * 0.2)

	# Fisher-Yates manuel (Array.shuffle() utilise le RNG global, pas le
	# nôtre — l'ordre de retrait doit rester déterministe par seed, §13.4).
	_removal_order.clear()
	for i in BLOB_COUNT:
		_removal_order.append(i)
	for i in range(BLOB_COUNT - 1, 0, -1):
		var j: int = _rng.randi_range(0, i)
		var tmp: int = _removal_order[i]
		_removal_order[i] = _removal_order[j]
		_removal_order[j] = tmp


func tick(ticks_elapsed: int) -> void:
	_ticks_elapsed = ticks_elapsed
	queue_redraw()


func _draw() -> void:
	var t: float = clampf(float(_ticks_elapsed) / float(lifetime_ticks), 0.0, 1.0)
	# Retrait par comptage (§10.2) : le nombre de blobs encore visibles
	# décroît par paliers avec le temps, jamais un fondu d'opacité global.
	var visible_count: int = ceili(float(BLOB_COUNT) * (1.0 - t))
	if visible_count <= 0:
		return
	var col := Color(_color.r, _color.g, _color.b, 1.0)
	for slot in visible_count:
		var i: int = _removal_order[slot]
		# Léger flottement vers le haut — un nuage qui monte doucement,
		# pas un décalque statique.
		var rise: Vector2 = Vector2(0, -_blob_rise_speed[i] * _ticks_elapsed)
		draw_circle(_blob_offsets[i] + rise, _blob_sizes[i], col)
