# Poing du Dragon v7 : BROUILLON de fiche

État : **brouillon, pas exécuté**. Il attend la fin de l'étude des tutos
vidéo (zips de Milan), puis le go de Milan. Objectif : 8/10 minimum.

## Ce que Milan a dit (v6 : 7/10)

- Caméra de jeu : rend bien. Caméra ciné : un peu trop abusée, mais léger.
- L'animation reste le bémol : il manque « une touche manga ». Même un coup
  simple n'est pas un coup simple : il y a une anatomie et une règle
  différentes. Le rythme est bon ; le corps secondaire et la victime sont des
  détails.

## Ce que l'étude a trouvé (sources dans le cerveau)

1. **Nos poses du coup chargé** (`ETUDE_TSB.md` §4 ter) :
   - pendant la charge, une **croix symétrique**, torse vertical ;
   - au contact, torse **vertical**, seul le bras part.
   - TSB et l'anime : compression en C, puis une **ligne** hors d'équilibre
     du pied arrière au poing.
2. **TSB, fichier officiel** :
   - clés éparses (~15/s) en Linear ;
   - le corps bascule fort sur les compétences (44-97°) ;
   - le combo se ferme par un **coup de pied** (M4).
3. **A/B clés éparses** : fidèle à TSB, mais presque invisible sur ce coup.
   Le levier est la **pose**, pas l'export.
4. **Croquis au labo de poses** (`outils/poselab.py`) :
   `captures/verification/2026-09-24-croquis-v7-charge-contact-vs-v6.png`.
   - Charge en C : torse enroulé à −70° de lacet et penché de 22°, tête
     rentrée, poing armé bas derrière, l'autre bras vise.
   - Contact en ligne : torse penché de 30 à 38° et tourné de 40°, bras
     horizontal, jambe arrière dans l'axe du torse, jambe avant quasi
     verticale, bras libre tiré en arrière et vers l'extérieur (hors
     silhouette en caméra de jeu).
   - Pas accroupi : c'était le rejet de Milan en v1-v2.

## Pistes de refonte (une par temps, chacune vue avant d'animer)

| temps | v6 | v7 proposée | pourquoi |
|---|---|---|---|
| charge f118-146 | croix symétrique, torse droit | **C comprimé** (croquis) ; tenue vivante gardée | anime (tame, compression), TSB Stoic Bomb (charge compacte) |
| coup f146-158 | torse vertical, bras seul | **ligne jetée** 30-38° (croquis) ; 1 image de dépassement puis retour | anime (Mattesi, Cartwright), TSB compétences |
| rafale h4 f78-104 | 4e poing | à décider avec Milan : **coup de pied ou genou** pour fermer le combo, corps qui bascule | TSB M4 = coup de pied ; variété (`variete_coups` faux depuis v4) |
| export | chaque image cuite | **poses clés seules** (~15/s) en Linear | TSB ; neutre visuellement ici, mais fidèle |
| caméra ciné | v6 | **un cran moins** (durées de gros plans, secousses) | retour Milan « un peu trop abusé » |
| aérien | aimé | **inchangé** | ne pas casser ce qui marche |

## Estimation (à affiner après l'étude des tutos)

- Le cerveau prédit 7,1 pour la v6 (Milan : 7).
- La refonte des poses du sol est le levier que Milan désigne lui-même
  (« l'animation »). Estimation prudente : **7,6 à 8,2** si les deux poses
  clés passent à l'écran.
- 8 n'est pas garanti : la « touche manga » est jugée par Milan, pas par une
  mesure. D'où la vérification visuelle pose par pose avant l'export.
