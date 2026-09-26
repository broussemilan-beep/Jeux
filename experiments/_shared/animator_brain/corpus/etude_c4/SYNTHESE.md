# Chantier 4 : synthèse. Un cours d'animation R6, appris en regardant

2026-09-26. Rédigé après la lecture complète des 12 notes de `corpus/etude_c4/`
(A1-A4 : fichiers exacts TSB et pack ; B1-B4 : tutos ; C1-C4 : vidéos, GIF,
images, goût de Milan), de leurs « Vérifications adverses », et de
`corpus/recherche/depots_yeux_2026-09-26/SYNTHESE_YEUX.md`.

**Comment lire.**
- Ce sont des apprentissages situés : « ici, tel animateur fait X parce que Y ».
  Aucune règle. Quand deux sources se contredisent, les deux restent écrites.
- **Les chiffres sont ceux de la vérification adverse** quand elle corrige la
  prose. La prose arrondit : surtout vers le haut (A4 verif, « biais
  systématique » : 1,4 / 162 / 57 / 164 / 178), mais aussi vers le bas (tête
  de M1 37° pour 50°, A1 V4). Le sens de l'erreur n'est donc pas prévisible.
- Repères de source : `A1 §1.1` = section de la note ; `A1 V2` ou `A1 verif 2` =
  point 2 de sa vérification adverse ; `i` = image à 60 i/s d'un fichier .rbxm ;
  `s` = seconde d'une vidéo.
- Registre de chaque apprentissage : **[JEU]** (M1-M4, pack battleground,
  caméra du joueur, jambes laissées à la marche), **[CINÉ]** (caméra écrite,
  coupes, cartes : Stoic Bomb, Ultimate1, combo au mur, Pew, GIF Serious Punch,
  anime), **[LES DEUX]**. Milan (C4 §3.8, l.215, orthographe d'origine) : « tsb
  est très bien masi faut uasis distinguer quelque chose on fais bcp de
  cinématique et ya bcp de ref qui sont en vision jeux ».
- Aucune image de référence dans le dépôt ; les deux images de preuve sont les
  nôtres (v6), dans `captures/verification/`.

---

## 0. En une page : les 12 choses les plus importantes comprises

1. **En linéaire, l'espacement des clés EST la courbe de vitesse.** [LES DEUX]
   Les 7 coups courts de TSB sont 100 % Linear (Enum décodé, A1 V2 ; les
   seules poses Constant du fichier, 67, sont dans WallComboPlayer, et
   Ultimate2 est cuite) ; dans M1, l'amorti se fait en espaçant les clés
   (0, 6, 8, 10, 14, 20, 26 ; torse 42°, 34°, 16°, 19°, 7°). La chute de Stoic
   Bomb (ciné) est une décélération faite de segments de 6 à 24 images (A2 §3,
   verif ; que ces segments soient Linear n'a PAS été décodé pour Stoic Bomb :
   « invérifiable », A2 verif).

2. **La vitesse se lit par contraste, pas par quantité.** [LES DEUX] Le poing
   de M1 passe de ~15 studs/s à 66 en UNE image puis tient un palier 67-73
   (A1 V2) ; Collateral Ruin : préparation 11-37 studs/s, seul moment rapide
   ~20 images (i74-i94), main gauche de ~50 à ~81 studs/s (A2 verif 5 ; le
   « 73-119 » de la prose ne vaut pas pour les deux mains). Sur le forum,
   ZensStarz, en accélérant la montée du poing sur un conseil, obtient
   « a spasm », puis ralentit le départ et finit sur un « jolt » (B3 §B3.2,
   verif 5) ; mais un passage lent→rapide trop brutal est aussi critiqué
   (OofDestroyer25, à propos d'un rechargement d'arme, B3 verif 5).

3. **Les parts partent souvent ensemble et s'arrêtent en décalé.** [LES DEUX,
   nuancé] Dans M1, le bras libre s'arrête vers i8, le poing à i10-14, le torse
   à i20, la tête glisse jusqu'à i26 (A1 §1.1, 5.2 ; tableau des parts confirmé
   A1 V3, mais la tête n'est pas posée à l'armé i6 : le départ n'est pas
   entièrement groupé). Mais ce n'est pas « la »
   méthode pro : Ultimate1 décale surtout les bras (la tête tombe sur une clé de
   torse 35 fois sur 46), et WallComboPlayer pose des clés complètes (A3 verif 2).

4. **La tête vise : elle contre-tourne le buste et regarde vers le bas.**
   [LES DEUX ; mesures toutes en JEU, le côté ciné n'est que vu sur des
   captures] Buste 137-162° contre tête 9-23° dans le monde (pack M1_1, M1_2,
   M1_4, A4 verif 1 ; M1_3 fait exception : buste 55°, tête 28°) ; marche :
   tête 0,0° pendant que le buste tourne de 33°. Dans les M1 mesurés, elle est
   baissée de -12 à -31° en élévation MONDE (C4 §2.2, §7.1, verif 2).
   Exceptions : l'uppercut du pack (la tête suit le lacet), les réactions (la
   tête bouge plus que le buste), TSB M4 (+17°, buste renversé), pack M1_1
   (part de 0°) (A4 verif 1, C4 verif 2).

5. **Qui bouge en premier dépend de qui reçoit la force.** [LES DEUX] Coup
   donné : buste et bras qui se retire d'abord, poing 2-3 images après (pack
   M1_2, M1_4, A4 §3.2). Coup reçu : souvent la partie frappée d'abord (Hit 2,
   Hit 3 ; pas Hit 1, A4 verif), puis le buste, puis les bras ; la victime du
   combo au mur change d'ordre selon le coup (A3 verif 8).

6. **Un combo de jeu est un balancier : la fin du coup N est l'armé du coup
   N+1.** [JEU] Écart 0,0000 entre la fin de M1 et le début de M2, de M2 et
   M3, de M3 et M4 (A1 V1) ; le torse oscille de 110-118° d'un côté à l'autre
   (M4 finit à +23°, pas +60°, A1 V1). Le pack fait presque de même : écarts
   de 0,000 à 0,30 selon les clips (M1_3→M1_4 : 0,29, A4 verif 2).

7. **Dans les cinématiques étudiées, le contact est le plus souvent masqué ou
   stylisé, rarement retiré ; le trajet, lui, peut être montré.** [CINÉ ; la
   dernière phrase est JEU] Contre-exemples : Xoaterz montre une image de
   contact (B3 verif 1), le GIF du Mii ne cache rien (C3 verif 1). Pew : la carte est la scène 3D
   passée en noir/blanc inversé, 7 images, silhouette visible (C1 verif 1).
   Ippo : le blanc est un voile sur une pose de passage réellement animée
   (C3 verif 2). GIF Serious Punch : le poing voyage LENTEMENT vers l'objectif
   0,6 s dans la fumée ; ce qui est court, c'est l'aboutissement (C3 verif 1).
   En jeu, la caméra ne coupe pas : le coup se lit de dos par la torsion du
   buste (A4 §1.4) et par un aplat de couleur d'1 image (C2 §1, verif).

8. **Tenir une pose, c'est décider QUI porte la vie.** [CINÉ : toutes les
   sources de ce point] Les bras de Stoic Bomb ne changent plus de rotation
   pendant ~3,2 s (i57-i249, A2 §2.1 ; recontrôlé de i57 à i141), mais leurs
   épaules glissent de 0,3-0,5 stud et une sphère pulse toutes les ~0,1 s
   (A2 verif 3) ; Ultimate1 superpose
   4-5 dérives lentes et une pulsation (A3 §1.3) ; chez Pew c'est la caméra
   (C1 verif 2). Mais le gel total existe aussi (All Might figé 1,0 s, B4 V5).

9. **L'animation porte l'horloge des effets.** [LES DEUX] TSB pose des
   KeyframeMarkers (`hitreg`, `StartHitbox`, `BeginSlowing`, `SpeedLinesStart`,
   `ChargingSound`…), souvent sur des clés VIDES créées exprès, hors des clés
   de pose (M1 `end`, M2 et M4 `hitreg`, Stoic Bomb : A1 V5 et oubli 2, A2
   oubli 5) ; pas toujours : le `hitreg` de M1 est sur la clé de pose i10.
   Le cerveau ne les avait jamais lus.

10. **Où l'on place le rig en R6.** [LES DEUX] Tout déplacement passe par la
    translation du Torso (la racine est un conteneur, A3 verif 3). Les membres
    se TRANSLATENT (lecture : pour faire ce que coude et genou absents ne
    permettent pas, « faux genou » A4 §1.3, bras allongé A4 oubli) : bras de M1 TSB de
    0,3 à 0,9 stud (B3 verif 2), bras du pack 1,2-1,7 stud (A4 oubli), jambe de
    course relevée (A4 §1.3), pop de M1_2 par un saut de translation de 1,9
    stud (A4 verif 3). Jambes : laissées à la marche en M1, posées ailleurs
    (TSB M4, Stoic Bomb, downslams).

11. **La méthode de travail va du grand au petit, et se juge en mouvement.**
    [LES DEUX] Chez trois auteurs de tutos : torse seul d'abord, puis bras,
    tête, jambes (B1 verif 1 ; Xoaterz B3 §A3, ordre non linéaire selon B3
    verif ; myloe B2 §4.2) ; plusieurs passages ; contrôle de profil,
    fantôme de la clé d'avant, rig lettré par face ; timing en dernier, par
    compression (B2 §4.2) ; versions multiples, animatic, référence collée à
    côté (C1 §1.1 B, E10).

12. **Les plaintes les plus constantes de Milan portent sur d'où part le poing
    et sur le corps entier ; il envoie des instants + une carte.** [LES DEUX] Ses plaintes de trajectoire
    courent du 09-03 au 09-26 : « du bas » (6 fois) et « de derrière » (C4 verif
    6). Son storyboard du 09-03 : ramassé, carte, extension vers le lecteur
    (C4 §1.3). Ses rares éloges portent sur une idée de mise en scène, le jeu
    aérien, la caméra, les progrès ; aucun ne cite un chiffre (C4 §3.7 ; mais
    C4 verif 7 : la lecture « les notes montent avec la mise en scène » est en
    partie fausse).

---

## 1. Le cours

### (a) Comment un animateur R6 travaille

**L'ordre de pose : du grand au petit.** [LES DEUX] Dans le tuto « SMOOTHLY »,
l'animateur pose le torse seul (bras et jambes collés) et le rejoue jusqu'à ce
que la ligne du corps raconte le coup, puis le bras passif, le bras qui frappe,
la tête, les jambes en dernier (B1 §2.1, verif 1 : titres lus à 303, 305, 384,
555, 635 s). Lecture (pas dite par l'auteur) : en R6 le torse porte tout, le
corps devient un bâton dont on règle la ligne d'action. Xoaterz commence aussi par le torse
(3/4 puis inclinaison franche), translate la jambe libre, place les bras sur la
diagonale, et revient en arrière si besoin (B3 §A3, verif). myloe (Blender) fait
torse, bras, tête et jambes en plusieurs passages (B2 §4.2).

**Ce qu'il pose d'abord dans le temps.** myloe pose la charge seule avant tout
timing, espace largement ses poses (0, 20, 40, 80) puis les rapproche (40→30,
80→60, vu sur la dope sheet à 222-236 s) (B2 verif 2). Temps arrêté recompté :
charge + fin de charge 271 s, retour 184 s, contact 131 s ; bras 218 s, jambes
192 s (B2 verif 1-2 ; temps passé avec l'os SÉLECTIONNÉ, pas forcément
manipulé). Il passe plus de temps sur ce que l'œil voit longtemps (charge
0,57 s, après 0,40 s) que sur l'image de contact (une image vidéo) (B2 verif 2
et 4).

**Les outils de regard.** [LES DEUX] Le rig lettré par FACE (F rouge, B bleu, R
vert, L jaune, U cyan, D orange) pour lire l'orientation d'un bloc sans visage :
un bras dont on voit la face D pointe vers la caméra (C1 verif 4 ; C4 §1.15). Le
fantôme de la clé d'avant, et celui de la clé 0 pour ce qui doit rester fixe
(pieds) ; un rayon de regard jugé loin au sol (B1 §2.1). La vue de profil stricte
(B2 §1.2), la caméra au ras du sol pour l'appui et la ligne d'équilibre tête-pied
(B3 §A3, §A5), la trajectoire affichée (C1 verif 6), le ralenti x0,25 et l'image
par image : « On what frames does the object change […] This is literally the
core of animation » (spelled_ayayron, B3 §B2).

**Versions et préparation.** [CINÉ surtout] Chez TSB : versions assumées (Last
Breath v1-v4, Earth-Splitting miss / rough / propre), un animateur qui fait la
victime (« I did Victim :D »), une référence collée dans le coin, un animatic en
bonhommes minuté et rejoué, des effets provisoires recyclés (C1 §1.1, verif 6).
« Corps en plan fixe, puis caméra » n'est pas universel : Last Breath v4 brut est
déjà coupé (C1 verif 6). Hypothèse : M3 et M4 ont été posés 1,5 fois plus lents
puis compressés (clés « entières à 60 » toutes paires ; écart ±0,0125 inexpliqué,
A1 V6).

**Deux fabrications chez le même studio.** Clés éparses en Linear (M1-M4,
Ultimate1), cuisson une clé par image (Ultimate2), hybride (WallComboVictim cuite
dès f132), segment cuit dans une anim à la main (Stoic Bomb i0-i11), rafale en
Constant (WallComboPlayer) (A3 §0.2, verif ; A2 §3). Le « style TSB » n'est pas
une interpolation, c'est une façon d'ordonner les parts (A3 §2.4). Piège : nos
outils interpolent tout en Linear et n'avaient jamais décodé l'EasingStyle (A3
§0.3 ; A1 oubli 1).

### (b) Poses et silhouettes sur un rig à blocs

**La ligne d'action s'obtient en alignant des blocs, en directions monde.**
[CINÉ] Les dessins que Milan envoie (OPM, MHA, Goku) font une seule diagonale du
pied arrière au poing. Dans l'essai en blocs de C4, un buste tourné de 55° puis
« penché dans ses axes » ne penchait pas vers la cible ; il a fallu décomposer
le penché (≈26° avant + ≈37-40° de côté) et viser le bras dans le monde (C4
§7.2, verif 3). Le lien avec « part du bas » reste une hypothèse non mesurée. La jambe R6 fait 2
studs : posée par direction (az 180, el -35, hanche 2,0), elle prolonge le buste
et la ligne casse à l'épaule en « éclair » (C4 §7.3, verif 4).

**Compact à la charge, une ligne à la frappe, le X pour la victime.** [LES DEUX]
Baki, Gon, Saitama de dos, Pew, TSB a54 : attaquants compacts ; la victime
projetée de 5b6ab8d1 est en X (C4 §2.4). Mii : charge ouverte, armé FERMÉ (épaule
cachée), frappe ouverte ; pendant l'armé, le bas avance vers la cible pendant que
le haut s'enroule (C3 R7, verif 5). Black Hole oppose fermé et ouvert quatre fois
(C2 §4). Xoaterz reproche « boring sameside posing », « looks like a stickman »,
mais aussi « asymmetric posing » : le défaut est la pose non motivée (B3 §A4,
oubli). Dans les ~6 images regardées, le 2e bras a chaque fois un rôle
différent de l'autre, pas le miroir (hanche, main ouverte, rejeté derrière,
caché devant ; Pew : les deux devant) (C4 §2.6).

**L'armé est dans le tronc.** [LES DEUX] Combo Moon : un demi-tour du torse avant
chaque coup, dans un sens qui alterne (C3 verif 6) ; Rock throw : FRONT→BACK en
~3 images source (C1 verif 8) ; GIF Serious Punch : genou haut, dos à la caméra
(C3 §1). Milan, dès le 09-03 : « tourné son buste […] plier les jambes le légèrement
le 2e bras placé et boum il envoi » (l.43, C4 §3.1).

**Ce que voit chaque caméra.** [LES DEUX] À 9 studs et 40° de champ, seul le
profil lit la ligne ; de face, le bras qui vise la caméra est un carré (C4 §7.4).
Mais 5be18338 (R6, de face) se lit bien parce que la caméra est collée au buste :
c'est la tête, la plus proche, qui grossit (C4 verif 5). D'après un calcul
géométrique (déduit, pas rendu), le poing énorme des dessins demanderait une
caméra à ~1 stud du poing et 15-30° de 3/4 (C4 §2.3). De dos, on lit la torsion du
buste et le bras qui se retire plus que le bras qui frappe (A4 §1.4, §3.9 ; C4
verif 5).

**Exagérer la lecture, pas les angles.** [LES DEUX] « if an animation isnt
exxagerated enough it looks terrible, especially for r6 » (B3 §B2) ; Milan veut
une anatomie de manga et refuse « le pose des jambe est un peu trop abusé »
(l.195, C4 §3.3).

### (c) Temps, espacement, clés

**Linéaire, paliers, claquements.** [JEU] M1 : dérive ~15 studs/s, une image
pour passer à 66, palier 67-73 sur 4 images, puis 36-37, puis 6-7 (A1 V2) ; M2 :
78-80 sur 3 images ; M4 : claquement d'une image du pied (88,5 studs/s), jambe
horizontale seulement f13-f14 (A1 V7). Le poing droit (bras dit « qui
recule ») va aussi vite que le poing qui frappe pendant 2 images, 64-71
studs/s (A1 V2) ; mais B3 verif 2 note qu'en azimut ce bras avance lui aussi
(az -19 → +113) : ce qui recule, c'est l'épaule droite. Dans le pack M1_4, le
bras qui se retire va plus vite que le poing (103 contre 63, A4 §1.4).

**Les clés se resserrent vers le contact.** [JEU] M4 : écarts de 5,3 / 4,0 / 2,7 /
1,3 images ; le `hitreg` tombe entre deux clés (B4 V2). Dans M1, la frappe occupe
i6-i10, le `hitreg` est à i10, et le grand balayage du bras vient après (B2
verif 5).

**Clés sélectives.** [JEU] M1 : à i10 torse et bras qui frappe seuls ; à i20
torse seul ; tête à i0, i8, i14, i26, pas à l'armé (A1 V3). M4 : claquement posé
sans les bras, qui filent pourtant à 57-68 studs/s portés par le torse (A1 V3).
Swift Sweep : tête non posée 40 images, sa vie est une seule interpolation (A1
oubli 6). Le débutant DeHapy pose 5 colonnes alignées sur Torso, bras et
jambes, écarts irréguliers ; la piste Head n'a aucune clé (B3 verif 3).

**Rotation continue.** [LES DEUX] Roblox tourne par le plus court chemin : un
tour complet demande au moins 3 segments de moins de 180°, donc 2 clés
intermédiaires ; TSB en met 3 (A2 verif 6).

**Grille de travail.** [LES DEUX] Moon : clés tous les 5, la clé « middle »
rapprochée du « drag » de 2-3 images (0, 5, 10, 12, 15…55) : une seule
compression brutale dans une grille lente (B1 verif 3). firytwig : « Keep the
inbetweens close to the chamber », « Don't ease out towards the main pose »,
« Even 1 frame of chamber matters » ; au kick, extension sans intermédiaire,
petit dépassement ; poing du lunge punch tendu ~0,07 s seulement (B1 §2.3,
verif 7 ; fichier à ~40 i/s variable, ±1 image source).

**Constant = poses qui claquent.** [CINÉ : combo au mur] WallComboPlayer : tenues de 5, 6, 8,
10, 8, 10, 8, 9, 6, 5, 5 puis 4 images, qui s'allongent puis raccourcissent vers
le coup ; à f352, tête et bras figés pendant que torse et jambes frappent (A3
verif 7). À vérifier dans Studio avant de copier (A3 oubli 6).

**Marqueurs.** [LES DEUX] `hitreg` au bout du segment rapide ; `SmokeSlash` en
pleine spirale, pas sur un coup ; `StartHitbox` / `EndHitbox` autour du seul
moment rapide de Collateral Ruin ; `TweenStuff` 6-8 images AVANT une arrivée,
`AwakenFinale` dessus (A1 §3 ; A2 §5 ; A3 verif 1). Un effet peut précéder son
marqueur (~0,08 s, A2 verif 4).

**Cadence dessinée.** [CINÉ] Dans l'anime, la cadence change dans le coup : JJK
ép. 19, anticipation en 3-3-2-3-3-2, trois images sur 1 (125 ms), contact
irrégulier (B4 V1) ; Yuta : dessin sur 3, caméra qui tremble sur 1 (B4 V3).
B4 §2 rapproche ça de la densité de clés mesurée sur M4 (écarts 5,3 → 1,3
images) : une analogie, pas une équivalence démontrée.

### (d) La frappe et le contact

**Ce qu'on montre.** [CINÉ] Surtout l'avant et la réaction. Xoaterz montre
pourtant l'image de contact (182,267 s), un 2e coup et ~1 s de vol de la
victime ; la « pose basse d'après » était la réception de la VICTIME (B3 verif 1).

**Ce qu'on cache, et comment.** [CINÉ] Filtre bichrome inversé sur la vraie
scène 3D, roches déjà dans la carte (Pew, 7 images, C1 verif 1, oubli 4) ; trait
blanc posé par-dessus des corps visibles (Sunrise) ; le bras en amorce devant la
caméra (Gojo) ; cases manga en rafales et tenues alternées (Slap, C1 verif 7) ;
voile blanc sur une pose de passage (Ippo, C3 verif 2) ; noir-silhouette puis
blanc, chaque carte avec son son grave à 1 image près, l'anticipation de
l'attaquant restant visible (IMPACT HAVEN, C2 verif 8, oubli 1) ; lueur du poing
qui balaie le cadre 7 images, visage de la cible qui anticipe (Nakamura, B4 V4) ;
silhouette désaturée avec croix de lumière, puis 1 blanc et 1 noir (Todoroki, B4
V6 : transposable en R6 par correction couleur + flares).

**Montrer le trajet lentement, c'est possible.** [CINÉ] GIF Serious Punch : le
poing voyage vers l'objectif 0,6 s dans la fumée, puis 1 image de contre-champ
(victime minuscule au fond), 3 cartes d'une image, un blanc qui se dissout
(C3 verif 1).

**Le point de contact se règle ; l'arrêt dépend du coup.** [LES DEUX] Le pro de
Milan pose le poing pile sur la tête du mannequin, image après image (B2 §2.3).
Le forum demande un arrêt net au contact (« freeze […] 2-3 frames »,
phantasmability ; « slight recoil », « move slightly forward to show the
momentum », d0cter_oof) ; LucensCat distingue crochet et direct, pas « touche ou
vide » (B3 verif 4).

**Le choc cuit, le sol traversé.** [JEU / LES DEUX] Swift Sweep : 5 clés à 1
image d'écart, torse qui alterne de ±0,06, pied qui dépasse d'une image (A1 §1.5,
verif). Pieds à -0,18 (Stoic Bomb) et -0,74 (Collateral Ruin) : le pro laisse
le corps s'enfoncer (A2 oubli 2 ; « pour vendre l'écrasement » est
l'interprétation du vérificateur).

**Hiérarchie par l'effet.** [JEU] M1 de nuit : anneau, anneau, smear, double
anneau (C3 §10) ; couleur réservée aux cartes du moment fort (C3 verif 8).

### (e) Tenir une pose

**Tenue vivante par superposition.** [CINÉ] Ultimate1 (f290-432) : clés de torse
tous les 4-12 images, écarts 0,3-8,2°, jamais 0 ; dérives de buste, tête, bras
et hanche (±0,015) ; une pulsation f356→361 (torse 8,2°, tête 10,5°) ; une fin
qui ramasse le corps avant de partir (A3 §1.3, verif 4). Cette pose est un bras
replié en travers de la poitrine : l'appeler « charge » plaquait notre coup
dessus.

**Tenue par translation, ou par autre chose que le corps.** [CINÉ] Stoic Bomb :
rotations des bras identiques de i57 à i141, épaules qui glissent de 0,3-0,5
stud, sphère qui pulse à ~10 Hz (A2 verif 3). Pew : corps quasi immobile, caméra
qui descend, fouette le ciel, fonce sur la tête (C1 verif 2). Rewind Clock : 2 s
de corps figés, caméra qui pousse de +35 % (C2 verif 4). Iczer : ~1,5 s de pose,
lignes et fond sur 1 (B4 V5). Goku : dessin « en 3 », cheveux et lumière (C3 §11).

**Le gel total existe aussi.** [CINÉ] All Might figé 1,0 s puis rafale sur 1 ;
débris de Yuta quasi figés 0,7 s (B4 V5, oubli 4).

**Dans les anims brutes, les « tenues » sont surtout des dérives.** [LES DEUX]
Psychic m1s : une seule tenue immobile (0,33 s), transitions de 4 à 8 images
(C1 verif 3). Crush : bras levé immobile 1,07 s, frappe 1-2 images, pose
immobile 1,0 s (C1 verif 3). Pack : tenues quasi mortes qui s'éteignent ; TSB :
poing qui dérive à 6-7 studs/s, torse à 0-1 (A4 verif 8).

**La fin de tenue prépare le geste suivant.** [LES DEUX] Black Hole : tenue de 4
images, puis les bras REDESCENDENT 6 images avant le jet vers le haut
(contre-anticipation, C2 verif 2). Les anims longues de TSB se ferment sur une
clé de repos pour le fondu ; la victime non (fin en plein vol, A3 oublis 1-2).

### (f) Deux corps

**La victime attend, puis répond en retard et en chaîne.** [CINÉ] WallComboVictim :
f8 identique à f0, pop d'une image à f9 (torse 14°, 1,16 stud, membres 37-48°),
bras jetés 2 images après (104° et 61°) ; au hit2, jambes f175, bras f176, torse
f179, tête qui finit 179→183 ; au hit3, rampe de 5 images et fin en plein vol
(A3 verif 8). Tenue en l'air : torse quasi immobile (8,2°/s), membres qui
tremblent (72-90°/s).

**La victime fait la moitié du travail.** [LES DEUX] « I did Victim » (C1) ; le
pro de Milan plie le mannequin autour du poing dans la même scène ; chez
f1b5bd4b, la victime se plie pendant les tenues de l'attaquant (B2 §2.1, §2.3,
verif). Swift Sweep (Victim) : repli en 5 images, tête lâchée à -83°, une seule
jambe recule, bras posés 2 images après le torse (A1 §1.7, V8).

**Qui mène.** [LES DEUX] Dans un échange, l'un tient pendant que l'autre agit
(Thundey), mais les deux bougent ensemble au contact : tendance, pas règle (B3
verif 10). Dans une prise, l'attaquant est le socle et la victime fait l'arc,
puis opposition verticale (Mythra, Blender, C3 B3).

**La conséquence peut arriver en retard, avec sa propre anticipation.** [CINÉ]
Gatling : ~1,4 s d'immobilité, frisson 0,2 s, pop blanc, départ en 0,15-0,2 s
(C3 verif 4). Sunrise : l'explosion part quand la lame rentre au fourreau, ~7 s
après la coupe (C1 verif 9). Le fichier ne dit pas où est la victime par rapport
au joueur (A3 §3.4).

### (g) Caméra et montage au service de l'anim

**Le montage accélère, puis donne un plan long avant le coup.** [CINÉ] Gojo :
plans de 1,07 → 0,27 s puis 1,27 s qui pousse vers le visage (C1 verif 7) ;
Sunrise : 12 coupes en 0,4 s puis 5,9 s ; Black Flash : creux lent de 0,5 s
avant le flash, coups d'avant sans accélération continue (C2 verif 6).

**Rideaux, échelle, sortie de cadre.** [CINÉ] Ippo change d'angle pendant les
flashs (vu sur 4 transitions, C3 §3, verif 2) ; le corps fait rideau (GIF TSB) ; letterbox = « on est en
cinématique ». Conséquence en plan très large, perso minuscule, longtemps (Pew
5,70-14,67 s, C1 §E4) ; Black Flash : poing au premier plan, victime minuscule
au fond, poussée lente 1,5 s (C2 verif 5) ; la charge filmée en morceaux (C1
§E3) ; le perso sort du cadre (Black Hole, C2 verif 7).

**Une coupe est un endroit où l'anim triche.** [CINÉ] Stoic Bomb : 145 studs en
une image, pile sur la coupe (f68 = i11) ; ce qui est le plus soigné (salto,
écrasement) est le moins visible, la charge plein cadre est presque figée.
Hypothèse : l'anim sert tous les joueurs, la cinématique le lanceur (A2 §3-4,
verif 1).

**La caméra peut sauver ou perdre une anim.** [LES DEUX] Selon le lecteur B3,
le court-métrage de DeHapy tient par ses amorces malgré une anim faible (B3
§5.9, jugement du lecteur) ; un torse qui
tourne peut « feel like facing the front » sur un rig d'une couleur (B3 §B2).

### (h) Jeu contre cinématique : ce qui change vraiment

| | [JEU] | [CINÉ] |
|---|---|---|
| durée | M1-M3 TSB 0,43-0,47 s, M4 0,69 s ; pack 0,65-0,70 s (A4 §2, verif 8) | charges de 0,5 à 5 s (Pew ≈5 s, C1 §1.2) |
| jambes | laissées à la marche en M1 (« take a look at battlegrounds games », B3 §B2) ; posées pour M4 (A4 verif 8) | posées : fente, jambe arrière, appui (B2 §5.1) |
| caméra | du joueur, de dos : on lit la torsion du buste (A4 §1.4) | écrite : coupe, amorce, échelle, trajet montré ou masqué |
| contact | pas de coupe : aplat d'1 image sur le corps, puis effet (Black Flash en jeu, corps de ~30 px, C2 oubli 4) ; `hitreg` dans l'anim | carte, voile, filtre, cases, contre-champ |
| triche | rien n'est déclarable (SYNTHESE_YEUX rang 6) | une pose peut tricher pour un plan (A2) |
| membres détachés | 0,3-0,9 stud en M1 TSB (B3 verif 2, 9) ; mais 1,2-1,7 stud dans les M1 du pack (A4 oubli) : pas « modérés » partout | acceptés pour exagérer (B3 §B2) |
| vitesse | « hit frames […] within the first 30-40 » (xnSly) | « if it's some animation or scene then it's fine » (isaiahbur) (B3 §B4) |
| dash | pose figée pendant que le script déplace, arrivée qui claque (A4 §1.8, verif 4) | non démontré dans la racine (C1 verif 5) |

Ce qui ne change pas : la tête qui vise, le buste qui porte le bras, le bras qui
se retire, la victime qui répond (A4 §2). Et Milan juge avec les mêmes mots dans
les deux registres (C4 §3).

### (i) Le goût de Milan (ses mots, orthographe d'origine, `milan_verbatim.jsonl` ; C4 §3 et §7.6, B3 §4)

- **Le corps entier.** « Tu oublies de utiles les jambes le peros est cense
  tourné son buste vers la droit charger sont moins droit plier les jambes le
  légèrement le 2e bras placé et boum il envoi » (l.43) ; « enft tu as a anime
  que les bras encore une fois » (l.169).
- **D'où part le poing.** « on dirait que le coup pars du bas alors que il doit
  allez droit » (l.44) ; « les coup parte tjrs du bas […] on dirait un
  enchainement d'uppercute mais en meme temps coup droit » (l.109) ; « le coup
  ne doit pas parti de derrière mais le bras se déboîte vers l'arrière et avance
  vers l'avant, ne te fis pas une animation humaine » (l.54) ; « dans aucune le
  bras est tendu derrière » (l.195). Mais aussi « le perso charge son poing à
  son arrière droit » (l.41) : il refuse le bras TENDU derrière, pas la charge à
  l'arrière droit (C4 verif 1 et 6). Son « déboîtement » ressemble à la
  translation d'épaule mesurée chez TSB (C4 §3.2, jamais vérifié avec lui).
- **Manga, pas gym.** « tu abuse pas assez le mouvement style manga » (l.10) ;
  « même un coup simple n'est pas coup simple genre y'a une anatomie et une
  règle différente » (l.133) ; « la règle de l'animation Disney jsp quoi ça ne
  fonctionne pas » (l.133) ; « le pose des jambe est un peu trop abusé » (l.195).
- **Lisibilité, puis vitesse.** « C bcp trop rapide on ne lit pas assez les
  mouvement » (l.34) ; « Ça manque de frame d'un début et d'une fin » (l.80) ;
  « le moment ultra rapide très bien » (l.191).
- **Accroupi.** « il esr accroupis er pas en trasnfere de poids » (l.102).
  Lecture de C4 §7.6 (déduite, jamais vérifiée avec lui) : il rejette rester
  bas PENDANT le coup, pas la charge basse.
- **Le style.** « dessiné », pas « peinture » (l.179, l.183) ; « c trop cubique »
  (l.181) ; « premium » ; les yeux (l.181).
- **Sa posture.** « nz prends pas mes parole pour de regle mais comme des piste »
  (l.113) ; « je suis pas expert mais j'ai l'œil » (l.172) ; « tu crée pas de
  règles grave dans la roche » (l.199).
- **Comment il regarde.** Ses 3 captures du 09-25 sont en pause, deux à
  0,5x (qu'il a choisi : le défaut est 1x) et une à 1x (C4 verif 8) ; il
  envoie des instants (C4 §3.6) ; il note l'ensemble : « le bras ne part
  pluq d'en bas mais ne change pas la note » (l.113) ; note globale 4 le 09-25 (l.176,
  C4 verif 7).
- **Sa critique est celle d'un animateur.** Ses retours ont des équivalents
  proches dans le forum (Q1-Q19, B3 §4), « presque mot pour mot » exagère (B3
  verif 6).

---

## 2. Ce que le cerveau croyait et qui est démenti

Liste des corrections relevées dans les 12 notes (après vérification adverse).

| Fichier corrigé | Ancienne lecture | Lecture vérifiée | Source |
|---|---|---|---|
| `ETUDE_TSB.md` §1 | seules Ultimate2 et WallComboVictim sont cuites ; ~98 % Linear | Stoic Bomb a un segment cuit (i0-i11, tête jusqu'à i22) ; WallComboVictim est hybride (cuite dès f132) ; WallComboPlayer a 67 poses Constant ; les 7 coups courts sont 100 % Linear (Enum décodé) | A2 §6.5 verif ; A3 §0.2 verif ; A1 V2 |
| `ETUDE_TSB.md` §4 bis | M4 : jambe horizontale f9-f15 | monte en diagonale f0-f12, horizontale f13-f14 après un claquement d'une image, petit saut +0,48 | A1 V7 |
| `ETUDE_TSB.md` §4 | Ultimate1 : « un bras qui bouge », tenues de 58, 35, 21 images | deux bras, buste 86°, recul 1,5 stud, un pas ; trois longues tenues mouvantes (≈170, 142, ≈60 images) | A3 §1.5, verif |
| `ETUDE_TSB.md` §4 | Stoic Bomb : « plongeon corps à l'horizontale » | salto qui part tête en bas (penché +158°) à l'apex | A2 §6.4 |
| catalogue / `ETUDE_ARCHIVE` | Stoic Bomb : dôme vu de dessus (sans plus) | dans le repère de l'anim, les pieds passent de 8,0 (i90) à 0,65 stud (i205) ; contact vers i213. « Il flotte » suppose que la HumanoidRootPart reste au sol (invérifiable) ; la vidéo ne permet pas de le voir | A2 §6.2, verif 2 |
| `ETUDE_ARCHIVE_VIDEOS_1` | Stoic Bomb : saisie en caméra de jeu 0-2,2 s | aucune saisie visible, joueur immobile jusqu'à 2,07 s ; mais le mannequin reste collé au joueur pendant le dôme (indice non exploité) | A2 §6.3, oubli 7 |
| `ETUDE_ARCHIVE_VIDEOS_1` | Pew : fouetté 3,3-3,5 s, carte 6,2-6,3 s « 2 images », coupe large 6,7 s | fouetté 2,27-2,60 s, carte 5,133-5,333 s (7 images, filtre sur la 3D), coupe large 5,70 s | C1 §3.1, verif 1 |
| `pro_tsb_m1_m4.json` | poses de poids 0 lues (fausses pointes) | bug corrigé dans `corpus.py` l.60-66 | A1 §0 |
| `pro_pack_battleground.json`, `fiches/VFX.md` | le chargeur ne lit pas les KeyframeMarker ; marqueurs connus seulement par le web | 35 marqueurs réels dans le .rbxm TSB, souvent sur des clés vides (pas le `hitreg` de M1) ; pack : marqueurs non lus, présence inconnue (A4 §0) | A2 §6.1, verif 4 ; A1 V5 |
| `corpus.py` / outils | Linear partout, EasingStyle jamais décodé | les poses Constant sont dessinées fausses entre les clés | A3 §0.3 ; A1 oubli 1 |
| `corpus/README.md` §3 | « tête pro 84° contre 25-30° chez nous : nos têtes bougent trop peu » | ces degrés sont de la contre-rotation pour que le regard ne bouge PAS dans le monde | A4 §3.1, verif 1 |
| `CARNET` / `REFERENCES_VIDEO` | contre-rotation de tête dans l'uppercut | l'uppercut du pack ne la fait pas : la tête suit le lacet (pas « vers le haut », élévation ≤ +7°) | A4 §4, verif 1 |
| `CARNET` 4.2 | « le gel reste un gel » | les tenues d'anime ont souvent une couche qui vit, mais le gel total existe aussi (All Might 1,0 s) : nuance modeste | B4 E3, V5 |
| `CARNET` l.459-461 | « Regarder devant, menton levé » | peut-être l'origine de la tête relevée de v6 ; les pros regardent -12 à -31° dans le monde | C4 §2.2 |
| `rapport_anime3d` | impact frames dessinées IMPOSSIBLES ; smear étiré IMPOSSIBLE | possibles en 2D par-dessus ; un smear-forme opaque qui remplace le membre est faisable | B4 §4.2-4.3 |
| étude Iczer existante | armé tenu ~2 s, poing plus gros que le buste | pose stable ~1,5 s, poing au moins aussi gros que la tête | B4 §4.4, V5 |
| `rapport_video_critique_poses.md` | Règles R1-R8, dont « bras armé derrière l'épaule » | une méthode de travail, à relire comme des questions ; le bras court de la pose ✓ est en raccourci : « replié » ou « tendu en profondeur » invérifiable | B3 §7.1-7.2, verif 7 |
| `etude_complete_dehapy.md` vs `rapport_video_critique_poses.md` | bras « tendu devant » contre « ramené derrière » | chacun décrit sans doute un bras différent ; non tranchable sur une image fixe | B3 §A4, verif 7 |
| `ETUDE_NOTES_BRUTES` (Black Flash) | « ralenti en gros plan sur la victime ensanglantée » | le bras tendu de l'attaquant au premier plan, la victime minuscule au fond | C2 §1, verif 5 |
| `ETUDE_NOTES_BRUTES` (Rewind Clock) | « 2 s de coups » | un contact figé 2 s, seule la caméra et les lueurs bougent | C2 §2 |
| `ETUDE_NOTES_BRUTES` (IMPACT HAVEN) | cartes blanches/noires de 2 f | 1 noir (silhouette) + 1 blanc dans 17 cas sur 19 ; exceptions 3,467 et 9,167 s | C2 §5, verif 8 |
| `ETUDE_NOTES_BRUTES` (Black Hole) | « se ramasse en regardant en haut » | la tête plonge pendant l'enroulement (confiance moyenne) ; puis contre-anticipation des bras, pas un tremblement | C2 §4, verif 2 |
| notes lot 3 (gatling) | anneaux de fumée puis « retour à la garde » | pas de retour : pose de fin tenue ≥ 2,2 s (le GIF est coupé), victime qui part ~1,4 s après | C3 §4, verif 3-4 |
| notes Ippo | « BLANC total à 1,4 / 5,0 / 5,8 / 8,4 » | au moins 11 blancs ; le blanc est un voile sur une pose de passage | C3 §3, verif 2 |
| `CATALOGUE_REFS` (Serious Punch) | « garde tenue 32 f » | pose NEUTRE, bras tombant, ≈1,07 s | C3 §1 |
| `fiches/UN_SEUL_COUP.md` | « frappe 5,2-5,9 s poing vers l'objectif (0,8 s) » ; conséquence « fente, poing en avant » | 5,07-5,27 s = retombée du genou ; poing qui voyage lentement 0,6 s dans la fumée ; à la fin, bras plié à l'horizontale devant le buste (confiance moyenne) | C3 §1, verif 1 |
| relecture 09-25 (aafdc91d) | pause de 0,3 s | 0,45 s | C3 §5 |
| relecture 09-25 (Mii) | torse presque horizontal ; trait violet = trajectoire | torse plutôt droit ; le trait est un élément du visualiseur | C3 §7, R7 |
| `CATALOGUE_REFS` d2fda413 | « Saitama en ombre » | le visage géant est Saitama ; la petite silhouette n'est pas lui (Boros selon la prose C4 §1.7, Genos selon la vérification, sans justification : non tranché) | C4 §1.7, verif |
| `CATALOGUE_REFS` 0ca551a4 | Deku, poing tendu | main OUVERTE, bras plié qui traverse | C4 §1.5 |
| cerveau (aucun lien) | « déboîtement » de Milan = ? | correspond à la translation d'épaule mesurée chez TSB (non vérifié avec lui) | C4 §3.2 |
| études tuto « SMOOTHLY » | intro : un perso seul ramassé contre le mur | deux personnages, trois impacts | B1 §4 |
| cerveau | frappe en 2 images, universel | deux régimes : coup unique après longue charge (myloe 60→62) et M1 de combo étalé (TSB) | B2 §5.3 |
| cerveau (texte du 04/09) | « anticipation 4-6 frames lentes, impact 1 frame » | plus proche pour un M1 sans être exact (TSB M1 : armé 6 images, frappe en palier de 4, A1 §2.5 ; psychic m1s : transitions de 4-8 images, C1 verif 3) ; en ciné, la tenue dure des secondes et l'impact est une carte | C1 §3.2, verif 3 |
| études « rig lettré » | couleur par membre | couleur et lettre par FACE et direction | C1 §3.3, verif 4 |
| études | le storyboard est une planche | c'est un animatic minuté, rejoué deux fois | C1 §3.5 |
| cerveau (convention) | « jambes au calque » chez TSB | vrai pour M1-M3 ; M4 pose les jambes (22 clés, 0,69 s) | A4 verif 8 |
| cerveau (contrôles) | pieds ≥ 0 toujours | les pros laissent les pieds passer sous le sol à l'impact | A2 oubli 2 |
| attente | sous-titres « TSB scrapped » = contenu technique | paroles d'une chanson | B4 §4.7 |
| attente | Ultimate1 = animation du Serious Punch | les poses ne collent pas ; marqueur « AwakenFinale » (« éveil » n'est qu'une interprétation du nom, A3 verif 1) ; modèle racine nommé « KJ » | C3 annexe ; A3 §0.1 |
| cerveau (juges) | un score automatique aide à juger | AnimationBench donne 4-5/5 à la v6 rejetée, mieux que TSB M1 ; temps d'écran changé v2→v3 (« aucun changement ») = v4→v5 (« un peu mieux »), 1,63 s chacun (pics 59 et 79 %) | SYNTHESE_YEUX §0, §6 |

---

## 3. Mes propres yeux

Ce que les exercices et vérifications ont révélé de mes erreurs de lecture, et
comment je m'en garde.

**L'exercice Stoic Bomb (A2 §1-2.3).** Prédiction écrite AVANT d'ouvrir le
fichier, puis comparée : accroupi court (juste sur le principe, raté la
torsion de 31° et l'asymétrie) ; saut + salto (juste pour le salto, raté le
saut : il est caché par une coupe) ; « chute avec un bras levé » (FAUX : avant-
bras croisés en X, vus de dessus-arrière à côté de la tête) ; « atterrit puis
charge debout » (FAUX d'après le repère de l'anim : pieds à 8 puis 0,65 stud du
sol) ; écrasement puis relevé (juste à ~0,2 s) ;
durée juste. Mes pièges : une vue de dessus supprime la hauteur ; un personnage
voisin n'est pas un repère de sol ; le nom (« Bomb ») crée une attente d'objet
tenu ; une coupe est un endroit où l'anim triche (A2 §2.3). Le vérificateur
ajoute que la vidéo ne permet PAS de voir le flottement (verif 2), que j'ai raté
la moitié des pulsations (une toutes les ~0,1 s, pas toutes les 0,2 s, verif 3), et que même avec les
chiffres j'ai mal lu les bras de l'accroupi (el -60 = vers le bas, pas « haut »,
verif 7).

**La prose arrondit, surtout vers le haut, pas toujours.** Vers le haut :
1,4 / 162 / 57 / 164 / 178 là où le JSON donne 1,26-1,31 / 154,7 / 51 / 146 /
156-161 (A4 verif) ; « 73-119 » pour une main qui démarre à 50 (A2 verif 5).
Vers le bas : tête de M1 37° pour 50° réels (A1 V4). Dans les deux sens :
« +5, +4, +3, +1 » pour 5,3 / 4,0 / 2,7 / 1,3 (B4 V2). Parade : recopier le JSON, jamais la phrase ; la vérification
adverse fait foi.

**Les projections trompent.** Un angle « sagittal » n'est pas l'angle réel
(164° affiché pour 146° vrais) ; un bras qui « traîne » en local file dans le
monde (A1 V3) ; la tête « baissée » se lit en élévation monde, pas relative au
torse (C4 §7.1) ; un buste penché dans ses axes ne penche pas vers la cible
(C4 §7.2). Parade : nommer le repère de chaque chiffre.

**Les images en double.** Les enregistrements d'écran contiennent des doublons :
les « % d'images immobiles » mesuraient la cadence de capture, pas l'animateur
(B2 verif, défaut 2) ; les anims brutes de « MORE Scrapped » tournaient à ~23-25
i/s dans une vidéo à 30 : comptes d'images gonflés de ~20 % (C1 oubli 1) ; Black
Hole à 60 i/s natif = 30 effectifs (C2) ; firytwig à fréquence variable ~40 i/s
(B1 verif 7) ; le GIF du Mii à 7,7 i/s (C3). Même notre v6 double ses cartes
(différence ≈0 à 4,767 et 4,833 s : 2,1 et 0,0 sur vignettes 64×36). Parade : `ffprobe`, chercher les
différences nulles, toujours donner la durée en SECONDES (B3 oubli final).

**Des descriptions de planches jamais affichées.** B1 a écrit des notes sur
trois tranches du tuto sans avoir reçu les images (l'outil renvoyait « request
limit ») : elles reprenaient la mémoire d'une étude antérieure ; il les a
marquées INVALIDE et tout relu (B1 §0). C1 et C3 ont eu le même refus et ont
relu (C3 a corrigé six passages écrits sur des images non reçues). Parade :
avant d'écrire « vu », vérifier que l'image a été affichée ; sinon « non vu ».

**Lire une intention là où il y a un outil ou un artefact.** Le jaune de
l'en-tête Blender dit « l'image porte une clé », pas « cet os a une clé » (B2
verif) ; « sélectionné » n'est pas « manipulé » (B2 verif 1) ; un trait violet
était un marqueur du visualiseur (C3 R7) ; une mesure d'énergie gonflée par le
volume d'une hitbox (C3 verif 6) ; un « détachement » de jambe produit par
l'outil de plantation (C4 verif 4).

**Nommer une pose d'après ce que je cherche.** « Tenue de charge » pour une
pose bras en travers de la poitrine (A3 verif 4) ; « chevelure qui pend » pour
un tronc du décor chez Baki (C4 verif 1) ; « flash d'impact différé » pour une
2e détente (B2 verif 7). Parade : décrire la géométrie avant de nommer.

**Généraliser depuis une coupe ou un compte de mots.** Tenues de GIF coupés =
bornes basses (C3 verif 3) ; « les reproches portent sur les jambes » alors que
l'easing et R15 dépassent (B3 verif 8) ; une caméra dite fixe qui bougeait (C1
verif 5 ; C2 verif 4-5). Parade : chercher le contre-exemple dans la même source.

**Les chiffres automatiques ne voient pas ce que Milan voit.** Pixels changés
égaux entre « aucun changement » et « un peu mieux » ; score slow-in/slow-out
qui préfère la v6 à TSB (SYNTHESE_YEUX §0, §6). Mes cinq faiblesses restent
(images une par une, profondeur 2D→3D, planches au lieu du cadrage réel, +0,3,
jeu et ciné confondus). Parade : vitesse réelle, cadrage réel, côte à côte avec
son ; une phrase en mots de corps AVANT de mesurer ; questions oui/non à un
sous-agent aveugle ; jamais une note tirée d'une mesure.

---

## 4. Avec ce nouvel œil, notre « Un seul coup » (v6)

**Ce que j'ai regardé.** La vidéo `captures/verification/2026-09-26-un-seul-coup-v6-scene-complete-avec-son.mp4`
(852×480, 30 i/s, 13,1 s, avec son) : les 60 images de 3,5 à 5,5 s lues une par
une (preuve : `captures/verification/2026-09-26-c4-synthese-v6-images-30is-3.5-5.5s.png`),
coupes, luminance et énergie du son mesurées image par image ; la planche de
clés de `usc_attaquant.rbxmx` (`…/2026-09-26-c4-synthese-v6-planche-cles.png`) et
la liste des 115 clés ; la fiche `UN_SEUL_COUP.md` §11 (ce que la v6 voulait).
Registre : **[CINÉ]**.

| temps vidéo | plan (coupes mesurées) | le corps (clés à 60 i/s) |
|---|---|---|
| 1,33-3,80 s | plan de 2,47 s ; 3/4 face en plongée, victime à droite | charge : buste à -70/-73°, penché +20°, hanche 2,42 ; gants de part et d'autre à hauteur d'épaule ; quasi immobile |
| 3,80-4,20 s | 0,40 s, plus proche et plus bas | tenue plein cadre (i228-250) |
| 4,20-4,467 s | 0,27 s, gros plan du bras armé | les bras s'ouvrent (i251-266), poings déjà à 22-32 studs/s |
| 4,467-4,733 s | 0,20 s puis 2 images ; la coupe tombe sur le départ (i268) ; poing tout près de l'objectif à la fin | détente : buste -77° → +16° en 16 images (4,5-9°/image), poing au plus ~45 studs/s ; contact à i283 |
| 4,733-4,867 s | carte inversée, 2 dessins × 2 images | le son monte ×8 sur la carte |
| 4,867-5,10 s | blanc pur 7 images, puis fondu 8 images | — |
| 5,10-8,60 s | plan très large 3,5 s, attaquant minuscule, ligne de roches | poings ≤ 0,45 stud/s de i287 à i632 (5,8 s), aucune part ne tourne de plus de 0,5°/image (A1 verif, A1 §8) ; débris et fumée bougent |

**Ce que la v6 fait déjà comme les pros.** Tête verrouillée en lacet (entre +7
et -11° dans le monde) pendant que le buste tourne de -77 à +16° (A1 §8, C4
§2.2) ; contact caché sous un filtre de
la scène 3D, comme Pew (C1 verif 1) ; son sur la carte (C2 verif 8) ; conséquence
en plan très large, décor changé (C1 §E4) ; au contact, poing à hauteur de
poitrine, buste presque de face (+16°) (NOYAU ; SYNTHESE_YEUX rang 5 : y +0,30).

**Ce qui est SÛR (mesuré).**
1. **La tête regarde au-dessus, pas en dessous** : +11 à +12° dans le monde
   de 3,1 à 4,45 s (temps de l'anim) ; les M1 pros -12 à -31° (en JEU), et
   les captures de Pew / TSB montrent le dessus du chapeau à la caméra (vu,
   non mesuré, C4 §1.10, §2.2, verif 2). (Qu'elle soit nette de profil et
   presque invisible aux cadrages de la vidéo est un jugement à l'œil, pas une
   mesure.)
2. **Pas de rupture de vitesse** : la fiche voulait « une vitesse qui ne fait que
   croître » sur 16 images ; poings déjà à 22-32 studs/s avant, ~45 au plus, soit
   un rapport ≈1,5 ; TSB M1 ≈4,5 (15 → 66 en une image) ; Collateral Ruin a un
   creux à 3-10 studs/s (i40-i64) puis une relance à 15-26 avant le moment
   rapide (A1 V2 ; A2 §5.1, verif 5). Attention au registre : M1 est un coup
   de JEU, la v6 une cinématique (A1 §8 le dit : « des façons de faire, pas
   des chiffres à copier »).
3. **Tout s'arrête ensemble** (i283-286 ; poing à 0,0 dès i287), puis 5,8 s
   de corps quasi figé ; chez TSB la suite fait 60 % de M1 et le torse
   continue (M2 : +42°, chiffre de prose, A1 §8), l'écrasement de Stoic Bomb
   continue ~8-11 images après le contact (penché max à i224 ; contact vers
   i213 selon A2 verif 2, i216 selon la prose) (A1 §1.1, §8 ; A2 §2.1).
4. **Le montage accélère jusqu'au coup sans plan long juste avant** : 2,47, 0,40,
   0,27, 0,20, 0,07 s (coupes recontrôlées par le contrôle adverse, seuil
   35/255). Gojo raccourcit PUIS tient 1,27 s ; Pew tient 0,75-0,9 s derrière
   l'épaule (prose 3,83-4,60 s ; verif 3,70-4,6 s) avant ~0,5 s finales ; le GIF TSB tient 0,6 s de poing
   dans la fumée (C1 verif 2, 7 ; C3 verif 1).
5. **Pas de « pose d'après » en plan rapproché** : carte → blanc → plan très
   large (mesuré : coupes). Que l'attaquant y soit trop petit pour être lu est
   un jugement.
   Pew garde 0,33 s de pose d'après dans le monde changé (C1 verif 1) ; Black
   Flash tient 1,5 s le poing au premier plan (C2 verif 5) ; le storyboard de
   Milan finit sur l'extension vers le lecteur (C4 §1.3). Chez nous, le poing
   vers l'objectif dure 2 images, AVANT la carte.
6. **115 clés, 6 parts à chaque clé** (A1 verif), et aucun arrêt étagé
   (point 3). Pas un défaut en soi (Ultimate2 et le pack sont cuits) ; que
   l'absence d'étagement soit ce qui manque reste une hypothèse (voir H6).

**Ce qui est SUPPOSÉ (hypothèses à montrer à Milan, pas un plan).**
- **H1. L'écart entre les deux poses est petit et étalé.** ~90° en 16 images ;
  myloe ~180° (face → dos, B2 §1.4), combo Moon et Rock throw : demi-tour en 2-3
  images (C3 verif 6, C1 verif 8) ; TSB M1 118° dont 34° en 2 images. Un
  animateur TSB poserait sans doute un armé plus enroulé (dos à la caméra, genou
  haut du GIF TSB, C3 §1) et collerait l'écart en 2-4 images. Mais la v6 a copié
  les mesures de Pew (-64 à -81°, fiche §11), d'un ordre voisin : confiance
  moyenne.
- **H2. Il manque un moment FERMÉ entre charge et frappe** : charge ouverte,
  frappe ouverte (bras gauche rejeté à az -131/-163) ; Mii : ouvert → fermé →
  ouvert (C3 R7), Black Hole alterne quatre fois (C2 §4). Confiance moyenne :
  Pew a lui aussi les deux bras devant, sur les côtés (C4 §1.10).
- **H3. En ciné, la rupture pourrait être dans le montage plutôt que dans le
  bras.** Le GIF TSB montre le trajet lentement puis casse par un contre-champ
  d'une image et 3 cartes (C3 verif 1) ; chez nous, ni tenue longue avant, ni
  vraie cassure. Un animateur anime garderait un dernier plan long (épaule ou
  poing en amorce, corps presque immobile, caméra qui pousse) puis un passage
  d'1 à 3 images (Gojo, Pew). Confiance moyenne.
- **H4. La tête relevée donne un regard « par-dessus ».** Effet sur la note
  inconnu (C4 §4). Avec 20° de penché, une tête presque neutre par rapport au
  buste suffirait ; relever la tête ne sert qu'au-delà de ~40° (C4 verif 2).
- **H5. La pose d'après est invisible chez nous.** Un pro (myloe) y passe son
  plus gros bloc de temps (retour 184 s ; mais charge + fin de charge 271 s,
  B2 verif 2) ; chez Pew, la pose d'après en plan rapproché ne dure que 0,33 s,
  ce qui dure c'est le plan large (C1 verif 1). Confiance moyenne.
- **H6. L'arrêt groupé se voit peu** puisque le contact est sous la carte ; une
  pose d'après rapprochée (H5) le montrerait.
- **H7. Le gel de 5,8 s n'est probablement pas le problème** : Pew tient 9 s de
  plan large, perso presque immobile (C1 §1.2) ; le GIF TSB ajoute une 2e vague
  ~1,1 s après le blanc (C3 R5).
- **Ce que je ne sais pas.** Pourquoi Milan a écrit « c trjs pas bon » : il n'a
  rien précisé. v5 → v6 est le plus gros changement mesuré (SYNTHESE_YEUX §2) :
  la quantité de changement ne prédit pas son avis. Pied gauche planté 4,63-12,5 s
  avec 1,37 stud de dérive (12 studs avec une autre définition du pied planté) :
  voulu ou patin, non regardé (SYNTHESE_YEUX §1.7, rang 7). Le bras gauche
  « az -131/-163 » (H2) et les chiffres de la charge (buste -70/-73°, hanche
  2,42) sont des mesures de cette synthèse, non recontrôlées.
  Si c'est moi qui juge, le +0,3 revient : ces hypothèses devraient passer par
  des questions oui/non à l'aveugle (SYNTHESE_YEUX rang 2), puis par Milan.

**Ce qu'on pourrait lui montrer (pas produire).** Un côte à côte v6 | Pew | GIF
TSB calé sur la carte, avec son, dans le scratchpad (refs jamais dans le dépôt),
et trois questions : la tête ? le dernier plan avant le coup ? la pose d'après ?

---

## 5. Pouvoir refaire : 3 exercices

**Exercice 1. Refaire TSB M1 de zéro, puis comparer.** [JEU]
- Ce qu'on fait : sans ouvrir le fichier, poser un M1 de 26 images en Linear
  d'après A1 §6 (clés 0, 6, 8, 10, 14, 20, 26 ; parts sélectives ; `hitreg` à
  i10 : dans TSB M1 il est sur la clé de pose i10, c'est chez M2 et M4 qu'il
  est sur une clé vide, A1 V5 ; `end` sur une clé vide à 25,3), en corrigeant
  avec les vérifications : tête non posée à l'armé et qui contre-anticipe
  (+8 → +21), 50° de tête pour 118° de buste, poing droit aussi rapide que le
  poing qui frappe pendant 2 images (épaule droite qui recule, bras qui
  avance en azimut), bras translatés de 0,3 à 0,9 stud (A1 V2-V4, B3 verif 2). Puis `planche_cles.py` sur les deux, et un rendu à la
  caméra du joueur (de dos).
- Ce qu'il teste : si « l'espacement est la courbe » est compris (palier
  66-73 obtenu ou pas) ; si les arrêts étagés se retrouvent sans les copier ;
  si la tête vise ; ce qui se lit de dos. Écarts à écrire en mots de corps,
  sans note.

**Exercice 2. Refaire Collateral Ruin de zéro, puis comparer.** [registre
non établi : aucune vidéo de ce coup, A2 §5]
- Ce qu'on fait : 2,13 s, 7 actes (plonger, enrouler, rassembler les mains
  au-dessus, lancer, toupie, jeter, sortie tassée), d'après A2 §5 corrigé
  (préparation jusqu'à 37 studs/s, pas 30) : un
  seul moment rapide d'environ 20 images (i74-i94), mains jointes en BARRE d'un
  seul côté (pas une croix), diagonale seulement i93-i98, tenue finale tassée ;
  torse et jambes posés serré, bras aux changements de pose (mais plusieurs
  clés portent toutes les parts à la fois : i0, i13, i22…, A2 verif) ; au moins 2 clés
  intermédiaires par tour ; marqueurs `StartHitbox` / `EndHitbox` ; pieds qui
  peuvent passer sous le sol à i90 (A2 verif 5-8, oubli 2).
- Ce qu'il teste : les rotations de plus de 180° (le piège du plus court
  chemin) ; une silhouette par acte ; le rapport préparation / rapide ; la
  hiérarchie torse+jambes puis bras (T 30, H 12, BD 13, BG 20, jambes 28).

**Exercice 3. Prédiction à l'aveugle au cadrage de jeu.** [JEU, puis CINÉ]
- Ce qu'on fait : un sous-agent qui n'a PAS lu A4 regarde, en vidéo à 30 i/s et
  vitesse réelle, trois clips du pack rendus à la caméra de jeu (de dos,
  distance de jeu) : Hit 2, Sidedash L, Forward Dash. Il écrit avant toute
  mesure : ordre de départ des parts, durée de la montée et du retour, s'il y
  a une anticipation, où est la tenue, ce que fait la tête. Puis on compare aux
  données exactes (A4 verif : Hit 2 tête avant le buste d'une image ; Sidedash
  contre-poussée +0,28 à i2 ; Forward Dash tenue qui dérive puis claque, bras
  tendu i46-58). Variante ciné : même exercice sur une vidéo coupée, avec la
  liste des pièges de Stoic Bomb (hauteur, repère voisin, nom, coupe).
- Ce qu'il teste : mes yeux, pas mes mains : lire du mouvement à vitesse réelle
  (faiblesse 1), la profondeur de dos (faiblesse 2), le cadrage réel
  (faiblesse 3), et la surestimation (prédire avant, vérifier après ;
  faiblesse 4). Le score est la liste des réponses justes et fausses, jamais un
  pourcentage.

---

## Annexe : où sont les preuves

- Notes complètes : `corpus/etude_c4/A1…C4*.md` (chacune avec sa Vérification
  adverse).
- Images de travail des lecteurs et vérificateurs : scratchpad de session
  (`c4/frames/…`), jamais versionnées (refs sous droits).
- Nos propres images, versionnées : `captures/verification/2026-09-26-c4-synthese-v6-images-30is-3.5-5.5s.png`
  (v6, 60 images de 3,5 à 5,5 s, temps relatif à 3,5 s incrusté) et
  `captures/verification/2026-09-26-c4-synthese-v6-planche-cles.png` (planche de
  clés de l'attaquant v6).
- Mesures v6 (coupes, blanc 4,867-5,067 s, énergie du son) : ffmpeg + numpy sur
  la vidéo v6, seuil de coupe 35/255 sur vignettes 64×36.

---

## Contrôle adverse de la synthèse

Contrôleur adverse, 2026-09-26. J'ai relu les 12 « Vérifications adverses »
en entier, et les passages de prose cités (A1 §1.1, §2, §3, §5, §8 ; A2 §2-5 ;
A3 §0-1 ; A4 §1.3, §2, §3 ; B1 §2.1 ; B2 §1-4 ; B3 §B2, §5 ; B4 §2 ; C1 §1.2,
§E1-E10, §3 ; C2 §2, §4 ; C3 §1, §3, §5, R5, reprise ; C4 §1, §2.3-2.6, §3,
§7.1-7.6). J'ai relu les lignes citées de `milan_verbatim.jsonl` (l.10, 34,
41, 43, 44, 54, 80, 102, 109, 113, 133, 169, 172, 176, 179, 181, 183, 186,
191, 195, 199, 214, 215), la fiche `UN_SEUL_COUP.md` (l.268-270) et
`SYNTHESE_YEUX.md` (§0, §1.7, §6, rangs 2, 5-7). J'ai aussi remesuré la vidéo
v6 (ffprobe ; différence d'images sur vignettes 64×36, seuil 35/255). Le
contrôle porte sur les chapitres 0 et 4 surtout. La consigne parlait du
« chapitre 5 » pour la séparation sûr / supposé : cette séparation est au
chapitre 4. J'ai contrôlé les deux.

### Ce qui est confirmé tel quel (échantillon, 38 affirmations)

- **Chapitre 0** :
  - M1 : clés 0-26 et torse 42/34/16/19/7° (A1 V2) ; 15 → 66 puis palier
    67-73 (A1 V2, A4 verif 8).
  - Collateral Ruin : préparation 11-37, rapide ~20 images (A2 verif 5).
  - Ultimate1 : tête sur une clé de torse 35/46 ; WallComboPlayer en clés
    complètes (A3 verif 2).
  - Pack : buste 137-162° contre tête 9-23° (A4 verif 1) ; marche 0,0° pour
    33°.
  - Tête des M1 à -12/-31° dans le monde ; TSB M4 à +17° (C4 verif 2) ; Hit 1
    en exception (A4 verif).
  - Écart 0,0000 M1→M2 (A1 V1) ; Pew 7 images, filtre sur la 3D (C1 verif 1) ;
    voile d'Ippo (C3 verif 2) ; poing lent 0,6 s du GIF TSB (C3 verif 1).
  - Stoic Bomb : dérive de 0,3-0,5 stud des épaules (A2 verif 3) ; All Might
    figé 1,0 s (B4 V5).
  - Translations : 0,3-0,9 stud en M1 TSB (B3 verif 2), 1,2-1,7 stud dans le
    pack (A4 oubli), pop de 1,9 stud (A4 verif 3).
  - Racine = conteneur (A3 verif 3).
  - « du bas » 6 fois, « de derrière » du 09-04 au 09-26 (C4 verif 6).
- **Chapitre 1** :
  - B1 : titres à 303/305/384/555/635 s (B1 verif 1).
  - B2 : dope sheet 40→30 / 80→60 ; temps 271 / 184 / 131 et 218 / 192 s
    (B2 verif 1-2) ; `hitreg` M1 à i10 (B2 verif 5).
  - Couleurs du rig lettré (C1 verif 4).
  - M4 : jambe horizontale f13-14 et 88,5 studs/s (A1 V7) ; écarts
    5,3/4,0/2,7/1,3 (B4 V2).
  - Rotations : 2 clés intermédiaires minimum, TSB en met 3 (A2 verif 6).
  - Tenues de WallComboPlayer 5-6-8-10-8-10-8-9-6-5-5 puis 4 (A3 verif 7).
  - TweenStuff 6-8 images avant l'arrivée (A3 verif 1).
  - JJK 3-3-2-3-3-2 (B4 V1) ; Gojo 1,07 → 0,27 puis 1,27 s (C1 verif 7) ;
    Sunrise 12 coupes puis 5,9 s, décalage de ~7 s (C1 verif 7 et 9).
  - Black Flash : creux de ~0,46 s (C2 verif 6) ; Rewind Clock +35 %
    (C2 verif 4).
  - Gatling : 1,4 s d'immobilité puis 0,2 s (C3 verif 4) ; WallComboVictim f8
    = f0, pop à f9, bras à f11 (A3 verif 8).
  - Citations de Milan : texte exact, lignes justes.
- **Chapitre 4** :
  - Remesuré sur la vidéo : 852×480, 30 i/s, 13,1 s. Coupes à 1,333 / 3,800
    / 4,200 / 4,467 / 4,667 / 4,733 / 4,800 / 4,867 / 8,600 s. Carte en 2
    dessins × 2 images ; blanc de 7 images (4,867-5,067) ; fondu d'environ
    8 images ; plan large de 5,10 à 8,60 s.
  - 115 clés, 6 parts, torse à 4,5-9°/image, poing ~45 après 22-32
    (A1 verif).
  - Tête à +11/+12° (C4 verif 2) ; « vitesse qui ne fait que croître » et
    Pew -64/-81° (fiche l.268-270).
  - AnimationBench 4-5/5, v5→v6 le plus gros changement, dérive de 1,37 stud
    (SYNTHESE_YEUX).
- **Chapitre 5** : clés et temps d'Ex. 1 ; pour Ex. 2, i74-i94, la barre à
  un seul côté, la diagonale i93-i98, les comptes T30/H12/BD13/BG20/J28 et
  les pieds sous le sol ; pour Ex. 3, les chiffres Sidedash / Forward Dash /
  Hit 2.

### Ce que j'ai corrigé dans ce fichier

1. **Chiffres et faits** :
   - « TSB n'a que du Linear » → les 7 coups courts sont Linear ;
     WallComboPlayer a 67 poses Constant et Ultimate2 est cuite (A1 V2).
   - « Segments linéaires » de Stoic Bomb : non décodé, « invérifiable »
     (A2 verif).
   - Collateral Ruin : « de 50 à plus de 70 selon la main » → main gauche
     ~50 à ~81 (A2 verif 5).
   - Oscillation du torse : « ~115° » → 110-118°, M4 finit à +23° (A1 V1) ;
     pack « fait de même » → écarts de 0 à 0,30 (A4 verif 2).
   - Stoic Bomb : « le corps ne tourne plus 3,2 s » → rotations des bras
     (i57-i249, recontrôlé jusqu'à i141) ; pulsation toutes les ~0,1 s.
   - `hitreg` « sur des clés vides » : faux pour M1, où il est sur la clé de
     pose i10 (A1 V5, oubli 2). C'était recopié dans l'exercice 1.
   - DeHapy : « 5 colonnes sur toutes les pistes » → la tête n'a aucune clé
     (B3 verif 3).
   - Tableau (h) : « M1 TSB 0,43-0,47 s » → M1-M3 seulement, M4 fait 0,69 s ;
     « membres détachés modérés » → le pack translate de 1,2 à 1,7 stud.
   - Marqueurs : « aucun dans le pack » n'était pas prouvé (A4 §0 : non lus).
   - Stoic Bomb « il flotte » → pieds à 8,0 puis 0,65 stud dans le repère de
     l'anim ; « il flotte » suppose la HumanoidRootPart au sol (A2 verif 2).
   - « Anticipation 4-6 frames, impact 1 » : « vrai pour un M1 » → plus
     proche sans être exact (frappe en palier de 4 ; transitions de 4-8
     images, C1 verif 3).
   - « Pixels changés égaux » → temps d'écran égal (1,63 s), pics différents
     (59 / 79 %).
   - Lacet de la tête v6 : « -7 à +11 » → « +7 à -11 » (A1 §8).
   - « Membres ≤ 0,45 » → poings (A1 verif).
   - Collateral Ruin : le « creux juste avant » est à i40-i64, suivi d'une
     relance à 15-26.
   - Pew : 0,75 → 0,75-0,9 s (C1 verif 2) ; écrasement de Stoic Bomb :
     8 → 8-11 images (contact i213, A2 verif 2).
   - Captures de Milan : « en pause à 0,5x » → 2 sur 3 à 0,5x, 1 à 1x
     (C4 verif 8).
   - Citations B2 : §1.2 → §4.2 ; « Ippo change d'angle dans chaque flash »
     → vu sur 4 transitions.
2. **Citations de Milan** : l.102, l.113, l.215, l.195 (§1b) et l.43 (§1b)
   avaient été normalisées alors que le titre dit « ses mots exacts ». Elles
   sont rendues à l'orthographe d'origine.
3. **Registre** :
   - point 8 [LES DEUX] → [CINÉ] : toutes ses sources sont ciné ;
   - « Constant » [LES DEUX] → [CINÉ] : WallComboPlayer = combo au mur,
     classé ciné dans l'en-tête ;
   - point 7 : la phrase « en jeu » est marquée JEU ;
   - point 4 : les mesures sont toutes en jeu ;
   - exercice 2 [LES DEUX] → registre non établi (aucune vidéo de Collateral
     Ruin) ;
   - chapitre 4, SÛR 2 : la comparaison v6 (ciné) / M1 (jeu) est signalée
     comme un repère, pas une norme.
4. **Formulations en règle ramenées à des observations** :
   - « presque toujours masqué » → « dans les cinématiques étudiées, le plus
     souvent », avec contre-exemples (Xoaterz, Mii) ;
   - « le 2e bras a toujours un rôle, jamais le miroir » → « dans les
     ~6 images regardées » ;
   - « il faut décomposer le penché » → « dans l'essai de C4, il a fallu » ;
   - « demande ~1 stud » → « d'après un calcul, demanderait » ;
   - « il récompense… jamais un chiffre » → « aucun éloge ne cite un
     chiffre », avec la réserve de C4 verif 7 ;
   - « Milan lit d'abord » → « ses plaintes les plus constantes » ;
   - « Il fait ainsi parce que » → « lecture, pas dite par l'auteur » ;
   - « pour remplacer coude et genou » et « pour vendre l'écrasement »
     marqués comme interprétations ;
   - « Exceptions voulues » → « Exceptions » ;
   - « l'équivalent R6 mesuré » → « une analogie » ;
   - « la prose gonfle » → « la prose arrondit, surtout vers le haut, pas
     toujours » : A1 V4 est un arrondi vers le bas. La même erreur était
     dans l'en-tête.
5. **Sûr / supposé (chapitre 4)** :
   - trois éléments rangés en SÛR étaient des jugements, maintenant marqués
     comme tels : la tête « nette de profil / invisible » ailleurs, la pose
     d'après « à taille lisible », et « ce qui manque, c'est l'étagement » ;
   - H5 généralisait « là où les pros mettent leur soin » à partir d'un seul
     tuto, et contre C1 verif 1 (pose d'après de 0,33 s chez Pew) : reformulé.

J'ai aussi retiré une phrase que j'avais moi-même ajoutée sans source
pendant ce contrôle (fantôme chez myloe).

### Ce qui reste douteux (non tranché ou non recontrôlé)

- **Mesures propres à cette synthèse, non recontrôlées** : « le son monte
  ×8 sur la carte », bras gauche à az -131/-163, charge (buste -70/-73°,
  hanche 2,42).
- **d2fda413** : Boros selon la prose C4 §1.7, Genos selon sa vérification,
  qui ne justifie pas ; le tableau dit « non tranché ».
- **Bras droit de TSB M1** : « arraché en arrière » (A1 §1.1, V2 : 64-71
  studs/s) ou bras qui avance en azimut, l'épaule seule reculant (B3
  verif 2) ? Les deux vérifications ne se contredisent pas sur la vitesse,
  mais bien sur la direction.
- **Chiffres venus de la prose, jamais recontrôlés par une vérification** :
  - A1 §8 : M2 +42° de torse après le contact ;
  - A2 §5 : 119 studs/s de Collateral Ruin ;
  - B2 §1.4 : myloe ~180°, qui vient d'une « étude existante » ;
  - C3 R5 : 2e vague ~1,1 s après le blanc ;
  - B4 §4.2-4.3 et §4.4 : lignes « rapport_anime3d » et « Iczer : poing au
    moins aussi gros que la tête » du tableau §2 ;
  - A1 §0 : « bug corrigé dans corpus.py l.60-66 », seulement « vérifié dans
    le code ».
- **Registre de Swift Sweep et de Black Hole Ability** : ce sont des capacités
  de jeu filmées avec une caméra écrite. Le classement [JEU] / [LES DEUX] est
  une convention de lecture.
- **Les « Parades » du chapitre 3** sont écrites en consignes (« jamais la
  phrase », « toujours en secondes »). Je les ai laissées : ce sont des
  méthodes de travail pour moi, pas des règles d'animation. Mais elles
  restent formulées en règles.
- **Coupe à 4,667 s** : différence de 37,6 pour un seuil de 35. Si le seuil
  bouge, le découpage « 0,20 s puis 2 images » peut changer.
