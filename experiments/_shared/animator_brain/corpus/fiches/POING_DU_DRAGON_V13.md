# Fiche de conception : Poing du Dragon v13, la scène complète

**Demande de Milan (2026-09-25, après la v12 notée 4)** : « Le dragon or,
le dragon est invoqué dans les airs comme Goku, puis le coup se transforme
en le dragon qui mange le perso. […] Je veux que tu refasses tout, je veux
la scène complète niveau 8,5/10 globale : animation à revoir, plus smooth,
plus abusé, plus en rapport avec nos refs ; VFX de qualité dessin, pas du
cube ou cartoon. Améliore notre architecture, vérifie le jugement. »

**Rappel** : `python3 outils/rappel.py "dragon qui mange invocation ultime"`.
Sources digérées ensemble ici :
- `../RELECTURE_LAST_BREATH_GOKU_2026-09-25.md` (Last Breath v1-v3 à 0,1 s,
  GIF Goku d514ee70 et 656d965b) ;
- `../RELECTURE_REFS_SUIRYU_2026-09-25.md` (tête, accent des yeux) ;
- `../RELECTURE_REFS_VFX_STYLE_2026-09-25.md` (échelle de valeurs, encre) ;
- `../tutos/ETUDE_ARCHIVE_VIDEOS_1_2026-09-25.md` §3 (temps d'un ultime) ;
- `AURA_DRAGON.md`, `COUP_CHARGE.md`, `VFX.md` ;
- retour v12 (`../../RETOURS.md`) : dragon 0,5 s et au mauvais endroit,
  VFX 2-4, animation 7,7, total 4.

## 1. Ce que la v12 ratait (mesuré, pas ressenti)

| | v12 | refs (Last Breath, Goku, ultimes TSB) |
|---|---|---|
| invocation | 0,50 s | Goku 2 s tenu ; Last Breath : le dragon tourne 3 s |
| le dragon à l'écran | 0,57 s (invocation) + montée finale | présent 4-6 s, énorme, plus long que le cadre |
| ce que fait le dragon | décor autour du bras, rentre dans le poing | il EST le coup : il mange la victime |
| abstraction plein écran | 0,1 s de cartes + blanc | 1,6-2,5 s (feu, rouge, soleil, manga) |
| part d'effet au pic | 0,33 | 0,49-0,77 (Roblox), 0,99 (anime) |
| conséquence large | 2,8 s calmes | 2,7-7 s, avec quelque chose qui se passe |
| matière du dragon | or éclairé (statue) | aplat + trait peint, yeux lumineux |

## 2. La scène v13, en secondes (60 i/s)

Les actes 1-3 (rafale, coup chargé, envol : 0-3,3 s) restent : Milan a noté
l'animation 7,7 et n'a rien reproché à ces actes. Tout ce qui suit l'apex
est refait.

| acte | frames | durée | ce qui se passe | ref |
|---|---|---|---|---|
| 1. rafale | 0-118 | 2,0 s | inchangé (4 coups, Black Flash) ; impacts en VFX dessinés | — |
| 2. coup chargé | 118-170 | 0,9 s | inchangé | Serious Punch |
| 3. envol | 170-200 | 0,5 s | inchangé (whip pan) | — |
| 4. calme | 200-224 | 0,4 s | il flotte au-dessus de la victime | COUP_CHARGE §7 |
| **5. invocation** | 224-360 | **2,3 s** | le poing monte au ciel ; le dragon d'or JAILLIT du poing vers le ciel (0,3 s), s'enroule en grand dans le ciel au-dessus de lui, tête qui rugit (gros plan 0,5 s), puis se tourne vers la victime | Goku 656d965b (tenu 2 s), Last Breath v1 (tourne 3 s) |
| 5b. regard | 336-360 | 0,4 s | contre-plongée sur l'attaquant, poing au ciel, le dragon derrière lui | Last Breath v1 13,6 s, v2 7,0 s |
| **6. le coup devient le dragon** | 360-392 | 0,5 s | il plonge et frappe vers la victime ; le dragon se RASSEMBLE dans le poing (spirale qui rentre), le poing s'arrête à 2 studs de la victime, flash, et la TÊTE du dragon sort du poing, gueule ouverte | Goku d514ee70 (le dragon sort du coup) |
| **7. il la mange** | 392-420 | **0,45 s** | la tête traverse vers la victime (et vers la caméra), la gueule s'ouvre en grand, se referme sur elle ; la victime disparaît dans la gueule | Last Breath v2 10,3 s (0,4 s) |
| 8. carte manga | 420-450 | 0,5 s | la gueule à l'encre (dessinée depuis NOTRE modèle), puis carte inversée | Last Breath v1 17,0 s |
| **9. plein écran** | 450-570 | **2,0 s** | tourbillon de feu peint (cœur blanc, bandes or, orange, rouge sombre) qui tourne, puis rouge radial et horizon à rayons, puis soleil orange avec la silhouette noire du dragon qui plonge | Goku 1,0-2,1 s ; Last Breath v1 18,3-20,4 s |
| 10. conséquence | 570-760 | 3,2 s | plan large : le dragon a plongé dans le sol, cratère, colonne d'explosion ; il ressort du sol en spirale vers le ciel en rugissant et se dissout ; la victime est recrachée dans le cratère ; l'attaquant atterrit | Last Breath v1 20,6 s (2,7 s), v3 (3,4 s) |
| 11. retour | 760-820 | 1,0 s | il se relève, regarde la victime | — |

Durée totale ≈ 13,7 s + hitstops (v12 : 8,8 s). Le dragon est à l'écran de
f236 à ~f420 puis dans la conséquence (~5 s au total, contre 0,57 s).

## 3. Le dragon (acte 5 à 10)

- **Or, dessiné** : aplat or, ombre orange franche (deux tons, pas de
  dégradé), trait brun sombre épais autour et sur chaque anneau du ventre,
  écailles en traits (pas sculptées), épines sombres, moustaches et crocs
  blancs, gueule rouge ; **yeux CYAN lumineux** (accent complémentaire,
  Dragon Ball Rage). Aperçu : matériau non éclairé à 2 tons + contour
  (coque inversée) ; Roblox : les deux tons peints dans la texture +
  Highlight (contour).
- **Mâchoire animable** : un os « Machoire » (charnière au fond de la
  gueule), angle piloté par la recette (`machoire` : [[a, degrés], …]).
  Fermée au repos (6°), rugissement 45°, morsure 58° puis claque à 4° en
  2 images.
- **Taille** : échelle 2,2 à l'invocation et à la morsure (tête ≈ 12 studs,
  corps ≈ 30 studs) : plus long que le cadre, comme Last Breath.
- **Chemin** : toujours échantillonné hors ligne sur les pistes réelles
  (staging.py), en temps de RECETTE.

## 4. Caméra (plans)

| frames | plan |
|---|---|
| 224-250 | contre-plongée 3/4 face, l'attaquant bas dans le cadre, le ciel au-dessus : le dragon JAILLIT vers le haut du cadre |
| 250-300 | plan très large en contre-plongée : le dragon s'enroule dans le ciel, l'attaquant petit au centre (échelle) |
| 300-336 | gros plan de la tête du dragon qui rugit (gueule 45°), secousse |
| 336-360 | contre-plongée sur l'attaquant, poing au ciel, dragon derrière |
| 360-392 | obari : caméra à côté de la victime, le poing arrive, radial derrière |
| 392-420 | de profil, un peu au-dessus : la tête traverse et engloutit la victime (lisible : profil = la gueule se voit) |
| 420-570 | plein écran (cartes et planches peintes, la 3D est masquée) |
| 570-760 | plan large, le cratère au premier plan, le dragon monte dans le ciel |
| 760-820 | dos de l'attaquant, la victime au loin |

## 5. VFX (tous « dessinés » : mesh + texture peinte à bord net + en 2)

- rafale : croissant d'impact en `arc_trait` (feu), lames courtes ;
- jaillissement du dragon hors du poing : `jaillissement_dessine` (feu) au
  poing + trait en spirale qui monte ;
- invocation tenue : aura or en langues dessinées autour du corps, rayons
  de lumière dans le ciel ;
- la tête sort du poing : `tornade_dessinee` autour du bras + flash ;
- la morsure : croissants de vent blancs + griffures d'encre ;
- conséquence : cratère, `jaillissement_dessine` + tornade au sol,
  débris, fumée, braises, traînée de feu.

Plein écran (acte 9) : planches PEINTES (PIL), jouées « en 2 » (12 i/s),
tournées et zoomées par le lecteur (Roblox : ImageLabel.Rotation / Size) ;
la silhouette du dragon et la gueule manga sont tirées de NOTRE modèle.

## 6. Son

Rugissement à la naissance (0,3 s), rugissement long au gros plan, souffle
coupé avant la sortie de la tête, claquement de mâchoire (grave, sec),
grondement sous le plein écran, explosion au retour du réel, rugissement
lointain qui monte, vent.

## 7. Jugement avant de montrer (porte)

- durées mesurées avec `outils/durees.py` sur NOTRE vidéo, comparées à
  Last Breath et Goku : invocation ≥ 1,8 s, plein écran ≥ 1,6 s, part
  d'effet au pic ≥ 0,5, conséquence ≥ 2,5 s ;
- regarder la bande à 0,1 s en entier, pas des images choisies ;
- `corps_bras.py`, `tour.py`, contacts ;
- prédiction VFX corrigée du biais mesuré (+3,0).

## 8. Pièges connus (hérités)

- tête de dragon entre l'objectif obari et le poing : la cacher (v10) ;
- images de serpent en temps de RECETTE, pas relatif (v12) ;
- cou vertical = pilier ; tête piquée = on ne voit que le crâne (v10b) ;
- spires devant le visage (v10b) ;
- un plan fixe choisi cache la durée (CARNET 4b.12).

## 9. Ce qui a été fait (tel que construit, 2026-09-25)

Écarts à la conception, tous vus à l'écran (planches `rev1`-`rev5`,
captures `captures/verification/2026-09-25-v13-*`) :

- **Coup à distance** (§2 acte 6) : la conception disait « le poing
  s'arrête à 2 studs ». La tête du modèle fait ~8 studs devant son os à
  l'échelle 1,4 : elle traversait la victime avant d'être sortie ; le
  détour « monte puis plonge » était illisible. Le poing s'arrête à ~5
  studs (`poing_s_arrete_avant_la_victime`, 3,5-7) ; la tête sort derrière
  le flash, ouvre la gueule 0,25 s, claque en avançant (CARNET 4b.22).
- **Jaillissement de profil**, fusion par derrière, gros plan à 15 studs
  (CARNET 4b.23).
- **Plein écran** : 0,5 s de carte manga + 0,83 s de tourbillon + 0,72 s
  de rouge + 0,4 s de soleil = 2,45 s (le soleil à 0,28 s laissait 4 images
  du vrai décor avant le blanc).
- **Conséquence** : le dragon JAILLIT du cratère (12 studs en 0,3 s) et
  recrache la victime, qui retombe 0,9 s ; la caméra le suit vers le ciel.
- **Pas cartoon** : boules de feu cel et nuages ronds cernés retirés des
  impacts du sol et de la morsure (CARNET 4b.24).
- **Revue sans Milan (v13c)** : fusion = le MUSEAU (6 studs devant l'os à
  l'échelle 1,9) touche le poing à f363, éclat d'or, fondu en 3 images, le
  poing garde le feu jusqu'au coup ; la tête naît et monte DERRIÈRE lui ;
  au regard elle est 12,5 studs au-dessus du poing ; morsure en
  contre-plongée ; flash au moment où la victime est avalée ; atterrissage
  à côté de la colonne de feu ; dernier plan de côté (les deux) ; sons
  jusqu'à la fin. Détail : `../../RETOURS.md` (2026-09-25, revue), CARNET
  4b.26.
- **v13d (Milan : planches retirées ; « le dragon n'apparaît pas là où il
  faut, et très peu »)** : bug du lecteur publié (three.js r128 sans
  `skinning` : dragon figé en pose de repos) corrigé en embarquant r134 ;
  f400-f574 : la victime dans la gueule, rase-mottes, grande boucle dans le
  ciel (sommet f508, 42 studs), retournement, plongeon dans le cratère au
  blanc (f564). Caméra : très large face à la boucle (l'attaquant donne
  l'échelle), contre-plongée au sommet, puis depuis le cratère.
- **v13e (Milan 7,85 : bugs, polissage, rythme « dans tous les sens »)** :
  allure mesurée (`outils/allure.py`) et refaite : lent / tenu sauf
  jaillissement, morsure, plongeon ; WA (invocation) en une courbe lente +
  anticipation ; WB (vol) monte en ralentissant, suspendu au sommet f510-527,
  plonge en accélérant ; remontée sans spirale. Caméra : recul continu
  f226-298, suivi de profil f480-530. Bugs : flash blanc à l'image 0 retiré,
  feu / fumée cel retirés du coup chargé, bras de la victime au rebond.
  Braise au fond du cratère.

