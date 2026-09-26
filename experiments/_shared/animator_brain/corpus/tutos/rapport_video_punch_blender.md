# Étude visuelle : « Expert Roblox Blender/Moon Punch Animation tutorial » (xkHILCmgbig, 1005 s)

Dossier de travail : `tutos_v/work_nate/` (abrégé `W/` ci-dessous).
- `W/f4/t_XXXX.png` : une image toutes les 4 s. `W/s1/t_XXXX.png` : une image par seconde (le nom = temps en s).
- `W/end30/e_NNNN.png` : toutes les images de 960 s à la fin (e_n = 960 + (n-1)/30 s).
- `W/sheets/` : planches (f4_*, tl_* = frises de timeline, loopA/loopB = coup final image par image, sel_* = moments choisis).
- `W/poses/` : images de preuve sauvegardées (listées en section 2).

Méthode et limites : la détection de changement de plan (seuil 0,25) n'a donné que 6 coupes (298 s, 948-954 s). C'est une
capture d'écran continue de Blender, **en accéléré (time-lapse) pendant le travail**, puis à vitesse réelle pendant les lectures
finales. Pas de son, pas de voix : **tout ce qui est « enseigné » tient en 5 textes incrustés** plus ce que montrent l'UI et le
résultat. Pas d'OCR : j'ai lu l'UI moi-même sur des recadrages agrandis, à 640x360, donc certains petits nombres restent flous.

Outil vu à l'écran : Blender, mode Pose, éditeur **Action Editor** (action « KaijoAction »), panneau d'add-on
**« Rbx Animations »** (Rebuild rig / Create IK constraints / Remove IK constraints / Import FBX / Apply armature transform /
Export animation). Canaux (os) : `UpperTorso-3`, `UpperArm.R`, `UpperArm.L`, `Head-3`, `UpperLeg.R`, `UpperLeg.L`, `Control`,
`ArmDEP.R` (lus sur `W/zoom/chan.png`). Le rig est visuellement un R6 à 6 blocs ; chaque face porte une lettre (F=avant, B=arrière,
L=gauche, R=droite, U=dessus), ce qui permet de lire les rotations. **Moon Animator n'apparaît jamais**, malgré le titre. Le carton
d'ouverture dit « Punch tut: Made by myloe » (0-6 s), et non Nate.Animations.

---

## 1) Déroulé (minutage vidéo → ce qui est montré)

Les numéros de clé ont été lus sur la règle de l'Action Editor (planches `W/sheets/tl_00..03.png`, une frise toutes les 16 s).

| Temps vidéo | Ce qu'on voit | Clés présentes (n° d'image Blender) |
|---|---|---|
| 0-6 s | Carton « Punch tut: Made by myloe » | — |
| 8-20 s | Perso au repos, vu de face et de dos, orbite de caméra | 0 |
| 20-92 s | **Construction de la 1re pose clé à l'image 40** (rotations bras/torse/jambes). Texte à 24-28 s : **« Make sure you have good poses »** | 0, 40 |
| 95-99 s | Texte : **« You can go in between keyframes for more detail »**. Ajout d'une clé intermédiaire à 20 | 0, 20, 40 |
| 100-124 s | Vues de profil de l'image 0/5 (repos) pour comparer | 0, 20, 40 |
| 132-212 s | Construction d'une pose à **80** : torse tourné, penché, grand écart des jambes (charge) | 0, 20, 40, 80 |
| 228 s | **Retiming** : les clés ont été déplacées | 0, 20, **30**, **70** |
| 244-356 s | Zoom timeline autour de 60 ; construction du **contact à 62** : bras tendu, torse retourné (300-340 s) | 0, 20, 30, **60, 62** |
| 360-362 s | Clic droit dans le Dope Sheet (menu Copy/Paste/Paste Flipped/Keyframe Type/Interpolation Mode/Easing Mode…), puis opérateur « **Paste Keyframes** » (`W/poses/13_menu_dopesheet_t361.png`) | 20, 30, … |
| 372-580 s | Allers-retours de retouche entre 20, 30, 60 et 62 (charge et contact) | 0, 20, 30, 60, 62 |
| 596-676 s | Poses de **retour** à 80 puis 70 | 0, 20, 30, 60, 62, 70, 80 |
| 692-724 s | Ajout d'un **intervalle à 61** (clé « ••• » 60-61-62) | … 60, 61, 62, 70, 75 |
| 740-756 s | Retour retouché : 75, 80, 85. Déplacement (**Move**, pas seulement rotation) de `UpperArm.L` (`W/poses/12_…t740.png`) | … 60, 61, 62, 75, 80, 85 |
| 772-900 s | Poursuite du suivi / de la récupération (clés vers 80-100), vues rapprochées, rotation « Trackball » | … 60, 61, 62, ~80, ~84, ~100 |
| 916-948 s | **Re-compression du retour** : la fin se resserre | 60, 61, 62, 67, 69, 91 → 60, 61, 62, 64, 66, 91 |
| 962-967 s | Texte **« Almost there! »**, lecture en boucle (l'en-tête du viewport affiche « fps: 61 » à 90) | End passe de 200 à **90** |
| 975-980 s | Texte **« Normal speed: »**, courte lecture de face | 60, 61, 62, 63, 66, 90 |
| 996-1005 s | Texte **« done!! »** : lecture en boucle de profil, puis gros plan (le résultat final) | final ci-dessous |

**Timeline finale** (`W/poses/10_timeline_finale_t1001.png`, recadrage x3 à 1001 s, End = 90) :

| Os | Clés |
|---|---|
| Summary | 0, 20, 30, 60, 61, 62, 63, 66, 90 |
| UpperTorso | 0, 30, 60, 62, 63, 66, 90 |
| UpperArm.R | 0, 30, 60, 62, 63, 66, 90 |
| **UpperArm.L (bras qui frappe)** | 0, 30, 60, **61**, 62, 63, 66, 90 (seul os avec une clé à 61) |
| Head | 0, 30, 60, 62, 63, 66 (pas de 90, lu sur la frise) |
| UpperLeg.R | 0, 30, 60, 62, 63, 66, 90 |
| UpperLeg.L | 0, **20**, 30, 60, 62, 63, 66, 90 (seul os avec une clé à 20) |
| Control, ArmDEP.R | 0 seulement |

Aucun **Graph Editor** n'apparaît sur les planches à 4 s ni sur les images à 1 s : toute l'édition de timing se fait dans
l'Action Editor (déplacement de points).

---

## 2) Poses clés du coup (lecture image par image du résultat final)

Source : la boucle finale, deux passages (`W/sheets/loopA.png` à 999,33-1000,97 s, `W/sheets/loopB.png` à 1000,87-1002,5 s,
recopié dans `W/poses/14_planche_boucle_image_par_image.png`). La boucle 0→90 dure **1,50-1,53 s** (repos à 999,37 → 1000,90 ;
1000,90 → 1002,40), soit **90 images en 1,5 s ≈ 60 i/s**. Une image vidéo (30 i/s) ≈ 2 images Blender. Les numéros de clé
attribués ci-dessous sont donc à ±1 image.
Caméra : profil, le personnage frappe vers la gauche de l'écran. On voit son côté gauche au repos (faces « L »).

| # | Image Blender (≈) | Fichier (plein + `_zoom`) | Ce que je VOIS |
|---|---|---|---|
| 1 | 0 | `W/poses/01_idle_f0_t1000.93.png` | Debout droit, bras le long du corps, de profil. |
| 2 | ~14 (entre 0 et 20/30) | `W/poses/02_debut_rotation_f~14_t1001.17_zoom.png` | Le corps pivote face caméra (on lit « FRONT »). **Les deux bras montent en garde** devant la poitrine, genoux légèrement fléchis. Transitoire presque symétrique. |
| 3 | ~30 (charge atteinte) | `W/poses/03_charge_f~30_t1001.43_zoom.png` | **Charge asymétrique.** Torse tourné d'~90° à l'opposé de la cible (sa face avant « F » face caméra), légèrement penché. **Bras droit (face R verte) horizontal vers la cible**, à hauteur d'épaule (bras de visée/garde). **Bras gauche armé en arrière**, horizontal au-dessus de l'épaule arrière, poing vers l'arrière. Jambe avant verticale sous le corps, **jambe arrière en diagonale vers l'arrière (~30-35° de la verticale)** : grand écart. Tête au-dessus de la jambe avant. |
| 4 | ~58 (fin de la tenue en mouvement) | `W/poses/04_charge_tardive_f~58_t1001.87_zoom.png` | Même charge, légèrement plus enroulée : le dessus du torse (bleu) apparaît davantage, donc le torse bascule un peu plus en avant ; tête plus basse ; bras avant rentré. **Entre ~30 et ~58, la pose ne bouge presque pas** (loopB #16→#30). |
| 5 | ~60-61 (intervalle) | `W/poses/05_breakdown_f~60-61_t1001.90_zoom.png` | Une seule image vidéo. Le torse a tourné et plonge vers l'avant, le bras de frappe passe devant, horizontal, **poing en tête** vers la cible. |
| 6 | ~62 (contact) | `W/poses/06_contact_f~62_t1001.93_zoom.png` | **Torse retourné : on voit son DOS (« BACK »)**, soit environ 180° de rotation depuis la charge. **Torse penché en avant à ~45°**, tête baissée et portée en avant dans l'épaule. **Bras gauche tendu à l'horizontale vers la cible, dans l'axe de l'épaule, et même décollé du torse** (il y a un vide entre le bloc bras et le torse : bras translaté en avant, voir `W/poses/11_…t312.png` et `12_…t740.png`, opérateur « Move »). **Bras libre (droit) ramené haut, contre l'épaule/la tête.** Jambe avant verticale ; **jambe arrière tendue loin derrière, presque couchée (~55-60° de la verticale)**. Silhouette : une longue diagonale du pied arrière jusqu'au torse, prolongée par le bras horizontal. |
| 7 | ~64 | `W/poses/07_retrait_f~64_t1001.97_zoom.png` | Le bras se rétracte déjà, poing plus bas et plus proche. Le reste est inchangé. |
| 8 | ~66 (retour/garde) | `W/poses/08_recul_garde_f~66_t1002.00_zoom.png` | Bras de frappe replié et **remonté au-dessus de l'épaule** (poing haut, derrière la tête). Torse toujours penché en avant, dos à la caméra, jambes toujours en fente. |
| 9 | ~88 | `W/poses/09_tenue_f~88_t1002.37.png` | Quasiment la même pose que 66 (la caméra dézoome pendant ce passage). Puis le passage 90→0 de la boucle ramène d'un coup au repos. |

Autres preuves : `W/poses/11_construction_contact_f62_Move_t312.png` (contact en construction à l'image 62, `UpperArm.L`
sélectionné, opérateur « Move » en bas à gauche), `W/poses/12_Move_UpperArmL_f75_t740.png` (info-bulle « Move selected items »
sur `UpperArm.L` à l'image 75).

Les 4 images les plus parlantes : 03 (charge), 05 (intervalle), 06 (contact), 08 (retour).

---

## 3) Timing / spacing / easing observés

Valeurs lues sur la timeline finale ; cadence ≈ 60 i/s, déduite de la durée de boucle mesurée.

| Segment | Images | Durée à 60 i/s | Nature |
|---|---|---|---|
| Repos 0 → 20 → 30 (charge) | 30 | 0,50 s | Mise en garde puis charge. La clé 20 ne touche que la jambe gauche (pied/appui). |
| 30 → 60 | 30 | 0,50 s | **Tenue en mouvement** : deux poses presque identiques, le perso « s'enroule » lentement. |
| 60 → 61 → 62 | **2** | **0,033 s** | **Frappe.** Rotation du torse d'~180° et bras tendu en 2 images. 61 = intervalle posé sur le seul bras de frappe (contrôle de l'arc). |
| 62 → 63 | 1 | 0,017 s | Clé juste après le contact (tenue d'impact ou début de retrait, impossible à trancher à 30 i/s). |
| 63 → 66 | 3 | 0,05 s | Retrait du bras vers la garde haute. |
| 66 → 90 | 24 | 0,40 s | Tenue en mouvement de la pose de retour, puis fin (End = 90). |

- **Rapport de spacing** : 60 images d'anticipation (~1 s) pour 2 images de frappe et ~27 de retour. Le contraste lent/explosif
  est extrême.
- **Méthode de timing vue à l'écran** : les poses sont d'abord posées avec des écarts larges (0/40, puis 80), puis **resserrées**
  en déplaçant les points (40→30 et 80→70→60 vers 228-276 s). Même chose pour le retour : 80/85/100 → 67/69/91 → 64/66/90
  (916-964 s). Enfin, **End est fixé à 90**.
- **Easing / interpolation** : **non visible.** Aucun graph editor n'est ouvert. Le menu contextuel montre bien les entrées
  « Interpolation Mode (T) » et « Easing Mode (Ctrl E) », mais je ne vois aucun choix fait dedans (l'action lancée est un
  « Paste Keyframes »). Par défaut, Blender interpole en Bézier : c'est une DÉDUCTION, pas une observation. Visuellement, 30→60 a
  l'air d'une dérive douce ; 60→62 est trop court pour que l'easing compte.
- **Clés tenues** : pas de clé dupliquée identique repérée. Les « tenues » sont des tenues en mouvement (deux poses proches, 30/60
  et 66/90).

---

## 4) Règles concrètes que ce tuto enseigne

(T = écrit à l'écran ; V = montré sans être écrit ; D = ma déduction.)

1. **Poser d'abord des poses fortes (T).** Énoncé : « Make sure you have good poses ». Preuve : texte à 24-28 s ; la première
   minute et demie sert à construire UNE pose (image 40) avec seulement 0 et 40 dans la timeline. Quand : avant tout travail de
   timing. Limite : le texte ne dit pas ce qu'est une « bonne » pose. La réponse est dans le résultat (règles 3 à 5).
2. **Ajouter des intervalles pour le détail (T).** Énoncé : « You can go in between keyframes for more detail ». Preuve : 95-99 s,
   ajout de la clé 20 ; plus tard, la clé 61 posée sur le seul `UpperArm.L` (692-724 s ; timeline finale). Quand : quand
   l'interpolation entre deux poses clés ne donne pas le bon trajet (arc du bras, appui du pied). Limite : ici l'intervalle est
   posé **par os**, pas sur tout le corps.
3. **Charge = torse tourné à l'opposé + bras de frappe armé haut en arrière + bras avant pointé vers la cible + fente (V).**
   Preuve : `03_charge…`, `04_charge_tardive…` (1001,43-1001,87 s ; construite vers 132-212 s). Quand : avant tout coup droit.
   Limite : de profil, je ne vois pas de « C » marqué. La compression vient de la rotation et de l'écart des jambes, pas d'un
   dos rond.
4. **Contact = rotation d'~180° du torse (on voit le dos), torse penché ~45°, bras tendu à l'horizontale dans l'axe de l'épaule
   et ALLONGÉ par translation, bras libre ramené contre la tête, jambe arrière tendue loin derrière (V).** Preuve : `06_contact…`
   (1001,93 s), construction à 300-340 s, « Move » sur `UpperArm.L` à 312 s et 740 s. Quand : l'image d'impact. Limite : le bras
   « décollé » du torse est une triche de silhouette, visible ~1 image seulement. Sur un R6 Roblox, il faut que le moteur accepte
   des décalages de position du bras (Motor6D), et pas seulement des rotations.
5. **Le bras libre ne reste pas symétrique (V).** À la charge, il est devant (visée) ; au contact et au retour, il est replié haut
   près de la tête. Preuve : images 03, 06, 08. Quand : toutes les poses clés. Limite : son rôle exact (garde ou contrepoids) n'est
   pas expliqué.
6. **Anticipation longue, frappe en 1-2 images, puis tenue (V).** Preuve : timeline finale (30→60 tenue ; 60-61-62 frappe ;
   66→90 tenue). Quand : coup lourd « one-shot ». Limite : 1 s d'anticipation, c'est trop long pour un M1 de combo façon TSB. Ce
   n'est pas un coup de combo.
7. **Poser large, puis resserrer le timing en déplaçant les clés (V).** Preuve : 40→30, 80→60 (228-276 s) ; 100/85→66/90
   (868-964 s) ; End 200→90 (964 s). Quand : après avoir validé les poses. Limite : aucune valeur cible n'est donnée, c'est
   empirique (lecture en boucle après chaque retouche).
8. **Retour : garder la fente et le penché, ne ramener que le bras (V, D).** Preuve : images 08-09. Le corps reste engagé jusqu'à
   la fin ; le retour au repos n'est pas animé (c'est la boucle qui le coupe). Limite : en jeu, il faudra un vrai blend vers
   l'idle.

---

## 5) Confrontation avec l'hypothèse
« charge = compression en C, contact = ligne du pied arrière au poing avec torse engagé ; TSB relie des poses clés espacées
d'environ 4 images (60 i/s) en interpolation linéaire »

- **Charge = compression en C : partiellement.** La charge est bien comprimée et asymétrique : torse tourné d'~90° à l'opposé,
  léger penché, bras de frappe armé en arrière, bras avant tendu, fente jambe arrière ~30°. En revanche, de profil, la silhouette
  n'est pas un « C » net. Le moteur principal de la charge est la **torsion** (le torse montre sa face avant à la caméra latérale),
  pas l'arrondi. Pour notre défaut « charge en croix symétrique » : ce tuto confirme qu'il faut casser la symétrie (un bras devant,
  un derrière, épaules tournées).
- **Contact = ligne pied arrière → poing, torse engagé : CONFIRMÉ, et même poussé plus loin.** La jambe arrière est quasi couchée,
  le torse penché à ~45° dans le prolongement, le bras est horizontal (et translaté pour allonger la ligne), la tête plonge.
  Ajout : le torse ne se contente pas de s'incliner, il **pivote d'~180°** entre charge et contact (face → dos), et le bras libre
  est ramené contre la tête.
- **Poses espacées d'~4 images à 60 i/s en linéaire : NON CONFIRMÉ par ce tuto** (qui n'est pas TSB). Ici les écarts sont très
  irréguliers : 20, 10, 30, **1, 1**, 1, 3, 24. La frappe elle-même (60→62) fait **2 images**, pas 4. L'interpolation n'est pas
  visible (probablement Bézier par défaut, non vérifié). Le seul point commun est l'ordre de grandeur « quelques images à 60 i/s »
  pour le passage charge→contact. Ce tuto ne dit rien sur TSB.

---

## 6) Incertitudes

- **Cadence 60 i/s** : déduite de la durée de boucle (90 images ≈ 1,5 s de vidéo) en supposant la vidéo à vitesse réelle pendant
  la lecture finale. Le compteur « fps: » du viewport affiche des valeurs de 61 à ~90, ce qui est incohérent avec une cadence cible
  de 60 (lecture floue à 640x360, ou time-lapse partiel). Je n'ai pas vu le réglage Frame Rate de la scène.
- **Correspondance image vidéo ↔ image Blender** : ±1 (30 i/s pour 60). Les poses « 61 » et « 63 » ne sont pas isolables avec
  certitude. L'image 05 est entre 60 et 61, l'image 07 entre 63 et 64.
- **Numéros de clé** : lus sur la règle agrandie, fiables à ±1 pour les frises zoomées, ±2 pour les vues larges (ex. 90 contre 91
  selon la frise).
- **Angles** (~90°, ~180°, ~45°, ~30°, ~60°) : estimés à l'œil d'après les lettres des faces. Pas de valeurs numériques de rotation
  visibles (le panneau Transform n'est jamais ouvert).
- **Bras « décollé »** : l'opérateur « Move » est vu sur `UpperArm.L`, mais je ne peux pas chiffrer la translation.
- **Rôle de la clé 20** (jambe gauche seulement) : non élucidé visuellement (appui ou petit pas probable, non vérifié).
- **Easing, interpolation, graph editor** : jamais montrés. Le menu contextuel entrevu à 361 s aboutit à « Paste Keyframes » ;
  je ne sais pas quelles clés ont été copiées.
- Échantillonnage à 1 s pour les textes : un texte affiché moins de 1 s aurait pu m'échapper. Les 5 textes trouvés tiennent
  chacun 3 à 5 s.
