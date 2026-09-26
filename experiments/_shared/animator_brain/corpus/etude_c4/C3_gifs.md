# Chantier 4 — C3_gifs : les 13 GIF de Milan, regardés image par image

Apprenti, pas enquêteur. Chaque GIF a été décomposé en TOUTES ses images
(ffmpeg, `-fps_mode passthrough`, horodatage réel de la GIF incrusté :
`#n t=…`, n = index 0-based). Les délais par image ont été lus avec ffprobe
(les GIF ont des cadences irrégulières : 60/70 ms alternés, 30/40 ms, etc.) ;
les temps cités sont ceux de la GIF, pas une cadence supposée.
Images de travail (jamais versionnées) :
`/tmp/claude-0/-home-user-Jeux/4796ac9e-8e41-51f7-91c4-7b92a6a187d0/scratchpad/c4/frames/C3_gifs/<id>/all/NNNN.png`
(NNNN = n+1), planches 4×4 dans `…/<id>/sheets/`, zooms `…/<id>/z_*.png`.

Statuts : **vu** (regardé moi-même sur les images), **mesuré** (outil :
ffprobe, différences d'images, luminance), **lu** (texte), **déduit**
(mon interprétation).

| id | contenu | durée | images | délai/image (ffprobe) |
|---|---|---|---|---|
| 48244687 | Serious Punch TSB | 10,07 s | 151 | 60/70 ms |
| 772ee6b0 | « Serious Punch 2 » | 7,19 s | 108 | 60/70 ms |
| 58322fc4 | boxeur type Ippo, ultime | 11,2 s | 224 | 50 ms |
| a0341700 | rafale gatling, caméra de dos | 6,24 s | 206 | 30 ms (6 × 40) |
| aafdc91d | perso orange, caméra lointaine | 4,23 s | 128 | 30 ms (13 × 60) |
| 6d3be6e1 | Mythra, saisie + projection | 4,19 s | 67 | 60/70 ms |
| 4e337114 | Mii Smash, coup chargé | 8,71 s | 67 | 130 ms (!) |
| 946bd286 | coup chapeau | 10,07 s | 151 | 60/70 ms |
| 3ee5a405 | double jab R6 | 1,56 s | 25 | 60/70 ms |
| 449345ad | M1 rue de nuit | 2,87 s | 46 | 60/70 ms |
| 656d965b | Goku poing levé | 2,0 s | 40 | 50 ms |
| 37d7971a | exemple Blender, projection à 2 | 3,2 s | 64 | 50 ms |
| fa7b867c | combo R6 « front » (Moon, rig coloré) | 3,23 s | 97 | 30/40 ms |

Mesuré : le Mii (4e337114) n'a que 7,7 i/s (130 ms par image) : c'est une
GIF sous-échantillonnée, ses « 2 images » valent 0,26 s. Tout timing fin
y est impossible.

---

# PARTIE 1 — Source par source

## 1. Serious Punch TSB (48244687) — 151 images, 10,07 s

### Ce que j'ai vu, dans l'ordre (vu, images citées)

| temps (s) | images | ce qui se passe | caméra |
|---|---|---|---|
| 0-0,27 | #0-#4 | perso de dos, debout, cape jaune, caméra de jeu, rien ne bouge | caméra de jeu, loin |
| 0,33-0,53 | #5-#8 | la caméra FONCE dans son dos, passe sur l'épaule (#6-#7 : cape jaune plein cadre) puis contourne l'épaule (#8 : torse violet de côté) | poussée + contournement (~0,2 s) |
| 0,6-1,6 | #9-#24 | on est DEVANT lui, collé : son bras noir couvre 60-90 % de l'écran, on voit le visage en haut du cadre (#10-#22). Le bras DESCEND lentement en diagonale devant l'objectif (#16 → #24) : c'est le bras qui va se poser dans la pose neutre | caméra très proche, qui recule doucement |
| 1,67-1,8 | #25-#27 | le bras arrive en bas-gauche (sa position de la pose neutre), un fin trait blanc suit son arc (#23-#26), révélation du perso de FACE en plan moyen | recul |
| 1,8-2,87 | #27-#43 | **pose neutre tenue** : debout, bras droit tendu en avant-bas en diagonale (pas une garde), bras gauche le long du corps, tête droite, visage inexpressif. Il y a un micro-mouvement (épaules, bras) mais la silhouette ne change pas | fixe, de face, léger contre-plongée |
| 2,93-3,13 | #44-#47 | **anticipation du saut** : le buste se tord et plonge vers la gauche de l'écran (#44 penche, #45 plié, #46-#47 accroupi, genoux fléchis, bras qui partent) | la caméra commence à suivre |
| 3,2-3,4 | #48-#51 | la caméra FOUETTE : le perso sort du cadre à droite (#49), on voit le sol puis le ciel en contre-plongée (#50-#51) | fouet ~0,2 s |
| 3,47-3,67 | #52-#55 | il RE-RENTRE par la gauche du cadre (#52-#53 : seulement la cape), s'installe à gauche | caméra au ras du sol |
| 3,73-4,47 | #56-#67 | **approche en pose tenue** : fente basse, une jambe devant pliée, l'autre tendue derrière, buste penché, bras avant tendu vers la cible, cape qui traîne derrière. La silhouette reste LA MÊME ~0,75 s, pendant que la caméra se rapproche doucement (il grossit dans le cadre : #56 petit → #67 moyen) | plan large bas qui se resserre |
| 4,53-5,07 | #68-#76 | **armé** : il se redresse ; GENOU HAUT (cuisse à l'horizontale), buste tourné DOS à la caméra / de profil, tête tournée vers le bas-gauche, bras droit plié devant le genou, bras gauche levé plié près de la tête (#70-#75). Tenue ~0,5 s pendant que la caméra tourne autour de lui et s'approche | orbite lente, contre-plongée |
| 5,07-5,27 | #76-#79 | **déroulé** : le buste pivote VERS la caméra, la tête arrive de face (#78), le bras passe devant la poitrine à l'horizontale ; UN trait blanc en arc (smear léger) sur 2 images (#77-#79) | caméra collée |
| 5,33-5,93 | #80-#89 | **poing dans la fumée** : très gros plan, le poing noir poussé vers l'objectif dans un tourbillon de fumée grise (le tourbillon tourne, #82-#88) ; on ne voit plus que poing + torse. Tenue ~0,6 s | très gros plan qui glisse |
| 5,93 | #89 | UNE image : le perso de dos-profil, poing tendu vers la victime au loin (qui est minuscule, au fond) | contre-champ large |
| 6,0 / 6,07 / 6,13 | #90, #91, #92 | 3 cartes encre, UNE image chacune (≈ 65 ms chacune) : croquis du perso, éclat de hachures radiales, grand X blanc | — |
| 6,2-6,6 | #93-#99 | blanc total 1 image (#93), puis le blanc se dissout en fumée (#94-#99) sur ~0,4 s ; on devine la fente | — |
| 6,67-9,4 | #100-#141 | **conséquence tenue** : de dos 3/4, genoux fléchis, accroupi, le bras de frappe PLIÉ à l'horizontale devant le buste (vu #100-#111 : je ne vois pas un bras tendu, contrairement à ce que dit la fiche UN_SEUL_COUP « fente, poing en avant » ; angle de dos, confiance moyenne) ; devant, un champ de dalles de roche grises en pyramides + colonnes de fumée au fond. La silhouette ne bouge presque pas (mesuré : différence d'image dans la zone perso 1-9 niveaux de gris sur #127-#141, contre 20-40 pendant l'action) | fixe, caméra de jeu derrière lui |
| 9,47-10,07 | #142-#150 | fin : retour debout, bras le long du corps, caméra de jeu derrière (mesuré : pic de différence #142-#143 = 15-17) | caméra de jeu |

### Ce que je comprends (déduit)

- **Le seul geste vraiment rapide** du personnage est le déroulé
  5,07→5,27 (3 images). Le saut (2,93-3,4) est rapide aussi mais il est
  « caché » par le fouet de caméra : on ne voit pas les membres, on voit la
  caméra partir. Tout le reste est tenu.
- **L'armé est une pose de lanceur (baseball / « pitch »)** : genou levé,
  dos tourné vers la caméra, un bras en haut, un bras en bas. Ce n'est PAS
  « poing tiré loin derrière la hanche ». La tension vient de la ROTATION du
  corps entier (dos → face) et du genou levé (le poids est sur une jambe,
  donc instable, donc il va devoir retomber = promesse de mouvement).
- **La libération se fait vers l'objectif**, pas vers la victime vue de
  côté : le spectateur est la cible (#78 : le visage et le poing arrivent
  face à nous). Puis UNE image de contre-champ (#89) nous remet la vraie
  géographie (lui, la victime au fond) juste avant les cartes.
- **Le « contact » n'est jamais montré.** Poing dans la fumée → contre-champ
  1 image → 3 cartes → blanc. C'est la leçon firytwig « you can skip the
  point of contact » appliquée à un ultime.
- **La tension se construit par la CAMÉRA qui tourne autour d'un corps
  presque immobile** (approche 0,75 s tenue, armé 0,5 s tenu avec orbite,
  poing 0,6 s tenu dans la fumée). Le corps donne 3 poses ; la caméra donne
  le mouvement.
- **Le début (0,33-1,8 s)** : la caméra passe DANS le dos, contourne
  l'épaule, puis le bras DESCEND lentement devant l'objectif jusqu'à sa
  place dans la pose neutre (un geste lent de 1 s vu à 20 cm : le geste le
  plus banal devient monumental parce qu'il est collé à l'objectif). C'est une transition « par le corps » :
  1,3 s où l'on ne voit presque que du noir (le bras). Je comprends que
  c'est un rideau : le passage de la caméra de jeu à la cinématique se fait
  en cachant l'écran avec le perso lui-même.

### Surprises / écarts avec ce que le cerveau croyait

- Le CATALOGUE parle de « garde tenue 32 f ». Ce que je vois 1,8-2,87 n'est
  pas une garde : c'est une pose NEUTRE (bras droit tendu vers le bas en
  diagonale, l'autre ballant), ~16 images GIF (≈ 1,07 s). Je ne sais pas
  d'où vient le « 32 f » (peut-être 32 images à 30 i/s ≈ 1,07 s : même
  durée, autre unité). **Déduit** : même durée, mot différent ; « garde »
  induit en erreur pour la pose.
- La fiche UN_SEUL_COUP dit « armé 4,6-5,1 : il se relève, bras armé ». Je
  précise ce que « bras armé » veut dire ici (vu, #70-#75) : genou haut,
  dos à la caméra, UN bras en haut près de la tête, UN bras plié devant le
  genou. L'armé est dans le TRONC tourné, pas dans un bras tiré en arrière.
- La fiche dit « frappe 5,2-5,9 poing vers l'objectif dans la fumée
  (0,8 s) ». Vu : la partie rapide ne dure que 3 images (5,07-5,27) ; 5,33-
  5,93 est une TENUE du poing tendu dans la fumée. Donc « frappe 0,8 s »
  mélange un geste de 0,2 s et une tenue de 0,6 s. C'est important : la
  frappe est courte, la tenue du résultat est longue.
- Les 3 cartes font UNE image GIF chacune (≈ 65 ms), pas « 4 f » (le
  catalogue dit 4 f : à 60 i/s, 4 f = 67 ms : même chose). Cohérent.

## 2. « Serious Punch 2 » (772ee6b0) — 108 images, 7,19 s

- **Vu** (planches s01, s03, s05, s06 relues image par image ; s02, s04, s07 lues une fois en planche) : c'est la MÊME animation que TSB avec un autre avatar (maillot
  Roblox, casquette, cape blanche). Mêmes poses dans le même ordre :
  bras qui balaie l'écran (0-1,0 s, #0-#15), pose neutre face caméra
  (1,33-2,13, #20-#32, bras droit tendu en diagonale vers le bas),
  anticipation + saut (2,2-2,67, #33-#40 : il se penche, se tord, la
  caméra le suit puis fouette vers le ciel #41), re-rentrée par le bord
  (#43), approche en fente tenue (2,93-4,0, #44-#60), armé genou haut
  (4,07-4,53, #61-#68), déroulé (4,6-4,67, #69-#70), poing dans la fumée
  (4,73-5,27, #71-#79), cartes (5,33 / 5,4 / 5,47 / 5,53 : 4 cartes =
  croquis, hachures, hachures + contre-jour, X), blanc (5,6) qui se
  dissout (5,67-5,93), conséquence (5,93-7,13).
- **Mesuré (par comparaison des temps)** : cartes TSB 6,0 contre SP2
  5,33 → décalage 0,67 s ; armé genou haut TSB 4,53 contre SP2 ≈ 4,0 →
  0,53-0,6 s. Cohérent avec la correction de Milan (« même anim décalée de
  0,6 s »). La GIF SP2 commence simplement plus tard dans la séquence.
- **Différence réelle** : SP2 a 4 cartes (#80-#83), TSB en a 3 visibles.
  Peut-être une image perdue à l'encodage de la GIF TSB : je ne sais pas.
- **Ce que ça m'apprend (déduit)** : la cape/le manteau suivent les
  mouvements comme un drapeau (grands pans plats, latence de 1-3 images
  derrière le corps, visibles #52-#67 TSB). Chez nous la cape est
  supprimée (mandat §1) : on perd ce « retard » qui lisait le mouvement.
  Il faudra que ce soit le buste / les bras qui portent ce retard.


## 3. Boxeur type Ippo (58322fc4) — 224 images à 50 ms, 11,2 s

### Déroulé vu (images citées)

| temps | images | corps | caméra / effets |
|---|---|---|---|
| 0-0,35 | #0-#7 | de dos, debout, garde basse ; une aura d'étincelles blanches sur le corps (charge) ; le mannequin gris devant lui | caméra de jeu, de dos, loin |
| 0,35-1,35 | #7-#27 | il lève les gants (#7), puis ENCHAÎNE des coups au mannequin (une gerbe d'éclats blancs à chaque coup, environ toutes les 2-3 images) en avançant d'un pas ; le corps penche, tourne à gauche/droite | caméra de jeu fixe |
| 1,4-1,55 | #28-#31 | **blanc plein écran** (mesuré : luminance 248 à 1,4 s, puis 239, 213, 199, 150, 109 : le blanc s'éteint en ~0,3 s) ; bandes noires cinéma apparaissent en haut et en bas | coupe vers la cinématique, cachée dans le blanc |
| 1,5-1,6 | #30-#32 | coup avec gerbe ROUGE (sang) + arcs blancs, les deux corps collés | plan rapproché |
| 1,65-2,45 | #33-#49 | le boxeur tisse (roulis) derrière le mannequin : tête basse, gants au visage, **traînées BLEUES** à la place du corps en mouvement | caméra DERRIÈRE le mannequin, épaule du mannequin en amorce (flou au 1er plan) |
| 2,5-3,45 | #50-#69 | il reste collé au mannequin, bas, gants hauts, aura bleue ; vu sur la planche s05 (3,2-3,45) : caméra toujours derrière le mannequin, le boxeur apparaît sur son côté. Le « 8 » (roulis de Dempsey) est la lecture du cerveau ; je vois des déplacements latéraux bas, je ne peux pas affirmer la figure en 8 | caméra derrière le mannequin, puis 3/4 |
| 3,5-4,2 | #70-#84 | **pose tenue** : accroupi très bas, buste ~45°, gant gauche tendu bas vers l'avant, droit au visage ; aura bleue ; ~0,7 s presque sans changement de silhouette | nouvel angle bas de face |
| 4,25-6,35 | #85-#127 | **série de coups** : un flash blanc toutes les ~0,25 s (mesuré, luminance > 180 : 4,25 / 4,5 / 4,75 / 5,0 / 5,3 / 5,5 / 5,8 / 6,05 / 6,3 = 9 flashs), chaque flash suivi d'un anneau ROUGE, d'éclaboussures rouges et d'arcs blancs ; le boxeur alterne les crochets | **l'angle change dans les flashs** (vu : #95→#97, #101→#102, #110→#112, #116→#117 : la caméra n'est plus au même endroit après le blanc) |
| 6,4-7,15 | #128-#143 | ralentissement : le boxeur continue en petit, la caméra recule, les effets s'éteignent (mesuré : luminance qui descend doucement de 67 à 56 sur 0,65 s) | plan plus large, moins de lumière |
| 7,2-8,25 | #144-#165 | **pose tenue en déplacement** : même silhouette (accroupi, buste ~45°, gants hauts) ~1 s, avec des **lignes de vitesse horizontales** blanches qui défilent partout | la caméra suit latéralement |
| 8,3-8,45 | #166-#169 | blanc (8,3-8,45, luminance 249 → 233), puis l'uppercut final dans une gerbe rouge | coupe cachée dans le blanc |
| 8,5-9,55 | #170-#191 | **tunnel** : lignes radiales noires et blanches + anneaux concentriques, le boxeur petit au centre (il fonce dans l'axe) | caméra derrière, dans l'axe |
| 9,6-9,85 | #192-#197 | retour caméra de jeu de dos ; il sort de sa pose basse et revient en garde debout | caméra de jeu |
| 9,85-11,15 | #197-#223 | **debout, immobile, aura blanche légère**, un anneau qui se dissipe au loin ; le mannequin a disparu ; à 10,8 s (#216) un point blanc minuscule en haut du cadre (je ne peux pas confirmer que c'est le mannequin) | fixe |

### Ce que je comprends

- **Le blanc sert de rideau de coupe** (vu, 4 fois) : chaque changement
  d'angle dans la série de coups tombe DANS le flash blanc. Le spectateur
  croit voir un seul flux violent ; en réalité ce sont des plans différents
  raccordés par un blanc d'une image. (déduit) C'est plus fort que ce que
  le cerveau avait noté (« BLANC total à 1,4 / 5,0 / 5,8 / 8,4 ») : il n'y
  a pas 4 blancs mais **au moins 11** (2 majeurs + 9 dans la série) ; les
  4 notés sont les plus longs.
- **Rythme de la série** (mesuré) : période ~0,25-0,3 s = 5-6 images à
  20 i/s. Par cycle : 1 image blanche + 1 image qui s'éteint + 2-3 images
  lisibles. C'est un métronome : le spectateur finit par l'anticiper, et
  le blanc plus long (8,3) + le tunnel cassent ce métronome pour le final.
- **Hiérarchie des tenues** : 0,7 s de pose basse tenue AVANT la série
  (3,5-4,2) = la tension ; 1 s de pose tenue en déplacement APRÈS la série
  (7,2-8,25) = la deuxième tension ; puis l'uppercut. **Deux montées**,
  chacune préparée par une pose tenue. (déduit)
- **Le corps n'a PAS besoin de poses variées pour lire la vitesse** : la
  silhouette tenue + les lignes de vitesse + la caméra qui suit suffisent.
- **La fin** : debout, immobile, 1,3 s, la victime absente. La consequence
  se lit par l'ABSENCE du mannequin (vu : il était au centre à 0-1,35 s,
  il n'y est plus à 9,85-11,15).

### Surprises
- Je croyais (cerveau) que les esquives étaient « lues par des traînées
  bleues » : oui, mais la traînée bleue REMPLACE le corps (on voit une masse
  bleue floue à l'endroit du buste, #36-#47), elle ne le suit pas. C'est un
  smear coloré, pas une particule.
- Les bandes noires cinéma (letterbox) apparaissent AVEC le premier blanc et
  disparaissent au retour de la caméra de jeu (vu : #28 sans barres → #33
  avec ; #192 sans). Elles signalent « cinématique » vs « jeu ».

## 4. Rafale « gatling » (a0341700) — 206 images à 30 ms, 6,24 s

### Déroulé vu
| temps | images | ce qui se passe |
|---|---|---|
| 0-0,15 | #0-#5 | perso de dos (chapeau de paille dans le dos, bras roses), il se tord, un bras part sur le côté |
| 0,18-0,48 | #6-#16 | **pose d'armé tenue ~0,3 s** : accroupi, les DEUX bras écartés sur les côtés, coudes pliés, poings en l'air (silhouette en « W » / cactus). Quasi identique de #7 à #16 (vu) |
| 0,52-0,61 | #17-#20 | changement brusque de silhouette : jambes tendues, le chapeau de paille apparaît en entier au centre (je lis : la tête/le buste basculent vers l'avant, vers la cible ; lecture de dos, confiance moyenne), les bras passent DEVANT, cachés par le dos |
| 0,64-3,97 | #21-#131 | **la rafale** : une masse blanche d'éclats + des BRAS FANTÔMES roses semi-transparents qui apparaissent à gauche, à droite et au-dessus des épaules, différents à chaque image (vu #24-#31, #36-#41, #64-#79). Le corps, lui, ne bouge presque pas : jambes fixes, dos fixe. Mesuré : luminance dans la zone au-dessus du perso qui monte de 86 à ~125-138 et reste en plateau 0,75-3,9 s |
| 3,97-4,09 | #131-#135 | fin : le buste tourne (chapeau passe sur le côté), un bras descend en avant-bas : **pose de fin** 3/4, penché, bras tendu |
| 4,09-5,55 | #135-#183 | **tenue de la pose de fin ~1,5 s** ; des anneaux de fumée en grappes flottent autour du mannequin puis s'effacent (4,1-4,6), le mannequin reste immobile, blanchi (vu #146-#182) |
| 5,58-5,7 | #184-#188 | **réaction DIFFÉRÉE** : le mannequin devient BLANC (1 image, #184-#185) puis s'envole au loin (#186 plus petit, #188 minuscule) |
| 5,7-6,21 | #188-#205 | le mannequin minuscule à l'horizon ; l'attaquant toujours dans sa pose de fin |

### Ce que je comprends
- **Correction de ce que le cerveau disait** : les notes (lot 3) disent
  « puis des anneaux de fumée (4,1-4,4 s) et retour à la garde ». Vu : il
  N'y a PAS de retour à la garde dans la GIF. L'attaquant **tient sa pose
  de fin ~2,1 s** (4,09 → 6,21, fin de la GIF), et la victime part avec
  **1,5 s de retard** sur le dernier coup (5,58 s). C'est le plus gros
  apprentissage de cette GIF.
- **Le « silence » entre le dernier coup et la conséquence** (1,5 s de
  fumée qui s'efface, rien ne bouge) est la même idée que la pause 0,3 s
  d'aafdc91d et que « Omae wa mou shindeiru » : la conséquence arrive
  QUAND LE SPECTATEUR NE L'ATTEND PLUS. (déduit)
- **Structure en 3 temps du corps** : armé en W tenu 0,3 s → éclatement
  (0,1 s) → rafale où le corps est un socle immobile et où SEULS les effets
  bougent (3,3 s) → pose de fin tenue. Le corps donne 2 poses ; la rafale
  est un effet, pas une animation de bras.
- **De dos** : les bras fantômes dépassent de la silhouette (à gauche, à
  droite, au-dessus) : c'est ce qui rend la rafale lisible alors que les
  vrais bras sont cachés par le dos (déjà noté par le cerveau, je confirme,
  vu #24-#31).

## 5. Perso orange, caméra de jeu lointaine (aafdc91d) — 128 images, 4,23 s

### Déroulé vu
| temps | images | ce qui se passe |
|---|---|---|
| 0-0,24 | #0-#7 | attaquant (orange) de dos près du mannequin, immobile |
| 0,27-0,6 | #8-#18 | **coup 1** : éclats blancs + fumée au sol + un anneau au sol qui s'étale |
| 0,63-1,08 | #19-#33 | **silence ~0,45 s** : la fumée retombe, il reste une bulle translucide autour des deux ; l'attaquant bouge à peine (vu) |
| 1,11-1,6 | #34-#48 | **coup 2, plus gros** : gerbe blanche plus large (#35-#37), puis éclats ROUGES, lames blanches, anneaux concentriques qui s'élargissent (#40-#47) |
| 1,65-4,2 | #50-#127 | l'attaquant garde la même silhouette (vu : de #60 à #127, **~2,5 s**) ; la victime part AU LOIN (elle remonte dans le cadre vers la ligne d'horizon en rétrécissant : je ne peux pas dire si elle monte ou si elle recule, la caméra regarde à plat), entourée d'un anneau blanc qui la suit (1,98-2,82), devient un point, **flashe en blanc** (3,3-3,48, #100-#105), puis reste un point gris |

### Ce que je comprends
- **Escalade en 2 temps avec un silence au milieu** : coup 1 petit
  (blanc + fumée), 0,45 s de rien, coup 2 gros (blanc + ROUGE + anneaux).
  Le silence mesure la différence entre les deux. (la relecture 09-25
  disait « pause 0,3 s » ; je compte 0,45 s de #19 à #33 : 15 images à
  30 ms. Écart de lecture, pas de fond.)
- **La couleur est réservée au coup qui compte** : coup 1 = blanc/gris
  seulement ; coup 2 = blanc + rouge. La hiérarchie se lit à la couleur.
- **L'attaquant ne bouge plus après le coup 2 (2,5 s)** : c'est encore une
  pose de fin tenue pendant que la conséquence (la victime) voyage.
- **Deuxième signal sur la victime** : l'anneau qui l'accompagne pendant
  qu'elle s'éloigne (le cerveau notait « envoyée TRÈS haut » : vu, elle
  monte DANS LE CADRE, mais c'est aussi ce que fait un objet qui recule vers
  l'horizon ; je ne tranche pas), puis un flash blanc tout en haut (3,3 s) : l'œil suit la
  victime jusqu'au bout, même quand elle fait 5 pixels. (déduit : sans ce
  flash, on la perdrait.)

## 6. Mythra — saisie + projection (6d3be6e1) — 67 images, 4,19 s

### Déroulé vu
| temps | images | ce qui se passe |
|---|---|---|
| 0-0,31 | #0-#5 | Tobi (noir, cheveux roux longs) avance vers Shinso ; **course basse, buste penché ~45°, une main devant** ; la caméra (3e personne du joueur) glisse légèrement |
| 0,38-0,56 | #6-#9 | il se redresse, bras tendu en avant : **éclat blanc à la main** (#7-#9 ≈ 0,19 s), petite traînée derrière le bras (#9) |
| 0,63-0,94 | #10-#15 | contact : les deux corps se collent, Tobi passe DERRIÈRE Shinso, l'enlace, les deux s'accroupissent ensemble |
| 1,0-1,31 | #16-#21 | **soulèvement en arc** : Shinso est basculé à l'horizontale (#17), puis porté AU-DESSUS de la tête de Tobi (#18-#20, Tobi debout de face, bras levés), puis redescend sur ses épaules (#21-#22). Tobi reste campé, jambes écartées, genoux pliés = socle |
| 1,38-2,0 | #22-#32 | les deux corps en boule au sol, Tobi agenouillé sur Shinso ; mouvement faible (tenue ~0,6 s d'un « nœud ») |
| 2,06-2,31 | #33-#37 | Tobi se relève en tenant Shinso, le soulève contre lui |
| 2,38 | #38 | **projection** : Shinso est à plat au sol à gauche, Tobi en bas à genoux |
| 2,44-2,75 | #39-#44 | **impact au sol** : grande forme ROUGE plate (#39-#43, rouge pur) : sur #42-#43 elle semble reprendre la SILHOUETTE de la victime (une copie rouge du corps à plat ; déduit, confiance moyenne), anneau blanc au sol qui s'élargit, fumée blanche, particules sombres qui montent (#43-#47) |
| 2,81-3,69 | #45-#59 | **tenue ~0,9 s** : Shinso au sol, Tobi accroupi à côté, regarde la victime ; tache sombre (brûlure) sur le sol, particules qui retombent ; la caméra dérive très lentement vers la droite |
| 3,75-4,13 | #60-#66 | Tobi se relève et commence à repartir (course basse) |

### Ce que je comprends
- **Le « socle »** : pendant tout le soulèvement, Tobi ne fait presque
  rien de spectaculaire : jambes écartées, genoux pliés, bassin bas. C'est
  la VICTIME qui décrit le grand arc. (déduit) Quand deux corps agissent,
  un des deux est le point fixe qui rend l'arc de l'autre lisible.
- **Le signal de saisie** (éclat blanc à la main, 0,19 s) est l'équivalent
  du « flash d'anticipation » des jeux de combat : il dit « c'est une prise
  » avant que les corps ne se touchent.
- **La tenue finale regarde la victime** : la tête de Tobi est tournée
  vers Shinso pendant 0,9 s. La pose de fin est une pose d'ATTENTION
  (regard), pas une pose de victoire.
- **La tache rouge est une forme plate posée sur le sol**, pas des
  particules en l'air : elle se lit en caméra de jeu parce qu'elle est
  grande et plate. (vu #39-#43)

## 7. Mii Smash, coup chargé avec hitbox (4e337114) — 67 images à 130 ms, 8,71 s

Attention (mesuré) : 7,7 i/s seulement. Chaque image = 130 ms. C'est
probablement un visualiseur de hitbox au ralenti / image par image (le
personnage est translucide, les hitbox sont des sphères rouges) : **je ne
peux pas savoir si ce timing est celui du jeu**. Je lis donc surtout
l'ORDRE des poses et les PROPORTIONS entre phases, pas les durées absolues.

| images | temps GIF | pose (vu, zoom `z_cles.png`) |
|---|---|---|
| #0-#9 | 0-1,17 | **charge tenue** : accroupi large, genoux fléchis, un bras levé plié près de la tête (poing haut arrière), l'autre bras tendu vers l'avant ouvert. Quasi identique 10 images |
| #10-#14 | 1,3-1,82 | **anticipation / armé** : le bassin recule et descend, le buste se tourne (on voit l'arrière de l'épaule), la jambe avant s'allonge en fente, le poing de frappe part vers l'arrière de la hanche |
| #15 | 1,95 | **dernière image avant la frappe** : buste enroulé au maximum, épaule de frappe cachée derrière le torse, trait violet déjà visible (CORRIGÉ à la reprise : ce trait reste collé sur la poitrine de #15 à #40, même pendant le retour ; c'est donc probablement un élément du visualiseur, pas un smear de trajectoire — voir « Reprise ») |
| #16-#17 | 2,08-2,21 | **frappe** : bras tendu à l'horizontale, 3 sphères rouges alignées sur le bras (hitbox active = 2 images) ; le passage #15 → #16 est UNE seule image : armé → extension totale |
| #18-#35 | 2,34-4,55 | **extension tenue** : bras tendu à l'horizontale, accroupi large (le torse reste plutôt droit, légèrement penché : je corrige la relecture 09-25 qui disait « torse presque horizontal ») ; 18 images quasi identiques (le bras ne se replie pas) ; trait violet persistant |
| #36-#39 | 4,68-5,07 | le bras se replie lentement, le buste se redresse |
| #40-#54 | 5,2-7,02 | le corps pivote (on passe de 3/4 dos à profil), les poings remontent devant le visage |
| #55-#66 | 7,15-8,58 | retour à la garde de face, tenue |

### Ce que je comprends
- **Proportions** (mesuré en images) : charge 10 → armé 6 → frappe 1 (+1
  hitbox) → extension tenue 18 → retour 31. **La frappe est 1 image sur
  67.** Même si le timing absolu est ralenti, la proportion est parlante :
  tout le coup est construit AUTOUR d'une image unique.
- **L'armé enroule le TORSE, pas le bras** (vu #12-#15) : l'épaule de frappe
  disparaît derrière le torse. Le bras suit, il ne mène pas.
- **La charge est une pose OUVERTE** (bras écartés, #0-#9) ; l'armé est une
  pose FERMÉE (enroulée, #15) ; la frappe est une pose OUVERTE et LONGUE
  (#16). Ouvert → fermé → ouvert-étiré : c'est le contraste qui fait le
  coup, pas l'amplitude d'un seul membre. (déduit)
- **L'extension est tenue plus longtemps que tout le reste** (18 images)
  et le retour est encore plus long (31) : chez Sakurai, la « punition »
  du coup chargé (endlag) est aussi la vitrine de la pose.

## 8. « Coup chapeau » (946bd286, Anim @LeftRight2601, VFX @MuichimeRBXL) — 151 images, 10,07 s

### Déroulé vu
| temps | images | ce qui se passe |
|---|---|---|
| 0-0,13 | #0-#2 | attaquant (chapeau haut-de-forme, batte) plié, dos rond, tête basse, le haut du corps penché À L'OPPOSÉ de la victime (noire, croix, à ~2 corps à droite) |
| 0,2 | #3 | **renversement** : il se redresse et se tord, batte dans le dos, un bras qui monte |
| 0,27-0,4 | #4-#6 | bras levé au-dessus de la tête, **éclat bleu-blanc au poing** (#5-#6), le corps passe en arc arrière |
| 0,47 | #7 | **carte encre 1 image** : hachures radiales noires sur blanc (le contact) |
| 0,53-1,0 | #8-#15 | **caméra basse, le perso en fente horizontale** (jambe arrière tendue au ras du sol, buste à plat, batte horizontale) ; une onde de choc (arcs blancs verticaux, poussière) passe ; la victime a disparu du cadre après #8 |
| 1,07-2,07 | #16-#31 | **contre-plongée vers le ciel, perso en amorce en bas-gauche, TENU ~1 s** : on regarde un débris (la victime ? une dalle) monter dans le ciel bleu. Le perso ne bouge presque pas (vu #17-#28) |
| 2,13-2,2 | #32-#33 | le bras/la batte se lèvent, éclat bleu-blanc qui gicle vers le ciel |
| 2,27-2,8 | #34-#42 | **9 cartes d'UNE image chacune** (≈ 65 ms) : hachures, éclat étoilé noir/blanc, cible JAUNE/ROUGE sur noir + crâne violet (#36-#37 : 2 images), cible noire sur blanc (#38-#39 : 2 images), gribouillis, coup de pinceau blanc sur noir, radial au trait. Polarité alternée à presque chaque image |
| 2,87-8,2 | #43-#123 | **conséquence-spectacle ~5,3 s** : explosion de dalles en contre-plongée ; ~0,6 s de silence NOIR (#53-#54 : 2 images noires = 0,13 s ; je me corrige : court) ; puis tourbillon de débris dans le ciel bleu, la victime minuscule qui monte au milieu (#99-#111), assombrissement progressif vers un bleu nuit violet avec éclairs (#112-#123) |
| 8,27-8,4 | #124-#126 | **noir 3 images (0,2 s)** |
| 8,47-9,53 | #127-#143 | nouveau plan : un perso BLEU en chute, et de **gigantesques poings rouges** qui arrivent en rafale (tunnel de lignes de vitesse rouges et blanches). Je ne sais pas si c'est la suite du même coup ou un 2e clip collé dans la GIF (l'avatar n'est plus le même) |
| 9,6-10,0 | #144-#150 | noir |

### Ce que je comprends
- **L'anticipation est un contre-mouvement complet** (#0 → #3) : plié et
  penché à l'opposé de la cible, il se déroule d'un coup (#3) et le bras
  monte (#4-#6) pour frapper vers le HAUT. La préparation va vers le bas et
  loin de la cible, le coup vers le haut. (vu ; « loin de la cible » est ma
  lecture de l'angle, confiance moyenne)
- **L'impact est une carte d'UNE image placée entre deux poses** (#7) :
  on ne voit jamais le contact ; avant la carte, bras levé ; après la
  carte, il est déjà en fente horizontale, le coup fini. La carte EST le
  contact. C'est la « coupe dans l'action » (IMPACT HAVEN), ici à 1 image.
- **La deuxième montée arrive après une tenue d'1 s** (1,07-2,07) où le
  perso regarde son œuvre monter. Puis un 2e coup très court (#32-#33) et
  la rafale de 9 cartes. **Escalade : 1 carte → tenue → 9 cartes.** Même
  structure que aafdc91d (petit coup, silence, gros coup), en plus long.
- **Le corps n'occupe que ~2,2 s sur 10** (0-1,0 puis 1,07-2,2 en amorce).
  Le reste (5,3 s) est la conséquence : débris, ciel, assombrissement,
  la victime minuscule.
- **Couleur réservée** : tout est gris/bleu/blanc SAUF 2 cartes (#36-#37,
  jaune + rouge + violet). Ce sont les 2 seules images tenues 2 fois
  dans la rafale de cartes. (vu) Le moment coloré est le « cœur » de
  l'impact.

## 9. Double jab R6 (3ee5a405) — 25 images, 1,56 s (caméra fixe de face, 3/4)

| images | temps | pose (vu) |
|---|---|---|
| #0-#2 | 0-0,13 | garde : poings jaunes écartés à hauteur d'épaules, coudes ouverts, genoux fléchis |
| #3 | 0,19 | armé : le buste tourne, un poing passe devant le visage, l'autre recule |
| #4-#8 | 0,25-0,5 | **jab 1 tendu vers la caméra-côté**, main de l'autre bras avec un petit éclat blanc à la hanche (1er plan) ; tête et buste penchés dans le coup ; **tenu ~0,25 s** (#4-#8) |
| #9 | 0,56 | **retour à la garde en 1 image** |
| #10-#13 | 0,63-0,81 | re-armé : tourne, re-garde |
| #14-#18 | 0,88-1,13 | **jab 2**, même pose que jab 1, tenue ~0,25 s |
| #19-#24 | 1,19-1,5 | retour garde, tenue |

- **Mesuré** (différence entre images, caméra fixe) : aucune image quasi
  immobile pendant les jabs (différence 4,5-14) → la « tenue » du jab est
  en fait un **mouvement résiduel lent** (le corps continue de dériver un
  peu), pas un gel. Seules #23-#24 sont presque immobiles (1,5 et 0,6).
- **Déduit** : le jab est « aller rapide / tenue vivante / retour très
  rapide (1 image) ». Le retour est plus rapide que l'aller : c'est ce qui
  garde le rythme sec (l'œil n'a pas le temps de lire le retour, il lit
  les deux extensions).
- Le cerveau notait « poing de la garde à l'extension en ~4 f (-6 → -2),
  extension tenue 10+ f » : je vois l'aller en 1-2 images GIF (≈ 60-130
  ms) et la tenue ≈ 0,25 s. Compatible.

## 10. M1 rue de nuit (449345ad) — 46 images, 2,87 s (caméra de jeu, de face)

| coup | images (flash) | effets (vu) |
|---|---|---|
| 1 | #4-#7 (0,25-0,44) | éclat blanc au poing (#4), puis anneau blanc autour du bras (#5-#6) |
| 2 | #13-#16 (0,81-1,0) | éclat (#13), anneau + trait (#14-#16) |
| 3 | #23-#25 (1,44-1,56) | gros éclat étoilé (#23) puis **arc de coupe** blanc (#24-#25, un vrai smear en croissant) |
| 4 | #32-#34 (2,0-2,13) | coup BAS (poing vers le sol), éclat + DOUBLE anneau |
| fin | #35-#45 (2,19-2,81) | garde neutre, léger rebond |

- **Mesuré** : pics de différence à #5-#6 (11), #13-#14 (13), #23-#24 (11),
  #31-#33 (9-11) → période ≈ 0,56-0,62 s par coup, régulière.
- **Vu** : entre les coups le perso NE revient PAS à la garde complète : il
  enchaîne en tournant le buste (#8-#12, #17-#22), le bras de la frappe
  suivante recule pendant que l'autre revient. Le M1 est une vague
  continue gauche-droite, le 4e coup casse la vague (vers le bas).
- **Hiérarchie par l'effet** : coups 1-2 = éclat + anneau simple ;
  coup 3 = éclat plus gros + smear ; coup 4 = double anneau. Le dernier
  coup d'une chaîne est signalé par la forme de l'effet, pas par sa taille
  seule.

## 11. Goku poing levé (656d965b) — 40 images, 2 s, anime 2D

- **Vu** : UNE pose tenue 2 s : jambes écartées, poing droit levé tendu vers
  le ciel, poing gauche à la hanche, tête vers le haut, cheveux SSJ3
  jusqu'aux genoux. Ciel de nuages avec rayons de lumière.
- **Mesuré** : décalage d'image (corrélation de phase) entre #0 et
  #3/#9/#19/#39 = 0 pixel → **la caméra est fixe**, le personnage ne se
  déplace pas. Différences image-à-image dans la zone perso : un pic toutes
  les 3 images (15,4 / 14,1 / 15,3 / 16,8…) et ~3-5 entre deux → **le dessin
  est animé « en 3 »** (une nouvelle image tous les 3 × 50 ms ≈ 0,15 s,
  mais la GIF à 20 i/s duplique). Les cheveux bougent le plus (pics 17-22),
  les jambes le moins (10-12), le ciel très peu (5-6).
- **Ce que je comprends (déduit)** : la « tenue » d'une pose d'invocation
  n'est pas une image figée : le CORPS est fixe, mais les cheveux, le bord
  des vêtements et la lumière vibrent (boil). Le mouvement est confié aux
  parties « secondaires », la silhouette reste tenue. En R6 sans cheveux ni
  cape, cette vibration devrait venir d'autre chose : lumière, aura,
  particules, micro-tremblement.
- **Surprise** : je m'attendais à une montée (le poing qui se lève) ; la
  GIF ne montre QUE la tenue. La charge est entièrement dans la tenue.

## 12. Exemple Blender, projection à deux (37d7971a) — 64 images, 3,2 s

| images | temps | ce qui se passe (vu, rig coloré FRONT/BACK/L/R) |
|---|---|---|
| #0-#2 | 0-0,1 | attaquant (vert/bleu, à gauche) accroupi, victime (rouge/jaune) debout, 2 m devant |
| #3-#9 | 0,15-0,45 | l'attaquant fonce BAS, se relève en tendant les bras vers la victime |
| #10-#19 | 0,5-0,95 | clinch : il passe sous/contre la victime, les corps s'emmêlent, la victime est soulevée (on voit son dos BACK) |
| #20-#35 | 1,0-1,75 | rotation : la victime tourne au-dessus/autour de l'attaquant (les étiquettes FRONT/BACK défilent) |
| #36-#42 | 1,8-2,1 | séparation : la victime part vers la droite et s'écrase à plat |
| #43-#62 | 2,15-3,1 | **tenue ~0,9 s** : attaquant debout de profil, victime à plat |
| #63 | 3,15 | boucle (retour image 0) |

- **Mesuré** : différence image-à-image 6-11 en continu de #8 à #41 (aucune
  tenue pendant 1,7 s), puis décroissance 3,5 → 0,3 de #43 à #62. C'est la
  même forme que Mythra : **un flux continu, puis une tenue longue sur le
  résultat**.
- **Déduit** : dans une prise, le mouvement ne se découpe pas en poses
  tenues ; c'est la RÉCEPTION qui est tenue. L'attaquant se REDRESSE
  pendant que la victime tombe (opposition verticale).

## 13. Combo R6 « front » Moon Animator (fa7b867c) — 97 images, 3,23 s, caméra fixe

| images | temps | pose (vu) | mesure (diff.) |
|---|---|---|---|
| #0-#16 | 0-0,53 | idle, face (FRONT), petite respiration | 0,1-0,4 (quasi immobile) |
| #17-#19 | 0,57-0,63 | **rotation ~180° en 2 images** : FRONT → BACK, genou gauche levé, bras droit armé en haut | 3,9-6,9 |
| #20-#22 | 0,67-0,73 | armé tenu de dos (BACK), bras en L au-dessus | 1,7-2,9 |
| #23-#25 | 0,77-0,83 | frappe : hitbox rouge, le perso de PROFIL, bras tendu | 3,3-4,7 |
| #26-#31 | 0,87-1,03 | **tenue** du profil, bras tendu | 1,0-1,2 |
| #32-#36 | 1,07-1,2 | re-rotation vers BACK, bras en L de l'autre côté (2e armé) | 1,3-4,9 |
| #37-#42 | 1,23-1,4 | frappe 2 (hitbox) : **pivot jusqu'à FRONT**, poing en uppercut au-dessus de la tête | 3,6-7,1, puis 0,7 à #42 |
| #43-#46 | 1,43-1,53 | tenue, poing levé | 1,2-1,8 |
| #47-#61 | 1,57-2,03 | toupie : le corps tourne (FRONT→profil→R→FRONT) en se ramassant, les bras croisés devant | 2,2-4,9 continu |
| #62-#67 | 2,07-2,23 | **frappe au sol** : grande hitbox rouge plate, le perso plié à 90°, poings vers le sol | 5,5-8,9 (le max) |
| #68-#76 | 2,27-2,53 | tenue pliée au sol | 0,1-2,5 |
| #77-#86 | 2,57-2,87 | relèvement continu vers l'idle | ~4,2 constant |
| #87-#96 | 2,9-3,17 | idle | 0,1-0,2 |

- **Ce que je comprends (où l'animateur place le rig)** :
  1. chaque attaque commence par une **rotation du torse ENTIER** (pas du
     bras) jusqu'à montrer le dos : l'armé est un 180° du corps ;
  2. la frappe **déroule** ce 180° et se termine de profil ou de face ;
  3. chaque frappe est suivie d'une tenue de 0,1-0,17 s (#26-#31, #42-#46,
     #68-#76) ;
  4. **les trois attaques vont dans trois directions** : horizontale
     (profil), verticale vers le haut (uppercut), verticale vers le bas
     (au sol, le plus fort mouvement mesuré). La variété est dans la
     DIRECTION, et le dernier coup est le plus ample.
- **Mesuré** : le mouvement le plus violent (8,9) est sur la frappe au sol,
  le coup final. L'amplitude monte d'un coup à l'autre (6,9 → 7,1 → 8,9).

## Annexe : planche de clés « Ultimate1 » du fichier TSB (tentative de pont)

`planche_cles.py --nom Ultimate1` sur `b64ecce0-tsb_anim.rbxm` : 129 clés,
10,02 s. La durée est presque celle de la GIF Serious Punch (10,07 s), d'où
l'envie de les relier. **Mais les poses ne correspondent pas** à ce que je
vois dans la GIF : pas de genou haut, pas de fente basse, le perso reste
debout avec des bras qui tournent devant la poitrine (planche i256-i434).
**Déduit : ce n'est probablement PAS l'animation du Serious Punch** (ou
alors le déplacement de la GIF vient d'ailleurs). Je ne m'en sers pas comme
preuve. Planche : `…/frames/C3_gifs/ult1.png`.

---

# PARTIE 2 — Les coups chargés comparés : comment chacun construit la TENSION puis la LIBÉRATION

(Consigne : ne pas résoudre notre coup, observer.)

| | Serious Punch TSB / SP2 | Mii Smash | Goku | coup chapeau | Ippo |
|---|---|---|---|---|---|
| **pose de charge** | neutre, debout, bras tombant (1,07 s) puis fente basse tenue (0,75 s) puis genou haut dos-caméra (0,5 s) | accroupi large, bras ouverts, poing haut (10 images / 1,3 s GIF) | poing au ciel, jambes écartées (2 s) | penché en avant, tête basse (0,13 s) | accroupi très bas, buste 45°, gants au visage (0,7 s + 1 s) |
| **qui bouge pendant la tenue** | la CAMÉRA (poussée, orbite, glissement dans la fumée) | rien (visualiseur) | les cheveux / la lumière (boil « en 3 ») | rien (trop court) | le décor (lignes de vitesse), la caméra qui suit |
| **armé** | rotation du corps : dos → face (genou haut) | enroulement du TORSE (épaule cachée) | — (pas montré) | renversement avant → arrière | — (esquives) |
| **libération** | 3 images de déroulé, vers l'objectif | 1 image (#15 → #16) | — | 1 image cachée derrière une carte | 1-2 images, cachées dans un flash |
| **contact** | jamais montré (fumée → contre-champ 1 image → cartes) | montré par la hitbox (outil, pas mise en scène) | — | jamais montré (carte #7) | caché dans le blanc |
| **après** | pose accroupie de fin tenue 2,7 s, champ de roches | extension tenue 18 im., retour 31 im. | — | 1 s de tenue puis 2e coup + 9 cartes + 5,3 s de débris | pose tenue 1,3 s, victime disparue |

## Ce que je vois de commun (déduit, à partir des lignes ci-dessus)

1. **La libération est TOUJOURS la chose la plus courte** (1 à 3 images),
   et elle est souvent INVISIBLE : cachée derrière une carte, un blanc, une
   fumée, ou simplement pas dessinée. Le spectateur ne voit pas le coup ;
   il voit l'AVANT et l'APRÈS, et son cerveau fabrique le coup.
2. **La tension n'est jamais une pose seule**. Elle est portée par
   « quelque chose qui bouge pendant que le corps ne bouge pas » : caméra
   (TSB), cheveux/lumière (Goku), décor qui défile (Ippo). Un corps figé
   dans un monde figé ne crée pas de tension ; un corps figé dans un monde
   qui bouge, oui.
3. **La tension se construit en PLUSIEURS paliers**, pas en une rampe :
   TSB = calme → saut (rupture) → approche tenue → armé tenu → frappe.
   Ippo = série → pose tenue → série → pose tenue en déplacement → final.
   Coup chapeau = coup 1 → tenue 1 s → coup 2. Chaque palier a sa propre
   tenue.
4. **L'armé tourne le corps entier** (TSB : dos à la caméra ; combo Moon :
   BACK ; Mii : épaule cachée). Aucun des coups forts n'arme seulement le
   bras. La direction de l'armé est souvent OPPOSÉE à celle du coup (coup
   chapeau : penché en avant pour frapper vers le haut).
5. **La conséquence dure plus longtemps que tout le reste réuni** :
   TSB 2,7 s de pose de fin tenue contre 0,2 s de frappe ; gatling 2,1 s de pose
   de fin + victime qui part 1,5 s APRÈS ; aafdc91d 2,5 s ; coup chapeau
   5,3 s ; Mii 18 + 31 images contre 1.

## Ce qui les distingue

- TSB est le seul où **la charge commence par du CALME** (1,07 s debout,
  bras ballants). Le calme est la première marche : l'indifférence du
  personnage EST la tension (déduit : c'est Saitama, l'ennui est le
  caractère).
- Goku est le seul où **la charge est la scène entière** (pas de frappe).
- Mii est le seul qu'on voit sans mise en scène : sans caméra, sans effets,
  il faut que la pose seule porte (ouvert → fermé → ouvert-étiré), et la
  proportion 1 image de frappe / 49 images de tenue + retour y est la plus
  nue.

---

# PARTIE 3 — Grands enseignements (apprentissages, pas règles)

## A. Sur le temps
- **A1. Ici, les animateurs tiennent la pose de FIN plus longtemps que la
  pose d'armé.** Gatling : armé 0,3 s, fin 2,1 s. aafdc91d : fin 2,5 s.
  Mii : extension 18 images. TSB : pose accroupie de fin 2,7 s. (vu + mesuré)
- **A2. La conséquence arrive EN RETARD.** Gatling : la victime part 1,5 s
  après le dernier coup (vu #184-#188). aafdc91d : la victime flashe 2 s
  après le coup. Le retard laisse le spectateur croire que c'est fini,
  puis le surprend. (vu)
- **A3. Un silence sépare deux montées** (aafdc91d 0,45 s ; coup chapeau
  1 s ; Ippo 0,7 s de pose tenue entre deux séries). (mesuré en images)
- **A4. Le retour est plus rapide que l'aller** (double jab : retour en 1
  image). (vu)
- **A5. Une tenue est rarement un gel** : double jab = dérive lente
  (mesuré), Goku = boil en 3 (mesuré), TSB = caméra qui tourne. Seules les
  vraies fins (idle Moon, conséquence Blender) descendent vers 0.

## B. Sur l'espace et le rig (où l'animateur pose les clés)
- **B1. L'armé se pose dans le TORSE, à ~180° du coup** (combo Moon : FRONT
  → BACK en 2 images ; TSB : dos caméra ; Mii : épaule cachée). La
  première clé à poser pour un coup fort serait donc la rotation du torse,
  le bras vient après. (vu ; l'ordre de pose est déduit)
- **B2. Varier la DIRECTION des coups** plutôt que leur force : combo Moon =
  horizontal / vers le haut / vers le bas. Le dernier est le plus ample
  (mesuré 6,9 → 7,1 → 8,9). M1 de nuit : 3 coups dans le même plan, le 4e
  vers le bas.
- **B3. Dans une prise à deux, un corps est le socle** (Mythra, Blender) :
  l'attaquant garde jambes écartées et bassin bas ; la victime fait l'arc.
  Et à la fin, **opposition verticale** : l'attaquant se relève pendant que
  la victime tombe.
- **B4. Ouvert → fermé → ouvert-étiré** (Mii) : la silhouette de la charge,
  de l'armé et de la frappe alternent l'ouverture. Le contraste
  d'ouverture fait le coup plus que l'amplitude d'un membre.
- **B5. Silhouette tenue en déplacement** (Ippo 1 s, TSB approche 0,75 s) :
  le corps ne bouge pas, c'est la position dans le monde qui bouge.

## C. Sur la caméra et le montage
- **C1. Le blanc (ou le noir) est un rideau de coupe** : Ippo change
  d'angle DANS chaque flash (au moins 11 fois). Coup chapeau : noir
  0,13-0,2 s avant un nouveau plan. TSB : blanc qui se dissout. (vu)
- **C2. Le corps lui-même sert de rideau** (TSB 0,33-1,8 s : bras qui
  couvre l'écran). (vu)
- **C3. Letterbox = « on est en cinématique »** (Ippo). (vu)
- **C4. La cible est parfois l'objectif** : TSB frappe VERS nous, puis UNE
  image de contre-champ remet la géographie. (vu)

## D. Sur les effets (au service de l'animation)
- **D1. La couleur est réservée au moment qui compte** : aafdc91d (rouge
  seulement au 2e coup), coup chapeau (jaune/rouge seulement sur 2 cartes
  tenues 2 images). (vu)
- **D2. Les effets remplacent les membres quand le corps est caché** :
  bras fantômes du gatling de dos, traînée bleue d'Ippo à la place du
  buste. (vu)
- **D3. La hiérarchie d'une chaîne se lit dans la FORME de l'effet** (M1 :
  anneau → anneau → smear → double anneau). (vu)
- **D4. Une tache au sol plate et grande** se lit en caméra de jeu
  (Mythra). (vu)

---

# PARTIE 4 — Ce que je saurais refaire en R6 (concret) et ce que je ne saurais pas

## Je saurais refaire (avec les poses et temps observés)
1. **Un combo de 3 coups type Moon (fa7b867c)**, à 30 i/s :
   - idle 16 images ;
   - coup 1 : torse +180° (FRONT→BACK) en 2 images, genou avant levé, bras
     droit en L au-dessus ; tenir 3 images ; déroulé jusqu'au profil en 3
     images, bras tendu horizontal ; tenir 5 images ;
   - coup 2 : re-rotation vers BACK en 4 images (bras gauche en L), déroulé
     jusqu'à FRONT avec uppercut au-dessus de la tête en 5 images ; tenir 4 ;
   - coup 3 : toupie ramassée 15 images, bras croisés devant ; frappe au sol
     en 5 images, torse plié ~90°, poings au sol ; tenir 9 ; relèvement 10 ;
     idle.
2. **Un double jab (3ee5a405)** : garde coudes ouverts ; armé 1 image
   (buste tourne) ; aller 1-2 images ; tenue ~0,25 s avec dérive lente du
   buste vers l'avant (pas un gel) ; retour 1 image ; re-armé 3-4 images ;
   2e jab identique.
3. **Une chaîne de M1 en vague (449345ad)** : période ~0,6 s, bras
   alternés, le buste tourne d'un côté à l'autre sans repasser par la
   garde ; 4e coup vers le bas.
4. **Une pose de fin tenue + conséquence différée (gatling)** : dernière
   frappe → pose 3/4 penchée bras tendu, tenue 1,5-2 s ; la victime blanchit
   1 image puis part.
5. **Une invocation tenue (Goku)** : jambes écartées, poing droit au ciel,
   gauche à la hanche ; corps FIXE ; tout le mouvement dans la lumière /
   particules / micro-tremblement renouvelé toutes les 3 images.
6. **La structure en paliers du Serious Punch**, comme découpage (calme
   1 s → rupture 0,2 s → approche tenue 0,75 s → armé genou haut dos-caméra
   0,5 s → déroulé 3 images → poing tenu 0,6 s → contact caché → fin tenue
   2,7 s).

## Je ne saurais pas (honnêtement)
- **Les angles exacts** des articulations dans ces GIF : je les ai vus en
  2D, souvent de loin, parfois de dos ; je n'ai rien mesuré en degrés. Les
  « ~45° », « ~90° », « 180° » sont des estimations à l'œil (statut vu,
  confiance moyenne).
- **La vraie courbe d'accélération** (easing) entre deux clés : les GIF à
  15-20 i/s sont trop pauvres pour la lire ; le Mii à 7,7 i/s encore moins.
- **Ce que fait le moteur vs l'anim** : dans les GIF de jeu (TSB, Ippo,
  gatling), je ne peux pas séparer ce qui est l'animation du rig, le
  déplacement scripté (root motion), le hitstop du moteur et la caméra.
- **Si le « Ultimate1 » du rbxm TSB est le Serious Punch** : les poses ne
  collent pas ; je ne l'utilise pas.
- **Le son** : les GIF n'en ont pas.
- **Le Mii** : impossible de savoir si le rythme de la GIF est celui du jeu.
- **La fin du coup chapeau** (8,47-9,53 : perso bleu, poings rouges géants) :
  je ne sais pas si c'est le même clip ou un autre collé.

---

# Couverture

Toutes les images des 13 GIF ont été extraites (1 374 images). Je les ai
regardées par planches de 16 (91 planches), avec des zooms image par image
sur les moments clés (départ, approche, armé, frappe de TSB ; charge du
Mii ; poses de fin d'aafdc91d ; prise de Blender ; gatling fin). Note d'honnêteté : pendant la session, une partie des lectures d'images a
été refusée par l'outil (limite de requêtes) ; j'ai RELU ensuite les
planches principales (TSB s01-s07 et s10, SP2 s01/s03/s05/s06, Ippo
s01-s03/s05/s06/s09-s11, gatling s01/s02/s09 + zoom fin, aafdc91d
s01-s03 + zoom fin, Mythra s01-s04, Mii s03/s04 + zoom clés, coup chapeau
toutes, combo Moon s01-s06, jab, M1, Goku, Blender) et corrigé mes notes
là où ma première rédaction s'appuyait sur des images non reçues (TSB
début et conséquence, gatling pose d'armé, aafdc91d trajectoire de la
victime, Mythra soulèvement, Mii torse, coup chapeau anticipation).
**Mise à jour de la reprise (2026-09-26)** : toutes les planches listées
ci-dessous comme « non relues » ont été relues à la reprise (TSB s08-s09,
SP2 s02/s04/s07, Ippo s04/s07/s08/s12-s14, gatling s03-s08 et s10-s13,
aafdc91d s04-s08, Mythra s05, Mii s01/s02/s05 + z_cles, combo Moon s07),
avec 4 mesures complémentaires (voir « PARTIE 5 — Reprise »). Il ne reste
**aucune planche non ouverte** sur les 13 GIF. Restent seulement lus en
planche 4×4 (pas image par image en plein format) : les zones où rien ne
change (tenues mesurées immobiles). Liste historique ci-dessous conservée :
Planches **non relues** après ce contrôle : TSB s08-s09 (7,47-9,53 s,
conséquence tenue : couverte par la mesure de différence d'image), SP2
s02/s04/s07, Ippo s04/s07/s08/s12-s14, gatling s03-s08/s10-s13,
aafdc91d s04-s08 (couverte par le zoom fin), Mythra s05, Mii s01/s02/s05
(couvertes par le zoom des clés).
Planches
**non ouvertes une à une** (couvertes seulement par mesure de luminance /
différence et par les planches voisines) : Ippo planches déjà relues mais
les zones 6,4-7,15 s lues plus vite ; gatling planches s04, s06-s08 (milieu
de la rafale, 1,4-3,5 s : j'ai vérifié par mesure que la luminance reste en
plateau et regardé s03/s05/s09-s13 autour) ; coup chapeau s07 (6,4-7,4 s,
débris) regardé, 7,47-8,2 regardé, rien d'autre ; combo Moon s07 (idle
final, mesuré immobile 0,1-0,2).

---

# PARTIE 5 — Reprise (2026-09-26) : les planches restantes, et ce qu'elles ajoutent

Rappels lancés avant la reprise : `rappel.py "pose de fin tenue"`,
`"blanc rideau de coupe"`, `"conséquence différée"` (--court). Le cerveau
renvoie surtout la fiche UN_SEUL_COUP, CARNET 4b.17 / §2 / 4b.2, l'étude
archive 09-25 §3 et la reconstruction Pew (tenue 4,7-4,8 s). Rien dans ces
rappels ne décrit les 4 points nouveaux ci-dessous (déduit de la lecture
des extraits courts ; je n'ai pas lu les rappels complets).

## R1. Ippo (58322fc4) : dans la série de coups, le GESTE lui-même est caché dans le blanc (vu, s07-s08)

- **Vu** #99 → #100-#101 (blanc, 2 images) → #102 : avant le blanc, gant
  gauche tendu vers la gauche de l'écran ; après, bras DROIT tendu vers la
  droite, avec un croissant rouge + des arcs blancs déjà en place. Même
  chose #105 → #106 (blanc rosé) → #107 (pose basse), #115 → #116 → #117,
  #120 → #121 → #122, #125 → #126 → #127.
- Entre deux blancs, le corps est **tenu** 3-4 images (#102-#105, #107-#109,
  #112-#115, #117-#120, #122-#125) pendant que les éclats rouges et les
  arcs blancs se dispersent.
- **Déduit** : un « coup » de la série = pose A tenue → blanc → pose B déjà
  à l'extension. On ne voit JAMAIS le bras voyager. Le blanc cache à la fois
  la coupe de caméra (déjà noté) ET le mouvement du membre. C'est la
  version extrême de « la libération est invisible » (Partie 2, point 1) :
  ici elle est invisible 9 fois de suite. Ce qui se lit, c'est la
  différence de silhouette entre deux poses tenues (gauche/droite,
  haut/bas) : les poses sont choisies CONTRASTÉES pour que le saut se lise.
- **Ce que je saurais refaire en R6** : une série « blanc-pose » : 2 images
  de blanc plein écran, puis une pose d'extension déjà atteinte (bras
  alterné, côté opposé à la précédente), tenue 3-4 images à 20 i/s
  (≈ 0,15-0,2 s) avec l'effet qui s'éteint ; période ~0,25 s (mesurée en
  Partie 1). Je ne saurais pas dire si le jeu fait ça par vraies coupes
  caméra ou par téléportation du rig : je ne vois que le résultat.

## R2. Ippo : le tunnel et la fin (vu, s12-s14)

- Tunnel #176-#191 : le boxeur est **fixe au centre du cadre, même taille**
  pendant 0,8 s ; ce qui change à CHAQUE image, ce sont les lignes radiales
  (redistribuées au hasard, les plus brillantes changent de côté) et les
  anneaux. **Déduit** : la vitesse est donnée par un bruit d'effet
  renouvelé à chaque image, pas par un déplacement du corps dans l'image.
- Sortie #192-#196 : de la pose basse à la garde debout en ~5 images
  (0,25 s), avec un anneau d'onde qui se dissipe derrière.
- Fin #197-#223 : debout, bras le long du corps, vapeur blanche sur les
  épaules. À #215-#217 (10,75-10,85 s) un point blanc scintille en haut au
  centre, là où le mannequin est parti (vu : 3 images, puis disparaît). Je
  maintiens la prudence de la Partie 1 : je ne peux pas prouver que c'est
  le mannequin, mais c'est à l'endroit de sa trajectoire (déduit : la
  « victime devenue étoile », comme aafdc91d R4).

## R3. Gatling (a0341700) : le milieu de la rafale et la conséquence (vu + mesuré, s03-s08, s10-s13)

- **Milieu de la rafale (vu, #32-#127)** : caméra fixe, chapeau et jambes
  immobiles à toutes les images ; seuls changent (a) la gerbe blanche, qui
  change de forme à chaque image, et (b) les bras fantômes roses, tantôt
  opaques et tendus (#61, #64 : bras tendu à gauche ; #93-#99 : à droite),
  tantôt transparents et flous.
- **Mesuré (grossier)** : masse de rose à gauche / à droite du chapeau,
  image par image (#15-#139). Le côté dominant ne change PAS à chaque image :
  il y a des **phases** d'environ 0,3-0,4 s (gauche dominant #48-#59 et
  #63-#71 ; droite dominant #93-#106 ; équilibré ailleurs). Mesure bruitée
  (le blanc des éclats se mêle au rose) : à prendre comme ordre de
  grandeur. **Déduit** : l'œil ne lit pas « gauche-droite-gauche » image
  par image mais des vagues ; la rafale a une respiration lente sous le
  bruit rapide.
- **Pose de fin (vu, #144-#205)** : le chapeau est passé dans le dos
  (pendu à l'épaule), la tête tournée, UN bras tendu vers l'avant-bas-
  droite ; tenue jusqu'à la fin de la GIF. Les anneaux de fumée (#144-#150)
  s'effacent en ~0,2 s.
- **Le mannequin pendant l'attente (vu + mesuré)** : il est déjà BLANCHI /
  translucide pendant toute la tenue (#152-#183 : gris-blanc, semi-
  transparent). Différence d'image dans sa zone : 0,3-0,6 (immobile) de
  #152 à #176, puis **3 petits sursauts** #177 (2,6), #179 (3,5), #182 (1,6)
  — un frisson de 0,2 s juste avant le départ. Puis #184 : blanc opaque et
  plus gros (1 image), #185-#187 : grosses différences (12,8 / 12,8 / 9,6),
  il file vers l'horizon et devient un point en ~5 images (≈ 0,15 s).
- **Déduit** : la conséquence différée n'est pas un simple « retard » :
  elle a sa propre petite anticipation (frisson 0,2 s → pop blanc 1 image →
  départ 0,15 s). C'est la structure anticipation → action appliquée à la
  VICTIME. Et le départ est ultra rapide comparé à l'attente (1,5 s
  d'attente, 0,15 s de vol) : contraste de temps maximal.

## R4. aafdc91d : la victime qu'on ne perd jamais des yeux (vu, s04-s08)

- #48-#63 : éclats rouges et arcs blancs qui s'éteignent autour de
  l'attaquant (~0,5 s) pendant que la victime monte au loin.
- #60-#85 : l'anneau autour de la victime **pulse** : petit (#60), grand
  (#64-#68), re-petit (#71-#72), re-grand (#76-#83), s'efface (#84-#86).
  Deux pulsations d'environ 0,35-0,4 s (compté en images à 30 ms).
- #96-#127 : la victime, minuscule à l'horizon, **blanchit
  progressivement** (#100-#111) puis redevient grise (#112-#127). Ce n'est
  pas un flash d'1 image : ≈ 0,35 s de montée, ≈ 0,4 s de descente (vu,
  estimé en images ; la mesure de luminance de la Partie 1 donnait 3,3-3,48
  pour le pic).
- **Déduit** : pour qu'un objet de quelques pixels reste lisible, on lui
  donne un signal qui VARIE lentement (pulsation, montée de blanc), pas un
  seul éclat bref qu'on raterait.
- L'attaquant, lui, est immobile de #64 à #127 (vu) : ~2 s.

## R5. Serious Punch TSB : la conséquence n'est pas totalement tenue (vu + mesuré, s08-s09)

- **Mesuré** (centre de la cape jaune, 6,6-10 s) : stable à ±5 px de #100
  à #115, puis **secousse** #116-#123 (7,73-8,2 s : le centre saute de
  y=213 à 257 puis 204, la taille apparente varie de 4 200 à 5 900 px) ;
  de nouveau stable à ±2 px de #127 à #141.
- **Vu** : pendant cette secousse, la silhouette ne change pas ; c'est le
  CADRE qui bouge (secousse de caméra, ou onde secondaire), et la fumée
  noire s'épaissit derrière les roches (#120-#127).
- **Vu** : le retour à debout se fait en 2 images (#141 accroupi → #142
  debout de dos → #143 debout droit). C'est presque une coupe : la fin
  n'est pas « jouée », le personnage rend la main au jeu.
- **Déduit** : même la « tenue » de fin a une deuxième vague ~1,1 s après
  le blanc (6,6 → 7,73 s). Ce rebond évite que la fin soit une image
  morte ; ensuite seulement vient le calme total (1,1 s) puis le retour
  sec au jeu.

## R6. Serious Punch 2 (772ee6b0) : trois précisions (vu, s02, s04, s07)

- s02 (1,07-2,07 s) : la pose neutre face caméra : bras droit tendu en
  avant-bas vers l'objectif, bras gauche ballant, genoux très légèrement
  fléchis ; la caméra recule de #16 à #20 puis s'arrête. Le perso ne bouge
  pas de #20 à #31 (vu).
- s04 (3,2-4,2 s) : à #49, des **blocs sombres flous** traversent le premier
  plan : des débris du sol arrachés par le saut qui passent devant
  l'objectif (lecture ; je ne vois pas d'où ils partent). Pendant la
  fente tenue (#50-#59), la caméra glisse autour de lui (on passe de
  3/4 dos à plus de profil), la silhouette reste. À #60-#63 la caméra se
  colle à lui au moment où il se redresse vers l'armé.
- s07 (6,4-7,13 s) : la conséquence commence caméra **collée** derrière
  lui (#96-#97) puis recule d'un coup au plan large (#98). Donc le « plan de
  conséquence » s'ouvre par un recul brusque, qui révèle l'ampleur du
  champ de roches.

## R7. Mii (4e337114) : l'armé AVANCE, et l'extension a un dépassement (mesuré + vu, s01-s02, s05, z_cles)

- **Mesuré** (abscisse moyenne des pixels clairs du personnage, caméra
  fixe) : charge #0-#9 ≈ 245-250 (immobile, différence 1,3-3,6) ; armé
  #10-#15 : 309 → 329 → 343 → 365 → 457 → 513 ; frappe #16 : 586, et le bord
  droit du personnage saute de 661 à 911 px en UNE image (le bras).
- **Vu** (#10-#15) : pendant l'armé, la jambe avant part en fente vers la
  cible et le bassin avance, tandis que le buste s'enroule et que le poing
  recule derrière le torse. **Déduit** : l'anticipation n'est pas « tout le
  corps recule » : le BAS avance vers la cible pendant que le HAUT s'enroule
  en arrière. Le corps s'étire entre les deux ; la frappe relâche le haut.
  Je rectifie la Partie 1 (« le bassin recule et descend ») : le bassin
  descend, mais d'après la mesure le corps entier se déplace vers la cible
  pendant l'armé.
- **Mesuré** (extension) : #16 → #18 la masse continue d'avancer (586 →
  644), puis revient (#19-#22 : 621 → 606) ; vraie immobilité seulement de
  #22/#23 à #30 (différence 0,85-1,2). **Déduit** : l'extension « tenue »
  est en fait un dépassement de 2 images puis un retour de 3-4 images, puis
  la vraie tenue. Même à 7,7 i/s, on voit que la pose de frappe n'est pas
  plantée net : elle dépasse et se pose.
- **Correction** : le trait violet de la poitrine reste visible de #15 à
  #40 et jusqu'au retour (s05 #64-#66 : encore une bande violette sur le
  torse). Ce n'est donc probablement pas un smear de trajectoire mais un
  marqueur du visualiseur (je ne sais pas lequel). Je retire l'idée « trait
  violet persistant = trajectoire ».
- s05 (#64-#66) : garde de face tenue, poings au visage, genoux fléchis.

## R8. Mythra s05 et combo Moon s07 (vu)

- Mythra #64-#66 : Tobi repart en course basse, buste penché, une main
  devant ; Shinso reste à plat au sol dans la tache sombre. La victime ne
  bouge plus du tout pendant que l'attaquant repart (la prise est
  « signée » par l'immobilité de la victime).
- Moon #96 : idle de face, bras le long du corps : l'anim boucle sur la
  pose de départ (confirme la mesure 0,1-0,2).

## Ce que la reprise change dans les grands enseignements (Partie 3)

- **A2 (conséquence en retard) s'affine** : la victime a sa propre
  anticipation (gatling : frisson 0,2 s → pop blanc → départ 0,15 s).
- **A5 (une tenue est rarement un gel) se confirme deux fois de plus** :
  Mii (dépassement puis pose), TSB fin (secousse secondaire 1,1 s après).
- **Nouveau, C5** : dans une série rapide, le blanc peut cacher le geste
  entier ; ce qui porte la lecture est le contraste entre deux poses
  tenues (Ippo R1).
- **Nouveau, B6** : l'anticipation peut être « bas vers la cible, haut en
  arrière » (Mii R7) ; ça rejoint le TSB (genou haut, dos tourné : le haut
  s'éloigne, mais le saut a déjà amené le corps près de la cible).
- **Nouveau, D5** : un objet minuscule reste lisible s'il porte un signal
  qui varie lentement (pulsation d'anneau, blanc progressif ; aafdc91d R4).
- **Nouveau, E1 (rythme)** : sous un bruit rapide (gatling, tunnel Ippo),
  il y a une respiration plus lente (phases de 0,3-0,4 s du côté dominant)
  — mesure grossière, confiance moyenne.

## Vérification adverse

Vérificateur indépendant. J'ai ré-extrait moi-même toutes les images des
13 GIF (PIL, durée de chaque image lue dans le fichier) dans
`c4/frames/verif_C3_gifs/<préfixe>/fNNN.png`, j'ai fait mes propres
planches (`sh_*.png`) et recadrages agrandis (`crop_*.png`), et j'ai
refait les mesures (différence entre images, abscisse des pixels clairs,
centre de la cape, saturation). Les nombres d'images et durées du lecteur
sont exacts (ex. TSB 151 im / 10,07 s ; Mii 67 im à 130 ms ; gatling 206
im / 6,24 s). Huit apprentissages contrôlés :

1. **« La libération est l'instant le plus court et souvent invisible »**
   NUANCÉ. TSB (`sh_48244687_76_93.png`) : #76-#79 n'est pas un
   « déroulé » de la frappe mais la retombée du genou haut vers
   l'accroupi. Le poing voyage ensuite VERS L'OBJECTIF pendant #80-#88
   (0,6 s, gros plan, fumée qui tourne) : le trajet du poing est donc
   montré, et lentement. Ce qui est court, c'est l'aboutissement : 1 image
   de contre-champ (#89), puis 3 cartes (#90-#92), puis blanc (#93-#94).
   La fumée est AVANT, pas après. Mii : le passage #15→#16 fait bien
   1 image, mais cette image dure 130 ms (GIF à 7,7 i/s), et la frappe
   est entièrement dessinée (bras tendu, hitbox rouge). Rien n'est caché.
   Coup chapeau : carte #7 entre #6 et #8 confirmée. Ippo : voir le
   point 2. Correction : « le contact n'est jamais dessiné et l'aboutissement
   dure 1 à 3 images. Le trajet, lui, peut être montré lentement (TSB) ».
2. **« Ippo : le blanc cache aussi le geste du bras »**
   RÉFUTÉ dans sa forme forte (« on ne voit jamais le bras voyager »).
   Recadrages à contraste renforcé (`crop_ippo_blancs.png`) : dans les
   images blanches, le boxeur reste entièrement visible sous un voile
   blanc. #100 et #110 montrent encore la pose A (gant à gauche). #101,
   #111 et #116 montrent une pose de PASSAGE (buste qui tourne, bras au
   centre). Le blanc est un voile posé sur l'intervalle, pas un
   remplacement. La cadence de ~5-6 images par coup (50 ms) est confirmée
   par la luminance (pics à #85, 90, 95, 100, 106, 110, 116, 121, 126),
   tout comme la pose tenue sur 3-4 images. La caméra change aussi d'angle
   pendant le blanc.
3. **« La pose de fin est tenue plus longtemps que l'armé »**
   NUANCÉ. Durées confirmées : armé du gatling #6-#16 = 0,30 s ; fin tenue
   #133-#205 ≈ 2,2 s. TSB : #100 (6,67 s) → #141 (9,40 s) = 2,73 s. Mii :
   extension stable #16-#30 ≈ 2 s. Mais la phrase « la conséquence dure
   plus que tout le reste réuni » est fausse pour TSB (≈ 6 s avant la
   frappe contre ≈ 4 s après) et pour le gatling (≈ 4 s de préparation et
   de rafale contre 2,2 s). Autre biais : le gatling (#205) et aafdc91d
   (#127) s'arrêtent alors que la pose est encore tenue. Ces durées sont
   des MINIMUMS imposés par la coupe du GIF, pas des choix de
   l'animateur.
4. **« La victime a sa propre anticipation (gatling) »**
   CONFIRMÉ, avec un décalage d'une image (`crop_gat_victim2.png`). Le
   mannequin gris reste immobile de la fin de la rafale (~#131, 3,97 s)
   jusqu'à #176 (5,33 s), soit ≈ 1,4 s. De #177 à #183, il tressaute, se
   dédouble et devient semi-transparent (≈ 0,2 s). #184 : il blanchit.
   #185 : blanc opaque, déjà décollé. #185-#190 : il file vers le fond
   (≈ 0,15-0,2 s), puis rapetisse jusqu'à #195. Dans ma zone, la
   différence est ≈ 0 de #152 à #184, puis 4-12 de #185 à #190. Mes
   valeurs diffèrent de celles du lecteur (autre cadrage), mais le motif
   est identique.
5. **« Mii : le bas avance vers la cible pendant que le haut s'enroule »**
   CONFIRMÉ. En mesurant l'abscisse moyenne des pixels > 110, je retrouve
   les chiffres du lecteur à ±2 px : #10-#15 310→515 ; #16 588 ; bord
   droit 661→911 ; #18 645 ; #22 608 ; différence < 1,2 de #23 à #30.
   Le bord gauche (le dos) passe de 35 à 299 px pendant l'armé : tout le
   corps se déplace. Réserve : #16-#17 comptent les sphères rouges de la
   hitbox, qui gonflent le bord droit. À #18, sans hitbox, le bras
   atteint 928 : le « dépassement » est aussi un bras qui finit de
   s'étendre.
6. **« Le torse passe de FRONT à BACK en 2 images avant chaque coup »**
   NUANCÉ (`sh_fa7b867c_0_96.png`). C'est vrai avant le coup 1 seulement
   (#17 FRONT → #18 profil → #19 BACK). Avant l'uppercut (#37-#41), le
   torse fait l'inverse, BACK → FRONT. Avant la frappe au sol (#62-#64),
   il revient de côté/vert vers une face accroupie. La règle juste :
   « chaque coup est précédé d'un demi-tour du torse, dans un sens qui
   alterne ». Les directions (horizontal / uppercut / sol) sont
   confirmées par la forme de la hitbox. En revanche, la « montée
   d'amplitude » (mes pics 6,5 → 6,8 → 8,5) est contaminée : le volume
   rouge de la hitbox au sol est bien plus grand et gonfle la différence.
   Cette mesure ne prouve pas que le coup est plus ample.
7. **« Double jab : aller 1-2 images, tenue ~0,25 s (#4-#8), retour en 1 image »**
   NUANCÉ (`crop_jab.png`). Le bras n'est tendu que de #4 à #6
   (≈ 0,13-0,19 s). À #7-#8, il est déjà REPLIÉ (poing à l'épaule) alors
   que le buste reste tourné. Le retour se fait donc en DEUX sauts d'une
   image (#6→#7 : le bras rentre ; #8→#9 : le corps revient en garde),
   séparés par une petite tenue de 2 images. Même structure au jab 2
   (#15-#17 tendu, #18-#19 replié, #20 garde). L'aller compte 1 image
   d'armé visible (#3) puis 1 image de claquement (#3→#4). « La tenue
   n'est pas un gel » est confirmé (la différence ne tombe jamais sous
   2,6 avant #23).
8. **« La couleur est réservée au moment qui compte »**
   NUANCÉ. aafdc91d est confirmé (`sh_aafdc91d_0_63.png`) : coup 1 blanc
   et gris ; coup 2 blanc, puis particules rouges à partir de #41 (pas
   dès #34). Coup chapeau : #36-#37 sont bien les seules CARTES en
   couleur (jaune, rouge, violet sur noir). En revanche, « les seules
   tenues 2 fois » est faux : #38-#39 (cible noire sur blanc) durent aussi
   2 images, et les notes du lecteur le disaient déjà (ligne du tableau
   §8). #36 et #37 ne sont d'ailleurs pas identiques : la forme grossit.
   Hors cartes, le ciel très saturé de #14-#31 et #43-#44 montre que
   « couleur rare » vaut pour les cartes, pas pour tout le clip.

Contrôlés en plus, hors des huit :
- Fin de TSB, deuxième vague : CONFIRMÉE (centre de la cape à 221-250 px
  de #100 à #115, saut de #116 à #123 (y 212→255→203), stable à ±1 px de
  #133 à #140, debout de #141 à #143). Seule réserve : « ±5 px » sur
  #100-#115 est trop serré, j'observe ±15 px.
- Goku : pics de différence toutes les 3 images CONFIRMÉS (≈ 7 contre
  ≈ 2,7). C'est la cadence « en 3 » ordinaire d'un dessin animé, pas
  forcément un choix de tension.
- Trait violet du Mii : correction CONFIRMÉE. La bande reste sur le torse
  à #15, #18, #40 et #55-#66 (`crop_mii_violet.png`) : c'est un élément
  du corps ou du visualiseur, pas une traînée.

Oublis importants :
- Ippo : ce qui est vraiment appris, c'est que le flash est un VOILE sur
  une pose de passage réellement animée (1 image), et non un trou.
- TSB : le trajet du poing est montré LENTEMENT, en gros plan, vers la
  caméra (0,6 s dans la fumée). L'accélération n'a lieu qu'au contre-champ
  (#89). Cela contredit le « frappe = 1-3 images » appliqué en bloc.
- Mii : la hitbox active (#16-#17) dure 2 images de 130 ms, et ses
  sphères dépassent nettement le poing (hitbox qui déborde du corps). Le
  retour de l'extension est très lent (#31-#40 ≈ 1,3 s) puis se pose
  (#41-#54).
- Double jab : même gabarit exact pour les deux jabs (3 images tendu,
  2 images replié, 1 image de retour) : un motif réutilisable tel quel.
- Durées de tenue finale mesurées sur des GIF coupés (gatling,
  aafdc91d) : ce sont des bornes basses. Aucune règle « fin > X s » ne
  doit en sortir sans source non coupée.
- Combo Moon : la mesure d'amplitude par différence d'images est
  faussée par le volume de hitbox dessiné. Il faudrait masquer le rouge
  avant de conclure.
