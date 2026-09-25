# Fiche de conception : l'aura DRAGON du Poing du Dragon (Goku x Izuku)

**Demande de Milan (2026-09-25)** : « l'aura du poing du dragon en forme de
dragon, je t'enverrai la ref », puis, avec 4 refs du Poing du Dragon de Goku
SSJ3 (film DBZ 13) : « mélange ça à Izuku pour le poing du dragon ».
Apprentissages, pas règles. À lire avant de poser la moindre clé d'effet.

**Sources digérées.**
- e92ac0d7 (affiche) : le dragon doré dresse la gueule AU-DESSUS du poing
  levé ; le corps passe derrière le perso.
- 6a961186 (illustration) : le dragon S'ENROULE derrière et autour du perso
  en spirale descendante, tête au-dessus du poing ; flammes orange, fond
  jaune-orange, ÉCLAIRS blancs ; traînée d'encre noire sous le perso.
- f254bee5 (GIF 2 s, 20 i/s) : poing levé vers le ciel, TENU 2 s immobile,
  rayons de lumière à travers les nuages : l'invocation est une tenue.
- 7a2b4ae8 (GIF 3 s, 10 i/s), lu image par image :
  1. poing vers l'objectif sur un ÉCLATEMENT RADIAL (jaune, bleu-vert,
     noir) ; une coquille d'aura blanche s'étend, le perso rapetisse ;
  2. 2 images de BLANC ;
  3. explosion de feu cel orange et blanc, traits noirs ;
  4. TOURBILLON de feu en spirale qui remplit l'écran (~1 s) ;
  5. le DRAGON SORT DU TOURBILLON : corps de serpent doré qui balaie le
     cadre (nageoires dorsales brunes en dents de scie, écailles en
     écusson), puis la tête : gueule ouverte, crocs, longues moustaches,
     crinière brune en flammes ; fin sur les crocs en très gros plan.
- Izuku (Deku) : 0ca551a4 (poing vers le lecteur, déjà au catalogue) +
  ce qu'on sait de One For All : ÉCLAIRS VERTS qui crépitent sur tout le
  corps (Full Cowl), pression d'air du Smash.
- Nos contraintes : style cel, 2-3 couleurs + blanc (CARNET §4b.2), l'air
  vend la vitesse (§4b.3), rien de réaliste ; rig R6 ; tout jouable dans
  Roblox (moteur VFXStudio) ; pas de cape ni d'écharpe (mandat).

## 0. CORRECTION (retour de Milan sur la v11, VFX 4/10)

- « Mélange ça à Izuku » voulait dire : la POSE d'Izuku mélangée à celle de
  Goku (animation), PAS les éclairs d'Izuku sur le dragon. Les éclairs verts
  sont retirés ; la §1 ci-dessous est une mauvaise lecture, gardée pour
  mémoire.
- « Le dragon est moche, pas du tout du modèle premium » : les cartes
  peintes et le ruban de Beams se lisent comme des AUTOCOLLANTS. Premium =
  un vrai modèle en VOLUME (lumière, contour, silhouette qui tourne).
  Remplacé par le dragon 3D riggé de `vfx_studio/modeles/dragon.py`
  (Blender, FBX, MeshPart skinné dans Roblox, SkinnedMesh dans l'aperçu).
- La pose (v10 de l'aérien, `dragon_clip.py aerien_v10`) : INVOCATION de
  Goku (poing vers le ciel, tenu, le dragon s'enroule autour du bras et
  dresse la tête au-dessus du poing), puis PLONGÉE d'Izuku (poing tendu vers
  l'objectif, épaule en avant, tête basse derrière le poing, autre bras
  rentré, jambes ensemble derrière).

## 0 bis. Ce que la v12 a changé (vu à l'écran, pas seulement mesuré)

- **Invocation = l'affiche** : bras droit tendu vers le ciel en « V » au
  bord de la tête, poing gauche armé à la hanche, jambes qui traînent
  derrière, regard devant menton levé ; caméra 3/4 face, -6°, corps + poing
  + tête du dragon dans le cadre. Le dragon s'enroule DERRIÈRE le perso, le
  cou monte au-dessus du poing puis la tête se couche à l'horizontale, de
  profil, gueule ouverte. (Essais écartés, captures `2026-09-25-v10a-*`,
  `-v12-tour-invocation-avant`.)
- **Plongée = Izuku** (inchangée) ; caméra obari plus basse et sur le côté
  (le bras traversait l'objectif).
- **Dragon premium** : écailles lisibles (~0,5 stud, peintes en volume),
  dos orange profond, ventre crème en plaques, crinière et nageoires brunes
  (les refs) ; matériau mat ; FEU qui coule le long du corps
  (`recettes.flammes_corps`, émetteurs sur des chemins) + lueur ; bloom
  dans le lecteur (= BloomEffect du jeu).
- **Bug corrigé** : les images de forme du dragon étaient écrites relatives
  au début de la couche, le moteur les lit en temps de recette -> le dragon
  avait 10 images d'avance sur le corps.
- Reste faible (à dire à Milan) : la tête du modèle est lisse (pas
  d'écailles sur le crâne) ; l'éclatement radial + le tourbillon de feu
  PLEIN ÉCRAN du GIF 7a2b4ae8 ne sont pas faits (on a le tourbillon au
  sol) ; en jeu, le dragon attend l'import du FBX (sinon repli rubans).

## 1. Le mélange (mauvaise lecture, v11)

- **Le dragon est de Goku** : doré, serpent long, tête de profil, crinière
  de flammes, nageoires dorsales foncées. C'est la SIGNATURE (celle qui
  manquait : `etat.signature_visuelle` faux depuis la v6).
- **Le courant est d'Izuku** : éclairs VERTS qui crépitent sur le corps et
  le long du dragon, pendant l'armé et la plongée. C'est ce qui dit « c'est
  la puissance de CE perso », pas une copie de Goku.
- **Palette** : or #ffc53d + or profond #ff8a1f + vert One For All
  #6dff8a + blanc. Contour brun foncé pour le dragon (cel).

## 2. Le dragon raconte trois temps (calqués sur nos actes v9)

1. **Armé (226-256)** : l'invocation. Le dragon SORT DU POING et s'enroule
   en spirale autour du bras puis derrière le corps (6a961186), tête
   au-dessus du poing, gueule vers la victime. Éclairs verts sur le corps.
   Tenue : le dragon ondule, il ne se fige pas (tenue vivante).
2. **Plongée (256-278)** : le dragon PART AVEC le poing : tête devant le
   poing, corps en traînée derrière, sur le trajet réel du poing. Les
   éclairs verts suivent le bras.
3. **Impact (288 ->)** : le TOURBILLON de feu au point d'impact, puis le
   dragon qui en SORT et monte en spirale vers le ciel, et se dissout
   pendant la révélation (la conséquence reste à l'écran, comme la fumée du
   Serious Punch).

## 3. Comment le faire dans Roblox (et donc dans l'aperçu)

- **Corps** = chaîne de Beams entre Attachments placés sur une courbe,
  texture d'écailles qui DÉFILE (Beam.TextureSpeed natif) : le dragon
  « coule » le long de son corps. Largeur par segment : large au cou, fine
  à la queue. Pas de mesh sculpté : impossible à produire proprement ici,
  et un ruban cel se lit mieux à distance.
- **Forme animée** = la courbe est CALCULÉE hors ligne (staging, à partir
  des pistes réelles du bras et du poing), échantillonnée à 30 Hz, et le
  moteur interpole : aucune simulation en jeu.
- **Tête** = une carte plate peinte (profil cel), qui contient l'axe du cou
  et se tourne vers la caméra ; vue de l'autre côté, elle est simplement en
  miroir (un profil reste un profil).
- **Éclairs** = segments brisés re-tirés toutes les 1/20 s (même graine =
  déterministe), en Beams ; comme LightningBolt, mais sans créer / détruire
  de Parts à chaque tirage.
- Coût : ~24 Beams pour le corps + 1 carte + ~12 Beams d'éclairs. À
  vérifier par critique.py.

## 4. Pièges connus

- Le ruban FaceCamera vu dans son axe devient un trait : la plongée est
  filmée depuis la victime (obari), dans l'axe ! -> le corps doit onduler
  latéralement pour garder une largeur à l'écran.
- La tête plein cadre en caméra obari cacherait le poing (piège du v9 : les
  anneaux dorés encombraient le poing) -> la tête passe À CÔTÉ du poing,
  pas devant.
- Un dragon qui apparaît d'un coup = un sticker. Il doit NAÎTRE (croissance
  de la tête vers la queue) et MOURIR (dissolution de la queue vers la
  tête).
