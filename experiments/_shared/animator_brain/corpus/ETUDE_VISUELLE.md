# Étude visuelle : ce que font les pros au moment du coup

Étude du 2026-09-24, faite à la demande de Milan : « regarder les 57 extraits
et les refs déjà envoyées, travailler le jugement et la logique d'animateur,
aller plus loin que la théorie ».

## Méthode

Pour chaque clip, `scraper/planches_etude.py` fabrique une planche : jusqu'à
3 moments forts (impacts, puis pics de mouvement) et, pour chacun, 12 images
de −30 à +14 f à 60 i/s. J'ai regardé ces planches **une par une** :

| lot | planches regardées |
|---|---|
| refs de Milan (vidéos) | 16 |
| images fixes de Milan | 15 |
| Sakugabooru | 41 |
| Danbooru | 15 |
| notre v5 | 1 |
| **total** | **88** |

- **Notes brutes, clip par clip** : `ETUDE_NOTES_BRUTES.md`.
- **Les planches elles-mêmes** (des images d'œuvres protégées) restent en
  local et ne sont pas versionnées.
- **Ce qui est versionné**, c'est ce qu'on en tire : ce document et les
  hypothèses du cerveau.

**Le décompte.** Pour chaque principe, j'indique dans combien de clips je
l'ai vu, pris parmi les 68 planches. Ce sont des comptes d'observation, pas
une statistique propre.

## Le constat central

Pendant 5 versions, on a corrigé la **mécanique du bras** : hauteur,
trajectoire, épaules, arcs. Les notes ont à peine bougé (6,0 puis 6,7, 6,7
et 6,8).

Les références disent autre chose. Au moment du coup, les pros travaillent
la **mise en scène** bien plus que le bras : cadrage, échelle, cartes
graphiques, silence, puis explosion.

Notre partie aérienne, la seule que Milan aime, applique déjà cette
grammaire : lignes de vitesse, caméra proche, cartes silhouette et X, blanc
total. Notre rafale et notre coup final ne l'appliquent pas.

## Les principes

Pour chaque principe : ce que font les refs, combien de clips le montrent,
ce qu'on fait nous.

### A. Cartes d'impact graphiques — environ 24 clips

Milan a envoyé la même carte en deux polarités (`41d7796b` puis
`a4a75c01` : étoiles noires sur blanc, puis blanches sur noir). L'alternance
noir/blanc d'une image à l'autre, c'est une même carte inversée. On retrouve
cette grammaire jusque dans une cinématique de jeu 3D (Honkai Star Rail).

**Ce que font les refs.** Au moment du choc, l'image 3D est remplacée par 2
à 8 cartes de 2 à 4 f chacune. On y trouve :
- une silhouette inversée (blanc sur noir) ;
- un dessin à l'encre hachurée, façon manga ;
- un négatif ou une « radio » où l'on voit le crâne ;
- une image posterisée en 2 tons ;
- une couleur plate ;
- des graphismes de cible, de croix ou d'étoile.

**Où on le voit.**
- **Roblox** : coup chapeau, Black Flash, Serious Punch 2, Serious Punch
  TSB, IMPACT HAVEN, Black Hole, Rewind Clock, Gemini.
- **Anime** : MHA (Nakamura), One Piece (Ishizuka, Mori, Shinya), DBS
  Broly, Hajime no Ippo, OPM, L'Attaque des Titans, parodie Gear 5.

**Chez nous.** La partie aérienne a des cartes (silhouette, X, blanc). La
rafale et le coup final n'en ont **aucune**.

### B. Le silence avant le boum : noir de 2 à 10 f — environ 14 clips

**Ce que font les refs.** Juste avant ou juste après l'impact, l'écran
passe au **noir**, souvent avec une toute petite étoile. C'est le temps mort
qui fait exploser la suite.

**Où on le voit.**
- **Roblox** : coup chapeau (8-12 f).
- **Anime** : Kekkai Sensen (le clip le mieux noté, 5892), OPM contre
  Boros, MHA, Dragon Ball, Boruto, FMA:B, One Piece, Ippo.

**Remarque.** C'est la vraie version de ma vieille hypothèse « tenue avant
le choc ». La mesure de pixels la ratait parce qu'elle cherchait un freinage
du mouvement, pas un écran noir.

**Chez nous.** Jamais.

### C. Blanc total de 2 à 15 f — environ 12 clips

**Ce que font les refs.** L'écran devient blanc, souvent en alternance avec
le noir (blanc 4 f, noir 4 f, sur MHA et One Piece), ou en blanc qui se
dissout en fumée (Serious Punch TSB).

**Chez nous.** Oui dans la partie aérienne ; au coup final, une bulle
blanche qui cache tout, mais pas de vrai blanc total.

### D. Le regard avant l'action — environ 10 clips

**Ce que font les refs.** Un très gros plan sur le **visage** ou les
**yeux**, tenu de 16 à 30 f, **avant** que le coup parte. C'est
l'intention : la charge se lit dans le regard, pas seulement dans la pose.

**Où on le voit.** Naruto (Matsumoto, 28 f sur les yeux), OPM (Saitama
contre le géant, Genos), Kekkai Sensen, One Piece, Dragon Ball, Gemini
(visage qui hurle), JJK, MHA.

**Chez nous.** Jamais. Notre caméra ne s'approche jamais d'un visage.

### E. Le poing en très gros plan, souvent vers la caméra — environ 11 clips

**La référence Saitama de Milan est exactement ça.** Sa planche manga
(`8965d689`) montre le poing qui vient **vers le lecteur**, plus gros que la
tête, au milieu des débris. Le même principe marche en 3D temps réel : dans
Umamusume, la chaussure remplit l'écran. Notre v5 montrait le coup de profil.

**Ce que font les refs.** Le poing ou le bras remplit l'écran, en raccourci,
tenu de 12 à 16 f : c'est la puissance faite image. Pendant la charge, la
caméra est collée au bras (Serious Punch TSB et Serious Punch 2).

**Chez nous.** Jamais. Le poing mesure 1/20 de l'écran.

### F. Contraste d'échelle — environ 9 clips

**Ce que font les refs.** On coupe d'un perso **minuscule** dans un plan
très large à un **très gros plan**, ou inversement : contact en gros plan,
puis conséquence en plongée très lointaine.

**Où on le voit.** Black Flash (plan lointain puis impact plein cadre),
Stagnant Rage, MHA, Hitori no Shita, OPM, Chainsaw Man, JJK, Dragon Ball
1986.

**Chez nous.** Le plan est toujours moyen, les deux persos en entier.

### G. Décor remplacé à l'impact — environ 6 clips

**Ce que font les refs.** À l'impact, le fond devient des lignes de
vitesse, une couleur plate (jaune, orange) ou un fond flou.

**Où on le voit.** Ippo, Dragon Ball (deux fois), MHA, Black Flash.

### H. Une caméra qui vit — environ 7 clips

**Ce que font les refs.**
- **Fouet vers le ciel** quand le perso saute ou frappe : Serious Punch TSB,
  Serious Punch 2, Umamusume.
- **Rotation, cadre penché** : Naruto, Soul Eater, Black Flash.
- **Zoom éclair** en 2 f : Black Hole.
- **Poussée jusque dans le corps**, qui fait transition : Serious Punch TSB.

### I. Torsion du tronc et poses extrêmes — environ 7 clips

**Ce que font les refs.**
- Le **tronc** s'enroule puis se déroule. On le voit de dos ou de
  trois-quarts, et la caméra suit le torse, pas le bras (Hajime no Ippo).
- Les M1 pro passent de face à dos (combo R6 front, 120-150°). Le pro du
  « pro contre noob » est tordu et compressé.
- IMPACT HAVEN : corps inversés.
- JJK : garde très large, arcs du corps entier.
- La **garde basse et large** est normale (Mii, JJK, Ippo). Le « accroupi »
  reproché visait la *boule*, pas la garde.

**Chez nous.** Le buste tourne de 45° dans la rafale. C'est timide.

### J. Lisibilité des silhouettes — tous les bons clips

**Ce que font les refs.** Les deux persos sont séparés, avec une ligne
d'action claire. Dans « noob contre pro » à l'épée, la pose pro est un T
lisible, la pose noob est encombrée.

**Chez nous.** Dans la rafale et au coup final, les deux persos **se
chevauchent** en plan moyen : le bras qui frappe disparaît contre la
victime, et le poing armé du coup chargé est caché derrière le corps.

### K. Smear et trajectoire dessinée — environ 5 clips

**Ce que font les refs.** Une traînée blanche porte la vitesse (tuto Moon
Animator). Dans JJK, de grands croissants noirs restent 10 f à l'écran. Chez
Ippo, un smear balaie tout l'écran.

### L. La victime se déforme — environ 4 clips

**Ce que font les refs.** Joue écrasée, corps plié autour du gant, bouche
grande ouverte, tête qui part (Ippo, Dragon Ball 1986, exemple Blender).

## Une nuance importante sur « le coup qui part d'en bas »

Dans OPM (Saitama contre le géant, planche 194936), le coup de Saitama
**monte**. La mise en scène est pourtant tout autre :
- la caméra est **sous** le poing ;
- le poing devient énorme contre le ciel ;
- l'ennemi est immense ;
- l'impact est hors champ.

Ce que Milan rejetait n'est donc peut-être pas la direction du coup, mais un
uppercut sorti d'une boule, filmé en plan moyen, qui ne raconte rien.

## Ce que ça change pour le cerveau

Nouvelles hypothèses « mise en scène » dans `hypotheses.json`, avec leurs
comptes de clips. Leur état est jugé à l'œil sur planche (source :
« jugement visuel »), partie par partie, pour v1 à v5. Les cartes, le noir
et le blanc sont en plus mesurables automatiquement par `clip_analyzer` (les
types de cartes y existent déjà).

## Ce que ça change pour la prochaine version

Il ne s'agit pas de toucher encore au bras. Pour le coup final, dans
l'ordre des refs :
1. très gros plan sur les yeux ou le visage, tenu 20 f ;
2. très gros plan sur le poing qui se serre ou s'arme, caméra collée au bras ;
3. départ en 2-4 f ;
4. noir de 6 f avec une petite étoile ;
5. 3 cartes de 4 f : silhouette inversée, encre hachurée, grand X ;
6. blanc total qui se dissout ;
7. plan très large sur la conséquence.

Pour la rafale : séparer les silhouettes (angle de caméra), un gros plan par
coup fort, décor remplacé par des lignes de vitesse à l'impact, torsion du
tronc bien plus grande.

## Lot 2 (Milan, 5 vidéos Roblox et animation) : ce que ça ajoute

Notes brutes dans `ETUDE_NOTES_BRUTES.md` (« LOT 2 »).

1. **L'ellipse** (« First time fighting a dummy »). On ne voit **jamais**
   le coup. Il y a d'abord un regard tenu 1,2 s, puis l'éclairage qui
   s'assombrit sur 2 f. Viennent ensuite 3 cartes de 2-3 f (noir griffé,
   encre hachurée, inversé), un blanc de 2 f, et le retour sur le même
   visage, surexposé. L'impact est **raconté**. Avant ça, le mannequin le
   malmène, pour rire : le contraste entre comique et sérieux donne son poids
   au moment sérieux.
2. **La hiérarchie des effets** (« punch practice », « cross punch »).
   - Petit coup : de petites lignes de vitesse au contact, 2-3 f, rien
     d'autre.
   - Coup principal : trois couches qui se suivent (étoile au poing sur 1 f,
     anneaux le long du bras sur 2 f, croissant de souffle sur 2-3 f).
   - Les « adornments » (particules, traînées) sont une couche **ajoutée** à
     une animation qui se lit déjà sans.
3. **Le métier du coup** (tuto firytwig) : armement, frappe, retour, avec
   les règles suivantes.
   - Les intervalles restent près de l'armement.
   - Pas d'amorti vers la pose de frappe.
   - Dépasser la pose (overshoot), ou tenir le membre.
   - Tout le corps dans le coup, surtout les hanches.

   **Mesuré chez nous :** le rythme du poing est **déjà au niveau** des M1
   pro (armement → contact en 5-10 f, extension tenue 8-10 f). Ce n'est pas
   ce qui retient la note.
4. **La rotation du corps et la caméra** (« pro vs noob » dans Blender,
   « punch practice »).
   - Le pro passe de « BACK » à « FRONT » face à la caméra, soit environ
     180° de torse. Il anime **en rotation, pièce par pièce** (les cercles
     sont des gizmos de rotation FK).
   - **Mesuré chez nous :** 98-137° sur les coups de puissance, contre
     109-162° pour les M1 pro. La rotation **existe en 3D**, mais notre
     caméra de côté l'écrase à l'écran.
   - Les pros vérifient sous **deux vues** (côté et dessus).
   - C'est un problème de lisibilité et de caméra, pas de corps.
5. **Le mouvement secondaire** (« cross punch ») : la queue et les oreilles
   suivent en retard pendant le suivi tenu. Notre R6 n'a rien qui pende.
   Ça ne s'appliquera que s'il a un accessoire.

**Ce que ça change dans le jugement.** Deux de mes hypothèses sur notre
retard sont écartées par la mesure : le rythme du poing, et en partie la
rotation du corps. Ce qui reste, c'est ce qui se voit à l'écran : l'angle,
la hiérarchie des effets, l'ellipse et la lisibilité.

**Leçon de méthode.** Les pros animent **un seul coup en boucle** (« cross
punch », « punch practice »), le perfectionnent et le regardent sous deux
angles. Nous, on a animé 9 s de technique d'un bloc.

## Lot 3 (Milan, 5 GIF de jeux battlegrounds, caméra de jeu) : ce que ça ajoute

Notes brutes dans `ETUDE_NOTES_BRUTES.md` (« LOT 3 »).

1. **Caméra de jeu contre cinématique : le point qui manquait.** Dans ces
   jeux, les coups ordinaires (M1, compétences) se jouent dans la **caméra du
   joueur** : fixe, souvent de dos, parfois lointaine. Ils doivent donc se
   lire de là. Seul l'**ultime** passe en cinématique. Chez le boxeur :
   - caméra de jeu de dos, puis blanc ;
   - angles proches qui changent toutes les ~0,6 s ;
   - quatre blancs de plus en plus gros ;
   - retour à la caméra de jeu de dos.

   Notre Poing du Dragon est entièrement pensé en cinématique, et jugé de
   profil. **On n'a jamais regardé s'il se lit depuis la caméra du joueur.**
2. **La hiérarchie des effets, confirmée en jeu.**
   - M1 : un éclat au poing sur 1 f et un anneau, à peine plus gros sur les
     coups 3-4.
   - Coup fort : éclat à éclats, gerbe rouge, anneaux qui s'élargissent.
3. **La rafale en masse** (« gatling »). Une rafale ultime très rapide ne se
   lit pas coup par coup. On la lit comme une **masse blanche de
   poings-smears** continue pendant 3 s, puis des anneaux de fumée. C'est le
   contraire d'une rafale courte de coups distincts, où chaque forme doit se
   lire : la règle d'usage décide laquelle choisir.
4. **La trace qui reste et la tenue sur la conséquence.**
   - Mythra : tache au sol, attaquant debout au-dessus, tenu 1,1 s.
   - Victime envoyée en point minuscule dans le ciel, visible même en caméra
     de jeu lointaine.
   - Notre partie aérienne (cratère, fumée) le fait déjà.
5. **Le contact prolongé** (Mythra) : saisie, soulèvement, projection. La
   victime est manipulée, pas seulement frappée.

**À vérifier sur notre travail, avant de toucher quoi que ce soit.** Une
planche de la v5 vue depuis une caméra de jeu (de dos, à distance de
joueur), pour juger si nos coups s'y lisent.

## Lot 4 : 4 refs revues en entier et la fiche « DEMI-DIEU »

Les 4 vidéos (Black Flash, Rewind Clock, Stagnant Rage, Black Hole) étaient
déjà dans le corpus. Mais la première étude ne regardait que 3 moments par
clip. Revues **du début à la fin**, elles montrent ce que les moments isolés
cachaient : **la structure**.

1. **Un ultime se construit en actes.**
   - **Black Flash :** caméra de jeu avec de petits effets (2,2 s), puis
     cinématique (2,6 s, cartes entre des plans collés et penchés), puis
     **ralenti tenu 1,4 s** sur la victime.
   - **Rewind Clock :** jeu, puis **signature** (anneau d'horloge tenu 1 s),
     puis le monde disparaît (fond blanc 2 s), puis les « radios » du crâne
     (1,2 s), puis retour à la caméra de jeu.
   - **Black Hole :** calme, anticipation, envol, geste (mains jointes),
     trou noir (3 s), **noir total 1 s**, puis retour au calme debout.
2. **La signature visuelle.** Chaque technique a son motif, qu'on reconnaît
   et qui annonce ce qui vient.
3. **Les variantes de jeu.** Stagnant Rage existe en version proche et
   lointaine, toute en caméra de jeu, sans cinématique : c'est une
   compétence, pas un ultime.

**La fiche Demi-Dieu** est un format de production : intention en une
phrase, 8 poses clés avec leurs frames (~1 s à 30 i/s), test de silhouette,
vues de référence, timing « lent → rapide → impact → stabilisation ».

- **Adoptée** comme modèle dans `corpus/FICHE_COUP_MODELE.md`, qui manquait
  au projet.
- **Critique :**
  - elle ne prévoit pas de **vue de dos**, alors que c'est la caméra du
    joueur en battleground ;
  - les silhouettes de la charge et du lancement sont presque identiques ;
  - l'image semble générée (texte abîmé), donc les poses sont à vérifier
    sur le vrai R6, dont les bras sont d'un seul bloc.
