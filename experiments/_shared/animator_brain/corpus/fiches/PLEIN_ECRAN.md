# Fiche de conception : le plein écran d'un ultime (planches)

**Rappel** : `python3 outils/rappel.py "plein écran planche dessinée encre
trait soleil silhouette tourbillon"`. Sources digérées ensemble :
- `../RELECTURE_LAST_BREATH_GOKU_2026-09-25.md` : Last Breath v1 (radial
  rouge-orange puis horizon rouge à rayons ~2 s, soleil orange avec une
  silhouette noire devant 0,1 s, soleil rayé de noir) ; Goku d514ee70
  (tourbillon de feu plein écran 1,1 s : cœur blanc, bandes orange, bandes
  rouge sombre, il tourne ; puis le corps du dragon entre en spirale) ;
- `../RELECTURE_REFS_VFX_STYLE_2026-09-25.md` : échelle de valeurs (cœur
  blanc -> saturé -> bord sombre, NOIR dans l'effet), silhouettes POINTUES
  (dents de scie, lames, langues), mouvement DESSINÉ (croissants, arcs,
  traits de vitesse), une forme signature par effet ;
- Slap TSB (6sXVqrZ_rYA) : planches manga plein écran 2,5 s ; Serious
  Punch (lvB-wTylH3Y) : carte inversée 2 images ;
- retour de Milan sur les planches v13 (2026-09-25, `../../RETOURS.md`) :
  « le tourbillon et le rouge : trop PEINTURE, pas dessiné » ; « le soleil :
  j'aime l'idée, bonne créativité, mais tu peux faire beaucoup mieux ».

## 1. Peinture contre dessin (ce qui a raté, mesuré sur nos planches)

| | v13 (« peinture ») | ce qu'il faut (« dessin ») |
|---|---|---|
| comment c'est fait | un champ de BRUIT lisse coupé en paliers de couleur | des FORMES tracées une à une : lames, langues, croissants |
| bords | ondulés, mous, au hasard (des taches) | tendus : courbes franches qui finissent en POINTE |
| trait | 22 lignes sombres posées par-dessus, sans lien avec les formes | chaque forme CERNÉE (trait d'encre qui s'amincit), hachures dans les ombres |
| lignes de vitesse | aucune (rouge : traînées au sol) | tracés effilés concentriques ou convergents, en paquets |
| image suivante (en 2) | même champ déphasé = ça « coule » | même dessin redessiné : le trait BOUT (tremble), les formes restent |

## 2. Les trois planches

1. **Tourbillon** (Goku 1,0-2,1 s, joué en 2, tourne) : fond rouge sombre ;
   6-8 LAMES de feu en spirale logarithmique (croissant effilé, pointe vers
   l'extérieur), empilées de l'extérieur sombre vers le cœur : rouge ->
   orange -> or -> blanc ; chaque lame cernée d'encre brune, hachures
   parallèles dans les lames sombres ; petites virgules de feu éjectées ;
   lignes de vitesse en spirale. 3 dessins qui « bouillent ».
2. **Rouge** (Last Breath v1 18,3 s, horizon rouge à rayons) : le dragon a
   plongé À L'HORIZON ; ciel rouge avec des lignes de vitesse noires qui
   CONVERGENT vers le point d'impact ; au point d'impact un dôme de langues
   de feu pointues (3 tons, cernées) ; sol noir avec des fissures en
   perspective. 2 dessins qui bouillent.
3. **Soleil** (Last Breath v1 20,3 s ; l'idée que Milan aime) : la
   silhouette est celle de NOTRE dragon (rendu du labo, masque), pas un
   ruban générique : crinière, cornes, moustaches, gueule. Soleil dessiné
   (disque blanc, anneau d'encre, couronne de rayons en triangles
   alternés), liseré de contre-jour orange à l'intérieur du bord de la
   silhouette (anime), lignes de vitesse, trame. Le dragon PLONGE (tête en
   bas) : c'est l'instant avant le cratère.

## 3. Pièges

- ne pas regénérer un champ de bruit « plus net » : c'est la méthode qui
  fait la peinture, pas le nombre de paliers ;
- garder le NOIR dans l'effet (refs VFX) sans tout salir : les ombres
  hachurées sont dans les lames sombres, pas sur le cœur blanc ;
- juger chaque planche à la taille de l'écran ET jouée (en 2, tournée),
  pas seulement en vignette.

## 4. Retiré (2026-09-25, Milan)

Tourbillon, rouge et soleil sont RETIRÉS du Poing du Dragon : « ça ne rend
pas bien pour du Roblox premium ». Seule la carte manga de la gueule reste
(0,5 s). Le temps libéré montre le dragon en 3D (fiche POING_DU_DRAGON_V13
§9, v13d). Les fonctions de dessin restent dans `build_planches.py` pour une
autre technique, sans être jouées.

