extends Node2D
## Primitive "shardBurst" — docs/ARCHITECTURE_VFX_v3.md §7.1 :
## "fragmentation orientée". Couche CONSEQUENCE typique (§9.3) : des
## éclats anguleux qui partent de l'origine dans un cône dirigé (jamais
## une explosion isotrope à 360°, §4 : "jamais un bruit isotrope").

const MIN_VALUE_HSV := 0.20
const MAX_VALUE_HSV := 0.92
const CONE_HALF_ANGLE := PI / 3.0  # 60° de part et d'autre de `direction`

var seed_val: int = 0
var lifetime_ticks: int = 15
var origin: Vector2 = Vector2.ZERO
var direction: Vector2 = Vector2.RIGHT
var shard_count: int = 8
var speed_px_per_tick: float = 3.0
var _color: Color = Color.from_hsv(0.0, 0.0, 0.4, 1.0)

var _ticks_elapsed: int = 0
var _rng := RandomNumberGenerator.new()
var _shard_dirs: Array[Vector2] = []
var _shard_speeds: Array[float] = []
var _shard_sizes: Array[float] = []


func configure(params: Dictionary) -> void:
	seed_val = params.get("seed", 0)
	lifetime_ticks = max(1, int(params.get("lifetime_ticks", 15)))
	origin = params.get("origin", Vector2.ZERO)
	position = origin
	direction = params.get("direction", Vector2.RIGHT)
	if direction.length_squared() < 0.0001:
		direction = Vector2.RIGHT
	direction = direction.normalized()
	# §8.2 : plafond 50-200 particules/effet — un burst reste un poignée
	# d'éclats distincts, jamais une pluie de particules (ça, c'est un
	# système de particules GPU, hors scope primitive scriptée).
	shard_count = clampi(int(params.get("count", 8)), 1, 16)
	speed_px_per_tick = params.get("speed_px_per_tick", 3.0)

	var value_pct: float = clampf(params.get("value_percent", 40.0), 0.0, 100.0) / 100.0
	var hue_deg: float = params.get("hue_deg", 0.0)
	var sat_pct: float = clampf(params.get("saturation_percent", 0.0), 0.0, 100.0) / 100.0
	var v: float = clampf(value_pct, MIN_VALUE_HSV, MAX_VALUE_HSV)
	_color = Color.from_hsv(hue_deg / 360.0, sat_pct, v, 1.0)

	_rng.seed = seed_val
	_shard_dirs.clear()
	_shard_speeds.clear()
	_shard_sizes.clear()
	for i in shard_count:
		var a: float = (_rng.randf() * 2.0 - 1.0) * CONE_HALF_ANGLE
		_shard_dirs.append(direction.rotated(a))
		_shard_speeds.append(speed_px_per_tick * (0.6 + _rng.randf() * 0.8))
		_shard_sizes.append(2.0 + _rng.randf() * 3.0)


func tick(ticks_elapsed: int) -> void:
	_ticks_elapsed = ticks_elapsed
	queue_redraw()


func _draw() -> void:
	var t: float = float(_ticks_elapsed) / float(lifetime_ticks)
	var alpha: float = 1.0 - clampf((t - 0.6) / 0.4, 0.0, 1.0)  # fade sur les 40% finaux
	if alpha <= 0.0:
		return
	var col := Color(_color.r, _color.g, _color.b, alpha)
	for i in shard_count:
		var dist: float = _shard_speeds[i] * _ticks_elapsed
		var p: Vector2 = _shard_dirs[i] * dist
		var size_px: float = _shard_sizes[i]
		# Éclat anguleux (triangle), jamais un cercle — "fragmentation",
		# pas une particule ronde générique.
		var tip: Vector2 = p + _shard_dirs[i] * size_px
		var perp: Vector2 = Vector2(-_shard_dirs[i].y, _shard_dirs[i].x) * size_px * 0.4
		var base_a: Vector2 = p - _shard_dirs[i] * size_px * 0.3 + perp
		var base_b: Vector2 = p - _shard_dirs[i] * size_px * 0.3 - perp
		draw_polygon(PackedVector2Array([tip, base_a, base_b]), PackedColorArray([col, col, col]))
