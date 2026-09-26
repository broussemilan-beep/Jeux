# M1 + réaction — premier clip de jeu du cerveau (2026-09-24)

Étape 3 de `experiments/_shared/animator_brain/PLAN.md`.

- **Contenu** : un M1 (direct du droit) et la réaction de la victime. Les
  deux rigs **R6 IK + FK V2.22** sont dans la même scène, animés à 60 fps.
- **Livraison** : deux KeyframeSequence Roblox.
- **Jugement** : par la **plage pro de leur catégorie**
  (`audit.calibrated_verdict`, corpus `battleground_animation_pack_v1.0.1`),
  et plus par nos anciens seuils fixes.

Ce n'est plus une cinématique : le clip dure **0,65 s** (durée médiane d'un
M1 pro) et la réaction **0,22 s**.

## Livrables (`output/`)

| fichier | contenu |
|---|---|
| `m1_attaquant.rbxmx` | KeyframeSequence 0,65 s, priorité Action, **jambes à poids 0** (comme le pro : la marche ou l'idle les mène), marker `hit` à 0,283 s |
| `m1_victime_reaction.rbxmx` | KeyframeSequence 0,22 s, jambes à poids 0 ; à jouer sur le marker `hit` de l'attaquant |
| `m1_poses_cles.png` | 9 poses clés, de profil et en caméra de jeu, sol visible |
| `m1_camera_de_jeu.gif` | le clip complet en caméra de jeu (30 i/s) |
| `m1_chaine_pics_pro_vs_notre.png` | vitesse par partie : M1 pro contre le nôtre **relu depuis le `.rbxmx`** |
| `verification.json`, `scene.json` | tous les chiffres ci-dessous |

**En jeu** : placer la victime à `CFrame_attaquant * CFrame.new(0, 0, -3.899) *
CFrame.Angles(0, math.pi, 0)` (3,899 studs devant, face à l'attaquant),
jouer `M1_Attaquant`, puis `M1_Victime_Reaction` sur
`GetMarkerReachedSignal("hit")`. Le hitstop, les VFX et les secousses de
caméra relèvent du script de jeu (étape 4 du plan).

Reconstruire : `python3 scripts/verify_export.py <Blender_R6.blend>`, puis
`scripts/render_review.py` et `scripts/motion_proof.py <pack.rbxm>`.

## Comment il est construit (`scripts/m1_clip.py`)

Principes lus dans le corpus et vérifiés sur les poses pro
(`corpus/README.md`), sans copier les courbes :

- **Le torse balaie un grand arc en lacet** : −98° à l'armement, +52° en fin
  d'arc. Il se penche progressivement vers l'avant, avec un léger avancé du
  bassin.
- **Le regard reste verrouillé sur la cible**, via la fonction *Track Object*
  du rig (tête qui suit `LookToPoint` sur la poitrine de la victime). Le
  pro fait pareil : sa tête compense la rotation du torse, ±12° en lacet
  monde.
- **Armement qui claque en 3 frames**, puis tenu jusqu'à f10.
- **Pendant la frappe, la main mène** : le bras culmine avant le torse, comme
  le pro. Le bras gauche vise la cible pendant l'armement, puis **tire en
  arrière** pendant la frappe.
- **Contact résolu par calcul** :
  - la portée du poing est mesurée à la pose d'impact ;
  - la victime est placée pour que le poing touche **exactement** la surface
    avant de son torse ;
  - chaque cible de main est résolue par `v222_rig.solve_control_for_tip`
    (Gauss-Newton sur le contrôle IK).
- **Victime** :
  - torse en mode FK, qui pivote sur **son propre centre** (une réaction pro
    ne déplace pas le torse) ;
  - **la tête mène** : extrême à +2 frames, torse à +3 ;
  - aller en ligne droite, retour qui ralentit, sans tenue.

## Vérifications (le fichier livré, pas l'aperçu)

| contrôle | résultat |
|---|---|
| contact à l'impact (f17) | poing sur la surface du torse : **0,0000 stud** |
| pénétration après l'impact | 0,035 stud max (tolérance 0,05), aucune frame en pénétration |
| tête attachée (translation du Neck) | **0** (les pros : 0 partout) |
| aller-retour par l'équation du moteur | 4e-15 stud |
| verdict calibré de l'attaquant (`frappe_legere`) | **32/38 mesures dans la plage pro** |
| verdict calibré de la victime (`reaction`) | **29/38** |
| phases de l'attaquant (f60) | armement 9, coup 12, tenue 18 : les trois dans la plage pro |

Comparaison avec nos coups précédents (même mesure, `corpus/README.md`) :

| mesure | M1 pro, médiane | `r6_directional_punch` | **ce M1** |
|---|---|---|---|
| amplitude tête | 84° | 25° | **99°** |
| amplitude torse | 91° | 54° | **98°** |
| amplitude bras droit | 150° | 99° | **113°** |
| vitesse max de la main | 68 studs/s | 52 | **71** |
| mesures dans la plage pro | — | 11/35 | **32/38** |

## Ce que la construction a appris au cerveau

Chaque point est corrigé et consigné dans le code concerné.

1. **Clé écrasée** : poser, rafraîchir, puis cler enregistrait l'ancienne
   valeur, car le rafraîchissement réévalue l'action.
   - Conséquence : clip statique.
   - **L'auto-test d'export passait quand même** : un clip immobile réussit
     trivialement l'aller-retour.
   - Corrigé dans `v222_rig.key_controls`. L'auto-test vérifie maintenant que
     le clip bouge et passe par les valeurs clées.
2. **« Torso Influence = 0 » détache aussi l'épaule** : bras à 1,73 stud du
   torse. La visée en repère monde passe par le solveur, pas par ce réglage.
3. **Les pros décalent les membres** : jusqu'à 1,7 stud pour les bras d'un
   M1, 1,8 pour les jambes d'un downslam ; la tête jamais. C'est le faux
   coude du rig IK. Mesure ajoutée au corpus. L'ancienne règle « rotation
   pure » ne vaut pas pour ce style.
4. **Un chiffre bon peut donner une pose illisible.** En v4, j'ai monté le
   bras gauche au-dessus de la tête pour faire passer une mesure d'amplitude.
   La revue visuelle l'a montré ; en v5, le bras vise la cible, comme le pro.
   Le verdict calibré guide, **la revue de pose tranche**.
5. **Détecter le coup** par la main qui va le plus loin devant le torse. Le
   bras de visée part lui aussi vers l'avant pendant l'armement et trompait la
   segmentation.

## Écarts restants, dits franchement

- **Attaquant** :
  - bras gauche moins ample que le pro (85° contre 124-196°) ;
  - un peu trop de « poses clés par seconde » (4,6 contre 2,6-3,4) ;
  - le bras culmine à 0,033 s, un poil plus tôt que la plage (0,042-0,225).
- **Victime** :
  - pic d'énergie un peu haut ;
  - 29 % du temps quasi immobile contre 0-7 % chez le pro ;
  - certaines plages pro sont extrêmement étroites (3 réactions presque
    identiques du même auteur, translation des bras 0,033-0,041) : ces écarts
    parlent plus du corpus que de l'animation.
- **Jambes** : dans l'aperçu, elles suivent le torse et penchent avec lui en
  milieu de rotation. C'est exactement ce que le jeu affichera avec des
  jambes à poids 0 sur un idle. Au-dessus d'une marche, l'effet sera
  différent.
- **Cibles de main en fin de clip** (f33, f39) : hors d'atteinte
  (résidu ~1,7 stud). Le bras pointe vers la cible sans l'atteindre, voulu
  pour le poing ramené au corps.
- **Pas encore de VFX, de hitstop ni de caméra de jeu scriptée** : étape 4.
- **Pas vu dans Roblox Studio** (pas de Studio ici) ; l'aller-retour par
  l'équation du moteur est le garde-fou.


## Étape 4 : le package Roblox complet (2026-09-24)

**`output/M1_Technique.rbxmx`** : un seul fichier à glisser dans Studio
(Workspace), puis **Play**. Le coup se rejoue en boucle toutes les 2,2 s.

| instance | rôle |
|---|---|
| `Attaquant`, `Victime` | mannequins R6 générés depuis les C0/C1 du vrai rig ; l'attaquant regarde −Z, la victime est placée devant lui et tournée vers lui |
| `Animations` | les deux KeyframeSequence ; l'attaquant porte 3 marqueurs `trail_on` (0,167 s), `hit` (0,283 s), `trail_off` (0,350 s) |
| `M1Technique` (ModuleScript) | la technique, voir le détail sous le tableau |
| `Demo` (Script, RunContext Client) | boucle de démonstration ; tourne où qu'il soit dans Studio |

Ce que fait `M1Technique` :

- place la victime ;
- joue les animations (id temporaire de Studio via
  `KeyframeSequenceProvider`, ou l'attribut `AnimationId` de la
  KeyframeSequence si tu publies l'animation) ;
- **sur les marqueurs** : traînée du poing, puis à `hit` réaction de la
  victime, hitstop (0,07 s, les deux animations figées), flash, étincelles,
  onde de choc, recul et secousse de caméra ;
- tous les réglages sont dans `M1.CONFIG`.

Les effets n'utilisent que des textures intégrées au client Roblox
(`rbxasset://textures/particles/sparkles_main.dds`) : rien à publier. Sources
Luau lisibles dans `luau/`.

**Tout le timing vient des marqueurs de l'animation**, aucun délai n'est codé
en dur : si l'animation change, les effets suivent.

### Le sens, vérifié à trois niveaux

1. **Fichiers d'animation relus**, en repère Roblox (`verify_export.py`,
   section `sens_roblox`) :
   - l'attaquant regarde −Z ;
   - le poing est devant lui à l'impact, sur la **face avant** du torse de la
     victime ;
   - la victime est tournée vers lui ;
   - sa tête est projetée **vers son dos** ;
   - à l'armement, le bras droit est **derrière**.

   Le script s'arrête si un seul de ces points est faux.
2. **Code Luau du module, exécuté** par l'interpréteur Luau officiel
   (`luau/run_sens_test.py`, avec des CFrame aux conventions Roblox, 11
   contrôles) :
   - victime devant et face à l'attaquant, même quand il est tourné ;
   - repère d'impact et étincelles dans le sens du coup ;
   - anneau perpendiculaire au coup ;
   - recul qui **éloigne** la victime (3,899 puis 4,799 studs) sans la faire
     tourner.
3. **Package écrit, relu** (`build_roblox_package.py`) :
   - références uniques et résolues ;
   - pose de repos exactement cohérente avec les Motor6D (écart 0) ;
   - visages sur la face avant (−Z) ;
   - victime devant et face à l'attaquant ;
   - 3 marqueurs ;
   - démo en contexte client.

Les deux sources Luau **compilent** avec `luau-compile` officiel.

### Aperçu

`output/m1_technique_apercu.gif` : caméra de jeu, avec hitstop, effets, recul
et secousse, **mêmes paramètres** que `M1.CONFIG` (lus dans le source Luau).
C'est une **approximation** des particules Roblox (Cycles, formes
simplifiées) ; positions, directions et timings sont calculés comme dans le
module. `output/m1_technique_impact.png` en montre 6 instants.

### Limites

- **Pas testé dans Roblox Studio lui-même** (pas de Studio ici). Le module est
  vérifié par compilation, exécution de sa géométrie et relecture du
  package, pas par une vraie partie.
- `RegisterKeyframeSequence` donne un id **temporaire, valable dans Studio**.
  Pour un vrai jeu, publie les deux animations et mets leur id dans
  l'attribut `AnimationId` de chaque KeyframeSequence.
- Les animations se jouent côté client dans la démo : pour une vraie
  compétence en multijoueur, il faudra le relais serveur habituel
  (RemoteEvent) ; la logique du module reste la même.

## Vérification (captures)

- `captures/verification/2026-09-24-m1-v222-poses-cles.png` : 9 poses clés,
  de profil et en caméra de jeu.
- `captures/verification/2026-09-24-m1-v222-technique-impact.png` : 6 instants
  de la technique complète (traînée, impact, étincelles et anneau dans le sens
  du coup, recul de la victime).
- `captures/verification/2026-09-24-m1-v222-chaine-pics-pro-vs-notre.png` :
  même profil de vitesse que le M1 pro (armement vers f3, quasi-arrêt vers
  f10, coup vers f14-16, le bras avant le torse), mesuré sur le fichier livré.
