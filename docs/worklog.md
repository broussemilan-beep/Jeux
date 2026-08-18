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
