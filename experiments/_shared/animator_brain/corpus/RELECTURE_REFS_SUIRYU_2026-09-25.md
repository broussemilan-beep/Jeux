# Relecture : le dragon « Dragon's Descent » de Suiryu (TSB), 5 images

Envoyées par Milan le 2026-09-25, juste après sa note de la v12 (VFX 2 à
4/10 : « le dragon apparaît 0,5 s et pas au bon endroit »). Images fixes :
ce qui touche au TIMING reste à confirmer sur la vidéo. Deux volets, comme
demandé : VFX et animation / mise en scène. Fichiers : `CATALOGUE_REFS.md`
(section Suiryu). Les images ne sont pas versionnées.

## Mesures (pixels, `sha1` au catalogue)

| image | part de l'image en violet | boîte (x0, y0, x1, y1) | remarque |
|---|---|---|---|
| 930606b5 (jeu, téléphone) | 13 % (~20 % de la zone de jeu) | 0,15-0,99 × 0,34-0,70 | bandes noires de l'enregistrement |
| d598c391 (3/4, près) | 32 % | 0,00-0,98 × 0,21-0,76 | |
| 996d38b7 (face, près) | 38 % | 0,00-1,00 × 0,07-0,78 | yeux incandescents 0,7 % de l'image |
| feb2d674 (gueule ouverte) | 27 % | 0,05-0,95 × 0,15-0,88 | + fumée grise, croissants blancs |
| 68f0ad1a (caméra de jeu paysage) | 16 % | 0,27-0,79 × 0,16-0,80 | **64 % de la hauteur d'écran** |

Violet médian ≈ RGB (140, 100, 235) (#8C64EB) ; ombre de trait violet
sombre ; accents : blanc (dents) et jaune-orange (yeux).

## Volet VFX : ce que c'est

1. **Une TÊTE, pas un corps.** Pas de serpent, pas d'écailles : un volume
   simple en goutte (large en haut, pointe qui touche le sol), vu DE FACE.
   On le lit comme un masque, d'un seul coup d'œil.
2. **Matière d'énergie, pas de matière réelle.** Violet plat,
   semi-transparent, presque sans ombrage (non éclairé) ; intérieur un peu
   plus clair, bord plus sombre. Le contour est flou : des bouffées de
   fumée violette débordent la silhouette. C'est un esprit, pas une statue.
3. **Le dessin est PEINT sur le volume.** Sourcils, cornes en volutes,
   pommettes, naseaux : des traits violet sombre, style cel, posés sur la
   surface (une texture de trait sur un mesh simple). Le détail est dans le
   TRAIT, pas dans la géométrie.
4. **Deux accents qui portent tout :**
   - les YEUX jaune-orange incandescents, avec lueur (bloom) : la seule
     couleur chaude, le point focal ;
   - le SOURIRE blanc aux dents pointues, très large : le contraste
     maximal. Il a une EXPRESSION (un sourire mauvais) : c'est un personnage.
5. **Moustaches** : traits sombres fins qui partent à l'horizontale et
   finissent en SPIRALE. Elles élargissent la silhouette.
6. **Un vrai objet dans le monde** : il projette une ombre au sol (Part /
   MeshPart, pas seulement des particules).
7. **La gueule qui s'ouvre** (feb2d674) : mâchoires en hauteur, intérieur
   violet sombre, anneau de dents blanches ; autour : croissants de vent
   blancs (arcs), fumée grise cel en nuages, éclats violets à la base.
   Probablement le moment où il avale / écrase la cible (« Descent »).
8. **Palette** : violet, violet sombre, blanc, et UNE couleur d'accent
   complémentaire (jaune-orange des yeux). 3 couleurs + accent : la règle
   cel du CARNET §4b.2, appliquée.

## Volet animation / mise en scène

1. **Il EST le coup, à la place du joueur.** Au sol, là où est le perso
   (on ne voit plus le perso) ; il fait face à la caméra et à la cible.
   Rien à voir avec notre dragon qui tourne autour du perso, en décor.
2. **Échelle** : en caméra de jeu, ~64 % de la hauteur de l'écran, plus
   haut qu'un bâtiment, deux à trois fois le perso. Notre dragon d'invocation
   v12 : une petite forme dorée au-dessus du perso.
3. **Face caméra, symétrique** : un visage de face se lit instantanément ;
   notre tête de profil devait être « lue ».
4. **Deux temps visibles** (à confirmer en vidéo) : la tête apparaît et
   SOURIT (tenue : on a le temps de lire l'expression), puis la GUEULE
   S'OUVRE et descend sur la cible (le nom : « Dragon's Descent »).
5. **La pointe au sol** : la tête SORT de la terre / du perso, comme une
   flamme ; elle a un point d'ancrage lisible.

## Ce que j'en tire (apprentissages, pas règles)

- **« Premium » chez TSB ≠ modèle réaliste.** Mon dragon v12 = serpent doré
  sculpté, écailles, profil : du détail géométrique qui ne se lit pas. Le
  dragon de TSB = une FORME simple + un TRAIT peint + une EXPRESSION + une
  lueur. Le premium est dans le DESIGN, pas dans les polygones.
- La signature se lit en UNE image : face, contraste maximal (dents
  blanches, yeux chauds sur violet), silhouette élargie (moustaches).
- C'est faisable avec notre studio : un mesh de tête simple (Blender), une
  texture de trait peinte, un matériau d'énergie (Roblox : MeshPart en
  ForceField ou Neon + transparence, texture ; aperçu : shader non
  éclairé), des particules de fumée au bord, des particules « lueur » sur
  les yeux, des Beams pour les moustaches ; la gueule qui s'ouvre = une
  mâchoire riggée (Bone) ou deux meshes.

## Questions pour Milan (avant de construire)

1. Notre Poing du Dragon garde-t-il le dragon DORÉ (Goku) dans ce STYLE-là
   (tête de face, énergie, trait peint, yeux qui brillent), ou passe-t-on
   au violet de Suiryu ?
2. Le dragon remplace-t-il le coup (il sort du poing / du sol et avale la
   cible, comme « Descent »), ou accompagne-t-il le perso ?
3. La vidéo de ce coup (pour le timing : durée du sourire, ouverture de la
   gueule, descente).
