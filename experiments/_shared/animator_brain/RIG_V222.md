# Rig « R6 IK + FK Blender Rig V2.22 » (Aeresei) — fiche mesurée

Milan a fourni les deux fichiers du post DevForum (2026-09-23) :
`Blender R6 Rig.blend` et `Studio R6 Rig.rbxm`. La page du post, avec sa
partie tutoriel, reste **illisible ici** : `devforum.roblox.com` est refusé
par le proxy, via curl comme via WebFetch. Ce qui suit est donc lu **dans le
fichier lui-même** (armature, contraintes, drivers, scripts embarqués) et
mesuré par `v222_rig.py`. Rien n'est tiré du texte du tutoriel.

Les binaires ne sont **pas** versionnés : aucune licence de redistribution
n'est indiquée. On les référence par leur empreinte SHA-256.

## Authenticité et sécurité

- `.blend` SHA-256 `ff75c44b…edcdc8` et `.rbxm` SHA-256 `a85e1ce1…93444` :
  identiques aux empreintes publiées par `dillydog580/animate-roblox-characters`.
- Les 5 scripts embarqués (`RigBootstrap`, `RigSelector`, `RigSettings`,
  `RigUtilities`, `RigEvents`) ont des empreintes identiques aussi. Ils
  n'importent que `bpy` et `mathutils`. Leurs `exec` ne chargent que les autres
  blocs texte du fichier. Aucun accès réseau, aucun processus.
- Ces scripts ne font **que de l'interface** : liste « Active Rig », panneau
  « Rig Settings », « Utilities » (attacher des accessoires, appliquer une
  texture), et un handler qui synchronise les os d'armes. Le rig s'anime donc
  **sans eux** : on l'ouvre toujours avec les scripts désactivés.

## Structure

| objet | rôle |
|---|---|
| `__PrimaryArmature` (propriété `_Rbx_R6_Rig_`) | les **contrôles** de l'animateur |
| `InternalArmature` | les 7 vraies parts Roblox (HumanoidRootPart, Torso, Head, bras, jambes), menées par des os `*_Positioner` |
| `RigSettingsHolder` (vides `Left Arm`, `Right Arm`, `Left Leg`, `Right Leg`, `Torso`, `Head`, `Body`) | les **réglages**, lus par 80 drivers |
| collections `MBlocky`, `M2012`, `M2016`, `F…` | variantes de corps (MBlocky visible par défaut) |
| `R6rig1_diff.png` (empaquetée, 1024×512) | la texture F/B/L/R/U/D des faces |

Contrôles (sur `__PrimaryArmature`) :

- `MasterControl` : tout le personnage.
- `LowerTorso-FK` : bassin.
- `UpperTorso-IKTarget` : poitrine. Le torse est une chaîne IK virtuelle
  `Spine → UpperTorso`, orientée par `Torso-Pole`.
- `RightLeg-IK`, `LeftLeg-IK` : pieds, avec `*Leg-Pole` pour le genou.
- `RightArm-IK`, `LeftArm-IK` : mains, avec `*Arm-Pole` pour le coude.
- `*Arm_FK`, `*Leg_FK` : contrôles FK.
- `*Arm_GrabPoint` : point d'agrippement.
- `LookToPoint` : cible du regard.
- `Head` : tête.

**Principe clé** : chaque membre R6 rigide est piloté par une chaîne à
**2 os virtuels** (bras = UpperArm → LowerArm, jambe = UpperLeg → LowerLeg).
La vraie part Roblox suit l'os virtuel du bas via `*_Positioner`. Quand on
place une main ou un pied, le membre rigide **s'oriente** vers ce point. C'est
exactement le « membre rigide piloté par IK » qu'on avait reconstruit à la main
dans `constraints.py`.

Réglages (propriétés des vides, drivers de type AVERAGE avec une courbe
0 → 0 / 1 → 1, donc sans Python) :

| réglage | défaut | effet |
|---|---|---|
| `Left/Right Arm` `IK/FK` | 0 (FK) | 1 = bras en IK (la main suit `*Arm-IK`) |
| `Left/Right Arm` `Grab` | 0 | 1 = main collée à `*Arm_GrabPoint` (**saisir un autre personnage**) |
| `Left/Right Arm` `Torso Influence` | 1 | 0 = la main ne suit plus le torse |
| `Left/Right Leg` `IK/FK` | 1 (IK) | pieds plantés par défaut |
| `Left/Right Leg` `Torso Influence` | 1 | 0 = les jambes ne suivent plus la rotation du torse |
| `Torso` `IK/FK` | 1 | torse en chaîne IK |
| `Head` `Track Object` | 0 | 1 = la tête regarde `LookToPoint` |
| `Head` `Ignore Rotation` | False | la tête ignore la rotation du personnage |
| `Body` `BodyType`, `Feminine` | 1, False | variante de corps |

## Conventions mesurées (probe du 2026-09-23, `v222_rig.py`)

- **Avant du personnage = +Y Blender. 1 unité = 1 stud. Semelles à z = 0.
  Scène à 60 fps.** HumanoidRootPart est à z = 3,0, comme notre FK
  (`export_roblox.py`).
- Le fichier contient une action `ArmatureAction` qui clé la pose de repos à la
  frame 0 sur **tous** les contrôles : elle écrase toute pose manuelle au rendu.
  `open_rig()` la détache.
- Changer un réglage ne réévalue les drivers que si le depsgraph est marqué
  (`update_tag`). `set_setting()` le fait. Sans ce tag, l'influence reste à
  l'ancienne valeur (piège trouvé et corrigé pendant le probe).
- `LowerTorso-FK` en **translation** locale : y = hauteur, z = −avant,
  x = côté. En **rotation** : **X+ = pencher en ARRIÈRE**, Z+ = pencher vers sa
  gauche, Y = torsion. C'est la même convention que le Torso Roblox, déjà
  prouvée par FK dans `poses.py`.
- `UpperTorso-IKTarget` : sa **translation** y+ fait pencher la poitrine en
  avant. Sa rotation est ignorée par l'IK.
- `RightArm_FK` X+ = le bras balance vers l'avant et monte.
- Main en IK : la translation de `RightArm-IK` (y = avant, z = haut) oriente le
  bras vers ce point.
- **Descendre le bassin garde les pieds plantés**, mais la semelle rigide
  s'enfonce de **0,17 à 0,24 stud** : la jambe s'incline et le R6 n'a pas de
  cheville. Même le rig pro a cette limite ; c'est la leçon « bord de semelle
  qui plonge » du README du cerveau. **Monter** le bassin au-delà de la jambe
  tendue décolle les pieds (pas d'étirement).

Preuve : `captures/verification/2026-09-23-v222-rig-pilote-headless.png`.
C'est une pose de **test**, rendue de face, de profil et de trois quarts
(Cycles CPU, sans GPU ni écran), faces étiquetées visibles.

## Tutoriel officiel (texte du post collé par Milan, 2026-09-23), recoupé

Le texte du post DevForum a été collé par Milan (le site reste bloqué ici).
Résumé, avec pour chaque point ce que le fichier et les mesures confirment.

**Prérequis annoncés** : le plugin Blender Animations de Cautioned. L'export
d'armes demande sa version 2.4.2 ou plus ; Blender 4.2 ou plus. L'auteur
prévient que toutes les fonctions du plugin n'ont pas été testées.
dillydog580 fournit la version 2.6.3 (GPL).

**Fonctions annoncées** — toutes retrouvées dans le fichier :

| fonction annoncée | dans le fichier | mesuré |
|---|---|---|
| IK + FK bras et jambes, mélange par curseur | réglage `IK/FK` (0 à 1) | oui |
| Torso influence bras et jambes | réglage `Torso Influence` | câblage lu |
| bascule IK/FK et Grab | réglages `IK/FK`, `Grab` | oui |
| la tête suit un objet | `Head` `Track Object` → `LookToPoint` | oui |
| points d'agrippement (« comme une poignée de porte ») | `*Arm_GrabPoint` + `Grab` | câblage lu |
| rotation du torse où UpperTorso, Spine et LowerTorso contribuent chacun | voir sous le tableau | oui |
| panneau intégré (réglages, raccourcis) | scripts `RigSettings` / `RigUtilities` / `RigSelector` | UI seulement |

Rotation du torse, mesurée :

- **Torse en IK** (défaut) : la **rotation** de `LowerTorso-FK` bascule tout
  le haut du corps autour du bassin. La **translation** de
  `UpperTorso-IKTarget` plie la poitrine. `Spine` est l'os de la chaîne, pas
  un contrôle.
- **Torse en FK** (`Torso` `IK/FK` = 0) : `Torso_FK` fait pivoter le torse
  autour de **son propre centre** (le centre reste à z = 3,0). `LowerTorso-FK`
  le fait pivoter autour du **bassin**.
- `Torso_FK` n'a aucun effet en mode IK. La rotation d'`UpperTorso-IKTarget`
  est ignorée dans les deux modes.

**Armes et props qui changent de parent** (tuto) :

1. Dans Studio, n'importe quel rig R6 (pas forcément celui fourni). Placer
   l'arme sur un membre, torse et tête compris.
2. Créer le joint avec RigEdit (Lite suffit). Rig en position (0, #, 0).
3. Plugin Cautioned, onglet « Rigging », « Export Weapon / Accessory ».
   Choisir le rig et l'arme (« Pick from Selection »), « Export Weapon »,
   ce qui donne un `.obj`. Puis « Clean Meta Parts ».
4. Dans Blender, panneau N, « Import New Rig (.obj) », et viser
   **`InternalArmature`**, jamais `__PrimaryArmature`.
5. Le plugin intégré fait le reste. C'est le handler de `RigEvents.py` lu
   plus haut : il clone l'os d'arme dans `__PrimaryArmature`, lui donne une
   forme et une couleur, et le clé.
6. À l'export, le rig en jeu doit porter **la même arme**.

**Accessoires** (tuto) :

1. Rig identique dans Studio, à (0, 0, 0), jambes posées sur le sol.
   Exporter tout le modèle en `.obj`.
2. Dans Blender : File > Import > Wavefront, avec **« Split By Group »
   activé**. Garder seulement les objets `Handle#`.
3. Sélectionner les accessoires d'un membre, puis Utilities > Accessories >
   « Attach Accessories », et choisir le membre. Côté code, c'est une
   contrainte Child Of sur l'os (`RigUtilities.py`).
4. Appliquer la texture du rig pour qu'il ressemble à celui de Studio.

**Ce que ça veut dire ici** :

- Les étapes **Studio** (joint RigEdit, export `.obj` de l'arme ou de
  l'avatar) sont faites par Milan : pas de Studio dans ce sandbox.
- Les étapes **Blender** (import sur `InternalArmature`, attache des
  accessoires) sont faisables en `bpy` sans écran, à condition d'enregistrer
  l'add-on Cautioned 2.6.3. Le handler d'armes est un script embarqué : on
  l'exécute **après** audit, ou on reproduit ses 4 opérations.
- L'export « as normal » du tuto passe par l'add-on Cautioned (`.rbxanim`,
  importé dans Studio par le plugin Cautioned). C'est le chemin standard des
  animateurs pro. Notre KeyframeSequence `.rbxmx` directe reste une
  alternative, vérifiable par l'aller-retour moteur.

## Ce que montre le GIF d'exemple envoyé par Milan

64 images × 50 ms = 3,2 s, dans Blender avec **deux** rigs V2.22 :

1. l'attaquant (vert) en garde basse, bras armé ;
2. il fond sur la victime (rouge/jaune) et la saisit ;
3. les deux corps s'emmêlent en rotation (projection) ;
4. la victime est jetée et atterrit à plat, loin ;
5. l'attaquant se redresse.

C'est l'objectif : **attaquant et victime animés ensemble** dans la même scène,
l'agrippement tenu par `Grab` et `*Arm_GrabPoint`. Le rig est conçu pour ça.

## Ce que ça change pour le cerveau

- Le rig V2.22 remplace notre rig maison pour **poser**. Nos solveurs
  (`constraints.py`) deviennent des vérificateurs, plus des poseurs.
- La **revue de pose** (étape 2 de `PLAN.md`) est disponible dès maintenant :
  `review_render()` de face, de profil et de trois quarts.
- **Reste à brancher** :
  - l'**export** : cuire `InternalArmature` en KeyframeSequence. Soit avec
    l'add-on Cautioned 2.6.3 (GPL, fourni par dillydog580), soit avec notre
    exporteur `export_kfseq.py`, en lisant les matrices des parts ; à vérifier
    ensuite par l'aller-retour `resolve_rbxmx` ;
  - **deux rigs dans une scène** (attaquant + victime).
