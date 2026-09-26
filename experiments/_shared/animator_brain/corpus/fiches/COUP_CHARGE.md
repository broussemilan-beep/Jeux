# Fiche de conception : le COUP CHARGÉ (poing puissant, Serious Punch, obari)

**Ce qu'est une fiche de conception.** Retour de Milan (2026-09-25 11:22) :
« j’ai l’impression que le cerveau se nourri mais que à 30% […] Et toi ausis ».
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

Mots exacts, orthographe d'origine, copiés de `corpus/milan_verbatim.jsonl`
(nettoyage du 2026-09-26 : les versions d'avant étaient des reformulations).

| quand | ses mots |
|---|---|
| r6_directional_punch (projet précédent) | 2026-09-03 14:32 : « le perso est censé charge son poing » ; 17:19 : « le perso charge son poing à son arrière droit » ; 19:13 : « le peros est cense tourné son buste vers la droit charger sont moins droit plier les jambes le légèrement le 2e bras placé et boum il envoi » ; 20:19 : « Il manque les épaules on dirait que le coup pars du bas alors que il doit allez droit » ; 2026-09-04 19:34 : « tu n’a pas réussi a donné le sentiment d’un coup poing […] Le perso met juste une espèce d’élancement du bras » |
| Dragon v3b | 2026-09-24 14:24 : « pareil pojr le grans coup final on dirait un enchainement d’uppercute mais en meme temps coup droit » |
| Dragon v4 | 2026-09-24 15:15 : « au coup final le coup par tjrs d’en bas […] moi sur lz coup de fin je verrai plus comme le coup de saitama **un coup qui se charge avec un le bust qui tourne** » |
| Dragon v5 | 2026-09-24 17:24 : « C tjrs pas bon je met 6,8 je vois pas trop de dif avec la v4 » |
| Dragon v6 | 2026-09-24 20:01 : « l’animation reste tjrs le bémols il manque un cap que on a pas par rapport à ce que je veux et nos ref » |
| Dragon v7 | 2026-09-25 06:22 : « Je vois aucun changement je t’avoue […] c’est trop simple fin revoi les animations de no ref dnas la lecture c plus exagère et un placement différent » |
| Dragon v7 (aérien) | ses 2 images : Deku, **poing vers le lecteur** [CONTREDIT 2026-09-26 : main OUVERTE, bras plié qui traverse, voir corpus/etude_c4/C4_images_et_gout.md §1.5] ; poing géant au premier plan ; 2026-09-25 06:22 : « dans l’idée c vrmt le coup charge de saitama » |
| Dragon v8 | 2026-09-25 11:04 : « c tjrs pas bon le coup final ce qui est normal car pas encore travailler » |
| 2026-09-25 11:19 | « même si je t’évoque poing charge puissance ça devrai faire écho à notre gif coup sérieux de saitama a la fois le gif et à la fois l’anime tsb » |

**Ce qui revient depuis le début** :
- le BUSTE qui tourne pour charger ;
- ~~le poing armé DERRIÈRE~~ [CONTREDIT par Milan le 2026-09-26 09:04 : « dans aucune le bras est tendu derrière » ; c'est le BUSTE qui tourne qui met le poing en arrière, voir CARNET 2.10] ;
- les jambes pliées ;
- l'autre bras placé ;
- un coup qui va DROIT, jamais de bas en haut ;
- le SENTIMENT d'un coup, pas un bras qui s'élance ;
- et, comme modèle, le Serious Punch de Saitama.

## 2. La référence : le Serious Punch (TSB), revu image par image

*Statut : vu dans les refs (48244687 et 772ee6b0, revus à 5 i/s le 2026-09-25) ; des lectures sont CONTREDITES depuis (marques dans le texte, `corpus/etude_c4/C3_gifs.md` §1).*

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
| 8. **conséquence** | **~1,2 s et plus** | plan large : cratère, pics de roche, le perso en FENTE BASSE, poing en avant, TENU [CONTREDIT 2026-09-26 : dans le GIF 48244687, à la fin, bras plié à l'horizontale devant le buste (confiance moyenne), voir corpus/etude_c4/C3_gifs.md §1] (de dos ou de 3/4) | large, fixe |

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
    presque debout, [CONTREDIT 2026-09-26 : l'Ultimate1 du .rbxm n'est pas le Serious Punch (poses qui ne collent pas, marqueur « AwakenFinale », modèle racine « KJ ») et n'est pas presque debout (deux bras, buste jusqu'à 86°), voir corpus/etude_c4/C3_gifs.md (annexe), corpus/etude_c4/A3_tsb_ultimes_mur.md §0.1 et corpus/etude_c4/A3_tsb_ultimes_mur.md §1.5] et le silence avant (CARNET §2.5b).
- **La conséquence tenue** (fente basse dans le cratère, ~1,2 s) est la
  pose qu'on retient. Rejoint CARNET §2.6b et myloe (pose d'après tenue).
- **Le corps n'est vraiment montré que deux fois**, et en très gros plan :
  l'armé et la frappe. Le reste, c'est de la caméra, de l'échelle et des
  effets.

## 3. Ce que disent les autres sources (relues pour cette fiche)

*Statut : lu (nos études relues pour cette fiche le 2026-09-25) ; les refs elles-mêmes n'ont pas toutes été re-regardées.*

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
- CARNET §1.3 cadrage ;
- CARNET §2.2 contact montré ou sauté ;
- CARNET §2.5b silence ;
- CARNET §2.6b suite longue ;
- CARNET §3.1 perspective forcée (GGXrd : avancer le bras vers la caméra
  plutôt qu'élargir le FOV) ;
- CARNET §1.10 TSB en réf visuelle.

## 4. Ce qu'on a déjà essayé, et pourquoi ça n'a pas marché

*Statut : essayé (r6_directional_punch, Poing du Dragon v3-v9) et retours de Milan (tableau §1).*

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

*Statut : non établi (pistes déduites des §2-4, pas essayées telles quelles).*

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
  et côte à côte (CARNET §1.10), puis les mesures, lancées à la main (piste :
  rien dans l'export ne les lance au 2026-09-26).

## 6. Sources consultées pour cette fiche

*Statut : lu (la liste dit ce qui a été relu et ce qui ne l'a pas été).*

- Relus : Serious Punch TSB et Serious Punch 2 (image par image) ;
  `ETUDE_NOTES_BRUTES.md` (Serious Punch, sakuga Saitama et poing, images
  fixes) ; `REFERENCES_VIDEO.md` ; `ETUDE_TSB.md` ; `repro/README.md` ;
  `r6_directional_punch/README.md` (retours de Milan) ; `notes_milan.jsonl`
  v1-v8 ; `CARNET.md` ; `FICHE_V7.md`.
- Pas relus en entier pour cette fiche : `ETUDE_VISUELLE.md` (sections
  A-L, résumées par les notes brutes), `TUTOS_ANIMATION.md`, les fiches
  `corpus/clips/*.json` (mesures d'analyse vidéo).

## 7. Reprise du coup final aérien (après la v9 : 7,7, « que les bras »)

*Statut : mesuré (`outils/corps_bras.py` sur la v9) et retour de Milan (v9, 7,7) ; les pistes sont non établies.*

Mesuré avec `outils/corps_bras.py`. À faire quand l'animation reprendra :
- **Calme vivant** : il flotte, avec une dérive lente du bassin et du torse
  (respiration, léger roulis) et une tête qui suit la victime. Aujourd'hui
  il est figé 24/24 images.
- **Armé porté par le corps** : pendant la tenue, le TORSE continue de
  s'enrouler lentement, le genou monte encore, les épaules se tassent.
  C'est la tension qui monte (la v5 au sol le faisait : « le buste continue
  de s'enrouler »). Aujourd'hui seule la direction du poing oscille.
- **Frappe menée par le corps** : pendant la ruée (263-278), le torse
  continue de tourner et de plonger, les jambes fouettent en retard
  (chevauchement), la tête rentre. Le bras suit le corps, au lieu d'un bloc
  translaté avec un bras qui bouge.
- **Enchaînement / smooth** : pas de segment où tout s'arrête puis repart
  d'un coup (calme -> départ LINEAR ; clés 263/270/278 identiques). Avant de
  montrer, regarder la pelure d'oignon du torse et l'espacement du torse
  dans les deux caméras, pas seulement des planches.
