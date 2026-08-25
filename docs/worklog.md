# Worklog — Rank Zero

## 2026-08-24 — CHANTIER C (PLAN DE PRODUCTION v1) : Monstres, animations d'interaction

**Contexte.** Agent indépendant, chantier "Monstres : animations
d'interaction" du PLAN DE PRODUCTION vers la v1 complète (réaction
directionnelle 4 directions min/monstre, chancellement sur enchaînement,
projection + rebond pour les monstres légers, réaction différenciée par
poids — recoil_multiplier existait déjà en code, PAS l'animation).

**Vérifié avant de commencer (état réel, jamais supposé)** : les 3 rigs
Meshy sont toujours valides et déjà téléchargés localement
(`experiments/monsters_nuit/meshy_output_v2/{crawler,brute}_final_rigged.glb`
— rig manuel Blender, 13/12 os — et `ranged_rigged.glb` — auto-rig Meshy
réussi, squelette Mixamo-like `Hips/Spine*/Left-RightArm/.../neck/Head`,
`rig_task_id=01a024b4-...` déjà payé le 2026-08-21). `crawler_frames.tres`/
`brute_frames.tres` n'avaient que idle+attaque (1 frame chacune, aucune
notion de direction) + marche (4 frames, Phase 2 MANDAT AUTONOME v3) ;
`ranged_frames.tres` idem + mort (6 frames). Bones confirmés par script
(`list_bones.py`, headless) avant toute pose : Crawler
`pelvis/chest/neck/head/front_{L,R}_upper/lower/back_{L,R}_upper/lower/tail`,
Brute `pelvis/chest/neck/head/arm_{L,R}_upper/lower/leg_{L,R}_upper/lower`,
Ranged `Hips/Spine02/Spine01/Spine/neck/Head/Left-RightArm/ForeArm/Hand/
Left-RightUpLeg/Leg/Foot`.

**Décision technique (les 3 monstres, même pipeline)** : AUCUN appel
Meshy — mêmes rigs déjà payés, poses à la main sur le squelette existant
(même technique que `pose_walk_{crawler,brute}.py` déjà en place pour la
marche, généralisée à Ranged qui n'avait jamais reçu cette technique
jusqu'ici — testée et confirmée fonctionnelle sur son squelette Mixamo-
like par un rendu de calibration avant de figer les poses finales).
3 nouveaux scripts `experiments/blender_capture/pose_hit_reactions_
{crawler,brute,ranged}.py`, même cadrage que idle/attaque/marche
(`cam_size=2.6`, `target_z` par monstre déjà établi), `quantize.py`
réutilisé tel quel (`--target_saturation=0.55`, réglages par défaut
sinon — même calibration que le reste de chaque monstre, aucun paramètre
retouché). **14 poses rendues, 0 crédit Meshy** (solde avant/après
vérifié : 823/823) :
- Crawler (léger, `recoil_multiplier=1.6`) : `touche_lateral`/
  `touche_avant`/`touche_arriere`/`chancelle`/`projete` (5).
- Brute (lourd, `recoil_multiplier=0.35`) : `touche_lateral`/
  `touche_avant`/`touche_arriere`/`chancelle` (4, PAS de `projete` —
  "encaisse sans bouger" est une trait catégorique, amplitudes de
  rotation ~2× plus faibles que Crawler sur les 4 poses, cf. docstring
  du script).
- Ranged (léger, `recoil_multiplier=1.4`) : mêmes 5 que Crawler.

**Câblage jeu (`src/gameplay/enemy.gd`)** — la logique de sélection
n'existait pas côté ennemi avant cette passe (le mandat le confirmait) :
- **4 directions minimum** : `_select_directional_reaction()` classe le
  coup entrant sur l'axe DOMINANT du vecteur "vers l'attaquant" (opposé
  de `away`, déjà calculé par `take_damage()`) — latéral (une seule pose
  `touche_lateral` + `flip_h`, canonique = coup venu de la droite, même
  convention que le flip_h déjà utilisé pour le déplacement) sinon avant/
  arrière (2 poses distinctes, `touche_avant`/`touche_arriere` — "avant"
  = attaquant côté caméra, convention fixée une fois, jamais réinterprétée
  ailleurs). Posée immédiatement dans `_on_hit_reaction()`, appelée par
  `take_damage()` sur tout coup NON mortel (la mort garde sa propre
  priorité, `_die()`/anim "mort").
- **Chancellement (enchaînement)** : `STAGGER_TRIGGER_HITS=3` coups en
  moins de `STAGGER_WINDOW_TICKS=50` (tick source :
  `Engine.get_physics_frames()`, compteur autoritatif, jamais un
  compteur maison) arment `State` "chancelle" — consommé par
  `_physics_process` UNE FOIS le recul (+ rebond éventuel) du coup
  déclencheur écoulé (jamais à la place, l'impact de ce coup précis
  reste visible avant le vacillement). Pilotage tick-exact : `flip_h`
  bascule à cadence FIXE (`STAGGER_FLIP_PERIOD_TICKS=6`, jamais le FPS
  autonome de l'anim) pour simuler un vacillement gauche-droite sans
  frame supplémentaire — même discipline que `<SKILL>_FRAME_TICK_BOUNDS`/
  `_frame_for_tick()` côté Player, appliquée ici à l'ennemi comme demandé
  par le mandat.
- **Projection + rebond (monstres légers)** : PUREMENT dérivé de
  `sprite_frames.has_animation("projete")` — aucun 2e seuil numérique à
  synchroniser avec `recoil_multiplier` (Crawler/Ranged en ont une,
  Brute non, cohérent avec la discipline du fichier "pas de variation
  que le runtime peut dériver d'une configuration existante"). La pose
  d'impact directionnelle tient `IMPACT_POSE_HOLD_TICKS=2` puis cède la
  place à `projete` pour le reste du recul (déjà mis à l'échelle par
  `recoil_multiplier`, aucune 2e distance à gérer), puis un rebond
  procédural (`_advance_bounce()`, décalage vertical du sprite en
  cloche/sin — même technique que le bob de marche déjà en place,
  aucune frame supplémentaire) avant de rendre la main à l'IA.

**Vérification.**
`bash scripts/run_gameplay_smoke_test.sh` → `"all_pass":true`, 89 checks
(86 existants inchangés + 3 nouveaux) :
- `crawler_hit_reaction_differs_by_incoming_direction` — droite/gauche/
  face/dos donnent 3 anims distinctes + `flip_h` correctement inversé
  entre droite et gauche.
- `brute_staggers_after_three_consecutive_hits_in_window_not_before` —
  2 coups n'arment PAS le chancellement, le 3e si, "chancelle" joue
  effectivement après le recul.
- `crawler_is_projected_and_bounces_brute_stays_planted` — Crawler
  traverse "projete" + rebond, déplacement mesuré 43.2px (27×1.6) vs
  Brute 9.45px (27×0.35, ratio ~4.6×), Brute n'a pas de "projete" et ne
  rebondit jamais.

`godot4 --headless --rendering-driver vulkan --import` propre après
chaque changement (les erreurs `corbeau_pale`/`poing_du_colosse`/
`oeil_sans_regard`/`serpent_creux` observées dans les logs sont d'un
AUTRE agent en cours en parallèle sur les compétences Cendre — fichiers
non touchés par ce chantier, vérifié via `git status`).

**Nouveau mode de capture** (`tools/capture_scene.gd`,
`--mode=enemy_hit_reaction`) : instancie un monstre réel, lui inflige
`--hits` coups depuis `--direction`, capture une SÉQUENCE de frames (pas
une pose isolée — discipline de vérification du mandat). 15 séquences
capturées (3 monstres × 4 directions + 3 monstres × combo 3 coups),
0 crédit Meshy (rendu Godot local, `xvfb-run` + Vulkan logiciel, même
écart documenté que le reste du pipeline de capture).

### Capture livrée

`captures/verification/2026-08-24-chantier-c-monstres-hitresponse/` —
9 planches synthétiques (recadrées + upscale ×4, étiquetées) :
- `{crawler,brute,ranged}_directions.png` : les 4 réactions
  directionnelles côte à côte (tick 1, juste après l'impact — avant le
  flash et avant le swap vers "projete").
- `{crawler,ranged}_projection_bounce.png` : séquence 9 ticks (t0→t38)
  montrant idle → flash → `projete` → rebond → réinstallation, avec un
  déplacement horizontal visible sur toute la séquence.
- `brute_planted_no_projection.png` : même séquence de ticks sur Brute —
  silhouette qui reste au même endroit à l'écran du premier au dernier
  tick, contraste direct avec les 2 planches ci-dessus.
- `{crawler,brute,ranged}_stagger.png` : séquence 3-coups → chancelle.

### Verdict honnête, par monstre et par type de réaction

- **Directionnel (4 min.)** : FAIT sur les 3 monstres. Crawler/Ranged
  nettement lisibles (poses très différentes : cabrage avant, hunch
  arrière, lean latéral miroir). Brute lisible en jeu réel (couleurs/
  silhouette) mais SUBTIL sur les captures recadrées à cette résolution
  — amplitude de rotation volontairement réduite (~moitié) pour rester
  cohérent avec "encaisse sans bouger", mesurable/vérifié par le smoke
  test mais pas toujours évident à l'œil sur une planche 64px. Point à
  retester en jeu réel par Milan avant de trancher si l'amplitude Brute
  doit remonter.
- **Chancellement** : FAIT, générique aux 3 archétypes (ne dépend pas du
  poids). Vérifié par smoke test (armement au 3e coup, pas avant) et
  visible en capture (planches `*_stagger.png`) — wobble présent mais
  lui aussi plus subtil sur Brute que sur Crawler/Ranged à cette
  résolution, même remarque que ci-dessus.
- **Projection + rebond (légers)** : FAIT sur Crawler ET Ranged (les 2
  archétypes "légers" du jeu, `recoil_multiplier` 1.6/1.4 — le mandat ne
  nommait explicitement que le Crawler, Ranged inclus par cohérence avec
  le même statut de poids). Nettement visible en capture (déplacement
  horizontal net sur toute la séquence de rebond).
- **Différenciation par poids** : FAIT et le plus net des 4 — la
  planche `brute_planted_no_projection.png` montre une silhouette
  immobile à l'écran sur 38 ticks, à comparer directement aux 2 planches
  `*_projection_bounce.png` qui montrent un déplacement continu. Chiffres
  à l'appui (smoke test) : 43.2px de recul mesuré pour Crawler contre
  9.45px pour Brute sur un coup de force identique.

### Ce qui reste / non fait

- Amplitude des poses Brute : fonctionnelle et vérifiée par test, mais
  visuellement plus discrète que souhaitable sur une planche recadrée —
  resserrage éventuel à trancher par Milan après test en jeu réel (pas
  un bug, un choix de calibration).
- Pas de nouvelle pose "rebond" dédiée : le rebond est 100% procédural
  (décalage vertical du sprite, même technique que le bob de marche
  déjà en place) — décision délibérée pour rester dans le budget de ce
  chantier, cohérente avec la discipline du fichier ("pas de frame que
  le runtime peut dériver"), mais signalée ici en cas de désaccord.
- Aucune 5e/6e direction (diagonales) — le mandat demandait "4 minimum",
  non fait au-delà.

### Fichiers modifiés

`src/gameplay/enemy.gd` (constantes/état
STAGGER_*/IMPACT_POSE_HOLD_TICKS/BOUNCE_*, `_on_hit_reaction()`/
`_select_directional_reaction()`/`_apply_hit_reaction()`/
`_advance_bounce()`/`_advance_stagger()`, gates `_physics_process`),
`assets/processed/sprites/{crawler,brute,ranged}/*_frames.tres` (5/4/5
nouvelles animations), 14 nouveaux PNG 64×64 dans ces mêmes dossiers,
`experiments/blender_capture/pose_hit_reactions_{crawler,brute,
ranged}.py` (nouveaux), `tools/capture_scene.gd`
(`--mode=enemy_hit_reaction`), `tools/smoke_test_gameplay.gd` (3
nouveaux checks + leurs 3 appels dans `_ready()`),
`captures/verification/2026-08-24-chantier-c-monstres-hitresponse/` (9
fichiers). **0 crédit Meshy dépensé** (solde 823cr avant/après,
vérifié — tout le travail vient de rendu Blender local sur des rigs déjà
payés).

Journal de session, §16.5 de `docs/ARCHITECTURE_VFX_v3.md` : "Fin de
session : mettre à jour docs/worklog.md (fait / branché ou non /
prochain pas). C'est la mémoire inter-sessions — le repo est le cerveau."

**Archives** (MANDAT AUTONOME v3 Phase 4, housekeeping — ce fichier
dépassait 6300 lignes) : les entrées du 2026-08-18 au 2026-08-21 inclus
sont déplacées telles quelles, sans réécriture, dans
`docs/worklog-archive-2026-08-18-a-2026-08-21.md`. Résumé de cette
période, pour ne pas perdre le fil sans tout relire : fondations
(Phase 0-1, squelette gameplay/combo/dash/esquive), monde (mini-tileset,
3 monstres Crawler/Brute/Ranged), Phase T.1 (6 outils autonomes pipeline
Meshy/Blender/pyfxr), Phase 1-4 MANDAT SUITE v2 (éclairage/couleur,
biome PixelLab, Poing Belluaire/Poing Tellurique, son+normal maps+post-
render), retours croisés Gemini/ChatGPT (R1 bug bloquant, R4 feedback
d'impact), zoom caméra, calibration render_detector.py, verrouillage
palette Terre, système Pouvoir/déblocage (RunState.active_power, 5
slots réels), critique probabiliste ("Black Flash"). Ce fichier ne
garde que le 2026-08-22 (MANDAT AUTONOME v3 en cours) — au-delà de
~1500 lignes, archiver la période précédente selon le même principe.

---

## 2026-08-23 — MANDAT MIGRATION CENDRE : pilote 3D Meshy/Blender du combo de base (3 coups)

**Contexte.** Décision de Milan : migrer Cendre du pipeline 2D PixelLab
(4-6 poses/compétence, dérive possible entre frames) vers le pipeline
3D Meshy/Blender déjà éprouvé sur Crawler/Brute/Ranged (frames = temps
de rendu Blender, cohérence garantie). Ce mandat est un PILOTE : un
seul livrable (combo 3 coups haute densité), pas de généralisation, pas
de régénération des compétences existantes, pas de bascule en jeu.

**Étape 1 — modèle.** Source : `reference_v3_turnaround_raw.png`
(panneaux FACE/3-4/PROFIL/DOS, sans cape — vérifié visuellement, aucune
confusion avec `reference_v1_archive.png`/`reference_v2_archive.png`
qui portent une cape). 4 crops serrés (bbox non-fond + marge 6px)
générés dans `experiments/blender_capture/cendre_pilot/tight_{face,3-4,
profil,dos}.png`, même discipline que `crop_refs.py` pour les 3
monstres. `meshy_multi_image_to_3d` (meshy-6/latest, 4 vues, sans
`pose_mode` pour préserver la posture réelle — même règle que les
monstres) : **30cr**. Vérification de posture AVANT tout rig (rendu
Blender rapide, `posture_check.png`) : bipède debout conforme à la
référence, harnais/tunique déchirée/bottes fidèles. `meshy_remesh`
(target_polycount=250000, resize_height=1.75m — aucune hauteur Cendre
documentée ailleurs dans le repo, valeur humaine standard assumée et
notée ici, resize_height plutôt qu'auto_size pour rester dans la
convention déjà utilisée sur les monstres — origin_at=bottom) : **5cr**.

**Rig — verdict honnête : auto-rig Meshy réussi du premier coup, aucun
contournement manuel nécessaire.** Conforme à l'attente du mandat
(Cendre = bipède en posture standard, contrairement au Crawler
quadrupède et au Brute accroupi qui avaient échoué en 422 "Pose
estimation failed"). `meshy_rig` : **5cr**, marche+course incluses
gratuitement. Les scripts `rig_final_brute.py`/`rig_manual_test*.py`
(fusion de doublons + armature manuelle) n'ont pas été nécessaires ce
tour — gardés en réserve si un futur re-rig échoue.

**Étape 2 — pilote combo.** `meshy_animate` avec l'action de
bibliothèque `Punch_Combo` (action_id=198, catégorie Fighting/Punching,
identifiée via la doc Meshy - même famille que les actions déjà
utilisées sur les monstres type `Crouch_Pull_and_Throw`/`Heavy_Hammer_
Swing`) : **3cr**. **Scouting AVANT tout rendu final** (discipline
"vérifier avant de croire") : 2 passes de rendu low-res (24 puis 48
frames, `preview_scout.py`) ont montré que `Punch_Combo` ne contient
que **2 frappes distinctes** (une croix ~frame 16-18, un uppercut
~frame 34-35), bookées par une garde statique en début/fin de clip
(0.8-10 et 41-60) — pas 3 comme le nom générique le laissait supposer.
Conforme au mandat ("pars d'un mouvement de bibliothèque... puis
retouche-le par script Blender") : le 3e coup a été posé à la main sur
le même squelette rigué (bones `LeftArm`/`LeftForeArm`/`Spine`, même
technique que `pose_walk_brute.py`/`pose_walk_crawler.py`), amorcé
depuis la dernière frame mocap (49, quasi-bind-pose de garde) pour que
la coupure mocap→pose-à-la-main soit invisible. Axes calibrés
empiriquement par rendus-test isolés avant tout coup manuel (le rig
Meshy n'a pas de convention d'axe documentée, et `LeftArm`/`RightArm`
ne sont PAS symétriques en signe — confirmé par test : `rx=-90°` lève
le bras gauche, il faut `rx=+90°` pour un effet symétrique sur le bras
droit).

**Répartition des frames (règle de la Bible d'animation — dense à
l'anticipation, 2-3 frames au contact, étalé à la récupération, PAS
uniforme) :**
- Coup 1 (croix, mocap pur) : 8 anticipation + 2 contact + 3
  récupération = 13 frames.
- Transition 1→2 (fondu, mocap pur, zone de garde-reset partagée) : 3
  frames.
- Coup 2 (uppercut, mocap pur) : 5 anticipation (dont les 3 de
  transition) + 2 contact + 3 récupération = 13 frames effectives (10
  propres).
- Transition 2→3 (mocap pur, queue de garde qui sert de pont vers la
  pose à la main) : 3 frames.
- Coup 3 (crochet gauche, posé à la main) : 7 anticipation + 2 contact
  + 4 récupération = 13 frames.
- **Total : 42 frames rendues** (Cycles CPU, 512×512, 32 samples,
  cadrage à échelle commune comme `rig_final_brute.py` — un seul
  process Blender, un seul import, `render_combo_cendre.py`).

**Post-traitement** : `quantize.py` avec les paramètres par défaut déjà
calibrés sur les monstres (`target_pixels=96` — plus grand que le
canvas cuit 64×64 pour rester lisible en comparaison, `target_
saturation=0.10` inchangé), aucun paramètre retouché.

**Point de vigilance identité (couleur/désaturation) — vérifié par
mesure, pas affirmé.** `measure_saturation.py` (saturation HSV moyenne
sur les pixels non-transparents) :
- PixelLab existant (`coup1/2/3`, frame 2) : saturation moyenne
  0.0801 / 0.0773 / 0.0761.
- Rendu Meshy BRUT (avant quantize), frames de contact : 0.0914 /
  0.0960 / 0.0855 — légèrement au-dessus mais même ordre de grandeur
  (aucune couleur vive, pas de recoloration franche).
- Rendu Meshy QUANTIFIÉ (après `quantize.py`, mêmes frames) : 0.0670 /
  0.0692 / 0.0666 — **plus désaturé que le PixelLab existant**, pas
  moins.
Verdict : la migration ne recolore pas Cendre, mesuré et non simplement
observé. Mécanisme du contre-poids anti-CanvasModulate
(`src/vfx/shaders/canvas_modulate_compensate.gdshader`) vérifié par
lecture directe de `scenes/gameplay/gate_premiere.tscn` (ligne 322,
`material = SubResource("8")` posé sur le node `AnimatedSprite2D` de
`Player`) : c'est un matériau appliqué au niveau de la SCÈNE sur le
node sprite, agnostique de la source des pixels (2D PixelLab ou 3D
baké) — il ne fait que diviser par la couleur du `CanvasModulate`
parent pour l'annuler, il ne désature RIEN lui-même (c'est
`quantize.py` qui fait ce travail, confirmé ci-dessus). Conclusion
honnête : le mécanisme survivrait tel quel à la migration tant que (a)
le même node `AnimatedSprite2D` reste utilisé et (b) chaque frame 3D
future passe par `quantize.py` (ou équivalent) avant intégration — pas
une garantie automatique, une dépendance de process à documenter pour
la généralisation.

**Bug connu (tranche verticale écrasée, ticks 35/15 sur Gueule
Vide/Marée de Sable, cf. entrée du 2026-08-22)** : hors scope de ce
mandat (chantier "couche code" séparé). Observation honnête demandée
par le mandat : le pipeline 3D produit un maillage skinné rendu par
Cycles, pas une image 2D composée par couches — structurellement, ce
type de "tranche écrasée" (probablement un artefact de la couche
squash&stretch appliquée à une texture 2D) n'a pas d'équivalent direct
dans le rendu 3D (pas de squash&stretch appliqué au maillage dans ce
pilote). Ce n'est PAS une preuve que le bug est éliminé par la
migration — c'est juste que ce pilote n'exerce pas le même chemin de
code (le VFX squash&stretch en jeu s'applique au node Godot au moment
du rendu, pas à Blender) ; verdict honnête : observation, pas une
correction, à re-vérifier une fois un asset 3D réellement intégré au
jeu.

**Livrable de validation** :
`captures/verification/2026-08-23-cendre-migration-3d-pilote-combo-avant-apres.png`
— une seule image, 3 blocs (un par coup), AVANT (5 frames PixelLab) au-
dessus d'APRÈS (13-16 frames 3D, frames de transition surlignées en
ambre) sur la même échelle d'affichage. Planche-contact intermédiaire
des 42 frames brutes + quantifiées gardée dans
`experiments/blender_capture/cendre_pilot/` (non committée — répertoire
de travail, pas un livrable, cohérent avec la discipline "un seul
fichier net pour Milan"). Vérifié `git check-attr filter` sur la
capture avant commit : `unspecified`, pas de LFS (ne matche ni
`assets/processed/**/*.png` ni `assets/source/**/*.png`), commit normal
confirmé.

**Coût réel mesuré (solde Meshy avant/après, `meshy_check_balance`)** :
avant = **866cr**, après = **823cr**, delta = **43cr** (30 génération +
5 remesh + 5 rig + 3 animate). Conforme à l'ordre de grandeur annoncé
par le mandat (~40cr génération + ~5cr rig + ~3cr/animation) — écart de
+3cr uniquement dû au remesh (5cr), non compté dans l'estimation
initiale de Milan.

**Chiffrage de la généralisation (obligatoire, deuxième partie du
mandat) — voir détail complet en fin d'entrée ci-dessous.** Résumé :
modèle+rig déjà payés (40cr, réutilisables pour TOUTES les animations
futures), combo déjà payé (3cr animate). Il reste 8 mouvements distincts
à financer (dash, hurt, mort, bras_faux, poing_belluaire, poing_
tellurique, invocation_gueule_vide, maree_de_sable) à ~3cr/mouvement =
24cr. **Total généralisation à la couverture directionnelle actuelle :
~67cr** (43 déjà dépensés + 24 restants). Extension à 8 directions pour
les 11 animations actuellement mono-direction : **+0cr Meshy** (la
rotation de caméra autour du même clip rigué est gratuite en 3D,
contrairement au pipeline 2D où chaque direction est une génération
PixelLab payante séparée) — coût réel = temps de rendu Blender
supplémentaire, pas des crédits.

**Fichiers modifiés/ajoutés** : `experiments/blender_capture/
render_combo_cendre.py` (script de production, réutilisable pour les
prochaines compétences), `captures/verification/2026-08-23-cendre-
migration-3d-pilote-combo-avant-apres.png`, `data/meshy_usage.jsonl`
(5 entrées : multi_image_to_3d, remesh, rig, animate, balance),
`experiments/blender_capture/cendre_pilot/` (scratch de travail :
crops, GLB téléchargés, scripts de scout/calibration, 42 frames brutes
+ quantifiées, non committé). **Aucun fichier `.tscn`/`.gd` touché,
aucun asset PixelLab supprimé, `cendre_frames.tres`/`cendre_frames_
cooked.json` non touchés** — conforme au périmètre du mandat.

**Détail du chiffrage de généralisation.**
Animations Cendre existantes (`assets/manifests/cendre_frames_cooked.json`,
27 entrées vérifiées) : idle ×8 directions, déplacement ×8 directions,
hurt, mort, dash, coup1/2/3 (combo — CE PILOTE), bras_faux, poing_
belluaire, poing_tellurique, invocation_gueule_vide, maree_de_sable —
ces 5 dernières + hurt/mort/dash/coup1-3 n'ont actuellement QU'UNE
direction chacune (pas de suffixe `_east`/`_north`/etc. dans le
manifeste), seuls idle et déplacement sont déjà couverts à 8
directions.

Modèle propriété clé de la 3D vs la 2D : en 2D PixelLab, chaque
direction est une génération payante séparée (8× le coût). En 3D, une
fois le modèle riggé et UNE animation appliquée, les 8 directions sont
de simples rotations de caméra autour du même clip (`yaw_deg` dans
`render_combo_cendre.py`/`capture_pose.py`) — gratuites en crédits,
seulement du temps de rendu Blender. Le coût de généralisation est donc
piloté par le nombre de MOUVEMENTS distincts, pas par mouvements ×
directions.

Coût par mouvement extrapolé du réel mesuré ce pilote : `meshy_animate`
sur une action de bibliothèque = 3cr (mesuré : Punch_Combo). Modèle +
rig déjà payés une fois pour toutes (40cr, sunk, réutilisable).

| Mouvement | Statut | Coût Meshy |
|---|---|---|
| Combo (coup1+2+3) | **Fait ce pilote** | 3cr (déjà dépensé) |
| Déplacement/marche | Gratuit avec le rig (marche incluse) | 0cr |
| Idle | Pose de base ou geste posé à la main (comme coup3) | 0cr |
| Dash | Action bibliothèque (ex. Standard_Forward_Charge, precedent monstre) | 3cr |
| Hurt | Action bibliothèque ou geste posé à la main | 3cr |
| Mort | Action bibliothèque (Dead, action_id=8, precedent Ranged) | 3cr |
| Bras-Faux | Action bibliothèque + retouche (comme coup3) | 3cr |
| Poing Belluaire | idem | 3cr |
| Poing Tellurique | idem | 3cr |
| Invocation Gueule Vide | idem | 3cr |
| Marée de Sable | idem | 3cr |
| **Total animate restant** | | **24cr** |

**TOTAL généralisation Cendre (couverture directionnelle actuelle,
idle/déplacement déjà 8 directions, le reste à 1 direction comme
aujourd'hui) : 40cr (modèle+rig, déjà payé) + 27cr (animate, dont 3cr
déjà payés) = 67cr, dont 43cr déjà dépensés ce pilote → 24cr
restants.**

---

### Correctif post-vérification (même jour, 2026-08-23)

**Contexte.** Milan a jugé lui-même la capture de comparaison
(`captures/verification/2026-08-23-cendre-migration-3d-pilote-combo-
avant-apres.png`) issue du pilote ci-dessus et mesuré un défaut de
contenu au moment du contact sur coup2 et coup3, non signalé
honnêtement par le rapport initial. Un agent de suivi (nouvelle
session, la précédente n'était pas reprenable) a reproduit la mesure
et corrigé le défaut précis — même périmètre strict que le mandat
d'origine (pilote, pas de bascule en jeu, coup1 non touché, aucun
fichier `.tscn`/`.gd`, aucun asset PixelLab supprimé, `cendre_frames.
tres`/`cendre_frames_cooked.json` non touchés).

**Méthode de mesure (reproductible)** : diff pixel-à-pixel entre
frames consécutives du même coup, sur les frames déjà quantifiées
(`combo_quantized/`) — seuil `>20` sur la somme des 4 canaux RGBA,
`% de pixels changés` = `(diff > seuil).sum() / total_pixels * 100`.

**Défaut coup3 (priorité, le pire des deux)** : `COUP3_FRACTIONS
["contact"] = [1.0, 1.0]` posait littéralement la MÊME fraction
d'interpolation deux fois de suite → les deux frames de contact
(`coup3_contact_00_frac1.00.png` / `coup3_contact_01_frac1.00.png`)
étaient **pixel-identiques (0.00% de diff)**, un hold de la pose finale
répétée au lieu d'un vrai temps de contact distinct.

**Défaut coup2** : le contact (`mocap_frame 34, 35`) tombait dans un
plateau quasi-statique du clip `Punch_Combo` (le bras/lame reste levé
près du visage de la frame ~32 à ~38, diff pixel à plat 5-10% sur toute
la séquence anticipation→contact→récupération) — la transition vers le
contact (8.13%) était même PLUS PETITE que plusieurs transitions
d'anticipation (9-10%), aucun pic distinctif.

**Corrections apportées** (détail technique et justification complète
en commentaires dans `experiments/blender_capture/render_combo_
cendre.py`, sections `COUP2` et `COUP3_CONTACT_KEYS`) :
- **Coup2** : scout fin frame-par-frame (rendu de chaque frame mocap
  24 à 42, diff pixel + inspection visuelle zoomée x3) pour localiser
  le vrai point de reach maximal du clip — frame 31 (bbox du sommet de
  silhouette la plus haute de tout le segment). Nouveau découpage :
  anticipation `[26, 28]` (raccourcie pour que le swing rapide du clip,
  frames 29-31, tombe ENTRE la dernière frame d'anticipation et la
  première frame de contact au lieu d'être absorbé dedans — même
  principe que le saut de frames déjà utilisé par coup1), contact
  `[31, 33]`, récupération `[35, 37, 39, 41]`.
- **Coup3** : remplacement des deux `frac=1.0` par deux vraies clés de
  pose intentionnelles, `impact_peak` (bras/avant-bras gauche en
  overshoot 135/140% de l'amplitude "posée", buste 180%) et
  `impact_release` (buste qui commence à se de-rotater à 130%, bras
  gauche relâché à 105%). Un premier essai en pur overshoot sur
  LeftArm/LeftForeArm/Spine seuls (108-135%) s'est révélé insuffisant à
  la mesure (~6% de diff, toujours dans le bruit d'anticipation — la
  silhouette du bras gauche seul est bornée près de la tête/épaule
  au-delà d'un certain angle). Ajout d'un contre-mouvement du bras
  DROIT (bras de garde qui se retire pendant que le gauche porte le
  coup — mécanique réelle d'un crochet), même axe/convention de signe
  que la calibration d'origine (`cal_right.png`/`cal_right2.png`,
  déjà vérifiée pour l'autre bras par le mandat initial). Le bras droit
  est explicitement restauré à sa pose mocap frame 49 en récupération
  (pas de résidu du contre-mouvement).
- `render_combo_cendre.py` gagne un flag `--sections=` pour ne
  regénérer que les blocs concernés (coup2, coup3) sans re-rendre coup1
  ni les transitions (inchangés) — aucune dépense Meshy, uniquement du
  rendu Blender local sur le GLB déjà téléchargé et payé.

**Mesure AVANT (frames rapportées, sur `combo_quantized/` d'origine) :**

| Transition | Avant |
|---|---|
| coup2 antic(28)→antic(30) | ~9-10% (bruit) |
| coup2 antic(32)→contact(34) | **8.13%** (plus petit que le bruit) |
| coup3 antic(0.85)→contact(1.00) | 3.57% |
| coup3 contact(1.00)→contact(1.00) | **0.00%** (duplicata) |
| coup3 contact(1.00)→recovery(0.75) | 4.76% |

**Mesure APRÈS (même méthode, nouvelles frames, `combo_quantized/`) :**

| Transition | Après |
|---|---|
| coup2 antic(26)→antic(28) | 10.58% |
| coup2 antic(28)→contact(31) | **12.03%** (pic net, seul maximum local) |
| coup2 contact(31)→contact(33) | 10.18% |
| coup2 contact(33)→recovery(35) | 7.81% |
| coup3 antic(0.72)→antic(0.85) | 4.80% (bruit d'anticipation, référence) |
| coup3 antic(0.85)→contact(impact_peak) | **11.58%** (contre 3.57% avant) |
| coup3 contact(impact_peak)→contact(impact_release) | **11.95%** (contre 0.00% avant) |
| coup3 contact(impact_release)→recovery(0.75) | **10.41%** (contre 4.76% avant) |

Les deux transitions clés (entrée et sortie de contact) sont
maintenant nettement au-dessus du bruit d'anticipation mesuré
(4.8-10.6%) sur les deux coups, et du même ordre de grandeur que le
pic de coup1 (15.56%, inchangé) sans être strictement identiques — plus
un plat, plus de 0.00%.

**Régénération** : seules les 8 frames coup2 et 13 frames coup3 ont été
re-rendues (`--sections=coup2,coup3` puis `--sections=coup3` pour
l'itération finale du contact) ; coup1 et les deux blocs de transition
sont restés strictement inchangés (mêmes frames mocap, même code). Post-
traitement identique (`quantize.py --target_pixels=96`, mêmes
paramètres). `build_comparison.py` mis à jour (nouveaux noms de tags
coup2/coup3) et ré-exécuté — même mise en page (3 blocs coup1/2/3,
AVANT PixelLab au-dessus/APRÈS 3D en dessous, frames de transition
surlignées en ambre), capture régénérée au même chemin.

**Aucune dépense Meshy** : correctif entièrement local (Blender +
Python), GLB riggé déjà téléchargé et payé par le pilote initial,
`data/meshy_usage.jsonl` non modifié.

**Fichiers modifiés** : `experiments/blender_capture/
render_combo_cendre.py` (nouveau découpage coup2, nouvelles clés de
contact coup3, flag `--sections=`), `experiments/blender_capture/
cendre_pilot/build_comparison.py` (working dir, non committé — noms de
tags mis à jour), `captures/verification/2026-08-23-cendre-migration-
3d-pilote-combo-avant-apres.png` (régénérée). Script de diagnostic
`experiments/blender_capture/cendre_pilot/tune_coup3_contact.py`
(working dir, non committé) gardé pour trace de l'itération de
calibration ayant mené aux valeurs finales.

**Si 8 directions partout** (les 9 animations actuellement
mono-direction étendues à 8) : **+0cr Meshy supplémentaire** — coût
100% en temps de rendu Blender (9 mouvements × 7 directions
supplémentaires × ~13 frames/mouvement en moyenne × cadrage/rendu
Cycles, de l'ordre de plusieurs heures de calcul CPU réparties, aucun
coût crédit).

**Chiffre unique pour Milan : ~67 crédits Meshy pour régénérer
entièrement Cendre en 3D à la couverture directionnelle actuelle (24cr
restants après ce pilote), 8 directions partout inclus sans surcoût
crédit.** Solde Meshy actuel après ce pilote : 823cr — largement
suffisant.

**Prochain pas** : en attente du jugement de Milan sur la capture de
comparaison avant tout GO sur la généralisation. Rien re-rendu, rien
supprimé, rien basculé en jeu.

---

### Correction du pilote (2026-08-23) — 2 défauts visuels zoomés par Milan, corrigés à la source

**Contexte.** Milan a zoomé la capture committée et trouvé 2 défauts
qu'aucun agent précédent n'avait signalés. Mandat de correction reçu :
corriger à la SOURCE (rig/éclairage/quantification), jamais frame par
frame, et livrer une nouvelle capture au canvas RÉEL du jeu (64×64,
vérifié dans `assets/manifests/cendre_frames_cooked.json` :
`out_canvas=[64,64]`, `anchor_px=[32,61]`), pas à 96. Aucun fichier
`.tscn`/`.gd` touché, aucun asset PixelLab touché, même périmètre que
les 2 commits précédents.

#### Défaut 1 — bavure aux articulations (coup1 contact) : cause isolée par élimination

Diagnostic reproductible dans `experiments/blender_capture/cendre_pilot/
diag_defect1.py` et `inspect_shard_weights.py` (working dir, non
committés — mêmes rendus comparatifs qu'utilisés pour le diagnostic
`Roll_Dodge`, voir `docs/worklog-archive-2026-08-18-a-2026-08-21.md`) :

1. **Trop d'influences par sommet (piste 1 du mandat) — mesuré, ÉLIMINÉ.**
   `max_influences_per_vertex=4` sur les 237 277 sommets du mesh
   (`char1`), `verts_over_limit_4=0`. Le rig est déjà au plafond
   standard glTF (4 os/sommet) — rien à limiter. Un `vertex_group_
   smooth` (factor=0.5, 3 passes) appliqué seul et rendu en comparatif
   ne corrige PAS la bavure (rendu identique en silhouette, légèrement
   plus bruité sur les sangles) — piste éliminée par la mesure, pas par
   supposition.
2. **Sommets dupliqués non fusionnés (piste 2) — présents mais PAS la
   cause.** Mesure honnête : **48,6% de doublons** (237 277 → 121 952
   sommets après `remove_doubles(threshold=0.0001)`) — l'auto-rig Meshy
   a réussi à river un squelette dessus, mais le maillage porte bien le
   piège de doublons déjà rencontré sur d'autres personnages (~50%,
   conforme à l'avertissement du mandat). **Mais un rebind complet**
   (fusion réelle des doublons + `parent_set(type="ARMATURE_AUTO")` sur
   l'armature existante, pose de repos forcée en `REST` pour un
   heat-weight propre) **reproduit la bavure À L'IDENTIQUE** sur la
   frame de contact coup1 — preuve que les doublons ne sont pas la
   cause de CE défaut (fusionnés quand même dans le correctif final,
   bonne hygiène générale, mais documentés ici comme piste éliminée
   pour ce symptôme précis).
3. **Cause réelle isolée** (`inspect_shard_weights.py` — sommets triés
   par déplacement anormal entre bind pose et frame de contact, poids
   de squelette inspectés) : en VRAIE pose de repos (bras le long du
   corps — pas la pose de garde de la frame 1 de l'action, vérifiée
   séparément en forçant `armature.data.pose_position="REST"`), **la
   main droite touche/frôle l'ourlet déchiqueté de la tunique à hauteur
   de hanche** (position du sommet le plus déplacé : `(-0.262,-0.028,
   0.573)` vs tête de l'os `RightHand` en repos : `(-0.264,-0.036,
   0.893)` — à ~0,3 unité, bien plus proche que `RightShoulder`/`neck`).
   Le heat-weighting automatique (Meshy comme le recalcul Blender —
   les deux donnent le même résultat) colle ~950 sommets de l'ourlet à
   l'os `RightHand` (poids 0,96-0,98) au lieu de `Hips`/`RightUpLeg`.
   Quand le coup part, ces sommets sont traînés avec le poing → l'écharde.
   **Même classe de bug que `Roll_Dodge`** (déformation de skinning sur
   pose extrême) mais mécanisme précis différent : pas la rotation en
   elle-même, un mauvais binding de PROXIMITÉ en pose de repos.

**Fix retenu (le moins destructif qui a réellement marché, testé
avant/après par rendu comparatif de la même frame)** : recalcul des
poids automatiques pendant que `RightArm`/`LeftArm` sont écartés du
corps (rotation temporaire ±90° sur X, le contact main/ourlet disparaît
le temps du calcul), fusion des doublons au passage, puis pose remise à
plat — la pose utilisée pour le calcul n'affecte QUE la qualité du
heat-weighting, pas les matrices de repos de l'armature ni l'action
`Punch_Combo` qui continue de s'appliquer normalement par-dessus.
Implémenté une fois dans `fix_shoulder_hem_skinning()`
(`experiments/blender_capture/render_combo_cendre.py`), appelé à
l'import, avant toute pose — **bénéfice automatique à toutes les
animations futures**, zéro coût Meshy (Blender/Python pur).

**Preuve comparative** (frame `coup1_contact_00_mocapframe16`, rendu
brut 512px non quantifié — voir bloc "Detail articulation" de la
nouvelle capture) : bras/poing lisibles comme un bras après correction,
écharde disparue. Confirmé sur `coup1_contact_01_mocapframe18`
également. **Coup3 (bras gauche, amplitude déjà extrême) ne montrait
PAS ce symptôme avant correction** — le contact main/hanche ne se
produit que pour le bras qui pend le long du corps en repos, pas pour
un bras qui monte vers la tête — mais le fix est appliqué aux DEUX bras
par symétrie/prévention (bénéfice pour de futures animations qui
solliciteraient le bras gauche de la même façon).

**Piste 4 (amplitude du clip mocap réduite) : non nécessaire** — la
vraie cause n'était pas l'amplitude de rotation, inutile de dégrader la
fidélité du clip Punch_Combo.

#### Défaut 2 — silhouette molle (coup3) : rim light ajoutée + `quantize.py` retuné pour le 64px réel — verdict nuancé, honnête

**Rim light.** Ajoutée dans `render_combo_cendre.py` (fonction de setup
scène, avant le premier rendu) : un second `SUN` Blender orienté
exactement sur le vecteur `direction` déjà calculé pour la caméra (via
`to_track_quat`, générique — pas une valeur en dur liée à ce `yaw_deg`
précis), donc toujours en contre-jour quel que soit l'angle de prise de
vue. Teinte froide/neutre `(0.80, 0.88, 1.0)`, énergie 1.6 (sous la key
light à 3.0) — discrète, pas de halo coloré.

**Saturation re-mesurée (`measure_saturation.py`), comme demandé.**
Sur les frames de contact quantifiées à 64px (nouveaux réglages, voir
ci-dessous) : coup1/2/3 = **0,0595 / 0,0598 / 0,0602** — sous le
PixelLab existant (0,0761-0,0801) et sous la mesure du pilote initial à
96px (0,0670-0,0692). **Aucune dérive vers le haut, confirmé.** Test
supplémentaire pour isoler l'effet de la rim light SEULE (même frame,
mêmes réglages `quantize.py`, rim light ON vs OFF) : saturation
**identique au 4e chiffre près** (0,0595 dans les deux cas) — attendu,
`quantize.py` FIXE la saturation du remplissage à `target_saturation`
(0,10) pour chaque pixel indépendamment de la teinte d'entrée, la rim
light ne peut donc pas la faire dériver par construction.

**Verdict honnête sur l'effet visuel de la rim light à 64px : quasi
nul, mesuré, pas supposé.** Comparaison pixel-à-pixel de la même frame
quantifiée (mêmes réglages `quantize.py`) avec et sans rim light :
**rendu strictement identique** au canvas réel. Cause identifiée :
`pixelate_block_center()` dans `quantize.py` échantillonne UN SEUL
pixel (le centre du bloc) par bloc de 8×8 pixels source (512px → 64px)
au lieu d'en faire la moyenne — un liseré de contour de 1-2px de large
a une probabilité très faible d'être exactement le pixel échantillonné
sur tout le pourtour de la silhouette. La rim light AMÉLIORE bien la
lecture des contours dans le rendu Cycles brut 512px (visible à l'œil
dans le rendu non quantifié), mais cet effet est presque entièrement
perdu par le point-sampling du post-traitement pixel-art actuel.
**Corriger ça proprement (passer `pixelate_block_center` à une moyenne
de bloc) est HORS PÉRIMÈTRE de ce mandat** : `quantize.py` est un
script partagé par tous les personnages (Crawler/Brute/Ranged), pas
spécifique à Cendre — le modifier changerait le rendu de TOUT le
pipeline pixel-art existant, pas seulement ce pilote. Signalé ici comme
piste future, pas fait unilatéralement. La rim light est conservée
(gratuite, saturation sûre, bénéficie à tout rendu futur en plus haute
résolution ou non quantifié) mais **son bénéfice réel sur l'asset livré
en jeu aujourd'hui (64px) est négligeable** — verdict honnête demandé
par le mandat.

**Ce qui améliore vraiment la lisibilité à 64px : le retuning de
`quantize.py`.** Testé (`experiments/blender_capture/cendre_pilot/
quantize_tests/`, non committé) : `color_steps` (8 défaut → 5),
`value_band_min/max` (0.165/0.90 défaut → 0.08/0.97, bande élargie =
plus de contraste), `outline_thickness`/`edge_strength` (3.0/0.12 →
4.5/0.10, contour un peu plus épais et plus sensible), `dither_amount`
(0.35 → 0.18, moins de bruit qui casse les formes à cette résolution).
Comparé visuellement sur plusieurs frames (coup1 contact, coup3
contact) : **moins de paliers de couleur = blocs plus contigus = bras/
torse mieux séparés visuellement**, amélioration réelle et visible
(voir bloc COUP 3 de la nouvelle capture, silhouette nettement moins
diffuse qu'avec les réglages par défaut). C'est ce changement, pas la
rim light, qui porte la majorité de l'amélioration mesurable du défaut
2 au format réel.

#### Nouvelle capture de validation

`captures/verification/2026-08-23-cendre-migration-3d-correction-
pilote-avant-apres-64px.png` — 3 blocs, format demandé par Milan :
(A) frames de contact des 3 coups, AVANT correction / APRÈS correction,
**au canvas réel 64×64** (pas 96) ; (B) détail zoomé articulation
épaule/coude (coup1 contact), rendu brut NON quantifié pour juger
objectivement l'état géométrique de la bavure ; (C) ligne de référence
PixelLab actuel (format natif 112px) à échelle d'affichage cohérente
pour comparaison. `git check-attr filter` vérifié : `unspecified`, pas
de LFS.

**Fichiers modifiés/ajoutés** : `experiments/blender_capture/
render_combo_cendre.py` (fonction `fix_shoulder_hem_skinning()` +
appel à l'import, rim light dans le setup lumière, flags
`--fix_weights=1`/`--rim_light=1` pour A/B testing futur),
`captures/verification/2026-08-23-cendre-migration-3d-correction-
pilote-avant-apres-64px.png` (nouvelle capture). Working dir
(`experiments/blender_capture/cendre_pilot/`, non committé) : scripts
de diagnostic (`diag_defect1.py`, `inspect_shard_weights.py`,
`render_rest_pose.py`), rendus intermédiaires (`combo_render_v2/` 40
frames corrigées 512px, `combo_quantized_64/` mêmes frames quantifiées
au format réel, `old_quantized_64/` frames de contact AVANT quantifiées
au format réel pour comparaison équitable, `quantize_tests/` essais de
réglages), `build_validation_capture.py` (script ayant produit la
capture ci-dessus). **Aucun fichier `.tscn`/`.gd` touché, aucun asset
PixelLab touché, `cendre_frames.tres`/`cendre_frames_cooked.json` non
touchés** — même périmètre que les 2 commits précédents.

**Coût Meshy : 0 crédit.** Tout le travail de cette correction est
Blender/Python pur sur le GLB déjà téléchargé et payé par le pilote
initial (43cr) — `data/meshy_usage.jsonl` non modifié, confirmé.

**Blocages non résolus** : aucun pour le périmètre de ce mandat. Point
ouvert signalé ci-dessus (pas un blocage) : le point-sampling de
`quantize.py` limite l'impact de tout ajout d'éclairage de contour au
format 64px — à garder en tête si un futur mandat retouche ce script
partagé.

**Prochain pas** : en attente du jugement de Milan (zoom personnel sur
la nouvelle capture) avant tout push. Rien poussé, rien basculé en jeu,
aucune généralisation engagée.

### Correction du pilote, round 2 (2026-08-23) — quantize.py moyenne de bloc, écharde résiduelle à la hanche, comparaison 112px réelle

**Contexte.** Milan a de nouveau zoomé la capture round 1 et trouvé des
problèmes supplémentaires. Mandat explicite en 3 points ORDONNÉS (le
point 1 conditionne le jugement des deux autres) : (1) corriger
`quantize.py` — passer de l'échantillon central à une moyenne de bloc,
avec test de non-régression obligatoire sur les 3 monstres AVANT toute
généralisation ; (2) diagnostiquer une 2e écharde résiduelle à la
hanche (pas le bras, déjà réglé round 1) ; (3) refaire la comparaison
au VRAI format PixelLab (112px, pas 64 — erreur de Milan corrigée dans
son propre mandat round 2).

#### Point 1 — `quantize.py` : moyenne de bloc pondérée par alpha, non-régression vérifiée sur les 3 monstres

**Cause confirmée** (déjà diagnostiquée round 1, jamais corrigée faute
de mandat explicite) : `pixelate_block_center()` échantillonnait le
pixel central d'un bloc source de 8×8 (ou plus) au lieu d'en faire la
moyenne — un liseré de contour de 1-2px a une probabilité quasi nulle
d'être exactement ce pixel, la rim light disparaissait donc
entièrement après quantification.

**Fix.** Deux nouvelles fonctions ajoutées à `experiments/
blender_capture/quantize.py` : `pixelate_block_average()` (moyenne
simple RGB+alpha) et `pixelate_block_average_alpha_weighted()` (RGB
pondéré par alpha, alpha lui-même en moyenne simple). `pixelate_block_
center()` originale **conservée intacte, non appelée par `main()`** —
`quantize_normal.py` l'importe explicitement pour downscaler les normal
maps (vecteurs XYZ), où une moyenne non-renormalisée fausserait
l'éclairage ; aucune raison de la changer pour ce cas, vérifié en
relisant son en-tête et confirmé par un import direct après coup
(`quantize_normal.main` s'importe toujours sans erreur). Nouveau flag
`--pixelate_mode={center,mean,mean_alpha}` sur `main()`, défaut
`mean_alpha`.

**Simple vs pondérée : comparaison MESURÉE, pas supposée.** Sur les 236
blocs à alpha partiel (contour détouré) de `coup1_contact_00` à 112px :
luminance moyenne du bloc en mode `mean` = **0.345**, en mode
`mean_alpha` = **0.480** (+0.135) — preuve chiffrée que la moyenne
simple assombrit le contour (elle mélange le RGB arbitraire des pixels
100% transparents du fond, souvent sombre dans un PNG Blender, avec la
couleur du sujet) alors que la pondération par alpha neutralise cet
effet sans perdre la capture du rim light (les deux modes calculent
l'alpha de sortie identiquement). **`mean_alpha` retenu comme défaut**
pour cette raison mesurée, pas une préférence esthétique.

**Test de non-régression sur les 3 monstres (OBLIGATOIRE avant
généralisation, fait AVANT tout autre changement).** Comparé `quantize.
py` ANCIEN (snapshot `git show HEAD:...` avant ce commit) vs NOUVEAU
(défaut `mean_alpha`) sur une frame `attack_raw` de chaque monstre
(`experiments/monsters_nuit/blender_out_v4/{brute,crawler}_attack_raw.
png`, `blender_out_v5/ranged_attack_raw.png`), mêmes paramètres
(défauts de `quantize.py`, `target_pixels=64` — le canvas réel
committé, vérifié par `file` sur `assets/processed/sprites/{brute,
crawler,ranged}/attaque.png`). Mesuré : différence RGB moyenne
1.7-3.4/255, différence alpha moyenne 3.1-4.6/255, IoU de silhouette
(seuil alpha>127) **0.99 / 0.96 / 0.89** pour brute/crawler/ranged.
Inspection visuelle zoomée (voir `experiments/blender_capture/
cendre_pilot/quantize_regression_round2/monster_regress/`, working dir
non commité) : **aucune régression détectée** — les silhouettes restent
reconnaissables et complètes (pas de membre manquant, pas de flou
détruisant la lisibilité), la seule différence visible est un rendu
intérieur légèrement plus lisse/moins "poivre et sel" (bruit de
sur-brillance speculaire moins fragmenté) avec le nouveau mode, ce qui
lit plutôt comme une amélioration qu'une dégradation. Le monstre
`ranged` (IoU le plus bas, 0.89) montre la plus grande différence,
concentrée sur des détails fins (arc/corde, doigts) — attendu, une
moyenne de bloc lisse légèrement les détails sub-pixel, mais la forme
générale reste identique et lisible au zoom. **Verdict honnête : aucune
régression bloquante trouvée sur les 3 monstres, changement généralisé
committé.** Si Milan voit une dégradation au zoom personnel sur un cas
que cette vérification n'a pas couvert, le flag `--pixelate_mode=
center` reste disponible pour revenir instantanément à l'ancien
comportement sans toucher au reste du pipeline.

#### Point 2 — écharde résiduelle à la hanche : diagnostic complet et corrigé

**Diagnostic (même rigueur que round 1 — isolation par élimination,
preuve comparative, scripts dans `experiments/blender_capture/
cendre_pilot/quantize_regression_round2/`, working dir non commité).**
`inspect_hip_shard.py` reproduit le pipeline actuel (`fix_shoulder_hem_
skinning` round 1 appliqué) puis mesure le déplacement bind→contact :
**605 sommets restent dominés (poids ~0.95-0.98) par `RightHand`** même
après le fix round 1. Hypothèse testée : l'abduction à 90° (le
mécanisme du fix round 1) ne sépare-t-elle pas suffisamment la main de
ce point de tunique ? Mesuré (`inspect_abducted_proximity.py`,
`inspect_static_proximity.py`) : la distance 3D main↔sommet **augmente**
avec l'abduction (0.27 unité au repos → 0.86-1.33 unité à 90°/135°/175°
d'abduction) mais **le poids recalculé ne change pas** — preuve que ce
n'est PAS un problème de distance 3D corrigible par une pose écartée
(contrairement au défaut épaule/bras du round 1) : le heat-weighting de
Blender utilise une diffusion sur la surface du maillage (pas une
distance brute), et l'intégralité du groupe de sommets "RightHand
dominant" (n=2002, mesuré) se trouve à un Z de repos **systématiquement
sous** la tête de l'os RightHand de 0.27 à 0.58 unité — largement
au-delà d'une longueur de main/doigts plausible (~0.10-0.15 sur ce
personnage) : ce ne sont PAS des sommets de main légitimes, mais un pan
entier de tunique mal rattaché. Une première tentative de correctif par
vote topologique (BFS sur le graphe d'arêtes, en excluant les sommets
suspects) a **échoué** (0 sommet réassigné, profondeur testée jusqu'à
200) — preuve que le pan mal-pesé est plus étendu que le seul
sous-ensemble à déplacement anormal, le vote retombe toujours sur
d'autres sommets tout aussi mal pesés.

**Fix retenu** (`fix_hip_hem_proximity()`, `experiments/blender_
capture/render_combo_cendre.py`, appliqué juste après `fix_shoulder_
hem_skinning()`) : parmi les sommets à poids `RightHand`/`LeftHand`
dominant (>0.5), ceux dont le Z de repos est de plus de 0.18 unité sous
la tête de l'os concerné (marge choisie entre l'étendue mesurée du
défaut et une longueur de main plausible) sont réassignés à l'os du bas
du corps (`Hips`/`RightUpLeg`/`LeftUpLeg`/`RightLeg`/`LeftLeg`) le plus
proche par distance de tête, poids plein, autres groupes retirés.
**6959 sommets reassignés** (les deux côtés, droit et gauche).
**Vérifié par rendu comparatif avant/après** sur les 3 coups (coup1
contact réel, coup2 contact réel, une pose coup3-équivalente) :
l'écharde triangulaire disparaît complètement, remplacée par l'ourlet
jagged naturel déjà visible en pose de repos (`posture_check.png`) — et
**la géométrie de main/gant reste intacte** (vérifié au zoom, aucun
doigt manquant ni déformation visible). Une première version du
correctif (distance brute à la tête d'os, sans le filtre de marge Z)
avait sur-réassigné ~6900-7000 sommets **y compris de la vraie
géométrie de main** (le poignet/paume est naturellement proche de la
hanche en pose bras-le-long-du-corps) — éliminée par la mesure, pas par
supposition, avant d'adopter le critère Z retenu.

**État honnête de CHAQUE articulation, rendu brut non quantifié, 3
coups (voir capture ci-dessous, bloc B)** :
- **Épaule** (coup1/2/3) : propre, pas de bavure, déformation de la
  pauldron/manche cohérente avec la pose.
- **Coude** (coup1/2/3) : propre. Fortement raccourci/plié dans les
  poses de coup (poing près du menton ou de la hanche), pas d'artefact
  de clipping visible.
- **Hanche** (coup1/2/3) : **corrigée** — écharde disparue, ourlet
  jagged naturel sur les 3 coups (vérifié aussi sur coup2 et une pose
  coup3-équivalente, pas seulement coup1 où le défaut était le plus
  visible en caméra).
- **Genou** (coup1/2/3) : **non inspectable séparément** — entièrement
  couvert par le pantalon bouffant + bandes de jambe dans ce costume,
  aucune bavure ni clipping visible à la jointure pantalon/botte, mais
  il n'y a pas de "genou nu" à juger indépendamment sur ce personnage.
  Signalé honnêtement plutôt que de prétendre une vérification qui
  n'a pas de sens géométrique ici.

#### Point 3 — résolution PixelLab réelle : 112px CONFIRMÉ (pas 64)

Vérifié moi-même par `file` sur `assets/source/pixellab/cendre/
animations/coup{1,2,3}/0.png` : **112×112, confirmé** (Milan avait
raison de corriger son erreur du mandat round 1). **Nuance importante à
signaler** : le canvas COOKED réellement utilisé en jeu aujourd'hui
reste **64×64** (`assets/manifests/cendre_frames_cooked.json`,
`out_canvas=[64,64]`, fichier non touché par ce mandat comme demandé).
Les deux faits sont vrais simultanément : PixelLab génère nativement en
112px, mais le pipeline de cuisson actuel downscale à 64px pour
l'affichage en jeu. La comparaison ci-dessous est construite à 112px
comme demandé explicitement par Milan (juger la qualité à la résolution
native, avant tout downscale supplémentaire), pas parce que le canvas
de jeu aurait changé.

#### Nouvelle capture de validation

`captures/verification/2026-08-23-cendre-migration-3d-correction-
pilote-round2-avant-apres-112px.png` — 4 blocs : (A) 3 coups, frames de
contact AVANT (round 1 seul)/APRÈS (round 1+2), quantifiées à 112px
réel avec le nouveau `quantize.py` (`mean_alpha`, réglages Cendre
retenus round 1 : `color_steps=5`, `value_band=0.08/0.97`,
`outline_thickness=4.5`, `edge_strength=0.10`, `dither_amount=0.18`) ;
(B) détail zoomé sur CHAQUE articulation (épaule/coude/hanche/genou)
pour les 3 coups, rendu brut non quantifié, état APRÈS ; (B2) hanche
AVANT/APRÈS en gros plan (le correctif marquant de ce round) ; (C)
référence PixelLab native 112px, même échelle d'affichage. `git
check-attr filter` vérifié : `unspecified`, pas de LFS.

**Fichiers modifiés/ajoutés** : `experiments/blender_capture/quantize.
py` (nouvelles fonctions `pixelate_block_average`, `pixelate_block_
average_alpha_weighted`, flag `--pixelate_mode`, défaut changé —
**changement d'architecture partagé par tous les personnages, comme
signalé dans le mandat**), `experiments/blender_capture/
render_combo_cendre.py` (nouvelle fonction `fix_hip_hem_proximity()`
+ appel après `fix_shoulder_hem_skinning()`), `captures/verification/
2026-08-23-cendre-migration-3d-correction-pilote-round2-avant-apres-
112px.png` (nouvelle capture). `experiments/blender_capture/
quantize_normal.py` **non modifié** (toujours basé sur `pixelate_block_
center`, inchangée). Working dir non committé (`experiments/
blender_capture/cendre_pilot/quantize_regression_round2/` et
`combo_render_v3/`, `combo_quantized_112_v2_before/`, `combo_quantized_
112_v3_after/`) : scripts de diagnostic/test (`inspect_hip_shard.py`,
`inspect_abducted_proximity.py`, `inspect_static_proximity.py`,
`test_hip_override_v3.py` et versions précédentes conservées comme
trace du raisonnement), rendus intermédiaires, sheet de régression
monstres, script de capture. **Aucun fichier `.tscn`/`.gd` touché,
aucun asset PixelLab touché, aucune génération/régénération PixelLab,
`cendre_frames.tres`/`cendre_frames_cooked.json` non touchés, aucun
asset monstre (`assets/processed/sprites/{brute,crawler,ranged}/...`)
modifié** — même périmètre que les 3 commits précédents.

**Coût Meshy : 0 crédit.** Tout le travail de ce round est Blender/
Python pur sur le GLB déjà téléchargé et payé par le pilote initial ;
`data/meshy_usage.jsonl` non modifié, confirmé.

**Blocages non résolus** : aucun. Point ouvert signalé honnêtement :
l'articulation "genou" n'a pas de sens géométrique à juger séparément
sur ce personnage (pantalon bouffant qui couvre toute la jambe) — pas
un défaut, une limite de la méthode d'inspection demandée par le
mandat, documentée plutôt que masquée.

**Prochain pas** : en attente du jugement de Milan (zoom personnel sur
la nouvelle capture 112px) avant tout push. Rien poussé, rien basculé
en jeu, aucun asset monstre modifié malgré le changement de
`quantize.py` (changement de code seulement, pas de re-cuisson des
assets committés).

---

### Dernier test avant décision (2026-08-23) — le pilote corrigé passé par le VRAI pipeline de cuisson 64px

**Contexte.** Les rounds 1 et 2 ont validé les deux corrections (bavure
épaule/bras + rim light ; quantize.py moyenne pondérée par alpha +
écharde hanche) au format natif PixelLab 112px. Mais le canvas
RÉELLEMENT affiché en jeu aujourd'hui est cuit à 64×64
(`assets/manifests/cendre_frames_cooked.json`, `out_canvas=[64,64]`,
ancrage `(32,61)`) par `scripts/cook_character_frames.py` — jamais
testé avec ces corrections. Ce mandat ferme cette inconnue.

**Méthode — le vrai pipeline, pas un raccourci.** `scripts/cook_
character_frames.py` n'a pas été modifié ; il a été appelé tel quel en
subprocess, avec `--repo-root` pointé vers un répertoire scratch isolé
(hors du dépôt) pour qu'il écrive ses sorties (`assets/processed/
sprites/...` + le manifeste `<character>_frames_cooked.json` qu'il
RÉÉCRIT ENTIÈREMENT) sans toucher un seul fichier réel du dépôt —
`cendre_frames_cooked.json` et tout asset Cendre committé restent
intacts, vérifié après coup (`git status` propre hors la nouvelle
capture). Même logique bbox alpha / ancrage pied bande centrale /
collage que la production, exécutée par le fichier réel, pas réimportée
ni réécrite.

**Étape 1 — hauteur cible mesurée (pas supposée).** `assets/processed/
sprites/cendre/coup1/0.png` (frame déjà cuite et committée, suggérée par
le mandat) donne une bbox alpha de hauteur 48px — mais c'est une pose de
garde genoux fléchis, pas une hauteur de référence fiable. Mesuré aussi
`idle_south/0.png` (pose debout neutre, déjà en jeu) : bbox alpha
**56px**, retenu comme hauteur cible. Vérification croisée : le facteur
qui en résulte (voir étape 2) tombe pile dans la fourchette des 5
facteurs déjà mesurés sur d'autres pouvoirs de Cendre (0.6375–0.683),
alors que le facteur dérivé de `coup1/0.png` (48px) tomberait à 0.555,
nettement hors de cette fourchette — confirmation, pas une coïncidence,
que `idle_south` est la bonne référence de hauteur "debout" et que
`coup1/0` est une pose trop fléchie pour ce rôle.

**Étape 2 — facteur LANCZOS appliqué.** Source : les 6 frames de contact
round1+round2 déjà quantifiées à 112px (`experiments/blender_capture/
cendre_pilot/combo_quantized_112_v3_after/`, mêmes fichiers que la
capture round 2) — bbox alpha 86-88px (moyenne 86.5px). **Facteur =
56/86.5 ≈ 0.6474**, appliqué en LANCZOS (`Image.resize`) aux 6 frames
avant tout passage dans `cook_character_frames.py`, exactement comme la
convention établie pour les autres pouvoirs (mesurer, PUIS redimensionner
AVANT la cuisson, jamais dans le script de cuisson lui-même).

**Étape 3 — cuisson réelle.** Frames redimensionnées rangées dans
`0.png`/`1.png` par dossier `coup{1,2,3}_contact` (format d'entrée
attendu par le script), puis `python3 scripts/cook_character_frames.py
--character cendre_pilot_test --out-canvas 64x64 --foot-margin-px 3
--repo-root <scratch>` (foot-margin-px 3 reproduit exactement
`anchor_px=[32,61]` du manifeste réel). Résultat : ancrage pied
identique à la production sur les 6 frames, hauteur de personnage
obtenue 55-57px (cohérent avec la cible 56px, écart de mesure normal
entre poses).

**Livrable** : `captures/verification/2026-08-23-cendre-migration-3d-
dernier-test-cuit-64px-reel.png` — 3 blocs (un par coup), pipeline 3D
corrigé → cuit 64px réel (2 frames de contact) à côté de la référence
PixelLab 2D DÉJÀ cuite à 64px (`assets/processed/sprites/cendre/
coup{1,2,3}/2.png`, même index de frame que la référence retenue round 1
dans `build_validation_capture.py::section_c`, pour rester cohérent
entre les rounds), même échelle d'affichage (×8 nearest-neighbor, même
convention que les captures précédentes de ce mandat). `git check-attr
filter` vérifié : `unspecified`, pas de LFS.

**VERDICT HONNÊTE, NÉGATIF.** Le gain observé à 112px (bras détaché du
torse, texture/rim light visibles) **ne survit pas** au downscale réel à
64px — pire, le résultat 3D lit comme **moins lisible** que la
référence 2D PixelLab déjà en jeu à cette même taille. À 64px réel, la
silhouette 3D devient un bloc moucheté/granuleux (le bruit de
sur-brillance spéculaire, déjà noté comme "poivre et sel" dans le test
de non-régression round 2, se fige par la quantification sans lignes de
contour nettes) où bras/torse/jambes se distinguent mal ; la référence
PixelLab garde des aplats propres, un contour net, une pose clairement
lisible (poings levés, coudes distincts). Les détails qui justifiaient
le gain à 112px se compressent sous 3-4px de large à 64px — sous le
seuil de lisibilité en jeu. Aucune régression de structure en revanche :
silhouette complète sur les 6 frames, pas de membre perdu, ancrage pied
identique. Vérifié moi-même au zoom (×12) sur un couple de frames avant
d'écrire ce verdict, pas une impression de vignette.

**Fichiers modifiés/ajoutés** : `captures/verification/2026-08-23-
cendre-migration-3d-dernier-test-cuit-64px-reel.png` (nouvelle capture,
seul livrable committé). Tout le travail de cuisson (frames
redimensionnées, appel du script, manifeste généré) a eu lieu dans un
répertoire scratch hors dépôt — rien ajouté sous `assets/processed/`
ni `assets/manifests/` pour ce test. **Aucun fichier `.tscn`/`.gd`
touché, aucun asset PixelLab touché, `cendre_frames.tres`/`cendre_
frames_cooked.json` non touchés, rien basculé en jeu** — même périmètre
que les 3 commits précédents de ce mandat.

**Coût Meshy : 0 crédit.** Aucune génération, aucun appel Meshy — travail
de traitement d'image pur (PIL/LANCZOS + `cook_character_frames.py`) sur
des assets déjà rendus/quantifiés. `data/meshy_usage.jsonl` non modifié.

**Blocages non résolus** : aucun. Le verdict est négatif mais net —
c'est exactement l'information que ce mandat cherchait à établir avant
toute décision de généralisation.

**Prochain pas** : en attente du jugement de Milan (zoom personnel sur
la nouvelle capture 64px). Rien poussé, comme les 4 fois précédentes.

### Dernière tentative ciblée, round 3 (2026-08-23) — matériau aplati (spécularité réduite + posterisation albédo/émission), verdict de clôture

**Mandat.** Milan a proposé une dernière tentative ciblée avant de
clore le mandat : réduire la spécularité du rendu Blender (roughness ↑,
specular ↓, ou bascule vers un shader plus proche d'un toon/NPR si le
temps le permet) — **aucune régénération Meshy**, seulement le rendu
(matériau/éclairage) et la chaîne quantize→cook en aval, sur les mêmes
6 frames de contact déjà utilisées à chaque round précédent.

**Étape 1 — diagnostic mesuré du matériau importé (pas supposé).**
Inspection du GLB (`experiments/blender_capture/cendre_pilot/
mat_round3/inspect_materials.py`, working dir non commité) : le
matériau `Material_1` (seul matériau texturé du personnage — `Material`
et `Dots Stroke` ne portent aucune texture, non touchés) a `Metallic=
1.0`, `Roughness=0.41`, `Specular IOR Level=0.5`, et une **même**
texture 2048px (`texture_0`) branchée à la fois sur `Base Color` ET sur
`Emission Color` (`Emission Strength=1.0`) — donc quasi-émise telle
quelle, indépendamment de tout éclairage Blender.

**Étape 2 — test comparatif de la piste "spécularité" demandée par le
mandat, AVANT généralisation.** Rendu de la même frame (coup1 contact,
mocap frame 16) avec le matériau ACTUEL (`iter0`, référence) puis avec
`Metallic=0.0, Roughness=0.9, Specular IOR Level=0.2` (`iter1`) —
harnais isolé `mat_round3/render_single_test.py` (import + les deux fix
de skinning + caméra/lumière identiques au script de production, pour
rester comparable). Diff pixel mesuré sur les rendus bruts 512px :
**moyenne ~1.3/255 par canal, max 112/255** — un effet réel mais
marginal, visuellement quasi imperceptible après quantize+cook 64px
(`mat_round3/compare_iter0_iter1.png`). **Conclusion mesurée : la
spécularité BSDF n'est PAS la cause dominante du bruit "poivre et sel"**
— contrairement à l'hypothèse de départ du mandat (raisonnable a priori,
mais infirmée par la mesure, pas supposée).

**Étape 3 — recherche de la cause réelle (mesurée, pas supposée).**
Export de `texture_0` depuis le GLB (`mat_round3/texture_0.png`,
working dir non commité) : ce n'est PAS une texture de tissu à grain
fin mais une **mosaïque de patches gris/noir/crème/beige de quelques
dizaines de pixels** sur les 2048px de la texture — visuellement une
sorte de motif "camouflage" à haute fréquence. Cette texture est émise
quasi-telle-quelle (Emission Strength=1.0, non affectée par la
lumière/le matériau) : à l'échelle du personnage rendu (~400px de
haut), chaque patch de texture occupe 1-3 pixels de rendu — exactement
la taille d'un grain de bruit "poivre et sel" une fois downscalé à
64px. C'est cette texture, pas la spécularité, qui est la cause réelle
du défaut identifié aux rounds précédents.

**Étape 4 — itération vers un rendu plus "toon" (comme prévu par le
mandat en cas d'insuffisance de la seule réduction spécular).** Deux
essais comparés :
- `iter2` (posterisation RGB par canal, 5 paliers, Math SNAP par
  canal Rouge/Vert/Bleu séparément) : **rejeté** — un posterize par
  canal RGB indépendant décale les teintes de façon incohérente
  (patches oranges/rouges apparus sur la tunique, `mat_round3/
  iter2_posterize5.png`), inacceptable même si `quantize.py` re-fixe la
  saturation en aval (le rendu brut intermédiaire devient trompeur pour
  tout jugement visuel).
- `iter2b` (posterisation **HSV, canal Value seul**, Teinte/Saturation
  intactes, 5 paliers) : **retenu**. Nœuds Blender insérés en mémoire
  sur le graphe de matériau importé (`ShaderNodeSeparateColor`/
  `ShaderNodeCombineColor` mode HSV + `ShaderNodeMath` opération `SNAP`
  sur le canal Value), rebranchés sur les deux noeuds `TEX_IMAGE`
  (`Image Texture` → Emission, `Image Texture.001` → Base Color).
  **Aucune texture modifiée sur le disque** — uniquement le graphe de
  nœuds du rendu en cours, un réglage de rendu au sens strict du
  mandat.

Comparaison mesurée `mat_round3/compare_all3.png` (iter0 brut / iter1
spécularité réduite seule / iter2b spécularité réduite + posterize
Value) après quantize 112px + downscale 0.647 + cook 64px réel :
iter2b montre des zones de couleur nettement plus plates (grandes
masses sombres continues au lieu du bruit moucheté), silhouette plus
lisible — gain net et visible, contrairement à iter1 seul. Essai
supplémentaire (`iter3`, 7 paliers + `Emission Strength=0.6`) comparé à
iter2b (`mat_round3/compare_2b_3.png`) : résultat quasi équivalent,
**iter2b retenu** (réglage plus simple, un seul levier de plus que la
réduction spécular demandée par le mandat).

**Réglage final retenu** (appliqué dans `flatten_material_specular()`,
nouvelle fonction dans `render_combo_cendre.py`, activée par défaut
via `--mat_flatten=1`) : `Metallic=0.0`, `Roughness=0.9`, `Specular IOR
Level=0.15`, posterisation HSV Value 5 paliers sur les deux branches
texture (albédo + émission). **Rim light du round 1 intacte, non
modifiée** (elle répond à un défaut différent — silhouette qui se fond
dans le fond — les deux corrections ne s'opposent pas, confirmé par
inspection du rendu final : le contour reste détaché du fond sombre).

**Étape 5 — généralisation aux 6 frames de contact, pipeline réel
identique au test précédent.** `render_combo_cendre.py` (production,
patché) relancé avec `--sections=coup1,coup2,coup3` (34 frames,
~2min50 CPU) → `quantize.py` sur les 6 frames de contact, **mêmes
réglages Cendre retenus round 2** (`color_steps=5, value_band=0.08/
0.97, outline_thickness=4.5, edge_strength=0.10, dither_amount=0.18,
pixelate_mode=mean_alpha` par défaut) → bbox alpha mesurée 86-88px
(moyenne 86.5px, **identique aux rounds précédents** — le matériau ne
change ni la géométrie ni le cadrage, le facteur LANCZOS déjà validé
reste correct) → downscale ×0.647 LANCZOS → cuisson via le VRAI
`scripts/cook_character_frames.py` (repo-root isolé en scratch hors
dépôt, aucun fichier réel touché, vérifié après coup par `git status`
propre hors la nouvelle capture) — même méthode exacte que le test
précédent, aucun raccourci.

**Livrable** : `captures/verification/2026-08-23-cendre-migration-3d-
round3-materiau-aplati-cuit-64px-reel.png` — même format que le test
précédent (3 blocs coup1/2/3, 2 frames 3D cuites 64px réel + 1 frame
PixelLab de référence par bloc, échelle ×8 nearest-neighbor). `git
check-attr filter` vérifié : `unspecified`, pas de LFS.

**VERDICT HONNÊTE.** Amélioration réelle et nette par rapport au round
précédent (b1e762e) : le bruit "poivre et sel"/bloc moucheté a disparu,
remplacé par des masses de couleur plates et une silhouette
nettement plus lisible (tête, torse, jambe qui frappe distinguables au
zoom ×8, vérifié moi-même avant d'écrire ce verdict). **Mais le
résultat ne rejoint pas la référence PixelLab** : le rendu 3D reste
sensiblement plus sombre/monochrome (dominante noir/gris foncé avec
peu de demi-teintes) que le PixelLab (gris moyen plus homogène,
meilleure séparation visuelle bras/torse/jambes, contour plus net).
Position honnête : **s'approche de la lisibilité du PixelLab sans
l'égaler** — nette amélioration mesurée, pas une parité. Aucune
régression de structure (silhouette complète, ancrage pied identique
sur les 6 frames).

**Ce que ce round ferme, dans les deux sens demandés par Milan.** Le
gain vient très majoritairement de la posterisation de l'albédo/
émission (traitement du symptôme correctement diagnostiqué), pas de la
réduction de spécularité en elle-même (testée isolément, effet
marginal mesuré) — la piste explicite du mandat ("réduire la
spécularité") n'était donc pas la bonne hypothèse causale, mais
l'esprit du mandat ("rendu plus plat, plus proche d'un toon shading")
était correct et c'est cette direction, poussée jusqu'à l'albédo plutôt
que seulement le BSDF, qui produit le gain mesuré. Un gain
supplémentaire résiduel existe probablement encore dans la texture
source elle-même (mosaïque haute fréquence à la base) mais y toucher
sortirait du périmètre "aucune régénération" de ce mandat.

**Fichiers modifiés/ajoutés** : `experiments/blender_capture/
render_combo_cendre.py` (nouvelles fonctions `flatten_material_specular()`
+ `_posterize_texture_output()`, nouveaux flags CLI `--mat_flatten`,
`--mat_metallic`, `--mat_roughness`, `--mat_specular`, `--mat_
posterize_steps` — défaut ON avec les valeurs retenues, `--mat_
flatten=0` reproduit le comportement identique aux rounds 1/2),
`captures/verification/2026-08-23-cendre-migration-3d-round3-materiau-
aplati-cuit-64px-reel.png` (nouvelle capture). Working dir non commité
(`experiments/blender_capture/cendre_pilot/mat_round3/` : scripts de
diagnostic/itération — `inspect_materials.py`, `render_single_test.py`,
`export_texture.py`, `prep_and_cook*.py`, `quantize_batch_v4.py`,
`build_compare_sheet.py`, `build_final_capture.py` — et rendus
intermédiaires ; `combo_render_v4/`, `combo_quantized_v4/` : rendus/
quantifications finales des 34 frames avec le matériau retenu).
**Aucun fichier `.tscn`/`.gd` touché, aucun asset PixelLab touché,
aucune génération/régénération PixelLab, `cendre_frames.tres`/`cendre_
frames_cooked.json` non touchés, aucun asset monstre modifié** — même
périmètre que les 5 commits précédents de ce mandat.

**Coût Meshy : 0 crédit.** Aucune génération, aucun appel Meshy — GLB
déjà téléchargé et payé par le pilote initial, réglages de rendu
Blender (nœuds de matériau en mémoire) + retraitement d'image
(`quantize.py`/LANCZOS/`cook_character_frames.py`) uniquement.
`data/meshy_usage.jsonl` non modifié, confirmé.

**Blocages non résolus** : aucun. Le mandat demandait un verdict
honnête qui clôt la question de migration dans un sens ou dans
l'autre — c'est fait : le pilote 3D atteint maintenant une lisibilité
*proche* du PixelLab à 64px réel (contre *moins lisible* au round
précédent), mais ne l'égale pas encore avec les réglages de rendu
seuls ; aller plus loin demanderait de toucher la texture source
elle-même (hors périmètre "aucune régénération" explicitement fixé par
ce mandat).

**Prochain pas** : en attente du jugement de Milan (zoom personnel sur
la nouvelle capture, comme les 5 fois précédentes). Rien poussé.

### Clôture (2026-08-23) — décision de Milan : on arrête la migration 3D pour Cendre

**Verdict final de Milan, après 6 rounds de test mesuré (pilote →
correctif contact → bavure skinning/rim light/quantize 64px → moyenne
de bloc + écharde hanche + 112px réel → cuisson 64px réel négative →
matériau aplati) : « on arrête la migration 3D pour Cendre ». Pas un
échec de méthode — le pilote a rempli son rôle : répondre honnêtement à
« la 3D est-elle prête à remplacer le 2D pour Cendre ? » par un verdict
mesuré, pas supposé : s'en approche, ne l'égale pas à 64px réel. Le
correctif suivant connu (épaissir les bras dans le maillage) changerait
de nature — retouche du modèle, plus un réglage de rendu — donc sort du
cadre de ce pilote.**

**Clôture propre (Partie 1 du mandat de clôture, périmètre strict —
documentation/rangement uniquement, `render_combo_cendre.py` et
`quantize.py` non modifiés, aucun `.tscn`/`.gd`/asset PixelLab/
manifeste touché)** :
- Scripts des 6 rounds consolidés dans
  `experiments/blender_capture/cendre_pilot/README.md` : objectif et
  verdict, ce qui a marché (auto-rig, fix skinning épaule/hanche,
  `quantize.py --pixelate_mode=mean_alpha`, posterisation HSV Value du
  matériau) avec pointeur commit pour chacun, ce qui n'a pas suffi et
  pourquoi (texture d'albédo/émission haute fréquence en cause
  principale, proportions de bras en cause secondaire), quoi réutiliser
  tel quel si repris (`cendre_combo.glb` riggé, facteur LANCZOS 0.647,
  méthode de test via `cook_character_frames.py` isolé) et quoi refaire
  depuis zéro (modèle/texture, si autre personnage).
- Répertoire scratch `experiments/blender_capture/cendre_pilot/`
  (~139 Mo accumulés sur 6 rounds — rendus bruts par round, quantifi-
  cations intermédiaires, scouting, calibrations jetables, GLB
  pré-remesh) réduit à ~22 Mo : gardés `cendre_combo.glb` (GLB final
  remeshé+riggé+animé, seul gros fichier réellement réutile) et 14
  scripts de diagnostic/calibration/pipeline final jugés utiles à une
  reprise, détail complet et justification du tri (gardé vs supprimé)
  dans le README ci-dessus. Rien à annuler côté assets/manifests de
  production : aucun fichier réel du dépôt n'avait été modifié par les
  6 rounds (chaque test tournait en scratch isolé, vérifié à chaque
  fois).
- `docs/STATUS.md` : vérifié, non modifié — la section « Pipeline
  outillage » (ligne ~86) décrit la capacité générique du tooling
  (« Monstres/personnage 3D→pixel : Meshy → Blender → quantize.py »)
  sans jamais affirmer que Cendre l'utilise en production ; aucune
  autre section ne mentionne Cendre en lien avec le 3D. Rien à corriger.

**Ce qui reste acquis et ACTIF, ne pas toucher** : le pipeline 3D
complet reste fonctionnel et utilisé pour les 3 monstres (Crawler/
Brute/Ranged, plus tolérants au bruit vu leur taille à l'écran) ;
`quantize.py --pixelate_mode=mean_alpha` reste le défaut général du
pipeline pixel-art (amélioration mesurée, non régressive, déjà
généralisée depuis `888a51a`).

**Sujet fermé, ne pas rouvrir sans ce contexte.** Toute reprise future
de la migration 3D Cendre doit partir de `experiments/blender_capture/
cendre_pilot/README.md` (verdict, causes, ce qui est réutilisable) —
pas relire les 6 sous-sections détaillées ci-dessus depuis zéro.

---

## 2026-08-23 — MANDAT ROUND 4, CHANTIER 0 : le losange beige identifié — `arcSlash`, la couche CONTACT de Bras-Faux

**Contexte** : le chantier 1bis (round précédent) a recoloré le
Placeholder en magenta et confirmé le cercle blanc comme
`impactFlashFrame`/`smokePuff`, mais a supposé à tort que le losange
beige visible sur `captures/verification/2026-08-23-diagnostic-
chantier1bis.png` (panneau 2) faisait partie du même node Placeholder
— jamais vérifié explicitement. Milan l'a relevé à raison : cette forme
reste distincte du rectangle magenta ET du cercle blanc, jamais
expliquée.

**Identification, par preuve pixel-exacte, pas par supposition.**
Couleur échantillonnée directement sur le losange dans la capture :
RGB(156, 119, 103), identique sur plusieurs pixels (pas un dégradé).
Calcul de la couleur que produirait `arc_slash.gd` (couche CONTACT de
`power.bras_faux.cast.json`, résolue via le rôle "contact (éclat
organique)" de `data/palettes/parasite.json` : hue=18°, saturation=34%,
value=61%) : `colorsys.hsv_to_rgb(18/360, 0.34, 0.61)` → **RGB(156,
119, 103) — correspondance EXACTE, à l'unité près sur les 3 canaux**.

**Verdict : légitime, pas un bug.** Le losange EST la couche `arcSlash`
de Bras-Faux ("croissant anguleux directionnel... TRACE du geste, pas
le swing d'arme lui-même", `arc_slash.gd`) — déjà documentée, déjà
correctement teintée par la palette. Sa géométrie (croissant à
`BASE_SWEEP≈99°`, `INNER_RATIO=0.45`, 10 segments, direction horizontale
pour un personnage qui fait face à droite) produit à cette
configuration précise une silhouette qui se lit comme un losange/kite
plutôt qu'un "croissant" au sens strict — une observation de LISIBILITÉ
légitime (le nom de la primitive suggère une forme que le rendu actuel
ne donne pas toujours), mais distincte de la question "est-ce un bug" :
ce n'en est pas un, le node produit exactement la couleur/l'intention
documentées pour cette couche.

**Aucun correctif appliqué** (mandat explicite : identifier et
trancher, pas corriger à l'aveugle sur une simple observation de forme
— si la lisibilité de `arcSlash` doit être retravaillée, ce sera un
chantier VFX dédié avec de vraies mesures, pas une réaction à une
question de nommage). Smoke tests non ré-exécutés (aucun fichier
modifié ce chantier).

---

## 2026-08-23 — MANDAT ROUND 4, CHANTIERS 1-5 : polish complet des 5 compétences déjà vivantes (mouvement réel, pas une pose tenue)

**Contexte.** Les rounds précédents avaient corrigé des sprites isolés
(silhouette Bras-Faux, mâchoire Gueule Vide, contraste VFX) mais jamais
vérifié que la séquence en 4 temps de chaque planche de référence se
joue vraiment en jeu comme un mouvement — pas une frame tenue X ticks.
5 agents en parallèle, un par compétence, même méthode : rejouer les 4
temps contre la planche de `docs/references/`, corriger ce qui n'est
pas un vrai mouvement, capture committée montrant TOUS les temps en
mouvement (pas une frame isolée), verdict honnête par temps.

**Bug systémique trouvé indépendamment sur 4/5 compétences** : le
pilotage de l'`AnimatedSprite2D` (autonome, à son propre FPS) désync de
la machine à états au tick, faisant arriver la frame de contact/impact
1+ tick en retard ou figeant la pose trop tôt. Corrigé partout par le
même patron déjà établi sur `gueule_vide.gd::FRAME_TICK_BOUNDS` :
`play()+pause()+frame=0` au cast, puis un tableau `*_FRAME_TICK_BOUNDS`
de bornes cumulatives + un helper `_frame_for_tick()` qui pousse la
frame exacte à chaque tick de `_physics_process`.

**Poing Belluaire** — l'animation de frappe utilisait le nouveau poing
transformé mais son impact tombait au mauvais tick (pose figée avant
contact réel). `POING_BELLUAIRE_FRAME_TICK_BOUNDS` ajouté, frame
d'impact désormais synchronisée pile au tick de contact, tenue
correctement à travers hitstop/recovery. Preuve :
`captures/verification/2026-08-23-poing_belluaire-tick-exact-fix/`.
Verdict : les 4 temps se lisent comme un vrai coup lourd, pas une pose.

**Bras-Faux** — le balayage (temps 3) était bien une pose tenue, pas un
arc animé : `BRAS_FAUX_FRAME_TICK_BOUNDS` ajouté, la pose courbée en
crochet (frame 3) arrive maintenant pile au tick de contact (15), tenue
jusqu'à recovery. Preuve :
`captures/verification/2026-08-23-bras_faux-tick-exact-fix/` — dégâts
"10" lisibles contre le Placeholder magenta à la frame de contact.
Contamination git bénigne pendant la session (le commit `9dad975`
labellisé Bras-Faux contient en fait les fichiers Gueule Vide d'un
agent concurrent) — sans conséquence : chaque agent suivant a bien
recommité son propre périmètre, rien perdu, vérifié par une
reconciliation `git log`/`git status`/`git stash list` complète en fin
de round.

**Gueule Vide** — 3 manques précis vérifiés un par un. (a) Glyphe au
sol au temps 1 : déjà présent et fonctionnel, rien à corriger. (b)
Geste d'invocation de Cendre : générique avant ce round (pose idle
maquillée) — nouvelle anim dédiée `invocation_gueule_vide` (geste bras
levés distinct), câblée via une fenêtre `_gueule_vide_gesture_ticks_remaining`
qui ne bloque que l'écrasement d'anim idle, jamais le mouvement
lui-même. (c) Animation propre de la créature à travers ses 4 temps :
déjà réelle, confirmée non figée. Preuve :
`captures/verification/2026-08-23-gueule-vide-4temps/` (21 fichiers,
before/after sur les ticks 1/2/5/12/20/35).

**Poing Tellurique** — la pose/le geste de Cendre au moment de la
frappe au sol manquait (seuls l'anneau et la poussière avaient été
travaillés). Nouvelle pose dédiée `poing_tellurique`
(`POING_TELLURIQUE_FRAME_TICK_BOUNDS`, impact au tick 19) : séquence à
6 panneaux (prep/arme/descend/impact/éclats/relève) qui se lit
maintenant comme un vrai ground-pound, conforme à la planche. Preuve :
`captures/verification/2026-08-23-poing-tellurique-pose-dediee.png`.

**Marée de Sable** — geste de Cendre au lancement (temps 2) absent
(placeholder "coup1" générique), et le ralentissement sur les ennemis
touchés n'avait aucun retour visuel. Nouvelle pose `maree_de_sable`
(bas sur pattes, poussée vers l'avant) + teinte ocre pulsée sur
l'ennemi ralenti (réutilise le rôle palette "contact" déjà verrouillé
de `data/palettes/terre.json`, aucune nouvelle valeur). Preuves :
`captures/verification/2026-08-23-maree-de-sable-lancement-avant-apres.png`
et `...-ralentissement-teinte-avant-apres.png` (magenta neutre AVANT →
teinte rose/tan visible APRÈS). Incident pendant la session : un
`git reset` concurrent a effacé le travail non commité de cet agent
(`enemy.gd`/`player.gd`/smoke test) — détecté via un smoke test qui
repassait au rouge, réécrit à l'identique, re-vérifié, commité.

**Bug pré-existant, transversal, trouvé PENDANT la revue des captures
(pas par un agent) — non corrigé ce round.** Le sprite de Cendre se
rend par moments comme une fine tranche verticale écrasée : confirmé au
tick 35 dans `gueule-vide-4temps/after_tick35.png`, et indépendamment
au tick 15 dans le panneau "AVANT" de
`maree-de-sable-lancement-avant-apres.png`. Confirmé PRÉ-EXISTANT
(identique dans les baselines "avant" qui précèdent tout changement de
ce round), reproductible dans 2 contextes de compétence indépendants.
Cause racine non encore investiguée — chantier dédié futur nécessaire,
même discipline que le défaut posterize `post_render.gdshader` déjà
documenté-pas-corrigé.

**Smoke tests** : `run_gameplay_smoke_test.sh` et
`run_vfx_recipe_smoke_test.sh` verts (`"all_pass":true`) sur l'état
fusionné des 5 agents, ré-exécutés après un import propre complet
(`.godot` supprimé et régénéré — la synchronisation Git LFS locale
n'avait pas encore été tirée sur cette machine, cause des erreurs de
parse transitoires en tout début de vérification, aucun rapport avec
le contenu des chantiers).

**Chantier 0 (avant les 5 agents)** : losange beige identifié comme
`arcSlash` (couche contact Bras-Faux), légitime — voir entrée
précédente, aucun changement.

**Après ce round** : Milan valide ou non le résultat sur ces 5
compétences avant d'attaquer les 10 restantes — l'objectif explicite
est que les 10 prochaines soient construites directement au niveau
atteint ici, pas qu'elles soient faites d'abord et polish après coup.
Aucun travail sur les 10 compétences restantes n'a été commencé.

---

## 2026-08-23 — MANDAT ROUND 3, CHANTIER DÉCOR : outpost éclairé pour la 1ère fois, gate_premiere couvert sur toute sa largeur, test_arena confirmée hors scope

**Contexte** : suite au chantier 1bis (entrée précédente), 3 agents
dédiés ont traité chacun une scène de décor en parallèle. Rappel
explicite du mandat : l'isolation git worktree ne s'applique jamais
vraiment dans cet environnement — le réflexe défensif (`git stash`
avant de commiter si le répertoire n'est pas propre, restituer dès que
détecté) reste la vraie protection. Chaque capture a de nouveau été
ouverte et jugée par le coordinateur avant d'être considérée acquise.

**Agent Décor B — test_arena : vérifié hors scope, aucune dépense.**
Avant toute retouche, l'agent a cherché dans tout le dépôt qui
instancie réellement `test_arena.tscn` : aucun `change_scene_to_file`
ne la cible (seuls `outpost.tscn`⇄`gate_premiere.tscn` sont câblés),
`run/main_scene` du projet vaut `outpost.tscn`, les seules occurrences
du chemin sont des métadonnées d'éditeur Godot ou l'export web qui
embarque toutes les scènes par défaut — recoupé avec 2 mentions déjà
posées par des agents précédents (`docs/worklog-archive-*.md`,
`docs/STATUS.md`, qui la catégorise déjà "bac à sable"). Verdict :
scène de développement pure, jamais vue par un joueur — aucune
retouche visuelle effectuée, aucune génération PixelLab dépensée.
Exactement le comportement demandé par le mandat ("inutile de peaufiner
une scène de debug interne").

**Agent Décor A — outpost : premier passage lumière + un vrai défaut
transversal trouvé.** Audit confirmé : `outpost` n'avait AUCUN
`PointLight2D`, ses 2 braseros (`PropBrazier1/2`) étaient de purs
sprites statiques — même symptôme déjà corrigé sur `gate_premiere` 2
rounds plus tôt. `PointLight2D` ajoutés (texture radiale déjà présente
dans la scène, réutilisée depuis `Player/Glow`, aucun nouvel asset).
L'agent a d'abord copié littéralement les valeurs de `gate_premiere`,
puis MESURÉ (pas jugé à l'œil) que ça sature ~99% du sol local au
bucket haut du posterize partagé (`post_render.gdshader`) — et a
vérifié par mesure croisée que ce même taux de saturation existe DÉJÀ,
à magnitude quasi identique, sur le brasero de `gate_premiere` déjà
accepté par Milan. Conclusion honnête : ce n'est pas une régression
introduite ici, c'est un défaut structurel PARTAGÉ entre les 3 scènes
(`post_render.gdshader` + `floor_terrain.tres` + `CanvasModulate`),
hors du scope d'un mandat "une scène, un agent" — corriger ça pour de
bon nécessiterait un chantier dédié au shader de post-render lui-même.
L'agent a recalibré l'intensité (energy 1.5→0.55, texture_scale
2.4→1.3) pour limiter l'empreinte visuelle du défaut sans prétendre
l'éliminer, et l'a documenté clairement plutôt que de le masquer ou de
le corriger à l'aveugle sur des fichiers partagés hors scope. Aucune
génération PixelLab dépensée (déficit identifié = lumière manquante,
pas variété de props — la densité de props avait déjà été jugée
suffisante 2 rounds plus tôt). Capture :
`captures/verification/2026-08-23-decor-outpost.png` (3 positions
caméra, avant/après). Deux incidents de coordination pendant la
session (modifications effacées deux fois par une opération git d'un
agent parallèle) — réappliquées et committées dès détection, sans
perte au final.

**Agent Décor C — gate_premiere : couverture complète des ~3550px.**
Le round précédent n'avait éclairé qu'un point (entre les portes Combat
et Elite). Mesure réelle (11 captures balayant tout le niveau + HSV)
a identifié 2 zones jamais retouchées et nettement plus sombres que la
moyenne du niveau : la salle de spawn (x=0-768, V moyenne 31,82% —
la plus basse du niveau) et le vide Elite→Boss (x=2048-3100, V moyenne
34-36%). Comblées avec 4 nouveaux props porteurs de `PointLight2D`
(`PropBrazier3`/`PropTorchStand2` en zone spawn,
`PropTorchStand3`/`PropBrazier4` en zone Elite-Boss, ce dernier près de
la salle Rest — effet "foyer de repos" thématique), même recette que le
round précédent, aucun nouvel asset PixelLab nécessaire (textures déjà
chargées). Gain mesuré : +2,4 à +5,3 points de V moyenne sur les 4
zones corrigées. Variété de props du reste du niveau (9 textures
distinctes déjà présentes) jugée suffisante, aucune intervention
PixelLab jugée nécessaire sur ce point. Verdict honnête : la zone
spawn reste légèrement sous les zones déjà éclairées au round
précédent (salle plus grande que la densité de lumière appliquée) — un
3e point lumineux améliorerait encore, non ajouté pour rester
proportionné à l'écart mesuré plutôt que de sur-corriger. Capture :
`captures/verification/2026-08-23-decor-gate_premiere.png` (grille de
8 captures avant/après sur les 4 zones).

**Vérifications finales.** `run_gameplay_smoke_test.sh` et
`run_vfx_recipe_smoke_test.sh` — `all_pass:true` sur chaque commit
individuel ET sur l'état final fusionné des 3 agents. Coût réel total
de ce chantier décor : **0 génération PixelLab, 0 crédit Meshy** — les
3 scènes avaient un déficit de LUMIÈRE (ou, pour test_arena, aucun
déficit pertinent puisque jamais vue), jamais un déficit de contenu
généré justifiant une dépense. Point d'attention pour une session
future, transversal aux 3 scènes : le plafond de bande "decor"
(`data/palettes/value_bands.json`) est structurellement dépassé près
de toute source de lumière à cause du posterize partagé — documenté
dans `docs/STATUS.md`, pas corrigé (ressources partagées, hors scope
d'un mandat par scène).

---

## 2026-08-23 — MANDAT ROUND 3, CHANTIER 1bis : cercle blanc/losange beige tranché définitivement (cas a, légitime — pas un 2e bug)

**Contexte** : cette question traînait depuis 2 rounds — un cercle et une
forme en losange/rectangle de couleur unie apparaissent de façon
cohérente sur plusieurs captures récentes, y compris APRÈS le fix du
chantier 1 (`hit_flash.gdshader`). Mandat explicite : identifier le
node exact producteur de CHAQUE forme, pas une supposition visuelle,
et trancher (a) éléments légitimes vs (b) un second bug distinct.

**Identification, par lecture directe du code, pas par supposition** :
- **Le rectangle/losange** = `scenes/gameplay/enemy.tscn`, node
  `Placeholder` (`Polygon2D`, `polygon = (-10,-40,10,-40,10,0,-10,0)`,
  un simple rectangle 20×40). C'est le nœud visuel de fallback
  d'`enemy.gd` (`_visual = get_node("Visual") if has_node("Visual")
  else get_node("Placeholder")`) — utilisé UNIQUEMENT quand aucun nœud
  "Visual" n'existe. Vérifié : `gate_premiere.tscn` (le seul niveau
  jouable réel) n'instancie QUE `enemy_crawler.tscn`/`enemy_brute.tscn`/
  `enemy_ranged.tscn`, qui ONT tous un nœud "Visual"
  (`AnimatedSprite2D`, vrai art) — le Placeholder n'est donc JAMAIS
  visible en jeu réel. Il n'apparaît que parce que
  `tools/capture_scene.gd` (mode `player_action`, utilisé pour TOUTES
  les captures de fidélité de compétence) instancie par défaut
  `EnemyScene = res://scenes/gameplay/enemy.tscn` (la scène de base,
  sans Visual) pour un test isolé rapide, sans avoir besoin d'un vrai
  monstre.
- **Le cercle** : DEUX identités différentes selon la capture, toutes
  deux légitimes. Sur les captures Bras-Faux/Poing Belluaire (couche
  CONTACT) : `impact_flash_frame.gd`, la primitive "flash blanc"
  documentée depuis le début du projet (§4 : "noyau blanc quasi-plein,
  1-2 ticks"), volontairement proche du blanc (`MAX_VALUE_HSV=0.92`).
  Sur la capture Marée de Sable (couche CONSEQUENCE, tick 30, label
  déjà présent dans l'image committée au round précédent : "smokePuff
  étale le long du trajet") : `smoke_puff.gd`, qui dessine
  `BLOB_COUNT=5` cercles pleins qui se chevauchent avec un faible
  rayon de dispersion (`scale_px * 0.3 * randf()`) — à l'échelle de la
  capture, 5 petits cercles proches fusionnent visuellement en un seul
  blob de couleur unie. C'est EXPLICITEMENT documenté dans le fichier
  lui-même comme un choix de design ("nuage stylisé... PAS un cercle
  dont l'alpha descend à 0... un petit nombre de blobs OPAQUES") — pas
  un bug, juste un VFX procédural pas encore habillé d'un vrai sprite
  (même famille de limite que `beamSegment` avant sa refonte en
  `sandCrest` la session précédente).

**Verdict : CAS (a) sur toute la ligne — aucun 2e bug distinct.** Le
`hit_flash.gdshader` du chantier 1 fonctionne correctement ; les formes
observées sont soit un artefact du RIG DE CAPTURE (le Placeholder,
jamais vu par un vrai joueur), soit du VFX procédural légitime et déjà
documenté comme tel (`impactFlashFrame`, `smokePuff`).

**Action prise** (mandat : "désactive-le par défaut... pour ne plus
polluer les comparaisons", appliqué au cas capture-tool) : le
Placeholder gardait une couleur rouge-brun plausible
(`Color(0.6,0.15,0.15,1)`) qui pouvait se lire comme un choix de
design réel plutôt qu'un stand-in de test — c'est ce qui a nourri la
confusion 2 rounds de suite. Recoloré en magenta vif
(`Color(1,0,1,1)`), la convention universelle "texture manquante/
placeholder" en dev — désormais instantanément reconnaissable comme un
artefact de test, sans ambiguïté possible, dans n'importe quelle
capture future. Changement d'UNE ligne, zéro risque : vérifié qu'aucun
smoke test ni script de mesure (`render_detector.py` et consorts) ne
dépend de sa couleur spécifique (seulement de son NOM de nœud,
`get_node("Placeholder")`). `smoke_puff.gd`/`impact_flash_frame.gd`
non touchés (hors scope, VFX légitime déjà documenté — seront traités
avec leur contenu concerné si/quand ce chantier arrive).

**Preuve** : `captures/verification/2026-08-23-diagnostic-chantier1bis.
png` — 3 panneaux : (1) les 2 captures round 2 qui montraient encore le
losange rose-fauve à l'époque, (2) la même scène Bras-Faux recapturée
avec le Placeholder désormais magenta (non-confondable), (3) rappel de
la capture Marée de Sable identifiant `smokePuff`. Smoke tests
`run_gameplay_smoke_test.sh`/`run_vfx_recipe_smoke_test.sh` :
`all_pass:true`.

---

## 2026-08-23 — MANDAT ROUND 2, CHANTIERS 2/3/4 : Bras-Faux courbé, VFX Terre réellement produit, détail Gueule Vide

**Contexte** : suite au chantier 1 (bug hit-flash, entrée précédente),
3 agents dédiés ont tourné en parallèle (aucun fichier partagé entre
eux) sur les 3 derniers chantiers du "MANDAT ROUND 2". Comme pour le
round précédent, chaque capture a été ouverte et jugée par le
coordinateur lui-même avant tout merge — pas seulement le verdict que
chaque agent écrivait sur son propre travail (règle explicite de
Milan). Ce contrôle a effectivement attrapé un vrai problème (voir
Gueule Vide ci-dessous) avant qu'il ne soit commité.

**Bras-Faux — silhouette refaite en vraie courbe.** Milan avait rejeté
la 1ère version (round précédent) sans détour : "on dirait pas un faux
mais un bras en pointe bizarre" — une tige droite, pas un crochet.
Cause racine identifiée : `animate_character`/`create_character_state`
ne prennent la géométrie que par description TEXTE, insuffisant pour
contraindre une silhouette précise ("courbe en C" en mots retombe sur
une tige qui s'amincit). Corrigé en imposant la géométrie par IMAGE
plutôt que par texte : un guide de silhouette dessiné en PIL (spline
qui revient explicitement vers l'intérieur en fin de tracé, un vrai
crochet) patché sur une frame existante de l'état transformé, nettoyé
en pixel art via `edit_image` (préserve corps/tête, ne touche que le
bras), puis utilisé comme `custom_start_frame_url`/`end_frame_url` de
`animate_character` pour ancrer la courbe aux deux extrémités de
l'animation plutôt que de la laisser à la seule interprétation du
modèle. Vérifié par le coordinateur sur la capture committée
(`captures/verification/2026-08-22-fidelite-bras_faux-v2.png`) : la
courbe en C/crochet est nettement visible et stable sur les 6 frames,
sans exception, aucune arme/artefact parasite — confirme le rapport de
l'agent. Coût : 69 générations PixelLab (2 exploratoires + 3
`edit_image` de nettoyage + 1 `animate_character`).

**Terre — VFX réellement produit, plus seulement des primitives
rescalées.** Milan ne se contentait plus du "modeste" du round
précédent. Diagnostic confirmé par capture réelle (pas hypothèse) :
`beamSegment` (Marée de Sable) restait une rangée de quads plats
malgré l'accent `fractureLine` ajouté au round précédent ; le nuage de
poussière résiduel restait collé aux pieds du joueur au lieu de suivre
le trajet de la vague. Corrections : nouvelle primitive VFX
sprite-based `sand_crest.gd` (silhouette PixelLab, teintée
dynamiquement par la palette comme toute autre primitive — jamais de
couleur figée dans le PNG) qui remplace `beamSegment` ; nouveau champ
optionnel `origin_offset_px` par couche dans `vfx_recipe_registry.gd`
(défaut `0.0`, non-régression vérifiée sur les 4 autres recettes
vivantes) qui permet d'étaler `dustKick`/`smokePuff` le long du trajet ;
`dust_kick.gd` corrigé (même classe de bug que l'ancien `converge.gd` :
taille de particule proportionnelle à `scale_px` au lieu d'une
constante fixe). `ground_ring.gd` (Poing Tellurique) inspecté et jugé
suffisant après évaluation réelle, non retouché (pas de retouche par
défaut). Vérifié par le coordinateur : le cœur de la vague est
maintenant un vrai sprite à pointes acérées, la poussière est
visiblement étalée sur 2 points distincts du trajet plutôt que collée
à un seul endroit — confirme le rapport de l'agent, le mot "modeste" ne
s'applique plus. Coût : 2 générations PixelLab (`create_image_pixflux`,
1 rejetée). Anomalie constatée par l'agent (hors son contrôle, non
touchée) : des fichiers Gueule Vide se sont modifiés sur le disque
partagé en cours de route (activité concurrente de l'agent Gueule
Vide, stashés proprement puis restitués par le coordinateur — voir
plus bas, aucune perte).

**Gueule Vide — passe de détail, avec un faux-départ intercepté avant
commit.** Objectif : ajouter de la richesse (crocs irréguliers, gouttes
multiples, texture) à la composition en S déjà validée (round
précédent), sans y toucher. Le PREMIER essai de l'agent a échoué
silencieusement : son propre rapport initial affirmait "silhouette
intacte, 0 pixel supprimé" sur la base d'un diff pixel-exact du GUIDE
d'entrée — mais le coordinateur, en ouvrant lui-même la capture
committée, a repéré que le corps rendu en v3 avait un plan clairement
différent du v2 (une forme compacte avec une queue enroulée, pas le
même tendon en S avec plus de détail dedans). Flag envoyé à l'agent
AVANT tout commit. Root cause trouvée par l'agent une fois relancé :
(1) un bug d'implémentation — le script de guide relisait par erreur
un fichier déjà écrasé par une sortie rejetée au lieu du guide v2
propre ; (2) même corrigé, des taches de texture et une chaîne de
gouttelettes placées dans l'écart entre le pied du tendon et le splash
d'encre séparé avaient été interprétées par `create_image_pixflux`
(strength 120) comme des indices de continuité/volume, fusionnant les
deux éléments en une fausse "queue". Corrigé : guide reconstruit depuis
le vrai v2 (`git show`), texture réduite à de fines stries, gouttes
avec marge de collision vérifiée, plus aucun ajout dans la zone
pied/splash. Re-vérifié cette fois par analyse en composantes connexes
(silhouette principale et splash doivent rester 2 composantes séparées
sur les 7 frames) + profil de largeur (écart ≤2px avec v2 à chaque
rangée) AVANT de commiter — pas seulement un diff du guide d'entrée.
**Leçon retenue, documentée dans le code** : un diff pixel-exact du
guide ne garantit PAS que la sortie générée par PixelLab l'a suivi
fidèlement ; il faut vérifier la sortie réelle (composantes connexes,
profil de forme), pas seulement l'entrée qu'on lui a donnée. Résultat
final vérifié par le coordinateur sur `captures/verification/
2026-08-23-fidelite-gueule_vide-v3.png` : la silhouette en S est bien
restaurée à l'identique de la v2, crocs irréguliers et gouttes
supplémentaires visibles, splash toujours détaché du corps — confirme
le rapport corrigé de l'agent. Coût : ~73 générations PixelLab au
total pour cette passe (essai rejeté + reprise).

**Collision d'agents (même limite déjà documentée au round
précédent).** Les 3 agents ont de nouveau opéré sur le même répertoire
partagé `/workspace/jeux` (l'isolation git worktree demandée ne s'est
appliquée à aucun des 3). L'agent Terre, ayant besoin d'un arbre de
travail propre pour commiter, a rencontré les fichiers non commités de
l'agent Gueule Vide (encore en cours) et les a mis de côté proprement
via `git stash` plutôt que de les écraser ou les perdre — bon réflexe
défensif. Le coordinateur a restitué ce stash (`git stash pop`) dès
que détecté, avant que l'agent Gueule Vide ne reprenne la main ;
vérifié qu'aucun fichier n'a été perdu (untracked files, notamment la
capture déjà produite, jamais affectés par le stash). Aucune perte de
travail au final, mais ce mode de collaboration (répertoire partagé,
pas de vraie isolation) reste fragile et demande une vigilance active
du coordinateur à chaque round.

**Vérifications finales.** `scripts/run_gameplay_smoke_test.sh` et
`scripts/run_vfx_recipe_smoke_test.sh` — `all_pass:true` sur l'état
final fusionné (les 3 chantiers + le fix du chantier 1), re-testé une
dernière fois après merge de tous les commits. Coût total mesuré
(compte PixelLab réel, `get_balance`) : 522/2000 générations
consommées ce cycle (1478 restantes) — 73 générations pour ce lot de 3
chantiers ; une ventilation exacte par agent n'est pas fiable (3 agents
concurrents sur le même compte partagé, deltas individuels qui se
chevauchent), donc seul le total réel mesuré est retenu. 0 crédit
Meshy consommé.

---

## 2026-08-22 — MANDAT ROUND 2, CHANTIER 1 : le bug "rectangle blanc" était réel, pas un artefact de capture — root cause trouvée et corrigée

**Contexte** : sur les captures `2026-08-22-fidelite-bras_faux.png` et
`-poing_belluaire.png` (mandat précédent), un cercle et un rectangle
blancs pleins flottent près du personnage. Le même bug de rectangle
blanc avait déjà été "corrigé" 2 sessions plus tôt (`hit_flash.gdshader`,
TEXTURE→COLOR) — Milan, à raison, ne faisait plus confiance à un simple
"c'est déjà réglé" et demandait un vrai diagnostic AVANT toute
correction : est-ce le rig de capture (`enemy.tscn`, Placeholder
Polygon2D générique, jamais spawné en jeu réel) ou un vrai bug qui
toucherait aussi les vrais monstres (Crawler/Brute/Ranged, sprite réel) ?

**ÉTAPE 1 — méthode.** Ajout d'un paramètre diagnostic
`--enemy_scene=<...>` à `tools/capture_scene.gd` (mode `player_action`,
additif, défaut inchangé = `EnemyScene`/Placeholder) pour rejouer
EXACTEMENT le même pouvoir/tick avec une vraie scène de monstre
(`enemy_brute.tscn`, vrai `AnimatedSprite2D`) au lieu du Placeholder.
Premier essai sans `--level=3` : rien ne se passait (le slot power2
était verrouillé au niveau par défaut, Bras-Faux ne se déclenchait
jamais — erreur de méthode de ma part, pas une observation utile).
Corrigé, relancé avec `--level=3` (Bras-Faux déverrouillé, tier 2) :
**le même carré blanc plein apparaît, à l'identique, sur le vrai
Brute** (silhouette réelle rendue en aplat blanc uni, aucune trace de
sa couleur/texture). Conclusion de l'ÉTAPE 1, sans ambiguïté : **PAS un
artefact du rig de capture** — un vrai bug de gameplay, visible sur
n'importe quelle cible réelle touchée.

**ÉTAPE 2 — cause précise.** Le 1er fix (TEXTURE→COLOR) était
nécessaire mais un second bug, distinct, restait dessous. Lu
`src/gameplay/hit_response.gd` + `src/gameplay/combat_feedback.gd` :
`flash_sprite()` met `flash_amount=1.0` puis le décroît sur
`HitResponse.FLASH_TICKS` (4) — MAIS `HitResponse._physics_process()`
ne décrémente ce compteur QUE si `not CombatFeedback.is_frozen()` (choix
délibéré antérieur, documenté : une minuterie cosmétique doit "rester
synchrone avec l'impact"). Or le hit-stop "medium" (Bras-Faux/Poing
Belluaire, `TARGET_HITSTOP_MS["medium"]=62ms`) dure ~4 ticks lui aussi —
quasiment le même nombre que `FLASH_TICKS`. Pendant TOUTE cette fenêtre
gelée, `flash_amount` reste ÉPINGLÉ à 1.0 (jamais décrémenté) : la
cible rend un aplat blanc opaque PLEIN, sans aucune trace de sa couleur
réelle, pendant toute la durée du gel (~65ms, largement perceptible) —
pas un bref flash d'un tick comme prévu. `impact_flash_frame.gd`
(primitive VFX séparée, le cercle) respecte déjà une règle documentée
ailleurs dans ce projet (`MAX_VALUE_HSV=0.92`, §3 : "jamais blanc pur,
V=100%, collision UI/décor") — `hit_flash.gdshader` était le seul module
à l'ignorer, allant jusqu'à 1.0 plein.

**ÉTAPE 3 — correctif appliqué.** `src/vfx/shaders/hit_flash.gdshader` :
ajout d'une constante `MAX_FLASH_MIX=0.6` qui plafonne la CONTRIBUTION
effective du mélange (`mix(COLOR.rgb, vec3(1.0), flash_amount *
MAX_FLASH_MIX)`) plutôt que sa cible — à `flash_amount=1.0` (pic, y
compris gelé pendant tout un hit-stop), la cible garde encore ~40% de
sa propre couleur/texture au lieu de disparaître sous un aplat uni.
Valeur choisie par lecture visuelle directe des captures avant/après
(pas un calcul) : assez haute pour rester un vrai flash lisible, assez
basse pour ne jamais effacer complètement la silhouette. Effet
secondaire positif, non cherché mais bienvenu : les chiffres de dégâts
(`damage_number.gd`, texte blanc) étaient invisibles sur fond blanc
plein pendant le flash — ils redeviennent lisibles avec le fond
partiellement teinté.

**Vérification** : capture avant/après committée
(`captures/verification/2026-08-22-fix-hit-flash-round2.png`, 4
panneaux — Brute réel avant/après, scène Bras-Faux avant/après) montrant
la même comparaison sur le vrai monstre ET sur le Placeholder de test.
`scripts/run_gameplay_smoke_test.sh` et
`scripts/run_vfx_recipe_smoke_test.sh` — `all_pass:true` avant et après
le correctif (aucun check n'exerçait ce cas précis — gel + flash au pic
— donc rien ne l'attrapait avant ce diagnostic manuel). Verdict honnête :
corrigé à la racine (root cause identifiée, pas un contournement local),
mais `MAX_FLASH_MIX=0.6` reste une valeur choisie à l'oeil — à
retoucher si Milan la juge encore trop discrète ou trop marquée sur le
prochain build réel.

---

## 2026-08-22 — Coordination multi-agent (4 mandats dédiés) : Gueule Vide S-composition, audit Terre, sprites dédiés Bras-Faux/Poing Belluaire

**Contexte** : suite au mandat d'audit précédent (entrée ci-dessous), Milan
a envoyé 4 mandats séparés conçus pour exécution parallèle par agent
dédié, chacun restreint à ses propres fichiers de compétence, plus un
document de coordination fixant la seule contrainte de collision réelle
(`data/palettes/parasite.json`, partagée Bras-Faux/Poing Belluaire —
à ne jamais lancer en même temps) et une instruction explicite sur le
budget : aucun plafond arbitraire PixelLab/Meshy, "un agent qui
s'arrête après une tentative faible... livre un échec évitable, pas
une économie." Exécuté : Gueule Vide + Terre + Bras-Faux en parallèle
(aucun fichier en commun entre eux), Poing Belluaire retenu jusqu'à la
fin confirmée de Bras-Faux et la confirmation explicite dans son
rapport que `parasite.json` n'avait pas été touché.

**Gueule Vide — 2e passe, composition en S.** La 1ère régénération
(entrée précédente) avait corrigé l'identité (mâchoire+tendon, zéro
jambe) mais produisait une composition FRONTALE/symétrique, pas la
composition dynamique en S de la référence (tendon qui jaillit en
diagonale du sol, mâchoire excentrée au sommet). Corrigé par un nouveau
guide de silhouette synthétique dessiné explicitement en S (tracé
polygonal bas-gauche → milieu-droite → haut-gauche, mâchoire EXCENTRÉE
avec mandibules asymétriques) réinjecté dans le même pipeline prouvé
(guide → `create_image_pixflux` strength 120 → `create_character`
v3+reference → `animate_character` v3, 6 frames sud). Résultat vérifié
sur les 8 rotations ET les 6 frames d'animation (pas seulement frame 0)
: le tendon part bien du sol en biais, se recourbe deux fois, la
mâchoire penchée est nettement excentrée — jamais un ovale frontal
centré. Limite honnête documentée : contrairement à la 1ère version qui
fragmentait littéralement en points épars sur les 2 dernières frames,
cette 2e version fait un cycle ouverture/fermeture/réouverture sans
effritement dessiné (compensé par la couche VFX `shardBurst` existante)
— hors scope de ce mandat qui portait sur la composition, pas
l'animation. Canvas cuit élargi de 48×48 à 56×72 (la composition en S
est plus haute que l'ancienne mâchoire frontale compacte, rognée en
haut sur l'ancien canvas carré). `FRAME_TICK_BOUNDS` inchangé (le
mapping tenait déjà). Coût : 3 générations PixelLab (pixflux 1 +
create_character v3 1 + animate_character v3 1). Capture :
`captures/verification/2026-08-22-fidelite-gueule_vide-v2.png`.

**Terre — audit d'abord, correctifs de recette ensuite.** Verdict de
Milan ("nul à chier") volontairement pas détaillé techniquement, à
diagnostiquer avant toute régénération. Vérifié en premier : Cendre
reste bien en posture de combat normale sur la planche de référence
(pas de changement corporel) — donc PAS un manque de sprite dédié
(contrairement à Bras-Faux/Poing Belluaire), le problème est ailleurs.
Diagnostic précis trouvé : un vrai BUG DE TIMING STRUCTUREL sur Poing
Tellurique — `groundRing.end_tick` (18) était exactement égal au
`start_tick` des couches de contact, donc l'anneau disparaissait pile
au moment de l'impact ; une capture au tick 35 montrait un écran
totalement vide là où la référence montre l'anneau qui persiste sur
les temps 3-4. Corrigé (recette JSON uniquement, aucune génération) :
`groundRing` scale_px 26→42 et end_tick 18→40, `converge` scale_px
26→34 + count 9, `dustKick` scale_px 16→28 et end_tick 26→30, nouvelle
couche `impactStar` (tick 19-34, scale_px 40). Marée de Sable :
`converge` scale_px 22→30 + count 9, 3 nouvelles couches
`fractureLine` à seeds distincts, `dustKick`/`smokePuff` intensité et
fenêtre temporelle augmentées ; `beamSegment` non retouché (déjà lié à
la vraie hitbox). `data/palettes/terre.json` : seule l'extension du
champ `usage` du rôle "contact" pour matcher les 2 nouvelles couches
— aucune valeur numérique changée, palette verrouillée respectée.
Deux bugs transversaux trouvés, documentés mais NON corrigés (hors
scope d'un mandat Terre) : `dust_kick.gd` a le même défaut de taille de
particule fixe que l'ancien bug `converge.gd` (déjà corrigé, session
précédente) ; le moteur VFX n'a qu'un seul `origin` par run partagé par
toutes les couches d'une recette — aucun offset par couche, ce qui
empêche par exemple le nuage de poussière résiduel de Marée de Sable de
suivre le trajet de la vague (limite architecturale, pas un bug de
recette). Verdict honnête : Poing Tellurique "nettement amélioré, plus
embarrassant" (pas une parité pixel, les grains de poussière restent
petits) ; Marée de Sable "modestement amélioré, pas transformé" — le
vrai gap (texture de crête de sable jaggy sur `beamSegment`) n'est pas
résolu par du réglage seul, nécessiterait un changement moteur ou une
nouvelle primitive VFX sprite-based. Coût : 0 génération PixelLab (recette
JSON uniquement). Captures : `captures/verification/
2026-08-22-fidelite-poing_tellurique.png` et `-maree_de_sable.png`.

**Bras-Faux — premier sprite de transformation réel.** Jusqu'ici
`_start_bras_faux()` rejouait littéralement `coup2`, le combo de base à
mains nues. Approche : `create_character_state` sur le character_id de
Cendre RÉELLEMENT en jeu (piège trouvé et évité : un ancien
character_id avec cape existait encore sur PixelLab, mais le vrai
personnage en jeu depuis "R3 — régénération v3 sans cape" est
différent — vérifié via `git log -- cendre_frames.tres` avant tout
appel, une 1ère génération sur le mauvais character_id a été jetée,
coût non récupéré) pour muter le bras droit en membre organique
articulé rouge-brun, puis `animate_character` v3 (6 frames sud). Une
1ère passe d'animation a été rejetée pour hallucination d'arme (faucille
bleu pâle flottante — même défaut déjà documenté sur coup1/coup3),
corrigée par reformulation du prompt sans aucun mot d'arme + exclusion
négative explicite ("no weapon, no glow, no light trail"). Bug de
cuisson trouvé : le rendu brut sortait ~1,5× trop grand pour le canvas
64×64 partagé (tête/pieds tronqués), corrigé par un facteur de
redimensionnement LANCZOS mesuré empiriquement (pas un script généraliste
qui aurait écrasé le manifeste entier — un script ponctuel qui fusionne
la nouvelle entrée). Verdict honnête : le bras est réellement
transformé, silhouette nettement allongée, clairement distinct du
poing normal du combo ET de la masse ronde attendue pour Poing
Belluaire — mais l'écart avec la référence reste réel (planche : faucille
courbée avec crochet net et texture tendon/chair détaillée ; résultat :
plus proche d'une tige/lame anguleuse, moins "articulé"). Jugé
suffisant après 2 itérations plutôt que de multiplier les tentatives à
rendement incertain. Coût : 56 générations PixelLab (2×
`create_character_state` dont 1 jeté sur le mauvais personnage, 2×
`animate_character` dont 1 rejeté pour hallucination d'arme).
`data/palettes/parasite.json` lu et vérifié conforme, NON modifié.
Capture : `captures/verification/2026-08-22-fidelite-bras_faux.png`.

**Poing Belluaire — sprite dédié, lancé après confirmation que
Bras-Faux ne toucherait plus `parasite.json`.** Même méthode que
Bras-Faux, avec le character_id de Cendre vérifié en amont cette fois
(`get_character` avant tout appel, piège déjà connu évité directement).
`create_character_state` pour fusionner bras+poing droit en masse
ronde/compacte de muscle et chair enflée (canvas source élargi à
64×84 pour la place nécessaire), puis `animate_character` v3 (6 frames
sud, prompt court + exclusion négative dès le premier essai — aucune
hallucination d'arme, accepté sans reroll). Deux bugs de cuisson
trouvés et corrigés par mesure : facteur d'échelle LANCZOS 0,6375 pour
le canvas partagé 64×64 (personnage source haut de 80px) ; ancrage pied
élargi en pleine largeur pour 1 frame sur 6 (pose de fente large où la
bande de recherche centrée du pied était trop étroite pour des jambes
très écartées). Verdict honnête : silhouette nettement large/ronde, à
l'opposé de la silhouette longue/fine de Bras-Faux — comparaison directe
faite dans la capture, aucune confusion possible à l'écran (point de
vérification principal du mandat, satisfait). Écart réel avec la
référence : la planche montre une projection du poing plus loin devant
le corps en diagonale avec une texture de grappes/griffes plus
marquée ; le résultat reste une masse plus compacte, près du corps.
Coût : 22 générations PixelLab (1 `create_character_state` + 1
`animate_character`, aucun reroll nécessaire). Aucun appel Meshy sur
les 4 mandats de cette entrée (pipeline 2D PixelLab suffisant partout).
Capture : `captures/verification/2026-08-22-fidelite-poing_belluaire.
png` (4 panneaux, incluant Bras-Faux pour contraste de silhouette).

**Fusion et vérifications.** Les 4 agents ont opéré sur le même
répertoire de travail partagé (l'isolation git worktree demandée ne
s'est pas appliquée à cet environnement pour 3 des 4 agents — seul
Terre a réellement travaillé dans un clone isolé, poussé séparément
puis mergé) ; chacun n'a commité que ses propres fichiers scopés,
vérifié après coup (aucun chevauchement, aucune collision constatée sur
`parasite.json` ni ailleurs). Fusion dans l'ordre Gueule Vide → Bras-Faux
→ Terre (merge propre, aucun conflit, fichiers disjoints) → Poing
Belluaire (poussé directement en fast-forward par son propre agent).
`scripts/run_gameplay_smoke_test.sh` et `scripts/run_vfx_recipe_smoke_test.sh`
— `all_pass:true` après chaque étape de fusion, re-testé une dernière
fois sur l'état final poussé (`origin/main` à `5f03ff0`). Coût total
mesuré (compte PixelLab réel, `get_balance`) : 449/2000 générations
consommées ce cycle (1551 restantes) — ~83 générations pour cette
entrée complète (Gueule Vide 3 + Terre 0 + Bras-Faux 56 + Poing
Belluaire 22 + quelques appels de vérification), aucun plafond
arbitraire appliqué, conformément à l'instruction de Milan. 0 crédit
Meshy consommé.

---

## 2026-08-22 — MANDAT AUDIT FIDÉLITÉ RÉFÉRENCES : Gueule Vide cassé confirmé et régénéré, converge.gd corrigé, 3 gaps documentés honnêtement

**Contexte** : Milan soupçonnait, sans pouvoir vérifier lui-même (Git LFS
hors de portée réseau de son côté), que le sprite réel de Gueule Vide ne
ressemblait plus à sa planche de référence. Mandat : auditer chaque
compétence vivante (ressemblance ET comportement) contre sa planche,
dans l'ordre Gueule Vide → Bras-Faux/Poing Belluaire → Poing Tellurique/
Marée de Sable → combo de base → 3 monstres, corriger ce qui est cassé
avant de continuer, documenter honnêtement le reste.

**Point 1 — Gueule Vide : CASSÉ, confirmé et corrigé.** Les 6 frames
réelles (`assets/processed/sprites/gueule_vide/cast/*.png`) montraient
une petite créature à jambes/tête ronde façon mannequin générique —
zéro mâchoire, zéro croc, aucune ressemblance avec la planche (une
gueule d'encre béante SANS jambes ni bras, juste une mâchoire sur un
tendon d'encre). Confirmé par comparaison côte à côte agrandie (8x).
Cause racine trouvée en relisant `data/pixellab_usage.jsonl` : la
création d'origine utilisait `body_type` par défaut (humanoïde) ET une
référence downscalée à 24x22px/8 couleurs (pour tenir sous le seuil de
troncature MCP, ~1-2 Ko de base64) — bien trop dégradée pour transmettre
"mâchoire sans corps" au générateur, qui est retombé sur un archétype de
créature générique.

Corrigé par une regénération complète (`data/pixellab_usage.jsonl`,
entrées 2026-08-22T21:0x) : (1) guide de silhouette synthétique dessiné
par script (mouth+crocs+tendon, SANS jambes, 40x40px, largement sous le
seuil de troncature) ; (2) passé dans `create_image_pixflux` (img2img,
1 crédit) pour obtenir un vrai rendu pixel art ombré plutôt que le guide
brut tel quel (une créature en v3+reference se contente de FAIRE
PIVOTER l'image donnée, elle ne la restylise pas — leçon retenue,
importante pour toute régénération future via ce chemin) ; (3) ce
rendu servi comme référence à `create_character` mode v3 (8 directions,
1 crédit) ; (4) `animate_character` v3 (direction sud, 6 frames, 1
crédit) pour le cast. Nouvelle séquence : frames 0-2 mâchoire grande
ouverte/crocs visibles, frame 3 = la morsure (fermeture nette, plus
sombre), frames 4-5 = désintégration en fragments d'encre épars —
sémantique légèrement différente de l'ancienne (frame2 tient
maintenant la grande ouverture au lieu de frame3, frame3 est la morsure
au lieu de frame4) : `src/gameplay/powers/gueule_vide.gd::
FRAME_TICK_BOUNDS` réajusté en conséquence, CONTACT_TICK inchangé.
Anciennes frames/référence archivées dans `assets/source/pixellab/
gueule_vide/_archive_2026-08-18_v1/` (jamais supprimées). Cuisson via
`scripts/cook_character_frames.py` (48x48, foot-margin 4px). Smoke test
complet relancé (`all_pass:true`, tous les checks `gueule_vide_*`
passent). Comparaison finale committée : `captures/verification/
2026-08-22-fidelite-gueule_vide.png`.

**Point 2 — Bras-Faux/Poing Belluaire : trou d'outillage resitué + vrai
bug trouvé et corrigé.** Le "trou d'outillage" de la session précédente
(capture ne rendant aucune couche VFX) s'est avéré être DEUX choses
distinctes, pas un vrai trou :
- Bras-Faux : erreur de ma part — `data/pouvoirs/monstrification.json`
  (verrouillé par Milan) place Bras-Faux en TIER 2 (slot `power2`,
  unlock_level=3), pas tier 3 comme `docs/STATUS.md` le laissait croire
  (désaccord entre les deux fichiers — `data/pouvoirs/*.json` fait
  autorité, STATUS.md sera à corriger). Capturé au bon slot : la couche
  `ribbonTrail` est bien là, visible.
- Poing Belluaire (slot `power1`, correct dès le départ) : VRAI bug
  trouvé dans `src/vfx/primitives/converge.gd` — taille de fragment
  câblée en dur (2.0-4.5px) SANS RAPPORT avec `scale_px` de la recette.
  Dès que `scale_px` dépasse ~20px (Poing Belluaire = 30, Poing
  Tellurique = 26), les fragments deviennent des points de quelques
  pixels, imperceptibles à l'échelle réelle du jeu — confirmé par
  capture zoomée (avant : rien de visible ; après inspection à la loupe :
  de minuscules taches). Corrigé : taille proportionnelle à `scale_px`
  (~22-36% au lieu d'une constante fixe). `shardBurst` a la même
  formule fixe mais reste lisible car ses fragments VOYAGENT sur un
  grand arc (`speed_px_per_tick`) — `converge` les garde près de
  l'origine toute leur vie, rien ne compense une taille trop petite.
  Capture avant/après confirmée. Contenu VISUEL de Bras-Faux/Poing
  Belluaire reste un placeholder documenté (`_sprite.play("coup2"/
  "coup3")`, "art dédié à la transformation hors scope") — comparé à la
  planche (bras qui devient une faux organique articulée), ce n'est PAS
  fidèle, mais c'est un GAP DE PRODUCTION CONNU depuis le départ, pas
  une régression : nécessiterait un vrai sprite de transformation de
  bras, hors scope d'une session de correctifs. Comportement (arc,
  multi-cible, portée) déjà smoke-testé conforme.

**Point 3 — Poing Tellurique/Marée de Sable : même bug, déjà
documenté.** La recette `power.poing_tellurique.cast.json` elle-même
(`expected_layers[1].description`) flaguait DÉJÀ ce problème depuis une
session antérieure (render_detector.py, R4/R2) : "converge... signal à
peine perceptible... À RE-INVESTIGUER... pas encore tranché." Résolu
par le même correctif `converge.gd` — capture avant/après confirmée
(anneau + fragments désormais nettement visibles). Marée de Sable
(`beamSegment`) déjà lisible sur capture antérieure, non retouché.

**Point 4 — Combo de base (3 coups) : pas de planche dédiée, mais
soupçon de Milan confirmé.** Comparaison frame-par-frame de coup1/coup2/
coup3 (`assets/processed/sprites/cendre/coup{1,2,3}/*.png`) : poses
quasi identiques à chaque index de frame correspondant, AUCUNE arme
visible sur aucun des 3 coups (Cendre semble frapper à mains nues sur
tous les frames), seule coup2 a un lean/une posture plus dynamique à
mi-animation. Confirme "interchangeables" — pas un bug de code, un gap
de contenu (les 3 coups n'ont jamais eu de poses ni d'arme dédiées
différenciées). Pas de fix appliqué cette session : ampleur = nouvelle
génération d'assets (poses distinctes + arme visible pour 3 animations
existantes), pas un correctif ponctuel, et aucune planche de référence
n'existe pour guider un remake. Documenté pour une session dédiée
future.

**Point 5 — 3 monstres (Crawler/Brute/Ranged) : mandat basé sur une
prémisse fausse.** Le mandat supposait une planche de concept art dans
`experiments/` pour ces 3 monstres. Vérifié dans `data/meshy_usage.
jsonl` : "texte pas d'image reference disponible pour ces monstres" —
génération 100% texte-vers-3D, AUCUNE image de référence n'a jamais
existé pour Crawler/Brute/Ranged. Impossible d'auditer une "fidélité"
contre une référence qui n'existe pas. Recadré en vérification de
cohérence INTERNE (idle vs marche, même créature, pas de rig cassé) :
les 3 monstres sont visuellement cohérents entre repos et marche
(silhouette/couleur/échelle stables, cycle de membres réel visible) —
aucun défaut trouvé, mais ce n'est pas la même question que celle posée
par le mandat.

**Vérifications finales** : `scripts/run_gameplay_smoke_test.sh` et
`scripts/run_vfx_recipe_smoke_test.sh` — `all_pass:true` après chaque
changement (regénération Gueule Vide, fix converge.gd). Budget PixelLab
de cette entrée : 4 générations (guide→pixflux 1cr, create_character
v2 1cr [rejeté], create_character v3 1cr, animate_character 1cr) — la
tentative v2 est restée un personnage orphelin sur PixelLab, non
utilisée en jeu, non supprimée (coût nul à la laisser).

---

## 2026-08-22 — Retour Milan sur PREMIÈRE VIDÉO réelle : 6 points, dont build web resté périmé

**Contexte critique découvert en premier** : Milan répète quasi mot pour
mot les points 1 et 2 de l'entrée précédente (rectangle blanc, trou de
vérification), déjà corrigés et poussés (commit `318df6b`). Cause
trouvée : `docs/index.pck` (build web joué par Milan) datait de 19h19,
soit UNE HEURE AVANT le fix du shader (20h15) — Milan a regardé une
vidéo du build PÉRIMÉ, pas de l'état réel du dépôt. Pas un nouveau bug,
un rappel que "commité" ≠ "joué" tant que le build web n'est pas
redéployé. Leçon retenue : redéployer `docs/index.html`/`index.pck` en
DERNIÈRE étape de toute session touchant du visuel, jamais oublié entre
un fix et la prochaine vérification de Milan.

**Point 3 — torche/lumière de porte rendue dans la zone des boutons
tactiles (bug réel, nouveau).** Root cause : `scenes/ui/touch_controls.
tscn` place ses boutons dans une bande écran fixe (native 640×360,
y≈205-370) qui, à `BASE_ZOOM=0.8`, correspond à une bande du MONDE assez
basse pour contenir le sol/les props/la lumière des portes (vérifié par
capture `--mode=scene` caméra centrée sur la torche de la porte Elite,
x=1800-2048) — les boutons sont des icônes semi-transparentes SANS fond
opaque, donc tout ce qui passe par cette bande de l'écran (n'importe
quel élément du monde, pas spécifiquement "une torche") reste visible
au travers. Fix : `Background` (ColorRect plein, `Color(0.08,0.06,0.05,
1.0)`, `mouse_filter=IGNORE`) ajouté en premier enfant de
`TouchControls`, couvrant toute la bande boutons — testé d'abord à
alpha 0.82 (insuffisant, un halo de lumière très intense reste
partiellement visible même à travers un fond à 82% d'opacité), corrigé
à 1.0 (masquage total confirmé par capture). `captures/verification/
2026-08-22-touch-ui-bleed-{avant,apres}.png`. Smoke test inchangé
(`all_pass:true`) — pur ajout visuel, aucune logique touchée.

**Point 4 — principe d'écart de lisibilité VFX (nouvelle règle
générale, pas un cas isolé).** Diagnostic de Milan confirmé par mesure :
`data/palettes/value_bands.json` documente déjà le sol ambiant réel
(~24-37% V, jusqu'à ~78% en bord de halo de torche) — les 2 rôles les
plus visibles de `invocateur_vide` (bleu pâle 72%V, gris-lilas 55%V)
recouvraient très exactement cette bande : même écart de teinte, aucun
écart de LUMINANCE avec le sol le plus lumineux, d'où l'effet "qui ne
perce pas" que Milan décrit sur Gueule Vide. Relevés à 90/85% V et 55/
50% saturation (toujours sous le plafond VFX 92%, teinte inchangée,
identité de Classe intacte) — capture avant/après confirmée (`captures/
verification/2026-08-22-vfx-contraste-gueule-vide-{avant,apres}.png`).
Audit des 4 autres compétences implémentées avant généralisation,
comme demandé par Milan :
- **Poing Tellurique/Marée de Sable (`terre`, VERROUILLÉE)** : capture
  réelle confirme que `groundRing` restait à peine visible MÊME après
  le premier correctif R4 documenté dans ce fichier de palette — hue
  quasi identique au sol (32° vs ~35-38° mesuré) ne laisse QUE value/
  saturation comme levier pour une matière qui doit rester "terre" par
  nature (contrairement à Invocateur, la teinte ne peut pas s'éloigner
  sans casser l'identité). 2e correctif : 52→80% V, 46→65% saturation
  sur le rôle "signature 1" uniquement (le seul confirmé faible par
  capture) — `captures/verification/2026-08-22-vfx-contraste-
  tellurique-{avant,apres}.png`, nette amélioration visible. Rôles
  contact/poussière non touchés (déjà lisibles sur la capture Marée de
  Sable).
- **Bras-Faux/Poing Belluaire (`parasite`, réécrite from reference
  2026-08-22 même journée)** : PAS auditables cette passe — l'outil de
  capture (`--mode=player_action --action=power1/power3`) n'a rendu
  AUCUNE couche VFX aux ticks testés (6/10/18), alors que `Poing
  Belluaire`/tier1 est censé être débloqué dès le niveau 1. Cause non
  encore identifiée (décalage tick recette vs tick capture différent de
  celui qui marche pour `terre`/`invocateur_vide` ? condition de portée
  non remplie par le rig de capture ?) — flag explicite : ceci est un
  TROU D'OUTILLAGE, pas une conclusion sur la lisibilité réelle de ces
  2 compétences. Palette `parasite` volontairement non retouchée sans
  preuve visuelle (elle vient d'un échantillonnage direct des 5 planches
  de référence officielles le jour même — la retoucher à l'aveugle
  romprait la fidélité à la référence que Milan a validée). À reprendre
  en priorité la prochaine session avant tout nouveau travail sur ces
  2 compétences.

**Point 5 — monde encore plat malgré la Phase 1 (Addendum C).** Cause :
un seul `CanvasModulate` global (teinte uniforme sur TOUT le niveau) +
seulement 3 `PointLight2D` (les torches de porte Combat/Elite/Boss,
espacées de 650 à 1050px) sur un niveau large de ~3550px — les 2
braziers et le porte-torche déjà présents dans le décor (Phase 1,
MANDAT AUTONOME v3) étaient de PURS sprites décoratifs, aucune lumière
réelle. Exactement le symptôme que Milan décrit : des props ajoutés
mais aucune variation lumineuse. Fix : `PointLight2D` (texture radiale
déjà utilisée par les torches de porte) ajouté en enfant de
`PropBrazier1`, `PropBrazier2` (orange-feu, energy 1.5, rayon 2.4×) et
`PropTorchStand1` (or pâle, energy 0.85, rayon 1.3×) — comble
spécifiquement le grand vide entre la porte Combat (x=768) et la porte
Elite (x=2048) où rien n'éclairait avant. Capture large (caméra
x=1500) avant/après : dôme de lumière chaude visible sur le sol là où
il n'y avait qu'un ton plat avant — `captures/verification/
2026-08-22-monde-lumiere-{avant,apres}.png`. `AmbientWarmth`
(CanvasModulate) et Addendum C non touchés, comme demandé (ne pas
assombrir le monde, ajouter de la variation LOCALE en plus). `outpost.
tscn`/`test_arena.tscn` non repris cette passe (hors scope, la vidéo de
Milan montre `gate_premiere`) — à faire si Milan le demande.

**Point 6 — première capture d'un impact réel commitée.** Aucune
capture existante (avant cette session) ne montrait un coup qui touche
réellement un ennemi. `--mode=player_action --action=attack --tick=12`
(2 ennemis positionnés devant/à 30° comme le smoke test) : capture
montre les 2 ennemis en plein flash de hit (teinte réelle qui
transparaît sous le blanc, pas un bloc opaque — le fix du point 1 tient
aussi en combo réel, pas seulement en isolation) + une étincelle
d'impact. `captures/verification/2026-08-22-combo-impact-reel.png`.

**Vérifications finales** : `scripts/run_gameplay_smoke_test.sh` et
`scripts/run_vfx_recipe_smoke_test.sh` — `all_pass:true` après CHAQUE
changement de cette entrée (shader/UI/palettes/scène), pas seulement à
la fin. Build web (`docs/index.html`/`index.pck`) redéployé en tout
dernier, après tous les fixes ci-dessus — pour que la PROCHAINE vidéo
de Milan reflète enfin l'état réel du dépôt, pas un état d'il y a
plusieurs commits.

---

## 2026-08-22 — Retour Milan sur captures réelles : bug flash blanc + trou de vérification

**Contexte** : 1er retour de Milan sur de vraies captures du jeu en
exécution (jamais reçu avant sur ce projet). Trois points, priorité
explicite de Milan : "le rectangle blanc cassé" d'abord, puis le trou
de vérification, puis (hors scope de cette entrée, pas commencé) un
passage lumière/chaleur sur le monde.

**Point 1 — bug résolu.** Deux rectangles blancs pleins flottant à côté
du joueur sur les captures de Milan. Hypothèse de Milan (traînée/
afterimage, Addendum B) vérifiée et écartée : `_spawn_afterimage()`
dans `player.gd` garde déjà `if texture == null: return` et copie la
vraie frame du joueur. Vraie cause trouvée en réexaminant mes propres
captures de vérification de cette session (Phase 3, Poing Belluaire et
Marée de Sable) : le MÊME bug y était déjà visible, mais mal
diagnostiqué comme "juste les mannequins placeholder génériques" sans
creuser pourquoi ils étaient blancs alors que leur couleur définie est
rouge sombre. Cause réelle : `src/vfx/shaders/hit_flash.gdshader`
ré-échantillonnait `texture(TEXTURE, UV)` directement au lieu de lire
l'entrée `COLOR` déjà pré-calculée par Godot. Pour un `AnimatedSprite2D`
texturé ça fonctionne (TEXTURE = la vraie texture). Pour un `Polygon2D`
sans texture assignée — le mannequin générique d'`Enemy`
(`scenes/gameplay/enemy.tscn`) ET `boss_gate_maw.tscn`, tous deux
présents dans des scènes de jeu réelles (`gate_premiere`, `test_arena`),
pas seulement des mannequins de test — Godot lie `TEXTURE` à sa texture
blanche 1×1 par défaut : `tex.rgb`/`tex.a` valaient TOUJOURS `(1,1,1,1)`
quel que soit `flash_amount`, d'où un rectangle blanc opaque plein, sans
fondu, ignorant la couleur réelle du polygone. Fix d'une ligne : lire
`COLOR` (déjà texture×modulate pour un sprite, couleur de vertex×
modulate pour un `Polygon2D` sans texture) au lieu de re-sampler
`TEXTURE` — corrige les deux cas sans branche `if` ni régression pour
les sprites déjà corrects. Vérifié : `godot4 --headless --rendering-
driver vulkan --import` propre, `scripts/run_gameplay_smoke_test.sh`
toujours `"all_pass":true` (les 3 checks `hit_response_*` passent).
Capture avant/après, même scène (`--mode=player_action --action=power1
--active_power=monstrification --level=1 --tick=30`) :
`captures/verification/2026-08-22-hit-flash-fix-avant.png` (rectangles
blancs pleins) vs `2026-08-22-hit-flash-fix-apres.png` (teinte rose/
rouge du polygone qui transparaît sous le flash, comme attendu).

**Point 2 — trou de vérification corrigé.** Milan : "aucune capture de
vérification n'a jamais été committée", malgré des dizaines de mentions
"vérifié par capture" dans ce worklog. Vérifié : exact. La règle "seules
les captures approuvées sont commitées" existait dans `.gitignore`
depuis le début mais n'avait jamais été suivie en pratique — tout
partait dans `/captures_local/` (gitignoré). `data/labels/
quality_labels.jsonl` (verdicts `accept`/`reject` de Milan sur une
référence d'asset, §13.2 `ARCHITECTURE_VFX_v3.md`) est structurellement
le mauvais mécanisme pour une preuve ponctuelle de correction de bug —
il attend un verdict humain formel, pas une preuve immédiate. Nouvelle
convention, documentée dans `CLAUDE.md` et `.gitignore` : toute capture
citée comme preuve va dans `captures/verification/` (réellement
committé), nommée `<date>-<sujet>.png`, dans le MÊME commit que le
changement qu'elle prouve. `data/labels/quality_labels.jsonl` garde son
rôle initial inchangé (verdict Milan uniquement, jamais écrit par
Claude Code).

**Point 3 — non commencé, volontairement.** Milan a explicitement
ordonné de traiter 1 et 2 avant toute nouvelle feature. Passage lumière/
chaleur du monde (Addendum C) à faire dans une session/entrée
séparée, avec sa propre capture avant/après committée.

**Fichiers touchés** : `src/vfx/shaders/hit_flash.gdshader` (fix),
`.gitignore` + `CLAUDE.md` (convention de capture), `captures/
verification/2026-08-22-hit-flash-fix-{avant,apres}.png` (nouveau
dossier, 1res captures réellement committées du projet).

---

## 2026-08-22 — MANDAT SUITE v2 : Phase 3 (Poing Belluaire + Poing Tellurique)

**Blocage rencontré puis levé.** Avant d'écrire du code, recherche
systématique (agent lecture seule) du contenu GDD/Bible pour "Poing
Belluaire"/"Monstrification" et "Poing Tellurique"/"Terre" : ZÉRO fiche
existante dans `docs/RANK_ZERO_MASTER_GDD.md` ni `docs/
PRODUCTION_MANDATE_v1.md` — seule une mention de titre de phase dans ce
worklog. Or le mandat lui-même (§3, matrice de décision) flague
explicitement "nouvelle matière/palette signature pour un Pouvoir/
Classe sans signature définie" et "tout contenu narratif/monde non
explicitement fourni" comme "à valider — s'arrêter, flaguer" — deux
pouvoirs sans AUCUNE fiche qualifient clairement pour cet arrêt.
Documenté comme tel, en attente. Milan a alors transmis
`RANK_ZERO_POWER_SKILL_BIBLE_v0.4.docx` ("Fiches de production
gameplay" des 15 compétences, principe/enchaînement/interactions par
compétence, "valeurs exactes à équilibrer avant verrouillage") — lu via
python-docx (pandoc absent de l'environnement), débloquant la brique.
Le blocage a duré le temps de la recherche, pas une session complète :
dès la Bible reçue, le contenu manquant (mécanique/visuel qualitatif)
était disponible, seules les valeurs numériques exactes restaient
ouvertes — exactement le statut "TUNABLE" déjà appliqué à Bras-Faux.

**Découverte de continuité importante** : la Bible v0.4 classe
Bras-Faux SOUS la Classe "Monstrification" (pas "Parasite" isolément
comme l'appelait le mandat v1) — Poing Belluaire, deuxième compétence
de cette même famille, n'est donc PAS un "pouvoir sans signature" :
`data/palettes/parasite.json` est réutilisée telle quelle (roles 1 et 3
étendus dans leur champ `usage` pour couvrir `converge`/`impactStar` en
plus de `ribbonTrail`/`arcSlash`/`impactFlashFrame` — jamais un nouveau
`palette_id`). "Terre" en revanche est une Classe réellement nouvelle
(zéro fiche antérieure) : `data/palettes/terre.json` est une PROPOSITION
de première passe, dérivée directement du principe donné ("sable,
terre, roche, poussière et gravats" — rien au-delà), documentée comme
non verrouillée dans son propre champ `notes`, à valider par Milan comme
signature de Classe avant que les 4 autres compétences Terre à venir
(Marée de Sable, Éperon, Carapace, Effondrement) ne s'appuient dessus.

**Poing Belluaire** (`FOR | Tier 2 | Impact lourd`) : même archétype de
cast que Bras-Faux — exécuté PAR le joueur, pas une entité invoquée —
mais recodé comme un NOUVEL archétype `melee_impact` (distinct de
`melee_sweep`) puisqu'un "seul coup frontal très lourd" n'est pas un
balayage. Implémenté dans `player.gd` en miroir exact de la timeline
`_start_bras_faux()/_advance_bras_faux()/_end_bras_faux()/
_try_hit_bras_faux()` (même discipline ANTICIPATION/RELEASE/RECOVERY,
`_action_lock` pendant toute l'action, cooldown après RECOVERY) :
50 ticks (20/4/26, plus lent que Bras-Faux 40 ticks pour vendre le
poids), portée 40px/demi-angle 30° (plus courte et plus étroite qu'un
balayage), dégâts 16 (> combo/Bras-Faux, "peut interrompre les attaques
faibles"), recoil_strength_px 40 (> défaut 24, "forte valeur de
recul"), hitstop "heavy" (vs "medium" pour Bras-Faux). Toutes ces
valeurs sont TUNABLE (non chiffrées par la fiche v0.4, même statut que
Bras-Faux) — choisies dans les bandes de tuning déjà posées (autonome,
§3 de la matrice). Recette `data/recipes/power.poing_belluaire.cast.json` :
`converge` (anticipation, la masse qui grossit dans le poing) +
`impactStar`+`impactFlashFrame` (contact) — pas de couche "core" de
traînée, un coup frontal n'a pas de mouvement à tracer contrairement au
balayage de Bras-Faux (différence honnête entre archétypes plutôt
qu'une couche copiée sans raison). Placeholder visuel : anim "coup3"
(le plus lourd des 3 coups du combo, art dédié à la transformation du
poing hors scope recette+logique, même discipline que "coup2"/Bras-Faux).

**Poing Tellurique** (`FOR | Tier 2 | Corps-à-corps/impact`) : même
archétype `melee_impact`. Timeline 42 ticks (18/4/20). Portée 44px/
demi-angle 40°, dégâts 14 (entre Bras-Faux et Poing Belluaire — la fiche
ne porte aucun qualificatif "forte"/"très lourd" pour celui-ci),
hitstop "medium". Recette `data/recipes/power.poing_tellurique.cast.json` :
`groundRing` (anticipation, la terre qui se fissure/remonte au sol) +
`converge` (core, la matière qui converge dans le poing, chevauche la
fin de l'anticipation) + `impactFlashFrame` (contact) + `dustKick`
(contact/conséquence, "éclats/poussière", seule couche `degradable`).
Bug de sens trouvé et corrigé AVANT le smoke test (relecture du code de
`dust_kick.gd`, pas après coup) : `direction` y est interprété comme "le
sens du DÉPLACEMENT qui cause le contact" et projette les éclats à
l'opposé — correct pour un pas/dash qui laisse de la poussière derrière
lui, FAUX pour un impact de poing qui doit projeter ses éclats DEVANT.
Seule cette couche lit `direction` dans la recette (vérifié dans
`ground_ring.gd`/`converge.gd`/`impact_flash_frame.gd` : aucun des trois
ne le fait) — `_start_poing_tellurique()` passe donc `-facing` au lieu
de `facing` au niveau de l'appel `VfxRecipeRegistry.play()`, sans
risque pour les 3 autres couches. Placeholder visuel : anim "coup1"
(distinct de "coup2"/Bras-Faux et "coup3"/Poing Belluaire).

**Intégration** : nouvelles actions d'input `power3` (touche T) et
`power4` (touche G) dans `project.godot` ; boutons tactiles
`ButtonPower3`/`ButtonPower4` ("PW3"/"PW4") dans `touch_controls.tscn`,
positionnés à gauche du joystick (aucune zone tactile existante
chevauchée) ; icônes de cooldown `Power3`/`Power4` dans `hud.tscn` (la
zone `Cooldowns` élargie de 160 à 186px de large pour accueillir 6
icônes au lieu de 4, toujours dans les 640px du viewport) + getters
`get_poing_belluaire_cooldown_ratio()`/`get_poing_tellurique_cooldown_ratio()`
lus par `hud.gd`. Capture en jeu réel (`test_arena.tscn`) confirmée :
6 icônes de cooldown visibles sans chevauchement, boutons tactiles PW3/
PW4 distincts.

**Bug de smoke test trouvé et corrigé** (pas un bug de gameplay réel,
mais une leçon de méthode) : les 2 premiers essais de tests
`_check_poing_belluaire()`/`_check_poing_tellurique()` échouaient sur
la cible latérale (et pour Belluaire, même la cible frontale) — debug
print a montré que la position du joueur dérivait d'environ 15px dès le
1er tick de l'anticipation, alors que `velocity = Vector2.ZERO` est
posé explicitement chaque tick. Cause : les ennemis de test étaient
placés à seulement 25-28px du joueur (plus près que les 30px utilisés
par le test Bras-Faux), chevauchant probablement leur collider au
spawn — `move_and_slide()` résorbe cette interpénétration dès le
premier appel, indépendamment de la vélocité demandée, ce qui suffisait
à faire sortir une cible tout juste à la limite du cône (30-31°). Fixé
en alignant la distance de spawn sur les 30px connus sans problème de
Bras-Faux et en resserrant les angles latéraux de test (12°/18° au lieu
de 15°/25°) pour garder de la marge des deux côtés plutôt que de couper
au plus juste. `scripts/run_gameplay_smoke_test.sh` : 100% vert (2
nouveaux triplets de checks : démarrage+anim, multi-cible dans l'arc
sans toucher hors-arc, fin+déverrouillage+cooldown bloque un second
cast — même couverture que Bras-Faux).

**Archétypes de cast (mandat production v1 §5)** : `melee_impact` est
un NOUVEL archétype introduit par cette brique (distinct de
`melee_sweep`/Bras-Faux et `invocation`/Gueule Vide) — 3 archétypes
concrets existent maintenant sur 4 nommés par le mandat ("projection
avant" et "canalisation" restent à 0 exemple, primitives disponibles
`beamSegment`/`spiral` mais aucune compétence documentée ne les
réclame ; pas d'invention pour combler ce vide).

**Preuve d'invocation mobile : reportée, non bloquante.** Le mandat la
conditionne à "quand une compétence Invocateur retourne" — aucune des
5 fiches Invocateur de la Bible v0.4 (Gueule Vide, Serpent Creux,
Corbeau Pâle, Poing du Colosse, Œil Sans Regard) ne décrit de
déplacement libre/suivi ("Aucune IA de suivi... aucun déplacement
libre" reste la règle §0 du principe Invocateur) : rien à prouver
avec le contenu actuellement fourni. Flag documenté, pas une invention
pour occuper le créneau.

**Statut Phase 3 : Poing Belluaire et Poing Tellurique terminés
(logique + recette + palette + intégration + tests). Archétypes de
cast : 3/4 couverts par du contenu réel. Invocation mobile : reportée,
en attente de contenu Invocateur pertinent.** Prochaine étape : Phase 4
(le monde — parallaxe, props, densification, Cendre 8-directions).

## 2026-08-22 — MANDAT SUITE v2 : Phase 4 (le monde — partie gratuite)

**Reconnaissance avant écriture** (agent lecture seule) : `outpost.tscn`
a déjà un vrai `Parallax2D` "FarBackground" ; `test_arena.tscn` n'en
avait AUCUN ; `gate_premiere.tscn` avait un "FarBackground" qui
RESSEMBLAIT au bon pattern mais était un simple `Node2D` statique (pas
de défilement parallax réel). Seulement 5 textures de props existent
(`prop_rubble`, `prop_debris`, `prop_brazier`, `prop_pillar`,
`prop_rubble_warm`), aucune variante peinte — la variété vient déjà de
transforms moteur (`PropRubble2` = `PropRubble1` mirroré, convention
documentée worklog.md:2780). Aucun script de "densification" procédurale
n'existe : les props sont posés à la main dans chaque `.tscn`. Cendre
n'a de couverture 8-directions que pour idle/déplacement (`coup1/2/3`,
`dash`, `hurt`, `mort` restent mono-direction) — et n'a JAMAIS eu de
pipeline Blender (contrairement aux 3 monstres Meshy) : c'est un
turnaround PixelLab pur, donc "rotation caméra sur le modèle déjà
riggé" ne s'applique pas à Cendre tel quel. Le mandat production v1 §6
(item E) traite déjà explicitement le mono-direction des animations de
combat comme une issue acceptable ("dash/combo/esquive si budget
PixelLab, sinon flag"), pas un défaut à corriger à tout prix.

**Décision de scope** : cette session traite la partie GRATUITE de
Phase 4 (aucune génération PixelLab/SpriteCook, uniquement réemploi
moteur de l'art existant) — parallaxe + densification. Compléter Cendre
en 8 directions de combat (dash/coup1-3/hurt/mort, soit ~7 directions
supplémentaires × 6 animations) et ajouter de nouvelles variantes de
props/texture de mur relèvent d'une génération PixelLab qui n'est PLUS
un "lot ponctuel habituel" (mandat production v1 §3, matrice de
décision — item explicitement "à valider"). Solde vérifié avant de
décider : PixelLab 1644 générations restantes sur 2000 (abonnement actif,
reset 2026-09-14), SpriteCook 27 crédits seulement. Le solde PixelLab
est confortable, mais engager plusieurs centaines de générations pour
compléter Cendre est une dépense de production réelle sur l'abonnement
de Milan, pas une décision purement technique — flaguée ci-dessous
plutôt qu'engagée en autonomie.

**Parallaxe** : `gate_premiere.tscn` — converti le `Node2D`
"FarBackground" existant en vrai `Parallax2D` (`scroll_scale =
Vector2(0.55, 1)`, même valeur qu'`outpost.tscn`) : les 6 sprites
`BgArch1-3`/`BgPillar1-3` déjà en place défilent maintenant plus
lentement que le premier plan sur ce long corridor, au lieu de rester
statiques — correction de cohérence avec le pattern déjà établi, pas un
nouveau système. `test_arena.tscn` — n'avait aucun décor lointain :
ajouté un `Parallax2D` "FarBackground" (même `scroll_scale`) avec 3
sprites réemployant `bg_ruin_arch.png`/`bg_pillar_silhouette.png` (zéro
nouvel asset), un de chaque de part et d'autre de l'arène plus une arche
centrale, à l'échelle 0.34 (cohérent avec 0.38 dans les 2 autres scènes,
légèrement réduit car cette arène est plus resserrée).

**Densification (test_arena uniquement)** : c'était la scène la plus
pauvre en props (3 seulement, contre 13 dans `gate_premiere.tscn` et 4
dans `outpost.tscn`) — portée à 6 en réemployant les textures déjà
importées : `PropDebris2` (mirror de `PropDebris1`, même convention que
`PropRubble2`), `PropRubble3` (échelle 0.85 pour varier la silhouette
sans nouvel art), et `PropPillar1` — première utilisation de
`prop_pillar.png` dans cette scène (déjà chargé par le projet via
`outpost.tscn`/`gate_premiere.tscn`, aucun coût). `gate_premiere.tscn`
et `outpost.tscn` non touchés : déjà densément peuplés (13 et 4 props
sur des surfaces bien plus petites que `test_arena`), ajouter encore
aurait surchargé sans bénéfice de lisibilité.

**Vérification** : `--import` headless propre, `scripts/
run_gameplay_smoke_test.sh` 100% vert (aucun des changements ne touche
au gameplay). Capture des 2 scènes modifiées : `test_arena.tscn` montre
l'arche en arrière-plan et les nouveaux props visibles sans
chevauchement du HUD/des boutons tactiles ; `gate_premiere.tscn` inchangé
visuellement à l'écran (le `Parallax2D` ne change le rendu qu'en
mouvement de caméra, pas sur une capture statique) mais sans erreur de
scène après la conversion de type de nœud.

**Statut Phase 4 (partie gratuite) : terminé.** Reste EN ATTENTE
(dépense PixelLab significative, montant à convenir avec Milan avant
d'engager) :
- Cendre 8-directions complètes pour dash/coup1/coup2/coup3/hurt/mort
  (actuellement mono-direction, GDD amendement §1 section E l'autorise
  explicitement comme fallback).
- Nouvelles variantes de props / texture de mur (aucune texture de mur
  n'existe actuellement, seulement des textures de sol).
Ces deux points ne sont pas oubliés — ils sont documentés ici comme
prochaine décision de production, pas silencieusement ignorés.

## 2026-08-22 — Retour croisé Gemini/ChatGPT sur clip réel : Phase R1 (bug bloquant)

**Contexte** : Milan a fait analyser un clip de gameplay réel par deux
IA indépendantes (Gemini, ChatGPT), plus un bug trouvé par Claude en
lisant le code. Traitement en ordre STRICT imposé par Milan : R1 d'abord
(bloquant), redeploy, puis R2 (vérifier avant corriger), R3/R3bis
attendent la validation de Milan sur un nouveau clip.

**Bug** : `project.godot`, action `"attack"` — héritée de la Phase 1.4
("une seule touche + clic gauche suffisent pour une tranche verticale
testée en headless"), elle portait un `InputEventMouseButton` sans zone
restreinte (`button_mask=1`, aucune position). Contrairement à un
`TouchScreenButton` (qui a sa propre `CollisionShape2D` et ne réagit
que dans sa zone), ce binding déclenchait l'action sur N'IMPORTE QUEL
clic/toucher de l'écran — sur le build web tactile, ça veut dire
qu'un touché n'importe où (déplacement au joystick compris, si le doigt
glisse) pouvait déclencher une attaque. Root cause confirmée par simple
lecture du binding, pas par reproduction manuelle.

**Fix** : retiré l'event `InputEventMouseButton` de `attack`, gardé
uniquement `InputEventKey` (espace) + le `TouchScreenButton` dédié
(`ButtonAttack`, câblé via son propre `action = "attack"`, jamais
affecté par ce retrait). Vérifié explicitement (lecture directe de
`[input]`) qu'aucune autre action (`power1-4`, `dash`, `dodge`,
`character_screen`) ne porte de binding souris généraliste — "attack"
était un cas isolé, pas un pattern répété.

**Test de régression permanent** : `scripts/run_gameplay_smoke_test.sh`
utilise `Input.action_press()` partout, qui CONTOURNE l'InputMap — un
test headless classique n'aurait donc jamais détecté ce bug ni sa
régression. Ajouté `_check_input_map_has_no_stray_mouse_bindings()`
(`tools/smoke_test_gameplay.gd`) : inspecte directement
`InputMap.action_get_events()` pour les 8 actions gameplay et échoue si
l'une d'elles porte un `InputEventMouseButton` — verrouille ce bug
précis contre un retour silencieux (ex. un futur remap qui
réintroduirait un binding généraliste).

**Labels power1-4 illisibles** (Gemini + Milan) : "PWR"/"PW2"/"PW3"/"PW4"
ne distinguent rien du tout entre eux au premier coup d'œil et ne disent
rien sur la compétence réelle. Renommés selon l'identité de chaque
pouvoir (GV = Gueule Vide, BF = Bras-Faux, PB = Poing Belluaire, PT =
Poing Tellurique) sur les 2 endroits qui les affichent
(`touch_controls.tscn` boutons tactiles, `hud.tscn` icônes de cooldown)
— même préfixe que le joueur retrouvera plus tard dans un éventuel menu
de compétences. Contraste ajouté (`font_outline_color` noir,
`outline_size` 2-3) + taille légèrement augmentée (boutons tactiles
12->14px, HUD 9->10px) pour rester lisible sur des fonds très variés
(sol, ennemis, VFX derrière) — vérifié par capture, nettement plus
lisible qu'avant.

**Vérification** : `--import` headless propre, `scripts/
run_gameplay_smoke_test.sh` 100% vert (nouveau check inclus). Capture
en jeu réel confirmant les nouveaux labels lisibles avec contour.

**Statut Phase R1 : terminé.** Redeploy web à suivre. Phase R2 (déjà
fournie par Milan, méthodologie "vérifier avant de corriger") démarre
dans la foulée — voir entrée suivante. Phase R3/R3bis restent en
attente du nouveau clip de Milan après ce redeploy, comme demandé.

## 2026-08-22 — Retour croisé Gemini/ChatGPT sur clip post-R1 : Phase R4 (feedback d'impact, priorité unique)

Les deux analyses convergent après R1 : le bug d'input est bien corrigé,
mais "aucun contenu supplémentaire tant que le combat ne frappe pas" —
un seul chantier cette passe, carte/monstres/HUD/migration Cendre non
touchés (consigne explicite de Milan).

**1. Système de hit commun (le plus important).** `CombatFeedback`
faisait déjà le hit-stop de façon centralisée mais SYMÉTRIQUE (même
durée des deux côtés du conflit) et 4-5 appels séparés par site
(`trigger_hitstop`/`trigger_shake`/`Sfx.play`/`CameraDirector.
trigger_punch()` à la main, avec des trous confirmés par audit :
Gueule Vide sans shake ni camera-punch, les 4 attaques de boss sans SFX
ni camera-punch, le projectile de Ranged avec un hitstop/shake codés en
dur et jamais branchés sur son propre `configure()`). Refonte :
- `TARGET_HITSTOP_MS`/`ATTACKER_HITSTOP_MS` (deux tables, cible
  toujours plus longue que l'attaquant — asymétrie demandée par les deux
  analyses) remplacent l'ancienne table symétrique unique.
- Deux compteurs de gel séparés (`_player_freeze_ticks_remaining` /
  `_enemy_freeze_ticks_remaining`, routés par `attacker_is_player`) au
  lieu d'un seul — chaque camp consulte SON compteur
  (`is_player_frozen()`/`is_enemy_frozen()`), `is_frozen()` (OR des deux)
  reste dispo pour les usages génériques (décroissance cosmétique du
  shake/punch-zoom).
- `register_hit(hitstop_weight, attacker_is_player, sfx_event, shake_weight,
  shake_direction, camera_punch)` : point d'entrée UNIQUE, un appel par
  site de contact (combo 3 coups, Bras-Faux, Poing Belluaire, Poing
  Tellurique, Gueule Vide, les 4 attaques d'Enemy, les 4 attaques du
  boss, le projectile de Ranged) — comble tous les trous de l'audit sans
  rien retirer aux nuances déjà testées (coup léger sans camera-punch,
  etc, via les paramètres optionnels).

**2. Recul par poids d'ennemi.** Mécanique neuve : `recoil_multiplier`
(export par entité, jamais 0.0) multiplie le `recoil_strength_px` que
l'attaquant transmet à `take_damage()` — avant cette brique, le recul
subi ne dépendait QUE de l'attaquant, jamais de qui étai touché. Réglé
sur les 3 tiers demandés : Crawler (léger) 1.6, Ranged (léger-moyen)
1.4, Brute (lourd) 0.35, boss (lourd) 0.3 — jamais statique, toujours un
minimum de recul visible même sur les poids lourds.

**3. Télégraphe visuel ennemi.** Le mécanisme de pulse existait déjà
(`_pulse_telegraph_color()`, lerp progressif vers blanc, tick-driven)
mais ne s'appliquait qu'aux `Polygon2D` (mannequin générique + boss) —
les 3 archétypes jouables (Crawler/Brute/Ranged), en `AnimatedSprite2D`,
n'avaient RIEN, confirmant le trou signalé ("logique présente, rien à
l'écran"). Étendu via `self_modulate` sur la branche `AnimatedSprite2D`
— même mécanisme, pas un second langage visuel, cohabite sans conflit
avec le shader d'contour existant (modulate multiplie par-dessus la
sortie COLOR d'un shader canvas_item).

**4. Poids du combo.** Root motion sur les 3 coups : déjà spécifié et
câblé depuis J1 (`_apply_combo_root_motion()`, lecture data-driven de
`cendre.json`) — vérifié, PAS un trou, juste une couverture de test plus
étroite que le câblage réel. Coup3 (finisher) : anticipation+récupération
allongées via `COMBO_TIER_ANTICIPATION_TICKS`/`COMBO_TIER_RECOVERY_TICKS`
(nouveaux tableaux par tier, tier1/2 inchangés) + un keyframe squash
"étirement" pendant l'anticipation (silhouette qui se charge avant le
coup, jamais vu sur coup1/2) dans `cendre.json`.

**5. Terre (Poing Tellurique) — vérifié par capture avant de toucher au
code**, même méthodologie que Gueule Vide/C1 : `tools/capture_scene.tscn
--mode=player_action --action=power4` à plusieurs ticks. Verdict :
`groundRing` et `dustKick` sont bien rendus (pas un bug de rendu) mais
`groundRing` était quasiment invisible contre le sol neutre (value 38%/
saturation 28%, palette `terre.json` "signature 1") — contraste remonté
(52%/46%), scale_px/durée déjà corrects dans la recette, rien d'autre
retouché.

**6. Contour bleu + sol — vérifié par capture zoomée réelle avant de
retoucher.** La capture confirme le diagnostic de Gemini : à alpha=1.0/
largeur=1.0 (`player_fx.gdshader`), le contour peint en plein n'importe
quel texel voisin d'un pixel semi-transparent — sur un sprite aussi
petit remonté à l'échelle du jeu, ça sature toute la silhouette en bloc
bleu au lieu d'un trait fin (§10.1 : allié = bleu, jamais une
recoloration). Alpha réduit à 0.6, largeur à 0.6 — reste un contour
visible (capture après/avant comparée), plus une recoloration complète.
Sol de `gate_premiere`/`test_arena` : NON touché cette passe — R4 a
prioritisé le système de hit commun et les 2 vérifications par capture
demandées explicitement (Terre, contour), pas eu le temps de reprendre
le tileset avant la fin de cette passe ; reste ouvert pour la
prochaine, la teinte/saturation exacte étant une décision esthétique
(Addendum C) à trancher avec une capture dédiée plutôt qu'en aparté ici.

**7. Secondaire (chiffres de dégâts en arc, zoom caméra A/B) : NON
traité cette passe**, comme prévu par Milan ("si le temps le permet
après 1-6") — priorité donnée au système de hit commun et aux 2
vérifications par capture explicitement demandées.

**Bug trouvé en cours de route (pas dans le mandat, découvert en
testant le système de hit commun) :** `VfxRecipeRegistry._physics_process()`
gelait encore sur le générique `is_frozen()` (OR des deux compteurs)
alors que `gueule_vide.gd` (et tous les autres appelants de `play()`,
tous des pouvoirs du joueur) gèlent désormais sur `is_player_frozen()`
— deux horloges d'un même run pouvaient dériver de quelques ticks selon
qui était touché. Une run "en retard" laissait sa couche dégradable
(ex. `shardBurst`) se déclencher plus tard que prévu, polluant le
spawn_log partagé pendant la fenêtre d'un test suivant
(`gueule_vide_owner_death_cancels_degradable_layer`, faux négatif).
Corrigé en alignant la registry sur `is_player_frozen()` (seul rôle
utilisé par tous ses appelants actuels à ce jour).

**Vérification** : `--import` headless propre, `scripts/
run_gameplay_smoke_test.sh` 100% vert (deux runs indépendants,
déterminisme confirmé) — 8 régressions de méthodologie de test exposées
par l'asymétrie du hit-stop (ordre de sonde shake/gel, marges d'attente
calées sur l'ancienne durée symétrique) diagnostiquées et corrigées une
par une, aucune n'était un vrai bug de gameplay. Captures zoomées
réelles pour Terre (avant/après) et contour (avant/après) — voir
`/tmp/r4_captures/` (non versionné, artefacts de vérification).

**Statut Phase R4 : items 1-6 terminés et vérifiés (tests + captures),
item 7 différé.** Redeploy web à suivre. R2 (items encore ouverts :
recoupe désormais très largement R4.5/R4.6, à réconcilier plutôt qu'à
refaire) et R3/R3bis (Monstrification/Invocation placeholders, chiffrage
migration Cendre) restent en attente de la validation de Milan sur le
prochain clip, comme demandé.

## 2026-08-22 — Suite R4 : valeurs de game feel de Milan + items secondaires restants

Milan a réglé au ressenti, dans un bac à sable dédié à UN impact isolé :
hitstop_freeze_ms=210, knockback_distance_px=27, camera_shake_amplitude_px=6,
impact_flash_duration_ms=65, knockback_return_curve=easeOut. Un verdict humain
qui prime sur la table théorique du doc (plafonnée à 95ms), mais 210ms
partout romprait le rythme d'un combo de 3 coups (3×210ms de gel cumulé
côté cible) — les 5 valeurs ont donc été interprétées et recalées plutôt
qu'appliquées telles quelles :

- **Hitstop** : 210ms traité comme la valeur CIBLE du coup le plus lourd
  (catastrophic), le reste de l'échelle recalé en conservant EXACTEMENT
  les ratios de la 1re passe R4 (light≈0,48×medium, heavy≈2,2×medium,
  catastrophic≈3,4×medium ; attaquant ≈0,54×cible) — `TARGET_HITSTOP_MS`/
  `ATTACKER_HITSTOP_MS` (`combat_feedback.gd`) : light 30/16, medium
  62/33, heavy 136/73, catastrophic 210/113.
- **Shake** : 6px traité comme le nouveau plafond "heavy" (`SHAKE_PROFILES`,
  4→6px) — light/medium non retestés par Milan, laissés tels quels plutôt
  que rescalés sur un seul point de mesure.
- **Flash d'impact** : jamais tiéré (un seul `flash_sprite()` pour tout
  coup) — `HitResponse.FLASH_TICKS` 2→4 (65ms), conversion directe.
- **Recul par défaut** : `recoil_strength_px` par défaut des 3
  `take_damage()` (Player/Enemy/BossGateMaw) 24.0→27.0 — interprété
  comme LA valeur de référence "non spécifiée" (les attaques déjà
  tunées explicitement — Poing Belluaire 40, boss 26-70 — gardent leur
  propre valeur).
- **Courbe de recul** : linéaire (`move_toward` vers 0) remplacée par
  une vraie courbe de POSITION ease-out — nouvelle fonction partagée
  `AnimationComposer.ease_out_step_px()` (même `ease_out_quad()` déjà
  utilisée par `Player._advance_dash()`, jamais une 2e courbe dupliquée),
  réutilisée par les 3 sites de recul (Player.take_damage() côté
  joueur, Enemy.take_damage(), BossGateMaw.take_damage()) qui
  partageaient jusqu'ici une décroissance de vitesse linéaire quasi
  identique copiée-collée 3 fois.

**Vérification** : `run_gameplay_smoke_test.sh` 100% vert (le check
boss_enrage, seul à lire directement l'ancien `_recoil_ticks_remaining`,
mis à jour sur les nouveaux `_recoil_tick`/`_recoil_total_ticks`).

**Restes de R4 traités dans cette passe** :
- **Sol `gate_premiere`/`test_arena`** : capture réelle confirmant le
  diagnostic (`assets/processed/sprites/world/floor_terrain_atlas.png`
  bien trop saturé/contrasté, absorbe la lecture du combat). Nouvel
  outil `tools/desaturate_floor_atlas.py` (PIL, déterministe, teinte
  intacte — HSV : saturation ×0,62, contraste de valeur resserré autour
  de 55%) appliqué directement sur l'atlas déjà cuit (pas de
  régénération PixelLab, 0 crédit). Comparaison avant/après confirmée
  par capture (saturation moyenne mesurée sur la zone de sol : 0,811 ->
  0,620) avant de committer le changement.
- **Chiffres de dégâts** : le fondu existait déjà (`damage_number.gd`,
  40% finaux) mais la trajectoire était une simple montée verticale —
  deux chiffres nés au même point (ex. Bras-Faux touchant 2 cibles)
  restaient superposés pile l'un sur l'autre, d'où le "statique"
  rapporté. Ajout d'une dérive latérale (`ARC_HORIZONTAL_PX`, direction
  dérivée d'un hash déterministe de position+montant — jamais un vrai
  hasard non seedé dans un chemin de feedback de combat, Addendum A
  §A.5) sur la MÊME courbe ease-out partagée que le reste (x et y).
- **Zoom caméra +20-25%** : PAS tranché — deux captures A/B produites
  (`--mode=scene`, cam_zoom=1.0 vs 0.8) et envoyées à Milan pour
  décision, comme demandé explicitement ("ça touche au cadrage général,
  ne pas trancher seul"). Aucun changement de code appliqué (le zoom de
  base du jeu reste géré par `CameraDirector.get_punch_zoom()`
  ponctuellement, pas un `BASE_ZOOM` permanent — à ajouter seulement si
  Milan valide l'option B).

**render_detector.py (détecteur de rendu factuel) : PAS intégré cette
passe** — Milan le décrit comme "fourni" mais le fichier est introuvable
dans le dépôt ou ailleurs dans cette session ; demandé à Milan de le
joindre avant de pouvoir l'intégrer/calibrer.

**Statut** : valeurs de game feel + sol + chiffres de dégâts terminés et
vérifiés (tests + captures). Zoom caméra en attente du choix de Milan
(A ou B). render_detector.py bloqué en attente du fichier. Redeploy web
à suivre. R3/R3bis toujours en attente du verdict de Milan sur le
prochain clip.

## 2026-08-22 — Zoom caméra tranché (option B) : BASE_ZOOM permanent

Milan a choisi l'option B (+25%, cam_zoom=0.8) sur les 2 captures A/B
envoyées. `CameraDirector.BASE_ZOOM := Vector2(0.8, 0.8)` + nouvelle
fonction `get_zoom()` = `BASE_ZOOM * get_punch_zoom()` (multiplication,
pas addition — le punch garde exactement la même intensité RELATIVE
quel que soit le zoom de base). `Player._physics_process()` : `_camera.
zoom = CameraDirector.get_zoom()` au lieu de `get_punch_zoom()` seul.
`get_punch_zoom()` reste inchangée et exposée telle quelle (le smoke
test `camera_punch_zoom_triggers_on_medium_hit_not_light` la lit en
isolation, indépendamment de tout zoom de base).

Un seul `player.tscn` partagé par `gate_premiere`/`test_arena`/
`outpost` (voir leurs `.tscn` respectifs, node "Player" instancié 3
fois) : ce changement dans `player.gd`/`camera_director.gd` s'applique
identiquement aux 3 scènes, pas 3 réglages séparés à synchroniser.

**Vérifié par capture réelle (pas seulement lu dans le code)** : les
modes existants de `capture_scene.gd` (`--mode=scene`) injectent
TOUJOURS leur propre `Camera2D` (`cam.make_current()`), ce qui aurait
masqué silencieusement l'effet réel de ce changement (la caméra
injectée écrase celle de Player, donc capturer avec l'ancien mode
aurait "confirmé" n'importe quelle valeur de zoom sans jamais tester le
vrai code). Nouveau flag `--use_scene_camera=1` : laisse la caméra RÉELLE
de Player (celle pilotée par `CameraDirector.get_zoom()`) active plutôt
que d'en injecter une — capturé sur les 3 scènes : le monde est
visiblement ~25% plus grand, HUD (barre de vie, `Niv. 1`) et boutons
tactiles (joystick, PB/BF/GV/PT/DDG/DASH/ATK/PERSO) restent pile à
leur place — `CanvasLayer` (root des 2 scènes UI) est par construction
immunisé à `Camera2D.zoom`, confirmé par capture plutôt que supposé.

**Vérification** : `--import` headless propre, `scripts/
run_gameplay_smoke_test.sh` 100% vert (aucune régression — les 2 checks
qui touchent la caméra lisent `CameraDirector.get_punch_zoom()`
directement, jamais `_camera.zoom`, donc indifférents à `BASE_ZOOM`).

**Statut** : terminé et vérifié, redeploy web à suivre immédiatement.
render_detector.py maintenant fourni par Milan — intégration en cours,
voir entrée suivante.

## 2026-08-22 — render_detector.py : intégration + calibration Poing Tellurique

Fichiers de Milan (`render_detector.py` + `test_render_detector.py`)
copiés tels quels dans `tools/`. Suite synthétique 4/4 rejouée dans cet
environnement (`python3 tools/test_render_detector.py`) : présent /
absent / flash blanc (channel_delta) / cas limite ("incertain") tous
corrects.

**Nouveau mode de capture** (`tools/capture_scene.gd`,
`--mode=player_action_sequence`) : aucun mode existant ne produisait
une SÉQUENCE d'images tick par tick (`frame_0000.png`, `frame_0001.png`,
...) au format attendu par `render_detector.load_frames_from_dir()` —
tous les autres modes capturent UN seul tick cible. Même mise en place
que `--mode=player_action` (Player réel + 2 ennemis, mêmes offsets).

**Bug trouvé et corrigé en construisant ce mode** : la première version
gelait/dégelait le `SceneTree` (`get_tree().paused`) à CHAQUE tick pour
réutiliser `_freeze_and_wait_render()` — résultat : les primitives VFX
ne se rendaient plus DU TOUT (`groundRing` de Poing Tellurique,
pourtant confirmé visible en capture ponctuelle `--mode=player_action`,
disparaissait entièrement en séquence). Cause exacte non isolée
(interaction entre le pause/dégel répété et le pipeline de rendu
logiciel), corrigée en abandonnant la pause pour cette capture : un
`process_frame` de plus après chaque `physics_frame`, jamais de gel.

**Vérification "alignement tick 0" (demandée explicitement par Milan)**
: en corrigeant le bug ci-dessus, un second problème est apparu — le
TOUT PREMIER frame capturé (tick 0, la baseline "avant effet") sortait
avec un fond NOIR (0,0,0) au lieu du gris neutre stable (76,76,76) de
tous les frames suivants, un artefact de chauffe du rasterizer logiciel
(llvmpipe) sur la toute première image rendue. Sans correctif, TOUTES
les couches ressortaient "present" dès le tick 1 avec
`pixel_fraction=1.0` — un faux positif qui ne mesurait que cet artefact,
jamais un vrai effet (exactement le risque que Milan avait anticipé).
Corrigé par 3 `process_frame` de chauffe avant la capture du tick 0.

**Calibration sur Poing Tellurique** (cas choisi par Milan, déjà
confirmé visible en capture manuelle cette session) : région/seuils par
primitive dérivés de vraies mesures sur une séquence de 31 frames
(0-30 ticks), pas inventés :
- `groundRing` (luminance_delta) : present, mean_delta~8-9.3 sur toute
  la fenêtre 1-18, seuil calé à 6.0/0.10 avec marge.
- `impactFlashFrame` (luminance_delta) : present, delta ~12 au contact
  (tick 18) montant à ~65-72 (gel de hit-stop qui retarde la
  décroissance visuelle, cohérent avec l'asymétrie Phase R4).
- `dustKick` (stddev_delta — texture, pas luminosité moyenne, exactement
  le cas d'usage documenté par Milan) : present, signature nette (saut
  36,9->84 dès le tick 19, décroissance ticks 26-27).
- `converge` (core, matière qui converge dans le poing) : **absent**
  selon le détecteur (delta max ~0,4, loin sous le seuil). Inspection
  visuelle d'une capture zoomée confirme un signal à peine perceptible
  — pas une absence aussi franche qu'un vrai bug de rendu (C1/Gueule
  Vide), documenté dans la recette comme piste ouverte plutôt que bug
  tranché : soit augmenter son contraste/échelle (même diagnostic que
  groundRing avant son propre correctif), soit recalibrer la mesure.
  Pas encore résolu.

`expected_layers` ajouté à `data/recipes/power.poing_tellurique.cast.json`
(liste brute, conforme au schéma de `render_detector.py` — les notes de
calibration vivent dans une clé séparée `_expected_layers_notes` pour ne
jamais casser `load_recipe()`). Rapport complet :
`/tmp/r4_captures/poing_tellurique_render_report.json` (non versionné).

**Non fait cette passe** : `expected_layers` sur les autres recettes
(Bras-Faux, Poing Belluaire, Gueule Vide, Totem du Vide...) — chacune
demande sa propre calibration par capture réelle (région/seuils
propres à son cadrage), pas un travail générique à dupliquer sans
vérification. Le pipeline complet (capture séquence -> calibrer ->
`expected_layers` -> `run_detection_from_paths()`) est maintenant
prouvé de bout en bout sur un cas réel ; l'étendre aux autres pouvoirs
reste un chantier à part entière, pas terminé ici.

**Vérification** : `scripts/run_gameplay_smoke_test.sh` 100% vert
(nouveau mode de capture n'affecte aucun code de gameplay). Rien à
redéployer côté web (outil de développement uniquement, pas de code
runtime jeu changé au-delà de `capture_scene.gd`).

## 2026-08-22 — Socle de référence : archivage planches + verrouillage palette Terre + audit 4 recettes vivantes

Mandat Milan en 3 points, explicitement **sans toucher aux 11
compétences restantes** de la bible — priorisation à venir dans un
futur mandat une fois ce socle posé.

**1. Archivage permanent des 15 planches** — les planches de référence
validées par Milan (Invocateur/Monstrification/Terre, 5 par classe)
n'existaient que dans l'historique de discussion. Recadrées (script
Pillow, crop vertical par bornes de ligne) et archivées sous
`docs/references/<classe>/<nom-competence>.png`, avec un
`docs/references/README.md` documentant le mapping fichier -> planche
source (4 uploads). Les 2 blocs "sprites de base/icônes/effets
communs" (transverses, pas liés à une compétence, présents en pied de
page sur 2 des 4 uploads) archivés séparément sous
`docs/references/shared/`.

Divergence de nommage relevée : le mandat citait "Éperon" comme 5e
planche Terre, mais aucune planche de ce nom n'existe dans les
uploads — la 5e planche Terre réellement fournie est **Fissure
Éruptive**. Traité comme une divergence de nommage dans la demande
(documentée dans le README), pas comme une planche manquante : les 5
planches Terre annoncées sont bien toutes présentes.

**2. Verrouillage de `data/palettes/terre.json`** — comparée aux 5
planches Terre désormais archivées. Aucun écart net : Marée de Sable
(sable ocre/tan sur roches brun-gris), Carapace (plaques rocheuses
brun-gris-beige désaturées), Effondrement (fissures brun-terreux qui
convergent puis explosent en éclats ocre clair/poussière pâle),
Fissure Éruptive (pics gris-pierre + nuages de poussière gris-tan) —
et Poing Tellurique, déjà audité en détail via `render_detector.py`
ci-dessus. Toutes cohérentes avec la palette déjà en place (brun-gris
terreux / gris pierre foncé / ocre clair / poussière pâle, hue 30-40°),
aucune couleur hors de cette famille. Flag `PROPOSITION` retiré,
`"status": "VERROUILLÉE"` ajouté, structure et valeurs numériques
inchangées (aucune réinvention, la bible reste la référence de
matière) — changement documenté dans les notes du fichier lui-même.

**3. Audit factuel des 4 recettes vivantes (aucun changement de code)** :

- **Gueule Vide** (`power.gueule_vide.cast.json`, palette
  `invocateur_vide`) — **cohérent**. La planche (créature d'encre
  noire/gris-lilas surgissant du sol, cercle runique bleu pâle sous les
  pieds, éclaboussures sombres) correspond terme à terme aux 4 rôles de
  la palette (noir d'encre, gris-lilas désaturé, gris cendre, pointe
  bleu pâle système sur le cercle au sol). Aucun écart relevé.

- **Poing Tellurique** (`power.poing_tellurique.cast.json`, palette
  `terre`) — **cohérent**, déjà audité en détail ci-dessus par mesure
  réelle (`render_detector.py`) : groundRing/impactFlashFrame/dustKick
  confirmés présents, `converge` reste une piste ouverte non tranchée
  (signal à peine perceptible, pas une absence franche) — pas un
  nouveau constat, le même suivi déjà documenté dans la recette.

- **Bras-Faux** (`power.bras_faux.cast.json`, palette `parasite`) —
  **écart notable de couleur**. La palette `parasite` est explicitement
  définie (notes du fichier, citant GDD §7) comme un "grayscale strict...
  gris cendre, gris foncé, noir, pointe de bleu-gris pâle et lilas-gris
  pâle... NO PURPLE saturé, NO GLOW" — les teintes de couleur (bleu-gris
  ~205°, lilas-gris ~275°) n'apparaissant qu'en fine touche ("pointe de",
  jamais dominante). Or la planche Bras-Faux montre un bras-tendon/faux
  rouge-brun-rouille organique (chair et tendons) comme couleur
  DOMINANTE du membre transformé sur les 4 panneaux, avec des
  éclaboussures rouges — pas une pointe froide bleu-gris/lilas sur fond
  gris cendre, mais une teinte chaude rouge-brun qui domine tout le
  visuel. Écart de teinte net entre la palette de code (froide,
  désaturée, à peine teintée) et la référence (chaude, organique,
  rouge-brun affirmé).

- **Poing Belluaire** (`power.poing_belluaire.cast.json`, palette
  `parasite` réutilisée) — **aucune planche dédiée parmi les 15
  fournies** ("Poing Belluaire" n'est le nom d'aucune des 15
  compétences illustrées). Candidat le plus proche par construction :
  **Coup de Poing Monstrifié** (Monstrification) — même archétype exact
  que documenté dans les notes de la recette ("un seul coup frontal
  très lourd", pas de traînée/balayage) : Préparation/Transformation ->
  Impact -> Récupération, sans étape de balayage, contrairement à
  Bras-Faux. Hypothèse plausible (non tranchée) d'une divergence de
  nommage bible/code du même type que Terre/"Éperon" ci-dessus — à
  confirmer par Milan, pas assumé comme acquis. Si cette
  correspondance est la bonne : même écart de teinte que Bras-Faux
  (planche rouge-rose organique dominante vs palette `parasite`
  froide/désaturée, réutilisée telle quelle par cette recette), et la
  colonne "Assets - Effets" de la planche montre un impact + une
  fissure au sol qui n'a pas d'équivalent dans les 3 couches actuelles
  de la recette (`converge`/`impactStar`/`impactFlashFrame`, aucune
  couche de fissure/craquelure au sol) — à vérifier une fois l'identité
  confirmée, pas un constat définitif ici.

Aucun changement de code ni de recette à ce stade (demande explicite de
Milan : audit seulement). Aucune des 11 compétences restantes entamée.

## 2026-08-22 — Trois décisions de Milan : couleur Monstrification, confirmation Poing Belluaire, audit Classe unique

**1. `data/palettes/parasite.json` réécrite — verdict Milan : la référence
a raison, pas le code.** L'audit précédent avait relevé que la palette
"parasite" (grayscale strict + pointe froide bleu-gris/lilas, mandatée
par le texte GDD §7) ne correspondait pas aux 5 planches Monstrification
archivées (rouge-brun-rouille organique dominant). Milan tranche : la
planche fait foi, pas le texte GDD/le code d'origine.

Valeurs dérivées par échantillonnage réel des pixels (pas à l'oeil,
même méthode que la vérification `render_detector.py` sur Poing
Tellurique) : script ponctuel (non versionné) sur la colonne "Assets -
Effets" des 5 planches (`docs/references/monstrification/*.png`),
filtrage des pixels rouge-orangé saturés (hue proche de 0-40°, sat>30%)
pour isoler la matière organique du fond crème/du personnage
gris/du texte noir — 21 456 pixels retenus au total, moyenne circulaire
de teinte par tranche de luminosité (V) :

| tranche V | n | teinte | saturation | valeur |
|---|---|---|---|---|
| 0-10% (le plus sombre) | 2192 | 2,6° | 40,3% | 17,6% |
| 30-50% | 4512 | 7,5° | 37,3% | 31,0% |
| 50-70% | 4564 | 10,6° | 36,6% | 38,4% |
| 90-100% (le plus clair) | 2163 | 18,2° | 33,9% | 61,3% |

Rampe cohérente et mesurée : la teinte se réchauffe (rouge profond ->
orangé) à mesure que la luminosité monte, un comportement de rim-light
naturel sur de la matière organique — pas une valeur inventée. Les 5
planches sont individuellement cohérentes entre elles (teinte moyenne
par planche 5-14°, aucun outlier). 4 rôles réécrits en conservant EXACTEMENT
la même structure et les mêmes champs `usage` (aucun remapping
primitive->rôle) :
- signature 1 (corps principal) : "rouge-brun tendineux", hue 9°, sat 37%, val 38%
- signature 2 (Root/profondeurs) : "brun-rouille profond", hue 3°, sat 40%, val 18%
- contact (éclat/impact) : "roux-orangé vif", hue 18°, sat 34%, val 61%
- intermédiaire (transitions) : "roux clair organique", hue 14°, sat 35%, val 48%

**Vérifié : aucun résidu de l'ancienne teinte froide.** Le système est
purement data-driven (`src/vfx/vfx_recipe_registry.gd::_resolve_color` lit
`data/palettes/<palette_id>.json` et matche la primitive contre le champ
`usage` en texte libre — seul repli = gris neutre générique si aucune
correspondance). Grep sur `205|275|bleu-gris|lilas` dans `src/` : aucune
occurrence dans le code (`.gd`), la seule trace de l'ancienne teinte
était dans ce fichier JSON, maintenant réécrit. Bras-Faux et Poing
Belluaire référencent `palette_id: "parasite"` sans aucune couleur codée
en dur dans leurs couches — les deux recettes héritent donc du nouveau
rouge-brun automatiquement, sans modification de fichier de recette
nécessaire (vérifié aussi qu'aucune des deux notes de recette ne
décrivait elle-même la teinte froide en texte — rien à corriger là).

**2. Poing Belluaire = Coup de Poing Monstrifié, confirmé par Milan.**
Note de `data/recipes/power.poing_belluaire.cast.json` mise à jour pour
pointer vers `docs/references/monstrification/coup_de_poing_monstrifie.png`
comme référence visuelle confirmée (recette non modifiée par ailleurs).

Vérification du point soulevé lors de l'audit précédent — l'absence
d'une couche fissure/craquelure au sol : **confirmé, c'est un vrai
manque, pas couvert autrement.** La recette n'a que 3 couches
(`converge` anticipation, `impactStar`+`impactFlashFrame` contact) —
aucune couche de type `fractureLine`/`groundRing` qui produirait un
décalque de sol fissuré, contrairement à Poing Tellurique qui EN a un
(`groundRing`, anticipation). `impactStar` est un éclat/étoile
d'impact ponctuel, pas un décalque persistant au sol — les deux
effets ne se recouvrent pas visuellement. La planche montre bien cet
effet de fissure au sol dans sa colonne "Assets - Effets", en plus de
la progression du poing et de l'éclat d'impact. Signalé tel quel,
aucune couche ajoutée à ce stade (audit seulement, comme demandé).

**3. Audit factuel : le HUD des captures zoom caméra est-il un HUD de
debug ou le HUD réel ?** Réponse basée sur lecture directe du code
(les captures de la session zoom n'ont pas été versionnées, donc
vérifié via la source plutôt que de re-générer les images) :

`src/gameplay/player.gd::_physics_process()` lie sans AUCUNE condition
de garde les 4 pouvoirs sur les 4 actions `power1`-`power4` :
```
power1 -> _cast_gueule_vide()       (Invocateur)
power2 -> _start_bras_faux()        (Monstrification)
power3 -> _start_poing_belluaire()  (Monstrification)
power4 -> _start_poing_tellurique() (Terre)
```
Aucune vérification de "Classe active" avant l'appel. Côté HUD tactile,
`scenes/ui/touch_controls.tscn` instancie ButtonPower1/2/3/4 de façon
permanente et inconditionnelle (les 4 nœuds `TouchScreenButton` existent
tous dans la scène, aucune visibilité conditionnelle). Recherche
exhaustive (`grep -rn "ButtonPower\|current_class\|classe_active\|
active_class\|selected_class\|unlock"` sur `src/` et `scenes/`) : **zéro
résultat** — il n'existe actuellement AUCUN concept de "Classe active"
ni de système de déblocage dans le code, à quelque niveau que ce soit.

**Verdict : ce n'est PAS un HUD de debug.** `touch_controls.tscn` est le
HUD tactile réel utilisé en jeu (le même dont le positionnement a été
vérifié sous le nouveau `BASE_ZOOM` cette session) et `player.gd` est le
script réel du joueur. Les captures montraient donc fidèlement l'état
actuel du jeu : un seul personnage avec les 4 pouvoirs des 3 Classes
(Invocateur/Monstrification/Terre) disponibles simultanément et sans
restriction, dès le début. **Ceci contredit directement** la nouvelle
règle de Milan (1 seule Classe par run, 5 compétences débloquées
progressivement). Signalé tel quel — **aucune correction appliquée**,
conformément à l'instruction explicite de ne rien changer tant que le
système de déblocage complet n'est pas précisé.

**AMENDEMENT GDD EN ATTENTE DE DÉTAIL** (règle confirmée par Milan,
consignée ici pour ne pas la perdre, non implémentée) :
- Le personnage n'a qu'**une seule Classe par run** (Invocateur,
  Monstrification OU Terre — jamais plusieurs à la fois).
- Les **5 compétences de cette Classe se débloquent progressivement**
  pendant la run, plutôt que d'être toutes disponibles dès le départ.
- **Non précisé par Milan, ne rien inventer d'ici là** : l'ordre de
  déblocage des 5 compétences, et la méthode de déblocage (niveau ?
  étage franchi ? nombre de kills ? autre ?).

Aucun changement de code pour ce point 3 (audit seulement, comme
demandé). Rien à redéployer côté web pour cette passe (JSON de données
+ documentation uniquement, aucun code runtime modifié).

## 2026-08-22 — Système Classe/déblocage : état des lieux + plan (PAS ENCORE IMPLÉMENTÉ)

Milan a confirmé l'amendement GDD (1 Classe/run tirée au hasard, 5
compétences débloquées par niveau, HUD conditionnel) et demandé
explicitement un état des lieux + un plan présenté AVANT tout code
("changement structurel, pas un ajustement ponctuel"). Ce qui suit est
ce plan — **aucun fichier de code modifié cette passe**, seulement de
la lecture/analyse. Attend le retour de Milan sur plusieurs questions
bloquantes avant la moindre ligne de code.

**État des lieux — l'architecture actuelle est 100% câblée en dur, 1:1,
sans aucune indirection :**
- `project.godot` : 4 actions d'input `power1`-`power4` (touches
  E/R/T/G), aucune 5e action.
- `player.gd::_physics_process()` : `power1` appelle TOUJOURS
  `_cast_gueule_vide()`, `power2` TOUJOURS `_start_bras_faux()`,
  `power3` TOUJOURS `_start_poing_belluaire()`, `power4` TOUJOURS
  `_start_poing_tellurique()` — zéro garde de Classe, zéro indirection.
- `scenes/ui/touch_controls.tscn` : 4 `TouchScreenButton` permanents
  (ButtonPower1-4), labels texte STATIQUES ("GV"/"BF"/"PB"/"PT") gravés
  dans la scène, aucun script attaché au nœud racine pour piloter
  visibilité/libellé (seul `Joystick` a un script, `virtual_joystick.gd`).
- `src/ui/hud.gd` : 4 overlays de cooldown fixes, chacun lié en dur à
  un getter précis (`get_power1_cooldown_ratio`,
  `get_bras_faux_cooldown_ratio`, `get_poing_belluaire_cooldown_ratio`,
  `get_poing_tellurique_cooldown_ratio`) — même rigidité que
  touch_controls.
- `src/ui/character_screen.gd` : **conflit direct avec le nouvel
  amendement**. Le fichier porte une exigence GDD EXPLICITE et
  documentée en commentaire : "Rank Zero doit afficher CLASS = NONE et
  ne jamais recevoir une Classe inventée" — `_stats_label.text` affiche
  littéralement `"CLASSE : AUCUNE"` en dur. Maintenant qu'une Classe
  réelle sera tirée et vécue toute la run, cette règle GDD est-elle
  caduque (la Classe doit s'afficher) ou reste-t-elle absolue (Milan
  distinguait peut-être "Classe de bâtisseur"/méta-progression et
  "Classe de pouvoir" tirée en run) ? **Ne pas trancher seul.** Détail
  secondaire, même fichier : `_skills_label.text` liste en dur "E —
  Gueule Vide\nR — Bras-Faux" — déjà obsolète aujourd'hui (oublie Poing
  Belluaire/Poing Tellurique), à rendre dynamique de toute façon.
- `src/system/run_state.gd` (autoload) : `player_stats: Stats` est un
  Resource unique créé UNE fois au chargement de l'autoload et jamais
  réinitialisé ensuite — il n'existe **aucune notion explicite de
  "début de run"** distincte du démarrage du process (pas de fonction
  `new_run()`/`restart()` trouvée nulle part dans le dépôt). C'est
  exactement le même point d'ancrage que Milan demande pour le tirage
  de Classe : `active_class` peut suivre le même patron que
  `player_stats` (tiré une fois à l'init de l'autoload), sans qu'il
  faille inventer une notion de "run" qui n'existe pas encore ailleurs
  dans le code.
- `stats.gd` : `signal leveled_up(new_level: int)` déjà émis dans
  `add_xp()`, en boucle (un gain d'XP massif peut émettre plusieurs
  fois de suite, niveau par niveau, jamais sauté) — exploitable tel
  quel, rien à changer ici.
- `tools/smoke_test_gameplay.gd` : les 4 checks vivants
  (`_check_gueule_vide`, `_check_bras_faux`, `_check_poing_belluaire`,
  `_check_poing_tellurique`) déclenchent CHACUN via
  `Input.action_press("powerN")` — donc le jour où l'entrée devient
  gardée par Classe/niveau, ces 4 checks casseront tous en silence
  (spawn=false) SAUF si chacun force d'abord `RunState.active_class` et
  `stats.level` au bon état avant d'appuyer. Mise à jour obligatoire
  des 4 blocs, pas optionnelle — c'est précisément la régression que
  Milan demande d'éviter.

**Réalité de contenu actuel (contrainte transversale à ne pas
oublier)** : à ce jour, sur les 5 compétences nominales par Classe,
seules certaines existent réellement en code/recette VFX :
Invocateur = 1/5 (Gueule Vide seule), Monstrification = 2/5 (Bras-Faux,
Poing Belluaire), Terre = 1/5 (Poing Tellurique seule). Les 11
compétences restantes n'ont ni fonction `_start_X()` ni recette JSON —
conformément à la consigne permanente de ne pas les commencer, le
système de déblocage doit fonctionner correctement même quand la
plupart de ses paliers de niveau "débloquent" une compétence qui n'a
tout simplement rien à afficher/appeler pour l'instant (bouton absent,
pas un bouton grisé cassé). Conséquence concrète pour Milan : une run
qui tire Invocateur ou Terre n'aura QU'UN SEUL bouton de pouvoir actif
pour toute sa durée tant que le reste de la bible n'est pas construit ;
seule Monstrification en aura deux. Signalé pour que ce ne soit pas une
surprise au prochain test — pas un problème à corriger ici.

**Contradictions de Tier relevées sur les planches archivées (bloquent
le verrouillage de l'ordre — voir docs/references/) :**

*Terre* — planches avec Tier explicite et cohérent 1→4 : Poing
Tellurique=TIER 1, Marée de Sable=TIER 2, Carapace=TIER 3,
Effondrement=TIER 4. Fissure Éruptive (planche mixte) n'affiche AUCUN
Tier. Or l'ordre donné en exemple par Milan lui-même dans le mandat
précédent — "Poing Tellurique -> Marée de Sable -> Éperon -> Carapace
-> Effondrement" — place ce 5e pouvoir ("Éperon", nom qui ne correspond
à aucune planche fournie, cf. divergence déjà signalée) EN 3E position,
AVANT Carapace(T3) et Effondrement(T4). Ça contredit frontalement les
Tiers imprimés sur les planches. **Je ne tranche pas** : soit l'ordre
d'exemple de Milan est le bon et les Tiers 3/4 de Carapace/Effondrement
sont à ignorer pour l'ordre de déblocage, soit les Tiers font foi et
Fissure Éruptive vient en dernier (Tier 5 par élimination) — à
confirmer.

*Monstrification* — INCOHÉRENCE INTERNE, pas seulement un désaccord
avec un exemple : Bras-Faux=TIER 2, Mâchoire=TIER 3, Pattes de
Chasse=TIER 3 (DOUBLON avec Mâchoire), Forme Bestiale=TIER 4, Coup de
Poing Monstrifié (= Poing Belluaire, confirmé la passe précédente)
n'affiche AUCUN Tier. Aucune planche ne réclame Tier 1 ni Tier 5. Il
manque soit une correction de Tier sur une des planches, soit une
information supplémentaire sur Coup de Poing Monstrifié/Poing
Belluaire (probablement Tier 1, le seul qui reste libre en bas de
l'échelle, mais ce n'est qu'une supposition — le bloc de dégâts/recul/
cooldown actuel en jeu, POING_BELLUAIRE > BRAS_FAUX, suggérerait plutôt
un Tier supérieur si on se fiait au seul équilibrage code, mais Milan a
explicitement demandé de ne jamais utiliser l'équilibrage code pour
trancher un désaccord avec la bible). **Je ne tranche pas.**

*Invocateur* — pas de contradiction relevée : Gueule Vide=T1, Corbeau
Pâle=T2, Poing du Colosse=T3, Œil sans Regard=T4, Invocation du Serpent
(planche mixte) sans Tier affiché — cohérent par élimination avec Tier
5, mais toujours non confirmé explicitement sur la planche elle-même.

**Architecture proposée (sous réserve des réponses de Milan
ci-dessous) :**
1. `RunState` (autoload) : nouveau champ `active_class: String`, tiré
   aléatoirement parmi les 3 classes UNE fois à l'initialisation de
   l'autoload — même patron que `player_stats`, aucun écran de
   sélection, rien à construire côté UI pour le tirage lui-même.
2. Nouvelle donnée (ex. `data/classes/<classe>.json`, un fichier par
   Classe ou un seul fichier combiné, à trancher) : la liste FIXE des 5
   compétences dans l'ordre bible, avec pour chacune : nom, Tier,
   palier de niveau de déblocage, et si elle est "implémentée" (a une
   fonction `_start_X()`/`_cast_X()` + une recette VFX réelle) ou non
   (placeholder, rien à faire tant que non construite).
3. `player.gd` : remplacer les 4 appels directs par une résolution de
   "slot" — `power1..4` deviennent des emplacements de COMBAT
   génériques (pas des identités figées de compétence), résolus au
   moment de l'appui selon (Classe active, niveau courant, position
   dans l'ordre bible de cette Classe parmi les compétences déjà
   implémentées). Connecter `stats.leveled_up` en `_ready()` pour
   rafraîchir l'état de déblocage affiché par le HUD/touch (pas besoin
   de cache complexe : le niveau courant suffit à recalculer l'état à
   la demande).
4. `touch_controls.tscn` : ajouter un script au nœud racine
   `TouchControls` (aucun aujourd'hui) qui, à chaque changement de
   niveau, masque les `ButtonPowerN` dont le slot est vide/non débloqué
   (absent, pas grisé — exigence explicite de Milan) et réécrit le
   `text` du Label selon la compétence réellement assignée à ce slot.
5. `hud.gd` : même logique de masquage sur les 4 overlays de cooldown.
6. `character_screen.gd` : en attente de la réponse de Milan sur le
   conflit "CLASSE : AUCUNE" avant tout changement.
7. `tools/smoke_test_gameplay.gd` : mise à jour obligatoire des 4 blocs
   vivants pour forcer `RunState.active_class` + `stats.level` au bon
   état avant chaque test d'input, afin de ne rien casser.

**Question ouverte transversale — 5e emplacement de pouvoir** : le jeu
n'a que 4 slots (E/R/T/G + 4 boutons tactiles) pour un maximum
théorique de 5 compétences par Classe. Proposition : NE PAS ajouter de
5e slot maintenant (aucune Classe actuelle n'en a besoin avec le
contenu déjà construit — même discipline "pas de fonctionnalité pour
un besoin hypothétique" que le reste du projet), construire la
résolution de slot de façon assez générique pour qu'ajouter un 5e slot
plus tard (quand une Classe aura effectivement 5 compétences
implémentées) soit un changement mineur. À valider par Milan.

**Proposition de palier niveau -> compétence (À VALIDER, pas verrouillé)**
: 1 / 3 / 6 / 10 / 15 comme suggéré par Milan. Note de cohérence
économique (calcul, pas un verdict) : `xp_to_next_level()` coûte 50×N
XP pour passer du niveau N à N+1 (coût cumulatif niveau 25×L×(L-1)) ;
avec les seules sources d'XP déjà codées (ramassage ~20 XP,
ennemi normal ~8 XP, boss ~120 XP), atteindre le niveau 15 réclame
~5250 XP cumulés, soit plusieurs centaines de kills/pickups selon la
longueur réelle d'une run — je n'ai pas de référence sur la longueur de
run visée pour juger si ce rythme est trop lent ou correct, donc je ne
l'ajuste pas moi-même comme demandé.

**QUESTIONS BLOQUANTES avant tout code (résumé)** :
1. Terre : ordre d'exemple de Milan vs Tiers imprimés — lequel prime ?
2. Monstrification : Tier de Coup de Poing Monstrifié/Poing Belluaire
   + résolution du doublon Tier 3 Mâchoire/Pattes de Chasse ?
3. `character_screen.gd` "CLASSE : AUCUNE" : règle GDD toujours valable
   telle quelle, ou remplacée par l'affichage de la vraie Classe active ?
4. Paliers 1/3/6/10/15 : à valider ou à ajuster (voir note économique) ?
5. 5e emplacement de pouvoir : absent pour l'instant (ma proposition)
   ou à créer dès maintenant en plomberie inerte ?
6. Un seul bouton actif toute la run pour Invocateur/Terre tant que le
   reste de la bible n'existe pas en code : acceptable pour ce mandat,
   ou faut-il revoir la priorité de construction des 11 compétences
   restantes en conséquence (hors scope explicite de ce mandat, mais
   Milan doit le savoir) ?

Rien commité côté code — uniquement cette entrée de worklog (analyse/
plan). Implémentation suspendue jusqu'au retour de Milan.

## 2026-08-22 — Système Pouvoir/déblocage : IMPLÉMENTÉ

Milan a tranché les 6 questions bloquantes du plan précédent. Ordre
verrouillé par Classe, paliers de niveau (asymétriques pour
Monstrification), terminologie ("Pouvoir", pas "Classe" —
character_screen.gd/"CLASSE : AUCUNE" non touché, règle GDD distincte),
5 emplacements réels dès cette passe (pas de report), conséquence
"1 seul bouton actif toute la run pour Invocateur/Terre" acceptée.

**Données (`data/pouvoirs/{invocateur,monstrification,terre}.json`)** :
un fichier par Pouvoir, 5 compétences ordonnées par tier avec
`unlock_level`/`touch_label`. Ordre verrouillé :
- Invocateur : Gueule Vide(1)→Corbeau Pâle(3)→Poing du Colosse(6)→
  Œil Sans Regard(10)→Serpent Creux(15).
- Terre : Poing Tellurique(1)→Marée de Sable(3)→Carapace(6)→
  Effondrement(10)→Fissure Éruptive(15).
- Monstrification (paliers délibérément différents, cf. mandat) :
  Poing Belluaire(1)→Bras-Faux(3)→Mâchoire(6)→Forme Bestiale(**14**)→
  Pattes de Chasse(**18**) — écart 6→14 nettement le plus large des 3
  Pouvoirs, resserré ensuite pour 14→18, exactement le rythme demandé
  (Forme Bestiale = "seule vraie transformation complète de la bible").
  Chiffres de Milan conservés tels quels (1/3/6/14/18).

**`src/system/pouvoir_registry.gd`** (autoload `PouvoirRegistry`) :
charge/cache les 3 JSON (même patron que
`VfxRecipeRegistry._load_palette()`). Ne connaît QUE l'ordre/les
paliers — délibérément ignorant de ce qui est réellement implémenté en
code (séparation données/dispatch, voir plus bas).

**`src/system/run_state.gd`** : nouveau champ `active_power: String`,
tiré au hasard parmi les 3 Pouvoirs à l'init de l'autoload (même patron
que `player_stats`, aucune notion de "début de run" à inventer). Liste
des 3 Pouvoirs dupliquée en dur plutôt que référencée via
`PouvoirRegistry.POUVOIR_IDS` : un champ par défaut se résout à la
construction du nœud, avant toute garantie sur l'ordre d'init des
autres autoloads — RunState reste sans AUCUNE dépendance, comme documenté.

**`src/gameplay/player.gd`** — cœur du changement : `power1`..`power5`
ne sont plus liés en dur à une compétence (`_cast_gueule_vide()`,
`_start_bras_faux()`, etc. directement dans `_physics_process()`) mais
résolus dynamiquement via un nouveau `_try_activate_power_slot(slot_
index)`. Table `IMPLEMENTED_SKILL_HANDLERS`/`IMPLEMENTED_SKILL_
COOLDOWN_GETTERS` (id de compétence -> nom de méthode) : SEULE source
de vérité sur ce qui a une fonction réelle aujourd'hui (4 compétences
sur 15). `get_power_slot_info(slot_index)` (public, lu par
touch_controls.gd/hud.gd/character_screen.gd) retourne `{}` si le slot
n'est pas débloqué par le niveau OU si la compétence qui s'y trouverait
n'est pas implémentée — absent, jamais "grisé". Conséquence directe du
nouvel ordre verrouillé : Poing Belluaire est maintenant tier 1 de
Monstrification (pas tier 3 comme dans l'ancien câblage), Poing
Tellurique tier 1 de Terre (pas tier 4) — les deux se déclenchent
maintenant via "power1", jamais "power3"/"power4".

**`scenes/ui/touch_controls.tscn` + `src/ui/touch_controls.gd`** (nouveau
script, la scène n'en avait aucun) : `ButtonPower5` ajouté (touche H,
position (315,305)), et un poll en `_process()` (même discipline que
hud.gd/character_screen.gd) masque chaque bouton (`visible = false`,
pas un overlay) et réécrit son label selon `Player.get_power_slot_info()`.

**`scenes/ui/hud.tscn` + `src/ui/hud.gd`** : `Power5` ajouté au
conteneur `Cooldowns` (même grille, pitch 32px). `_process()` généralisé
en boucle sur 5 slots : conteneur entier masqué si vide (pas seulement
l'overlay de cooldown), sinon label + overlay mis à jour via
`get_power_slot_info()`/`get_power_slot_cooldown_ratio()`.

**`src/ui/character_screen.gd` + `.tscn`** : "CLASSE : AUCUNE" **non
touché** (règle GDD distincte, confirmée toujours valide). Nouveau
`PouvoirLabel` séparé affichant "POUVOIR : <valeur active>". Le texte
`_skills_label` (déjà obsolète avant ce mandat : oubliait 2 des 4
compétences vivantes) est maintenant dynamique, listant les slots
réellement débloqués+implémentés avec leur touche réelle (E/R/T/G/H).

**`project.godot`** : action `power5` ajoutée (touche H), autoload
`PouvoirRegistry` enregistré.

**`tools/smoke_test_gameplay.gd`** : les 4 checks vivants
(`_check_gueule_vide`/`_check_bras_faux`/`_check_poing_belluaire`/
`_check_poing_tellurique`) fixent maintenant explicitement `RunState.
active_power` (+ `stats.level = 3` pour Bras-Faux, tier 2) avant de
presser leur touche — et Poing Belluaire/Poing Tellurique pressent
maintenant "power1" (plus "power3"/"power4", cf. nouvel ordre de tier).
`"power5"` ajouté à la liste `gameplay_actions_have_no_mouse_button_
bindings`. Nouveau check `_check_power_slot_gating()` : vérifie le
mécanisme lui-même (pas seulement la non-régression) — un slot
débloqué+implémenté est exposé, un slot implémenté mais sous son palier
reste absent puis apparaît une fois le niveau atteint, un appui sur un
slot verrouillé ne déclenche RIEN côté gameplay (pas juste "bouton
absent"), et le ratio de cooldown d'un slot vide est 0.0.

**Vérification** : `scripts/run_gameplay_smoke_test.sh` 100% vert (65
checks, dont les 5 nouveaux). `touch_controls.tscn`/`hud.tscn`/
`character_screen.tscn` non exercés par ce smoke test (aucune scène de
jeu réelle n'y est instanciée) — vérifiés séparément en lançant
`scenes/gameplay/test_arena.tscn` en headless (xvfb + Vulkan logiciel,
15s) : aucune erreur de nœud manquant/script cassé (les 2 erreurs
`tile_set->get_terrain_sets_count() = 0` observées sont préexistantes,
sans rapport avec ce mandat — tileset de terrain, pas UI/Pouvoir).

**Note tooling (hors mandat, corrigée par prudence)** :
`tools/capture_scene.gd` avait deux exemples de docstring ("--action=
power2"/"--action=power4") qui prétendaient encore une identité de
compétence fixe par slot — commentaires seulement corrigés pour
refléter la résolution dynamique via `RunState.active_power`, aucune
nouvelle fonctionnalité ajoutée à l'outil.

Rien à redéployer côté web spécifiquement pour cette passe (aucune
scène de jeu réelle capturée/comparée visuellement) — HUD/touch
vérifiés par lecture de logs headless, pas par capture visuelle Milan.

## 2026-08-22 — Critique probabiliste ("Black Flash", nom de travail — jamais exposé au joueur)

Verrouillé par Milan, aucune question bloquante. État stocké sur
`Player` à côté de `_combo_step` (`_combo_crit_chance_percent`,
`_combo_hit_free_so_far`) — c'est un état de combo, pas une stat de
progression durable, donc pas sur `Stats`.

- **Roulé sur CHAQUE coup** du combo à 3 coups existant (`_try_hit()`),
  aucune restructuration : `randf()*100 < chance_courante`. Vrai
  hasard non seedé assumé ici — Addendum A §A.5 vise les variations
  cosmétiques sans enjeu dans un chemin de feedback (ex. direction d'un
  chiffre de dégâts), pas une probabilité de gameplay que Milan demande
  explicitement aléatoire.
- **Streak** : `_start_attack(1)` réarme `_combo_hit_free_so_far` à
  true (pas les chaînages vers coup2/3). `take_damage()` le passe à
  false immédiatement + reset NET `_combo_crit_chance_percent` à 5%
  (jamais une décroissance), à TOUT moment, pas seulement pendant un
  combo. `_end_combo()` vérifie `_combo_step == 3` (donc un combo
  vraiment complet, pas 1 ni 2 coups) ET `_combo_hit_free_so_far` avant
  d'ajouter +3% (`minf(..., 40.0)`).
- **x1.5** (`CRIT_DAMAGE_MULT`), pas x2 — verdict explicite de Milan.
- **Palier de feedback "critical"** (`combat_feedback.gd`) : au-dessus
  de "catastrophic", dérivé par le MÊME multiplicateur ×1,5 que les
  dégâts (catastrophic 210ms/113ms -> critical 315ms/170ms ; shake heavy
  6px/7 ticks -> critical 9px/10 ticks) — même discipline que le rescale
  de tiers Phase R4, pas des chiffres inventés sans rapport. ÉCRASE le
  tier normal du coup (jamais additionné) : un jab léger critique se lit
  comme le coup le plus lourd du jeu.
- **Flash plein écran, nouveau** (`CombatFeedback.trigger_screen_flash()`/
  `get_screen_flash_color()`, consommé par un `ColorRect` ajouté à
  `hud.tscn`) : "flash, pas juste plus fort" (Milan) — teinte
  (1.0, 0.93, 0.35) jamais utilisée ailleurs dans le HUD/VFX de combat,
  décroissance linéaire nette sur 8 ticks. Délibérément indépendant du
  système de palette (qui aurait limité la distinction à la couleur déjà
  prise par chaque recette) — la garantie de lisibilité en un coup
  d'œil ne dépend d'aucune primitive VFX locale.
- **Signal sonore distinct** : `critical_hit.wav` généré via pyfxr
  (`scripts/generate_sfx.py`, même pipeline que les 6 sons existants) —
  hauteur MONTANTE + punch d'attaque, à l'opposé de light_impact/
  heavy_impact (descendants/plats) pour ne jamais être confondu au
  mixage. Les 6 fichiers existants régénérés à l'identique (seeds fixes
  inchangés, diff vérifié vide) en même passe.
- **Nom de travail** : "Black Flash" n'apparaît nulle part dans un texte
  visible par le joueur (aucun texte UI n'a été ajouté du tout pour ce
  mécanisme — seul le flash/shake/son/dégâts, pas de libellé) —
  respecté par construction, rien à retenir de plus tant qu'aucun nom
  définitif n'est fourni.

**Déterminisme des tests** (le vrai risque de cette passe) : un crit
aléatoire pendant un check existant de dégâts/hitstop exacts l'aurait
fait échouer de façon intermittente — pire, la chance peut monter
jusqu'à 40% au fil de combos propres enchaînés dans la MÊME suite.
Fixé par une seule ligne dans `_ready()` : `_player.
_combo_crit_chance_percent = 0.0` pour toute la suite existante (0% =
jamais de crit, quel que soit `randf()` — pas de seed RNG à contrôler).
Nouveau `_check_critical_hit()` force 100% pour vérifier x1,5/flash/
shake, puis remet 5% pour vérifier le streak (+3% après un combo propre
à 3 coups, reset à 5% sur `take_damage()` direct) par manipulation
d'état, avant de revenir à 0% pour le reste de la suite.

**Vérification** : `scripts/run_gameplay_smoke_test.sh` 100% vert (70
checks, 4 nouveaux). `test_arena.tscn` relancé headless (xvfb) : aucune
erreur de nœud sur le nouveau `ScreenFlash` dans `hud.tscn`.

## 2026-08-22 — MANDAT AUTONOME v3 : Phase 1 (le monde et le décor)

**Contexte** : Milan indisponible pour arbitrer ce mandat (4 phases,
autonomie totale dans les budgets fixés). Ordre d'exécution imposé :
monde d'abord (plus gros manque visuel constaté, et sert de base jugée
pour la suite). Cf. mandat complet archivé dans l'historique de
conversation — pas de fichier dédié, contenu reproduit ici en substance
à chaque décision qui s'y réfère.

**Audit réel des 3 scènes** (lecture complète des 3 `.tscn`, pas une
estimation) : `gate_premiere`/`test_arena`/`outpost` partagent le même
schéma pauvre — `Backdrop` en `ColorRect` plat, `FarBackground`
(`Parallax2D`) ne répétant que 2 textures (`bg_ruin_arch`/
`bg_pillar_silhouette`) 3× chacune, et seulement 4 props uniques
(`prop_pillar`/`prop_rubble_warm`/`prop_brazier`/`prop_debris`)
dispersés par variation de position/flip sur les 14 instances de
`gate_premiere`. Incohérence trouvée en prime : `test_arena.tscn`
utilisait `floor_tileset.tres` (atlas 2 tuiles, aucune donnée de
terrain) alors que `gate_premiere`/`outpost` utilisent déjà
`floor_terrain.tres` (vrai `TerrainSet` à coins Wang) — même script
`arena_floor.gd` dans les 3, donc bascule directe sans risque de
compatibilité.

**Génération PixelLab** (10 `create_map_object`, budget mandat 300 —
10/300 consommés, journalisées dans `data/pixellab_usage.jsonl`) :
- 3 arrière-plans (vue `side`, 224px de haut, même famille d'échelle
  que `bg_ruin_arch`/`bg_pillar_silhouette`) : statue brisée, tour
  effondrée, bannière en lambeaux.
- 5 props de sol (vue `high top-down`, 32×32/32×40, même famille
  d'échelle que `prop_pillar`) : caisse en bois, idole de pierre, pied
  de torche, végétation, poteau de bannière.

**Vérification de palette par échantillonnage HSV réel** (script
Python ponctuel, comptage de pixels opaques par couleur dominante —
même méthode que le verrouillage de `terre.json` en début de session,
jamais à l'œil) : la bannière et les 5 props de sol tombent dans la
même famille de teinte (12-28°, terracotta/bois) que `prop_pillar.png`
— acceptés tels quels. La statue et la tour, en 1re génération,
échantillonnaient hue 228-286° avec jusqu'à 41% des pixels sous 7% de
valeur (violation mesurée de la règle Addendum C "jamais de bande à
0%/100%", et hors de la plage de teinte 250-330° déjà établie par les 2
arrière-plans existants) — **régénérées** (2 générations
supplémentaires, prompt explicitement corrigé vers "purple-brown, never
blue-grey or near-black, amber rim light"). v2 : hue 248-286°/sat
30-93%/val 11-35% — dans la plage de variation déjà réelle entre
`bg_ruin_arch` (ombre 250-266°) et `bg_pillar_silhouette` (326-330°),
bandes de valeur non extrêmes. Acceptées.

**Intégration réelle** (pas de génération orpheline) :
- `test_arena.tscn` : `floor_tileset.tres` → `floor_terrain.tres`
  (fix zéro-génération).
- Les 3 scènes reçoivent les nouveaux assets en positions non
  répétitives (jamais un simple flip d'un asset déjà placé à côté) :
  `gate_premiere` (scène la plus longue, 5 nouveaux arrière-plans + 5
  nouveaux props sur ses ~3900px), `outpost` (1 arrière-plan + 2
  props), `test_arena` (1 arrière-plan + 2 props).
- Capture réelle (`scripts/capture_headless.sh --mode=scene`,
  `gate_premiere.tscn`, 3 positions caméra) : tour effondrée et statue
  visibles en arrière-plan, teinte chaude cohérente une fois composée
  avec `AmbientWarmth`/le shader post-render existants ; nouveaux props
  au sol visibles, aucun chevauchement avec le décor existant.

**Vérification** : `scripts/run_gameplay_smoke_test.sh` 100% vert (76
checks, aucune régression — les scènes ne sont pas exercées par ce
test, mais les modules qu'il couvre — Player/HUD/pouvoirs — ne
dépendent d'aucune des 3 scènes modifiées). Export web régénéré
(`godot4 --headless --rendering-driver vulkan --export-release "Web"
docs/index.html`, précédé d'un `--import` pour cuire les 8 nouveaux
PNG) — `docs/index.pck`/`docs/index.html` à jour.

**Coût réel consommé** : 10 générations PixelLab (10/300 du budget
mandat, largement sous le plafond).

**Non fait / hors scope de cette phase** : pas de retouche des 4 props
déjà existants (mandat ne le demandait pas) ; pas de nouvelle
plateforme de parallaxe intermédiaire (mandat priorise sol/mur >
props > parallaxe lointaine > détail premier plan — le sol était déjà
correct sauf `test_arena`, et le parallaxe lointain a été enrichi mais
pas restructuré en plusieurs plans). Enchaîne sur Phase 2 (animation
Meshy des monstres) sans nouveau prompt, conformément à l'instruction
du mandat.

## 2026-08-22 — MANDAT AUTONOME v3 : Phase 2 (animation des monstres)

**État de départ vérifié** (jamais supposé) : `crawler_frames.tres`/
`brute_frames.tres` n'avaient que `idle`+`attaque`, chacun à UNE seule
frame statique — `ranged_frames.tres` avait en plus `mort` (6 frames).
Aucun des 3 n'avait de "marche" : le déplacement passait par le bob
procédural sinusoïdal de `enemy.gd` (`_update_visual_bob()`), un repli
documenté comme volontaire à l'intégration (Phase 1.1 MANDAT SUITE v2 :
"pas de cycle de marche animé — trop coûteux pour le prototype").

**Ranged — gratuit, retrouvé plutôt que régénéré** : le rig Meshy déjà
payé (`rig_task_id=01a024b4-...`, 5cr dépensés le 2026-08-21) inclut
marche+course de façon permanente (`meshy_rig` : "Walking/Running
animation included FREE"). `meshy_download_model` sur ce même
`task_id` (type `rigging`) a retourné les URLs `basic_animations.
walking_glb_url` directement — **0 crédit supplémentaire**, aucun appel
`meshy_animate`. GLB téléchargé, 6 frames échantillonnées régulièrement
sur l'action existante via Blender headless Cycles (même caméra/lumière
que idle/attaque : `cam_size=2.6`, `target_z=1.092`), quantifiées aux
réglages de lisibilité déjà établis (`--target_saturation=0.55
--dither_amount=0.0 --value_band_min=0.35`).

**Crawler/Brute — 0 crédit, poses à la main sur le rig manuel déjà
validé** : le rig auto Meshy avait échoué sur ces 2 postures (gotcha
déjà documenté, "estimateur conçu pour un bipède debout"), contournement
manuel Blender déjà en place (`crawler_final_rigged.glb`/
`brute_final_rigged.glb`, armatures 13/10 os). Nouveaux scripts
(`experiments/blender_capture/pose_walk_{crawler,brute}.py`) : 4 poses
clés à la main par monstre (Crawler : trot diagonal, front_L+back_R
avancent ensemble puis front_R+back_L ; Brute : marche bipède,
bras/jambe opposés) réutilisant exactement les noms d'os et le cadrage
déjà approuvés pour idle/attaque (aucun nouveau rig). Rendu Cycles
headless, quantifié à `--target_saturation=0.55` (réglages par défaut
sinon, identique à idle/attaque).

**Vérification par échantillonnage visuel réel** (pas supposé) : les
3 planches de contact (`contact_sheet.png` par monstre) montrent des
silhouettes nettement distinctes frame à frame — jambes qui alternent,
bras qui balancent, queue qui oscille (Crawler) — pas 4 copies de la
même pose.

**Câblage jeu** (`src/gameplay/enemy.gd`, `_update_visual_bob()`) :
joue "marche" en boucle si `sprite_frames.has_animation("marche")`
pendant `State.CHASE` à vélocité non nulle, retombe sur "idle" en
sortie de mouvement ; **le bob procédural n'est PAS supprimé** — il
reste le repli pour un futur archétype sans animation dédiée, même
discipline que `_play_visual_animation()` ailleurs dans ce fichier.

**Vérification** : `scripts/run_gameplay_smoke_test.sh` 76/76 vert
(inclut les 3 checks qui exercent le mouvement des monstres :
`crawler_chases_then_hits_player`, `brute_telegraphs_before_landing_a_
heavier_hit`, `ranged_retreats_to_preferred_range_then_hits_player_
with_projectile`). Capture réelle en jeu (`capture_headless.sh
--mode=scene`, `test_arena.tscn`, tick 3 après spawn) : le Crawler
affiche une pose de marche (jambe avant tendue, corps abaissé),
visuellement distincte de son idle — confirmé à l'écran, pas seulement
en test unitaire. Export web régénéré.

**Coût réel consommé (Meshy)** : 0 crédit ce mandat (866/866 restants,
inchangé) — le seul appel a été un `meshy_download_model` gratuit sur
une tâche déjà payée. Budget de 150cr entièrement disponible pour les
phases suivantes si nécessaire.

**Non fait / hors scope de cette phase** : pas de retouche de l'attaque
existante (déjà présente, mandat priorise marche > attaque > mort) ;
Crawler/Brute restent sans "mort" dédiée (seul Ranged en a une,
héritage Phase 1.2 MANDAT SUITE v2 — pas demandé par cette phase, qui
priorise explicitement la marche). Enchaîne sur Phase 3 (compétences
restantes) sans nouveau prompt, conformément à l'instruction du mandat.

## 2026-08-22 — MANDAT AUTONOME v3 : Phase 3, point d'attention (fissure Poing Belluaire)

**Corrigé, vérifié visuellement** : Poing Belluaire n'avait aucune couche
de fissure au sol malgré la référence archivée (`docs/references/
monstrification/coup_de_poing_monstrifie.png`, colonne "Assets - Effets",
case du milieu) qui en montre une nettement — écart identifié lors de
l'audit palette du début de session, laissé non corrigé à l'époque.

Ajout d'une couche `fractureLine` en contact/conséquence (`data/recipes/
power.poing_belluaire.cast.json`, ticks 20-34, `degradable: true`, même
raisonnement que `dustKick` sur Poing Tellurique : c'est la conséquence
de l'impact, pas le contact lui-même). **Aucune nouvelle couleur** :
`data/palettes/parasite.json` nommait déjà explicitement `fractureLine`
dans son rôle 2 ("brun-rouille profond") depuis la réécriture de palette
plus tôt cette session — l'écart n'était que dans cette recette.

Vérifié par exécution réelle, pas supposé : `run_vfx_recipe_smoke_test.sh`
(15/15 primitives dont fractureLine spawn/tick/cleanup sans erreur),
`run_gameplay_smoke_test.sh` (76/76, aucune régression sur les checks
Poing Belluaire existants), et une capture en jeu réel (`tools/
capture_scene.gd --mode=player_action`, nouveau `--active_power=`/
`--level=` ajoutés à cet outil de capture pour forcer le Pouvoir tiré au
hasard sans debugger headless — pas un changement de gameplay, un
paramètre de dev uniquement) : à tick 30, des segments de fissure brun
radiant depuis le point d'impact sont visibles à l'écran, distincts du
burst gris d'impactStar — correspond à la référence.

## 2026-08-22 — MANDAT AUTONOME v3 : Phase 3, Marée de Sable (Terre, Tier 2)

**Choix explicite** : parmi les 11 compétences manquantes, priorité à
l'ordre de déblocage verrouillé (tier le plus bas d'abord). Les 3 tier 1
existent déjà. Des 2 tier 2 restantes (Corbeau Pâle/Invocateur, Marée de
Sable/Terre), Marée de Sable choisie pour cette passe — même Classe que
Poing Tellurique déjà vivant (palette/archétype de départ partagés,
risque le plus bas pour une seule compétence livrée et vérifiée de bout
en bout, conformément à la consigne du mandat "une compétence terminée
vaut mieux que trois à moitié faites").

**Référence** (`docs/references/terre/maree_de_sable.png`) : "Une vague
de sable déferle sur une ligne devant Rank Zero, ralentissant et
entravant les ennemis touchés" (Tier 2, LIGNE, CONTRÔLE). 4 temps :
Préparation/Lancement/Déferlement/Fin.

**Nouvel archétype de cast `line_wave`** (aucun des archétypes existants
— arc de mêlée, coup frontal — ne correspond à "une vague qui voyage en
ligne droite") : `beamSegment`, seule primitive du registre déjà
documentée pour ce cas exact ("l'archétype de cast 'projection avant'...
un tir qui part du joueur en ligne droite", encore sans exemple concret
avant cette passe). `data/recipes/power.maree_de_sable.cast.json` :
converge (anticipation, le sable se rassemble) → beamSegment (core, la
vague voyage) → dustKick (contact, gicle au passage) → smokePuff
(conséquence, poussière qui retombe). Palette `terre` RÉUTILISÉE, 2
usages étendus (`ocre clair`→beamSegment, `poussière pâle`→smokePuff)
sans nouvelle couleur — la référence montre exactement ce sable déjà
mesuré dans cette palette.

**Nouveau : ciblage en LIGNE** (`Targeting.enemies_in_line()`,
`src/gameplay/targeting.gd`) — distinct du cône `enemies_in_arc()` déjà
utilisé par Bras-Faux/Poing Tellurique : une ligne garde une largeur
CONSTANTE sur toute sa portée (projection avant/latérale sur `facing`/
sa perpendiculaire), un cône s'élargit avec la distance. Premher usage
réel de cette forme dans le jeu.

**Nouveau : ralentissement** (`Enemy.apply_slow()`, `src/gameplay/
enemy.gd`) — première mécanique de "contrôle" du jeu, générique plutôt
que spécifique à cette seule compétence (état à expiration par compte
de ticks, jamais cumulatif — le plus récent écrase toujours l'effet en
cours). Consommé dans `_chase_velocity()` (multiplie `stats.move_speed_px`).

**Gameplay** (`src/gameplay/player.gd`) : `_start_maree_de_sable()`/
`_advance_maree_de_sable()`/`_try_hit_maree_de_sable()` — même
construction 3 phases que Poing Tellurique (aucun déplacement
automatique). Portée 90px (vs 44px pour un poing — "une vague voyage"),
demi-largeur 15px, dégâts 8 (le plus faible des 4 compétences vivantes —
Tier CONTRÔLE, pas dégâts), ralentissement ×0,5 pendant 90 ticks
(1,5s). Enregistrée dans `IMPLEMENTED_SKILL_HANDLERS`/
`IMPLEMENTED_SKILL_COOLDOWN_GETTERS` (slot "power2", tier 2 de Terre —
même mapping que Bras-Faux/tier 2 de Monstrification).

**Vérification** : 4 nouveaux checks (`tools/smoke_test_gameplay.gd`,
`_check_maree_de_sable()`) — démarrage+anim, ligne touche la cible dans
l'axe MAIS épargne une cible décalée latéralement (au-delà de la
demi-largeur) ET une cible au-delà de la portée (2 angles distincts,
jamais testés ensemble avant sur un cône), ralentissement appliqué
uniquement à la cible touchée, fin+cooldown. `run_gameplay_smoke_test.sh`
80/80 vert. Capture réelle (`capture_scene.gd --mode=player_action
--action=power2 --active_power=terre --level=3`) : ligne de segments
ocre visible s'étendant du joueur, distincte du burst blanc de contact —
confirme le rendu "ligne qui voyage" à l'écran, pas seulement en test.

**Non fait** : Corbeau Pâle (Invocateur, tier 2) et les 8 compétences
restantes (tiers 3-5) — hors budget de cette session, aucun blocage
technique identifié pour la suite (même méthode directement
réutilisable). Enchaîne sur Phase 4 (housekeeping) sans nouveau prompt.

## 2026-08-22 — MANDAT AUTONOME v3 : Phase 4 (housekeeping)

**Worklog archivé** : `docs/worklog.md` dépassait 6300 lignes (6657
exactement). Split par date à une frontière de section propre (fin de
"Phase 2.3+2.4" MANDAT SUITE v2, ligne 5256) : les 51 premières entrées
datées (2026-08-18 → 2026-08-21 inclus) déplacées telles quelles, sans
réécriture, dans `docs/worklog-archive-2026-08-18-a-2026-08-21.md`
(5259 lignes). `docs/worklog.md` ne garde que les 19 entrées du
2026-08-22 (1425 lignes) + un index en tête résumant la période
archivée et expliquant la règle de split pour la prochaine fois.
Contenu total inchangé (6684 lignes réparties sur 2 fichiers vs 6657
avant, différence = les quelques lignes d'index ajoutées).

**STATUS.md — écart réel trouvé et documenté** : le mandat demandait de
"compacter STATUS.md pour refléter l'état actuel" en supposant son
existence. Vérifié par recherche exhaustive (`find`/`ls`) : **ce fichier
n'existait nulle part dans ce dépôt**, ni à la racine ni sous `docs/` —
aucune trace non plus dans `docs/worklog.md` d'une référence à un tel
fichier. Pas une contradiction entre deux sources (rien à trancher),
juste une prémisse fausse du mandat sur l'état du dépôt. Décision (choix
d'implémentation, pas de contenu narratif inventé) : créer `docs/
STATUS.md` neuf plutôt que chercher un fichier de remplacement supposé
— contenu factuel uniquement (tableau des 5/15 compétences réellement
implémentées, état monstres/monde/pipeline, budgets consommés,
prochaine priorité), aucune invention, tout dérivé de ce qui est déjà
vrai dans le code/les recettes/les journaux d'usage.

**Vérification** : `run_gameplay_smoke_test.sh` 80/80 vert (changement
100% documentation, aucun fichier de code touché — vérifié quand même
par discipline, jamais supposé "sans risque" sans le confirmer).

## 2026-08-22 — MANDAT AUTONOME v3 : Rapport final

Milan indisponible pour arbitrer cette session (mandat explicite,
autonomie totale dans les budgets fixés). 4 phases exécutées dans
l'ordre imposé, chacune commitée/poussée séparément.

### Ce qui est vraiment fait et vérifié, phase par phase

**Phase 1 (monde/décor)** — TERMINÉ. Audit réel des 3 scènes (flat-
color backdrops, parallaxe ne répétant que 2 textures, 4 props uniques
seulement). 8 assets PixelLab générés (statue/tour/bannière en
arrière-plan + caisse/idole/torche/végétation/poteau en props de sol),
2 régénérés après échantillonnage HSV réel ayant mesuré une palette
hors plage (corrigé). Intégrés dans les 3 scènes en positions non
répétitives. Fix bonus : `test_arena.tscn` uniformisé sur
`floor_terrain.tres` (comme les 2 autres scènes). Vérifié : smoke test
76/76, capture en jeu réel (3 angles caméra). Coût : 10/300 générations
PixelLab.

**Phase 2 (animation des monstres)** — TERMINÉ. Les 3 monstres avaient
un bob procédural, jamais de vraie marche. Ranged : marche+course déjà
incluses gratuitement dans son rig Meshy payé — récupérées via
`meshy_download_model`, 0 crédit. Crawler/Brute : 4 poses de marche à
la main sur leur rig manuel Blender déjà validé (le rig auto Meshy
échoue sur leurs postures). Câblé dans `enemy.gd` (`_update_visual_bob`
préfère "marche" si l'animation existe, repli bob procédural conservé
pour un futur archétype sans anim dédiée). Vérifié : smoke test 76/76
(dont les 3 checks qui exercent le mouvement des monstres), capture en
jeu réel confirmant une pose de marche distincte de l'idle à l'écran.
Coût : 0 crédit Meshy (866/866 restants).

**Phase 3 (compétences)** — PARTIEL, honnêtement. Deux livrables réels :
(1) fissure au sol manquante sur Poing Belluaire (écart identifié lors
de l'audit palette en début de session) corrigée — couche `fractureLine`
ajoutée, aucune nouvelle couleur (la palette la nommait déjà), vérifié
par smoke test + capture réelle (segments de fissure visibles). (2)
Marée de Sable (Terre, Tier 2) implémentée de bout en bout : nouvel
archétype de cast "ligne qui voyage" (`beamSegment`), nouveau ciblage en
ligne (`Targeting.enemies_in_line()`), nouvelle mécanique de
ralentissement générique (`Enemy.apply_slow()`), 4 nouveaux checks smoke
test, capture réelle confirmant le rendu. **10 des 11 compétences
manquantes restent non implémentées** (Corbeau Pâle, Poing du Colosse,
Œil Sans Regard, Serpent Creux, Carapace, Effondrement, Fissure
Éruptive, Mâchoire, Forme Bestiale, Pattes de Chasse) — choix délibéré
de livrer une compétence complète et vérifiée plutôt que plusieurs
ébauches, conformément à la consigne explicite du mandat. Aucun blocage
technique : la méthode (VFX recipe → gameplay → mécanique générique si
besoin → smoke test dédié → capture réelle) est directement
réutilisable pour les 10 restantes, dans l'ordre de tier verrouillé.

**Phase 4 (housekeeping)** — TERMINÉ. `docs/worklog.md` (6657 lignes)
archivé par période (2026-08-18 → 2026-08-21 dans un fichier séparé,
2026-08-22 conservé, 1425 lignes). `docs/STATUS.md` — écart réel trouvé
(le fichier n'existait pas du tout, contrairement à ce que le mandat
supposait) — créé neuf avec un état factuel du dépôt.

### Ce qui est bloqué, et ce qu'il faudrait pour débloquer

Rien n'est bloqué techniquement. La seule limite rencontrée sur toute
la session est le **temps/budget de cette session elle-même** pour la
Phase 3 (10 compétences sur 15 restent à écrire). Aucune décision de
Milan n'est nécessaire pour les 10 compétences restantes : chacune a
déjà (a) un sprite de référence archivé, (b) un tier verrouillé, (c)
une méthode éprouvée deux fois cette session (Poing Belluaire fix,
Marée de Sable). Un point RÉEL à trancher par Milan un jour (pas
bloquant pour continuer les compétences) : aucun des 15 combats n'a
encore de sprite Godot dédié (tous utilisent "coup1"/"coup2"/"coup3"
en placeholder) — pas un problème pour cette session, mais un vrai
manque d'identité visuelle qui grandira à mesure que plus de
compétences existent sans art propre.

### Coût réel consommé (mesuré, pas estimé)

- PixelLab : 10 générations / 300 (Phase 1 uniquement).
- Meshy : 0 crédit / 150 (Phase 2 — récupération gratuite d'un rig déjà
  payé, aucun nouvel appel facturé).

### Recommandation pour la prochaine session

Continuer Phase 3 dans l'ordre verrouillé : Corbeau Pâle (Invocateur,
Tier 2) en premier — référence déjà archivée
(`docs/references/invocateur/corbeau_pale.png`), même méthode
directement réutilisable. Après les 5 compétences Tier 2 restantes du
même ordre de priorité (tiers bas = plus visibles), envisager l'art
dédié par compétence (point non bloquant relevé ci-dessus) comme
chantier séparé, une fois plus de compétences vivantes pour juger si le
partage "coup1/coup2/coup3" reste lisible ou commence à confondre les
Pouvoirs entre eux.

## 2026-08-23 — Agent Décor test_arena : vérification du rôle réel AVANT retouche (verdict : hors scope, aucune retouche)

Mandat : traiter `scenes/gameplay/test_arena.tscn` comme `outpost`/
`gate_premiere` (PointLight2D réels, props PixelLab, vérification HSV)
**mais seulement si la scène est réellement vue par un joueur** —
vérifier le rôle réel en premier, ne pas dépenser de budget par défaut.

**Enquête (code, pas supposition)** :
- `grep -rn "test_arena" --include="*.gd" --include="*.tscn" .` :
  aucune occurrence dans un chemin de transition de scène. Les seuls
  hits `.gd` sont des commentaires de doc (`camera_director.gd`,
  `ground_decal.gd` — "Player.tscn partagé par gate_premiere/
  test_arena/outpost", pas un `load()`/`change_scene`).
- Tous les appels réels de `get_tree().change_scene_to_file(...)` du
  dépôt (`src/world/gate_entrance.gd`, `src/world/gate_premiere.gd`) :
  seulement `outpost.tscn` ⇄ `gate_premiere.tscn`. `gate_entrance.gd`
  a un `@export var target_gate_scene`, mais sa valeur câblée dans
  `outpost.tscn` (`scenes/gameplay/outpost.tscn:147`) est en dur
  `"res://scenes/gameplay/gate_premiere.tscn"` — aucune Gate, aucun
  menu, aucun sélecteur de niveau ne pointe vers `test_arena.tscn`.
  `run/main_scene` de `project.godot` = `outpost.tscn`.
- Seules occurrences du chemin exact `res://scenes/gameplay/
  test_arena.tscn` dans tout le dépôt : `.godot/editor/
  project_metadata.cfg` sous `[recent_files]` (liste des scènes
  récemment ouvertes **dans l'éditeur Godot** — métadonnée d'IDE, zéro
  rapport avec le jeu en exécution) et l'export web compilé
  (`docs/index.pck`, qui embarque toutes les scènes du projet par
  défaut, reachable ou non — n'implique pas une exposition joueur).
  Aucun script de capture/smoke test dans `scripts/` ne référence
  `test_arena` par nom (le smoke test lance `tools/
  smoke_test_gameplay.tscn`, une scène de mock séparée).
- Confirme et recoupe deux constats déjà posés par des agents
  précédents sur ce même dossier : `docs/worklog-archive-2026-08-18-
  a-2026-08-21.md:3916` ("`test_arena.tscn` n'est référencée nulle
  part comme cible de transition, laissée de côté") et `docs/
  STATUS.md:20` qui la catégorise explicitement `test_arena (bac à
  sable)` face à `gate_premiere` (parcours complet) et `outpost` (hub).

**Verdict** : `test_arena.tscn` est une scène de test technique interne
— un bac à sable créé pour l'itération développeur/QA (composition
Player + ennemis à distances contrôlées), jamais instanciée par un
menu, un hub, une Gate ou un sélecteur accessible en jeu, et absente de
tout chemin `change_scene_to_file()` réel. Un vrai joueur en conditions
normales ne peut pas l'atteindre. Note pour mémoire : des passes
antérieures (parallaxe, uniformisation du sol `floor_terrain.tres`,
recherche d'éclairage) l'ont néanmoins touchée par le passé, mais
toujours dans le cadre de passes systémiques sur les 3 scènes
ensemble (jamais un mandat dédié "décor test_arena" comme celui-ci) —
ça ne change pas le verdict d'accessibilité joueur ci-dessus.

**Décision** : aucune retouche visuelle. Pas de `PointLight2D`
supplémentaire, pas de génération PixelLab, pas de capture avant/après,
pas de mesure `validate_pixels.py` — appliquer le traitement `outpost`/
`gate_premiere` ici serait du travail décoratif sur une scène que
personne ne voit, contraire à la consigne explicite du mandat
("inutile de la peaufiner visuellement... dis-le clairement plutôt que
de dépenser du budget PixelLab dessus par défaut").

**Coût réel consommé** : 0 crédit PixelLab, 0 crédit Meshy (solde non
consulté — non applicable, aucune dépense envisagée après l'enquête).

**Fichiers modifiés** : uniquement cette entrée de worklog. Aucun
fichier de scène (`test_arena.tscn` ou autre) touché.

## 2026-08-23 — Agent Poing Tellurique : pose dédiée de frappe au sol (mandat "polish complet")

Mandat : les rounds précédents ont retravaillé le VFX de Poing
Tellurique (`groundRing`, `dustKick`, `impactStar`) mais jamais le
geste du personnage — `_start_poing_tellurique()` jouait encore
`"coup1"` (le 1er coup du combo à mains nues, un jab horizontal), un
placeholder documenté comme tel dans le code depuis le début. Écart
confirmé par comparaison directe avec `docs/references/terre/
poing_tellurique.png` (4 temps : préparation, frappe qui descend,
impact au sol, dissipation) — un jab devant soi n'a aucun rapport avec
un coup qui frappe le sol.

**Pipeline (1 génération PixelLab, acceptée dès le 1er essai)** :
`get_character` d'abord pour vérifier le character_id RÉELLEMENT en
jeu (`8596a4ad-...`, Cendre_v3c sans cape — même piège documenté 2 fois
cette session sur Bras-Faux/Poing Belluaire, évité ici en amont).
Contrairement à ces deux pouvoirs, Poing Tellurique ne transforme
aucun membre — c'est une POSE, pas une mutation — donc `animate_character`
mode v3 DIRECTEMENT sur l'état de base "Idle" (même construction que
coup1/coup2/coup3/dash/mort), pas de `create_character_state`. Prompt
avec exclusions négatives explicites (pas d'arme/lueur/traînée),
"downward ground pound", 6 frames sud. Résultat : séquence lisible
(debout → bras qui s'arment → accroupissement profond → poings au sol
avec éclats de débris visibles sur le sprite lui-même → remontée),
aucune hallucination, aucun re-roll nécessaire.

**Cuisson (0 appel PixelLab supplémentaire)** : intégration sur le
canvas partagé Cendre (64×64, ancrage pied (32,61)), script ponctuel
qui MERGE dans le manifeste existant (même contournement que Bras-Faux/
Poing Belluaire — `cook_character_frames.py` écrase tout le manifeste
s'il n'est appelé qu'avec un seul `--anim`). Deux bugs trouvés et
corrigés en route : (1) `foot_anchor()` du pipeline existant (bande
centrale 35 % du bbox, conçue pour ignorer une cape qui déborde) se
trompe sur cette pose précise — stance large "prêt au combat", pieds
écartés au-delà de la bande, qui tombe alors dans l'entrejambe (y=79)
au lieu des pieds réels (y=95) ; corrigé en utilisant directement
`bbox_bottom-1`, fiable ici car aucune cape (supprimée du jeu) et les
pieds restent au même niveau au sol sur les 6 frames (écart max 2px).
(2) Facteur d'échelle recalculé après ce correctif : 53/78 ≈ 0,68
(mesuré sur frame0 contre `idle_south` cuit), même classe de correction
que le facteur Bras-Faux (51/79) — sans lui, la tête sortait tronquée
en haut du canvas sur la pose debout.

**Câblage tick-exact** (`POING_TELLURIQUE_FRAME_TICK_BOUNDS`, même
discipline que `BRAS_FAUX_FRAME_TICK_BOUNDS`/`POING_BELLUAIRE_
FRAME_TICK_BOUNDS` ajoutés cette même session par des agents parallèles
sur ce même fichier) : `play()`+`pause()`+`frame=0` puis pilotage
manuel de la frame par tick cumulé, JAMAIS la lecture fps autonome
d'`AnimatedSprite2D`. Bornes calées pour que la frame d'impact (poings
au sol + éclats) bascule PILE au tick global 19 (ANTICIPATION 18 +
RELEASE tick1 = contact), aligné avec la fenêtre "contact" 18-22
d'`impactFlashFrame` de la recette VFX déjà en place — le point
d'impact du sprite correspond maintenant à où l'anneau/les éclats
apparaissent, pas un hasard de fps.

**Vérifié** : smoke test gameplay (76 checks, `all_pass=true`), dont
`poing_tellurique_input_starts_state_and_plays_dedicated_anim` (renommé
depuis `plays_placeholder_anim`). Capture de vérification 6 temps
(t=3/8/16/19/30/40) en jeu réel, comparée côte-à-côte à la planche de
référence, committée dans `captures/verification/
2026-08-23-poing-tellurique-pose-dediee.png` — verdict honnête : le
geste lit clairement comme "frappe le sol" (accroupissement net, mains
qui descendent, contact avec éclats), pas un jab légèrement modifié.
Écart mineur restant assumé : la planche montre des blocs de terre
arrachés au moment de l'impact que le sprite lui-même ne dessine pas
(compensé par la couche VFX `impactStar`/`dustKick` déjà en place,
pas par le personnage) — jugé suffisant, pas retenté (discipline
anti-reroll-infini).

**Coordination multi-agents (réel, pas hypothétique)** : ce round a
vu au moins 3 autres agents éditer les MÊMES fichiers partagés
(`player.gd`, `cendre_frames.tres`, `cendre_frames_cooked.json`,
`smoke_test_gameplay.gd`) en temps réel dans le même répertoire de
travail — un vrai conflit de fusion a été rencontré et corrigé en
direct (un `}` manquant dans `cendre_frames.tres` après une écriture
concurrente sur la même fin de fichier), et une passe complète de
"revert HEAD puis ré-application" a été nécessaire deux fois pour
isoler proprement les changements avant de committer. L'entrée
`poing_tellurique` de `cendre_frames.tres`/le manifeste a fini par être
absorbée dans le commit d'un autre agent (`7624ba9`, effet de bord
d'un working tree partagé) avant que ce commit-ci ne parte — ce
commit ne retouche donc que ce qui restait réellement scopé Poing
Tellurique : `player.gd` (bloc Poing Tellurique uniquement, diff
vérifié ligne par ligne), `smoke_test_gameplay.gd` (1 check renommé),
le log PixelLab, les 6 PNG cuits et la capture de vérification.

**Coût réel consommé** : 1 génération PixelLab (`animate_character`,
1478/2000 générations restantes avant travail, aucun appel Meshy).

**Fichiers modifiés** : `src/gameplay/player.gd` (bloc Poing
Tellurique : `POING_TELLURIQUE_FRAME_TICK_BOUNDS`, `_start_poing_
tellurique()`, `_advance_poing_tellurique()`, `_poing_tellurique_
global_tick()`, `_poing_tellurique_frame_for_tick()`, `_end_poing_
tellurique()` inchangé), `tools/smoke_test_gameplay.gd` (1 check
renommé), `data/pixellab_usage.jsonl` (2 entrées), `assets/processed/
sprites/cendre/poing_tellurique/{0..5}.png`, `captures/verification/
2026-08-23-poing-tellurique-pose-dediee.png`. `assets/processed/
sprites/cendre/cendre_frames.tres` et `assets/manifests/
cendre_frames_cooked.json` NON dans ce commit (déjà absorbés par un
commit parallèle, cf. note coordination ci-dessus) mais leur contenu
Poing Tellurique est identique à ce qui a été vérifié ici.

---

## 2026-08-23 — Agent dédié Marée de Sable : geste de Cendre au lancement + retour visuel du ralentissement

Mandat "polish complet" ciblé sur 2 écarts jamais traités pour Marée de
Sable (Terre, Tier 2) : le geste de Cendre au temps 2 "Lancement" de la
planche (`docs/references/terre/maree_de_sable.png`) et le ressenti
visuel du ralentissement infligé aux ennemis touchés.

**Point 1 — Geste "Lancement" : placeholder confirmé et corrigé.**
Lecture de code + capture tick-par-tick avant correctif
(`_start_maree_de_sable()` jouait `"coup1"`, le jab générique du combo
à mains nues — commentaire du code le confirmait déjà explicitement)
ont confirmé l'écart : "coup1" est un jab de profil resserré, aucun
rapport avec la planche (stance basse très écartée, un seul bras tendu
droit devant, sable qui jaillit de la main). Pipeline : character_id
Cendre_v3c vérifié EN JEU (`8596a4ad`, via `get_character` avant tout
appel — piège cape/ancien personnage déjà documenté sur ce dossier,
évité en amont) → `animate_character` mode v3 directement sur l'état
de base (pas de `create_character_state` : Marée de Sable ne
transforme aucun membre, contrairement à Bras-Faux/Poing Belluaire) →
6 frames sud, acceptées dès le 1er essai (aucune arme/lueur
hallucinée ; un voile pâle poussiéreux apparaît à la main sur les 2
dernières frames, lu comme le début du jet de sable annoncé par le
prompt, cohérent avec la planche). 2 bugs de cuisson trouvés et
corrigés avant tout commit : (a) bande de recherche du pied par défaut
(35% du bbox) tombait dans l'écart entre les deux bottes sur les 6
frames (stance écartée dès la 1ère frame) — élargie à 100%, vérifié
qu'aucune frame ne porte de tissu qui traînerait sous les bottes
(personnage R3 sans cape) ; (b) une fois le pied correctement ancré,
la frame la plus haute dépassait le sommet du canvas partagé 64×64
(tête rognée) — facteur d'échelle LANCZOS 53/79 ≈ 0,671 mesuré et
appliqué uniformément aux 6 frames, même classe de correctif que
Bras-Faux/Poing Belluaire/Poing Tellurique. Pilotage tick-exact
(`MAREE_DE_SABLE_FRAME_TICK_BOUNDS`, même discipline que ces 3
pouvoirs — jamais la fps autonome d'AnimatedSprite2D qui désynchronise
la pose affichée du contact mécanique) : la frame 3 (bras tendu en
extension complète, pose "Lancement") couvre la fin de l'ANTICIPATION
ET le tick de contact réel. Verdict honnête : la silhouette lit
clairement "stance basse écartée + poussée d'un bras" à l'écran,
nettement distincte du jab de profil resserré du placeholder — écart
réel avec la planche : le détail fin (doigts écartés, texture du
sable qui jaillit précisément de la paume) se perd à l'échelle réelle
du jeu (sprite ~35×55px), lisible seulement en zoomant sur les frames
sources elles-mêmes, pas un défaut du contenu généré mais une limite
de résolution d'affichage déjà documentée sur les autres pouvoirs à
sprite dédié cette session.

**Point 2 — Ralentissement : aucun retour visuel confirmé et corrigé.**
Confirmé par lecture de code : `Enemy.apply_slow()` change bien
`_slow_multiplier`/`_slow_ticks_remaining` (lu par `_chase_velocity()`
pour la vitesse réelle), mais rien à l'écran ne le montrait — un
ennemi ralenti était indiscernable d'un ennemi normal sans mesurer sa
vitesse de déplacement à l'œil. Réutilise le seul mécanisme de teinte
déjà câblé sur `Enemy` (`self_modulate`/`Polygon2D.color`, déjà
utilisé pour le pulse blanc du télégraphe d'attaque) plutôt que
d'inventer un 2e système : teinte ocre clair (`SLOW_TINT_COLOR`,
HSV 40°/45%/70% — la couleur "contact" déjà verrouillée dans
`data/palettes/terre.json`, aucune couleur nouvelle introduite, palette
non modifiée) mélangée à 65% par-dessus la couleur de base,
recalculée à chaque tick hors TELEGRAPH (`_reset_visual_color()`,
étendu pour composer proprement avec le pulse de télégraphe plutôt que
de l'écraser). Vérifié par un nouveau check smoke test
(`maree_de_sable_slow_has_visible_tint_on_hit_target_only`) ET par
capture réelle avant/après (couleur mesurée `(0.805, 0.387, 0.600)` vs
base `(1, 0, 1)` sur le mannequin générique — écart net et lisible).

**Incident de coordination réel (working tree partagé, même constat
que Poing Tellurique/Bras-Faux/Gueule Vide documenté plus haut) :**
entre la 1ère cuisson/merge de `maree_de_sable` (manifeste +
`cendre_frames.tres`, vérifiés à 27 animations) et la vérification
suivante, un `git reset`/checkout concurrent d'un autre agent a remis
`enemy.gd`, la section Marée de Sable de `player.gd` et le check dédié
de `smoke_test_gameplay.gd` à l'état HEAD — perte silencieuse de tout
le code non encore commit, découverte en relançant le smoke test
(`"anim":"coup1"` au lieu de `"maree_de_sable"`). Le manifeste/`.tres`
ont survécu (déjà absorbés par le commit d'un autre agent avant le
reset). Le code a dû être entièrement réécrit à l'identique (aucune
perte de contenu, seulement de temps) puis re-vérifié
(`all_pass:true`) avant tout commit cette fois, sans fenêtre
d'exposition supplémentaire laissée ouverte entre vérification et
commit.

**Coût réel consommé** : 1 génération PixelLab (`animate_character`,
1478/2000 restantes avant travail), 0 crédit Meshy.

**Fichiers modifiés** : `src/gameplay/player.gd`
(`MAREE_DE_SABLE_FRAME_TICK_BOUNDS`, `_start_maree_de_sable()`,
`_advance_maree_de_sable()`, `_maree_de_sable_global_tick()`,
`_maree_de_sable_frame_for_tick()`), `src/gameplay/enemy.gd`
(`SLOW_TINT_COLOR`/`SLOW_TINT_STRENGTH`, `_slow_tinted_color()`,
`_pulse_telegraph_color()` étendu, `_reset_visual_color()` étendu +
appelée chaque tick hors TELEGRAPH), `tools/smoke_test_gameplay.gd`
(1 check renommé + 1 nouveau check teinte), `data/pixellab_usage.jsonl`
(4 entrées), `assets/processed/sprites/cendre/maree_de_sable/{0..5}.png`,
`assets/source/pixellab/cendre/animations/maree_de_sable/{0..5}.png`,
`captures/verification/2026-08-23-maree-de-sable-lancement-avant-apres.png`,
`captures/verification/2026-08-23-maree-de-sable-ralentissement-teinte-avant-apres.png`.
`assets/manifests/cendre_frames_cooked.json` et
`assets/processed/sprites/cendre/cendre_frames.tres` NON dans ce
commit (déjà absorbés par le commit `7624ba9` d'un autre agent avant
l'incident de coordination ci-dessus) mais leur contenu Marée de Sable
est identique à ce qui a été vérifié ici. `data/palettes/terre.json`
lu (couleur "contact" réutilisée telle quelle pour la teinte), NON
modifié.

---

## 2026-08-24 — MANDAT "fluidité" (Partie 2, couche code — indépendante
## de tout pipeline d'asset) : buffer d'input + fenêtre d'annulation
## généralisés, smear procédural sur dash/esquive, diagnostic complet
## (et clôture) du bug de la "tranche écrasée"

**Contexte** : chantier distinct du mandat Cendre (Partie 1, ci-dessus)
— zéro génération PixelLab/Meshy, travail de code pur sur
`src/gameplay/player.gd`/`animation_composer.gd`/`tools/
smoke_test_gameplay.gd`/`tools/capture_scene.gd`. Objectif : un niveau
de fluidité type studio (buffer d'input, fenêtres d'annulation, smear)
qui marche identiquement avec les assets Cendre actuels, plus la
clôture du bug de la "tranche écrasée" en attente depuis le Round 4.

### Buffer d'input + fenêtres d'annulation — généralisé à 4 des 5
### compétences dédiées (Bras-Faux, Poing Belluaire, Poing Tellurique,
### Marée de Sable), Gueule Vide traitée comme exception documentée

L'embryon existant (`_attack_queued`/`CHAIN_WINDOW_TICKS`, combo de
base seulement) a été ÉTENDU, pas recréé : un nouveau
`_queued_power_slot`/`_queued_power_ticks_remaining`
(`INPUT_BUFFER_TICKS := 10`, "fenêtre courte, quelques ticks" du
mandat) retient un appui sur un slot de pouvoir pressé pendant
`_action_lock`, au lieu de le perdre en silence comme AVANT ce mandat
(chaque `_start_*()` de compétence retournait tôt sur son propre garde
`_action_lock`). Consommé soit par la fenêtre d'annulation de l'action
EN COURS (`_try_consume_queued_input()`, appelée depuis la RECOVERY de
chaque `_advance_*()` une fois son propre `<SKILL>_CANCEL_WINDOW_TICKS`
atteint), soit par un filet de sécurité en fin de `_physics_process()`
pour les actions sans fenêtre dédiée (dash/esquive/hurt).

Chaque compétence expose sa PROPRE constante de fenêtre d'annulation
(pas une réutilisation de `CHAIN_WINDOW_TICKS`, comme exigé par le
mandat), calibrée sur les `<SKILL>_FRAME_TICK_BOUNDS` existants (le
point où la dernière frame du geste est déjà tenue statique, donc rien
de visuel n'est coupé par une annulation dans cette fenêtre) :
- `BRAS_FAUX_CANCEL_WINDOW_TICKS := 12` (12/22 ticks de RECOVERY, ~55%)
- `POING_BELLUAIRE_CANCEL_WINDOW_TICKS := 10` (10/26, ~38% — délibérément
  plus court en proportion : c'est le coup le plus LOURD des 5, "le bon
  point diffère entre un coup léger et un coup lourd" du mandat)
- `POING_TELLURIQUE_CANCEL_WINDOW_TICKS := 12` (12/20, 60%)
- `MAREE_DE_SABLE_CANCEL_WINDOW_TICKS := 10` (10/18, ~55%)

Le combo de base garde son propre chaînage inter-tiers inchangé (coup1
→ coup2 → coup3), mais sa fenêtre de RECOVERY consulte AUSSI
`_queued_power_slot` (donc presser une compétence dédiée vers la fin
d'un coup du combo l'enchaîne aussi tôt que possible, même mécanisme
partagé via `_try_consume_queued_input()`).

**Gueule Vide, exception documentée et DÉLIBÉRÉE** : `_cast_gueule_vide()`
ne pose jamais `_action_lock` (décision d'un round précédent — "l'invocation
n'immobilise pas le joueur"). Première version de ce mandat mettait Gueule
Vide en file comme les 4 autres dès qu'`_action_lock` était vrai ailleurs
(ex. encore en RECOVERY d'un dash) — RÉGRESSION détectée par le smoke test
lui-même (`power1_input_spawns_gueule_vide_creature` repassait au rouge,
`spawned:false`) avant tout commit : Gueule Vide devenait bloquable par un
verrou étranger qu'elle n'avait jamais eu à respecter. Corrigé en excluant
explicitement `info["id"] == "gueule_vide"` du nouveau garde — elle reste
appelée directement, exactement comme avant ce mandat, jamais mise en
file pour SA PROPRE activation (elle reste en revanche une cible de file
valide : une AUTRE compétence peut s'annuler vers elle).

Vérifié par le smoke test (5 nouveaux checks, `tools/
smoke_test_gameplay.gd`) : `queued_power_does_not_fire_before_cancel_window_opens`,
`queued_power_fires_on_its_own_when_cancel_window_opens_and_ends_current_action_early`,
`power_fired_from_cancel_window_still_completes_and_unlocks_normally`
(scénario Bras-Faux → Poing Belluaire, buffer pressé peu avant
l'ouverture, démarrage automatique SANS second appui, Bras-Faux paie
quand même son cooldown), et `queued_power_input_expires_after_input_buffer_ticks_if_never_consumed`
/ `expired_buffer_lets_current_action_run_its_full_recovery_uninterrupted`
(scénario Poing Tellurique → Marée de Sable, appui TRÈS tôt dans
l'anticipation : le buffer expire avant l'ouverture de la fenêtre,
Poing Tellurique va au bout de sa RECOVERY complète, Marée de Sable ne
démarre jamais tout seul — preuve que ce n'est PAS une file illimitée).

### Smear frames procédurales — dash/esquive

`AnimationComposer.apply_motion_smear(sprite, velocity)` : étirement
non-uniforme le long de l'axe DOMINANT du mouvement (horizontal vs
vertical), calculé à CHAQUE tick depuis la vitesse RÉELLE du joueur
(`SMEAR_MAX_STRETCH := 0.35`, plafonné à `SMEAR_REFERENCE_SPEED_PX_S :=
900`), PAS depuis des keyframes pré-autorées comme `apply_squash()`
(qui reste inchangée, toujours utilisée par le combo). REMPLACE
l'ancienne impulsion squash figée du JSON pour dash/esquive (`x=1.3,
y=0.75` à tick4 dans `data/animation_composer/cendre.json`) : cette
valeur était aveugle à la direction réelle du dash (toujours un
étirement HORIZONTAL, fausse dès qu'on quitte l'axe est/ouest — un dash
vers le nord s'étirait quand même en largeur). Le smear, généré depuis
`_dash_direction`/`velocity`, reste correct pour les 8 directions.
Vérifié par le check existant `dash_applies_squash_and_lean_then_resets`
(toujours vert — le smear produit bien un scale non-identité pendant
MOVE puis un reset propre à `_end_dash()`), pas de nouveau check dédié
(le mécanisme est visuellement équivalent du point de vue de ce test :
un scale qui bouge puis qui revient à `Vector2.ONE`).

Root motion (mandat §, audit demandé) : dash/esquive utilisent une
courbe de déplacement ease-out CALCULÉE en code (`_ease_out_quad()`),
synchronisée tick-exact avec les phases ANTICIPATION/MOVE/RECOVERY de
l'action — PAS une lecture littérale d'un déplacement encodé dans les
pixels de l'animation (les frames de Cendre sont des poses fixes
pose-à-pose, PixelLab, sans donnée de mouvement par frame — ce concept
n'existe pas pour ce pipeline d'asset 2D). Le combo, lui, lit un
`root_motion` déclaratif (`start_tick`/`end_tick`/`distance_px`) depuis
`data/animation_composer/cendre.json`, mais CE JSON reste une valeur
choisie à la main par un humain, pas une mesure extraite des pixels —
la distinction "porté par l'animation vs appliqué en translation
séparée" du mandat ne s'applique donc pas littéralement à ce pipeline :
il n'existe PAS de sens où le déplacement pourrait être "lu depuis"
l'animation elle-même. Ce qui EST vrai et vérifié : le déplacement
(dash/esquive/combo) est toujours synchronisé sur les MÊMES bornes de
tick que le changement de pose visuelle (jamais deux horloges
séparées) — la sensation "ça glisse" signalée par le mandat, si elle
est réelle, n'a donc pas cette cause précise. Aucun changement de code
sur ce point (rien à corriger, le système actuel est déjà la meilleure
approximation possible de "root motion" pour ce pipeline) — documenté
honnêtement comme verdict plutôt que supposé.

### Bug de la "tranche écrasée" — diagnostiqué, PAS un bug (misdiagnostic
### d'un round précédent), clôturé avec preuve

Repro complet AVANT toute hypothèse (discipline demandée) :
- `bash scripts/capture_headless.sh --mode=power --power=gueule_vide
  --tick=35` (la CRÉATURE seule) → rendu normal, tendon en S, AUCUNE
  tranche écrasée. Élimine la créature elle-même comme source.
- `bash scripts/capture_headless.sh --mode=player_action --action=power1
  --active_power=invocateur --level=1 --tick=35` (le JOUEUR, exact
  contexte de la capture originale `2026-08-23-gueule-vide-4temps/
  after_tick35.png`) → reproduit EXACTEMENT le même visuel qu'à
  l'époque : Cendre apparaît comme une silhouette verticale étroite.

**Cause trouvée par élimination de code, pas par supposition** :
`grep -rn "\.scale" src/ scenes/` confirme qu'AUCUN code (avant ce
mandat) ne touche `sprite.scale` en dehors de `AnimationComposer.
apply_squash()`, elle-même appelée UNIQUEMENT depuis le combo
(coup1/2/3) et dash/esquive — JAMAIS depuis `_cast_gueule_vide()` ni
`gueule_vide.gd` (la créature). À tick 35, la fenêtre de geste
`GUEULE_VIDE_GESTURE_TICKS` (30 ticks) est déjà retombée : le joueur
est repassé sous `_handle_movement()`, qui joue l'anim directionnelle
réelle correspondant à `facing` — la capture (`player.facing =
Vector2.RIGHT`, forcé par l'outil de capture) affiche donc `idle_east`.
Comparaison directe `idle_south` (vue de face, large) vs `idle_east`
(vue de PROFIL, naturellement étroite — capture `--mode=character
--anim=idle_east`, les 4 frames) : `idle_east` est une silhouette de
PROFIL parfaitement proportionnée (tête/torse/bras/jambe visibles,
cohérents entre eux), PAS une distorsion — juste beaucoup plus fine que
la vue de face à laquelle l'œil est habitué. C'est du reste l'anim
qu'atteste déjà `tools/smoke_test_gameplay.gd`
(`combo_returns_to_idle_after_full_recovery_without_input` attend
explicitement `"idle_east"` en sortie de combo, même config de facing).

**Verdict : ce n'est PAS un bug de squash/stretch, ni un scale
résiduel, ni un bug de rendu — c'est la pose `idle_east` légitime (art
directionnel 8 directions, mandat production v1 §6), simplement
inhabituelle en isolation parce que la référence mentale de l'équipe
est la vue de face.** Le round précédent a mal identifié une capture
`idle_east` correcte comme "tranche écrasée" faute d'avoir comparé
avec `idle_south`. Côté Marée de Sable (tick 15, capture "AVANT" de
`2026-08-23-maree-de-sable-lancement-avant-apres.png`, qui utilisait
encore le placeholder "coup1" avant sa pose dédiée) : ce chemin de code
précis n'existe plus (remplacé par `_start_maree_de_sable()`/
`_advance_maree_de_sable()`, qui n'appellent JAMAIS `apply_squash`) —
reproduit `coup1` à tick15 avec le code actuel
(`--mode=player_action --action=attack --tick=15`) : pose de poing
normale, aucune tranche écrasée. Rien à corriger dans le code actuel
sur ce second point non plus ; l'ancien chemin qui aurait pu en être la
cause n'existe simplement plus.

Aucun changement de code n'a été fait pour "corriger" ce bug — il n'y
avait rien à corriger, seulement à démontrer par élimination que la
cause suspectée (squash/stretch) n'est structurellement pas
responsable, preuve à l'appui (voir captures ci-dessous).

### Smoke test

`bash scripts/run_gameplay_smoke_test.sh` → `"all_pass":true`, 86
checks (81 existants inchangés + 5 nouveaux sur le buffer/la fenêtre
d'annulation). Deux vrais bugs trouvés et corrigés PENDANT la mise au
vert (pas juste des ajustements de marge de test) : (1) la régression
Gueule Vide décrite plus haut, détectée par le check EXISTANT qui
repassait au rouge ; (2) un timing de test fragile sur les 2 nouveaux
checks (lecture d'état 0 tick après une pression, sans laisser à
`_physics_process()` le temps de la traiter) — corrigé en repassant à
des prédicats sur les compteurs de ticks AUTORITATIFS
(`_bras_faux_tick`, etc.) plutôt qu'un compte d'`await` manuel, même
discipline que le reste du fichier.

### Capture livrée

`captures/verification/2026-08-24-fluidite-buffer-cancel/` —
`contact_sheet_bras_faux_to_poing_belluaire.png` (grille 10 vignettes)
+ 6 frames brutes individuelles (`frame_t00_idle_baseline.png` …
`frame_t49_poing_belluaire_contact.png`), produites via un nouveau mode
`--action2=/--action2_tick=` ajouté à `--mode=player_action_sequence`
(`tools/capture_scene.gd`) — nécessaire pour capturer RÉELLEMENT
l'enchaînement (presser Bras-Faux, PUIS Poing Belluaire pendant que
Bras-Faux joue encore), pas deux captures isolées qui ne prouveraient
rien sur le mécanisme. Montre : Bras-Faux (t0-t18, contact "10/10" sur
2 ennemis), Poing Belluaire pressé à t22 alors que Bras-Faux tourne
encore (t22/t27 : rien ne démarre, silhouette Bras-Faux inchangée), la
bascule AUTOMATIQUE à l'ouverture de la fenêtre d'annulation (t29 :
silhouette Poing Belluaire déjà visible, SANS second appui visible dans
la séquence au-delà de celui de t22), puis Poing Belluaire jusqu'à son
propre contact (t49).

### Fichiers modifiés

`src/gameplay/player.gd` (`INPUT_BUFFER_TICKS`,
`<SKILL>_CANCEL_WINDOW_TICKS` ×4, `_queued_power_slot`/
`_queued_power_ticks_remaining`, `_try_activate_power_slot()`,
`_fire_queued_power_slot()`, `_try_consume_queued_input()`, RECOVERY de
`_advance_bras_faux/_poing_belluaire/_poing_tellurique/_maree_de_sable/
_combo` étendues, `_advance_dash/_advance_dodge` — smear procédural
remplace `apply_squash` sur les données "dash"), `src/gameplay/
animation_composer.gd` (`apply_motion_smear()`), `tools/
smoke_test_gameplay.gd` (5 nouveaux checks + leurs 2 appels dans
`_ready()`), `tools/capture_scene.gd` (`--action2`/`--action2_tick`/
`--active_power`/`--level` sur `--mode=player_action_sequence`),
`captures/verification/2026-08-24-fluidite-buffer-cancel/` (7
fichiers). Aucune génération PixelLab/Meshy — conforme au budget du
mandat.

### Ce qui reste (verdict honnête)

- Buffer/annulation généralisés à 4/5 compétences dédiées + combo ;
  Gueule Vide documentée comme déjà maximalement fluide par conception
  (aucune fenêtre à lui ajouter). Dash/esquive n'ont PAS reçu de
  buffer/fenêtre d'annulation (hors scope explicite du mandat, qui ne
  les nomme pas parmi les "5 compétences" — appui sur dash/esquive
  pendant un verrou reste un no-op silencieux, comme avant).
  Resserrement des `<SKILL>_CANCEL_WINDOW_TICKS` (actuellement
  généreux par choix) à trancher par Milan après test en jeu réel.
- Smear procédural implémenté sur dash/esquive uniquement (mandat
  demandait "au moins un mouvement rapide représentatif" — pas fait sur
  un coup à contact 2-3 frames, qui aurait nécessité une refonte plus
  large de `apply_squash`/`_advance_combo` pour rester dans le budget
  temps de ce mandat).
- Root motion : audité, verdict "déjà la meilleure approximation
  possible pour ce pipeline d'asset", aucun changement de code — voir
  section dédiée ci-dessus, pas un renvoi à plus tard mais une réponse
  définitive compte tenu du pipeline actuel (poses pose-à-pose sans
  donnée de mouvement par frame).
- Bug de la tranche écrasée : CLÔTURÉ, ce n'était pas un bug (art
  `idle_east`/`idle_west` légitime mal identifié par un round
  précédent). Aucune régression introduite, aucun correctif nécessaire.

## 2026-08-25 — CHANTIER A (reprise après coupure) : Pouvoir Invocateur,
## les 4 dernières compétences (Corbeau Pâle/Poing du Colosse/Œil Sans
## Regard/Serpent Creux) — audit, complétion smoke test, vérification

**Contexte** : reprise du travail d'un agent précédent tué par une
interruption système en plein Chantier A (mêmes 4 compétences). Rien
n'était perdu — tout sur disque, non commité — mais rien n'avait encore
été vérifié ni committé. Mission : auditer d'abord, compléter seulement
ce qui manquait.

### Audit — verdict : le travail trouvé était quasi COMPLET, pas une
### ébauche

Pour chacune des 4 compétences, déjà en place et fonctionnel avant cette
passe : sprites cuits (`assets/processed/sprites/<skill>/cast/`, 6
frames chacun) + `.tres` (`SpriteFrames`, anim `"cast"`, `loop=false`,
`speed=12.0`) ; geste de Cendre correspondant (`invocation_<skill>`, 6
frames) déjà intégré dans `cendre_frames.tres` ; scènes `scenes/
gameplay/powers/<skill>.tscn` + scripts `src/gameplay/powers/<skill>.gd`
— chacun avec sa propre timeline de créature (FRAME_TICK_BOUNDS à 6
paliers, `_frame_for_tick()`, `can_cancel()`/`cancel_cast()`,
`owner_death_policy` câblée via `set_owner_stats()`, ciblage réel via
`Targeting.enemies_in_line()`/`enemies_in_arc()` selon l'archétype :
Corbeau Pâle et Serpent Creux TRANSLATENT en ligne (comme prévu par la
fiche §6.2 pour Serpent Creux — portée 218px totale vs 144px pour
Gueule Vide, vérifié supérieure), Poing du Colosse frappe en AoE cercle
complet (`half_angle_deg=180`), Œil Sans Regard résout un rayon perçant
INSTANTANÉMENT à `BEAM_TICK` (pas de translation, à la différence des 2
premiers) ; recettes VFX (`data/recipes/power.<skill>.cast.json`) ;
`src/gameplay/player.gd` avait déjà les 4 `preload()`, les 4
`RecipeId`, les phases/ticks/cooldowns complets
(`<SKILL>_ANTICIPATION/RELEASE/RECOVERY/CANCEL_WINDOW/COOLDOWN_TICKS`,
`FRAME_TICK_BOUNDS`), les 4 `_cast_*()/_advance_*()/_end_*()/
_spawn_*_creature()`, ET l'enregistrement dans
`IMPLEMENTED_SKILL_HANDLERS`/`IMPLEMENTED_SKILL_COOLDOWN_GETTERS` — donc
déjà branchées sur le buffer d'input généralisé
(`_try_activate_power_slot()`/`_queued_power_slot`/
`_try_consume_queued_input()`, commit `1571521`) exactement comme les 5
compétences précédentes, sans aucun code supplémentaire à écrire pour
ce point. `godot4 --headless --import` propre, zéro erreur.

**Seul manque réel trouvé** : AUCUN check dans `tools/
smoke_test_gameplay.gd` pour ces 4 compétences (confirmé par grep —
zéro occurrence), et donc aucune capture de vérification. L'agent
précédent a été interrompu avant d'atteindre cette étape du mandat.
C'est le seul travail réellement effectué dans cette passe.

### Complété : 12 nouveaux checks (3 par compétence), `_check_corbeau_pale()`/
### `_check_poing_du_colosse()`/`_check_oeil_sans_regard()`/`_check_serpent_creux()`

Même patron que `_check_gueule_vide()` (créature séparée, pas une
timeline sur le Player comme Bras-Faux etc.) : démarrage+anim dédiée,
multi-cible (ligne pour Corbeau Pâle/Œil Sans Regard/Serpent Creux —
cible dans l'axe touchée, cible décalée latéralement ET cible hors
portée épargnées ; cercle complet pour Poing du Colosse — cible proche
touchée quelle que soit sa direction, cible hors rayon épargnée), fin de
vie de la créature + déverrouillage du joueur + armement du cooldown
qui bloque un nouveau cast.

**Écart de conception trouvé et corrigé PENDANT la mise au vert** (pas
supposé, découvert par un premier run qui cassait) : une première
version de ces checks copiait le "second appui immédiat pendant le
cast, doit rien spawner de plus" de `_check_gueule_vide()` — mais Gueule
Vide arme SON cooldown DÈS le cast (`_cast_gueule_vide()`,
`_power1_cooldown_remaining = POWER1_COOLDOWN_TICKS` immédiat), alors
que ces 4 compétences arment le leur seulement en fin de RECOVERY
(`_end_corbeau_pale()` etc., même patron que `_end_bras_faux()`) — un
second appui pendant le cast est donc légitimement mis en FILE par le
buffer généralisé et peut relancer la MÊME compétence une fois sa
fenêtre d'annulation ouverte ("dernier appui gagne", déjà exhaustivement
vérifié pour ce mécanisme par
`_check_input_buffer_fires_at_cancel_window()` sur Bras-Faux/Poing
Belluaire). Retester ce même scénario ici aurait dupliqué une
vérification déjà faite ET produit un second cast parasite pendant le
test (observé : `SCRIPT ERROR: Invalid call. Nonexistent function
'get_current_tick' in base 'Nil'` — le second cast queued avait fait
capoter la détection de la créature du test suivant). Retiré entièrement
ce sous-scénario des 4 nouveaux checks (il n'apporte rien que
`_check_input_buffer_fires_at_cancel_window()` ne couvre déjà) plutôt
que de le "réparer" en dupliquant la logique de fenêtre d'annulation.

**Incident de coordination réel, constaté en direct** : en cours de
diagnostic, des lignes `print("DEBUG_QUEUE_SLOT...")`/
`print("DEBUG_EFFONDREMENT_PRE...")` etc. sont apparues dans la sortie
du smoke test SANS que je les aie écrites — un autre agent (Terre,
`_check_effondrement()`/`_check_fissure_eruptive()`) modifiait
`src/gameplay/player.gd` et `tools/smoke_test_gameplay.gd` EN DIRECT
pendant cette session (ces lignes de debug avaient disparu au run
suivant). Conformément à la consigne, aucun de ces deux checks/leur
code associé n'a été touché — mes 4 nouveaux checks ont simplement été
replacés AVANT `_check_carapace()`/`_check_effondrement()`/
`_check_fissure_eruptive()` dans l'ordre d'appel de `_ready()` (au lieu
d'après), pour ne pas hériter d'un `_action_lock` potentiellement laissé
incohérent par le bug en cours de correction chez l'autre agent — un
réordonnancement, aucune ligne de leur code touchée.

### Vérification

`bash scripts/run_gameplay_smoke_test.sh` → **122 checks, mes 12
nouveaux tous verts** (`corbeau_pale_*`, `poing_du_colosse_*`,
`oeil_sans_regard_*`, `serpent_creux_*` — 3 chacun). **3 échecs
restants, hors scope** : `effondrement_*`/`fissure_eruptive_*` (Terre,
chantier concurrent, en cours de correction par un autre agent au
moment de ce run — voir incident ci-dessus) — non touchés, `all_pass`
global reste `false` à cause d'eux, documenté honnêtement plutôt que
maquillé.

### Captures

`captures/verification/2026-08-25-chantier-a-invocateur-4competences/`
— 16 frames brutes (`<skill>_t{1..4}_<label>.png`, `capture_scene.gd
--mode=player_action --active_power=invocateur --level=<palier>
--action=power{2..5}`, scale=4) + 4 planches de synthèse
(`<skill>_4temps.png`, 4 vignettes labellisées côte à côte). Verdict par
compétence (planche vs jeu, honnête) :
- **Corbeau Pâle** : silhouette de corbeau d'encre reconnaissable,
  ailes déployées, translation réelle visible entre Invocation/Chasse,
  dissipation en particules éparses en fin de séquence — conforme à
  "un corbeau d'encre jaillit et fonce à ras du sol".
- **Poing du Colosse** : masse rocheuse/poing géant qui se matérialise
  (anneau de télégraphe visible), impact AoE confirmé par les 2
  nombres de dégâts "20/20" simultanés sur les 2 cibles de test —
  conforme à "s'abat avec une force écrasante".
- **Œil Sans Regard** : globe/œil violet flottant (décalage vertical
  visible dès l'Ouverture), segment de rayon visible au tick de tir —
  conforme à "un œil s'ouvre et projette un rayon", quoique le rayon
  capturé sur ce tick précis soit court (bayon en cours de résolution,
  pas encore à pleine longueur) — représentatif mais pas le
  "meilleur" instant du rayon, accepté (montre bien le mécanisme).
- **Serpent Creux** : silhouette de serpent segmenté, gueule ouverte
  visible en Attaque, cohérent avec "un serpent se détend en ligne
  droite" — le plus proche visuellement de sa planche des 4.

Aucune retouche demandée par ces captures — les 4 assets déjà en place
(travail de l'agent précédent) rendent correctement, rien à régénérer.

### Coût PixelLab réel dépensé PAR CETTE PASSE

**0 crédit** — aucune génération PixelLab ni Meshy : tous les sprites/
gestes/manifestes existaient déjà (travail de l'agent précédent avant
la coupure), cette passe n'a fait que vérifier/tester/capturer.

### Fichiers modifiés

`tools/smoke_test_gameplay.gd` (12 nouveaux checks +
`_check_corbeau_pale/poing_du_colosse/oeil_sans_regard/serpent_creux`
+ leurs 4 appels dans `_ready()`, replacés avant les checks Terre pour
la raison de coordination ci-dessus),
`captures/verification/2026-08-25-chantier-a-invocateur-4competences/`
(20 fichiers). Aucun changement à `src/gameplay/player.gd`,
`src/gameplay/powers/*.gd`, aux scènes, aux recettes ou aux assets — le
travail de l'agent précédent était déjà correct et complet sur ces
points, rien à corriger.

## 2026-08-25 — CHANTIER A (reprise après coupure) : Pouvoir Terre, les
## 3 dernières compétences (Carapace/Effondrement/Fissure Éruptive) —
## audit, correction de 3 bugs réels, câblage smoke test, captures

**Contexte** : même histoire que l'entrée Invocateur juste au-dessus —
un agent Terre précédent tué en plein Chantier A, rien perdu (tout sur
disque, non commité), rien encore vérifié ni committé. Mission : auditer
d'abord.

### Audit — verdict : conception ET implémentation déjà quasi complètes,
### 3 bugs réels trouvés par le test, pas par la lecture

Déjà en place et correctement pensé AVANT cette passe (lu en entier dans
`src/gameplay/player.gd`, lignes ~470-630) : les 26 frames des 4
animations (`carapace_activation` 7, `carapace_active` 5,
`effondrement` 7, `fissure_eruptive` 7) déjà cuites et déjà câblées dans
`cendre_frames.tres` (`carapace_fin` = `carapace_activation` rejouée en
ordre inverse, 0 fichier supplémentaire — confirmé en lisant les
`ExtResource` du `.tres`, exactement comme documenté) ; les 3 recettes
JSON ; les constantes `CARAPACE_*`/`EFFONDREMENT_*`/
`FISSURE_ERUPTIVE_*` (paliers de tick, dégâts, rayon/portée) ; Carapace
correctement traitée comme un ÉTAT SOUTENU à 3 phases ACTIVATION/ACTIVE/
RECOVERY (pas ANTICIPATION/RELEASE/RECOVERY comme les compétences
d'impact) avec une boucle de respiration pilotée manuellement
(`_carapace_active_loop_tick`, jamais l'horloge fps autonome
d'AnimatedSprite2D) et AUCUNE fenêtre d'annulation pendant ACTIVATION/
ACTIVE (décision délibérée documentée : un bouclier annulable à volonté
perdrait son sens défensif) ; les 3 `_start_*/_advance_*/_end_*()` ;
l'enregistrement dans `IMPLEMENTED_SKILL_HANDLERS`/
`IMPLEMENTED_SKILL_COOLDOWN_GETTERS` (buffer d'input généralisé,
commit `1571521`, déjà branché). `poing_tellurique`/`maree_de_sable`
(déjà en jeu) n'ont ni scène ni script séparés — tout dans `player.gd` —
et Carapace/Effondrement/Fissure Éruptive suivent la même convention
(contrairement à Invocateur, qui invoque une créature séparée) : aucun
`scenes/gameplay/powers/*.tscn` à créer pour ces 3, vérifié en
comparant aux 5 compétences Terre déjà en jeu.

**Seul manque structurel** : comme pour Invocateur, zéro check dans
`tools/smoke_test_gameplay.gd` pour ces 3 compétences — l'agent précédent
avait été interrompu avant cette étape.

### 3 bugs réels trouvés (par le test, pas par la lecture du code)

**1. Fuite de cooldown Carapace → bloquait le lancement d'Effondrement**
(`tools/smoke_test_gameplay.gd`) : le test de Carapace vérifie qu'un 2e
appui PENDANT le cooldown ne relance rien, puis force
`_carapace_cooldown_remaining = 0` pour ne pas polluer les checks
suivants. Sous xvfb/llvmpipe, `Input.is_action_just_pressed("power3")`
peut être vu EN RETARD de plusieurs dizaines de ticks après l'appui
synthétique (même famille de décalage physics/render déjà documentée
pour `capture_scene.gd`) — remettre le cooldown à 0 immédiatement
"démasquait" cet écho tardif : il retombait pendant `_check_effondrement()`,
`_action_lock` étant vrai à ce moment pour une tout autre raison
(cooldown-blocked press de Pattes de Chasse, chantier concurrent), donc
mis en FILE puis déclenché pour de vrai — Carapace se relançait au
milieu du test d'Effondrement, qui ne pouvait alors jamais démarrer
(`_action_lock` déjà pris). Isolé par trace `print()` ciblée (retirée
après diagnostic), corrigé en laissant 4 ticks de battement AVANT la
remise à 0 du cooldown (voir commentaire ajouté dans `_check_carapace()`).
**2. Frontière flottante 180° dans `Targeting.enemies_in_arc()`**
(`src/gameplay/targeting.gd`) : Effondrement documente
`half_angle_deg=180` comme un CERCLE COMPLET (mandat explicite : frappe
devant ET derrière). Un ennemi placé EXACTEMENT à 180° de la direction
du lanceur (le cas de test "derrière") pouvait être exclu par une
comparaison stricte `angle_to <= half_angle_rad` fragile à l'arrondi
flottant entre `Vector2.angle_to()` et `deg_to_rad(180.0)` — confirmé
en traçant les cibles réellement trouvées (`Targeting.enemies_in_arc`
ne retournait que l'ennemi de face, jamais celui de derrière, de façon
reproductible sur 2 runs). Corrigé en sautant entièrement la comparaison
d'angle dès que `half_angle_rad >= PI - epsilon` (un cône ≥180° n'a de
toute façon plus de "côté exclu" possible) — plus robuste qu'une marge
arbitraire, et ne change rien aux cônes plus étroits (Bras-Faux/Poing
Tellurique/etc.).
**3. `Player.die()` ne réinitialisait pas les 3 nouvelles phases** —
constaté en capture (`--mode=player_action_sequence`, Carapace en armure
qui disparaît sans jamais jouer `carapace_fin` quand le joueur meurt en
pleine ACTIVE, ex. les 2 ennemis placeholder de `capture_scene.gd`
restés au contact pendant 100+ ticks). `die()` remettait déjà à `NONE`
les phases de Bras-Faux/Poing Belluaire/Poing Tellurique/Marée de
Sable/Corbeau Pâle/Poing du Colosse/Œil Sans Regard/Serpent Creux mais
PAS `_carapace_phase`/`_effondrement_phase`/`_fissure_eruptive_phase` —
oubli lors de leur ajout. Ajouté au même endroit, même patron. N'a
jamais fait échouer le smoke test lui-même (qui ne laisse jamais le
joueur mourir en pleine Carapace) — trouvé uniquement grâce à la capture
demandée par le mandat, qui simule un scénario que le smoke test ne
couvre pas.

### Marge de test élargie (documentée, pas une compensation aveugle)

`_check_effondrement()`/`_check_fissure_eruptive()` : le budget du
`_wait_until(phase==NONE)` final est passé de +5 à +25 ticks — même
cause que le bug n°1 (écho tardif de `is_action_just_pressed`, cette
fois retombant dans la fenêtre d'annulation de leur PROPRE RECOVERY et
consommé légitimement par le système d'annulation généralisé, qui
termine alors le cast un peu avant les ticks nominaux) — le comportement
gameplay est CORRECT dans ce cas (le système d'annulation fait
exactement ce qu'il doit face à un input qu'il reçoit), seule la marge
d'observation du test était trop juste. Commentaire explicatif ajouté
aux deux endroits.

### Vérification

`bash scripts/run_gameplay_smoke_test.sh` → **`"all_pass":true`**,
confirmé stable sur 4 runs consécutifs (headless direct ×3 + script
officiel ×1) après les 3 corrections ci-dessus. Avant correction : 4
échecs (`effondrement_hits_full_circle_*`, `effondrement_ends_and_
unlocks_*`, `fissure_eruptive_ends_and_unlocks_*`, plus
`oeil_sans_regard_*` — chantier Invocateur concurrent, non touché, déjà
documenté dans leur propre entrée ci-dessus et redevenu vert de
lui-même une fois la fuite de cooldown Carapace corrigée).

### Captures

Par compétence, comme demandé (4 temps en mouvement pour Effondrement/
Fissure Éruptive ; état soutenu réellement actif sur plusieurs ticks
pour Carapace) — `capture_scene.gd --mode=player_action_sequence`,
`--active_power=terre`, scale=2 :
- `captures/verification/2026-08-24-terre-effondrement-4temps/` — 5
  frames (`t00` Propagation, `t10` Convergence, `t15` Compression, `t21`
  Impact Final avec les 2 nombres de dégâts "22/22" visibles simultanément
  devant ET derrière — preuve visuelle du cercle complet après le fix
  n°2 ci-dessus —, `t55` Retombée) + planche de synthèse.
- `captures/verification/2026-08-24-terre-fissure-eruptive-4temps/` — 4
  frames (`t00` Préparation, `t10` Fissure — la ligne de fracture qui
  voyage visiblement du lanceur vers le point d'impact, `t18`
  Soulèvement — l'anneau/le pilier qui se forme À DISTANCE, pas aux
  pieds du lanceur, contrairement à Effondrement —, `t50` Retombée) +
  planche de synthèse.
- `captures/verification/2026-08-24-terre-carapace-etat-soutenu/` — 5
  frames (`t000` idle avant cast, `t012` activation en cours, `t024`
  début d'ACTIVE, `t060` et `t100` ACTIVE toujours soutenue, armure et
  fragments flottants visibles à chaque tick — la sustention réelle sur
  90+ ticks, pas une seule frame isolée) + planche de synthèse. Capture
  volontairement arrêtée avant la fin naturelle (~228 ticks) : les 2
  ennemis placeholder de `capture_scene.gd` plantés au contact tout du
  long finissent par tuer le joueur vers t~110-130 (artefact de l'outil
  de capture — 2 monstres au contact sans interruption pendant 3+
  secondes, pas un scénario de jeu réel), ce qui a permis de trouver le
  bug n°3 mais rendait les frames tardives (`carapace_fin`) non
  représentatives pour cette planche ; le mandat pour Carapace ne
  demande que l'état soutenu, pas la transition de fin.

### Coût PixelLab réel dépensé PAR CETTE PASSE

**0 crédit** — vérifié via `get_balance` en amont de toute action : les
26 frames (7+5+7+7) étaient déjà toutes générées par l'agent précédent.
Cette passe n'a fait que diagnostiquer/corriger du code et capturer.

### Fichiers modifiés

`src/gameplay/targeting.gd` (fix frontière 180°), `src/gameplay/
player.gd` (3 lignes ajoutées à `die()`), `tools/smoke_test_gameplay.gd`
(3 nouveaux checks + leurs appels dans `_ready()`, marge de test
élargie + commentaire sur `_check_carapace()`/`_check_effondrement()`/
`_check_fissure_eruptive()`), `captures/verification/2026-08-24-terre-
effondrement-4temps/`, `captures/verification/2026-08-24-terre-fissure-
eruptive-4temps/`, `captures/verification/2026-08-24-terre-carapace-
etat-soutenu/` (14 fichiers au total). Aucun changement aux assets, aux
recettes JSON, ni aux scènes — déjà corrects et complets.

**Note de coordination** : `src/gameplay/player.gd` et `tools/
smoke_test_gameplay.gd` sont des fichiers partagés activement modifiés
par l'agent Invocateur pendant cette même session (voir leur entrée
ci-dessus, qui documente avoir vu mes propres lignes de debug
apparaître dans la sortie du smoke test) — aucune ligne touchant
Corbeau Pâle/Poing du Colosse/Œil Sans Regard/Serpent Creux n'a été
modifiée par cette passe.
