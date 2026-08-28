extends CharacterBody2D
class_name Player
## Personnage jouable — mouvement 8 directions + stats + animations de
## base (Phase 1.3) + combo léger 3 coups (Phase 1.4). `AnimatedSprite2D`
## + `SpriteFrames` cuits par scripts/cook_character_frames.py, direction
## sud uniquement pour l'instant — voir docs/worklog.md.
##
## Entrée : actions UI par défaut de Godot (ui_left/right/up/down) pour le
## mouvement — aucune exigence de contrôles réels dans le mandat Phase 1.
## Une action dédiée "attack" existe dans project.godot (espace + clic
## gauche) car le combo, lui, a besoin d'un input propre à détecter au
## tick près (just_pressed), ce que les actions ui_* génériques ne
## garantissent pas aussi proprement pour du timing de combat.

const AttackAnimName := ["coup1", "coup2", "coup3"]

## MANDAT "retours de playtest réel" (point 1, PRIORITÉ ABSOLUE) — softlock
## confirmé : `die()` verrouillait l'input et jouait "mort" mais rien
## n'existait nulle part dans le dépôt pour en sortir (aucune fonction
## new_run()/restart(), déjà signalé comme un manque dans docs/worklog.md
## au sujet de RunState). GDD ne prévoit aucun écran de fin/narratif pour
## ce cas — option minimale explicitement autorisée par Milan : "un état
## mort qui permet de relancer une nouvelle run sans recharger la page".
## Délai avant d'accepter l'input de relance (au lieu d'un restart instantané
## dès `die()`) : laisse la frame "mort" se lire au moins une seconde avant
## qu'un appui accidentel (ex. la touche qui vient de tuer le joueur,
## encore enfoncée) ne relance déjà la run suivante.
const DEATH_RESTART_INPUT_ENABLED_TICKS := 60

## Timeline d'un coup, en ticks (60/s) — §6.2 du doc VFX donne des
## fourchettes pour les VFX/animations premium (anticipation 25-40%,
## release 5-12%, recovery 35-55%) ; ces chiffres respectent ces
## proportions pour un coup léger rapide (26 ticks ≈ 0,43s/coup).
const ANTICIPATION_TICKS := 8
const RELEASE_TICKS := 4
const RECOVERY_TICKS := 14
## Fenêtre de chaînage (mandat Phase 1.4 : "fenêtre de chaînage sur les
## derniers ticks de chaque RECOVERY") — dernier tiers de la recovery.
const CHAIN_WINDOW_TICKS := 6

## MANDAT "fluidité" (Partie 2, couche code) — généralisation de l'embryon
## de buffer d'input qui n'existait jusqu'ici QUE pour le combo de base
## (_attack_queued/CHAIN_WINDOW_TICKS ci-dessus) aux 5 compétences dédiées
## (Bras-Faux/Poing Belluaire/Poing Tellurique/Marée de Sable/Gueule Vide).
## Avant ce mandat, un appui sur un slot de pouvoir pendant `_action_lock`
## était silencieusement perdu (chaque `_start_*()` de compétence retourne
## tôt sur `_action_lock`, sans jamais retenir l'appui) — voir
## `_try_activate_power_slot()`/`_queued_power_slot` plus bas.
##
## `INPUT_BUFFER_TICKS` est volontairement COURT ("fenêtre courte, quelques
## ticks" du mandat) : il n'a jamais vocation à retenir un appui donné au
## tout DÉBUT d'une longue animation (ça ressemblerait à une file d'attente
## illimitée, pas un buffer) — seulement un appui donné PEU AVANT que la
## fenêtre d'annulation de l'action en cours ne s'ouvre (voir
## `<SKILL>_CANCEL_WINDOW_TICKS` sur chaque compétence ci-dessous), exactement
## comme un joueur qui anticipe la fin d'un coup. ~0,17s @ 60/s — même
## ordre de grandeur que les fenêtres d'input-buffer usuelles en jeu
## d'action (100-200ms).
##
## Ne s'applique volontairement PAS à `_attack_queued` (embryon existant,
## laissé TEL QUEL, non borné dans le temps) : c'est un mécanisme déjà
## validé/expédié, le retoucher pour lui ajouter une expiration serait un
## changement de comportement non demandé par le mandat et risquerait une
## régression sur le combo — "étends l'embryon", pas "réécris-le".
const INPUT_BUFFER_TICKS := 10

## Phase R4 (retour croisé Gemini/ChatGPT, MANDAT SUITE v2 : "poids du
## combo... coup 3 (finisher) : anticipation plus longue... ajouter une
## frame de stabilisation en fin de combo au lieu du retour instantané à
## idle/course"). Surcharge PAR TIER des constantes ci-dessus — tier1/2
## gardent EXACTEMENT ANTICIPATION_TICKS/RECOVERY_TICKS (aucune
## régression sur les 2 premiers coups), seul tier3 (le finisher, jamais
## chaînable plus loin — `_combo_step < AttackAnimName.size()` exclut
## déjà tier3 de la fenêtre de chaînage, donc allonger sa recovery ne
## grignote sur AUCUN chaînage réel) s'allonge : +4 ticks d'anticipation
## (silhouette qui se charge plus longtemps avant le coup) et +6 ticks
## de recovery (le temps de stabilisation demandé avant idle/course,
## RELEASE_TICKS/le tick de contact restent inchangés — seul l'AUTOUR du
## coup s'étire). Valeurs de départ TUNABLE, comme le reste des tiers.
const COMBO_TIER_ANTICIPATION_TICKS := [ANTICIPATION_TICKS, ANTICIPATION_TICKS, ANTICIPATION_TICKS + 4]
const COMBO_TIER_RECOVERY_TICKS := [RECOVERY_TICKS, RECOVERY_TICKS, RECOVERY_TICKS + 6]

const ATTACK_RANGE_PX := 48.0  # ~1.5m, GameConstants.PX_PER_METER
const ATTACK_DAMAGE := 10.0

## Feedback par tier de combo (mandat combat, escalade des 3 coups de
## base — délibérément adoucie sous le "heavy sur coup 3" du diagnostic
## externe : "ce sont des attaques de BASE, si elles tapent déjà en
## heavy il ne reste rien pour les tiers 5-6, contraire au principe
## d'escalade du doc").
##
## Décision de gabarit (à documenter dans docs/worklog.md) : le mandat
## demande "light-medium" pour le hit-stop du coup 2 et le shake du
## coup 3, mais CombatFeedback n'expose que les 5/3 profils discrets du
## doc (§9.1/§9.2) — pas de palier intermédiaire. À 60 ticks/s
## (CombatFeedback.TICK_MS ≈ 16,667 ms), "light" arrondit déjà à 1 tick
## et "medium" à 2 ticks : il n'existe aucune valeur entière DISTINCTE
## entre les deux pour matérialiser un "light-medium" de hit-stop. Choix
## retenu, dans l'esprit même de l'escalade demandée : arrondir vers le
## BAS (jamais vers le haut) sur toute ambiguïté de palier — un tier
## en-dessous de la couverture pleine reste un tier de base, jamais un
## plafond consommé par avance sur les tiers 5-6 futurs.
## Couleur VFX par tier — bible d'animation §3bis (MANDAT PERMANENT,
## 2026-08-27, "contraste façon Yomi Hustle"), exécuté ici sur le pilote
## (combo de base) uniquement, pas sur le reste du jeu. Axe 1 du mandat :
## pousser saturation/value des primitives déjà posées sur le coup
## au-delà de la précédente passe de lisibilité (Gueule Vide/Poing
## Tellurique, `data/palettes/invocateur_vide.json`/`terre.json` —
## saturation max observée là-bas 55%/65%). Ici : 88-100%, nettement
## au-dessus, `value_percent` proche du plafond dur `MAX_VALUE_HSV=0.92`
## partagé par arcSlash/impactStar/ribbonTrail (jamais dépassé — le
## clamp des primitives le ferait de toute façon, mais choisi
## intentionnellement, pas laissé au hasard du clamp).
## 3 teintes distinctes, une escalade chaude cohérente avec l'identité
## "Cendre/braise" du personnage plutôt qu'une couleur arbitraire par
## coup : ambre (jab) -> orange-rouge (knee-uppercut) -> rouge
## incandescent (overhead smash, le coup le plus lourd du combo de
## base). Escalade de teinte ET d'intensité, pas seulement d'intensité —
## lisible même sans comparer les 3 coups côte à côte.
const COMBO_TIER_FEEDBACK := [
	{"hitstop": "light", "recoil_px": 4.0, "shake": "", "arc_slash": false, "hue_deg": 30.0, "saturation_percent": 88.0, "value_percent": 90.0},
	{"hitstop": "light", "recoil_px": 8.0, "shake": "", "arc_slash": true, "hue_deg": 15.0, "saturation_percent": 94.0, "value_percent": 91.0},
	{"hitstop": "medium", "recoil_px": 14.0, "shake": "light", "arc_slash": false, "hue_deg": 5.0, "saturation_percent": 100.0, "value_percent": 92.0},
]

## Timeline du dash, en ticks (60/s) — mandat combat (B4) : "se lit
## actuellement comme une téléportation : pas de compression avant
## départ, pas de traînée, arrêt trop net." Découpage repris du
## diagnostic externe (2 anticipation / 5 déplacement / 4 recovery,
## 11 ticks ≈ 0,18s) — EXCEPTION EXPLICITE au §6.2 du doc VFX
## (bande "release" attendue 5-12%) : ici le déplacement EST le
## release (5/11 ≈ 45%), pas un simple appui visuel bref pendant qu'une
## autre couche porte le mouvement. Documentée dans docs/worklog.md
## plutôt que passée sous silence, comme demandé.
const DASH_ANTICIPATION_TICKS := 2
const DASH_MOVE_TICKS := 5
const DASH_RECOVERY_TICKS := 4

## Distance totale parcourue pendant DASH_MOVE_TICKS — point de départ à
## ressentir, pas un dogme (même réserve que les autres valeurs de
## tuning de cette session). ~2,5m, un peu court du 3m de portée
## d'invocation (POWER1_SPAWN_DISTANCE_PX) pour rester un déplacement
## d'esquive, pas un remplacement du mouvement normal.
const DASH_DISTANCE_PX := 80.0
## Vitesse de glissade au sol en tout début de RECOVERY, décroît vers 0
## de façon linéaire sur DASH_RECOVERY_TICKS (même schéma que le recul
## d'Enemy._physics_process, réutilisé ici côté joueur).
const DASH_RECOVERY_INITIAL_SPEED_PX_S := 220.0

## Esquive (mandat production v1 §1.3, décision Milan : "Dash ET esquive —
## deux actions séparées") — roulade/pas d'évitement avec i-frames, DISTINCTE
## du dash (pas un renommage). Même construction en 3 phases que le dash
## ci-dessus (anticipation -> déplacement ease-out -> recovery qui glisse),
## mais des proportions différentes : anticipation minimale (l'esquive doit
## répondre vite, c'est une réaction au danger), fenêtre active plus longue
## que le MOVE du dash (le joueur "paie" pour l'invincibilité par une
## recovery un peu plus engagée qu'un simple déplacement), distance plus
## courte que le dash (un "pas d'évitement", pas un sprint). Valeurs de
## départ TUNABLE (mandat §1.3 : "cooldown éventuel TUNABLE"), à ajuster
## une fois testées en jeu réel, jamais un dogme.
const DODGE_ANTICIPATION_TICKS := 2
const DODGE_ACTIVE_TICKS := 8
const DODGE_RECOVERY_TICKS := 6
const DODGE_DISTANCE_PX := 56.0
## Même schéma que DASH_RECOVERY_INITIAL_SPEED_PX_S, à l'échelle de la
## distance plus courte de l'esquive.
const DODGE_RECOVERY_INITIAL_SPEED_PX_S := 150.0
## Cooldown avant de pouvoir ré-esquiver — évite un spam d'i-frames en
## boucle (aucun combat réel n'exerce encore ce garde-fou, mais mieux vaut
## le poser maintenant que devoir le retrofitter une fois que G y branche
## de vraies attaques ennemies).
const DODGE_COOLDOWN_TICKS := 30

## Traînée (mandat B4/J2 : "opacité ~50% puis ~20%") — ce n'est PAS une
## primitive VfxDirector (contrat seed/configure générique, §7.1) : une
## after-image lit la texture/frame COURANTE du sprite du joueur, une
## donnée que seul Player possède, pas quelque chose qu'une recette JSON
## peut décrire (voir _spawn_afterimage() plus bas ; QUAND spawner, en
## revanche, est bien data-driven — _apply_afterimages() ci-dessus).
## Durée de fondu d'une after-image (Tween, temps réel — cohérent avec
## _spawn_afterimage() ci-dessous, un effet purement cosmétique, pas un
## système de combat qui doit rester en ticks purs). Le TIMING de
## déclenchement (quels ticks, combien, avec quelle opacité de départ)
## est lui data-driven depuis data/animation_composer/cendre.json (J2,
## mandat production v1 §4) — migré depuis les anciennes constantes
## DASH_AFTERIMAGE_TICKS/OPACITIES codées en dur, source unique désormais,
## et réutilisé par le combo (coup3) en plus du dash.
const AFTERIMAGE_FADE_SEC := 0.15

const GueuleVideScene := preload("res://scenes/gameplay/powers/gueule_vide.tscn")
const CorbeauPaleScene := preload("res://scenes/gameplay/powers/corbeau_pale.tscn")
const PoingDuColosseScene := preload("res://scenes/gameplay/powers/poing_du_colosse.tscn")
const OeilSansRegardScene := preload("res://scenes/gameplay/powers/oeil_sans_regard.tscn")
const SerpentCreuxScene := preload("res://scenes/gameplay/powers/serpent_creux.tscn")

## Invocation "Gueule Vide" (INVOCATEUR, data/recipes/power.gueule_vide.cast.json) :
## "Portée d'invocation : 4m". La créature apparaît à une distance fixe
## (3m) dans l'axe du regard (facing), laissant sa propre zone d'attaque
## (~1,5m) porter le reste de la portée totale sans la dépasser.
## "Cooldown suggéré : 6s" -> 360 ticks @ 60/s.
const POWER1_SPAWN_DISTANCE_PX := 96.0  # GameConstants.meters_to_px(3.0)
const POWER1_COOLDOWN_TICKS := 360  # 6s @ 60/s

## AUDIT "polish complet" (2026-08-23, agent dédié Gueule Vide) : Milan
## demandait de vérifier point par point si la planche de référence
## (docs/references/invocateur/gueule_vide.png, temps 2 "Émergence") se
## retrouve VRAIMENT en jeu — capture tick-par-tick (captures/verification/
## 2026-08-23-gueule-vide-4temps/) : confirmé, Cendre restait bloqué sur
## sa pose idle/déplacement générique du tick 0 au tick 42, AUCUN geste
## d'invocation, alors que _cast_gueule_vide() n'appelait ni _sprite.play()
## ni _action_lock (cf. commentaire ci-dessous sur _power1_cooldown_remaining,
## déjà documenté comme un choix délibéré). Corrigé SANS remettre en cause
## ce choix ("l'invocation n'immobilise pas le joueur") : au lieu de
## _action_lock (qui bloquerait aussi le déplacement/attaque, jamais
## demandé par le mandat ni par le GDD), une fenêtre séparée et courte
## protège uniquement le CHOIX D'ANIMATION du sprite (pas la vélocité) le
## temps que le geste "invocation_gueule_vide" (6 frames pose-à-pose,
## PixelLab, character_id Cendre_v3c 8596a4ad EN JEU — vérifié via
## get_character avant l'appel, même discipline que Bras-Faux/Poing
## Belluaire) se lise clairement, cf. _handle_movement(). Durée calée sur
## la même vitesse d'animation que bras_faux/poing_belluaire (12fps, 6
## frames = 30 ticks, cendre_frames.tres) : le joueur reste libre de
## bouger/attaquer pendant cette fenêtre (aucun _action_lock), seul le
## RENDU du sprite est protégé — s'il bouge avant la fin, _handle_movement()
## bascule immédiatement sur idle/déplacement au tick suivant (comportement
## voulu, pas un bug : rien n'oblige le joueur à rester immobile).
const GUEULE_VIDE_GESTURE_TICKS := 30  # 0,5s @ 60/s, 6 frames @ 12fps (même cadence que bras_faux/poing_belluaire).
var _gueule_vide_gesture_ticks_remaining: int = 0

## Bras-Faux (GDD §7.1, Parasite) — archétype de cast "frappe de zone"
## (mandat production v1 §5) : EXÉCUTÉ PAR LE JOUEUR (contrairement à
## Gueule Vide, une entité invoquée séparée), un seul balayage qui touche
## potentiellement plusieurs ennemis dans un cône, jamais une entité qui
## vit sa propre vie après le cast. "Portée ~1,5m, arc ~90°, durée
## ~0,5-0,7s, une frappe, aucun déplacement automatique" — 40 ticks
## (0,667s) : 14 anticipation (le membre se transforme) / 4 release
## (le balayage, contact au 1er tick comme le combo) / 22 recovery (le
## parasite se rétracte). Dégâts non chiffrés par la fiche (même statut
## que Gueule Vide, ATTACK_DAMAGE ci-dessus) : alignés sur le combo par
## défaut, à faire trancher par Milan. Cooldown NON chiffré par le GDD
## (contrairement à Gueule Vide, "cooldown suggéré 6s") — valeur de
## départ TUNABLE, plus courte que Gueule Vide (compétence de mêlée plus
## légère qu'une invocation), à ajuster une fois testée en jeu réel.
const BRAS_FAUX_ANTICIPATION_TICKS := 14
const BRAS_FAUX_RELEASE_TICKS := 4
const BRAS_FAUX_RECOVERY_TICKS := 22
const BRAS_FAUX_RANGE_PX := 48.0  # ~1.5m, GameConstants.PX_PER_METER
const BRAS_FAUX_HALF_ANGLE_DEG := 45.0  # arc total ~90°
const BRAS_FAUX_DAMAGE := 10.0
const BRAS_FAUX_COOLDOWN_TICKS := 180  # 3s @ 60/s, TUNABLE (non chiffré par le GDD)
const BrasFauxRecipeId := "power.bras_faux.cast"
const BRAS_FAUX_CAST_SEED := 51001  # Addendum A §A.5 : jamais l'horloge murale, même discipline que GueuleVide.CAST_SEED.

## 6 frames pose-à-pose (bras_faux/0..5.png) pilotées tick-exact — même
## discipline que GueuleVide.FRAME_TICK_BOUNDS /
## POING_BELLUAIRE_FRAME_TICK_BOUNDS ci-dessous, jamais la fps autonome
## d'AnimatedSprite2D. Lecture des frames (contact sheet vérifié
## visuellement, mandat "polish complet") : 0-2 = le bras se déploie
## progressivement en crochet (planche bras_faux.png, temps 2
## "Transformation"), quasi-identiques entre elles à l'œil (variations
## fines de posture du bras gauche/tête, pas un vrai déplacement) ; 3-5 =
## corps pivoté, bras balayé au-dessus de l'épaule (silhouette nettement
## DISTINCTE du cluster 0-2, la meilleure lecture disponible de "temps 3
## Balayage" dans les assets actuels), also quasi-identiques entre elles.
##
## AUDIT (2026-08-23, agent dédié Bras-Faux, mandat "polish complet") :
## avant cette table, `_sprite.play("bras_faux")` tournait en fps
## autonome (12fps, cf. cendre_frames.tres, speed=12.0 -> 5 ticks/frame).
## Capture tick-par-tick (scripts/capture_headless.sh --mode=
## player_action, ticks 3/8/13/15/16/17/18/20/25) : la pose affichée à
## RELEASE tick1 (contact, tick global 15, frame index floor(15/5)=3)
## restait ensuite STRICTEMENT IDENTIQUE jusqu'au tick global 25 inclus
## (10 ticks capturés, aucune différence visible) — parce que l'animation
## à 5 ticks/frame se termine à 30 ticks (6 frames) alors que le cast
## complet dure 40 ticks (14+4+22) : les 10 derniers ticks de RECOVERY
## tenaient déjà la dernière frame par simple fin de lecture, ET le
## cluster de frames 3-5 (déjà quasi-identiques en contenu, voir
## ci-dessus) s'étalait sans aucun repère avec les bornes de phase — rien
## ne garantissait que le "snap" vers la pose de balayage tombe pile au
## tick de contact plutôt qu'avant ou après. Constat identique à celui de
## POING_BELLUAIRE_FRAME_TICK_BOUNDS (même bug de architecture, trouvé
## indépendamment par l'agent Poing Belluaire sur son propre pouvoir).
## Bornes ci-dessous calées pour que la frame 3 (première pose du cluster
## "balayage") bascule PILE au tick global 15 (ANTICIPATION 14 + RELEASE
## tick1 = contact) au lieu d'un tick arbitraire dérivé du fps, et que les
## frames 4/5 (même cluster visuel, mais on garde la table à 6 entrées
## comme GueuleVide/PoingBelluaire) se répartissent sur le reste de
## RELEASE+RECOVERY plutôt que de figer instantanément sur la frame 5 dès
## la fin de la lecture fps native.
const BRAS_FAUX_FRAME_TICK_BOUNDS: Array[int] = [5, 10, 14, 18, 29, 40]

## Fenêtre d'annulation (mandat "fluidité", Partie 2) — PROPRIÉTÉ PROPRE à
## Bras-Faux (pas une réutilisation de CHAIN_WINDOW_TICKS, le mandat exige
## explicitement un point par animation) : dernier tiers de RECOVERY où le
## joueur peut déjà enchaîner l'action suivante — voir
## `_try_consume_queued_input()`/`_advance_bras_faux()`. Calée sur
## BRAS_FAUX_FRAME_TICK_BOUNDS ci-dessus : la frame 4 (cluster "balayage",
## dernière pose du cast) tient déjà, immobile, de RECOVERY tick 11
## (18+29-... voir bornes) jusqu'à la fin — s'annuler dès que la pose a
## fini de bouger ne coupe donc RIEN de visuellement nouveau, seulement la
## tenue statique en fin de geste. Généreuse par défaut (12 des 22 ticks de
## RECOVERY, ~55%) comme demandé, resserrable si jugé trop permissif en jeu
## réel.
const BRAS_FAUX_CANCEL_WINDOW_TICKS := 12

## Poing Belluaire (RANK_ZERO_POWER_SKILL_BIBLE v0.4, "Monstrification" §2)
## — même archétype "frappe de zone" que Bras-Faux (EXÉCUTÉ PAR LE JOUEUR,
## pas une entité invoquée), mais "Impact lourd" plutôt qu'un balayage :
## "L'avant-bras et le poing grossissent... un seul coup frontal très
## lourd... portée courte... forte valeur de recul... peut interrompre
## les attaques faibles." Timeline volontairement plus lente que
## Bras-Faux (50 ticks / 0,83s vs 40) pour vendre le poids : 20
## anticipation (compression -> grossissement -> pose d'impact, 3 beats
## narratifs du GDD dans UNE seule phase code, même discipline que
## Bras-Faux), 4 release (contact au 1er tick, comme le combo), 26
## recovery (retour anatomique, plus long qu'un simple retrait de
## membrane). Portée/angle plus courts et plus étroits (coup frontal,
## pas un balayage à 90°). Dégâts/cooldown NON chiffrés par la fiche
## (même statut que Bras-Faux) : damage relevé au-dessus du combo/
## Bras-Faux (16 vs 10) pour "peut interrompre les attaques faibles",
## recoil_strength_px monté à 40 (vs 24 par défaut) pour "forte valeur
## de recul", hitstop "heavy" (vs "medium" pour Bras-Faux) pour "gros
## recul/hit-stop" — toutes des valeurs de départ TUNABLE, à ajuster par
## Milan. Monstrification = même famille que Bras-Faux (la Bible v0.4
## classe explicitement Bras-Faux SOUS "Monstrification", pas "Parasite"
## séparément) : palette_id "parasite" RÉUTILISÉE, pas une nouvelle
## signature — §3 de la matrice de décision n'exige de valider QUE les
## pouvoirs "sans signature définie", ce qui n'est plus le cas ici.
const POING_BELLUAIRE_ANTICIPATION_TICKS := 20
const POING_BELLUAIRE_RELEASE_TICKS := 4
const POING_BELLUAIRE_RECOVERY_TICKS := 26
const POING_BELLUAIRE_RANGE_PX := 40.0  # ~1.25m, "portée courte"
const POING_BELLUAIRE_HALF_ANGLE_DEG := 30.0  # arc total ~60°, "coup frontal" pas un balayage
const POING_BELLUAIRE_DAMAGE := 16.0  # TUNABLE, > combo/Bras-Faux ("peut interrompre les attaques faibles")
const POING_BELLUAIRE_RECOIL_PX := 40.0  # TUNABLE, > défaut 24.0 ("forte valeur de recul")
const POING_BELLUAIRE_RECOIL_TICKS := 8
const POING_BELLUAIRE_COOLDOWN_TICKS := 240  # 4s @ 60/s, TUNABLE (non chiffré par le GDD), > Bras-Faux (coup plus lourd)
const PoingBelluaireRecipeId := "power.poing_belluaire.cast"
const POING_BELLUAIRE_CAST_SEED := 51002  # Addendum A §A.5, jamais l'horloge murale.

## 6 frames pose-à-pose (poing_belluaire/0..5.png) pilotées tick-exact —
## même discipline que GueuleVide.FRAME_TICK_BOUNDS, jamais la fps
## autonome d'AnimatedSprite2D. Lecture des frames : 0-4 = la masse
## poing/bras enfle progressivement (planche docs/references/
## monstrification/coup_de_poing_monstrifie.png, temps 1 "Préparation" +
## 2 "Transformation") ; 5 = poing en extension complète, pose "Impact"
## (temps 3) nettement distincte des 5 précédentes — pas de frame de
## retrait dédiée dans la séquence, tenue jusqu'à la fin du cast.
##
## AUDIT (2026-08-23, agent dédié, mandat "polish complet") : avant cette
## table, `_sprite.play("poing_belluaire")` tournait en fps autonome
## (12fps, cf. cendre_frames.tres). Sur une capture tick-par-tick
## (scripts/capture_headless.sh --mode=player_action), la pose affichée
## était identique entre l'ANTICIPATION tardive (tick 19-20) et TOUT le
## RELEASE (tick 21-24, contact inclus à RELEASE tick1) : frame index
## floor(tick_global/5) valait 4 (windup) sur toute cette fenêtre, et la
## frame 5 (Impact) ne s'affichait qu'au tick global 25 — 1 tick dans
## RECOVERY, APRÈS que les dégâts/hit-stop/recul aient déjà été
## appliqués. Le "coup" visuel arrivait donc systématiquement un temps
## entier trop tard par rapport au contact mécanique, alors même que le
## hit-stop "heavy" (CombatFeedback.register_hit, déjà câblé) gelait la
## logique du joueur (_physics_process retourne tôt sous is_player_
## frozen()) SANS geler le sprite (AnimatedSprite2D avance sur son
## `_process` propre, jamais gated par ce freeze) — la pose de contact
## réelle continuait donc de dériver pendant le gel plutôt que d'être
## tenue.
## DENSIFIÉ (campagne "densité d'animation", agent Monstrification) : 6 ->
## 14 frames (dans la fourchette 12-18 du mandat ; la génération v3 ne
## convergeait plus proprement vers la pose de fin au-delà de l'index 13
## sur 16 demandées — 2 frames de fin rejetées après contrôle visuel
## réel plutôt que gardées par défaut, voir docs/worklog.md). Silhouette
## de départ/fin INCHANGÉE (mêmes deux ancres `custom_start_frame_url`/
## `end_frame_url` que l'animation déjà validée). Répartition non
## uniforme : 7 frames sur l'anticipation (3-20), 4 sur le contact/pic
## (21-24, encadrant le tick de contact réel 21 = ANTICIPATION 20 +
## RELEASE tick1, cf. audit ci-dessus), 3 sur la recovery (32-50).
const POING_BELLUAIRE_FRAME_TICK_BOUNDS: Array[int] = [3, 6, 9, 12, 15, 18, 20, 21, 22, 23, 24, 32, 41, 50]

## Fenêtre d'annulation (mandat "fluidité", Partie 2) — PROPRIÉTÉ PROPRE à
## Poing Belluaire, DÉLIBÉRÉMENT plus courte en proportion que Bras-Faux
## (10 des 26 ticks de RECOVERY, ~38%, contre ~55% pour Bras-Faux) : "le
## bon point diffère entre un coup léger et un coup lourd" (mandat) — ce
## coup EST le plus lourd des 5 compétences (hitstop "heavy", recoil_px le
## plus élevé, cf. commentaire au-dessus de POING_BELLUAIRE_DAMAGE), il
## doit rester le plus long à annuler pour VENDRE son poids, pas juste
## copier le même ratio que les autres. Reste généreuse (pas un verrou
## total), juste proportionnellement plus engagée.
const POING_BELLUAIRE_CANCEL_WINDOW_TICKS := 10

## Poing Tellurique (RANK_ZERO_POWER_SKILL_BIBLE v0.4, "Terre" §1) —
## premier pouvoir de la Classe Terre implémenté : AUCUNE palette
## signature existante (contrairement à Monstrification ci-dessus), donc
## data/palettes/terre.json est une PROPOSITION de première passe dérivée
## directement du principe donné par la fiche ("le monde devient l'arme :
## sable, terre, roche, poussière et gravats") — tons terreux/minéraux,
## rien d'inventé au-delà de cette liste de matières. Même archétype
## "frappe de zone" que Bras-Faux/Poing Belluaire : "Rank Zero concentre
## terre et roche autour de son poing puis frappe... attaque frontale
## courte... peut toucher plusieurs ennemis proches." Timeline 42 ticks :
## 18 anticipation (appui -> matière qui remonte), 4 release (coup/
## impact, contact au 1er tick), 20 recovery (éclats/poussière qui
## retombent -> retour à la normale). Pas de qualificatif "très lourd"/
## "forte" dans la fiche (contrairement à Poing Belluaire) : damage/
## recoil/hitstop restent au niveau Bras-Faux (medium), légèrement en
## dessous de Poing Belluaire. Dégâts/cooldown NON chiffrés (même statut
## que les 2 autres) : valeurs de départ TUNABLE, à ajuster par Milan.
const POING_TELLURIQUE_ANTICIPATION_TICKS := 18
const POING_TELLURIQUE_RELEASE_TICKS := 4
const POING_TELLURIQUE_RECOVERY_TICKS := 20
const POING_TELLURIQUE_RANGE_PX := 44.0  # ~1.4m, "attaque frontale courte"
const POING_TELLURIQUE_HALF_ANGLE_DEG := 40.0  # arc total ~80°, "plusieurs ennemis proches"
const POING_TELLURIQUE_DAMAGE := 14.0  # TUNABLE, entre Bras-Faux (10) et Poing Belluaire (16)
const POING_TELLURIQUE_COOLDOWN_TICKS := 200  # ~3,3s @ 60/s, TUNABLE (non chiffré par le GDD)
const PoingTelluriqueRecipeId := "power.poing_tellurique.cast"
const POING_TELLURIQUE_CAST_SEED := 51003  # Addendum A §A.5, jamais l'horloge murale.

## Art dédié (agent Poing Tellurique, mandat "polish complet", 2026-08-23 ;
## PASSE DENSITÉ DE FRAMES, agent dédié Terre, 2026-08-28) : anim
## "poing_tellurique" propre, PAS un réemploi de "coup1". 16 frames
## pose-to-pose (mandat densité "12-18 frames premium", remplace les 6
## frames d'origine — RÉGÉNÉRATION COMPLÈTE via animate_character v3,
## même character_id Cendre_v3c 8596a4ad, même prompt "purely physical,
## no glow/no light effects" ; le contraste VFX déjà posé — data/palettes/
## terre.json, primitives groundRing/impactStar — n'est PAS touché par
## cette passe, seul le sprite du personnage change) : 0-10 anticipation
## (montée en garde -> bras levés haut, répartition FINE et volontairement
## NON UNIFORME — la plupart des frames sur l'anticipation, jamais un
## découpage régulier), 11-12 contact/pic (SEULEMENT 2 frames, la plus
## courte tenue possible : frame 11 = accroupissement le plus profond,
## poings au plus bas), 13-15 dissipation en se relevant. Frame de contact
## choisie par MESURE réelle (bounding-box alpha), pas par supposition :
## bbox_top de chaque frame cuite mesuré après cuisson (top=9 debout ->
## 33 accroupissement max, atteint aux frames 11 ET 12, jamais avant) —
## la frame 11 est la PREMIÈRE à atteindre ce minimum, donc la frappe
## commence pile là. Bornes calées pour que la frame 11 bascule PILE au
## tick global 19 (ANTICIPATION 18 + RELEASE tick1 = contact) — toujours
## aligné avec la fenêtre "contact" 18-22 d'impactFlashFrame et le
## start_tick=18/19 de dustKick/impactStar (data/recipes/
## power.poing_tellurique.cast.json), revérifié après régénération (capture
## en jeu, pas supposé).
const POING_TELLURIQUE_FRAME_TICK_BOUNDS: Array[int] = [2, 4, 6, 8, 10, 12, 13, 14, 15, 16, 18, 19, 22, 28, 34, 42]

## Fenêtre d'annulation (mandat "fluidité", Partie 2) — PROPRIÉTÉ PROPRE à
## Poing Tellurique : coup au sol "medium" (ni le plus léger ni le plus
## lourd des 5), fenêtre généreuse à mi-chemin entre Bras-Faux et Poing
## Belluaire (12 des 20 ticks de RECOVERY, 60%) — tombe dans les frames
## 13-15 ("dissipation en se relevant", POING_TELLURIQUE_FRAME_TICK_BOUNDS,
## PASSE DENSITÉ 2026-08-28) : la dissipation est déjà bien engagée à ce
## stade, aucune pose de contact n'est coupée par une annulation dans
## cette fenêtre.
const POING_TELLURIQUE_CANCEL_WINDOW_TICKS := 12

## Marée de Sable (Terre, Tier 2) — MANDAT AUTONOME v3 Phase 3. GDD :
## "Une vague de sable déferle sur une ligne devant Rank Zero, ralentissant
## et entravant les ennemis touchés." Portée/largeur NON chiffrées par le
## GDD : valeurs TUNABLE, plus longue mais plus étroite qu'un arc de mêlée
## (une "vague en ligne" voyage, un poing/balayage ne voyage pas).
const MAREE_DE_SABLE_ANTICIPATION_TICKS := 14
const MAREE_DE_SABLE_RELEASE_TICKS := 10
const MAREE_DE_SABLE_RECOVERY_TICKS := 18
const MAREE_DE_SABLE_RANGE_PX := 90.0  # ~2,9m, plus long que Poing Tellurique (44px) — une vague voyage.
const MAREE_DE_SABLE_HALF_WIDTH_PX := 15.0
const MAREE_DE_SABLE_DAMAGE := 8.0  # TUNABLE, la plus faible des 4 mêlée/ligne — Tier CONTRÔLE, pas dégâts.
const MAREE_DE_SABLE_SLOW_MULTIPLIER := 0.5  # vitesse divisée par 2, TUNABLE.
const MAREE_DE_SABLE_SLOW_DURATION_TICKS := 90  # 1,5s @ 60/s, TUNABLE.
const MAREE_DE_SABLE_COOLDOWN_TICKS := 220  # légèrement au-dessus de Poing Tellurique (contrôle > dégâts).
const MareeDeSableRecipeId := "power.maree_de_sable.cast"
const MAREE_DE_SABLE_CAST_SEED := 51004  # Addendum A §A.5, jamais l'horloge murale.

## Art dédié (agent Marée de Sable, mandat "polish complet", 2026-08-23) :
## anim "maree_de_sable" propre, PAS un réemploi de "coup1" (jab horizontal
## générique — écart confirmé par capture avant correctif sur plusieurs
## ticks et par comparaison directe avec le temps 2 "Lancement" de
## docs/references/terre/maree_de_sable.png, qui montre un bras unique
## projeté droit devant en position basse/écartée, aucun rapport avec un
## jab). Pipeline : character_id Cendre_v3c EN JEU (8596a4ad, vérifié via
## get_character AVANT l'appel), animate_character mode v3 DIRECTEMENT sur
## l'état de base (pas de create_character_state : Marée de Sable ne
## transforme aucun membre, contrairement à Bras-Faux/Poing Belluaire —
## même construction que coup1/coup2/coup3/Poing Tellurique). 6 frames sud,
## acceptées dès le 1er essai (aucune arme/lueur saturée hallucinée ; un
## voile pâle poussiéreux apparaît à la main sur les 2 dernières frames,
## lu comme le début du jet de sable annoncé par le prompt — cohérent avec
## la planche, pas un artefact à corriger). Facteur d'échelle LANCZOS
## 53/79 ≈ 0.671 mesuré sur la frame la plus haute (frame0, bras au repos)
## vs le gabarit déjà établi (bras_faux 53px/poing_belluaire 51px) — même
## classe de correctif que ces deux pouvoirs, appliqué uniformément aux 6
## frames avant ancrage pied (sans quoi la tête sortait du canvas partagé
## 64×64, vérifié et corrigé avant tout commit). Bande de recherche du pied
## élargie à 100% (foot_band_frac) pour les 6 frames : jambes écartées dès
## la 1ère frame, la bande centrale étroite par défaut tombait dans l'écart
## entre les deux bottes (vérifié pixel par pixel, aucune cape/tissu ne
## traîne sous les bottes sur ce personnage R3 sans cape, donc aucun risque
## de retomber sur le bug cape que cette bande visait à l'origine).
##
## PASSE DENSITÉ DE FRAMES (agent dédié Terre, 2026-08-28) : 16 frames
## pose-to-pose (mandat "12-18 frames premium", remplace les 6 frames
## d'origine — RÉGÉNÉRATION COMPLÈTE via animate_character v3, même
## character_id Cendre_v3c, prompt "purely physical, no glow/no light
## trail" ; le contraste VFX déjà posé — data/palettes/terre.json,
## sandCrest — n'est PAS touché, seul le sprite du personnage change).
## Frame de contact choisie par MESURE réelle (bord droit du bbox alpha
## après cuisson, pas par supposition) : l'extension du bras grandit
## progressivement (43->53px) et atteint son maximum pour la PREMIÈRE fois
## à la frame 11 (53px, plateau jusqu'à la frame 13) — c'est donc la
## frame 11 qui porte le contact, pas une frame médiane devinée. 0-10
## anticipation (stance qui s'élargit, bras qui se replie puis commence
## l'extension — répartition fine et volontairement NON UNIFORME, la
## plupart des frames ici), 11-12 contact/pic (SEULEMENT 2 frames : bras
## en extension complète, la plus courte tenue possible), 13-15
## dissipation (bras qui se relâche vers une position neutre). Bornes
## calées pour que la frame 11 bascule PILE au tick global 15
## (ANTICIPATION 14 + RELEASE tick1 = contact), revérifié après
## régénération (capture en jeu, pas supposé).
const MAREE_DE_SABLE_FRAME_TICK_BOUNDS: Array[int] = [2, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 24, 30, 36, 42]

## Fenêtre d'annulation (mandat "fluidité", Partie 2) — PROPRIÉTÉ PROPRE à
## Marée de Sable : Tier CONTRÔLE (dégâts les plus faibles des 4, voir
## MAREE_DE_SABLE_DAMAGE), pas d'impact "lourd" à vendre — fenêtre généreuse
## proche de Bras-Faux (10 des 18 ticks de RECOVERY, ~55%) — tombe dans les
## frames 14-15 (bras qui se relâche vers une position neutre,
## MAREE_DE_SABLE_FRAME_TICK_BOUNDS, PASSE DENSITÉ 2026-08-28), la
## dissipation est déjà bien engagée à ce stade.
const MAREE_DE_SABLE_CANCEL_WINDOW_TICKS := 10

## Carapace (Terre, Tier 3, DÉFENSIF) — CHANTIER A (2026-08-24, agent dédié
## Terre, plan de production v1). GDD/planche (docs/references/terre/
## carapace.png) : "La peau et le torse se couvrent de plaques rocheuses,
## augmentant la résistance aux dégâts" — un ÉTAT SOUTENU (buff actif sur
## une durée), pas un impact ponctuel. Traité STRUCTURELLEMENT différemment
## des 4 autres compétences Terre (mandat l'exige explicitement, même
## distinction déjà notée pour Poing Tellurique) : 3 phases ACTIVATION/
## ACTIVE/RECOVERY (pas ANTICIPATION/RELEASE/RECOVERY — il n'y a pas de
## "contact", Carapace ne touche jamais un ennemi). Voir
## power.carapace.cast.json pour le détail complet du raisonnement recette
## + la raison (architecturale, pas paresseuse) pour laquelle `_action_lock`
## reste vrai sur toute la durée (orbital, la couche VFX signature de
## l'état actif, est ancrée à une origine FIXE capturée au cast — aucune
## primitive de VfxDirector ne suit une entité qui se déplace ; laisser le
## joueur bouger ferait dériver les fragments de roche loin de lui,
## contrairement à la planche qui montre "3. CARAPACE ACTIVE" en posture
## statique).
const CARAPACE_ACTIVATION_TICKS := 24
const CARAPACE_ACTIVE_TICKS := 180  # ~3s @ 60/s, TUNABLE — pas chiffré par le GDD.
const CARAPACE_RECOVERY_TICKS := 24  # miroir de l'activation (carapace_fin = carapace_activation rejouée à l'envers).
const CARAPACE_DAMAGE_MULTIPLIER := 0.65  # 35% de dégâts en moins pendant tout le buff, TUNABLE.
const CARAPACE_COOLDOWN_TICKS := 360  # généreux, cohérent avec un buff long plutôt qu'un impact ponctuel, TUNABLE.
const CarapaceRecipeId := "power.carapace.cast"
const CARAPACE_CAST_SEED := 51006  # Addendum A §A.5, jamais l'horloge murale.

## Art dédié (agent Terre, CHANTIER A 2026-08-24) : Carapace TRANSFORME la
## peau/le torse (plaques rocheuses) — une MUTATION comme Bras-Faux/Poing
## Belluaire (create_character_state), PAS une simple pose comme Poing
## Tellurique/Marée de Sable. Pipeline : create_character_state sur
## Cendre_v3c (8596a4ad, vérifié via get_character) -> nouvel état "Carapace"
## (b51c67c6, plaques brun-gris anguleuses sur torse/épaules/avant-bras,
## fragments flottants) accepté au 1er essai. "carapace_activation" (6
## frames + référence) = interpolation v3 DIRECTE entre la rotation sud de
## l'état Idle (frame de départ) et la rotation sud du nouvel état Carapace
## (frame d'arrivée) — garantit que la dernière frame colle exactement à
## l'état déjà validé, pas une régénération indépendante qui pourrait
## diverger. "carapace_active" (4 frames + référence) = respiration/dérive
## d'un fragment généré DIRECTEMENT sur le character_id Carapace (état
## stable, pas une transition). "carapace_fin" : AUCUNE génération
## supplémentaire — réutilise les 7 mêmes PNG que carapace_activation, dans
## l'ordre INVERSE (armure qui se détache = l'activation rejouée à
## l'envers, cf. assets/manifests/cendre_frames_cooked.json).
##
## Pilotage tick-exact ACTIVATION (même discipline que MAREE_DE_SABLE_
## FRAME_TICK_BOUNDS ci-dessus) : bornes calées sur le contenu réel des 7
## frames (0-2 quasi-idle, 3 = plaques qui claquent sur le torse, 4-5 =
## armure qui se densifie, 6 = armure complète) — le "claquage" (frame 3)
## tombe au même tick que impactFlashFrame (tick 10, power.carapace.cast.json).
const CARAPACE_ACTIVATION_FRAME_TICK_BOUNDS: Array[int] = [3, 6, 9, 14, 18, 21, 24]
## RECOVERY : mêmes bornes relatives que l'activation, appliquées à
## "carapace_fin" (déjà en ordre inverse — frame 0 = armure complète, frame
## 6 = idle) : l'armure part complète et se dissout au même rythme qu'elle
## s'était formée, symétrie délibérée plutôt qu'une 2e mesure séparée.
const CARAPACE_RECOVERY_FRAME_TICK_BOUNDS: Array[int] = [3, 6, 9, 14, 18, 21, 24]
## Boucle ACTIVE : 4 frames animées (+ 1 référence identique à frame0,
## jamais rejouée — voir CARAPACE_ACTIVE_LOOP_FRAME_COUNT) qui tournent en
## continu tant que l'état soutenu dure, contrairement à toutes les autres
## compétences Terre (une seule passe linéaire jamais bouclée). Chaque
## frame tient CARAPACE_ACTIVE_LOOP_FRAME_TICKS ticks avant de passer à la
## suivante, modulo le nombre de frames — jamais la fps autonome
## d'AnimatedSprite2D (même bug de classe que documenté 4 fois ce cycle,
## mais ici la question ne se poserait même pas sans ce pilotage : Godot ne
## boucle pas nativement une fenêtre de N frames au milieu d'une anim plus
## longue).
const CARAPACE_ACTIVE_LOOP_FRAME_COUNT := 4
const CARAPACE_ACTIVE_LOOP_FRAME_TICKS := 10

## Fenêtre d'annulation (mandat "fluidité") — PROPRIÉTÉ PROPRE à Carapace :
## contrairement aux 4 autres compétences Terre, PAS de fenêtre pendant
## ACTIVATION ni ACTIVE (un bouclier qu'on peut annuler à volonté avant sa
## fin naturelle perdrait son sens défensif — décision délibérée, pas un
## oubli) — seule la toute fin de RECOVERY (queue, même convention que les
## autres) accepte un input mis en file, une fois l'armure déjà retirée.
const CARAPACE_CANCEL_WINDOW_TICKS := 10

## Effondrement (Terre, Tier 4, ZONE, IMPACT MAJEUR) — CHANTIER A
## (2026-08-24). GDD/planche (docs/references/terre/effondrement.png) :
## "Les fissures se propagent, convergent vers Rank Zero, puis le sol
## s'effondre et explose à l'impact" — AoE centré sur le LANCEUR (pas un
## cône frontal comme Poing Tellurique/Bras-Faux, ni une ligne comme Marée
## de Sable), anticipation plus longue qu'un impact simple (tier "majeur").
const EFFONDREMENT_ANTICIPATION_TICKS := 30
const EFFONDREMENT_RELEASE_TICKS := 6
const EFFONDREMENT_RECOVERY_TICKS := 26
const EFFONDREMENT_RADIUS_PX := 70.0  # AoE circulaire autour du lanceur, plus large que Poing Tellurique (44px, un arc).
const EFFONDREMENT_DAMAGE := 22.0  # TUNABLE, la plus élevée des 5 compétences Terre — "impact majeur" de la fiche.
const EFFONDREMENT_COOLDOWN_TICKS := 340  # généreux, cohérent avec des dégâts/portée au-dessus des 4 autres.
const EffondrementRecipeId := "power.effondrement.cast"
const EFFONDREMENT_CAST_SEED := 51007  # Addendum A §A.5, jamais l'horloge murale.

## Art dédié (agent Terre, CHANTIER A 2026-08-24) : Effondrement ne
## transforme aucun membre — une POSE, comme Poing Tellurique/Marée de
## Sable (animate_character v3 direct sur l'état "Idle", pas de
## create_character_state). Prompt : bras levés haut ensemble puis abattus
## au sol, stance large, accroupissement profond à l'impact — 6 frames sud
## + référence acceptées dès le 1er essai (0-2 lever progressif, 3-4 zénith
## bras en X puis rapprochés, 5-6 accroupissement profond bras au sol).
## Cohérent avec la planche : temps 1-2 (Propagation/Convergence) montrent
## Cendre debout/normal — le sprite lève simplement les bras pendant que le
## VFX (groundRing/fractureLine) porte les fissures ; temps 3-4
## (Compression/Impact) sont majoritairement portés par le VFX (converge/
## shardBurst/smokePuff), le sprite reste figé en accroupissement profond
## (frame 6) — aucune primitive "pic de roche" dédiée n'existe dans le
## registre actuel, limite documentée dans power.effondrement.cast.json.
##
## Pilotage tick-exact : frame 6 (accroupissement/impact) couvre TOUT le
## RELEASE + toute la RECOVERY (31 à 62) — le sprite ne bouge plus une fois
## le coup porté, seul le VFX continue de jouer l'explosion/la retombée.
const EFFONDREMENT_FRAME_TICK_BOUNDS: Array[int] = [4, 9, 14, 20, 25, 30, 62]

## Fenêtre d'annulation : queue de RECOVERY, un peu plus généreuse que
## Poing Tellurique (12 vs 12 des ~26 ticks de recovery, même proportion
## ~45%) — cohérent avec un impact déjà "vendu" dès le tick 31.
const EFFONDREMENT_CANCEL_WINDOW_TICKS := 12

## Fissure Éruptive (Terre, Tier 5, dernière compétence Terre) — CHANTIER A
## (2026-08-24). GDD/planche (docs/references/terre/fissure_eruptive.png,
## 4 temps : Préparation/Fissure/Soulèvement/Retombée) : effet RANGÉ, PAS
## centré sur le lanceur (contrairement à Effondrement) — la fissure part
## de Rank Zero et voyage au sol avant que les pics n'émergent à distance.
const FISSURE_ERUPTIVE_ANTICIPATION_TICKS := 20
const FISSURE_ERUPTIVE_RELEASE_TICKS := 8
const FISSURE_ERUPTIVE_RECOVERY_TICKS := 30
const FISSURE_ERUPTIVE_RANGE_PX := 110.0  # distance parcourue par la fissure avant l'éruption — la plus longue portée Terre.
const FISSURE_ERUPTIVE_IMPACT_RADIUS_PX := 40.0  # petit AoE circulaire AU POINT D'IMPACT, pas au lanceur.
const FISSURE_ERUPTIVE_DAMAGE := 18.0  # TUNABLE, entre Marée de Sable (8, contrôle) et Effondrement (22, impact majeur).
const FISSURE_ERUPTIVE_COOLDOWN_TICKS := 260
const FissureEruptiveRecipeId := "power.fissure_eruptive.cast"
const FISSURE_ERUPTIVE_CAST_SEED := 51008  # Addendum A §A.5, jamais l'horloge murale.

## Art dédié (agent Terre, CHANTIER A 2026-08-24) : Fissure Éruptive est la
## SEULE compétence Terre dont la planche montre un objet tenu (bâton
## planté au sol) — prompt PixelLab a délibérément INCLUS "gripping a plain
## rough wooden staff" plutôt que les exclusions négatives "no weapon"
## systématiques des 4 autres pouvoirs Terre (écart assumé, documenté dans
## data/pixellab_usage.jsonl). 6 frames sud + référence acceptées au 1er
## essai avec UNE réserve honnête : frame 3 (transition) montre une forme
## ambiguë près des mains/tête (ni clairement un bâton ni un artefact net)
## — frames 4-6 résolvent clairement en un outil tenu à deux mains planté
## au sol (silhouette proche d'une pioche/pelle plutôt qu'un bâton
## parfaitement lisse, mais lit sans ambiguïté comme un OUTIL DE TERRE
## planté — accepté, pas de reroll pour une nuance sur 1 frame de transition
## occupant 1 seul tick à l'écran, discipline anti-reroll-infini).
##
## Pilotage tick-exact : frame 6 (outil planté) couvre le RELEASE et toute
## la RECOVERY (20 à 58) pendant que le VFX (groundRing/shardBurst/
## smokePuff, tous décalés via origin_offset_px=FISSURE_ERUPTIVE_RANGE_PX)
## joue le Soulèvement/la Retombée À DISTANCE du personnage.
const FISSURE_ERUPTIVE_FRAME_TICK_BOUNDS: Array[int] = [3, 7, 11, 14, 18, 23, 58]

## Fenêtre d'annulation : queue de RECOVERY, proportion proche des 4 autres
## compétences Terre (~40% des 30 ticks de recovery).
const FISSURE_ERUPTIVE_CANCEL_WINDOW_TICKS := 12

## Corbeau Pâle / Poing du Colosse / Œil Sans Regard / Serpent Creux
## (INVOCATEUR, Tiers 2-5 — MANDAT ROUND 4 / PLAN DE PRODUCTION, agent
## Invocateur, docs/references/invocateur/) : contrairement à Gueule Vide
## (aucun _action_lock, "l'invocation n'immobilise pas le joueur" —
## exception documentée ci-dessus, jugée "déjà maximalement fluide" et
## donc non retouchée), ces 4 compétences REÇOIVENT le patron ANTICIPATION/
## RELEASE/RECOVERY + _action_lock + <SKILL>_CANCEL_WINDOW_TICKS déjà
## établi sur Bras-Faux/Poing Belluaire/Poing Tellurique/Marée de Sable
## (mandat "fluidité", commit 1571521) — branché DÈS la construction,
## comme l'exige le mandat ("pas de round de polish séparé après coup").
## Raison du choix : les 4 planches de référence montrent Cendre engagé
## dans un geste de cast à part entière sur plusieurs temps (contrairement
## au simple "bras tendu en arrière-plan" de Gueule Vide), et ce sont des
## compétences plus lourdes (Tier 2 à 5, jusqu'à l'ultime) qui méritent
## d'être de vraies actions engageantes, pas un aparté sans conséquence.
##
## Double timeline assumée et documentée (comme Gueule Vide) : CETTE
## timeline (ANTICIPATION/RELEASE/RECOVERY) ne pilote QUE le geste de
## CENDRE LUI-MÊME (son propre AnimatedSprite2D, "invocation_<skill>",
## 6 frames) et son _action_lock — la créature/l'effet invoqué est une
## scène séparée (src/gameplay/powers/<skill>.gd, patron GueuleVide :
## FRAME_TICK_BOUNDS/tick propre/contact via Targeting) instanciée au
## RELEASE (tick 1, même convention que _try_hit_bras_faux() etc.) et qui
## vit sa propre vie ensuite, DÉCOUPLÉE de _action_lock — Cendre peut donc
## se remettre à bouger (RECOVERY) pendant que la créature achève sa
## propre timeline plus longue, exactement comme Gueule Vide aujourd'hui.
## Durées/dégâts/portées TUNABLE (aucune fiche bible chiffrée pour ces 4
## compétences, sauf Serpent Creux §6.2 — "portée supérieure à Gueule
## Vide, attaque linéaire, plusieurs cibles possibles", respecté dans
## serpent_creux.gd).

const CorbeauPaleRecipeId := "power.corbeau_pale.cast"
const CORBEAU_PALE_ANTICIPATION_TICKS := 12
const CORBEAU_PALE_RELEASE_TICKS := 4
const CORBEAU_PALE_RECOVERY_TICKS := 16
const CORBEAU_PALE_CANCEL_WINDOW_TICKS := 10
const CORBEAU_PALE_COOLDOWN_TICKS := 200  # ~3,3s @ 60/s — compétence rapide/légère (Tier 2), cooldown court.
const CORBEAU_PALE_SPAWN_DISTANCE_PX := 32.0  # ~1m — le corbeau se forme tout près de Cendre avant de foncer (RANGE_PX propre, corbeau_pale.gd).
const CORBEAU_PALE_FRAME_TICK_BOUNDS: Array[int] = [6, 12, 16, 22, 27, 32]

const PoingDuColosseRecipeId := "power.poing_du_colosse.cast"
const POING_DU_COLOSSE_ANTICIPATION_TICKS := 18
const POING_DU_COLOSSE_RELEASE_TICKS := 6
const POING_DU_COLOSSE_RECOVERY_TICKS := 22
const POING_DU_COLOSSE_CANCEL_WINDOW_TICKS := 12
const POING_DU_COLOSSE_COOLDOWN_TICKS := 300  # 5s @ 60/s — "impact majeur" (Tier 3), le plus lourd des 4.
const POING_DU_COLOSSE_SPAWN_DISTANCE_PX := 64.0  # ~2m — plus proche que Gueule Vide (96px, 3m) : un poing s'abat, il n'a pas besoin d'approcher.
const POING_DU_COLOSSE_FRAME_TICK_BOUNDS: Array[int] = [8, 16, 24, 32, 39, 46]

const OeilSansRegardRecipeId := "power.oeil_sans_regard.cast"
const OEIL_SANS_REGARD_ANTICIPATION_TICKS := 16
const OEIL_SANS_REGARD_RELEASE_TICKS := 6
const OEIL_SANS_REGARD_RECOVERY_TICKS := 20
const OEIL_SANS_REGARD_CANCEL_WINDOW_TICKS := 10
const OEIL_SANS_REGARD_COOLDOWN_TICKS := 280  # ~4,7s @ 60/s — Tier 4, pierce en ligne.
const OEIL_SANS_REGARD_SPAWN_DISTANCE_PX := 64.0  # ~2m devant Cendre
const OEIL_SANS_REGARD_SPAWN_HEIGHT_OFFSET_PX := -40.0  # l'œil flotte "dans les airs" (fiche planche) — décalage vertical (Y négatif = vers le haut de l'écran), pas au sol comme les autres créatures.
const OEIL_SANS_REGARD_FRAME_TICK_BOUNDS: Array[int] = [7, 14, 22, 29, 36, 42]

const SerpentCreuxRecipeId := "power.serpent_creux.cast"
const SERPENT_CREUX_ANTICIPATION_TICKS := 20
const SERPENT_CREUX_RELEASE_TICKS := 6
const SERPENT_CREUX_RECOVERY_TICKS := 24
const SERPENT_CREUX_CANCEL_WINDOW_TICKS := 12
const SERPENT_CREUX_COOLDOWN_TICKS := 400  # ~6,7s @ 60/s — l'ultime (Tier 5/5), le plus long cooldown de la Classe.
const SERPENT_CREUX_SPAWN_DISTANCE_PX := 48.0  # ~1,5m — "déjà comprimé" tout près de Cendre, voir serpent_creux.gd RANGE_PX pour la portée réelle après relâchement.
const SERPENT_CREUX_FRAME_TICK_BOUNDS: Array[int] = [9, 18, 26, 35, 43, 50]

@export var stats: Stats = Stats.new()

## Direction de face courante (8 valeurs), utile aux futures frames
## directionnelles PixelLab (Phase 1.3+, 7 directions restantes) — mis à
## jour uniquement quand il y a un mouvement réel, jamais remis à zéro à
## l'arrêt (le perso garde sa dernière orientation).
var facing: Vector2 = Vector2.DOWN

## Verrouille l'animation de mouvement (idle/déplacement) pendant qu'une
## action ponctuelle (hurt/dash/mort/combo) joue — sinon _physics_process
## écraserait la pose dès la frame suivante. Pour hurt, levé par
## _on_sprite_animation_finished(). Pour le combo ET le dash (B4), la
## timeline en ticks ci-dessous est SEULE responsable du verrou
## (_end_combo()/_end_dash()) — aucun des deux ne doit dépendre du
## timing de lecture du sprite, qui est une horloge séparée (§16.3 : ne
## pas fusionner deux minuteries distinctes).
var _action_lock: bool = false

## MANDAT "retours de playtest réel" (point 1) — voir DEATH_RESTART_INPUT_
## ENABLED_TICKS ci-dessus. Remonte à 0 dans `die()`, incrémenté à chaque
## tick tant que `stats.is_dead()` (voir `_process_death_restart()`).
var _death_ticks: int = 0

## Phase 2.1 (MANDAT SUITE v2) : famille "footstep" — pas de données de
## contact au sol par frame pour l'instant (8 directions, aucune n'a de
## marqueur dédié), donc un pas toutes les FOOTSTEP_PERIOD_TICKS tant que
## le joueur se déplace réellement, plutôt que d'inventer une donnée de
## contact qui n'existe pas encore.
const FOOTSTEP_PERIOD_TICKS := 18
var _footstep_tick: int = 0

## 0 = pas d'attaque en cours. 1-3 = quel coup du combo joue actuellement.
var _combo_step: int = 0
enum ComboPhase { NONE, ANTICIPATION, RELEASE, RECOVERY }
var _combo_phase: int = ComboPhase.NONE
var _combo_tick: int = 0
var _attack_queued: bool = false
var _hit_applied_this_release: bool = false

## Généralisation du buffer d'input aux 5 compétences dédiées (voir
## INPUT_BUFFER_TICKS ci-dessus) — 0 = rien en file, sinon le slot 1-5
## dont l'appui a été retenu pendant que `_action_lock` était vrai. UN SEUL
## slot à la fois (dernier appui gagne, même discipline que _attack_queued) :
## jamais une vraie file à plusieurs emplacements, juste "quel est le
## prochain input". `_queued_power_ticks_remaining` porte l'expiration —
## voir `_try_activate_power_slot()`, `_fire_queued_power_slot()`,
## `_try_consume_queued_input()`.
var _queued_power_slot: int = 0
var _queued_power_ticks_remaining: int = 0

## Mandat "critique probabiliste" (verrouillé par Milan — nom de travail
## interne "Black Flash", JAMAIS un nom exposé au joueur : la bible n'a
## pas encore de nom définitif, aucun texte UI ne doit l'afficher tel
## quel). N'IMPORTE LEQUEL des 3 coups du combo existant peut critiquer
## (pas un 4e/5e coup, aucune restructuration). Stockés ici plutôt que
## sur Stats : c'est un état de combo (remis à zéro par un coup subi,
## jamais persisté entre les morts/runs comme le niveau), pas une stat
## de progression durable.
const CRIT_BASE_CHANCE_PERCENT := 5.0
const CRIT_STREAK_BONUS_PERCENT := 3.0
const CRIT_STREAK_MAX_CHANCE_PERCENT := 40.0
## x1.5, PAS x2 comme TSB — verdict explicite de Milan : Rank Zero est du
## PvE solo sans contre-jeu ennemi, un x2 fréquent déséquilibrerait sans
## retuning complet des PV ennemis.
const CRIT_DAMAGE_MULT := 1.5
## Teinte jamais utilisée ailleurs dans le HUD/les VFX de combat actuels
## (impactFlashFrame reste dans les tons de la palette de chaque
## recette) — "flash, pas juste plus fort" (Milan) : ce plein-écran est
## la garantie d'être identifiable en un coup d'œil, indépendamment de
## la primitive VFX locale du coup qui a critiqué.
const CRIT_SCREEN_FLASH_COLOR := Color(1.0, 0.93, 0.35, 0.55)
const CRIT_SCREEN_FLASH_TICKS := 8

## Chance courante (%), remise à CRIT_BASE_CHANCE_PERCENT par tout coup
## subi (jamais une décroissance progressive — reset net, cf. mandat).
var _combo_crit_chance_percent: float = CRIT_BASE_CHANCE_PERCENT
## true tant qu'aucun coup n'a été subi depuis le début du combo À 3
## COUPS en cours — vérifié seulement quand ce combo atteint son 3e coup
## et se termine naturellement (voir _end_combo()) pour décider du bonus
## de streak. Un coup subi le remet à false IMMÉDIATEMENT (take_damage()),
## qu'il soit suivi ou non d'un 3e coup — pas de bonus a posteriori
## possible pour un combo qui a encaissé un coup en cours de route.
var _combo_hit_free_so_far: bool = true

## Compteur de ticks absolu depuis le DÉBUT du coup courant (0 à la
## première frappe de _advance_combo() après _start_attack()), INDÉPENDANT
## des remises à zéro de `_combo_tick` à chaque transition de phase —
## root_motion (mandat production v1 §4, données dans
## data/animation_composer/cendre.json) s'exprime sur cette timeline
## continue (start_tick/end_tick), pas sur le tick relatif à une seule
## phase.
var _combo_step_absolute_tick: int = 0

## data/animation_composer/cendre.json — root_motion (J1) par nom
## d'animation ; squash/lean/afterimages y sont déjà présents mais pas
## encore lus (J2, mandat production v1 §4/§6). Chargé une fois au
## _ready(), jamais relu par tick.
var _animation_composer_data: Dictionary = {}

## NONE = pas de dash en cours. Timeline déclarative (B4), même
## discipline que le combo ci-dessus.
enum DashPhase { NONE, ANTICIPATION, MOVE, RECOVERY }
var _dash_phase: int = DashPhase.NONE
var _dash_tick: int = 0
var _dash_direction: Vector2 = Vector2.ZERO
var _dash_recovery_velocity: Vector2 = Vector2.ZERO

## Même rôle que _combo_step_absolute_tick : continu sur toute la
## timeline ANTICIPATION+MOVE+RECOVERY du dash (0 au premier tick),
## indépendant des remises à zéro de `_dash_tick` par phase — squash/lean/
## afterimages du dash (J2) s'expriment sur cette timeline continue.
var _dash_step_absolute_tick: int = 0

## Même discipline que DashPhase : NONE = pas d'esquive en cours. ACTIVE est
## la SEULE phase où is_invincible() renvoie true — l'anticipation et la
## recovery n'accordent aucun i-frame (mandat §1.3 : "roulade... avec
## frames d'invincibilité", pas une invincibilité de bout en bout de
## l'action).
enum DodgePhase { NONE, ANTICIPATION, ACTIVE, RECOVERY }
var _dodge_phase: int = DodgePhase.NONE
var _dodge_tick: int = 0
var _dodge_direction: Vector2 = Vector2.ZERO
var _dodge_recovery_velocity: Vector2 = Vector2.ZERO
var _dodge_step_absolute_tick: int = 0
var _dodge_cooldown_remaining: int = 0

## Gueule Vide n'utilise PAS _action_lock : l'invocation (0,7s) n'immobilise
## pas le joueur (rien dans le mandat ne l'exige, contrairement au combo/
## dash) — seul un cooldown la borne dans le temps.
var _power1_cooldown_remaining: int = 0

## Bras-Faux — même discipline de timeline que le combo/dash/esquive
## (ANTICIPATION/RELEASE/RECOVERY, _action_lock pendant toute l'action :
## contrairement à Gueule Vide, "aucun déplacement automatique" du GDD
## implique que le joueur reste engagé dans son geste, pas libre de
## bouger pendant qu'il balaie).
enum BrasFauxPhase { NONE, ANTICIPATION, RELEASE, RECOVERY }
var _bras_faux_phase: int = BrasFauxPhase.NONE
var _bras_faux_tick: int = 0
var _bras_faux_hit_applied: bool = false
var _bras_faux_cooldown_remaining: int = 0

## Poing Belluaire / Poing Tellurique — même discipline que Bras-Faux
## ci-dessus (une timeline de ticks propre par pouvoir, _action_lock
## pendant toute l'action : aucun des deux ne mentionne de déplacement
## automatique dans la fiche, contrairement à Pattes de Chasse).
enum PoingBelluairePhase { NONE, ANTICIPATION, RELEASE, RECOVERY }
var _poing_belluaire_phase: int = PoingBelluairePhase.NONE
var _poing_belluaire_tick: int = 0
var _poing_belluaire_hit_applied: bool = false
var _poing_belluaire_cooldown_remaining: int = 0

enum PoingTelluriquePhase { NONE, ANTICIPATION, RELEASE, RECOVERY }
var _poing_tellurique_phase: int = PoingTelluriquePhase.NONE
var _poing_tellurique_tick: int = 0
var _poing_tellurique_hit_applied: bool = false
var _poing_tellurique_cooldown_remaining: int = 0

enum MareeDeSablePhase { NONE, ANTICIPATION, RELEASE, RECOVERY }
var _maree_de_sable_phase: int = MareeDeSablePhase.NONE
var _maree_de_sable_tick: int = 0
var _maree_de_sable_hit_applied: bool = false
var _maree_de_sable_cooldown_remaining: int = 0

## Carapace (Terre, Tier 3, DÉFENSIF) — 3 phases ACTIVATION/ACTIVE/RECOVERY
## (pas ANTICIPATION/RELEASE/RECOVERY, voir le bloc de constantes CARAPACE_*
## plus haut pour le raisonnement complet). _carapace_active_loop_tick est
## un compteur SÉPARÉ de _carapace_tick : ce dernier reset à chaque
## transition de phase (même convention que tous les autres pouvoirs),
## alors que la boucle de respiration doit tourner en continu sur toute la
## durée d'ACTIVE sans se resynchroniser à rien d'autre qu'elle-même.
enum CarapacePhase { NONE, ACTIVATION, ACTIVE, RECOVERY }
var _carapace_phase: int = CarapacePhase.NONE
var _carapace_tick: int = 0
var _carapace_active_loop_tick: int = 0
var _carapace_cooldown_remaining: int = 0

## Effondrement (Terre, Tier 4) — même discipline ANTICIPATION/RELEASE/
## RECOVERY que Bras-Faux/Poing Belluaire/Poing Tellurique/Marée de Sable.
enum EffondrementPhase { NONE, ANTICIPATION, RELEASE, RECOVERY }
var _effondrement_phase: int = EffondrementPhase.NONE
var _effondrement_tick: int = 0
var _effondrement_hit_applied: bool = false
var _effondrement_cooldown_remaining: int = 0

## Fissure Éruptive (Terre, Tier 5) — même discipline ANTICIPATION/RELEASE/
## RECOVERY que les autres compétences Terre à impact ponctuel.
enum FissureEruptivePhase { NONE, ANTICIPATION, RELEASE, RECOVERY }
var _fissure_eruptive_phase: int = FissureEruptivePhase.NONE
var _fissure_eruptive_tick: int = 0
var _fissure_eruptive_hit_applied: bool = false
var _fissure_eruptive_cooldown_remaining: int = 0

## Mâchoire / Forme Bestiale — même discipline ANTICIPATION/RELEASE/RECOVERY
## que Bras-Faux/Poing Belluaire/Poing Tellurique/Marée de Sable ci-dessus
## (aucun déplacement automatique, _action_lock pendant toute l'action).
enum MachoirePhase { NONE, ANTICIPATION, RELEASE, RECOVERY }
var _machoire_phase: int = MachoirePhase.NONE
var _machoire_tick: int = 0
var _machoire_hit_applied: bool = false
var _machoire_cooldown_remaining: int = 0

enum FormeBestialePhase { NONE, ANTICIPATION, RELEASE, RECOVERY }
var _forme_bestiale_phase: int = FormeBestialePhase.NONE
var _forme_bestiale_tick: int = 0
var _forme_bestiale_hit_applied: bool = false
var _forme_bestiale_cooldown_remaining: int = 0

## Pattes de Chasse — ANTICIPATION/MOVE/RECOVERY comme le dash (DashPhase
## ci-dessus), PAS ANTICIPATION/RELEASE/RECOVERY : seul pouvoir de
## Monstrification avec un déplacement automatique du joueur pendant
## l'action (voir PATTES_DE_CHASSE_* ci-dessus).
enum PattesDeChassePhase { NONE, ANTICIPATION, MOVE, RECOVERY }
var _pattes_de_chasse_phase: int = PattesDeChassePhase.NONE
var _pattes_de_chasse_tick: int = 0
var _pattes_de_chasse_hit_applied: bool = false
var _pattes_de_chasse_cooldown_remaining: int = 0
var _pattes_de_chasse_direction: Vector2 = Vector2.ZERO
var _pattes_de_chasse_recovery_velocity: Vector2 = Vector2.ZERO

## Corbeau Pâle / Poing du Colosse / Œil Sans Regard / Serpent Creux
## (INVOCATEUR) — même discipline ANTICIPATION/RELEASE/RECOVERY que
## Bras-Faux/Poing Belluaire/Poing Tellurique/Marée de Sable ci-dessus
## (_action_lock pendant toute l'action, aucun déplacement automatique du
## joueur), voir le bloc de constantes CORBEAU_PALE_*/POING_DU_COLOSSE_*/
## OEIL_SANS_REGARD_*/SERPENT_CREUX_* plus haut pour le raisonnement
## complet (double timeline : Cendre lui-même ici, la créature invoquée
## sur sa propre horloge séparée dans src/gameplay/powers/<skill>.gd).
enum CorbeauPalePhase { NONE, ANTICIPATION, RELEASE, RECOVERY }
var _corbeau_pale_phase: int = CorbeauPalePhase.NONE
var _corbeau_pale_tick: int = 0
var _corbeau_pale_spawned: bool = false
var _corbeau_pale_cooldown_remaining: int = 0

enum PoingDuColossePhase { NONE, ANTICIPATION, RELEASE, RECOVERY }
var _poing_du_colosse_phase: int = PoingDuColossePhase.NONE
var _poing_du_colosse_tick: int = 0
var _poing_du_colosse_spawned: bool = false
var _poing_du_colosse_cooldown_remaining: int = 0

enum OeilSansRegardPhase { NONE, ANTICIPATION, RELEASE, RECOVERY }
var _oeil_sans_regard_phase: int = OeilSansRegardPhase.NONE
var _oeil_sans_regard_tick: int = 0
var _oeil_sans_regard_spawned: bool = false
var _oeil_sans_regard_cooldown_remaining: int = 0

enum SerpentCreuxPhase { NONE, ANTICIPATION, RELEASE, RECOVERY }
var _serpent_creux_phase: int = SerpentCreuxPhase.NONE
var _serpent_creux_tick: int = 0
var _serpent_creux_spawned: bool = false
var _serpent_creux_cooldown_remaining: int = 0

## Recul du joueur sous un coup ennemi (G, GDD §10 — voir take_damage()
## ci-dessous) : même construction qu'Enemy._recoil_ticks_remaining, mais
## portée par sa propre timeline (ACTIVE/NONE) au lieu d'une simple
## variable de compte à rebours, pour ne pas se faire écraser par
## _handle_movement() au tick suivant (§16.3, même piège que dash/dodge —
## voir le commentaire historique sur take_damage() plus bas).
enum HurtPhase { NONE, ACTIVE }
var _hurt_phase: int = HurtPhase.NONE
## Phase R4 (game feel Milan, "knockback_return_curve: easeOut") — voir
## Enemy._recoil_tick/AnimationComposer.ease_out_step_px(), même construction.
var _hurt_recoil_tick: int = 0
var _hurt_recoil_total_ticks: int = 0
var _hurt_recoil_total_distance_px: float = 0.0
var _hurt_recoil_direction: Vector2 = Vector2.ZERO

@onready var _sprite: AnimatedSprite2D = $AnimatedSprite2D
@onready var _camera: Camera2D = $Camera2D

## Phase 2.3 (MANDAT SUITE v2) : outlineSelective (allié = bleu, toujours actif)
## + directionalStreak (dash seulement) fusionnés dans un seul shader — un
## CanvasItem n'a qu'un slot `material`, HitResponse.flash_sprite() sauvegarde/
## restaure déjà ce matériau générique (Object quelconque) sans rien savoir de
## son contenu, donc aucune interaction spéciale à gérer ici.
const PlayerFxShader := preload("res://src/vfx/shaders/player_fx.gdshader")
var _fx_material: ShaderMaterial


func _ready() -> void:
	add_to_group("player")
	if has_node("/root/RunState"):
		stats = get_node("/root/RunState").player_stats
	_sprite.animation_finished.connect(_on_sprite_animation_finished)
	_animation_composer_data = _load_animation_composer_data()
	_fx_material = ShaderMaterial.new()
	_fx_material.shader = PlayerFxShader
	_sprite.material = _fx_material


func _load_animation_composer_data() -> Dictionary:
	const PATH := "res://data/animation_composer/cendre.json"
	if not FileAccess.file_exists(PATH):
		return {}
	var text: String = FileAccess.get_file_as_string(PATH)
	var parsed: Variant = JSON.parse_string(text)
	if parsed is Dictionary:
		return parsed
	return {}


func _physics_process(_delta: float) -> void:
	# Le shake ET le punch-zoom continuent de s'appliquer PENDANT un
	# hit-stop (c'est en partie ce qui vend l'impact) — lus avant le
	# retour anticipé ci-dessous, jamais après. Lookahead (mandat
	# production v1 §4, CameraDirector, J2) : direction du dash en cours
	# uniquement, Vector2.ZERO sinon (get_lookahead_offset() le gère déjà).
	var lookahead: Vector2 = CameraDirector.get_lookahead_offset(
		_dash_direction if _dash_phase != DashPhase.NONE
		else (_pattes_de_chasse_direction if _pattes_de_chasse_phase == PattesDeChassePhase.MOVE else Vector2.ZERO))
	_camera.offset = CombatFeedback.get_shake_offset() + lookahead
	_camera.zoom = CameraDirector.get_zoom()
	# Phase R4 : hit-stop asymétrique — le joueur consulte SON compteur
	# (attaquant quand il frappe, cible quand il encaisse un coup ennemi ;
	# CombatFeedback.register_hit() route déjà les deux compteurs selon
	# `attacker_is_player`, ce nœud n'a qu'à lire celui qui le concerne).
	if CombatFeedback.is_player_frozen():
		return

	if stats.is_dead():
		_process_death_restart()
		return

	if _power1_cooldown_remaining > 0:
		_power1_cooldown_remaining -= 1
	if _dodge_cooldown_remaining > 0:
		_dodge_cooldown_remaining -= 1
	if _bras_faux_cooldown_remaining > 0:
		_bras_faux_cooldown_remaining -= 1
	if _poing_belluaire_cooldown_remaining > 0:
		_poing_belluaire_cooldown_remaining -= 1
	if _poing_tellurique_cooldown_remaining > 0:
		_poing_tellurique_cooldown_remaining -= 1
	if _maree_de_sable_cooldown_remaining > 0:
		_maree_de_sable_cooldown_remaining -= 1
	if _carapace_cooldown_remaining > 0:
		_carapace_cooldown_remaining -= 1
	if _effondrement_cooldown_remaining > 0:
		_effondrement_cooldown_remaining -= 1
	if _fissure_eruptive_cooldown_remaining > 0:
		_fissure_eruptive_cooldown_remaining -= 1
	if _machoire_cooldown_remaining > 0:
		_machoire_cooldown_remaining -= 1
	if _forme_bestiale_cooldown_remaining > 0:
		_forme_bestiale_cooldown_remaining -= 1
	if _pattes_de_chasse_cooldown_remaining > 0:
		_pattes_de_chasse_cooldown_remaining -= 1
	if _corbeau_pale_cooldown_remaining > 0:
		_corbeau_pale_cooldown_remaining -= 1
	if _poing_du_colosse_cooldown_remaining > 0:
		_poing_du_colosse_cooldown_remaining -= 1
	if _oeil_sans_regard_cooldown_remaining > 0:
		_oeil_sans_regard_cooldown_remaining -= 1
	if _serpent_creux_cooldown_remaining > 0:
		_serpent_creux_cooldown_remaining -= 1
	if _gueule_vide_gesture_ticks_remaining > 0:
		_gueule_vide_gesture_ticks_remaining -= 1
	# Expiration du buffer d'input généralisé (mandat "fluidité") — décompte
	# à CHAQUE tick, quelle que soit la branche prise plus bas, sinon un
	# input mis en file pendant un dash/une esquive (qui n'ont pas de
	# fenêtre d'annulation dédiée, voir le filet de sécurité en bas de
	# fonction) ne serait jamais nettoyé à temps.
	if _queued_power_ticks_remaining > 0:
		_queued_power_ticks_remaining -= 1
		if _queued_power_ticks_remaining <= 0:
			_queued_power_slot = 0

	if Input.is_action_just_pressed("attack"):
		_attack_queued = true

	# Amendement GDD Pouvoir/déblocage (confirmé par Milan) : power1..power5
	# ne sont plus liés en dur à une compétence précise, voir
	# _try_activate_power_slot() et le bloc de constantes juste après ce
	# fichier pour la table des compétences réellement implémentées.
	for slot_index in range(1, 6):
		if Input.is_action_just_pressed("power%d" % slot_index):
			_try_activate_power_slot(slot_index)

	if Input.is_action_just_pressed("dash"):
		play_dash()

	if Input.is_action_just_pressed("dodge"):
		play_dodge()

	if _dash_phase != DashPhase.NONE:
		_advance_dash()
	elif _dodge_phase != DodgePhase.NONE:
		_advance_dodge()
	elif _bras_faux_phase != BrasFauxPhase.NONE:
		_advance_bras_faux()
	elif _poing_belluaire_phase != PoingBelluairePhase.NONE:
		_advance_poing_belluaire()
	elif _poing_tellurique_phase != PoingTelluriquePhase.NONE:
		_advance_poing_tellurique()
	elif _maree_de_sable_phase != MareeDeSablePhase.NONE:
		_advance_maree_de_sable()
	elif _carapace_phase != CarapacePhase.NONE:
		_advance_carapace()
	elif _effondrement_phase != EffondrementPhase.NONE:
		_advance_effondrement()
	elif _fissure_eruptive_phase != FissureEruptivePhase.NONE:
		_advance_fissure_eruptive()
	elif _machoire_phase != MachoirePhase.NONE:
		_advance_machoire()
	elif _forme_bestiale_phase != FormeBestialePhase.NONE:
		_advance_forme_bestiale()
	elif _pattes_de_chasse_phase != PattesDeChassePhase.NONE:
		_advance_pattes_de_chasse()
	elif _corbeau_pale_phase != CorbeauPalePhase.NONE:
		_advance_corbeau_pale()
	elif _poing_du_colosse_phase != PoingDuColossePhase.NONE:
		_advance_poing_du_colosse()
	elif _oeil_sans_regard_phase != OeilSansRegardPhase.NONE:
		_advance_oeil_sans_regard()
	elif _serpent_creux_phase != SerpentCreuxPhase.NONE:
		_advance_serpent_creux()
	elif _combo_step > 0:
		_advance_combo()
	elif _hurt_phase != HurtPhase.NONE:
		_advance_hurt()
	elif _attack_queued and not stats.is_dead() and not _action_lock:
		_attack_queued = false
		velocity = Vector2.ZERO
		_start_attack(1)
	elif _queued_power_slot > 0 and not stats.is_dead() and not _action_lock:
		# Filet de sécurité (mandat "fluidité") : couvre les cas où
		# `_action_lock` se lève SANS jamais traverser la fenêtre
		# d'annulation dédiée d'une compétence (dash/esquive/hurt, qui n'en
		# ont pas — voir _advance_dash()/_advance_dodge()/_advance_hurt())
		# — sans ce filet, un pouvoir mis en file pendant un dash resterait
		# en attente jusqu'à expiration au lieu de se déclencher "dès que
		# possible" (mandat) dès que le dash se termine.
		velocity = Vector2.ZERO
		_fire_queued_power_slot()
	else:
		_handle_movement()

	move_and_slide()


func _handle_movement() -> void:
	var input_dir := Vector2(
		Input.get_action_strength("ui_right") - Input.get_action_strength("ui_left"),
		Input.get_action_strength("ui_down") - Input.get_action_strength("ui_up")
	)
	if input_dir.length_squared() > 1.0:
		input_dir = input_dir.normalized()

	velocity = input_dir * stats.move_speed_px
	if input_dir.length_squared() > 0.0001:
		facing = input_dir.normalized()

	if not _action_lock and not stats.is_dead() and input_dir.length_squared() > 0.0001:
		_footstep_tick += 1
		if _footstep_tick >= FOOTSTEP_PERIOD_TICKS:
			_footstep_tick = 0
			Sfx.play("footstep")
	else:
		_footstep_tick = 0

	# Fenêtre de geste Gueule Vide (GUEULE_VIDE_GESTURE_TICKS, voir
	# _cast_gueule_vide()) : PAS d'_action_lock (le joueur reste libre de
	# bouger, choix délibéré), mais tant qu'il reste réellement immobile
	# (input_dir nul) le geste "invocation_gueule_vide" ne doit pas être
	# écrasé dès le tick suivant par idle_<suffix> — sinon la pose ne
	# durerait qu'1 frame, invisible en jeu (audit "polish complet" du
	# 2026-08-23). Un déplacement réel pendant la fenêtre reprend la main
	# immédiatement (input_dir.length_squared() > 0.0001 rend ce garde
	# faux) : aucun verrou de mouvement, seule la pose stationnaire est
	# protégée.
	var gueule_vide_gesture_active: bool = (
		_gueule_vide_gesture_ticks_remaining > 0 and input_dir.length_squared() < 0.0001
	)
	if not _action_lock and not stats.is_dead() and not gueule_vide_gesture_active:
		# E (mandat production v1 §6) : art réel par direction pour idle/
		# déplacement (8 rotations PixelLab, plus de flip_h ici — contrairement
		# au combo/dash/esquive qui restent "sud" seul + flip_h, hors scope
		# de cette brique, §6 "dash/combo/esquive si budget PixelLab, sinon
		# flag"). flip_h à false explicitement : sans ça la valeur laissée
		# par la dernière attaque (_start_attack, qui se flip elle-même
		# indépendamment depuis ce fix) doublerait le miroir sur un art
		# ouest déjà dessiné tel quel.
		_sprite.flip_h = false
		var suffix := _direction_suffix(facing)
		_sprite.play(("deplacement_" if input_dir.length_squared() > 0.0001 else "idle_") + suffix)


## Snappe une direction sur le compas à 8 branches le plus proche, dans la
## même convention que les rotations PixelLab (south/south_east/east/...) —
## Y+ = bas = sud (convention écran Godot, cohérente avec DodgeDirection/
## facing par défaut = Vector2.DOWN = "south").
static func _direction_suffix(dir: Vector2) -> String:
	if dir.length_squared() < 0.0001:
		return "south"
	const SUFFIXES := ["east", "south_east", "south", "south_west", "west", "north_west", "north", "north_east"]
	var octant: int = int(round(rad_to_deg(dir.angle()) / 45.0)) % 8
	if octant < 0:
		octant += 8
	return SUFFIXES[octant]


func _start_attack(step: int) -> void:
	if step == 1:
		# Nouveau combo à 3 coups qui démarre (pas un chaînage vers
		# coup2/coup3) : réarme le suivi "sans dégât encaissé" pour CE
		# combo — mandat critique probabiliste.
		_combo_hit_free_so_far = true
	_combo_step = step
	_combo_phase = ComboPhase.ANTICIPATION
	_combo_tick = 0
	_combo_step_absolute_tick = 0
	_hit_applied_this_release = false
	_action_lock = true
	# Auto-contenu (comme play_dash()/play_dodge()) plutôt que de dépendre du
	# flip_h laissé par le dernier _handle_movement() : depuis E (§6), ce
	# dernier remet flip_h à false à CHAQUE tick de mouvement (l'art
	# idle/déplacement est maintenant dessiné par direction, plus par
	# miroir) — le combo, encore art "sud" seul, doit se flipper lui-même
	# pour rester correct face à l'ouest.
	if facing.x != 0.0:
		_sprite.flip_h = facing.x < 0.0
	_sprite.play(AttackAnimName[step - 1])


## Timeline déclarative du coup courant — ANTICIPATION -> RELEASE (frappe
## au premier tick) -> RECOVERY (fenêtre de chaînage sur les derniers
## CHAIN_WINDOW_TICKS). Ne dépend jamais de la durée réelle de lecture du
## sprite, uniquement des compteurs de ticks ci-dessous — sinon changer la
## fps d'une anim de coup déréglerait silencieusement le combat.
func _advance_combo() -> void:
	_combo_tick += 1
	_combo_step_absolute_tick += 1
	var anim_data: Dictionary = {}
	if _combo_step >= 1 and _combo_step <= AttackAnimName.size():
		anim_data = _animation_composer_data.get(AttackAnimName[_combo_step - 1], {})
	_apply_combo_root_motion(anim_data, _combo_step_absolute_tick)
	_apply_squash_lean_afterimages(anim_data, _combo_step_absolute_tick)
	# Phase R4 : timeline PAR TIER (voir COMBO_TIER_ANTICIPATION_TICKS/
	# COMBO_TIER_RECOVERY_TICKS ci-dessus) — tier1/2 valent toujours
	# ANTICIPATION_TICKS/RECOVERY_TICKS, seul tier3 diffère.
	var anticipation_ticks: int = COMBO_TIER_ANTICIPATION_TICKS[_combo_step - 1]
	var recovery_ticks: int = COMBO_TIER_RECOVERY_TICKS[_combo_step - 1]
	match _combo_phase:
		ComboPhase.ANTICIPATION:
			if _combo_tick >= anticipation_ticks:
				_combo_phase = ComboPhase.RELEASE
				_combo_tick = 0
		ComboPhase.RELEASE:
			if _combo_tick == 1 and not _hit_applied_this_release:
				_try_hit()
				_hit_applied_this_release = true
			if _combo_tick >= RELEASE_TICKS:
				_combo_phase = ComboPhase.RECOVERY
				_combo_tick = 0
		ComboPhase.RECOVERY:
			var chain_window_start := recovery_ticks - CHAIN_WINDOW_TICKS
			if _combo_tick >= chain_window_start:
				if _combo_step < AttackAnimName.size() and _attack_queued:
					_attack_queued = false
					_start_attack(_combo_step + 1)
					return
				# Mandat "fluidité" : la même fenêtre de chaînage du combo de
				# base sert AUSSI de fenêtre d'annulation vers un pouvoir mis
				# en file (`_queued_power_slot`) — couvre à la fois "presser
				# une compétence dédiée vers la fin de coup3" (pas de coup4,
				# le combo se relance ou saute directement vers le pouvoir)
				# et "presser un pouvoir vers la fin de coup1/coup2 alors
				# qu'aucun attaque n'est en file". `_try_consume_queued_input`
				# gère aussi `_attack_queued` en interne (le cas tier3 déjà
				# écarté par AttackAnimName.size() ci-dessus tombe ici et
				# relance un combo tier1, comportement voulu : pas de coup4).
				if _try_consume_queued_input(_end_combo):
					return
			if _combo_tick >= recovery_ticks:
				_end_combo()


## Root motion (mandat production v1 §4, "constat fondateur" : "les
## attaques jouaient sur place, `velocity = 0` pendant le combo") — pousse
## le joueur en avant (`facing`) sur la fenêtre [start_tick, end_tick] de
## `data/animation_composer/cendre.json` pour le coup courant, JAMAIS en
## dehors (velocity remise à zéro par défaut). Via `velocity` uniquement
## (murs solides via move_and_slide(), déjà appelé une fois par frame en
## fin de _physics_process — jamais une écriture directe de `position`).
## Même construction ease-out par différence progress_after-progress_before
## que _advance_dash() (MOVE) : réutilise _ease_out_quad(), pas une
## nouvelle courbe dupliquée.
func _apply_combo_root_motion(anim_data: Dictionary, abs_tick: int) -> void:
	velocity = Vector2.ZERO
	var rm: Dictionary = anim_data.get("root_motion", {})
	if rm.is_empty():
		return
	var start_tick: int = int(rm.get("start_tick", 0))
	var end_tick: int = int(rm.get("end_tick", 0))
	var span: int = end_tick - start_tick
	if span <= 0 or abs_tick < start_tick or abs_tick > end_tick:
		return
	var distance_px: float = float(rm.get("distance_px", 0.0))
	var progress_before: float = _ease_out_quad(float(abs_tick - 1 - start_tick) / span)
	var progress_after: float = _ease_out_quad(float(abs_tick - start_tick) / span)
	var step_px: float = (progress_after - progress_before) * distance_px
	velocity = facing * (step_px * Engine.physics_ticks_per_second)


## AnimationComposer (mandat production v1 §4/J2) : squash (impulsion
## d'échelle, aussi utilisée comme "smear" mandat J2 pour coup3, voir
## _squash_notes du JSON) + lean (bascule de rotation, réutilise la même
## fenêtre que root_motion — le lean accompagne le même engagement dans
## le coup) + afterimages (traînée, réservée à coup3 pour l'instant).
## `sprite.scale`/`rotation_degrees` sont remis à leur valeur neutre par
## AnimationComposer lui-même quand `anim_data` est vide ou hors fenêtre —
## jamais besoin de les réinitialiser ici en plus.
func _apply_squash_lean_afterimages(anim_data: Dictionary, abs_tick: int) -> void:
	AnimationComposer.apply_squash(_sprite, anim_data.get("squash", []), abs_tick)
	var rm: Dictionary = anim_data.get("root_motion", {})
	AnimationComposer.apply_lean(_sprite, float(anim_data.get("lean_deg", 0.0)), facing,
		int(rm.get("start_tick", 0)), int(rm.get("end_tick", 0)), abs_tick)
	_apply_afterimages(anim_data, abs_tick)


## `afterimages` (data/animation_composer/cendre.json, _afterimages_notes) :
## { count, start_tick, spacing_ticks, opacities } — spawn un fantôme à
## chaque tick start_tick + i*spacing_ticks pour i in [0, count).
func _apply_afterimages(anim_data: Dictionary, abs_tick: int) -> void:
	var ai: Dictionary = anim_data.get("afterimages", {})
	if ai.is_empty():
		return
	var count: int = int(ai.get("count", 0))
	var start_tick: int = int(ai.get("start_tick", 0))
	var spacing: int = maxi(1, int(ai.get("spacing_ticks", 1)))
	var opacities: Array = ai.get("opacities", [])
	for i in count:
		if abs_tick == start_tick + i * spacing:
			var opacity: float = float(opacities[i]) if i < opacities.size() else 0.3
			_spawn_afterimage(opacity)
			return


func _end_combo() -> void:
	# Mandat critique probabiliste : un combo À 3 COUPS (pas 1 ni 2 —
	# `_combo_step` vaut encore sa dernière valeur ici, AVANT la remise à
	# zéro juste en dessous) terminé sans dégât encaissé pendant son
	# exécution ajoute +3%, cumulable, plafonné à 40%. `_combo_hit_free_
	# so_far` est déjà à false si un coup a été subi PENDANT ce combo
	# (take_damage() le pose immédiatement) — rien à vérifier de plus ici.
	if _combo_step == AttackAnimName.size() and _combo_hit_free_so_far:
		_combo_crit_chance_percent = minf(
			_combo_crit_chance_percent + CRIT_STREAK_BONUS_PERCENT, CRIT_STREAK_MAX_CHANCE_PERCENT)
	_combo_step = 0
	_combo_phase = ComboPhase.NONE
	_combo_tick = 0
	_attack_queued = false
	_action_lock = false
	# Garde-fou : squash/lean (J2) devraient déjà être retombés à neutre
	# avant la fin de la timeline (fenêtres toujours closes bien avant
	# RECOVERY_TICKS dans data/animation_composer/cendre.json), mais un
	# oubli de configuration future ne doit jamais laisser le sprite figé
	# étiré/penché en idle.
	_sprite.scale = Vector2.ONE
	_sprite.rotation_degrees = 0.0


## Un seul coup = une seule cible (mandat : "combo léger", pas une
## attaque en zone — ça, c'est le Totem). Réutilise Targeting, déjà
## éprouvé par le Totem/smoke test, plutôt que d'inventer une seconde
## recherche de cible.
func _try_hit() -> void:
	var target: Node = Targeting.nearest_enemy_in_radius(get_tree(), global_position, ATTACK_RANGE_PX)
	if target == null:
		return
	var tier: Dictionary = COMBO_TIER_FEEDBACK[_combo_step - 1]

	# Mandat critique probabiliste : roulé sur CHAQUE coup du combo, quel
	# que soit son tier — un vrai hasard non seedé est voulu ici (c'est
	# le mécanisme lui-même, pas un choix cosmétique dans un chemin de
	# feedback ; Addendum A §A.5 vise les variations cosmétiques sans
	# enjeu, pas les probabilités de gameplay). smoke_test_gameplay.gd
	# force `_combo_crit_chance_percent` à 0.0 pour ses checks existants
	# (jamais de crit qui casserait une assertion de dégâts/hitstop
	# exacts) et à 100.0 pour son propre check dédié — pas de RNG seedé
	# à contrôler pour rester déterministe en test.
	var is_critical: bool = randf() * 100.0 < _combo_crit_chance_percent
	var damage: float = ATTACK_DAMAGE * CRIT_DAMAGE_MULT if is_critical else ATTACK_DAMAGE
	target.take_damage(damage, global_position, tier["recoil_px"])

	# Phase R4 (retour croisé Gemini/ChatGPT, MANDAT SUITE v2) : point
	# d'entrée UNIQUE pour hit-stop (désormais asymétrique cible/
	# attaquant) + shake + camera-punch + SFX, un seul appel au lieu de
	# 4 dispersés. Seuils shake/punch inchangés (tier1/2 restent sans
	# shake ni punch, "light" exclu du punch — cf. smoke test
	# camera_punch_zoom_triggers_on_medium_hit_not_light) : Phase R4
	# unifie le POINT D'APPEL, pas la nuance déjà réglée par tier.
	#
	# Un critique ÉCRASE le tier normal du coup (jamais additionné) : le
	# palier "critical" (au-dessus de "catastrophic", voir
	# combat_feedback.gd) doit rester identifiable en un coup d'œil quel
	# que soit le tier du coup qui a critiqué — un jab léger critique se
	# lit comme LE coup le plus lourd du jeu, pas comme un jab amélioré.
	if is_critical:
		CombatFeedback.register_hit("critical", true, "critical_hit", "critical", facing, true)
		CombatFeedback.trigger_screen_flash(CRIT_SCREEN_FLASH_COLOR, CRIT_SCREEN_FLASH_TICKS)
	else:
		CombatFeedback.register_hit(
			tier["hitstop"], true,
			"light_impact" if tier["hitstop"] == "light" else "heavy_impact",
			tier["shake"], facing,
			tier["hitstop"] != "light" and tier["hitstop"] != "none")

	# impactFlashFrame + recoil sur chaque coup (mandat Phase 1.4). Le
	# recoil est déjà porté par Enemy.take_damage() (§4 : réaction de la
	# cible, jamais une primitive de l'attaquant) — ici on ne pose QUE le
	# flash d'impact, seule primitive qui appartient au coup lui-même.
	VfxDirector.spawn("impactFlashFrame", {
		"seed": 0,
		"origin": target.global_position,
		"lifetime_ticks": 2,
		"overdraw_cost": 12.0,
		# Addendum A §A.1/§A.2 : CONTACT protégée (primaire impactFlashFrame
		# + recul) — ne se sacrifie jamais sous pression de budget.
		"degradable": false,
	})

	# arcSlash sur le coup 2 seulement (mandat : "arc visuel bref sur 2
	# ticks") — trace du geste qui a touché, couche CONTACT protégée au
	# même titre que impactFlashFrame ci-dessus. Bible §3bis (2026-08-27)
	# : couleur du tier appliquée (hue/saturation/value), là où l'appel
	# retombait avant sur la couleur par défaut du script (gris/blanc
	# 0% saturation) faute de paramètre. Restriction coup2 CONSERVÉE
	# volontairement, pas étendue aux 3 coups : la forme "croissant" de
	# arcSlash représente une trajectoire BALAYÉE/courbe (§7.1) — ça
	# correspond au geste montant du genou-uppercut de coup2, mais pas
	# à coup1 (jab, trajectoire droite) ni coup3 (smash overhead,
	# trajectoire verticale droite). Y mettre un croissant courbe
	# mentirait sur la trajectoire réelle du coup et nuirait à la
	# lisibilité de silhouette — exactement ce que le mandat interdit de
	# sacrifier. coup1/coup3 gardent impactStar (radial, neutre sur la
	# trajectoire) comme seule "trace" en plus du flash.
	if tier["arc_slash"]:
		VfxDirector.spawn("arcSlash", {
			"seed": 0,
			"origin": target.global_position,
			"direction": facing,
			"lifetime_ticks": 2,
			"scale_px": 28.0,
			"hue_deg": tier["hue_deg"],
			"saturation_percent": tier["saturation_percent"],
			"value_percent": tier["value_percent"],
			"degradable": false,
		})

	# impactStar sur CHAQUE coup (mandat bible §3bis : "les éclats" du
	# mandat) — silhouette secondaire dentelée qui reste après le flash
	# neutre, teintée à la couleur du tier. Contrairement à arcSlash,
	# c'est une forme radiale qui ne suggère aucune trajectoire
	# particulière : elle convient aux 3 coups sans mentir sur le
	# mouvement, d'où sa présence systématique là où arcSlash est
	# volontairement réservé à coup2 (voir commentaire ci-dessus).
	VfxDirector.spawn("impactStar", {
		"seed": 0,
		"origin": target.global_position,
		"lifetime_ticks": 3,
		"scale_px": 22.0,
		"hue_deg": tier["hue_deg"],
		"saturation_percent": tier["saturation_percent"],
		"value_percent": tier["value_percent"],
		"degradable": false,
	})

	# ribbonTrail sur CHAQUE coup, "ligne de sol" façon Yomi Hustle
	# (bible §3bis, axe 1) — instruction explicite de Milan : essayer
	# d'abord de pousser ribbonTrail avant d'inventer une primitive.
	# sweep_deg réduit à 16° (par défaut 90°, un large swing) pour lire
	# comme une ligne fine directionnelle plutôt qu'un arc large — testé
	# en jeu réel (voir docs/worklog.md, entrée de cette passe) plutôt
	# que deviné. Couleur du tier, ancré au point de contact comme les
	# 2 primitives ci-dessus, brève (3 ticks, même durée qu'impactStar).
	VfxDirector.spawn("ribbonTrail", {
		"seed": 0,
		"origin": target.global_position,
		"direction": facing,
		"lifetime_ticks": 3,
		"scale_px": 36.0,
		"sweep_deg": 16.0,
		"hue_deg": tier["hue_deg"],
		"saturation_percent": tier["saturation_percent"],
		"value_percent": tier["value_percent"],
		"degradable": false,
	})


## Invocation "Gueule Vide" — instancie la créature en avant du joueur
## (facing), démarre son cast (42 ticks, autonome — voir gueule_vide.gd),
## pose le cooldown. N'appelle pas VfxRecipeRegistry directement : c'est
## la créature elle-même qui joue sa recette, ce script ne fait qu'un
## spawn de gameplay, comme Player._try_hit() spawne juste
## impactFlashFrame sans piloter le reste du VFX.
func _cast_gueule_vide() -> void:
	_power1_cooldown_remaining = POWER1_COOLDOWN_TICKS
	var dir := facing
	if dir.length_squared() < 0.0001:
		dir = Vector2.DOWN
	dir = dir.normalized()

	# Geste d'invocation de Cendre lui-même (voir GUEULE_VIDE_GESTURE_TICKS
	# ci-dessus) : PAS d'_action_lock (choix délibéré préservé), seule la
	# lecture du sprite est protégée le temps du geste — flip_h auto-contenu,
	# même discipline que _start_bras_faux()/_start_attack() (art "sud" seul).
	_gueule_vide_gesture_ticks_remaining = GUEULE_VIDE_GESTURE_TICKS
	if facing.x != 0.0:
		_sprite.flip_h = facing.x < 0.0
	_sprite.play("invocation_gueule_vide")

	var creature: Node2D = GueuleVideScene.instantiate()
	creature.global_position = global_position + dir * POWER1_SPAWN_DISTANCE_PX
	get_parent().add_child(creature)
	creature.set_owner_stats(stats)


## Corbeau Pâle (INVOCATEUR, Tier 2/5) — CONTRAIREMENT à Gueule Vide,
## POSE _action_lock (voir le bloc de constantes CORBEAU_PALE_* plus
## haut pour le raisonnement) : Cendre reste engagé dans son geste de cast
## (ANTICIPATION/RELEASE/RECOVERY, même patron que _start_bras_faux())
## pendant que la créature elle-même (instanciée au RELEASE, tick 1) vit
## sa propre timeline séparée et plus longue (corbeau_pale.gd).
func _cast_corbeau_pale() -> void:
	if stats.is_dead() or _action_lock or _corbeau_pale_cooldown_remaining > 0:
		return
	_action_lock = true
	_corbeau_pale_phase = CorbeauPalePhase.ANTICIPATION
	_corbeau_pale_tick = 0
	_corbeau_pale_spawned = false
	if facing.x != 0.0:
		_sprite.flip_h = facing.x < 0.0
	_sprite.play("invocation_corbeau_pale")
	_sprite.pause()
	_sprite.frame = 0


func _advance_corbeau_pale() -> void:
	_corbeau_pale_tick += 1
	velocity = Vector2.ZERO
	match _corbeau_pale_phase:
		CorbeauPalePhase.ANTICIPATION:
			if _corbeau_pale_tick >= CORBEAU_PALE_ANTICIPATION_TICKS:
				_corbeau_pale_phase = CorbeauPalePhase.RELEASE
				_corbeau_pale_tick = 0
		CorbeauPalePhase.RELEASE:
			if _corbeau_pale_tick == 1 and not _corbeau_pale_spawned:
				_spawn_corbeau_pale_creature()
				_corbeau_pale_spawned = true
			if _corbeau_pale_tick >= CORBEAU_PALE_RELEASE_TICKS:
				_corbeau_pale_phase = CorbeauPalePhase.RECOVERY
				_corbeau_pale_tick = 0
		CorbeauPalePhase.RECOVERY:
			if _corbeau_pale_tick >= CORBEAU_PALE_RECOVERY_TICKS - CORBEAU_PALE_CANCEL_WINDOW_TICKS:
				if _try_consume_queued_input(_end_corbeau_pale):
					return
			if _corbeau_pale_tick >= CORBEAU_PALE_RECOVERY_TICKS:
				_end_corbeau_pale()
	if _corbeau_pale_phase != CorbeauPalePhase.NONE:
		_sprite.frame = _corbeau_pale_frame_for_tick(_corbeau_pale_global_tick())


func _end_corbeau_pale() -> void:
	_corbeau_pale_phase = CorbeauPalePhase.NONE
	_corbeau_pale_tick = 0
	_action_lock = false
	_corbeau_pale_cooldown_remaining = CORBEAU_PALE_COOLDOWN_TICKS


func _corbeau_pale_global_tick() -> int:
	match _corbeau_pale_phase:
		CorbeauPalePhase.ANTICIPATION:
			return _corbeau_pale_tick
		CorbeauPalePhase.RELEASE:
			return CORBEAU_PALE_ANTICIPATION_TICKS + _corbeau_pale_tick
		CorbeauPalePhase.RECOVERY:
			return CORBEAU_PALE_ANTICIPATION_TICKS + CORBEAU_PALE_RELEASE_TICKS + _corbeau_pale_tick
		_:
			return 0


func _corbeau_pale_frame_for_tick(tick: int) -> int:
	for i in CORBEAU_PALE_FRAME_TICK_BOUNDS.size():
		if tick <= CORBEAU_PALE_FRAME_TICK_BOUNDS[i]:
			return i
	return CORBEAU_PALE_FRAME_TICK_BOUNDS.size() - 1


func _spawn_corbeau_pale_creature() -> void:
	var dir := facing
	if dir.length_squared() < 0.0001:
		dir = Vector2.DOWN
	dir = dir.normalized()
	var creature: Node2D = CorbeauPaleScene.instantiate()
	creature.travel_direction = dir
	creature.global_position = global_position + dir * CORBEAU_PALE_SPAWN_DISTANCE_PX
	get_parent().add_child(creature)
	creature.set_owner_stats(stats)


## Poing du Colosse (INVOCATEUR, Tier 3/5) — même patron que Corbeau Pâle
## ci-dessus (double timeline). Anticipation/recovery plus longues (geste
## plus lourd, "impact majeur") — voir POING_DU_COLOSSE_* plus haut.
func _cast_poing_du_colosse() -> void:
	if stats.is_dead() or _action_lock or _poing_du_colosse_cooldown_remaining > 0:
		return
	_action_lock = true
	_poing_du_colosse_phase = PoingDuColossePhase.ANTICIPATION
	_poing_du_colosse_tick = 0
	_poing_du_colosse_spawned = false
	if facing.x != 0.0:
		_sprite.flip_h = facing.x < 0.0
	_sprite.play("invocation_poing_du_colosse")
	_sprite.pause()
	_sprite.frame = 0


func _advance_poing_du_colosse() -> void:
	_poing_du_colosse_tick += 1
	velocity = Vector2.ZERO
	match _poing_du_colosse_phase:
		PoingDuColossePhase.ANTICIPATION:
			if _poing_du_colosse_tick >= POING_DU_COLOSSE_ANTICIPATION_TICKS:
				_poing_du_colosse_phase = PoingDuColossePhase.RELEASE
				_poing_du_colosse_tick = 0
		PoingDuColossePhase.RELEASE:
			if _poing_du_colosse_tick == 1 and not _poing_du_colosse_spawned:
				_spawn_poing_du_colosse_creature()
				_poing_du_colosse_spawned = true
			if _poing_du_colosse_tick >= POING_DU_COLOSSE_RELEASE_TICKS:
				_poing_du_colosse_phase = PoingDuColossePhase.RECOVERY
				_poing_du_colosse_tick = 0
		PoingDuColossePhase.RECOVERY:
			if _poing_du_colosse_tick >= POING_DU_COLOSSE_RECOVERY_TICKS - POING_DU_COLOSSE_CANCEL_WINDOW_TICKS:
				if _try_consume_queued_input(_end_poing_du_colosse):
					return
			if _poing_du_colosse_tick >= POING_DU_COLOSSE_RECOVERY_TICKS:
				_end_poing_du_colosse()
	if _poing_du_colosse_phase != PoingDuColossePhase.NONE:
		_sprite.frame = _poing_du_colosse_frame_for_tick(_poing_du_colosse_global_tick())


func _end_poing_du_colosse() -> void:
	_poing_du_colosse_phase = PoingDuColossePhase.NONE
	_poing_du_colosse_tick = 0
	_action_lock = false
	_poing_du_colosse_cooldown_remaining = POING_DU_COLOSSE_COOLDOWN_TICKS


func _poing_du_colosse_global_tick() -> int:
	match _poing_du_colosse_phase:
		PoingDuColossePhase.ANTICIPATION:
			return _poing_du_colosse_tick
		PoingDuColossePhase.RELEASE:
			return POING_DU_COLOSSE_ANTICIPATION_TICKS + _poing_du_colosse_tick
		PoingDuColossePhase.RECOVERY:
			return POING_DU_COLOSSE_ANTICIPATION_TICKS + POING_DU_COLOSSE_RELEASE_TICKS + _poing_du_colosse_tick
		_:
			return 0


func _poing_du_colosse_frame_for_tick(tick: int) -> int:
	for i in POING_DU_COLOSSE_FRAME_TICK_BOUNDS.size():
		if tick <= POING_DU_COLOSSE_FRAME_TICK_BOUNDS[i]:
			return i
	return POING_DU_COLOSSE_FRAME_TICK_BOUNDS.size() - 1


func _spawn_poing_du_colosse_creature() -> void:
	var dir := facing
	if dir.length_squared() < 0.0001:
		dir = Vector2.DOWN
	dir = dir.normalized()
	var creature: Node2D = PoingDuColosseScene.instantiate()
	creature.global_position = global_position + dir * POING_DU_COLOSSE_SPAWN_DISTANCE_PX
	get_parent().add_child(creature)
	creature.set_owner_stats(stats)


## Œil Sans Regard (INVOCATEUR, Tier 4/5) — même patron que Corbeau Pâle/
## Poing du Colosse ci-dessus. La créature (l'œil) flotte "dans les airs"
## (fiche planche) — décalage vertical au spawn, voir OEIL_SANS_REGARD_
## SPAWN_HEIGHT_OFFSET_PX plus haut.
func _cast_oeil_sans_regard() -> void:
	if stats.is_dead() or _action_lock or _oeil_sans_regard_cooldown_remaining > 0:
		return
	_action_lock = true
	_oeil_sans_regard_phase = OeilSansRegardPhase.ANTICIPATION
	_oeil_sans_regard_tick = 0
	_oeil_sans_regard_spawned = false
	if facing.x != 0.0:
		_sprite.flip_h = facing.x < 0.0
	_sprite.play("invocation_oeil_sans_regard")
	_sprite.pause()
	_sprite.frame = 0


func _advance_oeil_sans_regard() -> void:
	_oeil_sans_regard_tick += 1
	velocity = Vector2.ZERO
	match _oeil_sans_regard_phase:
		OeilSansRegardPhase.ANTICIPATION:
			if _oeil_sans_regard_tick >= OEIL_SANS_REGARD_ANTICIPATION_TICKS:
				_oeil_sans_regard_phase = OeilSansRegardPhase.RELEASE
				_oeil_sans_regard_tick = 0
		OeilSansRegardPhase.RELEASE:
			if _oeil_sans_regard_tick == 1 and not _oeil_sans_regard_spawned:
				_spawn_oeil_sans_regard_creature()
				_oeil_sans_regard_spawned = true
			if _oeil_sans_regard_tick >= OEIL_SANS_REGARD_RELEASE_TICKS:
				_oeil_sans_regard_phase = OeilSansRegardPhase.RECOVERY
				_oeil_sans_regard_tick = 0
		OeilSansRegardPhase.RECOVERY:
			if _oeil_sans_regard_tick >= OEIL_SANS_REGARD_RECOVERY_TICKS - OEIL_SANS_REGARD_CANCEL_WINDOW_TICKS:
				if _try_consume_queued_input(_end_oeil_sans_regard):
					return
			if _oeil_sans_regard_tick >= OEIL_SANS_REGARD_RECOVERY_TICKS:
				_end_oeil_sans_regard()
	if _oeil_sans_regard_phase != OeilSansRegardPhase.NONE:
		_sprite.frame = _oeil_sans_regard_frame_for_tick(_oeil_sans_regard_global_tick())


func _end_oeil_sans_regard() -> void:
	_oeil_sans_regard_phase = OeilSansRegardPhase.NONE
	_oeil_sans_regard_tick = 0
	_action_lock = false
	_oeil_sans_regard_cooldown_remaining = OEIL_SANS_REGARD_COOLDOWN_TICKS


func _oeil_sans_regard_global_tick() -> int:
	match _oeil_sans_regard_phase:
		OeilSansRegardPhase.ANTICIPATION:
			return _oeil_sans_regard_tick
		OeilSansRegardPhase.RELEASE:
			return OEIL_SANS_REGARD_ANTICIPATION_TICKS + _oeil_sans_regard_tick
		OeilSansRegardPhase.RECOVERY:
			return OEIL_SANS_REGARD_ANTICIPATION_TICKS + OEIL_SANS_REGARD_RELEASE_TICKS + _oeil_sans_regard_tick
		_:
			return 0


func _oeil_sans_regard_frame_for_tick(tick: int) -> int:
	for i in OEIL_SANS_REGARD_FRAME_TICK_BOUNDS.size():
		if tick <= OEIL_SANS_REGARD_FRAME_TICK_BOUNDS[i]:
			return i
	return OEIL_SANS_REGARD_FRAME_TICK_BOUNDS.size() - 1


func _spawn_oeil_sans_regard_creature() -> void:
	var dir := facing
	if dir.length_squared() < 0.0001:
		dir = Vector2.DOWN
	dir = dir.normalized()
	var creature: Node2D = OeilSansRegardScene.instantiate()
	creature.beam_direction = dir
	creature.global_position = global_position + dir * OEIL_SANS_REGARD_SPAWN_DISTANCE_PX + Vector2(0, OEIL_SANS_REGARD_SPAWN_HEIGHT_OFFSET_PX)
	get_parent().add_child(creature)
	creature.set_owner_stats(stats)


## Serpent Creux (INVOCATEUR, Tier 5/5 — l'ultime) — même patron que les
## 3 précédents. GDD §6.2 : "portée supérieure à Gueule Vide, attaque
## linéaire, plusieurs cibles possibles" — respecté côté portée dans
## serpent_creux.gd (RANGE_PX), pas ici.
func _cast_serpent_creux() -> void:
	if stats.is_dead() or _action_lock or _serpent_creux_cooldown_remaining > 0:
		return
	_action_lock = true
	_serpent_creux_phase = SerpentCreuxPhase.ANTICIPATION
	_serpent_creux_tick = 0
	_serpent_creux_spawned = false
	if facing.x != 0.0:
		_sprite.flip_h = facing.x < 0.0
	_sprite.play("invocation_serpent_creux")
	_sprite.pause()
	_sprite.frame = 0


func _advance_serpent_creux() -> void:
	_serpent_creux_tick += 1
	velocity = Vector2.ZERO
	match _serpent_creux_phase:
		SerpentCreuxPhase.ANTICIPATION:
			if _serpent_creux_tick >= SERPENT_CREUX_ANTICIPATION_TICKS:
				_serpent_creux_phase = SerpentCreuxPhase.RELEASE
				_serpent_creux_tick = 0
		SerpentCreuxPhase.RELEASE:
			if _serpent_creux_tick == 1 and not _serpent_creux_spawned:
				_spawn_serpent_creux_creature()
				_serpent_creux_spawned = true
			if _serpent_creux_tick >= SERPENT_CREUX_RELEASE_TICKS:
				_serpent_creux_phase = SerpentCreuxPhase.RECOVERY
				_serpent_creux_tick = 0
		SerpentCreuxPhase.RECOVERY:
			if _serpent_creux_tick >= SERPENT_CREUX_RECOVERY_TICKS - SERPENT_CREUX_CANCEL_WINDOW_TICKS:
				if _try_consume_queued_input(_end_serpent_creux):
					return
			if _serpent_creux_tick >= SERPENT_CREUX_RECOVERY_TICKS:
				_end_serpent_creux()
	if _serpent_creux_phase != SerpentCreuxPhase.NONE:
		_sprite.frame = _serpent_creux_frame_for_tick(_serpent_creux_global_tick())


func _end_serpent_creux() -> void:
	_serpent_creux_phase = SerpentCreuxPhase.NONE
	_serpent_creux_tick = 0
	_action_lock = false
	_serpent_creux_cooldown_remaining = SERPENT_CREUX_COOLDOWN_TICKS


func _serpent_creux_global_tick() -> int:
	match _serpent_creux_phase:
		SerpentCreuxPhase.ANTICIPATION:
			return _serpent_creux_tick
		SerpentCreuxPhase.RELEASE:
			return SERPENT_CREUX_ANTICIPATION_TICKS + _serpent_creux_tick
		SerpentCreuxPhase.RECOVERY:
			return SERPENT_CREUX_ANTICIPATION_TICKS + SERPENT_CREUX_RELEASE_TICKS + _serpent_creux_tick
		_:
			return 0


func _serpent_creux_frame_for_tick(tick: int) -> int:
	for i in SERPENT_CREUX_FRAME_TICK_BOUNDS.size():
		if tick <= SERPENT_CREUX_FRAME_TICK_BOUNDS[i]:
			return i
	return SERPENT_CREUX_FRAME_TICK_BOUNDS.size() - 1


func _spawn_serpent_creux_creature() -> void:
	var dir := facing
	if dir.length_squared() < 0.0001:
		dir = Vector2.DOWN
	dir = dir.normalized()
	var creature: Node2D = SerpentCreuxScene.instantiate()
	creature.travel_direction = dir
	creature.global_position = global_position + dir * SERPENT_CREUX_SPAWN_DISTANCE_PX
	get_parent().add_child(creature)
	creature.set_owner_stats(stats)


## Bras-Faux (GDD §7.1) — archétype "frappe de zone" : contrairement à
## _cast_gueule_vide() (une entité séparée qui vit sa propre timeline),
## le joueur EST l'exécutant, sur sa propre timeline de ticks (même
## discipline que _start_attack()/play_dash()/play_dodge()). Rejette la
## même façon que ces autres actions verrouillées : mort, déjà engagé
## dans une autre action, ou cooldown.
##
## Art dédié (agent Bras-Faux, 2026-08-22) : anim "bras_faux" propre,
## PAS un réemploi de "coup2" — bras droit réellement transformé en long
## membre organique rouge-brun tendu (create_character_state sur le
## character_id Cendre_v3c EN JEU (8596a4ad, vérifié via git log --
## cendre_frames.tres avant de choisir la source, PAS l'ancien
## character_id avec cape) puis animate_character mode v3 sur cet état,
## 6 frames south, cf. data/pixellab_usage.jsonl). Même discipline
## flip_h auto-contenue que _start_attack() (art "sud" seul, doit se
## flipper lui-même face à l'ouest plutôt que dépendre du dernier
## flip_h laissé par _handle_movement()).
func _start_bras_faux() -> void:
	if stats.is_dead() or _action_lock or _bras_faux_cooldown_remaining > 0:
		return
	_action_lock = true
	_bras_faux_phase = BrasFauxPhase.ANTICIPATION
	_bras_faux_tick = 0
	_bras_faux_hit_applied = false
	if facing.x != 0.0:
		_sprite.flip_h = facing.x < 0.0
	# Tick-exact (voir BRAS_FAUX_FRAME_TICK_BOUNDS ci-dessus) : play()
	# positionne l'AnimatedSprite2D sur "bras_faux", pause() coupe
	# immédiatement sa propre horloge fps pour que seule _advance_
	# bras_faux() décide de la frame affichée, jamais Godot — même
	# discipline que _start_poing_belluaire().
	_sprite.play("bras_faux")
	_sprite.pause()
	_sprite.frame = 0

	var dir := facing
	if dir.length_squared() < 0.0001:
		dir = Vector2.DOWN
	dir = dir.normalized()
	VfxRecipeRegistry.play(BrasFauxRecipeId, {
		"origin": global_position,
		"seed": BRAS_FAUX_CAST_SEED,
		"direction": dir,
	})


## Timeline déclarative (ANTICIPATION -> RELEASE, contact au 1er tick,
## même convention que _advance_combo() -> RECOVERY) — jamais dépendante
## de la durée réelle de lecture du sprite. Correction "polish complet"
## (2026-08-23) : le pilotage de la frame affichée est maintenant
## tick-exact (BRAS_FAUX_FRAME_TICK_BOUNDS, voir audit ci-dessus),
## PAS la fps autonome d'AnimatedSprite2D qui gelait la pose ~10 ticks
## avant la fin réelle du cast et ne garantissait aucun alignement entre
## le "snap" de pose et le tick de contact.
func _advance_bras_faux() -> void:
	_bras_faux_tick += 1
	velocity = Vector2.ZERO  # "aucun déplacement automatique" (GDD §7.1) — jamais de root motion ici.
	match _bras_faux_phase:
		BrasFauxPhase.ANTICIPATION:
			if _bras_faux_tick >= BRAS_FAUX_ANTICIPATION_TICKS:
				_bras_faux_phase = BrasFauxPhase.RELEASE
				_bras_faux_tick = 0
		BrasFauxPhase.RELEASE:
			if _bras_faux_tick == 1 and not _bras_faux_hit_applied:
				_try_hit_bras_faux()
				_bras_faux_hit_applied = true
			if _bras_faux_tick >= BRAS_FAUX_RELEASE_TICKS:
				_bras_faux_phase = BrasFauxPhase.RECOVERY
				_bras_faux_tick = 0
		BrasFauxPhase.RECOVERY:
			# Fenêtre d'annulation (BRAS_FAUX_CANCEL_WINDOW_TICKS) : dès
			# qu'elle est ouverte, un input déjà en file (attack ou un
			# autre slot de pouvoir) termine Bras-Faux tôt et démarre
			# l'action suivante SANS attendre la fin de RECOVERY — voir
			# _try_consume_queued_input().
			if _bras_faux_tick >= BRAS_FAUX_RECOVERY_TICKS - BRAS_FAUX_CANCEL_WINDOW_TICKS:
				if _try_consume_queued_input(_end_bras_faux):
					return
			if _bras_faux_tick >= BRAS_FAUX_RECOVERY_TICKS:
				_end_bras_faux()
	# Tick-exact (voir BRAS_FAUX_FRAME_TICK_BOUNDS) : appliqué APRÈS la
	# transition de phase éventuelle ci-dessus, pour que la frame reflète
	# l'état réel de CE tick (ex. RELEASE tick1 = contact -> frame 3 dès
	# ce même appel, pas un tick de retard) — même discipline que
	# _advance_poing_belluaire(). Rien à faire si le cast vient de se
	# terminer (_end_bras_faux() a remis NONE) : _handle_movement()
	# reprend la main sur _sprite au tick suivant.
	if _bras_faux_phase != BrasFauxPhase.NONE:
		_sprite.frame = _bras_faux_frame_for_tick(_bras_faux_global_tick())


func _end_bras_faux() -> void:
	_bras_faux_phase = BrasFauxPhase.NONE
	_bras_faux_tick = 0
	_action_lock = false
	_bras_faux_cooldown_remaining = BRAS_FAUX_COOLDOWN_TICKS


## Tick unique cumulé depuis le début du cast (ANTICIPATION puis RELEASE
## puis RECOVERY mis bout à bout) — même rôle que GueuleVide._tick /
## Player._poing_belluaire_global_tick(), recalculé à partir des
## compteurs par-phase existants plutôt que dupliqué en un 3e compteur.
func _bras_faux_global_tick() -> int:
	match _bras_faux_phase:
		BrasFauxPhase.ANTICIPATION:
			return _bras_faux_tick
		BrasFauxPhase.RELEASE:
			return BRAS_FAUX_ANTICIPATION_TICKS + _bras_faux_tick
		BrasFauxPhase.RECOVERY:
			return BRAS_FAUX_ANTICIPATION_TICKS + BRAS_FAUX_RELEASE_TICKS + _bras_faux_tick
		_:
			return 0


## Même schéma que GueuleVide._frame_for_tick() / Player._poing_belluaire_frame_for_tick().
func _bras_faux_frame_for_tick(tick: int) -> int:
	for i in BRAS_FAUX_FRAME_TICK_BOUNDS.size():
		if tick <= BRAS_FAUX_FRAME_TICK_BOUNDS[i]:
			return i
	return BRAS_FAUX_FRAME_TICK_BOUNDS.size() - 1


## "Frappe de zone" : TOUS les ennemis vivants dans l'arc, pas un seul
## (Targeting.enemies_in_arc(), pas nearest_enemy_in_radius()) — la
## distinction qui fait l'identité de cet archétype face au combo/Gueule
## Vide (une seule cible chacun). Recul individuel sur CHAQUE cible
## touchée (GDD §7.1 : "chaque coup qui touche impose un recul visible"),
## via Enemy.take_damage() comme pour le combo — jamais une primitive de
## la recette (data/recipes/power.bras_faux.cast.json, notes).
func _try_hit_bras_faux() -> void:
	var dir := facing
	if dir.length_squared() < 0.0001:
		dir = Vector2.DOWN
	dir = dir.normalized()
	var targets: Array = Targeting.enemies_in_arc(get_tree(), global_position, dir, BRAS_FAUX_RANGE_PX, BRAS_FAUX_HALF_ANGLE_DEG)
	if targets.is_empty():
		return
	for target in targets:
		target.take_damage(BRAS_FAUX_DAMAGE, global_position)

	# Même tier que Gueule Vide (tous deux importance_tier 2/6, feedback
	# "medium" dans les deux recettes) — pas un second barème de hit-stop.
	# Phase R4 : shake "light" ajouté (absent jusqu'ici sur TOUS les
	# pouvoirs du joueur, trou confirmé par audit — seul le combo tier3
	# en avait un) + point d'entrée unique register_hit().
	CombatFeedback.register_hit("medium", true, "heavy_impact", "light", dir, true)


## Poing Belluaire — même construction que _start_bras_faux() ci-dessus.
##
## Art dédié (agent Poing Belluaire, 2026-08-22) : anim "poing_belluaire"
## propre, PAS un réemploi de "coup3" — bras+poing droit réellement
## transformés en une seule masse ronde/compacte de muscle et chair
## enflée (create_character_state sur le character_id Cendre_v3c EN JEU
## (8596a4ad, vérifié via get_character AVANT l'appel — même piège que
## Bras-Faux avec e08932a2, évité ici en amont) puis animate_character
## mode v3 sur cet état, 6 frames sud, cf. data/pixellab_usage.jsonl).
## Silhouette délibérément large/ronde, à l'opposé de la silhouette
## longue/fine de Bras-Faux — les deux ne doivent jamais être confondues
## à l'écran. Même discipline flip_h auto-contenue que _start_bras_faux()/
## _start_attack() (art "sud" seul).
func _start_poing_belluaire() -> void:
	if stats.is_dead() or _action_lock or _poing_belluaire_cooldown_remaining > 0:
		return
	_action_lock = true
	_poing_belluaire_phase = PoingBelluairePhase.ANTICIPATION
	_poing_belluaire_tick = 0
	_poing_belluaire_hit_applied = false
	if facing.x != 0.0:
		_sprite.flip_h = facing.x < 0.0
	# Tick-exact (voir POING_BELLUAIRE_FRAME_TICK_BOUNDS ci-dessus) : play()
	# positionne l'AnimatedSprite2D sur "poing_belluaire", pause() coupe
	# immédiatement sa propre horloge fps pour que seule _advance_
	# poing_belluaire() décide de la frame affichée, jamais Godot.
	_sprite.play("poing_belluaire")
	_sprite.pause()
	_sprite.frame = 0

	var dir := facing
	if dir.length_squared() < 0.0001:
		dir = Vector2.DOWN
	dir = dir.normalized()
	VfxRecipeRegistry.play(PoingBelluaireRecipeId, {
		"origin": global_position,
		"seed": POING_BELLUAIRE_CAST_SEED,
		"direction": dir,
	})


func _advance_poing_belluaire() -> void:
	_poing_belluaire_tick += 1
	velocity = Vector2.ZERO  # aucun déplacement automatique (GDD : "un seul coup frontal").
	match _poing_belluaire_phase:
		PoingBelluairePhase.ANTICIPATION:
			if _poing_belluaire_tick >= POING_BELLUAIRE_ANTICIPATION_TICKS:
				_poing_belluaire_phase = PoingBelluairePhase.RELEASE
				_poing_belluaire_tick = 0
		PoingBelluairePhase.RELEASE:
			if _poing_belluaire_tick == 1 and not _poing_belluaire_hit_applied:
				_try_hit_poing_belluaire()
				_poing_belluaire_hit_applied = true
			if _poing_belluaire_tick >= POING_BELLUAIRE_RELEASE_TICKS:
				_poing_belluaire_phase = PoingBelluairePhase.RECOVERY
				_poing_belluaire_tick = 0
		PoingBelluairePhase.RECOVERY:
			# Fenêtre d'annulation (POING_BELLUAIRE_CANCEL_WINDOW_TICKS) —
			# même patron que Bras-Faux ci-dessus.
			if _poing_belluaire_tick >= POING_BELLUAIRE_RECOVERY_TICKS - POING_BELLUAIRE_CANCEL_WINDOW_TICKS:
				if _try_consume_queued_input(_end_poing_belluaire):
					return
			if _poing_belluaire_tick >= POING_BELLUAIRE_RECOVERY_TICKS:
				_end_poing_belluaire()
	# Tick-exact (voir POING_BELLUAIRE_FRAME_TICK_BOUNDS) : appliqué APRÈS
	# la transition de phase éventuelle ci-dessus, pour que la frame
	# reflète l'état réel de CE tick (ex. RELEASE tick1 = contact -> frame
	# 5 dès ce même appel, pas un tick de retard). Rien à faire si le cast
	# vient de se terminer (_end_poing_belluaire() a remis NONE) :
	# _handle_movement() reprend la main sur _sprite au tick suivant.
	if _poing_belluaire_phase != PoingBelluairePhase.NONE:
		_sprite.frame = _poing_belluaire_frame_for_tick(_poing_belluaire_global_tick())


## Tick unique cumulé depuis le début du cast (ANTICIPATION puis RELEASE
## puis RECOVERY mis bout à bout) — même rôle que GueuleVide._tick, mais
## recalculé à partir des compteurs par-phase existants plutôt que
## dupliqué en un 3e compteur.
func _poing_belluaire_global_tick() -> int:
	match _poing_belluaire_phase:
		PoingBelluairePhase.ANTICIPATION:
			return _poing_belluaire_tick
		PoingBelluairePhase.RELEASE:
			return POING_BELLUAIRE_ANTICIPATION_TICKS + _poing_belluaire_tick
		PoingBelluairePhase.RECOVERY:
			return POING_BELLUAIRE_ANTICIPATION_TICKS + POING_BELLUAIRE_RELEASE_TICKS + _poing_belluaire_tick
		_:
			return 0


## Même schéma que GueuleVide._frame_for_tick().
func _poing_belluaire_frame_for_tick(tick: int) -> int:
	for i in POING_BELLUAIRE_FRAME_TICK_BOUNDS.size():
		if tick <= POING_BELLUAIRE_FRAME_TICK_BOUNDS[i]:
			return i
	return POING_BELLUAIRE_FRAME_TICK_BOUNDS.size() - 1


func _end_poing_belluaire() -> void:
	_poing_belluaire_phase = PoingBelluairePhase.NONE
	_poing_belluaire_tick = 0
	_action_lock = false
	_poing_belluaire_cooldown_remaining = POING_BELLUAIRE_COOLDOWN_TICKS


## "peut interrompre les attaques faibles" (GDD) : couvert par le recul
## imposé à la cible (Enemy.take_damage()), pas une mécanique séparée
## d'interruption d'attaque adverse (aucun ennemi actuel n'a d'anticipation
## interruptible dans son propre code — inventer ce système serait hors
## scope de cette brique).
func _try_hit_poing_belluaire() -> void:
	var dir := facing
	if dir.length_squared() < 0.0001:
		dir = Vector2.DOWN
	dir = dir.normalized()
	var targets: Array = Targeting.enemies_in_arc(get_tree(), global_position, dir, POING_BELLUAIRE_RANGE_PX, POING_BELLUAIRE_HALF_ANGLE_DEG)
	if targets.is_empty():
		return
	for target in targets:
		target.take_damage(POING_BELLUAIRE_DAMAGE, global_position, POING_BELLUAIRE_RECOIL_PX, POING_BELLUAIRE_RECOIL_TICKS)

	# Phase R4 : shake "medium" ajouté (trou confirmé par audit, cohérent
	# avec le hit-stop "heavy" — "impact lourd" GDD) + point d'entrée
	# unique register_hit().
	CombatFeedback.register_hit("heavy", true, "heavy_impact", "medium", dir, true)


## Poing Tellurique — même construction que Bras-Faux/Poing Belluaire.
##
## Art dédié (agent Poing Tellurique, mandat "polish complet", 2026-08-23) :
## anim "poing_tellurique" propre, PAS un réemploi de "coup1" — écart
## confirmé (capture avant correctif : "coup1" est le 1er coup du combo à
## mains nues, un jab horizontal, aucun geste vers le sol, contrairement à
## la planche docs/references/terre/poing_tellurique.png qui montre un coup
## qui frappe littéralement le sol). Pipeline : character_id Cendre_v3c EN
## JEU (8596a4ad, vérifié via get_character AVANT l'appel — même piège que
## Bras-Faux/Poing Belluaire, évité en amont), animate_character mode v3
## DIRECTEMENT sur l'état de base (PAS de create_character_state : contrairement
## à Bras-Faux/Poing Belluaire, Poing Tellurique ne transforme aucun membre,
## c'est une POSE — même construction que coup1/coup2/coup3/dash/mort,
## toutes générées directement sur l'état "Idle" de ce personnage), 6 frames
## sud (accepté dès le 1er essai, aucun re-roll nécessaire : silhouette nette,
## aucune arme/lueur/traînée halluciné, cf. data/pixellab_usage.jsonl).
## Facteur d'échelle 53/78 mesuré sur frame0 (pose la plus proche d'un
## repos neutre) contre idle_south cuit (même bug de classe que le facteur
## bras_faux 51/79 — canvas animate_character v3 custom rendu à une échelle
## globale différente du canvas partagé, jamais un problème de pose).
## Même discipline flip_h auto-contenue que Bras-Faux/Poing Belluaire.
func _start_poing_tellurique() -> void:
	if stats.is_dead() or _action_lock or _poing_tellurique_cooldown_remaining > 0:
		return
	_action_lock = true
	_poing_tellurique_phase = PoingTelluriquePhase.ANTICIPATION
	_poing_tellurique_tick = 0
	_poing_tellurique_hit_applied = false
	if facing.x != 0.0:
		_sprite.flip_h = facing.x < 0.0
	# Tick-exact (voir POING_TELLURIQUE_FRAME_TICK_BOUNDS ci-dessus) : play()
	# positionne l'AnimatedSprite2D sur "poing_tellurique", pause() coupe
	# immédiatement sa propre horloge fps pour que seule _advance_
	# poing_tellurique() décide de la frame affichée, jamais Godot — même
	# discipline que _start_bras_faux()/_start_poing_belluaire().
	_sprite.play("poing_tellurique")
	_sprite.pause()
	_sprite.frame = 0

	var dir := facing
	if dir.length_squared() < 0.0001:
		dir = Vector2.DOWN
	dir = dir.normalized()
	# dustKick (data/recipes/power.poing_tellurique.cast.json) interprète
	# `direction` comme "le sens du DÉPLACEMENT qui cause le contact" et
	# projette ses éclats à l'opposé (dust_kick.gd : "la poussière part à
	# l'opposé, jamais dans le sens du mouvement") — pertinent pour un pas/
	# dash qui laisse de la poussière DERRIÈRE lui, mais un impact de poing
	# doit au contraire projeter ses éclats DEVANT, dans le sens du coup
	# (facing). Seule cette couche lit `direction` dans cette recette
	# (groundRing/converge/impactFlashFrame l'ignorent, vérifié dans leurs
	# configure()) : inverser `dir` ici est donc sans risque pour les 3
	# autres couches et corrige la lecture pour dustKick.
	VfxRecipeRegistry.play(PoingTelluriqueRecipeId, {
		"origin": global_position,
		"seed": POING_TELLURIQUE_CAST_SEED,
		"direction": -dir,
	})


## Timeline déclarative (ANTICIPATION -> RELEASE, contact au 1er tick,
## même convention que les autres pouvoirs de mêlée) — jamais dépendante de
## la durée réelle de lecture du sprite. Pilotage de la frame affichée
## tick-exact (POING_TELLURIQUE_FRAME_TICK_BOUNDS, voir doc ci-dessus),
## même discipline que _advance_bras_faux()/_advance_poing_belluaire().
func _advance_poing_tellurique() -> void:
	_poing_tellurique_tick += 1
	velocity = Vector2.ZERO  # aucun déplacement automatique (GDD ne mentionne aucun bond, contrairement à Pattes de Chasse).
	match _poing_tellurique_phase:
		PoingTelluriquePhase.ANTICIPATION:
			if _poing_tellurique_tick >= POING_TELLURIQUE_ANTICIPATION_TICKS:
				_poing_tellurique_phase = PoingTelluriquePhase.RELEASE
				_poing_tellurique_tick = 0
		PoingTelluriquePhase.RELEASE:
			if _poing_tellurique_tick == 1 and not _poing_tellurique_hit_applied:
				_try_hit_poing_tellurique()
				_poing_tellurique_hit_applied = true
			if _poing_tellurique_tick >= POING_TELLURIQUE_RELEASE_TICKS:
				_poing_tellurique_phase = PoingTelluriquePhase.RECOVERY
				_poing_tellurique_tick = 0
		PoingTelluriquePhase.RECOVERY:
			# Fenêtre d'annulation (POING_TELLURIQUE_CANCEL_WINDOW_TICKS) —
			# même patron que Bras-Faux ci-dessus.
			if _poing_tellurique_tick >= POING_TELLURIQUE_RECOVERY_TICKS - POING_TELLURIQUE_CANCEL_WINDOW_TICKS:
				if _try_consume_queued_input(_end_poing_tellurique):
					return
			if _poing_tellurique_tick >= POING_TELLURIQUE_RECOVERY_TICKS:
				_end_poing_tellurique()
	# Tick-exact (voir POING_TELLURIQUE_FRAME_TICK_BOUNDS) : appliqué APRÈS
	# la transition de phase éventuelle ci-dessus, pour que la frame reflète
	# l'état réel de CE tick (RELEASE tick1 = contact -> frame 4 dès ce même
	# appel, pas un tick de retard). Rien à faire si le cast vient de se
	# terminer (_end_poing_tellurique() a remis NONE) : _handle_movement()
	# reprend la main sur _sprite au tick suivant.
	if _poing_tellurique_phase != PoingTelluriquePhase.NONE:
		_sprite.frame = _poing_tellurique_frame_for_tick(_poing_tellurique_global_tick())


## Tick unique cumulé depuis le début du cast (ANTICIPATION puis RELEASE
## puis RECOVERY mis bout à bout) — même rôle que Player._bras_faux_global_tick()
## / Player._poing_belluaire_global_tick(), recalculé à partir des compteurs
## par-phase existants plutôt que dupliqué en un 3e compteur.
func _poing_tellurique_global_tick() -> int:
	match _poing_tellurique_phase:
		PoingTelluriquePhase.ANTICIPATION:
			return _poing_tellurique_tick
		PoingTelluriquePhase.RELEASE:
			return POING_TELLURIQUE_ANTICIPATION_TICKS + _poing_tellurique_tick
		PoingTelluriquePhase.RECOVERY:
			return POING_TELLURIQUE_ANTICIPATION_TICKS + POING_TELLURIQUE_RELEASE_TICKS + _poing_tellurique_tick
		_:
			return 0


## Même schéma que Player._bras_faux_frame_for_tick() / Player._poing_belluaire_frame_for_tick().
func _poing_tellurique_frame_for_tick(tick: int) -> int:
	for i in POING_TELLURIQUE_FRAME_TICK_BOUNDS.size():
		if tick <= POING_TELLURIQUE_FRAME_TICK_BOUNDS[i]:
			return i
	return POING_TELLURIQUE_FRAME_TICK_BOUNDS.size() - 1


func _end_poing_tellurique() -> void:
	_poing_tellurique_phase = PoingTelluriquePhase.NONE
	_poing_tellurique_tick = 0
	_action_lock = false
	_poing_tellurique_cooldown_remaining = POING_TELLURIQUE_COOLDOWN_TICKS


func _try_hit_poing_tellurique() -> void:
	var dir := facing
	if dir.length_squared() < 0.0001:
		dir = Vector2.DOWN
	dir = dir.normalized()
	var targets: Array = Targeting.enemies_in_arc(get_tree(), global_position, dir, POING_TELLURIQUE_RANGE_PX, POING_TELLURIQUE_HALF_ANGLE_DEG)
	if targets.is_empty():
		return
	for target in targets:
		target.take_damage(POING_TELLURIQUE_DAMAGE, global_position)

	# Phase R4 : shake "light" ajouté (trou confirmé par audit) + point
	# d'entrée unique register_hit().
	CombatFeedback.register_hit("medium", true, "heavy_impact", "light", dir, true)


## Marée de Sable — même construction que Poing Tellurique (3 phases,
## aucun déplacement automatique). Art dédié "maree_de_sable" (voir
## MAREE_DE_SABLE_FRAME_TICK_BOUNDS ci-dessus pour le pipeline complet) —
## remplace l'ancien placeholder "coup1".
func _start_maree_de_sable() -> void:
	if stats.is_dead() or _action_lock or _maree_de_sable_cooldown_remaining > 0:
		return
	_action_lock = true
	_maree_de_sable_phase = MareeDeSablePhase.ANTICIPATION
	_maree_de_sable_tick = 0
	_maree_de_sable_hit_applied = false
	if facing.x != 0.0:
		_sprite.flip_h = facing.x < 0.0
	# Tick-exact (voir MAREE_DE_SABLE_FRAME_TICK_BOUNDS ci-dessus) : play()
	# positionne l'AnimatedSprite2D sur "maree_de_sable", pause() coupe
	# immédiatement sa propre horloge fps pour que seule _advance_
	# maree_de_sable() décide de la frame affichée, jamais Godot — même
	# discipline que _start_bras_faux()/_start_poing_belluaire()/
	# _start_poing_tellurique().
	_sprite.play("maree_de_sable")
	_sprite.pause()
	_sprite.frame = 0

	var dir := facing
	if dir.length_squared() < 0.0001:
		dir = Vector2.DOWN
	dir = dir.normalized()
	VfxRecipeRegistry.play(MareeDeSableRecipeId, {
		"origin": global_position,
		"seed": MAREE_DE_SABLE_CAST_SEED,
		"direction": dir,
	})


func _advance_maree_de_sable() -> void:
	_maree_de_sable_tick += 1
	velocity = Vector2.ZERO
	match _maree_de_sable_phase:
		MareeDeSablePhase.ANTICIPATION:
			if _maree_de_sable_tick >= MAREE_DE_SABLE_ANTICIPATION_TICKS:
				_maree_de_sable_phase = MareeDeSablePhase.RELEASE
				_maree_de_sable_tick = 0
		MareeDeSablePhase.RELEASE:
			if _maree_de_sable_tick == 1 and not _maree_de_sable_hit_applied:
				_try_hit_maree_de_sable()
				_maree_de_sable_hit_applied = true
			if _maree_de_sable_tick >= MAREE_DE_SABLE_RELEASE_TICKS:
				_maree_de_sable_phase = MareeDeSablePhase.RECOVERY
				_maree_de_sable_tick = 0
		MareeDeSablePhase.RECOVERY:
			# Fenêtre d'annulation (MAREE_DE_SABLE_CANCEL_WINDOW_TICKS) —
			# même patron que Bras-Faux ci-dessus.
			if _maree_de_sable_tick >= MAREE_DE_SABLE_RECOVERY_TICKS - MAREE_DE_SABLE_CANCEL_WINDOW_TICKS:
				if _try_consume_queued_input(_end_maree_de_sable):
					return
			if _maree_de_sable_tick >= MAREE_DE_SABLE_RECOVERY_TICKS:
				_end_maree_de_sable()
	# Tick-exact (voir MAREE_DE_SABLE_FRAME_TICK_BOUNDS) : appliqué APRÈS la
	# transition de phase éventuelle ci-dessus, pour que la frame reflète
	# l'état réel de CE tick (RELEASE tick1 = contact -> frame 3 dès ce même
	# appel, pas un tick de retard). Rien à faire si le cast vient de se
	# terminer (_end_maree_de_sable() a remis NONE) : _handle_movement()
	# reprend la main sur _sprite au tick suivant.
	if _maree_de_sable_phase != MareeDeSablePhase.NONE:
		_sprite.frame = _maree_de_sable_frame_for_tick(_maree_de_sable_global_tick())


## Tick unique cumulé depuis le début du cast (ANTICIPATION puis RELEASE
## puis RECOVERY mis bout à bout) — même rôle que Player._poing_belluaire_
## global_tick()/_poing_tellurique_global_tick(), recalculé à partir des
## compteurs par-phase existants plutôt que dupliqué en un 3e compteur.
func _maree_de_sable_global_tick() -> int:
	match _maree_de_sable_phase:
		MareeDeSablePhase.ANTICIPATION:
			return _maree_de_sable_tick
		MareeDeSablePhase.RELEASE:
			return MAREE_DE_SABLE_ANTICIPATION_TICKS + _maree_de_sable_tick
		MareeDeSablePhase.RECOVERY:
			return MAREE_DE_SABLE_ANTICIPATION_TICKS + MAREE_DE_SABLE_RELEASE_TICKS + _maree_de_sable_tick
		_:
			return 0


## Même schéma que Player._poing_belluaire_frame_for_tick()/_poing_tellurique_frame_for_tick().
func _maree_de_sable_frame_for_tick(tick: int) -> int:
	for i in MAREE_DE_SABLE_FRAME_TICK_BOUNDS.size():
		if tick <= MAREE_DE_SABLE_FRAME_TICK_BOUNDS[i]:
			return i
	return MAREE_DE_SABLE_FRAME_TICK_BOUNDS.size() - 1


func _end_maree_de_sable() -> void:
	_maree_de_sable_phase = MareeDeSablePhase.NONE
	_maree_de_sable_tick = 0
	_action_lock = false
	_maree_de_sable_cooldown_remaining = MAREE_DE_SABLE_COOLDOWN_TICKS


## Ligne devant le joueur (Targeting.enemies_in_line(), pas un cône —
## une vague garde une largeur constante sur toute sa portée, contrairement
## à un arc de mêlée) : dégâts + ralentissement (apply_slow(), Enemy.gd)
## sur TOUS les ennemis touchés, "entravant" de la fiche.
func _try_hit_maree_de_sable() -> void:
	var dir := facing
	if dir.length_squared() < 0.0001:
		dir = Vector2.DOWN
	dir = dir.normalized()
	var targets: Array = Targeting.enemies_in_line(get_tree(), global_position, dir, MAREE_DE_SABLE_RANGE_PX, MAREE_DE_SABLE_HALF_WIDTH_PX)
	if targets.is_empty():
		return
	for target in targets:
		target.take_damage(MAREE_DE_SABLE_DAMAGE, global_position)
		if target.has_method("apply_slow"):
			target.apply_slow(MAREE_DE_SABLE_SLOW_MULTIPLIER, MAREE_DE_SABLE_SLOW_DURATION_TICKS)

	CombatFeedback.register_hit("medium", true, "heavy_impact", "light", dir, true)


## Carapace (Terre, Tier 3, DÉFENSIF) — voir le bloc de constantes CARAPACE_*
## et power.carapace.cast.json pour le raisonnement complet (état soutenu,
## PAS un impact ponctuel : 3 phases ACTIVATION/ACTIVE/RECOVERY, aucune
## fonction _try_hit_carapace() — Carapace ne touche jamais un ennemi).
func _start_carapace() -> void:
	if stats.is_dead() or _action_lock or _carapace_cooldown_remaining > 0:
		return
	_action_lock = true
	_carapace_phase = CarapacePhase.ACTIVATION
	_carapace_tick = 0
	_carapace_active_loop_tick = 0
	velocity = Vector2.ZERO  # "aucun déplacement automatique" — voir CARAPACE_* ci-dessus (VFX orbital ancré à une origine fixe).
	if facing.x != 0.0:
		_sprite.flip_h = facing.x < 0.0
	# Tick-exact (voir CARAPACE_ACTIVATION_FRAME_TICK_BOUNDS) : play()
	# positionne l'AnimatedSprite2D sur "carapace_activation", pause() coupe
	# immédiatement sa propre horloge fps, même discipline que tous les
	# autres pouvoirs à sprite dédié de ce fichier.
	_sprite.play("carapace_activation")
	_sprite.pause()
	_sprite.frame = 0

	VfxRecipeRegistry.play(CarapaceRecipeId, {
		"origin": global_position,
		"seed": CARAPACE_CAST_SEED,
		"direction": facing,
	})


## Timeline à 3 phases (ACTIVATION -> ACTIVE -> RECOVERY, voir CarapacePhase)
## — PAS ANTICIPATION/RELEASE/RECOVERY : il n'y a pas de "release"/contact,
## seulement une transition vers un état soutenu puis un retour. La bascule
## de sprite ("carapace_activation" -> "carapace_active" en boucle ->
## "carapace_fin") se fait aux DEUX changements de phase, jamais au milieu.
func _advance_carapace() -> void:
	_carapace_tick += 1

	match _carapace_phase:
		CarapacePhase.ACTIVATION:
			if _carapace_tick >= CARAPACE_ACTIVATION_TICKS:
				_carapace_phase = CarapacePhase.ACTIVE
				_carapace_tick = 0
				_carapace_active_loop_tick = 0
				_sprite.play("carapace_active")
				_sprite.pause()
				_sprite.frame = 0
		CarapacePhase.ACTIVE:
			_carapace_active_loop_tick += 1
			if _carapace_tick >= CARAPACE_ACTIVE_TICKS:
				_carapace_phase = CarapacePhase.RECOVERY
				_carapace_tick = 0
				_sprite.play("carapace_fin")
				_sprite.pause()
				_sprite.frame = 0
		CarapacePhase.RECOVERY:
			# Fenêtre d'annulation (CARAPACE_CANCEL_WINDOW_TICKS) — SEULE
			# fenêtre de tout le cast, voir la constante ci-dessus pour la
			# raison (ACTIVATION/ACTIVE n'en ont délibérément pas).
			if _carapace_tick >= CARAPACE_RECOVERY_TICKS - CARAPACE_CANCEL_WINDOW_TICKS:
				if _try_consume_queued_input(_end_carapace):
					return
			if _carapace_tick >= CARAPACE_RECOVERY_TICKS:
				_end_carapace()

	# Appliqué APRÈS la transition de phase éventuelle ci-dessus, même
	# discipline que _advance_poing_tellurique()/_advance_maree_de_sable() :
	# la frame reflète l'état réel de CE tick, jamais un tick de retard.
	match _carapace_phase:
		CarapacePhase.ACTIVATION:
			_sprite.frame = _carapace_frame_for_tick(_carapace_tick, CARAPACE_ACTIVATION_FRAME_TICK_BOUNDS)
		CarapacePhase.ACTIVE:
			# Boucle continue (voir CARAPACE_ACTIVE_LOOP_FRAME_TICKS/_COUNT ci-
			# dessus) — jamais la fps autonome d'AnimatedSprite2D, et jamais un
			# tick "global" cumulé depuis le cast (la boucle n'a pas de fin
			# naturelle avant CARAPACE_ACTIVE_TICKS, contrairement aux autres
			# compétences qui jouent une séquence linéaire une seule fois).
			_sprite.frame = (_carapace_active_loop_tick / CARAPACE_ACTIVE_LOOP_FRAME_TICKS) % CARAPACE_ACTIVE_LOOP_FRAME_COUNT
		CarapacePhase.RECOVERY:
			_sprite.frame = _carapace_frame_for_tick(_carapace_tick, CARAPACE_RECOVERY_FRAME_TICK_BOUNDS)


## Générique (contrairement aux autres compétences Terre) car ACTIVATION et
## RECOVERY partagent la MÊME table de bornes (CARAPACE_ACTIVATION_FRAME_
## TICK_BOUNDS == CARAPACE_RECOVERY_FRAME_TICK_BOUNDS, symétrie délibérée —
## "carapace_fin" est déjà les frames de "carapace_activation" en ordre
## inverse, donc la MÊME cadence d'affichage produit la transition miroir).
func _carapace_frame_for_tick(tick: int, bounds: Array[int]) -> int:
	for i in bounds.size():
		if tick <= bounds[i]:
			return i
	return bounds.size() - 1


func _end_carapace() -> void:
	_carapace_phase = CarapacePhase.NONE
	_carapace_tick = 0
	_carapace_active_loop_tick = 0
	_action_lock = false
	_carapace_cooldown_remaining = CARAPACE_COOLDOWN_TICKS


## Lu par Player.take_damage() (CARAPACE_DAMAGE_MULTIPLIER) — vrai dès le
## début de l'ACTIVATION (l'armure qui se forme compte déjà comme une
## protection en cours d'installation, pas seulement une fois complète) et
## jusqu'à la fin de la RECOVERY (les plaques encore visibles en train de
## se détacher protègent encore un peu), jamais après _end_carapace().
func is_carapace_active() -> bool:
	return _carapace_phase != CarapacePhase.NONE


func get_carapace_cooldown_ratio() -> float:
	return float(_carapace_cooldown_remaining) / float(CARAPACE_COOLDOWN_TICKS)


## Effondrement (Terre, Tier 4, ZONE, IMPACT MAJEUR) — même discipline
## ANTICIPATION/RELEASE/RECOVERY que Bras-Faux/Poing Belluaire/Poing
## Tellurique/Marée de Sable, voir le bloc de constantes EFFONDREMENT_* et
## power.effondrement.cast.json pour le raisonnement complet.
func _start_effondrement() -> void:
	if stats.is_dead() or _action_lock or _effondrement_cooldown_remaining > 0:
		return
	_action_lock = true
	_effondrement_phase = EffondrementPhase.ANTICIPATION
	_effondrement_tick = 0
	_effondrement_hit_applied = false
	velocity = Vector2.ZERO  # aucun déplacement automatique (GDD ne mentionne aucun bond).
	if facing.x != 0.0:
		_sprite.flip_h = facing.x < 0.0
	_sprite.play("effondrement")
	_sprite.pause()
	_sprite.frame = 0

	var dir := facing
	if dir.length_squared() < 0.0001:
		dir = Vector2.DOWN
	dir = dir.normalized()
	VfxRecipeRegistry.play(EffondrementRecipeId, {
		"origin": global_position,
		"seed": EFFONDREMENT_CAST_SEED,
		"direction": dir,
	})


func _advance_effondrement() -> void:
	_effondrement_tick += 1

	match _effondrement_phase:
		EffondrementPhase.ANTICIPATION:
			if _effondrement_tick >= EFFONDREMENT_ANTICIPATION_TICKS:
				_effondrement_phase = EffondrementPhase.RELEASE
				_effondrement_tick = 0
		EffondrementPhase.RELEASE:
			if _effondrement_tick == 1 and not _effondrement_hit_applied:
				_try_hit_effondrement()
				_effondrement_hit_applied = true
			if _effondrement_tick >= EFFONDREMENT_RELEASE_TICKS:
				_effondrement_phase = EffondrementPhase.RECOVERY
				_effondrement_tick = 0
		EffondrementPhase.RECOVERY:
			if _effondrement_tick >= EFFONDREMENT_RECOVERY_TICKS - EFFONDREMENT_CANCEL_WINDOW_TICKS:
				if _try_consume_queued_input(_end_effondrement):
					return
			if _effondrement_tick >= EFFONDREMENT_RECOVERY_TICKS:
				_end_effondrement()

	if _effondrement_phase != EffondrementPhase.NONE:
		_sprite.frame = _effondrement_frame_for_tick(_effondrement_global_tick())


func _effondrement_global_tick() -> int:
	match _effondrement_phase:
		EffondrementPhase.ANTICIPATION:
			return _effondrement_tick
		EffondrementPhase.RELEASE:
			return EFFONDREMENT_ANTICIPATION_TICKS + _effondrement_tick
		EffondrementPhase.RECOVERY:
			return EFFONDREMENT_ANTICIPATION_TICKS + EFFONDREMENT_RELEASE_TICKS + _effondrement_tick
		_:
			return 0


func _effondrement_frame_for_tick(tick: int) -> int:
	for i in EFFONDREMENT_FRAME_TICK_BOUNDS.size():
		if tick <= EFFONDREMENT_FRAME_TICK_BOUNDS[i]:
			return i
	return EFFONDREMENT_FRAME_TICK_BOUNDS.size() - 1


func _end_effondrement() -> void:
	_effondrement_phase = EffondrementPhase.NONE
	_effondrement_tick = 0
	_action_lock = false
	_effondrement_cooldown_remaining = EFFONDREMENT_COOLDOWN_TICKS


## Zone circulaire centrée sur le LANCEUR (half_angle_deg=180 couvre tout le
## cercle mathématiquement, voir targeting.gd/power.effondrement.cast.json)
## — contrairement au cône frontal de Poing Tellurique/Bras-Faux ou à la
## ligne de Marée de Sable. Réutilise Targeting.enemies_in_arc() tel quel,
## aucune nouvelle fonction de ciblage.
func _try_hit_effondrement() -> void:
	var dir := facing
	if dir.length_squared() < 0.0001:
		dir = Vector2.DOWN
	dir = dir.normalized()
	var targets: Array = Targeting.enemies_in_arc(get_tree(), global_position, dir, EFFONDREMENT_RADIUS_PX, 180.0)
	if targets.is_empty():
		return
	for target in targets:
		target.take_damage(EFFONDREMENT_DAMAGE, global_position)

	CombatFeedback.register_hit("heavy", true, "heavy_impact", "medium", dir, true)


func get_effondrement_cooldown_ratio() -> float:
	return float(_effondrement_cooldown_remaining) / float(EFFONDREMENT_COOLDOWN_TICKS)


## Fissure Éruptive (Terre, Tier 5) — même discipline ANTICIPATION/RELEASE/
## RECOVERY, voir le bloc de constantes FISSURE_ERUPTIVE_* et
## power.fissure_eruptive.cast.json pour le raisonnement complet (effet
## RANGÉ, l'impact tombe à FISSURE_ERUPTIVE_RANGE_PX devant le lanceur, pas
## sur le lanceur lui-même comme Effondrement).
func _start_fissure_eruptive() -> void:
	if stats.is_dead() or _action_lock or _fissure_eruptive_cooldown_remaining > 0:
		return
	_action_lock = true
	_fissure_eruptive_phase = FissureEruptivePhase.ANTICIPATION
	_fissure_eruptive_tick = 0
	_fissure_eruptive_hit_applied = false
	velocity = Vector2.ZERO
	if facing.x != 0.0:
		_sprite.flip_h = facing.x < 0.0
	_sprite.play("fissure_eruptive")
	_sprite.pause()
	_sprite.frame = 0

	var dir := facing
	if dir.length_squared() < 0.0001:
		dir = Vector2.DOWN
	dir = dir.normalized()
	VfxRecipeRegistry.play(FissureEruptiveRecipeId, {
		"origin": global_position,
		"seed": FISSURE_ERUPTIVE_CAST_SEED,
		"direction": dir,
	})


func _advance_fissure_eruptive() -> void:
	_fissure_eruptive_tick += 1

	match _fissure_eruptive_phase:
		FissureEruptivePhase.ANTICIPATION:
			if _fissure_eruptive_tick >= FISSURE_ERUPTIVE_ANTICIPATION_TICKS:
				_fissure_eruptive_phase = FissureEruptivePhase.RELEASE
				_fissure_eruptive_tick = 0
		FissureEruptivePhase.RELEASE:
			if _fissure_eruptive_tick == 1 and not _fissure_eruptive_hit_applied:
				_try_hit_fissure_eruptive()
				_fissure_eruptive_hit_applied = true
			if _fissure_eruptive_tick >= FISSURE_ERUPTIVE_RELEASE_TICKS:
				_fissure_eruptive_phase = FissureEruptivePhase.RECOVERY
				_fissure_eruptive_tick = 0
		FissureEruptivePhase.RECOVERY:
			if _fissure_eruptive_tick >= FISSURE_ERUPTIVE_RECOVERY_TICKS - FISSURE_ERUPTIVE_CANCEL_WINDOW_TICKS:
				if _try_consume_queued_input(_end_fissure_eruptive):
					return
			if _fissure_eruptive_tick >= FISSURE_ERUPTIVE_RECOVERY_TICKS:
				_end_fissure_eruptive()

	if _fissure_eruptive_phase != FissureEruptivePhase.NONE:
		_sprite.frame = _fissure_eruptive_frame_for_tick(_fissure_eruptive_global_tick())


func _fissure_eruptive_global_tick() -> int:
	match _fissure_eruptive_phase:
		FissureEruptivePhase.ANTICIPATION:
			return _fissure_eruptive_tick
		FissureEruptivePhase.RELEASE:
			return FISSURE_ERUPTIVE_ANTICIPATION_TICKS + _fissure_eruptive_tick
		FissureEruptivePhase.RECOVERY:
			return FISSURE_ERUPTIVE_ANTICIPATION_TICKS + FISSURE_ERUPTIVE_RELEASE_TICKS + _fissure_eruptive_tick
		_:
			return 0


func _fissure_eruptive_frame_for_tick(tick: int) -> int:
	for i in FISSURE_ERUPTIVE_FRAME_TICK_BOUNDS.size():
		if tick <= FISSURE_ERUPTIVE_FRAME_TICK_BOUNDS[i]:
			return i
	return FISSURE_ERUPTIVE_FRAME_TICK_BOUNDS.size() - 1


func _end_fissure_eruptive() -> void:
	_fissure_eruptive_phase = FissureEruptivePhase.NONE
	_fissure_eruptive_tick = 0
	_action_lock = false
	_fissure_eruptive_cooldown_remaining = FISSURE_ERUPTIVE_COOLDOWN_TICKS


## Impact À DISTANCE (pas au lanceur, contrairement à Effondrement) — même
## décalage que les couches VFX via `origin_offset_px` (power.
## fissure_eruptive.cast.json). half_angle_deg=180 = petit cercle complet
## au point d'impact, même technique de réutilisation de Targeting.
## enemies_in_arc() que _try_hit_effondrement() ci-dessus.
func _try_hit_fissure_eruptive() -> void:
	var dir := facing
	if dir.length_squared() < 0.0001:
		dir = Vector2.DOWN
	dir = dir.normalized()
	var impact_origin: Vector2 = global_position + dir * FISSURE_ERUPTIVE_RANGE_PX
	var targets: Array = Targeting.enemies_in_arc(get_tree(), impact_origin, dir, FISSURE_ERUPTIVE_IMPACT_RADIUS_PX, 180.0)
	if targets.is_empty():
		return
	for target in targets:
		target.take_damage(FISSURE_ERUPTIVE_DAMAGE, impact_origin)

	CombatFeedback.register_hit("heavy", true, "heavy_impact", "medium", dir, true)


func get_fissure_eruptive_cooldown_ratio() -> float:
	return float(_fissure_eruptive_cooldown_remaining) / float(FISSURE_ERUPTIVE_COOLDOWN_TICKS)


## Mâchoire (RANK_ZERO_POWER_SKILL_BIBLE, "Monstrification" T3, docs/references/
## monstrification/machoire.png — "Burst rapproché") — même archétype
## "melee_impact" que Poing Belluaire (un seul burst frontal, PAS un balayage) :
## "1 Préparation / 2 Apparition / 3 Morsure + Coup / 4 Disparition". Timeline
## 42 ticks : 16 anticipation (le bras se transforme en gueule, temps 1+2 dans
## une seule phase code, même discipline que les autres pouvoirs de mêlée déjà
## en jeu) / 4 release (la morsure ET le coup simultanés, contact au 1er tick
## comme le combo) / 22 recovery (la gueule se rétracte, temps 4). Portée/angle
## intermédiaires entre Bras-Faux (balayage 90°) et Poing Belluaire (coup
## frontal 60°) : un "burst" mord plus large qu'un simple poing mais reste un
## engagement rapproché, pas un balayage de zone. Dégâts/cooldown NON chiffrés
## par la fiche (même statut que les 4 autres pouvoirs de la Classe) : valeurs
## de départ TUNABLE, légèrement au-dessus de Poing Tellurique (tier3 vs tier1
## de Terre) mais sous Poing Belluaire (qui reste "LE" coup le plus lourd/
## interrompant documenté par le GDD).
const MACHOIRE_ANTICIPATION_TICKS := 16
const MACHOIRE_RELEASE_TICKS := 4
const MACHOIRE_RECOVERY_TICKS := 22
const MACHOIRE_RANGE_PX := 46.0  # ~1.45m, entre Poing Belluaire (40) et Bras-Faux/Poing Tellurique (44-48).
const MACHOIRE_HALF_ANGLE_DEG := 40.0  # arc total ~80°, un "burst" mord plus large qu'un coup frontal pur (60°).
const MACHOIRE_DAMAGE := 15.0  # TUNABLE, entre Poing Tellurique (14) et Poing Belluaire (16).
const MACHOIRE_COOLDOWN_TICKS := 200  # ~3,3s @ 60/s, TUNABLE, entre Bras-Faux (180) et Poing Belluaire (240).
const MachoireRecipeId := "power.machoire.cast"
const MACHOIRE_CAST_SEED := 51005  # Addendum A §A.5, jamais l'horloge murale — suite de la série 5100x déjà utilisée par les 4 autres pouvoirs de Monstrification/Terre.

## DENSIFIÉ (campagne "densité d'animation", agent Monstrification) : 6 ->
## 16 frames, silhouette de départ/fin INCHANGÉE (mêmes deux ancres
## `custom_start_frame_url`/`end_frame_url` = frame 0 et frame 5 de
## l'animation déjà validée — seules les 14 poses intermédiaires sont
## nouvelles). Répartition NON uniforme (mandat densité §2) : 8 frames sur
## l'anticipation (2-15, la gueule se love dans le bras), 4 sur le
## contact/pic (16-20, encadrant le tick de hit théorique 17 = ANTICIPATION
## 16 + RELEASE tick1), 4 sur la recovery (27-42). VÉRIFIÉ par capture
## réelle tick-par-tick (capture_headless.sh --mode=player_action_sequence)
## que la pose de morsure/coup est déjà pleinement affichée sur toute cette
## fenêtre de contact, pas seulement au tick exact du hit — le pic visuel
## couvre large la fenêtre où le hit peut réellement tomber, jamais un
## tick deviné à l'aveugle. Beaucoup de frames là où l'œil a le temps de
## les voir, peu sur le pic pour garder l'impression de vitesse.
const MACHOIRE_FRAME_TICK_BOUNDS: Array[int] = [2, 4, 6, 8, 10, 12, 14, 15, 16, 17, 19, 20, 27, 32, 37, 42]

## Fenêtre d'annulation (même discipline que <SKILL>_CANCEL_WINDOW_TICKS sur
## les 4 autres pouvoirs de Monstrification) — coup "burst" de poids
## intermédiaire (ni le plus léger Bras-Faux, ni le plus lourd Poing
## Belluaire) : fenêtre à mi-chemin, 12 des 22 ticks de RECOVERY (~55%, même
## proportion que Bras-Faux).
const MACHOIRE_CANCEL_WINDOW_TICKS := 12

## Forme Bestiale (RANK_ZERO_POWER_SKILL_BIBLE, "Monstrification" T4,
## docs/references/monstrification/forme_bestiale.png — "Transformation
## majeure") — data/pouvoirs/monstrification.json la documente explicitement
## comme "la seule vraie transformation complète de toute la bible" : traitée
## avec un gabarit au-dessus des 4 autres pouvoirs de la Classe (portée/arc/
## dégâts/recul/cooldown tous au maximum de la Classe), PAS un simple nouveau
## sprite de poing/membre comme Bras-Faux/Poing Belluaire/Mâchoire. "1
## Préparation / 2 Transformation / 3 Attaque large / 4 Retour brutal" — la
## seule compétence de la Classe qui documente explicitement une "attaque
## LARGE" (pas un simple coup/balayage de portée normale). Timeline 64 ticks
## (la plus longue de la Classe, délibéré — une transformation majeure prend
## plus de temps à se lire) : 24 anticipation (le corps entier se transforme,
## temps 1+début temps 2) / 6 release (l'attaque large à deux bras, temps 2
## fin + temps 3, contact au 1er tick) / 34 recovery (le retour à la forme
## humaine, temps 4 "Retour brutal" — la plus longue recovery de la Classe,
## cohérent avec "brutal"). Portée/arc nettement plus larges que les 4 autres
## pouvoirs (arc ~140° contre 60-90°, portée ~1,9m contre 1,25-1,5m) : "attaque
## large" du GDD, pas une frappe ciblée. Dégâts/recul/cooldown NON chiffrés par
## la fiche : valeurs de départ TUNABLE, toutes au-dessus de Poing Belluaire
## (jusqu'ici le pouvoir le plus lourd de la Classe) — cohérent avec le statut
## de transformation majeure/palier de niveau le plus tardif avant Pattes de
## Chasse (unlock_level 14, contre 1/3/6 pour les 3 autres).
const FORME_BESTIALE_ANTICIPATION_TICKS := 24
const FORME_BESTIALE_RELEASE_TICKS := 6
const FORME_BESTIALE_RECOVERY_TICKS := 34
const FORME_BESTIALE_RANGE_PX := 60.0  # ~1.9m, la plus longue portée de mêlée de la Classe.
const FORME_BESTIALE_HALF_ANGLE_DEG := 70.0  # arc total ~140°, "attaque large" — largement au-dessus des 4 autres pouvoirs.
const FORME_BESTIALE_DAMAGE := 26.0  # TUNABLE, au-dessus de Poing Belluaire (16) — le coup le plus lourd de la Classe.
const FORME_BESTIALE_RECOIL_PX := 48.0  # TUNABLE, > Poing Belluaire (40) — "brutal".
const FORME_BESTIALE_RECOIL_TICKS := 10
const FORME_BESTIALE_COOLDOWN_TICKS := 340  # ~5,7s @ 60/s, TUNABLE, le plus long de la Classe — une transformation majeure ne se répète pas à la cadence d'un simple coup.
const FormeBestialeRecipeId := "power.forme_bestiale.cast"
const FORME_BESTIALE_CAST_SEED := 51006  # Addendum A §A.5, jamais l'horloge murale.

## 6 frames pose-à-pose (forme_bestiale/0..5.png) pilotées tick-exact — même
## discipline que les 4 autres pouvoirs de mêlée de la Classe, construite
## tick-exact dès la 1ère passe (MANDAT ROUND 4, pas de round de polish
## séparé). Bornes calées sur le contact réel (ANTICIPATION 24 + RELEASE
## tick1 = tick global 25). Valeurs affinées après inspection visuelle des 6
## frames réelles (voir docs/worklog.md, section Forme Bestiale).
const FORME_BESTIALE_FRAME_TICK_BOUNDS: Array[int] = [8, 16, 22, 26, 34, 64]

## Fenêtre d'annulation — généreuse en proportion (18 des 34 ticks de
## RECOVERY, ~53%, même ordre de grandeur que Bras-Faux/Mâchoire) malgré la
## timeline la plus longue de la Classe : "Retour brutal" tient déjà sa pose
## finale sans bouger sur une bonne partie de cette fenêtre (même
## raisonnement que documenté sur Bras-Faux/Poing Belluaire/Poing Tellurique
## ci-dessus), rien de visuel n'est coupé par une annulation dans cette
## fenêtre.
const FORME_BESTIALE_CANCEL_WINDOW_TICKS := 18

## Pattes de Chasse (RANK_ZERO_POWER_SKILL_BIBLE, "Monstrification" T5,
## docs/references/monstrification/pattes_de_chasse.png — "Mobilité
## offensive") — SEUL pouvoir de la Classe avec un déplacement automatique du
## joueur pendant l'action (les 4 autres sont tous "aucun déplacement
## automatique" par construction, cf. commentaires ci-dessus) : "1
## Préparation / 2 Bond / 3 Frappe en mouvement / 4 Atterrissage". 3 phases
## ANTICIPATION/MOVE/RECOVERY comme le dash (_advance_dash() ci-dessous),
## PAS ANTICIPATION/RELEASE/RECOVERY comme les 4 autres pouvoirs de mêlée de
## la Classe — le "Bond" EST le déplacement, pas un simple appui visuel bref
## pendant qu'une autre couche porte le mouvement (même exception documentée
## sur le dash, §6.2 du doc VFX). Timeline 40 ticks : 10 anticipation
## (accroupissement, temps 1 "Préparation") / 14 move (le bond + la frappe en
## mouvement, temps 2+3 — le joueur avance réellement de
## PATTES_DE_CHASSE_DISTANCE_PX sur cette fenêtre, la frappe elle-même a lieu
## à PATTES_DE_CHASSE_STRIKE_TICK) / 16 recovery (l'atterrissage qui se stabilise,
## temps 4). Portée de frappe/largeur NON chiffrées par le GDD (même statut
## que les 4 autres pouvoirs) : bande étroite façon Targeting.enemies_in_line
## (Marée de Sable), pas un cône — "peut toucher plusieurs ennemis" en ligne
## sur le trajet du bond, jamais une seule cible. Dégâts modérés (mobilité
## D'ABORD, dégâts ensuite — même logique que Marée de Sable, tier CONTRÔLE/
## UTILITÉ plutôt que dégâts purs) : TUNABLE, sous Mâchoire.
const PATTES_DE_CHASSE_ANTICIPATION_TICKS := 10
const PATTES_DE_CHASSE_MOVE_TICKS := 14
const PATTES_DE_CHASSE_RECOVERY_TICKS := 16
const PATTES_DE_CHASSE_DISTANCE_PX := 70.0  # ~2.2m, bond solide mais plus court que le dash (80px) — un pouvoir de mêlée, pas un remplacement du dash.
## Tick (RELATIF à la phase MOVE, 1-indexed comme les autres compteurs
## _*_tick) où la frappe elle-même a lieu — à peu près à mi-bond, cohérent
## avec "Frappe en mouvement" (temps 3, ni au tout début du bond temps 2, ni
## à l'atterrissage temps 4).
const PATTES_DE_CHASSE_STRIKE_TICK := 7
const PATTES_DE_CHASSE_RANGE_PX := 50.0  # longueur de la bande de frappe devant la position du joueur AU tick de frappe.
const PATTES_DE_CHASSE_HALF_WIDTH_PX := 18.0
const PATTES_DE_CHASSE_DAMAGE := 14.0  # TUNABLE, mobilité/utilité d'abord — même ordre de grandeur que Poing Tellurique.
const PATTES_DE_CHASSE_COOLDOWN_TICKS := 200  # ~3,3s @ 60/s, TUNABLE.
const PattesDeChasseRecipeId := "power.pattes_de_chasse.cast"
const PATTES_DE_CHASSE_CAST_SEED := 51007  # Addendum A §A.5, jamais l'horloge murale.

## DENSIFIÉ (campagne "densité d'animation", agent Monstrification) : 6 ->
## 16 frames, silhouette de départ/fin INCHANGÉE (mêmes deux ancres
## `custom_start_frame_url`/`end_frame_url` = frame 0 et frame 5 de
## l'animation déjà validée). Bornes calées sur le tick de frappe réel
## (ANTICIPATION 10 + PATTES_DE_CHASSE_STRIKE_TICK 7 = tick global 17,
## inchangé). Répartition non uniforme : 5 frames sur l'anticipation
## (2-10), 3 sur l'approche du bond (12-16), 2 SEULEMENT au contact (17-18,
## la fenêtre la plus serrée de toute la Classe — la frappe elle-même est
## quasi instantanée dans le GDD), 2 sur la fin du bond (21-24), 4 sur
## l'atterrissage/recovery (29-40).
const PATTES_DE_CHASSE_FRAME_TICK_BOUNDS: Array[int] = [2, 4, 6, 8, 10, 12, 14, 16, 17, 18, 21, 24, 29, 33, 37, 40]

## Fenêtre d'annulation — la plus courte en proportion de toute la Classe (10
## des 16 ticks de RECOVERY, ~62%) : un pouvoir de mobilité doit rester
## réactif, l'esprit même de "peut s'enchaîner vite" plutôt qu'un coup lourd
## qu'on veut faire durer à l'écran.
const PATTES_DE_CHASSE_CANCEL_WINDOW_TICKS := 10


## Mâchoire — même construction que Bras-Faux/Poing Belluaire (create_character_state
## sur un membre, PAS une simple pose comme Poing Tellurique/Marée de Sable).
##
## Art dédié (agent Monstrification, 2026-08-24, MANDAT ROUND 4 — construit
## tick-exact dès cette 1ère passe, pas de round de polish séparé) : anim
## "machoire" propre, bras droit réellement transformé en gueule organique
## béante (create_character_state sur le character_id Cendre_v3c EN JEU
## (8596a4ad, vérifié via get_character AVANT tout appel — même piège déjà
## rencontré deux fois sur ce dossier, évité en amont) puis animate_character
## mode v3 sur cet état, 6 frames sud, cf. data/pixellab_usage.jsonl). Même
## discipline flip_h auto-contenue que les 4 autres pouvoirs de mêlée.
func _start_machoire() -> void:
	if stats.is_dead() or _action_lock or _machoire_cooldown_remaining > 0:
		return
	_action_lock = true
	_machoire_phase = MachoirePhase.ANTICIPATION
	_machoire_tick = 0
	_machoire_hit_applied = false
	if facing.x != 0.0:
		_sprite.flip_h = facing.x < 0.0
	# Tick-exact (voir MACHOIRE_FRAME_TICK_BOUNDS ci-dessus) : play() positionne
	# l'AnimatedSprite2D sur "machoire", pause() coupe immédiatement sa propre
	# horloge fps pour que seule _advance_machoire() décide de la frame
	# affichée, jamais Godot — même discipline que les 4 autres pouvoirs.
	_sprite.play("machoire")
	_sprite.pause()
	_sprite.frame = 0

	var dir := facing
	if dir.length_squared() < 0.0001:
		dir = Vector2.DOWN
	dir = dir.normalized()
	VfxRecipeRegistry.play(MachoireRecipeId, {
		"origin": global_position,
		"seed": MACHOIRE_CAST_SEED,
		"direction": dir,
	})


func _advance_machoire() -> void:
	_machoire_tick += 1
	velocity = Vector2.ZERO  # "aucun déplacement automatique" — même construction que Bras-Faux/Poing Belluaire.
	match _machoire_phase:
		MachoirePhase.ANTICIPATION:
			if _machoire_tick >= MACHOIRE_ANTICIPATION_TICKS:
				_machoire_phase = MachoirePhase.RELEASE
				_machoire_tick = 0
		MachoirePhase.RELEASE:
			if _machoire_tick == 1 and not _machoire_hit_applied:
				_try_hit_machoire()
				_machoire_hit_applied = true
			if _machoire_tick >= MACHOIRE_RELEASE_TICKS:
				_machoire_phase = MachoirePhase.RECOVERY
				_machoire_tick = 0
		MachoirePhase.RECOVERY:
			# Fenêtre d'annulation (MACHOIRE_CANCEL_WINDOW_TICKS) — même patron
			# que les 4 autres pouvoirs de mêlée ci-dessus.
			if _machoire_tick >= MACHOIRE_RECOVERY_TICKS - MACHOIRE_CANCEL_WINDOW_TICKS:
				if _try_consume_queued_input(_end_machoire):
					return
			if _machoire_tick >= MACHOIRE_RECOVERY_TICKS:
				_end_machoire()
	if _machoire_phase != MachoirePhase.NONE:
		_sprite.frame = _machoire_frame_for_tick(_machoire_global_tick())


func _machoire_global_tick() -> int:
	match _machoire_phase:
		MachoirePhase.ANTICIPATION:
			return _machoire_tick
		MachoirePhase.RELEASE:
			return MACHOIRE_ANTICIPATION_TICKS + _machoire_tick
		MachoirePhase.RECOVERY:
			return MACHOIRE_ANTICIPATION_TICKS + MACHOIRE_RELEASE_TICKS + _machoire_tick
		_:
			return 0


func _machoire_frame_for_tick(tick: int) -> int:
	for i in MACHOIRE_FRAME_TICK_BOUNDS.size():
		if tick <= MACHOIRE_FRAME_TICK_BOUNDS[i]:
			return i
	return MACHOIRE_FRAME_TICK_BOUNDS.size() - 1


func _end_machoire() -> void:
	_machoire_phase = MachoirePhase.NONE
	_machoire_tick = 0
	_action_lock = false
	_machoire_cooldown_remaining = MACHOIRE_COOLDOWN_TICKS


## "Morsure + Coup" (temps 3 de la planche) : DEUX actions simultanées dans le
## GDD, mais un seul jet de dégâts côté gameplay (même discipline que Poing
## Belluaire — pas de mécanique séparée pour "la morsure" vs "le coup", la
## recette VFX porte déjà la distinction visuelle avec ses 2 couches contact
## séparées, cf. data/recipes/power.machoire.cast.json).
func _try_hit_machoire() -> void:
	var dir := facing
	if dir.length_squared() < 0.0001:
		dir = Vector2.DOWN
	dir = dir.normalized()
	var targets: Array = Targeting.enemies_in_arc(get_tree(), global_position, dir, MACHOIRE_RANGE_PX, MACHOIRE_HALF_ANGLE_DEG)
	if targets.is_empty():
		return
	for target in targets:
		target.take_damage(MACHOIRE_DAMAGE, global_position)

	CombatFeedback.register_hit("medium", true, "heavy_impact", "light", dir, true)


## Forme Bestiale — "la seule vraie transformation complète de toute la
## bible" (data/pouvoirs/monstrification.json, notes) : create_character_state
## sur le CORPS ENTIER (canvas source élargi à 96×100, contre 56-72px de large
## pour les 4 autres pouvoirs de la Classe — la silhouette doit se lire
## nettement plus grande/massive qu'un simple bras/jambe transformé), pas
## juste un membre comme Bras-Faux/Poing Belluaire/Mâchoire/Pattes de Chasse.
##
## Art dédié (agent Monstrification, 2026-08-24) : anim "forme_bestiale"
## propre, character_id Cendre_v3c EN JEU vérifié via get_character AVANT
## l'appel (8596a4ad, même piège déjà rencontré deux fois évité en amont),
## create_character_state (corps entier -> bête hybride hanchée, deux bras
## griffus/tendons organiques massifs, tête à crâne conservée) puis
## animate_character mode v3, 6 frames sud (balayage large à deux bras).
func _start_forme_bestiale() -> void:
	if stats.is_dead() or _action_lock or _forme_bestiale_cooldown_remaining > 0:
		return
	_action_lock = true
	_forme_bestiale_phase = FormeBestialePhase.ANTICIPATION
	_forme_bestiale_tick = 0
	_forme_bestiale_hit_applied = false
	if facing.x != 0.0:
		_sprite.flip_h = facing.x < 0.0
	# Tick-exact (voir FORME_BESTIALE_FRAME_TICK_BOUNDS) : même discipline
	# play()+pause()+frame=0 que les 4 autres pouvoirs de mêlée de la Classe.
	_sprite.play("forme_bestiale")
	_sprite.pause()
	_sprite.frame = 0

	var dir := facing
	if dir.length_squared() < 0.0001:
		dir = Vector2.DOWN
	dir = dir.normalized()
	VfxRecipeRegistry.play(FormeBestialeRecipeId, {
		"origin": global_position,
		"seed": FORME_BESTIALE_CAST_SEED,
		"direction": dir,
	})


func _advance_forme_bestiale() -> void:
	_forme_bestiale_tick += 1
	velocity = Vector2.ZERO  # "aucun déplacement automatique" — l'attaque large tient sur place, contrairement à Pattes de Chasse.
	match _forme_bestiale_phase:
		FormeBestialePhase.ANTICIPATION:
			if _forme_bestiale_tick >= FORME_BESTIALE_ANTICIPATION_TICKS:
				_forme_bestiale_phase = FormeBestialePhase.RELEASE
				_forme_bestiale_tick = 0
		FormeBestialePhase.RELEASE:
			if _forme_bestiale_tick == 1 and not _forme_bestiale_hit_applied:
				_try_hit_forme_bestiale()
				_forme_bestiale_hit_applied = true
			if _forme_bestiale_tick >= FORME_BESTIALE_RELEASE_TICKS:
				_forme_bestiale_phase = FormeBestialePhase.RECOVERY
				_forme_bestiale_tick = 0
		FormeBestialePhase.RECOVERY:
			if _forme_bestiale_tick >= FORME_BESTIALE_RECOVERY_TICKS - FORME_BESTIALE_CANCEL_WINDOW_TICKS:
				if _try_consume_queued_input(_end_forme_bestiale):
					return
			if _forme_bestiale_tick >= FORME_BESTIALE_RECOVERY_TICKS:
				_end_forme_bestiale()
	if _forme_bestiale_phase != FormeBestialePhase.NONE:
		_sprite.frame = _forme_bestiale_frame_for_tick(_forme_bestiale_global_tick())


func _forme_bestiale_global_tick() -> int:
	match _forme_bestiale_phase:
		FormeBestialePhase.ANTICIPATION:
			return _forme_bestiale_tick
		FormeBestialePhase.RELEASE:
			return FORME_BESTIALE_ANTICIPATION_TICKS + _forme_bestiale_tick
		FormeBestialePhase.RECOVERY:
			return FORME_BESTIALE_ANTICIPATION_TICKS + FORME_BESTIALE_RELEASE_TICKS + _forme_bestiale_tick
		_:
			return 0


func _forme_bestiale_frame_for_tick(tick: int) -> int:
	for i in FORME_BESTIALE_FRAME_TICK_BOUNDS.size():
		if tick <= FORME_BESTIALE_FRAME_TICK_BOUNDS[i]:
			return i
	return FORME_BESTIALE_FRAME_TICK_BOUNDS.size() - 1


func _end_forme_bestiale() -> void:
	_forme_bestiale_phase = FormeBestialePhase.NONE
	_forme_bestiale_tick = 0
	_action_lock = false
	_forme_bestiale_cooldown_remaining = FORME_BESTIALE_COOLDOWN_TICKS


## "Attaque large" (temps 3) : arc le plus ouvert de la Classe
## (FORME_BESTIALE_HALF_ANGLE_DEG=70°, total 140°) — touche potentiellement
## TOUS les ennemis proches, pas une seule cible (Targeting.enemies_in_arc(),
## même fonction que Bras-Faux/Poing Belluaire/Mâchoire/Poing Tellurique,
## juste un arc nettement plus généreux).
func _try_hit_forme_bestiale() -> void:
	var dir := facing
	if dir.length_squared() < 0.0001:
		dir = Vector2.DOWN
	dir = dir.normalized()
	var targets: Array = Targeting.enemies_in_arc(get_tree(), global_position, dir, FORME_BESTIALE_RANGE_PX, FORME_BESTIALE_HALF_ANGLE_DEG)
	if targets.is_empty():
		return
	for target in targets:
		target.take_damage(FORME_BESTIALE_DAMAGE, global_position, FORME_BESTIALE_RECOIL_PX, FORME_BESTIALE_RECOIL_TICKS)

	# Le coup le plus lourd de la Classe (hitstop "heavy", plus fort que
	# Poing Belluaire) — cohérent avec "transformation majeure"/"Retour
	# brutal".
	CombatFeedback.register_hit("heavy", true, "heavy_impact", "medium", dir, true)


## Pattes de Chasse — SEUL pouvoir de Monstrification avec un déplacement
## automatique du joueur (voir PATTES_DE_CHASSE_* ci-dessus, "Mobilité
## offensive"). create_character_state sur les DEUX JAMBES (canvas source
## élargi à 56×88 pour la stance accroupie plus large que la pose neutre),
## pas un bras comme Bras-Faux/Poing Belluaire/Mâchoire.
##
## Art dédié (agent Monstrification, 2026-08-24) : anim "pattes_de_chasse"
## propre, character_id Cendre_v3c EN JEU vérifié via get_character AVANT
## l'appel (8596a4ad, même piège déjà rencontré deux fois évité en amont),
## create_character_state (jambes -> membres digitigrades griffus organiques)
## puis animate_character mode v3, 6 frames sud (accroupissement -> bond ->
## frappe en mouvement -> atterrissage bas).
func _start_pattes_de_chasse() -> void:
	if stats.is_dead() or _action_lock or _pattes_de_chasse_cooldown_remaining > 0:
		return
	var dir := facing
	if dir.length_squared() < 0.0001:
		dir = Vector2.DOWN
	_pattes_de_chasse_direction = dir.normalized()

	_action_lock = true
	_pattes_de_chasse_phase = PattesDeChassePhase.ANTICIPATION
	_pattes_de_chasse_tick = 0
	_pattes_de_chasse_hit_applied = false
	if _pattes_de_chasse_direction.x != 0.0:
		_sprite.flip_h = _pattes_de_chasse_direction.x < 0.0
	# Tick-exact (voir PATTES_DE_CHASSE_FRAME_TICK_BOUNDS) : même discipline
	# play()+pause()+frame=0 que les 4 autres pouvoirs de mêlée de la Classe.
	_sprite.play("pattes_de_chasse")
	_sprite.pause()
	_sprite.frame = 0

	VfxRecipeRegistry.play(PattesDeChasseRecipeId, {
		"origin": global_position,
		"seed": PATTES_DE_CHASSE_CAST_SEED,
		"direction": _pattes_de_chasse_direction,
	})


## ANTICIPATION/MOVE/RECOVERY (même construction que _advance_dash()) : MOVE
## déplace RÉELLEMENT le joueur (ease-out, même formule que le dash) et
## applique un jet de dégâts unique à PATTES_DE_CHASSE_STRIKE_TICK ("Frappe
## en mouvement", temps 3) — ni au tout début du bond, ni à l'atterrissage.
func _advance_pattes_de_chasse() -> void:
	_pattes_de_chasse_tick += 1
	match _pattes_de_chasse_phase:
		PattesDeChassePhase.ANTICIPATION:
			velocity = Vector2.ZERO
			if _pattes_de_chasse_tick >= PATTES_DE_CHASSE_ANTICIPATION_TICKS:
				_pattes_de_chasse_phase = PattesDeChassePhase.MOVE
				_pattes_de_chasse_tick = 0
		PattesDeChassePhase.MOVE:
			var progress_before: float = _ease_out_quad(float(_pattes_de_chasse_tick - 1) / PATTES_DE_CHASSE_MOVE_TICKS)
			var progress_after: float = _ease_out_quad(float(_pattes_de_chasse_tick) / PATTES_DE_CHASSE_MOVE_TICKS)
			var step_px: float = (progress_after - progress_before) * PATTES_DE_CHASSE_DISTANCE_PX
			velocity = _pattes_de_chasse_direction * (step_px * Engine.physics_ticks_per_second)
			if _pattes_de_chasse_tick == PATTES_DE_CHASSE_STRIKE_TICK and not _pattes_de_chasse_hit_applied:
				_try_hit_pattes_de_chasse()
				_pattes_de_chasse_hit_applied = true
			if _pattes_de_chasse_tick >= PATTES_DE_CHASSE_MOVE_TICKS:
				_pattes_de_chasse_phase = PattesDeChassePhase.RECOVERY
				_pattes_de_chasse_tick = 0
				_pattes_de_chasse_recovery_velocity = _pattes_de_chasse_direction * DASH_RECOVERY_INITIAL_SPEED_PX_S * 0.5
		PattesDeChassePhase.RECOVERY:
			velocity = _pattes_de_chasse_recovery_velocity
			_pattes_de_chasse_recovery_velocity = _pattes_de_chasse_recovery_velocity.move_toward(
				Vector2.ZERO, (DASH_RECOVERY_INITIAL_SPEED_PX_S * 0.5) / PATTES_DE_CHASSE_RECOVERY_TICKS)
			if _pattes_de_chasse_tick >= PATTES_DE_CHASSE_RECOVERY_TICKS - PATTES_DE_CHASSE_CANCEL_WINDOW_TICKS:
				if _try_consume_queued_input(_end_pattes_de_chasse):
					return
			if _pattes_de_chasse_tick >= PATTES_DE_CHASSE_RECOVERY_TICKS:
				_end_pattes_de_chasse()
	if _pattes_de_chasse_phase != PattesDeChassePhase.NONE:
		_sprite.frame = _pattes_de_chasse_frame_for_tick(_pattes_de_chasse_global_tick())


func _pattes_de_chasse_global_tick() -> int:
	match _pattes_de_chasse_phase:
		PattesDeChassePhase.ANTICIPATION:
			return _pattes_de_chasse_tick
		PattesDeChassePhase.MOVE:
			return PATTES_DE_CHASSE_ANTICIPATION_TICKS + _pattes_de_chasse_tick
		PattesDeChassePhase.RECOVERY:
			return PATTES_DE_CHASSE_ANTICIPATION_TICKS + PATTES_DE_CHASSE_MOVE_TICKS + _pattes_de_chasse_tick
		_:
			return 0


func _pattes_de_chasse_frame_for_tick(tick: int) -> int:
	for i in PATTES_DE_CHASSE_FRAME_TICK_BOUNDS.size():
		if tick <= PATTES_DE_CHASSE_FRAME_TICK_BOUNDS[i]:
			return i
	return PATTES_DE_CHASSE_FRAME_TICK_BOUNDS.size() - 1


func _end_pattes_de_chasse() -> void:
	_pattes_de_chasse_phase = PattesDeChassePhase.NONE
	_pattes_de_chasse_tick = 0
	velocity = Vector2.ZERO
	_action_lock = false
	_pattes_de_chasse_cooldown_remaining = PATTES_DE_CHASSE_COOLDOWN_TICKS


## Bande devant la position ACTUELLE du joueur (Targeting.enemies_in_line(),
## même fonction que Marée de Sable) — pas un cône : "peut toucher plusieurs
## ennemis" sur le trajet du bond, jamais une seule cible. Appelée au tick de
## frappe (voir _advance_pattes_de_chasse()), donc `global_position` reflète
## déjà le déplacement accumulé jusqu'à ce tick, pas la position de départ.
func _try_hit_pattes_de_chasse() -> void:
	var dir := _pattes_de_chasse_direction
	if dir.length_squared() < 0.0001:
		dir = Vector2.DOWN
	var targets: Array = Targeting.enemies_in_line(get_tree(), global_position, dir, PATTES_DE_CHASSE_RANGE_PX, PATTES_DE_CHASSE_HALF_WIDTH_PX)
	if targets.is_empty():
		return
	for target in targets:
		target.take_damage(PATTES_DE_CHASSE_DAMAGE, global_position)

	CombatFeedback.register_hit("medium", true, "heavy_impact", "light", dir, true)


func is_dead() -> bool:
	return stats.is_dead()


## Mandat production v1 §1.3 : "roulade... avec frames d'invincibilité (i-
## frames) dans la logique de dégâts." Vrai UNIQUEMENT pendant DodgePhase.
## ACTIVE — jamais pendant l'anticipation (le joueur n'a pas encore bougé)
## ni la recovery (il "paie" sa fenêtre d'invincibilité en restant
## vulnérable le temps de se relever).
func is_invincible() -> bool:
	return _dodge_phase == DodgePhase.ACTIVE


## H1 (GDD §17, HUD : "compétences équipées... cooldowns") — 0.0 = prêt,
## 1.0 = vient d'être utilisé. Un getter par cooldown plutôt qu'exposer
## les compteurs bruts : le HUD lit un ratio, jamais les ticks internes
## d'une timeline qui ne le regarde pas.
func get_dodge_cooldown_ratio() -> float:
	return float(_dodge_cooldown_remaining) / float(DODGE_COOLDOWN_TICKS)


func get_power1_cooldown_ratio() -> float:
	return float(_power1_cooldown_remaining) / float(POWER1_COOLDOWN_TICKS)


func get_bras_faux_cooldown_ratio() -> float:
	return float(_bras_faux_cooldown_remaining) / float(BRAS_FAUX_COOLDOWN_TICKS)


func get_poing_belluaire_cooldown_ratio() -> float:
	return float(_poing_belluaire_cooldown_remaining) / float(POING_BELLUAIRE_COOLDOWN_TICKS)


func get_poing_tellurique_cooldown_ratio() -> float:
	return float(_poing_tellurique_cooldown_remaining) / float(POING_TELLURIQUE_COOLDOWN_TICKS)


func get_maree_de_sable_cooldown_ratio() -> float:
	return float(_maree_de_sable_cooldown_remaining) / float(MAREE_DE_SABLE_COOLDOWN_TICKS)


func get_machoire_cooldown_ratio() -> float:
	return float(_machoire_cooldown_remaining) / float(MACHOIRE_COOLDOWN_TICKS)


func get_forme_bestiale_cooldown_ratio() -> float:
	return float(_forme_bestiale_cooldown_remaining) / float(FORME_BESTIALE_COOLDOWN_TICKS)


func get_pattes_de_chasse_cooldown_ratio() -> float:
	return float(_pattes_de_chasse_cooldown_remaining) / float(PATTES_DE_CHASSE_COOLDOWN_TICKS)


func get_corbeau_pale_cooldown_ratio() -> float:
	return float(_corbeau_pale_cooldown_remaining) / float(CORBEAU_PALE_COOLDOWN_TICKS)


func get_poing_du_colosse_cooldown_ratio() -> float:
	return float(_poing_du_colosse_cooldown_remaining) / float(POING_DU_COLOSSE_COOLDOWN_TICKS)


func get_oeil_sans_regard_cooldown_ratio() -> float:
	return float(_oeil_sans_regard_cooldown_remaining) / float(OEIL_SANS_REGARD_COOLDOWN_TICKS)


func get_serpent_creux_cooldown_ratio() -> float:
	return float(_serpent_creux_cooldown_remaining) / float(SERPENT_CREUX_COOLDOWN_TICKS)


## Amendement GDD Pouvoir/déblocage (confirmé par Milan, docs/worklog.md :
## 1 seul Pouvoir par run tiré au hasard — RunState.active_power — 5
## compétences débloquées par palier de niveau, ordre FIXE par Pouvoir).
## data/pouvoirs/<pouvoir_id>.json (lu par l'autoload PouvoirRegistry) ne
## connaît que l'ordre/les paliers de la bible, PAS ce qui existe
## réellement en code — cette table est la seule source de vérité sur
## les compétences qui ont une fonction/un cooldown réels aujourd'hui (4
## sur les 15 de la bible). Un id absent de cette table = slot vide
## (bouton absent), même si son palier de niveau est déjà atteint.
const IMPLEMENTED_SKILL_HANDLERS := {
	"gueule_vide": "_cast_gueule_vide",
	"bras_faux": "_start_bras_faux",
	"poing_belluaire": "_start_poing_belluaire",
	"poing_tellurique": "_start_poing_tellurique",
	"maree_de_sable": "_start_maree_de_sable",
	"carapace": "_start_carapace",
	"effondrement": "_start_effondrement",
	"fissure_eruptive": "_start_fissure_eruptive",
	"machoire": "_start_machoire",
	"forme_bestiale": "_start_forme_bestiale",
	"pattes_de_chasse": "_start_pattes_de_chasse",
	"corbeau_pale": "_cast_corbeau_pale",
	"poing_du_colosse": "_cast_poing_du_colosse",
	"oeil_sans_regard": "_cast_oeil_sans_regard",
	"serpent_creux": "_cast_serpent_creux",
}
const IMPLEMENTED_SKILL_COOLDOWN_GETTERS := {
	"gueule_vide": "get_power1_cooldown_ratio",
	"bras_faux": "get_bras_faux_cooldown_ratio",
	"poing_belluaire": "get_poing_belluaire_cooldown_ratio",
	"poing_tellurique": "get_poing_tellurique_cooldown_ratio",
	"maree_de_sable": "get_maree_de_sable_cooldown_ratio",
	"carapace": "get_carapace_cooldown_ratio",
	"effondrement": "get_effondrement_cooldown_ratio",
	"fissure_eruptive": "get_fissure_eruptive_cooldown_ratio",
	"machoire": "get_machoire_cooldown_ratio",
	"forme_bestiale": "get_forme_bestiale_cooldown_ratio",
	"pattes_de_chasse": "get_pattes_de_chasse_cooldown_ratio",
	"corbeau_pale": "get_corbeau_pale_cooldown_ratio",
	"poing_du_colosse": "get_poing_du_colosse_cooldown_ratio",
	"oeil_sans_regard": "get_oeil_sans_regard_cooldown_ratio",
	"serpent_creux": "get_serpent_creux_cooldown_ratio",
}


func _get_active_power() -> String:
	if not has_node("/root/RunState"):
		return ""
	return get_node("/root/RunState").active_power


## Compétence occupant l'emplacement `slot_index` (1..5) pour le Pouvoir
## actif de cette run — dictionnaire `{id, name, touch_label}` SI son
## palier de niveau est atteint ET qu'elle est réellement implémentée
## (voir IMPLEMENTED_SKILL_HANDLERS ci-dessus), dictionnaire vide sinon.
## C'est ce que touch_controls.gd/hud.gd lisent pour savoir si un
## emplacement doit afficher quelque chose du tout — absent, jamais
## grisé (exigence explicite de Milan).
func get_power_slot_info(slot_index: int) -> Dictionary:
	var pouvoir_id: String = _get_active_power()
	if pouvoir_id == "" or not has_node("/root/PouvoirRegistry"):
		return {}
	var skill: Dictionary = get_node("/root/PouvoirRegistry").get_unlocked_skill_for_slot(
		pouvoir_id, slot_index, stats.level
	)
	if skill.is_empty():
		return {}
	var skill_id: String = skill.get("id", "")
	if not IMPLEMENTED_SKILL_HANDLERS.has(skill_id):
		return {}
	return {
		"id": skill_id,
		"name": skill.get("name", ""),
		"touch_label": skill.get("touch_label", ""),
	}


func get_power_slot_cooldown_ratio(slot_index: int) -> float:
	var info: Dictionary = get_power_slot_info(slot_index)
	if info.is_empty():
		return 0.0
	return call(IMPLEMENTED_SKILL_COOLDOWN_GETTERS[info["id"]])


func _try_activate_power_slot(slot_index: int) -> void:
	var info: Dictionary = get_power_slot_info(slot_index)
	if info.is_empty() or stats.is_dead():
		return
	if get_power_slot_cooldown_ratio(slot_index) > 0.0:
		return
	# Gueule Vide reste l'EXCEPTION documentée (_cast_gueule_vide() ne pose
	# jamais _action_lock — "l'invocation n'immobilise pas le joueur", voir
	# le commentaire au-dessus de _power1_cooldown_remaining) : la mettre
	# en file ici la rendrait bloquable par un _action_lock ÉTRANGER
	# qu'elle n'a jamais eu à respecter avant ce mandat (ex. encore en
	# pleine RECOVERY d'un dash) — une régression sur un contrat déjà
	# validé, pas une amélioration. Elle garde donc le comportement exact
	# d'avant ce mandat : appelée directement, seul le cooldown la borne.
	if _action_lock and info["id"] != "gueule_vide":
		# Buffer d'input (mandat "fluidité", généralisation de l'embryon
		# _attack_queued aux 4 AUTRES compétences dédiées) : AVANT ce
		# mandat, chaque `_start_*()` de ces 4 compétences retournait tôt
		# sur son propre garde `_action_lock` (voir _start_bras_faux() etc.)
		# — l'appui était perdu en silence si le joueur était déjà engagé
		# dans une autre action (combo/dash/esquive/une des 5 compétences).
		# Retenu ici une fenêtre courte (INPUT_BUFFER_TICKS) au lieu
		# d'appeler le handler (qui no-opérerait de toute façon) : consommé
		# soit par la fenêtre d'annulation de l'action en cours (voir
		# `_try_consume_queued_input()`, appelé depuis chaque
		# `_advance_*()`), soit par le filet de sécurité en fin de
		# `_physics_process()` si l'action en cours n'a pas de fenêtre
		# dédiée (dash/esquive/hurt). Dernier appui gagne, même discipline
		# que `_attack_queued`.
		_queued_power_slot = slot_index
		_queued_power_ticks_remaining = INPUT_BUFFER_TICKS
		return
	call(IMPLEMENTED_SKILL_HANDLERS[info["id"]])


## Consomme `_queued_power_slot` s'il est toujours valide (compétence
## toujours implémentée sur le Pouvoir actif de cette run + cooldown
## écoulé) — factorisé car appelé à la fois par le filet de sécurité de
## `_physics_process()` (dash/esquive/hurt, sans fenêtre d'annulation
## propre) ET par `_try_consume_queued_input()` ci-dessous (fenêtre
## d'annulation propre à chaque compétence). Ne vérifie PAS `_action_lock`
## lui-même — c'est aux appelants de garantir qu'il est déjà (ou vient
## d'être) levé. Retourne true si une compétence a effectivement démarré.
func _fire_queued_power_slot() -> bool:
	if _queued_power_slot <= 0:
		return false
	var slot_index := _queued_power_slot
	_queued_power_slot = 0
	_queued_power_ticks_remaining = 0
	var info: Dictionary = get_power_slot_info(slot_index)
	if info.is_empty() or stats.is_dead() or get_power_slot_cooldown_ratio(slot_index) > 0.0:
		return false
	velocity = Vector2.ZERO
	call(IMPLEMENTED_SKILL_HANDLERS[info["id"]])
	return true


## Fenêtres d'annulation (mandat "fluidité") — appelée depuis la RECOVERY
## de chaque compétence dédiée (voir `<SKILL>_CANCEL_WINDOW_TICKS`) une
## fois le tick d'annulation atteint. Priorité à `_attack_queued` (même
## ordre que le combo lui-même) puis au pouvoir mis en file. `end_current`
## termine proprement l'action EN COURS (pose son cooldown, lève
## `_action_lock`) — chaque appelant passe sa propre fonction `_end_*()`
## plutôt que de dupliquer cette étape ici. Retourne true si l'action en
## cours a été terminée tôt pour laisser place à l'action en file (que
## celle-ci ait effectivement pu démarrer ou non — un pouvoir invalidé
## entre-temps, ex. cooldown qui vient d'expirer autrement, laisse
## simplement le joueur revenir à `_handle_movement()` au tick suivant,
## jamais un crash) — l'appelant doit alors `return` immédiatement, même
## discipline que le chaînage déjà en place sur le combo de base.
func _try_consume_queued_input(end_current: Callable) -> bool:
	if _attack_queued:
		_attack_queued = false
		_queued_power_slot = 0
		_queued_power_ticks_remaining = 0
		end_current.call()
		_start_attack(1)
		return true
	if _queued_power_slot > 0:
		var slot_index := _queued_power_slot
		# Validé AVANT de terminer l'action en cours (jamais après) : si le
		# pouvoir en file s'avère invalide (Pouvoir actif changé entre
		# temps, ce qui ne peut pas arriver en jeu réel mais reste vérifié
		# par prudence), l'action en cours continue sa RECOVERY normalement
		# au lieu d'être coupée pour rien.
		var info: Dictionary = get_power_slot_info(slot_index)
		if info.is_empty() or stats.is_dead() or get_power_slot_cooldown_ratio(slot_index) > 0.0:
			_queued_power_slot = 0
			_queued_power_ticks_remaining = 0
			return false
		end_current.call()
		_fire_queued_power_slot()
		return true
	return false


## Réaction à un coup subi. Même signature qu'Enemy.take_damage() (source_
## position + recoil_strength_px/recoil_ticks pour orienter le recul,
## cohérence entre les deux entités qui peuvent encaisser un coup) —
## appelée pour de vrai depuis G (Crawler/Brute/Ranged, GDD §10) : le
## recul manquait jusqu'ici (voir _advance_hurt() ci-dessous, qui règle
## le piège documenté par le commentaire historique — _handle_movement()
## écraserait `velocity` au tick suivant sans sa propre timeline).
##
## Si le joueur est DÉJÀ engagé dans une autre timeline (combo/dash/
## esquive/Bras-Faux — `_action_lock` déjà vrai), les dégâts/flash/
## chiffre/mort s'appliquent quand même, mais SANS superposer un recul
## cosmétique par-dessus une timeline en cours (le corrompre est pire que
## l'omettre) — scope volontairement limité pour cette brique G, à
## reconsidérer si Milan le juge insuffisant en jeu réel.
##
## Phase R4 (game feel Milan, bac à sable : knockback_distance_px=27) :
## défaut `recoil_strength_px` remonté de 24.0 à 27.0 — même défaut que
## Enemy.take_damage()/BossGateMaw.take_damage(), même raisonnement dans
## les 3 (voir Enemy.gd). Affecte Bras-Faux/Poing Tellurique/Gueule Vide
## (qui n'ont jamais fixé leur propre recoil_strength_px) et le
## projectile de Ranged côté joueur — pas les tiers du combo ni les 4
## attaques du boss, qui passent déjà leur propre valeur explicite.
func take_damage(amount: float, source_position: Vector2, recoil_strength_px: float = 27.0, recoil_ticks: int = 6) -> void:
	if stats.is_dead() or is_invincible():
		return
	# Carapace (Terre, Tier 3, CHANTIER A 2026-08-24) : "augmente la
	# résistance aux dégâts" — seul effet de Carapace, appliqué ICI plutôt
	# qu'un flag générique sur Stats (aucune autre compétence Terre n'a
	# besoin de modifier les dégâts subis, pas la peine de généraliser un
	# système de buffs pour un seul cas). is_carapace_active() couvre
	# ACTIVATION+ACTIVE+RECOVERY (voir sa docstring) : la réduction
	# s'applique dès que l'armure est visible à l'écran. `amount` est
	# réassigné (pas une variable locale séparée) pour que TOUT ce qui
	# suit dans cette fonction (apply_damage, le nombre de dégâts affiché)
	# lise la même valeur déjà réduite — jamais afficher un nombre plus
	# gros que les PV réellement perdus.
	if is_carapace_active():
		amount *= CARAPACE_DAMAGE_MULTIPLIER
	stats.apply_damage(amount)
	# Mandat critique probabiliste : "une seule touche reçue remet la
	# chance à 5%" — reset NET (pas une décroissance), à TOUT moment
	# (pas seulement pendant un combo). Si un combo est en cours,
	# _combo_hit_free_so_far tombe aussi à false immédiatement : ce
	# combo précis ne pourra plus jamais accorder le bonus de streak à
	# sa fin, même s'il continue et se termine après ce coup subi.
	_combo_crit_chance_percent = CRIT_BASE_CHANCE_PERCENT
	if _combo_step > 0:
		_combo_hit_free_so_far = false
	HitResponse.flash_sprite(_sprite)
	HitResponse.spawn_damage_number(amount, global_position, get_parent())
	# Phase 2.1 : le SFX d'impact vit côté ATTAQUANT (Enemy._execute_attack,
	# Projectile), même schéma que Player._try_hit() qui joue déjà le sien
	# en touchant un ennemi — pas de second son ici côté victime.
	if stats.is_dead():
		die()
		return
	if _action_lock:
		return
	var away: Vector2 = (global_position - source_position)
	if away.length_squared() < 0.0001:
		away = Vector2.RIGHT
	away = away.normalized()
	_hurt_recoil_direction = away
	_hurt_recoil_total_distance_px = recoil_strength_px
	_hurt_recoil_total_ticks = recoil_ticks
	_hurt_recoil_tick = 0
	_hurt_phase = HurtPhase.ACTIVE
	play_hurt()


## Réaction à un coup subi — pose juste l'animation/le verrou ; le recul
## lui-même vit dans _advance_hurt() (timeline dédiée, comme dash/dodge).
func play_hurt() -> void:
	if stats.is_dead():
		return
	_action_lock = true
	_sprite.play("hurt")


## Timeline de recul (G) — même construction que le recul d'Enemy
## (Phase R4 : courbe de position ease-out, AnimationComposer.
## ease_out_step_px()), mais posée comme phase à part (ACTIVE/NONE) pour
## être consultée par le if/elif de _physics_process() AVANT
## _handle_movement(), qui écraserait sinon `velocity` dès ce même tick si
## une touche de mouvement est tenue.
func _advance_hurt() -> void:
	if _hurt_recoil_tick < _hurt_recoil_total_ticks:
		_hurt_recoil_tick += 1
		var step_px: float = AnimationComposer.ease_out_step_px(
			_hurt_recoil_tick, _hurt_recoil_total_ticks, _hurt_recoil_total_distance_px)
		velocity = _hurt_recoil_direction * (step_px * Engine.physics_ticks_per_second)
	if _hurt_recoil_tick >= _hurt_recoil_total_ticks:
		_end_hurt()


func _end_hurt() -> void:
	_hurt_phase = HurtPhase.NONE
	_hurt_recoil_tick = 0
	_hurt_recoil_total_ticks = 0
	velocity = Vector2.ZERO
	_action_lock = false


## Direction du dash : l'input courant s'il y en a un (esquive dirigée,
## standard pour ce type d'action), sinon `facing` (dash "en avant" à
## l'arrêt) — jamais une direction nulle.
func play_dash() -> void:
	if stats.is_dead() or _action_lock:
		return
	var input_dir := Vector2(
		Input.get_action_strength("ui_right") - Input.get_action_strength("ui_left"),
		Input.get_action_strength("ui_down") - Input.get_action_strength("ui_up")
	)
	var dir := input_dir
	if dir.length_squared() < 0.0001:
		dir = facing
	if dir.length_squared() < 0.0001:
		dir = Vector2.DOWN
	_dash_direction = dir.normalized()

	_action_lock = true
	_dash_phase = DashPhase.ANTICIPATION
	_dash_tick = 0
	_dash_step_absolute_tick = 0
	_sprite.play("dash")
	if _dash_direction.x != 0.0:
		_sprite.flip_h = _dash_direction.x < 0.0

	# "shake light dès le premier tick, axe opposé au déplacement" —
	# déclenché ici, au tout premier tick de l'action (l'anticipation),
	# pas seulement au moment où le déplacement démarre.
	CombatFeedback.trigger_shake("light", _dash_direction)
	Sfx.play("whoosh")


## Même règle de direction que play_dash() (input courant sinon facing,
## jamais nul) — l'esquive DOIT pouvoir se diriger, c'est tout son intérêt
## défensif (s'écarter d'une attaque, pas juste "avancer plus vite").
##
## Placeholder visuel (mandat §1.3 : "le squelette logique... se code
## immédiatement avec un placeholder visuel ; l'animation dédiée se génère
## avec le lot v3") : réutilise l'anim "dash" ET les données squash/lean/
## afterimages de "dash" dans data/animation_composer/cendre.json — l'
## esquive est visuellement un dash pour l'instant, mais logiquement une
## action séparée (sa propre timeline de ticks, son propre cooldown, ses
## propres i-frames). Remplacer par une vraie anim "esquive" dédiée reste
## à faire une fois le lot v3 régénéré (pas dans le scope de cette brique).
func play_dodge() -> void:
	if stats.is_dead() or _action_lock or _dodge_cooldown_remaining > 0:
		return
	var input_dir := Vector2(
		Input.get_action_strength("ui_right") - Input.get_action_strength("ui_left"),
		Input.get_action_strength("ui_down") - Input.get_action_strength("ui_up")
	)
	var dir := input_dir
	if dir.length_squared() < 0.0001:
		dir = facing
	if dir.length_squared() < 0.0001:
		dir = Vector2.DOWN
	_dodge_direction = dir.normalized()

	_action_lock = true
	_dodge_phase = DodgePhase.ANTICIPATION
	_dodge_tick = 0
	_dodge_step_absolute_tick = 0
	_sprite.play("dash")
	if _dodge_direction.x != 0.0:
		_sprite.flip_h = _dodge_direction.x < 0.0


## Timeline déclarative du dash (B4) — ANTICIPATION (bref arrêt, buste
## "planté" avant le départ) -> MOVE (burst avec ease-out, DASH_DISTANCE_PX
## répartis sur DASH_MOVE_TICKS, pas une téléportation en un seul tick)
## -> RECOVERY (glissade qui décélère au sol, jamais un arrêt nul). Même
## discipline que _advance_combo() : ne dépend jamais de la durée réelle
## de lecture du sprite.
func _advance_dash() -> void:
	_dash_tick += 1
	_dash_step_absolute_tick += 1
	var dash_data: Dictionary = _animation_composer_data.get("dash", {})
	# Smear procédural (mandat "fluidité") REMPLACE l'ancienne impulsion
	# squash figée du JSON (voir AnimationComposer.apply_motion_smear) —
	# celle-ci étirait toujours l'axe horizontal peu importe la direction
	# réelle du dash, fausse dès qu'on quitte l'axe est/ouest. Le smear lui-
	# même est appliqué APRÈS le `match` ci-dessous (une fois `velocity`
	# recalculée pour CE tick), pas ici.
	AnimationComposer.apply_lean(_sprite, float(dash_data.get("lean_deg", 0.0)), _dash_direction,
		int(dash_data.get("lean_start_tick", 0)), int(dash_data.get("lean_end_tick", 0)), _dash_step_absolute_tick)
	_apply_afterimages(dash_data, _dash_step_absolute_tick)
	match _dash_phase:
		DashPhase.ANTICIPATION:
			velocity = Vector2.ZERO
			# Garantit l'échelle neutre au tout début du dash — plus de
			# apply_squash() ici pour la remettre à Vector2.ONE par défaut
			# à chaque tick (voir le smear plus bas, qui ne touche PLUS le
			# scale tant qu'il n'y a pas de vitesse réelle).
			_sprite.scale = Vector2.ONE
			if _dash_tick >= DASH_ANTICIPATION_TICKS:
				_dash_phase = DashPhase.MOVE
				_dash_tick = 0
		DashPhase.MOVE:
			var progress_before: float = _ease_out_quad(float(_dash_tick - 1) / DASH_MOVE_TICKS)
			var progress_after: float = _ease_out_quad(float(_dash_tick) / DASH_MOVE_TICKS)
			var step_px: float = (progress_after - progress_before) * DASH_DISTANCE_PX
			velocity = _dash_direction * (step_px * Engine.physics_ticks_per_second)
			# Phase 2.3 : directionalStreak actif UNIQUEMENT pendant MOVE (le
			# joueur est réellement rapide ici), jamais pendant ANTICIPATION/
			# RECOVERY — "jamais permanent" (§10.2).
			_fx_material.set_shader_parameter("streak_direction", _dash_direction)
			_fx_material.set_shader_parameter("streak_amount", 0.8)
			if _dash_tick >= DASH_MOVE_TICKS:
				_dash_phase = DashPhase.RECOVERY
				_dash_tick = 0
				_dash_recovery_velocity = _dash_direction * DASH_RECOVERY_INITIAL_SPEED_PX_S
				_fx_material.set_shader_parameter("streak_amount", 0.0)
		DashPhase.RECOVERY:
			velocity = _dash_recovery_velocity
			_dash_recovery_velocity = _dash_recovery_velocity.move_toward(
				Vector2.ZERO, DASH_RECOVERY_INITIAL_SPEED_PX_S / DASH_RECOVERY_TICKS)
			if _dash_tick >= DASH_RECOVERY_TICKS:
				_end_dash()
	# Smear procédural — lit `velocity` FRAÎCHEMENT calculée ci-dessus pour
	# CE tick (nulle en ANTICIPATION, pic en MOVE, décroissance en
	# RECOVERY), voir AnimationComposer.apply_motion_smear().
	AnimationComposer.apply_motion_smear(_sprite, velocity)


## Décélération quadratique (rapide puis qui s'adoucit) — "vitesse max
## avec ease-out" du mandat : plein régime dès le premier tick de MOVE,
## puis chaque tick suivant couvre un peu moins de distance.
func _ease_out_quad(x: float) -> float:
	var c: float = clampf(x, 0.0, 1.0)
	return 1.0 - (1.0 - c) * (1.0 - c)


func _end_dash() -> void:
	_dash_phase = DashPhase.NONE
	_dash_tick = 0
	velocity = Vector2.ZERO
	_action_lock = false
	# Même garde-fou que _end_combo() ci-dessus.
	_sprite.scale = Vector2.ONE
	_sprite.rotation_degrees = 0.0
	_fx_material.set_shader_parameter("streak_amount", 0.0)


## Timeline déclarative de l'esquive — même construction en 3 phases que
## _advance_dash() (anticipation plantée -> déplacement ease-out -> recovery
## qui glisse), mais SANS la moindre fenêtre d'i-frames en dehors de la
## phase ACTIVE (is_invincible() ci-dessus ne consulte que _dodge_phase).
## Réutilise les données squash/lean/afterimages de "dash" dans
## data/animation_composer/cendre.json (placeholder visuel, voir
## play_dodge()) — pas une nouvelle entrée JSON dupliquée pour l'instant.
func _advance_dodge() -> void:
	_dodge_tick += 1
	_dodge_step_absolute_tick += 1
	var dash_data: Dictionary = _animation_composer_data.get("dash", {})
	# Smear procédural (mandat "fluidité") REMPLACE ici aussi l'ancienne
	# impulsion squash figée — même raisonnement que _advance_dash().
	AnimationComposer.apply_lean(_sprite, float(dash_data.get("lean_deg", 0.0)), _dodge_direction,
		int(dash_data.get("lean_start_tick", 0)), int(dash_data.get("lean_end_tick", 0)), _dodge_step_absolute_tick)
	_apply_afterimages(dash_data, _dodge_step_absolute_tick)
	match _dodge_phase:
		DodgePhase.ANTICIPATION:
			velocity = Vector2.ZERO
			_sprite.scale = Vector2.ONE  # voir le même garde-fou dans _advance_dash()
			if _dodge_tick >= DODGE_ANTICIPATION_TICKS:
				_dodge_phase = DodgePhase.ACTIVE
				_dodge_tick = 0
		DodgePhase.ACTIVE:
			var progress_before: float = _ease_out_quad(float(_dodge_tick - 1) / DODGE_ACTIVE_TICKS)
			var progress_after: float = _ease_out_quad(float(_dodge_tick) / DODGE_ACTIVE_TICKS)
			var step_px: float = (progress_after - progress_before) * DODGE_DISTANCE_PX
			velocity = _dodge_direction * (step_px * Engine.physics_ticks_per_second)
			if _dodge_tick >= DODGE_ACTIVE_TICKS:
				_dodge_phase = DodgePhase.RECOVERY
				_dodge_tick = 0
				_dodge_recovery_velocity = _dodge_direction * DODGE_RECOVERY_INITIAL_SPEED_PX_S
		DodgePhase.RECOVERY:
			velocity = _dodge_recovery_velocity
			_dodge_recovery_velocity = _dodge_recovery_velocity.move_toward(
				Vector2.ZERO, DODGE_RECOVERY_INITIAL_SPEED_PX_S / DODGE_RECOVERY_TICKS)
			if _dodge_tick >= DODGE_RECOVERY_TICKS:
				_end_dodge()
	AnimationComposer.apply_motion_smear(_sprite, velocity)


func _end_dodge() -> void:
	_dodge_phase = DodgePhase.NONE
	_dodge_tick = 0
	velocity = Vector2.ZERO
	_action_lock = false
	_dodge_cooldown_remaining = DODGE_COOLDOWN_TICKS
	# Même garde-fou que _end_combo()/_end_dash() ci-dessus.
	_sprite.scale = Vector2.ONE
	_sprite.rotation_degrees = 0.0


## Fantôme de traînée (B4, généralisé au combo en J2 — voir
## _apply_afterimages()) — PAS une primitive VfxDirector (§7.1, contrat
## seed/configure générique) : copie la texture/frame COURANTE du sprite
## du joueur, une donnée que seul Player possède. `Sprite2D` autonome,
## parenté au même parent que Player (jamais à Player lui-même, sinon il
## suivrait son mouvement au lieu de rester "planté" derrière lui) —
## s'éteint tout seul via un Tween sur son opacité, jamais géré par
## VfxDirector/VfxBudget (ce n'est pas dans leur périmètre, §8.2).
func _spawn_afterimage(opacity: float) -> void:
	var texture: Texture2D = _sprite.sprite_frames.get_frame_texture(_sprite.animation, _sprite.frame)
	if texture == null:
		return
	var ghost := Sprite2D.new()
	ghost.texture = texture
	ghost.offset = _sprite.offset
	ghost.flip_h = _sprite.flip_h
	ghost.z_index = _sprite.z_index - 1
	ghost.modulate = Color(1.0, 1.0, 1.0, opacity)
	# add_child() AVANT de fixer global_position : le calcul global_position
	# a besoin de la transform du parent, indisponible tant que le nœud
	# n'est pas encore dans l'arbre.
	get_parent().add_child(ghost)
	ghost.global_position = _sprite.global_position
	var tween: Tween = ghost.create_tween()
	tween.tween_property(ghost, "modulate:a", 0.0, AFTERIMAGE_FADE_SEC)
	tween.finished.connect(ghost.queue_free)


func _on_sprite_animation_finished() -> void:
	if _combo_step > 0:
		return  # le combo gère son propre verrou via sa timeline de ticks (_end_combo())
	if _dash_phase != DashPhase.NONE:
		return  # le dash gère son propre verrou via sa timeline de ticks (_end_dash())
	if _dodge_phase != DodgePhase.NONE:
		return  # l'esquive gère son propre verrou via sa timeline de ticks (_end_dodge())
	if _bras_faux_phase != BrasFauxPhase.NONE:
		return  # Bras-Faux gère son propre verrou via sa timeline de ticks (_end_bras_faux())
	if _poing_belluaire_phase != PoingBelluairePhase.NONE:
		return  # même discipline (_end_poing_belluaire())
	if _poing_tellurique_phase != PoingTelluriquePhase.NONE:
		return  # même discipline (_end_poing_tellurique())
	if _maree_de_sable_phase != MareeDeSablePhase.NONE:
		return  # même discipline (_end_maree_de_sable())
	if _corbeau_pale_phase != CorbeauPalePhase.NONE:
		return  # même discipline (_end_corbeau_pale())
	if _poing_du_colosse_phase != PoingDuColossePhase.NONE:
		return  # même discipline (_end_poing_du_colosse())
	if _oeil_sans_regard_phase != OeilSansRegardPhase.NONE:
		return  # même discipline (_end_oeil_sans_regard())
	if _serpent_creux_phase != SerpentCreuxPhase.NONE:
		return  # même discipline (_end_serpent_creux())
	if _hurt_phase != HurtPhase.NONE:
		return  # le recul gère son propre verrou via sa timeline de ticks (_end_hurt())
	if _sprite.animation == "mort":
		return  # reste sur la dernière frame, jamais reverrouillé sur idle
	_action_lock = false


func die() -> void:
	stats.hp = 0.0
	_combo_step = 0
	_combo_phase = ComboPhase.NONE
	_attack_queued = false
	_hurt_phase = HurtPhase.NONE
	_dash_phase = DashPhase.NONE
	_dodge_phase = DodgePhase.NONE
	_bras_faux_phase = BrasFauxPhase.NONE
	_poing_belluaire_phase = PoingBelluairePhase.NONE
	_poing_tellurique_phase = PoingTelluriquePhase.NONE
	_maree_de_sable_phase = MareeDeSablePhase.NONE
	# CHANTIER A (Terre, 2026-08-24) : les 3 compétences Terre à impact
	# ponctuel/état soutenu ajoutées ce chantier manquaient ici — constaté
	# en capture (carapace_active en armure PUIS l'armure disparaît sans
	# jamais passer par "carapace_fin" quand le joueur meurt en plein
	# ACTIVE, ex. les 2 placeholders de capture_scene.gd qui restent au
	# contact tout du long). Sans ce reset, _carapace_phase (ou
	# _effondrement_phase/_fissure_eruptive_phase) reste bloqué sur une
	# valeur != NONE alors que _action_lock est déjà remis à `true` deux
	# lignes plus bas par mort — cohérent avec le patron déjà en place pour
	# bras_faux/poing_belluaire/poing_tellurique/maree_de_sable ci-dessus,
	# pas une exception nouvelle.
	_carapace_phase = CarapacePhase.NONE
	_effondrement_phase = EffondrementPhase.NONE
	_fissure_eruptive_phase = FissureEruptivePhase.NONE
	_corbeau_pale_phase = CorbeauPalePhase.NONE
	_poing_du_colosse_phase = PoingDuColossePhase.NONE
	_oeil_sans_regard_phase = OeilSansRegardPhase.NONE
	_serpent_creux_phase = SerpentCreuxPhase.NONE
	_action_lock = true
	_death_ticks = 0
	_sprite.play("mort")
	Sfx.play("death")


## MANDAT "retours de playtest réel" (point 1) — appelée chaque tick tant
## que `stats.is_dead()` (voir le early-return ajouté dans _physics_process),
## à la place de tout le reste (mouvement/attaque/pouvoirs restent tous
## verrouillés par `stats.is_dead()` déjà vérifié dans chacune de leurs
## fonctions d'entrée, mais rien ne les court-circuitait explicitement ici
## avant ce mandat — d'où le softlock : la boucle continuait de tourner
## sans jamais rien faire de nouveau). "attack" réutilisé comme touche de
## relance plutôt qu'une nouvelle action dédiée : déjà bindé clavier+souris
## (voir commentaire en tête de fichier), aucun nouvel écran/asset à
## inventer pour ce mandat.
func _process_death_restart() -> void:
	_death_ticks += 1
	if _death_ticks < DEATH_RESTART_INPUT_ENABLED_TICKS:
		return
	if Input.is_action_just_pressed("attack"):
		RunState.start_new_run()
