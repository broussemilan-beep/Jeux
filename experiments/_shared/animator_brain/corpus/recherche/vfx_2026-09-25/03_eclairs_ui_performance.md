# Rapport du groupe 3 : effets spécialisés et performance

Dossier de travail : `/tmp/claude-0/-home-user-Jeux/4796ac9e-8e41-51f7-91c4-7b92a6a187d0/scratchpad/vfx/g3/` (tous les clones sont là, en `--depth 1`, historique complet seulement quand c'était utile). J'ai ajouté deux prototypes, qui ne sont pas des livrables :
- `proto/evl_port.py` : portage Python d'EvLightning, qui sert à compter les segments.
- `proto/lb_port.py` : portage Python de la géométrie de Lightning-Beams, avec un bruit de Perlin écrit à la main.

J'ai aussi fait un clone partiel (sparse) de la doc officielle `Roblox/creator-docs` (contenu CC-BY-4.0, code MIT), pour vérifier les chiffres à la source. Rien n'a été écrit dans `/home/user/Jeux` : je l'ai seulement lu, pour relier les constats à `DragonFist.luau`.

Marquage : [CODE LU], [README], [PAGE] (page web ou fichier de la doc officielle lu), [NON TROUVÉ], [DÉDUIT].

---

### 11. Lightning-Beams

- **Identité**
  - URL : https://github.com/SamyBlue/Lightning-Beams. Auteur : Samy, pseudo « Quasiduck » sur le DevForum. Post DevForum du 29/10/2020 [PAGE].
  - Licence : MIT © 2020 Samy [CODE LU : LICENSE]. `PartCache` est une bibliothèque tierce (« Xan the Dragon ») embarquée sans fichier de licence propre [CODE LU]. Il faut vérifier sa licence d'origine avant de la reprendre.
  - Activité : dernier commit le 13/12/2021 ; release v1.1 du 27/05/2021 (archives de sources seulement) ; 86 étoiles, 14 forks.
  - Taille : `src/LightningBolt.lua` 356 lignes, `PartCache/` 297 lignes. Les sous-modules `LightningSparks.lua` (162 lignes) et `LightningExplosion.lua` (167 lignes) ont été **retirés du dépôt** au commit 039627d. Je les ai lus au commit a344a25 [CODE LU].
  - Homonymes :
    - Huzukawaiii/Lightning-Beams (2021), droblox/lightning-beams et DarkNightsAhead/Lightning-Beams sont des copies.
    - darkestdev/Lightning-Beams (2024) annonce une version typée compatible avec les Actors (Luau parallèle), mais ne contient que README et LICENSE, sans code [CODE LU].
    - **Le bon dépôt est SamyBlue.**
- **Ce que c'est vraiment**
  - Malgré son nom, **ce module n'utilise pas d'instances `Beam`**. Chaque éclair est une chaîne de `Part` cylindriques en `Neon`, tirées d'un pool (`PartCache`, 1000 Parts pré-créées). Toutes sont mises à jour à **chaque Heartbeat** : `Size`, `CFrame`, `Transparency` et `Color` pour chaque Part [CODE LU : l.17-30, 204-266, 275-354].
  - D'après l'auteur, une ancienne version en ImageHandleAdornment était plus rapide. La v2 annoncée (« mesh skinning ») n'a jamais été publiée [PAGE : DevForum].
- **Comment ça marche** [CODE LU]
  - Courbe support : Bézier cubique entre deux Attachments, avec `CurveSize0/1` comme pour un Beam. L'Attachment peut être factice (une table `{WorldPosition, WorldAxis}`), donc le module fonctionne sans instance.
  - Déplacement de chaque point : deux octaves de `math.noise` animées dans le temps (`AnimationSpeed`, `Frequency`) donnent un angle autour de l'axe (`noise0`). Un troisième bruit donne l'amplitude (`noise1` ∈ [MinRadius, MaxRadius]). L'inclinaison vaut `acos(bruit ∈ [0,1])`, soit une répartition sur un disque (la « uniform disk-point picking » annoncée).
  - `ExtrudeCenter(t) = exp(-5000·(t-0.5)^10)` épingle les extrémités. L'amplitude est quasi pleine sur les 80 % centraux.
  - Opacité le long de l'éclair : `DiscretePulse`, une impulsion trapézoïdale qui voyage à `PulseSpeed`, avec `PulseLength` et `FadeLength`. Au-delà de `ContractFrom`, le segment rétrécit au lieu de devenir transparent.
  - Couleur : `Color3`, ou `ColorSequence` qui défile (`ColorOffsetSpeed`).
  - Les fonctions `SpaceCurveFunction`, `OpacityProfileFunction` et `RadialProfileFunction` sont remplaçables.
  - `DestroyDissipate(t, force)` fait un fondu, un gonflement du rayon puis détruit l'éclair.
  - Sparks : de petits éclairs de 8 à 10 Parts naissent sur les segments dont la transparence est inférieure à 0.3.
  - Explosion : 14 éclairs de 10 Parts, chacun avec ses Sparks, plus trois ParticleEmitter clonés depuis des enfants du script (`ExplosionBrightspot`, `GlareEmitter`, `PlasmaEmitter`). Ces modèles d'émetteurs **ne sont pas dans git** [NON TROUVÉ].
- **Ce qu'on peut en tirer**
  - L'algorithme d'animation « bruit qui coule le long d'une Bézier, impulsion d'opacité, épinglage des bouts » est court et paramétrique. Je l'ai porté en Python en environ 50 lignes (`proto/lb_port.py`) : 30 segments, longueur moyenne de 1,41 stud pour 40 studs de corde, ce qui est cohérent [CODE LU + DÉDUIT].
  - Les trois fonctions de profil (Bézier, DiscretePulse, ExtrudeCenter) sont de bons paramètres à exposer dans notre chronologie.
  - Coût mesurable dans le code :
    - Par éclair et par frame : N Parts × 4 écritures de propriétés (défaut N = 30).
    - Une Explosion par défaut : jusqu'à 14 × (10 + 10 sparks × 10) ≈ 1 540 Parts, au-delà du cache de 1 000 Parts. Le module avertit lui-même de ce débordement (l.9) [CODE LU + DÉDUIT].
- **Limites / risques**
  - Tout est piloté par `os.clock()` et Heartbeat, sans lien avec nos marqueurs ni nos frames. Ce n'est pas déterministe (`math.random`, `Random.new()` sans graine).
  - `math.noise` est un bruit de Perlin propre à Roblox, dont l'implémentation n'est pas publiée. Un port Python ne peut pas reproduire les mêmes valeurs [DÉDUIT].
  - Cela contredit la règle citée dans son propre `PartCache` : « CFrame est la seule propriété rapide ».
  - Les Parts semi-transparentes ne se regroupent pas en un seul appel de rendu, donc environ un appel par segment [DÉDUIT de la règle MrChickenRocket, voir §27].
  - Projet abandonné depuis 2021.
- **Verdict : S'INSPIRER, priorité 3** (4 si on fait une technique électrique). Porter l'algorithme, pas le runtime.

### 12. EvLightning

- **Identité**
  - URL : https://github.com/evaera/EvLightning. Auteur : evaera (Eryn L. K.), code écrit en 2016.
  - Licence : MIT © 2018 Eryn Lynn. `Class.lua` vient de Bart Bes (MIT 2009) [CODE LU].
  - Activité : dernier commit le 07/05/2019 ; 52 étoiles, 11 forks.
  - Taille : `init.lua` 175 lignes, `Class.lua` 124 lignes. Un seul dépôt porte ce nom.
- **Ce que c'est vraiment** : un générateur **statique** d'éclair. Il calcule une géométrie une fois, puis `Draw()` crée des Parts `Neon` dans un Model, avec destruction par `Debris` [CODE LU].
- **Comment ça marche** [CODE LU]
  - Subdivision par déplacement du point milieu. `bends` passes ; à chaque passe, chaque segment est coupé entre 40 et 60 % de sa longueur.
  - Le nouveau point est décalé sur un cercle de rayon **fixe** entre ±5,3 studs, à un angle aléatoire. L'amplitude ne décroît pas avec la finesse.
  - La limite du `for` Lua n'est évaluée qu'une fois, donc le nombre de segments double à chaque passe (2^bends).
  - Fourches : à chaque coupe, la probabilité vaut `fork_chance × distance relative`, soit 0 en haut et le maximum en bas. La fourche est un sous-éclair de 20 à 40 studs dans la direction du segment, avec `fork_bends` passes, jusqu'à `max_depth`. L'épaisseur vaut `thickness − 0.2·depth`.
  - `GetLines()` renvoie `{origin, goal, depth}` : c'est **un format de données propre et sérialisable** (une liste de segments avec leur profondeur).
  - Mesure par le port Python (`proto/evl_port.py`, 200 tirages) : avec les réglages par défaut (bends 6), **225 Parts en moyenne par éclair (min 88, max 364)**. bends 4 donne 57 en moyenne, bends 3 en donne 25 [DÉDUIT : port fidèle, RNG différent].
- **Ce qu'on peut en tirer**
  - Le format `GetLines()`, et une option `seed`.
  - L'idée de fourches plus nombreuses vers la cible.
  - Un algorithme triviale à porter en Python, puis à précalculer en données dans le style de `DragonFistData.luau`.
- **Limites / risques**
  - Bug : README et code se contredisent. Le README annonce que « la transparence diminue à chaque fourche », mais le code recopie la même transparence [CODE LU].
  - Bug : avec une `seed`, toutes les fourches reçoivent **la même graine** (les options sont recopiées par `GetOptions()`). Leurs formes internes sont donc identiques [CODE LU].
  - Transparence 0.4 par défaut : environ 225 Parts semi-transparentes, soit à peu près autant d'appels de rendu [DÉDUIT]. C'est la moitié d'un budget de scène de 500.
  - `rojo.json` est au format Rojo 0.4 (obsolète).
- **Verdict : S'INSPIRER, priorité 3.** Reprendre le format et l'idée des fourches ; corriger l'amplitude (la diviser par deux à chaque niveau) et la graine (en dériver une par fourche).

### 13. Particle UI Module

- **Identité** : https://github.com/themwsama/Particle-UI-Module. Auteur : themwsama. Licence MIT © 2025 (LICENSE lu). 5 commits, tous du 11/09/2025, 0 étoile, aucune release. Taille : **README de 112 lignes et LICENSE. Aucun code.** Le fichier `ParticleUIMod.lua` annoncé est absent de toutes les branches et de tout l'historique [NON TROUVÉ].
- **Ce que c'est vraiment** : une annonce [README]. Le README promet un module ImageLabel qui gère texture, flipbook (`FlipbookLayout`, `FlipbookFramerate`, `FlipbookMode`), couleur, taille, transparence, vitesse, accélération, rotation, `Emit(n)` et `Enabled`. Aucune de ces promesses n'est vérifiable.
- **Alternatives réellement lisibles** (le nom est générique) :
  - `diigit/EmitYourParticles` : MPL-2.0, 640 lignes, mis à jour le 05/10/2025 [CODE LU]. Il tourne sur RenderStepped, fait un `Clone()`/`Destroy()` par particule sans pool, n'émet **qu'une particule au plus par frame** (`RateTick` remis à 0), et interpole des Number/ColorSequence sur n'importe quelle propriété de GuiObject.
  - `joeldesante/rParticle` : MIT, 132 lignes, 2022 [CODE LU]. Tourne sur Heartbeat, avec des callbacks `onSpawn`/`onUpdate`.
  - Post DevForum « UI Particle » (13/10/2025) : il lit les propriétés d'un **vrai ParticleEmitter** placé dans l'UI et les rejoue en ImageLabels. Code fermé, retiré du Creator Store, pas de flipbooks [PAGE].
- **Utile pour nos cartes d'impact, lignes de vitesse et flashs ?** [DÉDUIT, appuyé sur la doc]
  - **Flashs et blanc** : non. Un simple Frame suffit, comme aujourd'hui.
  - **Lignes de vitesse** : oui en tant qu'idée. Aujourd'hui, `screen()` crée 48 Frames figées (`DragonFist.luau` l.694-713). L'anime les re-tire toutes les 2 à 3 frames. Un petit émetteur UI déterministe (graine plus numéro de frame) rendrait des lignes qui bougent, et ce n'est pas à une bibliothèque de le faire : environ 40 lignes à nous.
  - **Cartes** : l'intérêt principal serait des flipbooks 2D en ImageLabel (`ImageRectOffset`/`ImageRectSize`). Ils sont précalculables dans Blender, sans passer par les particules.
  - Contraintes UI vérifiées dans la doc officielle [PAGE] :
    - Les GuiObjects n'ont aucun mode additif, contrairement à `LightEmission` pour les particules, Beams et Trails [NON TROUVÉ dans ImageLabel.yaml / GuiObject.yaml]. Tout « glow » UI doit donc être peint dans la texture.
    - `ViewportFrame` : pas de post-processing, et Neon/Glass « au plus bas niveau de qualité » (ViewportFrame.yaml l.13-17).
    - `CanvasGroup` consomme de la mémoire de texture et s'affiche blanc au-delà du plafond (CanvasGroup.yaml l.27-31).
    - `Path2D` (trait UI avec `Color3`, `Thickness`, sans transparence) permet un éclair 2D opaque (Path2D.yaml).
- **Verdict : IGNORER, priorité 1** pour le dépôt (vide). S'INSPIRER, priorité 2, du principe via EmitYourParticles et rParticle.

### 19. Roblox Luau Scripting

- **Identité** : https://github.com/Ray2fly2/Roblox-Luau-Scripting. Auteur : Ray2fly2. **Pas de fichier LICENSE**, donc droits réservés par défaut. Dernier commit le 18/07/2025 ; 4 étoiles. Taille : un « README.md » de 4 927 lignes (217 Ko, qui est en fait du HTML) et un `index.html`. Homonymes : `Cubitaa/Luau-Roblox-Scripting-Guide` (2026) et `Evevemue/...Portfolio`. Le plus plausible est Ray2fly2, premier résultat pour ce nom exact.
- **Ce que c'est vraiment** : des notes de cours pour débutants. La section « Particles & Effects » (l.3224-3363) contient 15 exemples de 1 à 6 lignes [CODE LU].
- **Comment ça marche** : `Instance.new` plus l'affectation de quelques propriétés. Les ID d'assets sont des bouche-trous (`rbxassetid://1234567`). On y trouve `wait()`, qui est déprécié, et `beam.Transparency = NumberSequence.new(0, 0.5, 1)`, un constructeur à 3 nombres qui n'est pas documenté et est probablement invalide [DÉDUIT]. L'exemple 1 (`Rate 50`, `Lifetime 1..3`) donne jusqu'à 150 particules simultanées, au-dessus du seuil de 50 à 100 de §27.
- **Ce qu'on peut en tirer** : rien que notre `DragonFist.luau` ne fasse déjà mieux. Notre convention d'émetteurs désactivés avec les attributs `EmitCount`/`EmitDelay` est plus avancée.
- **Limites** : pas de licence, niveau débutant, erreurs.
- **Verdict : IGNORER, priorité 1.**

### 27. roblox-dev-notes

- **Identité**
  - URL : https://github.com/shinjiesk/roblox-dev-notes. Auteur : Shinji esk. **Pas de LICENSE.** Créé le 01/03/2026, dernier commit le 02/04/2026. Contenu en **japonais**, au format GitBook.
  - Taille : `client-performance.md` 986 lignes, `server-performance.md` 1 048, `README.md` (guide de style Lua) 1 715, `billboardgui.md`, `explorer-filter.md`, et une petite application `lua-style/`. `.cursor/mcp.json` pointe vers le StudioMCP macOS.
  - C'est le seul dépôt de ce nom exact et il couvre bien overdraw, ParticleEmitter, Beam et Trail. L'autre candidat, `LionelBergen/RobloxDevelopmentNotes` (créé et figé le 10/09/2024), n'est pas pertinent [DÉDUIT].
- **Ce que c'est vraiment** : une synthèse secondaire, avec des sources en fin de fichier (§13 l.962-986) : doc officielle, MrChickenRocket (DevForum 2024 et RDC 2024), BlackoutCedar, zeuxcg. Elle vise surtout les maps et props, pas les VFX de combat [CODE LU].
- **Contenu utile** : §2-3 Overdraw, §2-4 VFX, §10 lecture des mesures (Shift+F2, MicroProfiler), §11 checklist.
  - J'ai vérifié les chiffres à la source (tableau ci-dessous).
  - Deux affirmations **ne sont pas sourcées** : « 50 à 100 particules simultanées par effet » (l.181, 833) et « la forme de la texture n'influe pas sur l'overdraw » (l.182) [README, NON TROUVÉ dans la doc officielle].
  - Incohérence : l'item de checklist « LightEmission à 0 pour fumée et brouillard » (l.834) renvoie à §2-4, qui ne parle pas de LightEmission [CODE LU].
- **Verdict : S'INSPIRER, priorité 4.** C'est une bonne carte des règles, mais le critique doit citer les **sources primaires** listées ci-dessous, pas ces notes.

#### Chiffres et règles vérifiables pour le futur « critique VFX »

Sigles utilisés :
- **CD** = `Roblox/creator-docs`, contenu en-us, commit du 25/09/2026 [PAGE].
- **MCR** = MrChickenRocket, « Real world building and scripting optimization » (DevForum t/3127146) [PAGE].
- **RDN** = roblox-dev-notes [README].

| # | Règle (contrôlable statiquement sur nos fichiers générés) | Seuil | Source exacte |
|---|---|---|---|
| P1 | `ParticleEmitter.Rate` | ≤ 400/s par émetteur, **≤ 100/s sur mobile** | CD `effects/particle-emitters.md` l.207 |
| P2 | `Lifetime` | plafonné à 20 s | CD particle-emitters.md l.194 |
| P3 | `FlipbookFramerate` | ≤ 30 i/s | CD particle-emitters.md l.420 |
| P4 | Flipbook : grilles 2×2/4×4/8×8/custom (exemple 1024² en 8×8) ; **marge transparente entre les images** (mip) | présence d'une marge | CD particle-emitters.md l.396-400 |
| P5 | Flipbooks **désactivés automatiquement** en mémoire basse (vieux téléphones) ; réutiliser les textures | nombre de textures flipbook uniques | CD particle-emitters.md l.405 |
| P6 | Coût GPU = pixels occupés à l'écran × couches qui se chevauchent (fill-rate, overdraw) | à mesurer (voir P16) | CD particle-emitters.md l.170 et l.210 ; improve.md l.384-388 |
| P7 | Changer les propriétés d'un ParticleEmitter peut avoir un impact « dramatique » | aucune propriété d'émetteur modifiée par frame | CD `performance-optimization/improve.md` l.337-338 |
| P8 | Particules simultanées par effet (`Rate×Lifetime.max` ou `EmitCount`) | 50 à 100 | RDN l.181 et l.833 (**non sourcé**) |
| P9 | 1 appel de rendu par ParticleEmitter et par Beam ; les Parts semi-transparentes ne se regroupent pas | budget de scène **500 appels de rendu / 500 k triangles** ; UI : s'inquiéter au-delà d'environ **150 appels** | MCR |
| P10 | Transparence : éviter les valeurs autres que 0 et 1 | nombre de Parts avec 0 < T < 1 | CD `performance-optimization/design.md` l.48 |
| P11 | `Highlight` : **255 au maximum** (les désactivés comptent) ; le 1er coûte **jusqu'à 1 ms GPU sur mobile** ; **ajouter ou retirer un Highlight = reconstruction de géométrie, donc pic** ; sur mobile, le coût croît avec la couverture d'écran | pré-créer, puis basculer les propriétés | CD `effects/highlighting.md` l.32, 154-162 ; Highlight.yaml l.49-56, 143-146 |
| P12 | `Beam.Segments` ≥ n−1 pour n points clés de Color ou Transparency (défaut 10) | contrôle statique | CD Beam.yaml l.356-371 |
| P13 | `Trail.Lifetime` entre 0,01 et 20 s (défaut 2) ; plus court = moins d'overdraw | — | CD Trail.yaml l.191-192 ; RDN l.188 |
| P14 | `UIGradient` : ≤ **6 arrêts de couleur** ; ne pas animer `Color`/`Transparency` (reconstruction), animer `Offset`/`Rotation` | contrôle statique | CD UIGradient.yaml l.32-56 |
| P15 | Budget de frame : 16,67 ms à 60 i/s ; privilégier l'événementiel au calcul par frame | — | CD design.md l.52 |
| P16 | Exemple d'appareil de référence (baseline) : 1 000 appels de rendu / 1 000 000 triangles (exemple, pas une règle) | — | CD design.md l.14 |
| P17 | Réseau client : ≤ 50 Ko/s en réception ; VFX côté client, le serveur n'envoie que l'événement | — | MCR ; RDN server-performance l.15 et §4-3 (UnreliableRemoteEvent ≤ 1 000 octets, l.214, non revérifié) |
| P18 | `LightEmission` : 0 = normal, 1 = additif ; **aucun chiffre de coût publié** | [NON TROUVÉ] | CD ParticleEmitter.yaml l.444-458 |
| P19 | Scene Analysis : `SceneAnalysisService` (compte des particules, triangles et appels de rendu par catégorie, y compris Particles et UI) est exposé au **MCP Studio** | utile seulement si Studio est disponible | CD `performance-optimization/scene-analysis.md` l.44, 68 et « Engine API » |

Constats sur notre code actuel [CODE LU dans `experiments/r6_poing_dragon/luau/DragonFist.luau` + DÉDUIT] :
- **`bodyFlash` (l.310-319) crée un `Highlight` à chaque événement puis le détruit par `Debris`.** D'après P11, c'est exactement le cas qui provoque des pics. Il vaut mieux créer un Highlight au chargement et animer `FillTransparency`/`Enabled`.
- Aura : `Rate = 60 × intensity` avec intensity ≤ 1,0 dans `DragonFistData.luau`, donc sous le plafond mobile de 100/s. Pic ≈ 60 × 0,6 = 36 particules simultanées, dans le seuil de P8.
- Braises : `Rate 25 × Lifetime 3` = 75 particules simultanées, dans le seuil.
- `ring` (T = 0,1) et `ball` (T = 0,2) sont des Parts semi-transparentes : elles ne se regroupent pas (P9, P10).

Mesure d'overdraw proposée pour le critique [DÉDUIT] : aucune source ne donne de seuil chiffré de couches. Le critique pourrait faire une **passe « overdraw » dans l'aperçu three.js en Chromium headless** :
- rendre chaque sprite, ruban ou carte avec un matériau additif qui écrit 1/255, puis lire les pixels ;
- produire les métriques : % d'écran à ≥ 4 couches, maximum de couches, somme des pixels × couches par frame, en comptant les cartes UI plein écran à transparence partielle comme 1 couche plein écran chacune ;
- les seuils seront à calibrer une fois sur un vrai téléphone.

---

## Synthèse du groupe

1. **Éclairs** : aucun des deux modules n'est réutilisable tel quel. Tous deux fabriquent des Parts Neon (225 Parts par éclair en moyenne pour EvLightning ; N Parts réécrites à chaque frame pour Lightning-Beams), sans lien avec nos marqueurs.
   - La bonne pièce est un **générateur Python à nous**. Il combinerait la subdivision et les fourches d'EvLightning (corrigées : amplitude divisée par deux à chaque niveau, graine dérivée par fourche) et l'animation de Lightning-Beams (bruit qui coule le long d'une Bézier, `DiscretePulse`, `ExtrudeCenter`).
   - Il **précalculerait des polylignes par frame** sous forme de données, au format `{origin, goal, depth}` d'EvLightning. three.js les lit directement ; Luau les dessine en Beams (FaceCamera, LightEmission 1, texture glow) ou en cylindres Neon **opaques** (T = 0, regroupables), le fondu se faisant par l'épaisseur.
   - Ne jamais compter sur `Random` ou `math.noise` de Roblox pour obtenir le même résultat que Python. Soit on précalcule, soit on écrit un PRNG et un Perlin identiques des deux côtés.
2. **Particules UI** : rien à adopter. On gagnerait davantage avec des flipbooks 2D précalculés en ImageLabel et des lignes de vitesse re-tirées de façon déterministe, écrites par nous. Les glows UI doivent être peints dans la texture, faute de mode additif.
3. **Performance** : le tableau P1 à P19 fournit des règles sourcées, directement contrôlables sur les données générées (Rate, Lifetime, flipbook, Highlight, Segments, UIGradient, transparence partielle, nombre d'appels de rendu estimé).
4. **Ce qui manque** : aucun seuil chiffré officiel pour l'overdraw, le coût de `LightEmission` ou le nombre de particules à l'écran. Il faudra les obtenir par la passe overdraw three.js ci-dessus, puis un calibrage unique sur un vrai appareil, ou via `SceneAnalysisService` et le MCP si Studio devient disponible.
5. **Correctif immédiat à planifier** : pré-créer le Highlight de `bodyFlash` au lieu de le créer et le détruire à chaque événement.
