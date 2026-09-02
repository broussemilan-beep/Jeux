# Le sacre — trône et couronne (R6, Roblox)

Prototype isolé, sans lien avec RANK ZERO ni MyAnimeRPG — même isolation
que `experiments/r6_aerial_kick_combo/`, dont ce prototype **réutilise
telle quelle** l'infrastructure de rig déjà vérifiée (`r6_rig.py`,
`anim_engine.py`, `export_kfseq.py`, `resolve_rbxmx.py`, le rig
`RigR6.rbxmx` importé depuis GitHub — voir `rig/PROVENANCE.md` du
prototype source, provenance identique ici). Ce qui est nouveau : la
géométrie du trône/couronne/escalier (`scripts/props.py`), la
chorégraphie de montée + assise + couronnement (`scripts/choreography.py`),
le calcul de la trajectoire de la couronne (`scripts/compute_crown_track.py`),
et le rendu « premium » du lecteur HTML (matériaux, éclairage, halo).

**Retour utilisateur (2e tour)** : « Améliore le texturing fais du
premium pareil pour le rig utilise le rig r6 Roblox que je t'ai envoyé
il est mieux, et rajoute à la scène en début le perso qui monte les
marches de manière dark mais fière puis s'assoie et met la couronne et
la couronne brille. » Trois demandes distinctes traitées séparément
ci-dessous : rendu premium, escalier + montée fière, éclat de la
couronne — plus une clarification sur le rig (voir "Rig du personnage").

## Demande

« Fais une [animation] où le perso est sur un trône et met une
couronne, crée les rig 3D. » Portée précisée avec l'utilisateur avant de
commencer : animation séparée du combo de coups de pied (pas une suite
de la même séquence), trône + couronne à modéliser/riguer comme
véritables objets 3D (pas un décor de fond).

## Ce qui est livré

- `output/character_sit_and_crown.rbxmx` — `KeyframeSequence` du
  personnage (rig R6 réel, 6 segments rigides, mêmes contraintes que le
  combo de coups de pied : pas de coude/genou, Motor6D 3 DOF). Couvre
  maintenant montée d'escalier + assise + couronnement, 175 keyframes.
- `output/throne.rbxmx` — `Model` du trône + escalier (21 `Part`,
  statique, ancré).
- `output/crown.rbxmx` — `Model` de la couronne (11 `Part` : bande +
  5 pointes + 5 gemmes), dans son repère local (centre = milieu de la
  bande — voir "La couronne change de parent" plus bas).
- `output/crown_track.json` — trajectoire monde de la couronne
  (position + rotation par échantillon), pour le script de re-weld
  qu'un vrai projet Roblox doit fournir (voir plus bas).
- Lecteur HTML (scène complète, personnage + trône + couronne, résolus
  par le moteur, texturing PBR réel appliqué en direct — voir "Relief et
  micro-reflet réels dans l'animation") : https://claude.ai/code/artifact/f5c8501a-1aa3-42c7-919b-c0745532914c

## Géométrie du trône et de la couronne

Tout en `Part` Roblox (`scripts/export_model.py`), dans le **même
repère** que le personnage (studs, -Z = avant, sol = Y 0). `Color3uint8`
(RGB direct) plutôt que `BrickColor` : l'index de palette `BrickColor`
n'est pas quelque chose que je peux garantir exact de mémoire, alors
qu'un triplet RGB est sans ambiguïté — ce choix n'a pas changé.

Trône : dais, 4 pieds, siège, dossier (monte au-dessus de la tête du
personnage debout), 2 accoudoirs, bande dorée + crête en forme de
couronne (bande + 5 pointes, voir "Passage aux références visuelles
utilisateur" plus bas — remplace les 3 fleurons-boules d'origine).
Couronne : bande (Cylinder) + 5 pointes (hauteur variable, la plus haute
à l'avant) + 5 gemmes (Ball).

### Texturing réel (`Material`) — corrigé après retour utilisateur

Version précédente : volontairement **pas** de propriété `Material`,
au motif que les valeurs numériques de `Enum.Material` n'étaient pas
vérifiables hors-ligne dans ce sandbox (pas de client Roblox). Retour
utilisateur, à raison : le texturing Roblox *est* précisément
`Material`/`Decal`/`Texture` sur les `Part`, pas un choix d'éclairage
dans un lecteur maison — ce que la version précédente avait fait à la
place.

Corrigé en sourçant les vraies valeurs plutôt qu'en les devinant : le
dump d'API officiel de Roblox (`Api-Dump.json`, généré par Roblox
lui-même à chaque version pour l'outillage tiers — Rojo, rbxts, etc.)
est suivi publiquement sur GitHub par
[MaximumADHD/Roblox-Client-Tracker](https://github.com/MaximumADHD/Roblox-Client-Tracker).
Ce n'est **pas** la même catégorie que les dumps de contenu client/
serveur écartés dans `rig/PROVENANCE.md` (des assets de jeu redistribués
sans licence) : c'est de la métadonnée d'API que Roblox publie
lui-même pour que les outils tiers fonctionnent. Valeurs extraites et
vérifiées (`export_model.MATERIAL_BY_NAME`), matériau assigné par pièce
(`props.py`, champ `material`, indépendant du champ `mat` qui pilote
uniquement l'éclairage stylisé du lecteur HTML) :

| Pièces | Material Roblox |
|---|---|
| Dais, pieds | `Wood` (512) — voir "Passage aux références visuelles utilisateur", révisé depuis `Slate` |
| Siège, dossier | `Fabric` (1312) — velours, révisé depuis `Marble`/`Slate` |
| Accoudoirs, bande dorée, crête-couronne, bande/pointes de la couronne | `Metal` (1088) |
| Coussin de la couronne | `Fabric` (1312) |
| Marches (alternées) | `Slate` (800) / `Cobblestone` (880) |
| **Gemmes de la couronne** | **`Neon` (288)**, teinte rose (`GEM_PINK`) |

(Table tenue à jour au fil des tours — les couleurs/matériaux du 2e tour
ci-dessous, dans le reste de cette section, décrivent le raisonnement
d'origine sur `Material`/`Reflectance` en général, toujours valable ; la
répartition pièce par pièce a été révisée au 6e tour pour coller aux
photos de référence de l'utilisateur.)

Le choix `Neon` sur les gemmes n'est pas arbitraire : ça relie le
texturing réel à la demande « la couronne brille » (voir plus bas) —
`Neon` émet une lueur nativement dans le moteur Roblox, sans avoir
besoin d'un `PointLight` séparé, donc l'effet de brillance existe
maintenant **aussi dans le fichier livré**, pas seulement dans le
lecteur HTML.

## Texturing niveau expert (3e tour) — recherché, pas improvisé

Retour utilisateur : « va chercher des outils, des articles, informe-toi
sur avec quoi et comment tu peux donner du texturing niveau expert ».
Recherche faite avant de coder quoi que ce soit (sources : documentation
officielle Roblox Creator Hub, DevForum, et un test isolé pour vérifier
le tuilage — pas des suppositions) :

### Ce que « niveau expert » veut vraiment dire sur Roblox

- **`SurfaceAppearance`** (la voie PBR moderne : `ColorMap`, `NormalMap`,
  `RoughnessMap`, `MetalnessMap`, `EmissiveMap`) **ne fonctionne QUE sur
  `MeshPart`** — vérifié explicitement (DevForum : *"SurfaceAppearance
  is currently not possible to use on Parts"*). Le trône et la couronne
  sont construits en `Part` primitives (Block/Cylinder/Ball), pas en
  `MeshPart` — les convertir demanderait un pipeline de modélisation
  complet (Blender, export `.fbx`/`.obj`, UV unwrap), hors de portée
  d'une génération procédurale par primitives.
- La voie qui **fonctionne sur un `Part`** est l'objet `Texture` (ou
  `Decal` pour une image posée une fois) : une image qui tuile sur une
  face, réglée par `StudsPerTileU`/`StudsPerTileV`. C'est la voie
  pertinente ici.
- **Dans les deux cas**, une vraie image doit d'abord être **uploadée
  sur le CDN de Roblox** (compte Roblox + Roblox Studio, ou l'Open Cloud
  API) pour obtenir un `rbxassetid://` — aucune des deux n'est
  accessible depuis ce sandbox. Ce n'est pas contourné en silence : les
  images sont livrées en fichiers séparés (voir plus bas), pas comme un
  `rbxassetid` inventé qui pointerait vers rien.

### Ce qui EST livré : de vraies images, générées et vérifiées

`scripts/gen_textures.py` génère 5 *color maps* PNG (256×256,
`textures/*.png`) — pierre (`slate_color`), marbre veiné
(`marble_color`), métal brossé (`metal_color`), tissu tissé
(`fabric_color`), pierre plus rugueuse (`cobblestone_color`). Seamless
**par construction**, pas par un flou de bord approximatif : chaque
motif est une somme d'ondes `sin`/`cos` à fréquences **entières** sur la
largeur/hauteur de l'image — une onde à fréquence entière est
exactement périodique sur l'image, donc la mosaïque ne peut pas avoir de
raccord visible. Vérifié en mosaïquant chaque image 2×2 et en inspectant
le résultat (pas juste supposé correct après écriture du code).

Ces mêmes images sont **utilisées réellement par le lecteur HTML** — pas
en aplat de couleur avec le nom du matériau en commentaire, mais
dessinées sur chaque face via une vraie transformation affine
(`fillTexturedFace()` dans le lecteur : les 3 premiers coins écran d'une
face déterminent la transformation qui envoie le rectangle
(0,0)-(uLong,vLong), en studs, exactement dessus — un parallélogramme,
comme le garantit la projection orthographique du lecteur — puis un
`CanvasPattern` mis à l'échelle pour qu'une tuile couvre un nombre fixe
de studs, l'équivalent visuel de `StudsPerTileU/V`).

**Bug de contraste trouvé par capture d'écran, pas supposé** : la
première version du métal brossé (40 bandes quasi aléatoires,
`gen_textures.py`) se moyennait en un aplat flou une fois tuilée à
petite échelle — invisible sur l'accoudoir en capture réelle. Corrigé en
réduisant à 6 bandes amples plutôt que 40 fines qui s'annulent ; le
marbre a eu le même traitement (contraste des veines doublé). Revérifié
par une nouvelle capture, zoomée sur l'accoudoir : le grain brossé et le
veinage sont maintenant visibles.

### Pour vraiment les poser dans Roblox Studio (étape qui demande ton compte)

1. Dans Roblox Studio, sélectionne une pièce du trône ou de la couronne
   (ex. `Seat`).
2. Insère un objet `Texture` dessus (bouton `+` dans l'Explorer, ou
   clic droit → Insert Object → Texture).
3. Dans les propriétés du `Texture`, clique sur `Texture` → `Upload...`
   et choisis le fichier PNG correspondant (`marble_color.png` pour le
   siège, `slate_color.png` pour la pierre structurelle, etc. — voir le
   tableau plus haut pour la correspondance pièce → matériau).
4. Règle `StudsPerTileU`/`StudsPerTileV` à environ 2,6–3,0 pour la
   pierre/le marbre, 1,3 pour le métal, 0,7 pour le tissu (mêmes valeurs
   que `studsPerTile` dans le lecteur — `throne_crown_final.html`,
   objet `MATERIALS`).
5. Répète par face si besoin (`Texture.Face`), ou pose un `Texture` par
   pièce si une seule face suffit visuellement.

### Reflectance — le seul levier PBR-adjacent qui ne demande aucune image

`BasePart.Reflectance` (0 = mat, 1 = chrome/miroir du ciel — vérifié via
documentation, indépendant de `Material`) est maintenant écrit sur
chaque pièce (`export_model.MATERIAL_DEFAULT_REFLECTANCE`) : 0.2 pour le
métal, 0.08 pour le marbre, 0.02 pour la pierre mate, 0 pour le tissu et
le néon. Contrairement à `Texture`/`SurfaceAppearance`, ça ne demande
aucun upload — c'est actif dès l'import du `.rbxmx`.

## Texturing niveau expert, 4e tour — MeshPart réel + bake PBR

Retour utilisateur : toujours pas satisfaisant, recherche personnelle en
cours côté utilisateur ; deux tableaux d'outils/dépôts GitHub partagés
(Blender+bpy, Material Maker, Krita, ArmorPaint, Substance 3D Painter…),
avec la consigne « explore et informe-toi dessus ». Chaque piste testée
**dans ce sandbox**, pas jugée sur description :

- **ArmorPaint** et **Material Maker** sont des applications GUI (X11) —
  aucune API de script/CLI headless trouvée pour l'un ou l'autre. Non
  utilisables ici (pas de serveur X interactif dans ce sandbox, et même
  `capture_headless.sh`/`xvfb-run` ne suffit pas : il faudrait piloter
  une UI, pas juste rendre une frame).
- **bpy (Blender 5.0.1 Python)** : testé en conditions réelles avant
  d'écrire quoi que ce soit — création de mesh, UV unwrap, matériaux à
  nœuds, **bake Cycles réel** (`bpy.ops.object.bake`), export `.fbx` —
  tout fonctionne en ligne de commande, sans affichage. C'est la seule
  piste des deux tableaux réellement scriptable ici.

Constat clé qui en découle : le texturing appliqué jusqu'ici
(`Texture`/`Decal` + `StudsPerTileU/V`, section précédente) est plafonné
— ce sont des `Part` primitives, et `SurfaceAppearance` (le vrai système
PBR de Roblox, avec relief/rugosité/métalness réels, pas juste une image
plate) **ne fonctionne que sur `MeshPart`**. Pour un texturing vraiment
« niveau expert », il faut donc de vrais maillages, pas des primitives.

### Ce qui est livré : un pipeline mesh + bake + export complet

Nouveau script `scripts/build_mesh_export.py`, qui **reconstruit** (ne
réutilise pas) le trône/l'escalier/la couronne comme de vrais objets
maillés bpy à partir des mêmes specs géométriques que `props.py` :

1. **Cartes PBR dérivées** (`scripts/gen_pbr_maps.py`), à partir des
   *color maps* déjà générées et vérifiées seamless (section
   précédente) — jamais du bruit natif Blender (Noise/Voronoi), qui
   n'est **pas** périodique par construction (vérifié par test) et
   aurait réintroduit un risque de raccord visible :
   - `RoughnessMap` : remap direct de la luminance de la color map vers
     une plage de rugosité par matériau (Pillow/numpy) — métal
     0.12–0.32 (brillant), tissu 0.65–0.88 (mat).
   - `MetalnessMap` : uniquement pour le métal, ~0.8–1.0.
   - `NormalMap` : un vrai **bake height→normal** en bpy/Cycles
     (`ShaderNodeBump` piloté par la luminance de la color map, sur un
     plan UV 1:1, bake `type='NORMAL', normal_space='TANGENT'`, CPU, 8
     échantillons) — hérite du caractère seamless de la color map source
     plutôt que d'être réinventé. **Bug trouvé par test, pas supposé** :
     `ShaderNodeBump.Distance` vaut par défaut `0.001` (quasi nul), pas
     `1.0` — la première passe produisait des normal maps totalement
     plates (écart-type des pixels ≈ 0.001) malgré un `Strength` non
     nul ; diagnostiqué en inspectant directement
     `bump.inputs['Distance'].default_value`, corrigé en le fixant
     explicitement à `1.0` et recalibrant les forces de relief pour
     cette distance. Revérifié visuellement (les normal maps montrent un
     vrai relief qui suit le motif de chaque color map) et
     numériquement (écart-type non nul).
   - 11 fichiers PNG dans `textures_pbr/` (5 normal maps, 5 roughness
     maps, 1 metalness map pour le métal seul — le tissu/la pierre/le
     marbre ne sont jamais métalliques).
2. **Reconstruction en vrais maillages** (`build_mesh_export.py`) :
   chaque pièce (`Block`→cube, `Cylinder`→cylindre avec la même
   convention d'axe que Roblox — longueur le long de l'axe local X, pas
   Z comme le natif Blender —, `Ball`→sphère UV) est créée à la bonne
   taille/position/rotation, **UV-dépliée** (`cube_project`, taille de
   tuile identique à `studsPerTile` du lecteur pour un aspect cohérent),
   puis reçoit un matériau à nœuds Principled BSDF câblé ColorMap→Base
   Color, NormalMap→Normal (via `ShaderNodeNormalMap`, espace couleur
   `Non-Color`), RoughnessMap→Roughness, MetalnessMap→Metallic (métal
   seulement). La couronne (gemmes) reçoit un matériau `Emission` plat
   (pas de PBR classique, cohérent avec `Neon`/`selfLit` du lecteur).
   **Bug trouvé par test, pas supposé** : la première version appelait
   `bpy.ops.wm.read_factory_settings(use_empty=True)` séparément avant
   chaque export (trône puis couronne) — ce reset efface **tous** les
   datablocks bpy, pas seulement les objets de la scène, donc le
   dictionnaire de matériaux partagé construit avant le premier export
   était détruit avant le second (`ReferenceError: StructRNA of type
   Material has been removed`). Corrigé en ne resettant qu'une seule
   fois, avant toute construction, et en construisant trône et couronne
   dans la **même** session bpy, chacun exporté par une simple sélection
   différente plutôt que par un reset intermédiaire.
3. **Export FBX** (`bpy.ops.export_scene.fbx`) : `output/throne_mesh.fbx`
   (21 objets : dais, 4 pieds, siège, dossier, 2 accoudoirs, coussin,
   bande dorée, crête-couronne [bande + 5 pointes], 4 marches) et
   `output/crown_mesh.fbx` (11 objets : bandeau + 5 pointes + 5 gemmes).
   Régénéré au 6e tour (références visuelles) avec la nouvelle géométrie/
   les nouveaux matériaux (`Wood` sur dais/pieds, `Fabric` sur siège/
   dossier).

**Vérifié par ré-import**, pas juste par l'absence d'erreur à l'export :
les deux fichiers ont été rechargés dans une session bpy neuve et
inspectés objet par objet — 32 objets au total, tous avec des UV
(`uv_layers` non vide), le bon matériau assigné (ex. `Backrest`→
`mat_Fabric`, `Armrest`→`mat_Metal`, les gemmes→`mat_Neon`), aucun
maillage dégénéré (0 sommet/face).

### Importer dans Roblox Studio et brancher SurfaceAppearance (étape qui demande ton compte)

Contrairement à `Texture`/`Decal` (section précédente), un `MeshPart`
importé se câble avec un objet `SurfaceAppearance`, pas un `Texture` :

1. Dans Roblox Studio : `File → Import 3D` (ou glisser-déposer dans
   l'Explorer), sélectionne `throne_mesh.fbx` puis `crown_mesh.fbx`. Chaque
   import crée un `Model` contenant un `MeshPart` par pièce, nommé comme
   dans la liste ci-dessus (`Seat`, `Armrest_2.6`, `Point_0_Gem`, etc.).
2. Sur chaque `MeshPart`, insère un objet `SurfaceAppearance` (`+` dans
   l'Explorer, ou clic droit → Insert Object → SurfaceAppearance).
3. Dans les propriétés du `SurfaceAppearance` : `ColorMap` → upload
   `textures/<matériau>_color.png` ; `NormalMap` → upload
   `textures_pbr/<matériau>_normal.png` ; `RoughnessMap` → upload
   `textures_pbr/<matériau>_roughness.png` ; pour le métal uniquement,
   `MetalnessMap` → upload `textures_pbr/metal_metalness.png`. Table de
   correspondance pièce → `<matériau>` (voir aussi le tableau à jour dans
   "Passage aux références visuelles utilisateur" plus bas) : Wood pour
   dais/pieds, Fabric pour siège/dossier/coussin, Metal pour accoudoirs/
   bande dorée/crête-couronne/bandeau-pointes de la couronne, Cobblestone
   pour une marche sur deux (l'autre en Slate).
4. `SurfaceAppearance.AlphaMode` doit rester `Overlay` (comportement par
   défaut) pour que `ColorMap` module la couleur du `MeshPart` plutôt que
   de la remplacer à plat.
5. Pour les gemmes (`Point_*_Gem`, matériau `Neon` côté bpy) : pas de
   `SurfaceAppearance` à poser — règle directement `MeshPart.Material =
   Neon` et une `Color3` assortie dans Roblox Studio ; l'effet de brillance
   pulsante reste une mise en scène du lecteur HTML (`drawCrownGlow()`),
   pas une propriété qui se transporte dans le fichier.

**Comme pour `Texture`/`SurfaceAppearance` en général**, uploader une
image demande un compte Roblox (Studio ou l'Open Cloud API) — non
disponible dans ce sandbox. Les fichiers sont livrés en `.png`/`.fbx`
séparés, jamais comme un `rbxassetid` inventé.

### Ce que ce pipeline change par rapport à la route `Part`+`Texture`

Les deux routes restent livrées, elles ne s'excluent pas :

| | `Part` + `Texture` (3e tour) | `MeshPart` + `SurfaceAppearance` (4e tour) |
|---|---|---|
| Géométrie | primitives Roblox natives (`export_model.py` → `.rbxmx`) | vrais maillages bpy, UV-dépliés (`build_mesh_export.py` → `.fbx`) |
| Relief/rugosité/métal réels | non (image plate tuilée) | oui (normal/roughness/metalness bakés) |
| Réaction à l'éclairage dynamique de la scène | couleur plate + `Reflectance` global | vrai relief qui réagit à l'angle de lumière |
| Effort d'installation Studio | Insert `Texture`, upload 1 image | Import 3D, Insert `SurfaceAppearance`, upload jusqu'à 4 images par matériau |
| Rig personnage compatible | oui (Part = joints Motor6D natifs) | n/a (le personnage reste en `Part`, seuls trône/couronne changent de route) |

## Relief et micro-reflet réels dans l'animation elle-même (5e tour)

Retour utilisateur après la livraison du pipeline `MeshPart`+bake : « Non,
crée l'animation avec le nouveau texturing » — les fichiers PBR
(`textures_pbr/*.png`, prêts pour `SurfaceAppearance` dans Studio) ne
suffisaient pas seuls ; il fallait que **l'animation qui joue dans le
lecteur** montre elle-même ce niveau de texturing, pas seulement le
livrer en pièces jointes séparées.

### Ce qui a changé

Le lecteur (`scripts/throne_crown_viewer.html`, maintenant **versionné**
dans le dépôt — il ne vivait jusque-là que dans le scratchpad de session,
jamais commit, contrairement à la règle « aucune décision/recette
n'existe ailleurs que dans un fichier versionné ») décode maintenant
**pixel par pixel**, au chargement, les mêmes `NormalMap`/`RoughnessMap`
bakées que celles livrées pour `SurfaceAppearance` (pas une texture à
part inventée pour le lecteur) :

- **Relief** (`buildBumpCanvas()`) : chaque pixel du `NormalMap` est
  décodé en vecteur normal tangent-espace (`R,G,B` → `x,y,z` ∈
  `[-1,1]`), projeté sur une direction de lumière rasante fixe en espace
  texture, et le résultat (assombri/éclairci) est appliqué sur chaque
  face via `globalCompositeOperation = "overlay"` — **avec la même
  transformation affine** que le calque couleur (`fillTexturedFace()`),
  donc aligné pixel pour pixel avec la tuile de couleur.
- **Micro-reflet** (`buildShineCanvas()`) : dérivé directement de la
  `RoughnessMap` (`(1-roughness)^1.6`), appliqué en `"screen"` — s'éteint
  de lui-même sur les zones à roughness élevée (tissu) sans liste de
  matériaux codée en dur, puisque c'est la carte bakée elle-même qui
  pilote l'intensité, matériau par matériau et pixel par pixel.

**Limite assumée, pas cachée** : la direction de lumière du relief est
fixe en espace texture (rasante identique sur chaque face), pas
recalculée en espace monde par face — ce lecteur reste un projecteur
orthographique Canvas 2D (voir plus haut), pas un moteur relighté par
pixel. Le relief affiché est en revanche une vraie donnée bakée (le même
fichier que celui livré pour Studio), pas un bruit décoratif ajouté pour
faire joli.

### Vérifié par capture d'écran A/B sur la même frame, pas supposé

Écart-type maintes fois trouvé dans ce projet entre "numériquement
correct" et "visuellement lisible" (le bug de signe Z, l'escalier
monochrome, la couronne trop discrète, le métal à 40 bandes) : même
prudence ici. Un script Playwright charge le lecteur construit, désactive
les deux nouveaux calques (`BUMP_READY`/`SHINE_READY` forcés à `false`),
capture ; les réactive, recapture **la même frame, même caméra** — le
dossier du trône (dossier ardoise + accoudoirs/fleurons métal) montre un
chevron de relief net et des reflets métalliques marqués côté "après",
absent côté "avant" (calque couleur seul). Forces calibrées à l'oeil
après un premier essai trop discret (`overlay` à 0.6/gain 190 → 0.85/gain
260 ; `screen` à 0.22 → 0.38) — même schéma que le halo de couronne ou le
métal 40→6 bandes : la première passe "correcte en théorie" ne se voyait
pas assez, corrigée après capture réelle, pas avant. Revérifié ensuite
sur toutes les phases (montée, assise, couronnement, pose finale) et les
3 angles de caméra : aucune régression, le halo de couronne fonctionne
toujours par-dessus.

### Le lecteur est maintenant reconstructible depuis le dépôt seul

Nouveau `scripts/build_viewer.py` : relance `dump_scene_data.py`, lit
**toutes** les images de `textures/` et `textures_pbr/` (indexées par nom
de fichier sans extension — `slate_color`, `slate_normal`,
`slate_roughness`, `metal_metalness`…), les embarque en base64 dans le
template versionné. Avant ce script, cet assemblage se faisait par des
commandes ad hoc non versionnées — un vrai trou par rapport à la règle
"le dépôt est le cerveau du projet" que ce tour corrige.

## Calibration — vérifiée par le calcul, pas à l'oeil

Les valeurs numériques du rig R6 permettent de calculer, sans deviner,
où le personnage debout a les pieds et où sont ses hanches assis :

- Torse au repos = `HumanoidRootPart` (aucune translation locale sur ce
  joint). Hanche = bas du torse = `HumanoidRootPart.Y - 1`. Pied =
  `HumanoidRootPart.Y - 3`. Sommet de la tête = `HumanoidRootPart.Y + 2`.
  (Lu sur `rig/r6_rig.json`, pas mesuré à l'oeil — voir
  `scripts/calibrate.py`.)

Conséquence : `HumanoidRootPart.Y = 3` donne un personnage debout pieds
à 0, tête à 5 studs — le standard R6. Le siège du trône est donc posé
avec le dessus à **Y = 2.0 au-dessus de sa propre estrade** (hanche
assise à Y=3, moins 1) pour que le personnage s'y encastre sans avoir à
changer sa hauteur de hanche en s'asseyant — **exactement le mécanisme
de l'assise R6 par défaut de Roblox** : le bassin ne descend pas, seules
les jambes tournent à la hanche. Comme ce rig n'a pas de genou, la jambe
entière (cuisse ET tibia, un seul segment rigide) pointe vers l'avant à
l'horizontale une fois assis — ce qui EST le look d'une assise R6
vanilla, pas une simplification à cacher.

Depuis l'ajout de l'escalier (voir plus bas), tout le trône repose sur
une estrade réelle à **PLATFORM_H = 2.0 studs** au-dessus du sol : les
valeurs ci-dessus restent écrites comme si le trône était au sol
(`props.throne_parts()`), puis **décalées une seule fois** de
+PLATFORM_H (`props._lift()`) avant export — un seul nombre à changer
si la hauteur de l'estrade change, jamais besoin de retoucher chaque
`Part` à la main. Le tableau ci-dessous montre les valeurs finales
(après décalage).

### Sémantique des axes du bras — établie par diagnostic, pas supposée

La première hypothèse (par analogie avec les jambes du combo de coups
de pied : X = amplitude du mouvement) était **fausse** pour les bras.
Vérifié en isolant chaque axe (`scripts/calibrate.py` contient la
méthode, un diagnostic ad-hoc l'a précédée) :

- **X positif** : le bras part vers l'avant (-Z) puis monte par-dessus,
  jusqu'à X=180° = au-dessus de la tête.
- **Z** (bras droit) **positif** : lève le bras vers l'extérieur (+X) et
  vers le haut — Z≈55° pose la main exactement sur le dessus de
  l'accoudoir. **Négatif** : ramène le bras vers l'intérieur (croise le
  corps). Bras gauche : signe opposé (symétrie miroir, vérifiée).

Conséquence mesurée, pas supposée : la portée verticale maximale du
poignet (bras droit, sans coude, longueur fixe) plafonne à **Y≈5,0** —
la couronne ne peut pas être « levée très haut au-dessus de la tête »,
seulement juste au-dessus, qui est déjà là où elle doit atterrir. Le
geste de couronnement est donc nécessairement bref (lever ~ juste
au-dessus, puis poser), pas un grand geste ample — contrainte du rig,
assumée plutôt que contournée par une pose qui aurait l'air fausse.

Valeurs retenues, toutes vérifiées par calcul de position monde contre
la géométrie du trône :

| Pose | Bras droit | Main droite (monde, après +PLATFORM_H) | Cible |
|---|---|---|---|
| assis, repos | (0,0,55) | (2.516, 5.048, -0.012) | accoudoir (X~2.6 Y~5.0) |
| prise (pickup) | (5,0,58) | (2.537, 5.121, -0.059) | coussin de la couronne (5.08 studs) |
| levée | (180,0,-35) | (0.549, 6.985, -0.350) | au-dessus de la tête (Y max ~7.0) |
| posée | (180,0,-45) | (0.293, 6.865, -0.431) | sommet de tête (0, 6.94, -0.48), écart 0.31 stud |

(Les mêmes écarts relatifs qu'avant l'escalier — seule l'origine Y a
changé, la géométrie du geste de couronnement, elle, est identique.)

## La couronne change de parent en cours de scène

Un `KeyframeSequence` anime les Motor6D d'**un seul rig**. Il ne peut
pas faire porter un objet par la main puis le faire "sauter" sur la
tête — ça demande de changer l'objet **parent** (coussin → main → tête)
en cours de clip, ce que ce format ne peut pas exprimer. Dans un vrai
projet Roblox, ça se fait par un script qui re-weld la couronne au bon
instant (typiquement sur un `Marker` de l'`AnimationTrack`).

`scripts/compute_crown_track.py` calcule cette trajectoire par la MÊME
cinématique directe que tout le reste du pipeline (pas une
approximation à l'oeil) et l'exporte en JSON (`output/crown_track.json`)
— trois phases :

1. `t < 1.35s` : statique, posée sur le coussin.
2. `1.35s ≤ t < 2.00s` : suit le bout de la main droite (orientation
   gardée verticale — la vriller avec la rotation complète du bras,
   ~175° sur cette fenêtre, aurait l'air faux).
3. `t ≥ 2.00s` : suit le sommet de la tête, **rotation de la tête
   comprise** — une fois posée, elle tourne avec la tête.

Deux points de recollement mesurés plutôt que masqués : saut coussin→
main à la prise = **0,000 stud** (coïncidence du calibrage, pas
garanti en général) ; saut main→tête à la pose = **0,307 stud** (léger,
assumé).

## Vérifications

- **Structure R6** (`scripts/run_scene.py`) : 6 segments rigides,
  aucune translation locale hors racine, rotations finies et dans une
  plage plausible (< 260°, marge au-dessus du 180° max utilisé). OK dès
  le premier export.
- **Round-trip moteur** (`scripts/resolve_rbxmx.py`, même outil que le
  combo de coups de pied) : `HumanoidRootPart` toujours correctement
  ignorée par l'Animator (0 stud/deg), Torso Y résolu par l'équation du
  moteur : min **3.000** (personnage debout au sol, début de la montée)
  à max **5.000** (assis sur l'estrade), amplitude 2.000 stud —
  exactement `PLATFORM_H`, cohérence vérifiée jusque dans le fichier
  final, pas seulement dans les courbes intermédiaires.
- **Vérification VISUELLE réelle**, pas juste des chiffres : capture
  d'écran automatisée du lecteur HTML via Playwright (Chromium
  pré-installé dans ce sandbox), à plusieurs instants de la scène. C'est
  cette capture qui a trouvé le seul vrai bug de ce prototype (voir
  ci-dessous) — les nombres de calibration étaient déjà bons et
  n'auraient rien révélé.

### Bug trouvé par capture d'écran, pas par les nombres

Premier export : la phase "approche" (personnage debout, avant de
s'asseoir) plaçait `HumanoidRootPart` à **Z = +1.6**. Signe inversé :
le siège et le dossier du trône occupent Z de -0.9 à +3.3, donc Z=+1.6
place le personnage débout **à l'intérieur du volume du trône**, caché
derrière le dossier gris. Aucune vérification numérique (hanche à la
bonne hauteur, mains sur les accoudoirs) ne pouvait le révéler — ces
calculs ne portent que sur la phase assise, pas sur la phase d'approche,
et un personnage caché reste "structurellement" correct. Seule la
capture d'écran réelle (pas une description imaginée) l'a montré :
au premier instant de la scène, aucune silhouette humaine visible,
seulement le trône. Corrigé en inversant le signe (Z=-1.6, cohérent avec
-Z = avant du personnage = côté ouvert du trône). Revérifié par une
seconde capture : le personnage est visible, debout devant le trône,
dès `t=0`.

## Escalier + montée « sombre mais fière »

Ajouté au 2e tour. Le trône repose désormais sur une estrade
(`props.PLATFORM_H = 2.0` studs) reliée au sol par un escalier de
`props.STAIR_N = 4` marches pleines (chaque marche est une boîte du sol
jusqu'à SON propre sommet, pas une marche flottante — silhouette
d'escalier plein). `choreography.climb_stairs()` fait grimper le
personnage marche par marche (jambe qui se lève ~30° puis se pose,
alternée, avec une légère contre-rotation du torse), avant
`choreography.full_scene()` qui l'enchaîne avec `sit_and_crown()`
(décalée de +PLATFORM_H en Y et de la durée de la montée en temps —
voir "Calibration" plus haut).

« Sombre mais fière » traduit en deux choix de mise en scène plutôt
qu'en pose précise : un pas **lent et délibéré** (0,75 s/marche) et des
**bras presque immobiles** (pas de balancement naturel de marche — c'est
la retenue qui lit comme sombre/impériale), avec le **menton constamment
levé** (`Head = (-6,0,0)`) du premier au dernier pas.

Raccord montée → assise vérifié par le calcul (`scripts/calibrate.py`) :
écart de **0,021 stud** entre la position du personnage à la toute fin
de la montée et au tout début de l'assise (décalée) — quasi invisible,
pas juste supposé continu.

### Bug réel trouvé par l'utilisateur : il montait les marches à reculons

Retour direct : « je veux que tu rajoute la logique que quand il monte
les escalier y'a une rotation [...] la il monte et s'assoit mais ça
voudrait dire que il les monte en arrière ». Exact, et pas détecté avant
ce retour : `root_pos` avançait bien en Z croissant (vers le trône) marche
après marche, mais `HumanoidRootPart` restait à l'identité — le
personnage gardait le cap -Z (l'avant du rig) du début à la fin, donc
avançait vers le trône **en marchant à reculons**, sans jamais s'être
tourné vers lui.

Corrigé en deux temps (`choreography.py`, `_FACE_STAIRS`/`_FACE_ROOM`,
`TURN_T`) :

1. **Pendant la montée**, `HumanoidRootPart = (0, 180, 0)` : le
   personnage fait face au trône (+Z) et avance donc en marchant
   réellement vers l'avant. La convention de la jambe qui se lève
   (X positif = vers l'avant, voir plus haut) reste inchangée : elle est
   locale au torse, donc bascule automatiquement de sens en même temps
   que tout le corps quand le cap change — aucune retouche des angles de
   jambe n'a été nécessaire, seul le cap racine change.
2. **En haut des marches**, un demi-tour sur place (`TURN_T`, racine
   immobile à `_CLIMB_Z1`) ramène `HumanoidRootPart` de 180 à 0 —
   l'orientation qu'attend `sit_and_crown()` (dos au dossier, face à la
   salle). Sans ce demi-tour le personnage se serait assis dos au vide.

Vérifié par deux méthodes independantes, pas juste relu :
- **Raccord montée → assise** : l'écart tombe à **0,0000 stud** (contre
  0,021 avant, voir ci-dessus) — le point d'arrivée du demi-tour a été
  calé pour coïncider exactement avec le premier point de l'assise.
- **Sens de la marche** : au moment où une jambe se lève, sa position
  monde est comparée à celle de la racine — la jambe porteuse du pas
  (`lead`) doit être **devant** (plus loin dans le sens de déplacement)
  que la jambe d'appui (`trail`). Mesuré à la 1ère marche : jambe avant
  à +0,67 stud du sens de marche, jambe arrière à -0,55 — confirme une
  marche avant, pas une marche arrière compensée par le sens de la
  caméra.

### Retour utilisateur suivant : « on dirait il tourne comme une toupie »

Juste après le correctif ci-dessus. Cause : la 1re version du demi-tour
faisait tourner `HumanoidRootPart` seul, à vitesse constante, de 180 à 0
— torse, tête, bras, jambes tous rigidement solidaires, comme un seul
bloc pivotant autour d'un axe fixe. Mécaniquement correct (le raccord
tombait déjà à 0,0000 stud), mais **aucun humain ne tourne comme ça** :
rien ne bouge à un rythme différent du reste, donc rien ne lit comme un
geste — d'où la toupie.

Corrigé en décomposant le demi-tour en 4 temps qui **ne bougent pas à la
même vitesse ni au même moment**, sur le modèle d'un « about-face »
militaire (cohérent avec le personnage « sombre mais fier ») :

1. la **tête part en premier** (« spotting » — le même principe que le
   `head_lead` mesuré dans le combo de coups de pied : on regarde où on
   va avant que le corps suive), le poids se transfère sur la jambe
   d'appui (léger creux vertical, -0,10 stud) et la jambe libre se
   soulève pour amorcer un pas de pivot ;
2. le **corps tourne pendant que la jambe libre est encore en l'air** —
   pas après qu'elle soit reposée, sinon on revient à tourner sur deux
   pieds plantés, exactement ce qui lit comme une toupie ;
3. la jambe se **replante déjà dans le nouveau cap** (« step turn »), le
   torse épaules-en-avant achève de se rattraper ;
4. tout est rattrapé et immobile — coïncide exactement avec la pose
   figée qu'attend l'assise.

Vérifié par le calcul, pas juste reécrit à l'oeil : au premier temps
(28 % du demi-tour), le corps (`HumanoidRootPart`) n'a **pas encore
bougé** (180°) alors que le cap effectif de la tête (racine + torse +
tête composés) est déjà à 87° — plus de la moitié du chemin parcouru
avant que le corps n'ait commencé à tourner. C'est précisément ce
décalage temporel entre les parties qui distingue un geste humain d'une
rotation mécanique unique.

### Bug trouvé par capture d'écran, encore une fois

Première version : les 4 marches étaient toutes de la même teinte pierre
(`STONE_DARK`) et la flaque de lumière du lecteur n'éclairait que le
trône, pas l'escalier. Résultat vérifié par capture (pas supposé) : en
vue 3/4, l'escalier se lisait comme un bloc sombre indistinct, aucune
marche individuelle visible — alors qu'une capture en vue de profil
confirmait que la géométrie elle-même était correcte (marches bien
étagées). Corrigé en alternant deux teintes de pierre par marche et en
recentrant/élargissant la flaque de lumière pour couvrir l'escalier —
revérifié par une nouvelle capture, les marches se détachent nettement.

## Rendu « premium » du lecteur

Éclairage à trois sources : une clé chaude (façon torche), un
remplissage froid faible (évite les noirs bouchés), et une direction de
vue fixe pour un speculaire/liseré de bord approximés (le rendu n'est
pas en perspective réelle — `proj()` est une rotation + projection
orthographique — donc la vue est une direction constante plutôt que
recalculée par pixel : suffisant pour un reflet stylisé, pas physique).
Ombres de contact au sol (ellipses dégradées sous le trône et le
personnage), fond en dégradé sombre avec flaque de lumière dramatique
plutôt qu'un plateau uniformément éclairé, teinte sombre et riche pour
le personnage (dont le `Material` réel reste celui de l'avatar du
joueur — hors de portée de ce pipeline, seul le rendu du lecteur est
stylisé pour lui). Tout ça reste propre au **lecteur** (Canvas 2D, pas
un moteur 3D Roblox).

**Correction depuis le retour utilisateur sur le texturing (2e
correction)** : la 1re version de ce rendu premium utilisait une
catégorie d'éclairage inventée pour le lecteur (`mat` :
stone/gold/gem/royal), déconnectée du fichier. Depuis l'ajout du vrai
`Material` Roblox par pièce (voir "Texturing réel" sous "Géométrie du
trône et de la couronne"), **le lecteur lit ce même champ** — `scripts/
dump_scene_data.py` porte `material` (pas une catégorie séparée) jusqu'au
JSON, et le lecteur associe un rendu à chaque vrai nom de matériau :
`Metal` (reflet net, liseré marqué), `Marble` (légèrement plus glacé et
clair que le reste de la pierre), `Slate`/`Cobblestone`/`Fabric` (quasi
mats), `Neon` (auto-éclairé, quasi indépendant de la direction de la
lumière — voir plus bas). Un changement de `Material` dans `props.py` se
répercute donc maintenant automatiquement dans le rendu du lecteur, sans
mapping séparé à tenir à jour à la main.

## « La couronne brille »

Une fois posée sur la tête (`t >= DATA.crowned_t`), un halo pulsé
(composition additive, `globalCompositeOperation = "lighter"`) s'anime
en boucle autour de la bande et de chaque gemme, plus 4 traits
scintillants tournants façon « sparkle » — lisible même en vignette,
pas juste un flou diffus. Première version trop discrète (halo de 16-30
px, alpha 0.16-0.34) : imperceptible à l'échelle du lecteur, corrigé en
l'agrandissant et en ajoutant les traits scintillants, revérifié par
capture d'écran.

Effet du **lecteur** pour le halo animé — mais la brillance existe
maintenant **aussi dans le fichier livré** : les 5 gemmes de la couronne
portent `Material = Neon` (voir "Texturing réel" plus haut), qui émet
une lueur nativement dans le moteur Roblox, sans `PointLight` séparé.
Pas encore de version animée/pulsée côté fichier (un `PointLight` avec
script de variation d'intensité serait la suite naturelle, non fait ici
— pas demandé explicitement pour le fichier, seulement observé comme
prolongement possible).

## Rig du personnage — pas de source alternative légitime trouvée

Retour utilisateur : « utilise le rig r6 Roblox que je t'ai envoyé il
est mieux ». Le fichier reçu était une **image** (capture d'écran de
Roblox Studio montrant les gizmos d'orientation d'un rig), pas un
fichier `.rbxmx`/`.rbxm` exploitable — clarifié avec l'utilisateur, qui
a confirmé vouloir « le rig par défaut de Roblox Studio » comme source.

Recherche faite avant de conclure, pas supposé : une recherche GitHub
pour un rig R6 par défaut alternatif ne remonte que des redistributions
de contenu client Roblox non licenciées (`RCCService*/content/models/
Thumbnails/Mannequins/R6.rbxmx`, `morpherEditorR6.rbxmx`) — exactement
la catégorie de dépôts déjà écartée à l'origine du projet (voir
`rig/PROVENANCE.md` : dumps de private servers, sans licence de
redistribution). Le DevForum Roblox, où la communauté documente parfois
ces valeurs par écrit (pas un dump de fichier), est bloqué par le proxy
réseau de ce sandbox.

Décision : garder le rig d'origine (dépôt Adonis, licence MIT). Ce
n'est pas un pis-aller silencieux — ce rig implémente déjà la géométrie
standard R6 (Torse 2×2×1, Tête 2×1×1, membres 1×2×1, six Motor6D nommés
standard), la même que toute installation de Roblox Studio, puisque R6
n'a qu'une seule géométrie standard sur toute la plateforme. Dit
honnêtement dans le lecteur HTML et ici plutôt que de prétendre à une
source changée qui ne l'a pas été.

## Passage aux références visuelles utilisateur (6e tour)

L'utilisateur a envoyé deux photos de référence (pas de texte) : une
couronne dorée à gemmes **roses**, et un trône baroque — dossier/siège en
velours rouge capitonné, pieds/socle en bois laqué sombre, filets et
ornements dorés, **couronné d'une vraie couronne dorée** posée sur le
sommet du dossier. Traduit en changements concrets, matériau par
matériau (jamais une teinte inventée à l'œil sans le vrai `Material`
derrière — même discipline que les tours précédents) :

| Pièce | Avant | Après | Pourquoi |
|---|---|---|---|
| Dais, 4 pieds | `Slate` gris pierre | **`Wood`** (nouveau, voir plus bas) | référence : socle/pieds en bois, jamais de pierre |
| Siège | `Marble` | **`Fabric`** rouge (déjà la palette velours de `fabric_color.png`, aucune nouvelle texture) | référence : coussin capitonné, pas de pierre polie |
| Dossier | `Slate` | **`Fabric`** rouge | idem |
| Accoudoirs, bande du dossier | `Metal` doré | inchangé | déjà cohérent avec les filets dorés de la référence |
| 3 fleurons-boules au sommet | boules dorées abstraites | **crête en forme de couronne** (`throne_crest_parts()`) | la référence montre une VRAIE couronne posée sur le trône, pas des boules |
| Gemmes de la couronne PORTÉE | rouge (`GEM_RED`) | **rose** (`GEM_PINK`) | référence `crown.jpg` : gemmes roses, pas rouges |

### `Wood` — nouveau matériau, bout en bout comme les autres

Même traitement complet que `Slate`/`Marble`/`Metal`/`Fabric`/
`Cobblestone` avant lui, pas un raccourci pour cette seule pièce :
`Enum.Material.Wood` était déjà dans `MATERIAL_BY_NAME`
(`export_model.py`, valeur `512`, vérifiée dès le tour "texturing niveau
expert" même si inutilisée jusqu'ici) ; `gen_textures.wood()` génère une
5e *color map* seamless ; `gen_pbr_maps.py` lui bake NormalMap +
RoughnessMap (pas de MetalnessMap, le bois n'est pas un métal) ;
`build_mesh_export.MATERIAL_TO_PBR` et le `MATERIALS`/`MATERIAL_TEXTURE`
du lecteur HTML gagnent chacun une entrée `Wood`.

**Premier essai illisible, trouvé par capture d'écran, pas supposé** :
la première version de `wood()` (7 bandes de fréquences proches +
15 % de bruit isotrope) ressemblait à un tissage/vannerie une fois
rendue sur les pieds du trône, pas à du bois — les bandes proches
s'annulaient partiellement entre elles ET contre le bruit isotrope (qui
varie en X ET en Y, alors que le veinage du bois ne doit varier qu'en Y,
le long du grain). Corrigé avec 4 bandes larges et nettes (pas de
quasi-annulation) + des veines fines (`|sin|` à une puissance, même
technique que `marble()`) toutes deux fonction de Y seul, et le bruit
isotrope réduit à un flou très léger plutôt qu'une composante dominante
— même catégorie de bug que le métal à 40 bandes ou l'escalier
monochrome : une texture "correcte en théorie" (seamless, bien
distribuée) peut quand même ne pas se lire comme le matériau visé une
fois posée sur la géométrie réelle.

### La crête-couronne réutilise la géométrie de la couronne portée

`throne_crest_parts()` appelle directement `crown_points()` (même
fonction que `crown_parts()`, la couronne que le personnage porte) à une
échelle différente plutôt que de redessiner une silhouette à la main :
même motif "pointe avant la plus haute" recopié sans risque de diverger
visuellement des deux couronnes. Différence assumée : la crête est un
ornement fixe du meuble (`Metal` doré statique, pas de gemmes/`Neon`) —
la couronne que le rituel de couronnement met en scène reste la seule à
porter des gemmes et à briller.

### Vérifié par capture d'écran contre la référence elle-même

Zoomé sur le sommet du dossier après reconstruction (`assise`/`pose
finale`, caméra face) : la crête se lit sans ambiguïté comme une
couronne à 5 pointes de hauteurs variées, posée sur un dossier de
velours rouge strié (relief du NormalMap toujours actif, voir tour
précédent) bordé d'or — silhouette directement comparable à la photo de
référence. `.rbxmx`/`.fbx` regénérés avec la nouvelle géométrie/
matériaux (`run_scene.py`, `build_mesh_export.py`), lecteur reconstruit
et republié à la même URL.

## Limites assumées

- Couronne tenue "à plat" (rotation identité) pendant tout le portage à
  la main plutôt que vrillée avec le bras — choix esthétique assumé,
  pas un oubli (voir section "change de parent").
- Le lecteur HTML dessine tout en boîtes (y compris les `Ball`/
  `Cylinder` du trône et de la couronne) — limite du renderer de
  prévisualisation, pas du fichier livré, qui porte la vraie `Shape`.

## Commandes

```bash
source ../r6_aerial_kick_combo/.venv/bin/activate   # venv partagé (numpy, bpy)
cd scripts
python3 calibrate.py          # vérifie hanche/mains/pieds contre la géométrie
python3 run_scene.py          # exporte character/throne/crown .rbxmx + sanité structurelle
python3 resolve_rbxmx.py ../output/character_sit_and_crown.rbxmx   # round-trip moteur
python3 compute_crown_track.py                          # trajectoire couronne -> JSON
SCENE_OUT=/tmp/throne_scene_data.json python3 dump_scene_data.py   # data du lecteur HTML
```
