extends Node
## Autoload "CombatFeedback" — docs/ARCHITECTURE_VFX_v3.md §9.1/§9.2.
##
## Hit-stop ET camera shake : les deux vivent dans la couche FEEDBACK
## (7/8, §4) — "pas des nœuds de scène", jamais une primitive VFX
## classique. Un seul autoload pour les deux car ils sont quasi toujours
## déclenchés ensemble au même instant de contact.
##
## §9.1 : "Implémentation : time scale local aux nœuds de combat, pas
## Engine.time_scale global (sinon l'UI gèle aussi)." Ici : PAS de
## ralentissement du temps réel — un compteur de ticks gelés que CHAQUE
## nœud de combat (Player, Enemy, GueuleVide, VfxDirector,
## VfxRecipeRegistry) consulte lui-même en tête de son
## _physics_process() et sur lequel il fait un retour anticipé. Un nœud
## qui ne consulte jamais is_frozen() (un futur HUD, par exemple)
## continue de tourner normalement — c'est exactement le "local aux
## nœuds de combat" du doc, sans toucher Engine.time_scale.
##
## Déterminisme (§13.4, Addendum A §A.5) préservé : un tick gelé est un
## tick SAUTÉ pour les nœuds qui le consultent, jamais un tick accéléré
## ou une simulation en temps réel — RNG/seeds ne voient jamais l'écart.

## §9.1 — 5 profils, valeurs initiales en ms, converties en ticks (60/s,
## ~16,667 ms/tick) par arrondi au plus proche à la création de ce
## fichier. "heavy"/"catastrophic" utilisent le milieu de leur
## fourchette (45-65 -> 55, 75-95 -> 85) — valeurs de départ, pas des
## vérités figées (le doc le dit explicitement).
const HITSTOP_MS := {
	"none": 0.0,
	"light": 12.0,
	"medium": 25.0,
	"heavy": 55.0,
	"catastrophic": 85.0,
}

## §9.2 — 3 niveaux, "heavy" utilise le milieu de 3-5px (4px).
const SHAKE_PROFILES := {
	"light": {"amplitude_px": 1.0, "ticks": 4},
	"medium": {"amplitude_px": 2.0, "ticks": 5},
	"heavy": {"amplitude_px": 4.0, "ticks": 7},
}

const TICK_MS := 1000.0 / 60.0

var _freeze_ticks_remaining: int = 0

var _shake_ticks_remaining: int = 0
var _shake_ticks_total: int = 0
var _shake_amplitude_px: float = 0.0
var _shake_direction: Vector2 = Vector2.ZERO


func _physics_process(_delta: float) -> void:
	# Ce nœud NE consulte JAMAIS is_frozen() sur lui-même : il est la
	# source de vérité du gel, pas un nœud de combat qui s'y soumet.
	if _freeze_ticks_remaining > 0:
		_freeze_ticks_remaining -= 1
	if _shake_ticks_remaining > 0:
		_shake_ticks_remaining -= 1


## `profile` : "none"/"light"/"medium"/"heavy"/"catastrophic". Un appel
## pendant un gel déjà actif prend le MAX (jamais additif — un hit-stop
## ne s'accumule pas indéfiniment sur des hits rapprochés, sinon un
## combo rapide finirait par tout figer).
func trigger_hitstop(profile: String) -> void:
	var ms: float = HITSTOP_MS.get(profile, 0.0)
	if ms <= 0.0:
		return
	var ticks: int = int(round(ms / TICK_MS))
	if ticks < 1:
		ticks = 1
	_freeze_ticks_remaining = maxi(_freeze_ticks_remaining, ticks)


func is_frozen() -> bool:
	return _freeze_ticks_remaining > 0


## `profile` : "light"/"medium"/"heavy" (pas de "none" — appelant ne
## déclenche simplement pas s'il ne veut aucun shake). `attack_direction`
## : direction de l'ATTAQUE (le shake part dans la direction OPPOSÉE,
## §9.2 : "Direction du shake = opposée à l'attaque").
func trigger_shake(profile: String, attack_direction: Vector2) -> void:
	var cfg: Dictionary = SHAKE_PROFILES.get(profile, {})
	if cfg.is_empty():
		return
	var dir := attack_direction
	if dir.length_squared() < 0.0001:
		dir = Vector2.RIGHT
	_shake_direction = -dir.normalized()
	_shake_amplitude_px = cfg["amplitude_px"]
	_shake_ticks_total = cfg["ticks"]
	_shake_ticks_remaining = cfg["ticks"]


## Décalage caméra courant — à lire chaque tick par le nœud qui porte la
## Camera2D (Player) et appliquer sur `camera.offset`. Jamais de bruit
## isotrope (§9.2) : un seul axe fixe (opposé à l'attaque), amplitude
## qui oscille et décroît le long de ce même axe — "courbe de retour
## obligatoire", jamais un vecteur aléatoire à chaque tick.
func get_shake_offset() -> Vector2:
	if _shake_ticks_remaining <= 0:
		return Vector2.ZERO
	var elapsed: int = _shake_ticks_total - _shake_ticks_remaining
	var t: float = float(elapsed) / float(_shake_ticks_total)
	# Décroissance linéaire vers 0 (courbe de retour) modulée par une
	# oscillation aller-retour sur l'axe du shake (2 cycles complets sur
	# la durée totale) — lit comme un tremblement qui s'éteint, pas un
	# glissement continu.
	#
	# cos, pas sin : trouvé en câblant B3 (docs/worklog.md) — avec sin,
	# le profil "light" (4 ticks) échantillonne l'oscillation UNIQUEMENT
	# à ses passages par zéro (4 ticks = exactement 2 cycles, un demi-cycle
	# par tick), donc get_shake_offset() valait 0 à CHAQUE tick pour ce
	# profil : trigger_shake("light", ...) ne bougeait jamais visiblement
	# la caméra. cos déphase d'un quart de cycle — non-nul sur les 3
	# profils (light/medium/heavy) — et donne en prime un premier tick à
	# pleine amplitude, cohérent avec "shake dès le premier tick" (mandat
	# combo/dash).
	var decay: float = 1.0 - t
	var oscillation: float = cos(t * TAU * 2.0)
	return _shake_direction * _shake_amplitude_px * decay * oscillation
