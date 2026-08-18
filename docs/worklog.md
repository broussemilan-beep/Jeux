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
