# Carnet d'apprentissage (pas des règles)

Demande de Milan (2026-09-25) : « rajoute encore plus de tutos, le but
apprendre et nourrir, pas forcément combler des trous… des tricks, des
pépites utiles, mais ça doit pas devenir des règles, mais de
l'apprentissage ; le but c'est qu'on soit hyper fort, polyvalent. »

Ce carnet est la **mémoire de ce que j'ai appris et pas encore prouvé
chez nous**. Il n'est lu par aucun contrôle automatique (`rules.py`,
`critic.py`). Une pépite n'en sort vers `LECONS.md` / `hypotheses.json`
que si un essai chez nous et un retour de Milan la confirment.

**Statut de chaque entrée**
- **texte vérifié** : j'ai lu la phrase moi-même dans la source primaire ;
- **lu par agent** : un agent l'a lue dans la source, pas moi ;
- **extrait** : résumé de moteur de recherche, indice seulement ;
- **mesuré chez nous** : j'ai mesuré la chose sur nos fichiers et sur une
  référence dans les mêmes conditions ;
- **essayé** : on l'a réellement appliqué, avec le résultat.

Sources complètes : `corpus/recherche/` (roblox, jugement, anime3d du
2026-09-25), `corpus/tutos/`, `corpus/TUTOS_ANIMATION.md`.

---

## 1. Voir et juger

**1.1 Juger en mouvement, pas sur des images.** *Texte vérifié* (*Illusion
of Life*, sweatbox) : Walt pouvait feuilleter les dessins, « but the only
way he really could tell how they would look was to have the drawings
filmed ». Williams teste en vidéo « at each stage – even the first
scribbles ».
- Chez nous : c'est exactement l'erreur de la v7 (planches figées).
  `outils/regard.py` est notre « pencil test » approché.
- Limite : c'est une approximation de l'œil, pas l'œil de Milan. Mes
  verdicts restent provisoires tant qu'il n'a pas vu la boucle.

**1.2 Le test de silhouette ne se transpose pas tel quel à une caméra de
dos.** *Texte vérifié* + *mesuré chez nous*.
- Disney : sur Mickey noir sur noir, « a hand in front of the chest would
  simply disappear » ; « Work in silhouette ».
- Essai (`outils/vues.py`, `scripts/regard_v7.py`) : en caméra de jeu, au
  contact v7, le bras qui frappe est à 8 % hors du tronc. J'ai d'abord
  cru à un défaut.
- **Mesuré ensuite sur TSB, même caméra** (`scripts/regard_v7_vs_tsb.py`)
  : médiane 15 %, M1 à 1 %. Le bras libre prend 22-53 % de l'image du
  perso chez TSB, 35 % chez nous. **Pas un défaut, c'est la caméra.**
- Ce qui lit un coup de dos : la torsion du corps, la victime, les
  effets. En caméra ciné, notre contact est à 94 % hors du tronc :
  lisible.
- **Leçon de méthode** : avant d'appeler défaut ce qu'un principe
  signale, mesurer la même chose sur la référence, dans la même caméra.

**1.3 Le cadrage fait partie de la pose.** *Texte vérifié* : « If he is
kicking, you do not have the camera in close on a waist shot. »
- Déjà appris chez nous (`pose_pour_sa_camera`, essai obari).
- Tension ouverte :
  - « tricher vers la caméra » (Lango, *extrait* ; GGXrd règle chaque image
    pour sa caméra, *lu par agent*) ;
  - contre « vérifier sous plusieurs angles ».
- Réponse pour Rank Zero : le lanceur voit la caméra ciné (`DragonFist.play`
  prend la caméra). Les autres joueurs voient d'où ils sont. Donc on
  triche pour la ciné, et la pose doit rester lisible de loin et de biais
  pour les spectateurs.

**1.4 « Never make a small change ».** *Texte vérifié* (Ham Luske) : « When
they ask for a change, they're thinking of a big one… otherwise they
wouldn't mention it. »
- Chez nous : « je vois aucun changement » (v7), et des amplitudes ~2x
  trop sages (essais de reproduction).
- Quand Milan demande un changement, le changement proportionné est
  probablement plus grand que ce que je juge suffisant.

**1.5 Pousser jusqu'à « trop », puis revenir.** *Texte vérifié* (Dave
Hand, refusé 6 fois par Walt) : « make it so extreme that you make me
mad ». Même passage : « he seldom asked an animator to tame down an
action if the idea was right ».
- Façon de faire : produire des variantes x1 / x1,5 / x2 / x3 et les
  juger côte à côte dans le cadrage réel. En cas de doute, prendre celle
  qui paraît un peu trop (mon biais connu va vers le sage).
- Limite : Walt refusait aussi la distorsion qui casse la crédibilité.

**1.6 Yeux neufs.** *Extrait*.
- Miroir, lecture à l'envers : `vues.miroir`.
- Le premier regard de Milan est la ressource rare. Ne pas le gaspiller
  sur une version que je n'ai pas moi-même regardée en boucle.

**1.7 Notes au format sweatbox.** *Texte vérifié* (note de Walt à Fred
Moore) : « have Doc jump back (just a little) in a fighting pose,
dropping his fanny and getting a stretch in the legs ».
- Une bonne note dit quelle partie du corps, dans quel sens, à quel
  moment et pour quelle intention. Elle ne dit pas « le principe X n'est
  pas respecté ».
- À appliquer à mes propres critiques.

**1.8 Ce que vaut une source de seconde main (calibré).** *Mesuré chez
nous* (`tutos/gemini_visuel_2026-09-25.md`).
- Description visuelle de Gemini, confrontée à 2 tutos que j'avais étudiés
  image par image :
  - la grande forme est juste ;
  - le bras est faux, la pose du bras avant fausse, les numéros d'image
    inventés ;
  - les TENUES et l'ordre de travail sont manqués.
- Même famille que les [EXTRAIT] des moteurs de recherche.
- Usage : une carte (où regarder, quoi chercher), jamais une pose ou un
  timing sans l'avoir vu soi-même.

**1.9 Les chiffres gardent, l'œil décide.** *Retour de Milan sur la v8
(jeu 7,8, ciné 7,2).*
- Sur la v8, les mesures ont évité des erreurs : fausse alerte du bras
  caché, mauvaise référence pour la bascule, torsion nette prise pour une
  amplitude.
- Elles ont aussi trop piloté le choix final : 13/13 règles, contraste.
- Ce qui a réellement amélioré les poses vient du regard (crochet masqué
  par le bras libre, fente) et des références (firytwig, Wimshurst).
- Ordre de travail :
  1. regarder en mouvement, plusieurs fois, note au format sweatbox (§1.7) ;
  2. décider à l'œil, refs à côté ;
  3. chiffres ensuite, pour vérifier et éviter les pièges.
- Une règle qui échoue est un signal à regarder, pas un veto.

**1.10 La réf TSB : pour départager APRÈS, à l'œil, jamais comme règle.**
*Demande de Milan (2026-09-25).*
- Le fichier officiel TSB (de Milan, non versionné) contient
  13 animations :
  - M1-M4 ;
  - Collateral Ruin (2,1 s), Stoic Bomb (4,7 s), Swift Sweep ;
  - Ultimate1 (10 s), Ultimate2 (2,9 s) ;
  - WallComboPlayer / WallComboVictim.
- Ordre de travail pour une technique :
  1. construire la NÔTRE d'abord (refs de Milan, carnet, jugement), sans
     regarder l'animation TSB équivalente, pour ne pas la recopier ;
  2. puis rendre la nôtre et la TSB la plus proche CÔTE À CÔTE, même rig
     R6, même caméra, synchronisées sur le contact ;
  3. départager à l'œil, pose par pose.
- TSB est une référence, pas un plafond : on peut faire mieux, et « ne
  pas faire comme TSB » n'est pas un défaut en soi. Les mesures sur TSB
  restent des repères situés (§1.2, §2.8), pas des seuils.

**1.11 La mémoire ne sert que si on la rappelle.** *Retour de Milan
(2026-09-25).*
- « Poing chargé puissant » devait me renvoyer au Serious Punch (le GIF
  TSB et « Serious Punch 2 »).
- Le jour même, j'ai relu ces deux GIF sans les reconnaître (« perso cape
  jaune »). Tout était pourtant écrit : notes brutes, étude visuelle,
  fiche v7.
- Cause : mes souvenirs d'une session à l'autre ne sont que les fichiers.
  Rien ne reliait un fichier ou un mot à ce qu'on en savait.
- Réparation :
  - `corpus/CATALOGUE_REFS.md` : fichier -> ce que c'est -> où c'est
    étudié ;
  - `outils/rappel.py "<concept>"` : ce que le cerveau sait déjà.
- Usage : AVANT toute technique ou toute relecture, lancer le rappel sur
  le concept et chercher chaque fichier de ref dans le catalogue.

## 2. Le coup et l'impact

**2.1 Lent contre rapide.** *Texte vérifié* (Williams) : « go just a
little too fast and then switch to going just a little too slow… the
slow against the fast ».
- **Mesuré chez nous** : vitesse du poing à la frappe / vitesse max pendant
  la préparation (`regard_v7_vs_tsb.py`,
  `captures/verification/2026-09-25-contraste-frappe-rafale-v7-vs-tsb.png`).
  - **Rafale v7 : 0,55 à 1,49.** Le poing va aussi vite, ou plus vite, en
    se ré-armant qu'en frappant : l'œil ne sait pas quel mouvement est « le
    coup ».
  - **TSB M1-M4 et Collateral Ruin : 2,3 à 5,7.**
  - Notre coup chargé : 31, grâce à la tenue.
- Limites de la mesure :
  - les M1 TSB sont des clips séparés qui partent du repos, alors que
    notre rafale est un seul clip enchaîné ;
  - en jeu, Roblox fond les M1 entre eux (fondu non mesuré ici).
  - L'écart réel est donc peut-être plus petit. Il reste que, dans notre
    clip, le ré-armement est le mouvement le plus rapide.
- **À essayer** (piste, pas règle) : ré-armer plus lentement (ou le cacher
  dans le recul), frapper en 1-2 images. Juger en regard vitesse réelle
  contre TSB.
- Contre-indication : une rafale « mitraillette » peut vouloir un flux
  continu (TSB Ultimate1 : 0,38). C'est un choix, pas un oubli.
- **Renforcé le 2026-09-25 (soir) par deux tutos lus par Gemini**
  (`tutos/gemini_transcriptions_2026-09-25.md`) :
  - Dong Chang : wind-up qui retient beaucoup d'images, punch en 1 image,
    follow-through lent ;
  - Wimshurst : pré-anticipation 3, anticipation 5, fouet 1, action 1,
    follow-through 4, aftermath 5 images (dessin 2D ; le rapport compte
    plus que les chiffres).
  - Avec Williams et la mesure TSB, ça fait quatre sources indépendantes.
    Reste une piste tant que Milan n'a pas vu d'essai.
- **Cinquième source, relue le 2026-09-25** (ref de Milan : tuto dessiné
  firytwig, texte lu en pleine résolution) : « Keep the inbetweens close to
  the chamber », « Do not ease out » (vers la pose de frappe), « Even 1
  frame of chamber matters ». Et la mesure tient sur les M1 de TSB
  ENCHAÎNÉS : 2,3-3,7 contre 0,55-1,49 chez nous
  (`RELECTURE_REFS_ANIMATION_2026-09-25.md`).

**2.1b Torsion du torse de la rafale : AU NIVEAU de TSB (erreur corrigée).**
*Mesuré chez nous* (`r6_poing_dragon/scripts/tutos_vs_tsb.py`).
- Le 2026-09-25 au soir, j'avais écrit « deux fois moins que TSB ». C'était
  **faux**. J'avais comparé la rotation NETTE (début -> fin de fenêtre) :
  - v7 : 33-68° ;
  - TSB : 84-110°.
- Or notre torse part d'abord en contre-rotation puis revient. En
  AMPLITUDE (max - min), on est au niveau :
  - v7 h1-h4 : 53 / 99 / 98 / 116° (le jab est à 53°, normal pour un jab) ;
  - TSB M1-M4 : 102 / 90 / 111 / 77° ;
  - l'étude visuelle du 2026-09-24 avait déjà mesuré 98-137°.
- Relecture des refs (2026-09-25) : les tutos « pro » de Moon et Blender
  montrent ~180° (le « BACK » face caméra), au-dessus de TSB. C'est un
  registre de démonstration, pas la norme du jeu.
- Leçon de méthode : avant de conclure sur un écart, vérifier qu'on compare
  la même grandeur. Une nette et une amplitude ne se comparent pas.

**2.1c Clés espacées contre cuisson image par image.** *Mesuré chez nous* +
*lu par Gemini*.
- Tutos : Sikasisi 2-4 images, Thundey base de 5, doc7090 Constant puis
  Linear, GGXrd sans interpolation.
- TSB mesuré : écart médian 2-4 images, en Linear.
- **v7 : une clé par image** sur la rafale et le coup chargé, cuites depuis
  l'IK. La fiche v7 prévoyait des clés éparses ; seul un A/B sur le coup
  chargé l'a fait.
- Une cuisson image par image garde les accélérations douces de l'IK
  partout. Des clés espacées en Linear donnent des segments à vitesse
  constante qui cassent net à chaque clé : c'est le « snap » des M1 TSB.
- **À essayer** : rafale en clés espacées (poses fortes seules, 2-5 images
  selon la phase), puis jugée contre TSB.

**2.1d Mener par le corps ou par la tête.** *Lu par Gemini* (Wimshurst,
oral) : mener l'action par le corps donne une impression passionnée, hors de
contrôle ; la mener par la tête donne un contrôle calculé.
- Piste de caractère pour Rank Zero : deux styles de combattant, sans
  changer les poses clés, seulement l'ordre de départ.

**2.2 Contact montré ou contact sauté.** *Texte vérifié*, deux maîtres,
deux gestes opposés au service du même but (un saut que l'œil sent sans
le voir) :
- Ken Harris ajoute UNE image de contact juste avant l'écrasement : « we
  won't see it, but we'll feel it ».
- Babbitt (via Natwick, manuscrit lisible) : on montre la main déjà passée
  au-delà du menton, le menton déjà déplacé, sans image de contact :
  « 10 times the impact ». Les vieux westerns coupaient le contact au
  montage.
- Chez nous : la v7 montre un contact que personne ne voit (flou, puis
  cartes). Deux essais possibles : (a) contact net tenu 2-3 images, puis
  les cartes ; (b) pas de contact, directement le résultat (victime déjà
  pliée) avec le flash.
- On choisit par coup, en variantes jugées en boucle.
- Dong Chang (lu par Gemini) : « le coup doit être ressenti par le
  spectateur, pas vu ». C'est presque mot pour mot Ken Harris.

**2.3 Anticipations invisibles.** *Texte vérifié* (sommaire + manuscrit) :
une ou deux images dans le sens opposé, trop rapides pour être vues, pour
le « snap ».
- Utile en jeu : ça coûte 1 à 3 images de réactivité seulement.
- À essayer sur la rafale, avec 2.1.

**2.4 L'anticipation peut être « corny ».** *Texte vérifié* (Williams) :
« then the great thing is to do something different – a surprise ».
- Même le principe le plus enseigné est un outil qui peut rater.

**2.5 Action et réaction dans le même cadre.** *Lu par agent*
(description Every Frame a Painting, Jackie Chan).
- Juger un coup avec la victime visible, pas l'attaquant seul.
- « Two good hits = one great hit » : le même coup montré deux fois
  (large puis serré), sans raccord exact, se lit comme un coup plus fort.
- Chez nous : c'est une piste pour le coup chargé (plan de jeu, puis gros
  plan).

**2.6 Le follow-through est long ; la lisibilité vit dans la pose
d'après.** *Extrait* (Sakurai « Follow-Throughs Make the Impact », Cooper).
- Rejoint `pose_apres_tenue` (tutos). Même idée par trois chemins.

**2.5b Le silence avant, et entre.** *Vu dans les refs de Milan*
(relecture du 2026-09-25).
- Tenue AVANT de partir :
  - 0,42-0,48 s debout avant un saut (deux jeux de la même famille) ;
  - 1,53 s immobile en caméra de jeu avant l'élan (Stagnant Rage) ;
  - 1,07 s avant la Black Hole.
- Silence ENTRE deux actions qui montent : 0,3 s de pause, puis une action
  plus grosse (aafdc91d).
- À essayer : une pause nette entre la rafale et le coup chargé. Chez nous
  la charge s'enchaîne sans silence ; à mesurer avec `planche_ref.py`
  avant d'y toucher.
- Contre-indication : en jeu, une tenue avant de partir coûte en
  réactivité. Réservée aux techniques qui prennent la main (ultime,
  cinématique).

**2.6b La suite peut être très longue.** *Vu dans les refs.*
- Mannequin : extension tenue et prolongée ~2 s après un coup chargé.
- « First time fighting a dummy » : ~4 s de gros plan sur l'attitude du
  perso après l'action.
- Projection : 0,8 s sur le résultat.
- Le paiement d'un coup peut être le personnage (attitude), pas le coup.

**2.7 Pousser une pose, ce n'est pas tout gonfler.** *Essayé*
(rafale v8, 2026-09-25, `r6_poing_dragon/scripts/dragon_clip.py`, RAFALE).
- Premier essai : amplitude x1,4 appliquée à tout (lacet d'armé, lacet de
  contact, bascule, bassin). Résultat :
  - le bras qui frappe doit traverser devant le corps : l'IK rate le
    contact (0,30 stud) ;
  - le pied avant de la fente n'atteint plus sa place (0,75) ;
  - l'épaule monte.
- Ce qui marche, c'est de pousser **là où les refs montrent l'exagération** :
  - l'ARMÉ (torse enroulé) ;
  - le BRAS LIBRE tiré en arrière au contact (direct, crochet, fente) :
    deux lignes nettes, et il sort de la silhouette du torse ;
  - la BASCULE de la fente seule (racine penchée).
- Le lacet de contact reste à peu près inchangé : c'est lui qui aligne le
  bras sur la cible.

**2.8 Mesurer la réf avant de pousser : la bascule des M1.** *Mesuré chez
nous.*
- Au contact, les M1 de TSB ne penchent vers la cible que de 8/31/17/-14°
  (pack 2-14°). Notre rafale est déjà à 12-16°.
- Le « corps presque à l'horizontale » des tutos (myloe, firytwig) vaut
  pour un coup lourd isolé (Collateral Ruin 23°, fente finale).
- Pencher les coups légers faisait descendre le torse (posture 0,31 > 0,24,
  retour de Milan v1 « accroupi ») et hausser l'épaule.
- Même piège qu'en §2.1b : transposer la mauvaise référence. Un tuto de
  démonstration n'est pas une M1 de jeu.

## 3. La 3D qui imite l'anime

**3.1 Perspective forcée : avancer le bras, pas élargir le FOV.** *Texte
vérifié* (4Gamer, GGXrd) : « If we widened the angle of view… the face in
the back would become too small. Instead, we would extend the arm of the
3D model and bring the hand closer to the camera. »
- **Déjà trouvé en reproduction** (`repro/saitama_obari.py`) : le poing
  géant vient de la perspective (corps qui plonge, bras disloqué vers
  l'objectif), à FOV raisonnable.
- Même conclusion par ASW et par notre essai. Confiance en hausse,
  toujours pas validée par Milan.
- R6 : translation du bloc bras (Motor6D), sans déformation.

- *Lu par Gemini* (SinChi) : obari = bras tiré en arrière, torse bombé en
  avant, poing droit vers la caméra. Même structure que notre prototype.
  L'œil Umakoshi (zoom agressif sur l'œil de celui qui charge) est une
  idée de plan pour la charge.

**3.2 Poings grossis à l'impact.** *Texte vérifié* : « In a punching
action, the fists are slightly enlarged ».
- R6 : seul un bloc entier se scale, et ça touche l'identité « 6 blocs ».
  C'est une décision de Milan, pas la mienne.

**3.3 Tenues irrégulières.** *Texte vérifié* : base 15 i/s en
cinématique, tenues « 2F, 3F, 5F, 1F, 1F, 2F, 2F, 3F, 4F » fixées coup
par coup.
- Rejoint `frappe_lineaire` (TSB : poses clés espacées).
- Idées *extrait* à essayer :
  - cadence par partie du corps (Hobie : veste en 4s, corps en 3s) ;
  - cadence comme caractère (Miles en 2s, Peter en 1s) : un rang faible
    moins fluide qu'un rang fort ?

**3.4 Caméra fluide + perso tenu = saccade (« strobing »).** *Extrait*
(Spider-Verse).
- Rejoint ce que `regard.py` a vu en v7 : wiggle + caméra qui avance =
  jamais une image nette.
- À essayer : caméra immobile pendant une tenue, ou qui avance par pas
  avec la pose.

**3.5 « As long as what you see on the screen is cool, it's OK. »** *Lu
par agent* (slides ASW « Bone Placement Tips »).
- Tester les pivots sur les poses les plus violentes, pas sur l'idle.

**3.6 Pose tenue en déplacement.** *Vu dans les refs* (boxeur 58322fc4).
- Une seconde avec la MÊME silhouette forte (très bas, torse ~45°, gants
  au visage) pendant que le corps fonce.
- La vitesse est lue par les lignes horizontales et la caméra qui suit,
  pas par des membres qui s'agitent. Puis frappe en ~2 images et flash.
- Contraire de notre rafale, où les bras bougent tout le temps. Piste pour
  une ruée vers la cible.

**3.7 De dos, une rafale se lit par ce qui dépasse de la silhouette.** *Vu
dans les refs + mesuré.*
- Gatling vu de dos (a0341700) : corps presque fixe, multiples de poings
  et traînées blanches tout AUTOUR de la silhouette (côtés, dessus).
- Recoupe §1.2 : de dos, le bras qui frappe est caché par le torse chez
  tout le monde. La lecture passe par ce qui dépasse.
- À essayer pour notre rafale en caméra de jeu : effets qui sortent de la
  silhouette (éclats latéraux, multiples), plutôt que chercher à montrer
  le bras.

**3.8 Poser en DIRECTIONS MONDE, puis faire le tour de la pose.** *Appris
en construisant (coup final aérien v9, 2026-09-25).*
- La 1re pose d'armé était un tas : le bras qui « vise » la victime, juste
  EN DESSOUS de lui, pendait comme un bras au repos. Le genou « levé »
  partait en ARRIÈRE : l'axe local du contrôle de jambe ne veut pas dire
  « devant ».
- Réparé en posant chaque membre par une direction monde depuis son pivot
  (épaule, hanche) : genou vers la victime, jambe arrière qui traîne, poing
  armé derrière, bras avant placé. On pose la silhouette qu'on veut voir,
  on ne devine plus les axes.
- Le « tour » à 8 angles (même pose, caméras tout autour) montre en une
  image depuis où la silhouette est ouverte. On choisit la caméra d'APRÈS
  la pose (repro leçon 2), au lieu de tâtonner caméra par caméra.
- Contre-indication : un bras qui vise une cible juste sous lui se confond
  avec le repos. Viser, c'est une direction qui n'est pas celle du repos.

**3.9 Le poing vers l'objectif marche en R6 si la caméra est CHEZ la
victime, à côté d'elle.** *Vérifié à l'écran (v9).*
- Caméra juste au-dessus et à côté du torse de la victime, grand angle
  (78°), visée qui suit le poing et la tête. Le poing grossit jusqu'à
  remplir le cadre, avec la tête derrière, comme la planche OPM.
- Recoupe l'essai obari (repro, leçon 4) et lève le blocage de la v6 (« le
  corps de la victime est toujours entre l'objectif et le poing ») : ce
  n'est vrai que si la caméra est derrière la victime, dans l'axe.
- Ce qui reste moins bien que le Serious Punch : leur gant sombre, dans la
  fumée, est une forme nette. Chez nous, les anneaux dorés du dragon
  encombrent le poing.
- v12 : le bras tendu passait À TRAVERS le plan proche de l'objectif (un
  « prisme » brun plein cadre). Œil plus bas et plus sur le côté.

**3.10 Un bras « levé au ciel » en R6 : mesurer où tombe le HAUT du bras.**
*Vu au tour à 8 caméras puis mesuré (invocation v12).*
- Cible IK à portée (1,55 stud du pivot) : le poing était bien au-dessus
  de l'épaule, mais le bras se couchait EN TRAVERS de la tête (haut du bras
  mesuré au cou). Cible au-delà de la portée (2,4) : le bras se tend, 25°
  vers l'extérieur, au bord de la tête : le « V » de l'affiche.
- Le poing au bon endroit ne dit rien de la silhouette : c'est la boîte
  entière qu'on voit.
- Même piège pour le regard : une cible de regard droit au-dessus de la
  tête la faisait basculer de 90° (cube couché). Regarder devant, menton
  levé.

## 4. Hitstop et caméra

**4.1 Secousse de caméra : rotation, bruit lisse, trauma².** *Texte
vérifié* (slides Eiserloh, GDC 2016) :
- « Camera shake is trauma² or trauma³ » ;
- « Use Perlin noise instead » ;
- en 3D, la secousse en translation est jugée « super lame ».
- **Chez nous** (`player_template.html`, `DragonFist.luau`) : translation
  X/Y + un peu de roulis, bruit blanc tiré à neuf chaque image (60 Hz),
  décroissance exponentielle. Côté Luau, `math.random`, donc non déterministe.
- Ce bruit blanc rend chaque image différente de la précédente : c'est
  exactement ce que `regard.py` compte comme « jamais vu ». Il pourrait
  expliquer une part de « caméra ciné un peu trop abusée » (Milan, v6).
- **À essayer** : variantes rotation seule + bruit lisse contre l'actuel,
  même dose, jugées en regard vitesse réelle. Ne pas changer sans les
  comparer.

**4.2 Le hitstop est un compromis, pas un « plus = mieux ».** *Extrait*.
- SFV : 8 / 12 / 15 images, et Ken à 8 / 10 / 12 (identité « nerveuse »).
- Smash : proportionnel aux dégâts, plafond 30.
- Monster Hunter : trop, puis pas assez, selon le public.
- Sakurai : garder l'attaquant légèrement en mouvement pendant le gel,
  secouer la victime (horizontal au sol, vertical en l'air).
- Chez nous : le gel reste un gel (décision v7). La secousse de la
  victime pendant le gel est à essayer.

**4.3 Sakurai, « Too Much is Just Right ».** *Lu par agent*
(description) : 3D → des éléments se perdent ; caméra reculée → pas
d'impact ; intervalles automatiques → pas de vie. Donc trop = juste.
- Nos trois conditions exactement : R6 3D, caméra de jeu reculée,
  interpolation Linear.

## 4b. VFX (relecture des refs, 2026-09-25)

**4b.1 Le style des refs est graphique (cel), jamais réaliste.** *Vu dans 14
refs.*
- Feu à bords durs cernés de rouge sombre, fumée en boules, éclats acérés,
  étoiles à 4 branches, anneaux en trait fin, croissants effilés, aura à
  pointes.
- Une tache floue de lumière seule ne lit pas « anime ».
- Contre-indication : la fumée qui se dissipe sur la conséquence est douce,
  et c'est voulu (Serious Punch).

**4b.2 2-3 couleurs + blanc par technique.** La palette fait la signature
(Black Flash rouge / noir / blanc, boxeur blanc / rouge / bleu-violet).

**4b.3 L'air vend la vitesse.** Croissants blancs qui tournent, lignes de
pression, vague au sol, spirale autour du membre, tourbillon de fumée.
Presque toutes les refs en ont ; le Poing du Dragon, aucun.

**4b.4 Au tier 1, le blanc net suffit** (449, aafdc91d) : étoile de 2 images,
anneau fin en 3-4 images, petit croissant. Lisible en caméra de jeu, même
tout petit.

**4b.5 Deux registres qui alternent** : VFX dans le monde 3D (caméra de jeu)
et cartes plein écran. Notre Dragon est fort sur les cartes, faible dans le
monde 3D.

**4b.6 Le son (mesuré, pas écouté : ECOUTE_REFS_SFX_2026-09-25.md).** Un
impact des refs = trait vertical large bande, surtout du grave (sub ~0,6 des
300 ms qui suivent). Le gros coup est précédé d'un VIDE (Stagnant Rage :
0,86 s où les aigus tombent de 25 dB). Le son suit l'image de 40 à 150 ms.
Je n'ai pas d'oreille : je règle sur des mesures, et Milan est le seul à
pouvoir dire si ça « sonne ».

**4b.7 Un effet qui LONGE le bras bouche le plan obari** (aura dragon,
2026-09-25). La caméra obari est chez la victime, dans l'axe du poing : tête,
cou ou corps qui suivent le bras passent entre l'objectif et l'attaquant.
Dans ce plan, l'effet doit se retirer (rentrer dans le poing) et revenir
APRÈS, dans un plan qui le montre (la révélation). C'est d'ailleurs ce que
fait le film : le dragon sort de l'impact, pas du bras qui frappe.

**4b.8 Une carte peinte doit toujours faire face à la caméra** : orientée
dans l'axe de ce qu'elle suit, elle disparaît dès qu'on la regarde par la
tranche. Face caméra, et l'image tournée selon l'axe projeté à l'écran.

**4b.9 Un détail de texture n'existe qu'à la distance de la caméra**
(dragon v12). 70 x 16 écailles de 0,2 stud tracées en 5 px : à 8 studs,
le corps se lisait comme un tube jaune uni, « du plastique ». Écailles de
~0,5 stud peintes en volume (bord libre foncé, reflet) : elles se lisent.
Et un métal très brillant sans environnement à refléter devient une
couleur plate.

**4b.10 Un modèle 3D nu se lit comme une statue** (dragon v12). Les refs
(7a2b4ae8) montrent le dragon ENVELOPPÉ d'énergie : il sort d'un tourbillon
de feu et en reste nimbé. Le modèle apporte le volume ; le feu qui coule le
long du corps (et traîne derrière quand il bouge) apporte la vie. Fait en
DONNÉE (émetteurs sur des chemins = points du corps) : aucun code moteur.

**4b.11 Une tête qui pique vers sa cible se lit comme un crâne** (armé v12).
Visée droit sur la victime, qui est EN BAS, la tête du dragon montrait son
dessus et sa crinière. De profil, horizontale, devant et au-dessus du poing :
la gueule ouverte se lit (l'affiche e92ac0d7). Et le perso reste DEVANT le
dragon : les spires qui passaient devant le visage cachaient le héros.

**4b.12 Une planche d'images fixes cache la DURÉE** (v12, Milan : « le
dragon apparaît 0,5 seconde »). Mes planches montraient un beau dragon ; en
temps réel il vivait 0,57 s. Le GIF de Goku tient l'invocation 2 s. Un
effet-signature se juge en vidéo à vitesse réelle, et sa durée se mesure
contre la ref.

## 5. Pistes à essayer (classées, aucune n'est décidée)

1. **Rafale : ré-armement lent, frappe rapide, clés espacées** (2.1,
   2.1c, 2.3). Quatre sources, plus le contraste mesuré contre TSB : même
   avec les M1 enchaînés, 2,3-3,7 chez TSB contre 0,55-1,49 chez nous. La
   torsion est hors de cause (2.1b corrigé). Mesures prêtes : `regard_v7_vs_tsb.py`, `tutos_vs_tsb.py`.
2. **Contact du coup chargé vu avant les cartes, ou sauté** (2.2). Deux
   variantes en boucle.
3. **Secousse rotation + bruit lisse** (4.1). A/B, même dose.
4. **Caméra immobile pendant les tenues** (3.4).
4b. **Silence avant le coup chargé** (2.5b) et **formes hors silhouette
   pour la rafale de dos** (3.7).
5. **Victime secouée pendant le gel** (4.2).
6. **Aérien Saitama/obari** : perspective forcée (3.1), déjà prototypée,
   à porter dans le rig V2.22.

Méthode pour chacune :
- deux ou trois variantes, dont une « trop » (1.5) ;
- regard vitesse réelle + vues de jugement ;
- comparaison à la référence dans la même caméra (1.2) ;
- note au format sweatbox (1.7) ;
- Milan tranche.

## 6. Mes biais connus (à relire avant de juger)

- **Je note mes VFX contre mes versions précédentes, pas contre le pack**
  (v10 : prédit 6, v11 : prédit 7 ; Milan : 4). Avant de noter, poser la
  capture À CÔTÉ d'une ref du pack ou d'une ref visuelle, même échelle.
- **« Mélange X à Y »** : demander de quoi (pose ? effet ? couleur ?) si ce
  n'est pas dit ; ici c'était la POSE d'Izuku, pas ses éclairs.

- Je juge sur des images figées et agrandies (1.1).
- Mes poses sont ~2x trop sages (1.4, 1.5).
- J'applique un principe comme une règle et j'appelle défaut ce qui ne
  l'est pas chez les pros (1.2, fausse alerte du 2026-09-25).
- Je cherche dans une source ce qui confirme mon plan (retour de Milan
  sur l'étude des tutos, 2026-09-25).
- Je fais confiance aux noms de mes contrôles (« genou devant ») sans
  regarder la pose de tous les côtés (3.8, v9).
- **J'anime le membre qui porte le coup et je fige le corps** (récurrent :
  « il manque les épaules » sur r6_directional_punch, « que les bras » sur
  la v9). Je conçois des poses, puis je les relie par des translations
  rigides. Garde-fou : `outils/corps_bras.py` sur chaque production, et la
  pelure d'oignon du TORSE (pas seulement du poing) avant de montrer.
- Je traduis les mots de Milan en ma propre étiquette et je perds son sens :
  pour lui, « coup final » = le coup aérien depuis la v7 ; j'avais mélangé
  avec la charge au sol (fiche COUP_CHARGE §4).
