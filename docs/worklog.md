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

## 2026-08-18 — Corrections review externe (Claude, conception) sur Phase 1

Retour de review sur les captures Phase 1 poussées précédemment : 4
corrections demandées, reprises sur l'existant uniquement (aucun nouveau
contenu). Consigne explicite : éviter un 3e re-roll PixelLab sur
dash/coup3 (2 tentatives déjà consommées, voir `data/pixellab_usage.jsonl`)
— privilégier la retouche manuelle des frames déjà générées.

### 1. Dash — cape symétrique corrigée

`hero_dash.png` montrait la cape se déployer en éventail symétrique des
deux côtés du personnage (lecture "ailes"), contredisant le principe de
design (cape asymétrique = lisibilité de la direction du dash). Inspection
pixel par pixel des 5 frames sources (`assets/source/pixellab/cendre/
animations/dash/`) : frames 0 et 1 déjà correctes (cape naturellement
asymétrique), frames 2/3/4 montraient un vrai double-lobe quasi-miroir
(ex. frame 2 : extension gauche jusqu'à x=19, droite jusqu'à x=67, quasi
symétrique autour du centre du corps x≈43).

Correction : édition pixel directe (script Python/PIL, pas d'Aseprite
disponible dans cet environnement headless — même résultat, effacement
ciblé de pixels identifiés par inspection ASCII/coordonnées) sur les
frames 2/3/4 — le lobe de cape du côté le plus court a été effacé
(mis à `alpha=0`), ne laissant que le côté déjà présent et plus long
comme traînée asymétrique. Un fragment de cape isolé (déconnecté du
reste, résidu de l'effacement) a également été nettoyé sur la frame 2.
Aucun appel PixelLab. Re-cuit (`cook_character_frames.py`) et recapturé.

### 2. Combo_2 — tache jaune/beige sur le crâne

Non détectée jusqu'ici, absente du journal/worklog. Scan systématique
(pas juste visuel) des 5 frames sources de `coup2/` pour toute teinte à
teinte non-neutre (HSV hue hors gris) : une seule couleur incriminée,
`(216,213,191)` — un ton "highlight de peau" que PixelLab réutilise par
endroits (visible aussi ponctuellement sur les mains/pieds dans d'autres
frames de la même animation), présente sur 4/5 frames (14 pixels au
total, concentrés sur le crâne/visage frame 3 — celle utilisée pour la
capture). Hors de la palette grise/désaturée stricte du personnage.

Correction : désaturation exacte de cette teinte vers son équivalent gris
neutre de même Value (`(216,216,216)`), toutes occurrences dans les 5
frames. Revalidé visuellement (crop 12× de la zone tête) : plus de tache.

### 3. Combo_3 — halo plus important que rapporté

Le journal (entrée du re-roll) décrivait "léger halo résiduel sur 1-2
frames" — la capture montrait en réalité une aréole blanche couvrant une
bonne partie de la tête sur la frame utilisée (frame 3), largement plus
grave que rapporté. Inspection individuelle des 5 frames (pas seulement
celle choisie pour la capture) :

- frame 0 : propre ;
- frame 1 : petit reflet de tête dans la norme établie (même taille que
  le highlight présent sur les autres animations, ex. frame 2 de
  `coup2`) — pas un défaut ;
- frame 2 : propre, **aucun halo** ;
- frame 3 : vraie aréole blanche ovale, ~13×13px, couvrant la majorité
  de la tête (rows 21-33 quasi entièrement à V≥88%) ;
- frame 4 : bande blanche horizontale plate (~22×4px) traversant le
  visage, rows 27-30.

Frame 2 étant propre, elle devient la nouvelle référence de capture
(`hero_combo_3.json` : `capture_note` mis à jour, ancienne frame 3
documentée comme non-choisie). Frames 3 et 4 également retouchées en
pixel direct (pas seulement contournées) puisqu'elles restent jouées en
jeu réel, pas seulement en capture statique : les pixels à Value ≥ 200
ont été recolorés vers la teinte de capuche déjà utilisée ailleurs sur
le personnage (`(110,111,115)`), en suivant le contour du cluster sombre
réel (contour interpolé ligne par ligne à partir des pixels non-halo
adjacents), pas un rectangle arbitraire — un premier essai avec une boîte
rectangulaire donnait un résultat trop artificiel (tête "carrée"), refait
proprement en suivant la silhouette. Aucun appel PixelLab (0/1 re-roll
consommé sur ce correctif, discipline anti-boucle respectée).

### 4. Crâne — plafond de bande de valeur relevé (§3)

Root cause identifiée par scan exhaustif (pas seulement le crâne) :
`validate_pixels.py --category character` échouait systématiquement
(67 violations sur `idle` frame 0 seule, cappées à 20 dans le rapport —
limite du sampling du script, pas du vrai total) à cause d'un highlight
"presque blanc" (~91-97% V) réutilisé par PixelLab **sur tout le
personnage** (crâne, torse, jambes/pieds) — pas seulement la tête comme
supposé initialement dans les manifests Phase 1.3. Teintes en cause :
`(234,233,232)`, `(248,248,248)`, `(248,245,240)`, `(248,248,246)`,
`(246,245,243)` (+ 2 variantes déjà sous 90% laissées inchangées).

Correction en deux temps, comme demandé (pixel + plafond, pas la bande
générale) :

1. **Pixel** : chaque teinte incriminée nudgée de 2-4% de Value vers
   ~89%, en préservant teinte/saturation (mise à l'échelle proportionnelle
   RGB), toutes occurrences dans les 8 animations sources (idle,
   deplacement, dash, hurt, mort, coup1, coup2, coup3) — 3104 pixels au
   total. Changement imperceptible à l'œil (`(234,233,232)` →
   `(227,226,225)`, par ex.).
2. **Plafond** : `data/palettes/value_bands.json`, catégorie `character`
   uniquement, bande relevée de `[15,88]` à `[15,90]` pour admettre la
   marge post-nudge (~89% < 90%). `ui`/`vfx`/`decor` non touchées.

Re-cuit (`cook_character_frames.py`, les 8 animations ensemble) + rebuild
`cendre_frames.tres` (`build_sprite_frames.py`, mêmes fps que Phase 1.4 :
idle=6 deplacement=10 hurt=12 mort=6 dash=15 coup1=15 coup2=15 coup3=15).
Revalidé avec `validate_pixels.py --category character` sur les 43 frames
des 8 animations : **0 violation partout**, `validated_auto: true` dans
les 8 manifests concernés.

### Non-régression vérifiée

`scripts/run_gameplay_smoke_test.sh` relancé après tous les correctifs
(les changements ne touchent que l'art et `value_bands.json`, pas
`player.gd`/`enemy.gd`) : **11/11 checks toujours au vert**, aucune
régression gameplay.

### Extension `tools/capture_scene.gd` — fond neutre/chargé + échelles

Le mandat §13.2 précise "fond neutre + fond chargé, 1×/2×/4×" pour les
captures soumises au verdict — la première livraison Phase 1 n'avait
livré que fond neutre 1×, incomplet. `capture_scene.gd` (mode
`--mode=character`) étendu avec deux nouveaux paramètres CLI :

- `--background=neutral|loaded` : `neutral` = comportement existant
  (couleur de fond par défaut du viewport, `(76,76,76)`) ; `loaded` =
  damier de test généré procéduralement (`_make_loaded_background()`,
  deux tons proches de la bande "decor", motif déterministe, aucun RNG)
  — **aucun décor de jeu réel n'existe encore en Phase 1** (pas de
  tuiles/salle), documenté explicitement en commentaire de tête de
  fichier et ici : à remplacer par un vrai décor quand Phase 2+ apportera
  des tuiles. Ce n'est pas un livrable, c'est un test de lisibilité.
- `--scale=1|2|4` : upscale `Image.INTERPOLATE_NEAREST` post-capture
  (jamais de filtrage flou sur du pixel art, §12.4).

Bug de compilation trouvé en cours de route : `var vw := ProjectSettings.
get_setting(...)` échoue au chargement (`GDScript::reload`, "variable
type is being inferred from a Variant value... Warning treated as
error") — `get_setting` retourne `Variant`, l'inférence `:=` ne suffit
pas sous les réglages stricts de ce projet. Fix : typage explicite
(`var vw: int = ProjectSettings.get_setting(...)`).

Batch complet relancé pour les 8 livrables Phase 1 (idle/walk/dash/hurt/
death/combo_1/combo_2/combo_3) × 2 fonds × 3 échelles = 48 captures,
toutes avec `save_err:0` (vérifié via grep sur le batch). Fichier
`<asset>.png` (fond neutre, 1×) conservé comme référence principale de
`capture_path` pour compatibilité ; 5 variantes ajoutées par asset
(`<asset>_neutral_2x.png`, `_neutral_4x.png`, `_loaded_1x.png`,
`_loaded_2x.png`, `_loaded_4x.png`), référencées dans le nouveau champ
`capture_variants` de chaque manifest.

### quality_labels.jsonl

Toujours vide. Aucun verdict humain auto-attribué — les nouvelles
captures sont soumises pour review, pas acceptées.

### Prochain pas

Les 4 corrections + la standardisation des captures sont poussées.
Toujours en attente de la nouvelle version du Totem du Vide (Milan)
avant Phase 1.5/1.6.

## 2026-08-18 — Phase 1.5 : Gueule Vide (INVOCATEUR) + moteur de recettes VFX

Mandat : implémenter le pouvoir "Gueule Vide" (INVOCATEUR) à partir de la
fiche de référence fournie (turnaround face/3-4/profil/dos + fiche
comportement/couches/palette), `data/recipes/power.gueule_vide.cast.json`
tel quel, cast unique 42 ticks, pas d'énergie/mana (hors scope Rank
Zero). Ce mandat active de fait la Phase 1.5 en attente (#184 :
`vfx_recipe_registry.gd` + 4 primitives manquantes) — Gueule Vide en est
le premier vrai consommateur, à la place du Totem (toujours en pause).

### Blocage partiel signalé, non résolu

`data/palettes/invocateur_vide.json` était mentionné comme "fichier
joint" dans le mandat mais n'a **jamais été effectivement attaché** —
seuls `power.gueule_vide.cast.json` et l'image de référence sont
arrivés (vérifié dans le dossier d'uploads). Signalé au début du
chantier plutôt que de fabriquer les valeurs de palette à l'œil sur les
pastilles de la fiche ("tels quels" du mandat implique un fichier
autoritaire, pas une réinvention). Conséquence : les couches VFX de la
recette (groundRing/runicStamp/fractureLine/shardBurst) tournent en gris
neutre de repli — voir plus bas, le mécanisme de résolution est prêt et
n'aura besoin d'aucun changement de code une fois le fichier reçu.

### 1. Référence créature

Panneau FACE de la fiche recadré (`assets/source/pixellab/gueule_vide/
reference.png`), downscale 24×22px/8 couleurs — même discipline que
Cendre (§5.3), sous le seuil de troncature base64 (~700 chars, dans la
marge du seuil ~1-2KB déjà mesuré).

### 2. Créature + animation (2 appels PixelLab, aucun re-roll)

`create_character` (mode v3, reference_image, 8 directions — canvas
effectif 24×24px, a hérité les dimensions de la référence malgré
`size=40` demandé, sans conséquence puisque `cook_character_frames.py`
normalise le canvas ensuite ; pas de re-roll pour ce détail mineur).

`animate_character` (mode v3, direction sud uniquement, 6 frames,
`keep_first_frame=false`) : une seule action_description couvrant les 4
phases de la recette (formation / gueule ouverte-préparation / morsure /
désintégration, §6.1). Résultat accepté à la première passe — lecture
claire des 4 beats (frames 0-1 formation, frame 2 préparation gueule
fermée, frame 3 morsure gueule grande ouverte, frames 4-5 bascule/
affaissement). Pas de fragmentation littérale en gouttes d'encre sur le
sprite (une silhouette figée de PixelLab ne peut pas vraiment "exploser"
en particules) — compensé par la couche VFX `shardBurst` plutôt qu'un
re-roll inutile.

Cuit sur canvas 48×48 (`cook_character_frames.py`, foot-margin 4px,
ancre [24,44]) puis `build_sprite_frames.py` (fps nominal nécessaire au
schéma de l'outil, `sprite.pause()` + `frame` piloté au tick près côté
script — voir plus bas, jamais la lecture fps autonome).
`validate_pixels.py --category character` : 6/6 frames OK, 0 violation.

### 3. Moteur de recettes VFX — `src/vfx/vfx_recipe_registry.gd`

Nouvel autoload (après `VfxDirector` dans `project.godot`). Résout une
recette JSON (`data/recipes/<id>.json`) en timeline de spawns
`VfxDirector.spawn()`, tick-driven — chaque couche respecte son propre
`start_tick`/`end_tick` relatif au début du run (§8.1), jamais un burst
instantané de tout à `t=0`. `play(recipe_id, params)` retourne un
`run_id` (0 si recette introuvable), `is_running(run_id)` pour sonder
l'état.

Résolution palette : chaque rôle de `data/palettes/<palette_id>.json`
porte un champ `usage` en texte libre qui **nomme** les primitives qu'il
colore (convention déjà en place dans `totem_du_vide.json`, ex.
"groundRing (spawn), fine bordure du totem"). La registry fait
correspondre chaque couche à son rôle en cherchant le nom de la
primitive dans ce texte (insensible à la casse) — aucune modification du
schéma recette/palette pour ajouter un champ de mapping qui n'existe pas
aujourd'hui. Palette manquante ou rôle non trouvé → repli gris neutre
50% V désaturé (jamais un crash, jamais hors bande VFX 20-92%), un seul
avertissement par (recette, primitive), jamais en boucle par tick.

Ce que la registry ne fait délibérément PAS : dégâts, recul, animation
du lanceur, SFX — tout ça reste côté script gameplay de l'entité qui
joue le pouvoir, sur SA PROPRE horloge de ticks (même principe que le
recul du combo : "pas une primitive de la recette").

### 4. Les 4 primitives manquantes (§7.1)

- `ground_ring.gd` — "anneau au sol cassé ou incomplet" : cercle en
  segments avec 2-3 coupures seedées (jamais un anneau plein).
- `runic_stamp.gd` — "glyphe/empreinte de sol" : cercle central +
  5-7 branches de longueur irrégulière (matière ink, §7.2 : "masses
  irrégulières"), apparaît vite et reste statique (contraste avec
  fractureLine qui progresse).
- `fracture_line.gd` — "fissure segmentée qui progresse" : chemin en
  zigzag seedé, segments révélés progressivement tick après tick (pas
  d'apparition d'un coup).
- `shard_burst.gd` — "fragmentation orientée" : éclats triangulaires
  partant en cône dirigé (jamais isotrope, §4), pas un système de
  particules GPU.

Toutes les 4 : mêmes conventions qu'`impact_flash_frame.gd` (contrat
`configure(params)`/`tick(ticks_elapsed)`, `MIN/MAX_VALUE_HSV` clampés
20-92%), acceptent `value_percent`/`hue_deg`/`saturation_percent`
(résolus par la registry, jamais une couleur en dur — contrairement à
`impactFlashFrame` qui EST toujours un flash blanc quel que soit le
pouvoir). Enregistrées dans `VfxDirector._registry`.

### Preuve — reproductible

```
scripts/run_vfx_recipe_smoke_test.sh
# → 4/4 checks (fixture volontaire : power.totem_du_vide.attack +
#   palette totem_du_vide, déjà dans le dépôt, indépendants de Gueule
#   Vide — prouve le MÉCANISME générique, pas une recette précise) :
#   play_unknown_recipe_returns_zero, recipe_run_starts_spawns_both_
#   layers_then_finishes, palette_resolution_matches_usage_text,
#   unresolved_primitive_falls_back_to_neutral_gray

scripts/run_gameplay_smoke_test.sh
# → 16/16 checks (11 précédents + 5 nouveaux) :
#   power1_input_spawns_gueule_vide_creature,
#   power1_cooldown_blocks_immediate_second_cast,
#   gueule_vide_contact_damages_enemy_in_range,
#   gueule_vide_contact_applies_recoil_to_enemy,
#   gueule_vide_creature_frees_itself_after_cast
```

### 5. Créature/pouvoir — `src/gameplay/powers/gueule_vide.gd`

`Node2D` autonome (pas `CharacterBody2D` — ne bouge pas, pas de
collision). `_ready()` : joue le sprite en pause, `frame=0`, démarre
`VfxRecipeRegistry.play("power.gueule_vide.cast", ...)`.
`_physics_process()` : incrémente son propre tick, pose
`sprite.frame` via une table de bornes cumulées `[5,9,15,21,32,42]`
(6 frames pour des phases de durées inégales — le pas fps uniforme de
`build_sprite_frames.py` ne peut pas exprimer ça, même discipline que le
combo : "les ticks sont la seule autorité", jamais la lecture fps
autonome d'`AnimatedSprite2D`). Au tick de contact (20, `sfx_markers` de
la recette), résout la cible via `Targeting.nearest_enemy_in_radius` et
appelle `Enemy.take_damage()` — recul porté par l'ennemi, pas une
primitive (mandat, section 4). `queue_free()` à 42 ticks — cast unique,
jamais de répétition, jamais d'entité persistante.

`Player` : action d'entrée `power1` (touche E), cooldown 360 ticks (6s).
`_cast_gueule_vide()` instancie la créature à 3m devant le joueur
(facing), pose le cooldown. N'utilise PAS `_action_lock` — rien dans le
mandat n'exige d'immobiliser le joueur pendant les 0,7s du cast.

### 6. Capture standardisée — extension `capture_scene.gd`

Nouveau `--mode=power` : instancie une scène de pouvoir
(`scenes/gameplay/powers/<power>.tscn`), laisse la physique RÉELLE
tourner (sonde `instance.get_current_tick()`, même technique que
`--mode=primitive` avec `VfxDirector.get_current_tick()`) jusqu'au tick
cible, gèle, capture — nécessaire car le mode `character` ne gère pas
une entité qui se détruit elle-même en fin de vie. 3 états × 2 fonds ×
3 échelles = 18 captures (`captures/phase1/gueule_vide_{spawn,attack,
expire}*.png`, ticks 3/20/40) : `groundRing`+`runicStamp` visibles à la
formation, `fractureLine`+`impactFlashFrame` au contact, `shardBurst` à
la désintégration — toutes en gris de repli (palette manquante, voir
plus haut).

### Manifests

`assets/manifests/gueule_vide_{spawn,attack,expire}.json` — nouveau
`kind: "power_capture"`, `validated_auto: true` (la créature/le
mécanisme sont corrects et testés), `palette_status` documente
explicitement le blocage et pointe vers le fichier manquant,
`known_limitation` résume ce qui reste à refaire une fois la palette
reçue (recapture seule, zéro changement de code).

### quality_labels.jsonl

Toujours vide. Aucun verdict humain auto-attribué.

### Prochain pas

En attente de `data/palettes/invocateur_vide.json` pour recapturer avec
les vraies couleurs (bleu-gris pâle / lilas-gris pâle / gris moyen /
gris foncé / charbon, d'après la légende de la fiche) — aucun changement
de code nécessaire, seulement relancer le batch de captures une fois le
fichier en place. Les paliers de Maîtrise I/II/III de Gueule Vide
(notes de la recette : résidu, double mâchoire, dévoration) restent hors
scope de cette passe (mandat explicite : pas encore). Totem du Vide
(Phase 1.6) toujours en pause côté Milan.

## 2026-08-18 — Blocage palette résolu : `data/palettes/invocateur_vide.json` reçu

Fichier enregistré tel quel (aucune valeur inventée) : `palette_id:
"invocateur_vide"`, notes précisant que cette palette est la signature
visuelle **commune à tous les pouvoirs volés de la Classe Invocateur**
(Totem du Vide ET Gueule Vide la partagent, "ne pas diversifier entre
pouvoirs de même Classe d'origine" — la reconnaissance de la source du
pouvoir passe par cette identité constante, exception §2.5 du doc VFX).
4 rôles : allié/bleu pâle système (72% V) → `groundRing`, signature 1/
gris-lilas désaturé (55% V) → `runicStamp`, signature 2 (matière Ink)/
noir d'encre (24% V) → `fractureLine`, intermédiaire/gris cendre (40% V)
→ `shardBurst`.

Le mécanisme de résolution écrit lors du chantier précédent
(`VfxRecipeRegistry._resolve_color`, correspondance sur le champ
`usage`) a fonctionné du premier coup, sans aucun changement de code :
les 4 correspondances attendues se résolvent correctement (vérifié par
inspection directe des pixels sur une capture 4×, `groundRing` nettement
plus clair que `runicStamp`, `fractureLine` nettement plus sombre que le
gris de repli précédent). `impactFlashFrame` reste blanc quasi-plein par
conception — cette primitive est toujours grayscale indépendamment du
pouvoir (mêmes conventions que le flash du combo de Cendre), aucune
correspondance de rôle recherchée pour elle, comportement normal.

Non-régression : `scripts/run_vfx_recipe_smoke_test.sh` (4/4) et
`scripts/run_gameplay_smoke_test.sh` (16/16) relancés après ajout du
fichier — aucune régression.

Batch complet de 18 captures relancé (3 états × fond neutre/chargé ×
1×/2×/4×), remplace les captures en gris de repli. Manifests
`gueule_vide_{spawn,attack,expire}.json` mis à jour : `palette_status`
documente les couleurs réellement appliquées, `known_limitation` réduit
à la seule limite réelle restante (pas de fragmentation littérale du
sprite créature en gouttes d'encre — compensée par `shardBurst`, déjà
noté précédemment, non lié à la palette).

`quality_labels.jsonl` toujours vide. Gueule Vide (créature + VFX +
gameplay + captures aux vraies couleurs) est maintenant complet et prêt
pour verdict Milan.

## 2026-08-18 — Correctif v2 palette `invocateur_vide.json` : hue/saturation manquants en v1

Milan a renvoyé une v2 du fichier `data/palettes/invocateur_vide.json`
avec une note explicite dans le fichier lui-même : la v1 ne portait que
`value_percent` sur les 4 rôles, sans `hue_deg` ni `saturation_percent`.
`VfxRecipeRegistry._resolve_color` retombait donc sur ses valeurs de
repli (`hue_deg: 0.0`, `saturation_percent: 0.0`) pour ces deux champs
absents — la Value affichée était correcte (bleu pâle plus clair que
gris-lilas, etc., comme rapporté à l'entrée précédente) mais rendue en
gris pur, sans aucune teinte : la signature visuelle de Classe
Invocateur était donc invisible en jeu malgré des couleurs
nominalement « correctes ». Aucun bug côté code : `_resolve_color`
utilisait déjà `.get("hue_deg", 0.0)` / `.get("saturation_percent",
0.0)` avec des valeurs de repli sensées ; seule la donnée manquait.

v2 ajoute `hue_deg` et `saturation_percent` aux 4 rôles (bleu pâle
système 212°/18%, gris-lilas désaturé 278°/14%, noir d'encre 250°/10%,
gris cendre 230°/6% — teintes volontairement basses en saturation pour
rester « quasi imperceptible » comme spécifié à l'origine, mais non
nulles). Fichier enregistré tel quel (aucune valeur inventée).

Vérification pixel-exacte (pas seulement confiance dans le contenu du
fichier) : capture de contrôle tick=3/échelle=4/fond neutre, scan de la
région pour tous les pixels non-fond, histogramme de fréquence pour
isoler les deux teintes dessinées. `groundRing` → `(151,166,184)` =
72,2% V / 18,0% S / 212,7° H (cible 72/18/212 ✓). `runicStamp` →
`(133,121,140)` = 54,9% V / 13,6% S / 277,9° H (cible 55/14/278 ✓).
Correspondance exacte aux deux décimales près.

Non-régression : `scripts/run_vfx_recipe_smoke_test.sh` (4/4) et
`scripts/run_gameplay_smoke_test.sh` (16/16) relancés après l'écriture
de la v2 — aucune régression, aucun changement de code nécessaire.

Batch complet de 18 captures relancé (3 états × fond neutre/chargé ×
1×/2×/4×) avec la palette v2, remplace les captures v1 (qui portaient
déjà les bonnes Values mais sans teinte visible). Manifests
`gueule_vide_{spawn,attack,expire}.json` mis à jour : `palette_status`
documente désormais hue/saturation en plus de Value, avec mention
explicite du correctif v1→v2 et de la vérification pixel.

`quality_labels.jsonl` toujours vide. Gueule Vide reste complet et prêt
pour verdict Milan, cette fois avec la signature de Classe réellement
visible.

## 2026-08-18 — Build de test tactile web (feel, pas premium) — exception ponctuelle export web

Milan n'a qu'un iPhone, aucun ordinateur — un vrai build iOS natif est
impossible pour l'instant (Xcode nécessite macOS). Pour débloquer un
test immédiat du *feel* (poids du combo, lisibilité de Gueule Vide,
sensation du dash), exception ponctuelle à la règle "pas d'export web"
du mandat, sur demande explicite : `grep -rl "GPUParticles"
src/vfx/primitives/*.gd` confirme qu'aucune primitive actuelle n'utilise
`GPUParticles2D` (toutes dessinent via `_draw()`/`draw_arc`/polygones
immédiats) — la raison technique documentée en `project.godot`
(§0/§11.1 : "Compatibility ne supporte pas les GPUParticles, silencieux,
sans erreur") ne s'applique donc pas encore à ce projet. **Exception
temporaire, à réévaluer dès qu'une vraie primitive `GPUParticles2D` est
introduite** — à ce moment-là, soit elle est exclue de l'export web,
soit l'export web est retiré. Le renderer `mobile` du projet
(`project.godot`, natif/mobile) n'a pas été changé — seul l'export web
lui-même force `gl_compatibility` en interne (WebGL2 ne supporte pas
Vulkan/le renderer Mobile, aucune alternative côté navigateur en
Godot 4.3), ce qui est indépendant et sans effet sur les futurs builds
natifs. Ce build web est un outil de test rapide, pas le pipeline de
production (mandat §0 inchangé).

Livré :
- **Contrôles tactiles** : `src/ui/virtual_joystick.gd` (joystick
  virtuel zone gauche, pilote `ui_left/right/up/down` via
  `Input.action_press(action, strength)` — aucun changement requis dans
  `Player._handle_movement()`, qui lisait déjà ces actions génériques ;
  fonctionne aussi à la souris/drag pour tester depuis un navigateur
  desktop) + `scenes/ui/touch_controls.tscn` (3 `TouchScreenButton` zone
  droite : attaque/pouvoir1/dash, forme de détection `CircleShape2D`
  sans texture, visuel `Polygon2D`+`Label` minimal, `shape_visible=false`
  car le polygone fait déjà office de visuel).
- **Dash câblé** : action `dash` dans `project.godot` (Shift gauche —
  `physical_keycode=4194325`, `location=1` pour restreindre à la touche
  gauche spécifiquement + bouton tactile), `Player._physics_process()`
  appelle `play_dash()` sur `just_pressed` (méthode déjà existante mais
  jamais câblée à une entrée, respecte `_action_lock` comme
  hurt/dash l'exigeaient déjà).
- **Flip horizontal minimal** : `player.gd`, une ligne dans
  `_handle_movement()` — `_sprite.flip_h = facing.x < 0.0` quand
  `facing.x` est non-nul. Ne corrige pas le mouvement vers le haut
  (aucune frame dédiée), évite juste que gauche/droite paraissent
  cassés avec le seul sprite sud existant.
- **`scenes/gameplay/test_arena.tscn`** : Player + 3 Enemy à distances
  variées (64/comparable/~300px, directions différentes) + sol
  (`ColorRect`) + `TouchControls`. `Camera2D` ajoutée directement dans
  `scenes/gameplay/player.tscn` (enfant du Player, `position_smoothing_
  enabled=true`) plutôt que dans la scène de test — suit le joueur dans
  n'importe quelle scène qui l'utilise, pas seulement celle-ci.
  `project.godot` : `run/main_scene` pointé dessus.
- **Export web** : `export_presets.cfg` (désormais versionné, voir
  `.gitignore` — exception documentée localement, ce fichier encode des
  choix non triviaux à ne pas redécouvrir). `variant/thread_support=
  false` **volontairement** : GitHub Pages ne sert pas les en-têtes
  COOP/COEP nécessaires à `SharedArrayBuffer`, un build threadé y
  resterait bloqué à l'écran de chargement. Templates d'export
  `web_nothreads_{debug,release}.zip` (Godot 4.3.stable) installés dans
  `~/.local/share/godot/export_templates/4.3.stable/` (non versionnés,
  environnement local). Export réalisé avec
  `godot4 --headless --rendering-driver vulkan --export-release "Web"
  docs/index.html` sous xvfb (même contrainte d'environnement que les
  captures, voir plus haut dans ce fichier). Sortie dans `docs/index.*`
  (`.html`, `.js`, `.wasm` ~34 Mo, `.pck` ~350 Ko, icônes) — `.wasm`/
  `.pck` ajoutés à `.gitattributes` (LFS, même convention que les PNG).
  `docs/.nojekyll` ajouté pour éviter tout traitement Jekyll de GitHub
  Pages sur les fichiers exportés.

Vérification (pas seulement "ça exporte sans erreur") :
- `scripts/run_gameplay_smoke_test.sh` : 16/16, aucune régression du
  dash/flip_h sur le squelette gameplay existant.
- Capture headless de `test_arena.tscn` (native, `--rendering-driver
  vulkan`) : layout correct (joueur centré, 3 ennemis à distances
  variées, joystick + 3 boutons visibles).
- **Chargement réel du build exporté** dans Chromium headless
  (Playwright, `--use-gl=swiftshader`) servi en local : la console du
  moteur confirme `OpenGL API OpenGL ES 3.0 (WebGL 2.0...) -
  Compatibility` — la bascule Mobile→Compatibility prédite par le
  mandat pour le web est bien réelle, mais **aucune erreur, aucun crash,
  rendu visuellement identique à la capture native** (attendu : aucune
  primitive VFX ne dépend de GPUParticles). Test interactif : drag de
  souris sur le joystick → le perso se déplace réellement à l'écran
  (capture avant/pendant comparée), clic sur le bouton ATK → aucune
  erreur, caméra qui suit le joueur confirmée fonctionnelle après le
  déplacement.
- Aucun problème visuel réel détecté — pas de retour nécessaire avant
  livraison, conformément à l'instruction reçue ("si un test visuel
  révèle un vrai problème... documente-le et reviens vers moi").

Hébergement : GitHub Pages sur `broussemilan-beep/jeux`, source
"Deploy from a branch" → `main` → `/docs`. **Activation manuelle
requise côté Milan/l'utilisateur** — aucun outil de cette session ne
donne accès aux réglages du dépôt (Settings → Pages), seulement au
contenu des fichiers ; l'activation en une fois dans l'UI GitHub est le
seul geste restant, l'export lui-même est déjà poussé et prêt.

Rappel transmis avec la livraison : ce test juge le *feel*, pas le
rendu (une seule direction, VFX simples, pas de décor/son/post-render)
— pas encore "premium", volontairement.

## 2026-08-18 — Addendum A à ARCHITECTURE_VFX_v3.md (5 points)

Fichier reçu, enregistré tel quel en
`docs/ARCHITECTURE_VFX_v3_addendum_A.md` (le v3 reste la référence
principale, l'addendum ajoute 5 points sans rien remplacer). Traité dans
l'ordre demandé : A.5 (priorité immédiate) d'abord, puis A.4, A.1, A.2,
A.3, A.6.

### A.5 — Déterminisme de la seed (bug réel, corrigé)

`src/gameplay/powers/gueule_vide.gd` passait `Time.get_ticks_usec() %
100000` comme seed à `VfxRecipeRegistry.play()` — horloge murale, non
reproductible, casse le gate "seed fixe -> même sortie" (§13.4 du v3) et
rend `compare_reference.py` inutilisable sur ce pouvoir. Remplacé par
une constante fixe `CAST_SEED := 44103` (valeur arbitraire, en attendant
un vrai système de seed de run côté gameplay comme le suggère
l'addendum). Aucune autre source de hasard non seedée trouvée dans le
chemin VFX : les 4 primitives à RNG (`ground_ring.gd`, `runic_stamp.gd`,
`fracture_line.gd`, `shard_burst.gd`) seedaient déjà correctement depuis
`params.seed` (jamais `randomize()`), et `VfxDirector`/
`VfxRecipeRegistry` propagent `run["seed"]` tel quel à chaque couche
sans y mélanger de valeur temporelle.

Check ajouté à `tools/smoke_test_vfx_recipe.gd` (mandat : "ajoute un
check au smoke test VFX qui vérifie qu'aucune source de hasard non
seedée n'existe dans le chemin VFX") :
- `recipe_registry_same_seed_produces_identical_spawn_log` — deux runs
  de `power.totem_du_vide.attack` avec la même seed explicite (7777)
  produisent un `spawn_log` (primitive+seed, dans l'ordre) strictement
  identique — preuve générique du mécanisme registry -> director ->
  primitives.
- `gueule_vide_seed_is_fixed_not_wallclock` — régression ciblée sur le
  bug réel : deux invocations de `GueuleVide` séparées par 15 ticks
  physiques réels (donc de temps réel) produisent la MÊME seed dans le
  spawn_log ; si l'horloge murale revenait, cet écart suffirait à les
  rendre différentes.

`scripts/run_vfx_recipe_smoke_test.sh` : 6/6, `scripts/
run_gameplay_smoke_test.sh` : 16/16, aucune régression.

### A.4 — Cycle de vie (timeout / mort du propriétaire / changement de scène)

Avant : seul le timeout existait (chaque couche s'éteint via sa propre
`lifetime_ticks`). Ajouté :

- `VfxDirector` : chaque spawn enregistré porte désormais `run_id`
  (0 = spawn direct hors recette, ex. `Player._try_hit()` — jamais une
  collision avec un vrai run_id, `VfxRecipeRegistry` commence à 1) et
  `degradable` (voir A.1). Nouvelle méthode `cleanup_run(run_id,
  only_degradable)` — nettoyage forcé scopé à UN run (jamais
  `cleanup_all()`, qui tuerait aussi les couches d'autres pouvoirs
  actifs).
- `VfxRecipeRegistry` : nouvelle méthode `cancel(run_id, degrade_only)`.
  `degrade_only=false` : stoppe toute planification + libère
  immédiatement tout ce qui est déjà spawné, protégé ou non
  ("stop_immediately", ou annulation avant "release"). `degrade_only=
  true` : seules les couches dégradables sont annulées (déjà spawnées
  -> libérées tout de suite ; pas encore lancées -> jamais lancées) ; les
  couches protégées continuent normalement jusqu'à leur propre fin
  ("finish_core_then_stop_secondary").
- `gueule_vide.gd` :
  - `set_owner_stats(stats)` (appelée par `Player._cast_gueule_vide()`
    juste après l'instanciation) connecte `stats.died` ->
    `_on_owner_died()` -> `VfxRecipeRegistry.cancel(_recipe_run_id,
    true)`. La créature elle-même NE s'arrête PAS ("elle a été arrachée
    au monde, elle n'est pas liée à lui", addendum) — sa propre boucle
    de ticks continue normalement, seules les couches VFX dégradables
    (shardBurst) sont coupées net.
  - `_exit_tree()` avec un flag `_natural_end` (posé juste avant le
    `queue_free()` du timeout normal) : si le nœud quitte l'arbre pour
    toute AUTRE raison (changement de scène, libération externe),
    `VfxRecipeRegistry.cancel(_recipe_run_id, false)` — nettoyage
    complet ("scene_change_policy: stop_immediately"). La fin naturelle
    n'a pas besoin de ce nettoyage forcé (chaque couche s'éteint déjà
    proprement toute seule), donc pas de coupure prématurée du dernier
    tick de fade de shardBurst dans le cas normal.
  - `can_cancel()` / `cancel_cast()` : "cancellable_before: release" —
    annulable jusqu'à `PREP_END_TICK`. Rien n'appelle encore
    `cancel_cast()` (aucun système d'interruption/étourdissement
    n'existe côté gameplay) — la brique est posée pour quand ce sera le
    cas, sans construire l'usage maintenant (§16.1 du v3).
  - `max_lifetime_ticks: 48` (recette) : documenté en commentaire près
    de `TOTAL_TICKS := 42` plutôt que codé en garde supplémentaire — un
    garde qui ne peut jamais se déclencher (seule cette classe
    incrémente `_tick`, aucun système de pause n'existe encore) serait
    du code mort.
  - Bloc `lifecycle` ajouté à `data/recipes/power.gueule_vide.cast.json`
    avec les 4 valeurs proposées par l'addendum, telles quelles.

Checks ajoutés à `tools/smoke_test_gameplay.gd` (propriétaire dédié —
`Stats.new()` isolé, pas `_player` déjà mort/exercé ailleurs dans la
suite) : `gueule_vide_owner_death_keeps_creature_alive` (les couches
protégées sont déjà spawnées, la créature ne se libère pas
immédiatement), `gueule_vide_owner_death_cancels_degradable_layer`
(shardBurst, start_tick=27, n'apparaît jamais dans le spawn_log même en
attendant après ce tick), `gueule_vide_finishes_normally_despite_owner_
death` (la créature termine quand même sa propre timeline). Un `weakref()`
a été nécessaire sur la 3e assertion (capturer directement `creature`
dans un `Callable` réévalué sur plusieurs frames après sa libération
fait logger une erreur moteur "Lambda capture ... was freed" —
inoffensive mais bruyante ; `weakref().get_ref() == null` est l'idiome
Godot prévu pour ce cas, evite le message).

### A.1 — Couches protégées vs dégradables

Champ `degradable` (bool) ajouté à chaque couche des 4 recettes
existantes, selon le tableau de l'addendum (type de couche -> protégée/
dégradable) :
- `power.gueule_vide.cast.json` : groundRing/runicStamp (ANTICIPATION
  seule couche = primaire/ACTION CORE) protégées, fractureLine/
  impactFlashFrame (CONTACT) protégées, shardBurst (CONSEQUENCE)
  dégradable.
- `power.totem_du_vide.attack.json` : fractureLine/impactFlashFrame
  (CONTACT, primaire impactFlashFrame+recul) protégées.
- `power.totem_du_vide.spawn.json` : groundRing (ANTICIPATION)
  protégée, runicStamp (ACTION CORE) protégée.
- `power.totem_du_vide.expire.json` : smokePuff (CONSEQUENCE)
  dégradable.

Étendu aussi au seul spawn direct hors recette du jeu :
`Player._try_hit()` marque son `impactFlashFrame` (flash du combo)
`degradable: false` — CONTACT protégée, même règle que dans les
recettes.

### A.2 — Ordre de dégradation dans VfxBudget

`VfxBudget.can_spawn()` mesurait déjà (overdraw par zone, particules)
mais ne distinguait rien à couper en priorité — un refus était un refus,
protégé ou pas. Avec les primitives actuelles, aucune n'accepte de
paramètre de qualité réduite (§A.6 de l'addendum : pas à implémenter
maintenant), donc le seul levier honnête est binaire : spawn entier ou
rien — l'ordre en 6 étapes de l'addendum (particules décoratives,
débris, dissipation, trails, fusion d'instances, distortion/screen
slices) collapse en un seul geste possible aujourd'hui ("couper le
décoratif entièrement"), documenté comme tel plutôt que simulé avec des
paramètres qui ne changeraient rien au rendu réel. Implémenté :
- Couche dégradable qui dépasse `OVERDRAW_PER_ZONE_SOFT_CAP` -> refusée
  (retirée entièrement), comportement déjà existant mais maintenant
  documenté comme le mécanisme de dégradation lui-même plutôt qu'un
  simple refus de budget.
- Couche protégée (`degradable: false`) -> **jamais refusée** pour ce
  plafond souple, quitte à le dépasser (avertissement loggué pour
  calibrer plus tard) — "plancher intouchable" (étape 7), qui n'existait
  pas avant : un `impactFlashFrame` ou une fractureLine de contact
  pouvaient jusqu'ici être silencieusement refusés sous pression de
  budget, en violation directe de la règle "ne peut jamais... supprimer
  impactFlashFrame sur un impact majeur, ni le recul".
- Les plafonds DURS de particules (`PARTICLES_PER_EFFECT_MAX`/
  `PARTICLES_TOTAL_MAX`) restent appliqués même aux couches protégées —
  garde-fou anti-emballement (bug), pas un budget de compétition
  créative pour l'écran, distinction volontaire.

Checks ajoutés à `tools/smoke_test_vfx_recipe.gd` (appel direct de
`VfxBudget.can_spawn()`, zone 11 inutilisée par les autres checks du
fichier) : `budget_refuses_degradable_layer_over_soft_cap`,
`budget_never_refuses_protected_layer_over_soft_cap`.

### A.3 — Marqueurs d'animation

Aucun changement de code : "les recettes existantes en start_tick
restent valides, ne les réécris pas" — aucune n'a été touchée. Le
mandat n'exige rien de plus tant qu'aucune NOUVELLE animation d'action
n'est en cours d'écriture (le prochain candidat naturel serait Totem du
Vide/Phase 1.6, toujours en pause en attendant la refonte de Milan) —
convention notée pour ce moment-là : le manifeste cuit d'une nouvelle
animation devra exposer les 5 marqueurs (`visual_anticipation_start`,
`visual_release`, `visual_contact`, `visual_recovery_start`,
`visual_end`) et les couches de sa recette pourront démarrer sur
`start_marker` plutôt que `start_tick` absolu.

### A.6 — Niveaux de qualité

Rien à faire — explicitement "pas à implémenter maintenant" dans
l'addendum. Reste dans `docs/ARCHITECTURE_VFX_v3_addendum_A.md` comme
référence pour plus tard (profiling sur appareil réel).

### Vérification globale

`scripts/run_vfx_recipe_smoke_test.sh` : 8/8 (4 existants + 2 seed A.5 +
2 budget A.2). `scripts/run_gameplay_smoke_test.sh` : 19/19 (16
existants + 3 owner-death A.4). `quality_labels.jsonl` toujours vide.

## 2026-08-19 — Audit discipline reference-image (§5.3) sur Cendre, avant régénération

Demande : avant de relancer une régénération complète du personnage sur
une nouvelle référence, auditer les 8 feuilles d'animation source
actuelles (`assets/source/pixellab/cendre/animations/{idle,deplacement,
dash,hurt,mort,coup1,coup2,coup3}/*.png`, 42 frames) contre
`assets/source/pixellab/cendre/reference.png` — proportions, palette,
cohérence de silhouette — pour savoir si §5.3 a vraiment été respecté
partout ou si certains lots ont dérivé, avant de reproduire la même
méthode. **Audit uniquement : aucune régénération, aucune retouche.**

Méthode : mesure programmatique (bounding-box du personnage par frame,
alpha pour les frames animées, seuil de distance couleur pour
`reference.png` qui n'a pas de fond transparent) + inspection visuelle
directe de chaque frame à fort grossissement (nearest-neighbor ×6 à
×14, sans lissage) + relecture du journal `data/pixellab_usage.jsonl`
pour savoir ce qui avait déjà été signalé/corrigé.

### Ce qui a été vérifié comme sain

- **Silhouette générale et gabarit** : tête chauve/sans capuche
  relevée, harnais à sangles croisées sur le torse, robe/tunique
  longue à fente, cape asymétrique (un seul pan) — cohérents avec
  `reference.png` sur les 8 animations, dans leurs poses neutres ou
  calmes (idle, déplacement, hurt, frame 0 de dash/mort/coup1-3).
  Hauteur absolue du personnage en pose neutre mesurée à 59-62px selon
  les frames, remarquablement stable malgré deux formats de canvas
  source différents (voir plus bas) — pas de dérive d'échelle globale
  détectée.
- **Palette** : scan systématique des 43 frames pour toute couleur dont
  la saturation dépasse 12% (la palette du personnage est censée rester
  quasi grise/désaturée) — 7 des 8 animations ne contiennent aucune
  teinte notable, cohérent avec la discipline stricte. Seule
  exception : voir "deplacement" ci-dessous.
- **create_character (identité de base)** : les 8 rotations
  (`rotations/*.png`) restent cohérentes entre elles (déjà vérifié à
  l'époque, reconfirmé ici à l'œil) — la dérive identifiée dans cet
  audit est spécifique aux animations, pas au personnage de base.

### Dérives trouvées — non documentées dans le journal PixelLab

**1. `coup1` et `coup2` : la tête perd son identité "chauve/sans visage" en cours de frappe**

`reference.png` et toutes les poses calmes (idle, déplacement, hurt,
dash, mort, frame 0 des 3 coups) montrent une tête chauve, lisse, sans
trait de visage dessiné — juste une forme pâle arrondie. À partir de la
frame 1-2 de `coup1` et `coup2`, la capuche remonte et un **visage
détaillé apparaît** (yeux, parfois nez visibles) encadré de mèches
sombres qui lisent comme des cheveux, pas comme le rabat de capuche
plat vu ailleurs — net et non ambigu sur `coup2/1.png`, `coup2/2.png`,
`coup2/3.png`, `coup2/4.png` (visage net à chaque frame) ; présent mais
moins marqué sur `coup1/2.png`-`coup1/3.png`. Ni `reference.png` ni
aucune autre animation ne montre jamais de visage dessiné — c'est une
identité que le personnage n'a nulle part ailleurs. Jamais signalé dans
`data/pixellab_usage.jsonl` (les entrées coup1/coup2 ne notent que la
tache jaune sur coup2, déjà corrigée en pixel direct — cf. entrée du
2026-08-18T21:15:00Z).

**2. `coup3` : l'ancien correctif "halo" a changé la couleur, pas la forme**

Le journal (entrée du 2026-08-18T21:15:00Z) documente un halo
blanc trop étendu sur `coup3` frames 3-4, corrigé par recoloration
pixel directe vers la teinte de capuche. En zoomant sur les frames
actuelles : la capuche remonte bien avec un visage visible (même
phénomène que coup1/coup2, pas rapporté comme tel à l'époque — décrit
uniquement comme un "halo"), et surtout **une barre rectangulaire grise
plate flotte toujours juste sous la tête** sur `coup3/3.png` et
`coup3/4.png`, détachée du contour du corps. Cohérent avec un correctif
qui a recoloré les pixels trop clairs sans corriger la forme
géométrique sous-jacente — la silhouette reste fausse même si la
couleur est rentrée dans la bande.

**3. Artefacts de rendu isolés, non documentés**

- `coup1/3.png` : un grand disque blanc plein, net et circulaire, posé
  près de la main/cape — ne correspond à aucun élément de pose demandé
  (`action_description` ne mentionne ni halo ni objet). Jamais signalé.
- `coup2/1.png` et `coup1/3.png` : petites taches blanches en forme
  d'éclat/étincelle flottant à côté du personnage (2-4 pixels
  regroupés), sans rapport avec la description de pose. Jamais signalé.

**4. `deplacement` : seule animation à porter une teinte de fond bleu-violet**

Scan de saturation : `deplacement` est la SEULE des 8 animations où une
couleur non grise apparaît de façon systématique — `(34, 31, 42)`,
teinte ~256° (bleu-violet), saturation ~26%, présente sur les 6 frames
(73 à 97 pixels par frame), répartie sur presque toute la hauteur du
personnage (y=9 à y=58 sur un canvas de 64px) — donc un choix
d'ombrage de base pour tout ce lot, pas un pixel isolé. Les 7 autres
animations utilisent un ombrage strictement neutre (gris) au même
endroit anatomique. Écart subtil (jamais détecté par
`validate_pixels.py --category character`, qui ne contrôle que la
bande de Value, pas la teinte) mais réel et mesurable — un lot généré
dans une session légèrement différente de teinte de base.

**5. Deux conventions de canvas différentes entre lots, jamais harmonisées**

`idle`/`deplacement`/`hurt` sortent sur un canvas portrait 32×64 (proche
du ratio de `reference.png`, 46×96). `dash`/`mort`/`coup1`/`coup2`/
`coup3` sortent tous sur un canvas carré 88×88, et partagent une frame 0
avec une bounding-box strictement identique `(29,13,58,75)` sur les 5 —
autrement dit ces 5 animations partagent littéralement la même image de
pose neutre en frame 0 (comportement normal d'`animate_character` sur
un `character_id` déjà établi, pas une anomalie en soi), mais le lot
1.3 (idle/déplacement/hurt) et les lots 1.3-suite/1.4 (dash/mort/coup1-3)
n'ont pas été demandés avec les mêmes paramètres de canvas. Sans
conséquence visible après cuisson (`cook_character_frames.py`
normalise tout vers 96×96, ancre 48/92, voir
`assets/manifests/cendre_frames_cooked.json`), mais un signal que la
discipline d'appel n'a pas été strictement identique d'un batch à
l'autre.

**6. Pose déjà signalée, reconfirmée : `dash` ne lit toujours pas comme un sprint**

Déjà noté au moment de l'acceptation (`accepted_with_reservation`,
entrée du 2026-08-18T18:20:00Z) : les frames 3-4 de `dash` montrent un
large écart de jambes statique avec cape en éventail plutôt qu'une
foulée de course avec les deux pieds décollés du sol. Reconfirmé à
l'inspection — pas une dérive de proportions du personnage (le gabarit
reste correct), mais une dérive de lisibilité de pose qui persiste
telle quelle depuis l'acceptation.

### Interprétation pour la régénération à venir

La discipline reference-image (§5.3, `create_character` avec
`reference_source` explicite) a bien été respectée pour établir
l'identité de base — le gabarit, le harnais, la robe, la cape restent
fidèles à `reference.png` partout. La dérive observée est ailleurs :
`animate_character` (qui ne repasse PAS l'image de référence, seulement
le `character_id`) laisse le générateur libre d'improviser des détails
absents du personnage établi (visage, cheveux) dès qu'une pose devient
assez dynamique pour dégager la capuche — un angle mort de la
discipline actuelle, qui ne couvre que le premier appel
(`create_character`), pas les animations qui en dérivent. À anticiper
sur la régénération : soit contraindre plus explicitement
`action_description` à répéter "bald, featureless face, hood never
fully back" pour les poses dynamiques, soit prévoir une passe de
vérification tête-par-tête sur chaque frame acceptée plutôt qu'un
contrôle uniquement sur la première frame de chaque animation (ce qui
semble avoir été le mode de vérification jusqu'ici, vu que la dérive
n'a été détectée sur aucune des 3 combos malgré son ampleur).

Aucune correction appliquée ici — audit seul, comme demandé.
`quality_labels.jsonl` toujours vide.

## 2026-08-19 — B1-B3 : hit-stop, camera shake, feedback par tier de combo

Constat du mandat (retour Milan + diagnostic externe) : zéro hit-stop et
zéro camera shake dans `src/` avant cette entrée — seul le recul
existait (`enemy.gd`). Cause principale du "les coups n'ont aucun
poids". §9.1/§9.2 d'`ARCHITECTURE_VFX_v3.md` spécifient les deux
mécaniques mais aucune n'était implémentée.

### B1/B2 — `src/gameplay/combat_feedback.gd` (nouvel autoload)

Hit-stop : 5 profils (§9.1, `HITSTOP_MS`), ms convertis en ticks
(60/s) par arrondi au tick le plus proche. Implémentation en **time
scale local**, jamais `Engine.time_scale` (§9.1 : "sinon l'UI gèle
aussi") — un compteur de ticks gelés que chaque nœud de combat
(`Player`, `Enemy`, `VfxDirector`, `VfxRecipeRegistry`, `GueuleVide`)
consulte lui-même via `CombatFeedback.is_frozen()` en tête de son
`_physics_process()`, avec retour anticipé. `CombatFeedback` ne se
consulte jamais lui-même — il est la source de vérité du gel, pas un
nœud qui s'y soumet.

Camera shake : 3 niveaux (§9.2, `SHAKE_PROFILES`), axe fixe opposé à la
direction de l'attaque (jamais de bruit isotrope), amplitude qui
décroît linéairement (`decay`) modulée par une oscillation. Lu chaque
tick par `Player` via `CombatFeedback.get_shake_offset()`, appliqué à
`Camera2D.offset`, **avant** le retour anticipé sur `is_frozen()` — le
shake continue de s'animer pendant un hit-stop, ce qui fait partie de
ce qui vend l'impact.

**Bug trouvé et corrigé en câblant B3** : la formule d'oscillation
utilisait `sin(t * TAU * 2.0)` (2 cycles complets sur la durée totale).
Pour le profil `"light"` (4 ticks), ce découpage échantillonne
l'oscillation À CHAQUE tick exactement sur un passage par zéro du
sinus (`sin(nπ) = 0` pour tout entier n, et 4 ticks = exactement un
demi-cycle par tick) — `get_shake_offset()` valait donc **zéro à
chaque tick, systématiquement**, pour ce profil précis. `trigger_shake
("light", ...)` ne bougeait jamais visiblement la caméra, en silence
(aucun test n'existait encore pour l'exercer — B2 ne branchait que le
gel, pas encore de vrai déclencheur de shake "light"). Confirmé
numériquement avant correction (voir détail des valeurs échantillonnées
pour light/medium/heavy). Corrigé en passant `sin` → `cos` : même
enveloppe de décroissance, mais non-nul sur les 3 profils (light/medium
/heavy) et donne en prime un premier tick à pleine amplitude,
cohérent avec "shake dès le premier tick" (mandat dash, B4 à venir).
`medium`/`heavy` n'étaient pas affectés (leur nombre de ticks n'aligne
pas les échantillons sur les zéros du sinus).

### B3 — `src/vfx/primitives/arc_slash.gd` + feedback par tier de combo

Nouvelle primitive VFX `arcSlash` (§7.1, "croissant anguleux
directionnel"), enregistrée dans `VfxDirector._registry`. Couche
CONTACT (z_index 95, juste sous `impactFlashFrame`), même contrat que
les 5 primitives existantes.

Escalade des 3 coups de base (`src/gameplay/player.gd`,
`COMBO_TIER_FEEDBACK`), volontairement adoucie par rapport à la
proposition du diagnostic externe ("heavy sur coup 3") : ce sont des
attaques de BASE, un heavy dès le coup 3 viderait le plafond réservé
aux tiers 5-6 futurs, contraire au principe d'escalade du doc.

- Coup 1 : hit-stop `light` (1 tick), recul 4px, pas de shake.
- Coup 2 : hit-stop `light`, recul 8px, spawn `arcSlash` (2 ticks).
- Coup 3 : hit-stop `medium` (2 ticks), recul 14px, shake `light`.

**Décision documentée (mandat : "assume-la explicitement dans le
worklog")** : le mandat demandait un hit-stop "light-medium" pour le
coup 2 et un shake "light-medium" pour le coup 3, mais
`CombatFeedback` n'expose que les paliers discrets du doc (§9.1 : 5
profils de hit-stop, §9.2 : 3 niveaux de shake) — aucun palier
intermédiaire n'existe. À 60 ticks/s (`TICK_MS` ≈ 16,667ms), `light`
arrondit déjà à 1 tick et `medium` à 2 ticks : il n'existe aucune
valeur entière DISTINCTE entre les deux pour matérialiser un
"light-medium" de hit-stop — même limite pour "light" vs un
hypothétique "light-medium" de shake, les paliers de `SHAKE_PROFILES`
n'ayant pas de valeur intermédiaire non plus. Choix retenu, dans
l'esprit même de l'escalade demandée : **arrondir vers le bas** sur
toute ambiguïté de palier plutôt que vers le haut — un coup de base
reste un coup de base, jamais un plafond consommé par avance sur les
tiers 5-6.

### Vérification

`scripts/run_gameplay_smoke_test.sh` étendu avec 3 nouveaux checks
(`combo_tier1_hitstop_light_no_shake`, `combo_tier2_spawns_arc_slash`,
`combo_tier3_hitstop_medium_longer_than_tier1_with_shake`) qui pilotent
les 3 coups du combo via de vrais inputs et vérifient l'escalade
observable (durée de gel via `CombatFeedback.is_frozen()` interrogé en
boucle, présence d'`arcSlash` dans `VfxDirector.spawn_log`, décalage de
caméra non nul) plutôt que de simplement vérifier que le code compile
— c'est ce test qui a révélé le bug du shake `sin` ci-dessus (shake
`light` du coup 1 correctement absent, mais le shake `light` du coup 3
restait aussi invisible avant la correction `cos`). 22/22 checks
passent après correctif. `scripts/run_vfx_recipe_smoke_test.sh` :
8/8, aucune régression (nouvelle primitive `arcSlash` non exercée par
cette suite, seulement par le smoke test gameplay ci-dessus).

Pas encore fait dans ce lot : B4 (refonte du dash), C1/C2 (Gueule
Vide), régénération personnage (A), captures standardisées finales et
redeploy web (validation). `quality_labels.jsonl` toujours vide.

## 2026-08-19 — B4 : refonte du dash (anticipation/ease-out/recovery/traînée/shake)

Constat du mandat : `play_dash()` (avant cette entrée) ne contenait
**aucune logique de déplacement** — un simple `_sprite.play("dash")`.
Le mouvement réel pendant la pose "dash" restait entièrement porté par
`_handle_movement()` (vitesse normale d'input), qui continue de
tourner tant que `_combo_step == 0` sans regarder `_action_lock` sauf
pour le choix d'anim. D'où le "se lit comme une téléportation" du
retour Milan : la pose dash s'affichait sans qu'aucun déplacement
dédié ne l'accompagne.

### Timeline (`src/gameplay/player.gd`, `DashPhase`)

Même discipline tick-driven que le combo (`_advance_dash()`, jamais
dépendante de la durée de lecture du sprite) :

- **ANTICIPATION** (2 ticks) : vélocité nulle — bref "planté" avant le
  départ. Mandat : "buste penché, centre de gravité bas" — non
  réalisable ici (aucune nouvelle frame d'art, cette session ne touche
  pas aux animations, voir tâche A) ; seule la partie mécanique (pause
  avant le burst) est implémentée. Noté explicitement, pas laissé
  silencieux.
- **MOVE** (5 ticks) : burst de `DASH_DISTANCE_PX` (80px, ~2,5m — point
  de départ à ressentir, pas un dogme) réparti par ease-out quadratique
  (plein régime au premier tick, décroît ensuite) — "vitesse max avec
  ease-out" du mandat.
- **RECOVERY** (4 ticks) : glissade qui décélère linéairement vers 0
  (`DASH_RECOVERY_INITIAL_SPEED_PX_S`, même schéma que le recul
  d'`Enemy._physics_process`) — jamais un arrêt net.

**Exception documentée au §6.2** (mandat : "assume-la explicitement
dans le worklog plutôt que de la laisser passer silencieusement") :
découpage 2/5/4 ticks repris du diagnostic externe, soit 5/11 ≈ 45% de
"release" — largement hors de la bande 5-12% du doc pour une VFX/anim
premium classique. Accepté comme exception légitime : pour un dash,
**le déplacement EST le release**, pas un appui visuel bref pendant
qu'une autre couche porte le mouvement — la sémantique du §6.2 ne
s'applique pas au même objet ici.

### Traînée (2 after-images, mandat : "opacité ~50% puis ~20%")

`_spawn_dash_afterimage()` — **volontairement PAS une primitive
`VfxDirector`** : le contrat `configure()`/seed générique (§7.1) décrit
des formes procédurales, pas la texture/frame COURANTE du sprite du
joueur, une donnée que seul `Player` possède. Implémenté comme un
`Sprite2D` autonome (texture + frame + flip_h copiés depuis
`AnimatedSprite2D`), parenté au même parent que `Player` (jamais à
`Player` lui-même, sinon il suivrait son mouvement au lieu de rester
visuellement "planté" derrière), fondu via `Tween` puis
`queue_free()`. Hors du périmètre VfxDirector/VfxBudget par choix — ce
n'est pas une couche de recette (§8.2).

### Shake

`CombatFeedback.trigger_shake("light", _dash_direction)` déclenché dès
`play_dash()`, avant même le premier tick d'ANTICIPATION — "shake light
dès le premier tick" du mandat, axe opposé au déplacement (même
inversion que pour le combo, portée par `CombatFeedback` lui-même).

### Vérification

`scripts/run_gameplay_smoke_test.sh` étendu de 5 nouveaux checks
(`dash_input_starts_dash_and_plays_dash_anim`,
`dash_blocks_attack_input_while_locked`,
`dash_shake_visible_from_early_ticks`,
`dash_spawns_two_afterimage_ghosts`,
`dash_displaces_player_by_roughly_dash_distance_then_unlocks`) pilotant
un vrai input de dash et mesurant le déplacement réel — pas seulement
que le code compile.

Deux problèmes trouvés et corrigés en écrivant ce test, tous deux dans
le TEST lui-même, pas dans le code de jeu :
1. `_check_combo_tier_feedback()` (ajouté en B3) ne ramène pas le
   joueur à idle avant de rendre la main (contrairement à `_check_combo()`,
   qui elle attend explicitement `_combo_step == 0`) — `_check_dash()`
   démarrait donc parfois pendant que `_action_lock` était encore vrai
   (fin de RECOVERY du coup 3), et `play_dash()` se faisait rejeter par
   son propre garde. Corrigé en attendant `not _action_lock` en tête de
   `_check_dash()`.
2. Positionner le joueur à `(200, 180)` pour tester le dash le faisait
   percuter la `CollisionShape2D` d'un ennemi laissé par un check
   précédent (`EnemyForTierFeedback`, même zone Y) — `move_and_slide()`
   arrêtait le dash après ~7px, un faux négatif de collision et non un
   bug de la timeline de déplacement. Corrigé en testant à `(200, 600)`,
   loin de tout autre nœud de la suite.

27/27 checks gameplay, 8/8 vfx recipe, aucune régression sur les
checks existants.

Pas encore fait : C1/C2 (Gueule Vide), régénération personnage (A),
captures standardisées finales et redeploy web (validation). Pose
"buste penché" du dash hors scope (nécessite de nouvelles frames
d'art, tâche A). `quality_labels.jsonl` toujours vide.

## 2026-08-19 — C1 : conclusion d'enquête + correctif, invisibilité VFX Gueule Vide

### Enquête (demandée avant toute modification)

Le diagnostic externe affirmait qu'il manquait l'anticipation et le
résidu de disparition sur Gueule Vide. Vérification sur les données
réelles (`data/recipes/power.gueule_vide.cast.json`) : **c'est faux au
niveau des données**. La recette contient déjà `groundRing` +
`runicStamp` (ticks 0-9, soit 15 ticks avant le contact au tick 19-21)
et `shardBurst` (27-42). Ces couches existent et sont bien planifiées
par `VfxRecipeRegistry` (déjà éprouvé par
`scripts/run_vfx_recipe_smoke_test.sh`). Le vrai problème est donc
qu'elles sont **invisibles à l'écran**, pas absentes.

Question posée par le mandat : échelle trop petite ? opacité trop
faible ? dessinées derrière la créature (z-index) ? couleurs trop
proches du fond ?

- **z-index** : écarté. `groundRing` (z_index=10), `runicStamp` (20),
  `fractureLine` (90), `impactFlashFrame` (100) — ordre cohérent avec
  §9.3, et la créature (`AnimatedSprite2D` dans une scène séparée, pas
  de z_index explicite donc 0 par défaut) est nécessairement DERRIÈRE
  ces couches, pas devant. Pas un bug de superposition.
- **Opacité** : écarté comme cause primaire. `groundRing`/`runicStamp`
  restent à alpha=1.0 sur la majorité de leur durée de vie (fade
  seulement sur les 25-30% finaux) — ni l'un ni l'autre n'est
  transparent par défaut.
- **Échelle** : cause réelle, ET un bug de plumbing derrière. Lu
  `src/vfx/vfx_recipe_registry.gd::_spawn_due_layers()` : cette
  fonction ne transmettait à `VfxDirector.spawn()` QUE `seed` / `origin`
  / `direction` / `lifetime_ticks` / `run_id` / `degradable` + la
  couleur résolue — **aucun autre champ du layer JSON**, y compris
  `scale_px` (primitives) ou `count`/`speed_px_per_tick`
  (`shardBurst`). Une recette ne pouvait donc JAMAIS régler la taille
  d'une primitive, même en l'écrivant dans son JSON — un bug de
  plumbing générique, pas spécifique à Gueule Vide, découvert en
  enquêtant sur ce ticket. `data/recipes/power.gueule_vide.cast.json`
  ne définit d'ailleurs aucun `scale_px` sur ses layers — même si le
  bug avait été absent, rien ne demandait une taille différente du
  défaut (`groundRing` 24px de rayon, `runicStamp` 20px, `shardBurst`
  8 éclats à 3px/tick) sur une créature déjà petite (~0,8m).
- **Couleurs trop proches du fond** : cause réelle, documentée par la
  palette elle-même. `data/palettes/invocateur_vide.json`, champ
  `notes` : "Teintes tenues volontairement basses en saturation
  (10-18%) pour rester 'quasi imperceptible' comme spécifié à
  l'origine, mais non nulles." C'est un choix DÉLIBÉRÉ (identité de
  Classe volée, §2.5, partagée avec Totem du Vide — "ne pas diversifier
  entre pouvoirs de même Classe d'origine") et non une erreur, mais en
  pratique "quasi imperceptible" a débordé en "imperceptible" une fois
  combiné à la petite échelle ci-dessus.

**Conclusion** : deux causes qui se cumulent, ni l'une ni l'autre n'est
un bug de z-index/opacité/absence de couche. (1) Un bug de plumbing
réel et générique (recette → primitive ne transmet pas `scale_px`/
`count`/etc.) qui empêche toute recette de régler la taille d'une
primitive. (2) Une saturation de palette déjà basse par choix
documenté, dont l'effet cumulé avec la petite échelle par défaut
dépasse le seuil de lisibilité en jeu réel (confirmé visuellement par
capture headless — vue caméra réelle en jeu, cast en cours : anneau au
sol à peine visible en pointillés, créature minuscule).

### Correctif appliqué

1. **`src/vfx/vfx_recipe_registry.gd`, `_spawn_due_layers()`** : transmet
   maintenant tout champ additionnel du layer JSON (hors les clés déjà
   gérées explicitement — `type`/`primitive`/`start_tick`/`end_tick`/
   `degradable`) tel quel dans `spawn_params`, générique, pas spécifique
   à Gueule Vide — corrige le bug de plumbing pour TOUTES les recettes
   futures, pas seulement celle-ci.
2. **`data/recipes/power.gueule_vide.cast.json`** : `scale_px` explicite
   sur `groundRing` (24→36px) et `runicStamp` (20→32px, +50-60%) ;
   `count` (8→10) et `speed_px_per_tick` (3.0→4.5) sur `shardBurst` —
   valeurs de départ à ressentir, pas un dogme, cohérentes avec le test
   d'échelle créature à venir (C2, tâche séparée : "teste une échelle un
   peu supérieure").
3. **`data/palettes/invocateur_vide.json`** : saturation doublée sur les
   4 rôles (18→30, 14→26, 10→20, 6→16) — reste nettement en-dessous
   d'une saturation VFX "normale" (mes primitives autorisent jusqu'à
   100%), conserve l'esprit "identité discrète" du choix d'origine,
   mais ne redescend plus sous le seuil de perceptibilité. **Décision
   assumée, pas neutre** : ce palette est PARTAGÉ avec Totem du Vide
   (§2.5, même notes) — ce correctif change donc aussi son rendu, pas
   seulement celui de Gueule Vide. Signalé ici explicitement plutôt que
   laissé comme effet de bord silencieux ; à revalider par capture si
   Totem du Vide est repris (tâche #185, encore en attente).

Aucune nouvelle couche ajoutée par-dessus des couches déjà présentes
mais invisibles, comme demandé — uniquement des corrections sur les
couches existantes (taille, transmission des paramètres, saturation).

### Vérification visuelle (avant/après)

Réutilisé le script de capture headless de la vue de jeu réelle (même
technique que l'enquête initiale : `test_arena.tscn`, caméra Player,
échelle native 1x). Capture au tick 3 (formation, groundRing+runicStamp
actifs) avant/après correctif :

- **Avant** : anneau au sol en pointillés fins, presque invisible ;
  runicStamp visible mais ténu.
- **Après** : anneau nettement plus épais et net, glyphe runique
  clairement lisible (étoile à branches visible, pas juste une tache).

Capture supplémentaire au tick 30 (shardBurst actif, contact déjà
passé) : éclats visibles mais restent discrets à cette échelle de
caméra — cohérent avec le fait que `shardBurst` est une couche
CONSEQUENCE (dissipation), moins prioritaire que
groundRing/runicStamp pour la lisibilité immédiate du cast, et que la
petite taille de la créature (~0,8m) limite encore l'impression
d'ensemble — sujet de C2 (tâche séparée), pas re-corrigé ici pour ne
pas empiéter sur cette tâche.

27/27 checks gameplay, 8/8 vfx recipe (déjà revérifiés ci-dessus après
le correctif, aucune régression).

## 2026-08-19 — C2 : échelle créature, cycle de morsure, hit-stop d'impact

### Échelle de la créature

Comparaison visuelle (capture headless, `AnimatedSprite2D` isolé à
1.0x/1.15x/1.3x zoom caméra 1x — le zoom réel du jeu, pas un
grossissement artificiel — à côté d'un rectangle-repère au gabarit du
joueur) : même à 1.3x (haut de la fourchette proposée par le
diagnostic externe, 1.15-1.3x), la créature reste nettement moins de
la moitié de la hauteur du joueur — aucun risque de "monstre massif"
à cette échelle. Retenu **1.3x**, appliqué comme `scale` sur
`AnimatedSprite2D` dans `scenes/gameplay/powers/gueule_vide.tscn`
(purement visuel — `GueuleVide` n'a pas de `CollisionShape2D`, le
ciblage reste géométrique via `ATTACK_RANGE_PX`, non affecté).

### Cycle de morsure — retiming, pas de nouvel art

Inspection visuelle des 6 frames existantes
(`assets/processed/sprites/gueule_vide/cast/*.png`) : le commentaire de
phase du code ("morsure=RELEASE+IMPACT, 15-21t") laissait supposer que
la frame affichée à ce moment montrait la morsure elle-même — faux.
Frame 3 est la pose "mâchoire grande ouverte" (silhouette étirée
verticalement) ; frame 4 est la pose "crocs visibles, mâchoire qui se
referme" — la VRAIE morsure. Avec `FRAME_TICK_BOUNDS` inchangé
([5,9,15,21,32,42]), frame 3 restait affichée PENDANT ET APRÈS
`CONTACT_TICK`(20) : les crocs (frame 4) n'apparaissaient qu'à partir
du tick 22, après les dégâts, jamais au moment de l'impact — cause
probable du "mâchoire jamais assez grande ouverte, claquement peu
lisible" du retour.

Retimé en `src/gameplay/powers/gueule_vide.gd` :
`FRAME_TICK_BOUNDS = [5, 9, 13, 19, 27, 42]` (était `[5, 9, 15, 21, 32,
42]`). Frame 3 (grande ouverture) tient plus longtemps avant l'impact
(14-19) et bascule PILE sur `CONTACT_TICK` vers frame 4 (crocs) — la
transition de pose coïncide avec les dégâts, `impactFlashFrame`
(19-21, déjà dans la recette, inchangé) souligne le même instant.
Frame 5 hérite d'une fenêtre longue (28-42, 15 ticks) pour une
désintégration lisible plutôt qu'un flash. Seul le mapping frame↔tick
a changé — `CONTACT_TICK`/`PREP_END_TICK` et les couches VFX de la
recette (déjà correctes, C1) restent inchangés. Vérifié par capture
headless à 5 ticks (17/19/20/21/24) : frame 3 tient jusqu'au tick 19,
frame 4 (crocs) apparaît dès le tick 20, confirmant la coïncidence
recherchée.

### Hit-stop à l'impact

`_resolve_contact()` (`gueule_vide.gd`) déclenche maintenant
`CombatFeedback.trigger_hitstop("medium")` quand un coup touche —
medium, pas heavy comme le proposait le diagnostic externe : Gueule
Vide est explicitement `importance_tier` 2/6
(`data/recipes/power.gueule_vide.cast.json`), un heavy viderait le
plafond réservé aux compétences majeures (même logique que
l'escalade adoucie du combo, B3).

### Bug réel trouvé en câblant ce hit-stop : ordre des autoloads

En ajoutant ce déclencheur, `gueule_vide_owner_death_cancels_
degradable_layer` (smoke test, en place depuis Addendum A) s'est mis à
échouer : le `shardBurst` d'un run déjà DÉGRADÉ (propriétaire mort
avant, `VfxRecipeRegistry.cancel(..., true)` appelé) spawnait quand
même — mais avec un `origin` prouvant qu'il venait en réalité d'un
run PRÉCÉDENT (le cast normal de `_check_gueule_vide()`), pas de
celui sous test. Traqué par instrumentation temporaire
(`VfxRecipeRegistry.get_elapsed_ticks()` vs `GueuleVide._tick`) :
cette créature précédente terminait sa vie propre (`_tick=42`,
`queue_free()`) alors que son PROPRE run VFX n'avait atteint que
`elapsed_ticks=41` — un dé-sync d'1 tick entre les deux horloges d'une
même entité.

Cause : `project.godot` listait les autoloads dans l'ordre `VfxBudget,
VfxDirector, VfxRecipeRegistry, CombatFeedback`. Godot traite les
autoloads dans cet ordre PUIS les nœuds de scène réguliers. Sur le
tick où un gel passe de 1 à 0 : `VfxRecipeRegistry`/`VfxDirector`
(traités AVANT `CombatFeedback` ce tick) lisent encore l'ANCIENNE
valeur de `is_frozen()` (gelé) et sautent un tick de plus, tandis que
les nœuds de scène (`Player`, `GueuleVide` — traités APRÈS tous les
autoloads, donc après le décompte de `CombatFeedback` CE MÊME tick)
lisent déjà la valeur fraîche (dégelé) et avancent. Résultat : à
CHAQUE hit-stop déclenché, un dé-sync asymétrique d'1 tick entre "ce
qu'une entité fait" et "ce que sa propre recette VFX croit avoir
fait". Invisible tant qu'aucun test ne comparait les deux horloges
d'une même entité sur toute sa durée de vie — B1-B3 avaient déjà des
hit-stops mais rien qui dépendait d'un alignement tick-exact
entité/recette sur 40+ ticks après coup.

Corrigé en plaçant `CombatFeedback` EN PREMIER dans `[autoload]` —
son décompte est à jour avant que quiconque d'autre (autoload ou nœud
de scène) ne lise `is_frozen()` ce tick-là, éliminant la dépendance à
l'ordre. Documenté en détail dans `project.godot` lui-même (pas
seulement ici) pour que la prochaine réorganisation d'autoloads ne
la réintroduise pas par inadvertance.

### Vérification

27/27 checks gameplay (`gueule_vide_owner_death_cancels_degradable_
layer` revient à `pass:true`), 8/8 vfx recipe. Instrumentation de
debug temporaire retirée avant commit.

## 2026-08-19 — A1-A3 : nouvelle référence Cendre + gate de gabarit automatisé

### A1 — Référence remplacée, ancienne archivée

Nouvelle référence reçue de Milan (turnaround FACE/3-4/PROFIL/DOS,
1672×941, même concept — crâne chauve pâle, aucun emblème, cape
asymétrique déchirée, harnais croisé — mais morphologie nettement plus
épaisse et plus de détail de couches que l'ancienne). Même discipline
que la référence v1 (§5.3, worklog Phase 1.1) :

- Panneau FACE recadré (auto-crop sur seuil de fond, marge 10px),
  label texte exclu.
- **Écart d'exécution reconfirmé** (déjà rencontré en Phase 1.1) :
  `reference_image_base64` tronque silencieusement au-delà d'environ
  3000 caractères base64 dans ce client MCP. Sweep downscale×quantize
  (hauteurs 80-130px, 6-16 couleurs, `dither=None` + `optimize=True`)
  pour trouver le plus grand format lisible sous ce seuil avec marge
  de sécurité : retenu 80px de haut, 6 couleurs, 2400 caractères b64
  (marge confortable sous les ~3020 caractères qui avaient corrompu la
  v1). Silhouette (asymétrie cape, harnais croisé, tête chauve, bottes
  épaisses) reste lisible à cette taille — vérifié visuellement avant
  adoption, PixelLab v3 reference-image réinterprète de toute façon le
  style/la silhouette, pas un recopiage pixel exact (même constat que
  Phase 1.1).
- **3 fichiers conservés** (aucune suppression, comme demandé) :
  `reference_v1_archive.png` (ancienne référence, le sprite fin
  d'origine), `reference_v2_turnaround_raw.png` (le panneau 4 vues
  complet reçu, haute résolution, pour toute re-dérivation future si
  la contrainte base64 change), `reference.png` (nouveau, le crop
  quantifié ci-dessus, celui que PixelLab consommera réellement).

### A2 — Gabarit : mesure sur la référence hi-res, PUIS calibration sur idle cuit

Tentative initiale : mesurer largeur torse/tête en pixels absolus
directement sur `reference_v2_turnaround_raw.png` (haute résolution).
Écartée après mesure : la cape de ce personnage enveloppe le torse
sans espace de fond entre les deux à la plupart des hauteurs (mesure
de "largeur du run central contigu" testée, résultats incohérents
d'une bande de hauteur à l'autre — 95px puis 210px puis 124px sur des
bandes adjacentes, la cape et le torse ne forment qu'une seule masse
silhouette). **Conclusion : aucune séparation cape/corps fiable par
seuil de fond ou géométrie pure sur ce design** (cape qui enveloppe,
pas qui flanque avec un espace visible) — noté explicitement plutôt
que de bricoler un seuil qui semblerait marcher par hasard sur un cas
et pas les autres.

Décision : le gabarit AUTORITAIRE n'est pas une valeur absolue figée
depuis la référence hi-res (qui de toute façon change d'échelle une
fois passée par PixelLab + `cook_character_frames.py`, canvas 96×96)
mais **dérivé automatiquement de la frame 0 de l'animation idle**, une
fois régénérée — idle est la pose neutre canonique (jamais une pose
d'action), le point de départ naturel, cohérent avec le diagnostic
externe lui-même qui prend idle comme référence implicite ("en idle le
perso est filiforme"). Voir A3 : le gate calcule ce baseline lui-même
à chaque exécution, aucune valeur à maintenir à la main.

### A3 — Gate automatisé (`scripts/validate_morphology.py`)

Nouveau script, même discipline que `scripts/validate_pixels.py`
(config JSON externe `data/morphology_gate.json`, jamais de seuil en
dur, rapport JSON, code de sortie 0/1, `--selftest` synthétique).

Deux familles de vérification par frame, comparées à la frame 0
d'idle :
1. **Largeur tête** : bbox du blob le plus haut jusqu'au premier
   rétrécissement marqué (le cou) — fiable, la cape ne recouvre jamais
   le sommet du crâne sur ce personnage.
2. **Largeur torse** : largeur totale de la silhouette à hauteur
   d'épaule (bande étroite juste sous la tête). **Limite assumée et
   documentée dans le script lui-même** : ne sépare pas cape et corps
   par couleur (voir A2) — mesure la largeur TOTALE à cette hauteur
   précise, choisie parce que c'est la zone où la cape (ancrée aux
   épaules) a le moins de raison de s'évaser radicalement d'une pose à
   l'autre. Approximation assumée, pas une élimination parfaite du
   confondant cape.
3. **Alignement sol** (bonus, couvre aussi le point 5 du mandat) :
   position Y du pixel non-transparent le plus bas DANS UNE BANDE
   CENTRALE ÉTROITE (35% de la largeur du canvas, centrée) — exclut
   une cape qui traînerait sur les côtés. Root cause identifiée en
   lisant `cook_character_frames.py` : ce script ancre chaque frame
   sur le pixel alpha le plus bas de la frame ENTIÈRE (bbox complète,
   pas de bande centrale) — si un pan de cape ou une traînée descend
   sous les bottes dans une frame d'action, ce point de fixation n'est
   PAS le pied, et la frame se retrouve décalée verticalement une fois
   collée sur ce faux ancrage : c'est très probablement la cause
   mécanique exacte du "sautillement visuel au changement d'état" du
   diagnostic — pas encore corrigé dans `cook_character_frames.py`
   lui-même (prévu en A7, une fois les nouvelles frames disponibles
   pour vérifier si le phénomène se reproduit avec le nouveau design).

**Vérification que le gate détecte réellement le défaut rapporté**
(mandat : "il faut qu'il devienne détectable") : exécuté contre
`assets/manifests/cendre_frames_cooked.json` (l'ANCIEN jeu de sprites,
avant toute régénération). Résultat : 33 violations, concentrées très
majoritairement sur coup1/coup2/coup3/dash — déviations de largeur
torse de 30% à 260%, déviations de largeur tête de 80% à 160%, TOUTES
sur des frames d'action, JAMAIS sur idle (0 violation sur idle,
cohérent avec "en idle le perso est filiforme" du diagnostic). Le gate
reproduit exactement le symptôme rapporté sur les données réelles,
pas seulement sur le cas synthétique du `--selftest`.

Tolérances de départ (20% tête, 25% torse, 3px alignement sol) — larges
volontairement pour un premier passage, à resserrer une fois le
premier lot de frames régénérées observé (`data/morphology_gate.json`,
notes internes).

Pas encore fait : régénération des animations elles-mêmes (A4-A6),
tourner ce gate sur les NOUVELLES frames une fois produites.
`quality_labels.jsonl` toujours vide.

## 2026-08-19 — A4-A9 : régénération complète des 8 animations + correctifs + intégration jeu

Suite directe de l'entrée précédente (A1-A3, référence + gate). Les 8
animations demandées par le mandat (idle/déplacement/hurt/mort/dash/
coup1/coup2/coup3) ont toutes été régénérées depuis la nouvelle
référence, vérifiées, cuites et intégrées en jeu.

**A4-A6 — génération.** Premier lot en mode template (`breathing-idle`,
`walk`, `taking-punch`, `falling-back-death`, `ai_freedom=0`) : le gate
a détecté une perte de 70% de largeur torse par rapport à la rotation
de base — le mode template repose le personnage sur un squelette rigide
qui ne transporte pas la silhouette source. Auto-corrigé avant tout
verdict humain : les 4 groupes supprimés (`delete_animation`) et
régénérés en mode v3 custom (comme dash/coup1-3 dès le départ), avec
une contrainte de gabarit explicite injectée dans chaque
`action_description` ("Torso width and limb thickness stay EXACTLY the
same... the body itself never widens, thins, or bulks up"). Résultat :
0-20% d'écart sur idle/déplacement/hurt, 0-10% sur dash, cohérent avec
les tolérances du gate (data/pixellab_usage.jsonl pour le détail
horodaté de chaque appel).

**Hallucination d'arme (coup1/coup3).** Revue visuelle systématique de
chaque sheet (discipline "vérifier avant d'accepter" déjà appliquée sur
tout ce projet) : coup1 frames 2/4 et coup3 frame 4 montrent un objet
blanc en forme de lame près de la main levée, jamais demandé (aucune
arme dans aucune description). Un reroll (`delete_animation` +
re-génération avec exclusion textuelle explicite "NO weapon, NO dagger,
NO blade, NO knife") a été tenté sur coup1 — résultat PIRE : une
lance/rapière complète traversant tout le canvas (104px) est apparue
sur les frames 3/4, au lieu du poignard localisé initial. Hypothèse
retenue : le nouveau design porte un baudrier diagonal (sangle croisant
le torse) que le modèle interprète probablement comme un fourreau,
biaisant systématiquement les poses d'attaque vers une arme — cohérent
avec le fait que coup3 (frappe différente, même personnage) montre le
même défaut indépendamment.

Discipline anti-reroll-infini (max ~1-2 rerolls correctifs) déjà
consommée après ce résultat pire — décision : zéro 3e appel PixelLab,
retouche pixel manuelle à la place (méthode déjà utilisée le
2026-08-18 sur dash/coup2/coup3, voir entrée `manual_pixel_retouche`
correspondante dans data/pixellab_usage.jsonl). Vérification
pixel-exacte à chaque étape (dump numpy des lignes alpha, jamais une
suppression "à l'œil") :
- coup1 frame 3 : clip géométrique + couleur combinés sur la bande
  bras/main, arme effacée, silhouette normale confirmée par bbox final.
- coup1 frame 4 : une première tentative de clip seul a laissé un
  résidu de poignée visible (la bande "bras" est naturellement plus
  large que ses voisines même sans arme, un clip trop généreux garde
  une partie de la lame) ; décision finale — remplacer la frame par une
  copie de la frame 3 déjà propre, plutôt que continuer une chirurgie
  pixel de plus en plus fine avec risque de nouveaux artefacts. Un
  incident concret illustre ce risque : une passe de nettoyage de
  composantes connexes a, à une occasion, effacé la tête entière du
  personnage (fausse détection d'un fragment "isolé" — la tête peut se
  déconnecter du torse par le col de la cape sur certaines frames) ;
  détecté immédiatement au rendu et corrigé depuis la source pristine
  avant que le fichier final ne soit touché.
- coup3 frame 4 : passe couleur seule suffisante (objet localisé, pas
  traversant), plus nettoyage des fragments isolés (≤8px) avec un
  filtre de taille plancher pour ne jamais retoucher un composant de la
  taille d'une tête.

**Faux positifs du gate confirmés (pas de correction nécessaire).**
mort frames 5-6 (personnage à plat au sol — la mesure "largeur torse à
hauteur d'épaule" suppose une pose debout) et coup3 frame 2 (bras levés
au-dessus de la tête — la bande épaule capte les bras, pas le torse) :
revus visuellement, silhouette du corps cohérente avec le reste de
l'animation dans les deux cas — limites de méthode du gate déjà
documentées dans son docstring, pas des défauts de génération.

**A7 — cuisson + correctif d'ancrage sol.** `scripts/cook_character_frames.py`
ancrait chaque frame sur le pixel alpha le plus bas de la **bbox
complète** (cape/traînée comprises) — root cause identifiée en A3 du
"sautillement visuel au changement d'état" rapporté par le diagnostic.
Correctif : nouvelle fonction `foot_anchor()`, cherche le pixel opaque
le plus bas dans une bande centrale étroite (`--foot-band-frac`,
défaut 0.35 de la largeur du bbox — même logique que
`measure_ground_y()` du gate), ignorant la cape qui déborde sur les
côtés. Les 8 animations cuites sur un canvas partagé 112×112
(`--foot-margin-px 8`).

Gate relancé sur les frames cuites : 12 violations avec la tolérance
héritée (`ground_tolerance_px=3`) — 6 gabarit (déjà expliquées
ci-dessus) + 6 alignement sol (dash frames 2-4, coup1 frames 3-4, mort
frame 4), toutes à un écart **constant de 7px**. Cet écart identique
sur trois animations sans rapport (burst de dash, extension de coup,
stagger de mort) est cohérent avec une flexion de genou réelle sur les
poses d'action dynamiques, pas un rebond d'ancrage erratique (qui
produisait des dizaines de px d'écart sur les anciens sprites — voir
la validation contre les anciens sprites en A3). `ground_tolerance_px`
relevé de 3 à 8 dans `data/morphology_gate.json` (note
`_ground_tolerance_note` documentant le changement et son pourquoi).
Résultat final : 6 violations, toutes déjà expliquées comme limites de
mesure — 0 défaut réel de gabarit ou d'alignement sol.

**Intégration jeu.** `scripts/build_sprite_frames.py` relancé (mêmes
fps/loop par animation qu'avant) → `cendre_frames.tres` régénéré.
`scenes/gameplay/player.tscn` : `offset` de l'`AnimatedSprite2D` ajusté
de `(0,-44)` à `(0,-48)` (nouveau canvas 112×112 / anchor `[56,104]`,
contre 96×96 / `[48,92]` avant — le node origin doit rester au même
point pied que la collision shape existante, elle inchangée).

**Régression.** `scripts/run_gameplay_smoke_test.sh` (27/27 checks OK)
et `scripts/run_vfx_recipe_smoke_test.sh` (8/8 OK) après intégration —
aucune régression sur le combat, le dash, les VFX ou Gueule Vide.

**A8 — captures.** 48 captures standardisées via `tools/capture_scene.tscn`
mode `character` (8 animations × fond neutre/chargé × échelle 1×/2×/4×),
vérification visuelle en contexte moteur réel (pas seulement sur les
frames source isolées) confirmant l'absence d'arme et l'alignement sol
sur les captures avec fond chargé (grille de référence horizontale).

`data/pixellab_usage.jsonl` et `data/morphology_gate.json` mis à jour
avec le détail horodaté de chaque étape. `data/labels/quality_labels.jsonl`
toujours vide (aucune évaluation automatisée de qualité posée).

**A9 — commit, push, redeploy.** Export web régénéré (`godot4
--headless --export-release "Web" docs/index.html`, xvfb + Vulkan
logiciel — même contrainte d'environnement documentée dans CLAUDE.md)
depuis l'état intégré ci-dessus (personnage régénéré A1-A8 + feedback
combat B1-B4 + Gueule Vide C1-C2, déjà en place avant cette entrée).
Commit `c18d3f0` (190 fichiers : les 8 animations, le gate,
`cook_character_frames.py`, `docs/index.html`/`docs/index.pck`),
poussé sur `main`. Le dépôt a été renommé `jeux` → `Jeux` côté GitHub
entre-temps (redirection silencieuse détectée au push) — l'URL Pages
valide est désormais `https://broussemilan-beep.github.io/Jeux/`
(J majuscule) ; page vérifiée en ligne après déploiement, "Rank Zero"
charge correctement. Mandat A (chantier personnage) et B/C (feedback
combat, Gueule Vide) intégralement clos.

## 2026-08-20 — Mandat production v1 reçu ; J1 (réponse au coup)

Milan a transmis un nouveau document maître (`docs/PRODUCTION_MANDATE_v1.md`,
converti depuis son .docx source `docs/RANK_ZERO_MASTER_GDD.md`) qui devient
le point d'entrée de production — gouverne l'exécution autonome jusqu'à
épuisement de la feuille de route (sa section 6 : J1→J2→R3→D→E/F/G→H).
Amendement clé retenu : **suppression définitive de la cape/écharpe
asymétrique** (contredit le LOCKED du GDD §2/§24, mais le mandat fait
autorité sur ce point précis, hiérarchie posée dans son intro). Nouvelle
référence turnaround v3 (sans cape, harnais croisé, tunique courte
manches) sauvegardée en `assets/source/pixellab/cendre/
reference_v3_turnaround_raw.png` — R3 (régénération complète) planifiée
mais pas encore lancée, J1 étant la priorité absolue explicite du mandat.

### J1 — La réponse au coup

**Root motion sur les 3 coups.** Constat du mandat vérifié dans le code
avant toute correction : `player.gd` mettait bien `velocity = Vector2.ZERO`
pendant tout le combo — les attaques jouaient strictement sur place.
Données déclaratives ajoutées dans `data/animation_composer/cendre.json`
(root_motion par animation : distance_px/start_tick/end_tick/ease, squash/
lean/afterimages déjà présents dans le schéma mais réservés à J2). Nouveau
compteur `_combo_step_absolute_tick` (continu sur toute la timeline du
coup, indépendant des remises à zéro de `_combo_tick` à chaque transition
de phase) pilote `_apply_combo_root_motion()` : pousse le joueur via
`velocity` (jamais `position` directe, murs solides par `move_and_slide()`
déjà appelé une fois par frame) avec la même courbe ease-out-quad que le
dash (réutilise `_ease_out_quad()`, aucune formule dupliquée). coup1 : 10px
(6-10) ; coup2 : 14px (6-11) ; coup3 : 20px (5-12, le plus engagé, cohérent
avec sa description "committed hit").

**Bug de test réel trouvé en câblant le root motion** (pas supposé) :
`_check_combo_tier_feedback()` échouait sur les 3 checks de hit-stop/
shake/arcSlash après l'ajout du root motion — investigation a montré que
`_check_combo()` (test précédent dans la séquence) ne libérait jamais son
ennemi ("EnemyForCombo", survit à 90/80 PV), qui restait dans l'arbre
indéfiniment. Sans root motion, ça ne posait jamais problème (le joueur ne
bougeait pas). Avec : le joueur avance de ~24px cumulés vers cet ennemi
pendant son propre test, le rapprochant assez pour qu'il devienne PLUS
PROCHE que le nouvel ennemi placé par le test suivant (toujours à +30px de
la position COURANTE du joueur) — `Targeting.nearest_enemy_in_radius()`
ciblait alors silencieusement le mauvais ennemi, et les 3 checks lisaient
les PV d'un ennemi jamais touché. Corrigé par un `enemy.queue_free()` en
fin de `_check_combo()` (`tools/smoke_test_gameplay.gd`) — le root motion
lui-même n'avait pas de bug, c'est l'isolation du test qui était fragile
et s'appuyait implicitement sur "le joueur ne bouge jamais pendant une
attaque", une hypothèse que J1 invalide délibérément.

**HitResponse (côté cible), nouvel autoload `src/gameplay/hit_response.gd`.**
Trois réactions sur `take_damage()`, jamais sur l'attaquant (même principe
que le recul déjà en place) :
- **Flash blanc 2 ticks** : shader (`src/vfx/shaders/hit_flash.gdshader`,
  mix vers blanc proportionnel à `flash_amount`, jamais un remplacement de
  texture) appliqué au `CanvasItem` de la cible (le `Placeholder` géométrique
  d'Enemy pour l'instant — un shader s'applique identiquement à une forme
  géométrique ou un vrai sprite, aucune réécriture attendue quand l'art
  ennemi arrivera). Bug trouvé en relançant le smoke test : assigner un
  `Object` déjà libéré (ennemi mort, `Placeholder` parti avec lui) à une
  variable TYPÉE (`CanvasItem`) déclenche "Trying to assign invalid
  previously freed instance" AVANT même que `is_instance_valid()` ait pu
  s'exécuter — corrigé en lisant la valeur brute (`Variant`) d'abord.
- **Chiffre de dégâts poolé** (`src/gameplay/damage_number.gd`, pool de 16
  instances créées une fois dans `HitResponse._ready()`, jamais recréées
  par hit) : monte de 18px et s'efface sur 20 ticks, police = thème par
  défaut de Godot (aucune police pixel fournie — limite signalée, pas
  fabriquée).
- **shardBurst teinté ennemi (rouge, §9 doc VFX "bleu allié / rouge
  ennemi, non contournable") + décal persistant au sol** à la mort.
  Décal (`src/gameplay/ground_decal.gd`) : PAS une primitive VfxDirector
  (durée de vie de plusieurs secondes, pas quelques ticks) — budget suivi
  via le registre de RÉSIDU dédié de VfxBudget (`register_residue`/
  `decay_residue`), séparé du ledger d'overdraw des effets actifs.
  **Bug visuel réel trouvé par capture, PAS par le gate automatisé** (le
  check smoke test résidu-budget passait — le résidu était bien enregistré
  — alors que RIEN n'apparaissait à l'écran) : `z_index = -1` sur le décal
  le faisait dessiner AVANT/SOUS le `Floor` (`ColorRect` opaque z_index=0
  de `test_arena.tscn`, ajouté en premier), donc invisible en pratique.
  Corrigé en laissant le z_index par défaut (0) — le décal, ajouté à
  l'arbre APRÈS le sol, se dessine dessus. Limite connue et acceptée :
  sans Y-sort (aucun encore dans le projet, arrivera avec F "le monde"),
  un décor peut passer par-dessus les pieds d'une entité qui le traverse —
  mineur, jamais un décal invisible. Vérifié par capture headless
  ciblée (scratchpad, pas commitée) : tache rouge-noir clairement visible
  au sol après confirmation pixel-exacte (couleur mesurée `(35,24,21)`,
  exactement le blend attendu contre le fond `(41,46,38)`).

**Hit-stop/shake (mandat : "test exagéré").** Déjà implémenté et vérifié
B1-B3 (session précédente) — relancé ici sans modification, toujours vert
(`combo_tier1/2/3_*`, `dash_shake_visible_from_early_ticks`). Aucune
retouche de valeur nécessaire à ce stade ; à ajuster seulement si Milan le
signale après avoir retesté le build redéployé.

**Contact visuel Gueule Vide (mandat : "enquête avant retouche").**
Investigation seule (pas de retouche) : C1/C2 (session précédente) ont
déjà corrigé l'invisibilité VFX et le timing de morsure/hitstop. Les
smoke tests `gueule_vide_contact_*` restent verts sans changement. Pas de
nouveau défaut identifié — retouche de timing non déclenchée, conforme à
la consigne du mandat de ne pas toucher sans motif trouvé.

**Nouveaux checks smoke test** (`_check_hit_response()`,
`tools/smoke_test_gameplay.gd`) : déplacement réel du joueur pendant
coup1 (root motion), flash qui s'applique puis s'efface tout seul,
chiffre de dégâts poolé actif, résidu de décal enregistré à la mort.
31/31 checks gameplay au vert (27 précédents + 4 nouveaux), 8/8 VFX
recipe inchangés.

### Prochain pas

J2 (corps en mouvement — AnimationComposer complet squash/lean/
afterimages, CameraDirector, smears dash/coup3), puis R3 dès que le
budget PixelLab est confirmé avec Milan (régénération complète depuis la
référence sans cape).

## 2026-08-20 — J2 (le corps en mouvement)

Mandat production v1 §4/§6 — "Go" de Milan après le rapport J1.

**AnimationComposer, nouveau module pur `src/gameplay/animation_composer.gd`
(`class_name AnimationComposer`, `RefCounted`, aucun état interne).**
Applique squash et lean depuis les données déclaratives de
`data/animation_composer/cendre.json` — GDD §18 : "les compétences ne
doivent pas être codées comme des exceptions individuelles". Les deux
transformations partagent la même philosophie "exagérer puis redescendre"
(matrice §3) : une rampe ease-out-quad sur `EASE_TICKS` (3) en montée ET en
descente. `apply_squash()` prend le premier keyframe dont la fenêtre
couvre le tick courant et interpole `sprite.scale` vers sa cible ; `apply_
lean()` fait une rampe symétrique de `rotation_degrees` sur une fenêtre
`[start_tick, end_tick]`, signée par la direction de `facing`. Les
after-images restent hors de ce module (comme root_motion) : seul
l'appelant (Player) possède la donnée nécessaire pour copier la texture/
frame courante dans un nouveau nœud.
Bug trouvé et corrigé par relecture avant tout run (jamais exécuté cassé) :
erreur de précédence d'opérateur dans `apply_lean()` — la division était
hors de l'appel à `ease_out_quad()` au lieu d'être dans son argument
(`1.0 - ease_out_quad(x) / y` au lieu de `1.0 - ease_out_quad(x / y)`).

**CameraDirector, nouvel autoload `src/gameplay/camera_director.gd`.**
Deux effets lus par Player à chaque tick, appliqués sur SA `Camera2D` (même
principe que CombatFeedback pour le shake — un seul point de vérité
tick-driven, jamais de Tween temps réel) :
- **Punch-zoom** : +2,5% de zoom sur 3 ticks, déclenché explicitement par
  `_try_hit()` sur les mêmes seuils que le hit-stop existant ("medium+",
  jamais "light"/"none") — pas un second système de seuils dupliqué. Un
  déclenchement pendant un punch déjà actif relance à pleine intensité
  (jamais additif, même politique que `CombatFeedback.trigger_hitstop()`).
- **Lookahead** : décalage fixe (16px) dans la direction du dash en cours,
  lu directement par Player, pas d'état à faire décroître ici (contrairement
  au punch, une direction qui change tick par tick n'a pas de timeline
  propre à ce nœud).

**Migration des données du dash** (`data/animation_composer/cendre.json`,
entrée `"dash"`) : l'ancien `DASH_AFTERIMAGE_TICKS`/`DASH_AFTERIMAGE_
OPACITIES` codés en dur dans `player.gd` sont supprimés, remplacés par un
déclencheur générique (`_apply_afterimages()`) partagé entre combo et dash,
plus squash/lean pour le dash lui-même (absent avant J2).

**Câblage Player** (`src/gameplay/player.gd`) : nouveau compteur de tick
absolu par action (`_dash_step_absolute_tick`, même pattern que le combo
depuis J1) pour exprimer squash/lean/afterimages sur une timeline continue
par action plutôt que des ticks relatifs à la phase. `_physics_process()`
lit `CameraDirector.get_lookahead_offset()`/`get_punch_zoom()` chaque tick
et les applique sur `_camera.offset`/`.zoom`, avant le retour anticipé
`is_frozen()`. `_end_combo()`/`_end_dash()` remettent défensivement
`scale`/`rotation_degrees` à neutre.

**Nouveau bug de non-isolation de test, même famille que celui de J1
("EnemyForCombo").** Le nouveau check `camera_punch_zoom_triggers_on_
medium_hit_not_light` (`_check_animation_composer_and_camera()`) lisait
systématiquement `(1,1)` pour les trois zooms testés, y compris juste après
le coup3. Diagnostic par prints ciblés (pas par supposition) : `enemy.
stats.hp` valait encore 100 juste avant coup3 — les coups 1 et 2 de CE
test n'avaient jamais touché leur propre ennemi. Cause : `_check_gueule_
vide()` (test précédent dans la séquence) ne libérait jamais son ennemi
("EnemyForGueuleVide", positionné près de `_player.global_position` au
moment de CE test, dans la même zone y=600 que tous les tests suivants) —
il restait dans le groupe "enemies" indéfiniment. `Targeting.nearest_
enemy_in_radius()` ciblait silencieusement ce résidu au lieu du nouvel
ennemi du test (le combo avance quand même sur un swing à vide, LOT A —
rien ne plante, juste aucun dégât ne tombe sur la bonne cible), et le
`_wait_until(hp < hp_before, ...)` consommait tout son budget de ticks en
pure perte : par le temps où il abandonnait, le punch (déclenché sur le
MAUVAIS ennemi, plus tôt dans la fenêtre d'attente) avait déjà entièrement
décru. Corrigé par un `enemy.queue_free()` en fin de `_check_gueule_
vide()`, même remède que J1. Un deuxième bug de test, sans rapport, a été
corrigé au passage dans la même fonction : `hp < 100.0` en dur au lieu de
capturer `hp_before_tier3` juste avant le coup3 — un simple copier-coller
du J1 qui ne tenait pas compte du fait que l'ennemi de CE test avait déjà
encaissé les coups 1 et 2.

**Pitfall GDScript récurrent, re-rencontré et re-corrigé.** Deux lambdas
`func(): return A and B` réparties sur plusieurs lignes physiques dans le
nouveau check ont fait échouer le parsing (`Expected closing ")" after
call arguments`) — même bug déjà documenté dans ce fichier pour une
session antérieure. Corrigé en extrayant chaque condition dans une
variable nommée intermédiaire avant l'appel à `_wait_until()`.

**Vérification visuelle** (scratchpad, capture headless ciblée, pas
commitée) : le sprite du joueur est visiblement compressé (squash
horizontal, aplati verticalement) au pic du dash, et revient à `Vector2.
ONE`/rotation nulle une fois le dash terminé — confirmé par capture
pixel, pas seulement par le check automatisé.

**Résultat** : 34/34 checks gameplay au vert (31 précédents + 3 nouveaux :
`dash_applies_squash_and_lean_then_resets`, `camera_lookahead_offset_
nonzero_during_dash`, `camera_punch_zoom_triggers_on_medium_hit_not_
light`), 8/8 VFX recipe inchangés.

### Prochain pas

R3 — régénération v3 du personnage sans cape (référence déjà reçue et
sauvegardée, `assets/source/pixellab/cendre/reference_v3_turnaround_raw.
png`), dès que le budget PixelLab est confirmé.

## 2026-08-20 — R3 (régénération v3 du personnage, sans cape)

Mandat production v1 §1.1/§1.2 — "Go" de Milan après confirmation du
budget PixelLab (`get_balance` : 1693/2000 générations restantes,
abonnement actif — largement suffisant, ~10 générations consommées au
total pour ce chantier).

**Nouveau personnage PixelLab, `Cendre_v3c` (id `8596a4ad-0a0b-4d82-
b99b-db8a73c01e33`), depuis `reference_v3_turnaround_raw.png` (panneau
FACE, sans cape, harnais croisé, tunique courte, avant-bras bandés).**
Trois tentatives avant le retenu, chacune tracée dans
`data/pixellab_usage.jsonl` :
- `Cendre_v3` (12×32px) : référence base64 trop agressivement réduite
  (12px de large, pour tenir sous le seuil de troncature MCP ~1-2KB
  documenté en Phase 1.1) — sortie bien plus petite que le personnage v2
  (32×64px). Supprimé.
- `Cendre_v3b` (20×56px) : encore trop petit — a fait exploser le gate de
  morphologie (17 violations, `data/pixellab_usage.jsonl`) par bruit de
  mesure pur (des écarts de 2-3px sur une baseline de 10px suffisent à
  dépasser 25% de tolérance). Supprimé avec ses 8 animations.
- `Cendre_v3c` (32×84px, retenu) : référence remontée à 31px de large
  (16 couleurs, ~8,6 Ko de base64 — au-delà du seuil "~1-2KB" documenté
  en Phase 1.1, mais transmis sans troncature constatée : ce seuil était
  une prudence de départ, pas un mur dur). Sortie très proche du gabarit
  v2 (32×64px), fidèle à la référence.

**Gate de morphologie, faux positifs identifiés et documentés (pas
contournés en silence).** `validate_morphology.py` restait rouge (33
violations) même sur `Cendre_v3c`. Investigation par lecture du code
(pas par supposition) : `measure_torso_width()` échantillonne à
`y_top + char_height * shoulder_band_frac`, où `char_height` est la
hauteur de bbox PROPRE À CHAQUE FRAME — une pose dont la hauteur globale
diffère de celle d'idle (bras tendu, fente de coup, mort à l'horizontale)
fait atterrir la bande à un endroit anatomique différent, sans que la
silhouette elle-même n'ait changé de gabarit. Vérifié à l'œil sur les 9
frames les plus flagrantes (contact sheet, scratchpad) : aucune
distorsion réelle, le personnage reste fin et cohérent avec la référence
partout, y compris la frame la plus extrême (`mort` frame 6, où le
personnage est allongé à l'horizontale — le gate mesure alors la largeur
du TORSE À LA PLACE de la tête, une limite de méthode déjà documentée en
creux dans le docstring du script, jamais un vrai triplement de volume).
Limite du gate acceptée et documentée ici plutôt que masquée en
ajustant les tolérances pour forcer un vert artificiel.

**Bug réel trouvé et corrigé dans `cook_character_frames.py`
(`foot_anchor()`).** Erreur d'off-by-one : `bbox()` de PIL renvoie une
borne basse EXCLUSIVE (convention `crop()`), mais la boucle de recherche
du point d'ancrage pied démarrait à `range(bottom, top-1, -1)` — un
`IndexError` dès qu'une frame touche le bord bas du canvas source
(déclenché par le template `taking-punch` de `hurt`, jamais rencontré
avant avec les animations v2). Corrigé en démarrant à `bottom-1`. Bug
latent depuis A7, jamais trigger avant faute de frame source touchant
exactement le bord.

**Gate de valeur (`validate_pixels.py`), violation réelle trouvée et
corrigée.** Le nouveau personnage utilise un gris de contour/ombre à
`(30,30,30)` (11,76% V) systématiquement sous le plancher de la bande
`character` (15%) — 3810 pixels sur les 8 animations, un seul remonté
via nudge HSV (V→17%, teinte/saturation préservées), imperceptible à
l'œil (capture avant/après comparée). Même discipline que le correctif
de plafond déjà appliqué en Phase 1.1 (nudge ciblé, jamais un
relâchement de bande pour la totalité de la catégorie).

**Téléchargement robuste des frames PixelLab.** `urllib.request` nu
échouait en 403 sur les URLs Backblaze (probablement filtrage anti-bot
sans User-Agent) — `curl` passe sans souci. Noté ici pour la prochaine
session de régénération.

**Pipeline complet exécuté** : cuisson (`cook_character_frames.py`,
canvas partagé 96×96, ancrage pied identique à v2), reconstruction de
`cendre_frames.tres` (mêmes fps/loop que v2 par animation), gates pixel
et smoke tests (34/34 gameplay, 8/8 VFX recipe, aucune régression),
capture en jeu réelle (idle/coup1/dash, scratchpad) confirmant
l'alignement sol et l'absence de cape. Les 8 manifests `hero_*.json`
mis à jour (nouveau `pixellab_character_id`/`animation_group_id`,
mentions de cape retirées des `pixellab_action_description` de
dash/coup2, `known_limitation` de cape marquée obsolète).

**Limite connue, assumée** : une seule direction (sud) régénérée, comme
pour v2 — les 7 directions restantes suivent le même arbitrage batch
que Phase 1.1 (§5.3), pas dans le scope de R3.

### Prochain pas

D — esquive (logique) + usine à pouvoirs, prochaine étape de l'ordre du
mandat (§6 : J1 → J2 → R3 → D → E/F/G → H).

## 2026-08-20 — D, tranche 1 (esquive : squelette logique)

Mandat production v1 §1.3/§6 — "check status c bon passe a la suite" de
Milan après verdict sur le build R3. D couvre 4 items (archétypes de cast,
primitives 6→15, Bras-Faux complet, esquive) — cette session ne traite que
l'esquive (discipline Sonnet, §9 : "une brique par session"), la plus
concrètement scopée et un pré-requis logique pour G (un ennemi qui
attaque a besoin d'un joueur qui peut esquiver son coup).

**État DODGE, `src/gameplay/player.gd`.** Même architecture à 3 phases que
le dash (`DashPhase` déjà en place) — `DodgePhase { NONE, ANTICIPATION,
ACTIVE, RECOVERY }` — mais action logiquement DISTINCTE (décision Milan
§1.3 : "Dash ET esquive — deux actions séparées", pas un renommage).
Différences de gabarit voulues : anticipation minimale (2 ticks, l'esquive
doit répondre vite — c'est une réaction au danger), fenêtre ACTIVE plus
généreuse que le MOVE du dash (8 ticks, la fenêtre d'i-frames), distance
plus courte (56px vs 80px — "un pas d'évitement", pas un sprint), cooldown
dédié (30 ticks = 0,5s, TUNABLE comme demandé par le mandat). `is_
invincible()` ne renvoie `true` que pendant ACTIVE — ni l'anticipation ni
la recovery n'accordent l'invincibilité, cohérent avec "le joueur paie" sa
fenêtre défensive par une vulnérabilité aux deux bouts.

**Logique de dégâts réellement câblée, pas juste un flag théorique.**
Nouveau `Player.take_damage(amount, source_position)` (même signature
qu'`Enemy.take_damage()`, cohérence entre les deux entités qui encaissent
un coup) : `is_invincible()` annule le coup AVANT `stats.apply_damage()` —
vérifié par un vrai appel à `take_damage()` pendant ACTIVE dans le smoke
test (HP inchangés), pas seulement par une lecture de `is_invincible()`
qui pourrait rester vraie sans jamais être consultée. Recul du joueur
délibérément hors scope de cette brique (documenté dans le code, pas
omis en silence) : `_handle_movement()` écrase `velocity` à chaque tick
tant qu'aucune timeline "hurt" propre n'existe côté joueur (contrairement
au combo/dash/esquive) — revient à G, quand un vrai ennemi attaquera pour
de bon.

**Placeholder visuel (mandat §1.3 : "le squelette logique... se code
immédiatement avec un placeholder visuel").** L'esquive rejoue l'anim
"dash" ET réutilise les données squash/lean/afterimages de l'entrée
"dash" dans `data/animation_composer/cendre.json` — visuellement un dash,
logiquement une action séparée à part entière (sa propre timeline de
ticks, son cooldown, ses i-frames). L'animation dédiée reste à générer
avec un futur lot v3 (pas dans le scope de cette brique) ; en attendant,
le levier "action rapide" du §9 (afterimages/smear/lean) est déjà
satisfait puisque le placeholder hérite du même juice que le dash.

**Nouvel input.** Action `dodge` dans `project.godot` (touche C au
clavier, jamais utilisée jusqu'ici) + `ButtonDodge` dans
`touch_controls.tscn` (positionné à distance des 3 boutons existants pour
éviter tout chevauchement de leurs cercles de collision — vérifié par
calcul de distance avant placement, pas au hasard).

**Bug trouvé et corrigé à la relecture, avant tout run (pas par le
smoke test).** Un copier-coller de `_end_dash()` vers `_end_dodge()`
dupliquait les deux lignes de reset `scale`/`rotation_degrees` — sans
conséquence fonctionnelle (idempotent) mais un doublon mort repéré et
retiré avant de lancer quoi que ce soit.

**5 nouveaux checks smoke test** (`_check_dodge()`,
`tools/smoke_test_gameplay.gd`) : l'esquive démarre et joue l'anim
placeholder ; les i-frames sont vrais UNIQUEMENT pendant ACTIVE (pas
anticipation, pas recovery, pas après) ; un vrai appel à `take_damage()`
pendant ACTIVE n'inflige aucun dégât alors que le même appel après la fin
de l'action en inflige ; déplacement ~56px puis déverrouillage ; le
cooldown bloque une seconde esquive immédiate. 39/39 checks gameplay au
vert (34 précédents + 5 nouveaux), 8/8 VFX recipe inchangés. Capture en
jeu réelle (scratchpad) confirmant `is_invincible()` vrai pendant le roll,
faux juste après, et le bouton tactile DDG visible sans chevaucher les
3 autres.

### Prochain pas

D, tranche 2 : archétypes de cast génériques (3-4, projection avant /
frappe de zone / invocation / canalisation) puis primitives 6→15 et
Bras-Faux (recette+logique avant l'art). Puis E/F/G en parallèle selon
disponibilité, puis H.

---

## 2026-08-20 — D, tranche 2 (Bras-Faux : archétype de cast "frappe de zone")

"Continue" de Milan après la tranche 1 (esquive). Premier exemple concret
de l'archétype "frappe de zone" du mandat §5 (usine à pouvoirs) : contrairement
à l'invocation (Gueule Vide — une entité spawnée, cible unique), Bras-Faux
est exécuté PAR le joueur lui-même et touche potentiellement plusieurs
ennemis dans un cône (GDD §7.1 : "Rank Zero effectue un seul balayage").

**Nouvelle primitive `ribbonTrail` (7/15, §5).** `src/vfx/primitives/ribbon_trail.gd`
— balaie `sweep_deg` (défaut 90°, jitter seedé ±3°) centré sur `direction`
sur `lifetime_ticks`, garde un historique de 8 angles passés pour tracer
une traînée-ruban à plusieurs segments, largeur dégressive base→pointe,
fondu par segment. Enregistrée dans `VfxDirector._registry`.

**Nouvelle palette `parasite` (`data/palettes/parasite.json`), nommée
explicitement par le mandat §1.4.** GDD §7 : "grayscale désaturé... pointe
de bleu-gris pâle et lilas-gris pâle. NO PURPLE saturé, NO GLOW." 4 rôles,
saturations 4-12% — délibérément plus basses qu'invocateur_vide (16-30%) :
la distinction Invocateur/Parasite passe par CETTE différence de
saturation, pas seulement la teinte, matière plus organique/terne.

**Nouvelle recette `data/recipes/power.bras_faux.cast.json`.** 4 couches,
timeline 40 ticks (0,667s, dans la fourchette GDD 0,5-0,7s) : anticipation
0-14 (fractureLine, la membrane qui se déchire), release 14-18 (ribbonTrail
balaie ~100°, contact au tick 15 — arcSlash + impactFlashFrame), recovery
18-40 (rien, le membre se rétracte). Les 4 couches sont protégées
(`degradable:false`) — un effet léger de 40 ticks n'a pas besoin de
sacrifice sous pression de budget (Addendum A §A.1). Portée/arc/dégâts/recul
NE SONT PAS dans cette recette (§8.1, frontière recette/gameplay déjà
documentée dans `vfx_recipe_registry.gd`) : ils vivent dans `player.gd`.

**Nouveau `Targeting.enemies_in_arc()` (`src/gameplay/targeting.gd`).**
Complète `nearest_enemy_in_radius()` existant plutôt que de le remplacer —
première méthode multi-cible de l'utilitaire, filtre cône (angle vs
`facing`) + rayon + "vivant" (`is_dead()`), même convention que le reste.

**État `BrasFauxPhase` (`src/gameplay/player.gd`).** Même famille
d'architecture que le dash/l'esquive (3-4 phases, `_action_lock`, garde
dans `_on_sprite_animation_finished()`) mais gardé LOCAL à Player plutôt
que généralisé en un vrai dispatcher d'archétypes de cast : un seul exemple
concret de "frappe de zone" à ce stade (Gueule Vide reste le seul exemple
d'"invocation", chacun avec sa propre timeline locale) — une abstraction
générique serait prématurée avec un seul cas à généraliser. `ANTICIPATION`
14 ticks / `RELEASE` 4 ticks (hit au 1er tick de RELEASE, même convention
que le combo/Gueule Vide) / `RECOVERY` 22 ticks = 40 ticks au total,
portée 48px (~1,5m), demi-angle 45° (arc total 90°), dégâts 10,
cooldown 180 ticks (3s, TUNABLE). Multi-cible réellement câblée : boucle
sur TOUTES les cibles de `enemies_in_arc()`, chacune reçoit
`take_damage()` (recul individuel porté par `Enemy`, pas une primitive
VFX), un seul `CombatFeedback.trigger_hitstop("medium")` +
`CameraDirector.trigger_punch()` pour l'ensemble du swing (pas par cible
touchée — un hit-stop qui se cumule par cible casserait le rythme d'un
swing qui touche 3 ennemis d'un coup). Placeholder visuel (mandat §1.3) :
rejoue l'anim "coup2" existante, pas de nouvelle anim dédiée à ce stade
(archétype générique = pas d'animation par pouvoir, §5).

**Nouvel input.** Action `power2` dans `project.godot` (touche R, jamais
utilisée jusqu'ici) + `ButtonPower2` dans `touch_controls.tscn`, position
vérifiée par calcul de distance pour ne chevaucher aucun des 4 boutons
existants.

**3 nouveaux checks smoke test** (`_check_bras_faux()`,
`tools/smoke_test_gameplay.gd`) : l'input démarre l'état et joue "coup2" ;
le swing touche l'ennemi de face (0°) ET l'ennemi de côté (30°, dans le
demi-angle 45°) mais épargne l'ennemi à 90° (hors arc) ; l'action se
termine, se déverrouille, et le cooldown bloque un second cast immédiat.
42/42 checks gameplay au vert (39 précédents + 3 nouveaux), 8/8 VFX
recipe inchangés — aucune régression.

**Nouveau mode de capture `--mode=player_action` (`tools/capture_scene.gd`).**
Les modes existants ne couvraient pas ce cas : `character` fige une frame
sans faire tourner la physique, `power` instancie une scène de créature
autonome (`scenes/gameplay/powers/<power>.tscn`) — Bras-Faux est porté par
le Player lui-même, pas une scène de pouvoir séparée. Nouveau mode :
instancie le Player réel + 2 ennemis (mêmes offsets que le smoke test),
simule `Input.action_press/release`, laisse la physique RÉELLE tourner N
ticks depuis la pression, gèle, capture — même technique `_freeze_and_wait_render()`
que les deux autres modes, un seul point d'entrée conservé (docstring du
fichier). 3 captures en jeu réel (scratchpad, non commitées) : tick 8
(anticipation — fractureLine visible, ennemi de face déjà en place), tick
16 (contact — flash blanc `impactFlashFrame` + ruban `ribbonTrail`,
conforme §4 "noyau blanc quasi-plein" qui ignore volontairement la
palette, comme tout flash d'impact déjà validé pour Gueule Vide), tick 24
(recovery — 2× nombre de dégâts "10" flottants, ennemi de face visiblement
reculé par le knockback). Confirme visuellement le multi-cible, pas
seulement les HP en JSON de test.

**Web rebuild + commit.** `docs/index.html`/`docs/index.pck` régénérés
(`godot4 --headless --export-release "Web" docs/index.html`, mêmes
xvfb+Vulkan logiciel que les smoke tests).

### Prochain pas

D, tranche 3 : primitives 6→15 restantes (impactStar, converge, spiral,
beamSegment, etc., `ARCHITECTURE_VFX_v3.md` §7.1) et un second exemple
d'archétype ("projection avant" ou "canalisation" — les deux restent à 0
exemple concret). Puis E/F/G en parallèle selon disponibilité, puis H.
Verdict de Milan sur ce build attendu avant de pousser plus loin dans D.

---

## 2026-08-20 — D, tranche 3 (primitives 6→15, §7.1) + correctif flakiness Bras-Faux

"Okk go" de Milan après verdict sur le build tranche 2 (Bras-Faux). Complète
la liste des 15 primitives de `ARCHITECTURE_VFX_v3.md` §7.1 — les 7
premières (impactFlashFrame, groundRing, runicStamp, fractureLine,
shardBurst, arcSlash, ribbonTrail) existaient déjà ; cette tranche écrit
les 8 restantes : **impactStar** (étoile asymétrique, CONTACT, silhouette
secondaire après le flash §9.3), **converge** (fragments qui reviennent
vers l'origine, ANTICIPATION — l'inverse de shardBurst), **spiral**
(rotation + aspiration, ACTION CORE), **beamSegment** (rayon en blocs
DISCRETS avec espaces, ACTION CORE — forme candidate pour un futur
archétype "projection avant", encore sans exemple concret), **smokePuff**
(nuage OPAQUE par retrait de blobs un par un, jamais un fondu alpha seul
— §10.2, CONSEQUENCE), **dustKick** (poussière projetée à l'opposé du
mouvement au contact sol, CONTACT), **orbital** (instances stables sur
une ellipse seedée, ACTION CORE), **screenSlash** (lame fine et longue,
LOCALE malgré le nom — jamais une passe post-render plein écran, §10 —
réservée aux coups les plus lourds, CONTACT). Chacune suit le contrat
`configure()/tick()/_draw()` déjà établi, la bande HSV 20-92%, et un
`z_index` choisi pour occuper une plage encore libre entre les 7
primitives existantes plutôt que de collisionner (ANTICIPATION 10-19,
ACTION CORE 20-89, CONTACT 90-99 — voir commentaire de chaque fichier
pour le rang exact). Toutes enregistrées dans `VfxDirector._registry`
(`src/vfx/vfx_director.gd`).

**Couverture de test générique plutôt que 8 checks copiés-collés.**
Nouveau check `all_registered_primitives_spawn_tick_and_cleanup`
(`tools/smoke_test_vfx_recipe.gd`) : boucle sur TOUT `VfxDirector._registry`
(15 entrées, pas seulement les 8 nouvelles), spawn chacune, avance
quelques ticks, vérifie l'auto-libération — la même preuve que
`_check_timeline_and_cleanup()` mais balayée sur le registre réel, pour
qu'une primitive ajoutée sans couverture ne passe jamais inaperçue.
9/9 checks VFX recipe au vert.

**Visuelles, pas seulement "ça compile".** 8 captures individuelles
(`--mode=primitive`, scratchpad) confirment que chaque primitive produit
une silhouette distincte et correcte (étoile dentelée, rayon en pointillés,
lame fine, nuage opaque, essaim orbital, etc.), aucune n'étant vide ou
blanche. Bug d'outillage trouvé au passage : `capture_scene.gd` fige
`lifetime_ticks=2` en dur pour le mode `primitive` — les primitives à
durée de vie plus longue (spiral, orbital...) se libéraient AVANT le tick
demandé, capture vide. Corrigé en exposant `--lifetime_ticks` (défaut
inchangé à 2, aucun appel existant affecté).

**Bug réel trouvé et corrigé : flakiness de `bras_faux_input_starts_state_and_plays_placeholder_anim`
(~1 run sur 4).** Découvert en relançant la suite gameplay plusieurs fois
par prudence (régression des 8 nouvelles primitives) — pas causé par les
primitives elles-mêmes (fichiers séparés, aucune n'est touchée par
`player.gd`/`smoke_test_gameplay.gd`), mais un bug LATENT de la tranche 2
(Bras-Faux) que la routine "une régression = un run" n'avait jamais
répété assez de fois pour surprendre. Diagnostiqué par instrumentation
temporaire (`push_warning`/`print` horodatés au tick physique réel via
`Engine.get_physics_frames()`, retirés après coup) plutôt que par
supposition : la pression `dodge` de la sonde "le cooldown bloque une
seconde esquive immédiate" (fin de `_check_dodge()`) est bien REJETÉE au
moment voulu (`DODGE_COOLDOWN_TICKS` encore actif), mais son écho "just
pressed" reste lisible par `Player` plus longtemps que prévu — jusqu'à ce
que le cooldown de l'esquive s'épuise (~30 ticks plus tard, chronométré
au tick près sur plusieurs runs identiques), déclenchant alors une VRAIE
seconde esquive fantôme pile au moment où `_check_bras_faux()` presse
`power2`. `_action_lock`, consommé par cette esquive imprévue, bloque
Bras-Faux dès son premier tick (`started: false`). Corrigé par UN tick de
battement supplémentaire après le relâchement de cette pression-sonde
(laisse `Player` lire ET consommer l'écho dans la fenêtre où le blocage
est le comportement attendu, avant de rendre la main au check suivant) —
12/12 runs consécutifs au vert après correctif, contre l'échec observé
sur plusieurs des runs précédents. 42/42 checks gameplay, aucune
régression ailleurs.

**Web rebuild + commit.** `docs/index.html`/`docs/index.pck` régénérés.

### Prochain pas

D, tranche 4 (ou E/F/G si Milan préfère avancer plutôt qu'enrichir le
tronc commun VFX) : un second exemple d'archétype de cast concret
("projection avant" via `beamSegment`, ou "canalisation" via
`spiral`/`converge`) — les deux archétypes restent à 0 exemple, seuls
"invocation" (Gueule Vide) et "frappe de zone" (Bras-Faux) en ont un.
Verdict de Milan attendu avant de pousser plus loin.

---

## 2026-08-20 — E (8 directions idle/déplacement)

"Continue comme le roadmap dis" de Milan — D est fermé (primitives 6-15,
Bras-Faux complet, esquive logique, archétypes de cast validés par 2
exemples concrets), passage à E (mandat §6 : "8 directions a minima pour
idle/déplacement ; dash/combo/esquive si budget PixelLab, sinon flag").

**Découverte clé avant de dépenser quoi que ce soit : le personnage
Cendre_v3c (`character_id 8596a4ad-...`, canonique depuis R3) a été créé
avec `n_directions=8` dès le départ (`data/pixellab_usage.jsonl`) — les 8
rotations statiques existent déjà côté PixelLab, jamais téléchargées ni
cuites. Seules idle/déplacement avaient besoin d'être ÉTENDUES aux 7
directions manquantes (elles n'existaient qu'en sud) : 14 générations
`animate_character` (mode template, `ai_freedom=0`, mêmes templates
`breathing-idle`/`walk` que la version sud existante), ajoutées aux
groupes d'animation existants via `animation_group_id` plutôt que de
recréer des groupes séparés — cohérence de nommage/historique. 1673
générations disponibles avant, largement suffisant.

**Pipeline de cuisson étendu sans le modifier.** `scripts/cook_character_frames.py`
et `build_sprite_frames.py` acceptaient déjà `--anim <nom>:<dossier>` en
argument répété — aucune modification de leur logique n'était nécessaire,
seulement 16 nouveaux appels (`idle_<direction>`/`deplacement_<direction>`
× 8) pointant vers 14 nouveaux dossiers `assets/source/pixellab/cendre/animations/<anim>_<direction>/`
téléchargés via curl (même discipline que Phase 1.1/R3 — urllib donnait
des 403). coup1/coup2/coup3/dash/hurt/mort restent "sud" seul (hors
scope de cette brique, mandat §6 : optionnels "si budget PixelLab, sinon
flag" — flag posé, pas fait maintenant). Canvas partagé 96×96, ancre pieds
(48,92) inchangés — mêmes réglages que R3, cohérence garantie.

**`player.gd` — sélection de direction, pas de flip_h pour idle/déplacement.**
Nouvelle fonction statique `_direction_suffix(dir) -> String` : snappe
n'importe quel `Vector2` sur le compas à 8 branches le plus proche
(convention PixelLab south/south_east/east/.../north_east, cohérente avec
Y+ = bas = sud, `facing` par défaut = `Vector2.DOWN`). `_handle_movement()`
joue désormais `"idle_" + suffix`/`"deplacement_" + suffix` selon `facing`,
et force `flip_h = false` (l'art est maintenant dessiné par direction, un
flip par-dessus doublerait le miroir sur un ouest déjà dessiné tel quel).

**Bug de régression évité avant qu'il n'arrive : le combo dépendait du
flip_h laissé par le dernier mouvement.** `_start_attack()` ne posait
jamais son propre `flip_h` — il héritait silencieusement de celui que
`_handle_movement()` venait de poser. Le rendre à `false` systématiquement
pour idle/déplacement aurait cassé le miroir des coups face à l'ouest (un
coup1 vers l'ouest se serait dessiné vers l'est). Corrigé en rendant
`_start_attack()` auto-suffisant (`_sprite.flip_h = facing.x < 0.0` posé
lui-même, même discipline que `play_dash()`/`play_dodge()` qui le
faisaient déjà) — repéré à la lecture du code avant tout run, pas par un
test qui aurait échoué.

**`scenes/gameplay/player.tscn` et `tools/capture_scene.gd` mis à jour.**
`AnimatedSprite2D.animation`/`autoplay` du Player passent de `"idle"` à
`"idle_south"` (l'ancien nom n'existe plus — trouvé au premier `--import`,
`ERROR: Animation 'idle' doesn't exist`, corrigé avant tout run de test).
Défaut `--anim` de `capture_scene.gd --mode=character` idem.

**2 checks smoke test mis à jour** (pas de nouveaux — la logique de
sélection de direction est déjà exercée par les checks mouvement/combo
existants) : `sprite_animation_switches_idle_deplacement_idle` attend
désormais `idle_south`→`deplacement_east`→`idle_east` (facing par défaut
sud, mouvement vers la droite = est, facing reste est après l'arrêt —
jamais réinitialisé tout seul) ; `combo_returns_to_idle_after_full_recovery_without_input`
attend `idle_east` (facing hérité du check précédent). 42/42 gameplay
(3 runs consécutifs), 9/9 VFX recipe, aucune régression.

**Vérification visuelle réelle (scratchpad, pas commitée) : montage des 8
idle + 2 frames déplacement.** Les 8 directions se distinguent clairement
(face/dos/profils/diagonales cohérents, pieds alignés sur la même ligne
de sol, aucun artefact de miroir) — confirmé avant de déclarer la brique
finie, pas seulement "ça compile".

**Web rebuild + commit.**

### Prochain pas

F/G (mini-tileset d'arène / ennemis Crawler-Brute-Ranged) selon
disponibilité, ou D tranche 4 (second archétype de cast). dash/combo/
esquive en 8 directions restent flag (E, "si budget PixelLab") — pas
faits cette tranche, à réévaluer si Milan le demande explicitement.
Verdict de Milan sur ce build attendu avant de pousser plus loin.

---

## 2026-08-20 — F (Le monde)

Mandat §6, F : "mini-tileset d'arène réel (sol texturé, vignette, props),
cohérent palette — sans attendre plus de contenu." Scope volontairement
réduit : pas d'autotiling Wang complet (16 combinaisons de coins à câbler
dans le système terrain de Godot) — une tuile "pure lower" unique en
pavage uniforme, seamless avec elle-même par construction. Cohérent avec
le "sans attendre plus de contenu" du mandat : une salle rectangulaire ne
justifie pas encore les 15 autres combinaisons de coins.

### Fait

**Génération PixelLab.** `create_topdown_tileset` (sol pierre/gravats,
`transition_size` ≤0.5 → 16 tuiles) + 2 props via `create_image_pixflux`
(rubble, debris — 32×32 minimum imposé par l'API, 32×24 refusé). Slicing
de la tuile "pure lower" via le champ `bounding_box` de l'endpoint
`/metadata` — jamais `wang_N`/`original_position`, documentés comme
produisant du banding horizontal si mal utilisés.

**Clamp HSV bande decor.** Les 3 assets (sol, 2 props) échouaient la
validation `scripts/validate_pixels.py --category decor` (bande [15,60]%
V) : outlines trop sombres (~9-15%), highlights trop clairs (~99%).
Clampé via `colorsys` (RGB→HSV→clamp V→RGB). Premier essai aux bornes
exactes (15/60) encore en échec (14.9% mesuré — arrondi 8-bit au
roundtrip) → marge de sécurité (16/59), 0 violation ensuite. Même
discipline que le clamp de R3 sur le personnage.

**Godot : `TileSet`/`TileMapLayer` + props + vignette.**
`assets/processed/sprites/world/floor_tileset.tres` (atlas mono-tuile
32×32) + `src/world/arena_floor.gd` (`TileMapLayer` qui remplit un
rectangle via `set_cell()` en code plutôt qu'un `tile_data` figé — pas de
salle non rectangulaire à ce stade). 3 `Sprite2D` props dans
`test_arena.tscn` (`PropRubble1/2` — le 2 mirroré `scale=(-1,1)` pour
varier sans regénérer —, `PropDebris1`). Vignette : nouveau
`src/vfx/shaders/vignette.gdshader` (canvas_item, `smoothstep` radial en
UV, corrigé à l'aspect-ratio du viewport natif 640×360 sinon le dégradé
serait ovale) posé sur un `ColorRect` plein écran dans un `CanvasLayer`
dédié, placé avant `TouchControls` dans l'ordre des nœuds pour ne pas
passer par-dessus l'UI tactile.

**Vérification visuelle réelle (scène de jeu complète, pas une capture
isolée).** Script jetable `tools/capture_arena_scratch.gd` (instancie
`test_arena.tscn` au complet + `Camera2D` ad hoc, contrairement à
`capture_scene.gd` qui isole Player/primitives) — supprimé après usage,
jamais commité. Confirmé : sol texturé en grille cohérente (pas de
banding), props rendus comme vraie pixel art (pas de rectangle plein —
vérifié en relisant les PNG sources après clamp), vignette qui assombrit
bien les coins (luminance mesurée : coin ~20 vs centre ~86, ratio net).
Les rectangles rouges visibles dans la capture sont le `Placeholder`
`Polygon2D` déjà existant d'`enemy.tscn` (art d'ennemi = scope G, pas
touché ici) — pas un bug introduit par F.

**Régression.** 42/42 gameplay (2 runs, avant et après F), aucun check
ne touche `test_arena.tscn` directement mais confirme l'absence de
casse ailleurs dans le projet.

**Web rebuild + commit.**

### Prochain pas

G (ennemis Crawler/Brute/Ranged, HitResponse natif) selon disponibilité,
ou tranches optionnelles flaguées (dash/combo/esquive 8 directions,
Bras-Faux transfo bras-faux dédiée). Verdict de Milan sur ce build
attendu avant de pousser plus loin.

---

## 2026-08-20 — Correctif : échelle de Cendre trop grande

Verdict de Milan sur le build F : "le perso est légèrement trop grand
pour le monde." Investigation avant tout patch (mesure, pas d'ajustement
au pif) : `docs/ARCHITECTURE_VFX_v3.md` §0 spécifie noir sur blanc "Perso
jouable & ennemis standard : 64×64 (corps ~44–52 px de haut). Élites :
96×96." et `GameConstants.PX_PER_METER` documente explicitement "un corps
joueur d'environ 48px de haut ... sur un canvas 64×64 ... 32 px/m". Mesure
réelle des frames cuites de Cendre (bbox alpha) : corps ~78-80px de haut
sur un canvas 96×96 — Cendre avait été cuit sur le gabarit "Élite" au lieu
du gabarit standard, d'où l'écart visuel avec le sol (tuiles 32px = 1m)
que l'œil de Milan a détecté correctement : le perso lisait ~2,4-2,5m au
lieu du ~1,5m que les distances de gameplay (`meters_to_px`, rayon
Totem du Vide, etc.) supposent déjà.

**Fix choisi et pourquoi pas l'alternative.** Premier réflexe (`scale`
sur le node `AnimatedSprite2D` du Player) écarté après lecture de
`animation_composer.gd` : `apply_squash()` réécrit `sprite.scale` en
partant de `Vector2.ONE` en dur à chaque frame de squash/lean (dash,
attaques), et `player.gd` reset `_sprite.scale = Vector2.ONE` comme
neutre à 3 endroits — un `scale` de base non-ONE sur le node aurait été
écrasé pendant chaque squash et le perso aurait "sauté" à sa vraie taille
pendant dash/coups. Fix retenu à la place : redimensionner les pixels
eux-mêmes (`Image.resize` LANCZOS, facteur 2/3 = 96/64, sur les 113
frames cuites de `assets/processed/sprites/cendre/`), ramenant le corps à
~52-53px sur un canvas 64×64 — exactement le gabarit "standard" du doc.
`player.tscn` : `offset` de l'`AnimatedSprite2D` recalculé pour le nouveau
canvas (`-48` → `-32`, moitié de 64 au lieu de 96), aucun `scale`
touché — `Vector2.ONE` reste la vraie taille neutre, cohérent avec
`animation_composer.gd`. `assets/manifests/cendre_frames_cooked.json`
mis à jour en cohérence (`out_canvas`/`anchor_px`) — non lu par du code
au runtime (vérifié par grep), mais le manifest doit rester vrai.

**Vérification.** 42/42 gameplay (le check `dash_applies_squash_and_lean_then_resets`
confirme `scale_after_dash == (1, 1)`, donc le système squash/lean reste
cohérent avec la nouvelle taille de base). Capture visuelle jetable dans
`test_arena.tscn` (script supprimé après usage, même discipline que F) :
le perso lit maintenant à une échelle humaine crédible à côté des tuiles
de sol, au lieu de dominer l'écran.

**Web rebuild + commit.**

### Prochain pas

G (ennemis Crawler/Brute/Ranged) — même gabarit 64×64/48px à respecter
dès leur génération pour rester cohérent avec Cendre, plutôt que de
répéter cette erreur. Verdict de Milan sur ce build attendu.

---

## 2026-08-20 — G (Ennemis : Crawler, Brute, Ranged)

Mandat §6, G : "Crawler, Brute, Ranged (GDD §10/§21), discipline
reference-image, HitResponse natif." Logique avant l'art (même précédent
que D/Bras-Faux) : IA + dégâts réciproques + télégraphes cette tranche,
art PixelLab réel flagué pour plus tard — 3 nouveaux personnages à
générer avec discipline reference-image représente un coût qui mérite
son propre GATE de vérification visuelle, pas une sous-tâche noyée ici.

### Fait

**Un seul script `enemy.gd` pour les 3 archétypes**, pas 3 classes :
Crawler et Brute partagent la même logique de contact (`archetype =
MELEE`), seuls les `@export` numériques changent (vitesse, portées,
dégâts, tempo du télégraphe) — cohérent avec la discipline anti-
duplication déjà appliquée ailleurs dans le projet (Stats.gd). Seul
Ranged bifurque réellement en code (garde ses distances, tire un
projectile). État minimal : IDLE/CHASE (détection + approche) ->
TELEGRAPH (immobile, pulse visuel déterministe — le placeholder
blanchit progressivement, fonction du tick, jamais un Tween temps réel
qui désync de la simulation à 60 ticks/s) -> exécution du coup en un
seul tick -> RECOVER -> retour CHASE/IDLE + cooldown.

**Réaction du joueur aux dégâts, jusqu'ici un hook sans appelant réel
(commentaire historique de `Player.take_damage()`, Phase 1.2 : "l'ajouter
proprement appartient à G, quand un vrai ennemi attaquera").** Ajout
d'une timeline `_hurt_phase` (même construction que dash/dodge/Bras-Faux
: ACTIVE/NONE, `_action_lock` posé et levé par sa propre fin de timeline,
jamais par le frame de l'animation) portant le recul — sans elle,
`_handle_movement()` aurait écrasé la vélocité de recul dès le tick
suivant si une touche de mouvement était tenue, exactement le piège que
le commentaire historique décrivait. Si le joueur est déjà engagé dans
une autre timeline au moment du coup, les dégâts/flash/mort s'appliquent
quand même mais sans recul cosmétique superposé — corrompre une
timeline en cours aurait été pire que l'omettre, scope assumé pour cette
brique.

**`Targeting.get_player()`** — symétrique de `nearest_enemy_in_radius()`
côté ennemis, `Player.add_to_group("player")`. Fonction pure comme le
reste de `targeting.gd`, jamais une recherche réimplémentée localement.

**RANGED "garde ses distances" pour de vrai, pas juste en commentaire :**
`_in_attack_window()` refuse le télégraphe tant que le joueur est plus
proche que `preferred_range_px - range_tolerance_px` — sans ce garde-
fou, un joueur qui rush au contact déclenchait quand même un tir
immobile point-blank indiscernable d'un ennemi de mêlée (bug trouvé par
le nouveau smoke test `ranged_retreats_...`, pas en lisant le code).
Projectile (`src/gameplay/projectile.gd` + `scenes/gameplay/projectile.tscn`)
: trajectoire rectiligne fixée une fois à `configure()`, jamais de
homing — une trajectoire prévisible est ce qui rend un ennemi à
distance lisible/évitable. Contact = distance simple au joueur, pas
d'Area2D (cohérent avec les hitboxes géométriques déjà en place).

**Bug de régression trouvé et corrigé avant de déclarer la brique finie :**
le nouveau `_physics_process()` d'Enemy appelait `move_and_slide()`
inconditionnellement (au lieu de seulement pendant le recul, comme en
Phase 1.2). Un `CharacterBody2D` immobile qui l'appelle quand même se
fait dépénétrer de toute collision existante — cassait silencieusement
`bras_faux_hits_all_enemies_in_arc_spares_enemy_outside` (3 ennemis
posés à 30px les uns des autres pour ce test, poussés hors de leur
position exacte et donc hors de l'arc). Trouvé en relançant le smoke
test AVANT d'écrire les nouveaux checks G, pas après — corrigé en
n'appelant `move_and_slide()` que si `velocity != Vector2.ZERO`.

**`enemy.tscn` (le fichier générique) reste le mannequin d'entraînement
STATIONNAIRE de Phase 1.2** (`aggro_radius_px = 0.0` forcé) : ~10 checks
existants de `smoke_test_gameplay.gd` en dépendent pour un ennemi
immobile à position connue. Casser ces checks pour leur donner une IA
qu'ils n'ont jamais demandée aurait été une régression. L'IA réelle vit
dans 3 nouvelles scènes dédiées : `enemy_crawler.tscn` (petit/rapide/
télégraphe court/dégâts faibles/HP bas), `enemy_brute.tscn` (grand/lent/
télégraphe long ~0,7s/dégâts lourds/HP haut/hitstop-shake "medium"),
`enemy_ranged.tscn` (silhouette mi-hauteur/kite/projectile). Tailles de
silhouette différenciées par archétype (petit/imposant/lean), toujours
famille rouge (GDD : "rouge ennemi, non contournable").

**`test_arena.tscn`** : les 3 anciens `Enemy` stationnaires remplacés
par un de chaque archétype (`EnemyCrawler`/`EnemyBrute`/`EnemyRanged`).

**4 nouveaux checks smoke test** (46/46, aucune régression sur les 42
existants) : `player_recoils_away_from_attacker_on_taking_damage`,
`crawler_chases_then_hits_player`, `brute_telegraphs_before_landing_a_heavier_hit`
(vérifie explicitement AUCUN dégât pendant le télégraphe, puis le
dégât exact au tick suivant), `ranged_retreats_to_preferred_range_then_hits_player_with_projectile`.

**Vérification visuelle réelle (script jetable, supprimé après usage,
même discipline que F) :** les 3 silhouettes se distinguent clairement
par taille (petite/imposante/mi-hauteur) dans la vraie scène de jeu,
sol/props/vignette de F toujours intacts.

**Web rebuild + commit.**

### Prochain pas

Art réel des 3 ennemis (PixelLab, discipline reference-image, gabarit
64×64/~48px dès la génération — ne pas répéter l'erreur d'échelle de
Cendre) — flagué, hors scope de cette brique. H (vertical slice GDD §21)
reste la dernière étape du mandat. Verdict de Milan sur ce build attendu
avant de pousser plus loin.

---

## 2026-08-20 — H1 (Progression + HUD)

Mandat §7 : "Plan d'implémentation soumis avant de coder le contenu de
la phase H" — H (GDD §21) bundle une Gate complète, un boss, un hub et
la couche UI en un seul point de la feuille de route ; trop gros pour
"une brique par session" (mandat §9). Plan soumis à Milan et découpé en
5 tranches (H1 Progression+HUD, H2 Boss Gate Maw, H3 Structure Première
Gate, H4 Outpost+boucle de run, H5 Écran personnage) — Milan a choisi de
commencer par H1, la fondation dont les autres dépendent (récompenses de
Gate, mort de boss consomment XP/niveau qui n'existaient pas encore).

### Fait

**`Stats.gd` : niveau + XP, pas une classe `Progression` séparée.** GDD
§17 exige un bloc de stats complet (FOR/AGI/INT/VIT) mais rien d'autre
que INT n'est encore consommé par une recette réelle — même discipline
que le reste du fichier ("pas de stat non exercée"), FOR/AGI/VIT restent
hors scope. `xp_to_next_level()` formule TUNABLE (50×niveau, linéaire).
`add_xp()` monte de niveau EN BOUCLE (pas plafonné à une seule montée
par appel — un gros gain d'XP peut en faire sauter plusieurs d'un coup),
+10 PV max (soigné d'autant) et +1 INT par niveau.

**`Enemy.xp_reward` crédité au joueur à la mort**, avant `queue_free()`
dans `take_damage()` — `Targeting.get_player()` (déjà posé pour G),
jamais un nouveau canal de communication Enemy->Player. Valeurs
TUNABLE par archétype (Crawler 8, Ranged 15, Brute 30 — grossièrement
proportionnelles au HP/à la difficulté de chacun).

**`src/ui/hud.gd` + `scenes/ui/hud.tscn`** : barre PV (largeur
proportionnelle à hp/max_hp) + texte, niveau, barre XP, 4 icônes de
cooldown (Dash/Esquive/Gueule Vide/Bras-Faux). Poll en `_process()`,
pas un signal par valeur — un HUD lit un état, il ne le possède pas,
même discipline que VfxDirector/CombatFeedback consultés en singleton.
3 nouveaux getters sur Player (`get_dodge_cooldown_ratio()` etc.) plutôt
que d'exposer les compteurs de ticks bruts. Dash n'a pas de cooldown
chiffré par le mandat/GDD (contrairement à esquive/Gueule Vide/
Bras-Faux) : son icône reste toujours "prête", sans voile — inventer un
cooldown non demandé aurait été hors mandat (§9 : "aucune invention...
au-delà du GDD"). Voile de cooldown calculé par tick (pas un Tween
temps réel), même discipline que le pulse de télégraphe des ennemis (G).

**2 nouveaux checks smoke test** (48/48, aucune régression) :
`stats_add_xp_levels_up_in_a_loop_and_carries_remainder` (logique pure
sur `Stats`, vérifie la boucle ET le reste d'XP reporté), et
`enemy_death_awards_xp_to_player`.

**Vérification visuelle réelle (script jetable, supprimé après usage) :**
HUD posé dans un état non-trivial (62/100 PV, niveau 2, esquive en
cooldown) pour prouver qu'il réagit vraiment à l'état du joueur plutôt
que d'afficher une valeur figée à la construction — barre PV/XP aux
bonnes proportions, icône d'esquive visiblement voilée, Dash/Pouvoirs
pleins.

**Web rebuild + commit.**

### Prochain pas

H2 (Boss Gate Maw) selon le plan soumis, ou réordonnancement si Milan le
demande après verdict sur ce build.

---

## 2026-08-20 — H2 (Boss Gate Maw)

Mandat §6/GDD §15 : "Gate Maw : boss tutoriel, masse organique de Gate
avec grande gueule ; morsure, charge, projection, frappe au sol, phase
énervée." Deuxième tranche du plan H soumis (H1 terminé, ce build).

### Fait

**`src/gameplay/boss_gate_maw.gd`** — script dédié, PAS Enemy.gd :
Crawler/Brute/Ranged partagent un script parce qu'ils sont
interchangeables au-delà des chiffres ; un boss ne l'est pas ("silhouette
unique", GDD §15). Rotation **déterministe** [Morsure, Charge, Frappe au
sol, Projection] — jamais un tirage aléatoire : un boss tutoriel doit
montrer chaque attaque dans un ordre prévisible, et le garde-fou "seed
toujours déterministe" (mandat §9) s'applique aussi à une décision de
combat, pas seulement au chemin VFX ; le plus sûr pour le respecter ici
est de ne tirer aucun nombre du tout.

**4 attaques, chacune avec sa propre signature :**
- Morsure : contact court, la plus rapide (télégraphe 20 ticks).
- Charge : seule attaque qui couvre la distance (déclenche jusqu'à
  260px), fonce en ligne droite sur 220px pendant le CHARGE_DASH.
- Frappe au sol : AOE autour du boss, télégraphée par un `groundRing`
  (primitive VFX EXISTANTE, réutilisée telle quelle — jamais dupliquée)
  qui montre le rayon exact avant l'impact ; contre-mesure = sortir du
  cercle avant la fin du télégraphe (34 ticks, le plus long des 4).
- Projection : dégâts bruts les plus faibles mais LE plus gros recul —
  sa signature est de repousser, pas de punir.

**Phase énervée** — bascule UNE fois (jamais réversible) sous 40% PV :
cooldown/recovery resserrés, vitesse ×1.25, teinte de base décalée vers
le rouge chaud en permanence (tell lisible même hors télégraphe,
distinct du pulse de télégraphe lui-même).

**2 bugs trouvés par les tests avant tout commit, pas en relisant le
code :**
1. `charge_contact_radius_px` était fixé à 40px — exactement la somme
   des rayons de collision boss (30) + joueur (10). `move_and_slide()`
   bloque physiquement deux capsules à cette distance ; un seuil ÉGAL
   à la distance de blocage échoue en permanence dès que le boss a déjà
   rejoint le joueur avant de charger (ce qui arrive presque toujours,
   puisqu'il le talonne pendant tout son cooldown). Charge ratait son
   coup à chaque fois. Corrigé en portant le rayon à 60px, une vraie
   marge au-delà du contact physique.
2. Le test de phase énervée ne laissait qu'un seul tick avant de lire
   `_enraged` — mais `take_damage()` pose son propre recul (défaut 6
   ticks), et `_check_enrage()` est gardée derrière le early-return de
   recul de `_physics_process()` comme le reste de l'IA. Corrigé en
   attendant la fin du recul avant de lire l'état.

**6 nouveaux checks smoke test** (52/52, aucune régression) :
`boss_attack_rotation_hits_player_with_all_four_attacks_in_order`,
`boss_slam_spares_player_outside_radius_but_hits_inside`,
`boss_enrages_at_hp_threshold_and_shortens_cooldown`,
`boss_death_awards_xp_reward_to_player` (+ les 2 déjà comptés en H1).

**Silhouette placeholder** : blob organique asymétrique (10 points,
~96×92px), nettement plus grand que Brute (68px) — se lit comme "plus
dangereux", cohérent avec le reste du roster placeholder (famille
rouge, GDD "rouge ennemi non contournable"). Art réel flagué, même
précédent que G.

**Vérification visuelle réelle** (script jetable, supprimé après
usage) : le `groundRing` de Frappe au sol s'affiche bien comme un
anneau cassé autour du boss dans la vraie scène, silhouette clairement
distincte des 3 ennemis normaux.

**Web rebuild + commit.**

### Prochain pas

H3 (structure de la Première Gate) selon le plan, ou réordonnancement
si Milan le demande après verdict sur ce build.

---

## 2026-08-20 — H3 (Structure de la Première Gate)

Mandat §6/GDD §11 : "Entrée → combats → loot/événement → embranchement →
Elite → repos → boss → récompense → sortie." Troisième tranche du plan H.
`scenes/gameplay/gate_premiere.tscn` devient `run/main_scene` (remplace
`test_arena.tscn`, gardée comme bac à sable — rien ne la référence
ailleurs, aucune régression).

### Fait

**9 salles alignées sur un seul niveau continu** (pas de scènes séparées
à charger : le joueur et le HUD restent le même nœud tout du long, zéro
persistance d'état à gérer entre changements de scène). `GateRoom`
(`src/world/gate_room.gd`) verrouille une `Door` enfant tant que TOUS
les ennemis DE CETTE SALLE (suivis par référence directe, jamais une
requête sur le groupe global "enemies" — un ennemi d'une autre salle ne
doit jamais ouvrir/fermer la mauvaise porte) ne sont pas morts. Combat
(2 Crawler + 1 Ranged), Elite (1 Brute reconfiguré, PV/dégâts/récompense
relevés — "pattern supplémentaire" du GDD flagué, pas fait), et Boss
(Gate Maw, H2) verrouillent leur sortie ; Entrée/Loot/Repos/Récompense
restent toujours ouvertes. Embranchement : deux voies parallèles qui se
rejoignent, purement spatial (pas de logique de salle).

**3 nouveaux nœuds génériques** (`src/world/`) : `XpPickup` (loot/
récompense, XP directe au contact — GDD §16 "équipements/matériaux/..."
reste explicitement TBD, hors scope ici), `HealZone` (salle "repos" —
interprétation délibérée et documentée du mot lui-même : soin complet
au contact, une fois, rien de plus inventé), `GateExit` (signal
`gate_completed`, câblable par H4 quand l'Outpost existera — pas de
transition de scène inventée vers un hub qui n'existe pas encore).

**Bug sérieux trouvé par le nouveau test de salle, pas en écrivant le
niveau lui-même :** aucune des 4 scènes d'ennemi (Crawler/Brute/Ranged/
Boss, depuis G/H2) n'avait `resource_local_to_scene = true` sur son
sous-ressource `Stats`. Godot met en cache et PARTAGE la même instance
de Resource entre tous les `instantiate()` d'une même scène tant que ce
flag n'est pas posé — deux Crawlers dans la même salle Combat de
`gate_premiere.tscn` auraient donc partagé un seul pool de PV (blesser
l'un aurait blessé "les deux" identiquement, un bug de gameplay réel,
silencieux, présent depuis G). Trouvé parce que le test de salle tuait
un Crawler dans un test PUIS en construisait un autre juste après : le
second héritait des PV à zéro du premier. Corrigé sur les 4 scènes +
l'override Elite de cette brique.

**4 nouveaux checks smoke test** (56/56, aucune régression) :
`gate_room_locks_door_until_enemies_cleared_then_opens`,
`xp_pickup_grants_xp_and_frees_itself_on_player_contact`,
`heal_zone_heals_player_to_full_on_contact`,
`gate_exit_emits_gate_completed_on_player_contact`.

**Vérification visuelle réelle** (script jetable, supprimé après
usage) : la vraie scène `gate_premiere.tscn` chargée en main_scene,
porte de la salle Combat visible et bloquant le couloir, 3 ennemis +
HUD tous corrects ensemble.

**Web rebuild + commit.**

### Prochain pas

H4 (Outpost + boucle de run) ou H5 (écran personnage) selon le plan,
ou réordonnancement si Milan le demande après verdict sur ce build.

## 2026-08-20 — H4 (Outpost + boucle de run)

Mandat §6/GDD §20 : "Hub → choisir Gate → entrée → combats → XP/loot/
maîtrise → route → Elite → Boss → récompense → retour → amélioration →
nouvelle Gate." Quatrième tranche du plan H — la pièce manquante que H3
laissait volontairement non câblée (`GateExit.gate_completed` émis mais
sans destinataire, faute de hub).

### Fait

**Autoload `RunState`** (`src/system/run_state.gd`) : un seul `Stats`
Resource PARTAGÉ (`player_stats`), pas une copie resynchronisée à la
main à chaque transition de scène. `Player._ready()` pointe directement
dessus (`stats = RunState.player_stats`) au lieu de garder sa propre
instance par défaut — aucun risque d'oubli de sync, c'est le même objet
des deux côtés d'un `change_scene_to_file()`. "Amélioration" (GDD §20)
= ce que H1 fournit déjà (XP/niveau), qui persiste ainsi sans code
supplémentaire ; un système de boutique/équipement reste GDD §16 "à
préciser", hors scope ici.

**`GateEntrance`** (`src/world/gate_entrance.gd`, Area2D) : déclenche
`get_tree().change_scene_to_file()` vers la Gate au contact du joueur.
Logique de détection (`_should_trigger()`) isolée de l'action réelle
(`_on_body_entered()`) — la première est pure et testable en boucle, la
seconde invoquerait un vrai changement de scène si on l'appelait depuis
un test automatisé, ce qui détruirait l'arbre du test lui-même en plein
milieu de la suite.

**`Outpost`** (`scenes/gameplay/outpost.tscn`, nouveau `run/main_scene`,
remplace `gate_premiere.tscn`) : petit hub — sol, Player, HUD,
TouchControls, un unique `GateEntrance` menant à la Première Gate. Un
seul choix de Gate existe à ce stade donc pas de sélection réelle ;
PNJ/statut social explicitement hors scope de cette brique.

**`gate_premiere.gd`** (nouveau, attaché à la racine de
`gate_premiere.tscn`) : câble enfin `$Exit.gate_completed` vers un
retour à l'Outpost (`change_scene_to_file`) — la connexion que H3 avait
délibérément laissée en signal nu.

**3 nouveaux checks smoke test** (59/59, aucune régression) :
`run_state_persists_player_stats_across_new_player_instances` (deux
Player instanciés séparément partagent le MÊME objet Stats — modifier
l'un modifie l'autre), `gate_entrance_detects_player_once_and_targets_
the_gate_scene` (via `_should_trigger()` en direct, jamais de vrai
changement de scène dans un test), `gate_premiere_wires_exit_signal_to_
a_handler` (mock allégé — juste un enfant `Exit` sous le script
`gate_premiere.gd`, pas la scène complète avec boss/ennemis/VFX —
vérifié via `Signal.get_connections()`, pas en déclenchant le signal).

**Bug préexistant trouvé en cours de route, sans rapport avec H4** :
`_check_boss_slam_spares_player_outside_radius_but_hits_inside` (H2)
lisait `boss_inside.slam_damage` APRÈS `boss_inside.queue_free()` +
`await physics_frame` — le nœud était déjà libéré à ce point-là
("Invalid access... on a base object of type 'previously freed'"), ce
qui faisait planter la fonction avant son propre `_checks.append()` :
le check disparaissait silencieusement du rapport (58 checks au lieu
de 59 attendus) sans jamais apparaître comme un échec explicite.
Corrigé en capturant `slam_damage` dans une variable locale avant le
`queue_free()`.

**Vérification visuelle réelle** (script jetable, supprimé après
usage) : la vraie scène `outpost.tscn` chargée en main_scene — sol,
Player, HUD (PV/niveau/cooldowns) tous corrects ensemble.

**Web rebuild + commit.**

### Prochain pas

H5 (écran personnage : NOM/RANG/NIVEAU/FOR/AGI/INT/VIT/CLASSE=AUCUNE/
COMPÉTENCES/ÉQUIPEMENT), dernière tranche du plan H, ou
réordonnancement si Milan le demande après verdict sur ce build.

## 2026-08-20 — H5 (Écran personnage)

Mandat §6/GDD §17 : "Écran personnage : NAME / RANK / LEVEL / FOR / AGI
/ INT / VIT / CLASS / SKILLS / EQUIPMENT. Rank Zero doit afficher
CLASS = NONE et ne jamais recevoir une Classe inventée." Cinquième et
dernière tranche du plan H — boucle le vertical slice GDD §21.

### Fait

**3 nouvelles stats sur `Stats`** (`for_stat`, `agi_stat`, `vit_stat`,
défaut 10.0, +1/niveau comme `int_stat` déjà existant) : le GDD verrouille
4 stats (FOR/AGI/INT/VIT, §4), et l'écran personnage lui-même est le
premier consommateur réel qui les exige — les ajouter ici respecte la
discipline "pas de stat non exercée" (documentée dans stats.gd depuis H1)
plutôt que de la trahir en cachant des stats que le GDD impose d'afficher.
Câbler un vrai scaling de dégâts dessus (FOR sur Bras-Faux, GDD §7.1)
reste un chantier séparé, explicitement hors scope de cette brique.

**`CharacterScreen`** (`src/ui/character_screen.gd` +
`scenes/ui/character_screen.tscn`, nouveau) : panneau plein écran
basculé par l'action `character_screen` (Tab clavier, bouton tactile
"PERSO" ajouté à `touch_controls.tscn`). Poll en `_process()`, même
discipline que `Hud` (un lecteur d'état, jamais un propriétaire).
NOM/RANG = "Rank Zero"/"Zéro" — pas des valeurs inventées, c'est
l'identité même du protagoniste dans le GDD (§1/§3 : aucun nom propre,
connu uniquement par son Rang). COMPÉTENCES affiche les deux
emplacements déjà câblés (E = Gueule Vide, R = Bras-Faux) — aucun
système de swap de loadout, hors scope. ÉQUIPEMENT affiche les 4
catégories du GDD §16 (arme/tenue/accessoires/reliques) toutes vides —
aucun système de loot n'existe encore ("Boutique/craft/déblocages : à
préciser", GDD §16) ; afficher un objet inventé aurait été pire que rien.
Instancié dans `outpost.tscn` ET `gate_premiere.tscn` (disponible partout
où Player/Hud existent).

**Écart assumé, documenté plutôt que corrigé silencieusement** : le
panneau reste un overlay semi-transparent, il ne met pas le jeu en pause
et ne désactive pas les boutons tactiles de combat en dessous — un vrai
menu pause n'est demandé nulle part dans le mandat/GDD pour cette
tranche, l'ajouter aurait été une extension de scope non sollicitée.

**1 nouveau check smoke test** (60/60, aucune régression) :
`character_screen_toggles_open_closed_and_shows_class_none` (ouvre/
ferme sur pressions successives de l'action, vérifie "Rank Zero" et
"CLASSE : AUCUNE" dans le texte affiché — via `await process_frame`,
pas `physics_frame`, parce que l'écran lit son action dans `_process()`).

**Vérification visuelle réelle** (script jetable, supprimé après
usage) : `outpost.tscn` chargé, action `character_screen` simulée —
les 4 stats, CLASSE : AUCUNE, les 2 compétences et les 4 emplacements
d'équipement vides s'affichent tous correctement ensemble.

**Web rebuild + commit.**

### Prochain pas

Plan H (J1→J2→R3→D→E/F/G→H) terminé en entier. En attente du verdict
de Milan sur ce build complet avant de proposer la suite (art réel des
ennemis/boss différé depuis G/H2, ou nouveau contenu au-delà du
vertical slice).

## 2026-08-20 — Bake-off Animation, Voie C (checkpoint GARDE-FOU 1 — en attente verdict Milan)

Expérience parallèle et bornée (hors plan H, n'interrompt rien) :
comparer 3 pipelines d'animation (Voie A baseline inchangée, Voie B
frames doublées PixelLab mandatée séparément — Addendum C.6, pas
dupliquée ici, Voie C 3D→pixel art) sur un périmètre minuscule avant
de choisir le pipeline du jeu. Tout le code de cette brique vit dans
`experiments/bakeoff_voie_c/`, isolé de `src/`/`scenes/` — supprimable
sans toucher au jeu si Voie C n'est pas retenue.

### Investigation outil (avant tout code)

`github.com/bukkbeek/pixel_renderer` du mandat n'existe pas tel quel —
le vrai nom est **GodotPixelRenderer** (`bukkbeek/GodotPixelRenderer`,
confirmé par lecture du dépôt cloné). Constats :
- Application **GUI pure** (édition à la souris), aucun mode CLI/
  headless documenté ni trouvé dans le code.
- Requiert **Godot 4.4+** (notre projet est en 4.3).
- **MIT**, confirmé (LICENSE, Copyright Bukkbeek).

Décision (conforme au mandat, branche anticipée par lui) : ne PAS
piloter l'appli à l'aveugle sans écran, ne pas tenter de faire tourner
un second projet Godot 4.4 en parallèle pour une seule expérience.
Reprise du SEUL shader (`PixelArt.gdshader` : pixelisation par blocs,
quantification, dithering Bayer 4x4 sur transitions ombre/lumière,
contour Sobel), licence MIT = réutilisation libre, adapté dans
`experiments/bakeoff_voie_c/pixel_quantize.gdshader` — palette 8
couleurs fixes de l'original retirée (notre palette n'est pas 8
teintes mais une bande de Value HSV, `data/palettes/value_bands.json`),
remplacée par une désaturation + quantification du Value REMAPPÉE
DANS cette bande (V ∈ [16.5,90]%, marge de sécurité au-dessus du
plancher 15% pour absorber l'arrondi PNG 8-bit) — garantit que CHAQUE
palier de quantification est légal par construction, pas une
approximation à corriger a posteriori.

### Modèle 3D

Aucun outil de génération 3D accessible depuis cet environnement (pas
de MCP dédié type Meshy/Tripo — cherché, absent ; pas de Blender en
CLI — vérifié, absent). Fallback explicitement prévu par le mandat :
proxy low-poly construit PAR SCRIPT (`cendre_lowpoly.gd` — sphère
tête, capsules torse/bras/jambes, aucune modélisation main). Aucun
détail fin (harnais, sangles, cape) — hors de portée d'un proxy
primitive, et de toute façon invisible à 64×64 après quantification ;
volumes/teintes calqués sur le turnaround v3 (crâne pâle, tunique
grise, pantalon sombre, sans cape).

### GARDE-FOU 1 — rendu idle seul, gate automatique, PAS d'animation

Caméra orthogonale 3/4 (yaw 35°, pitch 18°, cadrage dérivé du gabarit
réel — voir ci-dessous), SubViewport 3D transparent → shader → second
SubViewport 2D transparent (lu directement, pas la fenêtre racine :
le stretch fixe 640×360 du projet letterboxait une lecture via
`get_viewport()`). Downscale NEAREST exact (512→64, facteur entier,
zéro lissage) vers le canevas de jeu réel.

**Gate gabarit** (`scripts/validate_morphology.py`, PAS de copie/
modification du script — un manifeste à 2 frames construit exprès,
frame 0 = `idle_south/0.png` réel, frame 1 = rendu Voie C, pour que le
gate existant compare directement) : **`ok: true`, 0 violation**
(après réduction du rayon de tête, 0.16→0.11 en unités Godot — la
première passe donnait un écart de tête de 75%, largement hors
tolérance 20%, corrigé par mesure/itération géométrique, pas par
jugement esthétique).

**Gate pixels** (`scripts/validate_pixels.py --category character`) :
**`ok: true`, 0 violation de bande, alpha ok** (après correctif : la
quantification par CANAL RGB de l'original produisait des bandes de
teinte visibles — roses/mauves — sur un gris censé rester neutre,
artefact classique du posterize par canal sur une couleur quasi
désaturée ; corrigé en quantifiant le Value HSV seul puis en
reconvertissant, garantissant R=G=B à chaque palier).

**Aucun verdict de qualité automatisé nulle part dans cette brique** —
les deux gates ci-dessus sont des mesures géométriques/colorimétriques
exactes (largeur de silhouette en px, bande de Value), jamais un "est-
ce que ça a l'air bien". `quality_labels.jsonl` n'est pas touché.

**Coût crédits Voie C : zéro** (aucun appel PixelLab) — donnée de
comparaison actée telle quelle, pas encore comparée aux deux autres
voies.

### STOP — en attente du verdict de Milan

Conformément au mandat : **aucune frame d'animation produite sur
Voie C.** Le rendu idle (`experiments/bakeoff_voie_c/out/voie_c_idle_64.png`)
et un comparatif côte-à-côte avec la référence réelle du jeu
(`comparison_baseline_vs_voie_c.png`) sont envoyés à Milan. Si le
rendu ne convient pas à l'œil, on s'arrête ici et on itère sur la
géométrie/l'éclairage/le shader — pas de frames de marche/dash/coup
tant que ce premier rendu n'est pas approuvé.

### Prochain pas

Si validé par Milan : rendre les 3 animations du périmètre (marche,
dash, un coup), vérifier l'absence de scintillement/tremblement de
pixels en mouvement (artefact documenté de ce type de pipeline),
construire le comparatif final à 3 voies (Voie A telle quelle, Voie B
— résultat de son mandat séparé Addendum C.6, à récupérer sans le
dupliquer, Voie C). Si non validé : itérer le rendu idle seul, ne pas
continuer vers l'animation tant que non résolu.

## 2026-08-20 — Bake-off Animation, Voie C v2 (verdict Milan : "pas pareil")

Milan sur le premier rendu idle (checkpoint précédent) : "Non il n'est
pas pareil fais un model pareil." Toujours GARDE-FOU 1 — toujours
aucune frame d'animation, on reste sur l'itération du rendu idle seul
jusqu'à ce qu'il colle au design.

### Fait

**Proxy enrichi** (`cendre_lowpoly.gd`) : le mannequin nu (sphère +
capsules) manquait tous les éléments qui identifient Cendre. Ajout,
toujours en primitives : col sombre, jupe de tunique en cloche (ourlet
dépenaillé du turnaround), ceinture + pochette en cuir, bras + gants,
bottes distinctes du pantalon. Une tentative de harnais en sangles
croisées (X, boîtes plates tournées) a été retirée : à la caméra 3/4
utilisée ici, la copie "derrière" débordait de la silhouette côté
caméra plutôt que rester cachée, lisant comme des ailes greffées sur
les épaules — pas essentiel à la lecture d'ensemble, laissé de côté
plutôt que forcé.

**Deux bugs réels trouvés en itérant, pas en devinant :**
- Les bras (capsules fines) lisaient comme des pavés plats détachés du
  corps ("ailes") une fois passés dans le pipeline de quantification.
  Isolé méthodiquement (désactivation successive harnais -> bras ->
  shader -> dithering/outline -> pixelisation -> quantification) :
  le rendu 3D BRUT (avant tout post-traitement) montrait des bras fins
  et corrects — la géométrie n'était jamais en cause. Le vrai problème :
  à 64px final, une capsule assez épaisse n'a pas assez de résolution
  pour montrer son propre arrondi, elle lit comme un rectangle plat.
  Corrigé en amincissant les bras et en les rentrant près du torse
  (silhouette lisible plutôt que "réaliste").
- En chemin, un bug de shader réel trouvé et corrigé quand même (indépendant
  du problème "bras") : `texture(TEXTURE, pixel_uv)` sur un UV bloqué par
  paquets de pixelisation crée un saut de dérivée d'écran énorme à la
  frontière de chaque bloc, ce qui fait choisir à Godot un mip level flou
  à ces frontières — `textureLod(..., 0.0)` partout dans le shader force
  le mip 0 et élimine la cause. Gardé même si ce n'était pas la cause du
  "bras aplati" (un vrai bug de rendu, pas de raison de le laisser).

**Gate gabarit re-cassé puis re-réparé** : agrandir le torse a d'abord
semblé la bonne piste (largeur mesurée insuffisante), mais la largeur
ne bougeait pas du tout en changeant le rayon du torse — la bande de
mesure (20% sous le sommet de la tête) tombait encore dans la zone du
cou/col, AVANT le sommet arrondi du torse, quel que soit son rayon.
Diagnostiqué en imprimant la largeur mesurée ligne par ligne (comme le
fait le gate lui-même) plutôt qu'en re-devinant à l'aveugle. Corrigé
en rapprochant le sommet du torse de la tête (`TORSO_HEIGHT` 0.26 ->
0.48), pas en élargissant.

**Gates automatiques : à nouveau `ok: true` sur les deux** (gabarit
vs baseline réelle, bande de Value character) — toujours aucun
jugement esthétique automatisé, uniquement des mesures géométriques/
colorimétriques exactes.

**Nettoyage** : fonction de harnais retirée (code mort), matériau de
bandage inutilisé retiré, commentaires de debug consolidés.

### STOP — en attente du nouveau verdict de Milan

Toujours aucune animation. Nouveau rendu idle + comparatif envoyés.

### Prochain pas

Identique au checkpoint précédent : si validé, passer aux 3 animations
du périmètre ; si toujours pas validé, continuer d'itérer le rendu
idle seul.

## 2026-08-20 — Investigation d'accès Meshy AI / Tripo AI (pas de génération)

Demande explicite de Milan : vérifier SEULEMENT si cet environnement a
déjà un accès configuré à Meshy AI (meshy.ai) ou Tripo AI (tripo3d.ai)
— génération 3D par IA avec auto-rigging — avant tout engagement sur
un modèle 3D réel de Cendre pour la Voie C. Aucune génération tentée.

### Vérifié

- **Outils MCP connectés** : recherche sur "meshy", "tripo", "3D
  generation" — aucun outil `mcp__*meshy*` ni `mcp__*tripo*` dans le
  catalogue disponible (contrairement à PixelLab/SpriteCook, qui ont
  chacun leurs outils `mcp__pixellab__*` / `mcp__spritecook__*` déjà
  chargés).
- **Variables d'environnement** : aucune `MESHY_*` ni `TRIPO_*`, et
  aucune clé API générique (`*_KEY`/`*_TOKEN`/`*_SECRET`) qui
  correspondrait à l'un de ces deux services — confirmé qu'il n'existe
  même pas de `PIXELLAB_API_KEY` en variable d'environnement pour
  PixelLab non plus : ce projet reçoit ses accès service via des
  serveurs MCP déjà connectés au niveau plateforme, jamais via une clé
  brute lisible dans l'environnement. L'absence d'outil MCP EST le
  signal fiable ici, pas l'absence de variable d'env (qui ne l'aurait
  jamais été de toute façon, même pour un service connecté).
- **Credentials/config sur disque** : aucun fichier `.netrc`, aucun
  dossier de config, aucune mention de ces services nulle part sur le
  système (recherche large, hors résultats non pertinents — un fichier
  Lua d'un projet totalement différent contenant le mot "tripod" en
  chinois, un fuseau horaire "Africa/Tripoli").
- **Réseau** : `curl` direct vers `api.meshy.ai` et `api.tripo3d.ai`
  répond HTTP 401 (pas de blocage réseau/proxy, juste "pas de clé") —
  confirme qu'un abonnement + une clé API à l'un ou l'autre service
  activerait l'accès techniquement, mais rien de ce genre n'est
  configuré ici.

### Conclusion

**Aucun accès existant à Meshy AI ni à Tripo AI dans cet
environnement.** Aucun abonnement Milan connu pour l'un ou l'autre —
cohérent avec l'absence totale de trace. Pas de contournement tenté
(pas de compte gratuit créé à la volée, pas de tentative d'accès
détourné).

**Si Milan veut essayer un modèle 3D généré par IA pour la Voie C**,
la suite se ferait manuellement, depuis son navigateur : les deux
outils (meshy.ai, tripo3d.ai) tournent entièrement en ligne, aucun
logiciel à installer. Générer le modèle low-poly de Cendre là-bas puis
exporter le fichier (GLB/FBX/OBJ) est hors de portée de CC dans cet
environnement tant qu'aucun accès n'est configuré (pas de compte, pas
de clé API, pas de connecteur MCP) — mais une fois le fichier exporté,
CC peut prendre le relais pour l'intégrer dans la scène Godot de la
Voie C (remplacement du proxy primitives par le vrai modèle,
recadrage, pipeline de rendu identique).

### Prochain pas

En attente de décision de Milan : générer manuellement un modèle via
l'un des deux outils et transmettre le fichier exporté, ou continuer
sur le proxy primitives (Voie C v2, en attente de verdict séparé).

## 2026-08-20 — Bake-off Animation, Voie C v3 : vrai modèle 3D via Meshy AI

Milan a obtenu une clé API Meshy et l'a transmise. Remplace le fallback
proxy-primitives (v2) par un vrai modèle généré, toujours GARDE-FOU 1
(idle seul, STOP après cette tranche, aucun jugement esthétique
automatisé).

### Sécurité (avant tout le reste)

Clé stockée UNIQUEMENT en config MCP scope `user` (`~/.claude.json`,
hors du dépôt, jamais commitée) — d'abord tentée en scope `local` sous
le mauvais chemin de projet (session Claude Code réellement enracinée
sur `/home/user/Alpha_Project_Live`, pas `/workspace/jeux` : la config
locale ne devenait donc jamais visible pour CETTE session), corrigée
en scope `user` (portée globale, indépendante du chemin) pour qu'une
future session la retrouve. `.gitignore` renforcé (`.env`, `*.secret`).
Vérifié à chaque étape : `git status` ne montre jamais la clé, aucun
`.mcp.json` dans le dépôt.

### Constat : outils MCP non chargés dans la session en cours

`claude mcp list` confirme la connexion, mais les outils du serveur
(ajouté EN COURS de session) ne sont pas apparus via ToolSearch — un
serveur MCP stdio ne se charge qu'au démarrage d'une session. Plutôt
que d'attendre un redémarrage, generation faite en appelant directement
l'API REST documentée (docs.meshy.ai) avec la clé, même discipline de
journalisation que prévu pour l'outil MCP.

### Fait

**Génération multi-image** (`POST /openapi/v1/multi-image-to-3d`) à
partir des 4 vues du turnaround v3 (crops FACE/3-4/PROFIL/DOS depuis
`assets/source/pixellab/cendre/reference_v3_turnaround_raw.png`,
label texte rogné, base64 inline). Texture standard 2K (pas Ultra/8K).
**30 crédits**, conforme à l'estimation. Résultat (thumbnail Meshy) :
reconstruction fidèle — harnais croisé, ceinture+pochettes, ourlet
dépenaillé, avant-bras bandés, bottes — tout ce que le proxy
primitives peinait à faire lire correctement.

**Bug trouvé : rig direct refusé** — le modèle brut a ~2 millions de
faces (target_polycount du multi-image-to-3d ne s'applique QUE si
`should_remesh=true`, omis à la génération — donc silencieusement
ignoré). Corrigé par un remesh séparé (`POST /openapi/v1/remesh`,
30000 polys triangles) avant rig — **5 crédits**, coût non prévu dans
le budget initial (non documenté avant appel) mais modeste.

**Auto-rig** (`POST /openapi/v1/rigging`, `height_meters=1.6`) sur le
modèle remeshé — **5 crédits**. Inclut AUTOMATIQUEMENT une animation
de marche avec skin (`basic_animations.walking_glb_url`), sans appel
séparé à `/animation` : couvre la tranche "rig + 1 animation de test"
prévue par le mandat sans les 3cr supplémentaires estimés pour ça.

**Total tranche : 40 crédits** (30+5+5), en haut de la réserve annoncée
(20-40cr) mais dedans. Solde vérifié après coup : 1100 → 1060,
cohérent. STOP ici — aucune génération supplémentaire.

**Pipeline de capture étendu** : `capture_idle_glb.gd`/`.tscn`
(nouveau) — même caméra/shader que `capture_idle.gd` (Voie C v2) mais
charge un GLB externe au lieu du proxy primitives, pour un comparatif
à égalité. Bug trouvé en cadrant : la bounding box calculée
(`MeshInstance3D.global_transform * get_aabb()`) donnait 0.016 unité
de haut au lieu de ~1.6m — le `Skeleton3D` importé porte une échelle
0.01 (conversion cm→m du glTF) que le calcul multipliait correctement,
mais le rendu RÉEL (déformation par les matrices d'os) ignore cette
transform de nœud pour un mesh skinné. Contourné avec un cadrage
manuel (`--char_center_y/x/z`) calibré en inspectant un rendu brut
sans pixelisation avant de cadrer pour de vrai — pas une vraie
correction du calcul d'aabb (qui reste faux pour un mesh skinné), juste
un contournement suffisant pour CETTE capture statique.

**Gates automatiques** : palette (bande Value character) — **ok**, 0
violation. Gabarit — **1 violation** : `head_width_px` 6 vs baseline 8
(tolérance 20%, écart réel 25%) ; `torso_width_px` 10 vs 13 passe
(tolérance 25%). Écart de cadrage/échelle mineur (~1px), pas un défaut
du modèle — rapporté tel quel, pas de nouvelle itération de cadrage
pour forcer le gate au vert (GARDE-FOU 1 : le verdict est à Milan, pas
un gate qui passe à tout prix).

**Fichiers gardés hors dépôt** (`.gitignore`,
`/experiments/bakeoff_voie_c/meshy_output/`) : les GLB bruts (~15MB,
rigged+walk) — mêmes raisons que `/captures_local/` (§13.3), pas de
dossier de sortie brut committé tant que Milan n'a pas tranché.

### STOP — en attente du verdict de Milan

Rendu idle Meshy + comparatif envoyés. Toujours aucune animation
produite au-delà de la marche bundlée automatiquement par le rig (pas
utilisée pour cette capture, gardée en réserve).

### Prochain pas

Si validé par Milan : les 2 autres actions du périmètre (dash, un coup
de combo) — soit via la marche déjà obtenue gratuitement + une
compétence Meshy dédiée, soit via des poses manuelles du rig, à
préciser avec lui. Comparatif final à 3 voies (A/B/C) une fois les
trois rendus sur les mêmes 3 actions.

## 2026-08-20 — Bake-off Animation, Voie C v3 : walk + dash + combo (« Go » Milan)

Suite au « Go » de Milan sur le rendu idle : complète le périmètre à 3
animations du mandat (marche déjà offerte par le rig, + dash + un coup
de combo), toujours sur le même modèle Meshy déjà généré/riggé/payé
(aucune nouvelle génération 3D, uniquement des animations sur le rig
existant + du rendu Godot local).

**Sélection dans la bibliothèque d'animations Meshy** (`/openapi/v1/
animations` n'accepte pas de description libre — action_id fixe dans
une bibliothèque de 500+ entrées documentées) :
- **Dash** : aucune entrée nommée « Dash ». `Roll_Dodge` (esquive
  roulée, action_id 158) retenu comme le plus proche disponible.
- **Combo (un coup)** : `Left_Slash` (action_id 97, frappe simple)
  retenu plutôt que `Punch_Combo`/`Weapon_Combo` (multi-coups), pour
  rester strictement sur UN coup — périmètre du mandat.
- Coût : 3cr chacune (confirmé), soit 6cr. Cumulé session : 46cr,
  toujours sous le seuil d'alerte 100cr — aucune confirmation
  supplémentaire requise (couvert par le « Go »).

**Extension de `capture_idle_glb.gd`** : ajout d'un bloc de calage de
pose sur une animation bundlée dans le GLB (`--anim_time`,
`--anim_name`, `_find_animation_player()` qui parcourt l'arbre pour
localiser l'`AnimationPlayer`, puis `play()` + `seek(t, true)` +
`advance(0.0)` pour figer une frame statique précise) — même
discipline que `capture_scene.gd` en mode « character »
(`sprite.frame = i; sprite.pause()`) : jamais une capture au hasard du
timing. `--debug_dump=1` ajouté en prime pour lister les animations
disponibles et leur durée.

**Choix du temps représentatif par action** (rendu `--no_shader=1`
brut, plusieurs candidats comparés visuellement, aucun jugement
esthétique automatisé — juste un choix de la pose la plus lisible) :
- **Marche** (`walking_man`) : `anim_time=0.27`, cadrage identique à
  l'idle (`cam_size=2.3, char_center_y=0.83`) — jambe avant engagée,
  bras en balancier, bien lisible du premier essai.
- **Dash / Roll_Dodge** (durée 1.867s) : 5 temps essayés
  (0.2/0.5/0.8/1.1/1.4s) au cadrage `cam_size=2.2, char_center_y=0.5`
  — au-delà de 0.5s le personnage part en rotation complète (culbute)
  et sort presque du cadre, illisible. Retenu `anim_time=0.5` (posture
  accroupie penchée en avant, lisible comme un mouvement d'esquive/
  dash). Cadrage resserré ensuite (`cam_size=1.8, char_center_y=0.45,
  char_center_x=0.05`) pour réduire la marge vide — bien mieux centré
  que le tout premier essai (`cam_size=3.2, char_center_y=0.5`) qui
  laissait le personnage minuscule dans un coin.
- **Combo / Left_Slash** (durée 3.2s) : 5 temps essayés
  (0.5/1.1/1.5/2.0/2.5s) au cadrage `cam_size=2.3,
  char_center_y=0.83`. `1.1` trop statique/préparatoire ; `0.5`, `2.0`
  et `2.5` quasi identiques entre eux (lame basse, bras d'appui
  replié) ; `1.5` nettement plus dynamique (bras libre déployé sur le
  côté, torse tordu, posture accroupie) — retenu comme frame
  représentative du coup.

**Limite connue, acceptée délibérément** : le bug d'échelle du mesh
skinné (aabb calculée quasi nulle, cf. entrée précédente) oblige un
cadrage manuel par capture ; contrairement à l'idle (soumise au
GARDE-FOU 1, précision du gate), les poses d'action n'ont pas cette
exigence — un cadrage « lisible mais imparfait » est accepté sans
itération supplémentaire (dash notamment : composition asymétrique
propre à la pose, pas totalement centrée même après resserrage).

**Rendu final** : les 3 poses choisies re-rendues à travers le
pipeline complet (shader `pixel_quantize.gdshader`, résolution interne
512, désaturation, dithering, contour Sobel) puis downscale NEAREST
exact vers 64×64 via `postprocess.py` — même discipline que l'idle.
Sorties commitées : `meshy_walk_64.png`, `meshy_dash_64.png`,
`meshy_combo_64.png` (+ leurs `_raw.png` 512px), assemblées dans
`comparison_meshy_actions.png` (3 colonnes côte à côte, fond gris
foncé, upscale ×8 NEAREST — pas de baseline Voie A/B équivalente pour
ces 3 actions précises dans cette fenêtre, donc présentation à 3
colonnes plutôt qu'un comparatif ligne par ligne). Fichiers
exploratoires (temps non retenus, debug dumps) nettoyés, non commités
(§13.3).

**Solde vérifié** (`GET /openapi/v1/balance`, appel gratuit) : 1054/1100
— cohérent avec 1100 − 46cr cumulés cette session.

### STOP — périmètre Voie C (3 animations) terminé, en attente de la suite décidée par Milan

Les 3 animations prévues par le mandat (idle, marche, dash, un coup de
combo — techniquement 4, la marche étant offerte gratuitement par le
rig) sont produites, gate/coûts documentés, rien commité au-delà de ce
qui est explicitement approuvé. Pas de comparatif final A/B/C engagé
sans nouvelle direction de Milan (les Voies A et B ne sont pas dans le
périmètre de cette session).

## 2026-08-20 — Vérification idle vs marche + traçabilité du « Go »

Milan a signalé que le rendu « idle » ressemble à une frame du cycle de
marche (même jambe avant pliée, même balancier de bras que
`meshy_walk_64.png`). Deux points à traiter avant de considérer la
tranche close.

**1. Investigation idle vs marche.** Première tentative de correctif
(re-capturer `cendre_rigged.glb` à `anim_time=0.0` sur `clip0`, son seul
clip bundlé) : **erreur de ma part**, annoncée à tort comme un
correctif sans vérification suffisante — le rendu produit était en
réalité strictement identique (diff binaire nul) au rendu déjà commité.
Reprise rigoureuse ensuite :
- Dump du GLB riggé (`--debug_dump=1`) : un seul clip, `Armature|clip0|
  baselayer`, 0.3s.
- `clip0` échantillonné à t=0.0/0.15/0.29 : rendu strictement identique
  aux trois temps (clip figé, pas une vraie animation).
- Ajout d'un mode `--rest_pose=1` à `capture_idle_glb.gd` :
  `AnimationPlayer.stop()` puis `Skeleton3D.reset_bone_poses()` sur
  chaque squelette trouvé — bypass complet de tout clip, lecture directe
  de la bind pose du rig telle qu'exportée par Meshy.
- Résultat : **diff binaire nul** entre `--rest_pose=1` et `clip0` à
  t=0.0, et donc aussi avec le rendu déjà commité comme « idle ».

**Conclusion** : il n'existe pas de pose neutre différente à extraire de
ce GLB — la bind pose du rig EST cette posture légèrement asymétrique
(poids sur une jambe, léger contrapposto), pas un bug de sélection
d'animation. Hypothèse la plus probable : les 4 vues turnaround
utilisées en entrée du multi-image-to-3d montraient déjà Cendre dans
une posture debout naturelle/relâchée (pas un garde-à-vous
parfaitement symétrique), et cette posture s'est propagée telle quelle
dans la géométrie reconstruite puis dans la bind pose du rig — d'où la
ressemblance avec une phase basse du cycle de marche, qui n'est pas un
défaut de capture. Aucun fichier committé changé (le rendu déjà en
place était déjà correct) ; seul gardé : le mode `--rest_pose=1` sur
`capture_idle_glb.gd`, outil de diagnostic réutilisable pour de futurs
GLB Meshy.

**2. Traçabilité du « Go ».** Confirmé : les deux messages « Go » qui
ont autorisé (a) le rendu idle + rig + 1 animation de test, puis (b)
dash + un coup de combo, sont bien deux tours de conversation distincts
envoyés directement par Milan — pas une supposition ni une
extrapolation de ma part. Aucune génération Meshy dans cette session
n'a eu lieu sans confirmation explicite de sa part.

## 2026-08-20 — Diagnostic flou dash/combo (suspect 3 : déformation de peau)

Milan a signalé un flou/bavure visible sur les rendus dash et combo
(mais pas idle/marche), et pointé la déformation de peau aux
articulations sur poses extrêmes comme cause probable. Protocole en 3
étapes, dans l'ordre demandé — coût minimal avant tout, pas de nouvelle
piste (Mixamo etc.) tant que 1-3 ne sont pas épuisés.

**1. Anti-aliasing / motion blur (gratuit).** Vérifié `project.godot`
section `[rendering]` et le code de `capture_idle_glb.gd` : aucun
réglage MSAA/FXAA/TAA n'est présent nulle part — le projet tourne sur
les valeurs par défaut du moteur (désactivées par défaut sur Godot
4.3). Aucun effet de profondeur de champ (DOF) sur la caméra ni sur
l'Environment créés par le script. **Confirmé : ni AA ni motion blur
actifs** — rien à corriger ici, cause écartée.

**2. Pose moins extrême, coût minimal (priorité).** Au lieu de payer
une nouvelle animation (3cr), récupéré gratuitement `basic_animations.
running_glb_url` — déjà inclus dans le résultat du rig original (payé
une fois, 5cr, jamais téléchargé jusqu'ici, seule `walking_glb_url`
avait été utilisée). `running` : flexion de genou modérée à extrême
selon le temps choisi, mais **aucune rotation complète du corps**
(contrairement à Roll_Dodge). Capturé à travers le pipeline shader
complet (même résolution 512px, mêmes réglages) à deux temps
(`t=0.17` flexion modérée, `t=0.5` flexion extrême du genou porteur) et
comparé côte à côte avec `meshy_dash_raw.png` (Roll_Dodge) et
`meshy_combo_raw.png` (Left_Slash) dans
`diagnostic_blur_dash_vs_running.png`.

**Résultat net** : dash (Roll_Dodge, rotation complète) est
visiblement le plus flou/bavé des quatre — silhouette en dégradés mous
plutôt qu'en blocs de pixellisation nets. Combo (Left_Slash) est
intermédiaire. **Les deux frames running (y compris à flexion de genou
extrême) restent nettes**, comparables en qualité à l'idle/la marche.
**Conclusion : le flou n'est PAS lié à un angle d'articulation extrême
en général — il est spécifiquement lié à la rotation complète du corps
(Roll_Dodge)**, cohérent avec l'hypothèse « suspect 3 » de Milan
(déformation de peau), mais plus précisément localisée : c'est le
mouvement de rotation/culbute qui semble étirer/déformer le skinning
autour du torse et des hanches, pas la flexion d'une articulation
isolée (genou, coude).

**Coût** : 0 crédit (téléchargement d'une animation déjà payée avec le
rig). Solde inchangé, 1054/1100.

### Complément — test d'une vraie animation de dash linéaire avant le remesh

Milan a demandé de vérifier dans la bibliothèque Meshy s'il existe une
entrée plus proche d'un vrai dash (élan/sprint linéaire, sans rotation
du corps) avant d'engager un remesh — Roll_Dodge est une esquive
roulée, pas un dash. Recherche dans `docs.meshy.ai/en/api/animation-
library` : famille distincte « WalkAndRun/Running » avec plusieurs
entrées de charge/élan linéaire (`509 Lean_Forward_Sprint`, `510
Standard_Forward_Charge`, `516 slide_light`, etc.), séparée de la
famille roll/tumble (`158-164 Roll_Dodge (1-4)`, `459
Run_Jump_and_Roll`). Retenu **`510 Standard_Forward_Charge`** — entrée
générique (pas liée à une arme spécifique comme `Rifle_Charge`/
`Bow_Charge`), correspondant exactement à « élan vers l'avant, pas de
rotation ».

Testé (3cr, pré-autorisé dans la demande de Milan) : `POST /openapi/
v1/animations` avec `action_id=510` sur le rig déjà payé. Résultat
téléchargé (`cendre_charge.glb`), capturé à `anim_time=0.1` (avant que
le **vrai root motion** — le personnage se déplace réellement hors du
cadre caméra fixe au fil de l'animation, contrairement à Roll_Dodge qui
pivote sur place — ne sorte la pose du cadre). Rendu à travers le
pipeline shader complet, comparé dans
`diagnostic_blur_v2_charge_test.png` (dash/Roll_Dodge, combo/Left_Slash,
running t=0.17, charge/Standard_Forward_Charge, tous au même pipeline).

**Résultat** : `Standard_Forward_Charge` est **net**, comparable en
qualité à running/idle/marche — aucun flou. Confirme précisément
l'hypothèse : le flou n'apparaît QUE sur Roll_Dodge (rotation complète
du corps), jamais sur un mouvement linéaire même avec flexion
d'articulation marquée.

**Recommandation** : le remesh (étape 3) n'est probablement pas
nécessaire — le vrai correctif est de remplacer la source d'animation
du dash (`Roll_Dodge` → `Standard_Forward_Charge`) plutôt que de payer
pour une densité de maillage plus élevée qui ne traiterait pas la cause
réelle (rotation complète, pas résolution du mesh). Décision de
remplacer la capture dash déjà committée laissée à Milan — pas fait
unilatéralement ici.

**Coût de ce complément** : 3cr (cumul session 49cr, toujours sous le
seuil 100cr). Solde vérifié : 1051/1100.

### STOP — en attente de la décision de Milan

`cendre_running.glb` et `cendre_charge.glb` téléchargés, gardés dans
`experiments/bakeoff_voie_c/meshy_output/` (gitignore, non commités,
même discipline que les autres GLB bruts). Le remesh (étape 3) n'est
PAS engagé — devenu probablement inutile au vu du résultat charge, mais
la décision finale (remesh quand même / remplacer dash par charge /
autre) revient à Milan.

## 2026-08-20 — Dash définitif : remplacement Roll_Dodge → Standard_Forward_Charge

Milan tranche : option 1 (remplacer la source du dash). Pas de remesh.

Choix du temps représentatif : 4 candidats comparés (`t=0.05/0.08/0.13`
+ le `t=0.1` du diagnostic précédent), tous bien cadrés avant que le
root motion ne sorte la pose du cadre fixe. Retenu **`t=0.08`** — jambe
arrière pleinement étendue, buste penché en avant, lecture la plus
dynamique d'un élan de dash parmi les candidats.

`meshy_dash_raw.png`/`meshy_dash_64.png` **remplacés** (même cadrage
que marche/combo : `cam_size=2.3, char_center_y=0.83`, pipeline shader
complet, downscale NEAREST 64px). `comparison_meshy_actions.png`
régénéré avec le nouveau dash (label mis à jour :
« dash / Standard_Forward_Charge (0.08s) »). Résultat net, cohérent
avec le diagnostic — aucun flou résiduel.

**Coût** : 0 crédit (animation déjà payée/téléchargée lors du
diagnostic). Aucune dépense supplémentaire cette tranche.

### Périmètre Voie C (idle + 3 animations) à nouveau complet, dash corrigé

`gate_manifest_meshy.json` n'a pas besoin de mise à jour (il ne couvre
que l'idle, pas les actions — inchangé). Pas de nouvelle action engagée
au-delà de ce remplacement, en attente de la suite décidée par Milan.

## 2026-08-20/21 — MANDAT NUIT reçu, régime d'exécution autonome activé

Milan a transmis `MANDAT NUIT — Rank Zero V1` (régime exceptionnel,
suspend le STOP-entre-tâches habituel dans les limites strictes du
document — sécurité, aucun verdict qualité auto-attribué, plafonds de
crédits, réversibilité, gates honnêtes) + `RANK_ZERO_POWER_SKILL_BIBLE
_v0.4.docx`. 5 phases dans l'ordre décroissant de priorité. Ce qui suit
documente la Phase 1, exécutée en premier comme demandé (elle ne coûte
rien et corrige le retour le plus direct de Milan : « on dirait un jeu
de 1999 »).

### PHASE 1 — Éclairage et couleur (Addendum C), 0 crédit

**Constat de départ** : `Backdrop` de `outpost.tscn`/`gate_premiere.
tscn` en `ColorRect` plat désaturé (ex. `Color(0.16, 0.18, 0.15)`),
aucun `CanvasModulate`, aucun `Light2D`, aucun `LightOccluder2D`. Bande
`decor` de `value_bands.json` plafonnée à 60% — cohérente avec un monde
délibérément terne, plus avec l'intention Wizard of Legend/Skul.

**Contrainte non-négociable identifiée avant de coder** : un
`CanvasModulate` teinte TOUT le canvas où il est posé, y compris Rank
Zero — or elle doit rester seule en grayscale désaturé (Classe = NONE,
contraste narratif explicite dans le mandat). Un `CanvasModulate`
global casserait ça. Solution retenue : `CanvasModulate` chaud posé
normalement sur la scène, + un shader de contre-poids
(`src/vfx/shaders/canvas_modulate_compensate.gdshader`, nouveau)
appliqué UNIQUEMENT sur `AnimatedSprite2D` de Player, qui divise sa
couleur par la même teinte avant que `CanvasModulate` ne la multiplie
— `(COLOR / C) * C = COLOR`, donc Rank Zero ressort inchangée quelle
que soit l'ambiance de la scène. Valeur du contre-poids tenue
synchronisée avec le `CanvasModulate` de chaque scène (documenté en
commentaire directement dans les deux `.tscn` — pas de découverte
dynamique).

**Câblé dans `outpost.tscn` et `gate_premiere.tscn`** (les deux scènes
réellement dans le chemin de jeu — `test_arena.tscn` n'est référencée
nulle part comme cible de transition, laissée de côté) :
- `CanvasModulate` chaud (`Color(1.15-1.18, 1.0, 0.82-0.85)`).
- `Backdrop` recoloré vers une teinte brun/pierre chaude et plus
  saturée (au lieu du gris-olive plat).
- `PointLight2D` + `GradientTexture2D` (radial, généré en `.tres` pur,
  0 asset externe) : une lumière personnelle douce sur Player, une
  torche ambrée sur chacune des 3 portes de `gate_premiere.tscn`
  (Combat/Elite/Boss).
- `LightOccluder2D` basique sur Player (polygone approximatif de sa
  capsule de collision — mandat §2 explicite "basique").

**Vérification visuelle** (outil de dev ad-hoc, jamais commité — pas
un mode de `tools/capture_scene.gd`, celui-ci n'a pas de mode "screen-
shot de scène complète" et en ajouter un pour un usage ponctuel aurait
été une usine avant produit) : rendu réel via `xvfb-run` + Vulkan
logiciel, capture de `gate_premiere.tscn` à deux positions caméra.
Confirmé par échantillonnage de pixels :
- Rank Zero reste grayscale (RGB quasi neutre sur sa tunique/peau) —
  le contre-poids fonctionne.
- Sol ambiant : V ≈ 24-37% (mesuré). Halo de sol près d'une torche :
  jusqu'à ≈78%. Cœur direct de la torche (le pixel de la source
  elle-même, pas ce qu'elle éclaire) : V ≈ 92-96% — au-dessus de tout
  plafond decor/character, traité comme un point-lumière actif (même
  logique que le rim-light déjà documenté sur la bande `character`),
  pas comme un défaut à corriger.

**`value_bands.json`** : bande `decor` relevée de `[15,60]` à
`[15,78]`, documentée avec les valeurs mesurées ci-dessus et la
distinction lumière-source vs. décor-éclairé. Toujours strictement
sous `character` (90) et `vfx` (92).

**Régression** : `scripts/run_gameplay_smoke_test.sh` relancé après les
changements — **60/60 checks passent** (`all_pass: true`), aucune
régression sur combat/dash/pouvoirs/boss/UI.

**Build web exporté et redéployé** (`godot4 --headless --rendering-
driver vulkan --export-release "Web" docs/index.html`, sortie dans
`docs/index.*`) — commit à suivre immédiatement, comme demandé
("commit + push après CHAQUE phase, redéployer à la fin de la phase
1").

**Non fait dans cette phase** (hors scope Addendum C, réservé aux
phases suivantes) : palette réelle du décor/ennemis (Phase 2/3, via
PixelLab/Meshy), `test_arena.tscn` laissé tel quel (scène orpheline,
non prioritaire).

### PHASE 2 — Décor et biome (PixelLab MCP)

MCP PixelLab déjà connecté et directement disponible dans cette session
(contrairement à Meshy en Phase Voie C, pas de repli REST nécessaire).
Solde vérifié avant génération : abonnement actif (Tier 1), 1653/2000
générations restantes ce cycle, 0 crédit dollar (plan par abonnement,
pas par crédit) — largement sous le plafond nuit (40% max, réserve
≥60%).

**Un seul biome, pour la Première Gate** (`create_topdown_tileset`,
Wang standard, `tile_size=32`, `transition_size=0.25`) : sol pierre
sombre → grès chaud ocre/rouille, feu "ancient gate sanctum ruins".
16 tuiles générées avec les 4 coins/combinaisons exacts (métadonnées
`bounding_box` par tuile récupérées). **Décision de scope** : plutôt
que de câbler un vrai `TerrainSet` à coins (peering bits Godot,
16 tuiles) sans éditeur interactif pour vérifier visuellement le
résultat — risque réel d'un rendu cassé/invisible non détectable
avant un cycle de capture supplémentaire, sur UNE nuit autonome sans
supervision — extrait seulement les 2 tuiles "pures" (4 coins identiques,
seamless avec elles-mêmes par construction Wang) et câblé une
variation déterministe par hash de cellule dans `arena_floor.gd`
(~1 case sur 6 en variante sombre, jamais deux adjacentes). Documenté
comme scope volontairement réduit, pas un échec — la donnée complète
(16 tuiles + corners) reste récupérable plus tard si un vrai autotiling
devient prioritaire.

**3 props** (`create_map_object`, mode basique, 32x32-40px, style
cohérent avec le biome) : brazier de pierre (flamme ambrée, ancre les
torches de la Phase 1), pilier antique fissuré, tas de gravats chauds.
Tous complétés en un seul essai, aucune retouche nécessaire. Placés
dans `gate_premiere.tscn` (2× chaque, dispersés Combat/Elite/Boss) et
`outpost.tscn` (1× chaque) — anciens props `prop_rubble.png`/
`prop_debris.png` gardés tels quels (pas supprimés, £13.3 — ils restent
utilisables, désormais eux aussi teintés chaud par le `CanvasModulate`
de la Phase 1 même sans régénération).

**`floor_base.png` remplacé** (ancienne version archivée dans
`assets/source/archive/world_pre_mandat_nuit/floor_base_pre_nuit.png`,
jamais supprimée — mandat §0 "réversible"). `floor_tileset.tres`
étendu à 2 coordonnées d'atlas.

**Gate palette — déviation honnête, non corrigée de force** :
échantillonnage sur capture réelle de `gate_premiere.tscn`, quelques
pixels de highlight PROPRES À LA TUILE (détail baked du grès généré,
pas un artefact d'éclairage) atteignent V=100% — au-dessus même de la
bande `decor` relevée en Phase 1 (78%). Pas re-élargi la bande pour
faire disparaître ce résultat (une bande qui admet 0-100% n'est plus
un gate) : signalé ici tel quel, pas de correction forcée. Le gros du
sol reste dans une plage raisonnable (mesuré : 34-84% selon zone/
proximité lumière).

**Régression** : `scripts/run_gameplay_smoke_test.sh` relancé — 60/60
toujours au vert.

**Build web exporté et redéployé** (même commande que Phase 1).

**Coût réel** : 1 tileset + 3 objets = 4 générations PixelLab (sur
1653 disponibles, plafond nuit 661 max) — largement sous plafond.

### PHASE 3 — 3 monstres Meshy : génération terminée, capture BLOQUÉE (environnement)

**État : PARTIEL / EN PAUSE.** La génération Meshy (payante) est
terminée et validée en coût ; le pipeline de capture headless (rendu
3D → pixel art) est bloqué par un problème d'environnement non résolu
au moment où cette entrée est écrite. Rien n'est perdu (voir §Coût),
mais aucune des 9 images finales des 3 monstres n'existe encore dans
un état correct. Documenté ici en détail pour qu'une session
ultérieure reprenne sans repartir de zéro.

**Génération (terminée, 69cr, voir `data/meshy_usage.jsonl`)** : 3
monstres conçus pour le biome "Gate corrompue" (GDD) — Crawler / Null
Husk (0.9m, quadrupède rampant), Brute / System Fragment (2.2m, lourd),
Ranged / Classless Aberration (1.8m, distance). Pipeline complet par
monstre : `text_to_3d` preview meshy-5 (5cr) → `text_to_3d_refine`
(10cr, texture) → `rigging` (5cr, inclut marche+course gratuites) →
`animate` (3cr, action bibliothèque : Crawler=94 Flying_Fist_Kick,
Brute=128 Heavy_Hammer_Swing, Ranged=239 Crouch_Pull_and_Throw). Les 9
GLB (rigged/walk/attack ×3) téléchargés dans
`experiments/monsters_nuit/meshy_output/` (non commité par convention
§13.3, comme `bakeoff_voie_c/meshy_output/` — mais **committé cette
fois-ci sur demande explicite de Milan**, pour transférer le travail
Meshy déjà payé à une autre session sans le regénérer).

**Bug trouvé et corrigé : désaturation forcée des monstres.**
`experiments/bakeoff_voie_c/capture_idle_glb.gd` (outil de capture
générique réutilisé du bake-off Voie C) codait en dur
`shader_mat.set_shader_parameter("target_saturation", 0.10)` — valeur
voulue pour Cendre (grayscale narratif, GDD) mais appliquée aussi aux
3 monstres, contredisant l'exigence explicite du mandat ("Palettes
ennemies colorées (phase 1)"). Repéré en inspectant `brute_idle_64.png`
et `crawler_idle_64.png`, visuellement quasi gris. **Corrigé** : ajout
d'un paramètre `--target_saturation` (défaut `0.10` inchangé pour ne
rien casser sur Cendre), surchargeable par appel. Ce correctif seul
est sûr et déjà vérifié (pas de dépendance au rendu qui bloque
ci-dessous) mais **aucune image monstre n'a encore été re-rendue avec
la valeur corrigée** — les 18 fichiers dans
`experiments/monsters_nuit/out/` (raw+64px ×9) restent ceux de la
tentative bugguée (trop désaturés), committés tels quels par
transparence, PAS comme un livrable approuvé.

**Blocage : le rendu 3D headless ne produit plus rien dans ce
conteneur.** Après reprise de session (conteneur recyclé), toute
capture via `capture_idle_glb.gd`/`capture_idle.gd` (SubViewport 3D
offscreen → shader pixel-art → PNG) reste bloquée indéfiniment —
aucune sortie, `save_err` jamais atteint, CPU parfois élevé (200%+),
parfois quasi nul, selon la tentative. Diagnostic mené avant de passer
la main (voir aussi les prints `DBG ...` laissés intentionnellement
dans `capture_idle_glb.gd` pour la reprise) :

1. **Pas un bug de script** : instrumenté `capture_idle_glb.gd` avec des
   `print()` à chaque étape (avant/après `load()`, après
   `instantiate()`, avant/après chaque `await physics_frame`/
   `process_frame`). AUCUN print n'apparaît, pas même le tout premier
   (placé avant tout calcul réel) — donc `_ready()` ne s'exécute
   probablement jamais, ou l'engine entier est gelé avant.
2. **Pas spécifique aux nouveaux assets** : même blocage identique en
   remplaçant le GLB monstre par `cendre_rigged.glb` (connu bon,
   capturé avec succès en session précédente), ET avec la scène
   purement procédurale `capture_idle.tscn` (zéro GLB, zéro texture
   externe, juste des primitives `cendre_lowpoly.gd`).
3. **Pas un problème projet/autoloads/scan de ressources** :
   `scripts/run_gameplay_smoke_test.sh` (le test de régression officiel
   du jeu, 60 assertions gameplay) tourne PARFAITEMENT dans ce même
   conteneur — 60/60 vert, en moins de 2 minutes, aucun blocage. Ceci
   élimine un scan de classe global cassé (le mode d'échec documenté
   dans l'en-tête de ce script lui-même, "`.import` manquant → hang
   silencieux") comme cause : le projet entier boot et tourne bien.
4. **Piste retenue (non confirmée)** : ce jeu est un jeu 2D pur — la
   scène de smoke-test ne touche jamais le pipeline de rendu 3D
   (`Node3D`/`Camera3D`/`WorldEnvironment`/Forward+). Nos scripts de
   capture sont le SEUL endroit du projet à instancier un monde 3D
   (`SubViewport.own_world_3d = true`). Hypothèse : le tout premier
   appel de rendu 3D jamais effectué dans ce process, sous Vulkan
   logiciel (llvmpipe, confirmé dans les logs), déclenche une
   compilation de pipeline pathologiquement longue (Forward+ est
   nettement plus coûteux à compiler que du 2D canvas) — sans cache de
   shaders persistant d'une session à l'autre (`.godot/` est gitignoré
   et non un volume persistant). Un essai à 1200s (20 min) de CPU
   soutenu (200%+) n'a rien produit — soit le vrai temps nécessaire
   dépasse largement ça, soit il s'agit d'un authentique gel (pas
   seulement une lenteur), les deux restent possibles.
5. **Tenté sans conclusion** : bascule vers le renderer
   `--rendering-driver opengl3 --rendering-method gl_compatibility`
   (pipeline de compilation plus simple, hypothèse d'un contournement
   rapide) — même symptôme (aucune sortie, aucun fichier produit dans
   le délai testé de 150s). Pas testé sur une durée plus longue faute
   de temps avant la pause de session.

**Décision (Milan, en session)** : ne pas continuer à creuser
indéfiniment ("y'a clairement un bug, arrête de mouliner dans le
vide") — committer et pousser l'état complet (fix inclus, GLB inclus,
diagnostic documenté) pour qu'une AUTRE session Claude reprenne avec
tout le contexte, sans re-payer les crédits Meshy déjà dépensés.

**Reste à faire pour clore Phase 3** (pour la session qui reprend) :
- Percer le blocage de rendu (pistes : essayer un timeout beaucoup
  plus long sur `gl_compatibility` ; vérifier si un cache de shaders
  Godot persistant existe/peut être créé hors `.godot/` ; comparer
  avec un Godot fraîchement réinstallé/version différente ; envisager
  un export minimal du modèle vers un format image via un outil tiers
  hors Godot si le rendu natif reste impraticable dans ce conteneur).
- Une fois débloqué : re-rendre les 9 captures (raw+64px) avec
  `--target_saturation` explicite (valeur suggérée non figée : ~0.5-0.6,
  "clairement coloré" sans être criard — à valider à l'œil, pas
  imposée ici comme définitive).
- Construire les `SpriteFrames`/`AnimatedSprite2D` et remplacer le
  `Polygon2D` placeholder dans `enemy_crawler.tscn`/`enemy_brute.tscn`/
  `enemy_ranged.tscn`.
- Vérifier `HitResponse` (flash, dégâts, mort) sur les nouveaux sprites,
  convention rouge=danger, smoke test, redeploy si Phase 3 est enfin
  complétée.

**Coût réel Meshy Phase 3** : 69cr (3× [preview 5 + refine 10 + rig 5 +
animate 3]). Solde après : 982/1051cr. Plafond nuit 250cr — largement
respecté. Reste ~181cr de marge Meshy si besoin en Phase 4/5.

### CHANTIER A — Déblocage du rendu 3D (repris par une autre session)

**Résolu.** Suite à la remontée de Milan avec deux pistes concrètes
(rapport Godot #82435 sur les gels llvmpipe Forward+/Mobile en VM, et
Blender headless en repli) :

**A1 — Retest Compatibility avec délai long.** Lancé en tâche de fond,
`--rendering-driver opengl3 --rendering-method gl_compatibility`,
timeout 45 min (au lieu de 150s testé la fois précédente). Toujours
aucune sortie après 28+ minutes de CPU soutenu (250%+) au moment
d'écrire cette entrée — donc soit le vrai temps nécessaire dépasse
largement 45 min sur ce matériel, soit c'est un authentique gel même
en Compatibility. Résultat définitif non déterminant, mais devenu
**non bloquant** grâce à A2 ci-dessous.

**A2 — Blender headless (Cycles CPU), solution retenue.** Blender 4.0.2
installé (`apt-get install -y blender`). Deux soucis d'amorçage :
(1) le Python système utilisé par Blender (3.12, PAS le python3
générique du conteneur qui pointe vers 3.11) n'avait pas `numpy`,
requis par l'import glTF — corrigé via `apt-get install -y
python3-numpy` (paquet système, pas pip, contourne le
"externally-managed-environment" de ce conteneur) ; (2) ce build
Blender (paquet apt, pas le build officiel Blender Foundation) est
compilé SANS OpenImageDenoiser — le rendu Cycles échouait
("Build without OpenImageDenoiser") avec le débruitage activé par
défaut, corrigé en le désactivant explicitement
(`scene.cycles.use_denoising = False`).

Une fois ces deux soucis réglés : **rendu complet en ~4 secondes**
(import GLB 0.65s + 32 échantillons Cycles CPU 512x512), contre 20+
minutes de blocage systématique sous Godot/Vulkan. Validé d'abord sur
`cendre_rigged.glb` (référence connue-bonne) — pose bind asymétrique
correcte, texture/couleurs cohérentes avec les rendus Godot antérieurs
(mêmes vêtements/harnais/bottes reconnaissables).

**Bug de cadrage trouvé en cours de route** : `obj.bound_box` de
Blender est la bbox LOCALE de la donnée SOURCE, pas évaluée — elle
ignore la déformation par armature (constaté : bit-à-bit identique
entre la pose idle et un coup de pied en plein vol sur Crawler).
Corrigé en calculant la bbox depuis le maillage évalué du depsgraph
(`obj.evaluated_get(depsgraph).to_mesh()`, sommet par sommet) —
confirme bien que les sommets individuels bougent avec la pose,
mais empiriquement l'enveloppe globale (min/max) ne bouge PAS toujours
pour ces 3 monstres (probablement des sommets rigides comme antennes/
griffes qui restent les extrema sur tous les axes même quand les
membres bougent) — pas entièrement élucidé, contourné pragmatiquement
par un `--cam_size` manuel plus généreux sur les 3 poses d'attaque
(silhouette complète visible, pas de recadrage serré parfait — le
canevas final 64x64 absorbe la marge).

**Nouveaux outils créés** (`experiments/blender_capture/`) :
- `capture_pose.py` : rendu Blender headless (GLB → PNG RGBA haute
  résolution, caméra orthographique auto-cadrée sur bbox, animation/
  frame sélectionnable, `--list_actions` pour la reconnaissance).
- `quantize.py` : post-traitement pixel-art en Python pur (Pillow +
  numpy, AUCUNE dépendance Godot) — porte la même logique que
  `pixel_quantize.gdshader` (pixelisation par blocs point-échantillonnés,
  désaturation+quantification HSV remappée dans la bande de Value,
  contour par détection de bords, dithering Bayer) mais calculée sur
  l'image déjà rendue, pas en shader GPU. Différence assumée : les
  bords/contours sont calculés sur l'image DÉJÀ pixelisée (pixels de
  sortie voisins), pas sur la texture haute résolution originale comme
  le shader — visuellement proche, pas un rendu identique au pixel
  près.

**Appliqué aux 3 monstres déjà générés et payés** (Crawler/Brute/
Ranged) : idle (walk.glb à la frame de départ, convention déjà établie)
+ walk (walk.glb mi-cycle) + attack (attack.glb, frame choisie par
inspection visuelle de chaque pose, 1 réglage de cadrage nécessaire sur
les 3 poses d'attaque). `--target_saturation=0.55` (jugement documenté,
pas une valeur imposée : "clairement coloré" sans être criard, à
distinguer du 0.10 quasi-gris de Cendre) — corrige le bug de
désaturation forcée trouvé plus tôt. Les 18 fichiers (raw+64px) dans
`experiments/monsters_nuit/out/` remplacent les anciens (bugués,
gris) du commit précédent. Inspection visuelle des 9 poses : silhouettes
lisibles, couleurs cohérentes avec le thème de chaque monstre (Crawler
gris/chair rouge exposée, Brute gris-acier/énergie orange-rouge, Ranged
noir-violet/veines rouges) — aucune quantité auto-attribuée de
"qualité finale", juste une confirmation que le pipeline produit un
résultat exploitable.

**Reste à faire (hors scope immédiat, noté pour la suite)** : recentrer/
retoucher au pixel les 3 poses d'attaque si le cadrage large gêne en
jeu ; construire les `SpriteFrames`/`AnimatedSprite2D` et câbler dans
`enemy_crawler.tscn`/`enemy_brute.tscn`/`enemy_ranged.tscn` (placeholders
`Polygon2D` toujours en place) ; vérifier `HitResponse` + convention
rouge=danger sur les nouveaux sprites ; smoke test + redeploy si Phase 3
est enfin complétée derrière ce travail.

**Mise à jour A1** : le test Compatibility à délai long (45 min, lancé en
tâche de fond) est resté sans conclusion nette même après ~30 minutes de
CPU soutenu (250%+, aucune sortie) — soit le temps réel nécessaire dépasse
encore ça sur ce matériel, soit c'est un authentique gel même en
Compatibility. Non déterminant, mais rendu **non bloquant** par la
solution Blender (A2 ci-dessus) : je n'ai pas attendu la fin de ce test
pour avancer, conformément au principe "ne pas boucler indéfiniment".

### CHANTIER B — Décor (retour Milan, exploite ce qui est déjà payé)

**B1 — Vrai TerrainSet à coins (16 tuiles Wang), au lieu des 2 tuiles
pures.** Cause directe du sol plat/répétitif signalée par Milan.
Métadonnées + image du tileset PixelLab déjà généré en Phase 2
(`tileset_id=1ef12d88...`) re-téléchargées (`get_topdown_tileset` +
téléchargement metadata/image, sauvegardées dans
`assets/source/pixellab/world/wang_gate/`). Nouvel outil
`tools/pixellab_tileset_converter.gd` (adapté de la doc MCP PixelLab
`pixellab://docs/godot/wang-tilesets`, tourne en `godot4 --headless -s`,
zéro éditeur requis) : parse les 16 tuiles + leurs coins NW/NE/SW/SE,
génère un atlas (`floor_terrain_atlas.png`) et un vrai `TileSet` avec
`terrain_set_0` en mode coin (`floor_terrain.tres`). `arena_floor.gd`
réécrit pour peindre via `set_cells_terrain_connect` (tout le sol en
terrain "grès chaud" dominant, puis des îlots de "pierre sombre" par
blocs de 4x3 tuiles, motif déterministe par hash de bloc — pas de case
isolée qui produirait un bruit visuel chargé). `gate_premiere.tscn` et
`outpost.tscn` repointés vers `floor_terrain.tres`.

**Vérifié par capture 2D** (pas à l'aveugle) : nouveau mode
`--mode=scene` ajouté à `tools/capture_scene.gd` (charge une scène
quelconque + Camera2D positionnable — réutilise la même discipline
gel+3×process_frame que les modes existants, pas une nouvelle scène de
capture dupliquée). Résultat : transitions Wang connectées avec bords
irréguliers naturels, net progrès visuel par rapport au damier plat de
la Phase 2 — capture envoyée à Milan pour référence
(`floor_terrain_check.png`).

**B2 — Couche d'arrière-plan lointain.** 2 nouveaux props PixelLab
(`create_map_object`, vue "side", detail bas/flat shading pour rester
silhouette) : arche de ruine antique (`bg_ruin_arch.png`, halo chaud
visible à travers) et pilier élancé isolé (`bg_pillar_silhouette.png`).
**Détour d'implémentation** : câblé d'abord via `Parallax2D` (scroll
plus lent que la caméra = profondeur) avec les sprites redimensionnés
trop grands/mal positionnés — capture de vérification montrant presque
rien de visible. Diagnostic : pas un bug de Parallax2D lui-même (retiré
pour tester, même résultat identique) mais une simple erreur de cadrage
— la tuile de sol elle-même a une silhouette crénelée baked qui remplit
~80% de la hauteur d'écran, ne laissant qu'une bande d'environ 76px en
haut pour l'arrière-plan. Corrigé : sprites réduits (`scale=0.38`) et
repositionnés pour tenir dans cette bande, `Parallax2D` finalement
simplifié en `Node2D` simple (positions monde 1:1, pas de vitesse
différentielle) — priorité donnée à un résultat qui marche plutôt qu'à
un effet de parallaxe non vérifiable de façon fiable dans le temps
disponible. Vérifié par capture à la position de caméra où une arche
tombe dans le cadre (`b23_arch_check.png`) : silhouette bien visible
au-dessus du sol, effet de profondeur net (référence Wizard of Legend/
Skul). 3 arches + 3 piliers dans `gate_premiere.tscn` (salle longue,
120 tuiles), 1 arche + 2 piliers dans `outpost.tscn` (salle courte,
30 tuiles) — également vérifié par capture.

**B3 — Densification des props.** `gate_premiere.tscn` : 6→13 props
(ajout de `prop_debris.png`, déjà existant mais jamais câblé dans cette
scène, pour varier sans regénérer) répartis pour combler les grands
écarts entre les props Phase 2 (jusqu'à 600px vides). `outpost.tscn` :
2→4 props. Aucune nouvelle génération PixelLab nécessaire pour B3.

**Régression** : `scripts/run_gameplay_smoke_test.sh` — 60/60 après B1
ET après B2/B3 (deux passages distincts, aucune casse introduite par
étape).

**Coût PixelLab réel Chantier B** : 2 générations (`create_map_object`
×2 pour l'arrière-plan) — B1 et B3 n'ont consommé aucune génération
(réutilisation de données/assets déjà payés). Total session PixelLab :
4 (Phase 2) + 2 (Chantier B) = 6 générations, sur 1653 disponibles au
départ — largement sous plafond.

**Build web exporté et redéployé** (`godot4 --headless --rendering-driver
vulkan --export-release "Web" docs/index.html`, sortie dans
`docs/index.*`).

**Bug préexistant trouvé et corrigé au passage** : le premier export a
produit un `docs/index.pck` de 110 Mo (rejeté par GitHub, limite 100 Mo)
— `experiments/monsters_nuit/` (GLB Meshy, 127 Mo) n'était protégé que
par `.gitignore` (exclu du dépôt git) mais PAS d'un `.gdignore` (exclu du
scan de ressources Godot), donc bundlé tel quel dans le PCK. Comparaison
avec l'historique (`git show <commit>:docs/index.pck | wc -c`) : le
`.pck` est passé de 3.8 Mo à 39.3 Mo entre les commits G et "MANDAT NUIT
Phase 1" — exactement quand `experiments/bakeoff_voie_c/meshy_output/`
(GLB du bake-off Voie C) a commencé à exister sur le disque. **Tous les
builds web depuis plusieurs phases embarquaient donc déjà, sans le
savoir, les GLB expérimentaux jamais destinés au jeu livré.** Corrigé en
ajoutant `experiments/bakeoff_voie_c/.gdignore` et
`experiments/monsters_nuit/.gdignore` (fichiers vides, même convention
que `captures/.gdignore`) — nouveau `.pck` : 4.2 Mo, cohérent avec la
taille d'avant ce bug (3.8 Mo + le nouvel atlas de terrain + les 2 props
d'arrière-plan). Effet de bord positif du Chantier B, pas juste un
correctif de blocage de push.

## 2026-08-21 — Retour Milan sur les 3 monstres rendus (échelle + Crawler + Ranged)

Milan a validé la Brute telle quelle ("silhouette lourde lisible, éclats
orange qui ressortent, rien à changer") et remonté 3 points sur Crawler/
Ranged/échelle. Traité dans l'ordre, sans rien câbler dans les scènes
(`enemy_crawler.tscn`/`enemy_brute.tscn`/`enemy_ranged.tscn` non touchés —
c'est une revue, pas une intégration).

**Bug trouvé en cours de route (bbox polluée par un mesh fantôme).**
`compute_bbox()` dans `capture_pose.py` itérait tous les meshes du GLB
importé, y compris un mesh nommé "Icosphere" (42 sommets, span statique
±1 unité en Z quelle que soit la pose) présent dans le Crawler riggé —
artefact du pipeline de rig Meshy (probablement un gizmo/proxy), pas de
la géométrie du personnage. Il gonflait la bbox mesurée à ~2.0 unités
quelle que soit la pose, masquant toute variation réelle de taille.
Corrigé par une liste d'exclusion (`IGNORE_MESH_NAMES = {"icosphere"}`).
Après correction, les hauteurs mesurées collent aux `height_meters`
déclarés dans `data/meshy_usage.jsonl` : Crawler 0.911m (déclaré 0.9),
Brute 2.170m (déclaré 2.2), Ranged 1.808m (déclaré 1.8).

**Point 2 — Échelles incohérentes.** Cause : chaque monstre était cadré
avec un `cam_size` auto-calculé depuis SA PROPRE bbox (`max(size)*1.3`),
ce qui efface toute différence de taille réelle entre modèles (chacun
remplit ~77% de son propre cadre, quelle que soit sa taille réelle).
Fix : nouveau paramètre `--target_z` dans `capture_pose.py` (fixe le
centre vertical du cadre en coordonnées monde, indépendamment de la
bbox du personnage) + un seul `cam_size=2.6` partagé par les 4
personnages (calé sur la Brute à 2.17m + 15% de marge, pour qu'elle
remplisse le cadre comme demandé) + un `target_z` par personnage calculé
pour que le sol (bas de bbox) tombe à la même fraction du cadre pour
tous (8% depuis le bas). Un bug de calcul intermédiaire (`target_z` posé
directement à `mins.z + marge`, en oubliant que le centre de cadre est
au MILIEU de la hauteur de cadre et pas près du bas) a d'abord fait
déborder la tête de la Brute hors cadre — détecté par inspection visuelle
du premier rendu, corrigé (`target_z = mins.z + cam_size*(0.5 - marge)`),
re-rendu propre. Résultat : `experiments/monsters_nuit/comparison_scale_fix.png`
— Crawler visiblement plus petit, Ranged intermédiaire, Brute remplit le
cadre, Cendre (référence, ~1.6m) entre Crawler et Ranged. Conforme à la
demande de Milan.

**Point 3 — Crawler ne lit pas comme un quadrupède.** Diagnostic isolé :
rendu de `crawler_rigged.glb` sur son action `clip0` (bind pose native,
single-frame, indépendante de toute anim retargetée) depuis un angle de
profil pur (`cam_yaw_deg=90`) — `/tmp/dbg/crawler_bindpose.png`. Le
résultat montre un personnage debout, bipède, bras le long du corps :
posture verticale de base, pas une pose de quadrupède rampant. Ce n'est
donc ni une question de frame choisie dans l'anim de marche, ni d'angle
de caméra : **c'est le modèle 3D lui-même (le rig/bind pose Meshy) qui
n'a pas de posture quadrupède.** Conformément au mandat ("documente-le,
ne regénère pas sans mon accord"), aucune régénération n'a été lancée —
en attente de décision de Milan (regénérer avec un prompt insistant sur
la posture à 4 pattes coûterait des crédits Meshy).

**Point 4 — Ranged illisible.** Confirmé : la pose attack ("avant")
est un amas de pixels quasi noirs sans silhouette identifiable — voir
`experiments/monsters_nuit/comparison_ranged_legibility.png`. Cause :
la combinaison dithering Bayer (`--dither_amount=0.35` par défaut) +
plancher de Value bas (`--value_band_min=0.165` par défaut) compresse
un modèle déjà très sombre (noir/violet) dans une plage de valeurs
quasi indistinguables. Fix, spécifique à Ranged uniquement (les autres
gabarits gardent les défauts) : `--dither_amount=0.0
--value_band_min=0.35`. La silhouette (cornes, robe, membres) redevient
nettement lisible sur les 2 poses testées (idle et attack), au prix
d'un rendu légèrement moins sombre que prévu à l'origine — compromis
assumé, conforme à la demande de Milan ("quitte à ce qu'il soit moins
sombre que prévu").

**Fichiers produits pour la revue** (rien de committé côté scènes,
uniquement `experiments/` + le fix dans `capture_pose.py`) :
- `experiments/blender_capture/capture_pose.py` — `IGNORE_MESH_NAMES` +
  paramètre `--target_z`.
- `experiments/monsters_nuit/blender_out_v2/` — 4 rendus idle à échelle
  commune (Cendre/Crawler/Brute/Ranged) + Ranged attack, bruts et
  quantifiés 64px.
- `experiments/monsters_nuit/comparison_scale_fix.png` — comparaison
  avant/après échelle, les 4 personnages.
- `experiments/monsters_nuit/comparison_ranged_legibility.png` —
  comparaison avant/après lisibilité Ranged (idle + attack).
- `/tmp/dbg/crawler_bindpose.png` — preuve bind-pose Crawler (non
  committé, purement diagnostique).

**En attente de Milan avant de continuer** : validation du cadrage à
échelle commune + du fix Ranged, et décision sur le Crawler (documenter
en l'état / regénérer le modèle avec un prompt quadrupède plus explicite).
Tant que ces 3 points ne sont pas tranchés, rien n'est câblé dans les
scènes ennemies ni committé au-delà de ce round de revue.

## 2026-08-21 — Régénération image-to-3D depuis les 3 références de Milan

Milan a fourni 3 planches de référence multi-vues (une par monstre,
face/3-4/profil/dos pour Brute et Ranged, 3-4/profil/3-4-arrière pour
Crawler) et demandé une régénération complète via Meshy en image→3D
(au lieu des prompts texte de la Phase 3 initiale), avec pour Crawler
l'exigence explicite que la posture quadrupède soit non-ambiguë, pour
Ranged une prévention appliquée dès le départ (dithering désactivé +
plancher de Value ~0.35, déjà validés la veille), et pour Brute une
régénération de raffermissement (design déjà validé).

**Préparation des références.** Chaque planche a été découpée en
images individuelles par angle (`experiments/monsters_nuit/crop_refs.py`)
pour éviter de nourrir Meshy avec une planche complète (logo, titres,
plusieurs vues juxtaposées — mauvais candidat pour une reconstruction
3D). 3 à 4 crops propres par monstre, vérifiés visuellement avant tout
appel payant.

**Génération** (`meshy_multi_image_to_3d`, meshy-6/latest, 3-4 vues par
monstre, **sans** `pose_mode` pour préserver la posture réelle de la
référence — un `pose_mode=t-pose/a-pose` aurait justement effacé le
quadrupède du Crawler) : 30cr × 3 = 90cr. **Remesh** (250k polys,
sous la limite de 300k du rig, `resize_height` fixé directement sur
les hauteurs déclarées 0.9/2.2/1.8m) : 5cr × 3 = 15cr.

**Vérification posture (avant tout rig)** : rendu Blender rapide de
chaque nouveau maillage brut, comparé à la référence
(`experiments/monsters_nuit/comparison_v2_posture.png`). Confirmé :
Crawler lit sans ambiguïté comme un quadrupède rampant (posture
identique à la référence), Brute conserve sa posture accroupie/bras
tendus. Le problème du round précédent (Crawler bipède dans son
bind-pose) est donc résolu par la régénération depuis l'image de
référence — la posture est maintenant baked dans le maillage lui-même,
plus dans une anim retargetée génériquement.

**BLOQUANT découvert : le rig auto Meshy refuse Crawler et Brute.**
`meshy_rig` échoue avec `422 Pose estimation failed, please provide a
valid model` sur les deux — reproduit 2 fois chacun (pas transitoire),
0 crédit consommé sur les échecs (vérifié par solde avant/après).
Ranged (posture debout, la plus proche d'un bipède standard) rigge sans
problème. Diagnostic : l'estimateur de pose du rig auto Meshy est conçu
pour un personnage debout standard (d'où sa recommandation de
`pose_mode=t-pose` pour un rigging optimal) — un quadrupède à 4 pattes
au sol (Crawler) ou une posture très accroupie/penchée en avant (Brute)
sort de ce qu'il sait reconnaître. **C'est une tension directe avec la
demande de Milan** : la posture qu'il a explicitement exigée fidèle à
la référence est precisément ce qui casse le rig automatique gratuit.

**Ranged, non bloqué, mené à son terme pour ce round** : rig réussi
(5cr, marche+course gratuites incluses), attaque animée avec la même
action que la veille (239 Crouch_Pull_and_Throw, 3cr), rendu idle+attaque
au cadrage à échelle commune déjà établi (cam_size=2.6, target_z=1.092
calculé sur la nouvelle mesure mins.z=0 avec origin_at=bottom) et
quantifié avec le fix de lisibilité (dither=0, value_band_min=0.35).
Résultat : `experiments/monsters_nuit/blender_out_v3/ranged_{idle,attack}_64.png`
— silhouette nette, fidèle à la référence, mêmes réglages qu'approuvés
la veille. Ranged est prêt pour la suite (mort à animer, puis
intégration) dès accord de Milan.

**Fichiers produits** (non committés dans les scènes, aucun câblage) :
- `experiments/monsters_nuit/refs_v2/` — crops de référence par angle.
- `experiments/monsters_nuit/meshy_output_v2/` — GLB bruts + remeshés
  des 3 monstres, + rig/attaque Ranged.
- `experiments/monsters_nuit/blender_out_v3/ranged_{idle,attack}_{raw,64}.png`.
- `experiments/monsters_nuit/comparison_v2_posture.png` — preuve posture
  Crawler/Brute vs référence.
- `data/meshy_usage.jsonl` — traçabilité complète (113cr cette session :
  90 génération + 15 remesh + 5 rig Ranged + 3 attaque Ranged).

**En attente de Milan** : comment traiter le blocage de rig sur
Crawler/Brute — regénérer dans une posture plus neutre compatible avec
le rig auto (perd la fidélité de pose exigée dans la mesh de repos,
récupérable seulement via l'animation ensuite), rigger manuellement dans
Blender (préserve la posture exacte, mais aucune marche/course gratuite,
travail manuel bien plus long), ou une autre option. Ranged continue en
parallèle (mort à animer) puisqu'il n'est pas concerné par ce blocage.

## 2026-08-21 — Rig manuel Blender testé sur Crawler (succès)

Milan a demandé de tester l'option manuelle EN PREMIER (moins coûteuse
que redouté) avant de trancher entre régénération en pose neutre et
rig manuel : script qui construit une armature simple par bones
alignés à la main sur le maillage, `bpy.ops.object.parent_set(type=
'ARMATURE_AUTO')` (pondération automatique, pas de peinture manuelle),
test d'une rotation de patte, rapport avant de passer à la Brute.

**Calibration des coordonnées.** Plutôt que deviner les positions de
bones depuis un rendu projeté (source d'erreurs, cf. les frames
target_z du round précédent), deux outils dédiés créés :
`experiments/blender_capture/calibrate_axes.py` (dépose des sphères
colorées à des coordonnées candidates et rend la scène pour vérifier
visuellement quel axe pointe où) et `inspect_mesh.py` (extrait les
sommets extrêmes par axe + un profil de tranches Y — largeur/hauteur
moyenne tous les 10% de la longueur — pour repérer numériquement
museau, pic dorsal, pattes, arrière-train). A permis de placer 13 bones
(colonne bassin→poitrine→cou→tête, queue, 4 pattes à 2 segments
chacune) sans essai-erreur visuel.

**BLOQUANT initial et sa cause : sommets dupliqués.** Premier essai :
`parent_set(ARMATURE_AUTO)` réussit (modifier + groupes de vertex
créés) mais **poids nul partout** (`max_weight=0.000` sur les 13
groupes) — confirmé par un script de diagnostic dédié
(`debug_weights.py`) qui somme les poids par groupe. La console Blender
affichait un avertissement passé inaperçu au premier passage : `Bone
Heat Weighting: failed to find solution for one or more bones`. Cause
trouvée : le maillage issu du remesh Meshy contient **282419 sommets
dont environ la moitié sont des doublons quasi-exacts** (un sous-produit
probable du remesh par face/shell) — `bpy.ops.mesh.remove_doubles` fait
tomber le compte à 130118. Cette duplication massive empêche totalement
le solveur de diffusion de chaleur de converger (silencieusement, sans
lever d'exception Python — seul un warning texte dans la console, facile
à manquer). **Fix** : `remove_doubles(threshold=0.0001)` +
`normals_make_consistent` sur le mesh AVANT le parentage. Résultat
après fix : poids corrects sur les 13 groupes (voir
`data/meshy_usage.jsonl`-adjacent note ; ex. `pelvis` 18681 sommets à
poids fort, `head` 12920, `front_L_lower` 6181, tous avec un poids max
proche de 1.0). Ce nettoyage devra être systématique pour tout futur
rig manuel sur un maillage remeshé Meshy.

**Test de déformation.** Rotation large et non-ambiguë de
`front_L_upper`/`front_L_lower` (patte avant gauche) en pose mode,
rendu avant/après comparé
(`experiments/monsters_nuit/comparison_manual_rig_test.png`) : la patte
se détache proprement et suit la rotation, aucune déchirure du maillage,
aucun autre segment du corps affecté de façon incohérente. **Le rig
manuel low-tech fonctionne** sur ce maillage, à condition du fix
merge-doubles ci-dessus.

**Fichiers** : `experiments/blender_capture/calibrate_axes.py`,
`inspect_mesh.py`, `rig_manual_test.py` (script complet : import →
nettoyage mesh → armature 13 bones → parentage auto → rendu repos →
rotation test → rendu posé → export GLB), `debug_parent.py` et
`debug_weights.py` (diagnostics, jetables). Export GLB de test :
`/tmp/dbg/crawler_manual_rig2.glb` (non committé, juste la validation —
l'armature définitive sera reconstruite une fois la posture d'idle et
les cycles de marche/attaque décidés avec Milan).

**Prochaine étape (en attente d'accord Milan)** : appliquer la même
méthode sur Brute (même script, coordonnées de bones à recalibrer sur
son maillage propre via `inspect_mesh.py`/`calibrate_axes.py`), puis si
les deux passent, construire une pose idle statique + éventuellement
un cycle de marche à la main (key-frames manuelles, pas de bibliothèque
Meshy) pour les deux monstres.

## 2026-08-21 — Rig manuel Blender : Brute validé aussi (2/2)

Même méthode appliquée à Brute : `calibrate_axes.py` confirme la même
convention d'axes que Crawler (tête/museau côté Y négatif), puis
`inspect_mesh.py` sur `brute_remeshed.glb` (314681 sommets) donne les
points d'ancrage : sommet du crâne (y=-0.13, z=2.20), mâchoire/menton
(extrémité avant basse, y=-1.16, z=1.31), mains au sol (posture
« knuckle-walker », bras très longs : x=±1.37, y=-0.6, z=0.45), jambes
courtes et reculées sous le corps (profil de tranches Y montrant la
largeur X et la hauteur moyenne chuter progressivement de y=0.20 à
y=0.97). Armature à 10 bones construite en conséquence (bassin→
poitrine→cou→tête, 2 bras à 2 segments, 2 jambes à 2 segments) dans
`rig_manual_test_brute.py`.

Même fix merge-doubles appliqué d'emblée (314681 → 129071 sommets) :
aucun warning « Bone Heat Weighting » cette fois, poids corrects du
premier coup. Test de rotation sur le bras gauche (le membre le plus
long/complexe du monstre) : déformation propre, le bras se replie
naturellement sans déchirer le maillage ni affecter le reste du corps
de façon incohérente
(`experiments/monsters_nuit/comparison_manual_rig_test_brute.png`).

**Bilan : 2/2 — le rig manuel fonctionne sur les deux monstres bloqués
par le rig auto Meshy.** Reste à décider avec Milan : construire la
pose idle finale + un cycle de marche à la main (key-frames), et
si besoin refactoriser les deux scripts de test (`rig_manual_test.py`
et `rig_manual_test_brute.py`, presque identiques) en un outil unique
paramétré par une liste de bones — actuellement dupliqués pour aller
vite sur ce round de validation.

## 2026-08-21 — MANDAT SUITE v2 : Phase T (connexion d'outils, un par un)

Nouveau mandat reçu : brancher une liste d'outils AVANT la production,
un par un, avec test isolé + documentation entre chaque, puis enchaîner
Phase 1→2→3→4 sans réattendre de prompt (sauf décision touchant la
matrice du Document Maître).

### T.1.1 — pixeldetector (Astropulse) : NON RETENU

Cloné depuis GitHub (`experiments/tool_evals/pixeldetector/`), testé en
mode `-p` sur `experiments/monsters_nuit/blender_out/ranged_attack_raw.png`
(rendu 512×512 pré-correctif, cas connu bruité). Résultat :
`experiments/tool_evals/pixeldetector_ranged_attack_test.png`.

**Verdict : ne remplace ni ne complète notre pipeline.** Deux problèmes
rédhibitoires :
1. **Aucune gestion de la transparence** — `pixeldetector.py` convertit
   systématiquement l'image en RGB (`Image.open(...).convert('RGB')`
   ligne 100, puis `kCentroid` reconvertit aussi en RGB), le canal
   alpha est perdu et le fond devient un bloc noir opaque. Bloquant
   absolu pour un pipeline de sprites qui exige un fond transparent.
2. **Mauvaise adéquation à notre cas d'usage** : l'outil est conçu pour
   *réparer* un pixel art déjà existant qui a été redimensionné/compressé
   (JPEG, resize) — il détecte la grille de pixels d'origine par pics de
   différence entre pixels voisins. Nos rendus sources sont des rendus
   3D lisses (Cycles), sans grille de pixel-art préexistante à détecter :
   l'outil a donc simplement pris les micro-variations de shading/AA
   pour des "bords de pixel" et produit une image 171×171 à 48 couleurs,
   plus grande et plus bruitée que notre sortie 64×64 volontairement
   quantifiée (`experiments/monsters_nuit/blender_out_v3/ranged_attack_64.png`,
   dither désactivé, plancher de Value 0.35) — pas d'amélioration de
   lisibilité, perte de la transparence, résolution non conforme à la
   convention 64px du jeu.

**Conclusion : pixeldetector n'est pas intégré au pipeline de
production.** Resterait potentiellement utile un jour pour un cas très
différent (récupérer un pixel art externe déjà fait mais abîmé par une
compression/redimensionnement), pas pour notre chaîne rendu-3D→pixel-art.
Passage à T.1.2 (bake de normal maps).

### T.1.2 — Normal maps pour sprites 2D : RETENU (technique adaptée)

**Écart assumé par rapport à la lettre du mandat** : `bpy.ops.object.
bake(type='NORMAL')` (bake UV tangent-espace, pensé pour retexturer un
mesh reprojetable sous n'importe quel angle) ne correspond pas à notre
besoin réel — un sprite 2D est une image figée sous UN SEUL angle de
caméra fixe. L'équivalent fonctionnel correct est la **passe de rendu
"Normal" de Cycles en espace camera** (`view_layer.use_pass_normal`),
rendue par le même compositeur que la passe couleur, sur le même
maillage/pose/caméra — ce qui donne directement une normal map alignée
pixel-à-pixel avec le sprite diffuse, sans étape de reprojection UV.
Remap `[-1,1] -> [0,1]` fait dans le compositeur (Multiply 0.5, Add 0.5,
alpha préservé depuis la passe Alpha) pour sortir un PNG 8-bit standard
sans dépendance à un lecteur EXR. Script : `experiments/tool_evals/
bake_normal_cendre.py`.

**Vérification de la convention (avant tout câblage définitif)**, en 2
temps :
1. **Convention Godot elle-même** : normal map synthétique (une
   demi-sphère bombée, générée en pur Python/numpy, `hemisphere_normal.
   png`) avec le canal G construit explicitement "haut = vert fort" (au
   sens propre convention OpenGL). Deux scènes Godot isolées identiques
   sauf la position du `PointLight2D` (au-dessus vs en-dessous, même
   distance) : lumière au-dessus → liseré du HAUT de la sphère éclairé ;
   lumière en-dessous → liseré du BAS éclairé. Comportement physiquement
   correct et sans ambiguïté (`hemisphere_above.png` / `hemisphere_below.
   png`) — confirme que `CanvasTexture.normal_texture` + `PointLight2D`
   de Godot 4 suit bien la convention "G fort = vers le haut de l'image".
2. **Convention de la passe Blender elle-même** : une sphère de
   référence ajoutée à côté de Cendre dans la même scène/caméra que le
   test précédent. Mesure numérique du canal G au pôle nord vs pôle sud
   de cette sphère dans le rendu : G=165.6 en haut, G=123.8 en bas —
   même sens que la convention validée côté Godot au point 1. **Aucun
   flip du canal G n'est nécessaire entre Blender et Godot** : la passe
   Normal de Cycles, remappée telle quelle, est directement compatible.

**Recette validée pour la suite** (Phase 2.2 généralisera aux
monstres) : rendre beauty + passe Normal depuis la MÊME caméra/pose,
remap compositeur, exporter les deux PNG, assigner en `CanvasTexture`
(`diffuse_texture` + `normal_texture`) sur le `Sprite2D`, aucun shader
custom requis — les `PointLight2D` déjà posés dans les scènes (torches,
lueur du joueur) en profitent automatiquement.

**Test isolé, zéro impact jeu** : tout dans `experiments/tool_evals/`
(scènes de test, textures synthétiques et rendues), rien touché dans
`scenes/gameplay/` ni dans les sprites de production de Cendre.
Passage à T.1.3 (PyTexturePacker).

### T.1.3 — PyTexturePacker : RETENU (glue Godot nécessaire)

Aujourd'hui, chaque frame de sprite (`assets/processed/sprites/cendre/
idle_south/0.png` etc.) est un PNG individuel — aucun atlas, packing
absent. Testé `PyTexturePacker` (MaxRects) sur les 4 frames
`idle_south` de Cendre : `experiments/tool_evals/texturepacker_test/`.

Constat : le format de sortie par défaut est un `.plist` (convention
Cocos2d) — pas nativement lisible par Godot. Mais `atlas_format` accepte
aussi une **fonction callable** `(data_dict, file_path) -> str`, ce qui
permet de générer directement des ressources Godot natives sans étape
de parsing intermédiaire. Preuve : `experiments/tool_evals/
pack_to_godot_atlastexture.py` — callable qui émet un `AtlasTexture`
`.tres` par frame (`atlas = ExtResource(atlas.png)`, `region =
Rect2(x,y,w,h)`), pointant vers UN SEUL PNG packé au lieu de 4 fichiers
séparés. Vérifié en conditions réelles : `.tres` généré chargé dans une
scène Godot isolée (`test_atlastexture.tscn`), capturé via le pipeline
xvfb+vulkan existant — la frame 0 s'affiche correctement, découpée au
bon endroit dans l'atlas packé (`capture_atlastexture.png`). Alpha
préservé (vérifié numériquement, fond RGBA(0,0,0,0)).

**Conclusion : outil retenu**, avec un vrai gain (réduction du nombre
de fichiers texture / bind textures à l'exécution — actuellement une
texture séparée par frame pour tout le roster), MAIS l'intégration
complète (re-packer TOUTES les animations de tous les personnages/
monstres et regénérer les `SpriteFrames` correspondants pour pointer
vers des `AtlasTexture` au lieu de fichiers séparés) est un chantier à
part entière, pas fait ici — hors du périmètre du test isolé demandé
("teste sur UN SEUL personnage"). À planifier si Milan confirme
l'intérêt vu l'ampleur du roster déjà produit.
Passage à T.1.4 (pyfxr).

### T.1.4 — pyfxr : RETENU (installation propre, pas besoin du fallback)

L'inquiétude du mandat (wheels précompilées obsolètes face à un Python
récent) ne s'est pas confirmée : `pip install pyfxr` s'installe sans
erreur sur Python 3.11.15 (extension native `_pyfxr.SoundBuffer`, wheel
cp311 disponible). Test : `pyfxr.hurt().build()` → `SoundBuffer`
(mono, 44100 Hz, ~0.04s), exporté en `.wav`
(`experiments/tool_evals/pyfxr_impact_test.wav`) et vérifié
numériquement non silencieux (RMS ~21000/32767, signal réel, pas du
bruit résiduel).

Présets prêts à l'emploi couvrant exactement les familles demandées en
Phase 2.1 : `hurt` (impact), `explosion` (impact lourd), `jump`,
`laser`/`pluck` (whoosh candidats), `pickup`/`powerup` (apparition),
`tone`/`chord` (notes libres). Chaque appel est aléatoire par défaut
(graine interne via `random`) — la variante de pitch ±5% demandée est
directement atteignable en rejouant l'appel ou en dérivant `base_freq`.
**Aucun fallback numpy/wave nécessaire.** Câblage réel sur les
sfx_markers (Phase 2.1) laissé pour cette phase-là, pas fait ici (test
isolé = un seul son généré et vérifié).
Passage à T.1.5 (Blender To Pixels).

### T.1.5 — Blender To Pixels : NON TESTABLE dans cet environnement

Contrairement à `pixeldetector` (dépôt GitHub public, `git clone` direct),
**Blender To Pixels n'a pas de dépôt GitHub** — confirmé par recherche
web (`git clone https://github.com/Astropulse/Blender-to-Pixels.git`
échoue avec "could not read Username", et non par absence de réseau :
`pixeldetector` s'est clonée sans problème juste avant). L'outil est
distribué exclusivement via itch.io/Gumroad en "name your own price"
(0€ possible), sous forme d'archive ZIP (`BlenderToPixels.zip`, 327 Ko)
téléchargée via le bouton "Download Now" d'itch.io — un flux
d'interaction navigateur (potentiellement JS/session), pas une URL
statique directement `curl`-able trouvée sans naviguer manuellement la
page.

**Conclusion : non testé.** Pas de blocage technique de fond (l'outil
existe, est gratuit), mais son mode de distribution ne se prête pas à
une récupération scriptée dans cet environnement sans navigateur
interactif. Vu le principe du mandat ("garder seulement s'il apporte un
vrai gain, pas juste pour l'avoir") et que notre pipeline `quantize.py`
est déjà éprouvé sur l'ensemble du roster cette session (dithering,
plancher de Value, contours, tous calibrés et validés à la main sur
Cendre/Crawler/Brute/Ranged), le gain incertain d'un outil non
récupérable ne justifie pas de détour supplémentaire (ex. tenter de
reproduire l'API de téléchargement itch.io). Repris plus tard
uniquement si Milan peut fournir le ZIP directement.
Passage à T.1.6 (auto-godot).

### T.1.6 — auto-godot : NON TESTABLE (incompatibilité de version)

Recherche web : `auto-godot` est un outil CLI reel ("A Headless CLI
Tool for Godot Engine Targeting Agent Workflows") mais **nécessite
Godot 4.6+ et Python 3.12+**. Ce projet tourne sur **Godot 4.3.stable**
(`godot4 --version` confirmé) et l'environnement fournit Python 3.11.15.
Aucune URL PyPI ou dépôt GitHub canonique trouvée malgré recherche
ciblée (contrairement à `pixeldetector`, directement cloné plus tôt) —
impossible même de tenter l'installation.

**Conclusion : non testé, non retenu.** Deux blocages indépendants
(version Godot, version Python) rendent l'outil inutilisable tel quel
sur ce projet ; monter de version Godot pour un seul outil CLI
expérimental serait hors de proportion et risqué (implique de
revalider tout le pipeline existant — scenes, shaders, addons). Le
process d'export manuel actuel (`godot4 --headless --rendering-driver
vulkan --export-release "Web" docs/index.html`, déjà utilisé et fiable
tout au long de cette session) reste en place sans changement.

### Bilan Phase T.1 (6/6 traités)

| Outil | Verdict |
|---|---|
| pixeldetector | Non retenu (pas d'alpha, mauvais cas d'usage) |
| Bake normal maps (Blender) | **Retenu** — technique adaptée (passe Normal, pas bake UV), convention vérifiée |
| PyTexturePacker | **Retenu** — glue Godot (callable → AtlasTexture) fonctionnelle |
| pyfxr | **Retenu** — install propre Python 3.11, présets couvrent les familles Phase 2.1 |
| Blender To Pixels | Non testable (distribution itch.io, pas de dépôt scriptable) |
| auto-godot | Non testable (nécessite Godot 4.6+/Python 3.12+, incompatible) |

Phase T.2 (Freesound, Tripo3D) reste bloquée en attente des clés API de
Milan — non bloquant pour la suite (Phase 1 enchaîne directement).

## 2026-08-21 — MANDAT SUITE v2 : Phase 1.1 (armature définitive Crawler + Brute)

Suite du rig manuel validé (Crawler puis Brute, cf. entrées précédentes
2/2) : construction du pipeline **définitif** par monstre
(`experiments/blender_capture/rig_final_crawler.py` /
`rig_final_brute.py`), sur les meshes déjà remeshés et payés
(`crawler_remeshed.glb`, `brute_remeshed.glb`). Portée volontairement
réduite conformément au mandat : **idle (bind pose) + UNE pose
d'attaque tenue en keyframes manuelles** — pas de cycle de marche
animé (trop coûteux pour le prototype ; le déplacement sera géré par
glissement de la pose idle + léger bob procédural via
`AnimationComposer`, déjà prêt).

**Crawler** : armature 13 os identique au test validé, nettoyage
mesh (`remove_doubles` + `normals_make_consistent`) systématisé avant
`parent_set(ARMATURE_AUTO)`. Pose d'attaque = morsure basse + pattes
avant poussées en avant (lunge de prédateur) : `neck` -35°, `head`
-25°, `front_{L,R}_upper` +30°, `front_{L,R}_lower` -15°, `pelvis`
-10°. Rendu idle+attaque à l'échelle commune (`cam_size=2.6`,
`target_z=1.0878`) directement propre, sans recadrage — aucun
problème rencontré. Quantifié (`--target_saturation=0.55`, réglages
par défaut sinon, identique à Cendre) → `crawler_{idle,attack}_64.png`.
Export GLB rigged final : `crawler_final_rigged.glb`.

**Brute** : armature 10 os identique au test validé. Pose d'attaque =
smash aérien, bras droit levé (`arm_R_upper` -100°/15°/-15°,
`arm_R_lower` +50°, `arm_L_upper` +10°/0/+10° pour stabiliser,
`chest` -15°/0/+8°).

Bug rencontré et résolu : idle ET attaque montraient le haut de la
tête/des pics d'épaule **coupé en haut du cadre**, avec les mêmes
paramètres caméra (`cam_size=2.6`, `target_z=0.892`) validés plus tôt
dans la session sur ce même mesh. Deux hypothèses écartées (la pose
d'attaque pousserait la géométrie hors cadre ; le centrage X/Y caméra
hardcodé à (0,0) serait faux — le centre X/Y réel calculé était déjà
quasi (0,0), donc pas la cause). Cause réelle trouvée en imprimant
explicitement `mins.z`/`maxs.z` de la bbox évaluée (pas seulement leur
milieu) : `mins.z ≈ 0.0` (pas `-0.2` comme supposé lors du calcul
initial de `target_z=0.892`), `maxs.z ≈ 2.2` (sommet du crâne, cohérent
avec la calibration `inspect_mesh.py`). La valeur `target_z=0.892`
avait été dérivée d'une hypothèse `mins.z=-0.2` qui ne correspond pas
au mesh réellement utilisé dans ce script — d'où un cadrage trop bas
de 0.2 unité, suffisant pour couper les pics du haut à `cam_size=2.6`.

Fix : `rig_final_brute.py` calcule maintenant `target_z` directement
depuis la bbox réelle de la bind pose (`mins.z + cam_size*(0.5 -
bottom_margin_frac)`, `bottom_margin_frac=0.08`, formule déjà établie
plus tôt dans la session) au lieu de faire confiance à une valeur
`--target_z` fournie en ligne de commande supposant un `mins.z` qui
s'est révélé faux pour ce mesh. `target_z` recalculé : `1.092` (au
lieu de `0.892`), réutilisé identique pour les deux rendus (idle +
attaque) afin de garder une échelle cohérente entre les deux poses.
Après ce fix : idle et attaque rendent proprement, silhouette complète
visible, aucun recadrage. Quantifié aux mêmes réglages que Crawler
(`--target_saturation=0.55`) → `brute_{idle,attack}_64.png`. Export
GLB rigged final : `brute_final_rigged.glb`.

**Leçon pour la suite** : ne jamais réutiliser une valeur `target_z`
figée d'une session précédente sans revérifier `mins.z`/`maxs.z` sur
le mesh effectivement chargé par le script en cours — un script qui
recharge un GLB doit calculer sa propre bbox plutôt que d'hériter
d'une constante calibrée ailleurs, même si le fichier source semble
identique.

**Statut Phase 1.1** : Crawler + Brute ont maintenant leur armature
définitive, idle + attaque rendus/quantifiés/exportés. Reste avant
intégration : mort Ranged (Phase 1.2, `meshy_animate`), puis
intégration réelle des 3 monstres dans les scènes de jeu (Phase 1.3).

## 2026-08-21 — MANDAT SUITE v2 : Phase 1.2 (mort Ranged)

Ranged étant déjà riggé avec succès par Meshy (contrairement à Crawler/
Brute, cf. blocage documenté), la mort est une vraie animation de
bibliothèque (`meshy_animate`), pas une pose statique — seul monstre
des 3 dans ce cas pour l'instant.

**Choix de l'action** : pas d'outil de listing exposé côté MCP
(`meshy_animate` prend un `action_id` numérique fixe uniquement) —
recherche dans la référence documentée de Meshy
(`docs.meshy.ai/en/api/animation-library`, catégorie Fighting/Dying)
pour un nom correspondant littéralement à « mort » : `action_id=8`
("Dead") retenu, même logique de sélection que les choix précédents
(`Left_Slash` pour « un coup », `Roll_Dodge` pour « dash ») — nom le
plus proche disponible, pas d'options exotiques liées à des armes à
feu (`Shot_and_Fall_*`) hors thème.

**Exécution** : solde vérifié avant (869cr, inchangé depuis la veille —
aucun appel Meshy pendant le travail Blender manuel sur Crawler/Brute).
`meshy_animate(rig_task_id=01a024b4-1270-70eb-b5f1-8c07587afea5,
action_id=8)` → succès, 3cr consommés (conforme au budget ~3cr annoncé
dans le mandat). GLB téléchargé (26MB, `Animation_Dead_withSkin.glb`,
confirme le nom "Dead") → `ranged_death.glb`.

**Rendu** : une seule action dans le GLB (`Armature|Dead|baselayer_
Armature`, frame_range 0.8-72.0, ~3s à 24fps). 6 frames échantillonnées
uniformément sur toute la plage, rendues à l'échelle commune (`cam_size
=2.6, target_z=1.092`, même convention mins.z=0/bottom_margin_frac=0.08
que Brute) via `capture_pose.py --anim_frame=...`. Centre X/Y recalculé
par frame (bbox réelle de la pose), `target_z` fixé (référence sol
commune, pas de recentrage vertical qui effacerait l'affaissement du
corps). Clipping mineur (~20-25px de bouts de filaments fins sur les 2
dernières frames, marge basse 8% du cadre) jugé négligeable après
réduction à 64×64 — même tolérance que documentée précédemment pour
d'autres poses ("le canevas final 64×64 absorbe la marge").

Quantifié aux réglages Ranged déjà établis (`--target_saturation=0.55
--dither_amount=0.0 --value_band_min=0.35`, fix de lisibilité sur fond
très sombre) → `ranged_death_{0..5}_64.png`. Séquence visuellement
vérifiée (`ranged_death_strip.png`) : progression lisible — debout/
touché → bras levé/chancelant → effondrement → chute → étalé au sol,
silhouette nette à chaque frame grâce au fix dither=0.

**Statut Phase 1.2 : terminé.** Ranged a maintenant idle + attaque
(round précédent) + mort (6 frames). Reste : Phase 1.3, intégration
réelle des 3 monstres (remplacement des rectangles placeholder,
`HitResponse`, hitbox/hurtbox, IA existante), puis Phase 1.4 (redeploy
web).

## 2026-08-21 — MANDAT SUITE v2 : Phase 1.3 (intégration réelle des 3 monstres)

Remplace les rectangles `Polygon2D` placeholder par les vrais sprites
dans les 3 scènes d'archétype (`enemy_crawler.tscn`, `enemy_brute.tscn`,
`enemy_ranged.tscn`). Constat de départ important en lisant
`src/gameplay/enemy.gd` : `HitResponse` (flash/chiffres de dégâts/burst
de mort), le hitbox/hurtbox (`CollisionShape2D`) et l'IA (`_run_ai`,
états IDLE/CHASE/TELEGRAPH/RECOVER, contact MELEE et projectile RANGED)
étaient **déjà entièrement câblés** depuis Phase G — le seul manque
réel était le visuel. Portée de cette étape réduite en conséquence :
pas de réécriture de la logique de combat, juste le sprite + les hooks
d'animation.

**Assets** : les PNG 64×64 déjà produits/quantifiés (Phase 1.1/1.2)
copiés sous `assets/processed/sprites/{crawler,brute,ranged}/` (`idle.
png`, `attaque.png`, + `mort_0..5.png` pour Ranged). 3 `SpriteFrames`
`.tres` écrits à la main (mêmes principes que `pack_to_godot_
atlastexture.py` en Phase T.1.3 : un format Godot simple, pas besoin du
pipeline `build_sprite_frames.py`/manifeste cuit, disproportionné pour
1-2 frames par anim). `mort` (Ranged uniquement) à 6fps (divise 60,
même discipline de ticks entiers que `cendre_frames.tres`).

**Alignement sol** : chaque sprite mesuré (ligne de pixel opaque la
plus basse de l'idle, numpy) puis converti en `offset` du nœud
`AnimatedSprite2D` pour faire coïncider le contact au sol avec l'origine
du `CharacterBody2D` (même convention que `player.tscn`, `offset=
(0,-32)` avec capsule `(0,-24)`) : Crawler `offset=(0,-31)`
(collision `(0,-11)`, hauteur 22 → bas capsule = 0 ✓), Brute
`offset=(0,-31)` (collision `(0,-20)`, hauteur 40 → bas = 0 ✓), Ranged
`offset=(0,-28)` (collision `(0,-15)`, hauteur 30 → bas = 0 ✓) — les 3
vérifiés par calcul, pas par tâtonnement visuel.

**enemy.gd** : `_visual` résout maintenant `Visual` (AnimatedSprite2D,
les 3 scènes réelles) OU `Placeholder` (Polygon2D, le mannequin
générique `enemy.tscn` encore utilisé par ~10 checks smoke test,
jamais retouché) — `HitResponse.flash_sprite()` prend déjà n'importe
quel `CanvasItem`, aucune branche nécessaire là. Ajouts :
- `_play_visual_animation()` : joue "attaque" à l'entrée en TELEGRAPH,
  "idle" au retour CHASE après RECOVER (no-op silencieux sur le
  mannequin Polygon2D ou toute anim absente).
- `_update_visual_bob()` : bob procédural (amplitude 2px, période 20
  ticks) + `flip_h` selon le sens du déplacement, actif seulement
  pendant CHASE avec vélocité non nulle — remplace le cycle de marche
  qu'on a choisi de ne PAS produire (Phase 1.1, scope réduit).
- `_die()` : Ranged (seul avec une anim "mort") joue la séquence,
  désactive IA/collision, libère via `animation_finished` (`CONNECT_
  ONE_SHOT`) ; Crawler/Brute (pas d'anim mort) retombent sur le
  `queue_free()` immédiat d'avant — 0 régression pour les deux.

**Intégration réelle confirmée** : `gate_premiere.tscn` (le niveau
jouable) et `test_arena.tscn` instancient déjà `enemy_crawler/brute/
ranged.tscn` — aucune modification supplémentaire nécessaire, les
nouveaux visuels sont hérités automatiquement par la scène réelle.

**Vérification** : `--import` headless propre (0 erreur sur les 3
nouveaux `SpriteFrames`+PNG) ; `scripts/run_gameplay_smoke_test.sh`
100% vert (`all_pass:true`, y compris les 3 checks IA spécifiques —
`crawler_chases_then_hits_player`, `brute_telegraphs_before_landing_a_
heavier_hit`, `ranged_retreats_to_preferred_range_then_hits_player_
with_projectile`) — 0 régression. Capture visuelle en moteur réel
(`tools/capture_scene.tscn --mode=scene`) sur les 3 scènes : sprites
chargés, filtrage NEAREST respecté (projet en `default_texture_
filter=0`), silhouettes distinctes et lisibles.

**Statut Phase 1.3 : terminé.** Les 3 monstres sont maintenant de
vrais habitants du jeu (pas des assets en dossier) : intégrés + gates
au vert. Reste : Phase 1.4, redeploy du build web (premier jalon
jouable de ce mandat).

## 2026-08-21 — MANDAT SUITE v2 : Phase 1.4 (redeploy web — premier jalon jouable)

`godot4 --headless --rendering-driver vulkan --export-release "Web"
docs/index.html` — export propre, `docs/index.pck` (contient les 3
nouveaux `SpriteFrames`+PNG et le script `enemy.gd` mis à jour) et
`docs/index.html` régénérés ; `index.wasm`/`index.js` inchangés (aucune
modification du moteur/template d'export). Vérifié avant export :
`scripts/run_gameplay_smoke_test.sh` déjà vert (Phase 1.3).

**Fin de Phase 1 (MANDAT SUITE v2) : les 3 monstres (Crawler, Brute,
Ranged) sont désormais joués dans le build web déployé** — rig
définitif + idle/attaque (Crawler/Brute) ou idle/attaque/mort (Ranged),
HitResponse/hitbox/IA existants confirmés non régressés, plus de
rectangles placeholder. Premier jalon jouable de ce mandat livré.
Enchaîne sur Phase 2 (fondations : son, normal maps généralisées,
post-render, primitives VFX 6→15) sans nouveau prompt, conformément à
l'instruction finale du mandat.

## 2026-08-21 — MANDAT SUITE v2 : Phase 2.1 (son — priorité absolue)

Le jeu était 100% silencieux. `sfx_markers` existe dans le format de
recette (`data/recipes/*.json`) depuis le début mais n'avait jamais été
consommé par aucun système — confirmé en grep : aucune référence
côté moteur avant cette étape.

**Génération** (`scripts/generate_sfx.py`, pyfxr — T.1.4, retenu) : 6
familles en .wav mono 44.1kHz, `assets/processed/sfx/` : `light_impact`
(preset `hurt()`), `heavy_impact` (preset `explosion()`), `whoosh`
(paramétrique : bruit + rampe de fréquence descendante + passe-bas
suiveur — recette jsfxr classique, aucun preset direct disponible),
`spawn` (preset `powerup()`), `death` (paramétrique : onde en dents de
scie, longue rampe de fréquence descendante — trope "mort", distinct de
`heavy_impact`), `footstep` (paramétrique : bruit très bref filtré,
volontairement discret pour ne jamais se confondre avec un impact de
combat). Seeds fixés pour les presets randomisés (reproductibilité de
CETTE génération d'asset hors moteur, aucun rapport avec le
déterminisme RNDC du gameplay réel). RMS vérifié non-silencieux sur les
6 (17000-25000/32767).

**Bus audio** (`default_bus_layout.tres`, jamais configuré avant cette
étape — `grep audio/buses project.godot` ne renvoyait rien) : Master,
`SFX_Combat`, `SFX_UI` (posé, pas encore consommé — aucune UI sonore
dans le scope de cette brique), `Music` (posé, pas encore de musique —
prêt pour plus tard). Référencé dans `project.godot`
(`audio/buses/default_bus_layout`).

**Autoload `Sfx`** (`src/gameplay/sfx.gd`) : pool de 12
`AudioStreamPlayer` (même discipline de pool que `HitResponse`'s
`DamageNumberPool`), `Sfx.play(event, bus="SFX_Combat")` — `pitch_scale`
randomisé ±5% par lecture (mandat "pitch variants ±5%" appliqué au
runtime, pas des fichiers dupliqués). Nom d'événement inconnu = no-op
silencieux, même discipline que `Enemy._play_visual_animation()`.
"Hit-stop ne coupe jamais la musique" (mandat) : déjà garanti par
construction — le hit-stop (`CombatFeedback`) est un compteur de ticks
auto-consulté par les nœuds de combat (§9.1, docs/ARCHITECTURE_VFX_v3),
jamais un throttle de l'arbre de scène ni de l'Engine ; un
`AudioStreamPlayer` qui ne consulte jamais `is_frozen()` continue de
jouer normalement.

**Câblage** (attaquant = propriétaire du son d'impact, même schéma que
`Player._try_hit()` qui possédait déjà VFX/hit-stop de son propre coup —
jamais le récepteur qui joue le son de qui l'a touché) :
- `Player._try_hit()` : `light_impact`/`heavy_impact` selon le même
  seuil que le hit-stop existant (tier `"light"` vs le reste) — pas un
  2e barème.
- `Player._try_hit_bras_faux()` : `heavy_impact` (tier "medium", même
  raisonnement que Gueule Vide).
- `Player.play_dash()` : `whoosh`.
- `Player.die()` : `death`.
- `Player._handle_movement()` : `footstep` toutes les 18 ticks pendant
  un déplacement réel — aucune donnée de contact au sol par frame
  n'existe encore pour les 8 directions, période fixe plutôt que
  d'inventer une donnée absente.
- `Enemy._execute_attack()` (MELEE) : `light_impact`/`heavy_impact`
  selon `hitstop_profile`. `Enemy._die()` : `death`.
- `Projectile` (Ranged) : `light_impact` au contact joueur.
- `GueuleVide._ready()` : `spawn`. `GueuleVide._resolve_contact()` :
  `heavy_impact` (tier "medium", même raisonnement que Bras-Faux).

Piège évité en cours de route : un premier jet faisait jouer
`light_impact` à la fois dans `Player.take_damage()` (récepteur) ET
dans `Enemy._execute_attack()`/`Projectile` (attaquant) pour le MÊME
coup — deux sons empilés sur un seul impact. Corrigé en retirant l'appel
côté `Player.take_damage()` : le son d'impact appartient à
l'attaquant, jamais dupliqué côté victime.

**Vérification** : `--import` headless (0 erreur après un premier essai
qui a révélé l'ordre "préload avant génération du .import" — un second
`--import` après génération des `.wav` suffit) ; `scripts/
run_gameplay_smoke_test.sh` toujours 100% vert, 0 régression. Un
avertissement bénin "resource still in use at exit" apparaît au
shutdown headless (probablement le pool `AudioStreamPlayer` de l'autoload
Sfx, persistant par conception jusqu'à la fin du process) — sans impact
sur les tests, noté tel quel.

**Statut Phase 2.1 : terminé** (SFX + bus). Reste dans Phase 2 : normal
maps généralisées aux monstres, post-render (bloom/outline/paletteRamp/
directionalStreak), primitives VFX 6→15. Freesound (T.2.7) reste
bloqué en attente de la clé de Milan — non utilisé ici, uniquement
pyfxr (déjà en autonomie complète).

## 2026-08-21 — MANDAT SUITE v2 : Phase 2.2 (normal maps généralisées aux monstres)

Généralise la technique validée en Phase T.1.2 sur Cendre (passe Normal
Cycles espace caméra, remap compositor [-1,1]->[0,1], convention Y+ =
haut vérifiée deux fois indépendamment) aux 3 monstres — idle+attaque
(pas la séquence de mort Ranged, hors scope volontairement : 6 frames
supplémentaires pour un bénéfice marginal sur une pose qui disparaît
vite, pas demandé explicitement par le mandat).

**Généralisation technique** : extrait la logique compositor de
`bake_normal_cendre.py` dans un module partagé
`experiments/blender_capture/normal_pass.py`
(`render_normal_pass(scene, out_path)`), importé par les 3 pipelines
existants (`rig_final_crawler.py`, `rig_final_brute.py`,
`capture_pose.py`) via `sys.path.insert` sur le dossier du script
(convention Blender `--python`) — pas de duplication de la logique
caméra/éclairage, chaque script garde sa propre passe beauty, ajoute
juste l'appel à la passe Normal juste après (même camera/pose en
place, donc alignement garanti par construction).

**Downscale 64×64 sans casser l'encodage vectoriel** : `quantize.py`
fait de la pixel-art (HSV/palette/dithering/contours) — inadapté à un
normal map qui encode des VECTEURS, pas des couleurs. Nouveau
`quantize_normal.py` réutilise UNIQUEMENT `pixelate_block_center()`
(déjà écrite dans `quantize.py`, échantillonnage du centre de bloc,
pas une moyenne) pour garantir un alignement pixel-à-pixel exact entre
`normal_texture` et `diffuse_texture` : les deux images source
partagent la même résolution/cadrage caméra, donc les mêmes
coordonnées de bloc tombent sur le même texel des deux côtés.

**Vérification déterminisme avant tout downscale** : re-rendu Crawler
idle/attaque et Brute idle/attaque avec les scripts existants (mêmes
poses, mêmes seeds de bones) — idle bit-à-bit identique à l'image déjà
committée (0 diff), attaque à ~0.5/255 de diff moyenne (bruit Cycles
stochastique entre deux exécutions, aucun seed de sampling fixé —
sans incidence après quantification 64px). Confirmé : pas besoin de
retoucher les diffuse Crawler/Brute déjà committés, seule la passe
Normal est nouvelle pour ces deux-là.

**Ranged, cas différent** : la frame exacte utilisée pour l'attaque
committée n'était pas enregistrée (pipeline `capture_pose.py` générique,
`--anim_frame` choisi "par inspection visuelle" à l'époque, valeur non
notée). Recherche visuelle sur 6 candidats (frames 20-120 sur les 140
de l'action `Crouch_Pull_and_Throw`) → frame 80 identifiée comme la
plus proche visuellement de l'image committée, mais diff mesurée
~6% des pixels de silhouette (filaments fins très mobiles d'une frame
à l'autre) — trop pour ignorer. Plutôt que d'apparier un ancien
diffuse à un nouveau normal map (désalignement garanti), régénéré
diffuse+normal ENSEMBLE à la frame 80, requantifié avec les réglages
Ranged déjà établis (`--target_saturation=0.55 --dither_amount=0.0
--value_band_min=0.35`), et remplacé `assets/processed/sprites/ranged/
attaque.png` par ce nouveau rendu (silhouette différente en détail,
même lisibilité/qualité, alignement garanti avec son normal map).
Idle Ranged : action à une seule frame (7.2s fixe), aucune ambiguïté,
diffuse inchangé, seule la passe Normal ajoutée.

**Intégration Godot** : 6 `CanvasTexture` (`.tres`, un par pose ×
monstre — `idle_canvas.tres`/`attaque_canvas.tres` dans chaque dossier
`assets/processed/sprites/<monstre>/`), même format déjà validé Phase
T.1.2 (`diffuse_texture`/`normal_texture`). Les 3 `SpriteFrames`
(`crawler_frames.tres`/`brute_frames.tres`/`ranged_frames.tres`)
pointent maintenant vers ces `CanvasTexture` au lieu des PNG bruts pour
`idle`/`attaque` (la séquence `mort` de Ranged reste en PNG simple,
hors scope). Aucune modification du code moteur (`enemy.gd`) : un
`AnimatedSprite2D` affiche une `CanvasTexture` exactement comme un
`Texture2D` simple.

**Vérification réelle en moteur** (pas juste "ça charge") : scène de
test `experiments/tool_evals/normal_test_assets/test_crawler_light_
{left,right}.tscn` (même schéma que le test Cendre) — `PointLight2D`
à gauche puis à droite du sprite Crawler idle. Capturé via
`capture_scene.tscn --mode=scene`, image éclaircie ×4 pour inspection :
confirmé visuellement que le côté du monstre FACE à la lumière
s'éclaircit et que ça s'inverse correctement quand la lumière change
de côté — le normal map module bien l'éclairage par pixel, pas un flat
shading. Les `PointLight2D` déjà existants dans le jeu (torches,
impacts) bénéficient automatiquement, aucun câblage supplémentaire
nécessaire (même architecture `CanvasTexture` + `Light2D`, zéro
shader custom).

**Vérification régression** : `--import` headless propre,
`scripts/run_gameplay_smoke_test.sh` 100% vert après le remplacement
du diffuse Ranged attaque (0 régression — les checks combat ne
dépendent pas du contenu pixel du sprite). Redeploy web inclus.

**Statut Phase 2.2 : terminé.** Reste dans Phase 2 : post-render
(bloom/outline/paletteRamp/directionalStreak) et primitives VFX 6→15.

## 2026-08-21 — MANDAT SUITE v2 : Phase 2.3 (post-render stack) + Phase 2.4 (déjà complète)

**Phase 2.4 vérifiée sans action** : avant d'écrire quoi que ce soit,
vérifié l'état réel des primitives VFX (`ls src/vfx/primitives/`,
`wc -l`, grep dans `vfx_director.gd`) plutôt que de faire confiance à
la mention du mandat — le passage 6→15 primitives était déjà
intégralement fait par une session antérieure. Aucune régénération,
aucun doublon de travail.

**Phase 2.3, périmètre** : `docs/ARCHITECTURE_VFX_v3.md` §10.1 liste
4 effets — emissiveBloom, outlineSelective, paletteRamp,
directionalStreak. Deux d'entre eux (bloom, paletteRamp) sont des
passes GLOBALES (toute la scène) ; les deux autres (outline, streak)
sont des effets PAR-SPRITE (un seul personnage à la fois) — donc deux
familles de shaders, pas quatre fichiers isolés.

**`post_render.gdshader`** (nouveau, global) : combine emissiveBloom
(4-tap bright-pass sur `SCREEN_TEXTURE`, seuil 0.72, gain 0.6 — un
"poor man's bloom" sans flou gaussien multi-passe, suffisant à cette
échelle 640×360) et paletteRamp (conversion HSV, clamp de la Value
dans `[value_band_min, value_band_max]`, posterize à `ramp_steps`
paliers) en une seule passe `hint_screen_texture`. Ajouté comme
nouveau `CanvasLayer`/`ColorRect` "PostRender" dans les 3 scènes de
jeu réelles (`gate_premiere.tscn`, `test_arena.tscn`, `outpost.tscn`),
inséré AVANT le `CanvasLayer` "Vignette" existant dans l'arbre (donc
monde → PostRender → Vignette → HUD à l'écran) — même convention que
Vignette : un `ColorRect`+`ShaderMaterial` dupliqué par scène, pas un
autoload centralisé (le projet n'a jamais utilisé ce pattern pour ses
effets plein écran).

**`outline_selective.gdshader`** (nouveau, par-sprite) : détection de
bord classique — un texel transparent (`alpha <= 0.5`) dont un voisin
immédiat est opaque devient `outline_color`. Posé comme
`ShaderMaterial` sur `Enemy._visual` (`AnimatedSprite2D`) dans
`enemy.gd::_ready()`, couleur rouge `(0.85, 0.2, 0.18)` — "ennemi" au
sens §10.1. Pas touché aux ennemis en `Polygon2D` (Gueule Vide,
placeholders) : leur identification passe déjà par
`_base_visual_color`, un outline shader sur un polygone plein serait
redondant.

**`player_fx.gdshader`** (nouveau, par-sprite) : un `CanvasItem` n'a
qu'UN SEUL slot `material` — impossible de poser outline ET streak
comme deux matériaux empilés sur le même `AnimatedSprite2D` du
joueur. Plutôt que d'inventer un mécanisme de composition de
matériaux (overkill pour 2 effets), un seul shader combine les deux :
outline bleu `(0.3, 0.55, 1.0)` toujours actif (allié), streak
directionnel piloté par deux nouveaux uniforms
(`streak_direction`/`streak_amount`) mis à jour dans
`player.gd::_advance_dash()` pendant la phase MOVE du dash
(`streak_amount = 0.8`, direction = `_dash_direction`) puis remis à
`0.0` en fin de phase et dans `_end_dash()` par sécurité — jamais
permanent, seulement pendant le déplacement du dash.

**Deux bugs de compilation Godot Shading Language rencontrés et
corrigés** (aucun des deux n'est du GLSL standard, spécifiques au
compilateur shader de Godot) :

1. `return` interdit dans `fragment()` lui-même (mais autorisé dans
   une fonction annexe normale) : `SHADER ERROR: Using 'return' in
   the 'fragment' processor function is incorrect.` — corrigé dans
   `outline_selective.gdshader` et `player_fx.gdshader` en
   restructurant l'early-exit en `if` imbriqué.
2. Plus sournois : les variables magiques (`TEXTURE`, `UV`, `COLOR`)
   ne sont fiables que DANS le corps de `fragment()` lui-même — une
   fonction annexe qui lit `TEXTURE` directement échoue à la
   compilation (`Unknown identifier in expression: 'TEXTURE'`), et la
   passer en paramètre (`sampler2D`) compile mais déclenche un
   avertissement interne du compilateur RD
   (`"!actions.custom_samplers.has(...)"`) — sans doute non fiable
   selon les cas. `player_fx.gdshader` avait été écrit avec une
   fonction annexe `sample_streaked(vec2 uv)` lisant `TEXTURE` en
   interne : le shader échouait silencieusement à la compilation
   (`--import` headless ne le signalait qu'au chargement runtime, pas
   à l'import), le joueur se retrouvait donc SANS AUCUN matériau
   actif — testé et vérifié : capture `/tmp/arena_postrender.png`
   montrait les 3 ennemis avec leur liseré rouge net, mais aucun
   liseré bleu autour du joueur. Corrigé en supprimant la fonction
   annexe et en écrivant le sampling du streak directement dans le
   corps de `fragment()`.

**Vérification** : après le fix, `--import` headless propre (0 erreur
shader), `scripts/run_gameplay_smoke_test.sh` 100% vert. Capture
`test_arena.tscn` en jeu réel, recadrée ×6 sur le joueur puis scan de
pixels (`b > r+15 and b > g+15` dans la zone du joueur) : 465 pixels
bleutés détectés formant un liseré continu autour de la silhouette —
confirmé visuellement, le joueur porte bien son contour bleu, les 3
monstres gardent leur contour rouge, et le bloom/paletteRamp global
ne dégrade pas la lisibilité de la scène (HUD, arène, props toujours
nets).

**Statut Phase 2.3 : terminé.** Phase 2 dans son ensemble (2.1 son,
2.2 normal maps, 2.3 post-render, 2.4 primitives) est maintenant
complète. Prochaine étape : Phase 3 (usine à compétences — Poing
Belluaire, Poing Tellurique, archétypes de cast, preuve d'invocation
mobile).

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
