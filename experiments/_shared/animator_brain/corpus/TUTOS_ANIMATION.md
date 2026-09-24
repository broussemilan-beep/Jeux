# Tutos et explications d'animation : ce qu'on en tire

Recherche du 2026-09-24, à la demande de Milan : « Roblox d'abord, puis
général ». Retour qui la motive (v6, 7/10) : « Les poses manquent d'une
touche manga. Même un coup simple n'est pas un coup simple : il y a une
anatomie et une règle différentes. »

**Sources.** Trois rapports complets sont dans `tutos/`. Ils sont notés
[LU] (lu), [MESURÉ] (mesuré) ou [RÉSUMÉ-RECHERCHE] (vu seulement en extrait
de moteur de recherche).
- `rapport_devforum.md` : 31 fils du DevForum Roblox, dont des critiques
  d'animations de combat par des animateurs expérimentés.
- `rapport_roblox_web.md` : documentation officielle Roblox (dépôt
  `creator-docs`), code du plugin Blender, dépôts de modules de combat.
- `rapport_anime3d.md` :
  - Arc System Works (GGXrd, interview 4Gamer, diapositives de Motomura) ;
  - Cartwright (Skullgirls, GDC 2014) ;
  - Mattesi (*FORCE*) ;
  - 4 extraits JJK, MHA et OPM mesurés image par image.

**Ce qui était bloqué.**
- Toutes les vidéos : YouTube passe par une vérification anti-robot.
- Les images du DevForum (hébergées sur S3), reddit, TikTok.
- Les pages roblox.com, dont l'asset « TSB OFFICIAL Animations » (16072313171).

Aucune image protégée n'est commitée.

## 1. Ce que la recherche a corrigé tout de suite

**L'export Roblox était faux depuis le début.** Tous nos exports écrivaient
`EasingStyle = 1` en le croyant Linear. La doc officielle dit :
1 = **Constant**, 0 = Linear. En jeu, chaque pose restait figée puis sautait
à la clé suivante. C'est corrigé partout, avec un garde-fou dans
`verify_export.py` (`ANGLES_MORTS.md`, §3).

> **Correction (même jour, fichier TSB officiel, `ETUDE_TSB.md`).** Les
> critères ci-dessous viennent du **pack** battleground. Les vrais M1 TSB ne
> les suivent pas : TSB est plus proche de nous que du pack. L'écart
> principal mesuré avec TSB est ailleurs : la **forme de la frappe** (clés
> éparses en Linear, palier de vitesse), et la **bascule du corps** sur les
> compétences. Le tableau est gardé comme trace.

## 2. « L'autre anatomie » : trois critères mesurés sur les coups droits (étalon pack)

Mesures au contact, comparées aux 4 M1 du pack pro. Le code est
`perception.pose_impact`, l'état est calculé par `etats.py`. Image de preuve :
`captures/verification/2026-09-24-cerveau-ligne-epaules-pro-vs-nous.png`.

| critère | M1 pro | nous (v4-v6) | verdict |
|---|---|---|---|
| angle bras / ligne des épaules | 18-28° | médiane 55° | **écart** |
| torse détourné de la direction du coup | 72-79° | médiane 44° | **écart** |
| bras libre (1 = tendu vers l'avant avec l'autre) | 0,0-0,3 | 0,89 | **écart** |
| translation d'épaule au contact (bras « décollé ») | 0,58-0,92 stud | 0,96 | pas d'écart |
| inclinaison du torse vers la cible | 2-14° | 12-16° | pas d'écart |

**Lecture.** Chez les pros, le torse pivote presque de profil et le bras qui
frappe **prolonge la ligne des épaules** : une seule droite de l'épaule arrière
jusqu'au poing. Le bras libre est ramené contre le corps. Chez nous, le torse
reste face à la cible, le coup part de la poitrine et **les deux bras sont
tendus vers l'avant**.

Trois sources indépendantes disent la même chose :
- **Motomura (ArcSys)** : « mettre ou non l'épaule dans le coup » change
  entièrement la force lue.
- **Mattesi** : l'extension est une seule droite, du pied arrière au poing.
- **DevForum (Shift4D)** : « tourne le torse encore plus ».

C'est la piste la plus solide pour « un coup simple n'est pas un coup simple ».

**Limite honnête.** L'étalon est un pack de M1 battleground, pas un ultime
manga. Il donne la base « coup qui pèse ». L'anime pousse plus loin (points
3 et 4).

## 3. Règles spécifiques R6 / Roblox (DevForum, doc officielle)

- **Le bras R6 joue l'avant-bras** (fungi3432). On translate le bras entier
  quitte à décoller l'épaule. On le fait déjà au contact ; l'écart éventuel
  est dans la garde et l'armement (garde pro : 1,15 stud).
- **Le « genou » R6 est à la hanche. Exagérer plus que sur un rig articulé**,
  comme en stop-motion Bionicle.
- **Détacher les membres est autorisé pendant les images rapides.** Sur une
  pose tenue en jeu, orienter le membre vers l'épaule pour qu'il ne paraisse
  pas « tombé ». Les sources se contredisent : à arbitrer sur nos captures.
- **Le torse vend la puissance** : il suit le bras avec 1 à 2 images de retard,
  sur un profil de vitesse lent → rapide → lent.
- **M1 battleground : aucune piste sur les jambes.** La course se superpose à
  l'attaque. C'est vérifié dans le pack pro, où les pistes des jambes sont
  vides sur les 4 M1. Ça ne s'applique pas aux skills et ultimes, où tout le
  corps joue.
- **Les skills s'animent sur place, le déplacement se fait par script.**
  On utilise des Animation Events et une LinearVelocity qui décroît, comme
  dans TSB selon les commentateurs.
- **Robotique**, selon les critiques :
  - tout en linéaire ;
  - toutes les parties partent et arrivent en même temps ;
  - changement de direction instantané ;
  - arrêt « mort » en fin de coup ;
  - récupération sans effort ;
  - seuls les bras bougent ;
  - pause en l'air entre deux poses trop espacées.
- **Technique Roblox** :
  - pas de tangentes Bézier : un style d'easing par pose et par joint ;
  - Cubic est déprécié (direction inversée en jeu), CubicV2 le remplace ;
  - Back n'existe pas pour les poses : un dépassement se fait avec une clé ;
  - `Play()` fait un fondu de 0,1 s par défaut ;
  - hitstop : `AdjustSpeed(0)`.

## 4. Règles de l'anime (ArcSys, Cartwright, Mattesi, extraits mesurés)

| règle | chiffre ou source | sur R6 |
|---|---|---|
| Deux poses extrêmes : compression en C, puis extension en droite hors d'équilibre. Le trajet passe en 1 à 2 images. | JJK mesuré ; Cartwright : anticipation → smear → pose principale → retour | possible |
| Épaule dans le coup | Motomura | torse + translation de l'épaule |
| 1 image de dépassement, 1 image de retard, casser le corps | Cartwright GDC 2014 | possible (rotations hors anatomie, translations) |
| Anatomie par pose : poing grossi, jambe allongée | GGXrd, scale d'os par pose | scale impossible ; translation vers la caméra, ou pièce échangée |
| « Ajouter l'angle de vue au modèle, pas à la caméra » | Ishiwatari (GGXrd) | caméra de finisher face au coup, bras amené vers l'objectif |
| Tenir le pic : 1 à 4,6 s mesurés, animé en 2 ou en 3 avec un tremblement | JJK, OPM, MHA | tenue avec vibration de ±0,03 à 0,08 stud [PROPOSITION] |
| Animation limitée : poses tenues 1 à 5 images, sans courbe | GGXrd : « lisser puis sauter des images = 3D qui rame » | Constant ; **à tester en A/B seulement**, le rythme est jugé bon |

## 5. Ce qui entre dans le cerveau

Nouvelles hypothèses dans `hypotheses.json`. Chacune a sa règle d'usage
(`quand` / `contre_indication`) et ses sources.

- **Mesurées** : `ligne_epaules`, `bras_libre_ramene`, `bras_avant_bras`.
  Les états v4 à v6 sont calculés : faux, faux, vrai.
- **Jugées à l'œil** : `compression_extension`, `depassement_1f`,
  `recuperation_effort`, `poses_tenues_limitees`.

**Principe (Milan).** On nourrit, on ne comble pas. Aucune règle ne
s'applique partout. La prochaine étape est un **A/B sur un seul coup**,
jugé par Milan, avant toute généralisation.

## 6. Pistes ouvertes

- **Asset « TSB OFFICIAL Animations » (16072313171).** S'il est authentique,
  c'est la meilleure référence possible : les vraies poses, les easings et la
  densité de clés de TSB. Il faut l'ouvrir dans Studio et l'exporter en
  `.rbxm` (clic droit, puis « Save to File ») ; `corpus.load_rbxm_sequences`
  le lit déjà.
- **Tutos vidéo.** Fait : Milan a envoyé 6 vidéos, sans le son. Elles sont
  étudiées image par image aux §7 et §8.

## 7. Vidéos envoyées par Milan (zips du 2026-09-24) : étude visuelle

Six vidéos muettes (640x360), rejointes depuis les zips découpés. On les étudie
image par image, sur des planches. Les planches et les vidéos restent dans le
scratchpad : ce sont des refs protégées, donc elles ne sont jamais commitées.
Les quatre tutos longs ont chacun leur rapport dans `tutos/rapport_*` (§8).
Les deux courts sont décrits ci-dessous.

### 7.1 Nakamura, « Speed/Scale Contrast » (sakuga, 23 s) [VU]

- **Cadrage.** Course et saut en plan très large : le perso est minuscule.
  Coupe sec sur un gros plan où le poing grossit jusqu'à remplir le cadre.
  L'avant-bras est vu en raccourci et le poing vient vers l'objectif.
- **Impact.** 2 à 4 images en noir et blanc inversé, avec des rayons.
- **Après l'impact.** Retour en plan très large sur le dôme de l'impact, puis
  une tenue sur les conséquences.
- **Leçon.** La puissance ne vient pas de la pose seule. Elle vient du
  **contraste d'échelle d'un plan à l'autre** : petit/lent, puis énorme/rapide,
  puis petit/figé. Ça confirme `poing_gros_plan` : on amène le poing vers la
  caméra, on ne le grossit pas. Ça confirme aussi `cartes_impact`.
- **Nuance pour nous.** Ça sert la caméra **cinématique** (finisher). En
  caméra de jeu, on ne peut pas couper de plan. Il reste le poing vers la
  caméra et les cartes d'impact.

### 7.2 « Advanced Movement System » (vitrine Roblox R6, 27 s) [VU]

Ce système de mouvement est vendu comme « premium ». On a relu les dash à
6 i/s, recadrés. Ce qui le rend fluide et pas robotique :

- **Dash avant.** Le corps passe **à l'horizontale** (torse ≈ 90°, plongeon
  « superman », bras et jambes dans l'axe) pendant environ 1/6 s, puis il se
  roule en boule et se relève penché. C'est une pose extrême, tenue très
  peu de temps, entre deux poses normales.
- **Dash arrière et latéraux.** Salto arrière groupé, ou roue/roulade :
  rotation de tout le corps, jamais un simple glissement.
- **Course.** Torse penché vers l'avant, bras qui balancent haut, grande
  foulée, poussière à chaque pas. **Inclinaison directionnelle** : le corps
  penche du côté où on tourne.
- **Atterrissage.** Les bras s'ouvrent grand (T large), puis tout se
  compresse (squash), puis on revient au neutre. Le moment le plus lisible
  est la silhouette ouverte.
- **Leçon.** Même en Roblox « smooth », la qualité perçue vient de **poses
  très éloignées du neutre, en passant par tout le corps** (torse 60-90°),
  tenues peu de temps. Ce n'est pas un lissage. C'est cohérent avec
  `bascule_competence` : TSB compétences p90 44-97°, notre charge 35°.
- **Contre-indication.** C'est du mouvement (dash), pas un coup. On ne recopie
  pas ce plongeon tel quel sur une frappe. On garde le principe : une pose
  hors d'équilibre franche, pas une pose « debout + bras ».

## 8. Les quatre tutos longs : ce qu'ils disent vraiment

Quatre agents les ont étudiés image par image, sans le son. Le texte à
l'écran a été lu quand il y en avait. J'ai revérifié moi-même les images clés
de chaque rapport. Rapports complets :
- `tutos/rapport_video_uppercut_moon.md`
- `tutos/rapport_video_punch_blender.md`
- `tutos/rapport_video_techniques_anime.md`
- `tutos/rapport_video_critique_poses.md`

| vidéo | ce qu'elle apporte | sûr / estimé |
|---|---|---|
| **Uppercut R6, Moon Animator** (tuto « smooth ») | Linear ; 13 clés à 60 i/s, une toutes les 5 f ; la clé du milieu rapprochée à 2-3 f pour le snap ; **toutes les pistes clées aux mêmes images** (l'overlap est dans les poses : bras qui traîne « dislocated ») ; tenue **jamais figée** (wiggle en petits cercles qui ralentissent) ; départ accroupi, torse de profil | texte à l'écran lu ; angles estimés |
| **Punch R6, Blender** (add-on Rbx Animations) | charge **asymétrique** : torse ~90° détourné, bras avant tendu, bras arrière armé haut, grand écart ; frappe en **2 f** (60→62), avec une clé intermédiaire sur le seul bras ; contact : torse pivoté ~180°, penché ~45°, bras translaté vers l'avant, bras libre replié, jambe arrière presque couchée ; espacements très irréguliers | poses lues image par image ; angles à l'œil |
| **Techniques anime** (impact frames, smears, obari, Kanada, timing) | pic tenu = **images d'impact** (1 à ~55) ; armé tenu 0,9-1,8 s puis poing vers la caméra en ~8 images (obari) ; smear = trajet du bras en 1-2 images ; « hold and release » ; timing « en 4 » : 3-5 images par dessin pendant l'action, 8-10+ sur les clés | comptes approximatifs (30 i/s contre 24) |
| **Vlog DeHapy + critique Xoaterz** | planche ✗/✓ : ✗ **croix de face « stickman »**, ✗ accroupi tenu genoux écartés ; ✓ torse de 3/4, bras armé derrière, genou levé, « akin to The Serious Punch (TSB) » ; **ligne d'équilibre** tête → pied d'appui ; pros : pose tenue 8-10 i puis coup en 3-4 i à 30 i/s ; images d'impact faites dans Roblox (ColorCorrection, Highlight, FOV) | planche lue en clair ; repose en direct vue sans le son |

**Ce qui change dans le cerveau** (`hypotheses.json`) :
- **Nouvelles hypothèses** :
  - `silhouette_non_croix` (confiance 0,7) ;
  - `torsion_charge_contact` ;
  - `tenue_vivante` ;
  - `arme_tenu_long` ;
  - `ligne_equilibre`.
  Chacune a son `quand` et sa `contre_indication`.
- **Hypothèses existantes, nouvelles sources** : `compression_extension`,
  `frappe_lineaire`, `poses_tenues_limitees`, `cartes_impact`,
  `poing_gros_plan`, `bascule_competence`.
- **`ligne_epaules` recadrée** : confiance 0,4 → 0,55, mais seulement pour
  les coups qui comptent. Les M1 TSB la contredisent.
- **Nuance sur la compression.** Sur R6, la « compression en C » se lit
  surtout par la **torsion du torse**, pas par un dos rond. L'accroupi tenu
  est explicitement rejeté (Xoaterz, et Milan en v1-v2).

**Contrainte R6 découverte au labo** (`scripts/croquis_v7.py`). Le torse R6
est aussi le bassin : un torse de profil penché vers la cible fait basculer
la ligne des hanches. Au-delà de ~30°, les deux pieds ne peuvent pas rester
au sol sans grand écart. La « ligne jetée » se fait pied arrière en l'air.

**Ce qu'aucun tuto ne montre.** Aucun graph editor, aucune courbe. Le
« smooth » R6 vient des poses, de l'espacement des clés et d'amortis faits à
la main, jamais d'un lissage. C'est cohérent avec le fichier TSB (Linear
partout).

**Limites.**
- Aucune vidéo n'est de TSB lui-même.
- Toutes les vidéos sont sans le son.
- Les angles sont estimés sur du 640x360.
- Ce sont des indices convergents, pas des mesures. Le juge reste l'écran,
  puis Milan.
