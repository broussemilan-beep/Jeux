# Rapport : animation Roblox R6 de combat « anime » (sources web hors devforum)

Date : 2026-09-24. Chercheur : sous-agent « roblox_web ».

**Avertissement sur la méthode (à lire d'abord).** Le proxy de sortie de ce
sandbox ne laisse passer que **github.com** (et devforum.roblox.com). Sont
bloqués en lecture directe : create.roblox.com (Creator Hub), robloxapi.github.io,
raw.githubusercontent.com, medium.com, artstation.com, builtbybit.com,
gumroad.com, kitsblox.com, robloxanimations.com, nilo.io, fandom.com, x.com,
twicopy, scribd, namu.wiki, extensions.blender.org, lemon8, youtube.com.
En conséquence :

- La doc officielle Roblox a été lue **via le dépôt GitHub officiel
  `Roblox/creator-docs`** (source Markdown/YAML du Creator Hub) : fiabilité
  élevée.
- Les pages bloquées ne sont connues **que par les extraits du moteur de
  recherche** (WebSearch résume la page). Ces éléments sont marqués
  **[extrait recherche, page non lue]** : fiabilité moyenne, ne pas les citer
  comme des citations exactes.
- 5 fils devforum ont été lus parce qu'ils étaient critiques pour un fait
  technique (ils sont signalés [devforum] ; l'autre chercheur les couvre
  peut-être aussi).
- Aucune image n'a pu être téléchargée (voir §5).

---

## 1) Sources lues

### Lues directement (contenu réel)

| URL | Ce qu'on y trouve |
|---|---|
| https://github.com/Roblox/creator-docs/blob/main/content/en-us/animation/editor.md | Doc officielle de l'Animation Editor : 30 fps par défaut, styles d'easing, directions, priorités, bouclage, optimisation auto des keyframes. |
| https://github.com/Roblox/creator-docs/blob/main/content/en-us/animation/curve-editor.md | Curve Editor : modes Linear/Constant/Cubic, tangentes réservées au Cubic, conversion quaternion→Euler irréversible. |
| https://github.com/Roblox/creator-docs/blob/main/content/en-us/reference/engine/enums/PoseEasingStyle.yaml | Enum officiel : Linear, Constant, Elastic, Cubic (déprécié, bug), Bounce, CubicV2. |
| https://github.com/Roblox/creator-docs/blob/main/content/en-us/reference/engine/enums/PoseEasingDirection.yaml | Définitions In/Out/InOut des poses. |
| https://github.com/Roblox/creator-docs/blob/main/content/en-us/reference/engine/enums/AnimationPriority.yaml | 7 priorités, ordre et usage recommandé. |
| https://github.com/Roblox/creator-docs/blob/main/content/en-us/reference/engine/classes/AnimationTrack.yaml | Play(fadeTime=0.1, weight=1, speed=1), AdjustSpeed, AdjustWeight, mélange par priorité puis par poids, marqueurs. |
| https://github.com/Roblox/creator-docs/blob/main/content/en-us/reference/engine/classes/Motor6D.yaml | Motor6D.Transform écrasé chaque frame par l'Animator. |
| https://github.com/Roblox/creator-docs/blob/main/content/en-us/reference/engine/classes/Pose.yaml | Pose.CFrame (rotation + position) appliqué au Motor6D. |
| https://github.com/Roblox/creator-docs/blob/main/content/en-us/tutorials/use-case-tutorials/animation/create-an-animation.md | Tutoriel officiel : timeline réglable à 24 fps, poses clés de marche toutes les 3 frames. |
| https://github.com/Roblox/creator-docs/blob/main/content/en-us/animation/inverse-kinematics.md | IKControl (runtime) — peu utile pour le combat. |
| https://github.com/Cautioned/Blender-Animations-Plugin (+ `easing.py`, `planning.py`, `RigPart.lua` via recherche de code) | Plugin Blender↔Roblox de référence (« Roblox Animations Importer/Exporter », ex-RBXMonkey) : comment les courbes Blender sont converties/bakées. |
| https://github.com/troublegy/Moon-Animator-2-API (index.html) | Doc API non officielle de Moon Animator 2 : liste des easings, DEFAULT_FPS = 60. |
| https://github.com/dillydog580/animate-roblox-characters (README, SKILL.md, references/roblox-rigs-export.md) | « Skill » IA pour animer R6/R15 dans Blender : règles d'interpolation, 30 fps, rig R6 V2.22. |
| https://github.com/Sleitnick/RbxCameraShaker (+ CameraShakePresets.lua) | Module de camera shake le plus répandu sur Roblox, valeurs numériques des presets. |
| https://github.com/biotoxin495/CameraKit | Module caméra : valeurs par défaut shake + « FOV punch », exemple d'impact. |
| https://github.com/Mogom/KoF_Like_Game/blob/main/src/Shared/Modules/Combat/HitstopService.luau | Exemple de hitstop via AdjustSpeed(0) (projet amateur). |
| GitHub code search `hitstop AdjustSpeed language:Luau` | ~15 dépôts : le hitstop Roblox se fait quasi universellement par `track:AdjustSpeed(0)` puis restauration. |
| [devforum] https://devforum.roblox.com/t/animation-easing-styles/25374 | Annonce officielle 2016 des easing styles ; comportement de Constant. |
| [devforum] https://devforum.roblox.com/t/add-the-missing-easing-styles-for-animations/2397709 | « 5 sur 11 » easings supportés ; Moon Animator « bake » les autres. |
| [devforum] https://devforum.roblox.com/t/moon-animator-doesnt-export-animation-at-a-framerate-of-12/3051738 | Moon exporte à 60 fps ; astuce Constant pour un rendu « 12 fps ». |
| [devforum] https://devforum.roblox.com/t/how-to-make-low-fps-blocky-style-animation/2800541 | Tutoriel « low FPS / blocky » (easing Constant). |
| [devforum] https://devforum.roblox.com/t/do-you-animate-in-30fps-or-in-60-fps-blender/3193170/5 | Conseil de CAUTlONED (auteur du plugin Blender) : ×2 pour passer 30→60 fps. |
| [devforum] https://devforum.roblox.com/t/animation-slowing-like-ultimate-battlegrounds/3053080 | Ralenti en l'air (Sorcerer Battlegrounds) via AdjustSpeed. |

### Connues uniquement par extraits de recherche [page non lue]

| URL | Contenu (selon l'extrait) |
|---|---|
| https://kitsblox.com/blog/fix-choppy-roblox-animations | Espacement des keyframes pour un coup de poing de 0,3 s, trop/pas assez de clés, Cubic. |
| https://kitsblox.com/blog/best-roblox-combat-animations | Anticipation / impact / recovery, squash & stretch. |
| https://kitsblox.com/blog/moon-animator-vs-roblox-animation-editor | Moon : courbes Bézier par keyframe, IK, sub-frame ; même format KeyframeSequence. |
| https://kitsblox.com/blog/r6-vs-r15-roblox-rigs | Anatomie R6 : 6 blocs rigides, un pivot par membre, pas de coude/genou. |
| https://nilo.io/articles/export-blender-animation-roblox-studio | Bake Blender, 30/60 fps, réglages FBX. |
| https://create.roblox.com/store/asset/16072313171/The-Strongest-Battlegrounds-OFFICIAL-Animations | Pack « TSB OFFICIAL Animations » publié par @jp_Serene le 22/01/2024 (contenu non inspectable ici). |
| https://x.com/KirvKirv1 (Ultik) | Animateur de TSB (Omni-Directional Serious Punch, Atomic Samurai) — aucun texte de process accessible. |
| https://x.com/RobertAnim8er/status/1652780167671033856 | Animateur jeu vidéo (non-Roblox) : tout est animé à 30 fps, le 60 fps vient de l'interpolation moteur. |
| https://the-strongest-battlegrounds-rblx.fandom.com/wiki/Basic_Combat | M1 TSB : 4 coups, ragdoll au 4e, 3%+3%+4%+4 %. |
| https://medium.com/@jesus.lo.be.30/animating-at-roblox-e9483e8d5dd6 | Article Medium 2019 (FireJxsus) sur Blender→Roblox ; contenu non lisible. |
| builtbybit / robloxanimations.com / Gumroad (tojii « bganim », citrusapples « RobloxCombatSet ») | Descriptions commerciales de packs « battlegrounds » R6. |
| https://troublegy.github.io/Moon-Animator-2-API/ | Site de la doc API Moon (lu via son dépôt GitHub). |

---

## 2) Faits techniques Roblox qui changent le rendu d'une animation

Tous ces points viennent de sources lues directement, sauf mention contraire.

### 2.1 Interpolation : une seule courbe par pose et par joint, et seulement 5 formes

- **Styles d'easing des keyframes (PoseEasingStyle)** : `Linear` (0, **défaut**),
  `Constant` (1), `Elastic` (2), `Cubic` (3, **déprécié**), `Bounce` (4),
  `CubicV2` (5). — `PoseEasingStyle.yaml`.
- **Bug connu, officiellement documenté** : « Use CubicV2 going forward, Cubic
  has a bug where the direction is reversed between the editor and runtime. »
  → Une animation en `Cubic` (ancien) ne joue pas en jeu comme dans l'éditeur :
  l'ease-in devient un ease-out. **Toujours utiliser CubicV2.** —
  `PoseEasingStyle.yaml`.
- **Chaque Pose (= un joint à une keyframe) porte UN seul style + UNE seule
  direction** pour le segment jusqu'à la keyframe suivante. Il n'y a pas de
  tangentes Bézier libres dans le format KeyframeSequence classique. Le code du
  plugin Blender le dit explicitement : « Roblox stores one easing style on each
  Pose... mixed segments must be baked as dense linear poses. » —
  `Cautioned/Blender-Animations-Plugin/planning.py`.
- **Les tangentes n'existent que dans le Curve Editor**, et seulement en mode
  Cubic : « Cubic is the only mode that allows you to define tangents ». Ouvrir
  le Curve Editor convertit les quaternions en angles d'Euler, et « it's
  impossible to convert them back ». — `curve-editor.md`.
- **« 5 sur 11 »** : « Roblox only supports 5 out of the 11 existing easing
  styles for animations » (Pyseph, 29/05/2023). Sine, Quad, Back, Expo, etc.
  n'existent pas pour les poses. — [devforum] 2397709.
- **Constant = snap instantané**, dont le moment dépend de la direction :
  « You can tell it to instantly snap at the beginning, middle (inout) or end of
  the interpolation. » (annonce officielle 2016). Doc actuelle : « Removes
  interpolation between the selected keyframe and next keyframe. The animation
  will 'snap' from keyframe to keyframe. » — [devforum] 25374 ; `editor.md`.
- **Linear est le défaut, et la doc officielle le décrit elle-même comme
  robotique** : dans `editor.md`, la vidéo Linear illustre une rotation qui
  « appear stiff and robotic », la vidéo Cubic une rotation qui paraît « more
  natural ». → Une animation dont on n'a pas réglé l'easing est **robotique par
  défaut**.

### 2.2 Directions d'easing : convention inversée (piège)

- La doc de l'éditeur donne la définition « classique » : In = « slower at the
  beginning and faster toward the end », Out = « faster at the beginning and
  slower toward the end ». — `editor.md`.
- Mais l'enum `PoseEasingDirection` dit : In = « The EasingStyle curve is
  reversed, with the easing becoming linear as it approaches the next
  keyframe » ; Out = « EasingStyle curves are applied in the forward
  direction ». — `PoseEasingDirection.yaml`.
- Le code du plugin Blender de référence : « Pose easing names are reversed
  relative to TweenService's names » (`RigPart.lua`), et à l'export Blender
  EASE_IN → « Out », EASE_OUT → « In » (`easing.py` : « PoseEasingDirection has
  the opposite In/Out convention »).
- **Conséquence pratique** : pour tout outil maison qui génère des poses
  Roblox, ne pas supposer que In/Out signifie la même chose que dans
  TweenService ou Blender. **Vérifier à l'œil en jeu**, pas seulement dans
  l'éditeur (le bug Cubic ajoute un deuxième piège). *Contradiction non
  résolue entre `editor.md` et l'enum ; voir §6.*

### 2.3 Fréquence d'images

- **Éditeur Roblox** : « animations run at 30 frames per second » par défaut,
  timeline en secondes:frames (0:15 = ½ s). Le tutoriel officiel propose de
  passer la timeline à **24 fps** (menu engrenage). — `editor.md`,
  `create-an-animation.md`.
- **Moon Animator 2** : `DEFAULT_FPS = 60` (et `current_fps` modifiable, 120
  dans l'exemple) ; MIN_FRAMES = 60. — Moon-Animator-2-API `index.html`.
- **À l'exécution**, Roblox interpole entre les keyframes à la fréquence du
  rendu : le « 30 fps » est la grille d'édition, pas la fréquence d'affichage.
  Robert Morrison (animateur de jeux vidéo, pas Roblox) : « Game developers
  animate almost everything at 30fps... Anything that's 60fps you're seeing
  interpolation being done by the engine » [extrait recherche, x.com].
- **Moon exporte à 60** : un utilisateur règle Moon à 12 fps, mais
  l'animation exportée joue à 60 ; la solution a été de la réimporter dans
  l'éditeur Roblox et de mettre **toutes les keyframes en Constant**. —
  [devforum] 3051738 (vladxh).
- **Blender 30→60** : CAUTlONED (auteur du plugin Blender) : « when you are done
  animating in 30fps just scale your keyframes by 2 (30 x 2 = 60), and change
  blender to 60fps and export. » — [devforum] 3193170/5.

### 2.4 Bake : ce qui arrive aux courbes Blender et aux easings de Moon

- **Plugin Blender (Cautioned)** : les segments en LINEAR, CONSTANT, CUBIC,
  BOUNCE et ELASTIC sont exportés tels quels, en clés « creuses » avec easing
  (CUBIC→CubicV2). **Tout le reste (BEZIER avec poignées personnalisées, SINE,
  QUAD, EXPO...) est échantillonné à chaque frame en Linear** : « The evaluated
  samples use Linear between adjacent frames, which preserves BEZIER, SINE,
  QUAD, EXPO, and other unsupported curves. » Les contraintes et certains
  cycles forcent aussi un bake image par image. — `planning.py`.
  → **Oui, un export Blender typique (courbes Bézier du Graph Editor) bake
  chaque frame.** C'est ce qui explique les centaines de keyframes qu'on voit
  une fois l'animation importée dans l'éditeur Roblox.
- **Moon Animator** propose 11 familles d'easing (Sine, Quad, Cubic, Quart,
  Quint, Sextic, Expo, Circ, Back, Elastic, Bounce) × In/Out/InOut/OutIn, plus
  Linear et Constant (API Moon). Celles que Roblox ne supporte pas sont
  exportées en ajoutant des keyframes intermédiaires (« baking ») :
  « manually adding extra in-between keyframes to imitate the easing style's
  behavior », d'où des fichiers plus lourds. — [devforum] 2397709.
- **Optimisation automatique de l'éditeur Roblox** : il supprime les clés
  intermédiaires « If 3 or more consecutive keyframes have the same value in a
  track », et supprime une piste entière si elle ne contient que des valeurs
  par défaut. — `editor.md`. *Effet de bord à connaître : un « hold »
  (plusieurs clés identiques) est compacté ; le rendu reste identique, mais la
  structure change.*
- **Bouclage** : « A looping animation doesn't interpolate between the final
  keyframes and first keyframes » → il faut dupliquer la première pose à la
  fin. — `editor.md`.

### 2.5 Mélange de pistes : priorité, poids, fondu

- **Priorités** (de la plus forte à la plus faible) : Action4 > Action3 >
  Action2 > Action > Movement > Idle > Core. Idle est recommandée pour l'idle,
  Movement pour la locomotion, Action pour les actions qui doivent passer
  au-dessus. Le moteur évalue les pistes de la plus haute priorité à la plus
  basse « until joint weight reaches 1.0 ». — `AnimationPriority.yaml`.
- **Play(fadeTime = 0.1, weight = 1, speed = 1)** par défaut ; **Stop(fadeTime =
  0.1)** aussi. → **Chaque attaque démarre et s'arrête par défaut avec un fondu
  de 0,1 s (3 frames à 30 fps)**, qui adoucit (et donc « mollit ») la première
  pose. Pour une pose d'anticipation qui doit « claquer », il faut passer un
  fadeTime plus court ou nul (déduction, non testée ici). — `AnimationTrack.yaml`.
- À priorité égale, les poids sont moyennés : « the weights of the tracks will
  be used to combine the animations. » — `AnimationTrack.yaml`.
- **AdjustSpeed(0) met en pause**, une valeur négative joue à l'envers. C'est
  la brique du hitstop (voir 2.7). — `AnimationTrack.yaml`.
- **Marqueurs** : `GetMarkerReachedSignal(nom)` déclenche du code à un instant
  précis de l'animation (coup porté, VFX, son). `KeyframeReached` ne se
  déclenche que pour les keyframes dont le nom n'est pas « Keyframe ». —
  `AnimationTrack.yaml`.
- Conseil tiers : une attaque du haut du corps ne doit pas avoir de clés sur
  les jambes, pour que la locomotion reste visible dessous [extrait recherche,
  kitsblox « choppy »]. Cohérent avec le mécanisme de poids par joint ci-dessus.

### 2.6 Motor6D : on peut translater les membres (pas seulement les tourner)

- `Pose.CFrame` est un CFrame complet (position + rotation) appliqué au
  `Motor6D.Transform` du joint ; C0/C1 ne sont pas modifiés. — `Pose.yaml`.
- `Motor6D.Transform` est « overwritten every frame by the Animator after
  RunService.PreAnimation and before RunService.PreSimulation ». — `Motor6D.yaml`.
- **Conséquence pour le style anime** : une keyframe peut **décaler** un bras
  R6 (le sortir de l'épaule, l'avancer pour allonger visuellement un coup) ;
  c'est un décalage rigide, pas une déformation (le R6 ne se met pas à
  l'échelle par animation). Aucune source lisible ne documente l'usage de ce
  « déboîtement » par TSB/JJS ; c'est une possibilité technique, pas un usage
  confirmé (voir §6).
- La doc de performance recommande, pour l'animation procédurale, d'écrire
  `Motor6D.Transform` plutôt que C0/C1 (`performance-optimization/improve.md`,
  via recherche de code).

### 2.7 « Juice » au niveau du code (hors keyframes) : hitstop, shake, FOV

- **Hitstop** : le motif commun à ~15 dépôts GitHub Luau est
  `for _, track in humanoid:GetPlayingAnimationTracks() do track:AdjustSpeed(0) end`,
  puis on remet la vitesse d'origine après N frames ou secondes. On le
  déclenche sur un marqueur « HIT » (`GetMarkerReachedSignal("HIT")`,
  dépôt Andrei-TC/rblxGame) et on gèle **seulement l'attaquant et la
  victime** (Mogom/KoF_Like_Game, exemple « 6 frames = 100ms at 60fps »). Ce
  sont des projets amateurs : ils montrent le mécanisme, pas les valeurs de
  TSB.
- **Camera shake — RbxCameraShaker (Sleitnick)**, presets
  `CameraShakeInstance.new(magnitude, roughness, fadeIn, fadeOut)` :
  - Bump = (2.5, 4, 0.1, 0.75), PosInfluence 0.15, RotInfluence (1,1,1) — « high-magnitude, short, yet smooth »
  - Explosion = (5, 10, 0, 1.5), PosInfluence 0.25, RotInfluence (4,1,1) — « intense & rough »
  - Earthquake = (0.6, 3.5, 2, 10) ; Vibration = (0.4, 20, 2, 2) ; HandheldCamera = (1, 0.25, 5, 10) ;
    BadTrip = (10, 0.15, 5, 10) ; RoughDriving = (1, 2, 1, 1).
- **CameraKit (biotoxin495)**, valeurs par défaut : Shake 0.5 s, 0.15 stud,
  1.5°, fréquence 18 ; **PulseFieldOfView attaque 0.08 s, maintien 0, retour
  0.22 s** ; exemple d'impact : `Shake({Duration=0.75, Magnitude=0.28,
  RotationMagnitude=3})` + `PulseFieldOfView(7, {AttackDuration=0.04,
  ReleaseDuration=0.35})`, soit +7° de FOV en 0.04 s et retour en 0.35 s.
- Ralenti : Sorcerer Battlegrounds ralentit les animations de course en l'air
  via `AdjustSpeed` ([devforum] 3053080).
- Impact frames : les extraits de recherche indiquent qu'elles sont faites
  **par script (ViewportFrame côté client)**, pas dans l'animation
  [extrait recherche ; fils devforum « Advanced impact frames » 2468478 et
  « A Simple Impact Frame Showcase » 4355157, non lus].

---

## 3) Règles de pose et d'animation propres au combat anime R6 sur Roblox

Format : **règle** — chiffres — source — quand / quand pas.

1. **Ne jamais laisser l'easing par défaut (Linear) sur une pose finale.**
   Linear = « stiff and robotic » selon la doc officielle. La skill
   dillydog580 : « Linear interpolation is forbidden for final main movement »,
   courbes Bézier avec « intentional slow-in, slow-out, accents, overlap, and
   clean arcs ». — `editor.md` ; dillydog580 SKILL.md.
   *Quand pas* : Linear reste valable entre des clés très serrées (bake
   image par image) ou pour un mouvement mécanique voulu.

2. **Bloquer en Constant (pose à pose), puis décider segment par segment.**
   La skill dillydog580 : « Set blocking keys to constant interpolation »,
   puis poser le torse et les hanches, les jambes, les bras, et enfin la tête
   (dans cet ordre). Dans Roblox, garder Constant sur certains segments de la
   version finale donne le rendu « tenu puis claqué » propre au manga (voir
   règle 3). — SKILL.md ; `editor.md`.

3. **Aspect « anime / pose tenue » : Constant sur les segments voulus, et
   choisir la direction pour placer le snap.** Constant In/InOut/Out fait
   sauter au début, au milieu ou à la fin du segment (annonce 2016). Pour un
   rendu « bas fps » ou stepped, mettre toutes les clés en Constant ; « the
   less key frames you add, the more blocky it will be » ; il faut tester la
   bonne densité animation par animation (Happypigbaconalt 2024, réponse de
   Cerituam 2025). Pour « 12 fps », réimporter dans l'éditeur Roblox et mettre
   tout en Constant (vladxh). — [devforum] 25374, 2800541, 3051738.
   *Quand pas* : la locomotion et les idles, qui doivent rester fluides.
   *Aucune source lisible ne confirme que TSB ou JJS utilisent Constant* :
   l'extrait de recherche qui l'associe au style battlegrounds est une
   généralisation du moteur de recherche (voir §6).

4. **Pour le dépassement (overshoot), faire le rebond à la main.** Roblox n'a
   pas d'easing « Back ». Elastic « overshoots like an elastic curve » mais
   oscille plusieurs fois (effet ressort, rarement voulu sur un coup) ; Back
   n'existe que dans Moon, qui le bake. → En natif, poser une clé de
   dépassement 1 à 3 frames après le contact, puis une clé de retour.
   — `PoseEasingStyle.yaml`, API Moon, [devforum] 2397709. (Le nombre de frames
   est une déduction, pas un chiffre sourcé.)

5. **Densité de clés sur un geste rapide** : pour un coup de poing de 0,3 s,
   une clé au moins toutes les 3 à 4 frames (à 30 fps) pendant le mouvement,
   pour que l'interpolation suive l'arc voulu ; mais trop de clés « can cause
   stiffness ». L'idéal : des clés aux changements de pose majeurs (départ,
   anticipation, contact, follow-through, recovery). — [extrait recherche]
   kitsblox « fix choppy ».
   *Contradiction* : les animations bakées (Blender, Moon) ont une clé à
   chaque frame et sont réputées fluides → la « raideur » vient de clés denses
   **mal espacées**, pas de la densité en soi.

6. **Arcs : sur R6, ils doivent venir de plusieurs clés.** Le R6 a 6 blocs
   rigides, un pivot par membre, sans coude ni genou (kitsblox R6 vs R15
   [extrait recherche]). Une main qui décrit un arc entre deux clés d'un joint
   d'épaule ne suit l'arc que si l'interpolation de rotation le produit ;
   sinon il faut des clés intermédiaires (voir règle 5). → Pour un coup R6, les
   arcs lisibles passent par **la rotation du Torso (via la racine)** et par la
   **translation** des membres (§2.6), pas par une flexion.

7. **Ne clé-er que les joints concernés** (attaque haut du corps = pas de clés
   sur les jambes) et **choisir la priorité** : Action ou plus pour les
   attaques, Action2 à 4 pour ce qui doit passer au-dessus d'une autre action
   (hit reaction, grab). — kitsblox [extrait] ; `AnimationPriority.yaml`.

8. **Fondu d'entrée** : Play() fond par défaut sur 0,1 s. Pour une attaque
   « snappy », régler fadeTime court à l'appel. — `AnimationTrack.yaml`
   (valeur par défaut sourcée ; la recommandation est une déduction).

9. **Impact = animation + code.** Le « poids » vient du couple pose de contact
   et hitstop (`AdjustSpeed(0)` sur l'attaquant et la victime, déclenché par
   un marqueur), plus shake et coup de FOV (+7° en 0,04 s dans l'exemple
   CameraKit ; preset Bump ou Explosion de RbxCameraShaker). Mettre des
   **marqueurs nommés** dans l'animation pour caler ces effets. — GitHub
   (§2.7).

10. **Exagérer plutôt que reproduire le réel** : « Favor stylized, readable
    Roblox motion. Exaggerate arm swing, torso action, anticipation, impact,
    and silhouettes » ; vérifier chaque pose de face **et** de profil. —
    dillydog580 SKILL.md.

11. **Pieds** (hors combat aérien) : glissement maximal d'un pied posé =
    0,02 stud ; boucle fermée à 0,0001 d'unité et 0,1° près. — seuils de la
    skill dillydog580 (ses propres critères, pas une norme Roblox).

12. **Durées** : la skill dillydog580 vise 24 à 32 frames à 30 fps pour une
    action/boucle standard. Le tutoriel officiel de marche pose une clé toutes
    les **3 frames** (Contact 0, Low 3, Passing 6, High 9, Contact 12...) sur une
    timeline à 24 fps. — SKILL.md ; `create-an-animation.md`.

13. **Données de jeu TSB (contexte de timing, pas d'animation)** : combo M1 de
    4 coups, ragdoll garanti si le 4e touche, 3 % + 3 % + 4 % + 4 % = 14 % ;
    ragdoll de 2 s, annulable par un dash ; 0,5 s d'immunité au stun en se
    relevant. — Fandom TSB [extrait recherche]. Un site non officiel
    (the-strongest-battlegrounds.wiki) parle d'une parade « during the first 8
    frames of knockdown » : non vérifié, fiabilité faible.

---

## 4) Ce que « smooth » et « premium » veulent dire concrètement ici

Synthèse de ce que disent les sources lisibles et les extraits (pas de
citations inventées) :

- **« Smooth »** = en pratique :
  - pas d'easing Linear laissé par défaut (la doc Roblox appelle ça
    « robotic ») ; CubicV2 ou des courbes bakées ;
  - clés assez denses sur les gestes rapides pour que l'arc soit juste (au
    moins une toutes les 3-4 frames sur un coup de 0,3 s, d'après kitsblox) ;
  - boucles sans saut (première pose dupliquée en fin, seuils de continuité) ;
  - transitions propres entre pistes (priorités, poids, fondus, pas de clés
    sur les joints qui ne sont pas concernés) ;
  - souvent **faites dans Blender ou Moon puis bakées à 60 fps** : Moon est à
    60 par défaut, CAUTlONED conseille ×2 pour passer à 60. Le « lisse
    premium » de la communauté est donc souvent un bake dense, pas un petit
    nombre de clés CubicV2.
- **« Premium » / « high quality »** dans les packs commerciaux (BuiltByBit,
  KitsBlox/robloxanimations.com, Gumroad) [extraits recherche] :
  - couverture complète des états d'un système de combat (M1, heavy, dash
    avec variantes d'annulation, block, parry, hit reactions, finishers,
    animations de victime et de grab) : 27 à 184 animations par pack ;
  - animations « impactful and responsive right out of the box » ;
  - anticipation, impact exagéré, récupération qui s'enchaîne sur l'action
    suivante ; squash & stretch, follow-through, overlapping action ;
  - « tested in live combat systems with proper transitions, hitbox timing,
    and priority settings already configured » (KitsBlox) : le premium
    inclut donc l'intégration (timing des hitbox, priorités), pas seulement
    la pose ;
  - souvent livrées en R6 et R15.
- **Prix indicatifs des commissions** [extraits recherche] : à partir de 5 $
  (Chimz) ; 150 R$ minimum par animation (un autre animateur) ; 5 000 à
  7 000 R$ pour deux animations de combat ; offre d'emploi à 35 $/h ou
  10 000 R$/h pour un animateur R6 de Combat Warriors.
- **Ce qui rend un rendu « manga »** n'est documenté explicitement par
  **aucune source lisible**. Les briques techniques disponibles pour le
  produire sont : Constant (poses tenues/snap), clés de dépassement manuelles,
  translation des membres, hitstop par AdjustSpeed(0), coup de FOV et shake,
  impact frames par ViewportFrame. Leur combinaison est une inférence (voir §6).

---

## 5) Images téléchargées

**Aucune.** Tous les hébergeurs d'images pertinents sont bloqués par le
proxy : ArtStation (« Full Combat System R6 (40+ Animations) »
https://www.artstation.com/artwork/XnGZmn), BuiltByBit, Gumroad, KitsBlox, X,
YouTube, Fandom, raw.githubusercontent.com et les uploads du devforum. Les
seules images accessibles sur github.com étaient des captures de l'interface
de l'éditeur (creator-docs) ou un GIF de marche R6 (dillydog580
`docs/stylized-r6-walk-preview.gif`). Aucune ne montre de poses clés de
combat : elles n'ont pas été téléchargées. Le dossier
`scratchpad/tutos/roblox_web/` est créé mais vide.

---

## 6) Incertitudes et ce qui n'a pas pu être lu

- **Creator Hub (create.roblox.com) bloqué** : j'ai lu son équivalent source
  sur GitHub (`Roblox/creator-docs`, branche main à la date du jour). Il peut
  y avoir un léger décalage avec la version en ligne.
- **Contradiction In/Out** : `editor.md` donne In = lent au début, alors que
  `PoseEasingDirection.yaml` et le code du plugin Blender indiquent une
  convention inversée par rapport à TweenService et Blender. À trancher par
  un test visuel en jeu (ex. une rotation de 90° sur 30 frames en CubicV2 In,
  puis Out).
- **Contradiction densité de clés** : « trop de clés = raide » (kitsblox,
  extrait) contre bake de chaque frame largement pratiqué (Moon, Blender).
- **Contradiction Moon « Bézier par keyframe »** (kitsblox, extrait) : le
  format Roblox n'a pas de tangentes par pose, donc Moon bake forcément ces
  courbes ([devforum] 2397709). Les deux affirmations sont compatibles une fois
  qu'on sait que Moon bake.
- **Pratiques réelles de TSB, JJS, Jujutsu Zero, Heroes BG et Sorcerer BG** :
  aucune interview ni aucun texte de process d'animateur n'a été trouvé ou
  n'était lisible (X, YouTube et TikTok sont bloqués). Seuls sont confirmés
  les noms des animateurs TSB (Ultik/@KirvKirv1, @jp_Serene pour le pack
  « OFFICIAL Animations » du 22/01/2024). **On ne sait pas** si TSB utilise
  Constant, du bake à 60 fps, la translation de membres, ni quelles durées de
  hitstop ou quels réglages de shake. Les valeurs de §2.7 viennent de modules
  génériques ou de projets amateurs.
- **Pack « TSB OFFICIAL Animations »** (Creator Store 16072313171) : il
  permettrait d'inspecter les vraies KeyframeSequence de TSB (easings,
  densité de clés, fps, translations) dans Studio. C'est **la piste la plus
  riche**, mais elle est inaccessible depuis ce sandbox (nécessite Roblox
  Studio). À vérifier aussi : la licence ou les conditions d'usage (étude
  seulement).
- **Fiabilité des chiffres kitsblox** (0,3 s → une clé toutes les 3-4 frames)
  et des données TSB du Fandom : je ne les connais que par des résumés du
  moteur de recherche. Ils ne sont pas vérifiés mot pour mot.
- **Non lus** (bloqués) : article Medium de FireJxsus, article nilo.io
  Blender→Roblox, fiches BuiltByBit et Gumroad, ArtStation, doc en ligne de
  Moon Animator, Fandom TSB/JJS, fils X d'Ultik, descriptions de vidéos YouTube.
- **Pistes devforum repérées, laissées à l'autre chercheur** : « R6 IK + FK
  Blender Rig | V2.22 » (3586405, le rig de référence de la communauté),
  « Advice for positioning R6 limbs while animating? » (1533251), « Tips for
  making r6 animations » (3679871), « Combat Animation Lacks Power » (1875328),
  « Advanced impact frames » (2468478), « How to animate 2 characters and play
  it in-game like a takedown animation » (mrchipsma, cité dans 4020871),
  « Battlegrounds Camera Module » (3264520), « Tips on smooth animation »
  (1025384).
- Une tentative de diagnostic du proxy par `curl` a été refusée par le
  classifieur de permissions ; je ne l'ai pas contournée.
