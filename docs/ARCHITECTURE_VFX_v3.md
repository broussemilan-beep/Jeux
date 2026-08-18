# Architecture Animation & VFX Premium — Document de référence pour Claude Code (v3)

**Projet : Rank Zero**

> v3 remplace intégralement v2. Corrections : contradiction moteur résolue (Godot, plus aucun JS), résolution native et conventions fixées, juge qualité défini, mesures automatisables chiffrées, roadmap réécrite en tranche verticale, capture Playwright remplacée par capture Godot headless.

Transcrit tel quel depuis le PDF source `vfxarchitecturev3.pdf` (22 pages) fourni par Milan le 2026-08-18, pour que ce document — le cerveau du projet — vive dans le dépôt et pas seulement dans un upload de session. Aucune reformulation de contenu ; mise en forme Markdown seulement.

---

## 0. Décisions verrouillées

Ces décisions sont prises. Claude Code ne les rediscute pas ; toute exception passe par le directeur de projet (Milan).

| Décision | Valeur |
|---|---|
| Moteur | **Godot 4.3+** — export natif mobile (pas d'export web : le web Godot force le renderer Compatibility, qui casse les GPUParticles) |
| Renderer | **Mobile** (Vulkan/Metal), fixé dans Project Settings dès le premier commit |
| Langage | **GDScript** pour tout le runtime. Python uniquement pour les scripts de pipeline hors moteur |
| Données | Recettes, palettes, manifests, labels = **JSON** texte lisible, un fichier par objet |
| Résolution native | **640×360**, upscale entier uniquement (×2 = 720p, ×3 = 1080p), filtre Nearest, mipmaps désactivés |
| Logique | **60 ticks/s**. Toutes les durées d'animation/VFX s'expriment en ticks (1 tick ≈ 16,6 ms) |
| Tailles de canvas | Perso jouable & ennemis standard : **64×64** (corps ~44–52 px de haut). Élites : 96×96. Boss : 128×128+. VFX : 48, 96 ou 192 selon `importanceTier` |
| Capture | **Godot headless** (`--headless` + script de capture, ou Movie Maker `--write-movie`), jamais Playwright |
| Juge qualité | Gates automatiques (scripts) pour tout ce qui est mesurable + **verdict humain versionné** pour l'artistique. Aucun juge IA visuel (interdit — instabilité démontrée sur projet précédent) |
| Stratégie de production | **Tranche verticale d'abord** : 1 personnage, animations de base + 1 compétence complète, validés au seuil de référence par Milan, AVANT toute généralisation |

## 1. Mandat

Ce document ne définit **ni le système de combat, ni les pouvoirs, ni le lore, ni les classes** du jeu.

Il définit l'architecture technique et artistique permettant de produire des animations et VFX premium — lecture immédiate, mouvement nerveux, impact lourd, silhouettes mémorables — sous trois contraintes non négociables :

1. **Claude Code est l'unique exécutant technique** (il tournera en mode Sonnet : chaque fichier doit être petit, autonome, lisible, et chaque tâche doit être bornée — voir section 16).
2. **Le repo GitHub est le cerveau et le stockage.** Aucune décision, recette, palette, seed ou verdict qualité ne doit exister ailleurs que dans un fichier versionné.
3. **Le jeu tourne sur téléphone.** Chaque règle esthétique est filtrée par ce qu'un GPU mobile (Adreno, Mali, Apple A-series) tient à 60 fps sans surchauffe.

Références à étudier comme principes, jamais à copier : Dead Cells (pose-to-pose, anticipation, normal maps + toon shader), Hades/Hades II (couches de VFX, silhouettes par famille), CrossCode (lisibilité pixel), Vlambeer (impact frame, screenshake directionnel, knockback), guide VFX interne de League of Legends (hiérarchie primaire/secondaire, bandes de valeur, ordre clarté > bruit > thème > surprise).

Hades a demandé plus de 32 000 frames FX dessinées à la main : ce volume est remplacé ici par une architecture qui **réutilise, compose et paramètre** des briques visuelles au lieu de multiplier des assets uniques.

## 2. Objectif visuel mesurable

Une animation ou un VFX est accepté seulement s'il réussit les six tests suivants. Chaque test précise **comment il est mesuré** (auto = script, humain = verdict versionné de Milan).

1. **Lisible en une demi-seconde** — le joueur distingue début, danger, conséquence. *(humain, sur capture standardisée)*
2. **Silhouette identifiable sans couleur** — capture convertie en aplat noir : l'action reste reconnaissable. *(auto pour la génération de la capture silhouette ; humain pour le verdict)*
3. **Énergie directionnelle** — lignes, débris, trails et shake indiquent d'où part l'action et où elle finit. *(humain)*
4. **Hiérarchie claire** — personnage/ennemi > hitbox/danger > VFX secondaire > décor. *(auto partiel via bandes de valeur, section 3 ; humain pour le reste)*
5. **Image distincte** — deux pouvoirs ne deviennent jamais la même explosion recolorée. Toute nouvelle famille modifie au moins 3 dimensions parmi : forme primaire, matière, comportement de dissolution, palette, profil de feedback. *(auto : diff des champs de recette ; humain pour l'impression finale)*
6. **Correspondance hitbox/visuel** — écart max 8 %. Mesure automatique définie ainsi : sur les frames de la fenêtre de contact, calculer le masque alpha pondéré par opacité de l'effet, en extraire le rayon effectif (rayon du cercle centré sur le centroïde contenant 90 % de la masse d'opacité), comparer au rayon (ou demi-largeur) de la hitbox réelle. `abs(r_visuel - r_hitbox) / r_hitbox <= 0.08`. Pour les zones non circulaires, comparer les bbox sur chaque axe avec la même tolérance. *(auto : `scripts/check_hitbox_match.py`)*

Le pixel art n'est pas une contrainte de basse qualité : peu de couleurs par asset, formes franches, mais couches de rendu et comportement temps réel sophistiqués.

### 2.1 Hiérarchie primaire/secondaire par effet

Chaque effet a un élément **primaire** (porteur du signal gameplay : point focal, forte valeur, silhouette nette, opacité élevée) et un ou plusieurs éléments **secondaires** (thème/flavor : valeur basse, forme simple, faible opacité). Ordre de priorité en cas de conflit : clarté > minimisation du bruit > renforcement thématique > surprise.

## 3. Bandes de valeur et conventions chromatiques (chiffrées)

Les bandes ci-dessous sont les **valeurs initiales**, stockées dans `data/palettes/value_bands.json` et vérifiées par `scripts/validate_pixels.py`. Elles sont ajustables uniquement via ce fichier, jamais en dur dans le code.

| Catégorie | Bande de valeur (V en HSV, %) | Notes |
|---|---|---|
| UI | 0–12 et 94–100 | Seule catégorie autorisée aux extrêmes |
| Personnages / ennemis | 15–88 | Outline sombre autorisé jusqu'à 13 |
| VFX | 20–92 | Jamais 0 % ni 100 % — collision UI/décor |
| Décor | 15–60 | Le décor ne dépasse jamais la valeur d'un VFX actif |

Règles complémentaires :

- **Convention ami/ennemi verrouillée** : indicateurs alliés = bleu, indicateurs ennemis = rouge. Non contournable par les familles de pouvoirs.
- **Palettes analogiques par défaut.** Si deux couleurs complémentaires coexistent dans un effet, l'une est démotée en rôle secondaire (intensité et surface réduites).
- Chaque VFX possède au maximum 5 rôles de couleur : contour/masse sombre, corps, vif, pic/highlight (rare), résidu. Aucun gradient peint : les gradients viennent du shader `paletteRamp`.

## 4. Architecture en huit couches

1. **BODY** : animation/silhouette du personnage, ennemi ou invocation
2. **ANTICIPATION** : pose, tension, flash d'arme, sol qui se creuse, cible qui réagit
3. **ACTION CORE** : forme principale du coup, projectile, rayon, zone ou invocation
4. **TRAIL** : trajectoire, ruban, smear, afterimage, fragments en vitesse
5. **CONTACT** : impact, flash blanc, croissants, sparks, poussière, recul de la cible
6. **CONSEQUENCE** : statut, zone résiduelle, fissure, marque, débris + dissipation
7. **FEEDBACK** : hit-stop, shake, freeze, chroma offset limité, son, rumble
8. **POST-RENDER** : bloom, éclairage, color grading, vignette, distortion (1 passe globale/frame)

Chaque couche est activable/désactivable en mode debug, avec capture isolée par couche.

- **CONTACT — recul obligatoire** : tout coup qui touche une cible inclut un sous-composant `recoil` visible, même léger. Le shake de caméra suit la direction opposée à l'attaque (horizontal pour une frappe horizontale, vertical pour un slam), jamais un bruit isotrope.
- **CONTACT — flash blanc première frame** : primitive `impactFlashFrame` — noyau blanc quasi-plein (≤ 92 % de valeur), 1–2 ticks, affiché avant le corps de l'effet. Distincte d'`impactStar`.
- **CONSEQUENCE — dissipation = phase à part** : chaque recette porte un champ `dissipationProfile` (valeur, saturation, opacité réduites vs corps principal) avec budget de rémanence cumulée **par zone d'écran**, pas seulement par effet (section 8.2).

## 5. Pipeline de production hybride

### 5.1 Outils et rôles

| Outil | Rôle exclusif | Ne pas l'utiliser pour |
|---|---|---|
| PixelLab (tier 1) | silhouettes inédites, poses de personnages, entités, animations anatomiques de base | générer des particules ou des variations mineures |
| Pixel Composer | composition node-based, simulations, fluides stylisés, exports d'atlas VFX | l'animation expressive d'un personnage entier |
| Procédural runtime (GDScript) | trails, débris, poussière, sparks, ondes, fissures, glyphes, afterimages, variations seedées | simuler une silhouette complexe qu'un sprite dédié rendrait plus lisible |
| Aseprite / scripts Lua | corrections palette, pivots, layers, découpe/atlas, batch export | fabrication manuelle de centaines de variations |
| Python | bbox alpha, palette indexing, validation, atlas, metadata, manifests, checks hitbox | décisions artistiques |
| Shaders Godot (Mobile) | `paletteRamp`, bloom emissive, normal-lighting, dissolve, outline, distortion — 1 passe globale/frame | dessiner la silhouette principale d'un VFX |

### 5.2 Règle de décision

```
Anatomie/pose reconnaissable nécessaire ?
  → Oui : PixelLab, puis nettoyage/palette/atlas.
  → Non : composition de particules, fumée, énergie, flux, fragments ?
        → Oui : Pixel Composer, export spritesheet, post-traitement.
        → Non : variation temps réel possible (ligne, poussière, trail, onde) ?
              → Oui : procédural runtime.
              → Non : sprite frame-by-frame minimal, validé par key poses.
```

Aucun appel PixelLab pour une variation que Pixel Composer ou le runtime peuvent dériver d'une forme existante.

### 5.3 Discipline PixelLab (tier 1 = crédits limités)

- **Cohérence du personnage obligatoire** : toute génération d'animation ou de pose d'un personnage existant part de son image de référence canonique (`assets/source/pixellab/<perso>/reference.png`) via le workflow reference-image de PixelLab. Jamais de génération "de mémoire" du prompt seul.
- **Journal d'usage** : chaque appel est loggé dans `data/pixellab_usage.jsonl` (date, prompt, but, asset produit, accepté/rejeté). Avant tout batch > 5 appels, Claude Code présente l'estimation à Milan.
- Un asset PixelLab rejeté est archivé dans `assets/source/pixellab/_rejected/` avec la raison — jamais supprimé, jamais re-généré à l'identique.

## 6. Animation premium : pose-to-pose avant fluidité

### 6.1 Standard de frames (en poses, pas en interpolations)

```
IDLE      : 2 à 6 frames + micro-mouvement procédural (bob de pivot, pas de redraw)
WIND-UP   : 1 à 3 poses lisibles
RELEASE   : 1 pose d'action très forte
IMPACT    : 1 impact frame prioritaire
RECOVERY  : 1 à 3 poses
SMEAR     : 1 frame optionnelle, uniquement à très grande vitesse
```

Pas d'interpolation linéaire entre poses : ça casse le pixel art et affaiblit le mouvement. Valider le mouvement avec le minimum de poses avant d'ajouter des in-betweens ciblés (jamais automatiques). Sur mobile, moins de frames = moins de mémoire ; le pixel art tolère très bien 4 frames là où le réalisme en demanderait 8.

### 6.2 Time warping (en ticks à 60/s)

```
anticipation : 25 à 40 % du temps total
release      : 5 à 12 %
impact hold  : 0 à 2 ticks + hit-stop global
recovery     : 35 à 55 %
```

La vitesse perçue vient du **contraste temporel**, pas du nombre de frames. Un timing non linéaire est systématiquement plus percutant qu'un timing linéaire équivalent.

### 6.3 Conventions techniques (verrouillées)

- **Pivot** : bas-centre du canvas pour tout perso/ennemi (pieds au sol). VFX : pivot = point d'origine logique de l'effet, déclaré dans le manifest.
- **Nommage frames** : `<entité>_<action>_<index>` (ex. `hero_dash_02`). Une action = une ligne d'atlas.
- **Métadonnées par animation** (dans le manifest) : durée de chaque frame en ticks, frames d'anticipation/release/impact/recovery taguées, fenêtre de hitbox active, markers SFX.
- **Direction** : sprites dessinés face droite, flip horizontal runtime pour la gauche. Toute asymétrie visuelle importante (arme, cicatrice) est validée par Milan avant production.

### 6.4 Smears et silhouettes d'action

Bibliothèque de smears réutilisables : arc de lame/poing, capsule de dash, triangle de projectile rapide, masse écrasée/slam, éventail de fragments, ruban sinueux, lignes de tension.

Chaque smear : 1 frame, palette limitée, **pas de blur alpha peint** — il exagère la direction, jamais ne cache la pose finale. Le flou de mouvement réel passe uniquement par le shader `directionalStreak` (section 10) : des particules rapides sans flou directionnel se lisent comme des sauts de frame, pas comme de la vitesse.

## 7. VFX premium : bibliothèque de primitives recombinables

`src/vfx/primitives/` — **une primitive = un fichier GDScript autonome**, jamais un module monolithique.

### 7.1 Primitives de forme (15)

```
arcSlash          croissant anguleux directionnel
impactStar         étoile/éclat central asymétrique
impactFlashFrame   flash blanc quasi-plein, 1-2 ticks, avant le corps de l'effet
groundRing         anneau au sol cassé ou incomplet
fractureLine       fissure segmentée qui progresse
ribbonTrail        ruban de vitesse contrôlé par vélocité
shardBurst         fragmentation orientée
converge           fragments qui reviennent vers une cible
spiral             rotation/aspiration
beamSegment        rayon discret en segments
runicStamp         glyphe/empreinte de sol
smokePuff          nuage stylisé sans transparence floue
dustKick           poussière au contact sol
orbital            instances autour d'une ellipse seedée
screenSlash        coupe écran locale/flash directionnel limité
```

Chaque primitive reçoit : `seed`, palette, durée (ticks), direction, échelle, origine, courbe temporelle, `overdraw_cost` estimé.

```gdscript
VfxDirector.spawn("shardBurst", {
    "seed": seed,
    "origin": origin,
    "direction": dir,
    "palette": "cold_arcane",
    "intensity": 0.7,
    "lifetime_ticks": 13,
    "count": 14,
    "overdraw_cost": 0.4,
})
```

### 7.2 Matières (9)

```
crystal  : éclats nets, rebonds courts, lignes brillantes
ash      : grains légers, montée lente, dispersion sèche
ink      : masses irrégulières, tirage, gouttes fragmentées
paper    : bandes/feuillets, plis, rotation lente
glass    : pointes, cassures, scintillement discret
root     : segments qui poussent, bifurcations, copeaux
metal    : étincelles dures, ricochets, poussière lourde
mist     : plaques/cellules, pas de blur libre
starlight: points rares, convergence, traînées fines
```

Une recette VFX est **forme + matière + temps + palette + feedback**, jamais un PNG figé.

## 8. Architecture des recettes VFX

### 8.1 Schéma de données — `data/recipes/<id>.json`

```json
{
  "id": "power.example.impact.t3",
  "family": "impact",
  "importance_tier": 3,
  "layers": [
    { "type": "anticipation", "primitive": "groundRing",       "start_tick": 0 },
    { "type": "contact",      "primitive": "impactFlashFrame", "start_tick": 4 },
    { "type": "core",         "primitive": "impactStar",       "start_tick": 4 },
    { "type": "trail",        "primitive": "ribbonTrail",      "start_tick": 3 },
    { "type": "contact",      "primitive": "shardBurst",       "start_tick": 6 },
    { "type": "consequence",  "primitive": "fractureLine",     "start_tick": 7 }
  ],
  "dissipation_profile": { "value_mult": 0.5, "saturation_mult": 0.5, "opacity_mult": "…" },
  "palette_id": "power_unique_palette",
  "feedback": "heavy",
  "sfx_markers": [ { "tick": 4, "event": "impact_main" } ],
  "limits": { "particles": 42, "sprites": 8, "persistent_ticks": 33, "overdraw_budget": "…" }
}
```

`importance_tier` : 1 (idle/utilitaire) → 6 (ultime). Chaque palier augmente taille, saturation, opacité et intensité de mouvement autorisées, pour qu'un ultime ne ressemble jamais à une attaque de base. Le tier pilote aussi la taille de canvas VFX (48/96/192).

### 8.2 `VfxDirector` (GDScript, runtime)

Le `VfxDirector` :

- résout recette + palette + seed ;
- impose des budgets de particules/sprites/**overdraw estimé** par action ET par zone d'écran (grille 4×3 sur le viewport 640×360) ;
- fusionne les instances secondaires proches ;
- abaisse le LOD des VFX distants ;
- centralise le cleanup (timeout, mort, changement de scène) ;
- journalise seed + recette de chaque spawn pour replay et capture ;
- expose un mode debug par couche.

Sur mobile, le goulot n'est presque jamais le nombre de particules mais l'**overdraw** (pixels redessinés par blending additif superposé — jusqu'à 50–100× sur une grosse explosion). Plafonds initiaux : 50–200 particules par effet, 2000 simultanées à l'écran. `VfxBudget.gd` calcule un coût d'overdraw estimé (taille × opacité × couches superposées), pas un simple compte de particules.

```
src/vfx/
  vfx_director.gd
  vfx_budget.gd
  vfx_recipe_registry.gd
  vfx_capture_debug.gd
  primitives/         # 1 fichier .gd par primitive
  materials/          # 1 fichier .gd par matière
data/
  recipes/            # 1 fichier .json par recette
  palettes/           # value_bands.json + 1 .json par palette
  labels/             # quality_labels.jsonl (verdicts humains)
  pixellab_usage.jsonl
```

## 9. Feedback de combat haut de gamme

### 9.1 Hit-stop — 5 profils (alignés sur les 5 niveaux)

| Profil | Usage | Valeur initiale |
|---|---|---|
| none | déplacement, tir léger, utilitaire | 0 ms |
| light | hit rapide confirmé | 12 ms |
| medium | compétence, projectile lourd, garde brisée | 25 ms |
| heavy | finisher, slam, attaque de boss | 45–65 ms |
| catastrophic | événement exceptionnel uniquement | 75–95 ms |

Le freeze conserve les particules déjà nées et stoppe seulement ce qui vend le poids du coup ; il ne gèle jamais l'UI ni le son de façon incohérente. Implémentation : time scale local aux nœuds de combat, pas `Engine.time_scale` global (sinon l'UI gèle aussi).

### 9.2 Camera shake

```
light  : 1 px, 4 ticks
medium : 2 px, 5 ticks
heavy  : 3-5 px, 7 ticks
```

Courbe de retour obligatoire, jamais de bruit aléatoire isotrope. Direction du shake = opposée à l'attaque.

### 9.3 Séquence d'impact complète (tout impact majeur)

1. `impactFlashFrame` (1–2 ticks) ;
2. silhouette secondaire (`impactStar`, croissant, éclat) ;
3. fragments directionnels (`shardBurst`) ;
4. **recul visible de la cible** (`recoil`), même sur coup léger ;
5. conséquence au sol/à la cible si pertinente ;
6. hit-stop + SFX synchronisés via `sfx_markers`.

## 10. Post-render et shaders (contraintes mobile intégrées)

Le post-render **amplifie** les assets, jamais ne les sauve. Sur GPU mobiles tile-based (Apple A-series, Adreno, Mali), toute passe render-to-texture (bloom, blur, distortion) coûte une écriture mémoire hors puce : chaque passe supplémentaire se paie cash.

### 10.1 Shaders à prévoir

```
paletteRamp       : verrouille les couleurs finales sur rampes autorisées
emissiveBloom     : bloom uniquement sur masque emissive — 1 passe globale/frame
outlineSelective  : outline par équipe (bleu allié / rouge ennemi), danger, cible
normalLight       : éclairage discret via normal map optionnelle (persos/props premium)
dissolvePixel     : dissolution à motif pixel/seed, jamais alpha fade simple
heatDistort       : distorsion localisée, basse amplitude — 1 passe globale/frame
screenSlice       : bandes décalées, très limité
impactFlash       : flash local/radial, borné dans l'espace et le temps
directionalStreak : flou directionnel post-render pour objets rapides, jamais permanent
```

**Règle mobile impérative** : `emissiveBloom`, `heatDistort` et `screenSlice` = une seule passe de post-render globale par frame, jamais une passe par VFX.

Normal maps + toon shader façon Dead Cells : réservé aux personnages/ennemis/props premium, ajouté seulement si les captures sur device réel justifient le coût (décision Phase 2, jamais imposé à tous les VFX).

### 10.2 Règles de sécurité visuelle

- Aucun bloom permanent sur chaque projectile.
- Aucun shake sur les actions utilitaires.
- Aucun glitch universel pour masquer une absence de direction artistique.
- Aucun dissolve par alpha fade seul : toujours une logique de retrait (fragments, aspiration, cendre, pixels, lignes).
- Aucun trail opaque qui masque ennemis ou hitbox.
- Les VFX de danger ennemi ont priorité de contraste sur les VFX décoratifs alliés.
- Aucune valeur VFX à 0 % ou 100 % (section 3).

## 11. Exécution mobile réelle

### 11.1 Renderer et particules

Le renderer **Compatibility ne supporte pas les GPUParticles** (les particules disparaissent silencieusement, sans erreur). Le renderer **Mobile** est fixé dès le premier commit ; c'est lui qui détermine quelles primitives tournent en GPU particles vs sprites animés.

Diagnostic si des particules restent invisibles sur device : vérifier `OS.get_current_rendering_method()` sur l'appareil réel, confirmer que le `ParticleProcessMaterial` n'est pas nul, réduire `amount` à 10 pour isoler une limite mémoire GPU, lire `adb logcat` (Android).

### 11.2 Atlas et draw calls

Un atlas mal packé peut faire chuter un 2D mobile de 60 à ~38 fps (binds de texture répétés). Règles :

- packing MaxRects, taille max 2048, padding 2 px, power-of-two ;
- atlas séparés par contexte de chargement (personnages, VFX, UI, décor), chargés/déchargés par zone ;
- compression **ETC2 RGBA8** (Android) / **ASTC 6×6** (iOS) — activer `textures/vram_compression/import_etc2_astc` ; filtre **Nearest**, mipmaps off ;
- indexation de palette (1 octet/pixel) quand possible : −75 % de mémoire sprite.

### 11.3 Test sur device réel

Les simulateurs ne reproduisent ni le GPU réel, ni le throttling thermique, ni la pression mémoire. Boucle de test :

- **iPhone (device principal de Milan)** : export iOS via Xcode sur le Mac. Le provisioning gratuit (Apple ID, sans compte développeur payant) suffit pour installer des builds de test.
- **Android bas/moyen de gamme** si un appareil est disponible : `adb install` + `adb logcat`.
- La validation périodique se fait sur device, pas seulement en éditeur.

## 12. Pipeline d'asset, automatisation et repo GitHub

### 12.1 Dossiers

```
assets/
  source/
    pixellab/<perso>/reference.png + générations
    pixellab/_rejected/
    pixel-composer/         # graphes .pcg versionnés (texte)
    hand/
    external-licensed/
  staging/
  processed/
    sprites/
    vfx/
    normalmaps/
    atlases/
  manifests/

scripts/
  ingest_asset.py
  alpha_bbox.py
  quantize_palette.py
  validate_pixels.py      # palette + bandes de valeur (section 3)
  check_hitbox_match.py   # mesure 8% (section 2, test 6)
  build_atlas.py
  build_metadata.py
  compare_reference.py    # diff pixel vs capture de référence approuvée
  capture_headless.sh     # lance Godot --headless + scène de capture
  audit_manifest.py
```

### 12.2 Repo comme cerveau de Claude Code

Chaque recette, primitive, palette, manifest et verdict qualité reste un **fichier texte lisible** (JSON/GDScript), jamais un binaire opaque. Une primitive = un fichier, une recette = un fichier. Aucun fichier monolithique.

### 12.3 Git LFS — avec gestion du quota

Les binaires (sprites finaux, atlas PNG, normal maps) passent par **Git LFS**, jamais en Git classique.

```
git lfs install
git lfs track "assets/processed/**/*.png" "assets/source/**/*.png"
git add .gitattributes
git commit -m "LFS attributes"
```

**Attention quota** : GitHub LFS gratuit = ~1 Go de stockage et ~1 Go de bande passante/mois, vite dépassé par des itérations d'atlas. Discipline :

- seuls les assets **acceptés** vont dans `processed/` (LFS) ; les itérations rejetées restent locales ou dans `_rejected/` compressé ;
- pas de re-commit d'un atlas régénéré à l'identique (comparer le hash avant commit) ;
- si le quota approche, alerter Milan (options : data pack GitHub, ou déplacer `source/` hors LFS).

`.gitignore` exclut tout contenu reconstructible (`.godot/`, caches d'atlas temporaires).

### 12.4 Pipeline obligatoire par asset

```
source asset
  → sauvegarde immutable + manifest
  → alpha/bbox/crop
  → nearest-neighbor resize si nécessaire
  → quantification palette stricte
  → validation : pas d'anti-aliasing/flou/transparence interdite, bandes de valeur
  → pivot/hitbox/frames metadata
  → atlas (packé par contexte)
  → import moteur (renderer Mobile, ETC2/ASTC, Nearest, no mipmaps)
  → capture headless à seed fixée
  → comparaison avec capture de référence approuvée
  → check hitbox/visuel (écart max 8 %)
```

### 12.5 Manifest

```json
{
  "asset_id": "vfx_arc_crystal_t3_v1",
  "kind": "vfx",
  "source": "pixel-composer",
  "source_graph": "assets/source/pixel-composer/arc_crystal_t3.pcg",
  "recipe": "arcSlash + crystal + converge",
  "palette_id": "crystal_blue_white",
  "importance_tier": 3,
  "overdraw_cost": 2.1,
  "license": "internal",
  "seed": 44102,
  "frames": 6,
  "cell": [96, 96],
  "pivot": [48, 88],
  "frame_ticks": [3, 2, 2, 2, 3, 4],
  "processed_path": "assets/processed/vfx/vfx_arc_crystal_t3.png",
  "validated_auto": true,
  "human_label_ref": "labels/quality_labels.jsonl#L42"
}
```

`validated_auto` = tous les gates scripts passent. Un asset n'est **jamais** considéré final sans `human_label_ref` pointant vers un verdict humain positif (voir section 13).

## 13. Qualité : gates automatiques + juge humain versionné

### 13.1 Principe (leçon du projet précédent, non négociable)

Les juges IA visuels sont **interdits** : sur un projet antérieur, un modèle vision a produit des scores instables sur entrée identique, sensibles au fond de capture, avec inversions de signe. Les deux seuls juges stables sont :

1. **Gates automatiques déterministes** (scripts Python) pour tout ce qui est mesurable : palette, bandes de valeur, alpha, hitbox 8 %, budgets, seed-reproductibilité, cleanup.
2. **L'œil de Milan** sur captures standardisées pour l'artistique.

### 13.2 Verdicts humains versionnés — `data/labels/quality_labels.jsonl`

Une ligne JSON par verdict :

```json
{ "capture_id": "hero_attack1_seed44102_v3", "asset_id": "hero_attack1_v3", "verdict": "…" }
```

Règles :

- Claude Code **ne s'auto-attribue jamais** un verdict humain et ne marque jamais un asset final sans label positif.
- Un `reject` inclut toujours une raison exploitable ; la version suivante référence le label qu'elle corrige.
- Les captures soumises au verdict sont **standardisées** : fond neutre + fond chargé, 1×/2×/4×, seed fixée, mêmes conditions d'éclairage shader.

### 13.3 Capture automatisée (remplace Playwright)

- Scène de capture dédiée `tools/capture_scene.tscn` : charge une recette/animation, seed fixée, joue, exporte les frames en PNG (`get_viewport().get_texture().get_image().save_png()`), ou séquence complète via Movie Maker (`--write-movie`).
- Lancée par `scripts/capture_headless.sh` (Godot `--headless`).
- Chaque capture est nommée `<asset>_<seed>_<version>` et référencée dans le manifest.
- `compare_reference.py` diffe pixel à pixel contre la dernière capture **approuvée par label humain** — c'est ainsi que naît une "image de référence" : c'est toujours une capture ayant reçu un verdict `accept` de Milan, jamais une image choisie par la machine.

### 13.4 Tests automatisés (gates)

- seed fixe → même sortie / même capture ;
- budgets : particules, overdraw, rémanence cumulée par zone d'écran ;
- cleanup : destruction au timeout, à la mort, au changement de scène ;
- palette : aucune couleur hors palette, aucune valeur hors bande (section 3) ;
- alpha : pas de bord semi-transparent non voulu ;
- lisibilité : génération auto de la capture silhouette + capture taille native (verdict humain ensuite) ;
- hitbox/visuel : écart max 8 % (méthode section 2) ;
- stress : spam d'action sans fuite d'objets, timers, trails ou audio ;
- device réel : validation périodique sur téléphone, pas seulement en éditeur.

### 13.5 VFX Lab (écran laboratoire obligatoire)

- sélection recette, matière, palette, seed ;
- timeline tick par tick ;
- réglage de chaque couche, overlay hitbox/pivots ;
- affichage des budgets (particules, overdraw, persistance cumulée par zone) ;
- fond clair/sombre/chargé, preview 1×/2×/4× ;
- export capture + metadata en un clic.

## 14. Audio (minimal mais présent dès la tranche verticale)

Le feedback exige un son synchronisé ; le pipeline audio minimal est donc :

- SFX en `.wav` courts, mono, 44,1 kHz, dans `assets/processed/sfx/`, référencés par les `sfx_markers` des recettes ;
- bus Godot dédiés : `Master > SFX_Combat`, `Master > SFX_UI`, `Master > Music` — le hit-stop ne coupe jamais le bus Music ;
- en phase prototype, des SFX placeholder (générateurs 8-bit type sfxr, ou banques libres de droits documentées dans le manifest avec leur licence) sont acceptés ; le remplacement premium est une phase ultérieure ;
- règle anti-fatigue : toute action répétable a ≥ 2 variantes de SFX avec pitch aléatoire léger (±5 %).

## 15. Roadmap — tranche verticale d'abord

> Objectif de la tranche verticale : atteindre le **seuil de référence** validé par Milan sur UN personnage (animations de base) + UNE compétence complète. Rien n'est généralisé avant ce verdict. C'est le remède au pattern "usine préparée, jamais intégrée".

### Phase 0 — Fondations minimales (pas l'usine complète)

1. Projet Godot 4.3+, renderer Mobile, viewport 640×360 upscale entier, Nearest, ETC2/ASTC.
2. Repo + Git LFS + `.gitignore` + arborescence (sections 8.2 et 12.1).
3. `VfxDirector` + `VfxBudget` squelettes (spawn, seed, cleanup, budgets simples).
4. Scène de capture headless + `quality_labels.jsonl` + 3 scripts seulement : `validate_pixels.py`, `check_hitbox_match.py`, `compare_reference.py`.
5. **Definition of done** : une primitive de test s'affiche, capturée en headless, seed reproductible, gates verts.

### Phase 1 — Tranche verticale (LE livrable)

1. Personnage de test via PixelLab (reference.png canonique d'abord, validée par Milan).
2. Animations de base : idle, déplacement, dash, hurt, mort — pose-to-pose, conventions section 6.
3. Combo léger de base : **attaque 1 → attaque 2 → attaque 3** chaînées, avec fenêtre de chaînage (input buffer sur les derniers ticks de chaque RECOVERY) et une variation de pose/trajectoire par coup — pas 3 fois la même animation. Chaque coup suit le standard de frames de la section 6.1 et porte son propre `impactFlashFrame` + `recoil`.
4. UNE compétence complète (distincte du combo) : les 8 couches, avec **seulement les 4–6 primitives qu'elle exige** (obligatoirement `impactFlashFrame` + `recoil` inclus), 1 matière, 1 palette, 1 profil de feedback.
5. SFX placeholder synchronisés via markers, avec variantes de pitch par coup du combo (section 14).
6. Boucle d'itération : capture standardisée → verdict Milan dans `quality_labels.jsonl` → correction → recapture. Autant de tours que nécessaire.
7. **Definition of done** : Milan pose un `accept` sur le personnage animé, sur le combo ET sur la compétence, sur device réel (iPhone). Ces captures deviennent les références qualité du projet entier.

### Phase 2 — Généralisation de l'usine

1. Compléter les 15 primitives, les 9 matières, les 5 profils de feedback.
2. VFX Lab complet, pipeline Python complet (atlas, manifests, audit).
3. Étendre le set d'animations du personnage : attaque lourde, impact, compétences supplémentaires.
4. Normal maps + toon shader : décision sur captures device réel, persos premium uniquement.

### Phase 3 — Familles visuelles

1. Trois familles visuelles très différentes avec les mêmes primitives.
2. Chaque famille : palette analogique, contour, matière dominante, dissolution, profil de feedback, `importance_tier` cohérent.
3. Recolorisation seule interdite : une nouvelle famille modifie au moins 3 dimensions.

### Phase 4 — Exports Pixel Composer / PixelLab à l'échelle

1. Graphes Pixel Composer versionnés et documentés.
2. Silhouettes/poses PixelLab strictement nécessaires (discipline section 5.3).
3. Toute sortie absorbée par le pipeline automatisé, atlas par contexte.
4. Les meilleurs exports deviennent de nouvelles primitives/recettes réutilisables.

## 16. Instructions d'exécution pour Claude Code (mode Sonnet)

Claude Code tournera en Sonnet pour économiser les tokens. Conséquences opérationnelles :

1. **Une brique à la fois.** Chaque session vise UN livrable borné (une primitive, un script, une animation). Jamais "implémenter la section 8" en une passe.
2. **Lire avant d'écrire.** Avant toute modification, lire le fichier cible et son manifest/recette associé. Ne jamais régénérer un fichier existant de mémoire.
3. **Vérifier avant de déclarer fini.** Un livrable est fini quand : gates scripts verts + capture headless produite + entrée manifest à jour. Le déclarer avant = interdit. (Un projet précédent a accumulé des systèmes "préparés mais jamais branchés" — chaque brique doit être branchée et prouvée par capture avant de passer à la suivante.)
4. **Jamais de verdict artistique auto-attribué.** Si un choix est artistique (pose, timing perçu, lisibilité), produire la capture et attendre le label de Milan.
5. **Journal de session.** Fin de session : mettre à jour `docs/worklog.md` (fait / branché ou non / prochain pas). C'est la mémoire inter-sessions — le repo est le cerveau.
6. **Pas d'initiative de scope.** Aucun système de combat, pouvoir, classe ou lore ne naît de ce document. Les directives de contenu arrivent séparément (préparées par Claude, validées par Milan).

## 17. Checklist de validation premium

- Une pose de préparation est visible.
- L'action a une direction sans ambiguïté.
- L'impact possède une frame dominante (`impactFlashFrame` + silhouette secondaire).
- Un recul visible existe sur la cible touchée.
- La conséquence/dissipation ne concurrence pas le danger principal.
- La palette est limitée, analogique, et respecte les bandes de valeur chiffrées (section 3).
- Le VFX est lisible sur petit écran et testé sur device réel.
- Les trails n'occultent pas l'ennemi.
- La recette est seedée, budgetée (particules + overdraw + rémanence par zone) et nettoyée.
- La correspondance hitbox/visuel est vérifiée (méthode section 2, écart max 8 %).
- Manifest complet (provenance, licence, pivot, frame_ticks), binaires en LFS.
- Une capture headless standardisée existe et est référencée.
- Le verdict humain (`quality_labels.jsonl`) est positif — sinon l'asset n'est pas final.
- Variation majeure/maîtrise : forme réellement différente, pas une recolorisation.
- `importance_tier` cohérent avec la gravité gameplay réelle de l'effet.

## Instruction finale à Claude Code

Implémenter la Phase 0 puis la Phase 1 (tranche verticale) — rien d'autre. Ne créer aucun système de combat, lore, classe ou pouvoir à partir de ce document. Fixer en premier le renderer Mobile, la résolution 640×360 et Git LFS. La tranche verticale (1 personnage animé + 1 compétence complète, validés par Milan sur device réel) définit le seuil de référence de tout le jeu : l'usine complète ne se construit qu'après ce verdict.
