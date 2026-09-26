# Dépôt 4 : VeMo / ActionReward, l'œil vidéo par modèle vision-langage

Étude du 2026-09-26, dans le cadre du chantier 4 (les « yeux » du cerveau). Écrit en lecture seule : rien n'a été modifié dans `/home/user/Jeux`.

## 0. En bref

- **Dépôt trouvé** : `spatial-westlakenlp/ActionReward`, dossier `VeMo/`. Article : *Zero-Shot Text-to-Motion Evaluation using Video Language Models*, Ji, Wang et Zhang, ICML 2026 (OpenReview `Sf8ubkiEkW`). **Licence** Apache-2.0 (`VeMo/LICENSE`). **Dernier commit** : `cefe4d1`, le 2026-07-03 (« Update citation section header in README »). Cloné dans `/home/user/ext/ActionReward` (39 Mo, 65 fichiers).
- **Ce que c'est vraiment** : une petite version « camera-ready ». On y trouve 1 fonction de score (InternVL3-14B, P(oui) normalisée), un script qui recalcule les AUC à partir de scores **déjà calculés** et fournis en JSON, et des bouts de rendu Blender et SMPL copiés d'autres dépôts (MDM, CLoSD), dont une partie ne s'exécute pas telle quelle. **La sélection de vue par entropie, le cœur du « limiter la perte 3D->2D », n'existe pas dans le code** : elle n'apparaît que dans une figure et dans des colonnes JSON déjà calculées.
- **Test réel fait (CPU, numpy seul)** : j'ai reproduit la table principale et recalculé la sélection de vue à partir des scores par vue qu'ils publient. J'ai aussi appliqué leur échantillonnage d'images à notre vidéo v6, et adapté géométriquement (sans modèle) l'idée « quelle vue perd le moins d'info » à notre export `usc_attaquant.rbxmx`.
- **Ce que ça dit, chiffres à l'appui** :
  - le juge VLM atteint une AUC de 0,72, contre 0,83 pour un humain seul ;
  - la sélection de vue « min entropie » rapporte **+0,007 d'AUC** par rapport à une vue au hasard (0,721 contre 0,714). Elle ne fait qu'éviter les mauvaises vues (« max entropie » : 0,699) ;
  - **8 images ou 32 images donnent le même résultat** (0,720 contre 0,723) : le modèle juge des poses, pas du mouvement ;
  - sur notre vidéo, avec 8 images, **ni la frappe ni le contact ne sont vus**.
- **Pour nous** : pas le modèle, mais trois idées adaptées. (a) Des **questions fermées oui/non** plutôt qu'une note. (b) **Le désaccord entre vues et entre tirages d'images comme mesure d'incertitude**, qu'on affiche et qui ne décide rien. (c) Une **mesure géométrique de la perte de profondeur par vue**, très simple pour un R6 rigide.

---

## 1. Trouver le bon dépôt

- `WebSearch` « VeMo … ICML » : la fiche du poster ICML 2026 n°63904, *Zero-Shot Text-to-Motion Evaluation using Video Language Models*. Le résumé correspond mot pour mot à ce qu'en dit Milan : rendu 3D -> vidéo -> VLM, et « entropy-driven uncertainty analysis for identifying reliable rendered views ».
- Recherche GitHub « ActionReward » : trois résultats. Le seul pertinent est `spatial-westlakenlp/ActionReward` (Python, 18 étoiles, créé le 2026-05-19). Les deux autres n'ont rien à voir : `actionreward-core/actionreward` est un système de récompense PolygonID, `TropicalShadow/ActionReward` un plugin Minecraft. Le README de `VeMo/` renvoie lui-même vers ce dépôt et vers le poster ICML : c'est bien le bon.
- `ActionReward` est une vitrine prévue pour une série (VeMo, VeMo++, VeMoRL). **Seul VeMo est publié** ; VeMo++ et VeMoRL n'ont que des noms de contributeurs dans le README racine.
- L'article n'a pas pu être lu : `openreview.net` et `icml.cc` sont bloqués par le proxy, et `VeMo/assets/paper.pdf`, référencé par le README racine, **n'est pas dans le dépôt**. Ce qui suit vient du **code, des données et de la figure** `VeMo/assets/framework.jpg`, pas de l'article.

## 2. Ce qui est RÉELLEMENT implémenté (lu dans le code)

Il y a 1 458 lignes de Python en tout (hors `joints2smpl`).

| Fichier | Ce qu'il fait vraiment | Remarques |
|---|---|---|
| `VeMo/src/scorer/intervl3.py` (205 l.) | `InterVL3Scorer.score(video, prompt)` : échantillonne `num_segments` images **uniformément** (l. 152-164, `get_index`), les passe en 448×448 à InternVL3, puis lit les logits du **prochain token** et normalise `P(yes)/(P(yes)+P(no))` (l. 138-148) | Charge le modèle en bf16 avec `use_flash_attn=True` et `device_map='auto'` (l. 187-195) : il faut un GPU. Importe `storage.vlm.InternVL3_14B.conversation` (l. 16), donc les poids du modèle doivent être téléchargés dans le dépôt. |
| `VeMo/src/prompts.py` (9 l.) | Le seul gabarit : « is the human motion aligned with the text… judgment based on naturalness and faithfulness… answer "Yes"… "No" » | Le gabarit demande « Yes »/« No » avec majuscule, mais le score lit les tokens `"yes"`/`"no"` en minuscules (`intervl3.py:138`). La masse de probabilité lue n'est donc pas celle des réponses demandées. Ça marche quand même (AUC 0,72), mais c'est un détail de code que le README ne montre pas. |
| `VeMo/demo/demo.py` (21 l.) | Score de `demo/demo.mp4` avec « a person waves a friendly hello », puis calcul de l'entropie binaire | **`num_segments = 2`** (l. 9) : la démo juge une vidéo sur **deux images**. |
| `VeMo/src/evaluate_system.py` (80 l.) | Relit `storage/eval_scores/{mdm,mgpt}.json` (scores **pré-calculés**) et calcule AUC-ROC, AUPR, KS, Spearman, Kendall et Mann-Whitney contre le label humain | Aucun modèle n'est appelé : c'est de la méta-évaluation sur des nombres fournis. |
| `VeMo/src/blender/mesh_to_mp4.py` (185 l.) | Rendu Blender d'une suite d'`.obj` (maillage SMPL) : fond blanc, damier semi-transparent, peau bronze, soleil, 1088×1088, 20 i/s | `VIEW_OFFSETS` ne contient **que 2 vues** (l. 13-16), alors que les données publiées en ont **6 (0-5) plus « stick »**. **La caméra suit le centre du corps à chaque image** (l. 131-132) : on perd le déplacement global, seul le damier le laisse deviner. |
| `VeMo/src/blender/record2anim.py`, `blender_utils.py` | Importent `closd.*` (l. 8-10 et 4) | Copiés de CLoSD. Le module `closd` est absent, donc **non exécutable**. |
| `VeMo/src/visualize/*` (+ `joints2smpl/`) | Articulations -> SMPL par SMPLify (copie de MDM et joints2smpl) | Importe `utils.rotation_conversions`, absent. Il faut aussi le modèle SMPL (licence à part), CUDA par défaut (`--cuda True`) et torch. |
| `VeMo/src/visualize/show_metrics_on_videos.py` | Incruste les scores sur des vidéos à télécharger depuis Google Drive | Il en ressort que « human-opt view » = vue `'0'` (l. 29). |
| `VeMo/storage/` | `reserved_ids.txt` (1 101 invites HumanML3D) ; `eval_scores/*.json` (label oracle humain, 11 métriques de référence, 4 colonnes VeMo, 2 annotateurs) ; `vemo_out/saved_motion/*_scores.json` (P(oui) **par vue** pour 6 générateurs × 3 tailles d'InternVL3 × 8 ou 32 images) | C'est la partie la plus utile du dépôt : **des données**. |

**Dépendances** (`VeMo/requirements.txt`) : torch 2.8, torchvision, transformers 4.56, accelerate, decord, timm, flash-attn implicite. Le modèle de référence est InternVL3-**14B**, soit environ 28 Go en bf16 : impossible avec 15 Go de RAM et sans GPU. La version 1B tiendrait en mémoire, mais ses propres résultats la placent au niveau d'une métrique triviale (voir §3).

**Maturité** : c'est un dépôt de reproduction d'article. Il n'y a ni tests ni paquet, la chaîne de rendu est incomplète, et le code de sélection de vue est absent. Les colonnes « VeMo (min entropy view) » d'`eval_scores` ne se retrouvent **pas** dans les scores par vue publiés : les valeurs exactes ne correspondent que dans 161 cas sur 2 202 (voir test [5]). Elles viennent donc d'une autre passe d'inférence, qu'on ne peut pas régénérer avec ce qui est publié.

## 3. Tests réellement exécutés

Tous les scripts et sorties sont dans `…/scratchpad/c4/depots/vemo_test/`. `pip` est bloqué (pypi.org : 403 au proxy) : ni sklearn, ni scipy, ni torch. J'ai donc recodé l'AUC (Mann-Whitney avec rangs moyens) en numpy. **Il n'y a eu aucune inférence VLM** : 14B est impossible sur cette machine, et installer torch est impossible.

### 3.1 Reproduction et re-analyse de leurs données (`analyse_scores.py`, sortie `analyse_scores_sortie.txt`)

Tests sur mdm + mgpt, les 1 101 ids réservés, soit n = 2 202 (1 119 positifs).

**[1] Table principale reproduite (AUC)**

| Métrique | AUC |
|---|---|
| VeMo, vue choisie par un humain | 0,723 |
| VeMo, vue min-entropie | 0,720 |
| VeMo, vue au hasard | 0,711 |
| VeMo, vue max-entropie | 0,706 |
| Annotateur humain 1 | 0,829 |
| Annotateur humain 2 | 0,835 |
| −L1 (distance à la vraie capture) | 0,627 |
| MoBERT | 0,53 à 0,55 |
| MotionCritic | 0,506 |
| R-precision | environ 0,50 |

Le gain de VeMo sur les métriques existantes est réel : celles-ci sont presque au hasard.

**[2] Les humains entre eux** : ils ne donnent leur accord (oui/non) que dans 78 % (MDM) à 88 % (MotionGPT) des cas. C'est le plafond de n'importe quel juge.

**[3] AUC par vue et par modèle**

| Modèle | Vue 0 | Autres vues (1-5) | Squelette en bâtons |
|---|---|---|---|
| 14B | 0,723 | 0,70 à 0,72 | 0,61 |
| 8B | 0,69 | ≈ | 0,60 |
| 1B | 0,63 | ≈ | 0,56 |

- Avec **1B**, l'AUC (0,63) égale la métrique triviale −L1 (0,627).
- Le **squelette en bâtons** perd 0,11 d'AUC par rapport au maillage : **le volume aide le modèle à lire**.
- **8 images contre 32** : 0,720 contre 0,723 en 14B, et 0,642 contre 0,630 en 1B (32 est même moins bon). **Le modèle n'exploite pas le temps.**

**[4] Sélection de vue recalculée par moi** (entropie binaire H(p) sur les 6 vues maillage, choix de la vue d'entropie minimale ou maximale)

| Modèle | Vue humaine | Min-entropie | Hasard | Max-entropie | Moyenne des 6 vues |
|---|---|---|---|---|---|
| 14B-n32 | 0,723 | 0,721 | 0,714 | 0,699 | 0,716 |

L'idée tient, mais elle est modeste : **la vue la plus confiante vaut la vue qu'un humain aurait choisie, et gagne moins d'un point d'AUC sur une vue au hasard**. Sa vraie utilité est d'éviter la vue où le modèle hésite (−0,02).

**[5] Cohérence entre fichiers** : les colonnes VeMo d'`eval_scores` ne correspondent exactement aux scores par vue que dans 7 à 8 % des cas. C'est une autre passe d'inférence (texte « révisé » ?), donc non reproductible depuis le dépôt.

**[6] Désaccord entre vues (14B-n32)** : dans **21 % des cas**, au moins une vue dit « oui » et une autre « non ». L'écart max-min de P(oui) entre vues a une médiane de 0,12 et un 90e centile de **0,51**.
- **Globalement**, la vue change peu l'AUC.
- **Au cas par cas**, elle change souvent le verdict. C'est exactement notre problème (2) et (3).

**[7] Vraies captures humaines (HumanML3D)** : le juge leur dit « non » dans **24 %** des cas. Un juge VLM rejette donc souvent un mouvement correct.

**[8] Variantes cachées dans les données** (`0merge`, `0seq`, `0_paraphrase`) : toutes font un peu moins bien que la vue 0 seule (0,708 à 0,716). Les auteurs ont essayé d'autres présentations des images, sans gain.

### 3.2 L'œil de VeMo sur notre vidéo v6 (`echantillonnage.py`, planches `vemo_voit_n8.png` et `vemo_voit_n32.png`)

J'ai recopié telle quelle la formule `get_index` (`intervl3.py:152-164`) et l'ai appliquée à `2026-09-26-un-seul-coup-v6-scene-complete-avec-son.mp4` (30 i/s, 393 images, 13,1 s). Le découpage vient de `staging.json` (60 i/s), avec une réserve : la vidéo dure 13,1 s et la scène 12,5 s, donc un décalage de 0,6 s au plus est possible.

| Réglage | Pas entre images | Ce qui est vu |
|---|---|---|
| `num_segments=2` (la démo) | 6,55 s | 1 image de charge, 1 de conséquence |
| `num_segments=8` | 1,64 s | 0 image de frappe, **0 de contact**, 1 de charge (un gros plan) ; 3 des 8 images sont dans la conséquence |
| `num_segments=32` | 0,41 s | 1 image de frappe (4,70 s), 1 d'impact (5,10 s), 13 de conséquence |

Conclusion concrète : un juge qui tire les images **uniformément** dans le temps passe à côté des 0,27 s qui font le coup (frappe + contact). C'est l'inverse de notre besoin (1). Notre `outils/durees.py` travaille à cadence fixe de 30 i/s et `outils/regard.py` en persistance à 12/s : ils sont déjà plus justes que ça.

### 3.3 Adaptation géométrique de la « vue qui perd le moins » sur notre export (`ambiguite_vues.py`, `ambiguite_vues.json`, planche `ambiguite_vues.png`)

**Idée propre au R6.** Un bras R6 est un bloc rigide de 2 studs, sans coude. À l'écran, sa longueur projetée donne donc **exactement** la valeur absolue de sa composante en profondeur. **Seul le signe est perdu** : le bout part vers la caméra ou vers le fond, le membre est devant ou derrière le torse. C'est précisément l'erreur « bras devant/derrière le torse » de notre faiblesse (2). La mesure, par membre et par caméra, est `prof = |axe du membre · axe de visée|` : 0 quand le membre est vu de profil (lisible), 1 quand il pointe l'objectif.

Je l'ai calculée pour la caméra écrite de `staging.json` et pour 36 caméras en orbite (12 azimuts × 3 élévations), en relisant `usc_attaquant.rbxmx` comme le fait `staging.py`. Temps d'exécution : 0,37 s.

| Moment (image à 60 i/s) | Somme `prof` des 4 membres, caméra écrite | Rang de la caméra écrite sur 36 (0 = la plus lisible) | Ce qui se passe |
|---|---|---|---|
| Charge, milieu (226) | 2,58 | **30** | Bras droit 0,87 et bras gauche 0,76, pointés **vers** l'objectif |
| Fin de charge (266) | 1,77 | 10 | Bras droit 0,19, lisible |
| Frappe (275) | 1,63 | 4 | Bras droit **0,90 vers la caméra** : c'est le « poing vient VERS l'objectif » voulu par la fiche |
| Contact (283) | 1,14 | 3 | Bras droit 0,07 : vu de profil, lisible |

Lecture sans verdict :
- Au **contact**, la caméra écrite est parmi les plus lisibles, ce qui confirme le choix « de côté ».
- À la **frappe**, le raccourci est **voulu** : c'est un effet de cinéma, le poing jeté dans l'objectif. Il ne faut surtout pas le « corriger ».
- Au **milieu de la charge**, le plan écrit est l'un des moins lisibles pour les bras : les deux poings pointent vers l'objectif. Or c'est le moment que Milan a contesté six versions de suite (« le bras n'est jamais tendu derrière », « aucun changement »). Ce n'est **pas** une preuve que la caméra est la cause : c'est une observation à mettre à côté de ses retours.

Limites de la mesure :
- la somme `prof` favorise mécaniquement les vues de profil ;
- elle ignore l'occlusion, alors que `hors_silhouette` la donne, et je l'ai imprimée à côté ;
- elle ne dit rien de la beauté ;
- le rendu de `M.render` ne gère pas les accents dans les titres (« cam?ra »), c'est cosmétique.

## 4. Les briques utiles pour NOS yeux

| # | Brique (idée VeMo) | Faiblesse visée | Forme adaptée R6 / Roblox | Coût | Intérêt |
|---|---|---|---|---|---|
| A | **Perte de profondeur par vue**, en géométrie plutôt qu'en entropie de VLM (§3.3) | (2) bras devant/derrière ; (3) cadrage réel | Fonction `ambiguite(w, cam)` à côté de `vues.hors_silhouette` : par membre, `prof` et **signe** (vers la caméra / devant ou derrière le torse). Pour une **ref** reconstruite avec `geo_pose`, on liste les membres à `prof` élevée et on écrit « signe indécidable depuis cette vue, à trancher par l'occlusion ou par une autre ref » au lieu de deviner. Pour **nos** plans, on affiche la valeur à la caméra écrite, sans l'optimiser. | ~80 lignes, numpy, déjà prototypé (0,4 s) | Élevé |
| B | **Question fermée oui/non + P(oui) normalisée** (`intervl3.py:138-148`) plutôt qu'une note | (4) surestimation | Transposé à moi-même, faute de logits : pour chaque livraison, une liste de questions **factuelles** tirées des mots de Milan (« au contact, le poing est-il à hauteur de poitrine ? », « le buste tourne-t-il pendant la charge ? », « un bras est-il tendu derrière ? »). Un lecteur **à l'aveugle** (sous-agent qui ne sait pas quelle version est la nôtre ni laquelle est la nouvelle) y répond sur la vidéo au cadrage réel. Les réponses sont affichées, elles ne bloquent rien. | 0 dépendance ; une grille de questions par fiche | Élevé |
| C | **Désaccord comme incertitude** (entropie entre vues ; 21 % de désaccord chez eux) | (4) surestimation ; (2) profondeur | Poser la même question sur 3 présentations : caméra écrite, vue de profil, vue de dessus (ou 3 tirages d'images décalés). Si les réponses divergent, la lecture est marquée **incertaine**, et une prédiction de note faite sur une lecture incertaine est rabaissée ou accompagnée d'une fourchette. | Faible (3 rendus déjà faisables avec `geo_pose.camera_orbite`) | Moyen-élevé |
| D | **Leçon négative sur le temps** (8 ou 32 images, même AUC ; démo à 2 images) | (1) vitesse réelle | **Inverser** : ne jamais faire juger un coup sur des images tirées uniformément. Si un juge par images est utilisé, les images sont **ancrées sur les événements** (clés de `planche_cles`, marqueurs `staging.json` : départ, frappe, contact, ±2 images) et complétées par `regard.persistance` / `durees.py`, qui gardent la durée. | Nul (c'est une règle de méthode, consultative) | Moyen |
| E | **Le rendu compte** : maillage > squelette en bâtons (−0,11 d'AUC) ; caméra qui suit le corps = perte du déplacement | (3) cadrage réel ; (5) jeu / cinématique | Nos R6 ont déjà du volume. Mais pour une anim de **jeu** (M1), la caméra de jugement doit être **la caméra du joueur**, fixe par rapport au monde ou en 3e personne derrière l'épaule, **pas** une caméra qui suit le torse, sinon la translation (dash, recul) disparaît. Pour une **cinématique**, c'est la caméra écrite de `staging.json`, et seulement elle. | Faible : un préréglage « caméra joueur » dans le rendu de vérification | Moyen |
| F | **Méta-évaluation de nos propres yeux** (`evaluate_system.py` : AUC, Spearman, Kendall contre un label humain) | (4) surestimation (+0,3) | On a déjà `notes_milan.jsonl` et nos prédictions. La même logique, mesurer si **un** indicateur (le nôtre, `juge.py`, une mesure `geo_pose`) **classe** les versions comme Milan (Kendall sur les paires de versions), dit quels indicateurs valent quelque chose, au lieu de les empiler. Petit n, donc c'est un signal, pas une preuve. | ~50 lignes numpy (AUC et Kendall recodés, voir `analyse_scores.py`) | Moyen |

## 5. À inverser ou à ignorer

- **Ignorer le modèle** (InternVL3-14B) : 28 Go, GPU, flash-attn, et pypi bloqué ici. Et même disponible, il juge l'**alignement à un texte** (« une personne salue ») sur des mouvements du quotidien (HumanML3D), pas la **qualité** d'un coup d'anime. « Frappe-t-il vers le bas ? » est une question d'alignement qu'il pourrait peut-être poser ; « est-ce niveau TSB ? » non.
- **Ignorer la version 1B** : AUC 0,63, soit le niveau de −L1. Un faux juge.
- **Ignorer la chaîne SMPL / joints2smpl / CLoSD** : humain à 24 articulations, CUDA, modèle SMPL sous licence, imports cassés. Un R6 n'a pas de squelette SMPL et nous avons déjà `moon.render`, `geo_pose.rendre` et bpy.
- **Inverser l'échantillonnage uniforme** : pour un coup de 0,27 s, les images doivent suivre les événements, pas l'horloge.
- **Inverser « choisir la vue la plus lisible »** pour les cinématiques : un plan écrit peut vouloir la perte de profondeur (poing dans l'objectif, raccourci anime). La mesure A s'**affiche** à la caméra écrite, elle ne choisit pas la caméra. Pour le **jeu**, la caméra n'est pas à nous : c'est celle du joueur. Là non plus, on n'optimise pas la vue : on vérifie que le coup se lit depuis **cette** vue.
- **Ne pas prendre « min entropie » pour une vérité** : chez eux, la vue la plus confiante n'est pas plus juste qu'une vue humaine ; elle évite seulement la pire.

## 6. Les pièges

1. **Faux sentiment d'objectivité** : un P(oui) = 0,94 a l'air d'une mesure. Or leur meilleur juge n'atteint que 0,72 d'AUC, contre 0,83 pour un humain, et les humains eux-mêmes ne s'accordent qu'à 78-88 %. Un nombre sorti d'un VLM n'est pas plus « objectif » que ma note ; il est seulement plus opaque. Si l'on s'en sert, il s'affiche avec sa dispersion entre vues, jamais comme verdict (ce qui est conforme au refus des « règles gravées » de Milan).
2. **Le juge ne voit pas le mouvement** : n8 = n32. Présenter un score VLM comme un jugement « sur la vidéo » serait mensonger. C'est un jugement sur quelques poses, et notre faiblesse (1) resterait entière.
3. **Rejet de mouvements corrects** : 24 % des vraies captures sont notées « non ». Un juge qui dit non ne prouve rien.
4. **Tokens et gabarit** : « Yes/No » dans le gabarit, « yes/no » lus dans le code. Ce genre d'écart silencieux change la mesure. Si l'on bâtit un protocole de questions, il faut le figer et le versionner, et le tester sur des cas connus (les versions notées par Milan) avant d'y croire.
5. **Je me juge moi-même** : transposée à Claude (brique B), la question oui/non reste biaisée si c'est moi qui ai fait l'animation et qui sais quelle version est la nouvelle. D'où l'aveugle obligatoire : sous-agent sans contexte, versions mélangées. C'est notre +0,3 de biais mesuré.
6. **Dépendance lourde pour un gain mince** : torch + transformers + 28 Go de poids pour +0,007 d'AUC via la sélection de vue. Le rapport coût/gain est mauvais ; ce qui a de la valeur, ce sont les **idées**.
7. **Reproductibilité partielle** : les colonnes finales ne se régénèrent pas depuis le dépôt, l'article manque dans le dépôt et 2 vues sur 6 seulement sont dans le code. Il ne faut pas citer leurs chiffres de sélection de vue comme établis. Ceux de ce rapport sont **recalculés** à partir de leurs scores par vue.

## 7. Ce que je proposerais d'en faire (consultatif, rien d'appliqué)

1. Verser la **mesure A** dans `outils/vues.py` (ou dans un petit `outils/profondeur.py`) et l'afficher dans `rapport_regard.py` à la caméra écrite, pour les 4 moments de la fiche. Pour les refs, l'appeler après la reconstruction `geo_pose` afin de marquer « signe indécidable » sur les membres raccourcis. Coût : une heure.
2. Écrire, dans la fiche du moment, une **grille de 5 à 8 questions oui/non** tirées de `corpus/milan_verbatim.jsonl`. Les faire répondre à l'aveugle sur la vidéo **au cadrage réel**, avec les images ancrées sur les événements. Afficher les divergences entre les 3 présentations.
3. Petite **méta-évaluation** de nos indicateurs contre `notes_milan.jsonl` (AUC ou Kendall, code déjà recodé en numpy) : savoir lesquels suivent Milan avant d'en ajouter d'autres.

## Fichiers

- Dépôt (lecture seule) : `/home/user/ext/ActionReward` (VeMo : `VeMo/src/scorer/intervl3.py`, `VeMo/src/evaluate_system.py`, `VeMo/src/blender/mesh_to_mp4.py`, `VeMo/storage/`)
- Tests : `/tmp/claude-0/-home-user-Jeux/4796ac9e-8e41-51f7-91c4-7b92a6a187d0/scratchpad/c4/depots/vemo_test/`
  - `analyse_scores.py`, `analyse_scores_sortie.txt` : reproduction et re-analyse de leurs scores
  - `echantillonnage.py`, `echantillonnage_vemo.json`, `vemo_voit_n8.png`, `vemo_voit_n32.png` : ce que leur échantillonnage voit de notre v6
  - `ambiguite_vues.py`, `ambiguite_vues.json`, `ambiguite_vues.png` : perte de profondeur par vue sur `usc_attaquant.rbxmx`
