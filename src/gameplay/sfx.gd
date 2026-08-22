extends Node
## Autoload "Sfx" — Phase 2.1 (MANDAT SUITE v2). Le jeu était 100%
## silencieux ; `sfx_markers` existe dans le format de recette depuis le
## début (data/recipes/*.json) mais n'a jamais été consommé jusqu'ici.
##
## 6 familles générées hors moteur par pyfxr (T.1.4, retenu —
## scripts/generate_sfx.py, docs/worklog.md) : light_impact, heavy_impact,
## whoosh, spawn, death, footstep. Variantes de hauteur "+-5%" (mandat) ==
## `pitch_scale` randomisé au runtime, pas des fichiers dupliqués sur
## disque pour un effet aussi simple.
##
## Bus dédiés (`default_bus_layout.tres`) : SFX_Combat / SFX_UI / Music —
## le hit-stop (CombatFeedback) ne coupe JAMAIS la musique par construction
## (c'est un compteur de ticks auto-consulté par les nœuds de combat, pas
## un throttle de l'arbre de scène ni de l'Engine — un AudioStreamPlayer
## qui ne consulte jamais is_frozen() continue de jouer normalement).

const SAMPLES: Dictionary = {
	"light_impact": preload("res://assets/processed/sfx/light_impact.wav"),
	"heavy_impact": preload("res://assets/processed/sfx/heavy_impact.wav"),
	"whoosh": preload("res://assets/processed/sfx/whoosh.wav"),
	"spawn": preload("res://assets/processed/sfx/spawn.wav"),
	"death": preload("res://assets/processed/sfx/death.wav"),
	"footstep": preload("res://assets/processed/sfx/footstep.wav"),
	# Mandat critique probabiliste (verrouillé par Milan) : signal distinct
	# de light_impact/heavy_impact, voir scripts/generate_sfx.py.
	"critical_hit": preload("res://assets/processed/sfx/critical_hit.wav"),
}

const PITCH_VARIANCE := 0.05  ## +-5%, mandat Phase 2.1.
const POOL_SIZE := 12

var _pool: Array[AudioStreamPlayer] = []
var _next_index: int = 0


func _ready() -> void:
	for i in POOL_SIZE:
		var p := AudioStreamPlayer.new()
		add_child(p)
		_pool.append(p)


## `event` : une clé de SAMPLES. Nom inconnu -> no-op silencieux (même
## discipline que Enemy._play_visual_animation() : un événement de
## recette pas encore mappé ne doit jamais faire planter l'appelant).
func play(event: String, bus: String = "SFX_Combat") -> void:
	var stream: AudioStream = SAMPLES.get(event)
	if stream == null:
		return
	var p: AudioStreamPlayer = _pool[_next_index]
	_next_index = (_next_index + 1) % _pool.size()
	p.stream = stream
	p.bus = bus
	p.pitch_scale = 1.0 + randf_range(-PITCH_VARIANCE, PITCH_VARIANCE)
	p.play()
