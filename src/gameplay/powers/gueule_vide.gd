extends Node2D
class_name GueuleVide
## Invocation "Gueule Vide" — cast unique de 42 ticks (0,7s @ 60/s), pas
## une entité persistante (contrairement à un totem) : formation ->
## gueule ouverte/préparation -> morsure (RELEASE+IMPACT) -> désintégration
## (RECOVERY), conventions doc §6.1. Une seule attaque, jamais de
## répétition, `queue_free()` à la fin de son propre cast.
##
## Le recul (recoil) sur la cible touchée est OBLIGATOIRE à l'impact et
## porté par Enemy.take_damage() — "pas une primitive de la recette",
## data/recipes/power.gueule_vide.cast.json, note. Cette scène ne pilote
## QUE : son propre sprite (tick-exact, jamais la lecture fps autonome
## d'AnimatedSprite2D — même discipline que le combo de Player, "les
## ticks sont la seule autorité") et la couche visuelle VFX via
## VfxRecipeRegistry.play() ; le dégât/recul restent ici, pas dans la
## recette.

const RECIPE_ID := "power.gueule_vide.cast"

## docs/recipes/power.gueule_vide.cast.json, "notes" — bornes des 4
## phases (§6.1) et tick de contact (sfx_markers, tick=20, "morsure").
## TOTAL_TICKS reste sous le plafond de sécurité "lifecycle.
## max_lifetime_ticks" (48, "42 + marge") de la recette — seule cette
## classe incrémente _tick, aucun système de pause/étourdissement
## n'existe encore côté gameplay qui pourrait le dépasser.
const FORMATION_END_TICK := 9
const PREP_END_TICK := 15
const BITE_END_TICK := 21
const TOTAL_TICKS := 42
const CONTACT_TICK := 20

## Fiche de référence (INVOCATION : GUEULE VIDE, "COMPORTEMENT") :
## "Zone d'attaque : ~1,5m devant la créature" -> 48px, GameConstants.
## PX_PER_METER (même échelle que le combo de Player, ATTACK_RANGE_PX).
## Dégâts non chiffrés par la fiche (contrairement au combo, 10.0) —
## valeur par défaut alignée sur le dégât combo, à faire trancher par Milan.
##
## CORRECTIF (2026-08-26, MANDAT RETOURS DE PLAYTEST RÉEL, point 4 —
## "Gueule Vide imperceptible en jeu réel") : la valeur d'origine (48px)
## combinée à POWER1_SPAWN_DISTANCE_PX (96px, Player._cast_gueule_vide())
## ne mord que dans la bande [48px, 144px] devant le joueur (rayon centré
## sur la créature, elle-même à 96px). Un ennemi DÉJÀ EN TRAIN D'ATTAQUER
## le joueur au corps-à-corps — le déclencheur le plus probable pour
## lancer une invocation de riposte — est par construction à SA portée de
## contact à lui (`Enemy.attack_range_px` : 28px Crawler, 52px Brute à
## peine dans l'ancienne bande), donc dans l'angle mort entre le joueur et
## la créature : la morsure ne touchait jamais la cible la plus commune.
## Reproduit et confirmé par un nouveau check dédié AVANT ce correctif
## (`gueule_vide_hits_enemy_at_realistic_melee_contact_range`,
## tools/smoke_test_gameplay.gd — rouge avec 48px, vert avec 96px).
## Remontée à 96px = POWER1_SPAWN_DISTANCE_PX : le bord proche de la bande
## (spawn_distance - range) tombe à 0, la morsure couvre donc TOUT le
## chemin entre le joueur et la créature (aucun angle mort), jusqu'à
## 192px au-delà — un rayon de morsure large plutôt qu'un simple cône
## fin, cohérent avec une "gueule qui engloutit ce qui l'entoure" plus
## qu'avec une morsure chirurgicale à 1,5m pile. Écart honnête avec la
## fiche (~1,5m devenu ~3m) : nécessaire pour éliminer l'angle mort,
## documenté ici plutôt que masqué, à revalider par Milan si la fiche
## doit rester la référence numérique stricte.
const ATTACK_RANGE_PX := 96.0
const ATTACK_DAMAGE := 10.0

## Addendum A, §A.5 : "aucune source de hasard non seedée dans le chemin
## VFX" — l'horloge murale (Time.get_ticks_usec(), l'ancien code d'ici)
## rend compare_reference.py inutilisable et casse le gate "seed fixe ->
## même sortie" (§13.4 du v3). Valeur fixe en attendant un vrai système
## de seed de run côté gameplay (compteur d'événement, seed de run...).
const CAST_SEED := 44103

## 6 frames pose-to-pose (mandat : "4-6 frames") couvrant les 4 phases :
## formation (2 frames), préparation (1), morsure (1), désintégration
## (2). Bornes cumulées en ticks — jamais la fps autonome
## d'AnimatedSprite2D (qui ne peut pas exprimer des phases de durées
## inégales avec le pas fps uniforme de build_sprite_frames.py).
##
## AUDIT FIDÉLITÉ (2026-08-22, retour Milan, PREMIÈRE PASSE) : les 6
## frames PixelLab d'origine (créature à jambes façon mannequin générique)
## ne ressemblaient PAS à la planche de référence (docs/references/
## invocateur/gueule_vide.png — une gueule d'encre béante SANS jambes ni
## bras, seulement une mâchoire sur un tendon d'encre). Régénérées une
## première fois en v3+reference (voir data/pixellab_usage.jsonl,
## entrées 2026-08-22T21:0x) : silhouette correcte (mâchoire+tendon, zéro
## jambe) mais composition FRONTALE/symétrique — une mâchoire vue de
## face, pas la composition dynamique en S que montre la référence
## (tendon qui jaillit en diagonale depuis le sol, mâchoire penchée au
## sommet). Corrigé écarté par Milan (`captures/verification/
## 2026-08-22-fidelite-gueule_vide.png`, verdict "toujours pas fini").
##
## AUDIT FIDÉLITÉ, DEUXIÈME PASSE (2026-08-22, même journée) : nouveau
## guide de silhouette synthétique dessiné explicitement en S (tracé
## polygonal bas-gauche -> milieu-droite -> haut-gauche, largeur qui
## s'amincit en montant, mâchoire EXCENTRÉE en haut avec mandibules
## asymétriques) -> `create_image_pixflux` (strength 120) -> `create_
## character` v3+reference -> `animate_character` v3 (6 frames, sud
## seul). Résultat : la composition en S diagonale EST bien présente et
## COHÉRENTE sur les 6 frames (voir data/pixellab_usage.jsonl,
## entrées 2026-08-22T22:xx) — le tendon part du sol en biais, se
## recourbe deux fois, et la mâchoire penchée est nettement excentrée,
## jamais un ovale frontal centré. Lecture des frames, honnête : 0-1 =
## mâchoire grande ouverte, crocs visibles (le tendon "respire", pas de
## progression nette) ; 2 = début de fermeture (crocs qui se recouvrent
## partiellement) ; 3 = la morsure (mâchoire fermée, bande sombre nette,
## goutte qui pend) ; 4 = mâchoire toujours fermée (tenue post-morsure) ;
## 5 = réouverture/retrait (la gueule se rouvre légèrement, une volute
## d'encre se recourbe à la base). LIMITE CONNUE, documentée honnêtement :
## contrairement à l'ancienne v1 (qui montrait un vrai effritement en
## points épars sur les frames 4-5), cette séquence v2 ne fragmente PAS
## littéralement le sprite en fin de cast — la "désintégration" reste un
## cycle ouverture/fermeture/réouverture de la mâchoire, compensée comme
## avant par la couche VFX shardBurst de la recette plutôt que par un
## effritement dessiné. Le mandat de cette passe portait sur la
## COMPOSITION (le S), pas sur l'animation — non retenté pour rester dans
## le périmètre. Bornes de frames inchangées par rapport à la première
## passe (le mapping tenait déjà : frame 2 = fin de préparation/débute la
## fermeture, frame 3 = bite pile sur CONTACT_TICK) : frame 2 prolongée
## jusqu'à juste avant CONTACT_TICK (10-19), frame 3 bascule PILE sur
## CONTACT_TICK (20) et tient jusqu'à 27 ("claquement brutal" simultané
## aux dégâts), frames 4/5 se partagent la fin (28-34 / 35-42).
## CONTACT_TICK/PREP_END_TICK et les couches VFX de la recette restent
## inchangés. Canvas cuit changé de 48x48 à 56x72 (`scripts/
## cook_character_frames.py`) : la composition en S est nettement plus
## haute que l'ancienne mâchoire frontale compacte, un canvas carré 48x48
## rognait la mâchoire hors cadre en haut — vérifié visuellement avant
## de committer, `scenes/gameplay/powers/gueule_vide.tscn` (offset)
## inchangé, l'ancrage bas (base du tendon dans la flaque) tombe déjà au
## bon endroit par rapport à `groundRing`/`runicStamp` sans retouche.
##
## PASSE DÉTAIL (2026-08-23, même session, agent dédié) : Milan jugeait la
## v2 ci-dessus "pas assez détaillée" vs la richesse de la planche de
## référence — traits d'encre qui gouttent à plusieurs endroits, variation
## de texture sur la mâchoire, crocs irréguliers, éclats d'encre au sol.
## Mandat volontairement limité au DÉTAIL, silhouette/composition en S
## à préserver.
##
## FAUX-DÉPART CORRIGÉ AVANT COMMIT (leçon importante, gardée ici pour ne
## pas la reproduire) : un 1er guide enrichi + `create_image_pixflux`
## (strength 120) a produit un résultat que le rapport initial de l'agent
## déclarait "silhouette intacte" — FAUX. Le coordinateur a ouvert la
## capture de vérification lui-même (règle du mandat : juger sur l'image,
## pas sur le résumé de l'agent) et a repéré que le corps v3 avait un plan
## différent du v2 (silhouette compacte + queue enroulée) plutôt que le
## même tendon fin en S avec plus de détail dedans. Vérifié ensuite par
## analyse en composantes connexes (scipy.ndimage.label) : le splash
## d'encre détaché de la référence (une composante séparée, ~53-74px sur
## le v2) avait été FUSIONNÉ au corps principal en une vraie queue (corps
## +27% de pixels, splash disparu) — un changement de composition, pas un
## ajout de détail. Cause : (1) bug d'implémentation, le script de guide
## relisait par erreur le fichier déjà écrasé par la sortie rejetée plutôt
## que le guide v2 propre ; (2) même corrigé, des taches de texture
## multi-pixels + une chaîne de gouttelettes dans l'écart pied/splash ont
## été interprétées par pixflux comme des indices de volume/continuité.
## LEÇON : un diff pixel-exact du GUIDE ne garantit pas que la SORTIE
## pixflux/create_character l'a suivi fidèlement — img2img à strength 120
## réinterprète la composition, pas seulement la couleur ; vérifier la
## sortie réelle (composantes connexes + profil de largeur par rangée),
## jamais seulement le guide d'entrée.
##
## RÉSULTAT FINAL (après 2 re-tentatives, guide simplifié — points de
## texture 1px puis stries 1x3px, gouttes 2px avec marge de collision
## vérifiée avant génération, plus aucun ajout entre le pied du tendon et
## le splash détaché) : composantes connexes = corps + splash disjoints sur
## LES 7 FRAMES de la séquence (pas seulement la référence statique),
## profil de largeur du tendon comparé rangée par rangée au v2 original —
## écart <= 2px partout. Crocs nettement irréguliers (tailles très
## variées, un croc visiblement ébréché), plusieurs gouttes d'encre
## visibles à des points distincts le long du tendon (pas seulement sous
## la mâchoire), légère texture de surface. Écart honnête restant avec la
## planche : la référence montre une texture de mâchoire plus organique
## (chair déchirée) et des mares d'encre plus grandes/franches au sol que
## ce qui a été obtenu ici — jugé suffisant pour répondre au reproche "pas
## assez détaillé" sans prétendre à une fidélité pixel-parfaite. Canvas
## cuit resté à 56x72 (bbox opaque max mesurée sur les 6 frames x=[7,49]
## y=[5,69], marge confortable — aucun agrandissement nécessaire).
## Ancienne version (composition en S, moins détaillée) archivée dans
## `assets/source/pixellab/gueule_vide/_archive_2026-08-22_v3/` et
## `assets/processed/sprites/gueule_vide/_archive_2026-08-22_v3/` (cp,
## jamais mv, copiée depuis git HEAD pour garantir l'état réellement commit
## et pas une version intermédiaire). FRAME_TICK_BOUNDS inchangé (même
## lecture de phases que la passe composition, la richesse ajoutée ne
## déplace aucune des 6 poses).
const FRAME_TICK_BOUNDS: Array[int] = [5, 9, 19, 27, 34, 42]

@onready var _sprite: AnimatedSprite2D = $AnimatedSprite2D

var _tick: int = 0
var _recipe_run_id: int = 0
var _contact_resolved: bool = false
var _natural_end: bool = false
var _owner_stats: Stats = null


func _ready() -> void:
	_sprite.play("cast")
	_sprite.pause()
	_sprite.frame = 0
	Sfx.play("spawn")
	_recipe_run_id = VfxRecipeRegistry.play(RECIPE_ID, {
		"origin": global_position,
		"seed": CAST_SEED,
		"direction": Vector2.RIGHT,
	})


## Addendum A, §A.4, "owner_death_policy". À appeler juste après avoir
## ajouté cette scène à l'arbre (voir Player._cast_gueule_vide()) — la
## créature observe la mort de son invocateur sans lui être asservie.
func set_owner_stats(stats: Stats) -> void:
	_owner_stats = stats
	if _owner_stats != null and not _owner_stats.died.is_connected(_on_owner_died):
		_owner_stats.died.connect(_on_owner_died)


## "owner_death_policy": "finish_core_then_stop_secondary" — "la
## créature termine sa morsure même si le joueur meurt (elle a été
## arrachée au monde, elle n'est pas liée à lui)". La créature (ce
## script) continue donc sa propre timeline normalement ; seules les
## couches VFX dégradables de la recette (A.1) sont coupées net, les
## protégées vont au bout de leur vie.
func _on_owner_died() -> void:
	VfxRecipeRegistry.cancel(_recipe_run_id, true)


## "cancellable_before": "release" — annulable jusqu'à la fin de la
## préparation (avant PREP_END_TICK, la morsure), plus après. Rien ne
## l'appelle encore (aucun système d'interruption/étourdissement
## n'existe côté gameplay) — la brique est posée pour quand ce sera le
## cas, sans en construire l'usage maintenant (§16.1).
func can_cancel() -> bool:
	return _tick < PREP_END_TICK


func cancel_cast() -> bool:
	if not can_cancel():
		return false
	VfxRecipeRegistry.cancel(_recipe_run_id, false)
	_natural_end = false
	queue_free()
	return true


func _physics_process(_delta: float) -> void:
	# La créature agit pour le compte du joueur (Phase R4, hit-stop
	# asymétrique) — is_player_frozen(), pas le générique is_frozen().
	if CombatFeedback.is_player_frozen():
		return
	_tick += 1
	_sprite.frame = _frame_for_tick(_tick)

	if not _contact_resolved and _tick >= CONTACT_TICK:
		_contact_resolved = true
		_resolve_contact()

	if _tick >= TOTAL_TICKS:
		_natural_end = true
		queue_free()


## "scene_change_policy": "stop_immediately" — quitte l'arbre pour
## n'importe quelle raison AUTRE que sa propre fin naturelle (changement
## de scène qui libère toute la branche, libération externe) => aucune
## couche VFX de cette recette ne doit lui survivre. La fin naturelle
## (timeout, TOTAL_TICKS) n'a pas besoin de ce nettoyage forcé : chaque
## couche s'éteint déjà proprement via sa propre lifetime_ticks.
func _exit_tree() -> void:
	if not _natural_end:
		VfxRecipeRegistry.cancel(_recipe_run_id, false)


func _frame_for_tick(tick: int) -> int:
	for i in FRAME_TICK_BOUNDS.size():
		if tick <= FRAME_TICK_BOUNDS[i]:
			return i
	return FRAME_TICK_BOUNDS.size() - 1


## "Recul obligatoire sur la cible touchée à l'impact, porté par
## Enemy.take_damage() comme pour le combo, pas une primitive de la
## recette" — mandat Gueule Vide. Même schéma que Player._try_hit().
func _resolve_contact() -> void:
	var target: Node = Targeting.nearest_enemy_in_radius(get_tree(), global_position, ATTACK_RANGE_PX)
	if target == null:
		return
	target.take_damage(ATTACK_DAMAGE, global_position)
	# C2 (docs/worklog.md) : hit-stop medium à l'impact, pas heavy comme
	# le proposait le diagnostic externe — Gueule Vide est explicitement
	# importance_tier 2/6 (data/recipes/power.gueule_vide.cast.json), un
	# heavy ici viderait le plafond réservé aux compétences majeures.
	# Phase R4 (retour croisé Gemini/ChatGPT, MANDAT SUITE v2) : shake +
	# camera-punch ajoutés (Gueule Vide était le seul pouvoir du joueur
	# à n'avoir NI l'un NI l'autre, trou confirmé par audit) via le
	# point d'entrée unique register_hit() — attacker_is_player=true
	# (la créature agit pour le compte du joueur, même côté du conflit).
	CombatFeedback.register_hit("medium", true, "heavy_impact", "light", Vector2.RIGHT, true)


## Tick courant du cast — utile aux tests/captures (même contrat que
## VfxDirector.get_current_tick() et Player._combo_tick).
func get_current_tick() -> int:
	return _tick


func is_finished() -> bool:
	return _tick >= TOTAL_TICKS
