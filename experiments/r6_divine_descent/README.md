# La descente — chute divine (R6, Roblox)

Prototype isolé, sans lien avec RANK ZERO ni MyAnimeRPG — même isolation
que `experiments/r6_aerial_kick_combo/` et `experiments/r6_throne_crown/`,
dont ce prototype **réutilise telle quelle** l'infrastructure de rig déjà
vérifiée (`r6_rig.py`, `anim_engine.py`, `export_kfseq.py`,
`resolve_rbxmx.py`, le rig `RigR6.rbxmx` importé depuis GitHub — voir
`rig/PROVENANCE.md`, provenance identique aux deux autres prototypes).

## Demande

« Teste une nouvelle scène d'animation, crée-moi une scène où le
personnage descend du ciel tel la descente d'un dieu. » Scène séparée
des deux autres (pas de trône, pas de combo de coups de pied) : chute
libre depuis une haute altitude, atterrissage, relevé.

## Ce qui est livré

- `output/character_divine_descent.rbxmx` — `KeyframeSequence` du
  personnage (rig R6 réel, 6 segments rigides, mêmes contraintes que les
  deux autres prototypes : pas de coude/genou, Motor6D 3 DOF). 94
  keyframes, 3,10 s à 30 Hz.
- Lecteur HTML (chute + pause + coup + explosion + relevé, résolu par le
  moteur) : https://claude.ai/code/artifact/c21563ef-4b1b-4a7f-abe6-f68347dcc53c

## Chorégraphie

Cinq phases (`scripts/choreography.py`, fonction `divine_descent()`) —
restructurée en 2 beats distincts après un retour utilisateur explicite
(« il tombe du ciel... marque une pause et abat sa colère de son poing » :
la première version faisait atterrissage et coup de poing en un seul
mouvement continu) :

1. **Chute** (0,00 s → 1,32 s) — silhouette d'aile : bras écartés
   (`Right/Left Arm` Z≈±85, presque à l'horizontale), jambes tendues
   balayées vers l'arrière, tête et buste plongés vers le sol. Espacement
   des keyframes **décroissant** (0,55 s, puis 0,40 s, puis 0,25 s pour
   une distance de chute comparable) — imite l'accélération de la
   pesanteur (vitesse = distance/temps) sans coder de vraie physique, la
   même technique qu'un *ease-in* d'animateur. Altitude de départ :
   Y=34 studs (~17× la hauteur du personnage).
2. **Atterrissage + pause** (1,32 s → 1,75 s) — touche le sol à
   `LAND_T`=1,42 s, bras droit déjà remonté en amorce (*wind-up*, comme
   un marteau levé), **pas encore de poing au sol**. Tenu **immobile**
   jusqu'à `PAUSE_T`=1,75 s (même pose exacte aux deux keyframes — voir
   "Vérifié par capture d'écran" plus bas pour la preuve numérique que
   c'est un vrai arrêt, pas juste un ralentissement).
3. **Le coup** (1,75 s → 1,85 s, `STRIKE_T`) — le poing s'abat au sol en
   à peine 0,10 s : mouvement brusque, pas une transition lente comme le
   reste de la chorégraphie. Torse/tête plongent plus loin qu'au simple
   atterrissage. **C'est ce keyframe, pas l'atterrissage, qui déclenche
   l'explosion du lecteur** (aura dorée, onde de choc, fissures, débris —
   voir plus bas).
4. **Impact tenu** (1,85 s → 2,05 s) — le temps que l'explosion se lise
   avant que le personnage ne commence à se relever.
5. **Relevé** (2,05 s → 3,10 s) — le personnage se redresse en une pose
   fière et puissante (buste/tête inclinés vers l'arrière, bras
   légèrement écartés du corps, jambes debout).

## Calibré par le calcul, pas à l'oeil

Même discipline que `r6_throne_crown/scripts/calibrate.py` : les angles
d'impact ont été trouvés par balayage numérique de la cinématique
directe (`scripts/calibrate.py`), pas devinés puis ajustés à l'oeil.

**Premier essai, corrigé avant livraison** : une première pose d'impact
(hanche à Y=2,3, jambes à 40°/18°, bras à X=48°) laissait le poing droit
à Y=2,67 — *plus haut que la hanche elle-même*, très loin du sol. Un
balayage de la hauteur de hanche et des angles de jambe/bras
(`calibrate.py` + tests isolés, voir historique du script) a établi :

- **Hanche à Y=1,85** avec jambes à (22°,16°)/(8°,-10°) : les deux pieds
  touchent le sol à quelques centièmes de stud près.
- **Poing droit** : la distance minimale réellement atteignable au sol à
  cette hauteur de hanche est **Y≈0,66 stud**, quel que soit l'angle du
  bras essayé (balayage de -80° à +120°) — limite **réelle** du rig
  (longueur de bras fixe, pas de coude, torse incliné à angle fixe), pas
  une valeur mal réglée. Retenue telle quelle et documentée, plutôt que
  masquée par une pose qui prétendrait toucher le sol exactement.
- **Pas de genou, donc pas d'appui parfaitement symétrique** : une jambe
  davantage balayée vers l'avant lève mécaniquement son pied plus haut
  (segment rigide qui pivote autour d'un point fixe) — la fente
  d'atterrissage asymétrique (jambe avant plus ouverte que la jambe
  arrière) est donc un compromis assumé, vérifié par calcul à quelques
  centièmes de stud de clipping au pire, pas une pose parfaite. Même
  limite déjà documentée pour l'assise du trône (`r6_throne_crown`).

`scripts/calibrate.py` vérifie aussi que la hauteur de hanche décroît
strictement jusqu'à l'impact (pas de rebond parasite) et que toutes les
rotations restent finies et dans une plage plausible.

**Vérifié aussi que la pause est un vrai arrêt et que le coup est vraiment
bref**, pas seulement par construction du code mais par calcul sur les
échantillons résolus : la dérive de la racine entre `LAND_T` et `PAUSE_T`
est de 0,004 stud (bruit numérique, pas un mouvement réel), et le poing
droit tombe de 3,1 studs en seulement 0,10 s pendant le coup — deux
chiffres qui confirment que la structure en 2 beats demandée par
l'utilisateur (« marque une pause » puis « abat sa colère ») est
réellement ce que joue le fichier, pas juste ce que dit le commentaire du
code.

## Bugs trouvés par capture d'écran, pas par les nombres

Même leçon que dans les deux autres prototypes : la vérification
numérique (calibrate.py, round-trip `resolve_rbxmx`) garantit que le
fichier est *correct*, pas qu'il se *lit* correctement à l'écran. Deux
bugs réels, trouvés uniquement en regardant le rendu :

- **Personnage invisible pendant toute la chute** : `HumanoidRootPart.p`
  vaut **toujours** `[0,0,0]` dans les frames résolues par le moteur (la
  translation de la racine n'est jamais portée par elle-même — voir
  `export_kfseq.effective_pose_inputs()` : le mouvement de racine est
  replié dans la pose de `Torso`, `HumanoidRootPart` n'étant jamais
  `Part1` d'un `Motor6D`). Le lecteur lisait `HumanoidRootPart.p[1]`
  comme hauteur de caméra/personnage — toujours 0, donc une caméra
  ancrée sur une hauteur gelée à l'origine pendant que le vrai
  personnage tombait de Y=34 ailleurs, hors-champ. Corrigé en lisant
  `Torso.p` partout où une position monde du personnage est nécessaire
  (caméra, traînée de chute, ombre au sol) — jamais
  `HumanoidRootPart.p`, qui ne porte aucune position réelle dans ce
  format.
- **Traînée de chute visible en pleine opacité sur la pose finale** :
  son alpha dépendait uniquement de l'altitude (`SKY_Y - charY`), qui
  redevient "loin du sol" quand la hanche remonte vers la hauteur debout
  après l'atterrissage — donc la traînée, censée n'exister que pendant
  la chute, restait affichée derrière le personnage relevé. Corrigé en
  la coupant explicitement à `t >= IMPACT_T`, pas seulement par
  l'altitude.

## Caméra en poursuite verticale (mise en scène du lecteur, pas du fichier)

Le `KeyframeSequence` livré ne contient que les rotations des 6
`Motor6D` et la translation de la racine (repliée dans `Torso`, voir
ci-dessus) — aucune caméra. Le lecteur HTML fait suivre l'ancrage
vertical de la caméra sur `Torso.p[1]` pendant la chute (à 85 % de la
vitesse de descente, pour que le sol se rapproche visiblement plutôt que
de rester à distance fixe du personnage), puis le ramène en douceur au
cadrage au sol standard (même convention que le sacre) **dès que le
personnage touche le sol** (`LAND_T`=1,42 s) — pas au coup (`IMPACT_T`,
plus tardif désormais, voir "Chorégraphie") : la caméra doit déjà être
stable quand le poing s'abat, pas encore en train de se recadrer.
Entièrement une mise en scène du *lecteur* (Canvas 2D, projection
orthographique fixe), au même titre que l'éclairage à trois sources ou
le halo de couronne du sacre.

## Effets d'impact (lecteur uniquement)

`LAND_T` (le personnage touche le sol) et `IMPACT_T` (le coup) sont deux
instants **distincts** exportés séparément dans le JSON du lecteur
(`land_t` et `impact_t`) — pas le même comme dans la première version.
Les effets de CHUTE (colonne de lumière, traînée, caméra qui se stabilise,
voir plus haut) s'arrêtent à `LAND_T` ; l'EXPLOSION (flash plein-écran,
deux ondes de choc décalées, fissures au sol qui irradient et persistent,
débris qui volent et tournent, secousse de caméra ~0,4 s) attend
`IMPACT_T`, le moment réel du coup de poing — 0,43 s plus tard. Voir
« Plus divin » plus bas pour le détail de ces effets et pourquoi leur
bruit est déterministe (important pour la vérification par capture
d'écran, pas un détail cosmétique). Rien n'est codé en dur : les deux
instants sont lus dans les données du `KeyframeSequence` résolu, pas des
valeurs qui pourraient diverger du fichier.

## « Plus divin, comme s'il abattait sa colère sur le sol » (retour utilisateur)

Premier retour après la livraison initiale : la scène ne se lisait pas
assez comme un dieu qui s'abat sur le sol. Ajouté, toujours dans le
lecteur (rien de nouveau dans le `KeyframeSequence` — la pose ne change
pas, seule la mise en scène autour d'elle) :

- **Colonne de lumière divine** (`drawGodRay()`) qui descend AVEC le
  personnage pendant toute la chute, pas seulement à l'impact — la
  "descente d'un dieu" doit se lire dès le début, pas seulement au
  moment où il touche le sol.
- **Auréole dorée** (`drawDivineAura()`) autour du personnage, marquée
  pendant la chute et juste après l'impact, qui s'atténue une fois
  debout — cohérente avec le halo de couronne du sacre (même famille de
  mise en scène additive), mais ici pour lire "l'énergie qui vient de
  s'abattre", pas un bijou qui brille.
- **Impact nettement plus violent** :
  - flash plein-écran plus large et plus chaud (doré, pas blanc neutre) ;
  - **deux** anneaux d'onde de choc décalés de 0,10 s (une réverbération,
    pas un simple cercle qui s'étend une fois) ;
  - **fissures au sol** qui irradient du point d'impact en dents de scie
    (angles fixes mais déterministes par frame, pas `Math.random()` —
    important pour que deux captures à la même frame donnent la même
    image, voir plus bas) et persistent bien après que la poussière soit
    retombée ;
  - **débris** : petits carrés sombres qui volent, tournent et
    retombent, pas seulement de la poussière plate ;
  - **secousse de caméra** (`shakeOffset()`) pendant ~0,4 s après
    l'impact, amplitude qui décroît en carré du temps écoulé — un dieu
    qui frappe le sol doit se *sentir*, pas seulement se voir.

**Déterminisme du bruit, pas un détail cosmétique** : la secousse de
caméra et les fissures utilisent des fonctions de `sin()`/angles fixes
plutôt que `Math.random()`, pour une raison précise — la vérification de
ce projet se fait par capture d'écran Playwright à des instants `t`
précis (voir "Bugs trouvés par capture d'écran" plus haut) ; un bruit
non-déterministe rendrait deux captures de la même frame différentes
d'une exécution à l'autre, cassant la comparaison avant/après qui a déjà
servi à trouver deux bugs réels dans ce même prototype.

## Rig du personnage

Même rig R6 vérifié (dépôt Adonis, licence MIT) que les deux autres
prototypes de ce dossier — voir `rig/PROVENANCE.md`.

## Commandes

```bash
cd scripts
source ../../r6_aerial_kick_combo/.venv/bin/activate

# Verification numerique (FK, pas a l'oeil)
python3 calibrate.py

# Export du KeyframeSequence (+ verification structurelle)
python3 run_scene.py

# Assemble le lecteur HTML final (JSON de scene injecte dans le template)
python3 build_viewer.py
```
