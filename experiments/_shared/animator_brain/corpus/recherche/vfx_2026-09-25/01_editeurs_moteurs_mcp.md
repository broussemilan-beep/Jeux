# Rapport groupe 1 : éditeurs et moteurs VFX, pilotage par agent

Dossier de travail : `/tmp/claude-0/-home-user-Jeux/4796ac9e-8e41-51f7-91c4-7b92a6a187d0/scratchpad/vfx/g1/`. Tous les dépôts y sont clonés en `--depth 1`. Rien n'a été écrit dans `/home/user/Jeux`.

Deux contraintes réseau pèsent sur la vérification :
- **Pages bloquées par le proxy** : glama.ai, lobehub.com, lobechat.com, itch.io, docs.zilibobi.dev, npmjs, web.archive.org.
- **apis.roblox.com est aussi bloqué** (testé : connexion refusée).

---

### 1. VFX Editor

- **Identité**
  - URL : https://github.com/VirtualButFake/vfx-editor (le même dépôt apparaît aussi sous l'alias `tijnepema/vfx-editor`).
  - Auteur : Tijn Epema.
  - Licence : **MIT** (LICENSE.md lu).
  - Dernier commit : 2024-11-18. Version 1.0.9 dans CHANGELOG.md, 1.0.8 dans wally.toml.
  - Taille : environ 14 400 lignes Luau (Fusion 0.2).
  - Autre candidat du même genre : `Mqxsyy/Lumina`, un système de particules custom avec éditeur à nœuds. Il n'a pas été cloné, car hors du périmètre « éditeur des propriétés natives ». VirtualButFake est le bon dépôt pour ce nom.
- **Ce que c'est vraiment**
  - Un plugin Studio qui remplace la fenêtre Propriétés pour ParticleEmitter, Beam, Trail et les conteneurs [CODE LU : `src/lib/classDataHandler/classes/{particleEmitter,beam,trail,container}.luau`].
  - Il ajoute un éditeur de NumberSequence avec easings et Bézier, un éditeur de ColorSequence et une « bibliothèque de textures » avec flipbooks [CODE LU].
  - Ce n'est pas un moteur d'exécution : il n'y a aucun module runtime à embarquer dans le jeu [CODE LU].
- **Comment ça marche**
  - Tout vit dans Studio. Les courbes éditées sont gardées dans un attribut JSON sur l'instance : `SetAttribute(attributeName, HttpService:JSONEncode(points))`. Chaque point a la forme `{index, value, envelope, easingMode ∈ back|bounce|cubic|elastic|expo|linear|quad|quart|quint|sine|bezier, direction In|Out|InOut, handle1/handle2}` [CODE LU : `numberSequence/editor.luau` l.393-515]. Le nom d'attribut pour les Trails est `_vfxEditorGraph<Prop>` [CODE LU : `trail.luau` l.159].
  - L'échelle d'un effet est dans l'attribut `_vfxEditorScale` [CODE LU].
  - La prévisualisation « Emit » lit les attributs `EmitCount` (défaut 20) et `EmitDelay`, puis appelle `task.delay(delay, Emit)` [CODE LU : `particleEmitter.luau` l.25-40].
  - La bibliothèque de textures s'importe et s'exporte en JSON : `{name, content:[{name, id, flipbookLayout: "2x2"|"4x4"|"8x8"}]}` [CODE LU : `texturePicker/modals/importJson.luau`].
- **Ce qu'on peut en tirer**
  - **L'algorithme courbe → NumberSequence limitée à 20 keypoints** : `compressPoints` puis `numberTableToSequence` dans `numberSequence/editor.luau` (l.172-385) [CODE LU]. Il échantillonne une courbe à easing, supprime les points colinéaires, puis rééchantillonne selon le niveau de détail pour respecter la limite Roblox de 20 keypoints. C'est exactement ce dont a besoin notre chronologie Python quand elle émet des Size/Transparency de ParticleEmitter. La licence MIT permet de le porter en Python.
  - **La convention d'attributs `EmitCount`/`EmitDelay`**, qui est aussi celle de VFX Forge (voir n°2). Elle devient de fait un standard communautaire [CODE LU dans les deux dépôts].
  - Le format JSON de la bibliothèque de textures, pour cataloguer nos flipbooks générés hors ligne [CODE LU].
- **Limites / risques**
  - Projet dormant depuis novembre 2024.
  - Dépend entièrement de Studio.
  - Pas de timeline, pas de Beam/Trail animés dans le temps, pas de runtime.
- **Verdict** : **S'INSPIRER**, priorité **2**. On porte l'algorithme de compression à 20 keypoints en Python, et on s'aligne sur `EmitCount`/`EmitDelay`.

---

### 2. VFX Forge (module d'émission `forge-vfx` + plugin)

- **Identité**
  - Module runtime : https://github.com/zilibobi/forge-vfx.
  - Auteur : zilibobi.
  - Licence : **VFX-DL 1.1**, une licence maison « source-available copyleft » (LICENSE lu).
  - Dernier commit : 2026-07-26. Version 2.4.0 (Wally `zilibobi/forge-vfx@2.4.0`, npm `@zilibobi/forge-vfx`).
  - Taille : environ 9 550 lignes Luau dans `src/`, dont `lightning.luau` à 1 191 lignes et `mesh.luau` à 474.
  - Documentation : https://github.com/zilibobi/vfx-forge (site Next/MDX, **MIT**, dernier commit 2025-09-30, environ 1 250 lignes de contenu).
  - Plugin : fermé et payant (15 $ sur le Creator Store). La v2 est obfusquée, sous liste blanche, et distribuée par Discord [PAGE : DevForum 3867553].
- **Ce que c'est vraiment**
  - Le plugin est l'éditeur ; son code n'est pas disponible.
  - Le dépôt `forge-vfx` est le **moteur d'exécution** qui rejoue en jeu les effets créés dans Studio [CODE LU].
  - Types d'effets pris en charge [CODE LU : `src/emitters.luau`, `src/effects/*`] :
    - ParticleEmitter en burst ou en durée ;
    - Beam avec longueur et largeur animées, et flipbook ;
    - Trail ;
    - Mesh VFX (parts « Start » et « End » interpolés, flipbooks de Decal) ;
    - Bézier 3D ;
    - éclair (Lightning) ;
    - shockwaves : anneau, lignes, débris de roches ;
    - modèle en rotation ;
    - tremblement de caméra (Shake de sleitnick, MIT, vendorisé) ;
    - effet écran : une Part collée devant la caméra ;
    - Sound ;
    - tweeners et randomizers de n'importe quelle propriété ou attribut.
- **Comment ça marche**
  - **Format entièrement déclaratif** : des instances Roblox natives, plus des **attributs** et des **tags CollectionService**. Aucun script par effet.
  - Le dispatch se fait selon ClassName et tags [CODE LU : `emitters.dispatch`]. Tags : `BezierParticle`, `LightningBolt`, `Shockwave`, `CameraShake`, `PropertyTweener`, `AttributeTweener`, `PropertyRandomizer`, `AttributeRandomizer`, `ConstantVFX`, `LoadVFXTextures` (`src/mod/utility.luau` l.22-37).
  - Conventions de structure [CODE LU + docs MDX] :
    - un Mesh VFX est un `Model` contenant `Start` et `End` ;
    - les shockwaves sont une `Part` placée dans un dossier nommé `Rings`, `Lines` ou `Debris`, avec une Attachment taguée `Shockwave` ;
    - un effet écran est une `BasePart` avec l'attribut `Enabled=true` ;
    - un tweener est une `RayValue` dont le nom est la propriété visée ; la cible est le parent ou une `ObjectValue`, et la valeur finale est dans `_END_VALUE`.
  - Environ 150 attributs sont reconnus : `EmitDelay`, `EmitCount`, `EmitDuration`, `DestroyDelay`, `RepeatCount`, `SyncPosition`, `*_Start`/`*_End`/`*_Curve`/`*_Duration`, `Flipbook*`, etc. [CODE LU : grep de `attr.get`]. La documentation MDX sous MIT en donne une référence lisible par machine (`src/generics/attributes.ts`, `curves.ts`).
  - **Courbes** : un attribut *string* contient un buffer binaire de float32. Pour chaque point : position, puis tangentes gauche et droite, avec des blocs de 24 octets [CODE LU : `src/mod/common/path.luau`, `serializePath`/`deserializePath`]. L'évaluation est `alpha = 1 - bezier:getEase(t).y` (convention « Y vers le bas » de l'UI) [CODE LU].
  - **Flipbooks** : un buffer de float64 contenant les assetId [CODE LU : `src/mod/common/flipbook.luau`].
  - API : `vfx.init()` côté client, puis `vfx.emit(inst, …) → {Finished: Promise, Clear}`, `emitWithDepth`, `enable`/`disable` pour les effets continus, `retime`, `resize`, `recolor`, `cacheAttributes` [CODE LU : `src/init.luau`, `src/types.luau`].
  - Un « Schema » versionné sert aux descripteurs de propriétés [CODE LU : `src/schema.luau`]. Un système de « modifiers » (file de tweens et de random chaînés, codec versionné) est en cours d'écriture et n'est pas encore branché sur les effets [CODE LU : `mod/modifiers.luau`, `modifier_codec.luau`].
- **Y a-t-il un composer / une timeline ?**
  - **Pas de séquenceur explicite.** L'auteur le dit et renvoie vers Moon Animator [PAGE : DevForum].
  - **Mais il existe une timeline implicite, réutilisable en Luau à l'exécution** [CODE LU : `services/effects.luau`] :
    - `emit(model)` parcourt tous les descendants avec un seul `QueryDescendants` ;
    - chaque effet part dans sa propre Promise et attend son propre `EmitDelay` ;
    - un dossier `EmitOnFinish` enchaîne des sous-effets à la fin d'un effet ;
    - `retime(factor)` met à l'échelle tous les `EmitDelay` et `DestroyDelay`.
  - Notre chronologie Python (impact à t0, aura, dôme à t1…) se traduit donc directement en **un Model dont chaque enfant porte son `EmitDelay`**. Un seul `vfx.emit(clone)`, appelé depuis un marqueur d'animation, rejoue toute la séquence [DÉDUIT à partir du code lu].
- **Un agent sans Studio peut-il écrire ce format ?**
  - **Oui, en principe** [DÉDUIT]. Le format se réduit à des instances natives, plus `AttributesSerialize` et `Tags` (deux champs BinaryString en base64 dans le .rbxmx). Notre `experiments/_shared/rbxm_reader.py` décode déjà le format binaire. Il faudrait un encodeur d'attributs (format rbx-dom, que je n'ai pas vérifié ici [DÉDUIT]) et le codec Bézier de 24 octets (trivial à porter).
  - **Non vérifié** : que le plugin relise sans perte un fichier produit ainsi. Le runtime, lui, se contente de lire les attributs.
- **Ce qu'on peut en tirer**
  1. **Moteur d'exécution tout fait** pour DragonFist.luau. Il couvre Beam animé, mesh VFX à flipbook, shockwaves avec débris, camera shake et effet écran (utile pour les cartes d'impact en 3D), pour un coût quasi nul.
  2. **Format cible** pour notre générateur Python : chronologie → .rbxmx « Forge-compatible ».
  3. Des patterns à reprendre même sans le module : pool d'objets (`obj/ObjectCache.luau`), mouvement des CFrame en lot, `retime`/`resize`/`recolor` en lot, randomizers déclaratifs.
  4. `scripts/roblox_cloud_test.py` [CODE LU] exécute des tests Luau sur de vrais serveurs Roblox via l'API Open Cloud « Luau Execution » (`apis.roblox.com/cloud/v2/universes/{u}/places/{p}/…`), **sans Studio**. C'est une bonne idée pour valider headless que nos .rbxm se chargent. En revanche, apis.roblox.com est bloqué depuis ce bac à sable, et il faut une clé API.
- **Limites / risques**
  - **La licence VFX-DL est très restrictive.** Le module n'est autorisé qu'à l'exécution d'une expérience Roblox (et dans la barre de commande Studio pour visualiser). Sont interdits : plugins, outils en ligne de commande, **harnais de test**. Toute modification redistribuée reste sous VFX-DL.
    - On ne peut donc **pas** le faire tourner sous Luau ou lune dans notre bac à sable.
    - Le piloter via `execute_luau` d'un MCP (contexte plugin) est une zone grise, probablement interdite [DÉDUIT de l'article 3.c].
    - On ne peut pas le porter dans l'aperçu three.js. Réimplémenter les *sémantiques* à partir de la documentation MIT reste possible [DÉDUIT].
  - Le plugin est payant, fermé et obfusqué ; ses mises à jour passent par Discord.
  - Les textures restent des `rbxassetid` : il faut toujours les uploader, et create.roblox.com est bloqué.
  - Un seul auteur. Le projet est actif en 2026.
- **Verdict** : **ADOPTER** le **format** (instances, attributs, tags, `EmitDelay`) et le **module d'exécution dans le jeu**, sous réserve que Milan accepte la VFX-DL. **S'INSPIRER** pour tout ce qui tourne hors du jeu. Priorité **5**.

---

### 3. VFX Forge MCP

- **Identité**
  - URL attendue : `github.com/zilibobi/vfx-forge-mcp`. **Elle renvoie 404** : dépôt privé ou supprimé. `git ls-remote` échoue, et le dépôt n'apparaît pas dans la liste des 12 dépôts publics de zilibobi [PAGE : github.com/zilibobi].
  - Fiches catalogue sur Glama et LobeHub : bloquées par le proxy. **Tout ce qui suit vient des extraits de moteur de recherche** [PAGE, extraits de recherche seulement]. Licence, taille et date sont [NON TROUVÉ].
  - Aucune mention du MCP dans `forge-vfx` ni dans la documentation [CODE LU : grep].
- **Ce que c'est vraiment** [PAGE, extraits]
  - Un serveur MCP en stdio côté agent et un **WebSocket vers le plugin VFX Forge dans Studio**. Port `VFX_FORGE_PORT`, 3847 par défaut.
  - Il faut activer un « MCP bridge » dans les réglages du plugin.
  - Outils annoncés : explorer le DataModel ; créer, modifier et supprimer des instances ; modifier propriétés et attributs ; utiliser *partiellement* les outils VFX Forge ; documentation Roblox hors ligne.
- **Exige-t-il Studio ouvert ?**
  - **Oui**, ainsi que le plugin payant VFX Forge v2 [PAGE, extraits].
  - Le serveur tourne en local sur la machine de Milan. Notre bac à sable dans le cloud ne peut pas joindre son `localhost` ; il faudrait donc Claude Code **lancé sur le PC de Milan** [DÉDUIT].
- **Le jour où Studio est ouvert** [DÉDUIT] :
  - Claude génère le .rbxmx au format Forge. Il le fait importer, puis lance l'émission, règle les attributs par itérations et relit l'arbre.
  - Pour « voir » le résultat, il faut un outil de capture d'écran. **Rien n'indique que ce MCP en ait un.** Le fork 6xvl (voir n°14) en a un.
- **Verdict** : **S'INSPIRER / en attente**, priorité **2**. On ne peut rien adopter tant que le code est introuvable. L'idée d'un « bridge vers l'éditeur VFX » est bonne, mais un MCP Studio générique ouvert (n°14, alternatives) fait la même chose sans dépendre d'un plugin fermé.

---

### 14. RobloxForge

- **Candidats**
  - **ShugokiFable/RobloxForge** : le nom exact, https://github.com/ShugokiFable/RobloxForge. **MIT** (LICENSE lu), dernier commit 2026-09-13, v0.1.1, environ 3 150 lignes (Python + PowerShell). **Il n'a aucune fonction VFX** [CODE LU : grep, deux mentions génériques « VFX » et « particle counts » dans des références de design et de performance].
  - `RobloxForge-Studio-Scripters/...` : dépôt de scripts d'exploit (autofarm). À **ignorer**.
  - Les MCP Roblox qui ont **réellement** des fonctions VFX, et correspondent donc mieux à « agent/MCP avec fonctions VFX » [CODE LU pour chacun] :
    - **6xvl/robloxstudio-mcp-server** : MIT, 2026-08-24, environ 13 850 lignes TS. Outils `particle_create`, `particle_tune`, **`capture_screenshot`**, `import_rbxm`/`export_rbxm`, `eval_client_runtime`, profileurs.
    - **princeofscale/bloxforge** : MIT, 2026-09-01. Beams dans son constructeur de scènes, option `withPostFx` (Bloom, ColorCorrection, SunRays), captures d'écran annoncées [README].
    - **boshyxd/robloxstudio-mcp** : MIT, 2026-06-06, la souche d'origine.
  - Choix le plus plausible pour ce que Milan a vu : **ShugokiFable/RobloxForge** pour le nom. Pour les « fonctions VFX », c'est probablement une confusion avec **6xvl** ou **bloxforge** [DÉDUIT].
- **Ce que c'est vraiment (ShugokiFable)** [CODE LU + README]
  - Une « couche d'intelligence » par-dessus le **MCP Studio officiel de Roblox**.
  - Deux skills : `roblox-game-development` et `roblox-docs`.
  - Un MCP de 11 outils `rb_*` : doctor, recherche dans la doc (cache épars de `Roblox/creator-docs`), plan en tranches verticales, revues, « reçus de vérification » [CODE LU : `mcp_server/server.py`].
  - Installation Windows uniquement (scripts `.ps1` et `.bat`).
- **Ce qu'on peut tirer du groupe MCP pour le jour où Studio est ouvert**
  - Avec 6xvl, en local chez Milan : `import_rbxm` de notre effet, lancement d'un playtest, `eval_client_runtime` pour appeler `shared.vfx.emit(...)` en contexte runtime (autorisé par la VFX-DL), puis profilage (`capture_micro_profiler`, `get_scene_analysis`) pour mesurer le coût.
  - **Limite importante de la capture** : `capture_screenshot` repose sur `CaptureService.CaptureScreenshot` et `EditableImage`. Elle exige « Allow Mesh / Image APIs » et **ne marche qu'en mode Edit, viewport visible**, avec une attente d'au moins 0,1 s par capture [CODE LU : `studio-plugin/src/modules/handlers/CaptureHandlers.ts`].
    - On ne peut donc pas filmer image par image un effet d'une seconde.
    - Il faudrait un mode « scrub(t) » déterministe dans DragonFist (ou geler `TimeScale=0` sur les émetteurs) pour photographier la chronologie à des instants t donnés [DÉDUIT].
  - Idée à garder de RobloxForge : une doc officielle en cache local (`roblox-docs`) et des « reçus » de vérification. C'est proche de notre règle « captures committées comme preuve ».
- **Limites / risques**
  - RobloxForge : Windows seulement, pas de VFX, benchmark E2E pas encore fait [README].
  - Tous les MCP Studio exigent Studio ouvert, un plugin installé et HTTP autorisé.
- **Verdict**
  - RobloxForge (ShugokiFable) : **IGNORER**, priorité **1** (s'en inspirer au plus pour l'idée de doc locale et de reçus).
  - **6xvl/robloxstudio-mcp-server** comme MCP le jour où Studio est ouvert : **S'INSPIRER / préparer**, priorité **3**.

---

## Synthèse du groupe

1. **La pièce maîtresse est `forge-vfx`.** Son format est déclaratif et natif (instances, attributs, tags). Sa timeline implicite (`EmitDelay`, `EmitOnFinish`, `retime`) épouse notre chronologie d'événements. Son moteur d'exécution couvre Beam animé, mesh à flipbook, shockwaves, camera shake et effet écran.
2. **Ce qu'on assemble** : chronologie Python → **générateur .rbxmx « Forge-compatible »**. Il faut écrire l'encodeur `AttributesSerialize` et `Tags`, porter le codec Bézier de 24 octets, et reprendre la compression à 20 keypoints de VFX Editor (MIT). Ensuite, `DragonFist.luau` se réduit à « cloner le Model de l'effet, le positionner, `vfx.emit` au marqueur d'animation ».
3. **Point bloquant à trancher par Milan : la licence VFX-DL.** Elle permet l'usage en jeu, y compris commercial, mais interdit tout outil, CLI ou harnais de test, et impose le copyleft. On ne peut pas l'exécuter dans notre bac à sable. Sinon, on garde notre propre runtime et on reprend seulement les *idées* et le *format*.
4. **Ce qui manque** :
   - (a) une vérification que le plugin VFX Forge relit nos fichiers générés : il faut Studio une fois ;
   - (b) un moyen de *voir* le rendu Roblox sans Studio : aucun trouvé ; Open Cloud Luau Execution est headless sans image et bloqué ici ;
   - (c) le code du VFX Forge MCP, introuvable (404) ;
   - (d) l'upload des textures et flipbooks, bloqué (create.roblox.com).
5. **Le jour où Studio est ouvert**, on lance Claude Code en local chez Milan avec un MCP Studio ouvert (6xvl), plutôt que le MCP fermé de VFX Forge : on importe le .rbxm, on émet en playtest, on capture en mode Edit à des instants gelés, et on profile.

## Sources
- [zilibobi/forge-vfx](https://github.com/zilibobi/forge-vfx/) · [zilibobi/vfx-forge (docs)](https://github.com/zilibobi/vfx-forge) · [profil zilibobi](https://github.com/zilibobi?tab=repositories)
- [DevForum : VFX Forge](https://devforum.roblox.com/t/plugin-vfx-forge-an-advanced-custom-vfx-system/3867553) · [Glama : VFX Forge MCP](https://glama.ai/mcp/servers/zilibobi/vfx-forge-mcp) et [LobeHub](https://lobehub.com/mcp/zilibobi-vfx-forge-mcp) (extraits de recherche seulement)
- [VirtualButFake/vfx-editor](https://github.com/VirtualButFake/vfx-editor) · [Mqxsyy/Lumina](https://github.com/Mqxsyy/Lumina)
- [ShugokiFable/RobloxForge](https://github.com/ShugokiFable/RobloxForge) · [6xvl/robloxstudio-mcp-server](https://github.com/6xvl/robloxstudio-mcp-server) · [princeofscale/bloxforge](https://github.com/princeofscale/bloxforge) · [boshyxd/robloxstudio-mcp](https://github.com/boshyxd/robloxstudio-mcp)
