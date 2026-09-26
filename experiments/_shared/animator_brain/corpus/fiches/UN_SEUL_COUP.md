# Fiche de conception : UN SEUL COUP (Serious Punch, cinématique complète)

**Rappel** : `python3 outils/rappel.py "serious punch un seul coup conséquence
horizon"`. Choisie par Milan le 2026-09-26 (« Vazy 1 ») parmi
`../../PROPOSITIONS_CINEMATIQUE_2026-09-26.md`.

Sources digérées ensemble (relues à 0,1 s le 2026-09-26, bandes `durees.py`,
fichiers jamais versionnés, voir `../CATALOGUE_REFS.md`) :
- **Serious Punch TSB** (48244687, 10,07 s) ;
- **Serious Punch 2** (772ee6b0, 7,19 s) ;
- **Serious Punch de Pew** (lvB-wTylH3Y, 16,4 s dont 2 s de générique) ;
- la fiche `COUP_CHARGE.md` (structure du Serious Punch, obari, pistes §5,
  reprise §7) ;
- CARNET : 2.5b (silence avant), 2.6b (suite très longue), 4b.26 (relire
  comme un spectateur), 4b.28 (conditions du spectateur), 4b.29 (Roblox
  premium : de la 3D, pas de planches 2D), 4b.30 (lent / tenu + 1 à 3 coups
  rapides ; moins de coupes, un plan qui suit) ;
- RETOURS : 7,85 puis 8 (« pas premium mais mid haut ») ; « trop peinture »,
  planches retirées ; « le dragon va dans tous les sens ».

## 1. Ce que les trois refs font, à 0,1 s

| temps | TSB (48244687) | SP2 (772ee6b0) | Pew (lvB-wTylH3Y) |
|---|---|---|---|
| entrée | 0-0,3 caméra de jeu ; 0,4-1,7 le bras / la cape en TRÈS gros plan traverse l'écran (1,3 s) | 0-1,1 même traversée (manteau) | 0-0,9 caméra de jeu, perso de dos |
| calme | 1,8-2,9 plan moyen de FACE, debout, immobile (1,1 s) | 1,2-2,3 idem (1,1 s) | 1,0-2,2 3/4 bas, il lève le poing, tenu (1,2 s) |
| départ | 3,0-3,5 il part, la caméra fouette vers le ciel (0,5 s) | 2,4-2,9 idem, ciel (0,5 s) | 2,3-2,6 fouet vers le ciel (0,3 s) |
| approche | 3,6-4,5 plan large et bas, perso PETIT, fente (1 s) | 3,0-4,0 idem (1 s) | 2,7-3,6 3/4 derrière, il s'accroupit (0,9 s) |
| armé | 4,6-5,1 plus près, il se relève, bras armé (0,5 s) | 4,0-4,8 très bas, genou haut (0,8 s) | 3,7-4,7 armé TENU face-bas, tremble (1 s) |
| frappe | 5,2-5,9 poing vers l'objectif dans la fumée (0,8 s) | 4,9-5,3 idem (0,4 s) | 4,8-5,1 poing vers l'objectif, fumée (0,4 s) |
| impact | 6,0-6,1 carte ENCRE (silhouette + hachures radiales) ; 6,2-6,3 BLANC ; 6,4-6,5 le blanc se dissout | 5,4-5,5 2 cartes encre ; 5,6-5,9 blanc qui fond | 5,2-5,3 **2 images INVERSÉES** (la scène en noir sur blanc : perso et roches noirs, ciel blanc) |
| conséquence | 6,6-9,5 fente basse TENUE, poing en avant ; derrière lui un champ de grandes dalles de roche en pyramide + fumée ; caméra FIXE (3 s) | 6,0-7,1 idem (1,1 s, coupé) | 5,4-5,6 gros plan de 3/4 sur la fente, roches énormes au 1er plan ; **5,7-13,4 plan FIXE de DOS en hauteur d'homme : le perso minuscule au centre, un champ de roches sombres devant lui, fumées blanches qui montent puis s'effacent (5,7-8,2), tout tenu ; les roches s'enfoncent (12,7-13,4) ; plaine vide jusqu'à l'horizon** (7,7 s) |
| fin | 9,6 caméra de jeu, debout | — | 14,6 fin |

**Mesures (serious_punch_tsb.json)** : 1 impact en 10 s ; 1 seule carte
(267 ms) ; 3 tenues, la plus longue 467 ms ; « part rapide » 1 % du temps.

## 2. Ce que j'en retiens (lectures, pas règles)

- **Un seul coup rapide** dans toute la scène : l'élan (0,3-0,5 s) et la
  frappe (0,4 s). Tout le reste est tenu ou lent. C'est 4b.30 appliqué au
  perso : « part rapide » 1 % chez TSB.
- **Le corps n'est montré que deux fois en gros** (armé, frappe) ; le reste,
  c'est l'échelle (perso petit dans un plan large) et la caméra.
- **L'impact est court et PAUVRE en effets** : 1-2 cartes, un blanc, c'est
  tout. Pas d'explosion colorée. La puissance se lit APRÈS, dans le décor.
- **La conséquence est la scène.** TSB : 3 s de dalles de roche derrière la
  fente tenue. Pew : 7,7 s d'un seul plan fixe, de dos, perso minuscule,
  roches jusqu'à l'horizon. C'est le moment dont on se souvient.
- **Le décor raconte** : des dalles SOMBRES en pyramide (volumes simples,
  facettes plates : du Roblox, pas de la peinture), de la fumée BLANCHE qui
  monte en colonnes et s'efface.
- **La carte inversée de Pew** (la scène elle-même en noir sur blanc) est
  plus « Roblox premium » qu'une planche dessinée (4b.29 : 3D plutôt que
  2D) : elle se fait avec la scène 3D, sans image peinte.
- **Aucune des trois refs ne fend les nuages** ; c'est l'image du manga
  (Saitama contre Boros) et ce qui peut nous faire dépasser les refs (le
  « cap premium » demandé). À tenir sobre : un sillon qui s'ouvre, lent.

## 3. La scène (60 i/s, ~12,5 s)

Décor : une grande plaine ouverte (terre et pierre grises), des montagnes
basses tout autour à l'horizon (~450-600 studs), une couche de nuages
(~110 studs de haut). Pas d'arène fermée : il faut voir loin.

Personnages : l'attaquant (costume jaune, gants et bottes rouges, crâne nu :
Saitama en R6, SANS cape, mandat §1) face à la victime (noob) à ~16 studs.

| # | temps (s) | ce qui se passe | caméra | son |
|---|---|---|---|---|
| 1 | 0-1,3 | plan large de DOS : la plaine, la victime en garde au loin, lui debout, bras ballants. La caméra pousse jusque DANS son dos (le dos remplit l'écran = transition) | poussée continue de dos, basse | vent seul |
| 2 | 1,3-2,6 | **CALME** : debout, visage plat vers la victime, presque rien (respiration, un pan de poussière passe) | plan moyen de FACE, fixe, un peu en contre-plongée | vent ; silence |
| 3 | 2,6-3,05 | il se ramasse (6 i), part ; la caméra fouette vers le ciel | fouet | coup sourd au départ, souffle |
| 4 | 3,05-3,9 | **approche** : fente très basse, torse presque horizontal, traînée de poussière ; la victime lève sa garde | large et BAS, il est petit | pas qui claquent |
| 5 | 3,9-4,35 | **armé** : il se relève en tordant le buste, poing derrière à la hanche, genou haut, l'autre bras devant ; tenue 0,15 s qui tremble | très gros plan de FACE en contre-plongée, qui recule devant lui | aspiration |
| 6 | 4,35-4,72 | **frappe** : le poing vient VERS L'OBJECTIF dans un tourbillon de fumée (obari) ; contact SAUTÉ | la caméra est chez la victime | silence net juste avant |
| 7 | 4,72-5,35 | 2 images **INVERSÉES** (la scène 3D en noir sur blanc, 2 × 4 i), puis BLANC 0,2 s qui se dissout en fumée ; la victime part pendant le blanc | — | BOUM (grave) |
| 8 | 5,35-8,6 | **conséquence 1** : de DOS, un peu haut ; il est en fente, poing tendu, TENU. Devant lui la destruction FILE jusqu'à l'horizon : des dalles de roche sortent du sol en vague (le seul « rapide » de la conséquence, ~1,4 s pour 450 studs), des colonnes de fumée blanche montent ; la victime, un point, disparaît au loin | fixe, poussée très lente | grondement qui s'éloigne, rafales |
| 9 | 8,6-10,3 | **conséquence 2** : les nuages se FENDENT le long de la ligne (sillon bleu qui s'ouvre lentement) | plan haut, derrière lui, qui regarde la ligne et le ciel | vent qui retombe |
| 10 | 10,3-12,5 | **conséquence 3** : le vent retombe ; il se redresse lentement, baisse le bras, main à la hanche (« dans la poche »), regarde au loin ; la fumée s'étire | profil bas, lui à gauche, la ligne jusqu'à l'horizon à droite | quelques cailloux ; silence ; fin |

Proportions : départ + frappe (les seuls moments rapides) ≈ 0,9 s sur
12,5 s ; conséquence 7,2 s (entre TSB 3 s et Pew 7,7 s), vivante (vague,
fumée, nuages, redressement) plutôt que figée. 9 plans, dont 3 dans la
conséquence (4b.30 : peu de coupes, des plans qui durent).

## 4. Pièges (d'après nos propres erreurs)

- Ne pas recharger l'impact d'effets (v12 : VFX 2-4 ; v13 : « trop
  peinture ») : ici l'impact = 2 images inversées + blanc, point.
- Le poing vers l'objectif : un membre pointé vers la caméra cache tout sauf
  lui (repro obari) ; la caméra à côté de la victime, jamais derrière son
  corps (v6).
- La conséquence tenue ne doit pas être un écran figé : Pew tient 7,7 s
  parce que la fumée bouge ; chez nous, les 3 dernières secondes du Poing
  du Dragon étaient « statiques » (ETAT §5).
- Échelle : le perso doit être PETIT dans les plans larges (approche,
  conséquence), sinon la destruction n'a pas de mesure.
- Vérifier le rendu dans le lecteur publié, pas seulement dans mes captures
  (4b.28).

## 5. Livré (2026-09-26) et prédiction

Production : `experiments/r6_un_seul_coup/` (README : découpage final,
vérifications, ce qui a été corrigé en regardant). Écarts à ce plan :
- les moments rapides font ~1,4 s (élan + glissade ~1 s, frappe 0,37 s),
  pas 0,9 : la glissade vue en large et basse se lit lente, perso petit ;
- conséquence 1 filmée de 3/4 haut, pas de dos (CARNET 4b.31) ; la fente des
  nuages est calée sur le plan au-dessus des nuages (4b.32).

**Prédiction avant l'avis de Milan : 7,8/10** (structure et retenue du
Serious Punch tenues, destruction lisible jusqu'à l'horizon, nuages qui se
fendent ; restent : les persos R6 en blocs lisses, l'armé moins lisible que
le reste, la 1re conséquence tenue 3,3 s sans grand changement, fumées en
sprites doux plutôt que « dessinées »).

## 6. v2 (retour de Milan sur la v1, 2026-09-26)

Ses mots : « la scène où le perso réduit la distance, je veux que tu la
changes : ça doit être comme si le perso allait ultra vite, donc tu casses le
sol de son point de départ, puis la scène apparaît avec le moment où le perso
charge son poing et frappe la victime ; autre problème qui revient un peu,
comme dans le Poing du Dragon : le perso frappait vers le bas. Le perso
charge son poing, il l'arme en le ramenant à l'arrière et en tournant son
buste. » Refs ajoutées (catalogue) : Gon accroupi poing à la hanche (HxH),
Saitama manga coup à plat, Saitama de dos buste tordu, poing rouge (OPM).

**Mesuré sur la v1 (pas vu à l'œil avant lui)** : au contact le buste était
penché de 40°, le poing à 2,5 studs du sol (le bas-ventre d'une victime
elle-même accroupie en garde), la tête à 3,5 ; pendant l'armé le bras
pointait à -25°. C'est EXACTEMENT le défaut du Poing du Dragon v3-v7 (« les
coups partent du bas », COUP_CHARGE §1), revenu par la pose : « fente très
basse, torse presque horizontal » (TSB) appliquée au contact au lieu de
l'approche.

**v2** :
- départ : il se ramasse (plan de profil, en entier), part en 3 images, le
  sol casse (trou fissuré, dalles soulevées, poussière, sillage jusqu'à la
  victime) ; 0,27 s sur le trou vide ; coupe ;
- charge 1,4 s devant la victime : appuis larges, buste presque droit (12°)
  qui TOURNE jusqu'à -66°, poing ramené derrière, tenue qui tremble,
  cailloux qui se soulèvent autour des pieds, vent autour du poing ;
- frappe : bassin puis buste puis épaule, coup À PLAT : buste 7°, bras -5°,
  poing à 3,4 studs (poitrine d'une victime debout) ; tenue bras à -3°.
- Nouveaux contrôles d'export (verify_export.py) : bras à plat au contact et
  pendant la tenue (< 12°), buste presque droit (< 22°), poing à hauteur de
  poitrine (> 3,2), poing derrière le buste pendant la charge.

Prédiction v2 : **8,0/10**.

## 7. v3 : le POING CHARGÉ (clip de Milan, 2026-09-26, v2 notée 7/10)

« Le moment ultra rapide, très bien ; mais toujours pas le poing chargé, tu ne
captes pas le truc. » Son clip : 4 captures du Serious Punch de Pew (2,9 -
5,0 s de lvB-wTylH3Y, relues à 0,1-0,2 s) + Saitama de TSB (de dos).

**Ce que je n'avais pas compris** : le poing chargé est un MOUVEMENT d'arc
qu'on tend, pas une pose.
1. Il est en garde, face à elle.
2. Il s'ENFONCE (genoux très pliés) et TOURNE jusqu'à être de profil,
   presque dos à elle (Saitama TSB : on voit son dos) ;
3. les DEUX BRAS S'ALIGNENT sur la ligne des épaules, tendus : le poing
   droit loin derrière, l'autre bras vers la victime (Pew 3,9-4,5 : un T
   couché, bien lisible en R6 où un bras ne plie pas) ; la tête rentre ;
4. tenue ~0,8 s qui tremble (la tension monte) ;
5. tout se DÉROULE d'un coup (180°) : le bras qui visait revient, le poing
   part à plat.
La v2 avait le poing déjà derrière dès l'arrivée (0,6 stud de recul en
1,4 s) et le buste de face (-66°) : pas d'arc, donc pas de charge.

**v3** : garde à l'arrivée (0,2 s, vue après la coupe) -> l'arc se tend en
0,4 s (racine -48°, bassin -50°, bras alignés à ±180°, s'enfonce de 0,85)
avec dépassement -> tenue qui tremble (torsion +7°, compression) ->
dernière compression 4 i -> détente 12 i. Caméra de face côté poitrine :
le T se lit, la victime dans le cadre.

Prédiction v3 : **7,8/10** (le mouvement est celui du clip ; incertain :
est-ce la bonne lecture de « charger » pour lui, et la détente de 12 i).

## 8. v4 : la POSE de charge (Milan sur la v3 : « je vois aucun changement »)

Pas un bug (les fichiers v2 / v3 diffèrent) : Milan précise que c'est **la
pose de charge**. Revue en grand, sous plusieurs angles : Pew 2,95 / 3,4 /
4,2 / 4,6 s, TSB 4,6-5,1 s, SP2 4,2-4,8 s. Ce que les trois font et que la
v3 ne faisait pas : il se **RAMASSE comme un ressort écrasé** -- genoux très
pliés (hanches presque aux genoux), **buste COURBÉ en avant**, **tête basse**,
bras écartés SOUS le buste (poing derrière un peu bas, l'autre bras devant).
La v3 : presque debout (buste 17°), tête droite, bras en croix à hauteur
d'épaule -> un bonhomme debout bras écartés, pas une charge.

v4 : buste courbé 57° pendant la charge, hanches à -1,05, tête basse ; bras
écartés sous le buste ; la charge est filmée de SA droite, un peu de face,
en contre-plongée (l'angle de Pew face-gauche essayé : le bras avant cachait
le corps ramassé ; choisi avec le tour à 8 caméras de la pose). Le coup
reste à plat (buste 7°, bras -5°, poing 3,4 studs) : le bas et le courbé
sont pour la CHARGE, jamais pour l'arrivée du coup (CARNET 2.9).

Prédiction v4 : **7,6/10**.

## 9. Comparaison visuelle v4 contre les refs (demandée par Milan, 2026-09-26)

Planche 4 phases x (Pew, TSB SP1, TSB SP2, nous v4) + notre charge vue sous
l'angle de chaque ref + les 4 images anime. La planche contient des images
des refs : elle n'est PAS versionnée (règle des refs) ; ce qui suit en est
la lecture.

| phase | refs | nous v4 | écart |
|---|---|---|---|
| 1. il arme | TSB 4,6 : fente, GENOU AVANT LEVÉ haut (lanceur), bras qui arme derrière l'épaule ; Pew 3,4 / SP2 4,2 : il se tasse, buste courbé | il se tasse, bras qui s'écartent | pas de genou levé ; tassement lisible |
| 2. charge tenue | caméra COLLÉE et basse, le perso remplit 70-90 % de l'image ; SP2 4,5 et TSB 4,9 : buste tourné au point qu'on voit son CÔTÉ / DOS, bras qui charge CACHÉ derrière ; Pew 4,2 : courbé, bras écartés | vu de loin (~8 studs, le perso ~40 % de l'image), de sa poitrine, bras bien écartés ; jambe de la victime dans le cadre | cadrage trop LARGE ; torsion pas assez forte (on voit la poitrine, pas le côté/dos) |
| 3. départ | le bras passe À PLAT EN TRAVERS devant le buste qui tourne, en gros plan (TSB 5,2), fumée qui naît (Pew 4,8) | coupe sur le regard de la victime : l'attaquant est loin, on ne voit pas le buste tourner | la rotation du coup n'est pas montrée |
| 4. poing vers l'objectif | poing + avant-bras en 3/4, l'épaule derrière, TOURBILLON de fumée autour | un carré rouge plat qui remplit l'image, pas d'épaule, peu de fumée | poing de face pur (illisible), sans fumée |

Sous l'angle des refs (caméra basse de face), notre charge est masquée par la
jambe de la victime : chez les refs la victime n'est jamais dans le plan de
la charge.

**Pistes (non décidées, à montrer à Milan)** : (a) charge en GROS PLAN bas,
victime hors champ ; (b) torsion poussée jusqu'à montrer le côté/dos, bras
qui charge caché ; (c) option TSB : genou avant levé pendant l'armé ; (d)
montrer le départ du coup en gros plan (buste qui tourne, bras en travers)
avant le plan de la victime ; (e) plan du poing en 3/4 avec l'épaule et un
tourbillon de fumée.

