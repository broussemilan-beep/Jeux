# Fiche de conception : le COUP CHARGÉ (poing puissant, Serious Punch, obari)

**Ce qu'est une fiche de conception.** Retour de Milan (2026-09-25) :
« le cerveau se nourrit, mais à 30 %, et toi aussi ».
- Audit de la v8 : elle n'avait puisé que dans 4 sources sur ~15 (le
  carnet, trois tutos, des mesures TSB).
- Jamais consultés : l'étude visuelle, les notes brutes, les 41 extraits
  sakuga, les reproductions, l'étude TSB, le critique… et rien sur le
  Serious Punch.
- Cause : le cerveau empile des documents CHRONOLOGIQUES (une étude par
  jour). Rien ne rassemble tout ce qu'on sait au moment de DÉCIDER.

Une fiche de conception, c'est cette digestion : tout ce qui touche UN
moment de décision, rassemblé, relu et relié, avec sa source. Ce sont des
apprentissages, pas des règles. C'est le point d'entrée avant de poser la
moindre clé.

**Rappel** : `python3 outils/rappel.py "coup chargé"` ; refs :
`corpus/CATALOGUE_REFS.md`.

---

## 1. Ce que Milan veut (ses mots, dans l'ordre)

| quand | ses mots |
|---|---|
| r6_directional_punch (projet précédent) | « le perso est censé charger son poing » ; « il charge son poing à son arrière droit » ; « tourner son buste vers la droite pour charger son poing droit, plier les jambes légèrement, le 2e bras placé, et boum il envoie » ; « il manque les épaules, on dirait que le coup part du bas alors qu'il doit aller droit » ; « tu n'as pas réussi à donner le sentiment d'un coup de poing… une espèce d'élancement du bras » |
| Dragon v3b | « le coup final : enchaînement d'uppercuts et coup droit » |
| Dragon v4 | « au coup final le coup part toujours d'en bas ; je verrais plus le coup de Saitama, **un coup qui se charge avec le buste qui tourne** » |
| Dragon v5 | « c'est toujours pas bon ; je vois pas trop de différence avec la v4 » |
| Dragon v6 | « l'animation reste le bémol : il manque un cap par rapport à ce que je veux et nos refs » |
| Dragon v7 | « je vois aucun changement… trop simple… nos refs, c'est plus exagéré et un placement différent » |
| Dragon v7 (aérien) | ses 2 images : Deku, **poing vers le lecteur** ; poing géant au premier plan : « c'est vraiment le coup chargé de Saitama » |
| Dragon v8 | « le coup final, toujours pas bon, normal : pas encore travaillé » |
| 2026-09-25 | « poing chargé puissant doit faire écho au Serious Punch de Saitama, le GIF et l'anime TSB » |

**Ce qui revient depuis le début** :
- le BUSTE qui tourne pour charger ;
- le poing armé DERRIÈRE ;
- les jambes pliées ;
- l'autre bras placé ;
- un coup qui va DROIT, jamais de bas en haut ;
- le SENTIMENT d'un coup, pas un bras qui s'élance ;
- et, comme modèle, le Serious Punch de Saitama.

## 2. La référence : le Serious Punch (TSB), revu image par image

Deux enregistrements du même coup, deux avatars : **48244687 = IMG_3251**
(Saitama, cape jaune) et **772ee6b0** (« Serious Punch 2 »). Revus le
2026-09-25 à 5 i/s, en sachant enfin ce qu'ils sont. Même structure dans
les deux :

| temps | durée | ce qu'on voit | caméra |
|---|---|---|---|
| 1. entrée | ~0,8-1,6 s | la caméra traverse le corps (dos, cape, bras en très gros plan qui remplit l'écran) et ressort DEVANT le perso | poussée continue, transition par le corps |
| 2. **calme** | **~1-1,2 s** | debout, bras un peu écartés, visage plat tourné vers nous (l'adversaire). Presque immobile. | plan moyen de face, fixe |
| 3. départ | ~0,4-0,6 s | petit ramassé, puis la caméra FOUETTE (sol, ciel) | whip pan |
| 4. approche | ~0,8-1 s | plan large et bas : le perso, PETIT, en fente très basse, torse presque horizontal, cape au vent | large, au ras du sol |
| 5. armé | ~0,4 s | la caméra fonce devant lui en contre-plongée ; il se relève en tordant le buste, le poing armé à la hanche / derrière, genou haut | très gros plan bas, de FACE |
| 6. **frappe** | ~0,4 s | le **POING VIENT VERS L'OBJECTIF** dans un tourbillon de fumée ; on ne voit plus que le torse et le gant qui remplissent le cadre | caméra DEVANT, basse : obari |
| 7. impact | 1 carte + 0,2-0,4 s | carte à l'encre (silhouette dans des hachures radiales), puis BLANC total qui se dissout en fumée | — |
| 8. **conséquence** | **~1,2 s et plus** | plan large : cratère, pics de roche, le perso en FENTE BASSE, poing en avant, TENU (de dos ou de 3/4) | large, fixe |

**Ce que ça m'apprend** (en le regardant, pas en le mesurant) :
- **La frappe se voit DE FACE, poing vers la caméra**, pas de profil. C'est
  la même grammaire que la planche manga OPM (8965d689) et que Deku
  (0ca551a4).
  - Chez nous, v5-v8, le coup chargé traverse l'écran de côté.
  - L'info était dans les notes brutes depuis le 24/09 (« charge en très
    gros plan sur le POING dans la fumée ») et n'a jamais atteint la
    production.
- **Le calme d'abord** : ~1 s debout, presque rien. Le contraste calme ->
  violence fait la puissance.
  - Rejoint le visage plat de Saitama (sakuga 162980), l'Ultimate1 de TSB
    presque debout, et le silence avant (§2.5b du carnet).
- **La conséquence tenue** (fente basse dans le cratère, ~1,2 s) est la
  pose qu'on retient. Rejoint §2.6b et myloe (pose d'après tenue).
- **Le corps n'est vraiment montré que deux fois**, et en très gros plan :
  l'armé et la frappe. Le reste, c'est de la caméra, de l'échelle et des
  effets.

## 3. Ce que disent les autres sources (relues pour cette fiche)

**Anime** (`ETUDE_NOTES_BRUTES.md`, sakugabooru) :
- **OPM #12, Saitama contre Boros** (162980) : on ne montre PAS le bras du
  coup final. On montre un très gros plan du visage, puis l'effet, un trait
  qui traverse le noir.
- **OPM #01** (194936) : caméra SOUS le poing qui monte, poing énorme contre
  le ciel, impact hors champ. « Vers le haut » n'est pas mauvais en soi :
  c'est la mise en scène qui compte.
- **Poing vers la caméra, tenu** : 14 f (MHA S4, 281605), 16 f (MHA fan,
  200870). Le poing qui se serre en gros plan, tenu 16 f (One Piece,
  283898).
- **Bras tiré TRÈS loin en arrière**, étiré, tenu (Gear 5, 234966).
- **Gros plan du visage tenu ~24 f avant le coup** : Kekkai Sensen (le
  mieux noté), One Piece, DB.

**Images de Milan** :
- planche OPM : le poing plus gros que la tête, en raccourci, visage crispé
  derrière (8965d689) ;
- Deku (0ca551a4) ;
- charge basse et large style Baki (33393716).

**TSB** (fichier officiel, autre personnage que Saitama ; `ETUDE_TSB.md`) :
- **Stoic Bomb** : plongeon, puis charge **tenue 2,5 s**, bras croisés
  devant la poitrine (silhouette compacte), puis libération ;
- les compétences basculent le torse de 44 à 97° (nous, charge et coup :
  35°) ;
- l'**Ultimate1** est presque debout (7°) : la caméra et les effets font
  l'ultime.

**Tutos** (`tutos/`, carnet §2) :
- **myloe (punch Blender)** : charge TENUE 0,57 s, extension en UNE image,
  pose d'après TENUE, corps plié, dos vers nous ;
- **Dong Chang** : l'armé retient beaucoup d'images, le coup tient en
  1 image, suite lente ; « ressenti, pas vu » ;
- **Babbitt / firytwig** : on peut sauter le contact et montrer le
  résultat ;
- **Wimshurst** : le torse part en premier, le poing reste le plus
  longtemps derrière (fouet) ; un coup puissant sort le centre de gravité
  des pieds.

**Nos reproductions** (`repro/README.md`) :
- **obari** : la perspective suffit à faire un poing géant en R6 (corps qui
  plonge, bras déboîté, caméra à ~1 stud, grand angle) ;
- **la charge se juge depuis SA caméra** (de 3/4), la frappe depuis la
  victime ;
- **un membre pointé vers l'objectif cache tout**, sauf celui qui porte le
  coup.

**Carnet** :
- §1.3 cadrage ;
- §2.2 contact montré ou sauté ;
- §2.5b silence ;
- §2.6b suite longue ;
- §3.1 perspective forcée (GGXrd : avancer le bras vers la caméra plutôt
  qu'élargir le FOV) ;
- §1.10 TSB en réf visuelle.

## 4. Ce qu'on a déjà essayé, et pourquoi ça n'a pas marché

**Correction (2026-09-25, en construisant la v9).** Dans le Poing du Dragon, il
y a DEUX coups chargés : la charge au sol (f121-150, l'ex-uppercut) et le
coup aérien (f200-288). Depuis sa note v7 (« coup chargé aérien, qui part
toujours d'en bas »), Milan appelle « coup final » le coup **aérien**. La
première version de ce tableau mélangeait les deux.

- **v1-v8, aérien** : charge suspendue ~1 s vue DE DOS (plongée au-dessus de
  l'épaule), poing levé au-dessus de la tête, donc dans la colonne du corps et
  invisible. La plongée est filmée en contre-plongée depuis sous la victime,
  et le contact reste illisible (blocs plein cadre). C'est revu à l'œil sur la
  v8 avant de construire la v9.
- **v9, aérien** : fait d'après cette fiche. Résultat dans `r6_poing_dragon/README.md`, section v9.

Historique de la charge AU SOL :

| version | coup final | ce qui a été reproché | lecture aujourd'hui |
|---|---|---|---|
| v1-v4 | uppercut sorti d'une boule, puis enchaînement uppercut + direct | « part d'en bas », « enchaînement d'uppercuts » | pose en boule, en plan moyen, qui ne raconte rien |
| v5 | direct « Saitama » à f150, torse tourné | « pas de différence » | la charge était une CROIX (93 % des images) |
| v6 | + mise en scène (cartes, blanc, gros plan) | « il manque un cap » | le coup reste vu de côté |
| v7 | charge « Serious Punch », contact penché | « aucun changement » | pose correcte, mais floue (wiggle + caméra), contact recouvert par les cartes, vue de côté |
| v8 | inchangé | « pas encore travaillé » | — |

**Le fil commun des échecs** :
- on a retravaillé la POSE du coup, vue de CÔTÉ, sept fois ;
- la référence que Milan cite depuis la v4 montre le coup DE FACE, vers
  l'objectif, avec un calme avant et une conséquence tenue après ;
- on a corrigé ce qui se mesure (bras, épaules, torsion) au lieu de ce qui
  se voit (où est la caméra quand le poing part).

## 5. Ce que ça suggère pour la prochaine version (pistes, pas règles)

- **Structure en actes, comme le Serious Punch** : calme tenu, départ,
  armé en très gros plan, frappe vers l'objectif, carte, blanc, conséquence
  tenue.
- **Armé** (pour SA caméra, de 3/4 ou de face-bas) : buste qui tourne,
  poing derrière à la hanche ou à l'épaule, jambes pliées, genou haut,
  l'autre bras placé devant. C'est la demande de Milan mot pour mot, et la
  pose v7 est une base.
- **Frappe** : caméra devant et basse ; le poing vient vers l'objectif ;
  corps qui plonge et bras déboîté vers la caméra (obari, GGXrd). La frappe
  tient en 1-2 images ; la fumée et le tourbillon font la vitesse.
- **Contact** : sauté (Babbitt), on passe directement à la carte et au
  blanc. Ou alors montré net, 2-3 images, AVANT les cartes, jamais recouvert.
- **Conséquence** : fente basse, poing en avant, tenue 1 s ou plus, en plan
  large (cratère déjà présent).
- **Deux ou trois variantes jugées à l'œil en mouvement** (carnet §1.9).
  Ensuite seulement, comparaison visuelle au GIF Serious Punch, même durée
  et côte à côte (§1.10), puis mesures en garde-fou.

## 6. Sources consultées pour cette fiche

- Relus : Serious Punch TSB et Serious Punch 2 (image par image) ;
  `ETUDE_NOTES_BRUTES.md` (Serious Punch, sakuga Saitama et poing, images
  fixes) ; `REFERENCES_VIDEO.md` ; `ETUDE_TSB.md` ; `repro/README.md` ;
  `r6_directional_punch/README.md` (retours de Milan) ; `notes_milan.jsonl`
  v1-v8 ; `CARNET.md` ; `FICHE_V7.md`.
- Pas relus en entier pour cette fiche : `ETUDE_VISUELLE.md` (sections
  A-L, résumées par les notes brutes), `TUTOS_ANIMATION.md`, les fiches
  `corpus/clips/*.json` (mesures d'analyse vidéo).
