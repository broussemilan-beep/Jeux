# Dépôt 2 : AnimationBench, « l'œil artistique » ?

Étude du 2026-09-26, lecture seule, en pensant à nos cinq faiblesses de regard
(1 images une par une au lieu du mouvement ; 2 profondeur 2D->3D ; 3 jugement
sur planches et chiffres au lieu du cadrage réel ; 4 surestimation de +0,3 ;
5 anim de JEU ou de CINÉMATIQUE).

## 0. En une phrase

Le dépôt officiel ne contient **aucun code** : un README et une licence.
Une réimplémentation non officielle existe. Elle montre que les « principes
Disney » y sont évalués surtout par un **VLM distant (Qwen3-VL) qui répond
oui/non**, plus deux mesures géométriques (slow-in/slow-out par CoTracker,
squash & stretch par SAM3 sur une **balle**), toutes sur GPU. Testée sur nos
données, la seule brique portable (le score SISO) **ne sépare pas** notre v6
(« c trjs pas bon ») des animations TSB. Elle favorise même la cloche d'ease
disneyenne, contre la tenue suivie d'un départ sec de l'anime. **Ce qui vaut
d'être pris, ce sont trois idées de méthode, pas le code** : la grille de
questions observables, l'alignement de chaque mesure sur un humain, la
comparaison par paires.

## 1. Identification du dépôt

| Candidat | Ce que c'est | Retenu ? |
|---|---|---|
| `github.com/VideoVerses/AnimationBench` | Dépôt **officiel** de l'article arXiv 2604.15299 (« AnimationBench: Are Video Models Good at Character-Centric Animation? », HKUST / NTU / Pearl Studio, avril 2026). | Oui (c'est celui de Milan), mais il est **vide de code** |
| `github.com/blackzipper-hub/animationbench` | Réimplémentation « dimension-first », 1 seul commit « Add files via upload ». Auteur « 黑子佩 », absent de la liste des auteurs de l'article. | Oui, pour lire du code réel, avec les réserves ci-dessous |
| `github.com/AnimationBench/AnimationBench.github.io` | Source React/TS de la page projet (démo, graphiques). | Lu pour les définitions et l'étude humaine |

Clones (lecture seule, `--depth 1`) :
- `/home/user/ext/AnimationBench` : commit `12a0202`, **2026-04-17**, « Create
  LICENSE ». 2 fichiers en tout : `README.md` (75 lignes) et `LICENSE`.
  **Licence CC BY-NC-ND 4.0** : pas d'usage commercial, pas d'œuvre dérivée.
- `/home/user/ext/animationbench_blackzipper` : commit du **2026-05-07**,
  **aucun fichier LICENSE** (donc tous droits réservés par défaut). 2 875 lignes
  de Python, 385 fichiers (surtout des images de test).
- `/home/user/ext/animationbench_site` : commit du 2026-04-17 (688 Mo de médias).

Le texte de l'article n'est **pas lisible d'ici** : arxiv.org,
animationbench.github.io, alphaxiv et semanticscholar sont bloqués par le
proxy (403). Je n'ai pas pu vérifier les formules exactes de l'article. Ce qui
suit vient donc du code non officiel, de la source de la page projet et d'un
extrait de recherche web (FTOA = questions VLM du type « Does the character's
hair continue moving after the body has stopped? »). **On ne sait pas si
l'implémentation non officielle suit fidèlement l'article.**

## 2. Ce qui est RÉELLEMENT implémenté (implémentation non officielle)

| Dimension (README) | Ce que fait le code | Modèle et dépendances | Fichier:lignes |
|---|---|---|---|
| Anticipation | Pose UNE question oui/non à un VLM sur la vidéo. Score = 100 si « yes », 0 sinon, puis moyenne. **Les questions ne sont pas fournies** : `data/prompt_all/action/anticipation.json` ne contient que 50 prompts de génération (« The character jumps forward… »). | Qwen3-VL-plus via l'API DashScope (Alibaba), clé `DASHSCOPE_API_KEY`, vidéo échantillonnée à 8 i/s | `close_set/twelve_principles_anticipation.py:17-60`, `common/close_set.py:11,26-62`, `common/vlm.py:11-40,93-125`, `common/scoring.py:10-57` (ligne 48 : `100.0 if is_correct else 0.0`) |
| Follow-through / overlapping | Identique (oui/non VLM). Aucune question ni donnée fournie. | Qwen3-VL-plus | `close_set/twelve_principles_follow_through_overlapping.py` |
| Slow-in / slow-out | Script autonome. CoTracker3 suit une grille de 100 points sur un masque du sujet, 25 points sur le fond. Pour chaque image : médiane des vitesses du sujet, moins la projection de la vitesse du fond sur cette direction, le tout lissé par une moyenne glissante de 9 images. Score sur 0-5 : trois conditions sur la « cloche » (le milieu plus rapide que les 20 % du début et de la fin, max/min ≥ 2) et deux sur l'accélération et la décélération, chacune devant durer ≥ 5 % des images. `find_motion_bounds` ne détecte rien : il rogne seulement 2 % à chaque bout. | `torch.hub` CoTracker3 offline, `device='cuda'` codé en dur, masque PNG fourni à la main | `close_set/siso.py:47-58` (lissage), `61-73` (bornes), `76-114`, `117-168`, `171-234` |
| Squash & stretch | Porte d'entrée VLM (« Does the video contain a rebound event? »), sinon score 0. Ensuite SAM3 segmente « **ball** » (le prompt par défaut) image par image. Score = 0,7 × conservation de l'aire + 0,3 × variation d'anisotropie (valeurs propres de la covariance des pixels du masque). | SAM3 + torch + Qwen | `close_set/twelve_principles_squash_and_stretch.py:14-17,22-108,130-157` ; `models/sam_area_model.py:95-130,189-215` |
| Camera motion consistency | Code de VBench : CoTracker2 sur une grille 10×10, puis classe pan, tilt, zoom ou statique d'après le déplacement des points de bord **entre la PREMIÈRE et la DERNIÈRE image seulement**. La détection d'orbite est désactivée. Score = la caméra demandée dans le prompt figure-t-elle dans la liste prédite ? `split_video_into_scenes` (PySceneDetect) est défini mais **jamais appelé**. En cas d'échec de téléchargement, le code **désactive la vérification SSL** pour tout le processus. | CoTracker2, decord, scenedetect, cuda | `close_set/camera_motion.py:16-25,57-68,125-127,194-201,215-240` |
| Motion rationality | **Aucun évaluateur.** Seulement 50 prompts (« The character starts walking… ») et des images. | — | `data/prompt_all/motion_rationality/motion_rationality.json` |
| Diversity, novelty | Distance de caractéristiques VGG19 (importe `vbench2`, absent de `requirements.txt`) ; V-JEPA2 ViT-L. | torch, torchvision, transformers | `close_set/diversity.py:9-21`, `close_set/novelty.py:25-50` |
| IP (apparence, expression, mouvement) | Une fiche de personnage (`canonical_appearance`, `canonical_behavior`) déclinée en **dizaines de questions oui/non atomiques** (« Does Fred solve problems with brute force…? »), posées au VLM. | Qwen | `ip/motion.py:17-60`, `data/prompt_all/ip_prompt/*_evaluate.json` |

Maturité : un seul commit « upload ». Le paquet mélange des modules importables
(`animationbench.common…`) et des scripts autonomes (siso, camera, diversity).
`requirements.txt` est incomplet (il manque vbench2, decord, scenedetect,
imageio, transformers, torchvision, tqdm, sam3). Les données d'évaluation des
principes, c'est-à-dire les questions et les masques de la plupart des vidéos,
sont absentes. **Rien n'est exécutable de bout en bout ici** : pas de GPU, pas
de torch, pas de clé DashScope. Et quand bien même, l'API enverrait nos vidéos
en Chine, ce qui est exclu pour les refs sous droits.

Page projet : la section « Human Alignment » dit elle-même qu'elle est
« Simulating the paper's human preference study »
(`src/components/HumanEvalSection.tsx:107`). Les quatre essais de démo ont
tous `benchmarkPreference: "A"`. Les coefficients de Spearman de l'article ne
sont pas dans la source de la page. **Je ne peux donc pas vérifier
l'affirmation « strong alignment with human preference ».**

## 3. Test réel sur nos données (≈ 10 s de calcul, CPU)

Script : `scratchpad/ab/test_siso.py` ; résultats :
`scratchpad/ab/siso_resultats.json`. J'ai porté **à l'identique** les fonctions
de score de `close_set/siso.py` (lignes 47-168, exécutées depuis le fichier
cloné, sans les réécrire). CoTracker est remplacé de deux façons :
(a) **vitesses exactes** lues dans les KeyframeSequence (`geo_pose.mondes_rbxmx`
et `mondes_rbxm`, 60 i/s) : poing droit, poing gauche, torse, et la médiane
des 6 blocs, qui imite la médiane CoTracker sur les points du perso ;
(b) **flux optique Farneback** (OpenCV) sur notre vidéo v6 : les 10 % de pixels
les plus rapides servent de « sujet », la médiane globale de « fond ».

### Résultats (score SISO sur 5 ; « contraste » = pic ÷ 2e pic séparé de 0,15 s)

| Clip | Signal | SISO /3 | Accél. /2 | **Total /5** | Contraste brut | Contraste après lissage 9 img |
|---|---|---|---|---|---|---|
| **Notre v6** (Milan : « c trjs pas bon »), 60 i/s | poing D | 3 | 1 | **4** | 6,07 | 2,68 |
| | torse | 3 | 2 | **5** | 12,6 | 6,1 |
| | médiane 6 blocs | 3 | 2 | **5** | 14,0 | 6,75 |
| Notre v6 rééchantillonnée à 16 i/s (cadence d'une vidéo I2V) | poing D | 3 | 2 | 5 | 4,77 | **1,05** |
| **TSB M1**, 60 i/s | poing D | 2 | 2 | 4 | 29,2 | 12,3 |
| | torse | 1 | 1 | **2** | 1,96 | 1,68 |
| | médiane 6 blocs | 1 | 2 | 3 | 3,4 | 1,5 |
| TSB Collateral Ruin | poing D | 3 | 2 | 5 | 1,32 | 1,31 |
| TSB Ultimate1 | poing D | 2 | 2 | 4 | 1,42 | 1,31 |
| **Notre vidéo v6** (flux optique, 393 images à 30 i/s) | sujet − fond | 2 | 2 | 4 | 9,16 (à 1,27 s : saut d'image) | 1,09 |

Profils synthétiques (2 s à 30 i/s), pour voir ce que le score récompense :

| Profil de vitesse | Total /5 |
|---|---|
| vitesse constante (robot) | 0 |
| **cloche d'ease in/out (Disney)** | **5** |
| **tenue 1,5 s, frappe en 2 images, tenue (anime / TSB)** | **3** |
| tenue, frappe en 2 images, recul amorti | 5 |
| **bruit pur (tremblement)** | **3** |

### Ce que ça montre, vraiment
1. **Le score ne suit pas l'avis de Milan.** La v6 qu'il juge « pas bonne »
   obtient 4 à 5 sur 5 ; le M1 de TSB en obtient 2 à 4. Un départ sec suivi
   d'une tenue obtient **la même note que du bruit** (3/5). La métrique mesure
   à quel point une courbe ressemble à une cloche d'ease disneyenne, pas la
   qualité d'un coup d'anime.
2. **Le lissage sur 9 images efface les départs secs.** À 16 i/s, notre
   contraste lent/rapide au poing passe de 4,77 à 1,05. Le « coup » disparaît
   du signal, alors que c'est exactement ce que l'œil lit (CARNET 2.1 : TSB
   2,3 à 5,7 ; notre rafale v7 0,55 à 1,49).
3. **Un seul score par clip ne veut rien dire pour nos scènes.** Le code
   suppose une vidéo de 5 s avec un seul mouvement. Notre scène fait 12,5 s,
   a plusieurs temps et **7 sauts d'image probables** (à 4,2 s ; 4,47 ; 4,73 ;
   4,8 ; 4,87 ; 8,6 ; 10,3 s). Le flux optique à travers une coupe devient le
   « pic » (9,16 à 1,27 s).
4. **La médiane des points suit le corps, pas le poing.** Sur le M1 de TSB,
   la médiane donne 7,6 u/s quand le poing atteint 71 u/s. Le principe mesuré
   est celui du déplacement global du perso.

## 4. Briques utiles POUR NOUS (idées réécrites, jamais de code copié)

Aucune ligne n'est à reprendre : dépôt officiel sans code et sous licence ND,
réimplémentation sans licence. Ce qui suit, ce sont des **idées de méthode**,
réécrites à notre façon.

**B1. La fiche décomposée en questions observables oui/non**, horodatées, sans
note agrégée (le format `canonical_behavior` des fiches IP).
- Faiblesses : 3, 5 et un peu 4.
- Forme chez nous : chaque fiche de moment (`corpus/fiches/*.md`) reçoit une
  liste de 5 à 12 questions **observables** tirées des mots exacts de Milan
  (`milan_verbatim.jsonl`). Par exemple : « Au contact, le poing est-il à
  hauteur de poitrine ? », « Le torse tourne-t-il avant que le bras parte ? »,
  « Le coup se lit-il sur la bande 12/s en vignette ? ».
- Chaque question porte :
  - **son mode de réponse**, mesure `geo_pose`, `corps_bras` ou `durees`
    quand c'est mesurable, sinon « regardé à vitesse réelle au cadrage
    réel » ;
  - **son cadrage**, JEU (caméra joueur, vignette) ou CINÉ (plan écrit, pose
    trichée admise pour ce plan) ;
  - la **preuve** (image, instant).
- On publie la liste des réponses, **jamais un pourcentage** : c'est une
  observation, pas un verdict.
- Coût : faible (un bloc JSON par fiche et un script de rapport d'environ
  100 lignes branché sur `rapport_regard.py`).
- Intérêt : 7/10.

**B2. « Alignement humain » : chaque mesure doit gagner sa place face à
Milan.** L'article revendique une corrélation de Spearman entre ses scores et
des préférences humaines par paires ; c'est la bonne idée, même non vérifiable
ici.
- Faiblesse : 4 (et le faux sentiment d'objectivité).
- Forme chez nous : un petit script qui, pour chaque mesure de nos outils
  (contraste lent/rapide, tenue, part d'effet, corps/bras…), calcule le
  Kendall tau contre les notes de Milan (`notes_milan.jsonl`, 27 lignes) et
  contre ses préférences entre paires de versions. Chaque mesure est affichée
  avec son alignement et un intervalle honnête : avec une dizaine de points,
  une corrélation reste très fragile.
- Le test ci-dessus en donne l'exemple : SISO serait marqué « non aligné ».
- Coût : faible (une demi-journée). Intérêt : 8/10.

**B3. Comparer par paires plutôt que noter dans l'absolu**, format « Which
output better demonstrates anticipation? A/B » (`HumanEvalSection.tsx:31`).
- Faiblesse : 4.
- Forme chez nous : avant chaque livraison, prédire aussi **des préférences**
  (« Milan préférera v6 à v5 sur la charge ? oui/non, confiance ») à côté de
  la note chiffrée exigée par NOYAU. Les préférences se vérifient mieux que
  ±0,3 sur 10, et elles alimentent B2.
- Coût : quasi nul. Intérêt : 7/10.

**B4. Vitesse relative « sujet moins caméra »** (`siso.py:212-219`).
- Faiblesses : 1 et 3.
- Idée juste : ce que lit le joueur, c'est la vitesse **à l'écran** une fois
  retiré le mouvement de caméra.
- Chez nous, c'est plus simple et exact : on connaît la caméra (piste de
  `scene.json` / staging). Il suffit de projeter le poing avec la vraie caméra
  (`vues.projeter` / `espacement`) pour obtenir la vitesse à l'écran image par
  image, en mode jeu ET en mode ciné. Pour les refs vidéo, le flux optique
  sujet − fond **par plan** suffit.
- **Garder la courbe, jeter le score** : il faut inverser le critère (voir §5).
- Coût : faible. Intérêt : 6/10.

**B5. Découper en plans avant toute mesure de mouvement** (PySceneDetect est
importé mais pas utilisé dans `camera_motion.py`).
- Faiblesses : 3 et 5.
- Forme chez nous : nos mesures vidéo (`durees.py`, `juge.py`) repèrent déjà
  les sauts d'image ; il suffit de rendre le découpage par plan systématique
  en amont (un plan = un cadrage = une mesure).
- Coût : nul à faible (`pip install scenedetect` est léger mais pas
  nécessaire). Intérêt : 5/10.

**B6. Classer le mouvement de caméra (pan, tilt, zoom, fixe) depuis les
pixels.**
- Faiblesse : 5, mais **pour les refs seulement** (quelle caméra TSB utilise
  au contact). Pour nos anims, la caméra est connue et ce serait inutile.
- Forme chez nous : Farneback par fenêtres courtes à l'intérieur d'un plan ;
  pas la comparaison première/dernière image de VBench.
- Coût : moyen. Intérêt : 4/10.

**B7. Aire et anisotropie d'un masque dans le temps** (squash & stretch).
- **Inutile sur le corps R6** : 6 blocs rigides, pas d'étirement.
- Réutilisable pour les **VFX** (onde de choc, smear, boule d'énergie) :
  l'étirement du masque d'effet au contact et sa conservation d'aire sont
  lisibles sur nos rendus, avec numpy seul.
- Coût : faible. Intérêt : 3/10.

**B8. Follow-through / overlapping.** Pour nous, c'est le **décalage de pic de
vitesse entre blocs** (torse, puis épaule, puis bras), exact depuis la
KeyframeSequence. Nous l'avons déjà en partie (`planche_cles` bande
« rythme », `corps_bras.py`). Les questions « hair / clothing lag » sont sans
objet : pas de cape ni d'écharpe (GDD amendé). Intérêt : 3/10 (déjà couvert).

## 5. À inverser ou ignorer

- **Inverser le critère SISO.** Il récompense l'accélération et la
  décélération longues (≥ 5 % du clip) et la cloche. Le combat anime / TSB
  demande l'inverse : une tenue, puis un départ en 1 à 3 images (« do not ease
  out », tuto firytwig, CATALOGUE `afaa00eb`). Notre CARNET 2.1 (« lent contre
  rapide ») mesure déjà la bonne chose.
- **Ignorer :**
  - le squash & stretch sur le corps ;
  - la cohérence caméra au sens VBench : est-ce que la vidéo générée a fait le
    pan demandé ? Chez nous, la caméra est écrite, donc toujours « conforme » ;
  - novelty, diversity, IP appearance : ce sont des mesures de générateurs
    vidéo, pas d'animation posée à la main ;
  - « motion rationality » : pas de code du tout.
- **Ne pas confondre présence et qualité.** Les dimensions « principes » posent
  la question « y a-t-il une anticipation ? ». Nos animations ont toujours une
  anticipation, et Milan dit quand même « pas bon ». Sa critique porte sur la
  forme de la pose, la hauteur du poing, qui porte le mouvement : pas sur la
  présence d'un principe.

## 6. Pièges

1. **Faux sentiment d'objectivité**, démontré au §3 : 4 à 5 sur 5 pour une
   version rejetée, et autant de points pour du bruit que pour un départ sec
   d'anime. Un chiffre sur 5 ou sur 100 rassure exactement comme nos +0,3.
2. **Juge VLM oui/non binarisé à 100 ou 0** (`scoring.py:48`) : aucune nuance,
   et le résultat dépend de la formulation de la question (non fournie ici).
   Pour nous, le VLM, c'est Claude : ajouter un second juge VLM ne corrige pas
   notre biais, ça le double.
3. **Dépendances lourdes et GPU** : torch, CoTracker2/3, SAM3, V-JEPA2 ViT-L,
   VGG19, vbench2, et `cuda` codé en dur (`siso.py:171`,
   `camera_motion.py:215`). Rien de léger à installer dans le conteneur.
4. **API externe** (DashScope) : nos vidéos, et surtout les refs sous droits,
   partiraient chez un tiers. Exclu.
5. **Sécurité** : `camera_motion.py:65-68` désactive la vérification des
   certificats TLS pour tout le processus. À ne jamais exécuter tel quel.
6. **Licences** : officiel CC BY-NC-ND (on ne peut rien en dériver) ;
   réimplémentation sans licence. On ne verse **aucun** code dans le dépôt,
   seulement des idées réécrites. Le portage de test reste dans le scratchpad.
7. **Mauvais domaine** : le benchmark note des générateurs image-vers-vidéo
   sur des clips de 5 s à un seul mouvement, surtout des personnages cartoon
   déformables. Il ne dit rien du R6 rigide, des coupes de montage ni de la
   différence entre jeu et ciné.
8. **Alignement humain non vérifiable** : article inaccessible depuis le
   conteneur, et la section de la page projet n'est qu'une démo « simulée ».

## 7. Verdict pour les yeux du cerveau

AnimationBench n'est **pas un œil artistique utilisable**, mais il donne trois
leçons de méthode qui visent nos faiblesses 3, 4 et 5 :
- **une grille de questions observables par moment, étiquetées JEU ou CINÉ,
  sans agrégat** (B1) ;
- **aucune mesure n'est crue avant d'avoir montré qu'elle classe comme Milan**
  (B2) ;
- **prédire des préférences entre paires plutôt qu'une note absolue** (B3).

Pour la faiblesse 1 (voir le mouvement), sa seule brique de mouvement (SISO)
fait pire que nos outils, parce que son lissage efface le départ sec. Pour la
faiblesse 2 (profondeur 2D->3D), rien du tout.

Proposé, pas appliqué : ce rapport ne modifie rien dans `/home/user/Jeux`.
