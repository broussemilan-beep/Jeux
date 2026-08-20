extends Node2D
## Primitive "spiral" — docs/ARCHITECTURE_VFX_v3.md §7.1 : "rotation/
## aspiration". Points seedés qui tournent autour de l'origine tout en se
## rapprochant du centre (aspiration) — la forme principale d'un pouvoir
## d'invocation/canalisation en cours de formation (§5, archétype
## "canalisation"), distincte de converge (fragments discrets qui
## VIENNENT de l'extérieur) : ici c'est une matière déjà en rotation
## continue, pas des fragments individuels qui voyagent en ligne. Couche
## ACTION CORE (§4) — c'est la forme principale du geste en cours, pas un
## accompagnement (TRAIL) ni une conséquence.

const MIN_VALUE_HSV := 0.20
const MAX_VALUE_HSV := 0.92
const TURNS := 1.4  # nombre de tours complets sur la durée de vie — une aspiration nette, pas un tourbillon infini

var seed_val: int = 0
var lifetime_ticks: int = 14
var scale_px: float = 30.0
var origin: Vector2 = Vector2.ZERO
var point_count: int = 5
var _color: Color = Color.from_hsv(0.0, 0.0, 0.5, 1.0)

var _ticks_elapsed: int = 0
var _rng := RandomNumberGenerator.new()
var _phase_offsets: Array[float] = []
var _sizes: Array[float] = []


func configure(params: Dictionary) -> void:
	seed_val = params.get("seed", 0)
	lifetime_ticks = maxi(1, int(params.get("lifetime_ticks", 14)))
	scale_px = params.get("scale_px", 30.0)
	origin = params.get("origin", Vector2.ZERO)
	position = origin
	point_count = clampi(int(params.get("count", 5)), 1, 12)
	z_index = 25  # ACTION CORE : au-dessus de runicStamp (20) — forme principale distincte du glyphe de sol.

	var value_pct: float = clampf(params.get("value_percent", 50.0), 0.0, 100.0) / 100.0
	var hue_deg: float = params.get("hue_deg", 0.0)
	var sat_pct: float = clampf(params.get("saturation_percent", 0.0), 0.0, 100.0) / 100.0
	var v: float = clampf(value_pct, MIN_VALUE_HSV, MAX_VALUE_HSV)
	_color = Color.from_hsv(hue_deg / 360.0, sat_pct, v, 1.0)

	_rng.seed = seed_val
	_phase_offsets.clear()
	_sizes.clear()
	for i in point_count:
		_phase_offsets.append((TAU / float(point_count)) * i + _rng.randf() * 0.3)
		_sizes.append(2.0 + _rng.randf() * 2.0)


func tick(ticks_elapsed: int) -> void:
	_ticks_elapsed = ticks_elapsed
	queue_redraw()


func _draw() -> void:
	var t: float = clampf(float(_ticks_elapsed) / float(lifetime_ticks), 0.0, 1.0)
	var alpha: float = 1.0 - clampf((t - 0.8) / 0.2, 0.0, 1.0)  # fade sur les 20% finaux
	if alpha <= 0.0:
		return
	var col := Color(_color.r, _color.g, _color.b, alpha)
	# Le rayon décroît avec le temps (aspiration) tandis que la rotation
	# accumule des tours — deux mouvements combinés, pas juste un cercle
	# qui rétrécit.
	var radius: float = scale_px * (1.0 - t * 0.7)
	var rotation_now: float = TAU * TURNS * t
	for i in point_count:
		var angle: float = _phase_offsets[i] + rotation_now
		var p: Vector2 = Vector2(cos(angle), sin(angle)) * radius
		draw_circle(p, _sizes[i], col)
