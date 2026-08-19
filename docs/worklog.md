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
