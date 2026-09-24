# Cerveau d'animateur — audit honnête et plan (2026-09-23)

Demande de Milan : *« fais un plan/audit de ce qu'on vient de comprendre, regarde
s'il faut aller plus loin. Sincèrement tout le travail jusqu'ici c'est assez bof,
pareil pour le dernier trou noir. »* Deux outils sont cités :
`dillydog580/animate-roblox-characters` et le rig *R6 IK + FK Blender Rig V2.22*.

## 0. La cible, reformulée

On veut un **animateur freelance qu'on dirige** : « fais-moi ça », « reproduis
cette vidéo », « fais le poing du dragon ». Il doit livrer **animation + VFX**
au niveau des jeux battlegrounds (TSB) : détaillé, fluide, lisible en jeu.

Le cerveau doit **apprendre** de tout ce qu'on lui donne : packs, vidéos, retours.
Il ne doit pas **se figer** sur une recette. Ce qui fait un bon poing ne vaut pas
forcément pour un déplacement.

## 1. Pourquoi le résultat est « bof » : constat, avec preuves

1. **On fabrique des cinématiques, pas des animations de jeu.** J'ai mesuré le
   pack premium qu'on possède déjà (`battleground_animation_pack_v1.0.1.rbxm`,
   19 animations, 842 keyframes, bakées à 60 Hz) :

   | catégorie | animations | durée |
   |---|---|---|
   | coups M1 | M1_1 à M1_4 | 0,65-0,70 s |
   | réaction victime | Hit 1-3 | **0,22-0,27 s** |
   | garde touchée | Block Hit | 0,20 s |
   | dashes | Side/Forward/Back | 0,53-1,23 s |
   | capacités | Uppercut, Downslam | 0,81-1,08 s |
   | cycles | Idle, Walk, Run, Block Idle | 0,65-1,10 s |

   Le trou noir dure 8,2 s. C'est une scène caméra, jugée comme un film. Le
   niveau TSB se joue sur des clips de moins d'une seconde, lisibles depuis la
   caméra de jeu.
2. **On pose à l'aveugle.** Les poses sont des angles d'Euler tapés dans du
   Python. On ne les regarde jamais une par une de face et de profil. Preuve :
   l'inversion d'axes (le torse penchait en arrière au lieu de l'avant) est
   passée inaperçue pendant une dizaine de prototypes.
   `animate-roblox-characters` impose au contraire un rendu de face et de
   profil, plus une critique écrite, **après chaque pose**. Le rig V2.22 a ses
   faces étiquetées F/B/L/R justement pour ça.
3. **Nos mesures prouvent l'absence de défauts, pas la qualité.** Le 23/23 de
   l'audit ne dit pas que l'animation est bonne. Les seuils ont été choisis par
   moi, sans calibration. Rien ne mesure :
   - le contraste de timing (tenues et claquements) ;
   - la lisibilité de la silhouette ;
   - l'amplitude ou la durée par rapport à de vraies animations pro.
4. **Le pack premium n'a servi qu'une fois**, pour trois amplitudes de M1_1.
   C'est exactement le « copier bêtement » à éviter : un chiffre lu une fois,
   jamais versé dans le cerveau.
5. **Les VFX ne sont pas du Roblox.** Ils n'existent que dans un aperçu
   Three.js, donc impossible de les mettre en jeu. Un freelance livre des
   ParticleEmitter, Beam et Trail, avec textures et Attachments, plus le script
   qui les déclenche.
6. **Il n'y a pas de victime.** Dans TSB, une technique, c'est un attaquant et
   une victime synchronisés (réaction, projection, atterrissage). La vidéo
   « Pro » envoyée montre exactement ça : coup en fente basse, impact rouge,
   mannequin projeté qui retombe au loin. Nos mannequins sont animés à la main,
   sans système de réaction.
7. **Rig maison au lieu du rig standard.** V2.22, c'est le rig des animateurs
   pro : IK/FK, pole targets, faces étiquetées. C'est celui de la vidéo : le
   contrôleur `MasterController` est visible à l'écran. On en a reconstruit un
   morceau (IK des jambes) en Python.
8. **L'aperçu ne ressemble pas au rendu Roblox.** Éclairage et matériaux
   diffèrent, donc on ne juge pas le mouvement comme en jeu.

Correction de ma part : au tour précédent, j'avais lu la vidéo « Pro » comme
une rotation sur soi suivie d'une auto-projection. C'était faux. En relisant
les frames en grand : le personnage est animé dans Blender avec le rig V2.22,
face à un mannequin jaune, puis le résultat en jeu montre le coup, l'impact et
la victime projetée.

## 2. Ce que les deux outils apportent, et leurs limites ici

### `dillydog580/animate-roblox-characters`

Cloné et relu en entier : `SKILL.md`, `references/`, `scripts/`.

- **Ce que c'est** : une méthode d'animateur plus des scripts Blender. La
  méthode suit ces étapes :
  1. un brief ;
  2. les poses clés (anticipation, action, suite du geste, retour ;
     pour la locomotion : contact, bas, passage, haut) ;
  3. un blocking en clés constantes ;
  4. le Graph Editor en Bézier ;
  5. le mouvement secondaire ;
  6. l'audit (pied planté ≤ 0,02 stud, boucle ≤ 0,1°) ;
  7. l'export `.rbxanim`, puis un GIF.
- **Ce qu'on reprend** :
  - la boucle **pose → rendu face et profil → critique → correction** avant
    d'interpoler ;
  - l'ordre de pose : bassin et torse, puis jambes et appuis, puis bras,
    puis tête ;
  - l'interdiction du linéaire en final ;
  - la liste des « erreurs typiques d'IA ».
- **Limites** :
  - Il exige un Blender graphique piloté par MCP et refuse le mode
    `--background`. Ici on n'a que `bpy` 5.0.1 sans écran : on reprend la
    méthode, pas ce garde-fou.
  - Il ne contient **aucune connaissance de style** (aucun corpus, aucun chiffre
    TSB). C'est une discipline, pas un cerveau.

### R6 IK + FK Blender Rig V2.22

- Le rig est hébergé sur devforum.roblox.com, et ce domaine est **refusé par le
  proxy de ce sandbox**. Revérifié aujourd'hui : `connect_rejected`.
- **Solution** : Milan télécharge les deux fichiers du post DevForum,
  `Blender R6 Rig.blend` et `Studio R6 Rig.rbxm`, et les envoie ici comme la
  vidéo. On vérifie alors les SHA-256 publiés par dillydog580 (`ff75c44b…edcdc8`
  et `a85e1ce1…93444`), puis on ouvre le fichier avec l'auto-exécution des
  scripts désactivée.
- **Ensuite** : on pose les contrôles IK/FK via `bpy`, et on fait les rendus de
  face et de profil avec les faces étiquetées.

## 3. Ce qu'il faut ajouter : l'architecture cible

| couche | rôle | existe ? |
|---|---|---|
| **A. Corpus** | chaque source ingérée devient une fiche normalisée (voir détail sous le tableau) | non |
| **B. Taxonomie** | catégories de technique, chaque connaissance y est rattachée | non |
| **C. Principes / statistiques** | principes universels (arcs, chevauchement, équilibre, appuis) séparés des chiffres par catégorie (durées, ratio anticipation/action, amplitudes, dépassement) | principes seulement |
| **D. Revue de pose visuelle** | rendu de face, de profil et en caméra de jeu pour chaque pose clé, faces étiquetées, critique écrite | non |
| **E. Mesures de qualité** | distance à la distribution de la catégorie ; contraste de timing ; lisibilité de silhouette | non (défauts seulement) |
| **F. Livrable Roblox complet** | détail sous le tableau | animation seulement |
| **G. Attaquant + victime** | réactions tirées du corpus (Hit, Block Hit), projection balistique, atterrissage, synchronisation par marker | non |

- **Fiche du corpus (A)** : catégorie, rig, fréquence d'images, durée, phases
  détectées, courbes de vitesse par membre, amplitudes, résultats d'audit,
  provenance.
- **Livrable Roblox complet (F)** :
  - KeyframeSequence de l'attaquant et de la victime, avec des
    `KeyframeMarker` (`hit`, `vfx_*`) ;
  - VFX en instances Roblox (`.rbxmx` : Attachment, ParticleEmitter, Beam,
    Trail, textures) ;
  - un module Luau qui joue l'animation, les VFX, le hitstop et les secousses
    de caméra sur les markers.

La règle anti-blocage, pour que le cerveau apprenne sans se figer :

- **Aucune constante globale.** Chaque chiffre appris est lié à une catégorie
  et à une phase, et stocké comme une distribution (médiane, plage, nombre
  d'exemples), jamais comme une seule valeur.
- **Une catégorie avec trop peu d'exemples est signalée.** Le cerveau le dit
  et retombe sur les principes universels, au lieu d'extrapoler depuis une
  catégorie voisine.
- **On ne copie jamais un chiffre d'une source directement dans un
  prototype.** Il passe d'abord par le corpus.

Taxonomie v1 proposée : frappe légère (M1), frappe lourde ou finisher,
dash/déplacement ponctuel, locomotion cyclique, réaction/victime, garde,
aérien, charge/incantation, cinématique. Le pack couvre déjà cinq de ces neuf
catégories.

## 4. Plan séquencé

| # | étape | sortie vérifiable |
|---|---|---|
| 0 | ✅ **fait (2026-09-23)** — fichiers reçus, empreintes identiques ; rig piloté headless par `v222_rig.py` (voir `RIG_V222.md`) | hashes identiques à ceux publiés |
| 1 | ✅ **fait (2026-09-24)** — 19 animations du pack mesurées et rangées (`corpus/`, `taxonomy.py`) ; `audit.calibrated_verdict()` remplace les seuils fixes pour les catégories du corpus ; nos protos comparés (voir `corpus/README.md`) | écart chiffré entre nos protos et le pro, catégorie par catégorie |
| 2 | Outil de revue de pose : rendu face/profil/3-4 ✅, **export depuis le rig ✅, deux rigs par scène ✅** (2026-09-23, voir `RIG_V222.md`) ; reste la caméra de jeu et la critique écrite systématique | planches de revue committées |
| 3 | ✅ **fait (2026-09-24)** — `experiments/r6_m1_v222` : M1 0,65 s + réaction 0,22 s sur deux rigs V2.22, contact exact, 32/38 et 29/38 mesures dans la plage pro, export avec marker `hit` et jambes à poids 0 | distance au corpus, aller-retour moteur |
| 4 | ✅ **fait (2026-09-24)** — `r6_m1_v222/output/M1_Technique.rbxmx` : mannequins, animations à marqueurs, module Luau (hitstop, flash, étincelles, onde de choc, traînée, recul, secousse), démo ; sens vérifié sur les fichiers, le code Luau exécuté et le package relu | `.rbxmx` qui se charge ; aperçu fidèle |
| 5 | **Test de généralisation** : une catégorie jamais travaillée (dash ou marche), sans réglage à la main | audit vs corpus de la bonne catégorie |
| 6 | ✅ **produit (2026-09-24)** — brief libre « poing du dragon » : `experiments/r6_poing_dragon` (proposition : `SCENE_POING_DU_DRAGON.md`). Technique ultime de 8,8 s sur deux rigs V2.22 : animation, caméra, VFX, effets d'écran, planches manga, package Roblox, module Luau testé, lecteur jouable. En attente de la revue de Milan (critère : niveau de la vidéo « Pro ») | revue de Milan |
| 7 | Nourrir en continu : chaque pack, vidéo ou retour devient une fiche du corpus | le corpus grossit, les seuils bougent avec lui |
| 8 | **Scène à venir, demandée par Milan (2026-09-24)** : un combat à deux dans le style IMPACT HAVEN, « beaucoup plus dynamique ». Fiche mesurée dans `corpus/REFERENCES_VIDEO.md` : 19 impacts en 8 s ; carte silhouette + carte blanche ; tenue **avant** le choc et saut de pose caché par les cartes ; corps acrobatiques ; caméra fixe et large. Pas encore commencée | revue de Milan |

## 5. Risques, dits franchement

- **Pas de Roblox Studio ici.** On ne verra jamais le rendu exact du jeu.
  L'aller-retour par l'équation du moteur reste notre garde-fou pour
  l'animation. Pour les VFX, on vérifie la structure des instances, pas leur
  rendu réel.
- **Corpus petit** : un pack, 19 animations. Les statistiques par catégorie
  seront fragiles tant qu'on n'aura pas plus de sources. github.com est
  accessible ; devforum.roblox.com et create.roblox.com ne le sont pas.
- **Vidéos** : reconstruire des poses 3D à partir d'une vidéo n'est pas fiable.
  On en tire le **timing** (tenues et claquements, mesurés image par image à
  60 fps) et des poses annotées, pas des angles exacts.
- **Licences** : ni le pack ni le rig n'ont de licence de redistribution. Le
  dépôt stocke les **mesures dérivées**, jamais les fichiers source (comme le
  fait dillydog580).
