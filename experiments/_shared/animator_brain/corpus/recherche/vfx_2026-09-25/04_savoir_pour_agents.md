# Rapport g4 : connaissances VFX écrites pour des agents IA

**Méthode.** J'ai cloné les dépôts en `--depth 1` dans `/tmp/claude-0/-home-user-Jeux/4796ac9e-8e41-51f7-91c4-7b92a6a187d0/scratchpad/vfx/g4/` (dossiers `Roblox-Skill-for-AI/`, `roblox-suite/`, `game-designer/`, `agent-docs/`, et en plus `robloxIA/`). J'ai lu en entier chaque fichier VFX. Je n'ai rien écrit dans `/home/user/Jeux`.

**Point de méthode important.** La piste 18 (agent-docs) est un miroir hors ligne de la documentation officielle Roblox (`Roblox/creator-docs`), avec en plus le fichier `Full-API-Dump.json`. Je m'en suis servi comme **arbitre** pour vérifier les affirmations des trois autres sources. Le marquage suit ce principe :
- **[PAGE]** : documentation officielle lue localement dans ce miroir ;
- **[CODE LU]** : vérifié dans le fichier `Full-API-Dump.json` (valeurs par défaut, signatures) ou dans le code d'un dépôt.

---

### 15. « Roblox Skill for AI — VFX »

**Identité**
- URL : https://github.com/ProjectDevRate/Roblox-Skill-for-AI. Le fichier VFX est `skills/vfx-particles-and-beams/SKILL.md` (253 lignes).
- Licence : **MIT** (fichier LICENSE lu, « ProjectDevRate contributors »).
- Activité : dépôt créé et dernier commit le 2026-08-12, 0 étoile.
- Taille : environ 7 000 lignes (md + py), 23 skills.
- Homonymes écartés : sentinelcore/roblox-skills, MSayib/roblox-dev-skill, andrian-syh/roblox-best-practices-skill. J'ai retenu celui-ci parce que son nom correspond exactement.

**Ce que c'est vraiment**
- Un pack de skills au format SKILL.md. Le fichier VFX est un aide-mémoire qui couvre ParticleEmitter, Beam, Trail et Highlight.
- L'auteur annonce avoir sondé les valeurs par défaut sur un Studio réel (moteur 0.734) via le pont MCP [README, `VERIFICATION.md`]. J'ai confronté ces valeurs à l'API dump et **elles concordent** [CODE LU], ce qui rend l'annonce crédible.

**Comment ça marche**
- Du markdown pur avec des extraits de code Luau. Rien n'est sérialisable ni exécutable.
- Le script `scripts/validate_skills.py` valide seulement le format des skills.

**Ce qu'on peut en tirer (concret)**
- Valeurs par défaut exactes [CODE LU, recoupées avec l'API dump] :
  - ParticleEmitter : Rate 20, Lifetime 5–10, Speed 5.
  - Beam : Width 1, Segments 10, TextureMode **Stretch**, TextureSpeed 1, FaceCamera false, LightInfluence 0.
  - Trail : Lifetime 2.
  - Highlight : FillTransparency 0.5, DepthMode AlwaysOnTop.
- Recette d'impact en rafale : Rate 0, Lifetime 0.4–0.8, Speed 12–20, SpreadAngle 25,25, Acceleration (0,-30,0), Drag 2, LightEmission 0.6, puis `Emit(30)`.
- Courbes types :
  - Size 0.5 → 2 (à 0.3) → 0 ;
  - Transparency 1 → 0 (à 0.1) → 1 (apparition rapide, disparition lente) ;
  - Color d'un jaune chaud (255,220,120) vers un brun (120,30,0).
- Trail d'épée : Lifetime **0.2–0.4 s**.
- Trail invisible : la cause habituelle est deux attachments au même point (largeur nulle).
- Beam : sans `FaceCamera=true`, il disparaît vu par la tranche.
- Nettoyage : il faut attendre `Lifetime.Max` avant de détruire. Un `Destroy` immédiat coupe les particules en vol.
- `CanQuery=false` n'est respecté que si `CanCollide=false` [README, sondé].
- Post-processing (skill lighting) :
  - Bloom : Intensity 0.4, Size 24, Threshold 0.95 ;
  - ColorCorrection : Contrast 0.1, Saturation 0.15 ;
  - tous ces effets sont interpolables avec TweenService.
- Animation : connecter `GetMarkerReachedSignal` **une seule fois par track** ; `LoadAnimation` crée une nouvelle track à chaque appel (conforme à la doc [PAGE]).

**Affirmations douteuses ou fausses**
- Commentaire « `LightEmission = 1` : glow, unaffected by scene lighting ». C'est une confusion : LightEmission règle le mélange additif, et c'est LightInfluence=0 qui rend l'effet insensible à l'éclairage [PAGE].
- Limite de Highlight « de l'ordre de quelques centaines ». Elle est vague ; la doc dit 255, mais aussi « 31 slots » ailleurs (voir la piste 18).
- Aucune mention des flipbooks au-delà de `Grid4x4` + `Loop` : pas de OneShot, pas de Custom, pas de framerate.

**Ce qu'elle apporte de neuf par rapport aux autres :** des valeurs par défaut sondées et justes, et un tableau des erreurs courantes (Trail invisible, `AlwaysOnTop` qui traverse les murs, `Rate` laissé actif sur un effet ponctuel).

**Limites / risques :** couverture VFX mince. Rien sur la synchronisation fine, les flipbooks, la structure d'un combat ou l'overdraw chiffré.

**Verdict : S'INSPIRER, priorité 3.**

---

### 16. « roblox-suite — VFX Skill »

**Identité**
- URL : https://github.com/nonlooped/roblox-suite
- Fichiers VFX dans `roblox-vfx/` (460 lignes au total) :
  - `SKILL.md` (118 lignes) ;
  - `references/particle-emitter-properties.md` (104) ;
  - `references/shapes-flipbooks-and-advanced.md` (113) ;
  - `scripts/EffectBurst.lua` (125).
- Fichiers liés :
  - `roblox-animation/references/integration-and-events.md` (93) et `3d-animations.md` (213) ;
  - `roblox-user-interfaces/references/particles-in-ui.md`.
- Licence : **MIT** (LICENSE lu, © 2026 nonlooped).
- Activité : dernier commit 2026-09-21, relecture de la skill VFX datée du 2026-06-17, 16 étoiles.
- Taille : 28 skills, environ 33 800 lignes (md + lua).

**Ce que c'est vraiment**
- La skill VFX la plus complète des quatre sur les flipbooks et le lien avec les marqueurs d'animation.
- Elle est très fidèle à la doc officielle, en grande partie reformulée : les limites 400/100 et 20 s, l'avertissement Sphere/Cylinder sur Attachment et la désactivation des flipbooks faute de mémoire figurent tous textuellement dans `effects/particle-emitters.md` [PAGE].

**Comment ça marche**
- Du markdown avec un front-matter `read_when` et `last_reviewed`, plus `catalog.json`.
- `EffectBurst.lua` [CODE LU] : clone chaque ParticleEmitter d'un gabarit, force `Enabled=false` et `Rate=0`, appelle `Emit(count)`, puis `Debris:AddItem(clone, Lifetime.Max)`. Le gabarit n'est jamais modifié.

**Ce qu'on peut en tirer**
- Flipbooks :
  - grille 2x2, 4x4, 8x8 ou Custom, avec **marges transparentes entre les frames** (mipmaps) ;
  - OneShot ignore `FlipbookFramerate` et joue le sheet une seule fois sur la durée de vie de la particule ;
  - Random fait un fondu entre frames ;
  - `FlipbookStartRandom` + framerate 0 donne une frame fixe tirée au hasard (débris, variété) ;
  - `FlipbookBlendFrames` fait un fondu linéaire (la propriété existe bien [CODE LU]) ;
  - précharger les atlas avec `ContentProvider:PreloadAsync`.
- Structure d'un effet : 2 à 5 émetteurs sur la même Attachment :
  - cœur lumineux rapide avec LightEmission élevé ;
  - fumée plus lente et plus longue ;
  - étincelles rapides, courtes, en `VelocityParallel` ;
  - halo très grand, très transparent, additif ;
  - le tout étagé en `ZOffset`.
- Formes :
  - Disc + `ShapePartial=1` : émission sur le seul bord (anneau d'onde de choc) ;
  - Sphere + `ShapePartial=0.5` : demi-dôme ;
  - Sphere et Cylinder **exigent un BasePart parent**, qui peut être minuscule et invisible [PAGE].
- Synchronisation : marqueur → trouver l'Attachment du rig → `Emit`. Garder un traitement minimal dans le handler, avec `task.defer`. Le paramètre du marqueur est une chaîne libre à parser (« leftFoot,heavy » ou JSON). Déconnecter les connexions sur `Stopped` ou `Died`.
- LOD : désactiver au-delà de 100–300 studs, `Rate` divisé par deux à mi-distance. Les émetteurs d'un Attachment ne rendent **pas** dans un ViewportFrame.
- UI : pools d'ImageLabel animés par tween dans un CanvasGroup (30 à 80 particules max). Utile pour nos cartes plein écran.
- Motif réutilisable : le modèle « cloner puis détruire » d'`EffectBurst`, sous licence MIT.

**Contradictions et erreurs**
- `3d-animations.md` affirme que `LoadAnimation` avec la même Animation renvoie **la même** track. **Faux** : la doc dit « always creates a **new** AnimationTrack » et renvoie vers `GetTrackByAnimationId` [PAGE]. Cela contredit aussi la piste 15.
- `roblox-animation/SKILL.md` : TweenService serait utilisable sur « NumberSequence ». `integration-and-events.md` : on pourrait interpoler « Rate, Speed » d'un émetteur. **Faux** pour NumberSequence et pour Speed (un NumberRange). TweenService ne gère que number, bool, CFrame, Rect, Color3, UDim, UDim2, Vector2, Vector2int16, Vector3 et EnumItem [PAGE]. `Rate` reste interpolable.
- « EmissionDirection est ignoré sur une Attachment ». La doc dit seulement qu'on *peut* faire tourner l'Attachment « au lieu de » régler la propriété [PAGE]. « Ignoré » n'est pas établi [DÉDUIT].
- Menu « Render → Overdraw » de Studio : non vérifiable [DÉDUIT].
- `EffectBurst` [CODE LU / DÉDUIT] :
  - le `Debris` après `Lifetime.Max` ne tient pas compte de `TimeScale` : avec TimeScale < 1, les particules sont coupées avant la fin ;
  - `clone:Clear()` sur un clone neuf ne sert à rien.

**Ce qu'elle apporte de neuf :** les flipbooks dans le détail, les pièges de forme, la couche marqueurs → VFX → UI, les effets en ScreenGui et le motif de clonage d'`EffectBurst`.

**Limites / risques :** aucune recette chiffrée pour un impact de combat, et deux erreurs d'API sur l'animation et les tweens.

**Verdict : S'INSPIRER (le motif EffectBurst est adoptable sous MIT), priorité 4.**

---

### 17. « game-designer — VFX Guide »

**Identité**
- URL : https://github.com/AlexWynn-AM/game-designer (description : « knowledge base … for AI agents »).
- Fichiers VFX :
  - `guides/particle-effects-vfx-visual-feedback.md` (**1 896 lignes**) ;
  - `templates/rojo-project/src/shared/Modules/VFXRecipes.luau` (242 lignes).
- Licence : **aucun fichier LICENSE** [NON TROUVÉ], donc tous droits réservés par défaut.
- Activité : dernier commit 2026-05-08, 0 étoile.
- Taille : environ 18 900 lignes de markdown et 1 300 lignes de gabarit.

**Ce que c'est vraiment**
- Un long guide rédigé, probablement généré par IA [DÉDUIT : ton, sources DevForum listées en fin de fichier].
- C'est la source la plus riche en **recettes chiffrées**, mais la moins fiable.

**Comment ça marche**
- Tableaux de propriétés, recettes Luau complètes et un module `VFXRecipes`.
- `VFXRecipes` [CODE LU] est une table déclarative `{nom → propriétés}` appliquée par `Instance.new`. Recettes : fire, smoke, sparkle, dust, rain, snow, impact, heal. Il utilise les textures intégrées `rbxasset://textures/particles/smoke_main.dds` et `sparkles_main.dds`.
- C'est exactement le format « recette sérialisable » qui nous intéresse.

**Ce qu'on peut en tirer (valeurs à valider visuellement)**

Recettes de particules :

| Recette | Réglages |
|---|---|
| Feu | Rate 80, Lifetime 0.4–0.8, Speed 3–6, Spread 15, Acceleration +2 Y ; Size 1.5 → 2.5 (à 0.3) → 0 ; Transparency 0.3 → 0.6 (à 0.8) → 1 ; Color blanc-jaune → orange → rouge sombre ; LightEmission 1, LightInfluence 0, RotSpeed ±40, Rotation 0–360 |
| Fumée | Rate 30, Lifetime 3–5, Speed 1–3, Drag 2 ; Size 1 → 6 ; Transparency 0.5 → 0.8 → 1 ; gris ; LightEmission 0, **LightInfluence 1** (fumée éclairée par la scène) |
| Poussière d'impact au sol | Rate 0, `Emit(20)`, Lifetime 0.8–1.5, Speed 5–12, Spread 60, Acceleration -8 Y, Drag 3 ; Size 0.5 → 2 → 3 ; beige (180,160,130) |
| Explosion | `Emit(50)`, Lifetime 0.3–0.8, **Speed 20–50**, Spread 180,180, **Drag 5** ; Size 2 → 5 (à 0.3) → 0 ; Color blanc-jaune → orange → gris ; LightEmission 1, RotSpeed ±100 |
| Impact (module) | Lifetime 0.2–0.5, Speed 8–15, Drag 5, LightEmission 0.8, Spread 180 |
| Traînée d'épée en particules | Rate 60, Lifetime 0.15–0.3 |

Beam, Trail et formes :
- Éclair : chaîne de 8 Beams entre Attachments décalées au hasard de ±4 studs, Width 1.5, `Segments=1`, LightEmission 1, FaceCamera, fondu à 0.15 s. Le guide renvoie aussi au module « Lightning Beams » (`SamyBlue/Lightning-Beams`), que je n'ai pas vérifié.
- Trail d'épée : Lifetime 0.3, FaceCamera, LightEmission 1 ; WidthScale 1 → 0.2 ; Transparency 0 → 0.3 → 1 ; activé seulement pendant le coup.
- Trail de dash : attachments à ±2.5 Y sur HumanoidRootPart, Lifetime 0.5.
- **Onde de choc** : Part Cylinder en Neon, interpolée de 0.2×2×2 à 0.2×20×20 avec Transparency 1 en 0.5 s (Quad Out).

Retours à l'écran et caméra :
- Aura : PointLight dont Brightness passe de 1 à 3 et Range de 10 à 20, en boucle Sine.
- Flash de bouche : PointLight Brightness 5, Range 30, ramenée à 0 en 0.15 s.
- Post-processing local si parenté à `workspace.CurrentCamera`, global sous Lighting.
- Bloom d'activation : Threshold 0.3, Size 40, Intensity 0 → 2 en 0.1 s puis retour à 0 en 0.5 s.
- Flash de dégâts avec ColorCorrection : TintColor (255,100,100), Brightness 0.15, Saturation -0.3, retour en 0.5 s.
- Flash plein écran avec une Frame : blanc, intensité 0.8, 0.1 s.
- FOV punch : +8° sur 0.25 s pour un coup léger, +15° sur 0.4 s pour un coup lourd, retour en Elastic Out.
- Tremblement de caméra par `math.noise` : 1.5 pendant 0.4 s pour un coup, 4 pendant 0.8 s pour une explosion.
- Tableau des plages « subtil / modéré / intense » (Rate, Lifetime, Speed, Size, Drag, Segments, Trail.Lifetime, Bloom Threshold, Blur Size, amplitude du tremblement, FOV punch).
- `BlurEffect` : seul celui de plus grande Size s'applique [PAGE, confirmé].

**Erreurs ou affirmations douteuses** (tranchées par l'API dump [CODE LU] ou la doc [PAGE])

| Affirmation du guide | Réalité | Marquage |
|---|---|---|
| Beam TextureSpeed par défaut 0, en studs/s | 1 par défaut, en cycles/s | [CODE LU][PAGE] |
| Beam et Trail TextureMode par défaut Wrap | **Stretch** | [CODE LU] |
| Beam et Trail LightInfluence par défaut 1 | 0 via `Instance.new` | [CODE LU] |
| Trail MinLength par défaut 0 | **0.1** | [CODE LU] |
| CurveSize décale « selon la direction de face » (corde qui « pend » avec -5) | Décalage selon le **RightVector (axe X)** de l'Attachment ; la corde ne pend vers le bas que si X pointe vers le bas | [PAGE / DÉDUIT] |
| Pluie : Squash -3 « étire en gouttes » | Squash négatif élargit et aplatit ; c'est l'inverse | [PAGE] |
| Plafond de 16 000 particules, culling vers 800 studs, < 5 000 particules sur mobile | Non vérifiable | [DÉDUIT] |
| `LockedToPart=true` coûte moins cher | Non vérifiable | [DÉDUIT] |
| Maximum 20 keypoints par séquence | Absent de la doc | [NON TROUVÉ] |
| IDs de textures communautaires | Non vérifiables | [DÉDUIT] |

Autres défauts :
- Le Trail d'épée est déclenché par `KeyframeReached` (API héritée). Les pistes 15 et 16 recommandent `GetMarkerReachedSignal`.
- Code de LOD : `emitter.Parent.Position` est faux si le parent est une Attachment (position locale), et la boucle Heartbeat parcourt chaque émetteur. Cela contredit le conseil de la piste 16 [DÉDUIT].
- Le tremblement qui multiplie `camera.CFrame` dans RenderStepped dépend de l'ordre d'exécution du script caméra [DÉDUIT]. robloxIA recommande PreRender avec un décalage appliqué puis retiré.
- `VFXRecipes.burst` crée un émetteur neuf à chaque appel, alors que le guide recommande le pooling.

**Ce qu'il apporte de neuf :** la seule source avec des recettes complètes pour fumée, feu, explosion, poussière et onde de choc, plus toute la couche « juice » écran et caméra (bloom, CC, FOV, shake, flash) chiffrée.

**Limites / risques :** pas de licence (reprendre les chiffres, pas le texte ni le code), de nombreuses valeurs par défaut fausses, rien sur les flipbooks.

**Verdict : S'INSPIRER (chiffres de départ à valider), priorité 3.**

---

### 18. « Do Big Studios Agent Docs »

**Identité**
- URL : https://github.com/Do-Big-Studios/agent-docs
- Licence : fichier LICENSE **Apache-2.0**. Le contenu est une copie de `Roblox/creator-docs`, dont la licence amont n'a pas été vérifiée [DÉDUIT].
- Activité : dernière synchronisation le 2026-06-09. Le workflow tourne toutes les 6 h mais aucun commit depuis juin, donc la synchronisation est peut-être arrêtée [DÉDUIT].
- Taille : 9 162 fichiers, environ 69 Mo, 1 109 fichiers md (environ 192 000 lignes), 1 275 fichiers yaml de référence API (environ 207 000 lignes).

**Ce que c'est vraiment** [CODE LU : `.github/workflows`]
- Un **miroir automatique**, sans savoir VFX rédigé exprès. Il rassemble :
  - `Roblox/creator-docs/content` ;
  - le site de Luau et ses RFC ;
  - la doc de la bibliothèque Vide ;
  - `roblox-api/Full-API-Dump.json`, tiré de `RobloxAPI/build-archive`.

**Comment ça marche**
- Markdown et YAML de référence (propriétés, défauts, descriptions), plus un JSON avec pour chaque membre : `Default`, `Serialization.CanSave/CanLoad`, `Security`, les tags.

**Ce qu'on peut en tirer : c'est la pièce la plus utile du groupe**
- **La doc officielle hors ligne**, alors que create.roblox.com est bloqué dans notre bac à sable. Un `grep` suffit.
- L'API dump permet de :
  - générer et valider nos `.rbxmx` : liste exacte des propriétés sérialisables et valeurs par défaut ;
  - trancher toutes les contradictions de valeurs par défaut (voir la liste finale) ;
  - détecter les API inutilisables : `ParticleEmitter:FastForward(numFrames)` existe mais demande `RobloxScriptSecurity` [CODE LU].
- **Marqueurs pour notre exporteur `.rbxmx`** : `KeyframeMarker` est un enfant d'un `Keyframe`, avec `Name` et `Value` (chaîne). `GetMarkerReachedSignal(nom)` se déclenche pour chaque marqueur de ce nom et passe `Value` en paramètre [PAGE `KeyframeMarker.yaml`]. Aucune des trois skills ne le mentionne.
- Faits officiels introuvables ailleurs :
  - `LightInfluence` vaut 1 si l'émetteur est inséré dans Studio, **0 via `Instance.new`** ;
  - Beam : il faut **au moins n-1 segments** pour afficher correctement n keypoints de Color ou Transparency ;
  - Trail : changer ses attachments efface les segments déjà tracés ; changer `Color` recolore aussi les anciens segments ; changer `Lifetime` s'applique rétroactivement ;
  - la taille d'une texture de flipbook doit être un **multiple exact** de la grille (`FlipbookIncompatible`) ;
  - Highlight : le premier highlight à l'écran coûte jusqu'à environ 1 ms GPU sur mobile, les suivants presque rien ; créer ou supprimer un highlight reconstruit la géométrie (pics de coût), il vaut mieux modifier ses propriétés ;
  - recette officielle d'explosion (tutoriel) : texture `6101261905`, **Drag 10, Lifetime 0.2–0.6, Speed 20–40, Spread 180/180, `Emit(100)`**.
- **Contradiction interne à la doc officielle :** la limite de Highlight vaut 255 dans le YAML et dans `highlighting.md` ligne 32, mais « 31 slots » dans ce même fichier ligne 147 [PAGE].

**Limites / risques :** pas de pédagogie VFX de combat (le tutoriel « artist » est de niveau débutant), synchronisation arrêtée depuis juin. On peut aussi cloner directement `Roblox/creator-docs` et `RobloxAPI/build-archive` [DÉDUIT].

**Verdict : ADOPTER comme référence d'API hors ligne (grep sur la doc + JSON pour le générateur .rbxmx), priorité 5.**

---

### Hors liste, mais trouvé et pertinent : NenoEDX/robloxIA

**Identité**
- URL : https://github.com/NenoEDX/robloxIA
- Fichiers : `skills-roblox/roblox-37-vfx-combat-pipeline/SKILL.md` (111 lignes, en espagnol), `scripts/impact_sequencer.luau` (443 lignes), et `roblox-36-asset-pipeline/scripts/blender_flipbook_example.py` (168 lignes).
- Licence : « MIT » déclaré dans le front-matter, **pas de fichier LICENSE trouvé**.
- Activité : dernier commit 2026-09-13.
- C'est l'une des deux seules sources VFX Roblox que la recherche de code GitHub a trouvées pour `FlipbookLayout` + `GetMarkerReachedSignal`.

**Ce qu'il apporte : la seule vraie structure de VFX de combat du lot** [README / CODE LU]

| Frames (à 60 fps) | Couche |
|---|---|
| 0 | Hitstop de 2 à 6 frames (`AdjustSpeed(0)` sur les tracks) |
| 0–1 | Flash additif en Neon, ≤ 0.1 s |
| 1–3 | Carte d'impact en ImageLabel plein écran, 1 à 2 frames |
| 2–14 | Flipbook |
| 3–20 | FOV punch et shake par `math.noise` en PreRender (appliqué puis retiré) |
| 4–30 | Particules secondaires |
| 6–24 | Couches de son, avec un silence de 0.05–0.1 s |

- Budgets par impact : ≤ 3 émetteurs, ≤ 6 meshes éphémères en pool, ≤ 1 carte d'impact par seconde.
- Le script Blender rend N frames RGBA avec `film_transparent`, puis les assemble avec `magick montage`, et refuse une planche de plus de 1024 px.

**Erreurs**
- Il affirme qu'une `Lifetime` trop courte « tronque » un flipbook OneShot, et fixe un framerate de 24–30. **Faux** : en OneShot, le framerate est ignoré et l'animation est répartie sur toute la durée de vie [PAGE].
- Le montage utilise `-geometry +0+0` (aucune marge entre les frames), ce qui contredit l'exigence d'espacement de la doc [PAGE].
- Il ne propose que les grilles 4, 16 et 64 frames et ignore la grille Custom.

**Verdict : S'INSPIRER, priorité 4** (c'est notre cas d'usage exact). Je signale aussi, **sans les avoir lus** [NON TROUVÉ / non lus] : `bikotoru/roblox-ai-genkidama-pipeline` (R6 + VFX + Blender MCP), `Streetdude123/roblox-skills` (cartes d'impact anime), `brockmartin/roblox-game-skill` (`animation-vfx.md`).

---

## Synthèse transversale par thème

**Flipbooks**
- Seules la piste 16 et la doc sont justes et complètes. La piste 15 n'en parle presque pas, la piste 17 donne seulement le tableau des propriétés.
- Règles sûres [PAGE] : framerate max 30 ; OneShot = frames réparties sur Lifetime ; taille de texture multiple exact de la grille ; marges entre frames ; désactivation automatique sur mobile quand la mémoire manque ; `FlipbookStartRandom` + framerate 0 pour une frame fixe variée.
- Pour notre pipeline Blender : image ≤ 1024 px (garde-fou de robloxIA, non vérifié en doc [DÉDUIT]), marge transparente par cellule.

**Synchronisation**
- Les trois skills s'accordent sur `GetMarkerReachedSignal`. La piste 17 utilise encore `KeyframeReached`.
- Aucune n'explique la sérialisation : c'est `KeyframeMarker(Name, Value)` sous `Keyframe` [PAGE]. Notre exporteur Python peut donc écrire les marqueurs directement dans la KeyframeSequence.

**Structure d'un combat**
- Piste 16 : empilement de 2 à 5 émetteurs.
- Piste 17 : la couche écran et caméra.
- robloxIA : la chronologie en frames et les budgets.
- Les pistes 15 et 18 n'apportent rien sur ce point.

**Contradictions à retenir**
- Valeurs par défaut Beam et Trail (pistes 15 et 17) : c'est la piste 15 qui a raison [CODE LU].
- `LoadAnimation` : la piste 16 se trompe, la piste 15 a raison.
- TweenService sur les séquences : la piste 16 se trompe, la piste 17 a raison.
- Limite de Highlight : 255 ou 31 selon l'endroit de la doc.
- OneShot et Lifetime : robloxIA se trompe, la piste 16 et la doc ont raison.

**Synthèse du groupe**
1. Ce groupe n'apporte **pas de code à reprendre tel quel**, sauf éventuellement `EffectBurst.lua` (MIT) et le module `VFXRecipes` comme *format*.
2. La pièce maîtresse est **agent-docs** : la doc officielle et l'API dump hors ligne. Elle sert d'arbitre de vérité et d'entrée pour générer des `.rbxmx` valides (défauts, propriétés sérialisables, `KeyframeMarker`).
3. À assembler pour notre studio :
   - un schéma de recette déclaratif à la `VFXRecipes`, mais complet (flipbook, ZOffset, TimeScale, Shape) ;
   - les chiffres de la piste 17 et du tutoriel officiel comme valeurs de départ ;
   - l'empilement en 2 à 5 couches et les règles de flipbook de la piste 16 ;
   - la chronologie en frames et les budgets de robloxIA ;
   - des marqueurs `KeyframeMarker` écrits dans notre `.rbxmx`.
4. Ce qui manque partout :
   - une mesure réelle de l'overdraw et du coût (tout est qualitatif ou invérifiable) ;
   - des recettes de qualité anime pour les rubans, l'aura et les dômes (MeshPart + texture qui défile) ;
   - un rendu de contrôle hors Studio ;
   - une vérification de la limite de 1024 px et du comportement réel de `TimeScale` et `ZOffset`.
5. À corriger dans DragonFist.luau [DÉDUIT] :
   - fixer `LightInfluence` explicitement, puisque `Instance.new` donne 0 ;
   - modifier les propriétés du Highlight plutôt que le recréer ;
   - vérifier l'axe X des Attachments de Beam pour `CurveSize` ;
   - geler les émetteurs pendant le hitstop avec `TimeScale=0`, qui fige les particules [PAGE].

---

## Liste consolidée : 36 faits et recettes VFX

1. `Rate` : jusqu'à 400 particules/s par émetteur, 100/s sur mobile. `Emit(n)` sert aux rafales, avec `Rate=0` [PAGE doc ; pistes 15, 16, 17].
2. `Emit(particleCount = 16)` fonctionne même si `Enabled=false` [CODE LU dump ; PAGE ; piste 17].
3. `Lifetime` est plafonnée en interne à 20 s ; `Lifetime=0` n'émet rien [PAGE ; pistes 16, 17].
4. `LightInfluence` vaut 1 si l'émetteur est inséré dans Studio, **0 via `Instance.new`** [PAGE ; 18]. Beam et Trail valent aussi 0 dans le dump [CODE LU ; 15].
5. `LightEmission` règle le mélange (0 = normal, 1 = additif). Il n'éclaire pas la scène (PointLight pour cela). Avec LightEmission > 0, les couleurs sombres deviennent transparentes [PAGE ; 16, 17].
6. `Brightness` (ParticleEmitter, Beam, Trail) amplifie la lumière propre quand LightInfluence < 1 ; plage 0–10 000 pour Beam et Trail [PAGE ; 17].
7. `ZOffset` avance ou recule le rendu en studs sans changer la taille à l'écran. Un positif rapproche de la caméra. Il sert à étager les couches et à éviter le z-fighting des Beams [PAGE ; 16, 17].
8. `Orientation` `VelocityParallel` : étincelles et traînées étirées ; `FacingCameraWorldUp` : billboard verrouillé sur Y [PAGE ; 15, 16].
9. `Squash` > 0 donne une particule haute et fine, < 0 large et plate. La « pluie à Squash -3 » de la piste 17 est donc inversée [PAGE].
10. `Drag` est une demi-vie en secondes de la vitesse. Une valeur négative accélère [PAGE]. Explosions : Drag 5 à 10 [17, 18].
11. `TimeScale` va de 0 à 1 (0 fige l'émetteur). Il sert au ralenti ou au gel de hitstop [PAGE ; 16 ; usage hitstop DÉDUIT].
12. `Speed`, `Rotation`, `RotSpeed` et `Rate` ne touchent que les nouvelles particules ; `Color`, `Size`, `Transparency`, `Acceleration`, `LightEmission` et `ZOffset` s'appliquent aussi aux particules existantes [PAGE ; 16].
13. `LockedToPart=true` pour une aura collée au personnage ; `VelocityInheritance` + `Drag` pour « semer » des particules derrière un objet [PAGE ; 15, 16].
14. `SpreadAngle` : un axe à 360 donne un cercle, les deux à 360 une sphère ; 180,180 est la valeur « omnidirectionnelle » des recettes [PAGE ; 17].
15. Sphere et Cylinder ne s'affichent correctement qu'avec un **BasePart** parent, qui peut être invisible [PAGE ; 16].
16. Disc + `ShapePartial=1` : émission sur le seul bord (anneau d'onde de choc). Sphere + 0.5 : demi-dôme. Cylinder + 0 : cône [PAGE ; 16].
17. Flipbook : grilles 2x2, 4x4, 8x8, ou Custom (`FlipbookSizeX/Y`). La taille de la texture doit être un **multiple exact** de la grille [PAGE ; 16, 18].
18. `FlipbookFramerate` : maximum 30 fps, en NumberRange [PAGE ; 16, 17].
19. OneShot ignore le framerate et répartit toutes les frames sur la durée de vie [PAGE ; 16 ; robloxIA contredit à tort].
20. `FlipbookStartRandom=true` + framerate 0 : une frame fixe aléatoire par particule (débris variés). Random = fondu entre frames. `FlipbookBlendFrames` = fondu linéaire [PAGE, CODE LU ; 16].
21. Laisser un espacement transparent entre les frames (mipmaps). Les flipbooks sont désactivés automatiquement en manque de mémoire. Réutiliser les atlas et les précharger avec `PreloadAsync` [PAGE ; 16, 17].
22. Structure pro d'un effet : 2 à 5 émetteurs sur la même Attachment (cœur additif, fumée, étincelles `VelocityParallel`, grand halo transparent), étagés en ZOffset [16].
23. Chronologie d'un impact à 60 fps : hitstop 2–6 frames → flash Neon ≤ 0.1 s → carte d'impact 1–2 frames → flipbook de la frame 2 à 14 → caméra de 3 à 20 → secondaires de 4 à 30 ; ≤ 3 émetteurs et ≤ 1 carte d'impact par seconde [robloxIA, README].
24. Explosion (tutoriel officiel) : Drag 10, Lifetime 0.2–0.6, Speed 20–40, Spread 180/180, `Emit(100)` [PAGE ; 18].
25. Explosion (piste 17) : Speed 20–50, Drag 5, Size 2 → 5 → 0, Color blanc-jaune → orange → gris, LightEmission 1, `Emit(50)` [17, à valider].
26. Fumée : Lifetime 3–5, Size 1 → 6, Transparency 0.5 → 1, Drag 2, **LightInfluence 1** ; feu et étincelles : LightEmission 1, LightInfluence 0 [17].
27. Toujours terminer `Transparency` à 1 et faire apparaître vite (1 → 0 à t=0.1) pour éviter le « pop » ; les keypoints doivent commencer à 0 et finir à 1, sinon le constructeur lève une erreur [15 ; PAGE].
28. Onde de choc sans particules : Part Cylinder en Neon, de 2 à 20 studs de diamètre avec Transparency → 1 en 0.5 s (Quad Out) [17].
29. Trail d'épée : Lifetime 0.2–0.4 (défaut 2) ; `MinLength` vaut 0.1 par défaut ; WidthScale 1 → 0.2 ; activer seulement pendant le coup ; deux attachments distinctes, sinon largeur nulle [15, 17 ; CODE LU].
30. Trail : changer ses attachments efface le tracé ; `Color` et `Lifetime` s'appliquent rétroactivement ; `Enabled=false` + `Clear()` pour une coupe nette [PAGE ; 18].
31. Beam : courbe de Bézier cubique dont les points de contrôle sont décalés de `CurveSize` le long du **RightVector (X)** de chaque Attachment ; `Segments` ≥ n-1 keypoints ; `FaceCamera=true` sinon il disparaît vu de côté [PAGE ; 15, 18].
32. Beam et Trail : TextureMode par défaut **Stretch** ; TextureSpeed en cycles/s (défaut 1, négatif pour inverser) ; `SetTextureOffset(0)` réinitialise le défilement [CODE LU, PAGE ; 15 ; la piste 17 se trompe].
33. Highlight : FillTransparency 0.5 et AlwaysOnTop par défaut ; limite de 255 (ou 31 selon un autre passage de la doc) ; premier highlight à environ 1 ms GPU sur mobile ; modifier ses propriétés plutôt que le créer ou le supprimer [CODE LU, PAGE ; 15, 18].
34. Marqueurs : `KeyframeMarker(Name, Value)` enfant d'un `Keyframe` ; `track:GetMarkerReachedSignal(nom)` reçoit `Value` ; connecter une seule fois par track ; `LoadAnimation` crée toujours une **nouvelle** track [PAGE ; 15 ; la piste 16 se trompe].
35. Couche écran et caméra : post-processing sous `CurrentCamera` = local ; flash de bloom Intensity 0 → 2 en 0.1 s puis retour à 0 en 0.5 s ; FOV punch +8° sur 0.25 s ou +15° sur 0.4 s ; tremblement par `math.noise` appliqué puis retiré en PreRender ; TweenService ne peut pas interpoler NumberSequence, ColorSequence ni NumberRange [17, robloxIA ; PAGE ; la piste 16 se trompe].
36. Coût : le taux de remplissage et l'overdraw dominent (taille × recouvrement × transparence) ; tester aux qualités min et max ; VFX ponctuels côté client (le serveur envoie un identifiant d'effet et une position) ; les émetteurs, Beams et Trails ne rendent pas dans un ViewportFrame [PAGE ; 15, 16, 17].
