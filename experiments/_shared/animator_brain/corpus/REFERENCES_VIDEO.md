# Références vidéo de Milan : timing mesuré image par image (2026-09-24)

Toutes les vidéos et images envoyées ont été relues. Les frames ont été
extraites avec ffmpeg, puis regardées sur des planches contact à 30 i/s
autour de chaque moment clé.

On tire d'une vidéo **le timing et le vocabulaire visuel**, pas des angles
exacts (voir `PLAN.md`, section 5). Les durées sont données en frames à
30 i/s (« f »). Les vidéos sources ne sont pas versionnées.

## Fiches

| réf | quoi | durée | à retenir |
|---|---|---|---|
| Black Flash (JJK, 3 sept.) | rafale de 6 coups, puis finish cinématique | 6,3 s | intervalles entre impacts 15/10/7/7/10 f ; chaque impact : **1 f de corps teinté rouge plat**, sphère noire, croix de flare, étoile rouge, encre, étincelles, soit 6-7 f en tout ; finish = gros plans extrêmes + inserts 2D tenus 2 f chacun, puis plan au ras du sol tenu 44 f |
| Rewind Clock (3 sept.) | horloge, puis arrêt du temps, puis rayons X | 9,9 s | décor blanchi, **freeze d'environ 2 s** avec orbite lente de ~10°, rafales de flashes d'1 f (blanc, glitch RVB, encre), 3 pulsations de palette en rayons X |
| Stagnant Rage (3 sept.) | poings de feu, variantes proche et lointaine | 9,8 s | activation = **flash blanc du corps sur 2 f** ; accroupi 8 f, décollage avec étoile au sol, arc de 10 f, plaquage en 3 f, dôme de feu ; charge en silhouette noire bordée de rouge ; méga-explosion en étoile à pics |
| Serious Punch (TSB, GIF) | ultime de Saitama | 10 s | caméra scénarisée : plongée, volet par le bras, **garde tenue 32 f**, saut, whip pan de 6 f, **temps suspendu en l'air 28 f** (poing armé, genou levé), dolly de 22 f, poing vers le bas dans une **fumée qui tourne** (24 f), **3 planches manga d'1 f** (croquis, lignes radiales, grand X), **écran blanc 6 f**, brouillard 8 f, révélation d'un **sol soulevé en pics** tenue 84 f |
| Moon Animator (30 août) | combo solo de 5 coups, VFX blancs monochromes | ~2,9 s | clés sur tous les membres toutes les 3-7 frames ; VFX **à pleine taille dès la 1re frame**, effacés en 3-6 f ; accroupi, plongée horizontale, slam avec pics blancs au sol |
| Pro vs noob, épée (23 sept.) | même combo, version noob puis pro | 2 × ~2 s | pro = armé lent de 14 f en ease-in, puis coups en **2-3 f**, **hold de 5-6 f au sommet**, hold final de 15 f ou plus ; noob = 16 f de dérive molle, sans hold |
| Gemini (IA) | invocation d'un soleil | 10 s | montage : push-in, snap d'expression, **impact frames inversées** (silhouette blanche sur noir, ~20 frames), soleil au-dessus de la tête, contrechamp de dos sur l'explosion. Cohérence non fiable (vidéo IA) |
| Images fixes | impact frames manga, One Punch Man, The Creator | — | étoile blanche à 4 branches sur fond noir, lignes verticales ; lignes radiales ; poing en raccourci extrême |
| IMPACT HAVEN (24 sept., short « AAA ») | combat à deux, acrobatique, sans particules | 8,2 s d'action | **19 impacts**, un toutes les 8-16 f (médiane 10 f) ; chaque impact = **1 f de silhouette** (persos blancs sur noir) **+ 1 f blanche** ; le mouvement **freine jusqu'à l'arrêt ~3 f avant**, puis **explose** juste après ; caméra fixe, large, de profil ; une traînée blanche droite par attaque ; fin en crash zoom sur le perso. Détail plus bas |

## Ce qui revient partout (principes, pas des chiffres à copier)

1. **Contraste de temps.** Tenue longue, puis action en 2-3 f, puis tenue
   longue sur le résultat. Le noob échoue précisément là.
2. **Le rythme d'une rafale n'est pas régulier.** Il accélère, puis se
   relâche avant le finish (15/10/7/7/10 f).
3. **Graphisme d'1 frame.** Teinte plate du corps, écran blanc, inversion,
   planches dessinées. Cette couche plein écran ne se fait ni avec des
   particules ni avec l'animation.
4. **La caméra est une piste animée**, synchronisée aux coups : push-in,
   whip pan, dolly, contre-plongée. Ce n'est pas la caméra de jeu.
5. **Le décor encaisse** : dalles basculées, pics, cratère. Une grosse
   technique se lit à ce qu'elle laisse au sol.
6. **Une palette par technique** : rouge/noir/blanc, or/blanc, feu.
   Monochrome blanc pour les combos de base.

## IMPACT HAVEN : mesures (24 sept.)

Short Roblox « IMPACT HAVEN » (@mariigamesreal), envoyé par Milan comme
référence « niveau AAA, mais encore différent ». Capture d'écran à 60 i/s
d'une source à 30 i/s. Mesures automatiques sur la zone de jeu (luminance,
image par image, de 1,7 à 10,2 s).

**Impacts.** 19 en 8,2 s. Écart entre deux impacts : 8 à 16 f (0,27-0,53 s),
médiane 10 f.
- Chaque impact tient 2 f, sans exception (deux fois, la silhouette est
  remplacée par un noir complet) :
  - 1 f de **silhouette** : persos en blanc pur sur fond noir, avec les
    traînées ;
  - puis 1 f de **blanc** plein écran.
- Pas d'étincelles, pas de fumée, pas d'onde : tout l'effet d'impact est dans
  ces deux cartes plein écran et dans le mouvement.

**Mouvement autour de l'impact** (différence moyenne entre images, médiane
sur 17 impacts) :

| moment | mouvement |
|---|---|
| −6 à −4 f | fort : l'approche |
| −3 à −1 f | presque nul : **tenue juste avant le choc** |
| 0 à 1 f | les 2 cartes |
| +2 f | encore tenu |
| +3 f | **le pic de tout le cycle** (environ 2 fois l'approche) |
| +4 à +7 f | décroissance (11,6 → 5,5 → 5,4 → 3,3) |

Le poids vient donc de ce qui entoure le choc :
- un arrêt **avant** le contact (on retient le coup) ;
- un flash qui cache le moment exact ;
- une réaction qui part à pleine vitesse puis ralentit.

C'est l'inverse de notre hitstop, qui gèle **après** le contact.

**Chorégraphie.**
- Échange à deux : les deux persos attaquent, esquivent, saisissent.
- Corps entiers tournés à 90-180°, projections, un perso qui vole à
  l'horizontale.
- Appui sur les mains, genoux, corps enchevêtrés au sol.
- Aucune garde de boxe. Silhouettes toujours lisibles : on les vérifie
  d'ailleurs à chaque impact, puisque la carte silhouette les montre seules.

**Caméra et décor.**
- Plan large de profil, horizon bas, beaucoup de ciel, presque sans coupe :
  l'animation porte tout.
- Une seule traînée blanche droite, dans l'axe du déplacement, pendant 1-2 f
  par attaque.
- Fin : crash zoom jusqu'au contact avec le perso, puis blanc, puis noir.
- Décor vide : baseplate et ciel.

**Différences avec le Poing du Dragon** (constat, pas encore des règles) :

| | IMPACT HAVEN | Poing du Dragon |
|---|---|---|
| impacts | 19 en 8 s, les deux persos frappent | 4 coups, puis la technique |
| arrêt | tenu **avant** le contact | gel **après** le contact (hitstop) |
| effet d'impact | 2 cartes plein écran, rien d'autre | flash du corps, étincelles, onde, fumée |
| caméra | fixe, large, de profil | 3 plans dans la rafale, whip pan, dolly |
| corps | acrobatique, corps entier en rotation | boxe, debout puis fente |
