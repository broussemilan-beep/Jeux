# A4 — Pack battleground (19 animations R6), lu comme un apprenti

Chantier 4, 2026-09-26. Source unique : `battleground_animation_pack_v1.0.1.rbxm`
(19 KeyframeSequence R6), plus une comparaison avec 4 M1 du fichier officiel TSB.
Ce sont des **apprentissages** (« ici, l'animateur fait X parce que Y »), pas des règles.

Statuts : **vu** = j'ai regardé la planche moi-même ; **mesuré** = sorti d'un script
sur les poses exactes du fichier ; **lu** = texte d'une étude existante du dépôt ;
**déduit** = mon interprétation.

## 0. Méthode et outils (pour pouvoir refaire et vérifier)

Tout est dans `scratchpad/c4/frames/A4_pack_battleground/` (rien n'est écrit dans le dépôt).

- `etude.py` : pour chaque animation, lecture exacte des poses
  (`corpus.load_rbxm_sequences` + `resample_linear` à 60 i/s, équation du moteur).
  Il produit trois fichiers :
  - `<nom>_film.png` : planche-contact, une case toutes les 2 images (30 i/s) ou
    toutes les 3 (20 i/s) pour les clips longs, et toutes les images pour les
    réactions. Trois vues fixes : 3/4 face, profil droit, **dos (caméra de jeu)**.
  - `<nom>_courbes.png` : courbes image par image (tracé détaillé plus bas).
  - `<nom>.json` : les séries.
- Ce que tracent les courbes :
  - hauteur, avance et décalage latéral du torse ;
  - buste : lacet, penché, côté ;
  - tête dans le torse ;
  - bras et jambes en **swing / écart** dans les axes du torse. Swing 0 = pendu,
    +90 = pointé devant, 180 = en haut, -90 = derrière. Écart + = vers l'extérieur,
    - = croisé devant. C'est continu, contrairement à l'azimut de `geo_pose`, qui
    saute quand le bras pend.
  - vitesse des bouts (poings, pieds, torse).
- `poses.py` : poses choisies en grand, 2 à 4 vues, pelure d'oignon possible.
  Fichiers : `1_Run_poses.png`, `2_M1_1_poses.png`, `backdash_poses.png`,
  `fdash_poses.png`, `downslam_v2_poses.png`, `block_idle_pose.png`.
- `resume.py` : amplitudes, images des extrêmes, harmoniques H1/H2 et phase des
  cycles (FFT).
- `phases.py` : découpe mouvement / tenue. Une tenue, c'est quand **tous** les
  bouts vont à moins de 4 studs/s.
- `extremes.py` : images où beaucoup de courbes changent de sens, donc des poses
  clés probables. Validé sur TSB M1, où elles tombent exactement sur les clés
  réelles (6, 8, 10, 14, 20).
- `fists.txt` : trajectoire des poings image par image (M1_1-4, Uppercut).
- `tsb_M1_planche.png` : planche de clés de TSB M1 (`outils/planche_cles.py`).

**Rappels lancés avant** : `rappel.py` sur « cycle de course », « dash »,
« réaction », « M1 combo », « tête regard cible ». J'ai relu `corpus/README.md`,
`ETUDE_TSB.md`, `TUTOS_ANIMATION.md` §1-3 et
`corpus/poses/sources/pro_pack_battleground.json`. Ce dernier est l'étude
géométrique déjà faite des M1_1-4, de l'Uppercut et des Downslams : armé, contact,
trajectoire du poing. Je ne la recopie pas : je la cite quand je m'appuie dessus
et je vais plus loin (cycles, dashes, réactions, garde, enchaînement, regard,
comparaison TSB).

**Ce que le fichier est, techniquement** (mesuré) :
- **cuit** : une clé par image, pour toutes les parts. Écart entre clés de 1 image
  à 60 i/s. Exceptions : Uppercut, Block Hit et Block Idle ont un écart de
  0,857 image, soit **70 i/s**, cuits à une autre cadence.
- les **poses clés d'origine ne sont donc pas lisibles directement**. Je les
  retrouve par les extrêmes, les changements de sens, les tenues et les creux de
  vitesse.
- priorité non renseignée (`None`) sur les 19 clips.
- le chargeur ne lit pas les `KeyframeMarker`, et je n'ai pas vérifié s'il y en a.

---

## 1. Par animation

### 1.1 Idle (1,10 s, boucle)

Vu : `1_Idle_film.png`. Mesuré : `resume.py --cyc`.

- **La pose** : quasi neutre, debout.
  - Hanche à 2,94, soit 0,06 plus bas que le repos.
  - Pieds un peu écartés (±0,66 latéral contre ±0,5 au repos), pied gauche
    0,21 en arrière.
  - Buste tourné de +3,8°, tête contre-tournée de +3,4° : le regard reste droit.
  - Bras le long du corps.
  - **Ce n'est pas une garde de combat.** La garde est un clip à part
    (Block Idle, bras seulement).
- **Le mouvement est minuscule** :
  - torse : 0,03 stud de montée et descente ;
  - penché : 1,5° ;
  - tête : 2,3° ;
  - bras : 2 à 3° d'écart.
- **Mais il est ordonné.** Toutes les courbes sont des sinus purs (H2/H1 < 0,1)
  de période 66 images, avec des pics décalés d'environ un quart de période :

  | courbe | image du pic |
  |---|---|
  | penché avant | 15,6 |
  | hauteur | 30,7 |
  | écart des bras | 44 à 46 |
  | tête levée | 46,8 |

- Ici, l'animateur fait respirer le corps comme une vague : la poitrine penche,
  le corps monte, puis les bras s'ouvrent et la tête se lève. Le décalage donne
  du vivant sans amplitude (déduit).
- Vu du dos à la caméra de jeu, c'est presque invisible (vu, `1_Idle_film.png`).
  L'idle du pack est une base calme, pas une pose de caractère (déduit).

### 1.2 Walk (0,98 s = 2 pas, boucle)

Vu : `1_Walk_film.png`, `1_Walk_courbes.png`. Mesuré.

- **Construction classique contact → bas → passage → haut** (mesuré, pieds
  image par image) :
  - contact du pied gauche vers i0 (jambe G devant, +43°) ;
  - point **bas** du torse à i5 (-0,17), juste après le contact ;
  - passage vers i15-18 ;
  - point **haut** à i23 (-0,02), environ 6 images avant le contact suivant (i29-30).
  - La hauteur oscille **deux fois par cycle** (H2 dominant) : un rebond par pas.
- **Poids** :
  - buste penché en avant en permanence, de 13 à 17° : une marche « de
    combattant », pas une marche neutre ;
  - penché côté presque nul (±0,6°).
- **Ce qui oscille une fois par cycle** (sinus, H2/H1 ≈ 0,01) :
  - lacet du buste ±16,7° ;
  - bras de -13 à +36° : ils vont plus devant que derrière, donc ils balancent
    **surtout devant le corps** ;
  - jambes de -40 à +43°.
- **Opposition** : épaule droite en avant quand la jambe gauche est devant (pic
  du lacet à i59, jambe G devant à i59).
- **Asymétrie** : la courbe des jambes n'est pas un sinus pur (H2/H1 = 0,23).
  La jambe recule lentement, pied au sol, et revient plus vite en l'air.
- **Tête = gyroscope** (mesuré) :
  - la tête tourne de ±16,4° dans le torse, en phase inverse du lacet (±16,7°) ;
  - direction du regard dans le monde : **0,0° sur tout le cycle**.
  - Ici, l'animateur annule exactement la rotation du buste pour que le regard ne
    bouge pas. Soit c'est fait à la main avec soin, soit c'est contraint (déduit).
  - Seul le hochement reste : tête levée de 0,6 à 6,4°, deux fois par cycle.
- **Pieds et vitesse au sol** (mesuré) :
  - le pied d'appui glisse vers l'arrière à environ **7 studs/s** (G : +1,21 à
    i4 → -0,67 à i20) ;
  - le pied qui revient monte jusqu'à 0,75 stud (i10) ;
  - écart avant/arrière des pieds : environ 3 studs.
  - Conséquence (déduit) : pour que les pieds ne patinent pas, le personnage doit
    avancer à environ 7 studs/s, sous la WalkSpeed par défaut de Roblox (16).
    Sinon il faut accélérer le clip (`AdjustSpeed`) en proportion.

### 1.3 Run (0,65 s = 2 pas, boucle)

Vu : `1_Run_film.png`, `1_Run_poses.png` (5 poses en 4 vues). Mesuré.

- **Poses clés du pas** (vu + mesuré, `1_Run_poses.png`) :

  | image | pose | ce qu'on mesure |
  |---|---|---|
  | i0 | **contact** | jambe D devant +67°, pied D à +1,31 devant, 0,26 au-dessus du sol ; bras D derrière (-47°), bras G devant (+137°) |
  | i3-4 | **bas** | torse au plus bas (-0,43) |
  | i10 | **passage** | jambes croisées sous le corps, bras près du corps : silhouette la plus compacte |
  | i16-17 | **haut / envol** | jambe arrière tendue à l'horizontale derrière, pied G à 2,4-2,6 de haut à i22-26 (talon aux fesses) |
  | i20 | contact G | miroir exact de i0 |

- **Temps** :
  - 20 images par pas, soit 0,33 s ;
  - phase au sol courte : le pied D est au sol de i3 à i8 environ (y ≈ 0),
    **environ 6 images sur 20** ;
  - vol vers i10-13 : les deux pieds sont en l'air (D à 0,93-1,42, G à 0,28-0,76).
- **Posture** :
  - torse **abaissé en permanence** de 0,27 à 0,43 stud ;
  - buste penché de **33 à 43°** vers l'avant. Il penche le plus au passage (i10)
    et le moins au contact (i19-39).
  - C'est une course de sprint et d'anime, très penchée (déduit).
- **Ce qui oscille** :
  - lacet ±21,7° et côté ±14,8°, en phase (le buste roule et vire ensemble) ;
  - **bras de -48 à +137°** : 185° d'amplitude, le poing monte au-dessus de
    l'épaule devant ;
  - écart des bras ±22°, en diagonale : bras devant = croisé vers l'intérieur,
    bras derrière = ouvert.
  - Vu de dos, ce balancier en diagonale fait déborder les bras bleu et vert de
    chaque côté du torse. C'est ce qui rend la course lisible depuis la caméra de
    jeu (vu, ligne « dos »).
- **Jambes** :
  - de -88 à +67°, forte asymétrie (H2/H1 = 0,18). La jambe reste 24 images à
    reculer (au sol puis en poussée) et revient devant en 15 images.
  - Écart des jambes de -18° au contact : **le pied se pose sous la ligne
    médiane**, comme sur un fil (vu en vue de face).
- **Faux genou R6** (mesuré) : la jambe qui revient est **translatée** jusqu'à
  1,1-1,6 stud (valeurs des Poses). La tête, elle, ne l'est jamais. Ici,
  l'animateur « raccourcit » la jambe par translation pour que le pied passe
  au-dessus du sol : R6 n'a pas de genou.
- **Tête** :
  - contre-rotation de ±16,3° pour un lacet de ±21,7°, soit un regard monde de
    ±3° (mesuré) ;
  - tête levée de +13° en permanence pour compenser le buste penché de 33-43°.
    Le regard reste plus bas que l'horizon (déduit du calcul).
- **Décalage bras / jambes** (mesuré, phases H1) : pic avant du bras D à
  i19,8, pic arrière de la jambe D vers i21,9. Le bras précède sa jambe opposée
  d'environ 2 images.
- **Vitesse au sol** (mesuré) : le pied planté recule d'environ 1,5 stud en
  4 images, soit **environ 22 studs/s** (19 à 25 selon l'intervalle). C'est
  l'ordre de grandeur de vitesse de course que le clip suppose (déduit).

### 1.4 M1_1 à M1_4 (0,65-0,70 s chacun)

Vu : `2_M1_*_film.png`, `2_M1_1_poses.png`, `2_M1_1_courbes.png`. Mesuré :
`fists.txt`, `phases.py`. La géométrie de l'armé et du contact est déjà dans
`pro_pack_battleground.json` (lu). Ce que j'ajoute :

- **Quatre coups, quatre formes, deux bras** (vu + mesuré sur les trajectoires
  de poing) :

  | clip | coup | trajectoire du poing | fin du coup |
  |---|---|---|---|
  | M1_1 | **crochet droit large** | cercle de derrière la tête (i10 : -1,6 derrière, 4,0 de haut) → côté droit (i14 : +1,8) → devant (i15-16 : +2,9) → en travers à gauche (i18 : -1,8) | le poing **traverse la cible et continue** |
  | M1_2 | **direct gauche** | arrive à +3,4 devant à i11 | pic à **127 studs/s** à i11, puis **arrêt sec** (8,9 à i12) |
  | M1_3 | coup court du **bras gauche** | l'avant-bras balaie en travers de la poitrine (revers ou coude : non tranché, comme l'étude existante) ; poing max 71 studs/s | le bras droit reste armé derrière tout le clip |
  | M1_4 | **direct droit plein corps** | demi-cercle par la droite, rotation du buste de **161°** | arrêt à +3,3 devant, puis la plus longue tenue |

  Alternance des bras : D, G, G, D.
- **L'enchaînement est UNE chorégraphie coupée en 4** (mesuré) :
  - fin de M1_1 → début de M1_2 : écart des poings 0,06 stud ;
  - fin de M1_2 → début de M1_3 : 0,00 ;
  - fin de M1_3 → début de M1_4 : 0,30 ;
  - M1_1 part du repos exact, M1_4 finit dans une pose (pas au repos).
  - Ici, l'animateur a animé le combo d'un seul tenant puis l'a découpé. Chaque
    clip commence là où le précédent s'arrête : la préparation d'un coup est la
    pose finale du précédent. C'est pourquoi M1_2 n'arme qu'en 4 images et M1_4
    en 6 (déduit, cohérent avec `corpus/README.md` §2).
- **Temps de chaque clip** (mesuré, `phases.py`, T = tenue < 4 studs/s) :

  | clip | armé | lâcher → contact | après | tenue |
  |---|---|---|---|---|
  | M1_1 | i0-i10 : garde levée en 4 images, puis enroulement à -98° | i10-i16 (6 f) | continuité jusqu'à i22 | **i23-i39 (17 f)** |
  | M1_2 | i0-i4 | i5-i11 (6 f) | — | i12/14-i39 : **21-26 f** |
  | M1_3 | balayage i1-i9 | retour i10-i16 | — | i22-i39 (18 f) |
  | M1_4 | i0-i6, lent (poings 5-8 studs/s) | i7-i16 (9 f) | — | **i22-i42 (21 f)** |

  - Les tenues ne sont pas tout à fait mortes : une dérive qui s'éteint
    (M1_1 : lacet +52 → +45 de i23 à i33, puis immobile).
- **La chaîne cinétique mesurée** (pics de vitesse, images) :
  - M1_2 : le buste tourne le plus vite à **i8**, le bras qui se retire aussi à
    i8 (92 studs/s), le poing qui frappe arrive à **i11** : **3 images de retard**.
  - M1_4 : buste à i11 (36°/image), poing gauche qui se retire à i11
    (103 studs/s), poing qui frappe à **i13** : **2 images de retard**.
  - M1_1 : buste et poing ensemble à i14 (le bras est porté par le buste). Puis
    le bras **continue seul** de i15 à i22, quand le buste freine (swing de 100
    à 180° dans le torse) : c'est le suivi.
  - Ici, l'animateur fait partir le buste et le bras qui se retire ensemble, puis
    le poing arrive 2 à 3 images après. Le bras qui se retire va souvent **plus
    vite que le poing qui frappe** (M1_4 : 103 contre 63 studs/s).
- **Deux formes de vitesse au contact** :
  - crochet (M1_1) : bosse large (68 → 102 → 91 → 84 → 68), le poing ne
    s'arrête pas ;
  - direct (M1_2) : un « pop » d'une image (45 → **127** → 9).
  - Le crochet vend le balayage, le direct vend l'impact sec (déduit).
- **Tête = gyroscope, aussi en combat** (mesuré) :

  | clip | amplitude du lacet du buste | amplitude du regard de la tête dans le monde |
  |---|---|---|
  | M1_1 | 156° | **21°** |
  | M1_2 | 137° | **9°** |
  | M1_3 | 55° | 28° |
  | M1_4 | 162° | 23° |

  Ici, l'animateur contre-tourne la tête de 61 à 85° dans le torse pour que les
  yeux restent sur la cible. Le corps entier tourne sous une tête qui vise.
- **Jambes jamais posées** (mesuré, poids 0) : elles suivent le torse en bloc.
  En jeu, la marche ou la course du dessous les pilote. Les pieds glissent
  jusqu'à 2,2 studs et descendent jusqu'à -0,25 sous le sol : c'est un
  artefact, pas un choix (lu dans l'étude existante, recoupé ici).
- **Vu du dos** (caméra de jeu, vu sur les films) :
  - en tenue de M1_2 et M1_4, le bras qui frappe est **caché derrière le torse**.
  - Ce que le joueur voit, c'est la rotation du dos et le bras qui s'est retiré,
    au premier plan.
  - Ici, le coup se lit depuis la caméra de jeu par la **torsion du buste**, pas
    par le bras (déduit ; important pour nos caméras « de jeu »).

### 1.5 Uppercut (0,82 s, cuit à 70 i/s)

Vu : `3_Uppercut_film.png`, `3_Uppercut_courbes.png`. Mesuré.

- **Le mouvement le plus « souple » du pack** : aucune tenue (`phases.py` :
  mouvement de i2 à i49), des courbes en cloche partout.
- **Armé** i0 → i14, 14 images :
  - accroupi (torse -0,71 à i15) ;
  - buste tourné à -69°, penché de +25° en avant, **penché de côté -34°**
    (épaule droite haute) ;
  - tête contre-tournée de -31° ;
  - bras gauche devant et bas.
  - À **i14, les poings ne bougent presque plus** (creux de vitesse) : c'est
    l'instant d'enroulement maximum.
- **Lâcher** i14 → i25 :
  - le corps **remonte de 0,98 stud** (de -0,71 à +0,26 : plus haut que le repos,
    sur la pointe) ;
  - le buste se déroule jusqu'à +58° et passe en arrière (-12° vers i30) ;
  - le bras droit monte à **164°** (au-dessus de la tête) ;
  - poing à 94-99 studs/s vers i19 ;
  - retour au repos exact en i30 → i49, 20 images.
- **La tête n'est pas un gyroscope ici** : regard monde sur 101°. Elle suit le
  coup vers le haut (mesuré). Ici, la tête accompagne la direction du coup,
  parce que la cible monte (déduit).
- Jambes non posées : les pieds passent jusqu'à -0,39 sous le sol quand le buste
  bascule (mesuré). C'est un artefact en R6 si le calque de jambes du dessous ne
  compense pas.

### 1.6 Downslam V1 (1,08 s) : marteau à deux mains

Vu : `3_Downslam_V1_film.png`. Mesuré.

- **Armé** i0-i15, 16 images :
  - bras montés au-dessus de la tête (swing 0 → 180) ;
  - buste **cambré en arrière** (-20° mesuré par mon repère, -48° dans l'étude
    existante, qui prend un autre avant) ;
  - jambe droite ramenée en arrière (-77°) ;
  - la tête se baisse (el -20) puis se relève.
- **Frappe** i16-i26 :
  - le buste bascule jusqu'à **l'horizontale** (+84°) ;
  - le torse descend de **1,4 stud** (hanche de 3,0 à 1,6) ;
  - les deux poings arrivent **pile au sol** (y min -0,03) ;
  - pic à 100 studs/s vers i20, arrivée **amortie** (48, 24, 7).
- **Tenue** au sol i30-i42, puis relevé en 23 images.
- Ici, les jambes **sont posées** (contrairement aux M1) : les pieds restent au
  sol (y ≥ -0,10) alors que le torse descend de 1,4. L'animateur a « planté »
  les pieds, sinon ils traverseraient le sol (mesuré + déduit).
- La tête se relève (el +18 à i24) quand le buste est couché : elle regarde
  devant, pas le sol (mesuré).

### 1.7 Downslam V2 (1,08 s) : coup de poing au sol, « atterrissage de super-héros »

Vu : `3_Downslam_V2_film.png`, `downslam_v2_poses.png`. Mesuré.

- **Armé** i0-i13 :
  - le corps s'enroule et **descend déjà** (torse de 0 à -1,1 entre i8 et i14) ;
  - buste penché fort sur le côté ;
  - bras droit en l'air.
- **Frappe en 2 images** (i13 → i15) : poing à **162 studs/s**, la valeur la plus
  haute du pack, puis arrêt sec au sol. L'étude existante a mesuré que le bras
  est figé dans le torse : c'est le **roulis du buste** qui abat le poing (lu).
- **Pose d'arrivée** tenue d'environ 20 images :
  - jambe gauche **couchée à l'horizontale derrière**, au sol ;
  - genou droit (jambe D verticale) ;
  - poing droit au sol, tête baissée.
  - C'est la silhouette de l'atterrissage de super-héros, lisible de loin (vu).
- **Relevé** lent, environ 22 images (i38-i60), retour au repos exact.
- **Comparaison des deux Downslams** :

  | | V1 | V2 |
  |---|---|---|
  | lâcher | 10 images | 2 images |
  | arrivée | amortie | sèche |

  Ici, V1 vend le poids qui s'écrase, V2 la vitesse qui claque (déduit).

### 1.8 Forward Dash (0,97 s)

Vu : `3_Forward_Dash_film.png`, `fdash_poses.png`, courbes. Mesuré (`phases.py`).

- **Trois temps très nets** :
  1. **Entrée lente** (i2-i24, environ 15 images utiles, bouts à 18 studs/s au
     plus) : le corps glisse vers une **pose de glisse**.
     - buste tourné de profil (lacet jusqu'à -70°) ;
     - tête contre-tournée (regard monde ±20°) ;
     - **jambe droite tendue à l'horizontale derrière** (-77°) ;
     - bras gauche pointé devant, bras droit levé derrière ;
     - torse qui s'abaisse doucement.
  2. **Tenue i25-i40 (16 images, environ 0,27 s)**, pratiquement immobile.
     C'est là que le script fait voyager le personnage (déduit : l'animation ne
     translate pas le corps vers l'avant, avance ≈ 0).
  3. **Claque de freinage** i41-i50 :
     - le buste pivote de **-65 à +57° en environ 5 images** (vitesse angulaire
       jusqu'à 2 314°/s) ;
     - poings à 113 studs/s ;
     - jambe droite projetée devant (+50°) pour freiner ;
     - le torse descend encore (accroupi).
     - Puis **tenue finale** i51-i58.
- Ici, l'animateur vend la vitesse par l'**immobilité de la pose pendant le
  voyage** : le corps devient un projectile figé, trainée derrière, profil vers
  la direction. Toute l'énergie visible est mise dans l'arrivée (freinage qui
  claque). Le départ est doux, parce que le script fait le départ (déduit).

### 1.9 Backdash (1,23 s) : un vrai salto arrière

Vu : `3_Backdash_film.png`, `backdash_poses.png` (14 poses, profil + dos). Mesuré.

- **Ce n'est pas un simple recul : ce sont deux rotations arrière** (vu) :
  1. **Rondade arrière / flip sur les mains** :
     - i0-i10 : les bras balancent au-dessus de la tête (swing 0 → 180 en
       10 images), le buste se cambre ;
     - i12 : corps à l'horizontale, bras vers le sol ;
     - i16-i20 : **à l'envers sur les mains**. Poings à y = -0,24 : les mains
       touchent le sol (mesuré). Le torse est au plus bas (-0,8).
     - i26 : horizontale, pieds vers l'arrière ;
     - i32-i37 : réception accroupie (torse -0,8 à i37).
  2. **Salto groupé en l'air** :
     - i44-i56 : corps en boule ;
     - le torse **monte de +1,4 stud à i50** : le saut est dans l'animation.
     - i62 : ouverture ;
     - i66-i68 : réception (creux -0,35) ;
     - i74 : debout au repos exact.
- **Pas une seule tenue** sur 74 images : c'est du mouvement continu,
  acrobatique (mesuré).
- Le déplacement horizontal n'est **pas** dans l'animation (avance ≈ -0,2), mais
  **la hauteur du saut, si** (déduit : le script recule le personnage, l'anim
  gère la verticale).
- Tête : se lève pendant le salto (el +54 vers i55) (mesuré).

### 1.10 Sidedash L / R (0,53 s)

Vu : `3_Sidedash_L_film.png`, courbes. Mesuré.

- **R est le miroir exact de L** : écart maximal 0,00 sur toutes les courbes
  miroir (mesuré). L'animateur a fait un côté et l'a copié en miroir.
- **Contre-mouvement d'abord** : le torse part de **0,3 stud du côté opposé** en
  2 images (i0 → i2, vers la droite pour un dash à gauche), puis file à gauche
  (-0,7 à i11) (mesuré). Ici, l'animateur pousse sur la jambe opposée avant de
  partir : une anticipation minuscule de 2 images.
- **Pose** :
  - le corps se **penche vers la direction du dash** (penché côté -45° en
    8 images), comme un patineur ou une moto en virage ;
  - les membres **extérieurs** s'écartent en traînée : jambe droite à +36° vers
    l'extérieur, bras droit à +45° ;
  - le bras intérieur est rentré.
- **Temps** :
  - entrée rapide en 8 images (ease-out) ;
  - maintien approximatif i8-i16 ;
  - **retour lent** en 16 images.
  - Aucune tenue stricte (toujours au-dessus de 4 studs/s).
- Tête contre-tournée (+18°) et baissée (-16°) (mesuré).

### 1.11 Hit 1, Hit 2, Hit 3 (0,22-0,27 s) : réactions

Vu : `4_Hit_*_film.png` (toutes les images, 3 vues). Mesuré (valeurs image par
image dans la sortie de la session, reprises ci-dessous).

- **Ce sont des « flinch » additifs courts** : départ au repos exact, retour au
  repos exact. Jambes non posées. Pas de translation (mesuré).
- **Structure commune** : le sommet est atteint en **2 à 4 images**, le retour
  prend 9 à 12 images. L'attaque est très rapide, le retour en ease-out long.
- **Hit 1 : coup reçu sur le côté gauche du visage** :
  - buste tourné vers sa droite (lacet -23° à **i2**), penché en arrière de -6° ;
  - **tête** qui tourne encore plus à droite (+25,5° dans le torse à **i3**) ;
  - bras qui suivent à **i4**.
  - **Cascade d'une image : buste (i2) → tête (i3) → bras (i4).**
  - Regard monde : 46°, le **double** du buste.
  - Rebond : le penché passe à +3,4 (vers l'avant) à i9 avant de se poser.
    L'animateur fait légèrement dépasser en sens inverse (dépassement).
- **Hit 2 : coup reçu du côté droit, qui remonte** :
  - tête tournée à gauche (-16,5) et **menton levé** (+17,9) à **i3** ;
  - buste qui pivote (+34,6) à **i4** ;
  - bras projetés vers l'extérieur et le haut (+33 et +26) à i3.
  - La tête **précède** le buste d'une image.
  - La tête dépasse ensuite en sens inverse (+4,6 à i11).
- **Hit 3 : coup frontal au menton** (mesuré, très lisible) :

  | image | ce qui se passe |
  |---|---|
  | i1-i3 | la **tête** part en arrière (+17 → +36 → +42°) alors que le buste **ne bouge pas encore** : il avance même de +1° |
  | i4-i6 | puis le buste bascule en arrière (-6 → -20 → **-27°** à i6) |
  | i5-i7 | bras gauche au sommet |
  | i11 | bras droit au sommet, **8 images après la tête** |

  - Ici, l'animateur fait partir **la partie frappée d'abord**. La tête est
    touchée : elle part, puis traîne le reste du corps en cascade (tête → buste
    → bras). C'est l'inverse d'un coup donné, où le buste mène (déduit ;
    très clair sur le film, profil i1-i6).
  - Le buste basculé de 27° entraîne les jambes (non posées) : les pieds
    décollent vers l'avant. C'est un artefact R6 accepté (vu).
- **Comment la réaction dit d'où vient le coup** (déduit) :
  - par la **direction de la tête**, la première partie qui bouge : droite,
    gauche + haut, arrière ;
  - puis par la rotation du buste dans le même sens.
  - Le lien avec M1_1 (crochet droit qui balaie de la droite à la gauche de
    l'attaquant, qui pousse la tête de la victime vers sa droite), M1_2 et M1_4
    est plausible. **Le pack ne l'écrit nulle part : c'est une hypothèse.**

### 1.12 Block Idle et Block Hit (70 i/s)

Vu : `block_idle_pose.png`, `5_Block_Hit_film.png`. Mesuré.

- **Calque « bras seulement »** : torse, tête et jambes à poids 0 (mesuré).
- **Garde en X devant le visage** :
  - bras levés à environ 178° de swing, croisés vers l'intérieur de 19 et 24° ;
  - translatés de 1,15-1,21 stud pour passer devant la tête ;
  - poings à 1,0 devant et 1,9 au-dessus du centre du torse, donc à hauteur du
    front.
- **Block Idle quasi figé** (0,14° d'amplitude). C'est une pose tenue, pas un
  cycle vivant (mesuré).
- **Block Hit** :
  - secousse de 3,5° en **1 image** ;
  - maintien 2-3 images ;
  - retour quasi linéaire en 10 images.
  - Très petit (poings à 6,5 studs/s au plus).
- **Vu du dos** (caméra de jeu), la garde est **presque invisible** : on voit
  à peine un bord de bras vert (vu, `block_idle_pose.png`). Ici, la lisibilité
  du blocage en jeu ne peut pas venir de l'animation seule. Elle vient
  probablement d'un effet ou d'un son (déduit, non vérifié dans le pack).

---

## 2. Comparaison pack contre TSB : deux écoles

Mesuré sur TSB M1-M4 (`tsb_M1_planche.png`, vitesses image par image) et vu
sur la planche de TSB M1.

| | Pack battleground | TSB (M1-M3) |
|---|---|---|
| fabrication | **cuit**, une clé par image, courbes lisses (éditeur à courbes) | **clés éparses** (7-8 clés par M1), interpolation Linear |
| durée d'un M1 | 0,65-0,70 s | 0,43-0,47 s |
| armé | vrai contre-mouvement : M1_1 s'enroule à -98° en 10 images | pas de pose d'armé : le buste tourne déjà à vitesse **constante** (M1 : lacet +48 → +6 en 6 images, poings à 12-16 studs/s) |
| lâcher | 5-9 images, vitesse **en cloche** (ou un pop d'une image pour le direct) | **1 image** pour passer de 16 à 71 studs/s, puis **palier** 2-4 images (67-73), puis palier à 36, puis environ 6 |
| tenue | quasi morte (1-4 studs/s, qui s'éteint), 17-28 images | **jamais morte** : 6-7 studs/s (une clé de torse seule à i20 fait dériver le corps) |
| regard (tête) | très stable : 9-28° pour 137-162° de buste | stable mais moins : 18-49° pour 111-118° |
| jambes | non posées | non posées (même convention) |

Validation de la méthode par extrêmes (`extremes.py`) : sur TSB M1, les
extrêmes tombent exactement sur les clés (i6, i8, i10, i14, i20). Sur le pack,
ils forment des grappes : M1_1 vers i4-5, i10, i12-15, i19, i22-23, i28 ;
Hit 3 vers i3, i5-6, i9, i11. Ces grappes sont **probablement** les poses
d'origine de l'animateur du pack (déduit, faible confiance).

**Lecture (déduit)** :
- Le pack est l'école « animation 3D classique » : poses, ease in/out, arcs,
  suivi, puis tenue. C'est lisible et « joli », plus lent et plus rond.
- TSB est l'école « pose à pose linéaire » : des vitesses qui changent par
  marches, un lâcher en une image, un corps qui ne s'arrête jamais tout à fait.
  C'est plus sec, plus court, plus « jeu ».
- Les deux partagent les mêmes décisions de fond : jambes laissées au calque du
  dessous, tête qui vise, buste qui porte le bras, bras qui se retire.
- Ce ne sont pas deux vérités : ce sont deux textures. Milan vise TSB et l'anime.
  La texture TSB (marches de vitesse, pas de tenue morte) est la plus proche.

---

## 3. Grands enseignements (transversaux)

1. **La tête est un gyroscope, et c'est une animation active** (mesuré).
   - Marche : regard 0,0° sur tout le cycle. Course : ±3°. M1 : 9-28° pour
     137-162° de buste.
   - Pour obtenir ça, la tête tourne **beaucoup** dans le torse (61-85° en M1).
   - **Correction pour le cerveau** : `corpus/README.md` §3 lisait « amplitude
     tête pro 84° contre 25-30° chez nous = nos têtes bougent trop peu ». Ces
     84° sont surtout de la **contre-rotation pour ne PAS bouger dans le
     monde**. Le bon critère n'est pas « plus d'amplitude de tête » mais « le
     regard reste sur la cible pendant que le buste tourne ». Exceptions
     voulues : l'uppercut (la tête suit le coup vers le haut) et les réactions
     (la tête bouge **plus** que le buste).
2. **Qui bouge en premier dépend de qui reçoit la force** (mesuré).
   - Coup donné : buste et bras qui se retire d'abord, poing 2-3 images après.
   - Coup reçu : la partie frappée d'abord (tête), puis le buste 1-3 images
     après, puis les bras jusqu'à 8 images après.
   - Ça éclaire l'ancienne contradiction « tête en avance ou en retard » :
     ce n'est pas une règle de style, c'est la **source de la force**.
3. **Chaque clip du combo commence dans la pose de fin du précédent** (mesuré).
   Le combo est animé d'un tenant puis découpé. La tenue finale (17-28 images)
   sert de fenêtre d'enchaînement : avec le fondu Roblox de 0,1 s, on passe au
   clip suivant sans saut (déduit).
4. **Le mouvement est mis là où le script ne peut pas le mettre** (déduit sur
   mesures).
   - Les dashes ne translatent pas vers l'avant : c'est le script. L'animation
     donne **la pose de voyage figée** et **l'arrivée qui claque**.
   - La hauteur, elle, est dans l'animation : salto +1,4, uppercut +0,26,
     downslam -1,4.
   - Pour vendre la vitesse, ici, l'animateur **arrête** le corps (Forward Dash)
     ou le **penche dans la direction** avec les membres extérieurs en traînée
     (Sidedash). Il ne l'agite pas.
5. **Les contacts avec le sol sont exacts quand les jambes sont posées**
   (mesuré).
   - Poings des downslams pile au sol (-0,03 et -0,01).
   - Mains du backdash au sol (-0,24).
   - Pieds maintenus au sol quand le torse descend de 1,4.
   - Quand les jambes ne sont pas posées (M1, uppercut, hits), les pieds
     traversent le sol : c'est la convention de calque, acceptée.
6. **R6 sans genou** (mesuré) : on raccourcit la jambe qui revient par
   **translation** (jusqu'à 1,6 stud en course) et on abaisse le torse (-0,3 à
   -0,4 en course) au lieu de plier. La tête n'est **jamais** translatée.
7. **Cycles** (mesuré).
   - La hauteur rebondit deux fois par cycle, avec un creux 3-5 images après le
     contact et un sommet 3-7 images avant le suivant.
   - Lacet, bras et jambes font une oscillation par cycle, en opposition.
   - La jambe recule lentement et revient vite (asymétrie H2).
   - Les bras balancent surtout **devant** le corps, et en **diagonale** en
     course.
   - L'idle respire en vague décalée (quart de période entre penché, hauteur,
     bras et tête).
8. **Rythme d'une attaque de pack** : armé (4-16 images selon ce que la pose
   d'avant fournit), lâcher 2-10 images, arrivée **sèche** (pop, 2 images) ou
   **amortie** (48-24-7), tenue 13-28 images, relevé 20-23 images (downslams).
   Les réactions : sommet en 2-4 images, retour en 9-12.
9. **Caméra de jeu (dos)** (vu) : plusieurs choses fortes sont invisibles
   de dos. La garde, le bras qui frappe en tenue et l'idle se voient mal. Ce qui
   se lit de dos : la torsion du buste, le bras qui se retire, le balancier en
   diagonale de la course, la jambe tendue du dash. Ici, les poses du pack
   semblent pensées en 3/4 ou de profil, pas pour la caméra de dos (déduit).

---

## 4. Ce qui me surprend ou contredit le cerveau

- **Contredit** : « tête pro 3 fois plus ample, donc nos têtes bougent trop
  peu » (`corpus/README.md` §3). C'est de la contre-rotation (voir §3.1). Si on
  « amplifie la tête » sans cette intention, on fait l'inverse du pro.
- **Nuance** : `CARNET` et `REFERENCES_VIDEO` parlent de la contre-rotation de la
  tête dans le tuto uppercut. Le pack montre que **son uppercut ne le fait pas**
  (regard monde sur 101°). Ce choix dépend du coup, ce n'est pas universel.
- **Surprise** : le Backdash est une rondade suivie d'un salto groupé
  (1,23 s de pure acrobatie), pas un pas en arrière.
- **Surprise** : le Forward Dash passe 16 images **immobile** au milieu. La
  vitesse est vendue par l'absence de mouvement.
- **Surprise** : le Walk du pack suppose environ 7 studs/s, et le Run environ
  22. Avec la WalkSpeed par défaut (16), la marche patinerait.
- **Surprise** : dans le finisher M1_4, le **bras qui se retire** va plus vite
  (103 studs/s) que le poing qui frappe (63).
- **Nuance sur les tenues** : le pack tient ses poses de façon quasi morte,
  alors que TSB ne s'arrête jamais (dérive à 6-7 studs/s). L'idée de « tenue
  vivante » du cerveau est plus proche de TSB que du pack.
- **Surprise** : les dashes latéraux ont une anticipation de 2 images dans le
  sens opposé (0,3 stud), qu'on ne voit pas sans les courbes.

---

## 5. Ce que je saurais refaire maintenant en R6 (concret)

- **Un cycle de course « battleground »** (40 images à 60 i/s) :
  - clés de pose : contact i0, bas i4, passage i10, haut i16, contact opposé
    i20, puis le miroir ;
  - buste penché de 35-43° et abaissé de 0,3-0,4 ;
  - lacet ±22° et côté ±15° en phase ;
  - tête contre-tournée de ±16° et levée de +13° ;
  - bras de -48 à +137° avec un écart en diagonale de ±22° ;
  - jambes de -88 à +67°, retour devant en 15 images, recul en 25 ;
  - jambe qui revient translatée vers le haut ;
  - pied posé sous la ligne médiane (-18°).
- **Une marche de combattant** (60 images) : penché de 13-17°, lacet ±17°
  **exactement annulé par la tête**, bras de -13 à +36°, jambes ±40°, rebond de
  0,15 stud deux fois par cycle.
- **Une réaction à un coup** :
  - pose sommet en 2-3 images, **la partie touchée en premier** ;
  - le buste 1-3 images après, les bras 2-8 images après ;
  - léger dépassement en sens inverse ;
  - retour au repos en environ 10 images.
  - La direction de la tête dit d'où vient le coup.
- **Un combo M1 de 4 clips enchaînés** :
  - animer la séquence d'un tenant, couper aux fins de tenue, chaque clip
    démarrant de la pose de fin du précédent ;
  - buste et bras qui se retire d'abord, poing 2-3 images après ;
  - tête qui vise ;
  - pour la texture TSB : clés éparses, lâcher en 1 image, paliers, tenue qui
    dérive.
- **Un dash** : entrée douce vers une pose de glisse de profil (jambe arrière
  horizontale, bras avant pointé), tenue figée pendant que le script déplace,
  claque de freinage en environ 5 images (buste qui pivote de plus de 100°,
  jambe devant, accroupi).
- **Un dash latéral** : 2 images de contre-poussée, penché de 45° dans la
  direction en 8 images, membres extérieurs écartés, retour en 16 images.
- **Un coup au sol** :
  - version lourde : bras au-dessus de la tête, cambré, abattu en 10 images,
    arrivée amortie, torse -1,4, pieds replantés ;
  - version sèche : lâcher en 2 images par roulis du buste, bras figé dans le
    torse, pose de super-héros tenue 20 images.

## 6. Ce que je ne saurais pas (honnête)

- Les **vraies clés** de l'animateur du pack : le fichier est cuit. Mes « poses
  clés » sont des extrêmes et des tenues (faible confiance sur leur nombre exact).
- Les **tangentes et l'easing** d'origine (outil, courbe) : invisibles une fois
  cuit.
- L'**appariement** coup → réaction (M1_n → Hit n) : plausible, non écrit.
- Les **KeyframeMarker** / événements (moment du dégât, du VFX) : non lus.
- Ce que le joueur voit **vraiment en jeu** avec le calque de jambes du dessous,
  le fondu de 0,1 s, `AdjustSpeed` et la caméra : je n'ai rien lancé dans
  Roblox. Mes vues « dos » sont des caméras fixes de mon rendu.
- Le rendu reste des blocs : je ne juge pas le rendu final ni le style de
  personnage.
- Pourquoi l'Uppercut et le Block sont cuits à 70 i/s : inconnu (autre outil ou
  autre export ?).
- Couverture : les 19 animations ont été regardées. Sur les planches, l'Idle
  et le Block Idle sont presque statiques : je les ai surtout lus par les
  courbes. Le Walk et M1_3 ont été regardés en planche 20-30 i/s, sans planche
  de poses en grand.

## Vérification adverse

Vérificateur indépendant, 2026-09-26. Méthode : j'ai recalculé moi-même les
mondes depuis le .rbxm, avec `corpus.load_rbxm_sequences` et `resample_linear`
à 60 i/s, et `geo_pose.descripteurs`. Mon script est
`frames/verif_A4_pack_battleground/v.py`. J'ai relancé `planche_cles.py` sur
Forward Dash, M1_2, Uppercut, Hit 3, Downslam V1 et V2 (PNG dans le même
dossier) et j'ai regardé Forward_Dash.png, fdash_poses.png et Downslam_V2.png.
Les easings ont été lus avec `parse_enum_and_vector2`. Je n'ai rien modifié
dans le dépôt.

Conclusion générale : pas d'hallucination de fond. Les poses, les
enchaînements et les directions sont justes. En revanche, plusieurs chiffres
de la prose sont **arrondis vers le haut**, ou viennent d'une **projection
sagittale** qui n'est pas l'angle réel. Le JSON du lecteur lui-même le
contredit.

### Les 8 vérifications

1. **Tête gyroscope** : **confirmé**.
   - Chiffres reproduits à 0,1° près. Amplitude du lacet du buste / de la tête
     dans le monde :
     - Walk : 33,4 / 0,0 ;
     - Run : 43,4 / 6,1 ;
     - M1_1 : 156,5 / 21,4 ;
     - M1_2 : 137,1 / 9,3 ;
     - M1_4 : 161,6 / 22,9 ;
     - Uppercut : 127,2 / 101,1 ;
     - Hit 1 : 23,2 / 45,9.
   - La lecture de README §3 (« 84° de tête pro ») est bien de la
     contre-rotation.
   - Correction pour l'Uppercut : la tête ne va **pas vers le haut**. Son
     élévation monte au plus à +7°. Elle suit le **lacet** du buste (la tête
     dans le torse ne bouge que de 33 à 46°).
   - Exception partielle : M1_3 (buste 55°, tête dans le monde 28° : la moitié
     seulement est annulée).
2. **Combo = une chorégraphie en 4 clips** : **confirmé**.
   - Écarts fin → début (pièces / bouts) : M1_1→M1_2 0,041 / 0,057 ;
     M1_2→M1_3 0,000 ; M1_3→M1_4 0,288 / 0,301.
   - M1_1 part du repos (lacet 0).
   - Armés : M1_1 10 images, M1_2 4, M1_4 6. M1_3 prend 9 images (lacet de -66
     à -121 à i9) : ce n'est pas « environ 6 ».
3. **M1_2 : pop d'une image 45 → 127 → 9** : **nuancé**.
   - Les vitesses sont exactes (poing gauche 44, 126,6 et 8 à i10-12).
   - Mécanisme non vu : le pop est un **saut de translation** de la Pose Left
     Arm, de (0,81, -0,64, -0,53) à (-0,54, -0,20, 0,71), soit 1,9 stud en une
     image. Le bras ne tourne que de 34°. Le poing passe de 1,32 à 3,42 devant.
     L'animateur « détache » le bras vers l'avant.
4. **Forward Dash** : **nuancé**.
   - Confirmé : les trois temps, l'entrée à 17 studs/s au plus, les vitesses
     de 110 à 113 à i42-43, le pic de 2 361°/s à i42, et l'absence d'avancée
     du torse (entre -0,19 et +0,05).
   - Corrections :
     - lacet final **+51°**, pas +57 (le JSON du lecteur donne bien 51,1) ;
     - la tenue i25-40 est une **tenue qui dérive** : lacet de -57 à -65°,
       torse de -0,38 à -0,49 ;
     - **oubli** : la pose finale tient le **bras droit tendu droit devant à
       l'horizontale** (az 0, el 0, poing 3,2 devant) de i46 à i58. Le dash
       finit sur un direct, pas seulement sur un freinage.
5. **Downslam V1/V2** : **nuancé**.
   - Confirmé : poings au plus bas à -0,03 et -0,01, pieds à -0,10 et -0,08,
     lâcher de V2 en 2 images (96, 155, puis 7 : arrêt net), et pose de
     super-héros tenue de i17 à environ i42 (vu).
   - Corrections :
     - torse **-1,26** (V1) et **-1,31** (V2), pas -1,4 (le JSON du lecteur
       donne 1,74 et 1,69) ;
     - pic de V2 **154,7 studs/s**, pas 162 (162 semble venir du lacet de
       M1_4) ; il reste le maximum du pack ;
     - dans la tenue de V2, le bras gauche est replié à plat sur le dos.
6. **Uppercut** : **nuancé**.
   - Confirmé à 60 i/s : -0,71 à i15, +0,26 à i25, lacet -69° à i13, penché
     +25°, côté -34°, poing à 94 studs/s à i19.
   - Le clip est cuit à 70 i/s : en indices natifs, c'est i18, i29 et i22.
   - « Bras à 164° » est une projection sagittale. L'angle réel depuis le bras
     pendu est de **146° au plus** (i25). Le bras monte **en travers vers la
     gauche** (az -96° dans le repère du coup ; poing à 1,5 devant, 0,9 à
     gauche, 3,0 au-dessus du centre du torse).
7. **Cycles et vitesse imposée** : **nuancé**.
   - Walk confirmé : le pied au sol recule à 7,05 studs/s, de façon constante.
   - Run : le pied D est au sol de i3 à i8 (6 images, confirmé), mais il
     **accélère** pendant l'appui : 15 → 27 studs/s (pas de 0,25 à 0,45 par
     image). Aucune vitesse constante ne supprime le patinage.
   - La « pose de contact i0 » est en l'air (pied à 0,26). Le vrai contact
     arrive à i3, en même temps que le bas du rebond. Le bas i3 et le haut
     i16-17 sont confirmés.
8. **Deux écoles, pack contre TSB** : **nuancé**.
   - Confirmé :
     - clés M1 de TSB : 0, 6, 8, 10, 14, 20, 25, 26 ;
     - EasingStyle 0 (Linear) sur toutes les Poses de M1 à M4 ;
     - vitesses du poing gauche de M1 : 15 (constante), 66 en 1 image, 69-72,
       puis 36, puis 6-7 ;
     - durées : 0,433, 0,467 et 0,445 s.
   - Corrections :
     - « 7 à 8 clés » ne vaut que pour M1 à M3. **M4 a 22 clés, dure 0,69 s et
       pose les jambes** : « jambes au calque » ne vaut donc pas pour TSB M4 ;
     - la dérive de 6-7 studs/s est celle du **poing gauche**, qui interpole
       entre ses propres clés i14 et i26. Le torse ne bouge qu'à 0-1 studs/s :
       sa clé isolée en i20 n'en est pas la cause.

### Vérifié en passant (non retenu dans les 8)

- **Sidedash** : confirmé.
  - Test miroir : écart de 0,0001.
  - Contre-poussée de +0,28 à i2, puis -0,64 à i11-13.
  - Penché de côté de -38° à i8 et de -42° au plus.
- **Hits** : durées (0,217 à 0,267 s) et courbes de Hit 1 exactes.
  - Dépassements confirmés : +3,4 à i9 (Hit 1) et +4,6 à i11 (Hit 2).
  - Mais dans Hit 1, le **buste culmine avant la tête** (i2 contre i3). La
    règle « la tête part d'abord » ne vaut que pour Hit 2 et Hit 3.
  - « RA à i11 » dans Hit 3 est un extrême de balancement dans le torse (bras
    qui traîne). Les pics de vitesse des deux bras tombent ensemble à i5.
- **Garde** : poings à 1,0 devant et 1,9 au-dessus, confirmés. Bras en X
  confirmés (az -83 et +95). Mais l'angle réel des bras est de **156 à 161°**
  depuis le bras pendu, pas 178° (même biais de projection).

### Oublis importants

- **Bras translatés dans toutes les attaques.** Les Poses des bras ont une
  translation de 1,2 à 1,7 stud dans M1_1 à M1_4 et dans l'Uppercut (torse
  jusqu'à 0,78). Le lecteur ne l'a noté que pour les jambes de la course et
  pour la garde. C'est un procédé central du pack : allonger le bras
  au-delà du rig.
- **M1_1 : le bras gauche part devant d'abord.** Le poing gauche est tendu à
  3,0 studs devant pendant l'armé (i9-12), avant le crochet droit : un bras
  qui vise ou qui tire. Le lecteur ne décrit que le crochet.
- **Forward Dash** : la pose finale est un bras droit tendu droit devant (voir
  le point 4).
- **M1_2 à M1_4 : regard baissé en permanence.** La tête dans le monde regarde
  18 à 31° vers le bas : menton rentré, en plus de la stabilisation en lacet.
- **Biais systématique des chiffres de prose.** Plusieurs valeurs sont
  arrondies vers le haut (1,4 / 162 / 57 / 164 / 178) alors que le JSON donne
  moins. Il faut reprendre les chiffres du JSON, pas de la prose, avant de les
  verser au cerveau.
