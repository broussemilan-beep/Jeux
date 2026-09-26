# Lint du cerveau : rapport du 2026-09-26

> **Consultatif.** Produit par `outils/lint_cerveau.py` (brique A7 du plan de réorganisation,
> §2.4 point 10). Rien n'est bloqué : chaque ligne est une question à relire, pas une faute.
> Heuristiques : il y a des faux positifs (un « toujours » qui veut dire « encore », un § d'un
> autre document). Relancer : `python3 outils/lint_cerveau.py --md <sortie.md>`.

Fichiers lus : `experiments/_shared/animator_brain/corpus/CARNET.md`, `experiments/_shared/animator_brain/corpus/fiches/AURA_DRAGON.md`, `experiments/_shared/animator_brain/corpus/fiches/COUP_CHARGE.md`, `experiments/_shared/animator_brain/corpus/fiches/PLEIN_ECRAN.md`, `experiments/_shared/animator_brain/corpus/fiches/POING_DU_DRAGON_V13.md`, `experiments/_shared/animator_brain/corpus/fiches/UN_SEUL_COUP.md`, `experiments/_shared/animator_brain/corpus/fiches/VFX.md`, `experiments/_shared/animator_brain/corpus/CATALOGUE_REFS.md`, `experiments/_shared/animator_brain/ETAT.md`, `experiments/_shared/animator_brain/NOYAU.md`.

Messages de Milan lus (`corpus/milan_verbatim.jsonl`) : 210. Citations attribuées à Milan vues : 43, retrouvées mot pour mot (casse et ponctuation près) : 8. Entrées vues : 117. Chemins vus : 248. Renvois vus : 58. Phrases en absolu vues : 49. Annonces de garde-fou vues : 5.

## Compte par type

| type | nb | ce que ça veut dire |
|---|---:|---|
| `entree_sans_statut` | 54 | entrées sans statut (mesuré / lu / vu / essayé / retour de Milan / CONTREDIT) |
| `citation_milan_introuvable` | 35 | citations attribuées à Milan introuvables mot pour mot dans milan_verbatim.jsonl |
| `chemin_introuvable` | 0 | chemins cités qui n'existent pas dans le dépôt |
| `ligne_hors_fichier` | 0 | renvois fichier:ligne au-delà de la fin du fichier |
| `renvoi_introuvable` | 3 | renvois § dont la section n'existe pas |
| `renvoi_ambigu` | 15 | § nus absents du fichier courant, présents ailleurs (préciser le fichier) |
| `absolu_sans_source` | 22 | phrases en « jamais / toujours / doit / il faut » sans source dans la phrase |
| `garde_fou_introuvable` | 3 | garde-fous / contrôles annoncés absents du code cité |
| `garde_fou_non_verifiable` | 2 | garde-fous annoncés sans rien de vérifiable |

Parmi les citations introuvables, 12 sont très proches d'un vrai message (≥ 85 % des caractères) : probablement ses mots avec l'orthographe corrigée. Les autres sont des reformulations, des messages d'avant la moisson (projets précédents), ou des mots jamais écrits.

## entree_sans_statut (54)

- experiments/_shared/animator_brain/corpus/CARNET.md:321 [2.9] aucun marqueur -- **2.9 « Il frappe vers le bas » : c'est la HAUTEUR DU POING AU CONTACT et
- experiments/_shared/animator_brain/corpus/CARNET.md:505 [4b.2] marqueur hors des statuts : « Black Flash rouge / noir / blanc, boxeur blanc / rouge / bleu-violet » -- **4b.2 2-3 couleurs + blanc par technique.** La palette fait la signature
- experiments/_shared/animator_brain/corpus/CARNET.md:508 [4b.3] aucun marqueur -- **4b.3 L'air vend la vitesse.** Croissants blancs qui tournent, lignes de
- experiments/_shared/animator_brain/corpus/CARNET.md:512 [4b.4] marqueur hors des statuts : « 449, aafdc91d » -- **4b.4 Au tier 1, le blanc net suffit** (449, aafdc91d) : étoile de 2 images,
- experiments/_shared/animator_brain/corpus/CARNET.md:516 [4b.5] marqueur hors des statuts : « caméra de jeu » -- **4b.5 Deux registres qui alternent** : VFX dans le monde 3D (caméra de jeu)
- experiments/_shared/animator_brain/corpus/CARNET.md:527 [4b.7] marqueur hors des statuts : « aura dragon, 2026-09-25 » -- **4b.7 Un effet qui LONGE le bras bouche le plan obari** (aura dragon,
- experiments/_shared/animator_brain/corpus/CARNET.md:534 [4b.8] aucun marqueur -- **4b.8 Une carte peinte doit toujours faire face à la caméra** : orientée
- experiments/_shared/animator_brain/corpus/CARNET.md:538 [4b.9] marqueur hors des statuts : « dragon v12 » -- **4b.9 Un détail de texture n'existe qu'à la distance de la caméra**
- experiments/_shared/animator_brain/corpus/CARNET.md:545 [4b.10] marqueur hors des statuts : « dragon v12 \| 7a2b4ae8 » -- **4b.10 Un modèle 3D nu se lit comme une statue** (dragon v12). Les refs
- experiments/_shared/animator_brain/corpus/CARNET.md:551 [4b.11] marqueur hors des statuts : « armé v12 » -- **4b.11 Une tête qui pique vers sa cible se lit comme un crâne** (armé v12).
- experiments/_shared/animator_brain/corpus/CARNET.md:579 [4b.14] marqueur hors des statuts : « audit du raisonnement, 2026-09-25 » -- **4b.14 Compter les couches n'est pas juger** (audit du raisonnement,
- experiments/_shared/animator_brain/corpus/CARNET.md:598 [4b.16] marqueur hors des statuts : « 9 refs de dragons \| Dragon Ball Rage \| Suiryu » -- **4b.16 L'accent complémentaire dans les yeux** (9 refs de dragons). Or →
- experiments/_shared/animator_brain/corpus/CARNET.md:613 [4b.18] marqueur hors des statuts : « « Last Breath » v1-v3, animations abandonnées de TSB » -- **4b.18 Le dragon de TSB, c'est notre idée, exécutée autrement** (« Last
- experiments/_shared/animator_brain/corpus/CARNET.md:621 [4b.19] marqueur hors des statuts : « 5 effets stylisés » -- **4b.19 Du NOIR dans l'effet, et des pointes, pas des taches** (5 effets
- experiments/_shared/animator_brain/corpus/CARNET.md:629 [4b.20] aucun marqueur -- **4b.20 Un VFX « dessiné » passe par un MESH : forme simple + dessin peint
- experiments/_shared/animator_brain/corpus/CARNET.md:647 [4b.21] aucun marqueur -- **4b.21 La morsure se raconte en deux fois, et ce qui DURE, c'est l'avant
- experiments/_shared/animator_brain/corpus/CARNET.md:670 [4b.24] marqueur hors des statuts : « v13 » -- **4b.24 « Pas cartoon » : les boules de feu cel à contour sont ce qui
- experiments/_shared/animator_brain/corpus/CARNET.md:684 [4b.25] marqueur hors des statuts : « `outils/juge.py`, refs `clips/juge_refs_ultimes.json` » -- **4b.25 Juger les PROPORTIONS DE TEMPS contre des refs mesurées pareil**
- experiments/_shared/animator_brain/corpus/CARNET.md:693 [4b.26] aucun marqueur -- **4b.26 Relire SA scène comme un spectateur, plan par plan, sans Milan**
- experiments/_shared/animator_brain/corpus/CARNET.md:727 [4b.28] marqueur hors des statuts : « v13, « le dragon n'apparaît pas là où il faut, et très peu » » -- **4b.28 Vérifier dans les conditions du spectateur, pas les miennes**
- experiments/_shared/animator_brain/corpus/CARNET.md:736 [4b.29] aucun marqueur -- **4b.29 Roblox premium : le dragon en 3D plutôt que des planches 2D**
- experiments/_shared/animator_brain/corpus/CARNET.md:763 [4b.32] marqueur hors des statuts : « même scène » -- **4b.32 Un événement ne se lit que s'il arrive PENDANT le plan qui le
- experiments/_shared/animator_brain/corpus/fiches/AURA_DRAGON.md:74 [0 ter. Après la v12 (VFX 2-4/10) : la ref TSB de Suiryu] marqueur hors des statuts : « VFX 2-4/10 » -- ## 0 ter. Après la v12 (VFX 2-4/10) : la ref TSB de Suiryu
- experiments/_shared/animator_brain/corpus/fiches/AURA_DRAGON.md:93 [0 quater. v13 : Milan tranche (or, invoqué dans les airs, il] marqueur hors des statuts : « or, invoqué dans les airs, il MANGE » -- ## 0 quater. v13 : Milan tranche (or, invoqué dans les airs, il MANGE)
- experiments/_shared/animator_brain/corpus/fiches/AURA_DRAGON.md:112 [2. Le dragon raconte trois temps (calqués sur nos actes v9)] marqueur hors des statuts : « calqués sur nos actes v9 » -- ## 2. Le dragon raconte trois temps (calqués sur nos actes v9)
- experiments/_shared/animator_brain/corpus/fiches/AURA_DRAGON.md:126 [3. Comment le faire dans Roblox (et donc dans l'aperçu)] marqueur hors des statuts : « et donc dans l'aperçu » -- ## 3. Comment le faire dans Roblox (et donc dans l'aperçu)
- experiments/_shared/animator_brain/corpus/fiches/AURA_DRAGON.md:145 [4. Pièges connus] aucun marqueur -- ## 4. Pièges connus
- experiments/_shared/animator_brain/corpus/fiches/COUP_CHARGE.md:46 [2. La référence : le Serious Punch (TSB), revu image par ima] marqueur hors des statuts : « TSB » -- ## 2. La référence : le Serious Punch (TSB), revu image par image
- experiments/_shared/animator_brain/corpus/fiches/COUP_CHARGE.md:82 [3. Ce que disent les autres sources (relues pour cette fiche] marqueur hors des statuts : « relues pour cette fiche » -- ## 3. Ce que disent les autres sources (relues pour cette fiche)
- experiments/_shared/animator_brain/corpus/fiches/COUP_CHARGE.md:140 [4. Ce qu'on a déjà essayé, et pourquoi ça n'a pas marché] aucun marqueur -- ## 4. Ce qu'on a déjà essayé, et pourquoi ça n'a pas marché
- experiments/_shared/animator_brain/corpus/fiches/COUP_CHARGE.md:172 [5. Ce que ça suggère pour la prochaine version (pistes, pas ] marqueur hors des statuts : « pistes, pas règles » -- ## 5. Ce que ça suggère pour la prochaine version (pistes, pas règles)
- experiments/_shared/animator_brain/corpus/fiches/COUP_CHARGE.md:192 [6. Sources consultées pour cette fiche] aucun marqueur -- ## 6. Sources consultées pour cette fiche
- experiments/_shared/animator_brain/corpus/fiches/COUP_CHARGE.md:203 [7. Reprise du coup final aérien (après la v9 : 7,7, « que le] marqueur hors des statuts : « après la v9 : 7,7, « que les bras » » -- ## 7. Reprise du coup final aérien (après la v9 : 7,7, « que les bras »)
- experiments/_shared/animator_brain/corpus/fiches/PLEIN_ECRAN.md:30 [2. Les trois planches] aucun marqueur -- ## 2. Les trois planches
- experiments/_shared/animator_brain/corpus/fiches/PLEIN_ECRAN.md:51 [3. Pièges] aucun marqueur -- ## 3. Pièges
- experiments/_shared/animator_brain/corpus/fiches/POING_DU_DRAGON_V13.md:33 [2. La scène v13, en secondes (60 i/s)] marqueur hors des statuts : « 60 i/s » -- ## 2. La scène v13, en secondes (60 i/s)
- experiments/_shared/animator_brain/corpus/fiches/POING_DU_DRAGON_V13.md:57 [3. Le dragon (acte 5 à 10)] marqueur hors des statuts : « acte 5 à 10 » -- ## 3. Le dragon (acte 5 à 10)
- experiments/_shared/animator_brain/corpus/fiches/POING_DU_DRAGON_V13.md:75 [4. Caméra (plans)] marqueur hors des statuts : « plans » -- ## 4. Caméra (plans)
- experiments/_shared/animator_brain/corpus/fiches/POING_DU_DRAGON_V13.md:89 [5. VFX (tous « dessinés » : mesh + texture peinte à bord net] marqueur hors des statuts : « tous « dessinés » : mesh + texture peinte à bord net + en 2 » -- ## 5. VFX (tous « dessinés » : mesh + texture peinte à bord net + en 2)
- experiments/_shared/animator_brain/corpus/fiches/POING_DU_DRAGON_V13.md:105 [6. Son] aucun marqueur -- ## 6. Son
- experiments/_shared/animator_brain/corpus/fiches/POING_DU_DRAGON_V13.md:112 [7. Jugement avant de montrer (porte)] marqueur hors des statuts : « porte » -- ## 7. Jugement avant de montrer (porte)
- experiments/_shared/animator_brain/corpus/fiches/POING_DU_DRAGON_V13.md:121 [8. Pièges connus (hérités)] marqueur hors des statuts : « hérités » -- ## 8. Pièges connus (hérités)
- experiments/_shared/animator_brain/corpus/fiches/POING_DU_DRAGON_V13.md:129 [9. Ce qui a été fait (tel que construit, 2026-09-25)] marqueur hors des statuts : « tel que construit, 2026-09-25 » -- ## 9. Ce qui a été fait (tel que construit, 2026-09-25)
- experiments/_shared/animator_brain/corpus/fiches/UN_SEUL_COUP.md:21 [1. Ce que les trois refs font, à 0,1 s] aucun marqueur -- ## 1. Ce que les trois refs font, à 0,1 s
- experiments/_shared/animator_brain/corpus/fiches/UN_SEUL_COUP.md:60 [3. La scène (60 i/s, ~12,5 s)] marqueur hors des statuts : « 60 i/s, ~12,5 s » -- ## 3. La scène (60 i/s, ~12,5 s)
- experiments/_shared/animator_brain/corpus/fiches/UN_SEUL_COUP.md:87 [4. Pièges (d'après nos propres erreurs)] marqueur hors des statuts : « d'après nos propres erreurs » -- ## 4. Pièges (d'après nos propres erreurs)
- experiments/_shared/animator_brain/corpus/fiches/UN_SEUL_COUP.md:102 [5. Livré (2026-09-26) et prédiction] marqueur hors des statuts : « 2026-09-26 » -- ## 5. Livré (2026-09-26) et prédiction
- experiments/_shared/animator_brain/corpus/fiches/VFX.md:17 [1. Ce que Milan a validé, et ce qui est resté théorique] aucun marqueur -- ## 1. Ce que Milan a validé, et ce qui est resté théorique
- experiments/_shared/animator_brain/corpus/fiches/VFX.md:41 [2. Ce qu'un VFX de combat pro contient (sources croisées)] marqueur hors des statuts : « sources croisées » -- ## 2. Ce qu'un VFX de combat pro contient (sources croisées)
- experiments/_shared/animator_brain/corpus/fiches/VFX.md:72 [3. Les contraintes Roblox (doc officielle, lue hors ligne)] marqueur hors des statuts : « doc officielle, lue hors ligne » -- ## 3. Les contraintes Roblox (doc officielle, lue hors ligne)
- experiments/_shared/animator_brain/corpus/fiches/VFX.md:109 [4. Ce que les pistes nous donnent (verdicts, détails dans `r] marqueur hors des statuts : « verdicts, détails dans `recherche/` » -- ## 4. Ce que les pistes nous donnent (verdicts, détails dans `recherche/`)
- experiments/_shared/animator_brain/corpus/fiches/VFX.md:130 [5. Le studio VFX qu'on assemble (proposition)] marqueur hors des statuts : « proposition » -- ## 5. Le studio VFX qu'on assemble (proposition)
- experiments/_shared/animator_brain/corpus/fiches/VFX.md:168 [6. Décisions qui reviennent à Milan] aucun marqueur -- ## 6. Décisions qui reviennent à Milan
- experiments/_shared/animator_brain/corpus/fiches/VFX.md:183 [7. Contradictions à trancher (relevées par l'inventaire)] marqueur hors des statuts : « relevées par l'inventaire » -- ## 7. Contradictions à trancher (relevées par l'inventaire)

## citation_milan_introuvable (35)

- experiments/_shared/animator_brain/corpus/CARNET.md:3 « rajoute encore plus de tutos, le but apprendre et nourrir, pas forcément combler des trous… des tricks, des pépites utiles, mais ça doit pas devenir des règles, mais de l'apprentissage ; le but c'est qu'on soit hyper fort, polyvalent. »
  - au plus près (71 % des mots dans l'ordre, 72 % des caractères ; 2026-09-25T07:45, 18c384378ac6f629) : 'rajoute encor plus de tuto le but apprebdre et nourrir pas forcement combler de trou on esr largement perfectible, le temps travail sur tes taches regarde si on'
- experiments/_shared/animator_brain/corpus/CARNET.md:345 « tu ne captes pas le truc du poing chargé »
  - au plus près (60 % des mots dans l'ordre, 55 % des caractères ; 2026-09-25T11:19, f8f8ab19c4da26bc) : 'Pause juste que es que notre cerveau a une bonne mémoire et a bien tout les outils et es que tu les a ausis ? Parce que je suis étonné que tu t’en souvienne pas'
- experiments/_shared/animator_brain/corpus/CARNET.md:630 « on dirait c'est dessiné, sûrement parce que ça passe par des meshes 3D »
  - au plus près (60 % des mots dans l'ordre, 72 % des caractères ; 2026-09-25T17:51, 38aeca1ca0d89e42) : 'Un trukc pour toi pour les VFX qui complète les animation c que c limite on ditzit et sûrement parce que ça passe par des mesh 3d on ditzit c dessiné'
- experiments/_shared/animator_brain/corpus/CARNET.md:678 « les yeux cassent le truc, trop cubique »
  - au plus près (50 % des mots dans l'ordre, 56 % des caractères ; 2026-09-25T19:00, 8c8ba8639e4bd8f8) : 'Je me permet tes yeux du dragon sont ausis se qui casse le truck ça fais moche\nEt c trop cubique aussi pas assez travaillée'
- experiments/_shared/animator_brain/corpus/CARNET.md:694 « revois, il y a des problèmes, je veux voir si tu vois sans moi »
  - au plus près (88 % des mots dans l'ordre, 96 % des caractères : TRÈS PROCHE, orthographe corrigée ? ; 2026-09-25T19:43, 8039fba726647634) : 'Revoit y’a des problèmes je veux voir si tu vois sans moi'
- experiments/_shared/animator_brain/corpus/CARNET.md:733 « je ne vois pas X »
  - au plus près (100 % des mots dans l'ordre, 67 % des caractères ; 2026-09-24T17:24, 6d3aecf97fca9bb8) : 'C tjrs pas bon je met 6,8 je vois pas trop de dif avec la v4 . Es que le scrappeur a permis de nourrir le cerveau ?'
- experiments/_shared/animator_brain/corpus/CARNET.md:737 « ça ne rend pas bien pour du Roblox premium »
  - au plus près (83 % des mots dans l'ordre, 85 % des caractères : TRÈS PROCHE, orthographe corrigée ? ; 2026-09-25T21:08, 3af5d420beeaf8cf) : 'Bon. Finalement tu peux retiré les 3 planches je trouve que ça rends pas bien pour du Roblox premium , ensuite je ne voit tjrs pas le dragon comme il faut'
- experiments/_shared/animator_brain/corpus/CARNET.md:744 « le dragon va dans tous les sens hyper rapidement »
  - au plus près (71 % des mots dans l'ordre, 90 % des caractères : TRÈS PROCHE, orthographe corrigée ? ; 2026-09-25T22:21, db8847d8b763e660) : 'Okk j’ai vue je te met un totale de 7,85 une bette avance , je donne pas 8 car y’a quelque bug , il manque un polishage certain et un vrai cap pour passé au pre'
- experiments/_shared/animator_brain/corpus/fiches/AURA_DRAGON.md:3 « l'aura du poing du dragon en forme de dragon, je t'enverrai la ref »
  - au plus près (43 % des mots dans l'ordre, 48 % des caractères ; 2026-09-25T18:04, e0e789cab95b15bb) : 'Le dragon or le dragon est invoquer dans les air comme goku puis le coup se transforme en le dragon qui mange le perso , et es que tu as bien analysé tout ? Mêm'
- experiments/_shared/animator_brain/corpus/fiches/COUP_CHARGE.md:4 « le cerveau se nourrit, mais à 30 %, et toi aussi »
  - au plus près (60 % des mots dans l'ordre, 48 % des caractères ; 2026-09-24T15:15, dd807cffecb62e5b) : 'je met 6,7 juste le bras ne part pluq d’en bas mais ne change pas la note , sur tout que au coup final le coup par tjrs d’en bas . oyi stop regler petit a petit'
- experiments/_shared/animator_brain/corpus/fiches/COUP_CHARGE.md:27 « le perso est censé charger son poing »
  - au plus près (83 % des mots dans l'ordre, 97 % des caractères : TRÈS PROCHE, orthographe corrigée ? ; 2026-09-03T14:32, c0fd5c928592a114) : 'C bcp trop rapide on ne lit pas assez les mouvement y’a pas de logique le perso est censé charge son poing'
- experiments/_shared/animator_brain/corpus/fiches/COUP_CHARGE.md:27 « il charge son poing à son arrière droit »
  - au plus près (100 % des mots dans l'ordre, 95 % des caractères : TRÈS PROCHE, orthographe corrigée ? ; 2026-09-03T17:19, f5748501ebb4b1b8) : 'Regarde l’image 1 le perso charge son poing à son arrière droit'
- experiments/_shared/animator_brain/corpus/fiches/COUP_CHARGE.md:27 « tourner son buste vers la droite pour charger son poing droit, plier les jambes légèrement, le 2e bras placé, et boum il envoie »
  - au plus près (67 % des mots dans l'ordre, 89 % des caractères : TRÈS PROCHE, orthographe corrigée ? ; 2026-09-03T19:13, caeb61cda775f344) : 'Tu oublies de utiles les jambes le peros est cense tourné son buste vers la droit charger sont moins droit plier les jambes le légèrement le 2e bras placé et bo'
- experiments/_shared/animator_brain/corpus/fiches/COUP_CHARGE.md:27 « il manque les épaules, on dirait que le coup part du bas alors qu'il doit aller droit »
  - au plus près (83 % des mots dans l'ordre, 97 % des caractères : TRÈS PROCHE, orthographe corrigée ? ; 2026-09-03T20:19, 314842a7f2bc32c2) : 'Il manque les épaules on dirait que le coup pars du bas alors que il doit allez droit'
- experiments/_shared/animator_brain/corpus/fiches/COUP_CHARGE.md:27 « tu n'as pas réussi à donner le sentiment d'un coup de poing… une espèce d'élancement du bras »
  - au plus près (90 % des mots dans l'ordre, 69 % des caractères ; 2026-09-04T19:34, 04d685580df4a5c2) : 'Enft pour le combat mal grès tout ce que tu as tenté tu n’a pas réussi a donné le sentiment d’un coup poing et encore moins le rendu et encore moins comme je l’'
- experiments/_shared/animator_brain/corpus/fiches/COUP_CHARGE.md:28 « le coup final : enchaînement d'uppercuts et coup droit »
  - au plus près (83 % des mots dans l'ordre, 74 % des caractères ; 2026-09-24T14:24, 4296e0e2d6e21e17) : 'tjrs pas bon en gros les coup parte tjrs du bas , pareil pojr le grans coup final on dirait un enchainement d’uppercute mais en meme temps coup droit , etudie c'
- experiments/_shared/animator_brain/corpus/fiches/COUP_CHARGE.md:29 « au coup final le coup part toujours d'en bas ; je verrais plus le coup de Saitama, **un coup qui se charge avec le buste qui tourne** »
  - au plus près (76 % des mots dans l'ordre, 67 % des caractères ; 2026-09-24T15:15, dd807cffecb62e5b) : 'je met 6,7 juste le bras ne part pluq d’en bas mais ne change pas la note , sur tout que au coup final le coup par tjrs d’en bas . oyi stop regler petit a petit'
- experiments/_shared/animator_brain/corpus/fiches/COUP_CHARGE.md:30 « c'est toujours pas bon ; je vois pas trop de différence avec la v4 »
  - au plus près (67 % des mots dans l'ordre, 71 % des caractères ; 2026-09-24T17:24, 6d3aecf97fca9bb8) : 'C tjrs pas bon je met 6,8 je vois pas trop de dif avec la v4 . Es que le scrappeur a permis de nourrir le cerveau ?'
- experiments/_shared/animator_brain/corpus/fiches/COUP_CHARGE.md:31 « l'animation reste le bémol : il manque un cap par rapport à ce que je veux et nos refs »
  - au plus près (82 % des mots dans l'ordre, 82 % des caractères ; 2026-09-24T20:01, 02a79cfd2ea5f715) : 'Je te met 7 je te trouve que ça rends assez bien ne caméra jeux , en cinéma peut être un peu trop abusé mais léger , Aprs l’animation reste tjrs le bémols il ma'
- experiments/_shared/animator_brain/corpus/fiches/COUP_CHARGE.md:32 « je vois aucun changement… trop simple… nos refs, c'est plus exagéré et un placement différent »
  - au plus près (75 % des mots dans l'ordre, 62 % des caractères ; 2026-09-25T06:22, 356a3960c1c3eb0e) : 'Je vois aucun changement je t’avoue , 3 choses enft l’animation est tjrs pas bonne à mon goût c’est trop simple fin revoi les animations de no ref dnas la lectu'
- experiments/_shared/animator_brain/corpus/fiches/COUP_CHARGE.md:33 « c'est vraiment le coup chargé de Saitama »
  - au plus près (80 % des mots dans l'ordre, 85 % des caractères : TRÈS PROCHE, orthographe corrigée ? ; 2026-09-25T06:22, 356a3960c1c3eb0e) : 'Je vois aucun changement je t’avoue , 3 choses enft l’animation est tjrs pas bonne à mon goût c’est trop simple fin revoi les animations de no ref dnas la lectu'
- experiments/_shared/animator_brain/corpus/fiches/COUP_CHARGE.md:34 « le coup final, toujours pas bon, normal : pas encore travaillé »
  - au plus près (78 % des mots dans l'ordre, 68 % des caractères ; 2026-09-25T11:04, 9dee96b94f1c4166) : 'En caméra jeux je te met 7,8 apart sur le coup final en gros et en cinéma 7,2 y’a pas de gros changement et c tjrs pas bon le coup final ce qui est normal car p'
- experiments/_shared/animator_brain/corpus/fiches/COUP_CHARGE.md:35 « poing chargé puissant doit faire écho au Serious Punch de Saitama, le GIF et l'anime TSB »
  - au plus près (67 % des mots dans l'ordre, 66 % des caractères ; 2026-09-25T11:19, f8f8ab19c4da26bc) : 'Pause juste que es que notre cerveau a une bonne mémoire et a bien tout les outils et es que tu les a ausis ? Parce que je suis étonné que tu t’en souvienne pas'
- experiments/_shared/animator_brain/corpus/fiches/PLEIN_ECRAN.md:17 « le tourbillon et le rouge : trop PEINTURE, pas dessiné »
  - au plus près (67 % des mots dans l'ordre, 65 % des caractères ; 2026-09-25T20:24, cf95f861682b091b) : 'Juste je n’aime pas ces 2 plans je les trouve trop peinture , et pas dessiné donc pas obligé de les remplacer apart si tu peux faire mieux et le 3e plan je trou'
- experiments/_shared/animator_brain/corpus/fiches/PLEIN_ECRAN.md:17 « le soleil : j'aime l'idée, bonne créativité, mais tu peux faire beaucoup mieux »
  - au plus près (40 % des mots dans l'ordre, 46 % des caractères ; 2026-09-25T15:39, 844f1c953f622056) : 'Non en gros je voulais pas que ça se mélange au éclairé de izuku mais que la pose reste celle que on a vue de izuku mélangé à celle de goku envoyé avant , que t'
- experiments/_shared/animator_brain/corpus/fiches/POING_DU_DRAGON_V13.md:3 « Le dragon or, le dragon est invoqué dans les airs comme Goku, puis le coup se transforme en le dragon qui mange le perso. […] Je veux que tu refasses tout, je veux la scène complète niveau 8,5/10 globale : animation à revoir, plus smooth, p »
  - au plus près (91 % des mots dans l'ordre, 89 % des caractères : TRÈS PROCHE, orthographe corrigée ? ; 2026-09-25T18:04, e0e789cab95b15bb) : 'Le dragon or le dragon est invoquer dans les air comme goku puis le coup se transforme en le dragon qui mange le perso , et es que tu as bien analysé tout ? Mêm'
- experiments/_shared/animator_brain/corpus/fiches/POING_DU_DRAGON_V13.md:157 « le dragon n'apparaît pas là où il faut, et très peu »
  - au plus près (100 % des mots dans l'ordre, 96 % des caractères : TRÈS PROCHE, orthographe corrigée ? ; 2026-09-25T21:10, e17c91a8d7c54913) : 'Non tu n’a pas compris ne gros dans la scène que tu as créé y’a un problème avec le dragon il n’apparaît pas là où il faut et très peu'
- experiments/_shared/animator_brain/corpus/fiches/POING_DU_DRAGON_V13.md:164 « dans tous les sens »
  - au plus près (50 % des mots dans l'ordre, 55 % des caractères ; 2026-09-04T12:16, 6a290307e030f1a5) : "Dans Roblox (rigs R6 ou R15), les animateurs étirent les articulations au-delà de l'anatomie normale sur la frame d'impact pour donner de la force visuelle (une"
- experiments/_shared/animator_brain/corpus/fiches/VFX.md:4 « notre propre studio de VFX qui viendra combler l'animation »
  - au plus près (100 % des mots dans l'ordre, 97 % des caractères : TRÈS PROCHE, orthographe corrigée ? ; 2026-09-25T13:53, f22d809a50daa635) : 'Okkk je vais voir Aprs on va explore un autre gros point important les VFX j’ai exploré des pistes que tu vas exploré pour nous faire notre propre studio de VFX'
- experiments/_shared/animator_brain/corpus/CATALOGUE_REFS.md:3 « si je t'évoque poing chargé puissant, ça devrait faire écho au Serious Punch de Saitama, le GIF et l'anime TSB »
  - au plus près (69 % des mots dans l'ordre, 75 % des caractères ; 2026-09-25T11:19, f8f8ab19c4da26bc) : 'Pause juste que es que notre cerveau a une bonne mémoire et a bien tout les outils et es que tu les a ausis ? Parce que je suis étonné que tu t’en souvienne pas'
- experiments/_shared/animator_brain/corpus/CATALOGUE_REFS.md:33 « LA référence Saitama »
  - au plus près (50 % des mots dans l'ordre, 53 % des caractères ; 2026-09-23T20:07, 9d90c8d71a905581) : 'Ba en gros ça doit littéralement devenir je demande à un animateur pro genre sur fiver je lui dis fais moi ça ou reproduis ça ou jsp fais la technique poing du '
- experiments/_shared/animator_brain/corpus/CATALOGUE_REFS.md:34 « coup qui part d'en bas »
  - au plus près (100 % des mots dans l'ordre, 90 % des caractères : TRÈS PROCHE, orthographe corrigée ? ; 2026-09-25T06:22, 356a3960c1c3eb0e) : 'Je vois aucun changement je t’avoue , 3 choses enft l’animation est tjrs pas bonne à mon goût c’est trop simple fin revoi les animations de no ref dnas la lectu'
- experiments/_shared/animator_brain/corpus/CATALOGUE_REFS.md:109 « peint, pas dessiné »
  - au plus près (67 % des mots dans l'ordre, 79 % des caractères ; 2026-09-25T20:24, cf95f861682b091b) : 'Juste je n’aime pas ces 2 plans je les trouve trop peinture , et pas dessiné donc pas obligé de les remplacer apart si tu peux faire mieux et le 3e plan je trou'
- experiments/_shared/animator_brain/ETAT.md:12 « pas premium mais mid haut »
  - au plus près (100 % des mots dans l'ordre, 84 % des caractères ; 2026-09-26T07:13, 7c97115e265e947c) : 'Je te met 8 c pas premium mais c’est mid haut , sur tout que j’aimerai savoir juste une chose quand es que notre studio est un frein dans la qualité ? Es que le'
- experiments/_shared/animator_brain/NOYAU.md:50 « rien à inscrire »

## renvoi_introuvable (3)

- experiments/_shared/animator_brain/corpus/CARNET.md:333 UN_SEUL_COUP.md §11  -- `corpus/poses/` et la fiche UN_SEUL_COUP §11** (en attendant la synthèse :
- experiments/_shared/animator_brain/corpus/CATALOGUE_REFS.md:24 REFERENCES_VIDEO.md §2  -- \| **772ee6b0-image.gif** \| 92c11db65569cadf \| **« Serious Punch 2 », coup type Serious Punch (TSB)**. Manteau, 7 s. Poing armé près de la tête, accroupi très ba
- experiments/_shared/animator_brain/ETAT.md:51 UN_SEUL_COUP.md §11  -- adverse ; puis synthèse -> fiche UN_SEUL_COUP §11 -> v6 -> preuves.

## renvoi_ambigu (15)

- experiments/_shared/animator_brain/corpus/fiches/AURA_DRAGON.md:30 §4b.3 (absent de ce fichier ; existe dans CARNET.md) -- vend la vitesse (§4b.3), rien de réaliste ; rig R6 ; tout jouable dans
- experiments/_shared/animator_brain/corpus/fiches/COUP_CHARGE.md:75 §2.5b (absent de ce fichier ; existe dans CARNET.md) -- presque debout, et le silence avant (§2.5b du carnet).
- experiments/_shared/animator_brain/corpus/fiches/COUP_CHARGE.md:77 §2.6b (absent de ce fichier ; existe dans CARNET.md) -- pose qu'on retient. Rejoint §2.6b et myloe (pose d'après tenue).
- experiments/_shared/animator_brain/corpus/fiches/COUP_CHARGE.md:132 §1.3 (absent de ce fichier ; existe dans CARNET.md) -- - §1.3 cadrage ;
- experiments/_shared/animator_brain/corpus/fiches/COUP_CHARGE.md:133 §2.2 (absent de ce fichier ; existe dans CARNET.md) -- - §2.2 contact montré ou sauté ;
- experiments/_shared/animator_brain/corpus/fiches/COUP_CHARGE.md:134 §2.5b (absent de ce fichier ; existe dans CARNET.md) -- - §2.5b silence ;
- experiments/_shared/animator_brain/corpus/fiches/COUP_CHARGE.md:135 §2.6b (absent de ce fichier ; existe dans CARNET.md) -- - §2.6b suite longue ;
- experiments/_shared/animator_brain/corpus/fiches/COUP_CHARGE.md:136 §3.1 (absent de ce fichier ; existe dans CARNET.md) -- - §3.1 perspective forcée (GGXrd : avancer le bras vers la caméra plutôt
- experiments/_shared/animator_brain/corpus/fiches/COUP_CHARGE.md:138 §1.10 (absent de ce fichier ; existe dans CARNET.md) -- - §1.10 TSB en réf visuelle.
- experiments/_shared/animator_brain/corpus/fiches/COUP_CHARGE.md:190 §1.10 (absent de ce fichier ; existe dans CARNET.md) -- et côte à côte (§1.10), puis mesures en garde-fou.
- experiments/_shared/animator_brain/corpus/fiches/PLEIN_ECRAN.md:65 §9 (absent de ce fichier ; existe dans UN_SEUL_COUP.md, POING_DU_DRAGON_V13.md) -- §9, v13d). Les fonctions de dessin restent dans `build_planches.py` pour une
- experiments/_shared/animator_brain/ETAT.md:32 §7 (absent de ce fichier ; existe dans UN_SEUL_COUP.md, VFX.md, POING_DU_DRAGON_V13.md, COUP_CHARGE.md) -- en arc tendu (fiche §7, CARNET 2.10 ; vidéo
- experiments/_shared/animator_brain/ETAT.md:35 §8 (absent de ce fichier ; existe dans UN_SEUL_COUP.md, POING_DU_DRAGON_V13.md) -- courbé 57°, tête basse, bras écartés sous le buste ; fiche §8 ; vidéo
- experiments/_shared/animator_brain/ETAT.md:37 §9 (absent de ce fichier ; existe dans UN_SEUL_COUP.md, POING_DU_DRAGON_V13.md) -- aux refs (fiche §9) -> « le bras n'est jamais tendu derrière, c'est le buste
- experiments/_shared/animator_brain/ETAT.md:39 §10 (absent de ce fichier ; existe dans UN_SEUL_COUP.md) -- tourné, gros plans (fiche §10 ; vidéo

## absolu_sans_source (22)

- experiments/_shared/animator_brain/corpus/CARNET.md:62 « doit » : Donc on triche pour la ciné, et la pose doit rester lisible de loin et de biais pour les spectateurs.
- experiments/_shared/animator_brain/corpus/CARNET.md:105 « jamais » : - Usage : une carte (où regarder, quoi chercher), jamais une pose ou un timing sans l'avoir vu soi-même.
- experiments/_shared/animator_brain/corpus/CARNET.md:298 « doit » : - le bras qui frappe doit traverser devant le corps : l'IK rate le contact (0,30 stud) ;
- experiments/_shared/animator_brain/corpus/CARNET.md:328 « jamais » : Le bas et le penché servent à l'élan et à la charge (Gon), jamais à l'arrivée du coup droit (Saitama manga : à plat, épaule devant).
- experiments/_shared/animator_brain/corpus/CARNET.md:530 « doit » : Dans ce plan, l'effet doit se retirer (rentrer dans le poing) et revenir APRÈS, dans un plan qui le montre (la révélation).
- experiments/_shared/animator_brain/corpus/CARNET.md:534 « doit » : **4b.8 Une carte peinte doit toujours faire face à la caméra** : orientée dans l'axe de ce qu'elle suit, elle disparaît dès qu'on la regarde par la tranche.
- experiments/_shared/animator_brain/corpus/CARNET.md:601 « jamais » : Et le dragon est au POING ou à la place du perso : il EST le coup (projectile qui part du poing, gueule qui avale), jamais un décor qui tourne autour.
- experiments/_shared/animator_brain/corpus/CARNET.md:652 « jamais » : Le dragon est plus long que le cadre : on ne le voit presque jamais entier.
- experiments/_shared/animator_brain/corpus/CARNET.md:698 « il faut » : - un modèle qu'on déplace par un OS se place par son os ; si le bout qui compte (le museau) est 6 studs devant, c'est ce bout-là qu'il faut amener au contact (la tête de 11 studs posée sur l'attaquant
- experiments/_shared/animator_brain/corpus/CARNET.md:709 « doit » : - ce que l'aperçu fait, Roblox doit le faire : le dragon 3D ignorait sa transparence dans VFXStudio.luau (opaque en jeu quand il devait disparaître) ; un test le garde maintenant.
- experiments/_shared/animator_brain/corpus/CARNET.md:759 « doit » : Et la destruction doit GRANDIR avec la distance (le V s'ouvre, les roches passent de 2 à 20 studs) : à taille constante, vue de loin, il ne restait qu'un trait de fumée.
- experiments/_shared/animator_brain/corpus/fiches/AURA_DRAGON.md:148 « doit » : -> le corps doit onduler latéralement pour garder une largeur à l'écran.
- experiments/_shared/animator_brain/corpus/fiches/AURA_DRAGON.md:153 « doit » : Il doit NAÎTRE (croissance de la tête vers la queue) et MOURIR (dissolution de la queue vers la tête).
- experiments/_shared/animator_brain/corpus/fiches/COUP_CHARGE.md:42 « jamais » : - un coup qui va DROIT, jamais de bas en haut ;
- experiments/_shared/animator_brain/corpus/fiches/COUP_CHARGE.md:185 « jamais » : Ou alors montré net, 2-3 images, AVANT les cartes, jamais recouvert.
- experiments/_shared/animator_brain/corpus/fiches/UN_SEUL_COUP.md:64 « il faut » : Pas d'arène fermée : il faut voir loin.
- experiments/_shared/animator_brain/corpus/fiches/UN_SEUL_COUP.md:214 « jamais » : Sous l'angle des refs (caméra basse de face), notre charge est masquée par la jambe de la victime : chez les refs la victime n'est jamais dans le plan de la charge.
- experiments/_shared/animator_brain/corpus/fiches/VFX.md:68 « jamais » : Le pack le fait (TimeScale 0,1 s) ; nous, jamais, alors que c'était promis dans la fiche du Dragon.
- experiments/_shared/animator_brain/corpus/fiches/VFX.md:76 « Il faut » : Il faut compresser nos courbes (algorithme de VFX Editor, sous licence MIT).
- experiments/_shared/animator_brain/corpus/fiches/VFX.md:84 « il faut » : - les flipbooks sont **désactivés automatiquement sur les téléphones à court de mémoire** : il faut réutiliser les atlas.
- experiments/_shared/animator_brain/corpus/fiches/VFX.md:94 « il faut » : - **le créer ou le détruire provoque un pic** : il faut le pré-créer puis changer ses propriétés.
- experiments/_shared/animator_brain/corpus/CATALOGUE_REFS.md:17 « jamais » : - Les fichiers eux-mêmes (œuvres protégées) ne sont jamais versionnés.

## garde_fou_introuvable (3)

- experiments/_shared/animator_brain/corpus/CARNET.md:326 seuil : < 22; seuil : < 12; seuil : > 3.2
  - phrase : Garde-fou mis dans l'export : buste < 22°, bras < 12°, poing au contact > 3,2 studs, victime debout (sa poitrine est la cible).
  - code cherché : experiments/r6_un_seul_coup/scripts/verify_export.py
- experiments/_shared/animator_brain/corpus/fiches/UN_SEUL_COUP.md:145 seuil : < 12; seuil : < 22; seuil : > 3.2
  - phrase : - Nouveaux contrôles d'export (verify_export.py) : bras à plat au contact et pendant la tenue (< 12°), buste presque droit (< 22°), poing à hauteur de poitrine (> 3,2), poing derrière le buste pendant la charge.
  - code cherché : experiments/r6_un_seul_coup/scripts/verify_export.py
- experiments/_shared/animator_brain/corpus/fiches/UN_SEUL_COUP.md:247 mots : poing sur le côté, pas derrière; mots : épaule droite reculée par le buste
  - phrase : Contrôle d'export remplacé : « poing sur le côté, pas derrière » + « épaule droite reculée par le buste ».
  - code cherché : experiments/r6_un_seul_coup/scripts/verify_export.py

## garde_fou_non_verifiable (2)

- experiments/_shared/animator_brain/corpus/CARNET.md:823 annonce sans identifiant, mots cités ni seuil : à relire à la main
  - phrase : Garde-fou : `outils/corps_bras.py` sur chaque production, et la pelure d'oignon du TORSE (pas seulement du poing) avant de montrer.
  - code cherché : experiments/_shared/animator_brain/outils/corps_bras.py
- experiments/_shared/animator_brain/corpus/fiches/COUP_CHARGE.md:189 annonce sans identifiant, mots cités ni seuil : à relire à la main
  - phrase : Ensuite seulement, comparaison visuelle au GIF Serious Punch, même durée et côte à côte (§1.10), puis mesures en garde-fou.
  - code cherché : experiments/r6_poing_dragon/scripts/verify_export.py, experiments/r6_m1_v222/scripts/verify_export.py, experiments/r6_un_seul_coup/scripts/verify_export.py, experiments/_shared/animator_brain/rules.py
