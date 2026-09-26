# B4 — Le langage de l'animation anime, et ce qu'il devient sur un R6

Chantier 4, identifiant `B4_techniques_anime`. Travail d'apprenti : j'ai regardé, mesuré et lu mes sources sans chercher à confirmer une idée ni à réparer le poing chargé.

**Statuts utilisés :**
- **vu** : je l'ai regardé moi-même (Read sur les images).
- **mesuré** : c'est un chiffre sorti d'un outil (écart entre images, corrélation de phase, espacement des clés).
- **lu** : c'est un texte (incrustation, script affiché, sous-titres).
- **déduit** : c'est mon interprétation.

Ce sont des apprentissages (« ici, l'animateur fait X parce que Y »). Aucun n'est une règle.

Les brouillons bruts et toutes les planches sont dans
`/tmp/claude-0/-home-user-Jeux/4796ac9e-8e41-51f7-91c4-7b92a6a187d0/scratchpad/c4/frames/B4_techniques_anime/`. On y trouve `brouillon.md` (les observations horodatées de toute la vidéo), `ysh/` (Yuta), `dsh/` (planches à 12 i/s dédoublonnées), `nat/` (extraits à la cadence native avec la durée de chaque image), `full/` (images en pleine résolution) et `r6_*.png/json/txt` (planches de clés TSB).

---

## 0. Méthode, et pourquoi les chiffres de durée tiennent

- **Vidéo du tuto :** 29,97 i/s, 780 s, muette (ffprobe ne trouve aucun flux audio). Tout le texte vient des incrustations.
- **Anime sources :** ≈ 24 i/s.
- **Lecture d'une cadence à travers le 30 i/s.** Quand on regarde une source à 24 i/s dans une vidéo à 30 i/s, chaque cadence laisse une signature :
  - un plan animé **sur 1** donne des tenues **1-1-1-2** (33/33/33/67 ms) ;
  - **sur 2** donne **2-3** (67/100 ms) ;
  - **sur 3** donne **3/4**.
- **Validation (mesuré) :** j'ai testé la méthode sur l'exemple de David Nethery, où l'incrustation donne la réponse (« ON ONES / ON TWOS / ON THREES »). L'outil `nat/nethery.txt` retrouve 1-1-1-2, puis 2-3, puis 4-4-3. La méthode donne la bonne réponse sur un cas connu.
- **Limite honnête :** quand la caméra ou le fond bougent sur 1 alors que le perso est sur 2, l'outil voit « sur 1 ». Je le signale à chaque fois (cas Sakura et Furuhashi).
- **Yuta :** C09ZMD9_D9I est déjà à 24 i/s (554 images). Là, j'ai séparé le mouvement de caméra du mouvement de dessin par **corrélation de phase** : un décalage global, puis un résidu après recalage.
- **Planches de genga numérotées (images 0212…, 0400…, 0554…) :** j'ai mesuré l'écart moyen entre cellules consécutives. Un écart d'environ 0,2 à 5 veut dire que c'est le même dessin (tenue). Un écart de 12 ou plus veut dire que c'est un nouveau dessin.

---

## 1. Source par source

### 1.1 « Every (Anime) Animation Technique Explained in 12 Minutes » (iMV9Tlpo1wY, Arikendo)

**Couverture :**
- Les 780 s entières à 1 i/s, lues à la session précédente (`brouillon.md`, lignes 1-96).
- Puis 12 i/s dédoublonné sur les sections de combat (planches `dsh/`).
- Puis la cadence native sur 14 moments clés (`nat/`).
- Le script de l'auteur lu en pleine résolution (`full/script_*.png`).

**Impact frames (16-57 s)**
- **Nakamura, poing au visage, mesuré au pas 30 i/s** (`nat/nakamura_punch_00-02`, vu + mesuré) :
  - 33,30-33,40 s : visage neutre.
  - 33,43-33,66 s (≈ 0,23 s) : un **arc de lumière jaune** entre par la gauche et le visage se coupe en deux (moitié éclairée, moitié sombre).
  - 33,67 s : le poing est **déjà au contact de la joue**. Aucune image ne montre son trajet.
  - 33,67-34,57 s (≈ 0,9 s) : **contact tenu**. Poing et visage ne bougent presque pas, mais des arcs électriques bleus rampent autour du poing à chaque image (signature 1-1-1-2, donc sur 1).
  - 34,60-35,17 s (≈ 0,6 s) : impact frames noir et blanc, sur 2 (tenues de 67-100 ms), où le visage est réduit à des taches.
  - 35,20-35,97 s (≈ 0,8 s) : impact en couleur (fond orange, poing devenu une boule de lumière qui écrase la joue).
  - Total ≈ 2,5 s pour un seul coup, dont environ 0 s de trajet.
  - *Déduit :* ici, l'anticipation passe par la **lumière** et non par le bras. Le spectateur « sent » le coup arriver par le changement d'éclairage, puis découvre le résultat. Le coup n'est pas un mouvement, c'est un **état** (avant, puis après) prolongé.
- **Deku (film MHA), 24,0-25,1 s** (vu) :
  - le poing flou et énorme au 1er plan ;
  - 24,50 s : **une seule image blanche** (33 ms) ;
  - puis la caméra pousse sur le visage ;
  - une image hachurée tenue 167 ms.
- **Deku OFA, 49,9-52,2 s** (vu) :
  - le mouvement de base est une **marche lente** ;
  - toutes les 0,3-0,5 s arrive une ponctuation : un faisceau coloré (1 image), puis un éclat plein écran sur noir (1 image, 33 ms), puis le fantôme d'un prédécesseur superposé (67-100 ms), puis on revient à la marche ;
  - une couleur différente à chaque ponctuation (bleu, rouge, vert, orange, violet, rose, jaune).
  - *Déduit :* l'intensité vient d'images isolées posées sur un mouvement simple, pas d'un mouvement plus violent.
- **Formes pures** (vu) :
  - 26,25 s : 2 yeux jaunes et un trait sur fond noir, tenus ≈ 0,67 s. Une impact frame peut être longue.
  - Chansard (36-37,8 s) : la palette change **à chaque image**.
  - 42,25 s : le même dessin décliné en trois versions (trait genga, aplat noir sur jaune, aplat noir sur rouge). C'est donc un dessin refait, pas un filtre.
- **Script de l'auteur, lu à 167,3 s :**
  > « Impact frames occurs when impact happens like a punch, explosion you name it to fully [stylize] it more. Its a more stylize drawing usually flashing for a couple of [seco]nds but sometimes animators likes to draw a crazy number of impact frames. […] animators either draw them black and white or colored ones. Althought yutaka nakamura usually use them different compare to what they were mean for. He places the impact […] more so to make scenes i guess flash[i]er »

**Kutsuna lighting (57-84 s)** (vu, `dsh/b_kutsuna_00,05`)
- Les éclairs sont des **formes épaisses** redessinées en entier à chaque image (sur 1). Ils dessinent un **contour autour de la main** (FMA, 59,5-60,8 s) et **recolorent tout le plan** (rouge, puis blanc pendant 2 images).
- Hiromitsu Seki (76,4-77,8 s) : l'éclair bleu part fin, s'épaissit, puis **éclaire le visage du côté de l'éclair** jusqu'au blanc presque total.
- Script, lu : « Kutsuna Lighting is a basically a technique of drawing lighting that moves very zig [zag] … created by kenichi kutsuna ».
- *Déduit :* dans l'anime, la lumière est un acteur. Elle bouge sur 1, elle a une forme dessinée et elle change la couleur du monde.

**Smears (84-113 s)** (vu, `dsh/c_smear_00-05`, `full/smears5.png`, `full/t110.9.png`)
- **Fille au gourdin (84,7-85,7 s) :**
  - une pose d'armé nette ;
  - puis 1 à 2 images où le bâton devient une **forme longue frangée** qui traverse tout le cadre ;
  - puis le contact et les éclats, et on revient à une pose nette.
  - Le smear n'existe qu'entre deux poses nettes.
- **Boxe (88,2-90,7 s) :**
  - le corps entier devient un flou horizontal pendant 2 images (smear « photographique ») ;
  - dans l'échange, le bras qui frappe n'existe que comme une traînée couleur peau pendant 1 image, puis il est déjà au bout.
- **« Bad Animation » (98,3 s)**, texte incrusté, lu : membres frangés de poils blancs, sans direction.
  - *Déduit :* l'auteur rejette ce smear parce qu'il ne raconte pas la trajectoire.
- **Smear devenu effet :**
  - la trace d'un passage devient une lame violet-noir qui traverse la cabine (106,9 s), et le perso est remplacé par sa trace pendant 1 image ;
  - smear circulaire (95,2 s) : un œil au centre d'une étoile blanche.
- **Doodley (vu en pleine résolution, 110,9 s), lu :**
  - « not actual terminology, just how I would categorize them » ;
  - ARC multiples (copies du bras le long de l'arc, fondues dans une traînée) ;
  - PATH multiples (copies du corps le long de la trajectoire) ;
  - SPEED multiples (plusieurs bras qui tremblent sur place, pour la vitesse sans trajectoire).
- **Script, lu (partiel, le texte déborde du cadre) :** « […stretc]hing the drawing. It can be use to make th[…] [not reall]y like smooth but more like to insinuate […] [co]nvey speed […] [ver]y spiky like yutaka nakamura or very wobb[ly] ».
- **Black Rock Shooter (171,3-172,4 s) :** smear « spiky » vu, avec des arcs blancs pointus en X au bout du sabre.

**Cubic debris (113-148 s)** (vu, `dsh/d_debris_00-08`)
- **Les débris sont des polyèdres plats à 2 tons** (clair et ombre, parfois 3).
- **Ils sont en 3 couches de taille :**
  - des gros blocs **noirs en silhouette** au 1er plan (124,6-127,8 s) ;
  - des moyens bruns ;
  - des petits lumineux au fond.
- Ils **continuent de dériver** pendant que le perso est tenu.
- **Naruto (122,25-122,33 s) :** le trajet du coup de Sakura tient en **2 images floues**, puis le mur se fissure en carreaux.
- **Naruto contre le géant rouge (131-132,3 s) :** **contact tenu ≈ 1,2 s**. Seuls les éclats de pierre bougent : c'est un duel de pression.
- **117,9 s :** un **noir tenu ≈ 0,8 s** entre deux plans.

**Yutapon cubes (148-207 s)** (vu, `dsh/e_yutapon_*`, script lu)
- **Script, lu :**
  > « Yutapon Cubes and cubic debris arent the same thing. […] in a technical sense yutapon cubes are more timing dependent. Theres a big emphasize on the hold and release where for cubic debris its just debri flying everywhere. […] He drew debris like this because he believe that it was easier to draw because cubes are easy to [draw] with different perspectives and he was inspired by other animators […] satoru utsunomiya […] very popular among webgen animators »
- **Mesuré (`nat/yutapon_hold`, 157,0-159,6 s) :** la « tenue » (la glace qui craque sous le perso de dos) **et** l'explosion de cubes qui suit sont toutes deux au motif 1-1-1-2, donc sur 1. *Déduit :* la tenue n'est pas une image figée, c'est un mouvement minuscule animé sur 1, puis un lâcher de pleine amplitude.
- **« For animators » (174,3-176,8 s, vu) :** une grille de cubes dessinés au trait dans toutes les orientations, qui tournent image par image (sur 2). C'est la feuille d'étude de l'animateur : il s'entraîne à dessiner un cube tournant avant de s'en servir comme débris.
- **Mesuré (`nat/sukuna_flame`, JJK S2, 201,5-204,1 s) :** la flamme est **sur 2** (tenues 2 et 3 à 30 i/s).

**Rotoscopie et mannequin 3D (207-278 s)** (vu en pleine résolution, `full/mannequin.png`)
- Des pages « Animation Material » d'ufotable montrent un **mannequin 3D bleu à blocs rigides** : tête, torse, bassin, segments de membres. C'est presque un R6 articulé.
- Il est posé dans le **décor 3D final avec la vraie caméra**, lance rouge en main. Les compteurs sont lisibles : 0:01:15, 0:02:04, 0:02:13, 0:05:12, 0:05:18.
- En 0:05:12, la jambe du mannequin est énorme au 1er plan. L'image finale (258,3 s) reprend **exactement ce cadrage**, mais avec un perso dessiné : armure au trait, cheveux au vent, étincelles au sol.
- *Déduit :* chez ce studio, la pose, la caméra, la perspective et le timing se décident sur un mannequin rigide. Le dessin ajoute ce que le mannequin ne peut pas faire (tissu, cheveux, déformation, effets). **Le mannequin rigide est une vraie étape pro, celle du blocking.**
- **Studio d'arts martiaux (212,4-214,4 s)**, sous-titres lus : « The actions scenes... done by action- », « When he did a series called Garo... ». Et à 260-261 s : « but that versus filming martial arts experts... the reality that brings ».
- **Mesuré (`nat/garo_roto`, `nat/cage2`) :** les combats rotoscopés sont presque entièrement sur 1 (51 tenues de 1 contre 17 de 2 ; 76 contre 18). *Déduit :* le rotoscope donne la continuité du réel, mais peu de tenues. L'auteur dit, lu : « This is not bad i just dont like how they use it here ».

**Kanada style (278-350 s)** (vu, `dsh/g_kanada_00,01,03`)
- **Fire Force (278,8-280,8 s) :**
  - les flammes sont des ailes anguleuses en aplats, qui changent de forme à chaque image ;
  - atterrissage « grenouille » : accroupi, genoux écartés, bras en V, pose tenue ≈ 0,4 s pendant que les flammes dansent.
- **Vieil homme projeté (282,6-283,4 s) :** des silhouettes en étoile, **chaque image une pose très différente**, lisibles même minuscules sur le ciel.
- **Générique Kanada (292-294 s) :** pas d'intervalles doux, on saute de pose en pose. Les explosions sont des étoiles orange anguleuses.

**Background animation et Itano (350-437 s)** (vu, `dsh/h_bg_itano_03,13`)
- Le décor défile en perspective sous la caméra.
- Des **images orange pleines, d'une seule image**, sont intercalées (366,8 et 367,0 s).
- Comparaison « Illustrated Background » / « 3D Background » (lu).
- Itano : des chaînes et des traînées en courbes, la caméra qui tourne, tout sur 1.

**Character acting (437-484 s)**
- **Toji contre Megumi (JJK S2, 447,4-450,4 s, vu + mesuré `nat/megumi`) :**
  - plan large sur 1 ;
  - 3 images de fouetté de caméra presque noires ;
  - **insert en gros plan des mains**, sur 2-3 (tenues de 67-100 ms) ;
  - échange en plan moyen, sur 1 ;
  - gros plan du visage ;
  - **poing déjà dans la joue, contact tenu ≈ 0,3 s** avec micro-variations (la joue se déforme, les yeux se révulsent) ;
  - plan de dos : Megumi est projeté.
- *Déduit :* même un combat « réaliste » alterne les échelles de plan et les cadences. Le coup au visage ne montre pas le trajet.

**Kagenashi, Ebata, Umakoshi (484-602 s)** (vu, `dsh/j_kagenashi_00`, `k_ebata_uma_06,10,12`)
- **« No Shadows » / « Shadows »** côte à côte (lu, vu) : les aplats sans ombres restent lisibles en mouvement.
- **Ebata (563,9-567,7 s) :** une main qui se tend vers la caméra et grossit (raccourci) ; trois filles qui sautent, tenues de 2 (sur 2).
- **Spike, Cowboy Bebop (580,8-583,2 s) :** grands arcs de manche de balai, poses clés en diagonale forte.
- **Umakoshi eye (590-592,2 s) :** la caméra pousse sur l'œil. Pupille minuscule dans un grand blanc, puis l'œil **devient un éclat blanc** qui efface tout.

**Timing (602-716 s)** (vu `full/timing_txt.png`, `dsh/l_timing_01,02` ; mesuré `nat/*`)
- **Nethery, lu :** « It is all the same frame rate, 24 FPS but the number of drawings per second makes a big difference in the look of the animation ».
- **Furuhashi, lu :** « this is animated in 4's ». *Mesuré :* la caméra glisse sur 1 pendant que les dessins sont tenus 67-167 ms. Je ne peux donc **pas** confirmer « sur 4 » à l'outil. Ce que je vois : des poses très différentes (bras levé, torsion, pouce) avec peu d'intervalles.
- **643,5 s (vu) :** capture de l'écran de montage de l'auteur (Vegas, timecode 00:10:08.29) avec un « YES ». L'auteur vérifie image par image.
- **678,5-680,5 s (vu) :** un dessin clé avec, dans la marge, une **échelle d'espacement** (un trait et des barres inégalement espacées) entourée en rouge. C'est la note que l'animateur clé laisse à l'intervalliste. Je ne lis pas les chiffres (flou).
- **Pipeline (668-677 s, lu) :** Storyboard, Layout, Key Animation, In-betweens, Compositing.
- **One Piece, Akihito Ota (mesuré `nat/ota`, 624,8-629,6 s) :**
  - la course de Luffy et le gros plan de l'œil sont **sur 1** ;
  - la révélation de Kaido est **sur 2** ;
  - et 4 cadrages s'enchaînent en ≈ 0,5 s : Kaido minuscule dans un cratère, en pied, en buste, puis visage plein cadre.
- **Bleach, 607,3-609,4 s (vu) :**
  - gros plan tenu d'Ichigo, puis gros plan extrême de l'œil ;
  - coupe sur une lame noire ;
  - anneau bleu sur fond noir (1 image), puis flash blanc inversé (2 images) ;
  - puis plan large de débris, tenu ≈ 0,7 s.
- **609,8-611,2 s (vu) :** le **storyboard/layout gris** est montré avant le plan final (611,3 s et suite). Un coup de pied **en raccourci extrême** : le pied devient énorme vers la caméra (612,4-612,75 s).

**Obari punch (716-756 s)** (vu `dsh/m_obari_00,02-06`, mesuré `nat/sakura_obari, iczer, allmight`)
- **Sakura (Naruto) :**
  - bras en croix sur un fond radial violet, **tenue ≈ 0,5 s** (716,75-717,25 s) où seul le fond pulse ;
  - la tête tourne ;
  - le poing arrière passe au 1er plan ;
  - cri en gros plan ;
  - le poing vers la caméra occupe la moitié de l'écran (718,33-718,5 s) ;
  - 2 images radiales grises ;
  - plan large avec l'onde et les rochers, puis une éclaboussure d'encre en diagonale fait la transition.
  - Trajet du poing ≈ 0,3 s sur ≈ 2,5 s au total.
- **Iczer-1 (728-731,7 s) :**
  - le **poing (gant rouge hachuré) est plus gros que la tête** ;
  - pose armée **tenue ≈ 1,6 s** (729,17-730,75 s), mesurée sur 1 (motif 1-1-1-2), où seuls les lignes et les éclairs bougent ;
  - puis le poing arrive plein écran (731,58-731,67 s).
- **All Might (739,0-740,25 s, mesuré) :** ≈ 0,85 s de « charge » (gros plan du cri, arcs de vent qui tournent, sur 1), puis 2 images pour le coup, dont un poing plein écran flou.

**Outro (755-779 s) :** un montage de gags, sans enseignement technique (vu à 1 i/s).

### 1.2 « Speed/Scale Contrast (Sakuga Study: Yuta) » (C09ZMD9_D9I, 23 s)

Les 554 images ont été regardées sur 24 planches d'une seconde (`ysh/y_00-23`), avec les clés en plein format (`ysh/k1-k5`). Vidéo muette.

- **Échelle par profondeur (vu, #50-#84) :**
  - une jambe entre par le haut et le **pied atterrit énorme au 1er plan** (#53-#57) ;
  - puis le perso s'éloigne : moyen en #61, petit en #63, **minuscule sur la rambarde** en #72-#84.
  - Il passe de plein cadre à environ 1/15 de l'écran en ≈ 0,5 s.
- **Le colosse (#85-#110) :** un impact graphique au loin, puis une **tenue de 19 images (0,8 s)** où l'on découvre la masse du colosse. Le perso minuscule monte vers lui.
- **La frappe (#154-#195, 6,4-8,1 s) :**
  - le perso vole vers la caméra et le **poing grossit** jusqu'à cacher le visage (#181) ;
  - puis le poing de profil **reste fixe au même endroit de l'écran** (#187-#193) pendant que des lignes de vitesse horizontales défilent : la caméra accompagne le poing.
- **Mesuré (corrélation de phase) :** de #160 à #195, il y a un **nouveau dessin toutes les 3 images** (#163, 166, 169, … 193, sur 3). **Entre** les dessins, toute l'image se décale de 1-2 px à chaque image. Le résidu tombe d'environ 14 à environ 4 après recalage, donc c'est un **tremblement de caméra sur 1** sur un dessin tenu.
- **Impact (#196-#217, ≈ 0,9 s) :**
  - une dizaine de dessins abstraits : poing en silhouette inversée, faisceau blanc horizontal qui s'affine, fente, onde en arc, éclat ;
  - le noir et le blanc **s'alternent à chaque dessin** ;
  - cadence sur 2, puis 1-2, puis 2-3.
- **Conséquence :**
  - plan large, le perso minuscule collé contre une énorme courbe (la joue du colosse), avec des arcs d'onde (#219-#228) ;
  - 1 dessin noir tenu 5 images ;
  - des débris flottants, **tenus 18 images (0,75 s)**.
- **Chute et coup de pied (#314-#355) :**
  - le perso tombe tête en bas, sur 3 ;
  - ses **semelles face caméra** (#344) ;
  - puis **noir avec 4 points blancs** (les semelles réduites à des points, #347) ;
  - puis le négatif (#349), puis un éclat radial ;
  - puis une **tenue de 33 images (1,4 s)** où presque rien ne bouge.
- **Fin :** Yuta accroupi, essoufflé, tenu 1 s ; puis un fondu au noir en 8 images, sur 1.
- *Déduit :*
  1. le contraste d'échelle est fabriqué par la **caméra** : perso minuscule en plan large contre pied ou poing plein cadre ;
  2. le rythme alterne des rafales (1-2 images par dessin, noir/blanc) et de **longues tenues (0,75-1,4 s)** ;
  3. le contact « réaliste » n'est jamais montré : il est remplacé par des formes pures ;
  4. **le dessin et la caméra n'ont pas la même cadence**.

### 1.3 Planches de genga (anime3d, 12 images, toutes lues)

- **01, Nakamura, impact frames MHA :** 5 feuilles de papier au crayon.
  - La silhouette blanche est **réservée** dans des hachures radiales, avec une croix de lumière.
  - Deux feuilles n'ont plus de perso du tout.
  - Donc c'est **dessiné à la main**, avec une composition différente par feuille (vu).
- **02, genga Bones (Deku), « A 22 » :**
  - la **main tendue fait environ la taille de la tête** (raccourci) ;
  - les crayons de couleur sont des indications (jaune/orange/bleu = zones d'effet et de lumière) ;
  - annotation ハイコン : je lis les kana ; le sens « haut contraste » est **déduit**.
  - Vu.
- **03, genga MHA, main tendue vers la caméra :**
  - légende « エフェクト濃度 » (densité d'effet), jaune 強 / orange 中 / violet 弱 : **l'animateur code l'intensité de l'aura en 3 niveaux** (lu) ;
  - la case « Time( + ) » sert à noter la durée en secondes + images (lu).
- **04, genga JJK Itadori A, « A 8 » :**
  - une **petite échelle d'espacement** en haut à gauche (barres qui se resserrent) ;
  - poing armé haut près de la tempe, visage grimaçant plein cadre ;
  - couleurs de ligne : bleu = ombre, orange = rougeur/sang.
  - Vu.
- **05, genga JJK Itadori B :** le **bras entier est un aplat beige en forme d'éclair étiré** (un smear-forme opaque, pas une traînée transparente). Vu.
- **06, JJK ép. 19 :** contact croisé, le poing de Todo dans la joue d'Itadori. Vu.
- **07-08, One Punch Man 1 :** poing écrasé plein cadre, éclairé en chaud ; contre-plongée où le poing est plus grand que le buste. Vu.
- **09, MHA S2E10 :** le bras de Deku s'étend, la main brille. Vu.
- **10, planche 24 i/s Todoroki (0212-0243), mesuré :**
  - 0212-0221 : chaque image change (sur 1) ;
  - **0222-0236 : 15 impact frames toutes différentes** ;
  - 0237 : croix noir et blanc ;
  - **0238 BLANC, 0239 NOIR** ;
  - 0240-0243 : l'explosion en couleur.
  - ≈ 0,75 s d'impact entre le dernier plan « normal » et la couleur.
- **11, planche 24 i/s Deku (0554-0603), mesuré :**
  - 0562-0576 : 15 impact frames sur 1 ;
  - puis **0577-0600 : l'extension du bras est SUR 2 EXACTEMENT** (écarts alternés ≈ 3 / 30-65) pendant 24 images, soit **1 s**. La main grossit jusqu'au blanc.
  - La partie lente, c'est la tenue héroïque, pas le coup.
- **12, planche 24 i/s JJK ép. 19 (0400-0431), mesuré :**
  - 0400-0416 : **anticipation sur 3** (tenues 0401-03, 0404-06, 0409-11, 0412-14, écarts ≈ 0,2-5) ;
  - **0417-0419 : sur 1** (l'accélération) ;
  - **0420-0431 : contact sur 2**, soit 0,5 s de contact tenu vivant.

### 1.4 Sous-titres « Making Abilities from Different Anime in Roblox Studio » (Q0mXhHCW2OM)

Lu en entier ; dédoublonné pour la lecture. **Je n'ai pas la vidéo**, donc rien de vu.

- **Fireball :** « I created two fireballs inside a mesh, which I am animating with the mesh animator plugin. I could have done this using scripts ». Il parle d'une explosion inspirée du système de particules de Unity.
- **Hado 90 (Bleach) :** « create a template in advance and use scripts to save their original position, move them down and bring them back to the initial position with a tween […] split the model into layers and use tweening on the first one, then the second one ». Le cercueil se construit donc **par couches décalées**. C'est une forme de décalage (overlap), réalisée par script et non à la main.
- **Aveu :** « There are a few things I could have done differently […] such as adding more animation to the upper body or the swords ». *Déduit :* chez ce créateur, l'animation du perso passe **après** les effets.
- **Katakuri (One Piece) :**
  - il modélise le bras de mochi dans Blender ;
  - « use a Blender feature called damp tracks […] constraints that cause the axis of an object to always point smoothly towards the target. I saw a video of someone animating a cat's tail with damp tracks » ;
  - puis un bug d'import : « in the import settings, you have to go to file geometry and I had it set to stud […] set it to centimeters and that fixed the bug ».
- **Autres outils :** « I used the lightning module for the lightning bolts ». Pour les rochers : « made almost the same way as my [Hado] 90 layers ».

### 1.5 Sous-titres « TSB MORE SCRAPPED/CUT CONTENT » (hRzXUe6okOU)

- Lu en entier. **Ce ne sont que les paroles d'une chanson** (« Overtime, most things fade away… »). Il n'y a **aucun contenu technique**.
- La vidéo elle-même n'est pas dans mes sources.
- Je n'en tire rien sur la manière de faire de TSB. Je le dis plutôt que d'inventer.

### 1.6 Complément R6 : comment les pros posent les clés (TSB)

Mesuré avec `planche_cles.py`. Fichiers `r6_M4.png/json/txt`, `r6_Ultimate2.*`, `r6_Collateral Ruin.*`.

- **M4 (coup de pied, 0,69 s, jambes posées) :**
  - marqueur `hitreg` à l'image 13 (60 i/s) ;
  - **écarts entre clés avant le coup : +5, +4, +3, +1** (≈ 83, 67, 50, 17 ms). Les clés **se resserrent en approchant du contact**.
  - après le coup, clés tous les 1 à 3 intervalles, **posées membre par membre en alternance** (BG en 18, T/H/jambes en 19, BD en 20, BG en 21, BD en 24-25…) : les bras se posent en léger décalage ;
  - arc de profil : points espacés près du coup, serrés ensuite.
  - Vu : planche `r6_M4.png`.
- **Collateral Ruin (2,13 s) :**
  - écarts de 4 à 8 images pendant la montée ;
  - de 0,7 à 2,7 images autour du hitbox (`StartHitbox` 1,255 s, `EndHitbox` 1,633 s) ;
  - des marqueurs `SpeedLinesStart` et `SpinnerSmokeEffect` pilotent les effets **depuis l'anim**.
- **Ultimate2 : 174 clés, une par image à 60 i/s**, donc une animation **cuite** (probablement depuis un autre logiciel ; je ne sais pas lequel). Deux méthodes coexistent donc chez TSB : clés espacées à la main (M4) et cuisson image par image (Ultimate2).
- **Limite :** le JSON de l'outil **ne contient pas le style d'interpolation** (`easing` vide). Je ne peux pas dire si TSB utilise Constant (en marches d'escalier) ou Linear.

---

## 2. Grands enseignements (tous sources confondues)

### E1. La cadence change à l'intérieur d'un même coup, et c'est elle qui fabrique l'accélération
- **Preuve mesurée, planche 12 (JJK) :** anticipation sur 3, puis frappe sur 1, puis contact sur 2.
- **Autres preuves mesurées :**
  - Ota : course sur 1, révélation sur 2 ;
  - Deku planche 11 : impact frames sur 1, extension sur 2 ;
  - Yuta : dessin sur 3 et caméra sur 1.
- **Pourquoi ça marche (déduit) :** une tenue longue (sur 3) donne du poids et fait attendre. Le passage sur 1 est ressenti comme une rupture de vitesse, **même si l'amplitude ne change pas**.
- **Côté R6 (mesuré sur M4) :** les pros obtiennent l'équivalent avec la **densité de clés** (+5, +4, +3, +1 avant le contact).

### E2. Le trajet du coup est presque absent : on montre l'avant, puis l'après
Ce que j'ai vu :
- Nakamura : 0 image de trajet ;
- Toji : on coupe du plan moyen au contact déjà établi ;
- Sakura (Naruto) : 2 images floues ;
- All Might : 2 images ;
- Sakura (Obari) : ≈ 0,3 s ;
- Yuta : le poing grossit sur 3, sans aucune image de contact réaliste.

*Déduit :* le spectateur reconstruit le trajet. Ce qui compte, c'est la **différence entre la pose armée tenue et le résultat**, et la netteté de la rupture.

### E3. Les tenues ne sont pas figées
Mesuré :
- yutapon, tenue sur 1 ;
- Iczer, pose tenue 1,6 s sur 1, où seuls les effets bougent ;
- Nakamura, contact 0,9 s où les arcs électriques bougent sur 1 ;
- JJK, contact sur 2 pendant 0,5 s ;
- Toji, contact ≈ 0,3 s avec micro-variations.

*Déduit :* « tenir » veut dire que **le corps ne bouge presque plus pendant qu'une autre couche vit** (effet, lumière, caméra, déformation). Ça **nuance** la décision v7 du cerveau (« le gel reste un gel », CARNET 4.2). Dans ces anime, le gel du corps s'accompagne toujours d'autre chose qui bouge.

### E4. L'impact est une séquence de dessins différents, pas un filtre
- **Chiffres mesurés :** 15 impact frames différentes (Todoroki, Deku) ; 10 dessins en 0,9 s (Yuta) ; 10 dessins en ≈ 0,6 s (Nakamura).
- **Ce qui revient :** un blanc et un noir d'une image chacun juste avant la couleur (Todoroki 0238/0239) ; le noir et le blanc qui s'alternent à chaque dessin (Yuta) ; des palettes qui changent à chaque image (Chansard, Deku OFA).
- Le genga 01 montre que c'est dessiné au crayon, feuille par feuille.
- *Déduit :* la variation de **forme** empêche l'œil de s'habituer. Un filtre répété sur la même image ne crée pas cet effet.

### E5. L'échelle se fabrique avec la caméra et le raccourci
- Pied plein cadre, puis perso minuscule (Yuta) ; Kaido en 4 cadrages en 0,5 s (Ota).
- Poing plus gros que la tête (Iczer, genga 02, 03) ; contre-plongée (OPM 08).
- Pieds face caméra réduits à 4 points (Yuta #347).
- Le **mannequin 3D rigide d'ufotable** prouve que la perspective et l'échelle se décident dès le blocking, sur un corps rigide, avec la vraie caméra (vu).

### E6. La lumière et la couleur sont des acteurs
- Nakamura anticipe par la lumière.
- Kutsuna recolore le plan et éclaire le visage du côté de la source.
- Deku OFA change de couleur à chaque ponctuation.
- Des images orange pleines d'une seule image servent de coupure (bg 366,8 s).
- Le genga 03 code la densité d'effet en 3 couleurs.

### E7. Le smear est une forme qui raconte une trajectoire, entre deux poses nettes
- Il dure 1-2 images.
- Il peut être :
  - opaque (bras-éclair beige, genga 05) ;
  - flou photographique (boxe) ;
  - multiple (arc, chemin, vitesse) ;
  - devenu effet (lame violette).
- Un smear sans direction (frange) est jugé raté par l'auteur (« Bad Animation », lu).

### E8. Les débris lisibles sont simples et en couches
- Polyèdres à 2 tons, 3 tailles (silhouettes noires devant), qui dérivent pendant les tenues.
- **Le yutapon, c'est « hold and release »** (lu, puis mesuré : tenue sur 1, puis lâcher).

### E9. La méthode de travail
Ce que les sources montrent de la manière de faire :
- storyboard, layout, clé, intervalles, compositing (lu) ;
- blocking sur mannequin rigide dans le décor 3D (vu, ufotable) ;
- référence filmée avec des pratiquants (lu, Garo) ;
- l'animateur clé note l'espacement à la main pour l'intervalliste (vu, 678,5 s et genga 04) ;
- il code la densité d'effet (lu, genga 03) ;
- il s'entraîne à dessiner le cube tournant (vu) ;
- l'auteur vérifie image par image dans sa timeline (vu).

Côté Roblox (lu, Q0mX) :
- effets en maillages animés au plugin ou par tween script, en couches décalées ;
- appendice animé dans Blender avec des contraintes « damp track » ;
- l'animation du perso passe après les effets, de son propre aveu.

---

## 3. Transposition sur R6 : ce que je saurais refaire, et comment

Toutes ces propositions sont **déduites**. Chiffres à 60 i/s ; 1 dessin sur 3 à 24 i/s ≈ 7,5 images à 60 i/s.

1. **Phrase de cadence 3 → 1 → 2 (d'après la planche 12, JJK) :**
   - anticipation en 3-4 clés espacées de ≈ 7-8 images, avec de faibles écarts entre elles (quasi-tenues) ;
   - frappe en 2-3 images ;
   - contact tenu ≈ 30 images (0,5 s), avec une micro-variation toutes les ≈ 5 images (tête qui recule de 2-3°, épaule qui pousse).
   - Sur le modèle M4 : des clés qui se resserrent (+5, +4, +3, +1) jusqu'au marqueur de coup.
2. **Pose tenue et caméra sur 1 (d'après Yuta) :**
   - les clés du corps restent espacées (ou quasi constantes pendant la montée du poing) ;
   - le tremblement de caméra, lui, est redonné à chaque image par script.
   - Les deux couches ont des cadences séparées.
3. **Tenue vivante (d'après Iczer et Nakamura) :**
   - corps quasi immobile (±1-2°) pendant 1 à 1,5 s ;
   - une couche d'effet sur 1 (Beam et arcs électriques redessinés, particules) ;
   - une lumière (PointLight ou ColorCorrection teintée) qui éclaire le perso **d'un côté**.
4. **Pas de trajet visible (d'après Nakamura et Toji) :**
   - en cinématique, couper la caméra à l'image du lâcher : le plan suivant commence au contact déjà établi.
   - En caméra de jeu (pas de coupe possible) : 1-2 images de smear-forme à la place du trajet (voir le point 6).
5. **Impact en séquence :**
   - 10 à 15 images différentes sur 0,4-0,9 s, en ScreenGui/ImageLabel image par image (flipbook), noir et blanc alternés, avec un blanc et un noir d'une image avant la couleur.
   - *Contradiction avec `rapport_anime3d` :* il y classe « impact frames dessinées : IMPOSSIBLE ». Le projet a pourtant déjà produit des « planches plein écran dessinées » (tâche 185). Il faudrait écrire **POSSIBLE en 2D par-dessus**, impossible seulement sur le rig.
6. **Smear-forme opaque (d'après le genga 05) :**
   - pendant 1-2 images, masquer le bras (Transparency) et afficher un maillage plat en forme d'éclair, orienté selon la trajectoire.
   - Les multiples (arc et chemin) se font en clones translucides des membres.
   - *Contradiction :* l'étude existante dit « smear étiré IMPOSSIBLE → Trail/Beam ». La forme opaque qui **remplace** le membre est possible sans déformer le rig.
7. **Échelle :**
   - caméra à ≈ 1-2 studs du poing, grand FOV, poing dans l'axe de l'objectif ;
   - alterner avec un plan très large où le perso est minuscule (Yuta, Ota).
   - Le mannequin d'ufotable montre que c'est exactement le travail que le R6 sait faire.
8. **Débris :** parts plates en 2 tons (Neon ou SmoothPlastic, éclairage plat), en 3 tailles avec des blocs noirs au 1er plan, tenus en l'air (ancrés) puis lâchés.
9. **Ponctuation (d'après Deku OFA) :** sur un mouvement simple, insérer toutes les 0,3-0,5 s un flash coloré d'une seule image, d'une couleur différente à chaque fois.

**Ce que je ne saurais pas faire (honnête) :**
- déformer le corps (courbure du bras, joue qui s'écrase) ;
- faire rouler les yeux ou l'œil d'Umakoshi (le visage R6 est un decal) ;
- les cheveux et le tissu en décalage (le R6 n'a pas d'os pour ça) ;
- redessiner la **forme** de l'éclair à chaque image comme Kutsuna. Avec des Beam, on change la texture ou les points, pas le trait. Je ne l'ai pas essayé.

Je ne sais pas non plus :
- si TSB utilise l'interpolation Constant (le style n'est pas dans le JSON) ;
- ce que valent ces transpositions **à l'écran**, puisque rien n'a été testé dans cette étude ;
- lire les chiffres des échelles d'espacement (flou).

---

## 4. Surprises et contradictions avec le cerveau

1. **Le gel.** CARNET 4.2 dit « le gel reste un gel ». Dans toutes mes mesures, la tenue du corps s'accompagne d'une couche qui bouge sur 1 ou sur 2. Ce n'est pas une réfutation du hitstop de jeu, mais le « gel total » ne ressemble à aucun de ces anime.
2. **Impact frames.** `rapport_anime3d` les dit IMPOSSIBLES. Elles sont possibles en 2D par-dessus, et le projet l'a déjà fait.
3. **Smears.** L'étude existante dit « étiré IMPOSSIBLE ». Le genga 05 montre un smear qui **remplace** le membre par une forme : faisable par échange de pièce.
4. **Iczer.** L'étude existante dit armé « TENU ~2 s » et poing « plus gros que le buste ». Je mesure la pose stable sur ≈ 1,6 s (729,17-730,75 s) et je vois un poing au moins aussi gros que la tête. L'écart est mineur, mais le chiffre est plus précis.
5. **La « tenue » du yutapon** est animée sur 1 (mesuré). Je m'attendais à une image figée.
6. **Le mannequin rigide.** Chez ufotable, un mannequin à blocs rigides fait le blocking. Le « défaut » du R6 (corps rigide) correspond donc exactement à l'étape pro de la pose et de la caméra. Ce qui manque au R6, c'est la couche dessinée qui vient après.
7. **Les sous-titres TSB « scrapped »** ne sont que des paroles de chanson. Il n'y a aucune information technique dedans.

---

## 5. Couverture et ce qui n'a pas été regardé

**Regardé :**
- iMV9 : les 780 s à 1 i/s (toutes les images, session précédente) ;
- à 12 i/s dédoublonné, **62 planches sur 187** :
  - impact, smear et débris en entier ;
  - yutapon : 14 sur 16 ;
  - obari : 6 sur 10 ;
  - le reste par sondage ;
- 14 extraits à cadence native ;
- 20 images en pleine résolution ;
- Yuta : les **554 images**, toutes ;
- genga : les **12**, toutes ;
- les 2 fichiers .vtt : en entier ;
- TSB : 3 animations en planche de clés (M4 regardée en image, les 2 autres en chiffres seulement).

**Pas regardé à 12 i/s** (vu seulement à 1 i/s, avec quelques extraits ciblés) :
- Kanada 294-350 s ;
- background animation 350-406 s ;
- character acting hors 447-451 s ;
- kagenashi hors 484-491 s ;
- Ebata hors 563-568 s ;
- timing 613-716 s hors les extraits natifs Ota, Abe et Furuhashi ;
- Obari 745-756 s.

La raison : ces passages parlent surtout de gestes calmes, de décor ou de style de dessin, loin de mon angle (combat, timing, transposition R6). J'ai préféré mesurer les moments de combat au pas natif plutôt que de survoler plus de planches.

**Non disponible :**
- la vidéo « Making Abilities… » (seulement les sous-titres) ;
- la vidéo « TSB scrapped » (seulement des sous-titres de chanson).

---

## Vérification adverse

Vérificateur indépendant. J'ai essayé de réfuter 8 apprentissages en retournant moi-même aux sources. Mes extractions et mes mesures sont dans `c4/frames/verif_B4_techniques_anime/` :
- `cells.py` : écart moyen entre cellules des planches 24 i/s ;
- `yuta/` : les 554 images réextraites de C09ZMD9_D9I, avec `phase.py` (corrélation de phase) ;
- `yuta_158_221.png`, `nak_sheet.png`, `nak_4.png`, `icz_sheet.png`, `am_hold.png`, `mannequin_sheet.png`, `man_sheet.png` : planches que j'ai regardées ;
- `M4.*` : `planche_cles.py` relancé.

**V1. Cadence 3 → 1 → 2 dans JJK ép. 19 (planche 12) : NUANCÉ.**
- *Ce que j'ai regardé :* la planche lue avec Read, puis l'écart entre cellules que j'ai recalculé.
- *Tenues mesurées :* 0401-03 (3), 0404-06 (3), 0407-08 (**2**), 0409-11 (3), 0412-14 (3), 0415-16 (**2**), puis 0417, 0418 et 0419 changent à chaque image (sur 1). Viennent ensuite 0419-20 (2), 0421 (**1**), 0422-23 (2), 0424-26 (≈3), 0427-28 (2) et 0429-31.
- *Corrections :*
  1. L'anticipation n'est pas « sur 3 » pur. C'est une alternance **3-3-2-3-3-2** : l'œil la lit comme sur 3, mais avec des tenues de 2 intercalées.
  2. La « frappe sur 1 » ne dure que **3 images** (125 ms).
  3. La phase 0420-0431 est **irrégulière** (1, 2 et 3). Ce n'est pas un contact figé : le bras d'Itadori continue d'avancer et Todo réagit.
  4. 0400 appartient à un autre cadrage : il y a une coupe entre 0400 et 0401.
- L'idée générale (la cadence change à l'intérieur du coup) tient.

**V2. M4 (TSB) : les clés se resserrent avant le hitreg : CONFIRMÉ, avec une précision.**
- *Ce que j'ai regardé :* j'ai relancé `planche_cles.py --rbxm tsb_anim.rbxm --nom M4`. La sortie est identique à `r6_M4.txt`.
- *Temps réels du JSON :* 0 ; 0,0887 ; 0,1554 ; 0,2000 ; 0,2221 s. Les écarts sont donc 0,089 / 0,067 / 0,045 / 0,022 s, soit **5,3 / 4,0 / 2,7 / 1,3 images à 60 i/s**. Le « +5, +4, +3, +1 » vient d'un arrondi. En réalité, c'est une décroissance régulière d'environ 1,3 image par écart.
- *Précision :* le hitreg (0,211 s) tombe **entre** la clé de 0,200 s et celle de 0,222 s. La clé la plus serrée arrive donc 11 ms **après** le marqueur, pas dessus.
- La pose des bras en alternance après le coup (BG 18, BD 20, BG 21, BD 24-25, BG 28, BD 29) est confirmée.

**V3. Yuta : dessin sur 3, caméra sur 1 : CONFIRMÉ, mais les numéros d'image sont faux.**
- *Ce que j'ai regardé :* corrélation de phase refaite sur mes propres images (#156-#200), et planche `yuta_158_221.png` regardée.
- Les nouveaux dessins tombent aux **#161, 164, 167, 170, 173, 176, 179, 182, 185, 188, 191, 194**. Ce ne sont pas les #163, 166… 193 cités par le lecteur : il y a un décalage de 2. J'ai vérifié que sa numérotation de fichiers est la même que la mienne (f0161 identique chez nous deux).
- Entre deux dessins, le décalage global est bien de ±1-2 px à chaque image, avec un signe qui alterne (un tremblement).
- Le résidu après recalage vaut ≈3-7, contre ≈10-25 brut.
- *Précision :* le tremblement commence dès #157, donc **avant** que le perso quitte le plan large.
- *Oubli :* le résidu monte à 6-7 en fin de séquence (#190-193). Donc quelque chose bouge aussi sur 1 en plus de la caméra : les lignes de vitesse.

**V4. « Nakamura : 0 image de trajet » : NUANCÉ, presque réfuté dans sa formulation.**
- *Ce que j'ai regardé :* les 47 images natives de 33,20 à 34,73 s (`nak_sheet.png`), dont 4 en grand (`nak_4.png`).
- De 33,43 à 33,63 s, ce qui entre par la gauche n'est pas un simple « arc de lumière sur le visage ». C'est une **masse jaune pâle bordée de jaune vif qui avance de gauche à droite** : elle occupe un tiers, puis la moitié du cadre, jusqu'à toucher la joue. Au même moment, le visage tourne légèrement et la bouche change (33,43 → 33,50).
- *Correction :* le bras n'est pas dessiné, mais le trajet **est montré** pendant ≈7 images, sous la forme de la lueur du poing qui balaie le cadre. C'est un smear devenu forme de lumière, pas une absence de trajet.
- La suite est confirmée :
  - contact à 33,67 s ;
  - arcs électriques qui changent à chaque image jusqu'à 34,57 s ;
  - bascule en noir et blanc à 34,60 s.

**V5. « Les tenues ne sont pas figées, une autre couche vit » : NUANCÉ (contre-exemples trouvés).**
- *Iczer, confirmé :* j'ai réextrait 728,8-732 s (`icz_sheet.png`). De 729,17 à 730,67 s, la pose est stable, et les lignes et le fond changent avec la signature 1-1-1-2 (un doublon toutes les 5 images). Ça fait ≈1,5 s.
- *Premier contre-exemple, dans la même section Obari :* le plan All Might qui suit immédiatement (731,70-732,70 s) est une image **strictement figée pendant ≈1,0 s** (écart < 2/255 sur 30 images, `am_hold.png`).
- *Deuxième contre-exemple, chez Yuta :* la tenue des « débris flottants » (#236-#252, ≈0,7 s) est **quasi figée**. Les écarts valent 0 à 0,9/255, avec une retouche infime toutes les ≈4 images. La tenue finale (#356-#388) ne bouge qu'à très faible amplitude (0,2-2,5).
- *Correction :* « chaque tenue mesurée garde quelque chose en mouvement » est faux en général. Les deux coexistent : une tenue vivante (Iczer, Nakamura) et un vrai gel ou quasi-gel (All Might, débris de Yuta). La nuance apportée à CARNET 4.2 doit donc rester modeste : le gel total existe aussi dans ces sources.

**V6. L'impact, séquence de 10-15 dessins différents : NUANCÉ.**
- *Todoroki (planche 10), regardée et mesurée :*
  - 0222-0236 font bien 15 images toutes différentes ;
  - mais seules 0222-0225 sont des formes abstraites en noir et blanc ;
  - 0226-0236 (11 images) montrent la **silhouette de Todoroki restée lisible**, désaturée en bleu-violet, avec des croix de lumière qui se déplacent. Ce n'est pas la même nature d'image.
  - 0238 BLANC et 0239 NOIR sont confirmés (luminance 243 et 0).
- *Deku (planche 11) :* sur 0562-0576, **0566 est une image en couleur** (visage de Deku, bras rouge) intercalée au milieu des impact frames, et 0572 est un noir plein.
- *Yuta :* je compte **12 dessins** sur #197-#219 (23 images ≈ 0,96 s), pas 10.
  - Ils sont surtout sur 2 (sauf 207 et 210 sur 1, et 211 sur 3).
  - Ils n'alternent **pas** noir et blanc à chaque dessin : 201, 203, 205 et 207 sont tous sombres. L'alternance stricte n'existe que sur 208-216.

**V7. Deku : l'extension sur 2 pendant 24 images : CONFIRMÉ.**
- 0577-0600 forment exactement 12 paires : écarts ≈3-16 à l'intérieur d'une paire, contre 23-65 entre deux paires. Ça fait 24 images, soit 1 s.
- *Précision :* l'écart à l'intérieur des paires grandit en fin de plan (9-16 sur 0596-0600). La lueur semble donc évoluer plus vite que le dessin.
- Le bras est déjà tendu dès 0577. C'est surtout la **main qui grossit vers la caméra** et le blanc qui envahit l'image, plus qu'un bras qui s'étend.
- « La tenue héroïque, pas le coup » reste une interprétation.

**V8. Mannequin à blocs chez ufotable, étape de blocking : NUANCÉ.**
- *Ce que j'ai regardé :* 1 i/s de s209 à s262, et 6 i/s de 255 à 259,5 s.
- Le mannequin bleu à blocs rigides dans le décor 3D final est confirmé, avec les compteurs 0:01:18, puis 0:05:09 à 0:05:19.
- La jambe énorme au 1er plan (≈257,0-257,8 s) et le plan final au même angle bas (259,2-259,3 s) sont confirmés.
- *Oublis qui changent la lecture :*
  1. Tout ce passage est rangé sous l'étiquette **« Rotoscoping »** par l'auteur.
  2. Juste après, à 260-262 s, on voit des acteurs en **combinaison de capture de mouvement** (marqueurs, caméras). Le mannequin sert donc très probablement à visualiser un mouvement **capturé ou de référence**, dans le décor et à la caméra. Rien ne prouve qu'un animateur le pose à la main comme on bloque un R6.
  3. Entre le mannequin et l'image finale, il y a une étape **genga au trait bleu et rouge** (255,3-256,5 s) : c'est là qu'on redessine.
- *Correction :* « le rigide correspond à l'étape pro de pose et de caméra » tient pour la caméra et la perspective. Pour la pose, c'est une référence rotoscopée que l'auteur n'aime pas (« I just dont like how they use it here »), pas un blocking de clés.

**Contrôle secondaire.**
- Les sous-titres « TSB MORE SCRAPPED » sont bien des paroles de chanson (confirmé).
- Q0mX : les citations « mesh animator plugin », « tween… layers », « damp tracks », « stud → centimeters » et « lightning module » sont retrouvées telles quelles.
- L'« aveu » (« adding more animation to the upper body or the swords ») porte sur le Hado 90. En faire « l'animation du perso passe après les effets » reste une extrapolation.

### Oublis importants
1. **Planche 11 (Deku), 0556-0561 :** un plan couleur à fond radial bleu, qui change à chaque image (sur 1), **précède** les impact frames. L'ordre complet est donc : plan sur 1, puis impact frames, puis extension sur 2. Et 0566 est une image couleur glissée dans l'impact.
2. **Planche 10 (Todoroki) :** l'« impact » est surtout une **tenue désaturée de la silhouette avec des croix de lumière qui bougent** (0226-0236). Le corps reste lisible pendant l'impact, ce qui est directement transposable sur un R6 (ColorCorrection désaturée + flares en mouvement), et plus simple qu'un flipbook de dessins.
3. **Yuta est une étude au trait noir sur blanc** (pas un anime fini en couleur). L'alternance noir/blanc de l'impact joue donc sur une image quasi monochrome. Il faut s'en souvenir avant de la transposer à une scène Roblox colorée.
4. **Dans le passage Obari, 733,0-737 s :** une longue rafale en majorité sur 1 (écarts de 20 à 100) suit le gel d'All Might. Le contraste « gel total de 1 s, puis rafale sur 1 » est un vrai exemple de rupture de cadence que le lecteur n'a pas relevé.
5. **Nakamura :** la lumière qui arrive **modifie l'ombre du visage à chaque image** (33,43-33,63 s), et le visage anticipe (il tourne, la bouche change) **avant** le contact. La victime réagit donc avant l'impact : c'est une anticipation de la cible, pas seulement de l'attaquant.
