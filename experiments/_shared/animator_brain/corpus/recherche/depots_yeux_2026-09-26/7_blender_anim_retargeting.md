# Dépôt 7 : Blender Animation Retargeting (Mwni) : étude pour les « yeux » du cerveau

Date : 2026-09-26. Lecture de TOUT le code (1 879 lignes) plus un test réel sur
notre export `usc_attaquant.rbxmx` dans bpy 5.0.1. Rien n'a été modifié dans
`/home/user/Jeux` ; le dépôt est cloné en lecture seule dans
`/home/user/ext/blender-animation-retargeting`. Les scripts de test sont dans
le scratchpad : `c4/retarget_test/`.

## 0. Verdict court

- Ce n'est **pas un œil**. C'est un outil de CORRECTION et de TRANSFERT entre
  deux armatures Blender (Milan l'avait bien classé). Il ne mesure rien, ne
  regarde aucune vidéo, ne produit aucun chiffre ni aucune image de jugement.
- Sur un R6, le transfert d'os à os est **exact** : 0,000° d'erreur, mesurée
  sur 400 images de notre attaquant, y compris vers une cible aux axes de
  repos tournés de 90° et aux membres de longueurs différentes.
- La correction « pieds/mains » par IK est **contre-productive sur un R6**.
  Mesuré : pour remettre au sol des pieds qui flottent de 0,46 stud, elle
  penche le TORSE de 42 à 45°, parce que la chaîne IK inclut forcément le
  torse (une jambe R6 est un seul os).
- Pour nos 5 faiblesses : aucun apport direct. Deux retombées indirectes
  valent la peine (§5) : la mesure du glissement des pieds plantés, déjà
  écrite chez nous mais jamais branchée sur « Un seul coup », et une règle
  de conversion vers R6 par DIRECTION de membre, à retenir si un jour on
  convertit un squelette humain (mocap, pose estimée sur une vidéo) en R6.

## 1. Le bon dépôt

- **`Mwni/blender-animation-retargeting`**, https://github.com/Mwni/blender-animation-retargeting
  (732 étoiles, 70 forks, 14 issues ouvertes ; créé le 2020-02-27 ;
  branche par défaut `stable`).
- Une recherche GitHub sur le nom ne sort que 2 dépôts. L'autre,
  `ujs204/blender-animation-retargeting` (0 étoile, créé en 2025-09), reprend
  la même description mot pour mot : c'est une copie. On retient donc Mwni,
  qui correspond aussi à l'indice donné.
- **Dernier commit** : `424f08b`, 2026-08-09 09:45 +0200, « bump minor
  version » (v2.4.0). Le projet est donc maintenu.
- **Licence** : `SPDX:GPL-3.0-or-later`, déclarée dans `blender_manifest.toml:8`.
  Le dépôt ne contient **aucun fichier LICENSE** : la licence n'existe que
  dans le manifeste. Conséquence : on peut **utiliser** l'addon comme outil ;
  en revanche, **copier son code** dans notre dépôt nous ferait passer sous
  GPL. Les idées utiles tiennent en quelques lignes de maths : on les
  réécrit, on ne copie rien.
- **Dépendances** : Blender ≥ 4.4 (manifeste), Python pur (`bpy`,
  `mathutils`, `difflib`). Ni GPU, ni modèle, ni réseau. **Il tourne sur
  notre bpy 5.0.1 sans rien installer** (vérifié).

## 2. Ce qui est RÉELLEMENT implémenté (code, pas README)

| module | ce qu'il fait vraiment |
|---|---|
| `mapping.py` | liste de paires `os source -> os cible`, faite à la main ; « Guess » = similarité de NOMS (`difflib.SequenceMatcher`, l.116) + synonymes (l.8 : clavicle/shoulder, thigh/upperleg…) + regroupement gauche/droite sur les noms. Le README parle de « name and topology » : **aucune topologie n'est utilisée**, seulement les noms. `get_intermediate_bones` (l.224) : les os PARENTS non mappés entre deux os mappés. |
| `alignment.py` | l'utilisateur pose la cible pour imiter la pose de repos de la source ; « Apply » enregistre par os `rest = bone.matrix` et `offset = bone.matrix_basis` (l.60-65). |
| `drivers.py` | le cœur du transfert. Sur chaque os cible, 6 drivers Python (loc xyz, rot xyz), qui appellent des fonctions mises dans `bpy.app.driver_namespace` (l.82-85). `drive_bone_mat` (l.180-238) : `mat = offset @ D⁻¹ @ (échelle_cible⁻¹ · échelle_source) @ basis_source @ D`, avec `D = rot(source_repos)⁻¹ @ rot(cible_alignée)` (l.218-236). C'est une **conjugaison de la transformation locale** par l'écart des repères de repos. Les os intermédiaires non mappés voient leur delta ajouté à l'os mappé suivant (l.187-211). La cible est forcée en **Euler XYZ** (l.91). |
| `ik.py` | « Correct Feet / Hands » : une contrainte IK Blender sur l'os « pied » ou « main », avec `chain_count` = nombre de parents jusqu'à l'« origine » + 1 (l.150-163), une cible vide placée à `longueur d'os` sur l'axe Y (l.121), plus un cube de contrôle pour décaler la cible à la main. **Le pôle est commenté** (l.124, 147, 167) : aucun contrôle du sens du genou ou du coude. |
| `drivers.py` `drive_ik_target_mat` (l.252-282) | la cible IK = la transformation MONDE de l'os source, recalée de repos source à repos cible, plus le cube de contrôle. Rien n'est adapté à la longueur des jambes. |
| `baking.py` | `bpy.ops.nla.bake` avec `visual_keying=True` entre la première et la dernière clé de la source (l.90-94) ; option « Linear » : toutes les clés passent en LINEAR (l.103) ; import FBX en lot. |
| `savefile.py` | configuration en JSON (`.blend-retarget`) : paires d'os, matrices rest et offset, membres IK, matrices des deux armatures. |

**Maturité** : environ 1 900 lignes, aucun test, pas d'API en script (tout
passe par l'interface et des propriétés). **Bugs trouvés en lisant, dont
un confirmé à l'exécution :**

1. `context.py:35-36` : `bpy.ctx.object`, qui n'existe pas. **Confirmé** :
   choisir l'os d'un membre IK lève `AttributeError: module 'bpy' has no
   attribute 'ctx'`. L'exception est avalée, et le membre reste inactif tant
   qu'on ne décoche puis recoche pas la case (mesuré : `enabled` False, puis
   True après la bascule).
2. `mapping.py:387` appelle `handle_source_update`, qui n'existe pas (la
   méthode s'appelle `handle_source_change`, `context.py:80`). Le bouton
   « Use anyway » plante.
3. `mapping.py:251` appelle l'opérateur `'retarget.use_invalid_source_anyway'`,
   alors qu'il est enregistré sous `'mappings.use_invalid_source_anyway'`
   (l.382). En plus, la ligne additionne deux retours d'appels de layout
   (`label(...) + operator(...)`).
4. Piège d'usage (pas un bug, mais il m'a trompé, §4) : en script, si l'on
   saute l'étape « Apply » de l'alignement, `rest` reste l'identité et le
   transfert devient faux sans le moindre message d'erreur.

## 3. Entrées / sorties

- **Entrée** : deux armatures Blender dans la même scène, dont la source
  porte une Action. Pas de vidéo, pas d'image, pas de KeyframeSequence.
- **Sortie** : des drivers vivants sur la cible, ou une Action cuite (Euler
  XYZ, Bézier ou Linear). Pour Roblox, il faut ensuite notre propre chaîne
  (lire les matrices des parts, puis `roblox_export.write_kfseq`).

## 4. Test réel sur nos données (≈ 10 min de travail, ~3 s de calcul par essai)

**Montage** (`c4/retarget_test/test_retarget.py`) :

1. `usc_attaquant.rbxmx` est échantillonné comme le joue le moteur
   (`vues.lire_kfseq`, 60 i/s, 400 premières images) ;
2. une armature SOURCE R6 de 6 os (Torse racine, Tête, 2 bras, 2 jambes ;
   tête d'os à l'épaule ou à la hanche) est animée image par image.
   Fidélité vérifiée : **0,0000 stud et 0,000°** d'écart avec notre export ;
3. une armature CIBLE R6 : identique, ou bras ×1,3 et jambes ×0,8, ou roll
   de 90° sur les bras ;
4. l'addon est enregistré tel quel (copie non modifiée), puis on crée les
   paires d'os, on fait l'alignement, les drivers, et la cuisson
   (`baking.transfer_anim`) ;
5. on mesure l'erreur d'orientation de chaque part (monde, corrigée du
   repos) et la hauteur et le glissement des pieds.

**Premier résultat, FAUX, et c'était ma faute** : de 104 à 180° d'erreur,
même avec une cible identique. Diagnostic : j'avais sauté `store_alignments`,
donc `rest` valait l'identité. Avec le parcours de l'interface (Set Up puis
Apply), c'est exact. Je le garde ici parce que c'est exactement le type de
piège qui donnerait un faux chiffre à nos yeux (§6).

**Résultats (parcours correct)** :

| cible | erreur de rotation max (6 parts, 400 images) | pieds de la cible |
|---|---|---|
| identique | 0,000° | identiques à la source |
| roll des bras +90° | 0,000° | identiques |
| bras ×1,3, jambes ×0,8 | 0,000° | **flottent** : point le plus bas 0,46 (G) et 0,58 (D) stud, jamais au sol |
| idem + roll 90° | 0,000° | idem |
| jambes ×0,8 + « Correct Feet » (origine = Torse) | 0,000°, rien ne change | toujours 0,46 et 0,58 : **l'IK n'a aucun effet**, car sa cible suit la HANCHE source (la tête de l'os jambe), pas le pied |
| idem + cube de contrôle abaissé de 0,46 stud (le geste de l'animateur) | Torse **penché de 42 à 45°** | pieds à 0,08-0,20 stud |
| cube abaissé de 1,06 stud | Torse penché de **55 à 70°** | pieds de -0,48 à +0,02 (sous le sol) |

Lecture :

- la cible IK = `longueur d'os` le long de l'os (`ik.py:121`). Sur un
  humanoïde, l'os « pied » commence à la cheville, donc on copie la
  cheville. Sur un R6, l'os « jambe » commence à la hanche : l'IK copie la
  hanche, ce qui ne corrige rien ;
- `chain_count = 2` (mesuré dans les contraintes créées) : la chaîne
  contient le Torse. Pour déplacer un pied, le solveur ne peut que faire
  tourner la jambe rigide ET le torse, et les deux jambes se disputent le
  même torse ;
- la vraie correction R6 d'un changement de longueur de jambe, c'est de
  **baisser la racine** (hauteur de hanche), puis de re-résoudre les
  jambes en gardant le bassin libre. C'est ce que fait déjà notre
  `constraints.plant_pose` / `foot_lock_pass` (`constraints.py:1-30`,
  mesuré sur black_hole : 2,96 studs de glissade corrigés).

**Retombée du test sur NOTRE anim** (`c4/retarget_test/glisse_pieds.py`,
mesure directe dans l'export, sans l'addon) :

- première mesure, lâche (bas-centre de la jambe à moins de 0,25 stud) :
  « 12,18 studs de glissement » pour le pied gauche. **Chiffre trompeur** :
  il comptait la glissade d'élan, où le pied rase le sol ;
- mesure stricte (coin le plus bas du bloc à moins de 0,1 stud ET vitesse
  verticale inférieure à 0,5 stud/s) :
  - pied G planté de 3,22 à 4,43 s : dérive 1,02 stud ;
  - pied G planté de 4,63 à 12,5 s : dérive 1,37 stud (chemin 2,70) ;
  - pied D planté de 2,90 à 4,47 s : dérive 0,28 ; de 4,73 à 12,5 s : 0,69 ;
  - pied D planté de 0 à 2,62 s : 0,004.
- Ce sont des **mesures, pas un verdict**. La fiche `UN_SEUL_COUP.md` prévoit
  une glissade (l.106-107) et une phase « armé » à 3,9-4,35 s (l.75) ; il
  faut revoir ces fenêtres à vitesse réelle pour dire si la dérive est voulue
  (poussée, recul après le coup) ou si c'est un patin involontaire.
  `verification.json` d'« Un seul coup » ne contrôle que la HAUTEUR des
  pieds (`sol.plus_bas_*`), jamais leur glissement. `audit.contact_report`
  (`audit.py:299-340`), qui fait exactement cette mesure, n'est pas appelé
  par les scripts d'« Un seul coup » (grep : aucune occurrence).

## 5. Briques utiles, faiblesse par faiblesse

| brique | faiblesse | forme adaptée R6 / Roblox | coût | intérêt |
|---|---|---|---|---|
| **Patin des pieds plantés, affiché par appui** : fenêtres, dérive max, chemin ; le thème de l'addon (le foot-sliding est le 1er défaut d'un transfert) | 3 (juger au vrai rendu), 4 (surestimation) | brancher `audit.contact_report` (ou `glisse_pieds.py`) dans `verify_export.py` d'« Un seul coup » et des futures productions ; afficher la DÉFINITION (seuils) à côté du chiffre ; sur la bande `durees.py` ou la planche, surligner les fenêtres d'appui qui dérivent, pour aller les voir à vitesse réelle | 0,5 h (le code existe) | moyen |
| **Test d'aller-retour de transfert (identité = 0)** : avant de croire une conversion d'espace, la passer sur un cas où le résultat est connu | 4 (faux chiffres), 2 (repères) | déjà présent pour l'export moteur (`aller_retour_max` = 3e-14) ; à étendre à toute nouvelle conversion (reconstruction `geo_pose`, lecture des `.rbxm` pros, futur import non-R6) : cas identité, cas roll 90°, cas proportions | 0,5 h par conversion | moyen |
| **Conjugaison par l'écart de repos** `D⁻¹ · T · D` (drivers.py:218-236) | 2 (profondeur, repères) | seulement si l'on convertit un jour un squelette NON R6 (mocap, Mixamo, pose 3D estimée sur une vidéo) : c'est la façon propre d'exprimer une rotation d'un repère d'os dans un autre ; 10 lignes numpy à réécrire (GPL : ne pas copier) | 1 h | faible aujourd'hui |
| **À INVERSER : copier la rotation de l'os** → pour le R6, **copier la DIRECTION du membre** (épaule→poignet, hanche→cheville) + la torsion | 2 | sur un squelette avec coudes et genoux, mapper « bras supérieur → Right Arm » copie la rotation du HAUT du bras et ignore l'avant-bras : le poing R6 part à côté de la vraie main. La bonne réduction R6 vise la main (swing) puis garde la torsion. Notre `geo_pose` (az/el du membre dans le repère du torse) est déjà du bon côté : garder ce principe | 2 h si besoin un jour | faible (préventif) |
| **Couche de « triche » par plan** (le cube de contrôle : un décalage monde posé PAR-DESSUS l'anim transférée, sans toucher la base) | 5 (jeu contre cinématique) | idée d'organisation, pas un œil : l'anim de JEU reste propre (base), et chaque plan de cinématique porte sa couche d'offsets (poing avancé vers la caméra, buste plus tourné) ; on MESURE l'écart base/plan (degrés, studs) pour savoir combien on triche, sans seuil | 3-4 h (pipeline) | faible à moyen |
| Configuration déclarative JSON (paires d'os, matrices rest/offset) | aucune | inutile : nos 6 parts sont fixes | 0 | nul |
| Devinette des paires par noms (SequenceMatcher + synonymes) | aucune | inutile en R6 | 0 | nul |
| IK pieds/mains de l'addon | aucune (outil de correction) | **à ne pas utiliser en R6** : la chaîne inclut le torse (42-45° de torse pour 0,46 stud de pied, mesuré) ; notre `constraints.py` (bassin résolu) est la bonne forme | 0 | nul, ou négatif |

Sur les faiblesses 1 (mouvement à vitesse réelle), 2 (profondeur à partir
d'une vidéo), 3 (cadrage réel), 4 (surestimation), 5 (jeu contre
cinématique), le dépôt **n'apporte aucun mécanisme de regard**. Tout ce qui
est listé plus haut est une conséquence de l'étude (le test), pas une
fonction de l'addon.

## 6. Pièges

- **Faux sentiment d'objectivité, vécu deux fois pendant ce test** :
  1. un transfert faux à 180° a d'abord ressemblé à « l'addon est cassé ».
     C'était une étape d'alignement sautée, sans le moindre message. Toute
     conversion doit d'abord passer un test où la réponse est connue
     (identité = 0) avant qu'on croie un seul de ses chiffres ;
  2. « 12 studs de glissement » contre « 1,37 stud » sur la même anim :
     seule la définition du pied planté changeait. Un chiffre de patin sans
     sa définition, sans ses fenêtres et sans un regard à vitesse réelle
     trompe. On affiche donc toujours les fenêtres, et on ne donne aucun
     verdict (conforme au NOYAU).
- **« Correction » qui abîme la pose** : l'IK pieds d'un outil générique
  appliquée à un R6 déplace le TORSE, qui porte tout le mouvement (« tu
  n'animes que les bras », « le corps porte le mouvement »). Un outil de
  correction peut donc dégrader silencieusement la lecture de la pose.
- **Euler XYZ + Bézier à la cuisson** (drivers.py:91, baking.py:103) :
  retournements possibles entre deux clés, alors que Roblox interpole en
  quaternion (slerp). Si on s'en servait un jour, cuire à chaque image et
  relire en matrices, jamais les courbes Euler.
- **Drivers Python** : dans Blender avec interface, un fichier rouvert sans
  « Auto Run Python Scripts » garde des drivers morts (en `bpy` headless,
  ils ont bien tourné pendant notre test). Dépendance fragile pour une
  chaîne automatisée.
- **GPL-3.0** : ne rien copier dans le dépôt Jeux ; réécrire les 10 lignes
  de maths si besoin.
- **Dépendance lourde ?** Non : Python pur, sans GPU. Le coût réel est
  ailleurs : c'est un outil d'interface (propriétés et opérateurs), qu'il
  faut piloter en imitant l'interface (et on tombe sur ses bugs 1-3).

## 7. Recommandation pour nous

1. **Ne pas intégrer l'addon** dans la chaîne. Notre R6 va déjà d'un bout à
   l'autre en R6 exact (`roblox_export`, rig V2.22) : il n'y a rien à
   « retargeter ». Son IK est inadaptée à des blocs rigides.
2. **Prendre la leçon et pas le code** : brancher la mesure du patin des
   pieds plantés (déjà écrite : `audit.contact_report`) dans la
   vérification d'« Un seul coup » et des productions suivantes, affichée
   par fenêtre avec sa définition, sans seuil bloquant. Puis revoir les deux
   fenêtres mesurées (G 3,22-4,43 s, 1,02 stud ; G 4,63-12,5 s, 1,37 stud)
   à vitesse réelle, pour décider si c'est voulu.
3. Garder en réserve la règle « direction du membre, pas rotation de l'os »
   pour le jour où l'on convertira un squelette humain (mocap, pose estimée
   sur une ref) en R6. Et toujours le cas identité = 0 d'abord.

## Annexe : commandes du test

```bash
cd /tmp/claude-0/-home-user-Jeux/4796ac9e-8e41-51f7-91c4-7b92a6a187d0/scratchpad/c4/retarget_test
SA=1   SL=1   RO=0  python3 test_retarget.py plain 400   # contrôle identité -> 0,000°
SA=1.3 SL=0.8 RO=90 python3 test_retarget.py plain 400   # proportions + roll -> 0,000°, pieds flottants
SA=1   SL=0.8 RO=0  python3 test_retarget.py feet  400   # IK pieds : bug bpy.ctx, chain_count 2, sans effet
python3 glisse_pieds.py /home/user/Jeux/experiments/r6_un_seul_coup/output/usc_attaquant.rbxmx 0.1
```
(`animation_retargeting/` dans ce dossier = copie non modifiée du dépôt,
renommée pour être importable ; SA/SL = échelle des bras/jambes de la
cible, RO = roll des bras en degrés.)
