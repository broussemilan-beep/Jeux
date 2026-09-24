# Poing du Dragon : technique ultime, 2 rigs R6 V2.22

Étape 6 du plan (`experiments/_shared/animator_brain/PLAN.md`) : un brief libre,
à partir de l'exemple de Milan, « le poing du dragon de Goku ». La
proposition, fondée sur ses références, est dans
`../_shared/animator_brain/SCENE_POING_DU_DRAGON.md`.

Livré : animation + VFX + caméra + effets d'écran, jouable dans un lecteur
HTML **et** packagé pour Roblox (animations, module Luau, démo).

## Ce que ça fait (8,8 s à 60 i/s, hitstops en plus)

| frames | beat | détail |
|---|---|---|
| 0-118 | rafale | 6 coups au rythme du Black Flash (écarts 30/20/14/14/20 f) ; chaque coup : teinte plate du corps 2 f, flash, étincelles, onde, fumée, hitstop 0,05 s ; le 5e décolle la victime, le 6e la jongle |
| 118-146 | anticipation | fente très basse, poing armé à la hanche, glissade dans la poussière, aura qui s'allume |
| 146-170 | uppercut | le corps se déplie en 4 f ; la victime part en l'air |
| 170-200 | envol | accroupi, décollage avec étoile au sol |
| 196-208 | whip pan | 12 f, traînées plein écran |
| 200-256 | temps suspendu | au-dessus de la victime : poing armé chargé en or, genou haut, jambe arrière tendue |
| 236-288 | dragon | trois rubans (or, blanc, fumée) enroulés en hélice autour du bras |
| 256-288 | plongée | contre-plongée, contact en l'air (hitstop 0,12 s), la victime est écrasée au sol |
| 288-294 | planches manga | 3 × 2 f, générées depuis NOTRE pose (`build_manga.py`) |
| 294-322 | écran blanc, puis brouillard | détails dans le paragraphe suivant |
| 322-490 | révélation | détails dans le paragraphe suivant |
| 490-526 | retour | l'attaquant se relève |

- **294-322, écran blanc** : pendant qu'il masque la scène, la caméra change de plan, les pics du cratère sortent du sol et la victime est éjectée.
- **322-490, révélation** : attaquant en appui trois points au centre du cratère, victime couchée à 15 studs, fumée, braises.

## Chaîne de production (dans l'ordre)

```bash
BL=/chemin/Blender_R6.blend           # rig V2.22 (non versionné, licence)
python3 scripts/verify_export.py $BL  # anime (dragon_clip.py), vérifie, exporte les 2 KeyframeSequences
python3 scripts/build_manga.py $BL    # 3 planches manga depuis la silhouette de la pose
python3 scripts/build_player.py       # staging.py (caméra + effets) -> lecteur HTML
python3 scripts/build_roblox_package.py   # DragonFistData.luau + PoingDuDragon.rbxmx, relu
python3 luau/run_sens_test.py /chemin/luau  # sens du module, exécuté par Luau officiel
python3 scripts/render_poses.py $BL   # planche de revue des poses clés
```

## Vérifications (chiffres du dernier passage)

- **Contacts.** Écart entre le poing et la partie visée, sur les 9 frappes :
  - 6 coups de la rafale, uppercut, contact en l'air, écrasement ;
  - écart ≤ 0,07 stud, et aucune pénétration dans les 10 frames qui suivent ;
  - seule exception : 0,11 stud après l'écrasement, pendant les planches manga qui couvrent l'écran.
- **Sol.** Une jambe R6 est une seule boîte. Les pieds visent donc le contact
  du coin le plus bas, pas celui du bout du pied (`box_lowest` et mode `"g"`).
  Point le plus bas :
  - attaquant −0,14 : le poing enfoncé dans le cratère, voulu ;
  - victime −0,16 : pendant l'écrasement, masqué par les planches manga.
- **Tête** jamais décalée : 0 stud, comme chez les pros.
- **Export.**
  - Clés : 263 pour l'attaquant et 150 pour la victime, au lieu de 527 frames. `roblox_export.reduce_keyframes` ne garde que les clés que l'interpolation linéaire du moteur ne sait pas reproduire.
  - Écart max après réduction, rejoué par le moteur : 0,017 stud.
  - Aller-retour du fichier : 5e-15.
- **Sens**, relu dans les fichiers : 9 contrôles sur 9.
  - L'attaquant regarde −Z, la victime lui fait face.
  - Le poing est devant, la victime recule vers −Z.
  - À l'apex, la victime est en l'air et l'attaquant au-dessus d'elle.
  - Le poing descend au contact en l'air.
  - À la fin, la victime est éjectée loin devant et couchée.
- **Verdict calibré par segment** : mesures dans la plage pro, sur 38.

  | segment | catégorie | dans la plage |
  |---|---|---|
  | coups de la rafale | frappe_legere | 16 à 25 |
  | réactions | reaction | 17 à 23 |
  | uppercut, plongée | frappe_lourde | 19 |

  Les écarts restants sont en bonne partie structurels :
  - une rafale enchaîne plus vite qu'un M1 isolé (durée 0,4 s contre 0,65 s) ;
  - notre victime recule par l'animation, alors que chez le pro le recul vient d'un script (déplacement du torse 0 dans le pack).

  La 1re passe a corrigé ce que le corpus a signalé :
  - coups trop secs (4 200°/s contre 2 100 max) → armement tenu et action plus longue ;
  - torse trop peu tourné (43° contre 67-131°) → balayage de ±45° ;
  - réactions qui agitaient trop les bras et pas assez le torse ;
  - uppercut trop explosif (41 studs/s contre 14).
- **Package Roblox** relu (`PACKAGE OK`) :
  - 3 362 instances, références uniques ;
  - pose de repos cohérente avec les Motor6D (écart 0) ;
  - victime devant et face à l'attaquant ;
  - 15 markers ;
  - Demo en RunContext Client ;
  - les 3 fichiers Luau compilent avec `luau-compile`.
- **Test de sens Luau** (`luau/sens_test.luau`) : SENS OK, aucun échec.
  - placement de la victime, même attaquant tourné ;
  - repère de scène posé au sol : un vrai bug corrigé, les effets et la caméra auraient été 3 studs trop haut ;
  - coups vers l'avant, cratère devant et au sol, frappe en l'air vers le bas ;
  - caméra exacte à chaque clé, tenue jusqu'aux coupes, sans saut ailleurs ;
  - ordonnanceur : 32/32 événements, une seule fois, dans l'ordre malgré les hitstops ;
  - positions de fin.

## Revue visuelle (et ce qu'elle a changé)

- **Planche des poses clés** (`output/dragon_poses_cles.png`) : profil et
  trois-quarts de 20 poses. Elle a conduit à abandonner le « genou au sol »
  de l'atterrissage, impossible proprement avec une jambe R6 d'un seul bloc,
  au profit d'un appui trois points.
- **Test de lisibilité de silhouette** (rendus Blender de la pose seule) : la
  pose du temps suspendu se lisait comme un bloc. Elle a été exagérée : poing
  plus haut et plus loin derrière, bras avant tendu vers la cible, jambes en
  ciseau.
- **Lecteur** : 5 passes de cadrage, captures à l'appui.
  - Les plans étaient trop serrés (personnages coupés), reculés de ~45 %.
  - Le flash doré du corps se confondait avec le jaune du noob : il est
    passé au blanc-orangé.
  - Pendant le temps suspendu, le poing chargé sortait du cadre.

## Dans Roblox Studio

1. Insérer `output/PoingDuDragon.rbxmx` dans le Workspace, puis lancer Play :
   la démo rejoue la technique en boucle, avec la caméra cinématique.
2. **Planches manga** : importer `output/manga_1..3.png` (Asset Manager), puis
   coller les IDs dans `DragonFist.CONFIG.MANGA_IDS`. Sans elles, le module
   affiche des images plein écran noir / blanc / noir.
3. En jeu : `DragonFist.play(attaquant, victime, dossierAnimations, require(DragonFistData))`.
   Les deux HumanoidRootPart sont ancrés pendant la technique, puis replacés
   là où les corps ont fini.

## Limites, dites franchement

- **Jamais testé dans Roblox Studio** : ce sandbox n'y a pas accès. Ce qui est vérifié :
  - les fichiers ;
  - le code exécuté par Luau ;
  - le package relu.

  Le rendu réel des particules reste à voir chez Milan.
- Les **effets du lecteur** sont une approximation Three.js des émetteurs Roblox
  du module : mêmes durées, tailles et vitesses, pas le même moteur de
  particules. Les textures du module sont celles intégrées au client Roblox
  (étincelle, fumée, feu).
- **Aucune catégorie « aérien » dans le corpus**. Le temps suspendu et la plongée
  sont jugés contre `frappe_lourde` (3 exemples) : un verdict fragile.
- **Les planches manga** sont des silhouettes R6 encrées (blocs) : elles frappent
  en 2 frames, elles ne remplacent pas un dessin à la main.
- **Victime à la fin** : replacée debout là où elle gît (l'animation s'arrête). Un
  ragdoll serait la suite logique.

## v2 (2026-09-24) : après le retour de Milan (6/10)

Retour : « problèmes sur l'enchaînement, ça manque de puissance, il est
accroupi ». Détail dans `../_shared/animator_brain/RETOURS.md`.

**Ce qui a changé côté cerveau.** Ces changements valent pour toutes les
productions, pas seulement celle-ci :
- **Nouvelle mesure `affaissement_torse_studs`** (corpus reconstruit). C'est la
  hauteur absolue du torse sous la position debout ; l'ancienne mesure ne
  voyait que la variation pendant le clip.
- **Règles `rules.py`, avec leur source (`LECONS.md`)** :
  - posture ;
  - escalade de la rafale ;
  - un angle de caméra au moins toutes les 2 frappes ;
  - impact final visible ;
  - plongée lisible.
- **Les poses partent des cibles du corpus** (`rules.design_targets`), au lieu
  d'être tapées de tête puis jugées après coup.

**Ce qui a changé dans la technique :**

| | v1 | v2 |
|---|---|---|
| rafale | 6 coups identiques | 4 coups qui montent : jab G, direct D, crochet G, coup au corps qui soulève |
| posture | bassin −0,5 stud en permanence | debout : affaissement médian 0,11 stud (pro ≤ 0,12) |
| appuis | pieds écartés, qui glissent | pieds sous les hanches, un vrai pas par coup (le pied avant se lève puis se replante), appuis qui pivotent avec le bassin |
| hitstop | 0,05 s partout | 0,03 → 0,045 → 0,06 → 0,085, puis uppercut 0,10, frappe 0,13, impact 0,16 |
| recul de la victime | — | 0,28 → 0,47 → 0,67 → 1,22 stud |
| caméra de la rafale | 1 plan fixe | 3 plans : trois-quarts, contrechamp de côté, plan bas |
| impact final | caché : coupe sur les planches dans la frame du contact | visible 10 f + gel de 0,16 s : onde de choc en dôme, mur de poussière, pics qui sortent, puis seulement les planches |
| règles apprises | 3/7 | **7/7** |

**Deux problèmes trouvés en route, et leur cause :**
- **Appui trop écarté.** Une jambe R6 droite (2 studs) écartée de *d* abaisse la
  hanche de 2 − √(4 − d²) : l'appui large de la v1 *obligeait* à s'accroupir.
- **Pas de taille en R6.** Tourner le torse de 85° avec les pieds cloués croise
  les jambes. Les appuis pivotent donc avec le bassin (60 %), comme un boxeur
  sur l'avant du pied.

**Inchangé** : toute la partie aérienne, que Milan a jugée bonne. Contacts ≤ 0,07
stud sans pénétration, sens 9/9, package relu, test Luau OK.

**Honnêtement.** Les règles prouvent que les défauts signalés sont corrigés.
Elles ne prouvent pas que ça frappe fort, c'est à Milan d'en juger. Le verdict
calibré des coups légers bouge peu (18-27/40), parce qu'une rafale reste plus
serrée qu'un M1 isolé.

### Retour de Milan sur la v2 : 6,7/10

« Les bras sont trop hauts, il est accroupi et pas en transfert de poids. »
Les trois défauts sont **mesurés** : ils sont devenus les règles 6 et 7 du
cerveau (`../_shared/animator_brain/LECONS.md`). `scripts/check_rules.py`
passe maintenant 10 règles ; la v2 en passe **7/10** (`output/regles_v2.json`).

| mesure pendant la rafale | v2 | pros (pack) |
|---|---|---|
| décalage vertical de l'épaule | médiane +0,69, max +1,29 | médiane −0,59 à −0,92, max +0,04 |
| poing au contact | 4,4 studs du sol, bras +4-5° | 2,5-3,6, bras −20 à 0° |
| transfert de poids (torse au-dessus du pied avant) | 0,16-0,39 stud | frappe lourde 0,33-0,92 ; M1_1 0,74 |

Cause : l'IK des bras du V2.22 **translate** l'épaule quand la main vise
trop haut ou trop près (garde collée, coups au visage). Et chaque coup
avançait le pied avant avec le corps : au contact, le pied est encore en
l'air. Preuve, en profil au contact : `scripts/profile_contact.py`, puis
`captures/verification/2026-09-24-poing-dragon-v2-epaules-vs-pro.png`.

## v3 (2026-09-24) : la rafale refaite après le retour sur la v2

Seule la rafale (f0-108) change. L'aérien, l'impact et la révélation sont
inchangés.

**Les quatre coups, tous au corps** (réf. Black Flash) :

| coup | cible | réaction de la victime |
|---|---|---|
| jab G | poitrine | le buste est repoussé |
| direct D | plexus | elle se plie en avant |
| crochet G | côtes | elle se plie de côté |
| coup au corps D | foie | elle se plie autour du poing et décolle |

**Comment chaque coup est construit** (`dragon_clip.py`) :
- **Placement du corps** (`fitp`) : le corps se place d'après le point de
  contact. Le pivot d'épaule est mis à 2,2 studs du point touché, bras sous
  l'horizontale : à cette distance, l'IK du V2.22 **baisse** l'épaule au lieu
  de la hausser (carte mesurée, `LECONS.md` 6).
- **Appuis plantés** de l'armement à la récupération. Le torse recule
  au-dessus du pied arrière à l'armement, puis passe devant le pied avant au
  contact. Le pas se fait après le coup, pendant la récupération.
- **Mains en arc** autour de l'épaule (`arm_point`) : l'IK interpole en ligne
  droite, une main allant de derrière à devant traverserait le corps
  (`LECONS.md` 9).
- **Garde basse, bras tendus vers le bas**, comme les M1 du pack (mains vers 2 studs).
- **Abaissement automatique du bassin** (`auto_low`) : seulement si un pied
  planté n'atteint pas le sol, au plus 0,2 stud. Il s'arrête dès que baisser
  n'aide plus.
- **Solveur IK plus robuste** : il part de plusieurs points de départ. Sur une
  pose, le contrôle d'un pied divergeait à 6 studs.

**Règles : 10/10** (`output/regles_v3.json`), contre 7/10 pour la v2 avec les
mêmes règles :

| mesure | v2 | v3 | pros |
|---|---|---|---|
| épaule (médiane / max) | +0,69 / +1,29 | −0,61 / −0,01 | −0,59 à −0,92 / +0,04 |
| poing au contact | 4,4 studs, bras +4-5° | 2,5-3,2 studs, bras −15 à −30° | 2,5-3,6, −20 à 0° |
| transfert de poids | 0,16-0,39 | 0,62-0,68 | 0,33-0,92 |
| affaissement (médiane) | 0,11 | 0,04 | ≤ 0,12 |
| recul de la victime | 0,28 → 1,22 | 0,28 → 0,39 → 0,57 → 1,35 | — |

**Autres contrôles**, tous inchangés en v2 comme en v3 :
- contacts ≤ 0,05 stud ;
- sens 9/9 ;
- test Luau `SENS OK` ;
- `PACKAGE OK` ;
- écart de réduction 0,017 stud.

Point le plus bas de l'attaquant : −0,08, au lieu de −0,14 en v2. Une pose
intermédiaire a été ajoutée dans la descente vers la fente.

**Caméra.** Le crochet frappe maintenant le flanc côté −x. Le plan B passe de
profil, de ce côté, sinon le dos de la victime cachait l'impact. Vérifié aux
frames 57-72.

**Preuves** :
- `captures/verification/2026-09-24-poing-dragon-v3-profil-contact.png` :
  profil au contact des 4 coups, contre les M1 pro ;
- `captures/verification/2026-09-24-poing-dragon-v2-vs-v3-rafale-profil.png` :
  le lecteur, v2 contre v3, aux 4 contacts.

**Honnêtement :**
- La distance entre les torses reste d'environ 3 studs. Le vrai bout portant du
  Black Flash obligerait à ramener la main près de l'épaule, et l'IK la hausse :
  on retomberait sur le défaut de la v2.
- Au contact, la jambe arrière est inclinée de 41 à 52°, et l'IK la décroche de
  la hanche (jusqu'à 1,2 stud). Les pros font pareil sur leurs coups lourds
  (downslam : jusqu'à 1,8 stud, 41°). Ça se lit comme une fente, mais c'est à
  juger à l'œil.

### v3b : bras horizontal, le corps descend (retour de Milan sur la v3)

Retour : « tu donnes des coups vers le bas ». C'était vrai : bras de −15 à −30°
au contact, pour une médiane pro de −3°. Sur la référence « Pro » de Milan
(vidéo 17-52-55, image à 4,25 s), le bras est **horizontal** et c'est le
**corps** qui descend en fente.

- **Cible prise à hauteur d'épaule** : `target_h` cherche sur le torse de la
  victime le point à la hauteur du pivot d'épaule de l'attaquant, 0,1 stud
  plus bas.
- **Coups 1 à 3** : debout, bras horizontal, poing à 3,2-3,3 studs.
- **Coup 4 (au corps)** : pas d'entrée. Le pied avant se lève pendant
  l'armement et se pose en fente large juste avant le contact. Le bassin
  descend de 0,6, bras horizontal dans le ventre, poing à 2,7 studs.
- **Poussée** : si la victime se plie vers le poing, le poing recule avec sa
  surface, et le corps avec lui, pour que l'épaule ne remonte pas.

**Règles : 11/11** (`output/regles_v3b.json`).
- **Règle des bras** : elle a maintenant un plancher, et la médiane de la
  rafale doit rester à ±10° de la médiane pro.
- **Règle de posture** : la fente finale est jugée au standard frappe_lourde,
  les coups légers au standard frappe_legere.

| | v3 | v3b | pros |
|---|---|---|---|
| bras au contact | −15 à −30° | −5 à −7° (médiane −5,9) | −20 à 0° (médiane −3) |
| poing au contact | 2,5-3,2 studs | 3,2-3,3, puis 2,7 (fente) | 2,5-3,6 |
| épaule (médiane / max) | −0,61 / −0,01 | −0,62 / −0,02 | −0,59 à −0,92 / +0,04 |
| transfert de poids | 0,62-0,68 | 0,59-0,84 | 0,33-0,92 |

**Contrôles** :
- contacts 0,05 stud, 0,005 de pénétration au plus ;
- sens 9/9 ;
- `SENS OK` ;
- `PACKAGE OK`.

**Preuve** : `captures/verification/2026-09-24-poing-dragon-v3-vs-v3b-bras-horizontal.png`
(lecteur en profil, v3 contre v3b, aux 4 contacts) et
`captures/verification/2026-09-24-poing-dragon-v3b-profil-contact.png`.

### v4 : le poing arme haut et voyage à plat (retour de Milan sur la v3b)

Retour : « les coups partent toujours du bas, le coup final ressemble à des
uppercuts et à un coup droit à la fois ». Mesuré (`scripts/fist_path.py`) : le
poing partait de la hanche et montait de 1,1 à 1,7 stud dans les 0,1 s avant
le contact. Chez les pros, il arme à hauteur d'épaule et avance à plat. Milan a
envoyé 5 exemples : style manga, à ne pas copier bêtement (fiche dans
`corpus/REFERENCES_VIDEO.md`).

**Chaque coup a maintenant sa forme** :

| coup | armement | trajet | autre bras |
|---|---|---|---|
| jab G | poing sur le côté, à hauteur d'épaule | court, de côté vers l'avant | part en arrière (contre-rotation) |
| direct D | torse tourné presque dos à la cible, poing en arrière à hauteur d'épaule | arc horizontal | vise la cible, puis garde |
| crochet G | poing sur le côté | arc horizontal | en garde |
| final D | manga : poing derrière la tête, pied avant levé | fente avec pas d'entrée, bras à plat | vise, puis garde |

- **Garde** : mains devant la poitrine.
- **Extension** : tenue jusqu'à 6 f après le contact.
- **Clés en arc** : de la garde à l'armement, la main passe par une clé sur le
  côté, pour que l'IK ne traverse pas le corps.

**Règles : 13/13** (`output/regles_v4.json`) :
- nouvelle règle **trajectoire du poing** : montée de 0,00 pour les 4 coups
  (v3b : 1,1-1,7), seuil 0,32 ;
- l'armement manga du final est jugé au standard coup lourd, comme sa posture ;
- la règle d'épaule exige « pas haussée en moyenne », et non plus la médiane
  des M1 pro (voir `LECONS.md` 11).

**Contrôles** : contacts 0,05 stud, sens 9/9, `SENS OK`, `PACKAGE OK`, sol
≥ −0,12.

**Preuve** : `captures/verification/2026-09-24-poing-dragon-v4-trajectoire-poing-vs-pro.png`
(trajectoires) et `2026-09-24-poing-dragon-v4-armement-contact.png` (lecteur,
armement et contact).

## v5 (2026-09-24) : le coup final devient un coup chargé

Retour de Milan sur la v4 (6,7) : « au coup final, le coup part toujours d'en
bas » ; piste : « le coup de Saitama, un coup qui se charge, avec le buste qui
tourne ».

**Ce qui avait été mal lu** (`../_shared/animator_brain/ANGLES_MORTS.md` §1).
Les v3, v3b et v4 corrigeaient les 4 coups de la rafale, alors que le « coup
final » était très probablement l'**uppercut de f150**. Il sortait d'une boule
accroupie (torse à 1,4 stud de f125 à f146) et le poing montait de 4 studs.
Aucune règle ne le regardait.

**v5, f108-170.**

| temps | v4 | v5 |
|---|---|---|
| 108-121 | glisse en fente très basse | 2 pas pour se replacer, appuis larges, genoux souples |
| 121-146 | boule accroupie, poing à la hanche | **charge** : buste enroulé dos à la cible (132°), poing armé à hauteur d'épaule derrière, l'autre bras vise ; tenue vivante de 18 f (le buste continue de s'enrouler) ; aura et poing qui brillent |
| 146-150 | l'uppercut se déplie de bas en haut | **départ en 4 f** : hanche, puis buste, puis bras, trajet à plat |
| 150 | poing monte à 5,9 studs | contact à hauteur d'épaule, **montée du poing 0,00** ; extension tenue, l'autre bras tire en arrière |
| après 150 | gel de 0,10 s | impact court (0,05 s) puis **explosion** : 2e souffle dans l'axe du coup, onde et gerbe au sol |
| victime | lancée à la verticale | éjectée en diagonale (arrière puis haut), moins affaissée avant le coup |

- **Caméra de la charge** : plan de profil à hauteur d'yeux. La contre-plongée
  au ras du sol de la v4 faisait monter à l'écran n'importe quel coup.
- **Lecteur** : les temps sont renommés « Charge » et « Coup chargé ».

**Mesures (perception du cerveau).** Coup final : tenue de 13 f, départ en
1 f, buste enroulé de 132°, poing qui monte de 0,00 dans les 6 f avant le
contact (v4 : +1,48).

**Contrôles.**
- règles : 13/13 ;
- contacts : 0,05 stud sur les 7 coups ;
- sol : ≥ −0,115, comme en v4 ;
- sens : 9/9, `SENS OK`, `PACKAGE OK`.

**Essayé puis retiré.** Des poignées AUTO sur les clés, pour la fluidité.
Elles haussaient l'épaule dans la rafale (0,33 stud) et la mesure qui les
justifiait était faussée par le tempo (`CERVEAU_V2.md`, correction).
L'outil reste dans `dragon_clip.py`, désactivé.

**Preuve** :
`captures/verification/2026-09-24-poing-dragon-v4-vs-v5-coup-final-profil.png`.

## v6 (2026-09-24) : la mise en scène du sol

Retour de Milan sur la v5 (6,8) : « je vois pas trop de différence avec la
v4 ». Le cerveau a mesuré que le bras, le rythme du poing et la rotation du
torse sont déjà au niveau des coups de base pros. Ce qui retient la note,
c'est la **mise en scène** de la rafale et du coup chargé, restée la même
depuis la v1. La partie aérienne, que Milan aime, applique déjà la grammaire
des refs. **La v6 ne touche à aucune pose** : elle change la caméra, la
hiérarchie des effets et raconte l'impact. Fiche écrite avant d'animer :
`FICHE_V6.md`.

| temps | v5 | v6 |
|---|---|---|
| rafale : caméra | 3 plans ; h3 et h4 filmés de −x, le dos de l'attaquant cache le poing | un plan par coup, **toujours du côté +x** (aucun passage de l'autre côté de l'axe) : haut, bas 3/4 arrière, plongée, profil franc pour h4 ; lente poussée dans chaque plan |
| rafale : effets | le même effet complet (étoile, halo, étincelles, fumée) et un flash du corps entier sur les 4 coups | **hiérarchie** : h1 à h3 = éclat 2 f et un anneau blanc, rien d'autre ; h4 = effet moyen, flash du corps et **fond de vitesse** 0,1 s |
| charge | plan de profil large | **plan rapproché de profil**, tête et bras qui vise, la victime au bout du regard ; lente poussée |
| f150 | impact de 0,05 s puis explosion | **impact raconté** : contact 3 f, **noir + étoile**, **3 cartes** tirées de notre pose (silhouette inversée, encre hachurée, **gros plan du poing** qui perce le cadre), **blanc** ; l'animation est gelée 0,43 s pendant la séquence, le blanc reste plein 0,02 s de plus puis se dissout sur un **plan très large** de la conséquence ; l'explosion sort du blanc |
| aérien | — | inchangé |

**Nouveau dans le lecteur.**
- Bouton caméra **« Jeu »** : caméra d'un joueur de battleground, derrière
  l'attaquant en verrouillage d'épaule (décalage de 1,75 stud à droite, FOV
  70).
- Les cartes (`output/carte_1..3.png`) sont générées depuis la pose de f150
  par `scripts/build_cartes.py`.

**Module Roblox.** Même séquence en Luau (`DragonFist.cartePhase`, identique
à celle du lecteur), fond de vitesse en `ScreenGui`, hiérarchie des impacts
par `tier`. Nouvel emplacement `CONFIG.CARTE_IDS` ; sans images, repli
noir / blanc / noir.

**Contrôles.**
- règles : 13/13 ;
- contacts : 0,05 stud sur les 7 coups ; poses identiques à la v5 (exports
  inchangés) ;
- sens : `SENS OK`, dont 11 nouveaux tests de la séquence de cartes (durée =
  gel, phase juste à chaque âge) et de la hiérarchie ; `PACKAGE OK`.

**Essayé puis écarté**, chaque fois vu à l'écran
(`captures/verification/2026-09-24-poing-dragon-v6-essais-camera-rejetes.png`) :
- **caméra d'épaule pour la rafale** : le dos de l'attaquant cache le coup ;
- **très gros plan de face sur le regard** : le visage R6 a un sourire fixe,
  c'est comique, pas tendu ;
- **poing vers la caméra au contact** : dans l'axe du coup, le corps de la
  victime est toujours entre l'objectif et le poing. Le principe vit dans la
  1re carte, pas dans la caméra 3D.

**Corrigé en regardant la vidéo à 60 i/s.**
- La 3e carte était d'abord un grand X, le même que celui des planches de
  l'aérien : le X revenait deux fois, et le vrai final (f298) perdait sa
  signature. Elle est remplacée par le gros plan du poing ; le X reste
  réservé à l'aérien.
- Au premier instant après le gel, une image du plan du contact passait
  sous le fondu blanc. Le blanc est maintenant tenu 0,02 s après le gel,
  le temps d'atteindre la coupe de f151 (même règle en Luau, testée).

**Découverte, pas corrigée.** En caméra « Jeu », la victime reste cachée
derrière l'attaquant pendant presque toute la rafale, et l'éclat des coups de
base est masqué par son corps. Le lanceur voit la caméra ciné ; ce sont les
**autres joueurs** qui liraient mal la rafale. Question pour Milan.

**Preuves** :
- `captures/verification/2026-09-24-poing-dragon-v5-vs-v6-rafale-cote-du-bras.png` ;
- `captures/verification/2026-09-24-poing-dragon-v6-charge-et-impact-raconte.png` ;
- `captures/verification/2026-09-24-poing-dragon-v6-camera-de-jeu-shift-lock.png`.
