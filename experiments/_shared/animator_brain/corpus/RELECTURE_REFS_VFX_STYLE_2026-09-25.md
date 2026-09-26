# Relecture : 5 effets stylisés (style anime, Roblox), 2026-09-25

Envoyés par Milan sans texte, après les deux archives vidéo. Images fixes
(pas de timing). Mesures : part de pixels d'effet (blanc / saturé), palette
6 couleurs. Fichiers au catalogue (section « Effets stylisés »).

| image | ce que c'est | effet | blanc | saturé | sombre |
|---|---|---|---|---|---|
| 8005ceb1 | deux jaillissements au sol, bleu et orange | 35 % | 17 % | 17 % | 0 % |
| f23068ce | tranchée de roche en fusion (Roblox) | 18 % | 1 % | 18 % | 3 % |
| 81f070a6 | trois auras (rouge, bleue, jaune) sur des persos | 13 % | 2 % | 11 % | 71 % (fond de nuit) |
| 0f85f7a1 | tornade / couronne de feu | 13 % | 0 % | 13 % | 0 % |
| 22c8d49c | impact sombre rouge et noir | 15 % | 1 % | 14 % | 1 % |

## Ce que je lis, effet par effet

**Jaillissements bleu / orange (8005ceb1).** Des lames de flamme ou de
cristal en DENTS DE SCIE qui montent, en 3 tons : bout sombre (bleu nuit /
brun), milieu saturé, cœur BLANC. À la base, un arc blanc incandescent (un
croissant), et des TRAITS NOIRS courbes (comme des griffures d'encre)
PLANTÉS DANS l'effet clair. Étincelles en diagonale. La moitié de l'effet
est blanche (17 % de l'image), l'autre saturée : le contraste vient du
blanc contre le saturé, et du noir posé dessus.

**Tranchée en fusion (f23068ce).** Une LIGNE au sol : tranchée de roche
sombre (mesh) à l'intérieur jaune-orange ; grandes pointes triangulaires
jaunes en Neon qui en sortent ; arcs jaunes (demi-anneaux) le long ; traits
de vitesse jaunes parallèles à la direction ; débris noirs semés autour.
L'effet est bien plus grand que le mannequin (minuscule au bout).

**Auras (81f070a6).** Rouge : scintillements en croix + petites lames
autour du corps. Bleue : cœur blanc très lumineux + particules en VIRGULES
(flammèches enroulées). Jaune : feu cel qui couvre le corps, rayon de
lumière vertical au-dessus de la tête. Chaque aura : une forme de
particule signature + un point lumineux au sommet.

**Tornade de feu (0f85f7a1).** Des CROISSANTS en spirale (meshes qui
tournent) blanc-jaune au cœur, orange au bord ; une couronne de langues de
flamme pointues qui montent ; halo de lueur. Trois tons + lueur.

**Impact sombre (22c8d49c).** Étoile blanche au centre (flash), lueur
rouge, et des VEINES noir-cramoisi qui éclatent en étoile sur le sol et
vers le haut (projection d'encre) ; étincelles rouges ; une pointe sombre
verticale. L'énergie « sombre » = encre noire + rouge + cœur blanc.

## Ce qu'ils disent ensemble

1. **Échelle de valeurs : cœur BLANC → couleur saturée → bord SOMBRE, et
   du NOIR dans l'effet.** Les griffures noires (8005ceb1), les veines
   d'encre (22c8d49c), la roche sombre (f23068ce) : le noir fait ressortir
   le lumineux. Nos effets n'ont presque jamais de noir dedans (seulement
   la fumée).
2. **Silhouettes pointues** : dents de scie, lames, langues de flamme,
   pointes triangulaires. Jamais de taches rondes.
3. **Mouvement dessiné** : croissants en spirale, arcs, traits de vitesse
   dans le sens de l'effet.
4. **Lueur (halo) autour**, jamais sur tout : le cœur blanc déborde.
5. **Une forme signature par effet** (virgules bleues, croix rouges,
   langues jaunes) : on reconnaît l'effet à sa forme de particule.

## Comparaison avec nos effets (captures v12)

- Notre impact au sol (`captures/verification/2026-09-25-v12-impacts-debris-bloom.png`) :
  étoile blanche, anneau, feu cel à contour, croissants, débris : la
  structure y est, mais le feu est en TACHES arrondies (pas de dents de
  scie), il n'y a pas de noir dans l'effet, et la part de blanc est faible.
- Notre tourbillon (mesh « tourbillon » qui défile) : un cône flou, pas des
  croissants nets en spirale ni une couronne de langues.

## Ce que le studio devrait avoir (pistes, pas décidées)

- Textures : lames / flammes en dents de scie 3 tons avec cœur blanc ;
  griffures d'encre noires ; veines d'encre en étoile ; virgules.
- Meshes : croissants en spirale qui tournent (tornade) ; pointes
  triangulaires Neon ; tranchée.
- Recettes : « jaillissement » (lames + arc blanc + griffures + étincelles),
  « tornade » (croissants + couronne), « impact sombre » (flash + veines +
  lueur rouge).
