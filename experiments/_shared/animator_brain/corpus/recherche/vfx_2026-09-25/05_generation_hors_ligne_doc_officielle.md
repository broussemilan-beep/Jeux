# Rapport G5 : génération hors ligne (textures, flipbooks, smears) et documentation officielle Roblox

Tout a été cloné dans `/tmp/claude-0/-home-user-Jeux/4796ac9e-8e41-51f7-91c4-7b92a6a187d0/scratchpad/vfx/g5/` (en `--depth 1`). Les essais de rendu sont dans `g5/essais/`, avec les scripts `t_ghibli.py`, `t_render.py`, `sheet.py`, `t_smear2.py` et les images dans `out/`. Rien n'a été écrit dans `/home/user/Jeux`.

**Environnement vérifié :**
- `import bpy` fonctionne : bpy 5.0.1. Il n'y a pas de binaire `blender` dans le PATH, ce qui ne gêne pas [CODE LU].
- **Cycles CPU rend correctement sans interface** [CODE LU].
- **EEVEE échoue** : `Couldn't open libEGL.so.1` [CODE LU]. Tous les rendus hors ligne passent donc par Cycles CPU.

---

### 20. GhibliGenerator
- **Identité** :
  - URL : https://github.com/SpectralVectors/GhibliGenerator. Auteur : SpectralVectors. 99 étoiles.
  - Licence : **GPL-3.0** (fichier LICENSE lu).
  - Dernier commit : 2022-07-13, version v0.8.5 ; l'extension cible Blender 2.80+ [CODE LU].
  - Taille : environ 7 600 lignes de Python, dont beaucoup de fichiers `Drivers/*.py`.
  - Homonymes sans rapport (générateurs d'images « style Ghibli » par IA) : Kshitiz-98-coder, ranjiofficio, preethpjm, White7007. Le bon dépôt est celui de SpectralVectors.
- **Ce que c'est vraiment** : une extension Blender qui crée par script des objets et des matériaux procéduraux « anime » [CODE LU] :
  - effets : Explosion, EnergyRing, EnergySphere, ElectricArcSphere, SmokeCloud, SmokeRing, SmokeTrail, FirePlane, HeatRipple ;
  - « Action Planes » (lignes de vitesse) et flashs (Color, Gradient, Circular) ;
  - sols et ciels.

  Aucune fonction d'export de spritesheet [CODE LU].
- **Comment ça marche** : chaque `Objects/<X>.py` expose une fonction `generate<X>()` [CODE LU] qui :
  - ajoute une primitive (`bpy.ops.mesh.primitive_*`) ;
  - empile les modificateurs Subsurf → Displace (texture `CLOUDS`) → Subsurf ;
  - construit un matériau par nœuds : Fresnel/Voronoi/Wave → ColorRamp en interpolation `CONSTANT` (c'est le rendu cel en aplats) → Emission mélangée à Transparent.

  Exemples : `Objects/Explosion.py` utilise une rampe blanc→jaune→orange→gris à positions 0 / 0,034 / 0,056 / 0,114 / 0,5 et une émission de 10. `Objects/EnergyRing.py` est un cylindre ouvert, déplacé en Z par un groupe de sommets, avec une texture Wave SAW et Voronoi étiré (échelle 20 / 0,1 / 1).

  Tout est impératif (bpy.ops), sans format de données.
- **Essai réel (bpy 5.0.1)** :
  - Tel quel, les 9 générateurs d'effets **plantent** : `'Material' object has no attribute 'shadow_method'`. Cette propriété a été supprimée dans Blender 4.2+ [CODE LU].
  - Après une rustine d'une ligne (commenter `shadow_method` dans une copie), **les 9 fonctionnent** [CODE LU].
  - J'ai animé l'échelle de l'explosion et le décalage de la texture de bruit (un empty sert de `texture_coords_object`, ce qui fait « bouillir » le bruit), puis rendu 16 images de 256 px avec Cycles CPU, 16 échantillons, fond transparent (`film_transparent`, RGBA). Durée : **environ 16 s**. Anneau d'énergie : 5 s.
  - `sheet.py` (PIL, environ 15 lignes) assemble une **feuille 4×4 de 1024×1024, avec un alpha propre (0 à 255)**. Fichiers : `essais/out/explosion_4x4_1024.png` et `energyring_4x4_1024.png`.
  - Deux constats :
    - il faut `view_transform='Standard'`, sinon AgX délave les couleurs ;
    - les assets bruts sont pensés pour une caméra en perspective (Fresnel) : en vue orthographique de face, l'explosion est plate, en aplats jaunes. Il faut une direction artistique pour obtenir la qualité TSB.
- **Ce qu'on peut en tirer** : les **recettes de shader** plutôt que le code.
  - Rampe `CONSTANT` pilotée par Fresnel pour des bandes façon cel.
  - Displace par bruit animé via un empty pour le bouillonnement.
  - Voronoi étiré par Mapping pour des filaments d'énergie.
  - Mélange Emission/Transparent piloté par une rampe pour découper la silhouette.

  Combinées à notre propre boucle rendu → feuille (celle de l'essai), on a un pipeline de flipbooks hors ligne.
- **Limites / risques** :
  - GPL-3 : ne rien intégrer tel quel dans notre dépôt. Les images rendues ne sont a priori pas concernées [DÉDUIT].
  - Projet abandonné depuis 2022 et cassé sur Blender 4.2+.
  - `register()` active `add_curve_sapling` et `node_arrange`, deux extensions devenues externes [CODE LU].
  - EEVEE est indisponible ici, donc Cycles, plus lent.
- **Verdict** : **S'INSPIRER**, priorité **3**. Recopier 4 ou 5 recettes de nœuds dans notre propre script bpy, jamais le code lui-même.

### 21. SMEAR
- **Identité** :
  - URL : https://github.com/MoStyle/SMEAR. Auteurs : Jean Basset, Pierre Bénard, Pascal Barla (Inria), article SIGGRAPH 2024.
  - Licence **ambiguë** : `LICENSE.md` et les en-têtes SPDX disent **CeCILL-2.1** ; `blender_manifest.toml` dit `GPL-3.0-or-later`. Les deux sont copyleft et compatibles entre elles [CODE LU].
  - Dernier commit : 2025-11-20, version 1.1.8, Blender 4.2 minimum.
  - Taille : environ 1 010 lignes de Python, plus **un .blend de 21 Mo qui contient les arbres Geometry Nodes : le cœur de l'effet est en binaire, pas en code lisible**.
  - Homonyme : AIdanpdn/Blender-Smear-Rig (un seul .blend, pas de licence, 0 étoile), à ignorer.
- **Ce que c'est vraiment** : une extension qui calcule des « smear frames » sur une animation 3D [README + CODE LU] :
  - intervalles allongés (« elongated in-betweens ») ;
  - intervalles multiples (copies transparentes) ;
  - lignes de mouvement (tubes le long des trajectoires).
- **Comment ça marche** :
  - `deltas_generation_functions.get_animation_deltas_ribbon` projette, pour chaque image, chaque sommet sur la vitesse du centroïde. Avec une armature, le calcul se fait os par os : plan « ruban » entre les vitesses des deux articulations, poids en smoothstep, puis lissage temporel avec le noyau (1−x²)² [CODE LU].
  - Le résultat est stocké dans des attributs `delta_<frame>` sur les sommets.
  - Un modificateur GN, « Smear Frames Controler », est ajouté par append depuis le .blend. Ses entrées sont sérialisables : Smear Length, Past/Future Length, Weight by Speed, Activate Lines, Probability, Seed, Radius, Activate Multiples, etc. (liste relevée à l'exécution) [CODE LU].
- **Essai réel (bpy 5.0.1)** :
  - Test : `register()`, une sphère animée avec anticipation puis frappe rapide, `bpy.ops.scene.bake_deltas_and_trajectories()` → **FINISHED en 0,1 s, sans interface** [CODE LU].
  - Réglages : `Activate Elongated` et `Activate Lines` à True, Probability à 0,3. Rendu Cycles des images 6 à 10.
  - **Le smear allongé est bien visible** sur les images de frappe 7 et 8. Les lignes s'ajoutent en géométrie : la sphère passe à 44 002 sommets évalués. Fichier : `essais/out/smear_strip.png`.
- **Ce qu'on peut en tirer** :
  1. **Hors ligne** : appliquer SMEAR au bras R6 ou au poing pendant la frappe, puis soit rendre des sprites de smear (flipbook, plan face caméra), soit exporter le maillage déformé de 1 à 3 images comme MeshPart affiché uniquement sur ces images [DÉDUIT].
  2. **L'algorithme** (delta par sommet = projection sur la vitesse, allongement pondéré passé/futur, sélection des graines de lignes selon un seuil de vitesse) est court et réimplémentable dans notre propre bpy, ce qui éviterait la contrainte copyleft [DÉDUIT].
- **Limites / risques** :
  - Roblox ne déforme pas de maillage à l'exécution, hors peau (skinning) ou EditableMesh. Un smear 3D devra donc être précalculé [DÉDUIT].
  - La logique GN est enfermée dans le .blend.
  - Le résultat dépend de l'aléa pour les lignes (Seed) et le poids des lignes explose vite.
- **Verdict** : **S'INSPIRER**, priorité **4** : un outil de prévisualisation et de production hors ligne de maillages ou sprites de smear. Le réimplémenter si on veut l'intégrer à notre dépôt.

### 22. « Flipbook » (plusieurs projets portent ce nom)
Candidats trouvés :
- **nezuo/roblox-flipbook-packer** (le plus pertinent) :
  - https://github.com/nezuo/roblox-flipbook-packer, licence MIT (LICENSE.txt lu), dernier commit 2023-03-17, 355 lignes de Rust (eframe/egui + rfd).
  - Ce qu'il fait [CODE LU] : prend une séquence d'images ou une feuille, choisit la grille (≤4 images → 2×2 de 512 px ; ≤16 → 4×4 de 256 ; au-delà → 8×8 de 128), redimensionne en CatmullRom en gardant les proportions, centre chaque image dans sa cellule et produit **toujours du 1024×1024**. Au-delà de 64 images, rien n'est prévu. Il sait aussi découper une feuille en séquence.
  - Uniquement une interface graphique (boîtes de dialogue), pas de ligne de commande.
- zZfriend123321/VfxFlipbookStudio (« Easy VFX ») : le dépôt ne contient qu'un README d'une ligne et PRIVACY.md. C'est une application de bureau fermée, sur GPU, avec un nœud « AI Edit » optionnel [README]. Pas de code ; seule l'idée est évaluable.
- GandalfWisdom/FlipbookBuddy : MIT, 326 lignes de Luau, 2025-12. Il anime une **ImageLabel** d'interface via `ImageRectOffset`/`ImageRectSize` et lit la résolution avec `AssetService:CreateEditableImageAsync` [CODE LU]. Il dépend de Nevermore et suppose une grille carrée.
- flipbook-labs/flipbook : un Storybook pour l'interface Roblox, homonyme sans rapport.

**Questions clés**
- **Blender en ligne de commande** : sans objet pour ces outils (Rust ou Luau). Notre `sheet.py` en PIL remplace le packer en 15 lignes, testé.
- **Format Roblox** : voir la section 24. Grille 2×2, 4×4, 8×8 ou Custom ; 1024×1024 ; fond transparent ; **marge entre les images obligatoire** (le packer la crée de fait en centrant, mon essai ne l'avait pas).

- **Ce qu'on peut en tirer** :
  - **Réimplémenter les règles du packer en Python** dans notre outillage : choix de grille selon le nombre d'images, cellule = 1024 / N, centrage avec marge.
  - Ajouter la grille Custom (FlipbookSizeX/Y) et une **marge mip** configurable.
  - FlipbookBuddy donne le schéma pour animer nos **cartes d'impact plein écran** (ScreenGui/ImageLabel) à partir d'une feuille ; à réécrire en 30 lignes sans Nevermore [DÉDUIT].
- **Limites** : le packer est ancien (il ignore la grille Custom apparue depuis), l'interface ne se scripte pas, et Studio Easy VFX est fermé.
- **Verdict** : packer → **S'INSPIRER** (règles à reprendre en Python), priorité **4**. FlipbookBuddy → **S'INSPIRER**, priorité **2**. VfxFlipbookStudio → **IGNORER**, priorité 1.

### 23. Babylon Quarks Standalone
- **Identité** :
  - URL : https://github.com/Soullnik/babylon.quarks-standalone. Auteur : Mikalai Lazitski (soullnik). Licence **MIT** (LICENSE lu). Dernier commit : 2026-07-29. 9 étoiles.
  - Taille des sources hors tests : `quarks.core` 11 730 lignes, `babylon.quarks` 6 403, `babylon.quarks-editor` 9 322 [CODE LU].
  - Moteur d'origine : Alchemist0823/three.quarks, MIT, 1 039 étoiles, dernier commit 2026-05-20. Il contient aussi `quarks.nodes`, un graphe de nœuds VFX avec interpréteur et compilateurs WebGPU et WASM (environ 2 900 lignes) [CODE LU].
- **Ce que c'est vraiment** : un système de particules façon Unity Shuriken, avec un éditeur à pile de modules (Main, Emission avec rafales, Shape, Speed / Force / Color / Size / Rotation over Life, Noise, Texture Sheet, Renderer, Sub-emitters), une timeline, l'annulation, un export et un import JSON [README + CODE LU]. `docs/SHURIKEN_PARITY.md` est une matrice de parité avec Unity, bien faite [CODE LU].
- **Comment ça marche / format** : JSON sérialisable (`examples/public/*.json`, lu) [CODE LU].
  - Clés `ps` : `duration`, `looping`, `startLife`, `startSpeed`, `startSize`, `startColor`, `emissionOverTime`, `emissionBursts`, `shape`, `renderMode`, `uTileCount`/`vTileCount`/`startTileIndex`, `blending`, `behaviors[]`.
  - Valeurs typées : `ConstantValue`, `IntervalValue{a,b}`, `PiecewiseBezier{functions:[{function:{p0..p3},start}]}`, `Gradient` de `ColorRange`.
  - Comportements, par exemple `SizeOverLife{size}` et `FrameOverLife{frame}` (numéro de tuile selon la vie).
  - `PiecewiseBezier.refreshTable` échantillonne la courbe sur 257 points.
  - `editor/core/scrub.ts` rejoue la simulation à pas fixe (1/60) pour se positionner à un instant t : c'est l'idée d'une timeline déterministe.
- **Ce qu'on peut en tirer (idées transposables)** :
  1. **Taxonomie des valeurs** (constante / intervalle / courbe / dégradé) pour nos données d'événements, puis **compilation vers Roblox** :
     - `IntervalValue` → NumberRange ;
     - courbe → NumberSequence de **20 points au maximum** (limite officielle, voir la section 24). Il faut échantillonner puis simplifier (type RDP) ;
     - `Gradient` → ColorSequence (20 points au maximum), avec la transparence séparée dans son propre NumberSequence ;
     - `FrameOverLife` et les tuiles → FlipbookLayout Custom + FlipbookMode OneShot ;
     - `emissionBursts` → `Emit(n)` programmés sur nos marqueurs.
  2. **Matrice de parité « Roblox »** sur le modèle de SHURIKEN_PARITY.md : signaler ce que Roblox ne sait pas faire [DÉDUIT d'après les docs Roblox lues] : pas de SpeedOverLife en courbe (seulement Drag et Acceleration), pas de RotationOverLife en courbe (RotSpeed constant ou aléatoire), pas de bruit ni de turbulence, pas de sous-émetteurs natifs.
  3. **Scrub par re-simulation à pas fixe** pour que le lecteur three.js reste synchrone avec les marqueurs d'animation.
  4. Pour l'aperçu three.js, **ne pas adopter quarks tel quel** : il ferait plus que Roblox. Mieux vaut un simulateur qui imite exactement Roblox (NumberSequence linéaire avec enveloppe, Drag en demi-vie, SpreadAngle, modes de flipbook). La logique de batching de quarks (MIT) peut servir de référence [DÉDUIT].
- **Limites / risques** : dépend de Babylon ≥ 9 pour la version standalone ; l'éditeur React est lourd ; le modèle Unity est plus riche que Roblox, avec un risque d'aperçu mensonger.
- **Verdict** : **S'INSPIRER**, priorité **3**. Reprendre le format des valeurs typées, la matrice de parité et le scrub.

### 24. Documentation Roblox : Effects (Beam, Trail, ParticleEmitter, flipbooks)
- **Identité** : https://github.com/Roblox/creator-docs, commit `cc850a8` du 2026-09-25. Licence : textes CC-BY-4.0 (`LICENSE`), code MIT (`LICENSE-CODE`). Fichiers lus :
  - `content/en-us/effects/particle-emitters.md`, `beams.md`, `trails.md` ;
  - `reference/engine/classes/ParticleEmitter.yaml`, `Beam.yaml`, `Trail.yaml` ;
  - `reference/engine/enums/ParticleFlipbookLayout.yaml`, `ParticleFlipbookMode.yaml`, `ParticleFlipbookTextureCompatible.yaml`, `TextureMode.yaml` ;
  - `reference/engine/datatypes/NumberSequence.yaml`, `ColorSequence.yaml` ;
  - `art/modeling/texture-specifications.md`, `performance-optimization/improve.md`.

**Grille de flipbook personnalisée : CONFIRMÉE** [PAGE]
- `FlipbookLayout` (`Enum.ParticleFlipbookLayout`) : None = 0, Grid2x2 = 1, Grid4x4 = 2, Grid8x8 = 3, **Custom = 4**.
- Avec Custom, la grille est définie par **`FlipbookSizeX`** (colonnes) et **`FlipbookSizeY`** (lignes), deux entiers. **La référence les marque `serialization: can_load: true, can_save: true`, donc on peut les écrire dans un .rbxmx** [PAGE]. Leur nom exact dans le XML n'est pas vérifié [DÉDUIT].
- Aucune valeur maximale n'est documentée pour SizeX/SizeY [NON TROUVÉ].

**Propriétés flipbook de ParticleEmitter** [PAGE]
- `FlipbookFramerate` (NumberRange) : **30 images/s au maximum**.
- `FlipbookMode` : Loop = 0, **OneShot = 1** (la cadence vaut alors durée de vie / nombre d'images, et FlipbookFramerate est ignoré), PingPong = 2, Random = 3 (ordre aléatoire avec fondu enchaîné).
- `FlipbookStartRandom` (bool) : combiné à une cadence de 0, chaque particule affiche une image fixe tirée au hasard.
- **`FlipbookBlendFrames`** (bool, nouveau) : fondu linéaire entre images, ou changement instantané.
- `FlipbookIncompatible` (string) : le message d'erreur affiché.

**Taille de texture pour un flipbook : les docs se contredisent**
- L'énumération `ParticleFlipbookTextureCompatible` dit : « **Flipbook playback requires a 1024×1024 texture** », sinon l'état passe à NotCompatible et la lecture est désactivée. États : Unknown → Compatible ou NotCompatible, en lecture seule.
- `FlipbookIncompatible` dit au contraire : « texture size must be an **exact multiple of the flipbook layout size** ».
- Aucune propriété de classe exposant cette énumération n'a été trouvée [NON TROUVÉ].
- **Règle prudente : toujours livrer du 1024×1024.**

**Autres exigences sur les flipbooks** [PAGE]
- **Marge transparente entre les images obligatoire**, davantage à cause du mip-mapping.
- Les flipbooks coûtent de la mémoire ; sur les appareils à mémoire faible, **le client désactive automatiquement les flipbooks**. Réutiliser les textures.

**ParticleEmitter : autres limites** [PAGE]
- Lifetime plafonnée à **20 s**.
- Rate : **400 particules/s par émetteur (100 sur mobile)**. Le tutoriel du curriculum core règle pourtant Rate à 50 000 sur un très grand volume, ce qui contredit la limite.
- TimeScale de 0 à 1.
- LightEmission : 0 = mélange normal, 1 = additif.
- Size, Transparency et Squash sont des NumberSequence interpolées linéairement sur l'âge, avec une enveloppe aléatoire tirée à l'émission.
- **NumberSequence et ColorSequence : 20 points au maximum** (`NumberSequence.yaml` l.144, `ColorSequence.yaml` l.152).
- Orientation : FacingCamera, FacingCameraWorldUp, VelocityParallel, VelocityPerpendicular.
- Sphere et Cylinder s'affichent mal sous une Attachment.
- ZOffset en studs, fractionnaire.
- Méthodes : `Emit(n)`, `Clear()`.
- Pas de taille maximale de particule documentée [NON TROUVÉ].

**Beam** [PAGE]
- Segments : 10 par défaut. Il en faut au moins n−1 pour n points de couleur ou de transparence. Aucun maximum documenté [NON TROUVÉ].
- Brightness de 0 à 10 000.
- LightInfluence bornée de 0 à 1.
- TextureSpeed en cycles par seconde, négatif pour inverser le sens.
- TextureMode : Wrap ou Static (longueur / TextureLength) ; Stretch (TextureLength répétitions).
- CurveSize0/1 : courbe de Bézier.
- `SetTextureOffset(0..1)`.
- **Pas de flipbook sur Beam ni sur Trail** (on anime par défilement de texture).

**Trail** [PAGE]
- Lifetime **de 0,01 à 20 s** (2 s par défaut).
- WidthScale de 0 à 1 (multiplicateur de l'écart entre les deux attachments).
- MinLength / MaxLength (0 = sans maximum).
- TextureMode : Stretch, Wrap, Static (« tamponné »).
- `Clear()`.

**Textures** [PAGE]
- `texture-specifications.md` annonce « jusqu'à 4096×4096 » à un endroit et « 1024×1024 maximum » à deux autres.
- Formats acceptés : png, jpg, tga, bmp.
- Roblox peut réduire la résolution sous charge.

**Performance** [PAGE]
- Taille des particules → fill-rate.
- Superposition de transparences → overdraw.
- « Property changes to ParticleEmitters can have a dramatic impact on performance » : attention à notre module Luau qui modifie des propriétés à l'exécution [DÉDUIT].

- **Verdict** : **ADOPTER** comme référence normative, priorité **5**. Ces valeurs sont à encoder dans un validateur de nos données (grille, 1024, marge, ≤20 points, ≤30 images/s, ≤20 s, ≤400/s).

### 25. Documentation Roblox : curriculum Artiste / VFX
- **Fichiers lus** :
  - `tutorials/curriculums/artist/{index,work-with-particle-emitters,next-steps}.md` ;
  - `tutorials/curriculums/core/building/create-basic-visual-effects.md` ;
  - `tutorials/use-case-tutorials/vfx/{use-particles-for-explosions,custom-particle-effects,create-volcanoes,create-waterfalls,laser-traps-with-beams,basic-particle-effects}.md`.
- **Ce que c'est** : le curriculum « Intro to VFX art » (Mansion of Wonder) est **très débutant** [PAGE] : Color, Texture (identifiants d'une dizaine de textures de départ), Size de 1 à 10, Speed de 10 à 100, LightEmission, RotSpeed, Lifetime de 0,5 à 2 s. La matière utile est dans les tutoriels VFX.
- **Recettes relevées** [PAGE] :
  - **Explosion en rafale** : Texture `rbxassetid://6101261905`, Drag 10, Lifetime 0,2 à 0,6, Speed 20 à 40, SpreadAngle 180,180, Enabled désactivé, puis `Emit(100)` par script. Couleur en dégradé, transparence qui s'estompe en courbe.
  - **Fumée** : texture en niveaux de gris, bords flous, fond transparent (`rbxassetid://3845808160`). Transparency de 0 à 1, Size de 3 à 10, Color orange → gris foncé → blanc, Acceleration (2, 2, 0), Rate 40.
  - **Éclaboussures de lave en flipbook** (volcan) :
    - Grid8x8 en OneShot, Orientation FacingCameraWorldUp.
    - Size : points (0 ; 4,31 ± 0,762) et (1 ; 6,2 ± 0,875). Squash : (0 ; −0,075 ± 0,263) et (1 ; −0,413 ± 0,412).
    - ZOffset 1, Lifetime 1,5 à 2, Rate 0,37, Drag 0,5, LightEmission 0,1, LightInfluence 0,25.
    - Astuce anti-répétition : **deux émetteurs de flipbook légèrement différents** plus un remplissage.
    - SplashFill : Transparency aux points 1 / 0 à 0,19 / 0 à 0,795 / 1 ; Speed 12 à 20 ; Acceleration (0, −25, 0) ; LightEmission 1 ; LightInfluence 0 ; Brightness 8.
  - **Coulée de lave** : trois Beams superposés (couleur plate chaud → froid, croûte, même croûte avec attachments inversés et vitesse différente pour casser la répétition).
  - **Cascade** : Beam avec Width0 60 → Width1 20, TextureSpeed 0,4, TextureLength 64, Wrap, ColorSequence et Transparency à 5 ou 6 points. Chute : CurveSize0 10, CurveSize1 20.
  - **Laser** : Beam avec Texture `6060542021`, LightEmission 0,5, largeur 4, TextureSpeed 2.
  - **Reflet (flare)** : LightEmission 1 (additif), ZOffset 1, Rate 0,45, plus une PointLight de Brightness 2 et Range 36.
- **Verdict** : **S'INSPIRER**, priorité **3**. Ce sont des « recettes de référence » à convertir en entrées de notre base de recettes : l'explosion en rafale, les deux flipbooks désynchronisés et les Beams superposés s'appliquent directement à l'impact, à la fumée et aux rubans du dragon.

### 26. Documentation Roblox : Weapons Kit
- **Fichier lu** : `content/en-us/resources/weapons-kit.md` (520 lignes). Le code du kit est un modèle Marketplace, **absent du dépôt** [NON TROUVÉ].
- **Ce qu'on peut en tirer : le schéma de nommage déclaratif des effets** [PAGE]
  - **Projectile** : `ShotEffect` dans `Assets/Effects/Shots`, qui contient :
    - `Beam0`/`Beam1`, deux Beams de traînée entre `Attachment0` (arrière) et `Attachment1` (avant) ;
    - `TrailParticles` sous Attachment0 et `LeadingParticles` sous Attachment1 ;
    - `HitEffect` (Attachment déplacée au point d'impact) avec `HitSound` et `HitParticles`. La doc dit « Class.Sound » pour HitParticles : c'est une coquille, il s'agit d'un émetteur ;
    - `Mesh` pour un projectile visible.
  - **Configuration** : `ShouldMovePart`, `BeamFadeTime` (0), `BeamWidth0`/`BeamWidth1` (1,5 / 1,8), `NumHitParticles` (3), `HitParticlesUsePartColor`.
  - **Bouche du canon** : `MuzzleParticles` (`NumMuzzleParticles` 50) ; `MuzzleFlash` est un Beam entre `MuzzleFlash0` et `MuzzleFlash1`, avec `MuzzleFlashTime` 0,03 s, rotation aléatoire de −π à π et taille de 1 à 1.
  - **Traînée** : `TrailLength` ou `TrailLengthFactor` (multiplicateur de la distance parcourue sur la dernière image), `ShowEntireTrailUntilHit`.
  - **Marques d'impact** : `HitMarkEffect` (BulletHole) et `AlignHitMarkToNormal`, avec des enfants `Glow` (Decal qui s'efface vite), `BulletHole` (visible 4 s puis s'efface en 1 s), `ImpactBillboard`/`Impact` (ImageLabel qui grandit en 0,1 s puis rétrécit de moitié et s'efface en 0,1 s).
  - **Explosion** : `ExplodeOnImpact`, `BlastRadius` 8, `BlastPressure` 10 000, `BlastDamage` 100.
- **Verdict** : **S'INSPIRER**, priorité **3**.
  - La convention « le nom de l'instance est le rôle » (Beam0/1, TrailParticles, HitEffect, MuzzleFlash) plus des valeurs de configuration est un bon modèle de **gabarit de VFX sérialisable en .rbxmx**, piloté par un module générique.
  - Les timings de l'impact en billboard (0,1 s de croissance, 0,1 s de retrait) et du flash de bouche (0,03 s) servent de repères.

---

## Synthèse du groupe
1. **Chaîne de flipbooks hors ligne faisable dès maintenant, prouvée en essai** : bpy 5.0.1 avec **Cycles CPU** (EEVEE indisponible, pas de libEGL), fond transparent, vue « Standard », une image par pas, puis assemblage PIL en **1024×1024**, grille 2/4/8 ou Custom (FlipbookSizeX/Y), **avec marge**. Temps mesuré : environ 16 s pour 16 images de 256 px.
2. **Contenu** : réécrire nous-mêmes les recettes de nœuds de GhibliGenerator (GPL, cassé sur Blender 4.2+ faute de `shadow_method`) : explosion en aplats, anneau d'énergie, fumée, lignes de vitesse. **SMEAR** (CeCILL/GPL) fonctionne sans interface pour produire des smears et des lignes de mouvement de référence ; ces smears 3D devront être précalculés en sprites ou en MeshParts.
3. **Normes** : encoder les limites officielles dans un validateur :
   - flipbook 1024², marge, 30 images/s au maximum ;
   - durée de vie ≤ 20 s (particules) et de 0,01 à 20 s (Trail) ;
   - ≤ 400 particules/s ;
   - ≤ 20 points par séquence ;
   - Beam : segments ≥ points − 1.
4. **Modèle de données** : reprendre de quarks les valeurs typées (constante / intervalle / courbe / dégradé), compilées vers NumberRange ou NumberSequence ramenés à 20 points au plus, plus une matrice de parité Roblox. Reprendre du Weapons Kit la convention de nommage des rôles.
5. **Ce qui manque** :
   - un chemin automatisé pour **téléverser** les textures (Open Cloud Assets API) et récupérer les `rbxassetid` ;
   - la vérification réelle du nom XML de `FlipbookSizeX/Y` et du respect des 1024² ;
   - un maximum officiel pour Beam.Segments et Size [NON TROUVÉ] ;
   - un moteur de rendu anime rapide sans GPU : EEVEE est bloqué, Cycles est lent pour de gros volumes.
