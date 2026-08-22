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
## qui ne consulte jamais is_frozen()/is_player_frozen()/is_enemy_frozen()
## (un futur HUD, par exemple) continue de tourner normalement — c'est
## exactement le "local aux nœuds de combat" du doc, sans toucher
## Engine.time_scale.
##
## Déterminisme (§13.4, Addendum A §A.5) préservé : un tick gelé est un
## tick SAUTÉ pour les nœuds qui le consultent, jamais un tick accéléré
## ou une simulation en temps réel — RNG/seeds ne voient jamais l'écart.
##
## Phase R4 (retour croisé Gemini/ChatGPT sur clip réel, MANDAT SUITE
## v2) : "un seul système utilisé par TOUTE attaque qui touche". Audit
## préalable (agent lecture seule) a confirmé que le hit-stop était
## SYMÉTRIQUE (un seul compteur global, joueur et ennemis gèlent
## identiquement) et que chaque site d'attaque appelait hit-stop/shake/
## SFX/camera-punch séparément, avec des trous (Bras-Faux/Poing
## Belluaire/Poing Tellurique/Gueule Vide sans AUCUN shake ; enemy.gd
## sans AUCUN camera-punch ; boss_gate_maw.gd sans AUCUN SFX ni
## camera-punch). `register_hit()` ci-dessous est désormais le POINT
## D'ENTRÉE UNIQUE que chaque site d'attaque appelle pour un coup qui
## touche — hit-stop asymétrique + shake + camera-punch + SFX déclenchés
## ensemble, un seul appel par impact.

## §9.1 — 5 profils, valeurs initiales en ms, converties en ticks (60/s,
## ~16,667 ms/tick) par arrondi au plus proche à la création de ce
## fichier. "heavy"/"catastrophic" utilisent le milieu de leur
## fourchette (45-65 -> 55, 75-95 -> 85) — valeurs de départ, pas des
## vérités figées (le doc le dit explicitement).
##
## Phase R4 (1re passe) : remplacées par deux tableaux ASYMÉTRIQUES
## (cible gèle plus longtemps que l'attaquant, convergence Gemini/
## ChatGPT sur le clip post-correctif R1 : "hit-stop ~50-80ms côté cible
## / ~30-40ms côté attaquant"). "medium" calé au centre des deux
## fourchettes (65ms cible / 35ms attaquant) ; light/heavy/catastrophic
## suivaient le même ratio que l'ancien tableau symétrique (light≈0,48×
## medium, heavy≈2,2×medium, catastrophic≈3,4×medium).
##
## Phase R4 (2e passe, verdict de Milan dans un bac à sable dédié à UN
## impact isolé) : hitstop_freeze_ms=210 — un verdict humain qui prime
## sur la table théorique du doc (plafonnée à 95ms), mais 210ms partout
## romprait le rythme d'un combo de 3 coups enchaînés (3×210ms de gel
## cumulé côté cible). Le nombre de Milan est donc traité comme la
## VALEUR CIBLE DU COUP LE PLUS LOURD (catastrophic, côté cible) — proche
## de l'ancien 221ms, cohérent avec "le plus lourd" plutôt qu'un remplacement
## uniforme — et le reste de l'échelle est RECALÉ sur ce nouveau sommet en
## conservant EXACTEMENT les mêmes ratios que la 1re passe (jamais des
## chiffres inventés sans rapport) : medium_cible = 210/3,4 ≈ 62ms,
## light_cible = medium_cible×0,48 ≈ 30ms, heavy_cible = medium_cible×2,2
## ≈ 136ms. Côté attaquant : même ratio attaquant/cible que la 1re passe
## (~0,54×, dérivé de l'ancien tableau 17/31, 35/65, 77/143, 119/221 —
## tous ≈0,54-0,55) appliqué aux nouvelles valeurs cible. Toujours des
## valeurs À CONFIRMER par Milan sur le prochain build (un seul point de
## sandbox ne couvre qu'un impact isolé, pas l'enchaînement réel).
const TARGET_HITSTOP_MS := {
	"none": 0.0,
	"light": 30.0,
	"medium": 62.0,
	"heavy": 136.0,
	"catastrophic": 210.0,
}
const ATTACKER_HITSTOP_MS := {
	"none": 0.0,
	"light": 16.0,
	"medium": 33.0,
	"heavy": 73.0,
	"catastrophic": 113.0,
}

## §9.2 — 3 niveaux, "heavy" utilise le milieu de 3-5px (4px).
##
## Phase R4 (verdict Milan, bac à sable) : camera_shake_amplitude_px=6,
## au-delà même de l'ancien "heavy" (4px) — testé sur UN impact isolé,
## pas explicitement rattaché à un tier précis. Traité comme LE NOUVEAU
## PLAFOND "heavy" (le tier que Milan sent le plus proche d'un impact
## fort en bac à sable) ; "light"/"medium" restent aux valeurs
## précédentes (non retestées par Milan) — à reconfirmer séparément
## plutôt que rescaler tout le tableau sur un seul point de mesure.
const SHAKE_PROFILES := {
	"light": {"amplitude_px": 1.0, "ticks": 4},
	"medium": {"amplitude_px": 2.0, "ticks": 5},
	"heavy": {"amplitude_px": 6.0, "ticks": 7},
}

const TICK_MS := 1000.0 / 60.0

## Deux compteurs séparés (Phase R4) plutôt qu'un seul global : au
## moment d'un impact, le CÔTÉ QUI ENCAISSE gèle plus longtemps que le
## CÔTÉ QUI FRAPPE. "player"/"enemy" désigne un RÔLE pour ce compteur
## (l'entité qui consulte is_player_frozen()/is_enemy_frozen()), pas
## littéralement "le nœud Player" — Gueule Vide (créature invoquée qui
## attaque des ennemis pour le compte du joueur) consulte
## is_player_frozen() côté attaquant, un Projectile tiré par Ranged
## consulte is_enemy_frozen() côté attaquant, etc. Cohérent avec le
## principe "consulté, jamais possédé" : chaque nœud de combat sait déjà
## de quel côté du conflit il se trouve.
var _player_freeze_ticks_remaining: int = 0
var _enemy_freeze_ticks_remaining: int = 0

var _shake_ticks_remaining: int = 0
var _shake_ticks_total: int = 0
var _shake_amplitude_px: float = 0.0
var _shake_direction: Vector2 = Vector2.ZERO


func _physics_process(_delta: float) -> void:
	# Ce nœud NE consulte JAMAIS is_frozen()/is_player_frozen()/
	# is_enemy_frozen() sur lui-même : il est la source de vérité du gel,
	# pas un nœud de combat qui s'y soumet.
	if _player_freeze_ticks_remaining > 0:
		_player_freeze_ticks_remaining -= 1
	if _enemy_freeze_ticks_remaining > 0:
		_enemy_freeze_ticks_remaining -= 1
	if _shake_ticks_remaining > 0:
		_shake_ticks_remaining -= 1


## Point d'entrée UNIQUE pour tout impact qui touche une cible (Phase
## R4) : hit-stop asymétrique + shake + camera-punch + SFX, déclenchés
## ensemble depuis CET appel plutôt qu'éparpillés site par site.
##
## `hitstop_weight` : "none"/"light"/"medium"/"heavy"/"catastrophic" —
## pilote le hit-stop asymétrique (TARGET_HITSTOP_MS/ATTACKER_HITSTOP_MS).
## `attacker_is_player` : qui a frappé — true si le joueur ou une entité
## de son côté (ex. la créature Gueule Vide) vient de toucher un
## ennemi ; false si un ennemi/projectile/boss vient de toucher le
## joueur. Détermine QUEL compteur (_player_.../_enemy_...) reçoit la
## durée COURTE (attaquant) et lequel reçoit la durée LONGUE (cible).
## `sfx_event` : passé tel quel à Sfx.play(), "" pour ne rien jouer.
## `shake_weight` : "" désactive le shake pour ce coup (ex. combo tier1/
## tier2, un jab léger n'a jamais eu de shake — préservé tel quel,
## Phase R4 n'invente pas un shake sur des coups qui n'en avaient jamais
## eu par choix explicite). `shake_direction` : direction de L'ATTAQUE
## (voir trigger_shake ci-dessous), ignorée si shake_weight == "".
## `camera_punch` : false pour les coups légers (préserve le test
## `camera_punch_zoom_triggers_on_medium_hit_not_light` — un jab léger
## ne doit jamais zoomer la caméra, seuls les coups medium+ le méritent).
func register_hit(
	hitstop_weight: String,
	attacker_is_player: bool,
	sfx_event: String = "",
	shake_weight: String = "",
	shake_direction: Vector2 = Vector2.ZERO,
	camera_punch: bool = false
) -> void:
	var target_ticks: int = _ms_to_ticks(TARGET_HITSTOP_MS.get(hitstop_weight, 0.0))
	var attacker_ticks: int = _ms_to_ticks(ATTACKER_HITSTOP_MS.get(hitstop_weight, 0.0))
	if attacker_is_player:
		_player_freeze_ticks_remaining = maxi(_player_freeze_ticks_remaining, attacker_ticks)
		_enemy_freeze_ticks_remaining = maxi(_enemy_freeze_ticks_remaining, target_ticks)
	else:
		_enemy_freeze_ticks_remaining = maxi(_enemy_freeze_ticks_remaining, attacker_ticks)
		_player_freeze_ticks_remaining = maxi(_player_freeze_ticks_remaining, target_ticks)

	if shake_weight != "":
		trigger_shake(shake_weight, shake_direction)
	if camera_punch:
		CameraDirector.trigger_punch()
	if sfx_event != "":
		Sfx.play(sfx_event)


func _ms_to_ticks(ms: float) -> int:
	if ms <= 0.0:
		return 0
	return maxi(1, int(round(ms / TICK_MS)))


## Compatibilité : "un impact quelconque est-il en cours, tous côtés
## confondus" — utilisé par les minuteries purement cosmétiques qui ne
## jouent aucun rôle de combat (décroissance du flash HitResponse,
## décroissance du shake/punch caméra) : pas de raison de leur faire
## porter la distinction de rôle, elles doivent juste rester synchrones
## avec l'impact le plus long des deux côtés.
func is_frozen() -> bool:
	return _player_freeze_ticks_remaining > 0 or _enemy_freeze_ticks_remaining > 0


## Consulté par le joueur et toute entité de son côté du conflit
## (Gueule Vide en tant qu'attaquante).
func is_player_frozen() -> bool:
	return _player_freeze_ticks_remaining > 0


## Consulté par les ennemis/le boss/les projectiles ennemis.
func is_enemy_frozen() -> bool:
	return _enemy_freeze_ticks_remaining > 0


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
