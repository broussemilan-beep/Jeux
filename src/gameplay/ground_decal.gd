extends Node2D
## Décal persistant au sol (mandat production v1 §4, HitResponse : "décal
## persistant au sol, registre à budget par zone, via VfxBudget"). PAS une
## primitive VfxDirector (§7.1, contrat seed/configure générique pour un
## effet de quelques ticks) : un décal vit BEAUCOUP plus longtemps
## (`LIFETIME_TICKS`, plusieurs secondes) et son budget se suit via le
## registre de RÉSIDU dédié de VfxBudget (`register_residue`/
## `decay_residue`), séparé du ledger d'overdraw des effets actifs — même
## distinction que documentée en tête de vfx_budget.gd. Même discipline
## que `Player._spawn_dash_afterimage()` : un nœud autonome, hors du
## périmètre de VfxDirector, mais celui-ci consulte `CombatFeedback.
## is_frozen()` lui-même (c'est un nœud de combat qui avance en ticks purs,
## pas un Tween en temps réel comme l'afterimage — un décal doit pouvoir
## survivre à travers plusieurs hit-stops sans que sa durée de vie dérive).

const LIFETIME_TICKS := 480  # 8s @ 60/s — assez long pour rester lisible sans s'accumuler indéfiniment
const RESIDUE_COST := 6.0    # fraction du plafond souple par zone (20.0, vfx_budget.gd) — ~3 décals simultanés par zone avant que le plus vieux ne parte
const FADE_START_FRAC := 0.7  # commence à s'effacer sur les 30% finaux de sa vie

var _zone_idx: int = -1
var _ticks_elapsed: int = 0
var _radius_px: float = 10.0
var _color: Color = Color(0.1, 0.05, 0.05, 0.55)


## Retourne l'instance créée, ou null si le budget de résidu de la zone
## est déjà plein (silencieux, comme un spawn VFX refusé — jamais une
## erreur, un décal en moins n'est jamais bloquant pour le gameplay).
static func spawn(parent: Node, world_pos: Vector2, radius_px: float, color: Color) -> Node2D:
	var zone_idx: int = VfxBudget.zone_index_for(world_pos)
	var verdict: Dictionary = VfxBudget.register_residue(zone_idx, RESIDUE_COST)
	if not verdict["ok"]:
		return null
	var decal := Node2D.new()
	decal.set_script(load("res://src/gameplay/ground_decal.gd"))
	decal._zone_idx = zone_idx
	decal._radius_px = radius_px
	decal._color = color
	# PAS de z_index négatif : le sol de test_arena.tscn ("Floor", un
	# ColorRect opaque z_index=0 couvrant toute l'arène) est un sibling
	# ajouté AVANT ce décal — un z_index<0 le fait dessiner AVANT/SOUS ce
	# sol opaque, donc invisible en pratique (bug réel trouvé par capture
	# visuelle, docs/worklog.md : le check smoke test résidu-budget passait
	# alors que rien n'apparaissait à l'écran — "vérifier avant de
	# déclarer fini" ne s'arrête pas au gate automatisé). z_index par
	# défaut (0) : le décal se dessine APRÈS le sol (ordre d'ajout à
	# l'arbre), donc dessus. Limite connue et acceptée pour l'instant :
	# sans Y-sort (aucun encore dans le projet, arrivera avec F "le
	# monde"), un décal peut passer par-dessus les pieds d'une entité qui
	# le traverse — anomalie mineure, jamais un décal invisible.
	parent.add_child(decal)
	decal.global_position = world_pos
	return decal


func _physics_process(_delta: float) -> void:
	if CombatFeedback.is_frozen():
		return
	_ticks_elapsed += 1
	if _ticks_elapsed >= LIFETIME_TICKS:
		VfxBudget.decay_residue(_zone_idx, RESIDUE_COST * (1.0 - _fade_alpha()))
		queue_free()
		return
	queue_redraw()


func _fade_alpha() -> float:
	var t: float = float(_ticks_elapsed) / float(LIFETIME_TICKS)
	if t <= FADE_START_FRAC:
		return 1.0
	return 1.0 - (t - FADE_START_FRAC) / (1.0 - FADE_START_FRAC)


func _draw() -> void:
	var alpha: float = _fade_alpha()
	if alpha <= 0.0:
		return
	var col := Color(_color.r, _color.g, _color.b, _color.a * alpha)
	# Tache irrégulière plutôt qu'un cercle parfait — quelques points
	# excentrés déterministes (pas de RNG, un décal ne rejoue jamais).
	draw_circle(Vector2.ZERO, _radius_px, col)
	draw_circle(Vector2(_radius_px * 0.4, _radius_px * 0.15), _radius_px * 0.5, col)
	draw_circle(Vector2(-_radius_px * 0.3, -_radius_px * 0.2), _radius_px * 0.4, col)
