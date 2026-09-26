# Relecture image par image : Last Breath v1-v3 (TSB) et Poing du Dragon (Goku)

Pourquoi ce fichier existe : Milan, après la v12 (note 4), a demandé « le
dragon or est invoqué dans les airs comme Goku, puis le coup se transforme
en le dragon qui mange le perso… est-ce que tu as bien analysé tout ?
Même visuellement ? ». Réponse honnête : **non**. Les passages Last Breath
de la vidéo TSB « animations abandonnées » (4e0sX6p8-30) n'avaient été vus
qu'à une image par seconde. Ce fichier est la relecture à **0,1 s** (bandes
`outils/durees.py`, 10 vignettes = 1 s, courbe de part d'effet dessous).

Les images ne sont pas versionnées (refs sous droits) ; seul ce texte
dérivé l'est. Rejouer la relecture :

```
ffmpeg -ss 108 -t 24 -i 4e0sX6p8-30*.mp4 lb1.mp4          # Last Breath v1
ffmpeg -ss 131.5 -t 14.5 -i 4e0sX6p8-30*.mp4 lb2.mp4      # v2 (+ début v3)
ffmpeg -ss 145.5 -t 16 -i 4e0sX6p8-30*.mp4 lb3.mp4        # v3 (+ début v4)
python3 outils/durees.py lbN.mp4 lbN_bande.png 0.1
```

Les titres incrustés (« Last Breath v1 » …) ont été lus sur des images
isolées pour attribuer chaque passage à sa version.

## 1. Last Breath v1 (24 s, la version la plus longue)

| t (s) | ce qu'on voit | durée |
|---|---|---|
| 0-2,5 | ouverture : éclatements radiaux plein écran orange / blanc / noir, silhouette noire au centre | 2,5 s |
| 2,5-5 | plein écran noir et rouge, éclairs orange ; horizon rouge avec rayons de lumière (4-5) | 2,5 s |
| 5,2-5,4 | flash blanc-jaune | 0,2 s |
| 5,5-6,2 | vol dans le ciel bleu, traînées orange | 0,7 s |
| 6,3-6,6 | une boule tombe et devient un soleil orange rayé de noir | 0,3 s |
| 6,7-7,9 | explosion de feu au sol, plan large | 1,2 s |
| 8-10,2 | plan large calme, le perso debout (respiration) | 2,2 s |
| 10,3 | anneau blanc (le déclencheur) | 1 image |
| 10,5-13,4 | **le dragon violet tourne autour du perso au sol** (corps, fumée violette) | **~3 s** |
| 13,5 | éclat violet | 0,1 s |
| 13,6-14,3 | coupe : portrait de l'attaquant en contre-plongée | 0,7 s |
| 14,4 | la caméra lève les yeux vers le ciel | 0,1 s |
| 14,5-15,4 | le dragon s'enroule dans le ciel autour de la victime en l'air | ~1 s |
| 15,4 | cercle sombre | 1 image |
| 15,5-16,4 | flash blanc, éclatement orange, lignes radiales, étoile jaune | 0,9 s |
| 16,5-16,9 | plein jaune puis pâle | 0,4 s |
| **17,0-17,5** | **cartes MANGA à l'encre : éclaboussure brun-noir et la GUEULE du dragon avec ses dents, dessinée à l'encre** | **0,5 s** |
| 17,6-17,7 | cartes inversées, fissurées | 0,2 s |
| 17,8-18,2 | silhouettes de blocs R6 sombres dans le feu orange | 0,4 s |
| 18,3-20,2 | plein écran radial rouge-orange, puis horizon rouge à rayons | **~2 s** |
| 20,3-20,4 | soleil orange avec une silhouette noire devant | 0,1 s |
| 20,5 | blanc | 1 image |
| 20,6-23,3 | explosion, puis **traînée de feu qui brûle le terrain**, fumée, plan large | **~2,7 s** |
| 23,4-24 | après-coup : la victime au sol | 0,6 s |

Lecture : v1 est une suite d'**abstractions plein écran** (radial, rouge,
soleil, manga) entrecoupées de plans réels courts. Le dragon lui-même
n'est jamais montré longtemps en entier : il tourne (3 s), s'enroule dans
le ciel (1 s) ; **le moment où il mange est raconté par une carte manga
de la gueule (0,5 s)**, pas par un plan 3D de la morsure.

## 2. Last Breath v2 (plus réel, le dragon en 3D)

| t (s) | ce qu'on voit | durée |
|---|---|---|
| 1,1-2,0 | gros plan : le dragon violet (aplat, écailles dessinées en trait sombre, reflet blanc) s'enroule au ras du perso | 1 s (montré 2 fois) |
| 5,0-5,9 | plan large au sol : l'attaquant envoie la victime en l'air | 0,9 s |
| 6,0-6,9 | plan moyen, la victime monte | 0,9 s |
| 7,0-7,8 | **très gros plan du visage de l'attaquant, poussée caméra, œil violet** | 0,8 s |
| 7,9-8,5 | contre-plongée : l'attaquant regarde la victime dans le ciel | 0,6 s |
| 8,6-9,1 | **le corps du dragon (écailles violettes, trait noir) balaie tout le cadre en montant** | 0,5 s |
| 9,2-10,2 | ciel, **disque de soleil blanc** à gauche ; la queue du dragon s'enroule autour de la victime | 1 s |
| **10,3-10,6** | **la TÊTE du dragon, gueule grande ouverte (dents, yeux), traverse vers la caméra et avale la victime** | **0,4 s** |
| 10,7-11,1 | le soleil, le dragon s'éloigne, petit | 0,4 s |
| 11,2-12,9 | gros plan de la victime ; le corps du dragon (écailles, œil jaune) passe derrière et l'engloutit | 1,7 s |

Lecture : la morsure en 3D dure **0,4 s** et se fait **de profil / en
traversée vers la caméra**, sur fond de ciel avec un soleil blanc ; elle
est préparée par 0,8 s de gros plan du regard et 0,5 s de corps qui
envahit le cadre. Après la morsure, 1,7 s de corps qui défile derrière la
victime (le dragon est si long qu'il passe encore).

## 3. Last Breath v3 (le retour au sol)

| t (s) | ce qu'on voit | durée |
|---|---|---|
| 0,7-2,8 | ciel : la victime, minuscule, retombe en tournant | 2,1 s |
| 2,9-3,4 | elle tombe vers la caméra | 0,5 s |
| 3,5-4,6 | elle s'écrase au sol ; derrière, le corps du dragon file au ras du sol comme un train | 1,1 s |
| 4,7-8,1 | plan large vide : le corps du dragon n'est plus qu'une traînée violette à l'horizon | 3,4 s |

Puis « Last Breath v4 » (rig lettré F/B/L/R, blocage d'animation de la
victime : chute, rebonds, tentative de se relever).

Lecture : la **conséquence** est longue et lente (2 s de chute, 3,4 s de
plan vide avec le dragon qui s'en va) ; la victime ne disparaît pas, elle
est relâchée et s'écrase.

## 4. Poing du Dragon (Goku, GIF d514ee70, 3 s)

| t (s) | ce qu'on voit |
|---|---|
| 0-0,5 | poing levé vers nous, fond de lignes de vitesse radiales jaune/bleu ; anneau de choc à 0,2 |
| 0,6-0,7 | blanc plein écran |
| 0,8-1,0 | explosion rouge-orange |
| 1,0-2,1 | **tourbillon de feu plein écran** : cœur blanc, bandes orange, bandes rouge sombre ; il tourne |
| 2,2-2,5 | le corps du dragon d'or (anneaux d'écailles, trait brun sombre, épines) entre en spirale dans le tourbillon |
| 2,6 | la tête, gueule ouverte, rugit en gros plan |
| 2,7-2,9 | la tête passe tout contre la caméra (crocs, moustaches), puis le corps traverse |

Et l'invocation (GIF 656d965b, 2 s) : Goku debout sur un rocher, **poing
tendu droit vers le ciel, TENU 2 s**, contre-plongée 3/4, ciel de nuages,
rayons de lumière ; seuls les cheveux et l'aura vivent. Le plan ne bouge
presque pas.

**Dessin du dragon d'or (d514ee70, affiche DBZ 13, Dragon Ball Rage)** :
jaune-or en aplat, ombre orange franche (pas de dégradé), **trait brun
sombre** épais tout autour et sur chaque anneau du ventre, épines dorsales
sombres, moustaches blanches, crocs blancs, intérieur de gueule rouge ;
dans la version Roblox (Dragon Ball Rage) les yeux sont CYAN lumineux.

## 5. Ce qui entre dans le cerveau (apprentissages, pas règles)

1. **La morsure se raconte en deux fois** : un plan 3D très court (0,4 s,
   tête qui traverse vers la caméra) ET une carte manga à l'encre de la
   gueule (0,5 s). Aucune des deux ne tient longtemps ; ce qui dure, c'est
   l'avant (regard, corps qui envahit) et l'après (plein écran de feu,
   conséquence).
2. **Le dragon est plus long que le cadre** : on ne le voit presque
   jamais en entier. Il envahit (corps qui balaie tout le cadre 0,5 s),
   s'enroule, passe derrière. C'est la taille qui fait « abusé ».
3. **Le soleil blanc dans le ciel** (v2) et le **soleil orange à
   silhouette noire** (v1) : un disque simple, très lisible, donne
   l'échelle et la direction.
4. **Tempo d'ultime mesuré** (v1) : tourner 3 s → portrait 0,7 s → ciel
   1 s → flashs 1,3 s → manga 0,5 s → rouge 2 s → soleil → conséquence
   2,7 s. En tout ~13 s après le déclencheur. v2 : ~6 s du lancer à la
   fin de l'engloutissement.
5. **Goku** : l'invocation est un plan TENU presque fixe (2 s) ; le coup
   est une abstraction (radial → blanc → explosion → tourbillon plein
   écran ~1 s) d'où SORT le dragon, tête vers la caméra. Le dragon naît
   du coup.

## 6. Inventaire honnête : ce qui a été vu, et comment

| ref | comment | quand |
|---|---|---|
| Last Breath v1-v3 (4e0sX6p8-30, 118-160 s) | bandes 0,1 s, chaque vignette regardée | 2026-09-25 (ce fichier) |
| reste de 4e0sX6p8-30 (5 min) | 1 image/s + planche + courbes | `tutos/ETUDE_ARCHIVE_VIDEOS_1_2026-09-25.md` |
| Serious Punch Pew (lvB-wTylH3Y), Stoic Bomb, Slap, Sunrise, Thunder Dragon, Black Flash Gojo | 1 image/s + durées d'effet mesurées | idem, `clips/durees_effets_archive1_2026-09-25.json` |
| GIF Poing du Dragon (d514ee70), invocation (656d965b) | bandes 0,1 s, chaque vignette | 2026-09-25 (ce fichier) |
| GIF Serious Punch TSB (48244687) | image par image (étude visuelle) + durées | `ETUDE_NOTES_BRUTES.md`, `clips/durees_effets_2026-09-25.json` |
| 5 images Suiryu, 5 images « dragons 2e envoi », 5 images effets stylisés | regardées une à une + mesures de couleur | `RELECTURE_REFS_SUIRYU_2026-09-25.md`, `RELECTURE_REFS_VFX_STYLE_2026-09-25.md` |
| tutos texte (10 transcriptions) | lus en entier | `tutos/ETUDE_ARCHIVE_VIDEOS_1_2026-09-25.md` §2 |
| tuto flipbooks (TdU0A8etl1o, 12 min) | 1 image / 5 s + transcription | idem §3 bis |

Pas vus du tout (pas reçus) : les vidéos des tutos sans parole (Energy
Beam HJoVSZfK2Dw, VFX Part 1 ITd1yAZs1As, TSB scrapped hRzXUe6okOU).
