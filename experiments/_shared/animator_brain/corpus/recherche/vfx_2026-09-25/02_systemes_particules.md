# Rapport du groupe 2 : systèmes de particules et d'émission Roblox

Dossier de travail : `/tmp/claude-0/-home-user-Jeux/4796ac9e-8e41-51f7-91c4-7b92a6a187d0/scratchpad/vfx/g2/`. Tous les dépôts y sont clonés en `--depth 1`. J'y ai aussi écrit un petit lecteur de `.rbxm` binaire, `_tools/rbxm_dump.py` (Python, lz4/zstd), qui extrait le code source des ModuleScripts. Je m'en suis servi pour lire le module d'exécution de Qwinkle (`_qwinkle_module_src/`, 69 fichiers). Rien n'a été écrit dans `/home/user/Jeux`.

---

### 4. Lumina

- **Identité** : https://github.com/Mqxsyy/Lumina (auteur Mqxsyy). Licence MIT (fichier LICENSE lu). Dernier commit sur `main` le 2024-07-21. Il existe une branche `1.0.0` (dernier commit le 2024-06-21, donc plus ancienne que `main`) et des tags 0.1.0 → 0.2.1. Taille : environ 13 900 lignes de TypeScript (roblox-ts) sur `main`, dont environ 5 600 pour l'API et le reste pour l'interface React ; environ 16 200 lignes sur la branche `1.0.0` [CODE LU]. Post DevForum : https://devforum.roblox.com/t/update-020-lumina-a-custom-particle-system/2963557. Dernier message en juillet 2026. Plaintes récurrentes sur les performances et le gel de l'éditeur de script ; le développement est présenté comme « intermittent » [PAGE]. Le README lui-même déconseille l'usage en production [README].
- **Ce que c'est vraiment** : un plugin Studio (éditeur de graphe à nœuds) plus une API de particules « maison » en Luau compilé depuis TypeScript. Il n'utilise pas le ParticleEmitter natif [CODE LU].
- **Comment ça marche** :
  - Architecture calquée sur le VFX Graph de Unity. Un `NodeSystem` possède des groupes Spawn, Initialize, Update, Render et Logic (`src/API/NodeSystem.ts`). Il n'accepte qu'un seul nœud Spawn (`ConstantSpawn` ou `BurstSpawn`) et un seul nœud Render [CODE LU].
  - Chaque particule est une `Part` tirée d'un `ObjectPool`, avec `SurfaceGui` et `ImageLabel` (`PlaneParticle.ts`). L'émission au-delà de 1 passe par `SurfaceGui.Brightness`. L'orientation peut être FacingCamera, VelocityParallel ou VelocityPerpendicular. La mise à jour se fait par `RenderStepped` et `Workspace:BulkMoveTo` ; `MeshParticle` et `VolumetricParticle` suivent le même schéma [CODE LU].
  - Flipbook : planche de sprites découpée par `ImageRectOffset`/`ImageRectSize`. L'image courante vaut `floor(frameCount × âge/durée de vie)` [CODE LU].
  - Données : un `savedata.json` (voir `examples/*/savedata.json`) liste des systèmes, chacun avec ses groupes, et dans chaque groupe des nœuds `{className, order, fields:[{name, data}]}` [CODE LU]. Pour le charger, il faut coller le JSON dans une `StringValue` puis cliquer sur « load » dans le plugin [CODE LU, `examples/howToLoadFromTextFile.txt`].
  - Exporter un effet revient à générer du code (`src/API/VFXScriptCreator.ts`). Le plugin écrit un ModuleScript dont chaque nœud s'imprime via `GetAutoGenerationCode()`. Le module exposé propose `.Start()` et `.Stop()`, et dépend de `ReplicatedStorage.Lumina_API`, installé par le plugin avec le `RuntimeLib` de roblox-ts [CODE LU].
  - Pas de marqueurs ni de chronologie. Pas d'imbrication. Pas de post-processing [CODE LU, aucun nœud correspondant].
- **Ce qu'on peut en tirer** :
  - La taxonomie Spawn / Initialize / Update / Render, comme schéma propre de nos émetteurs scriptés.
  - Le patron « graphe → génération de source Luau » (`VFXScriptCreator.ts` + `AutoGenLib.ts`) : c'est exactement notre démarche « chronologie Python → DragonFist.luau ».
  - La maths d'orientation VelocityParallel pour un plan tourné vers la caméra (`CheckOrientation` dans `PlaneParticle.ts`), utile pour des traits de vitesse en MeshPart si on sort du natif.
- **Limites / risques** :
  - Le coût est élevé : une Part plus un ou deux SurfaceGui par particule, et des écritures de propriétés à chaque image [CODE LU] ; les ralentissements sont confirmés sur le forum [PAGE].
  - Dépendance au runtime roblox-ts et au plugin ; version 1.0.0 inachevée ; l'auteur prévient lui-même.
- **Verdict** : **S'INSPIRER**, priorité 2. On retient le schéma de nœuds et la génération de code, pas le moteur.

---

### 5. Qwinkle's Part-Icles 2

- **Identité** :
  - Plugin : https://github.com/QwinkleTee/Qwinkles-Particles-2 (v40.2, commit du 2026-07-31). Il ne contient qu'un `.rbxm` et un `bundle.json` : le code est obscurci (`loadstring` et un blob encodé préfixé « LPH »). Tous droits réservés, décompilation interdite [CODE LU + README].
  - Module d'exécution : https://github.com/QwinkleTee/Qwinkles-Particles-2-Module (commit du 2026-07-30). Luau lisible : 69 ModuleScripts, 19 121 lignes, extraits avec mon outil [CODE LU].
  - Licence du module (`LICENSE.md` lu) : utilisation et modification dans ses propres jeux, pas de redistribution. Pour un usage commercial, une attribution visible est obligatoire.
  - Payant : 8 000 Robux ou 20 $, essai de 7 jours [README]. Documentation : https://www.qwinkleparticles2.com/ (vue seulement dans les résultats de recherche).
- **Ce que c'est vraiment** : le système de ce groupe le plus complet, de très loin. N'importe quelle instance devient un émetteur : Part, MeshPart, Model, Attachment, Beam, Trail, PointLight, Highlight, ImageLabel, Blur, Bloom, ColorCorrection, Atmosphere. S'y ajoutent des types spéciaux : CameraShake, Lightning, Rocks, Rope [CODE LU, `TypeRegistry`, `ScreenEmit`, `Highlight`, `CameraShake`, `Rocks`, `Lightning`].
- **Comment ça marche** :
  - **Données.** L'item « transformé » porte l'attribut `Transformed=true`, plus `EmitCount`, `EmitDelay`, `EmitDuration`. Ses enfants sont une `Configuration` nommée `PartIcleProperties`, qui contient environ 200 attributs (voir la liste dans `GetData.lua` : `Lifetime`, `Rate`, `Speed`, `BloomIntensity`, `CCTintColor`, `HLFillTransparency`, `FlipbookMode`, `TotalKeyFrames`…), et un `RenderTemplate` qui est le visuel cloné à chaque particule [CODE LU]. Tout est donc sérialisable en `.rbxmx` [DÉDUIT].
  - **Courbes.** Ce sont des `NumberSequence` natives stockées en attribut. Le champ `Envelope` de chaque point clé sert de variance par particule : une seule intensité aléatoire par particule, pour que les points voisins dérivent ensemble. L'échantillonnage se fait par recherche dichotomique puis interpolation linéaire (`Graph.lua`, `GenerateSeed` / `QueryPointsWithTime`) [CODE LU].
  - **API.** `Particle:Activate()` lance une seule boucle par image : `BindToRenderStep` côté client, `Heartbeat` côté serveur (`Engine.lua`). Les autres appels sont `AbsoluteEmit(root)`, `AbsoluteEmitAt(root, cf, opts)` (qui renvoie un `PlayHandle` offrant Disable, SoftDisable et SetTimescale pour une seule lecture), `AbsoluteEnable/Disable`, `AbsoluteSetTimescale(root, 0 = gel, <0 = lecture inversée)` et `Particle.await(durée)` [CODE LU + README].
  - `AbsoluteEmit` parcourt l'arbre. Sur un `ParticleEmitter`, un `Trail` ou un `Beam` natif, il lit les mêmes attributs `EmitCount/EmitDelay/EmitDuration` et appelle `:Emit(n)` ou active l'instance pendant la durée voulue. Un jeton de génération empêche un `Disable` d'être écrasé par un tir différé. Il renvoie la durée totale de l'effet, calculée récursivement (`Duration.lua`) [CODE LU, `Part_Icles.lua` l.305-395].
  - **Imbrication** (`NestedEmit.lua`) : au moment de l'émission, on parcourt le `RenderTemplate` source. Chaque nœud `Transformed` est tiré avec pour lien le clone parent (suivi de la position à chaque image) et un prédicat `parentAlive` qui tue l'enfant quand le parent meurt. Le jeton de lecture est propagé [CODE LU].
  - **Flipbooks** (`Flipbook.lua`) : on échange la texture d'un `Decal`, d'une `Texture`, d'un `Beam` ou d'une `MeshPart` à partir de décalques numérotés rangés dans un dossier `MeshFlipbooks` / `BeamFlipbooks`, donc un asset par image, préchargé par `ContentProvider:PreloadAsync`. L'index d'image suit le temps effectif, ce qui respecte l'échelle de temps et le gel [CODE LU]. Sur l'`ImageLabel`, c'est une planche de sprites [README].
  - **Post-processing** (`ScreenEmit.lua`) : Blur, Bloom, ColorCorrection ou Atmosphere est cloné dans `Lighting`, puis ses propriétés (`Intensity`, `Size`, `Threshold`, `Brightness`, `Contrast`, `Saturation`, `TintColor`…) sont animées par courbe sur la durée de vie, enfin le clone est détruit [CODE LU].
  - **Performance** : une seule boucle, une réserve de clones LIFO avec expiration, des mises à jour « par pas » (`TotalKeyFrames`, pour éviter d'écrire les propriétés à chaque image) et `BulkMoveTo` [CODE LU `Update.lua` + README].
  - **Rocks** : chaque trajectoire de débris (arcs, rebonds, pose finale) est entièrement précalculée au tir avec une douzaine de raycasts, puis jouée comme `pose(t)`. C'est déterministe et réversible [CODE LU, en-tête de `Rocks.lua`].
- **Ce qu'on peut en tirer** :
  1. **La convention d'attributs `EmitCount` / `EmitDelay` / `EmitDuration`** sur les émetteurs natifs. Spark (n°8) utilise la même : c'est de fait le standard de la communauté. En l'adoptant dans nos `.rbxmx` générés, nos modèles VFX deviennent jouables par ces outils et lisibles par les artistes.
  2. **`AbsoluteEmit(root)` renvoie la durée totale** : un seul appel pour tirer un arbre, et nettoyage automatique. À réécrire nous-mêmes (environ 60 lignes), pas à copier.
  3. **Courbe = `NumberSequence` avec `Envelope` comme variance** : un format natif Roblox, sérialisable, que notre Python sait produire.
  4. **Post-processing animé par courbe dans Lighting**, directement transposable à notre flash blanc et à nos cartes d'impact : Contrast/Saturation/TintColor de ColorCorrection, Bloom au moment de l'impact.
  5. **Échelle de temps et gel par arbre**, pour synchroniser le hitstop de l'animation avec les VFX.
  6. **Débris précalculés et déterministes**, pour le cratère de DragonFist (cohérent avec nos seeds).
  7. **L'imbrication « l'enfant suit le clone parent et meurt avec lui »**.
- **Limites / risques** :
  - Plugin payant et fermé ; Studio obligatoire pour composer un effet.
  - Le module ne peut pas être redistribué hors de nos jeux, et l'attribution est obligatoire en usage commercial.
  - Le format V2 n'est pas documenté et dépend de la version (« les anciens effets doivent être ré-enregistrés », dit le README).
  - Générer nous-mêmes un arbre `PartIcleProperties` serait fragile [DÉDUIT].
  - Je n'ai rien exécuté (pas de Studio) : les performances annoncées ne sont pas mesurées.
- **Verdict** : **S'INSPIRER** fortement, priorité 5. C'est la meilleure référence d'architecture du groupe. On pourrait l'**ADOPTER** comme moteur d'exécution seulement si Milan achète le plugin et accepte l'attribution. Même dans ce cas, je recommande de réécrire les 4 à 5 patrons ci-dessus dans notre propre module.

---

### 6. Voxel Particles Plugin

- **Identité** : https://github.com/WildCake/Voxel-Particles-Plugin (auteur WildCake). **Aucun fichier LICENSE**, donc tous droits réservés par défaut [CODE LU : absence]. Très actif : v26, commit du 2026-09-18. Environ 8 400 lignes de Luau (dont `VoxelParticleSystem.luau` : 2 753 lignes ; éditeur `init.legacy.luau` : 3 897 lignes), plus `tools/build_plugin.py` (486 lignes). Commentaires en russe. Post lié probable : https://devforum.roblox.com/t/voxel-particle-system/3980189 [PAGE non lue, résultat de recherche seulement].
- **Ce que c'est vraiment** : un système de particules « cubes » : chaque particule est une `Part` Neon anchored. Il est rendu côté client, et accompagné d'un plugin d'édition et de 32 préréglages [CODE LU].
- **Comment ça marche** :
  - Les **préréglages sont des tables Luau pures** (`Internal/BundledPresets/*.luau`, par exemple `Landing_1.luau`) : `burstCount`, `rate`, `maxParticles`, `perParticle = {size={min,max}, speed=…}`, courbes à 3 points `{start, mid, finish}`, `material`, `lodNear/lodFar`, `targetFps`, `visualUpdateStep`, graines de bruit [CODE LU].
  - Le déclenchement passe par un binder : tag CollectionService `VoxelEmitter`, attribut `VoxelPreset`, et attribut `VoxelBurst` pour les rafales (`VoxelEmitterBinderTemplate.luau`). L'API propose `VoxelParticleSystem.Attach(anchor, config)`, puis `Emitter:Emit(n)`, `SetEnabled`, `Configure`, `Destroy` [CODE LU].
  - Le coût est géré par une lourde infrastructure :
    - réserve de 512 Parts, dont le préchauffage crée au plus 8 Parts par image ;
    - budget global réparti équitablement entre émetteurs (`VoxelFairShareAllocator`) ;
    - admission par la caméra à 15 Hz ;
    - paliers de qualité (`ClientVfxQuality`) ;
    - rafales mises en file et plafonnées par image ;
    - `BulkMoveTo` [CODE LU, `Emitter:Emit` l.2459+, `createCube` l.437].
  - `build_plugin.py` construit un `.rbxmx` de façon déterministe (identifiants uuid5) à partir d'un manifeste JSON [CODE LU].
  - `AGENTS.md` et `LESSONS.md` montrent que le dépôt est piloté par un agent qui utilise le « Roblox Studio MCP officiel » pour inspecter Studio [CODE LU].
- **Ce qu'on peut en tirer** :
  1. **Préréglage = table Luau** : le format le plus simple à écrire pour un agent, et testable hors ligne avec notre binaire `luau`. C'est le bon modèle pour les paramètres de DragonFist.
  2. **La politique de budget** : distance, paliers de qualité, plafond de rafales par image ; à reprendre si nous créons des débris en Parts.
  3. **La construction déterministe de `.rbxmx` en Python** (idée, pas le code).
  4. **Le fichier `LESSONS.md`** comme journal d'erreurs lu par l'agent, proche de notre `CARNET.md`.
  5. Un piège documenté (`LESSONS.md`, v25) : appliquer la courbe de taille dès la naissance d'une particule, sinon elle apparaît une image à la mauvaise taille.
- **Limites / risques** : pas de licence, donc aucune réutilisation de code. Esthétique « cubes Neon » (style Minecraft), très éloignée du rendu anime. Coût processeur par Part.
- **Verdict** : **S'INSPIRER**, priorité 3 (format des préréglages, budget, outillage d'agent). Le moteur n'est pas pour nous.

---

### 7. OpenVFX

- **Identité** : https://github.com/Bloodhundur/OpenVFX (auteur « Shay »). Aucun LICENSE. Dernier commit le 2025-10-26. Script de 191 lignes, plus `VFXJSON.luau` de 26 329 lignes (données) [CODE LU]. Page Creator Store (asset 120478283866410) non consultable, create.roblox.com étant bloqué [NON TROUVÉ]. Homonymes sans rapport : l'organisation `openvfx/*` (outils Linux, 2015) et `mirelahmd/OpenVFX` (éditeur vidéo en Go) [CODE LU via recherche GitHub].
- **Ce que c'est vraiment** : un **navigateur de bibliothèque d'assets**, pas un moteur. Le plugin décode un JSON (Textures par catégorie, Beams, Artists) ; un clic insère une Part avec une Attachment et un `ParticleEmitter` configuré (`FlipbookLayout` Grid 2x2/4x4/8x8, `FlipbookMode` OneShot, 24 im/s) [CODE LU].
- **Comment ça marche** : chaque entrée a la forme `{Texture: "rbxassetid://…", Type: "Static" | "2x2" | "4x4" | "8x8", Resolution, Credits}`. J'ai compté environ 3 870 textures (Impact 694, Circle 478, Crescent 286, Smoke 235, Lightning 155, Slash 95…), réparties en 2 345 statiques et environ 1 520 flipbooks, plus environ 300 préréglages de Beam [CODE LU, décompte fait par script].
- **Ce qu'on peut en tirer** :
  - Un **catalogue JSON d'ID d'assets classés par type d'effet, avec leur grille de flipbook**. Il pourrait amorcer un choix de textures par l'agent (crescent, impact, slash), mais nous ne pouvons pas voir les images (create.roblox.com bloqué).
  - Le schéma `{Texture, Type grille, Resolution}` est un bon format pour **notre propre** catalogue de flipbooks rendus par Blender.
- **Limites / risques** : 3 783 crédits sur ~3 870 valent « ? », donc provenance et droits inconnus. Pas de licence. Aucune logique VFX.
- **Verdict** : **S'INSPIRER** (format du catalogue), priorité 2. Ne pas utiliser les ID en production sans vérifier les droits.

---

### 8. Spark

- **Identité** : https://github.com/rbxrootx/Spark (auteur rbxrootx). Le README annonce la licence MIT mais **il n'y a pas de fichier LICENSE** [CODE LU]. Un seul commit, le 2025-03-06. 93 lignes de Lua. C'est le seul dépôt « Spark » VFX Roblox trouvé ; aucun homonyme pertinent sur GitHub [CODE LU via recherche].
- **Ce que c'est vraiment** : un petit utilitaire qui lit les attributs `EmitCount`, `EmitDelay` et `EmitDuration` sur un `ParticleEmitter` et `EmitDelay` / `EmitDuration` sur un `Beam`. `ProcessVFXAttachment(root)` parcourt l'arbre récursivement [CODE LU].
- **Comment ça marche** : `task.delay` sert pour le délai. Pour la durée, une boucle `Emit(count)` et `task.wait(1/Rate)` s'exécute jusqu'à la fin [CODE LU].
- **Bugs relevés** [CODE LU pour le code, DÉDUIT pour la sémantique Roblox, non exécuté] :
  - `Emitter._CancelEmission = false` écrit un champ Lua sur une Instance. Roblox lève « not a valid member », donc **le module plante au premier appel**. Il faudrait passer par un attribut ou une table faible.
  - Avec `Rate = 0`, `task.wait(1/0)` devient une attente infinie.
  - `tick()` est déprécié.
- **Ce qu'on peut en tirer** : la confirmation de la convention d'attributs (voir n°5), et un contre-exemple instructif : l'annulation doit être indexée hors de l'Instance.
- **Verdict** : **S'INSPIRER** (la convention seulement), priorité 1. Ne pas prendre le code.

---

### 9. TARNATlON roblox-vfx

- **Identité** : https://github.com/TARNATlON/roblox-vfx (le nom s'écrit bien avec un L minuscule à la place du I). Auteur des commits : Micah Hinckley. LICENSE MIT (© 2019) lu. Dernier commit le 2020-08-07 ; dépôt créé en 2021 ; abandonné. 901 lignes de Lua, projet Rojo (`default.project.json`), avec une `TestPlace.rbxlx` [CODE LU].
- **Ce que c'est vraiment** : une mini-API de particules 3D (Parts) et une abstraction d'« Effect » [CODE LU].
- **Comment ça marche** :
  - `VFX.DescribeEmitter(id, props, precreated)` enregistre un descripteur : `Actor` (Part modèle), `Rate`, `Velocity`, `Acceleration`, `Drag`, `RotationalVelocity`, `Lifetime`, `ActorProps` et `Motors`. Chaque prop peut être une valeur, un `NumberRange` ou une fonction (`GetValue.lua`). `Motors` contient des fonctions `(delta, particle) → valeur` appelées à chaque image [CODE LU].
  - `VFX.CreateEmitter(id, extended)` renvoie un objet avec `:Start()`, `:Emit(n)`, `:Stop()`, `:Destroy()`. Une seule boucle Heartbeat met tout à jour, avec `BulkMoveTo` et `PartCache`. Le débit baisse au-delà de 45 studs de la caméra [CODE LU].
  - `VFX.DescribeEffect(id, {Play, Stop, Cancel})` puis `CreateEffect(id):Play(...)` : `Play` s'exécute dans une coroutine annulable (`SpawnCancellable.lua`) avec `wait` et `memory` injectés, et `Stop` nettoie via cette table `memory` [CODE LU].
  - **Le README est périmé** : il documente `CreateEmitter(props)`, alors que le code exige `DescribeEmitter` puis `CreateEmitter(id)` [CODE LU].
- **Ce qu'on peut en tirer** :
  - Le patron **Effect = Play / Stop / Cancel + mémoire + coroutine annulable**. C'est ce qu'il faut à DragonFist quand la technique est interrompue (stun en battlegrounds) : tout nettoyer proprement.
  - Les props de type « valeur, intervalle ou fonction », simples et lisibles.
  - `PartCache` (commentaire cité de zeuxcg : « CFrame est la seule propriété rapide »), qui résume le coût des particules 3D.
- **Limites / risques** : obsolète (`wait()`, pas de types) ; `Motors` écrit Size et Transparency à chaque image (coûteux) ; aucun support natif.
- **Verdict** : **S'INSPIRER**, priorité 2. Licence MIT, donc copiable, mais seule l'idée Play/Cancel vaut le coup.

---

### 10. ROBLOX Visual Effect System

- **Identité** : https://github.com/slitherylemur/ROBLOX-Visual-Effect-System (auteur slitherylemur). Aucun LICENSE. Un seul commit, le 2025-11-17. **Le dépôt ne contient qu'un README** : aucun code [CODE LU].
- **Ce que c'est vraiment** : le **plan de mémoire universitaire** d'un projet (diagramme de Gantt mermaid, janvier–mars 2025). Il prévoit : un schéma de données d'effet, un éditeur de chronologie à keyframes en plugin, la gestion d'assets (ParticleEmitter, Beam, Trail, Sound), un aperçu en temps réel via TweenService, une sérialisation vers ModuleScript, puis une API et un chargeur d'exécution [README].
- **L'idée** : c'est exactement notre architecture (chronologie → sérialisation en ModuleScript → exécution). Le projet ne nous apprend rien d'autre, puisque rien n'est implémenté publiquement. Le même auteur a un dépôt `pi-roblox-bridge` (TypeScript, 2026), non examiné [NON TROUVÉ, hors périmètre].
- **Avertissement** : la recherche web a aussi renvoyé `supportxauusdgobler-art/pulse-timeline-runtime` et `sathsaramusiccd-stack/Roblox-Timeline-Sync`. Ce sont des noms de comptes aléatoires avec des titres en « 2026 » bourrés de mots-clés, typiques des dépôts pièges (malware) optimisés pour le référencement [DÉDUIT]. Je ne les ai **pas** clonés ; à éviter.
- **Verdict** : **IGNORER**, priorité 1. Il confirme seulement que notre approche est la bonne.

---

## Réponses aux questions clés

**Particules 3D ou ParticleEmitter natif ?**
- Tous les systèmes « 3D » (Lumina, Voxel, TARNATlON, Qwinkle) paient la même chose : un script Luau tourne à chaque image, une Part est clonée et prise dans une réserve, et les positions passent par `BulkMoveTo` ; toute autre propriété écrite coûte cher [CODE LU dans les 4].
- Voxel a besoin d'une réserve de 512 Parts, d'une admission caméra, de budgets et de paliers pour tenir ; Qwinkle met ses mises à jour à pas discrets [CODE LU].
- Le natif, lui, est géré par le moteur, avec une seule Instance par émetteur [DÉDUIT, connaissance générale de Roblox].
- Règle pour nous : **natif** pour tout ce qui est billboard (étincelles, fumée, braises, flipbooks d'impact, anneaux en sprite). **Parts/MeshParts** seulement pour ce qui exige de la vraie géométrie ou un contrôle exact : débris du cratère (précalculés à la Qwinkle), dôme ou anneau de choc en MeshPart animé par courbe, éclairs segmentés. Toujours en petit nombre (dizaines, pas centaines).

**Description et déclenchement d'un effet** :
- Qwinkle et Spark : arbre d'instances, attributs `EmitCount/EmitDelay/EmitDuration`, puis `AbsoluteEmit(root)`, qui renvoie une durée.
- Voxel : table Luau, tag et attribut, puis `Emit(n)`.
- Lumina : JSON de nœuds exporté en ModuleScript `.Start()/.Stop()`.
- TARNATlON : descripteur plus `Effect:Play/Stop/Cancel`.
- Aucun ne se synchronise sur les marqueurs d'animation : c'est à nous de le faire (`GetMarkerReachedSignal`).

**Imbrication, flipbooks, post-processing** : seul Qwinkle les couvre tous les trois dans du code réel ; voir la fiche n°5 (`NestedEmit.lua`, `Flipbook.lua`, `ScreenEmit.lua`). Pour les flipbooks : grille native 2x2/4x4/8x8 sur ParticleEmitter (OpenVFX, Qwinkle) ; échange de texture image par image pour Beam et MeshPart (Qwinkle) ; `ImageRectOffset` pour ImageLabel et SurfaceGui (Lumina).

---

## Synthèse du groupe

Aucun moteur n'est à adopter tel quel. Qwinkle est excellent mais fermé et soumis à attribution ; les autres sont faibles, sans licence, ou sans code. Les pièces à assembler dans notre propre `DragonFist.luau` / runtime VFX :

1. **Préréglages en tables Luau** (façon Voxel), générés par Python et testés hors ligne avec `luau`.
2. **Modèles VFX `.rbxmx`** générés avec la convention `EmitCount` / `EmitDelay` / `EmitDuration`, plus une fonction `EmitTree(root) → durée`, recodée à la manière de Qwinkle.
3. **Courbes en `NumberSequence` avec `Envelope`** comme variance.
4. **Post-processing animé par courbe** (clone dans Lighting, puis destruction) pour le flash blanc et les cartes d'impact.
5. **Échelle de temps et gel des VFX** branchés sur le hitstop.
6. **Débris de cratère précalculés et déterministes** à partir de la seed.
7. **Effect Play/Cancel avec mémoire** (façon TARNATlON), pour nettoyer en cas d'interruption.
8. Un **catalogue maison de flipbooks** au format `{asset, grille, résolution}` (façon OpenVFX), alimenté par Blender.

**Ce qui manque partout** :
- la synchronisation sur les marqueurs de KeyframeSequence ;
- un aperçu hors Studio ;
- une mesure objective du coût (overdraw, nombre de particules) ;
- une chaîne d'upload d'assets sans Studio (create.roblox.com est bloqué chez nous).

Sources : [Lumina](https://github.com/Mqxsyy/Lumina), [fil DevForum de Lumina](https://devforum.roblox.com/t/update-020-lumina-a-custom-particle-system/2963557), [Qwinkles-Particles-2](https://github.com/QwinkleTee/Qwinkles-Particles-2), [Qwinkles-Particles-2-Module](https://github.com/QwinkleTee/Qwinkles-Particles-2-Module), [Voxel-Particles-Plugin](https://github.com/WildCake/Voxel-Particles-Plugin), [OpenVFX](https://github.com/Bloodhundur/OpenVFX), [Spark](https://github.com/rbxrootx/Spark), [roblox-vfx](https://github.com/TARNATlON/roblox-vfx), [ROBLOX-Visual-Effect-System](https://github.com/slitherylemur/ROBLOX-Visual-Effect-System).
