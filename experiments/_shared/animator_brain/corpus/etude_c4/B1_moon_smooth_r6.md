# Chantier 4 — B1 : la méthode Moon Animator et ce qui rend un R6 « smooth »

Identifiant : B1_moon_smooth_r6. Rédigé le 2026-09-26. Toutes les images de travail
sont dans `scratchpad/c4/frames/B1_moon_smooth_r6/` (hors dépôt). Les notes brutes, au fil
de la lecture, sont dans `scratchpad/c4/notes/B1_brut.md`.

Statuts : **vu** (je l'ai regardé moi-même), **mesuré** (outil, pixels), **lu** (texte
incrusté à l'écran), **déduit** (mon interprétation).

## 0. Honnêteté d'abord : un incident de lecture

Pendant la première passe, **aucune planche-contact ne s'affichait** : l'outil renvoyait
« request limit » au lieu de l'image. J'ai d'abord écrit des notes pour les tranches
256-760 s, puis 0-335 s, puis 288-623 s **sans avoir vu l'image**. Ces notes
reprenaient en réalité ma mémoire de l'étude existante. Je m'en suis rendu compte,
j'ai marqué toutes ces sections **INVALIDE** dans `B1_brut.md` et j'ai tout relu jusqu'à
voir réellement les images :
- `RELECTURE-3` couvre 240-760 s ;
- `RELECTURE-4` couvre 0-239 s.

Tout ce qui suit s'appuie **seulement** sur ces relectures valides et sur les
extractions à 10-60 i/s.

Leçon pour le cerveau : un agent peut produire une description plausible d'une
image qu'il n'a jamais reçue. Avant d'écrire « vu », il faut vérifier que l'image a
vraiment été affichée.

## 1. Couverture

| Source | Ce qui a été regardé | Cadence |
|---|---|---|
| Tuto « [OLD] How to animate R6 SMOOTHLY » (0vjAiAR-YFk, 761 s, @VoidGamrTheMonke) | les 761 images, en 48 planches de 16 (`cs/cs_*.png`) | 1 i/s |
| idem, démos jouées | intro 0-4 s (`hf/intro.png`) ; lecture « torse seul » 266-271 s (`hf/torse_seul.png`, `hf/torse_zoom.png`) ; résultat final 745,9-748,4 s (`hf/final_loop.png`, `hf/final_zoom.png`) | 30 i/s |
| « [FOR SALE] Advanced Movement System » (olr5q-iIlKI, 27,5 s) | tout (`hf/amw_a/b/c.png`) | 10 i/s |
| idem | dash avant, dash latéral (`hf/amw_dash1/2.png`) ; réception (`hf/amw_land.png`) | 30 i/s ; 15 i/s |
| Tuto dessiné firytwig (afaa00eb, 7,25 s) | planche fixe lue en gros plan (`fir/q_*.png`) ; les 4 boucles animées | 60 i/s (`hf/fir_kick60`, `fir_punch60`, `fir_b12`, `fir_b34`) |
| Combo Moon Animator (85e1a98f, 22,7 s, EclipseThemDev) | tout (`hf/combo_2fps.png`) | 2 i/s |
| idem, timeline | positions des clés mesurées (`combo/f_10.0.png`) ; tête de lecture suivie image par image (`combo/playhead.json`) ; pose à chaque clé (`combo/keys_slow.png`) | image par image |
| Comparaison pro | TSB M1 (`tsb_M1.png`, `tsb_M1.json`, outil `planche_cles`) | — |

**Non couvert :**
- dans le tuto, les passages accélérés « x5 » et « x10 » (jambes 685-745 s) ne sont vus qu'à 1 i/s : je n'ai pas extrait les clés une à une ;
- dans le combo, les sections « Linear Easing Test » (0-2 s) et « No camera movement » (2-4,7 s) ne sont vues qu'à 2 i/s, et la lecture temps réel 5,2-8,2 s n'est vue qu'à 6 i/s ;
- les valeurs d'angle du tuto ne sont pas lisibles (640x360). Les angles cités sont des estimations à l'œil.

---

## 2. Par source

### 2.1 Tuto « How to animate R6 SMOOTHLY » : la méthode, dans l'ordre

**Outils et installation (lu/vu)**
- Moon Animator 2, Phobos Rotation (trackball, « press T twice ») et le plugin de l'auteur (8-11 s).
- Le rig est un R6 par défaut, équipé d'« IK Adornments ». Chaque face est colorée selon sa direction locale (vu 48-63 s, puis 396, 442, 438, 650 s) :
  - avant rouge « F/FRONT », droite verte « R », gauche jaune « L » ;
  - dessus cyan « U », dos bleu « B/BACK », dessous orange « D » ;
  - boules blanches aux extrémités ;
  - un **rayon blanc de regard** sort de la tête (40 s).
- Ce rig sert d'instrument de mesure : à tout moment, la couleur qu'on voit dit comment chaque bloc est tourné. Le « bras vert » est un bras dont on voit la face droite, ce n'est pas forcément le bras droit.
- La timeline est étirée « until it counts up in 5 » (19-28 s) : graduations 0, 5, 10… La tête de lecture peut quand même tomber entre deux graduations (« 0:07 », « 0:12 » à 26-27 s).

**Étape 1 — le torse d'abord, seul, et le reste suit sans être posé (vu 29-300 s)**
- « Now for the Torso Move it down slightly » (29-35 s) : flèche de POSITION verticale sur le torse.
  - Toute la silhouette descend : à 34-35 et 41-42 s, les jambes paraissent raccourcies (elles passent sous le sol).
  - En R6, le torse porte bras, jambes et tête. Les pieds traversent donc le sol, et l'auteur ne s'en occupe pas avant la toute fin (étape 5).
- Pose de départ au trackball (49-56 s) : le bloc entier est tourné d'environ 90° (de profil, face verte visible à 52 s) et un peu penché. Les bras ne sont pas posés.
- Pendant toute la phase torse (64-300 s), **le mannequin est un bloc rigide** : bras et jambes collés, dans l'axe du torse.
  - L'auteur juge donc la ligne du corps entier comme un bâton qui plonge, se redresse, se cambre et roule. [déduit] C'est la ligne d'action, sans aucun membre pour distraire.
- Les rôles des clés sur le torse (lu : titres « Point ONE… FIVE ») et ce que je vois :
  - **Anticipation** (65-79 s) : le bloc se tasse et plonge un peu vers l'avant. Il le déplace en position (flèches à 65-71 s), pas seulement en rotation.
  - **Drag** (82-99 s) : le bloc reste penché. À 91-94 s, il est un peu plus redressé et tourné. [vu] À 1 i/s, je distingue mal anticipation et drag.
  - **Middle**, « The Main Part of the movement » (100-146 s, la clé la plus longue à régler) :
    - le bloc se REDRESSE (103-106 s) ;
    - de profil, il se CAMBRE vers l'arrière, à l'opposé du fantôme penché (130-131 s) ;
    - puis il ROULE (143-146 s, FRONT incliné d'environ 30° à l'œil).
  - **Exaggeration** (147-184 s) puis **More Exaggeration** (185-193 s) : le roulis continue **dans le même sens**, un cran plus loin (190-191 s plus incliné que 184 s).
  - **Wiggle** (194-265 s) : petites variations autour de la pose finale, en rotation et en translation (flèches à 209-223 s et 241-253 s).
- **Comment il juge une clé (vu) :**
  - il se met presque toujours DE PROFIL, face verte (116-136, 165-176, 228-255 s) ;
  - il compare la pose au **fantôme rouge de la clé précédente** (touche B) ;
  - l'écart entre le bloc et le fantôme, c'est la quantité de mouvement sur 5 images ;
  - pour le wiggle, il garde la caméra **fixe** de face-3/4 (194-227 s) pour voir des écarts de quelques degrés.
- Lecture du « torse seul » à 30 i/s (`torse_zoom`, 268,10-269,67 s, vu) :
  - 6 images vidéo presque immobiles (le bloc reste de profil) ;
  - **en UNE image vidéo, il passe de profil à face** (268,47 s) ;
  - puis environ 0,9 s de tenue qui roule doucement.
  - [déduit] Le « coup » se lit déjà sur le torse seul, avant tout bras.

**Étape 1b — les deux astuces de timing (vu 271-297 s)**
- Timeline à 271-274 s :
  - « 1:00 | 60f » ;
  - clés du torse à 0, 5, 10… 60, soit 13 clés ;
  - les autres pistes n'ont qu'un point, à 0.
- **Astuce 1** : on décale les clés 2 à 13 de +5, ce qui donne 0, 10, 15, 20… (276-278 s).
  - « this makes it look like speed is building up! » ;
  - puis « Though I DO NOT reccomend doing this for this animation ».
- **Astuce 2**, gardée (288-295 s) : la clé Middle passe de 15 à 12 (« 0:12 | 12f »). La fin est tirée de −5 : la dernière clé passe de 60 à 55 (« 0:57 » pendant le glisser, 295 s).
  - [vu partiellement] Je n'ai pas vu la fenêtre 15-30 après le décalage. Que 20→15, 25→20, etc. reste plausible (l'étude existante le dit), mais je ne l'ai pas vu moi-même.

**Étape 2 — le bras « passif » d'abord (vu 301-383 s)**
- « Seeming as the left arm doesnt do much in the animation, lets do that first ». Le bras gauche est :
  - soit tendu DEVANT, à peu près à l'horizontale (331-339 s, contre-plongée, bout orange vers la caméra) ;
  - soit ramené devant la poitrine (355-364 s), selon la clé.
- Correction de ma lecture antérieure (invalide) : un bras R6 ne se plie pas. Il est tendu ou tourné, jamais « replié ».
- « just move it with the torso » : ce bras garde sa relation au torse ; il n'a pas sa propre trajectoire.
- Ensuite, « add some drag and exaggeration to anything that seems too bland » (345-349 s) : il repasse sur chaque clé.
- Il utilise aussi les flèches de position sur le bras (352-353 s) : il déplace le bras, pas seulement il le tourne.

**Étape 3 — le bras qui frappe, traité comme un second torse (vu 384-547 s)**
- Pose 0 : bras droit en travers devant le bas-ventre, bout vers la hanche opposée (394-399 s, face « D » visible à 396 s). C'est une garde basse d'uppercut.
- **Anticipation** : le bras descend et part vers l'arrière, le long de la cuisse (408-416 s).
- **Drag** : le torse a déjà tourné, mais le bras reste bas.
  - Il est **translaté**, décroché de l'épaule : flèche de position rouge à 428-429 s, décrochage visible à 426 s.
  - Texte lu : « It may look dislocated but it helps everything flow smoothly! »
- **Middle** (444-475 s) :
  - à 448-449 s, le bras **flotte en l'air, détaché**, à côté de la tête : il l'a d'abord DÉPLACÉ en position ;
  - puis il le redresse à la verticale (450-451 s) ;
  - à 455-463 s, on voit la face BLEUE « B » du bras : il a tourné d'environ 180° vers l'avant-haut ;
  - le torse est très penché, et la jambe droite (encore non posée) part en diagonale.
  - [déduit] Il construit la pose clé par placement direct, pas par rotation à l'épaule.
- **Exaggeration** (480-514 s) : caméra fixe. Il essaie plusieurs inclinaisons et torsions du bras autour de la verticale. À 504-505 s apparaît une variante très différente (face B + R, bras écarté), puis il revient.
- « once… all the movement from the hand has stopped, for every other keyframe move it with the torso » (524-531 s).

**Étape 4 — la tête (vu 551-630 s)**
- Il pose la tête à la clé 0, puis active le fantôme de la clé 0.
- À chaque clé, il fait **toucher le rayon blanc et le rayon rouge** au sol (571-591 s). Il se met loin, au-dessus ou derrière, pour voir les rayons en entier : il juge une DIRECTION, pas un visage.
- « For the middle exagerate it depending on the direction of the torso » (594-600 s) : au coup, la tête accompagne le torse.
- Après « more drag », la tête suit le torse (610-617 s).

**Étape 5 — les jambes, en dernier et au plus long (vu 631-745 s)**
- Il pose les jambes de la clé 0 : appuis écartés en A, pieds bien plus écartés que les hanches (653-654 s, vue de dos).
- À chaque clé, il ramène « the white ball inside the red ones », c'est-à-dire le bout de chaque jambe dans l'empreinte fantôme de la clé 0 (661-665 s).
  - « Tip: ONLY use position to move the leg up and down, not left or right » (666-670 s).
- Cette étape est montrée en accéléré x10 : 35 s de vidéo, soit plusieurs minutes de travail réel.
- « For this leg i made it raise so we can just make it move with the torso » (733-738 s) : une jambe décollée n'a plus besoin d'être recalée.
- [déduit] C'est une IK faite à la main : le torse a bougé à chaque clé, donc les pieds ont glissé, et il les recale un par un.

**Le résultat final à 30 i/s (`final_zoom`, vu + comptage à l'œil)**

| Instant | Ce qu'on voit |
|---|---|
| 746,77 s | pose de départ, de profil, ramassé |
| 746,77-746,87 s (4 images vidéo) | léger tassement |
| 746,90 s | le torse bascule, le bras est encore en travers (drag) |
| **746,93 s** | **bras déjà en haut, torse face caméra et penché : tout le coup tient en UNE image vidéo** (1/30 s, soit 2 images à 60 i/s : l'intervalle 10→12 de l'astuce 2) |
| 746,97-747,03 s | fin de la rotation du bras (on passe de la face B à la face R) : exagération |
| 747,07-748,07 s (~31 images, ~1,0 s) | tenue qui dérive à peine |

- Période de la boucle mesurée : **40 images vidéo, soit 1,33 s** ; 55 images à 60 i/s donneraient 0,92 s. Même écart sur la lecture du torse seul : 1,13 s mesurée contre 1,0 s attendue. **Écart non résolu** (lecture Moon plus lente que le temps réel dans l'enregistrement ? pause de bouclage ?).

**L'intro (vu à 30 i/s)**
- Il y a **deux personnages** : l'attaquant plaque une victime contre le mur. La lecture « un perso ramassé seul » était fausse.
- Trois impacts, à 0,10 s, 0,60 s et 1,70 s. À chacun :
  - la victime devient rouge vif pendant 1 image, puis le rouge s'estompe sur 10-15 images ;
  - une gerbe blanche radiale grossit sur 3-5 images.
- Entre les impacts, l'attaquant bouge peu. [déduit] L'effet porte le choc, pas un grand geste.

### 2.2 Advanced Movement System (vu 10/15/30 i/s)

- **Dash avant** (13,65-14,58 s, à 30 i/s) :
  - appel, corps à 45° (13,78 s) ;
  - **corps à l'horizontale, bras devant et jambes derrière dans UNE seule ligne, pendant 3 images** (13,82-13,88 s) ;
  - roulade avant tête en bas (13,92-14,02 s) ;
  - boule au sol (14,05-14,08 s) ;
  - relevé accroupi, buste penché (14,12-14,18 s) ;
  - course (dès 14,22 s).
  - Total : environ 0,55 s. Le corps fait un tour complet sur l'axe latéral en environ 0,25 s (compté).
- **Dash latéral** (15,85-16,58 s) : même structure (horizontale, par-dessus, boule, relevé), environ 0,7 s.
- **Réception** (15 i/s) :
  - en l'air, bras ouverts à l'horizontale (21,53-21,87 s) ;
  - à l'impact, corps tassé, tête rentrée, bras qui retombent, fumée (22,00-22,13 s, environ 0,2 s) ;
  - remontée d'environ 0,3 s.
- Autres rubriques (vu à 10 i/s) :
  - shift lock : rotation progressive d'environ 2,5 s ;
  - leaning : le corps penche du côté de la course (7,0-7,3 s à gauche, 8,3-8,6 s à droite) ;
  - sprint : buste penché, poussière à chaque pas.

### 2.3 firytwig, « Attacks Animation Tutorial » (lu + vu à 60 i/s)

- **Planche (lu).**
  - Colonnes « Chamber / Attack / Recovery ».
  - Quatre schémas d'espacement :
    - l'intervalle collé au chamber est coché bon ;
    - l'intervalle au milieu est barré : « Keep the inbetweens close to the chamber » ;
    - l'intervalle collé à la pose est barré : « Don't ease out towards the main pose, you can ease out from the overshoot to the main pose though » ;
    - un segment bleu au-delà de la pose : « Overshoot ».
  - Encadré : « Keep it as snappy as possible / Minimize frames in between / Do not ease out / Hold or overshoot the attacking limb / Put the whole body into the attack / especially the hips ».
  - En bas : « Even 1 frame of chamber matters » ; « Every action has an equal and opposite reaction » ; « you can skip the point of contact ».
- **Boucles, mesurées à 60 i/s de capture.**

| Phase | Side kick | Lunge punch |
|---|---|---|
| Garde | ~0,35 s | — |
| Chamber (dessin quasi fixe) | 1,05-1,30 s (~0,27 s) | pose large 1,03-1,22 s, puis ramassé 1,23-1,30 s |
| Passage chamber → attaque | **aucun dessin intermédiaire** (1,30 → 1,32 s) | **aucun dessin intermédiaire** (fente complète à 1,32 s) |
| Attaque | à 1,32-1,33 s, jambe un peu plus haute que 1,35-1,47 s (petit **overshoot** qui revient) ; tenue ~0,17 s ; traits de vitesse | tenue 1,32-1,47 s |
| Suite | recovery ~0,2 s | fente encore tenue, **poing déjà ramené** (1,48-1,68 s) ; puis relevé |

  - « Even 1 frame of chamber matters » : le chamber est dessiné en rouge, sur un seul dessin d'environ 0,08 s (0,28-0,35 s).
  - « Skip the point of contact » : deux versions côte à côte. À 0,37-0,43 s, la version de droite montre le sac déjà courbé. [déduit, incertain] Elle saute l'image du contact.

### 2.4 Combo Moon Animator (mesuré + vu)

- Sections lues à l'écran : « Linear Easing Test », « No camera movement », « No effects + Slowdown ».
- La fenêtre Moon montre des **pistes d'effets** (Circle, Shockwave 1-2, CircleShockwave, MeshPart) : les VFX sont animés comme des objets dans la même timeline.
- **Clés mesurées** (seuil de luminosité sur `f_10.0.png`, calé sur les graduations 0 et 180) :
  - CFrame (racine) : 0, 10, 15, 20, 30, 35, 39, 45, 55, 60, 65, 70, 80, 85, 92, 100, 105, 110, 115, 121, 132, 139, 150, 155, 160, 169 ;
  - Torse, bras et tête : **les mêmes images** ;
  - jambe droite : les mêmes, plus 18 et 103 ;
  - écarts : 10,5,5 | 10,5,4,6 | 10,5,5,5 | 10,5,7,8 | 5,5,5,6 | 11,7,11 | 5,5,9 ;
  - durée : 169 images, soit 2,8 s.
- **Tête de lecture suivie** (`playhead.json`) : 5,2-8,2 s en temps réel, 9,8-20,8 s au ralenti environ x4.
- **Poses à chaque clé** (`keys_slow.png`) :

| Clés | Pose |
|---|---|
| 0 | debout |
| 10-15 | garde basse |
| 18-20 | jab |
| 35-45 | appuis très larges, bras armé derrière, tenu 10 images |
| 55-60 | de dos (rotation) |
| 70-80 | grande fente basse, bras au-dessus de la tête |
| 85-92 | debout de profil, bras tendu |
| 100-115 | torsion, puis bras en l'air |
| 121-132 | ramassé |
| 139-155 | en l'air |
| 160-169 | réception accroupie |

  - [déduit] Chaque coup prend environ 10 images d'armement, puis environ 5 de frappe et environ 5 de suite. Deux poses voisines sont très différentes : debout, fente basse, dos, en l'air.

### 2.5 Comparaison : TSB M1 (mesuré, `planche_cles`)

- 7 clés en 0,43 s : images 0, 6, 8, 10, 14, 20, 26 (écarts 6, 2, 2, 4, 6, 6).
- Le lacet du buste passe de +48° à −70° : environ 118° en 14 images, dont 34° en 2 images (6→8).
- **Parts posées** : le torse à toutes les clés (7/7), la tête à 4, le bras droit à 5, le bras gauche à 6 ; à i20, **le torse seul** ; les jambes jamais.

---

## 3. Grands enseignements

1. **Du plus grand au plus petit.** Ici, l'animateur pose d'abord le torse et le rejoue seul, puis le bras passif, le bras actif, la tête, et les jambes en dernier (vu 29-745 s). Parce qu'en R6 le torse porte tout, le corps entier devient un bâton dont on règle la ligne. [déduit] L'autorité du mouvement vient du buste ; les membres « suivent » ou « traînent ». Le TSB M1 va dans le même sens : le torse y est la seule part clefée à chaque clé (mesuré).
2. **Le « smooth » en linéaire ne vient pas de courbes.** Il vient de quatre choses (vu + mesuré) :
   - (a) une grille lente (5 images) avec une seule compression brutale (2 images entre drag et middle) ;
   - (b) le retard porté par la pose (bras décroché qui traîne, tête qui garde son regard) ;
   - (c) un dépassement dans le même sens (exagération, puis encore plus d'exagération) ;
   - (d) une tenue vivante d'environ 1 s après environ 0,17 s d'action.
   - Rapport action/tenue mesuré sur le résultat : environ 1:7.
3. **La vitesse est un écart, pas un mouvement.**
   - Le tuto juge l'écart au fantôme de profil ;
   - firytwig ne dessine aucun intermédiaire entre chamber et attaque ;
   - le résultat final fait tout le coup en 1 image vidéo.
   - Trois sources, un même geste : deux poses très différentes, collées en temps, et l'œil fabrique la vitesse.
4. **Le chamber est tenu, l'attaque est tenue, le trajet n'existe pas** (firytwig, mesuré) :
   - chamber d'environ 0,1-0,27 s ;
   - attaque d'environ 0,17 s, avec un petit overshoot qui revient ;
   - la suite commence par ramener le membre pendant que le corps reste dans la fente.
5. **Translater les membres est permis.** Le bras est déplacé en position (448-451 s, 428 s) et décroché de l'épaule au drag ; le torse est déplacé autant que tourné. [déduit] En R6, où rien ne plie, la translation remplace le coude et le genou absents.
6. **Des outils de regard intégrés au rig** :
   - des faces colorées par direction ;
   - un rayon de regard pour verrouiller la tête ;
   - des boules aux pieds pour verrouiller les appuis ;
   - un fantôme de la clé 0 (et non seulement de la précédente) pour ce qui doit rester fixe.
7. **Contradiction utile entre sources.**
   - Le tuto et le combo posent **toutes les parts aux mêmes images**.
   - TSB M1 pose le torse plus souvent que les membres, et la tête rarement (mesuré).
   - Les deux marchent. Les tutos communautaires font le décalage dans la pose ; le pro ajoute des clés de buste seul.
8. **La grammaire des acrobaties R6** (Movement System) : une pose extrême où tout le corps est aligné sur une seule ligne, tenue 2-3 images, puis une rotation complète compressée en environ 0,25 s, puis une réception basse qui dure plus longtemps que la descente.

## 4. Ce qui me surprend ou contredit le cerveau

- **L'intro a deux personnages.** Les études précédentes décrivaient un perso seul, ramassé contre le mur.
- **Le Middle du torse est un cambré en arrière puis un roulis**, pas seulement un roulis sur le côté (130-131 s).
- **La pose clé du bras est construite par translation** (le bras flotte détaché à 448 s), pas seulement par rotation à l'épaule.
- **La tête est jugée par un rayon au sol**, loin du perso, pas par le visage.
- **Le bras gauche est tendu devant**, pas replié : ma propre note invalide disait « replié ».
- **Les durées ne collent pas** : la boucle mesurée fait 1,33 s au lieu de 0,92 s attendues. Les durées lues dans une capture de Moon ne sont peut-être pas fiables.
- **La pratique des pros contredit la règle « toutes les parts aux mêmes clés »** du tuto (TSB M1).
- **Le rythme du combo** est irrégulier, avec un écart de 10 images en tête de chaque coup : il ne suit pas la grille stricte de 5.

## 5. Ce que je saurais refaire en R6, concrètement

- **Un uppercut façon tuto, à 60 i/s, en linéaire :**
  - clés torse à 0 (profil, tassé), 5 (plonge), 10 (drag), **12** (redressé, cambré, tourné face, roulé d'environ 30°), 15-20 (roulis en plus, même sens), puis 25-55 (wiggle décroissant, rotation et translation de quelques degrés) ;
  - bras droit en travers devant à 0, derrière et bas à 5-10 (translaté hors de l'épaule), vertical au-dessus de la tête à 12 (tourné d'environ 180°), puis collé au torse ;
  - tête : regard fixe jusqu'à 10, accompagne à 12, suit ensuite ;
  - jambes : pieds recalés sur la clé 0 à chaque clé, une jambe levée qui suit le torse.
- **Un coup firytwig :**
  - chamber tenu 6-16 images ;
  - 0 intermédiaire ;
  - attaque avec overshoot d'1-2 images puis retour, tenue environ 10 images ;
  - recovery qui rentre d'abord le membre.
- **Un dash R6 :**
  - appel en 2 images ;
  - 3 images à l'horizontale, bras et jambes dans l'axe ;
  - rotation de 360° en environ 15 images ;
  - relevé accroupi en environ 6 images.
- **Organiser un combo** en blocs de 10+5+5 images, avec des poses voisines très contrastées ; la racine est clefée aux mêmes instants.

**Ce que je ne saurais pas :**
- les angles exacts du tuto (non lisibles) ;
- le contenu précis de chaque clé du wiggle ;
- la valeur de translation du bras « disloqué » ;
- si l'écart de durée vient de l'enregistrement ;
- les poses exactes du combo en l'air (139-150, hors cadre).

## 6. Suggestions pour nos productions (pistes, pas règles)

1. **Refaire le poing chargé en torse seul d'abord** (bras collés, jambes non posées), rejoué jusqu'à ce que la ligne du buste raconte la charge et la frappe. Ensuite seulement, poser les bras, puis les pieds recalés.
2. **Autoriser la translation des bras** au drag et au placement de la pose clé.
3. **Chercher la compression dans les clés, pas dans les courbes** : 2 images entre la dernière pose lente et la pose de frappe, et aucun intermédiaire.
4. **Mesurer notre rapport action/tenue** et le comparer à environ 1:7 (uppercut) et à environ 0,17 s d'attaque tenue (firytwig).
5. **Ajouter à nos outils de regard** un « rayon de regard » et un « fantôme de la clé 0 » pour les pieds et la tête.

## Vérification adverse

Vérificateur indépendant, 2026-09-26. J'ai réextrait toutes les images moi-même avec
ffmpeg, aux instants exacts, sans passer par les planches du lecteur. Mes extractions
sont dans `scratchpad/c4/frames/verif_B1_moon_smooth_r6/` : `ordre.png`, `fin_a.png`,
`fin_b.png`, `fin_timeline.png`, `astuces.png`, `astuces2.png`, `bras.png`,
`combo_tl.png`, `tsb_M1.png/.json` (planche_cles relancé), `fir_sheet.png`,
`fir_kick_zoom.png`, `intro.png`. J'ai regardé chacune de ces images.

| # | Apprentissage | Verdict | Ce que j'ai regardé | Correction |
|---|---|---|---|---|
| 1 | Ordre : torse seul, puis bras passif, bras actif, tête, jambes | **confirmé** | 16 images (29-635 s). À 150 et 250 s, bloc rigide. « Now Lets animate the arms! » à 303 s ; « Seeming as the left arm… first » à 305 s ; « uppercut/Right Arm » à 384 s ; « The Head is probably the easiest » à 555 s ; « And finally, the Legs! » à 635 s | Les temps sont décalés de 2 à 4 s (303 et 635 s au lieu de 301 et 631 s), sans conséquence |
| 2 | Le coup tient en une image vidéo, puis ~1 s de tenue | **nuancé** | 156 images natives à 30 i/s (745,5-750,7 s). Boucle 1 : #39-42 tassement, #43 drag, #44 bras en haut (face B), #45-47 fin de rotation, #48-78 tenue. **Boucle 2 : #83 drag, puis #84 image intermédiaire (bras à l'horizontale, flou), puis #85 bras en haut** | « Une image » dépend de la phase d'échantillonnage : 1 à 2 images vidéo selon la boucle. Le rapport 1:7 ne vaut que si l'on compte la frappe seule (~4 images). En comptant tassement + drag + frappe (~9 images) contre ~31 de tenue, on est à ~1:3,5 |
| 3 | Astuces de timing : 15→12 gardée, +5 déconseillé | **confirmé**, et complété | Zoom de la timeline à 271-300 s. On lit « 13 KEYFRAMES \| 60 FPS » et « 1:00 ». À 280,5 s, clés 0, 10, 15, 20… (astuce 1) ; à 284,5 s, retour à 0, 5, 10… ; « Though I DO NOT reccomend ». Sous-titre de l'astuce 2 : « move the middle keyframe closer to the drag (normally by 2 or 3 frames) and move the [reste]… left ». **À 298-300 s, clés à 5, 10, 12, 15, 20, 25, 30, 35** ; dernière clé à 55 (confirmé aussi à 746 s : « 0:55 \| 55f ») | Ce qui manquait au lecteur est visible : après l'astuce 2, les clés 20→60 reculent toutes de 5. On obtient 0, 5, 10, 12, 15…55, soit toujours 13 clés. La règle écrite est « 2 ou 3 images plus près du drag », pas une valeur fixe |
| 4 | Les membres se translatent (bras décroché au drag, pose placée en position) | **confirmé** | 20 images de 424,5 à 465,5 s. À 426,5 s, bras hors de l'épaule, en bas à gauche ; à 428,5 s, flèche de position rouge ; « It may look dislocated… ». À 448,5-449,5 s, bras rouge flottant détaché à côté de la tête ; à 450,5 s, redressé ; à 455-463 s, face bleue « B » du bras au-dessus de la tête | « Environ 180° » est une estimation. Je vois la face B, je ne peux pas mesurer l'angle |
| 5 | Combo Moon : toutes les parts sur les mêmes images | **nuancé** | Image à 10,0 s extraite moi-même, timeline zoomée x3. J'ai relevé les centres à 9,14 px/image (0 et 180 servent de repères). CFrame : 0, 10, 15, 20, 30, 35, 39, 45, 55, 60, 65, 70, 80, 85, 92, 100, 105, 110, 115, 121, 132, 139, 150, 155, 160, 169 : **identique** au lecteur (±0,3). Jambe droite : +18 et +103, **confirmé**. En-tête : « 0:04 \| 0.067s », donc 60 i/s | **Oubli : Torso, Right Arm, Right Leg, Head et Left Arm ont une double clé à 0 et ~1**, alors que CFrame n'en a qu'une à 0. La piste Left Leg est hors cadre, donc invérifiable. La formule « toutes les parts aux mêmes images » est donc presque vraie, pas vraie. La règle des blocs 10+5+5 est une lecture moyenne : on mesure aussi 8, 11, 7, 9 |
| 6 | TSB M1 : le pro clefe le torse plus souvent que les membres | **confirmé**, un chiffre à préciser | planche_cles relancé sur tsb_anim.rbxm. Clés i0, 6, 8, 10, 14, 20, 26 ; T 7/7, H 4, BD 5, BG 6 ; i20 = T seul ; jambes jamais ; lacet +48 → −70, dont +6 → −28 entre i6 et i8 (34°) | `--liste` annonce **8 clés** pour M1 : la 8e ne porte aucune part du corps (écartée par l'outil). Il faut écrire « 7 clés posées sur 8 ». La mention « jambes jamais » est un constat de l'outil (poids ≠ 0), pas une preuve que le pro ne touche jamais les jambes par la racine |
| 7 | firytwig : chamber tenu, zéro intermédiaire, attaque tenue + overshoot | **nuancé** | Toutes les images natives. Le fichier est **à fréquence variable, 40 i/s en moyenne, pas 60** : les images « à 60 i/s » du lecteur contiennent des doublons, précision ±33 ms. Kick : chamber de 1,033 à 1,283 s, extension complète à 1,317 s sans intermédiaire ; jambe plus longue à 1,317-1,367 s qu'à 1,400-1,467 s (overshoot vu) ; retour au chamber à 1,483 s. Tenue ~0,17 s : **confirmé** | **Punch : le bras n'est tendu que de 1,317 à ~1,383 s ; dès 1,400 s, le poing est ramené** alors que la fente reste tenue (le lecteur dit : tenue jusqu'à 1,47 s, poing ramené à 1,48 s). L'attaque du punch tient ~0,07 s, pas ~0,15 s |
| 8 | Durée de boucle mesurée ≠ timeline | **confirmé** (le constat, pas l'explication) | Redémarrages de boucle aux images natives #39 (746,77 s) et #79 (748,10 s) : 40 images, soit 1,33 s. Timeline : « 60 FPS », dernière clé « 0:55 \| 55f » | 55 images à 60 i/s font 0,92 s, contre 1,33 s mesurée : l'écart est réel. La cause reste non résolue. Il faut donc s'interdire de tirer des durées « temps réel » de cette capture |

**Hors échantillon, contrôlé rapidement :**
- L'intro a bien deux personnages ; les rougissements sont vus vers 0,13, 0,60 et 1,73 s (confirmé).
- Mais à 1,47 s, l'attaquant fait un grand déplacement, il se retourne et s'écarte du mur. « Entre les impacts, le corps bouge peu » est donc trop fort.

**Oublis importants :**
1. Combo : double clé en 0 et ~1 sur toutes les parts sauf CFrame. On voit aussi des marqueurs jaunes sur la règle (vers 52-53, 63 et 76-77), probablement des événements ou marqueurs d'effets, que le lecteur ne mentionne pas.
2. Résultat final, 2e boucle : il existe une image intermédiaire (#84, bras à l'horizontale). Le « coup en une image » n'est pas une propriété de l'animation mais de l'échantillonnage à 30 i/s d'une anim à 60 i/s.
3. Résultat final : à chaque bouclage (#39, #79), on passe de la pose de tenue accroupie face caméra à la pose de départ debout de profil, **sans aucune transition**. La tenue ne revient pas à la pose 0.
4. Astuce 2 : la fenêtre 10-35 après le décalage est visible (298-300 s : 10, 12, 15, 20…). Le lecteur l'a déclarée « non vue ».
5. Les bras sont eux aussi montrés en accéléré (« x5 » visible à 340 s), pas seulement les jambes : la couverture « à 1 i/s » est donc lacunaire sur l'étape 2.
6. firytwig : fréquence variable (40 i/s en moyenne). Toute mesure « à 60 i/s » de ce fichier doit être lue à ±1 image source.
