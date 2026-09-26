# Synthèse de l'étude complète des tutos (2026-09-25)

Refaite après le retour de Milan (« je vois aucun changement » sur la v7 ;
« as-tu tout lu, ou cherché à combler nos trous ? »). Cette fois : les 4
vidéos longues regardées EN ENTIER par moi à 1 image/s (≈ 3 440 images), tous
les textes relus, chaque démonstration jouée revue image par image, sans
hypothèse à confirmer. Notes détaillées : `etude_complete_*.md`.

## Ce qui est mieux que nous, et pourquoi (par ordre d'importance estimée)

| # | ce qu'ils font | ce que nous faisons | sources |
|---|---|---|---|
| 1 | **Le corps d'abord.** Tout le mouvement est posé et jugé sur le TORSE seul, puis bras, tête, jambes | notre code part de la cible du poing (IK) et place le corps après : le corps n'a pas sa propre courbe | uppercut (256-301 s) |
| 2 | **Placement / cadrage** : le perso remplit le cadre, caméra basse et inclinée pendant les temps forts | plans moyens/larges : en caméra de jeu et après le coup, le perso fait ~1/4 du cadre | extraits pros, LEVEL 1→99 |
| 3 | **La pose d'APRÈS** le coup est la plus extrême (corps plié, très bas) et tenue 0,4-1 s ; l'extension ne dure qu'1 image | notre extension est tenue 0,43 s (hitstop + cartes) et la pose d'après 0,13 s | punch (1000 s), uppercut, Xoaterz |
| 4 | **Rôles de clés** (anticipation, drag, milieu, exagération qui DÉPASSE, amorti) jugés en rejouant, « exagère ce qui est fade » | clés de position calculées une fois | uppercut |
| 5 | **Obari / Saitama** : armé tenu 1-2 s, fond uni radial, puis poing VERS l'objectif (40-60 % du cadre), coupe sur plan large | notre coup chargé aérien est filmé de côté | techniques anime (714-745 s), images de Milan |
| 6 | **Hold-and-release partout** (charge, débris suspendus puis lâchés) | nos débris suivent une physique | techniques anime (yutapon) |
| 7 | **Images d'impact variées** (silhouettes, encre, aberration RGB, rouge/blanc, flou) | une séquence noir/étoile/cartes/blanc | Xoaterz, Thundey, techniques anime |
| 8 | **Garde sobre, temps forts extrêmes** (planche ✓ : idle droite et détendue) | exagération répartie | Xoaterz |
| 9 | **Retouche sans fin** d'une même pose sous tous les angles (10 min sur 16 dans le tuto punch) | pose calculée, jugée sur une planche 3 vues | punch |

## Ce qui CONTREDIT ce qu'on croyait

- **La croix n'est pas mauvaise en soi** : l'armé de l'obari punch de Sakura
  est une croix de face, et c'est très fort parce que tout le reste (tenue,
  fond radial, caméra qui avance, poing vers l'objectif) la porte. La
  planche de Xoaterz vise une pose posée seule. `silhouette_non_croix`
  rétrogradée (0,7 → 0,4).
- **L'accroupi** : rejeté pendant une charge (Milan v1-v2, Xoaterz « perma
  crouched »), mais la pose d'ARRIVÉE d'un coup est très basse et large chez
  les deux animateurs des tutos. Ce n'est pas la même chose.

## Ce que ça veut dire pour « je vois aucun changement »

La v7 a changé deux poses (charge, contact) de quelques dizaines de degrés,
sur ~0,5 s, dans un cadrage où le perso est petit, sans toucher à la pose
d'après, au cadrage ni à la méthode (corps d'abord). Les tutos montrent que
la différence visible vient de ces trois-là.

## Limites

Vidéos sans le son (les explications orales manquent : surtout Xoaterz qui
repose en direct). Angles estimés à l'œil sur du 640x360. Un tuto par
animateur. Aucune source n'est TSB. Rien de ceci n'est certifié tant que ce
n'est pas vu à l'écran puis jugé par Milan.

## Couverture réelle (vérifiée le 2026-09-25, contenu des zips)

Sur les 19 vidéos demandées, les zips en contenaient **4** (xkHILCmgbig,
0vjAiAR-YFk, C09ZMD9_D9I, iMV9Tlpo1wY), plus 2 choisies par Milan
(LWMujy7LSC0, olr5q-iIlKI). **Aucun sous-titre ni description** n'était dans
les zips : toute l'étude est visuelle. **Manquent 15 vidéos** :
- Roblox (10) : uoXd04yPN8s, KneO6y3FebM, AH30avEEC9A, ILaV0JYHzwY,
  2FwaIG87LYo, Cu7Xl-cZVBU, bzS9B3-iVH0, 5_Zr4yYSLks, l_bE_-wcVBg,
  5u2GSOwjOlM (texte seul) ;
- général (5) : kZsboyfs-L4, g64E-UNRqcg, -HXx1fK415I, 234m7y8D3cE,
  yhGjCzxJV3E (talk GGXrd).
YouTube reste bloqué depuis ce sandbox (« Sign in to confirm you're not a
bot »). Cette synthèse ne vaut donc que pour 6 vidéos sur 21.

**Mise à jour 2026-09-25 (soir).** Les 15 manquantes ont été lues par
Gemini, **sur transcription seulement**. Milan a collé le texte :
`gemini_transcriptions_2026-09-25.md`, avec ma lecture critique et les
mesures contre TSB. Trois transcriptions sont vides (DAS, Charlotte,
Nate.Animations). Couverture : parole de 18 vidéos + image de 6. L'image
des 15 reste à voir.
