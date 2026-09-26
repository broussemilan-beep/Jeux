# A2 — TSB : Stoic Bomb (exercice d'œil à l'aveugle) + Collateral Ruin

Identifiant : A2_tsb_stoic_collateral. Images de travail : scratchpad/c4/frames/A2_tsb_stoic_collateral/
(v30/fNNN.png = vidéo Stoic Bomb extraite à 30 i/s, fNNN => t = (NNN-1)/30 s).

## 1. PRÉDICTION À L'AVEUGLE (écrite AVANT d'ouvrir le .rbxm)

Vidéo : `BpDlTrnlIUk_Stoic Bomb ｜ The Strongest Battlegrounds.mp4`, 640x360, 30 i/s, 9,53 s, pas de piste son.
Regardé : planche 4 i/s de tout (overview4fps.png), puis 30 i/s de 0 à 5,3 s (sA1, sA2, sB, sC, sD, sE, sF),
zoom sur le joueur au décollage (sOrange.png), en l'air (sAir.png), à la fin dans le cratère (sH.png), 10 i/s de 6 à 9,4 s (sG).

Qui est qui (vu) : le joueur = avatar ORANGE (veste orange, chapeau melon noir à bande orange). Le mannequin =
personnage noir aux cheveux en pics tenant une barre d'haltères, étiquette « 100% Weakest Dummy » (f1-f60).
La caméra suit l'orange => c'est lui qui lance le coup.

Ce que je crois voir, dans l'ordre (temps vidéo) :
- 0,00-2,07 s : joueur quasi immobile (idle), bras le long du corps (sOrange f55-f63). Rien d'animé chez lui.
  (Le mannequin, lui, bouge sa barre ; c'est son idle, hors sujet.)
- ~2,10 s (f64) : première image d'anticipation : tête qui plonge, buste qui commence à se pencher.
- 2,13-2,20 s (f65-f67) : accroupi profond, buste très penché en avant, tête basse, bras écartés/fléchis vers
  l'arrière-bas. PRÉDICTION : pose clé « ressort » tenue ~3 images (0,1 s).
- 2,23 s (f68) : COUPE caméra -> plan très large, en hauteur, sur le parc. Le joueur est HORS CHAMP de f68 à f71
  (2,23-2,33 s) : je ne vois PAS le décollage ni la montée. PRÉDICTION : le rig pose une extension de saut
  (corps allongé, bras vers le haut ou le long) que la caméra ne montre pas.
- 2,37-2,43 s (f72-f74) : le joueur entre par le haut de l'image, vu de dessous/dos, corps à l'horizontale ou
  retourné (je crois voir des semelles / les jambes en l'air) : PRÉDICTION : une rotation (salto / vrille) à l'apex.
- 2,47-2,53 s (f75-f77) : vu de face, visage vers le ciel, bras écartés : fin de rotation.
- 2,57-2,87 s (f78-f87) : chute pieds en bas, caméra au-dessus qui plonge avec lui ; un bras (côté droit de
  l'image) levé, main près de la tête / au-dessus. PRÉDICTION : pose de chute tenue, un bras armé en haut.
- 2,77-3,40 s : éclairs jaunes/noirs qui tombent du ciel, croix de lumière (lens flare) centrée sur lui : il
  descend à travers ; le sol se rapproche (dalles qui grossissent). Pose illisible : effets devant le corps.
- ~3,40 s (f103) : atterrissage à côté du mannequin (qui est au sol / à côté).
- 3,47-3,60 s : rayons blancs + anneaux + assombrissement (vignette noire) ; 3,63 s+ : DÔME ROUGE autour de
  lui, anneaux blancs qui tournent.
- 3,60-4,97 s : charge : une sphère noire hérissée qui PULSE à hauteur de main, devant/sous lui, à peu près
  toutes les 6 images (~0,2 s : f131, f137, f143, f146, f149) ; étoile blanche qui clignote. PRÉDICTION de pose :
  debout, légèrement penché, un bras (ou les deux) tendu vers le bas/l'avant tenant la « bombe », TENU ~1,4 s
  avec micro-mouvement. Honnêtement : vue du dessus + saturation rouge : je ne distingue que la tête (chapeau)
  et le haut du buste jaune ; les bras sont noyés.
- 5,00 s (f151) : flash blanc plein écran + la caméra RECULE très vite (dézoom f150-f160), 5,33 s retour du décor
  large, disque lumineux au sol ; 5,53 s (f167) sphère noire (implosion) ; 5,57-5,77 s onde de choc rouge en
  anneau/dôme qui balaie la caméra ; 5,80 s+ : sol en morceaux, fumée, cratère.
- 6,1-6,9 s : le joueur est au centre du cratère, compact (accroupi ? un genou ?) ; ~7,0 s il paraît plus
  grand, face caméra : PRÉDICTION : il se relève (pose finale debout). Le mannequin est éjecté (ragdoll rose à
  droite, 6,0-6,9 s). Résolution trop faible pour être sûr.

Mes prédictions chiffrées de l'anim (avant vérité) :
 P1. anticipation accroupie courte (~0,1 s) juste avant le saut ;
 P2. saut + salto/vrille à l'apex ;
 P3. chute avec un bras levé ;
 P4. réception + longue pose de charge ~1,4 s, bras vers la bombe ;
 P5. explosion puis pose accroupie et relevé ;
 Durée totale de l'anim estimée : de 2,1 s à ~7 s vidéo => ~5 s.

---------------------------------------------------------------------------------------------------

## 2. LA VÉRITÉ : Stoic Bomb dans tsb_anim.rbxm (ouvert APRÈS la prédiction)

Outils : `planche_cles.py` (SB_planche.png, SB.txt, SB.json) ; la planche standard est illisible ici (le torse
monte à 148 studs, la caméra fixe dézoome : 24 petites figurines). J'ai donc écrit un rendu « caméra qui SUIT le
torse » (scratchpad/c4/tools_A2/suivi.py -> SB_suivi_cles.png : les 52 clés, 3/4 face + profil ; SB_dessus.png :
10 instants vus de DESSUS comme dans la vidéo), plus `stats.py` (clés par membre) et la lecture brute des
`KeyframeMarker` du .rbxm (jamais lus avant par le cerveau : le chargeur `corpus.load_rbxm_sequences` les ignore).

Durée 4,72 s = 284 images à 60 i/s ; 57 Keyframes dont 52 porteurs de poses ; 6 marqueurs.

### 2.1 Les actes, clé par clé (mesuré = SB.txt ; vu = SB_suivi_cles.png)
| images 60 | temps anim | ce qui est posé | statut |
|---|---|---|---|
| i0-i10 | 0-0,17 s | ACCROUPI d'élan : hanche 3,00 -> 2,28 ; buste penché +28°, TOURNÉ +31° (lacet), penché côté +14 ; bras DROIT jeté haut-arrière (az +137, el -60), bras gauche bas-arrière. Toutes les parts clées À CHAQUE IMAGE (segment cuit) | mesuré + vu |
| i11 | 0,18 s | TÉLÉPORTATION : hanche 2,28 -> 146,87 studs en UNE image ; corps RETOURNÉ (penché +158°, tête en bas, jambes en l'air) | mesuré + vu |
| i11-i22 | 0,18-0,37 s | salto : le buste revient de +158° à +102° ; seule la TÊTE est clée image par image (i12-i21), le reste interpole | mesuré |
| i22-i57 | 0,37-0,95 s | fin du salto (penché -53° à i32 = renversé en arrière, jambes devant) puis redressement -39, -25, -11, -4 ; les bras passent d'une ÉTOILE (i20-i28, bras et jambes écartés, visage au ciel) au X : les avant-bras se croisent devant la poitrine entre i37 et i57 | mesuré + vu (SB_dessus i20, i28) |
| i57-i249 | 0,95-4,15 s | TENUE du X : 192 images (3,2 s) où les BRAS ne sont plus jamais re-clés (sauf i90 BD, i141 H BD BG avec des valeurs identiques au 1/100e) ; buste figé (lacet -6, penché +2). SEUL le Torso (la racine) est clé, pour dessiner la trajectoire verticale | mesuré |
| i57-i90 | 0,95-1,50 s | CHUTE rapide dessinée à la main : hanche 122 -> 99 -> 42 -> 19 -> 10,9 ; vitesse max i63-i74 = 57 studs en 11 images (~310 studs/s), puis freinage brutal (2,6 puis 1,2 stud/image) | mesuré |
| i90-i205 | 1,50-3,42 s | FLOTTEMENT : hanche 10,9 -> 3,53 en 115 images (7,4 studs), clés de plus en plus espacées (7, 12, 10, 12, 17, 12, 16, 12, 24 images) : une décélération exponentielle faite de segments LINÉAIRES. Le perso est à ~8 puis ~0,5 stud au-dessus du sol : il N'A PAS atterri | mesuré |
| i205-i216 | 3,42-3,60 s | vraie arrivée au sol en 11 images : jambes clées à i206 (1 image APRÈS le torse), hanche 3,53 -> 2,60 ; à i213-216 le buste tourne de -6 à -29° et plonge de +2 à +15° | mesuré + vu |
| i216-i249 | 3,60-4,15 s | écrasement qui CONTINUE après le contact : penché +32° à i224 (+8 images), hanche 2,49 ; tenu, remonte lentement (2,58, 2,70) | mesuré + vu |
| i249-i283 | 4,15-4,72 s | les bras s'OUVRENT vers l'avant-bas (RA torse az -88 -> -24, el +15 -> -64), buste se redresse +30 -> +8, hanche 2,97 | mesuré + vu |

Marqueurs (lu, noms exacts du fichier) : i67 `ChargingSound` ; i90 `Voiceline` ; i97 `BeginSlowing` ; i205
`HitboxExplosion?` (point d'interrogation dans le nom) ; i216 `FinalBoarExplosion` ; i282 `End`.

### 2.2 Recalage vidéo <-> anim (mesuré à l'image près, ±1 image vidéo)
- 1re image où le joueur bouge : f64 (2,10 s) ; la coupe caméra f68 (2,233 s) tombe EXACTEMENT sur la
  téléportation i11. D'où t0 de l'anim ≈ 2,05 s vidéo (± 0,03 s).
- i19 -> 2,37 s : le joueur entre par le haut de l'image, en vrille (f72) : OK.
- i25-i30 -> 2,47-2,55 s : « visage au ciel, bras écartés » (f75-f77) = l'étoile du salto : OK.
- i50-i90 -> 2,88-3,55 s : chute rapide = caméra qui plonge avec lui, dalles qui grossissent, traits de feu : OK.
- i90 `Voiceline` -> 3,55 s : rayons blancs + vignette sombre (f105-f109, 3,47-3,60 s).
- i97 `BeginSlowing` -> 3,67 s : le dôme devient rouge plein (f110-f112, 3,63-3,70 s).
- ~i177 -> 5,00 s : flash blanc + recul caméra (aucun marqueur à cet instant : déclenché autrement, je ne sais pas comment).
- i205 `HitboxExplosion?` -> 5,47 s : sphère noire d'implosion f166-f167 (5,50-5,53 s).
- i216 `FinalBoarExplosion` -> 5,65 s : anneau rouge qui balaie la caméra f168-f174 (5,57-5,77 s).
- i283 fin -> 6,77 s ; dans la vidéo le joueur est compact dans le cratère 6,1-6,9 s puis plus grand ~7,0 s
  (reprise de l'idle). Cohérent, mais à 25-30 px de haut je ne peux pas confirmer l'ouverture des bras.

### 2.3 Comparaison honnête prédiction / vérité
| prédiction | verdict | pourquoi |
|---|---|---|
| P1 accroupi d'élan court ~0,1 s avant le saut | JUSTE sur le principe (0,17 s réel, dont ~0,1 s visible avant la coupe) ; RATÉ : la torsion du buste (+31°) et l'asymétrie des bras (droit jeté haut-arrière, gauche bas) | vue de face-dessus, 3 images vidéo seulement, perso de ~60 px |
| P2 saut + salto/vrille à l'apex | JUSTE (salto i11-i57, départ tête en bas) ; RATÉ : le saut lui-même (145 studs en 1 image) | la coupe cache la montée : le perso est hors champ f68-f71 |
| P3 chute avec un bras levé près de la tête | FAUX : les deux avant-bras se croisent en X devant la poitrine | vue de DESSUS-arrière : des avant-bras croisés devant le haut du buste apparaissent « à côté de la tête » (vérifié : SB_dessus.png, rangée az 180°) |
| P4 atterrissage à 3,4 s puis charge debout ~1,4 s, bras vers la « bombe » | FAUX sur l'atterrissage : il FLOTTE de 3,55 à 5,47 s (8 -> 0,5 stud du sol) et ne touche le sol qu'à 5,65 s. À moitié juste sur les bras : ils sont bien devant, là où pulse la sphère noire | caméra au zénith = aucune information de hauteur ; le mannequin à côté, à la même échelle, m'a servi de faux repère de sol ; et le nom « Bomb » m'a fait chercher un objet tenu (biais d'attente) |
| P5 explosion puis accroupi puis relevé | JUSTE à ~0,2 s près (écrasement i216-i249, ouverture i249-i283) mais je n'ai PAS vu que l'écrasement vient APRÈS l'explosion au sol et non avant | perso minuscule dans le plan très large |
| durée ~5 s (2,1 -> ~7 s) | JUSTE : 4,72 s (2,05 -> 6,77 s) | |

Ce que l'exercice apprend à mon œil (déduit) :
1. Une vue de dessus supprime la hauteur : ne jamais conclure « il est au sol » sans ombre, contact ou repère de
   perspective. Ici l'ombre du joueur est noyée dans le rouge.
2. Un personnage voisin n'est pas un repère de sol : il peut être soulevé aussi (ici je ne sais pas si le
   mannequin l'est : son anim de victime n'est pas dans le fichier).
3. Le nom du coup crée une attente (bombe = objet dans la main) qui déforme la lecture d'une tache d'effet.
4. Une coupe caméra est un endroit où l'anim peut tricher : je dois me demander « qu'est-ce qui se passe
   pendant que je ne vois pas ? ».

## 3. Stoic Bomb : comment c'est fabriqué (où il place le rig, dans quel ordre)

- **Le vol entier est dans l'animation**, pas dans la physique : c'est la translation du Torso (RootJoint) qui
  monte à 148 studs en une image et redescend par 12 clés à la main (mesuré). Conséquence (déduit) : la
  HumanoidRootPart reste au sol ; la caméra du jeu doit suivre le TORSE (script), sinon elle resterait par terre.
- **Tricher sous une coupe** : la téléportation d'une image est invisible car la caméra coupe sur la même image
  (mesuré : f68 = i11). L'animateur n'a pas animé de montée du tout : il a posé le perso en haut, retourné.
- **Une tenue de 3,2 s obtenue en NE clant PAS** : les bras sont posés à i57 puis abandonnés ; seules les clés du
  torse existent (mesuré, rythme par membre : BD 26 clés dont 12 dans l'accroupi). La pose est rigide à 0,01
  près. Pourquoi ça marche ici (déduit) : pendant cette tenue, la caméra est au zénith et le dôme rouge + une
  sphère noire qui pulse ~toutes les 0,2 s (vu, f131/137/143/146/149) apportent tout le « vivant ». La vie de la
  tenue est déléguée aux effets. Contraste : Collateral Ruin, filmé au sol, garde une tenue qui dérive (§4).
- **Courbe de chute dessinée en segments linéaires** : espacements de clés 6, 11, 9, 7, 12, 10, 12, 17, 12, 16, 12,
  24 images pour des hauteurs 99 -> 3,5 (mesuré). Même en Linear, en rapprochant les clés au début et en les
  écartant ensuite, il fabrique une décélération (le « freinage » i74-i90 puis la dérive).
- **Des segments cuits dans une anim clée à la main** : i0-i11 toutes parts à chaque image, tête à chaque image
  jusqu'à i21 (mesuré). Contredit (légèrement) `ETUDE_TSB.md` §1 qui dit que seules Ultimate2 et
  WallComboVictim sont cuites. Hypothèse (déduit) : l'accroupi et le salto viennent d'un outil (easing ou IK)
  puis ont été cuits, le reste posé à la main.
- **Ordre de pose à l'arrivée** : torse i205, jambes i206 (1 image après), torse tourne et plonge i213-i216,
  tête i215 : les jambes préparent l'appui juste avant le contact, le buste encaisse APRÈS (mesuré).
- **L'impact du corps est petit** : 11 images, hanche -0,9 stud, torsion -23°, penché +13° puis +32°. Toute la
  violence est portée par les deux marqueurs d'explosion (i205, i216) et par la caméra.
- **Les marqueurs font de l'anim l'horloge maîtresse** : son de charge, voix, ralentissement, hitbox,
  explosion finale, fin. L'animateur (ou le dev) place les événements sur la timeline de l'anim, pas l'inverse.

## 4. Relation anim / caméra / effets dans Stoic Bomb (ce que la caméra montre ou cache)

| moment | l'anim fait | la caméra/les effets montrent | ce que le spectateur reçoit (déduit) |
|---|---|---|---|
| 0-2,05 s | rien (idle) | plan de jeu normal | calme, échelle du lieu |
| 2,05-2,23 | accroupi tordu 10 images | plan de jeu | un « ressort » bref |
| 2,23-2,37 | téléportation + début du salto | COUPE en plan très large, ciel/parc vide, perso hors champ | « il est parti très haut » sans le voir monter |
| 2,37-2,88 | salto étoile -> X | plan large en plongée, perso qui entre par le haut | silhouette lisible qui tourne |
| 2,88-3,55 | pose X figée, chute à ~310 studs/s puis freinage | caméra qui plonge avec lui, éclairs noirs/jaunes, croix de lumière | la vitesse est vendue par le décor et les traits, pas par la pose |
| 3,55-5,00 | X figé, flotte à quelques studs | zénith serré, dôme rouge plein cadre, anneaux, sphère qui pulse | « ça charge » ; la hauteur disparaît ; le corps est presque caché |
| 5,00-5,47 | X figé, fin du flottement | flash blanc puis recul très rapide en plan large | respiration, changement d'échelle avant le coup |
| 5,47-5,77 | chute finale 11 images, écrasement | implosion noire puis anneau rouge qui balaie l'écran | l'impact EST l'explosion ; le corps est minuscule |
| 5,8-9,5 | écrasement, ouverture des bras, fin | plan large fixe, débris, fumée, cratère 3,5 s | la conséquence dure plus que le coup |

Leçon (déduit, pas règle) : dans ce coup, ce que l'animateur a clé avec le plus de soin (salto, écrasement,
ouverture) est justement ce que la caméra montre le moins bien ; ce que la caméra montre plein cadre (la charge)
est une pose figée. Hypothèse : l'anim est faite pour TOUS les joueurs autour (caméras de jeu normales), la
cinématique est faite pour le lanceur. À vérifier sur une vidéo filmée par un autre joueur (je n'en ai pas).

## 5. Collateral Ruin : étude en profondeur (aucune vidéo de ce coup dans mes sources : 3D seulement)

Fichiers : CR_planche.png, CR.txt, CR.json, CR_suivi_a.png (i0-i74), CR_suivi_b.png (i75-i128), traj.py
(positions/vitesses par image), stats.py. 2,13 s = 128 images ; 37 Keyframes, 33 porteurs de poses ; 6 marqueurs.

### 5.1 Les actes (mesuré sur traj.py ; vu sur CR_suivi_*)
| acte | images | vitesse des mains (studs/s) | pose | marqueur |
|---|---|---|---|---|
| 1 plonger / ramasser | i0-i22 | 11-21 puis 1-6 (mini-tenue i10-i16) | fente très large, jambe droite loin devant, buste penché +27-29°, hanche 2,79 -> 2,19 ; bras qui tombent vers le sol devant (vue de dessus : bras gauche pointé au sol) | i13 `SpeedLinesStart` |
| 2 enrouler | i22-i40 | ~30 (les deux mains ensemble) | le buste tourne le DOS (lacet cumulé -58 -> -148°), les bras balaient autour et remontent derrière la tête | i37 `SpeedlinesFinale` |
| 3 lever / rassembler | i40-i64 | 3-10 (le creux) | les deux mains se rejoignent AU-DESSUS de la tête (i61 : RA (-1,72 ; 3,49 ; 1,62), LA (-1,52 ; 3,47 ; 1,60), écart 0,2 stud), buste qui se redresse (penché 40 -> 18°) et commence à revenir (-153 -> -112°) | |
| 4 lancer la rotation | i64-i73 | 15-26 | mains jointes au-dessus, le buste se dévisse, penché remonte à 38° | i67 `SpinnerSmokeEffect` |
| 5 TOUPIE + frappe | i74-i90 | 73-119 (le seul moment rapide) | bras tendus à l'horizontale mains jointes, ~1 tour complet en 15 images (lacet -11 -> +354° de i75 à i90, ~1 460°/s), jambe droite levée (pied à 1,38 stud du sol à i76) ; à i90 la hanche touche son point le plus BAS (1,94) et le buste penche à 55° : le coup s'abat | i75 `StartHitbox` |
| 6 jeter | i90-i98 | 50 -> 9 | le corps continue : bascule sur le côté (≈70° mesuré, penché côté ~67°), bras GAUCHE jeté vers le ciel (main à 5,3 studs), bras droit vers le sol, jambes à ~3 studs d'écart | i92 `DownMesh`, i98 `EndHitbox` |
| 7 tenue finale | i98-i128 (0,5 s) | 0,2-3 (bras droit), 3-21 (bras gauche) | la diagonale tenue : un bras en haut, un en bas ; dérive lente : bras gauche redescend 5,1 -> 3,07 puis remonte 3,76 ; hanche 2,43 -> 1,97 -> 2,09 | |

Rotation totale du buste de i45 à i95 : ~610° (≈1,7 tour), dont ~560° entre i65 et i95 (mesuré, lacet cumulé,
approximatif car calculé depuis l'axe avant d'un buste très penché). Le perso ne se déplace pas : le Torso reste à
moins de 0,9 stud de l'origine (mesuré) ; tout déplacement éventuel en jeu est hors de l'anim.

### 5.2 Comment un geste de 2 s reste lisible (déduit à partir des mesures ci-dessus)
1. **Un seul moment rapide, au bon endroit** : les mains vont à 11-30 studs/s partout, tombent à 3-10 juste
   avant, puis montent à 73-119 pendant 16 images seulement. Rapport ~3 à 4 avec la préparation, ~10 avec le
   creux. L'œil n'a pas à chercher « le coup ».
2. **Une silhouette différente par acte** : fente basse vers le sol / dos tourné / ligne VERTICALE bras au ciel
   / croix horizontale qui tourne / DIAGONALE finale. Aucune silhouette ne revient deux fois.
3. **Les deux mains jointes = un seul point à suivre** pendant tout le lancer (écart 0,2-1,2 stud de i61 à i85,
   mesuré). Hypothèse : elles tiennent un objet ou font un marteau à deux mains ; sans vidéo je ne sais pas.
4. **Le creux avant l'explosion** (acte 3, 0,4 s à 3-10 studs/s) : c'est la « charge » de ce coup, courte,
   montée vers le haut, pas une pose figée.
5. **Le poids descend à la frappe** : hanche la plus basse (1,94) exactement à l'image où le buste est le plus
   penché (i90), puis rebond (2,43) et tassement (1,97) : l'arrivée a un rebond amorti.
6. **Pose finale tenue 0,5 s mais vivante** : dérive lente, et le bras gauche est clé UNE image avant le torse
   (i101 BG / i102 T ; i106 BG / i107 T) : les parts ne bougent jamais toutes ensemble.
7. **Les marqueurs encadrent l'action rapide** : hitbox active de i75 à i98 (23 images, 0,38 s) = exactement la
   toupie + le jet ; les traits de vitesse commencent dès l'accroupi (i13) : l'effet annonce, l'anim livre.

### 5.3 Où il place le rig (mesuré, stats.py)
- Torso 30 clés, jambes 28 chacune : le corps et les appuis sont clés toutes les 3 à 7 images (≈14 clés/s),
  c'est la pulsation de l'anim.
- Bras droit 13 clés, bras gauche 20, tête 12 : les bras ne sont clés qu'aux CHANGEMENTS de pose (écarts jusqu'à
  18 images : BD i55 -> i73). Entre deux, ils gardent leur rotation locale et sont portés par le buste qui tourne.
  Méthode lue dans les données (déduit) : poser le moteur (buste + jambes) serré, puis les bras en poses clés
  espacées ; le mouvement des bras dans le monde vient en grande partie du buste.
- **Pendant la toupie, une clé de buste tous les 3 à 5 images, soit ≤ 125° de rotation entre deux clés** (mesuré :
  i73->76 +53°, i76->80 +117°, i80->85 +105°, i85->90 +125°). Explication (déduit, cohérente avec l'interpolation
  de rotation par le plus court chemin) : au-delà de 180° entre deux clés, Roblox tournerait dans le mauvais
  sens ; pour obtenir un tour complet, il faut au moins 3 clés intermédiaires. C'est une contrainte technique très
  concrète pour nos rotations.
- Pas de segment cuit ici : toutes les clés sont espacées (contrairement au début de Stoic Bomb).

## 6. Surprises / contradictions avec ce que le cerveau croyait
1. **KeyframeMarker réels, jamais lus** : le cerveau n'avait que des sources web sur `GetMarkerReachedSignal`
   (`corpus/fiches/VFX.md` l.104, `recherche/roblox_2026-09-25.md`) et `pro_pack_battleground.json` écrit « le
   chargeur ne lit pas les KeyframeMarker ». Le .rbxm TSB en contient 35 (lu, compté) : M1-M3 `hitreg` à i10/i10/i8 et
   `end` ; M4 `hitreg` i13 ; Swift Sweep `Kick1` i24, `SmokeSlash` i36, `Kick2` i52 ; Ultimate1 `ParticleActivate`
   i16, `TweenStuff` i281, `StartLoop` i495, `AwakenFinale` i497 ; WallComboPlayer `hit1/2/3` i9/176/352 ; plus
   ceux de Stoic Bomb et Collateral Ruin. Le pack battleground n'en a aucun (lu).
2. **Stoic Bomb n'atterrit pas pendant le dôme** : il flotte (mesuré). Le catalogue/ETUDE_ARCHIVE décrivent un
   dôme « vu de dessus » sans le dire ; `pro_tsb_ultimes.json` le savait (« descente lente en vol f90-f204 »).
3. **« Saisie en caméra de jeu 0-2,2 s … jette la victime »** (ETUDE_ARCHIVE_VIDEOS_1 l.~40) : je n'ai vu AUCUNE
   saisie ni lancer : le joueur est immobile jusqu'à 2,07 s (f55-f63, sOrange.png) et le mannequin garde sa barre.
   Je ne peux pas dire ce qui arrive au mannequin pendant la coupe.
4. **« plongeon corps à l'horizontale »** (ETUDE_TSB §4) : c'est un salto qui part TÊTE EN BAS à l'apex
   (penché +158°) et se redresse ; le corps passe par l'horizontale (i20-i22) sans « plonger ».
5. **Segment cuit dans Stoic Bomb** (i0-i11 toutes parts, tête jusqu'à i21) : nuance ETUDE_TSB §1.
6. **Tenue sans vie** : 3,2 s de bras figés à 0,01 près chez TSB. Le cerveau répète « tenues vivantes » : ici le
   pro fait l'inverse et ça tient, parce que les effets et le cadrage portent la vie (déduit). Ça dépend du plan.

## 7. Ce que je saurais REFAIRE maintenant en R6 (concret)
- **Accroupi d'élan de saut (10 images à 60 i/s)** : hanche -0,7 stud, buste penché +28° ET tourné +31°, bras
  droit jeté haut-arrière, bras gauche bas-arrière, en arrivant sur la dernière image quasi tenue (i9-i10).
- **Saut « tricheur »** : téléporter la racine (translation du Torso) sur une image synchronisée avec une coupe,
  poser le perso retourné à l'apex, salto en ~45 images en posant l'étoile (bras/jambes écartés) au milieu puis
  refermer.
- **Chute + flottement** en ne clant que la racine : clés serrées au début (6-11 images) puis de plus en plus
  espacées (12-24), en Linear.
- **Tenue compacte** : avant-bras en X devant la poitrine (poings dans les axes du torse : avant +1,26-1,31, haut
  +0,5-0,66, côté ±0,8-1,0 ; épaules rapprochées), tête baissée ~-16°, figée si la caméra et les effets la font
  vivre, dérivante sinon.
- **Arrivée au sol** : jambes clées 1 image avant le contact, puis sur 11 images hanche -0,9 et torsion du buste
  -23°, penché qui continue à +32° 8 images APRÈS le contact, tenir ~25 images, relâcher en ~34 images.
- **Toupie de Collateral Ruin** : mains jointes, clé de buste tous les 3-5 images (≤ 120° entre deux clés), une
  jambe levée pendant le tour, hanche au plus bas à l'image de la frappe, puis diagonale finale (un bras au ciel,
  l'autre au sol, corps basculé) tenue 30 images avec des clés décalées d'une image entre bras et buste.
- **Marqueurs** : nommer les événements dans l'anim (SpeedLines au début de la préparation, StartHitbox /
  EndHitbox autour des images rapides, un marqueur par effet d'impact) plutôt que des timers dans le script.

Ce que je NE saurais PAS faire / pas vérifié :
- Les effets et la caméra de Collateral Ruin en jeu (aucune vidéo) ; ce que tiennent les mains jointes.
- Ce que fait le mannequin pendant Stoic Bomb (son anim n'est pas dans le fichier ; est-il soulevé ?).
- Ce qui déclenche le flash blanc à ~5,0 s (aucun marqueur à cet instant) ; ce que fait `BeginSlowing`.
- Le son (la vidéo n'a PAS de piste audio : ffprobe ne montre qu'un flux vidéo).
- Les easings exacts de chaque pose (j'ai lu les positions interpolées ; l'étude TSB dit Linear pour ~98 %).
- Le script de caméra (suit-il le Torso ? déduit seulement de la téléportation).

## 8. Non couvert / limites
- Vidéo 640x360 : pendant le dôme le joueur fait ~25-30 px de haut (estimé à l'œil), les bras sont noyés.
- 6,0-9,5 s regardé à 10 i/s seulement (plan fixe, fumée) ; 0-2,0 s à 30 i/s mais seul le mannequin bouge.
- Le lacet cumulé de Collateral Ruin est approximatif (buste très penché : l'axe « avant » se projette mal).
- Je n'ai pas étudié les 11 autres anims du fichier (hors de mon angle) ; seuls leurs marqueurs sont listés.

## Vérification adverse

Vérificateur indépendant, 2026-09-26. Je suis retourné aux sources sans réutiliser SB.txt, CR.txt, traj.py ni stats.py.
- Lecture directe du .rbxm TSB avec `corpus.load_rbxm_sequences` (parts clées par Keyframe, matrices ET translations des Pose).
- Descripteurs `geo_pose` sur `resample_linear` à 60 i/s.
- Lecture brute des `KeyframeMarker` (Name, Value, Keyframe parent).
- Rendus 3D recalculés (`rend.py`).
- Réextraction complète de la vidéo à 30 i/s (286 images) et différences entre images.
- Planches regardées avec Read : m62_77, m_mid, m126_149, m160_175, sb_crouch, cr_sil.
- `planche_cles.py` relancé sur Collateral Ruin (CR_verif.png/.txt).

Tout est dans `frames/verif_A2_tsb_stoic_collateral/` (dump.py, v.py, cr.py, rend.py).

| # | apprentissage | verdict | ce que j'ai regardé | correction |
|---|---|---|---|---|
| 1 | Coupe caméra = téléportation de la racine | **confirmé** | Pose Torso i10 z=-0,72 puis i11 z=143,87, soit une hanche de 2,28 à 146,87. Descripteurs à i11 : penché +158°. Vidéo : différence entre images 4,8 à f67 puis 31,0 à f68 (coupe). Perso absent de f68 à f71, il entre par le haut à f72 (m62_77.png). L'accroupi est visible de f64 à f67 (4 images vidéo, soit ~8 images d'anim) : t0 ≈ 2,05 s tient à ±1 image. | aucune |
| 2 | Flotte jusqu'à 5,65 s | **nuancé** | Pieds (bout des jambes) : 8,0 stud à i90, 0,65 à i205, 0,05 à i213, -0,18 à i216 (enfoncés). Hanche : 3,53 à i205, puis **remonte à 3,60 à i209** avant la chute. Vidéo f106-f149 : vue plongeante, aucun indice de hauteur lisible. | Les chiffres sont justes dans le repère de l'anim. Contact des pieds vers i213 (≈5,60 s) plutôt qu'à i216. Micro-remontée non vue : +0,07 de i205 à i209, une anticipation minuscule avant de tomber. « Au-dessus du sol » suppose que la HumanoidRootPart reste au sol, et aucun script ne permet de le vérifier. La vidéo ne permet PAS de voir qu'il flotte : l'explication « faux repère du mannequin » reste une hypothèse. |
| 3 | Tenue de 3,2 s sans vie, vie déléguée aux effets | **nuancé (fort)** | Rotations des bras identiques de i57 à i141. En revanche, la **translation** des Pose des bras est re-clée avec d'autres valeurs : bras droit y de -0,157 (i57) à -0,285 (i90) puis -0,523 (i141) ; bras gauche de -0,242 à -0,764. Poings par rapport au torse : haut 0,70 → 0,47 (droit) et 0,95 → 0,61 (gauche) entre i90 et i141. Tête re-clée à i141 (~1-2°). Buste penché -4 (i57) → 0 (i63) → +2 (i74). Vidéo m126_149 : la sphère noire revient à f128, 131, 134, 137, 140, 143, 146, 149. | « Valeurs identiques à 0,01 près » est faux pour les translations. Les bras GLISSENT lentement vers le bas (~0,3-0,5 stud en 84 images) : c'est une dérive, pas une pose figée. L'animateur fait vivre la tenue par la translation des épaules, pas par la rotation. La sphère pulse **toutes les ~3 images (0,1 s)**, pas toutes les 0,2 s : la moitié des pulsations a été ratée. |
| 4 | 35 KeyframeMarkers, recalés « à une image près » | **nuancé** | Lecture brute : 35 marqueurs, noms et images exacts, Value vide sauf WallComboPlayer (« 0 »). Recalage : HitboxExplosion? i205 → 5,474 s = f165, où les éclats rouges apparaissent (OK). FinalBoarExplosion i216 → 5,65 s ≈ f170, mais l'anneau rouge plein cadre est **déjà là à f168 (5,567 s)**. | Liste, noms et nombre confirmés. « Nouveau pour le cerveau » confirmé : aucun nom de marqueur dans le dépôt. L'anneau précède FinalBoarExplosion de 2-3 images vidéo (~0,08 s) : ce n'est pas « à une image près ». ChargingSound et Voiceline sont des marqueurs SONORES et la vidéo n'a pas de son : ils sont invérifiables, ne pas dire qu'ils tombent sur un changement d'effet. |
| 5 | Collateral Ruin : un seul moment rapide i74-i90, 16 images, encadré par la hitbox | **nuancé** | Vitesses recalculées image par image. Main gauche : 49,9 / 63 / 64,8 à i74-i76 ; **80,6 / 77,8 / 66,7 / 51,6 à i91-i94**. Main droite : 52 / 51 / 42 à i91-i93. Préparation : main gauche jusqu'à 37,3 à i24. | Le « rapide » dure ~i74-i94 (≈20 images), pas 16, et ne s'arrête pas à i90. Le chiffre 73-119 ne vaut pas pour les deux mains à la fois : la gauche démarre à 50. Préparation 11-37 et non 11-30. Le cadrage par la hitbox i75-i98 reste juste, et même mieux, puisqu'elle couvre aussi i91-i94. |
| 6 | Rotation continue : une clé tous les ≤125° ; il faut ≥3 clés intermédiaires par tour | **nuancé** | Clés du Torso 70, 73, 76, 80, 85, 90 : écarts 3-5 images, confirmé. Angle géodésique réel entre clés : 49, 101, 114, 121° (tous < 180°). Lacet projeté : +53, +117, +105, +125°, identique au lecteur. | Mesure et explication (chemin le plus court) cohérentes. Mais le calcul est faux : pour 360° avec des segments < 180°, il faut au minimum 3 segments, donc **2 clés intermédiaires**, pas 3. TSB en met 3 (4 segments), par marge. |
| 7 | Accroupi d'élan tordu et asymétrique | **nuancé (lecture des bras fausse)** | Chiffres justes : hanche 2,28, lacet +31, penché +28, côté +14, bras droit axes torse az +137 el -60. Rendus sb_crouch.png (i0/i5/i10, 4 vues). Bras gauche : axes torse az -15 el -25, repère du coup az -58 el -46. | el -60 veut dire que le bras droit pointe VERS LE BAS (derrière, sur le côté), pas « en haut ». Le bras gauche est az -15 dans les axes du torse, donc vers l'AVANT-bas-côté, pas « en arrière ». Au rendu, les deux bras sont écartés vers l'extérieur et sous l'horizontale, suivant la torsion : un vers l'arrière-droite, l'autre vers l'avant-gauche. Poings à ±2 studs du torse sur le côté. |
| 8 | Une silhouette par acte ; diagonale finale tenue 0,5 s | **nuancé** | cr_sil.png (i10, 30, 61, 76, 80, 84, 90, 95, 120 ; face, profil, dessus). Hauteur de la main gauche : 5,31 à i95, puis 5,10 (i98), 3,07 (i112), 3,76 (i128) ; hanche ~2,0. | Les silhouettes par acte sont vues (fente, dos, mains jointes en haut, jet à i95). La « croix horizontale » est en fait une BARRE à un seul côté : les deux bras sont joints et tendus du même côté, pas une croix. La diagonale « un bras au ciel » n'existe qu'autour de i93-i98. La tenue i107-i128 est une AUTRE pose, tassée : le bras gauche est redescendu en travers au-dessus de la tête, à ~1-1,7 stud au-dessus du centre du torse. C'est la pose de sortie, pas la diagonale. |

Autres apprentissages contrôlés au passage (hors des 8) :
- n°2, chute en segments : chiffres **confirmés** (hauteurs 122,16 / 98,92 / 42,37 / 19,25 / 10,89 … 3,53 ; ~308 studs/s de i63 à i74 ; écarts 6…24). « Sans easing » est **invérifiable** : le chargeur ignore l'EasingStyle des Pose.
- n°4, X de bras : **confirmé** (poing droit côté gauche -0,9, poing gauche côté droit +0,72, bras droit az -86 / bras gauche az +80 dans les axes du torse).
- n°13, segment cuit : **confirmé** (i0-i11 toutes parts à chaque image, courbe du Torso en sortie douce -0,11 … -0,72 ; tête i0-i22). ETUDE_TSB.md l.25 à nuancer.
- n°10, placement du rig : comptes **confirmés** (T 30, H 12, BD 13, BG 20, JD/JG 28). Mais « les parts ne bougent jamais toutes en même temps » est **faux** : i0, i13, i22, i33, i55, i73, i112 et i128 clent toutes ou presque toutes les parts sur la même image. Le décalage d'une image (BG i101/106 contre T i102/107) est ponctuel. Jambes : écarts jusqu'à 9 images (i76-i85), pas 3-7.
- n°12, poids à la frappe : hanche 1,94 à i90, **confirmé**. En revanche, le buste n'est PAS « le plus penché » à i90 : 55° à i90, **66° à i92**, 57° dans la tenue. Et à i90 les pieds sont à **-0,43 / -0,74 stud, sous le sol** : une partie de la « descente du poids » est le corps qui s'enfonce dans le sol, pas une flexion.

### Oublis importants (visibles dans les sources, absents des notes)
1. **Les bras de Stoic Bomb dérivent par TRANSLATION** (Pose.Position des épaules re-clée à i90 et i141) : une technique de « tenue vivante » qui ne touche pas les rotations. Le lecteur n'a comparé que les rotations.
2. **Pénétration du sol assumée** : pieds à -0,18 (Stoic Bomb i216-i220) et jusqu'à -0,74 (Collateral Ruin i90). Le pro laisse les pieds passer sous le sol à l'impact pour vendre l'écrasement. À connaître avant d'imposer un contrôle strict « pieds ≥ 0 » à nos anims.
3. **Micro-remontée avant la chute finale** de Stoic Bomb : hanche 3,53 → 3,60 entre i205 et i209, puis chute à 2,60 en 7 images. Une anticipation de 0,07 stud.
4. **La sphère noire pulse à ~10 Hz** (toutes les 3 images vidéo), en alternance avec un flash blanc (f126-f149) : la cadence de la vie apportée par les effets est deux fois plus rapide que noté.
5. **Les marqueurs sont sur des Keyframes vides à des temps hors grille** (1,1221 ; 1,5037 ; 3,4242 ; 1,2554 s…), distincts des Keyframes de pose. D'où les doublons « i90 », « i205 » dans les listes : ce ne sont pas des clés de pose.
6. **L'anneau rouge plein cadre (f168) précède le marqueur FinalBoarExplosion** d'environ 0,08 s. Soit l'effet est lancé par HitboxExplosion? + délai, soit le recalage t0 a 2 images d'erreur. À ne pas figer comme « effet = marqueur à l'image près ».
7. **Pendant tout le dôme, le mannequin est collé au joueur** (f106-f149) : il porte encore sa barre, à la même échelle. Soit il a été emmené dans le saut, soit il est lui aussi en l'air. Son anim n'est pas dans le fichier, et c'est un indice majeur (saisie ?) que le lecteur mentionne sans l'exploiter.
