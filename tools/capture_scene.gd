extends Node2D
## Scène de capture headless — docs/ARCHITECTURE_VFX_v3.md §13.3.
##
## "Scène de capture dédiée tools/capture_scene.tscn : charge une
## recette/animation, seed fixée, joue, exporte les frames en PNG
## (get_viewport().get_texture().get_image().save_png()) [...] Lancée par
## scripts/capture_headless.sh."
##
## Trois modes, un seul point d'entrée (jamais deux scènes de capture qui
## dupliqueraient la technique pause+3×process_frame ci-dessous) :
##
## --mode=primitive (par défaut, Phase 0) : capture UNE primitive nommée
##   à UN tick donné.
##   --primitive=impactFlashFrame   nom de primitive (VfxDirector._registry)
##   --seed=44102                   seed déterministe (traçabilité replay)
##   --tick=1                       tick physique auquel capturer
##   --lifetime_ticks=2             durée de vie donnée à la primitive (def. 2,
##                                  §4 "1-2 ticks" d'impactFlashFrame) — augmenter
##                                  pour capturer un tick significatif d'une
##                                  primitive à la durée de vie naturellement plus
##                                  longue (D, tranche 3 : spiral/orbital/etc.),
##                                  sinon le director la libère avant --tick.
##   --out=/chemin/absolu/sortie.png
##
## --mode=character (Phase 1.3+) : instancie le Player, joue une
##   animation nommée, capture une frame précise de cette animation.
##   --anim=idle_south               nom d'animation (SpriteFrames du Player) —
##                                  idle/déplacement sont désormais 8 rotations
##                                  réelles (E, mandat §6) : idle_south,
##                                  idle_north, idle_east, idle_west,
##                                  idle_south_east, idle_south_west,
##                                  idle_north_east, idle_north_west (et
##                                  déplacement_<même liste>) — coup1/2/3,
##                                  dash, hurt, mort restent "sud" seul.
##   --frame=0                      index de frame à capturer dans cette animation
##   --out=/chemin/absolu/sortie.png
##   --background=neutral|loaded    §13.2 "fond neutre + fond chargé" (def. neutral)
##   --scale=1|2|4                  §13.2 "1×/2×/4×" (def. 1), upscale NEAREST post-capture
##   Pas de RNG ici (frames PixelLab pré-cuites, pas de primitive
##   procédurale) donc --seed n'a pas de sens ; la traçabilité vient du
##   character_id/animation_group_id loggés dans data/pixellab_usage.jsonl.
##
##   "fond chargé" (§13.2) : aucun décor de jeu réel n'existe encore en
##   Phase 1 (pas de tuiles/salle) — matérialisé ici par un damier de test
##   généré procéduralement (_make_loaded_background), pas un asset final.
##   À remplacer par un vrai décor quand Phase 2+ apportera des tuiles.
##
## --mode=power (Phase 1.5+) : instancie une scène de pouvoir
##   (res://scenes/gameplay/powers/<power>.tscn), laisse la physique RÉELLE
##   tourner jusqu'à un tick donné (la créature pilote son propre cast en
##   autonome, contrairement au mode character qui pose juste une frame
##   figée), gèle puis capture — nécessaire ici car le mode character ne
##   gère pas une entité qui se détruit elle-même (queue_free) en fin de vie.
##   --power=gueule_vide            nom de la scène (scenes/gameplay/powers/<power>.tscn)
##   --tick=2                       tick physique auquel capturer (< durée totale du cast)
##   --background=neutral|loaded, --scale=1|2|4  mêmes conventions que character.
##   --out=/chemin/absolu/sortie.png
##
## --mode=player_action (D, Bras-Faux) : instancie le Player RÉEL (pas une
##   scène de pouvoir séparée) et simule une pression d'input via
##   Input.action_press/release — nécessaire pour toute action portée par
##   player.gd lui-même (Bras-Faux, esquive, dash, combo) plutôt que par
##   une scène de créature autonome comme Gueule Vide. Place aussi 2
##   ennemis (front + côté, mêmes offsets que _check_bras_faux() du smoke
##   test) pour rendre visible le recul multi-cible, pas juste le VFX seul.
##   --action=power2                 nom de l'InputMap action à presser 1 frame
##                                    (amendement GDD Pouvoir/déblocage :
##                                    power1..power5 sont des emplacements
##                                    génériques résolus via RunState.
##                                    active_power + le niveau du joueur,
##                                    voir Player.get_power_slot_info() —
##                                    fixer active_power dans le débogueur
##                                    avant de lancer cette capture si le
##                                    Pouvoir tiré au hasard ne convient pas)
##   --tick=16                       tick physique auquel capturer (compté
##                                    depuis la pression, pas depuis _ready())
##   --enemy_scene=<res://...tscn>    override diagnostic (CHANTIER 1, 2026-08-22,
##                                    "MANDAT ROUND 2") : par défaut EnemyScene
##                                    (le Placeholder Polygon2D générique, JAMAIS
##                                    spawné en jeu réel — gate_premiere.tscn
##                                    n'instancie que enemy_crawler/enemy_brute/
##                                    enemy_ranged). Permet de rejouer EXACTEMENT
##                                    la même capture avec une VRAIE scène de
##                                    monstre (Visual AnimatedSprite2D) pour
##                                    distinguer un artefact d'outil de capture
##                                    d'un vrai bug de rendu — sans ce paramètre,
##                                    aucun moyen de le vérifier autrement qu'en
##                                    rejouant la scène gate_premiere en vrai.
##   --background=neutral|loaded, --scale=1|2|4  mêmes conventions que character.
##   --out=/chemin/absolu/sortie.png
##
## Voir CLAUDE.md "Environnement de capture — écart documenté" : cette
## scène elle-même ne sait rien de xvfb/Vulkan logiciel — c'est
## scripts/capture_headless.sh qui choisit COMMENT lancer Godot. Ce
## fichier reste portable vers un vrai `--headless` le jour où ça
## fonctionnera dans l'environnement d'exécution.

const PlayerScene := preload("res://scenes/gameplay/player.tscn")
const EnemyScene := preload("res://scenes/gameplay/enemy.tscn")
const EnemyCrawlerScene := preload("res://scenes/gameplay/enemy_crawler.tscn")
const EnemyBruteScene := preload("res://scenes/gameplay/enemy_brute.tscn")
const EnemyRangedScene := preload("res://scenes/gameplay/enemy_ranged.tscn")


func _ready() -> void:
	var args := _parse_args()
	var mode: String = args.get("mode", "primitive")
	if mode == "character":
		await _run_character_capture(args)
	elif mode == "power":
		await _run_power_capture(args)
	elif mode == "player_action":
		await _run_player_action_capture(args)
	elif mode == "scene":
		await _run_scene_capture(args)
	elif mode == "player_action_sequence":
		await _run_player_action_sequence_capture(args)
	elif mode == "enemy_hit_reaction":
		await _run_enemy_hit_reaction_capture(args)
	elif mode == "enemy_chase_facing":
		await _run_enemy_chase_facing_capture(args)
	else:
		await _run_primitive_capture(args)


## --mode=player_action_sequence (render_detector.py, tools/README) : même
## mise en place que --mode=player_action (Player réel + 2 ennemis, mêmes
## offsets), mais capture UNE image PAR TICK de tick 0 (juste avant la
## pression du bouton — la baseline "avant effet" qu'attend render_detector)
## à --ticks=N inclus, nommées frame_0000.png.. dans --out_dir — le format
## exact que render_detector.load_frames_from_dir() attend (tick 0 = frame
## où l'input a été envoyé, comme documenté dans son schéma expected_layers).
## Jamais un seul geler-capturer-figer comme les autres modes : ici on doit
## geler PUIS DÉGELER entre deux captures pour laisser la physique avancer
## d'un tick à la fois — nouvelle fonction dédiée plutôt que de complexifier
## _freeze_and_wait_render() (qui ne dégèle jamais ailleurs, par design).
##   --action=power4                nom de l'InputMap action à presser 1 frame
##                                    (même remarque que --mode=player_action
##                                    ci-dessus : power1..power5 sont
##                                    génériques depuis l'amendement
##                                    Pouvoir/déblocage, dépend de
##                                    RunState.active_power)
##   --ticks=30                     dernier tick capturé, inclus (def. 30)
##   --out_dir=/chemin/absolu/      dossier de sortie (créé si besoin)
##   --scale=1|2|4                  même convention qu'ailleurs (def. 1)
##   --active_power=<id>            override diagnostic (mandat "fluidité",
##                                    Partie 2) — même rôle que --active_power
##                                    de --mode=player_action ci-dessus, requis
##                                    ici pour capturer un ENCHAÎNEMENT entre 2
##                                    compétences dédiées d'un même Pouvoir
##                                    (voir --action2 ci-dessous).
##   --level=<n>                    override diagnostic, même rôle que
##                                    --mode=player_action.
##   --action2=<name>               DEUXIÈME action InputMap pressée EN PLUS
##                                    de --action, au tick --action2_tick (les
##                                    deux ci-dessous doivent être fournis
##                                    ensemble) — mandat "fluidité" (Partie 2) :
##                                    seule façon de capturer RÉELLEMENT le
##                                    buffer d'input + la fenêtre d'annulation
##                                    en action (presser une 2e compétence
##                                    PENDANT que la 1ère joue encore, plutôt
##                                    que deux captures séparées qui ne
##                                    prouveraient rien sur l'enchaînement).
##   --action2_tick=<n>              tick (même horloge que les frames
##                                    capturées, 0 = juste avant --action) où
##                                    presser --action2.
##   --action3=<name>                TROISIÈME action InputMap, même
##                                    mécanique qu'--action2 (bible §3bis,
##                                    2026-08-27 — nécessaire pour vérifier
##                                    coup3 d'un combo de base à 3 coups en
##                                    jeu réel, pas seulement les 2 premiers
##                                    coups). Extension symétrique minimale,
##                                    aucun nouveau pipeline : même code que
##                                    --action2 ci-dessous, dupliqué pour un
##                                    3e appui plutôt que généralisé en
##                                    tableau (2 usages connus à ce jour,
##                                    pas de raison d'anticiper un 4e).
##   --action3_tick=<n>              tick où presser --action3 (même horloge).
func _run_player_action_sequence_capture(args: Dictionary) -> void:
	var action_name: String = args.get("action", "")
	var last_tick: int = int(args.get("ticks", "30"))
	var out_dir: String = args.get("out_dir", "")
	var scale: int = int(args.get("scale", "1"))
	var action2_name: String = args.get("action2", "")
	var action2_tick: int = int(args.get("action2_tick", "-1"))
	var action3_name: String = args.get("action3", "")
	var action3_tick: int = int(args.get("action3_tick", "-1"))
	if action_name == "" or out_dir == "":
		push_error("capture_scene[player_action_sequence]: --action et --out_dir sont requis.")
		get_tree().quit(1)
		return
	if not InputMap.has_action(action_name):
		push_error("capture_scene[player_action_sequence]: action InputMap introuvable '%s'." % action_name)
		get_tree().quit(1)
		return
	if action2_name != "" and not InputMap.has_action(action2_name):
		push_error("capture_scene[player_action_sequence]: --action2 introuvable '%s'." % action2_name)
		get_tree().quit(1)
		return
	if action3_name != "" and not InputMap.has_action(action3_name):
		push_error("capture_scene[player_action_sequence]: --action3 introuvable '%s'." % action3_name)
		get_tree().quit(1)
		return
	if not DirAccess.dir_exists_absolute(out_dir):
		DirAccess.make_dir_recursive_absolute(out_dir)

	# Même remarque que --mode=player_action : RunState.active_power est
	# tiré au hasard par défaut, un dev qui veut un Pouvoir précis (requis
	# pour --action2, qui vise une AUTRE compétence dédiée du MÊME Pouvoir)
	# doit pouvoir le forcer en headless.
	var forced_active_power: String = args.get("active_power", "")
	if forced_active_power != "":
		RunState.active_power = forced_active_power
	var forced_level: int = int(args.get("level", "0"))

	var player := PlayerScene.instantiate()
	player.global_position = Vector2(320, 200)
	player.facing = Vector2.RIGHT
	add_child(player)
	if forced_level > 0:
		player.stats.level = forced_level

	# Mêmes offsets que _run_player_action_capture()/_check_bras_faux().
	var enemy_front := EnemyScene.instantiate()
	enemy_front.global_position = player.global_position + Vector2(30, 0)
	add_child(enemy_front)

	var enemy_side := EnemyScene.instantiate()
	var side_dir := Vector2.RIGHT.rotated(deg_to_rad(30.0))
	enemy_side.global_position = player.global_position + side_dir * 30.0
	add_child(enemy_side)

	await get_tree().physics_frame

	# Chauffe de rendu (render_detector.py, vérification "alignement tick 0"
	# demandée par Milan) : constaté empiriquement que la TOUTE PREMIÈRE
	# image capturée après l'instanciation de la scène peut sortir avec un
	# fond NOIR (0,0,0) au lieu du gris neutre (76,76,76) stable de tous les
	# frames suivants — un artefact du rasterizer logiciel (llvmpipe) qui
	# n'a pas fini d'appliquer la couleur de fond/canvas dès la 1re image
	# rendue, pas un vrai changement de scène. Sans ce chauffage, ce frame
	# servirait de BASELINE à render_detector (tick 0) et ferait ressortir
	# une fausse détection massive ("tout" a changé dès le tick 1, jamais
	# crédible pour une seule primitive VFX) sur 100% de l'image. Quelques
	# process_frame de plus ici, AVANT de capturer la vraie baseline,
	# laissent le rasterizer se stabiliser une bonne fois.
	for i in range(3):
		await get_tree().process_frame

	var frame_paths: Array[String] = []
	# Tick 0 = capturé AVANT la pression, baseline "avant effet" — cohérent
	# avec le docstring de render_detector.py ("tick 0 = frame ou l'input a
	# ete envoye" : ce nom capture l'état juste avant que l'action ne prenne
	# effet, la première frame OU l'effet peut apparaître est le tick 1).
	#
	# PAS de pause ici (contrairement aux autres modes de ce fichier) :
	# geler/dégeler le SceneTree À CHAQUE tick d'une séquence s'est avéré
	# casser le rendu des primitives VFX (constaté empiriquement — un
	# groundRing visible en capture ponctuelle --mode=player_action
	# disparaissait entièrement en séquence avec pause/dégel répétés,
	# cause exacte non isolée mais reproductible). À la place : un seul
	# process_frame supplémentaire après chaque physics_frame pour laisser
	# le rendu rattraper le tick qui vient d'avancer, jamais de pause.
	frame_paths.append(await _capture_sequence_frame_no_pause(out_dir, 0, scale))

	Input.action_press(action_name)
	await get_tree().physics_frame
	await get_tree().process_frame
	Input.action_release(action_name)
	# --action2 pressée au tick 0 pile (rare, mais gardé cohérent avec le
	# reste de la boucle ci-dessous plutôt qu'un cas à part non couvert).
	if action2_name != "" and action2_tick == 0:
		Input.action_press(action2_name)
		await get_tree().physics_frame
		await get_tree().process_frame
		Input.action_release(action2_name)

	for tick in range(1, last_tick + 1):
		frame_paths.append(await _capture_sequence_frame_no_pause(out_dir, tick, scale))
		if tick < last_tick:
			await get_tree().physics_frame
			await get_tree().process_frame
			# Presse --action2 UNE FOIS le tick atteint (mandat "fluidité") —
			# APRÈS avoir capturé la frame de ce même tick (la frame N montre
			# l'état AVANT que cette pression ne prenne effet, cohérent avec
			# la convention "tick 0 = avant --action" déjà en place ci-dessus),
			# et APRÈS le couple physics_frame/process_frame qui fait avancer
			# la simulation d'un tick — même point d'insertion que --action au
			# tout début de cette fonction.
			if action2_name != "" and tick + 1 == action2_tick:
				Input.action_press(action2_name)
				await get_tree().physics_frame
				await get_tree().process_frame
				Input.action_release(action2_name)
			# Même point d'insertion, même logique, pour un 3e appui —
			# indépendant du bloc --action2 ci-dessus (les deux peuvent
			# tomber sur le même tick sans interférence, même s'il n'existe
			# pas de cas d'usage connu qui les ferait coïncider).
			if action3_name != "" and tick + 1 == action3_tick:
				Input.action_press(action3_name)
				await get_tree().physics_frame
				await get_tree().process_frame
				Input.action_release(action3_name)

	var report := {
		"out_dir": out_dir,
		"action": action_name,
		"action2": action2_name,
		"action2_tick": action2_tick,
		"action3": action3_name,
		"action3_tick": action3_tick,
		"ticks_captured": frame_paths.size(),
		"frames": frame_paths,
	}
	print("CAPTURE_RESULT ", JSON.stringify(report))
	get_tree().quit(0)


## Capture SANS geler le SceneTree (voir note ci-dessus) — un process_frame
## de plus avant la capture pour laisser le rendu rattraper le dernier
## physics_frame consommé par l'appelant, jamais de pause/dégel.
func _capture_sequence_frame_no_pause(out_dir: String, tick: int, scale: int) -> String:
	await get_tree().process_frame
	var img: Image = get_viewport().get_texture().get_image()
	if scale > 1:
		img.resize(img.get_width() * scale, img.get_height() * scale, Image.INTERPOLATE_NEAREST)
	var path := out_dir.path_join("frame_%04d.png" % tick)
	_save_png(img, path)
	return path


## --mode=enemy_hit_reaction (CHANTIER C, production v1, "Monstres :
## animations d'interaction") : instancie UN monstre réel (crawler/brute/
## ranged), lui inflige `--hits` coups de take_damage() venant de
## `--direction` (même convention que Enemy._select_directional_reaction()
## et les checks smoke test — right=(50,0), left=(-50,0), front=(0,50),
## back=(0,-50)), capture une SÉQUENCE de frames (tick 0 = idle avant tout
## coup, puis 1 frame par tick jusqu'à `--ticks`) — jamais une pose
## isolée, la discipline de vérification du mandat demande la réaction EN
## MOUVEMENT. Même technique "process_frame sans pause" que
## _run_player_action_sequence_capture() (une pause/dégel répétée a déjà
## cassé du rendu VFX ailleurs dans ce fichier, note ci-dessus).
##   --monster=crawler|brute|ranged
##   --direction=right|left|front|back
##   --hits=1                        nombre de take_damage() successifs (un par
##                                    tick, 3 = déclenche le chancellement,
##                                    STAGGER_TRIGGER_HITS dans enemy.gd)
##   --ticks=30                      ticks capturés APRÈS le dernier coup
##   --out_dir=/chemin/absolu/
##   --scale=1|2|4
func _run_enemy_hit_reaction_capture(args: Dictionary) -> void:
	var monster_name: String = args.get("monster", "crawler")
	var direction: String = args.get("direction", "right")
	var hits: int = int(args.get("hits", "1"))
	var last_tick: int = int(args.get("ticks", "30"))
	var out_dir: String = args.get("out_dir", "")
	var scale: int = int(args.get("scale", "1"))
	if out_dir == "":
		push_error("capture_scene[enemy_hit_reaction]: --out_dir requis.")
		get_tree().quit(1)
		return
	if not DirAccess.dir_exists_absolute(out_dir):
		DirAccess.make_dir_recursive_absolute(out_dir)

	var scene: PackedScene
	match monster_name:
		"brute":
			scene = EnemyBruteScene
		"ranged":
			scene = EnemyRangedScene
		_:
			scene = EnemyCrawlerScene

	var offsets: Dictionary = {
		"right": Vector2(50, 0), "left": Vector2(-50, 0),
		"front": Vector2(0, 50), "back": Vector2(0, -50),
	}
	var offset: Vector2 = offsets.get(direction, Vector2(50, 0))

	var enemy := scene.instantiate()
	enemy.global_position = Vector2(320, 220)
	add_child(enemy)

	await get_tree().physics_frame
	for i in range(3):  # chauffe de rendu, même remarque que player_action_sequence
		await get_tree().process_frame

	var frame_paths: Array[String] = []
	frame_paths.append(await _capture_sequence_frame_no_pause(out_dir, 0, scale))

	for h in range(hits):
		if not is_instance_valid(enemy):
			break
		enemy.take_damage(5.0, enemy.global_position + offset)
		await get_tree().physics_frame
		await get_tree().process_frame

	for tick in range(1, last_tick + 1):
		if not is_instance_valid(enemy):
			break
		frame_paths.append(await _capture_sequence_frame_no_pause(out_dir, tick, scale))
		if tick < last_tick:
			await get_tree().physics_frame
			await get_tree().process_frame

	var report := {
		"out_dir": out_dir, "monster": monster_name, "direction": direction,
		"hits": hits, "ticks_captured": frame_paths.size(), "frames": frame_paths,
	}
	print("CAPTURE_RESULT ", JSON.stringify(report))
	get_tree().quit(0)


## --mode=enemy_chase_facing (MANDAT playtest réel, retour Milan 2026-08-26 :
##   "les 3 monstres restent TOUS orientés dans la même direction ... ne le
##   font jamais") : livrable avant/après de VÉRIFICATION VISUELLE demandé
##   par le mandat, complément de _check_enemy_faces_chase_direction_in_
##   multiple_directions() (tools/smoke_test_gameplay.gd, assertion logique
##   sur flip_h) — ici on capture le RENDU réel, deux PNG montrant le même
##   monstre chasser un Joueur réel posé successivement à GAUCHE puis à
##   DROITE de sa position de départ (le Joueur ne se déplace pas
##   lui-même, c'est le monstre qui chasse — Targeting.get_player() n'a
##   besoin que d'un Joueur vivant dans le groupe "player", aucune pression
##   d'input requise).
##   --monster=crawler|brute|ranged (def. crawler)
##   --offset_px=200                distance Joueur/monstre à chaque
##                                   repositionnement (def. 200 — hors
##                                   attack_range_px des 3 archétypes ET
##                                   sous aggro_radius_px, garantit un vrai
##                                   CHASE en mouvement, jamais un
##                                   télégraphe immobile ni un retour à IDLE)
##   --ticks=40                     ticks physiques attendus après chaque
##                                   repositionnement du Joueur avant de
##                                   capturer (def. 40 — laisse le monstre
##                                   quitter IDLE, entrer CHASE, et
##                                   _update_visual_bob() poser flip_h)
##   --out_dir=/chemin/absolu/      écrit facing_left.png puis facing_right.png
##   --scale=1|2|4                  même convention qu'ailleurs (def. 1)
func _run_enemy_chase_facing_capture(args: Dictionary) -> void:
	var monster_name: String = args.get("monster", "crawler")
	var offset_px: float = float(args.get("offset_px", "200"))
	var wait_ticks: int = int(args.get("ticks", "40"))
	var out_dir: String = args.get("out_dir", "")
	var scale: int = int(args.get("scale", "1"))
	if out_dir == "":
		push_error("capture_scene[enemy_chase_facing]: --out_dir requis.")
		get_tree().quit(1)
		return
	if not DirAccess.dir_exists_absolute(out_dir):
		DirAccess.make_dir_recursive_absolute(out_dir)

	var scene: PackedScene
	match monster_name:
		"brute":
			scene = EnemyBruteScene
		"ranged":
			scene = EnemyRangedScene
		_:
			scene = EnemyCrawlerScene

	var enemy := scene.instantiate()
	enemy.global_position = Vector2(320, 220)
	add_child(enemy)

	var player := PlayerScene.instantiate()
	add_child(player)

	# --- Moitié 1 : Joueur posé à GAUCHE de la position de DÉPART du monstre
	# -> le monstre doit chasser vers -x (flip_h attendu = true,
	# "touche_lateral" gauche, même convention que
	# _select_directional_reaction()). ---
	player.global_position = enemy.global_position + Vector2(-offset_px, 0)
	await get_tree().physics_frame
	for i in range(wait_ticks):
		await get_tree().physics_frame

	var visual_left: AnimatedSprite2D = enemy.get_node("Visual")
	var flip_h_left: bool = visual_left.flip_h
	var velocity_x_left: float = enemy.velocity.x
	var state_left: int = enemy._state

	await _freeze_and_wait_render()
	var img_left: Image = get_viewport().get_texture().get_image()
	if scale > 1:
		img_left.resize(img_left.get_width() * scale, img_left.get_height() * scale, Image.INTERPOLATE_NEAREST)
	var path_left := out_dir.path_join("facing_left.png")
	var err_left := _save_png(img_left, path_left)

	# --- Moitié 2 : Joueur téléporté à DROITE de la position COURANTE du
	# monstre (déjà avancé vers -x pendant la moitié 1 — ancrer sur cette
	# position à CE moment précis, jamais sur la position de départ figée,
	# sous peine de sortir du rayon d'aggro : `offset_px` cumulé à la
	# distance déjà parcourue dépasserait `aggro_radius_px` et le monstre
	# retomberait en IDLE au lieu de renverser son cap — piège trouvé en
	# vérifiant le premier essai de cette capture, diagnostic explicite
	# dans le rapport JSON ci-dessous, "state":0/IDLE inattendu) -> le
	# monstre doit RENVERSER son cap et chasser vers +x (flip_h attendu =
	# false). Dégèle d'abord : le monstre doit continuer de chasser
	# RÉELLEMENT, pas reprendre depuis un état gelé artificiellement. ---
	get_tree().paused = false
	player.global_position = enemy.global_position + Vector2(offset_px, 0)

	for i in range(wait_ticks):
		await get_tree().physics_frame

	var flip_h_right: bool = visual_left.flip_h
	var velocity_x_right: float = enemy.velocity.x
	var state_right: int = enemy._state

	await _freeze_and_wait_render()
	var img_right: Image = get_viewport().get_texture().get_image()
	if scale > 1:
		img_right.resize(img_right.get_width() * scale, img_right.get_height() * scale, Image.INTERPOLATE_NEAREST)
	var path_right := out_dir.path_join("facing_right.png")
	var err_right := _save_png(img_right, path_right)

	var report := {
		"out_dir": out_dir, "monster": monster_name, "offset_px": offset_px, "ticks": wait_ticks,
		"facing_left_png": path_left, "facing_left_save_err": err_left,
		"facing_right_png": path_right, "facing_right_save_err": err_right,
		"diagnostic": {
			"left_half": {"flip_h": flip_h_left, "velocity_x": velocity_x_left, "state": state_left},
			"right_half": {"flip_h": flip_h_right, "velocity_x": velocity_x_right, "state": state_right},
		},
	}
	print("CAPTURE_RESULT ", JSON.stringify(report))
	get_tree().quit(0 if (err_right == OK and err_left == OK) else 1)


## --mode=scene (Chantier B, vérification décor) : instancie une scène
## RÉELLE quelconque (res://scenes/...) via une Camera2D positionnée à la
## demande, laisse tourner quelques ticks si besoin, capture — pour
## vérifier un décor (TileMapLayer, props) sans dépendre d'un mode dédié
## par écran. Pas un remplacement des modes existants (character/power/
## player_action restent la référence pour le personnage/les pouvoirs) :
## seulement pour des scènes qui n'ont pas encore de mode spécifique.
##   --scene_path=res://scenes/gameplay/gate_premiere.tscn
##   --cam_x=640 --cam_y=300 --cam_zoom=1.0
##   --wait_ticks=1                 ticks physiques avant capture (def. 1)
##   --background=neutral|loaded, --scale=1|2|4  mêmes conventions qu'ailleurs.
##   --use_scene_camera=1           Phase R4 (BASE_ZOOM permanent) : n'injecte
##                                  PAS de Camera2D — laisse la caméra RÉELLE
##                                  de la scène (celle de Player, pilotée par
##                                  CameraDirector.get_zoom() à chaque tick)
##                                  rester active, pour vérifier le zoom de
##                                  base EN JEU RÉEL plutôt qu'un cam_zoom
##                                  choisi à la main qui l'écraserait. --cam_x/
##                                  y/zoom ignorés dans ce mode (def. 0/off).
##   --out=/chemin/absolu/sortie.png
func _run_scene_capture(args: Dictionary) -> void:
	var scene_path: String = args.get("scene_path", "")
	var out_path: String = args.get("out", "")
	var cam_x: float = float(args.get("cam_x", "320"))
	var cam_y: float = float(args.get("cam_y", "180"))
	var cam_zoom: float = float(args.get("cam_zoom", "1.0"))
	var wait_ticks: int = int(args.get("wait_ticks", "1"))
	var scale: int = int(args.get("scale", "1"))
	var use_scene_camera: bool = args.get("use_scene_camera", "0") == "1"
	if scene_path == "" or out_path == "":
		push_error("capture_scene[scene]: --scene_path et --out sont requis.")
		get_tree().quit(1)
		return
	if not ResourceLoader.exists(scene_path):
		push_error("capture_scene[scene]: scène introuvable '%s'." % scene_path)
		get_tree().quit(1)
		return

	var packed: PackedScene = load(scene_path)
	var instance: Node = packed.instantiate()
	add_child(instance)

	if not use_scene_camera:
		var cam := Camera2D.new()
		cam.position = Vector2(cam_x, cam_y)
		cam.zoom = Vector2(cam_zoom, cam_zoom)
		add_child(cam)
		cam.make_current()

	for i in range(wait_ticks):
		await get_tree().physics_frame

	await _freeze_and_wait_render()

	var img: Image = get_viewport().get_texture().get_image()
	if scale > 1:
		img.resize(img.get_width() * scale, img.get_height() * scale, Image.INTERPOLATE_NEAREST)
	var err := _save_png(img, out_path)

	var report := {
		"save_err": err, "out_path": out_path, "size": [img.get_width(), img.get_height()],
		"mode": "scene", "scene_path": scene_path, "use_scene_camera": use_scene_camera,
		"cam": [cam_x, cam_y, cam_zoom], "wait_ticks": wait_ticks, "scale": scale,
	}
	print("CAPTURE_RESULT ", JSON.stringify(report))
	get_tree().quit(0 if err == OK else 1)


func _run_player_action_capture(args: Dictionary) -> void:
	var action_name: String = args.get("action", "")
	var target_tick: int = int(args.get("tick", "16"))
	var out_path: String = args.get("out", "")
	var background: String = args.get("background", "neutral")
	var scale: int = int(args.get("scale", "1"))
	# --enemy_scene= (CHANTIER 1, diagnostic) : par défaut EnemyScene
	# (Placeholder), override possible vers une vraie scène de monstre.
	var enemy_scene_path: String = args.get("enemy_scene", "")
	var enemy_scene: PackedScene = EnemyScene
	if enemy_scene_path != "":
		if not ResourceLoader.exists(enemy_scene_path):
			push_error("capture_scene[player_action]: --enemy_scene introuvable '%s'." % enemy_scene_path)
			get_tree().quit(1)
			return
		enemy_scene = load(enemy_scene_path)
	if action_name == "" or out_path == "":
		push_error("capture_scene[player_action]: --action et --out sont requis.")
		get_tree().quit(1)
		return
	if not InputMap.has_action(action_name):
		push_error("capture_scene[player_action]: action InputMap introuvable '%s'." % action_name)
		get_tree().quit(1)
		return

	if background == "loaded":
		add_child(_make_loaded_background())

	# --active_power=<id> (outil de capture uniquement, jamais consulté par
	# le gameplay réel) : RunState.active_power est tiré au hasard à la
	# construction de l'autoload — un dev qui veut capturer précisément un
	# power1..5 d'un Pouvoir donné doit pouvoir le forcer sans debugger
	# attaché en headless (cf. docstring ci-dessus, "fixer active_power
	# dans le débogueur" n'est pas praticable ici).
	var forced_active_power: String = args.get("active_power", "")
	if forced_active_power != "":
		RunState.active_power = forced_active_power
	var forced_level: int = int(args.get("level", "0"))

	var player := PlayerScene.instantiate()
	player.global_position = Vector2(320, 200)
	player.facing = Vector2.RIGHT
	add_child(player)
	if forced_level > 0:
		player.stats.level = forced_level

	# Mêmes offsets que _check_bras_faux() (tools/smoke_test_gameplay.gd) :
	# un ennemi devant (0°, dans l'arc) et un sur le côté (30°, dans l'arc)
	# pour que le recul multi-cible soit visible dans la capture, pas
	# seulement le VFX seul sur une salle vide.
	var enemy_front := enemy_scene.instantiate()
	enemy_front.global_position = player.global_position + Vector2(30, 0)
	add_child(enemy_front)

	var enemy_side := enemy_scene.instantiate()
	var side_dir := Vector2.RIGHT.rotated(deg_to_rad(30.0))
	enemy_side.global_position = player.global_position + side_dir * 30.0
	add_child(enemy_side)

	await get_tree().physics_frame

	Input.action_press(action_name)
	await get_tree().physics_frame
	Input.action_release(action_name)

	# Compté depuis la pression (pas depuis _ready()) — même sonde par
	# comptage de physics_frame que le smoke test (_wait_until), la
	# physique RÉELLE du Player pilote son propre état, aucune horloge
	# externe à interroger comme VfxDirector.get_current_tick() en mode
	# primitive.
	var ticks_waited := 0
	while ticks_waited < target_tick:
		await get_tree().physics_frame
		ticks_waited += 1

	await _freeze_and_wait_render()

	var img: Image = get_viewport().get_texture().get_image()
	if scale > 1:
		img.resize(img.get_width() * scale, img.get_height() * scale, Image.INTERPOLATE_NEAREST)
	var err := _save_png(img, out_path)

	var report := {
		"save_err": err,
		"out_path": out_path,
		"size": [img.get_width(), img.get_height()],
		"mode": "player_action",
		"action": action_name,
		"tick": target_tick,
		"background": background,
		"scale": scale,
	}
	print("CAPTURE_RESULT ", JSON.stringify(report))
	get_tree().quit(0 if err == OK else 1)


func _run_power_capture(args: Dictionary) -> void:
	var power_name: String = args.get("power", "")
	var target_tick: int = int(args.get("tick", "2"))
	var out_path: String = args.get("out", "")
	var background: String = args.get("background", "neutral")
	var scale: int = int(args.get("scale", "1"))
	if power_name == "" or out_path == "":
		push_error("capture_scene[power]: --power et --out sont requis.")
		get_tree().quit(1)
		return

	var scene_path := "res://scenes/gameplay/powers/%s.tscn" % power_name
	if not ResourceLoader.exists(scene_path):
		push_error("capture_scene[power]: scène introuvable '%s'." % scene_path)
		get_tree().quit(1)
		return

	if background == "loaded":
		add_child(_make_loaded_background())

	var power_scene: PackedScene = load(scene_path)
	var instance: Node2D = power_scene.instantiate()
	instance.global_position = Vector2(320, 260)
	add_child(instance)

	# Physique RÉELLE (pas de pause avant le tick cible) : la créature
	# avance sa propre horloge en autonome — même sondage que
	# _run_primitive_capture() pour VfxDirector.get_current_tick(), avec
	# la même course déjà trouvée en Phase 0 (l'ordre entre la reprise
	# d'un `await physics_frame` et le `_physics_process` d'un AUTRE nœud
	# pour ce même pas n'est pas garanti).
	while is_instance_valid(instance) and instance.get_current_tick() < target_tick:
		await get_tree().physics_frame

	if not is_instance_valid(instance):
		push_warning("capture_scene[power]: '%s' s'est libéré avant le tick %d (durée de vie trop courte)." % [power_name, target_tick])

	await _freeze_and_wait_render()

	var img: Image = get_viewport().get_texture().get_image()
	if scale > 1:
		img.resize(img.get_width() * scale, img.get_height() * scale, Image.INTERPOLATE_NEAREST)
	var err := _save_png(img, out_path)

	var report := {
		"save_err": err,
		"out_path": out_path,
		"size": [img.get_width(), img.get_height()],
		"mode": "power",
		"power": power_name,
		"tick": target_tick,
		"background": background,
		"scale": scale,
	}
	print("CAPTURE_RESULT ", JSON.stringify(report))
	get_tree().quit(0 if err == OK else 1)


func _run_character_capture(args: Dictionary) -> void:
	var anim_name: String = args.get("anim", "idle_south")
	var frame_index: int = int(args.get("frame", "0"))
	var out_path: String = args.get("out", "")
	var background: String = args.get("background", "neutral")
	var scale: int = int(args.get("scale", "1"))
	if out_path == "":
		push_error("capture_scene[character]: --out manquant, rien à écrire.")
		get_tree().quit(1)
		return

	if background == "loaded":
		add_child(_make_loaded_background())

	var player := PlayerScene.instantiate()
	player.global_position = Vector2(320, 260)
	add_child(player)

	var sprite: AnimatedSprite2D = player.get_node("AnimatedSprite2D")
	sprite.play(anim_name)
	sprite.frame = frame_index
	sprite.pause()  # fige sur cette frame précise, jamais une capture "au hasard" du timing

	# PAS d'await physics_frame ici, volontairement : Player._physics_process
	# bascule automatiquement idle/deplacement selon le mouvement (aucune
	# entrée pressée pendant une capture) — le laisser tourner ne serait-ce
	# qu'un pas physique écraserait silencieusement l'anim demandée
	# (hurt/dash/mort) en la remettant sur "idle". L'état déjà posé
	# ci-dessus (frame gelée) est rendu correctement par les process_frame
	# de _freeze_and_wait_render() sans qu'aucune physique n'ait besoin de
	# tourner.
	await _freeze_and_wait_render()

	var img: Image = get_viewport().get_texture().get_image()
	if scale > 1:
		img.resize(img.get_width() * scale, img.get_height() * scale, Image.INTERPOLATE_NEAREST)
	var err := _save_png(img, out_path)

	var report := {
		"save_err": err,
		"out_path": out_path,
		"size": [img.get_width(), img.get_height()],
		"mode": "character",
		"anim": anim_name,
		"frame": frame_index,
		"frame_count": sprite.sprite_frames.get_frame_count(anim_name),
		"background": background,
		"scale": scale,
	}
	print("CAPTURE_RESULT ", JSON.stringify(report))
	get_tree().quit(0 if err == OK else 1)


## "fond chargé" (§13.2) : damier de test généré procéduralement — aucun
## décor de jeu réel n'existe encore en Phase 1 (voir note de tête de
## fichier). Motif déterministe (aucun RNG), deux tons neutres proches de
## la bande "decor" (data/palettes/value_bands.json) pour rester dans
## l'esprit d'un fond de jeu sans prétendre en être un.
func _make_loaded_background() -> Sprite2D:
	var vw: int = ProjectSettings.get_setting("display/window/size/viewport_width", 640)
	var vh: int = ProjectSettings.get_setting("display/window/size/viewport_height", 360)
	var img := Image.create(vw, vh, false, Image.FORMAT_RGBA8)
	const CELL := 16
	# Tons ocre chauds (2026-08-22, principe d'écart de lisibilité Milan) —
	# avant, un damier gris neutre désaturé, qui ne représentait pas le sol
	# ambiant réel des salles éclairées (Addendum C) et masquait les VFX
	# trop discrets/trop clairs restant lisibles ici mais invisibles en jeu
	# réel. Valeurs dérivées de data/palettes/value_bands.json (sol ambiant
	# mesuré ~24-37% V, hue ocre ~35-38°) : un "fond chargé" qui teste
	# vraiment contre l'ambiance qui pose problème.
	var tone_a := Color8(76, 62, 42, 255)
	var tone_b := Color8(92, 78, 55, 255)
	for y in range(vh):
		for x in range(vw):
			var cell_index := (x / CELL) + (y / CELL)
			img.set_pixel(x, y, tone_a if cell_index % 2 == 0 else tone_b)
	var sprite := Sprite2D.new()
	sprite.centered = false
	sprite.position = Vector2.ZERO
	sprite.texture = ImageTexture.create_from_image(img)
	return sprite


func _run_primitive_capture(args: Dictionary) -> void:
	var primitive_name: String = args.get("primitive", "impactFlashFrame")
	var seed_val: int = int(args.get("seed", "0"))
	var target_tick: int = int(args.get("tick", "1"))
	var out_path: String = args.get("out", "")
	# Défaut historique (2) gardé tel quel pour ne rien changer aux appels
	# existants — certaines primitives (D, tranche 3) ont une durée de vie
	# naturelle bien plus longue ; --lifetime_ticks permet de capturer un
	# tick significatif de LEUR propre timeline plutôt que de les figer
	# artificiellement à 2, ce qui les libérerait avant --tick demandé.
	var lifetime_ticks: int = int(args.get("lifetime_ticks", "2"))

	if out_path == "":
		push_error("capture_scene: --out manquant, rien à écrire.")
		get_tree().quit(1)
		return

	# Centre du viewport logique 640×360 (§0) — origine par défaut d'un
	# test isolé, aucun perso/salle n'existe encore en Phase 0.
	var origin := Vector2(320, 180)

	VfxDirector.clear_log()
	var node := VfxDirector.spawn(primitive_name, {
		"seed": seed_val,
		"origin": origin,
		"lifetime_ticks": lifetime_ticks,
		"overdraw_cost": 12.0,
	})
	if node == null:
		push_error("capture_scene: spawn refusé pour '%s' (budget ou primitive inconnue) — voir logs ci-dessus." % primitive_name)
		get_tree().quit(1)
		return

	# Avance jusqu'au tick demandé via le vrai pas physique (60/s, §0) —
	# jamais un délai réel (create_timer), qui dérive sous charge hôte.
	# EN SONDANT VfxDirector.get_current_tick(), pas en comptant les
	# `await physics_frame` un par un : trouvé pendant la validation
	# Phase 0 (docs/worklog.md) que le signal `physics_frame` peut
	# réveiller ce coroutine AVANT que VfxDirector._physics_process ait
	# fini de tourner pour ce même pas (ordre non garanti entre la
	# reprise d'un `await` et le traitement physique des autres nœuds).
	# Compter les réveils du signal comme s'ils valaient chacun un tick
	# VfxDirector était donc faux d'un cran, silencieusement — sonder
	# l'état RÉEL du compteur élimine la course au lieu de la masquer.
	while VfxDirector.get_current_tick() < target_tick:
		await get_tree().physics_frame

	# GÈLE la simulation avant d'attendre le rendu. Trouvé pendant la
	# validation Phase 0 (docs/worklog.md) : le pipeline de rendu de
	# Godot bufferise plusieurs images — un seul process_frame après le
	# tick cible capture une image pas encore rasterisée (fond par défaut
	# seul, VFX absent), mais attendre plusieurs process_frame SANS geler
	# laisse la physique continuer d'avancer (1 tick/frame avec
	# max_physics_steps_per_frame=1, project.godot) et tuait la primitive
	# de test (durée de vie 1-2 ticks, §4) avant même la capture. Geler
	# arrête net l'avancement des ticks (VfxDirector, un autoload,
	# n'échappe pas à la pause par défaut) SANS arrêter le rendu — la
	# redraw déjà posée par le dernier tick(...) continue d'être
	# rasterisée normalement pendant qu'on attend.
	await _freeze_and_wait_render()

	var img: Image = get_viewport().get_texture().get_image()
	var err := _save_png(img, out_path)

	var log_entry: Dictionary = VfxDirector.spawn_log[0] if VfxDirector.spawn_log.size() > 0 else {}
	var report := {
		"save_err": err,
		"out_path": out_path,
		"size": [img.get_width(), img.get_height()],
		"primitive": primitive_name,
		"seed": seed_val,
		"tick": target_tick,
		"spawn_log_entry": log_entry,
		"active_count": VfxDirector.get_active_count(),
		"current_tick": VfxDirector.get_current_tick(),
		"engine_max_physics_steps": Engine.get_max_physics_steps_per_frame(),
		"engine_physics_ticks": Engine.physics_ticks_per_second,
		"pixel_at_origin": var_to_str(img.get_pixel(int(origin.x), int(origin.y))),
		"pixel_corner": var_to_str(img.get_pixel(10, 10)),
	}
	print("CAPTURE_RESULT ", JSON.stringify(report))

	get_tree().quit(0 if err == OK else 1)


## Gèle la simulation puis attend 3 process_frame avant de lire le
## viewport — technique prouvée en Phase 0 (docs/worklog.md) : le pipeline
## de rendu de Godot bufferise plusieurs images, un seul process_frame
## après avoir posé l'état voulu capture parfois une image pas encore
## rasterisée. Geler (get_tree().paused = true) arrête net toute
## simulation (physique, autoloads) SANS arrêter le rendu, donc la
## dernière redraw posée continue d'être rasterisée normalement pendant
## qu'on attend — utilisé tel quel par les deux modes de capture.
func _freeze_and_wait_render() -> void:
	get_tree().paused = true
	await get_tree().process_frame
	await get_tree().process_frame
	await get_tree().process_frame


func _save_png(img: Image, out_path: String) -> Error:
	var dir_path := out_path.get_base_dir()
	if dir_path != "" and not DirAccess.dir_exists_absolute(dir_path):
		DirAccess.make_dir_recursive_absolute(dir_path)
	return img.save_png(out_path)


func _parse_args() -> Dictionary:
	var result := {}
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--") and arg.contains("="):
			var kv := arg.substr(2).split("=", true, 1)
			result[kv[0]] = kv[1]
	return result
