# Reproduire pour comprendre (2026-09-25)

Demande de Milan : « améliore le cerveau et le jugement dans l'absorption, la
compréhension et la reproduction : savoir refaire comme dans la vidéo, puis
autrement, et faire plus (le coup chargé de Saitama) ».

## L'outil : `outils/moon.py`

Un mini Moon Animator R6 : FK (chaque membre tourne autour de son pivot
dans les axes du torse, les membres suivent le torse), translation des membres
(bras « disloqué »), pieds plantés par translation de la jambe, wiggle, clés
interpolées exactement comme Roblox en Linear (`roblox_export.solve`), rendu
perspective avec fond remplacé. C'est la manière de travailler des tutos,
à l'inverse de notre pipeline IK (qui part de la cible du poing).

## Ce que j'ai reproduit, et ce que la reproduction m'a appris

| essai | passes | verdict à l'écran | preuve |
|---|---|---|---|
| uppercut Moon (`uppercut_moon.py`) | 4 | passe 1 : torse de face, poses 2x trop sages ; passe 4 : même lecture que la vidéo (départ de profil ramassé → bras vertical, corps ouvert vers la caméra, fente basse), mais corps encore plus haut et moins large que l'original | `captures/verification/2026-09-25-repro-uppercut-*.png` |
| punch Blender (`punch_blender.py`) | 2 | timeline exacte (0/20/30/60/61/62/63/66/90) ; la charge en K et la pose d'après pliée se lisent ; pose d'après encore moins couchée que l'original | `2026-09-25-repro-punch-blender-vs-video.png` |
| coup chargé Saitama/obari (`saitama_obari.py`) | 3 | poing à 0,86 stud de l'objectif, ~55 % du cadre ; la charge était un tas illisible tant que je la jugeais depuis le point de vue du coup (passe 2) ; lisible une fois jugée depuis SA caméra | `2026-09-25-essai-saitama-*.png`, `repro/saitama_obari_essai.mp4` |

**Leçons de la reproduction (ce que je ne savais pas en regardant seulement) :**
1. **Mes premiers réglages sont systématiquement ~2x trop sages.** Pour
   ressembler à la vidéo il a fallu doubler l'enroulement (55° → 95°), baisser
   le corps de 0,3-0,5 stud, écarter les pieds de 1,2 à 2,5 studs. L'œil
   « trouve assez » une pose que la vidéo dépasse de loin.
2. **Une pose n'existe que depuis sa caméra.** La même pose est un K lisible
   de côté et un tas de blocs d'en dessous. Les animateurs tournent autour
   (tuto punch) ; l'obari coupe entre deux caméras : la charge de 3/4, le
   poing depuis la victime. Il faut concevoir chaque pose POUR un plan.
3. **Corps d'abord, ça marche** : la passe « torse seul » de l'uppercut se
   lit déjà comme un coup ; les bras ajoutés après ne font que préciser.
4. **La perspective suffit à faire un poing géant en R6** : aucune mise à
   l'échelle ; corps qui plonge (0,7-1,05 stud) + bras déboîté (1 stud) +
   caméra à 1 stud + grand angle 85°.
5. **Un membre pointé vers l'objectif cache tout** (le genou de la charge,
   passe 2) : dans un plan, les membres doivent partir sur les CÔTÉS du
   cadre, pas vers la caméra, sauf celui qui porte le coup.

Limites : rendu à blocs sans texture ; comparaisons à l'œil ; vues de la
vidéo en 640x360 ; l'essai Saitama n'est pas encore dans la technique (ni
victime animée, ni effets, ni rig V2.22).
