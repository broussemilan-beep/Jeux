# Chantier 4 — B2 : un coup de poing de A à Z (tuto Blender « myloe ») + pro contre noob

Identifiant : `B2_punch_blender_pro_noob`. Tout ce qui suit est un APPRENTISSAGE (« ici, l'animateur fait X parce que Y »), pas une règle.
Statuts : **vu** (regardé moi-même), **mesuré** (outil : différence d'images, lecture de clés .rbxm, comptage), **lu** (texte à l'écran), **déduit** (mon interprétation).

Dossier de travail (hors dépôt) : `/tmp/claude-0/-home-user-Jeux/4796ac9e-8e41-51f7-91c4-7b92a6a187d0/scratchpad/c4/frames/B2_punch_blender_pro_noob/` (abrégé `W/`).
- `W/tuto_sheets/t00..t62.png` : les 1006 images à 1 i/s du tuto, en planches de 16 (toutes regardées).
- `W/bones/b*.png`, `W/hdr/h*.png` : recadrages agrandis de l'en-tête du viewport « (n° d'image) _Rig : os sélectionné », pour les 1006 secondes. Transcription complète seconde par seconde : `scratchpad/c4/notes/_journal_os_B2.md` ; segments et comptage : `scratchpad/c4/notes/_segments_B2.py` (relançable).
- `W/end30/` : 955-1005 s à 30 i/s (1517 images) ; `W/end_sheets/boucle_finale.png` (999,2-1001,0 s image par image, avec la différence d'image).
- `W/clips/<id>_sNN.png` : les 6 enregistrements de Milan à 30 i/s, en planches de 60 images, **tous regardés en entier** ; `W/clips/9e_result60.png`, `f1_resultat_natif.png`, `8556_natif.png` : passages clés aux images natives (≈60 i/s) avec la différence d'image ; `W/clips/99_noob_res.png` / `99_pro_res.png` : noob et pro épée côte à côte à 15 i/s.
- `W/ana.py` : mesure des tenues (différence moyenne d'image < 0,3 = immobile) sur les images natives.
- `W/tsb_M1.png/.json` : planche de clés du M1 de TSB (outil `planche_cles.py`), pour comparer ce que fait l'expert Blender à une anim pro de jeu.

Rappel lancé avant (`rappel.py --court`) : « tenue », « pro contre noob », « rotation du torse ». Études existantes relues pour aller plus loin : `corpus/tutos/etude_complete_punch_blender.md`, `corpus/tutos/rapport_video_punch_blender.md`, `corpus/ETUDE_NOTES_BRUTES.md` (lot 2 + ref 17-51-39), `corpus/clips/pro_vs_noob_poing.json`.

---

## PARTIE 1 — Le tuto « Expert Roblox Blender/Moon Punch Animation tutorial » (xkHILCmgbig, 16 min 45)

### 1.1 Ce qu'est la vidéo (vu)
Carton « Punch tut: Made by myloe » (0-7 s). Capture continue de Blender en accéléré, sans voix. Rig R6 dont chaque face porte une lettre (F rouge, B bleu, L jaune, R vert, dessus) : c'est ce qui permet de lire les rotations. Textes incrustés (lu) : « Make sure you have good poses » (24-28 s), « You can go in between keyframes for more detail » (95-99 s), « Almost there! » (962-966 s), « Normal speed: » (975-979 s), « done!! » (998-1004 s). Moon Animator n'apparaît jamais (vu, confirme l'étude existante).

### 1.2 Ce que j'ai ajouté aux études existantes : le JOURNAL de ce qu'il touche, seconde par seconde (mesuré par transcription)
L'en-tête du viewport affiche en permanence « (n° d'image courante) _Rig : os sélectionné ». Le texte est **jaune** quand l'image courante porte une clé pour cet os, **blanc** entre deux clés. Je l'ai lu sur des recadrages agrandis pour les 997 secondes utiles (8-1004 s). Chaque seconde est donc classée : « posé sur l'image N, os X » ou « défilement/lecture » (le numéro change d'une seconde à l'autre, texte blanc).

**Où passe son temps (mesuré, `_segments_B2.py`) :**

| Mesure | Secondes (sur 997) |
|---|---|
| Arrêté sur une image-clé à poser | 593 (59 %) |
| **Défilement / lecture de la timeline (il regarde bouger)** | **404 (41 %)** |
| Aucun os sélectionné (il tourne la caméra, regarde) | 393 |

| Par os sélectionné | s |
|---|---|
| UpperArm.L (bras qui frappe) | 150 |
| **UpperLeg.L (jambe)** | **144** |
| UpperLeg.R (jambe) | 101 |
| UpperTorso | 94 |
| UpperArm.R (bras libre) | 89 |
| Head | 26 |

→ **Les deux jambes (245 s) reçoivent plus de temps que les deux bras (239 s)**, et la jambe gauche presque autant que le bras qui frappe. (mesuré ; lecture du nom d'os fiable, quelques secondes ambiguës près des changements.)

| Par groupe de poses (images Blender) | s |
|---|---|
| **Retour / suivi (66-100)** | **241** |
| Frappe + contact (61-62) | 131 |
| Charge (20-40) | 124 |
| Fin de charge (60) | 90 |
| Repos (0) | 6 |

→ **La pose d'APRÈS le coup reçoit le plus de temps de tout le tuto** (mesuré). Le contact lui-même (62) : 116 s. La charge et sa fin (20-60) : 214 s au total.

**Dans quel ordre il pose (première fois qu'il s'arrête sur chaque image, en s de vidéo) (mesuré) :**
0 (8 s) → **40** (15 s) → 20 (105 s) → 80 (125 s) → 60 (234 s) → **62** (243 s) → 61 (261 s) → 30 (270 s) → … → 70 (658 s) → 75 (689 s) → 86 (769 s) → 89/94 (796 s) → 100 (857 s) → 82 (885 s) → 73 (928 s) → **66 (977 s) → 90 (985 s)**.
Lecture (déduit, appuyé sur la timeline lue par l'étude existante) : il pose d'abord la **charge** seule (image 40, 90 s de travail), puis un intervalle (20), puis une pose plus loin (80) ; vers 215-233 s il **déplace les clés** (40→30, 80→60) ; puis il construit le **contact 62** ; toute la **seconde moitié** de la vidéo sert à construire et re-construire la **fin** (70, 75, 86, 94, 100, 82, 73…), et c'est seulement dans les 30 dernières secondes que les dernières clés prennent leur place définitive (66 et 90).

**Ordre des os dans une pose (mesuré sur le journal) — « du centre vers les bouts » :**
- Pose 40 (charge) : UpperTorso (17 s) → Head (21) → UpperLeg.L (25) → UpperLeg.R (28) → **2e passage** UpperTorso (31) → UpperArm.R (37) → UpperArm.L (45) → jambes (51-52) → bras → torse → bras → jambe gauche (62-68) → bras droit (73-81) → bras gauche (82-91).
- Pose 80 : UpperTorso (125) → UpperArm.L → UpperArm.R → UpperLeg.L → UpperLeg.R → …
- Pose 62 (contact) : UpperTorso (299) → UpperArm.L (305-315) → UpperArm.R (316-329) → Head → UpperLeg.R → UpperTorso → UpperLeg.R.
- Pose 80 du retour (585-679) : 10 s **sans rien sélectionner** (il regarde) → UpperTorso → UpperArm.L → UpperArm.R → UpperArm.L → torse → bras droit (10 s) → tête → jambes.
→ Ici, l'animateur commence **presque toujours par le torse**, puis les bras, puis tête/jambes, et il fait **plusieurs passages** sur la même pose (torse → bras → jambes → torse → bras…). (déduit : il fixe d'abord la ligne du corps, ce qui porte l'intention, puis accroche les membres à cette ligne ; le 2e passage corrige les membres qui ne suivent plus le torse retouché.)

**Autres gestes vus (vu, avec temps) :**
- **Vue de profil stricte (orthographique, on ne voit qu'une colonne jaune « L ») à intervalles réguliers** : 435, 518, 529, 541, 547, 699 s, et la vue finale 999 s. Il contrôle la silhouette dans la vue où l'on voit la ligne d'action.
- Vue **depuis la cible** (483-487 s) : visage vers la caméra mais torse montrant sa face R → tête contre-tournée par rapport au torse.
- « **Move selected items** » (translation, pas seulement rotation) sur les bras : 453, 455-456, 462, 507, 740 s ; « Move » affiché 413-415 s. Il déplace les pièces, il ne fait pas que les tourner.
- **Rotation contrainte à un axe** (lignes rouge/jaune qui traversent l'écran) : 569, 744-750, 934 s.
- **~21 s d'affilée en « Trackball » sur UN seul bras, en gros plan, sur l'image 94** (800-820 s, info-bulle lue « Trackball style rotation of selected items »). Même genre de gros plan sur le dos/l'épaule de la pose de retour (944-953 s).
- 12 s d'affilée sur la jambe gauche à l'image 60 (446-457 s) puis 15 s encore (562-576 s) : la fin de charge est réglée **par la jambe** autant que par le bras.
- Clé 61 : aux secondes 711-714 l'en-tête affiche « 61 UpperArm.L » en BLANC (pas de clé), puis en JAUNE à 715 s → **c'est à ce moment qu'il insère l'intervalle 61 sur le bras qui frappe** (mesuré). Il passe ensuite 8 s sur le bras LIBRE à 61 (716-723 s, en jaune). ⚠ Contradiction non résolue : l'étude existante lit la timeline finale avec une clé à 61 sur le seul UpperArm.L ; mon journal voit aussi du jaune sur UpperArm.R à 61 (261 s et 716-723 s). Soit la clé a été supprimée plus tard, soit ma lecture du jaune est fausse (texte petit). Je ne tranche pas.
- « Normal speed: » (975 s) n'est pas la fin : de 977 à 988 s il est encore **en train de poser la jambe droite sur les images 66 et 90** (mesuré). Il retouche la jambe du retour après avoir vu le résultat à vitesse réelle.

### 1.3 Le résultat final, image par image (vu + mesuré sur `W/end_sheets/boucle_finale.png`, 30 i/s)
Boucle mesurée : repos à 999,37 s → repos suivant à 1000,90 s = **1,53 s** (confirme ~90 images à 60 i/s).

| Temps vidéo | ≈ image Blender (60 i/s) | Ce que je vois | diff d'image |
|---|---|---|---|
| 999,37-999,53 | 0-10 | Debout, profil (colonne jaune) | ~0-1 |
| 999,57-999,77 | 12-24 | Les bras montent en garde, le torse commence à tourner (rouge F visible) | 1,4-1,9 |
| **999,80-1000,37** | **26-60** | **Charge : corps détourné, bras armé ; bouge à peine** | **0,0-0,9** (tenue en mouvement ~0,57 s) |
| **1000,40** | **~62** | **Bras tendu à l'horizontale, corps couché : UNE image vidéo** | **4,9** |
| 1000,43 | ~64 | Bras qui se rétracte | 2,4 |
| **1000,47-1000,87** | **66-90** | **Pose d'après : corps plié vers l'avant, DOS à la caméra (bleu), fente** — dérive lente | 0,0-2,8 |
| 1000,90 | 0 | Retour sec au repos (coupure de boucle) | 4,4 |

Ce que ça apprend : le spectateur voit **deux poses longues** (charge 0,57 s ; après-coup 0,40 s) et **le coup lui-même 1 image**. Les deux études existantes le disaient ; je le confirme par la mesure de différence d'image. La nouveauté : le journal montre que le temps de travail suit la même hiérarchie que le temps d'écran — il passe le plus de temps sur les poses que l'œil voit longtemps (retour 241 s, charge 214 s), pas sur l'image de contact que l'œil voit 1/30 s.

### 1.4 Pourquoi ça marche (déduit)
- L'œil ne peut pas lire un bras qui bouge en 1 image ; il lit **l'état avant** (tension, enroulé) et **l'état après** (corps jeté, déséquilibré, dos tourné). Le cerveau du spectateur « remplit » le coup : plus l'écart entre les deux poses est grand, plus le coup paraît violent. D'où : la charge tourne le torse d'un côté, l'après-coup le montre de l'autre côté (face → dos, ~180° d'après l'étude existante).
- Les jambes portent la crédibilité de ces deux poses (fente, jambe arrière couchée) : un bras seul ne dit pas « tout le corps a frappé ». C'est cohérent avec le temps passé sur les jambes.
- Les tenues ne sont jamais figées (diff 0,3-0,9 pendant la charge) : le personnage reste vivant.

---

## PARTIE 2 — Les enregistrements de Milan

### 2.1 9e47148b — pro contre noob, poing (Blender, puis rendu en jeu) (vu, 30 i/s en entier + natif 6,9-8,2 s)
- **0-1,0 s** : vue de face, rig pro (lettres F, rouge) en charge : bras de frappe replié en arrière (brun, bandé), genoux fléchis, fente ; gizmos de rotation successivement sur la jambe (0,13-0,27 s), la hanche (0,33-0,37), le bras (0,47-0,53), le torse (0,70-0,87), le bras avant (0,93-1,0).
- **1,0-2,0 s** : le torse tourne (on voit les faces F puis bleu/jaune), le bras libre passe devant, gizmo sur le torse (1,33-1,57).
- **2,0-3,2 s** : vue plus basse : torse couché très bas vers l'avant, jambes en grand écart (jambe arrière jaune tendue), gizmos torse puis jambe (2,33-2,73), torse (3,0-3,17).
- **3,23-3,33 s** : saut de pose (on défile), **3,37-4,0 s** : contact vu de dos (« BACK ») : bras tendu jusque dans le mannequin, jambes en fente, gizmo sur le **mannequin** (3,87-3,93).
- **4,2-6,0 s** : **il anime le MANNEQUIN** (jaune) : gizmos sur la tête, le torse, les jambes de la victime ; le mannequin se plie autour du poing, tête qui bascule, jambes qui fléchissent (4,33 → 5,6). (vu) → Ici, l'animateur construit la réaction de la victime **dans la même scène, posée contre le poing**, et pas après coup. (déduit : le coup se vend autant par le corps qui le reçoit que par celui qui le donne.)
- **6,0-6,63 s** : relecture sous plusieurs angles (face, profil strict, dos).
- **Résultat en jeu, 6,67-8,70 s, images natives (`W/clips/9e_result60.png`) :**
  - 6,90-7,10 : charge, poing armé près de la tête, torse tournant ; bouge par petites touches (diff 0-3,2).
  - **7,117 : extension en UNE image (diff 5,3)** : bras tendu, torse couché en avant.
  - **7,117-7,50 : pose étendue tenue ~0,4 s** avec micro-mouvements (diff 0-2,7) ; aucune tenue parfaitement figée ≥0,1 s (mesuré : 44 % d'images immobiles, pas de tenue continue).
  - 7,517-7,567 : le bras se retire, le corps se redresse (diff 2,9-6,4).
  - **7,583 : éclat rouge plein écran** (diff 20,6), qui se déploie jusqu'à ~7,95 ; la victime est projetée (visible en l'air 7,98-8,20 en haut à droite).
  - Lecture (déduit) : **l'explosion est retardée d'environ 0,45 s après l'extension** — le coup touche, on tient, puis ça « détone ». Je ne peux pas savoir si c'est voulu comme « impact différé » ou si c'est une 2e frappe ; le montage montre en tout cas que l'effet ne tombe pas sur l'image d'extension.
- **Noob (8,73-9,10 s)** : rig debout parfaitement droit, bras qui sort à l'horizontale **seul** ; tenue figée 0,23 s (mesuré), aucun mouvement de torse ni de jambe (vu).

### 2.2 99a73bd5 — pro contre noob, épée (vu en entier, 30 i/s)
**Construction noob (0-4,7 s)** : profil strict ; il fait tourner la pièce entière autour de la hanche, penche le torse petit à petit (0,33-2,0), change d'angle (vue de dessus 2,2-3,3), revient au profil. Les poses restent des colonnes qui basculent.
**Résultat noob (4,73-7,33 s, `99_noob_res.png`)** : torse FACE caméra la plupart du temps (on lit « FRONT »), bras qui croisent devant le corps, l'épée balaie à travers le personnage (5,13-5,40 ; 6,66-6,93). **Aucune tenue ≥ 0,1 s** (mesuré, `ana.py`) : ça bouge tout le temps à la même vitesse. Immobilité 36 %, mais éparpillée en images isolées.
**Construction pro (7,47-12,67 s)** : 3 poses nettes, chacune travaillée longtemps sur le même numéro d'image :
- 8,07-8,87 : **armement** — torse penché, épée basse en arrière ; gizmos torse → tête/torse → bras.
- 8,87-10,40 : **estoc** en vue 3/4 face : fente, bras d'épée tendu horizontal, bras libre replié ; gizmos torse (9,0-9,17), bras (9,23-9,97), jambes (9,97-10,4).
- 10,43-12,13 : **grand armement haut** vu de dos (« BACK ») : torse vrillé, bras d'épée levé au-dessus de la tête, bras libre (jaune) jeté en arrière, jambes en fente ; gizmo sur le poignet/l'épée 10,5-11,8 (≈1,3 s sur l'angle de la lame).
**Résultat pro (12,67-14,98 s, `99_pro_res.png`)** : garde tenue 0,15 s (12,70) → armement bras haut (13,0-13,4) → estoc bras tendu (13,47-13,74) → vrille (13,8-13,94) → **coup haut, épée au-dessus** (14,0-14,4) → **pose finale tenue 0,5 s** (14,48-14,98). Immobilité 54 % (mesuré). Chaque pose se lit instantanément : silhouettes en diagonale, bras loin du corps, torse montré de profil ou de dos, jamais de face à plat.
→ Différence concrète (vu + mesuré) : **même durée de résultat (~2,5 s), mais le pro a des arrêts francs (0,15 s et 0,5 s) et des poses qui changent de côté du corps ; le noob a un débit continu et des poses de face où les membres se croisent devant le torse.**

### 2.3 f1b5bd4b — pro contre noob, Blender (vu en entier + natif 4,9-6,75 s)
**Construction pro (0-3,93 s)**, caméra collée au rig, mannequin en bois à droite :
- 0-1,43 : **chambre vue de 3/4 dos** : torse tourné (on lit la face R et le dessus), poing replié devant la poitrine, coude haut, genou avant levé ; gizmos sur le bras (1,03-1,43).
- 1,47 : bascule de la pose (on défile) ; 1,50-2,63 : torse montrant **BACK**, bras qui arrive vers le mannequin, gizmos jambes (1,63-1,83, 2,30-2,43) puis avant-bras (2,07-2,27, 2,47-2,53).
- 2,70-2,77 : défilement, **2,77-3,93 : extension vue de face (« FRONT »)** : bras tendu à l'horizontale, **poing exactement sur la tête du mannequin**, torse de face, jambes en fente ; gizmos alternés poing (2,93-3,37, 3,57-3,63) et hanche/jambes (2,87-2,90, 3,67-3,83). Il ajuste **le point de contact** image après image.
**Résultat pro (3,97-7,28 s, natif `f1_resultat_natif.png`)** : ce sont **deux coups enchaînés** (vu) :
- 4,92-5,18 : chambre (bras croisés devant, faces du dessus visibles), bouge peu.
- **5,183 → 5,25 : passage à la pose de frappe en ~2-4 images natives** (diff 9,6-12,6).
- 5,25-5,6 : frappe tenue, dos à la caméra ; **le mannequin se plie en arrière pendant cette tenue** (sa tête part vers la droite).
- 5,6-6,0 : tenue, **bras libre (jaune) jeté loin en arrière** comme contrepoids.
- **6,017 → 6,083 : 2e frappe, même vitesse** (torse qui repasse de BACK à FRONT) ; 6,1-6,6 : tenue, **mannequin plié très fort, tête projetée** ; 6,63-6,75 : retour.
- Mesuré : 39 % d'immobilité seulement, parce que **pendant les tenues de l'attaquant, c'est la victime qui bouge** (les pics de mouvement tombent à 5,22-5,35 et 6,05-6,55).
**Noob (7,30-7,57 s)** : debout de profil, gizmo sur la hanche, rien ne bouge (vu).

### 2.4 8556a37c — « Cross punch » (Moon Animator, boucle d'1 s) (vu en entier + natif 0,15-1,05 s)
- 0,0-0,2 : garde, poings (contour orange lumineux) devant le visage.
- 0,23-0,47 : **armement lent** : le buste tourne jusqu'à montrer le dos, poing à hauteur d'épaule, la queue suit (diff faibles).
- **0,483-0,517 : départ en 2 images natives** (diff 7,3 puis 11,4).
- 0,517-0,567 : étoile blanche à pointes au point d'impact (3 images) ; 0,583-0,60 : anneaux concentriques le long du bras ; 0,617-0,717 : grand croissant de souffle.
- **0,72-0,97 : suivi tenu ~0,25 s**, corps tourné, bras croisé devant ; la queue continue de bouger (mouvement secondaire).
- 0,983 : retour sec à la garde (coupure de boucle).
- Mesuré : 60-67 % d'images immobiles par boucle. Même architecture que myloe : armement long, coup en 2 images, pose d'après tenue.

### 2.5 6a0095ed — « Punch practice », de côté puis de dessus (vu en entier)
- Vue de côté (0-1,33 s puis boucle) : garde basse, jambes écartées ; armement 0,23-0,40 (bras recule, torse tourne) ; **frappe 0,47-0,53 avec traits de vitesse blancs 2-3 images** ; la victime recule 0,53-0,63 ; **fin très basse, accroupie, tenue** 0,67-0,83 (tenue mesurée 0,12 s à 0,87). Boucle ~1,33 s.
- Version « with adornments » (1,67-3,30) : particules orange aux articulations + traits de trajectoire, **ajoutés sur la même animation** (vu) : l'animation se lit déjà sans.
- **Vue de dessus (3,33-6,73 s)** : on voit le torse pivoter de ~45-90° (estimé à l'œil) et le bras traverser en diagonale ; de côté, cette rotation était presque invisible. (vu, angle déduit)

### 2.6 df406483 — « First time fighting a dummy » (vu en entier)
- 0-2,9 s : **comique** — le mannequin l'envoie voler (0,37-0,43 : bloc rouge qui frappe, grosses traînées noires), caméra qui le suit dans le ciel, il tournoie minuscule (1,47-2,1), retombe (2,4-2,8).
- 2,87-2,93 : il frappe le mannequin, éclat radial blanc (le mannequin est projeté 3,0-3,3, on le voit rouler au loin).
- **3,37-4,70 : gros plan visage de 3/4 bas, œil jaune, tenu ~1,3 s** (seulement la respiration).
- 4,73-4,77 : l'éclairage s'assombrit ; **4,80-4,83 carte NOIRE (silhouette griffée blanche)** ; **4,87-4,93 carte BLANCHE hachures radiales** ; 4,97-5,0 carte inversée ; **5,03-5,07 BLANC total** ; **5,10-7,33 : même gros plan, surexposé, cheveux qui bougent**, tenu ~2,2 s.
- Lecture (déduit) : le coup n'est pas montré ; l'ellipse est racontée par 4 cartes de ~2 images (≈0,25 s en tout) prises en sandwich entre deux longues tenues du même plan. Le contraste comique → sérieux donne du poids au moment sérieux.

---

## PARTIE 3 — Comparaison avec une anim pro de jeu : le M1 de TSB (mesuré, `planche_cles.py`, `W/tsb_M1.png`)
7 clés en 0,43 s (i0, 6, 8, 10, 14, 20, 26 à 60 i/s). **Jambes jamais posées** (laissées à l'anim du dessous).
- Lacet du buste : +48° (i0) → +6° (i6) → **−28° (i8)** → −44° (i10) → −63° (i14) → −70° (i20) → −65° (i26).
  Donc 34° en 2 images, puis 16° en 2, 19° en 4, 7° en 6 : **le buste part d'un coup et freine** vers la pose étendue.
- Bras qui frappe (azimut dans le repère du coup) : −54° (i6) → −16° (i8) → +50° (i10) → +119° (i14) : 38°, **66°, 69°** : **le bras accélère quand le buste freine**, avec 2 à 4 images de retard.
- Lecture (déduit) : chaîne cinétique posée clé par clé — le torse mène, le bras suit. Le coup occupe i6→i14 (8 images, 0,13 s), pas 2 images comme chez myloe. C'est un M1 de combo, pas un coup chargé : la brièveté extrême de myloe (60→62) sert un coup unique après une longue charge, alors que le M1 doit se lire en jeu sans charge.

---

## PARTIE 4 — Grands enseignements (transversaux)

### 4.1 Ce qui sépare un pro d'un noob (vu sur 3 comparaisons + mesuré)
1. **Le corps entier contre le bras seul.** Noob poing (9e47148b 8,73) et noob Blender (f1b5bd4b 7,30) : torse vertical immobile, un bras sort. Pro : torse tourné de ~90-180° entre armement et frappe (face ↔ dos lisible grâce aux lettres), jambes en fente, bras libre qui part en contrepoids. (vu)
2. **Des arrêts francs contre un débit continu.** Épée : pro 54 % d'immobilité, tenues 0,15 s et 0,5 s ; noob 36 %, aucune tenue ≥ 0,1 s (mesuré). Myloe : charge 0,57 s, coup 1 image, après-coup 0,40 s (mesuré). Cross punch : 60-67 % d'immobilité (mesuré).
3. **Des poses montrées de profil ou de dos, jamais de face à plat ; membres loin du corps.** Noob épée : « FRONT » à plat, bras qui se croisent devant le torse, silhouette illisible. (vu)
4. **La victime fait partie de l'animation.** Pro 9e47148b anime le mannequin autour du poing (4,2-6,0 s) ; pro f1b5bd4b : la victime se plie pendant les tenues de l'attaquant (mesuré : les pics de mouvement tombent pendant ses tenues). Le noob n'a pas de victime qui réagit. (vu + mesuré)
5. **Le pro règle le point de contact** : f1b5bd4b 2,93-3,63 s, gizmo sur le poing image après image pour le poser pile sur la tête du mannequin. (vu)

### 4.2 Où et dans quel ordre le pro place le rig (myloe, mesuré sur le journal ; confirmé en partie par les pros de Milan)
- Poser **la charge d'abord**, seule, longtemps (image 40 : 90 s), avant tout timing.
- Dans une pose : **torse en premier**, puis bras, puis tête/jambes, **et plusieurs passages**. Les pros de Milan font de même dans leurs constructions (99a73bd5 : torse → bras → jambes à 9,0-10,4 s ; f1b5bd4b : bras ↔ jambes en alternance). (vu)
- **Les jambes ne sont pas un détail** : 245 s de jambes contre 239 s de bras chez myloe ; clé 20 sur la seule jambe gauche ; retouche de la jambe droite du retour jusqu'à la dernière minute.
- **Translation des bras** (Move), pas seulement rotations : le bras est décollé du torse pour allonger la ligne.
- Contrôle en **profil strict** régulier (silhouette) et en **gros plan** (poignet, épaule).
- **~40 % du temps à faire défiler/rejouer** : il juge le mouvement, pas les images fixes.
- **Timing en dernier et par compression** : poses espacées largement (0/40/80), puis clés rapprochées (40→30, 80→60 ; retour 100/85 → 66/90) ; la fin d'anim (End) n'est fixée qu'à la toute fin.

### 4.3 Hiérarchie de l'effort = hiérarchie de ce qui se voit (déduit, appuyé par mesures)
Temps de travail : retour 241 s > charge+fin de charge 214 s > contact 131 s. Temps d'écran : charge 0,57 s, retour 0,40 s, contact 1 image. L'animateur met son soin là où l'œil s'attarde.

### 4.4 Le temps de l'effet (vu sur 3 clips)
L'effet visuel ne tombe pas forcément sur l'image du coup : cross punch = étoile → anneaux → croissant sur ~0,2 s ; pro poing en jeu = éclat rouge ~0,45 s APRÈS l'extension ; « dummy » = le coup n'est jamais montré, remplacé par 4 cartes de 2 images. Chaque fois, **une tenue précède et une tenue suit** l'événement rapide.

---

## PARTIE 5 — Ce qui me surprend / contredit ce que le cerveau croyait
1. **Les jambes pèsent autant que le bras qui frappe** dans le travail de l'expert (mesuré). Le cerveau parle surtout du torse et du bras ; plusieurs anims pros de TSB ne posent même pas les jambes. Les deux sont vrais selon le contexte : un M1 de combo peut se reposer sur l'anim de marche ; un coup unique filmé doit poser les jambes, parce que la fente et la jambe arrière couchée sont ce qui se lit dans les poses tenues.
2. **Le retour reçoit plus de travail que le contact** (mesuré). Cela prolonge l'intuition « la pose d'après est la plus importante » de l'étude existante : ce n'est pas juste le résultat, c'est là que l'expert passe son temps.
3. **« Frappe en 2 images » n'est pas universel** : TSB M1 étale le coup sur 8 images, avec un buste qui part fort puis freine et un bras qui accélère ensuite (mesuré). Myloe (coup unique après longue charge) : 2 images. Il y a deux régimes et ils ne se remplacent pas.
4. **Les tenues « vivantes » ne sont presque jamais figées** : chez myloe diff 0,3-0,9 pendant la charge ; chez le pro en jeu, aucune tenue continue ≥ 0,1 s malgré 0,4 s de pose étendue. Le seul qui tient une pose parfaitement figée, c'est le noob poing (0,23 s, mesuré), et ça se lit comme un arrêt mort.
5. L'effet d'impact peut arriver **après** la pose de coup (pro 9e47148b, ~0,45 s) : je pensais l'effet collé à l'image de contact.
6. Contradiction interne : une clé à 61 sur le bras LIBRE (lue en jaune à 261 s et 716-723 s) contre la timeline finale lue par l'étude existante (61 sur le seul bras qui frappe). Non tranché.

---

## PARTIE 6 — Ce que je saurais refaire en R6 maintenant (concret, 60 i/s)
Coup unique façon myloe (ce n'est pas LA réponse au poing chargé ; c'est ce que je sais construire d'après ce que j'ai vu) :
- **i0 repos.** **i12-24** : garde qui monte, torse qui commence à tourner (clé intermédiaire posable sur une seule jambe pour régler l'appui, comme la clé 20).
- **i30 charge** : torse tourné ~90° à l'opposé de la cible et légèrement penché ; bras de frappe armé haut en arrière (translation de l'épaule vers l'arrière autorisée) ; bras libre pointé vers la cible ; jambe avant fléchie sous le corps, jambe arrière en diagonale (~30°).
- **i30→i60** : la même charge, un peu plus enroulée (torse +quelques degrés, tête plus basse) : tenue en mouvement de 0,5 s.
- **i61** (bras qui frappe seulement) : intervalle qui fait passer le poing devant, en tête.
- **i62 contact** : torse retourné (on voit le dos, ~180° depuis la charge), penché ~45° ; bras tendu dans l'axe de l'épaule et **translaté vers l'avant** ; bras libre replié haut contre la tête ; jambe arrière couchée loin derrière.
- **i63-66** : le bras se rétracte vers une garde haute, le reste du corps **ne bouge pas**.
- **i66→i90** : pose d'après tenue en mouvement (corps plié, dos à la caméra, fente) ; c'est elle qui doit recevoir le plus de soin.
- Ordre de travail : torse → bras → tête/jambes, deux passages par pose ; contrôle en profil strict ; timing par compression à la fin ; relire en boucle souvent.
Réaction de victime (d'après f1b5bd4b / 9e47148b) : poser la victime **pendant la tenue de l'attaquant** (elle se plie autour du point d'impact, tête qui part), et poser le poing exactement au point de contact.
Variante M1 de combo (d'après TSB M1) : buste 34° en 2 images puis freinage sur 12 images, bras qui accélère 2-4 images plus tard ; jambes laissées à l'anim du dessous.

## Ce que je ne saurais pas faire / pas vérifié
- Les angles exacts des poses de myloe (le panneau Transform n'est jamais ouvert ; angles à l'œil).
- Les courbes (Bézier ou autre) : aucun éditeur de courbes ouvert dans le tuto.
- Chiffrer la translation du bras (Move) : vue, non mesurable.
- Juger si le retard de l'éclat rouge (9e47148b) est une intention d'« impact différé » ou une 2e frappe.
- Les pros de Milan sont des extraits de résultats et de constructions accélérées : je ne vois ni leurs courbes ni leur timeline.
- Rien ne me dit si ces poses « marchent » avec la caméra de jeu TSB : myloe juge en profil, pas en caméra épaule.

## Non couvert / limites
- Le tuto a été regardé en entier à 1 i/s (planches de 16) + journal complet de l'en-tête ; à 30 i/s seulement la fin (955-1005 s) : je n'ai pas repassé à 10-30 i/s les brèves lectures en cours de travail (ex. 215-233 s, 680-688 s, 837-854 s) parce que ce sont des défilements manuels, pas des lectures à vitesse réelle.
- Le son des clips n'a pas été écouté.
- La lecture jaune/blanc de l'en-tête est fiable pour les numéros et os, moins pour la couleur sur quelques secondes (2-3 s ambiguës autour des changements).

---

## Vérification adverse

Vérificateur adverse, sans rien modifier dans le dépôt. Mes extractions sont dans `scratchpad/c4/frames/verif_B2_punch_blender_pro_noob/` (abrégé `V/`) : `boucle/` + `boucle_sheet.png` (998,9-1001,4 s à 30 i/s), `M1.png/.json` (planche_cles.py relancé), `tl_200_244.png` (dope sheet agrandie à 200-244 s), `t970_993.png`, `9e_7_8.png`, `9e_noob.png`, `f1_49_68.png`, `f1_noob.png`, `df_sheet.png`. J'ai aussi relancé `_segments_B2.py` et `ana.py`, et relu `hdr/h0700.png` et `h0900.png`.

**Défaut de méthode qui touche plusieurs affirmations : le jaune de l'en-tête ne veut pas dire « cet os a une clé ».** Sur `hdr/h0700.png` et `h0900.png`, le texte est jaune alors qu'**aucun os n'est sélectionné** (« (62) _Rig » à 702, 709 et 728 s ; « (61) _Rig » à 732 et 784 s ; « (73) _Rig » à 928 s). Dans Blender, cette couleur vient de l'objet armature : elle dit que l'image courante porte une clé, quel que soit l'os. Toute lecture « jaune = clé sur l'os X » est donc fausse.

**Deuxième défaut : les enregistrements d'écran contiennent des images en double.** Dans les suites de différences natives de `ana.py`, on trouve des 0,0 réguliers toutes les 2 à 3 images en plein mouvement (épée noob 4,79-7,34 ; pro poing 7,0-8,6). En cross punch, l'image ne change qu'une fois toutes les ~4 images pendant l'armement (0,15 / 0,233 / 0,333 / 0,40 s). Les « % d'images immobiles » mesurent donc surtout la cadence de capture, pas le jeu de l'animateur. Seules les tenues faites de zéros consécutifs sur ≥ 0,1 s sont fiables.

| # | Apprentissage | Verdict | Ce que j'ai regardé | Correction |
|---|---|---|---|---|
| 1 | Jambes ≈ bras (245 contre 239 s) | **nuancé** | `_segments_B2.py` relu : `bone[o]` compte aussi les secondes de défilement où un os reste sélectionné. Recompté sur les seules secondes arrêtées sur une image : UA.L 134, UL.L 107, UL.R 85, UA.R 84, torse 82, tête 19 | En temps arrêté, **bras 218 s contre jambes 192 s**. 53 s de « jambe » sont du défilement avec la jambe restée sélectionnée (95-104, 119-124, 577-584…). Les jambes reçoivent beaucoup (~47 %), mais pas plus que les bras. « Sélectionné » ne veut pas dire « manipulé ». |
| 2 | Le retour reçoit plus de travail que le contact, et le plus de tout le tuto | **nuancé** | `V/tl_200_244.png` : dope sheet à 200-214 s avec des clés en 0/20/40/80. À 222-234 s, les clés sélectionnées (jaunes) glissent. À 236 s : 0/20/30/60. Décompte avant/après 215 s | Les **57 s passées sur l'image « 80 » avant 215 s** portaient sur la pose qui deviendra **60** (fin de charge), pas sur le retour. Recompté : retour 184 s, fin de charge 147 s, contact 131 s, charge 124 s. Le retour reste le plus gros groupe et dépasse le contact. En revanche, **charge + fin de charge = 271 s > retour 184 s** : l'ordre « retour 241 > charge 214 » de 4.3 s'inverse. |
| 3 | Clé 61 insérée à 715 s sur le bras qui frappe ; « contradiction » UpperArm.R | **nuancé** (la contradiction est **réfutée**) | `hdr/h0700.png` : 711-714 blanc (711-712 sans os, 713-714 UpperArm.L), 715 jaune UpperArm.L, 716-723 jaune UpperArm.R, et jaune sans aucun os à 702, 709, 728, 732 et 784 | À 715 s, une clé apparaît bien sur l'image 61 pendant que UpperArm.L est actif. L'en-tête ne permet pas de dire sur quel os. Le jaune à 716-723 s (et 261 s) sur UpperArm.R ne prouve **aucune** clé sur ce bras : il dit seulement que l'image 61 porte une clé. Il n'y a donc pas de contradiction avec l'étude existante. |
| 4 | myloe : charge tenue 0,57 s, coup 1 image, pose d'après 0,40 s, boucle 1,53 s | **confirmé** | Réextraction à 30 i/s (`V/boucle_sheet.png`), différence d'image plein cadre : saut à 999,367 (2,13, repos debout) ; charge 999,80-1000,367 (0,0-0,85) ; **bras tendu seul à 1000,40** (2,11) ; 1000,433 bras qui revient ; corps plié, dos bleu 1000,467-1000,867 ; retour debout 1000,90 (1,99) | Rien à corriger sur les temps. Précision : c'est une lecture du viewport Blender filmée à 30 i/s. « Une image vidéo » correspond au mieux à 2 images Blender, donc on ne voit pas si 61 et 62 sont toutes deux affichées. |
| 5 | TSB M1 : buste qui part fort puis freine, bras qui accélère ensuite, coup sur 8 images | **nuancé** | `planche_cles.py --nom M1` relancé (`V/M1.png`) : lacet +48/+6/−28/−44/−63/−70/−65, azimut LA −82/−54/−16/+50/+119, **marqueur `hitreg` à i10**, `end` à i25, parts posées T H BD BG | Les chiffres sont exacts. Oublis : (a) **le coup est enregistré à i10**, soit 4 images après i6, pas au bout des 8 images ; (b) en vue de profil, le bras bleu est **déjà tendu à l'horizontale à i8**, et la suite de l'azimut (+50 → +119) est un balayage **après** le hitreg ; (c) le buste tourne déjà de 42° entre i0 et i6 (7°/image) avant la bouffée de 17°/image. Dire que le bras accélère quand le buste freine est vrai pour l'azimut, mais cette accélération tombe après le contact. |
| 6 | Épée : pro 54 % immobile avec tenues 0,15 et 0,5 s, noob 36 % sans tenue, même durée ~2,5 s | **nuancé** | `ana.py` relancé et suites de différences imprimées image par image | Les **tenues du pro sont réelles** (zéros consécutifs 12,697-12,813 et 14,48-14,98) et **le noob n'a aucune tenue**. Par contre, les 36 % du noob sont **entièrement des images en double** de la capture (0,0 toutes les 2-3 images), et les 54 % du pro en contiennent aussi. Autre point : **l'anim du noob est une boucle de 1,50 s** (la suite de différences 4,79-5,30 se répète telle quelle à 6,29-6,80). Les deux résultats n'ont donc pas « la même durée ». |
| 7 | Pro poing en jeu : l'explosion arrive ~0,45 s après l'extension | **nuancé** | `V/9e_7_8.png` (une image native sur deux, 6,955-8,223) | Le délai est confirmé : extension à 7,122, éclat à 7,590 (0,47 s). Mais à **7,523-7,557 l'attaquant ramène le bras et re-tourne le buste**, et l'éclat tombe **juste après ce ré-armement**. C'est donc plus probablement une 2e détente cachée par le flash qu'un « impact différé » de la pose tenue. Il finit accroupi très bas, poing en avant (7,96-8,22). Autre point : `ana.py` sur 6,67-8,70 trouve une **vraie tenue figée de 0,30 s à 6,69** (la charge), ce qui contredit « aucune tenue figée ≥ 0,1 s » de 2.1. |
| 8 | Noob au poing : torse figé, seul le bras sort ; tenue figée 0,23 s = arrêt mort ; pas de victime | **réfuté** (en l'état) | `V/9e_noob.png` et `V/f1_noob.png` | Les deux « noob » sont des **chutes de gag de ~0,35 s coupées par le centre de contrôle iOS** (9,14 s et 7,60 s). f1b5bd4b : le bras **ne bouge pas du tout**, seul un gizmo de hanche est visible. 9e47148b : deux rigs debout (vert R et jaune L, **la victime est donc là**), le bras ne commence à monter qu'à ~9,07-9,10, puis la vidéo est coupée. Les 0,23 s « figées » sont le début de l'extrait, pas une tenue d'animation. On ne peut rien comparer image par image avec les pros. |

**Autres contrôles rapides (hors des 8) :**
- 41 % de défilement : le comptage se reproduit (404/997). Mais ce sont des secondes de **vidéo accélérée et montée**, pas des secondes de travail. Et 311 de ces 404 s se passent sans aucun os sélectionné. Les longs blocs 894-920, 942-976 et 990-1004 s sont des lectures de prévisualisation.
- « Normal speed » : les retouches sont confirmées à 977-988 s (gizmo de rotation visible sur la jambe à 980, 983 et 987 s dans `V/t970_993.png`). Mais la légende s'affiche **pendant** ces retouches. La lecture en vitesse réelle qu'elle annonce semble être 990-1004 s. « Il voit la vitesse réelle, puis corrige » n'est donc pas établi.
- f1b5bd4b, deux coups et victime qui se plie pendant les tenues : **confirmé** (`V/f1_49_68.png` : BACK à 5,25-5,98, bras libre jeté en arrière à 5,58-5,98, FRONT à 6,08, mannequin presque à l'horizontale à 6,13-6,33).
- df406483, les cartes : **confirmé** (4,745 assombri ; 4,812-4,862 noir ; 4,878-4,962 hachures ; 4,978-5,012 inversé ; 5,045-5,078 blanc ; 5,112 gros plan surexposé). Nuance : les cartes **dessinent le poing** (bras et traits de vitesse façon manga). Le coup est donc montré, sous forme dessinée.
- Cross punch : `ana.py` ne trouve **aucune tenue ≥ 0,1 s**. Les 60-67 % d'images immobiles viennent de la cadence saccadée de l'aperçu (une image nouvelle toutes les ~4 images natives pendant l'armement), pas de tenues.

**Oublis importants :**
1. La couleur de l'en-tête Blender est liée à l'armature, pas à l'os (voir plus haut). Cela invalide toute attribution « clé sur tel os » tirée du journal.
2. Le déplacement des clés 40→30 et 80→60 se voit sur la dope sheet (222-236 s). Il fallait réaffecter le temps « 80 » d'avant 215 s à la pose 60.
3. Des images en double gonflent tous les « % immobiles » des enregistrements.
4. Le marqueur `hitreg` i10 du M1 TSB n'est pas mentionné.
5. Le ré-armement juste avant l'éclat rouge (9e47148b, 7,523-7,557) n'a pas été vu.
6. La boucle de 1,50 s du noob à l'épée n'a pas été vue.
7. Les extraits « noob » au poing sont des chutes coupées. Ce ne sont pas des animations complètes.
8. Les cartes de df406483 représentent le poing dessiné.
