# Worklog — Rank Zero

Journal de session, §16.5 de `docs/ARCHITECTURE_VFX_v3.md` : "Fin de
session : mettre à jour docs/worklog.md (fait / branché ou non /
prochain pas). C'est la mémoire inter-sessions — le repo est le cerveau."

---

## 2026-08-18 — Phase 0 (fondations minimales)

### Fait

- Transcrit le PDF `vfxarchitecturev3.pdf` (fourni par Milan) dans
  `docs/ARCHITECTURE_VFX_v3.md` — le doc devient une source versionnée,
  pas seulement un upload de session.
- `CLAUDE.md` racine : pointe vers l'architecture + ce worklog au
  démarrage de session.
- Godot 4.3.stable installé (`/opt/godot`, lien `godot4`), git-lfs
  installé, `mesa-vulkan-drivers` + `vulkan-tools` installés (Vulkan
  logiciel Mesa lavapipe/llvmpipe — aucun GPU dans ce sandbox).
- `project.godot` : renderer Mobile, viewport 640×360 (upscale entier,
  Nearest, mipmaps off au niveau projet), 60 ticks/s, ETC2/ASTC à
  l'import. Autoloads `VfxBudget` puis `VfxDirector`.
- Arborescence complète §8.2 + §12.1 (`assets/`, `data/`, `src/vfx/`,
  `scripts/`, `tools/`), dossiers vides marqués `.gitkeep`.
- `git lfs track "assets/processed/**/*.png" "assets/source/**/*.png"`
  → `.gitattributes`. `.gitignore` exclut `.godot/`, `assets/staging/*`,
  `/captures_local/` (sorties de capture NON approuvées — jamais
  commitées telles quelles, §13.3).
- `src/vfx/vfx_budget.gd` : budgets particules (200/effet, 2000 total —
  chiffres exacts §8.2) + overdraw/rémanence par zone d'écran (grille
  4×3), ces deux derniers seuils étant des valeurs de départ non
  chiffrées par le mandat, marquées comme telles dans le code.
- `src/vfx/vfx_director.gd` : `spawn()`/cleanup centralisé/journal de
  spawns (seed+recette) pour replay. Registre `_registry` = un nom de
  primitive -> un fichier réel, jamais une entrée fantôme.
- `src/vfx/primitives/impact_flash_frame.gd` : primitive `impactFlashFrame`
  (§4, §7.1) — choisie comme primitive de test PARCE QU'elle est
  nommément obligatoire dans tout impact majeur (§9.3), donc utile dès
  le premier commit plutôt qu'un stub jetable.
- `tools/capture_scene.tscn` + `.gd` : capture headless d'une primitive
  nommée à un tick donné, seed tracée.
- `scripts/capture_headless.sh`, `validate_pixels.py`,
  `check_hitbox_match.py`, `compare_reference.py` — les 3 scripts +
  la scène de capture demandés par le §15 Phase 0 point 4.
- `data/palettes/value_bands.json` (chiffres exacts §3),
  `data/labels/quality_labels.jsonl` (vide, aucun verdict encore).

### Écarts trouvés et corrigés (tous vérifiés par exécution réelle, pas supposés)

1. **`--headless` ne rend rien dans ce sandbox.** Vérifié par un test
   isolé AVANT d'écrire le moindre fichier du dépôt : `godot4 --headless`
   (et `--display-driver headless` seul) forcent le RenderingServer en
   mode `dummy` — `get_viewport().get_texture()` retourne toujours une
   texture nulle. `--display-driver headless` seul donne le même
   résultat cassé : Godot a besoin d'un vrai serveur d'affichage (même
   virtuel) sur cette machine pour créer un contexte de rendu, aucun mode
   "vraiment headless" ne fonctionne ici. Solution validée :
   `xvfb-run` + `--rendering-driver vulkan` sur Vulkan logiciel (Mesa
   lavapipe, aucun GPU dans ce sandbox — confirmé via
   `vulkaninfo --summary`, device "llvmpipe"). Documenté dans
   `CLAUDE.md` et en tête de `scripts/capture_headless.sh`. N'affecte
   QUE l'outillage de capture dans CET environnement — le renderer
   Mobile du jeu tournera sur Vulkan/Metal matériel normalement sur
   device réel.
2. **Rattrapage physique en rafale au démarrage.** Le moteur accumule du
   retard réel pendant la compilation des shaders (plusieurs secondes),
   puis peut exécuter jusqu'à 8 ticks physiques (`max_physics_steps_
   per_frame`, défaut Godot) dans une seule frame rendue pour rattraper.
   Un `impactFlashFrame` (1-2 ticks, §4) peut naître et mourir entre deux
   frames RÉELLEMENT dessinées — disparition silencieuse, exactement la
   classe de bug que §11.1 dénonce pour les particules invisibles.
   Corrigé : `physics/common/max_physics_steps_per_frame=1` dans
   `project.godot` — la simulation ralentit plutôt que de sauter des
   ticks. Coût accepté : ralentissement perçu sous charge extrême,
   jamais un état court-vécu escamoté (cohérent avec l'exigence de
   déterminisme du mandat, §13.4).
3. **Course entre la reprise d'un `await physics_frame` et
   `VfxDirector._physics_process`.** Constaté empiriquement (prints de
   diagnostic, timeline complète) : le signal `physics_frame` peut
   réveiller un coroutine AVANT que le `_physics_process` d'un AUTRE
   nœud (ici l'autoload `VfxDirector`) ait fini de tourner pour ce même
   pas — l'ordre n'est pas garanti entre la reprise d'un `await` et le
   traitement physique des autres nœuds. Compter les réveils du signal
   comme s'ils valaient chacun un tick `VfxDirector` était donc faux
   d'un cran, silencieusement (`tools/capture_scene.gd` demandait tick=1
   et capturait parfois AVANT que le tick 1 ait réellement eu lieu).
   Corrigé : sonder `VfxDirector.get_current_tick()` dans une boucle
   `while ... < target: await physics_frame`, jamais compter les
   itérations d'`await`.
4. **`queue_free()` retire le nœud du rendu avant que son dernier tick
   n'ait été rasterisé.** `VfxDirector._physics_process` libérait
   l'entité DANS LE MÊME appel que son dernier `tick()` — sur une
   primitive de 2 ticks, une capture pile au tick 2 tombait sur un écran
   vide (le nœud avait déjà disparu de l'arbre de rendu). Corrigé :
   libération décalée d'un pas (`ticks_elapsed > lifetime_ticks`, pas
   `>=`) — l'entité reste visible et capturable pendant TOUTE sa durée
   de vie déclarée, la libération n'arrive qu'au tick suivant, jamais
   dessiné.
5. Latence du pipeline de rendu de Godot (plusieurs images tampons) :
   un seul `process_frame` après le tick cible capturait un écran pas
   encore rasterisé. Corrigé en gelant la simulation
   (`get_tree().paused = true`, qui arrête `_physics_process` de
   `VfxDirector` sans arrêter le rendu) puis en attendant 3
   `process_frame` avant de lire `get_viewport().get_texture()`.

### Preuve — Definition of done Phase 0 (§15 point 5), reproductible

```
mkdir -p captures_local
scripts/capture_headless.sh --primitive=impactFlashFrame --seed=44102 --tick=1 --out=captures_local/x.png
python3 scripts/validate_pixels.py --image captures_local/x.png --category vfx     # ok=true
python3 scripts/check_hitbox_match.py --selftest                                    # 7/7 (formule §2 test 6 vérifiée sur cas géométriques exacts)
python3 scripts/compare_reference.py --asset-id impactFlashFrame_seed44102_tick1_v1 --candidate captures_local/x.png  # ok=true, status=candidate
```

Reproductibilité seed vérifiée directement : deux exécutions au même
seed produisent des PNG **identiques octet pour octet** (`cmp`, exit 0).
Une seed différente ne change pas le rendu de cette primitive précise
(elle ne consomme délibérément pas `seed` — pas d'aléatoire visuel dans
un flash, documenté dans le fichier lui-même) ; la traçabilité seed
existe déjà dans `VfxDirector.spawn_log` pour les primitives futures qui
en auront besoin.

`captures_local/` n'est jamais commité (gitignored) : ce sont des
candidats, pas des références approuvées (§13.3).

### Limite connue, non bloquante pour Phase 0

`check_hitbox_match.py` attend une image où l'alpha isole RÉELLEMENT
l'effet (fond transparent hors de l'effet). La capture actuelle de
`tools/capture_scene.gd` exporte le VIEWPORT COMPLET (fond + VFX, alpha
opaque partout) — adaptée à `validate_pixels.py` (bandes de valeur) et
au verdict humain (§13.2, captures standardisées), mais PAS directement
utilisable comme entrée du gate hitbox tel quel (le script mesurerait la
masse du fond, pas celle de l'effet). `check_hitbox_match.py` est donc
prouvé exact via son propre `--selftest` (disque/rectangle synthétiques,
réponse connue par géométrie) plutôt que sur une capture réelle — il n'y
a de toute façon aucune vraie hitbox gameplay avant Phase 1 (pas de
personnage, pas de combat). À revisiter en Phase 1 : soit exporter le
VFX sur fond transparent (sous-viewport dédié), soit composer la
comparaison différemment une fois qu'une vraie recette+hitbox existe.

### Branché / testé

Chaîne complète prouvée de bout en bout par exécution réelle (pas
supposée) : Godot 4.3 → capture headless (xvfb+Vulkan logiciel) → PNG
640×360 → 3 gates Python, tous verts, y compris leurs `--selftest`
respectifs (7/7, 7/7, 4/4).

### Prochain pas

Phase 1 (§15) : tranche verticale. Personnage de test via PixelLab
(reference.png canonique, validée par Milan AVANT toute animation),
idle/déplacement/dash/hurt/mort pose-to-pose, combo 3 coups chaîné,
UNE compétence complète (8 couches, 4-6 primitives, `impactFlashFrame`
+ `recoil` obligatoires), SFX placeholder. Rien de tout ça ne démarre
sans direction de contenu (personnage/pouvoir/lore) — hors scope de ce
document (§1, §16.6), à recevoir séparément.

---

## 2026-08-18 — Phase 1 (tranche verticale), en cours

Direction de contenu reçue de Milan : turnaround perso (4 vues + palette
en couches) et 3 recettes + 1 palette pour une compétence "Totem du Vide".
Entrée dans le §15 enfin possible.

### Fait — 1.1 Personnage PixelLab

- Turnaround (image 4 panneaux FACE/3-4/PROFIL/DOS + swatches palette,
  pas un sprite isolé) recadré et downscale (panneau FACE, fond neutre
  conservé) en `assets/source/pixellab/cendre/reference.png` — c'est la
  référence canonique exigée par §5.3, jamais le panneau brut multi-vues.
- `create_character(mode="v3", reference_image_base64=..., size=48,
  n_directions=8)` → personnage "Cendre" (id `f6b77b57-...`), 8 rotations
  téléchargées dans `assets/source/pixellab/cendre/rotations/`.
- Cohérence entre vues (§5.3) vérifiée à l'œil : les 8 rotations composées
  côte à côte gardent silhouette/capuche/harnais/palette cohérents.
- Écart d'exécution : `reference_image_base64` tronque silencieusement
  au-delà d'environ 1-2 Ko dans ce client MCP (3020 caractères → image
  corrompue côté serveur PixelLab, alors que `reference_image_url`
  n'était pas utilisable faute d'hébergement public). Contourné par
  quantification de couleurs (palette réduite à 16 couleurs) + downscale
  du crop pour rester sous ce seuil — qualité suffisante pour une
  génération v3 reference-image (le modèle réinterprète de toute façon
  la silhouette/style, pas un exact recopiage pixel).
- Journal d'usage (§5.3) : `data/pixellab_usage.jsonl`, y compris le
  test-sonde jeté ("Cendre_test", marqué `rejected`) qui a servi à trouver
  ce seuil de troncature avant de lancer la vraie génération.
- Statut : **`generated_awaiting_milan_verdict`** — pas encore de verdict
  humain (§13.2). À soumettre avec les captures animation/combo/pouvoir
  (Phase 1.7) avant toute généralisation, comme demandé.
- Recettes + palette Totem du Vide sauvegardées telles que fournies dans
  `data/recipes/power.totem_du_vide.{spawn,attack,expire}.json` et
  `data/palettes/totem_du_vide.json` — pas encore résolues par du code
  (Phase 1.5).

### Fait — 1.2 Squelette gameplay minimal

- `src/gameplay/game_constants.gd` : une seule constante pour l'instant
  (`PX_PER_METER = 32.0`) — convertit les distances en mètres du mandat
  ("rayon 3m") en pixels, à partir de la taille de corps §0 (~48px ≈
  1,5m). Centralisé pour ne jamais recopier ce chiffre en dur ailleurs.
- `src/gameplay/stats.gd` (`Resource`) : hp/max_hp/int_stat/move_speed_px.
  INT est déjà là car le Totem (Phase 1.6) doit scaler ses dégâts dessus.
- `src/gameplay/targeting.gd` : `nearest_enemy_in_radius()`, statique,
  réutilisable par n'importe quel pouvoir futur — écrit une fois pour
  répondre littéralement à "ennemi le plus proche en zone" du mandat
  Totem, pas seulement pour lui.
- `src/gameplay/enemy.gd` / `player.gd` (`CharacterBody2D`) + scènes
  `scenes/gameplay/{enemy,player}.tscn`. Player porte déjà la rotation
  "south" de Cendre en Sprite2D statique (provisoire — Phase 1.3 la
  remplace par de l'animation réelle). Enemy est un placeholder
  géométrique (pas d'art ennemi reçu, hors scope §1/§16.6) mais porte
  déjà `take_damage()` + un vrai recul physique (`recoil`, §4 : "recul
  visible de la cible... réaction de l'ennemi, pas une primitive du
  pouvoir") — nécessaire dès maintenant pour que Phase 1.6 (Totem) ait
  quelque chose à appeler.
- Hitbox = `CapsuleShape2D` posée à la main, jamais dérivée du sprite
  (cohérent avec le test hitbox/visuel §2).

### Écart trouvé et corrigé (Phase 1.2)

Un `.png` ajouté au dépôt hors éditeur (téléchargé via `curl`, comme les
rotations PixelLab) n'a pas de fichier `.import` compagnon. Constaté par
exécution réelle : référencer une telle image dans une `.tscn` ne se
contente pas d'échouer proprement — ça avorte en cours de route le scan
qui enregistre les `class_name` du projet (les autres scripts, sans
rapport avec la texture, perdaient soudain la résolution de `Stats`,
`Player`, etc.), le script racine de la scène de test ne chargeait donc
plus, `_ready()` ne tournait jamais, et Godot restait assis à tourner
sans jamais quitter — un hang silencieux à pleine charge CPU, aucun
message d'erreur visible en surface (il fallait lire les logs en
entier). Corrigé : passage `godot4 --headless --rendering-driver vulkan
--import` (import forcé de toutes les ressources, silencieux, quitte
seul) ajouté SYSTÉMATIQUEMENT avant toute exécution de scène dans
`scripts/run_gameplay_smoke_test.sh` ET `scripts/capture_headless.sh` —
ce dernier n'avait pas encore été touché par ce problème en Phase 0
(aucun asset externe alors) mais le sera dès la première capture Phase 1
avec de l'art PixelLab dedans.

### Preuve — 1.2, reproductible

```
scripts/run_gameplay_smoke_test.sh
# → SMOKE_TEST_RESULT {"all_pass":true,"checks":[...5 checks...]}
```
5/5 vérifications passent : ciblage plus-proche-en-zone (ignore une
cible hors rayon), `take_damage()` réduit les PV du bon montant, le
recul pousse la cible dans la direction opposée à l'attaquant, des
dégâts léthaux marquent l'ennemi mort ET libèrent le nœud, le joueur se
déplace et met à jour son `facing` sous une entrée simulée.

### Prochain pas

Phase 1.3 : animations de base (idle/déplacement/dash/hurt/mort) pour
Cendre, pose-to-pose (§6.1/6.2/6.3), remplacement du Sprite2D statique du
Player par un vrai AnimationPlayer.

---

## 2026-08-18 (suite) — Phase 1.3 (animations de base)

### Fait

- 5 animations PixelLab pour Cendre, **direction sud uniquement** pour ce
  premier passage (discipline batch §5.3 : couvrir les 8 directions ×
  5 animations dépasserait 5 appels et exige une estimation présentée à
  Milan — remis à un batch ultérieur, une fois le style validé) :
  - `idle` (template `breathing-idle`, 4f), `deplacement` (template
    `walk`, 6f), `hurt` (template `taking-punch`, 6f) : acceptées à la
    première passe.
  - `mort` et `dash` : le premier essai ne lisait pas comme l'action
    demandée (`falling-back-death` ressemblait à une garde de combat,
    pas une chute ; le dash ressemblait à un changement de posture
    accroupie, pas un sprint). Re-roll en mode v3 custom avec des
    descriptions plus explicites (§16.3 "vérifier avant de déclarer
    fini" — pas d'acceptation automatique). `mort` : nette après re-roll
    (titube → s'effondre → reste au sol). `dash` : mieux mais encore
    imparfait (lecture "fente basse dynamique" plutôt qu'un sprint net) —
    accepté comme résultat de base (pas de boucle de re-roll indéfinie),
    signalé pour le verdict Milan.
  - Journal complet (y compris le test-sonde rejeté et les 2 groupes
    supprimés via `delete_animation`) dans `data/pixellab_usage.jsonl`.
- **Écart d'exécution constaté** : le canvas de sortie change de taille
  entre animations (32×64 pour idle/marche/hurt, 88×88 pour mort/dash —
  le mode v3 custom élargit le canvas selon l'amplitude du mouvement).
  Or `AnimatedSprite2D` n'a qu'UN SEUL `offset`, appliqué à toutes les
  frames de toutes les animations : sans normalisation, changer
  d'animation aurait fait sauter les pieds du personnage.
  Corrigé par un vrai script de pipeline, `scripts/cook_character_frames.py` :
  calcule la bbox alpha de chaque frame source, recadre sur un canvas
  commun (96×96) avec le pivot bas-centre (§6.3) toujours au même pixel.
  Sortie dans `assets/processed/sprites/cendre/<anim>/` + manifeste
  `assets/manifests/cendre_frames_cooked.json`. C'est la première vraie
  utilisation de la distinction `source/` (brut PixelLab) vs
  `processed/` (cuit pour le jeu) posée en Phase 0 (§12.1).
- `SpriteFrames` généré (`assets/processed/sprites/cendre/cendre_frames.tres`,
  28 frames sur 5 animations) et câblé sur `scenes/gameplay/player.tscn`
  via un `AnimatedSprite2D` (remplace le `Sprite2D` statique), avec
  `offset = Vector2(0, -44)` calculé pour aligner le pivot cuit sur
  l'origine du nœud.
- `player.gd` : bascule idle/déplacement automatique selon le mouvement,
  plus `play_hurt()`/`play_dash()`/`die()` — pas encore appelés par du
  vrai gameplay dans cette tranche (aucun système n'inflige de dégâts au
  joueur, hors scope Phase 1), mais prêts pour quand le combat réel
  câblera dessus. Un verrou `_action_lock` empêche `_physics_process`
  d'écraser une animation ponctuelle (hurt/dash) en cours ; levé par le
  signal `animation_finished`, jamais par un minuteur à côté.

### Preuve — Phase 1.3, reproductible

```
scripts/run_gameplay_smoke_test.sh
# → 6/6 checks, dont "sprite_animation_switches_idle_deplacement_idle"
#   (idle -> deplacement sous entrée -> idle au relâchement)
```

Vérification visuelle en plus des checks logiques (`tools/capture_player_pose.gd`,
même technique de capture headless que Phase 0) : ligne de sol dessinée
au Y du nœud Player, capture des 5 animations, mesure programmatique
(numpy) du rang de pixel des pieds vs la ligne de sol — **alignement au
pixel près sur les 5 animations**, y compris `mort`/`dash` malgré leur
canvas source différent (88×88 vs 32×64), preuve que le pivot cuit par
`cook_character_frames.py` fonctionne réellement, pas juste "à l'œil".

### Limite connue, non bloquante

- Seule la direction sud existe (7 directions × 5 animations restantes,
  batch futur avec estimation Milan).
- Timing simplifié : une frame = une durée uniforme par animation (fps
  fixe), pas encore le détail §6.2 (anticipation 25-40%/release
  5-12%/impact hold/recovery 35-55% avec frames taguées). Le manifeste
  cuit (`cendre_frames_cooked.json`) donne déjà canvas+ancre par frame ;
  le tagging de phase reste à ajouter quand le combo (Phase 1.4) aura
  besoin de fenêtres de hitbox précises.
- `dash` accepté avec réserve (silhouette pas franchement "sprint") —
  à trancher par Milan, pas par moi, avec les autres captures.

### Branché / testé

`scenes/gameplay/player.tscn` charge `AnimatedSprite2D` +
`cendre_frames.tres`, joue `idle` par défaut, bascule sur `deplacement`
sous entrée — prouvé par exécution réelle headless (smoke test 6/6 +
capture visuelle mesurée), pas supposé.

### Prochain pas

Phase 1.4 : combo léger 3 coups chaînés (fenêtre de chaînage sur les
derniers ticks de chaque RECOVERY, variation de pose/trajectoire par
coup, `impactFlashFrame` + `recoil` sur chaque coup).

---

## 2026-08-18 (suite) — Finalisation pour review externe (Claude conception)

Demande explicite de Milan : que son reviewer conception inspecte tout
depuis git plutôt que via des screenshots. Pas de nouveau contenu — push
complet + captures standardisées + nettoyage + manifests, sur l'état
Phase 1.1-1.3 déjà en place.

### Fait — 1. Push complet + vérification LFS

- Rien à committer côté code au moment de la demande (Phase 1.3 déjà
  poussée en `f47226c`) — la vérification a donc porté sur l'intégrité
  du push précédent, pas sur du contenu nouveau à ce stade.
- `git lfs push origin main --all` relancé explicitement : **63/63
  objets LFS uploadés** (le call est idempotent — confirme qu'ils sont
  bien sur le serveur, pas seulement des pointeurs locaux résolus).
- Visibilité du repo vérifiée via l'outil de session (pas de requête API
  GitHub anonyme fiable dans ce sandbox, le proxy sortant la bloque) :
  **`broussemilan-beep/Jeux`, `visibility: public`, `can_push: true`**.
- URL : https://github.com/broussemilan-beep/Jeux

### Fait — 2. Captures standardisées (`captures/phase1/`)

Extension de la scène de capture existante plutôt qu'une scène
parallèle (`tools/capture_scene.gd` gagne un `--mode=character` à côté
du `--mode=primitive` de Phase 0 — même technique pause+3×process_frame,
un seul point d'entrée, cf. commentaire en tête du fichier). Écart trouvé
en cours de route : sans précaution, `Player._physics_process` (bascule
auto idle/déplacement) écrasait l'animation demandée (hurt/dash/mort)
dès qu'un `await physics_frame` s'écoulait pendant la capture — corrigé
en ne laissant tourner AUCUNE physique pour ce mode (l'état posé
manuellement suffit, le rendu n'en a pas besoin).

5 captures produites, fond neutre (gris projet, aucun décor), frame
représentative choisie à l'œil par animation (pas systématiquement la
frame 0, qui est souvent une pose neutre peu lisible en capture unique) :

| Fichier | Anim | Frame capturée | Pourquoi |
|---|---|---|---|
| `hero_idle.png` | idle | 0 | boucle de respiration, toute frame est représentative |
| `hero_walk.png` | deplacement | 3 | foulée la plus large de la marche |
| `hero_dash.png` | dash | 4 | pose la plus dynamique (fente + cape) |
| `hero_hurt.png` | hurt | 3 | pic de recul visible |
| `hero_death.png` | mort | 6 | état final, allongé au sol |

**Totem du Vide (spawn/attack/expire) : PAS ENCORE IMPLÉMENTÉ.** Phase
1.5 (moteur de recettes VFX + 4 primitives manquantes) et Phase 1.6
(script d'orchestration du Totem) n'ont pas démarré — voir tâches #184
et #185. Aucune capture `totem_*` livrée : pas de solution de repli
livrée à la place, conformément à la consigne. De même, `hero_combo_1/2/3`
n'existent pas : Phase 1.4 (combo 3 coups) n'a pas démarré non plus.

Les captures ne passent PAS par Git LFS (fichiers de quelques Ko,
contrairement aux assets sources/traités) — décision délibérée pour
rester simple, GitHub les affiche nativement de toute façon. Un
`captures/.gdignore` empêche Godot de les traiter comme des ressources
de jeu à importer (elles ne sont référencées par aucune scène).

### Fait — 3. Nettoyage

- **Réclamation "F_L incrusté sur une frame d'attaque" : NON RETROUVÉE.**
  Inspection visuelle exhaustive à fort zoom (×3 à ×6) de TOUTES les
  frames existantes — `reference.png`, les 8 rotations, et les 4-7
  frames de chacune des 5 animations (idle/déplacement/hurt/mort/dash),
  cuites ET sources — aucun texte, watermark ou artefact incrusté nulle
  part. Par ailleurs, **aucune frame d'attaque/combo n'existe encore
  dans ce dépôt** (Phase 1.4 pas démarrée) : la description ("frame
  d'attaque") ne correspond à rien de généré ici. Hypothèse la plus
  probable : confusion avec les anciens assets FRACTURE (`game/`, projet
  abandonné) ou une autre capture non versionnée. À clarifier avec
  Milan plutôt que de fabriquer un correctif pour un fichier qui
  n'existe pas.
- **"Sheet de test 8 poses quasi identiques" : identifié comme le set de
  8 rotations directionnelles (`assets/source/pixellab/cendre/rotations/`),
  PAS un reste de génération non trié.** C'est le tour de personnage
  canonique (§5.3) dont dérivent toutes les animations — conservé,
  documenté explicitement dans le nouveau manifest `hero_turnaround.json`
  pour éviter toute confusion future. Aucun fichier de travail temporaire
  trouvé dans le dépôt (arborescence complète auditée : aucun sheet de
  probe, aucun test PixelLab jeté n'a jamais été committé — les essais
  rejetés vivent uniquement dans `data/pixellab_usage.jsonl` en tant que
  journal, jamais comme fichier image).
- Nettoyage réel effectué : suppression de `tools/capture_player_pose.gd`
  et `.tscn` (outil de vérification de pivot Phase 1.3, remplacé par le
  `--mode=character` officiel de `capture_scene.gd` — un seul outil de
  capture, pas deux qui se recouvrent).

### Fait — 4. Manifests (§12.5) + statut qualité

6 nouveaux fichiers manifest, un par asset (§12.2 "une recette = un
fichier") : `assets/manifests/hero_{idle,walk,dash,hurt,death,turnaround}.json`.

**Écart trouvé en vérifiant plutôt qu'en supposant** : j'ai fait tourner
`scripts/validate_pixels.py --category character` sur toutes les frames
traitées (pas juste survolé à l'œil) — **échec systématique sur les 5
animations** (~20 pixels sur 450-1030 selon la frame). Cause unique et
commune : le sommet du crâne chauve du personnage atteint ~91-92% de
Value (HSV), au-dessus de la borne haute de la bande "character"
(15-88%, §3). Même violation sur toutes les animations (racine commune :
la tête, pas un défaut par frame/animation). **Non corrigé ici** — je
n'ai pas retouché les pixels : c'est un choix qui touche la direction
artistique (couper la valeur du crâne, ou ajuster la bande elle-même)
et Milan doit trancher, pas moi silencieusement. Chaque manifest porte
`"validated_auto": false` avec le détail exact de la violation.

Corrigé au passage (trouvé en construisant les manifests, pas cherché
exprès) : l'animation `mort` tournait à 8 fps, qui ne divise pas 60 —
7,5 ticks/frame, impossible à exprimer en ticks entiers (§0). Recalée à
6 fps (10 ticks/frame). Nouveau script `scripts/build_sprite_frames.py`
qui refuse maintenant toute fps ne divisant pas 60 exactement, pour que
ça ne puisse plus se reproduire silencieusement. Non-régression
reconfirmée (smoke test 6/6) après le changement.

`data/labels/quality_labels.jsonl` : **toujours vide, 0 octet** — aucun
verdict humain donné, aucun `accept` auto-attribué (§13.2/§16), conforme
à la consigne explicite.

### Prochain pas

Toujours Phase 1.4 (combo 3 coups) — inchangé. Cette session n'a ajouté
aucun contenu de gameplay, uniquement finalisé/documenté/nettoyé
l'existant pour la review externe.

---

## 2026-08-18 (suite) — Phase 1.4 (combo léger 3 coups)

Note de Milan : le pouvoir du Totem du Vide va changer (nouvelle version
à venir) — Phase 1.5/1.6 restent donc en pause, seul le combo avance.

### Fait

- 3 animations PixelLab pour Cendre (`coup1`/`coup2`/`coup3`, direction
  sud uniquement — même discipline batch §5.3 que Phase 1.3), trajectoire
  et pose distinctes par coup comme demandé : frappe avant courte
  (coup1), retournement/dos de main (coup2), frappe lourde à deux mains
  overhead (coup3).
  - `coup3` a nécessité un re-roll : le premier essai avait un halo/burst
    de lumière blanche parasite (frames 3-4) sans rapport avec la
    demande, et une jambe levée qui lisait comme un coup de pied ou un
    sort plutôt qu'une frappe à deux mains — prompt reformulé en
    excluant explicitement magie/lueur ("no magic, no glow, no light
    effects"). Le résultat retenu est bien meilleur mais garde un très
    léger halo résiduel autour de la tête sur 1-2 frames — accepté
    (discipline anti-boucle, pas de second re-roll), signalé pour
    arbitrage Milan plutôt que retenté silencieusement.
  - Détail complet (prompts, group IDs, raisons de rejet) dans
    `data/pixellab_usage.jsonl`.
- `scripts/cook_character_frames.py` et `scripts/build_sprite_frames.py`
  relancés avec les 8 animations ensemble (les 5 de Phase 1.3 + les 3
  nouvelles) pour que `cendre_frames.tres` et le manifeste cuit restent
  complets — **écart trouvé** : un run intermédiaire du script de cuisson
  avec seulement `coup1`/`coup2` en argument avait écrasé
  `cendre_frames_cooked.json` et fait disparaître les 5 animations Phase
  1.3 du manifeste (les PNG traités eux-mêmes étaient intacts sur
  disque, seul le manifeste était tronqué) — corrigé en relançant le
  script avec les 8 noms d'animation ensemble.
- **Machine à états du combo dans `player.gd`** (`ANTICIPATION` ->
  `RELEASE` (frappe au premier tick) -> `RECOVERY`), en ticks purs (60/s,
  jamais liée à la durée réelle de lecture du sprite — deux horloges
  séparées, §16.3) :
  - `ANTICIPATION_TICKS=8`, `RELEASE_TICKS=4`, `RECOVERY_TICKS=14`,
    `CHAIN_WINDOW_TICKS=6` (derniers ticks de la recovery, mandat :
    "fenêtre de chaînage sur les derniers ticks de chaque RECOVERY").
  - Un appui sur "attack" pendant l'anticipation/release d'un coup reste
    en mémoire (`_attack_queued`) et n'est consommé qu'à l'ouverture de
    la fenêtre — bufferisation volontaire (feel standard, pas un bug).
  - Chaque coup applique dégâts (`ATTACK_DAMAGE=10.0`) + recul sur
    l'ennemi le plus proche en portée (`Targeting.nearest_enemy_in_radius`,
    déjà éprouvé par le Totem) et pose `impactFlashFrame`
    (`VfxDirector.spawn`) — le recul reste porté par
    `Enemy.take_damage()` (mandat : "pas une primitive du coup, une
    réaction de l'ennemi"), le coup ne pose QUE le flash d'impact.
  - Le 3e coup n'ouvre pas de fenêtre de chaînage (`_combo_step <
    AttackAnimName.size()` dans la condition) — combo fixe à 3, jamais
    une boucle infinie.
  - Nouvelle action input `attack` (espace + clic gauche) ajoutée à
    `project.godot` — **écart trouvé** : la syntaxe `Object(Type,
    prop=val,...)` que j'avais écrite pour les `InputEventKey`/
    `InputEventMouseButton` intégrés a fait planter le parsing complet
    du fichier projet (`Expected property name as string`) au premier
    lancement headless suivant. La syntaxe correcte pour un littéral
    `Object(...)` dans le format texte de Godot est `"prop":val` (guillemets
    + deux-points), pas `prop=val` (réservé aux assignations de clé de
    section top-level) — corrigé, reproduit et vérifié.
- `tools/capture_scene.gd` étendu avec `--mode=character` (déjà fait
  juste avant cette entrée de worklog, réutilisé tel quel ici) pour les
  captures `hero_combo_1/2/3.png` — 3 nouveaux manifests §12.5
  (`assets/manifests/hero_combo_{1,2,3}.json`), même statut
  `validated_auto:false` que les 5 animations Phase 1.3 (même violation
  de bande de valeur, tête du personnage — voir `hero_idle.json` pour le
  détail, non re-décrit ici).

### Écart trouvé et corrigé (bug de test, pas de gameplay)

Le premier passage des nouveaux checks de smoke test faisait **tourner
Godot indéfiniment sans jamais imprimer de résultat** (même classe de
symptôme que le bug Phase 1.2 : script en échec de parsing -> `_ready()`
du nœud racine ne tourne jamais -> `quit()` jamais appelé -> le moteur
reste assis à afficher un écran vide). Cause réelle, différente cette
fois : une expression lambda `func(): return A and B` répartie sur deux
lignes physiques dans `tools/smoke_test_gameplay.gd` — `Expected closing
")" after call arguments` à la recompilation du script. Corrigé en
gardant chaque lambda `_wait_until(...)` sur une ligne logique unique
(extraction d'une variable intermédiaire pour ne pas dépasser une
longueur raisonnable). Reproduit et vérifié : le process tournait
toujours à pleine charge CPU après 2m37 sans sortie avant le fix, 0
process godot restant après.

Séparément (bug de synchronisation dans le TEST, pas dans le jeu) : le
check "retour à idle après recovery complète" lisait l'animation UNE
frame trop tôt — `_end_combo()` remet `_combo_step` à 0 mais ne pousse
pas elle-même l'anim "idle" (c'est `_handle_movement()` qui le fait, au
`_physics_process` SUIVANT, les deux branches étant mutuellement
exclusives dans le même appel). Corrigé en ajoutant un
`await get_tree().physics_frame` avant de lire l'anim finale.

### Preuve — Phase 1.4, reproductible

```
scripts/run_gameplay_smoke_test.sh
# → 11/11 checks, dont les 5 nouveaux :
#   attack_input_starts_coup1, combo_hit_damages_enemy_in_range,
#   combo_hit_applies_recoil_to_enemy, chain_window_press_advances_to_coup2,
#   combo_returns_to_idle_after_full_recovery_without_input
```

Les checks sondent l'état réel (`_wait_until`, boucle qui interroge
`_combo_step`/`_combo_phase`/`_combo_tick` jusqu'à condition vraie, comme
`capture_scene.gd` sonde `VfxDirector.get_current_tick()` en Phase 0)
plutôt que de compter des `await physics_frame` à l'aveugle — même
discipline que le reste du projet après le bug de course découvert en
Phase 0.

### Limite connue, non bloquante

- Toujours direction sud uniquement pour les 3 nouveaux coups (7
  directions × 8 animations restantes désormais, batch futur).
- `coup3` garde un très léger halo résiduel (voir plus haut) — signalé,
  pas corrigé sans arbitrage Milan.
- Le Totem du Vide (Phase 1.5/1.6) est en pause — nouvelle version du
  pouvoir annoncée par Milan, pas encore reçue.

### Branché / testé

Combo jouable de bout en bout (attack -> coup1 -> [chaînage] -> coup2 ->
[chaînage] -> coup3 -> retour idle), dégâts+recul+impactFlashFrame réels
sur un ennemi en portée — prouvé par exécution réelle headless (11/11),
pas supposé.

### Prochain pas

En attente de la nouvelle version du Totem du Vide (Milan). Rien à
démarrer côté Phase 1.5/1.6 avant réception. Phase 1.7 (captures/gates/
manifest finaux) reste après le Totem.
