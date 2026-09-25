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

## v7 (2026-09-24) : les poses du coup chargé

Retour de Milan sur la v6 (7/10) : « il manque une touche manga… même un coup
simple n'est pas un coup simple ». Avant d'animer, on a étudié le fichier TSB
officiel et 6 tutos vidéo (`../_shared/animator_brain/corpus/TUTOS_ANIMATION.md`
§7-8). Le diagnostic, mesuré, porte sur deux poses :
- **la charge était une croix** : torse droit (0-1°), deux bras à l'horizontale
  écartés, sur 93 % des images, contre 0 % chez l'attaquant TSB ;
- **le contact restait droit** : penché de 20°, et le bras libre partait vers
  l'avant avec l'autre.

Fiche : `FICHE_V7.md`. Décision de Milan : aucun coup de pied.

| temps | v6 | v7 |
|---|---|---|
| charge f121-146 | croix, torse droit | **« Serious Punch »** : racine penchée de 22° vers la cible, poing armé HAUT derrière l'épaule (+40°), bras avant replié qui vise bas, **genou avant levé** ; tenue **vivante** (oscillations du poing qui s'amortissent, f131/136/140/144) |
| départ f144-150 | clés 146 / 148 en courbes | **clé du milieu rapprochée** (148 → 149) et segments 144 → 146 → 149 → 150 en **Linear** : palier de vitesse du poing de 0,51 à **0,90** (TSB ≥ 0,85) |
| contact f150 | penché 20°, bras libre en avant (+0,88) | penché **36°**, bras libre **ramené à la hanche** (−0,64) ; torsion charge → contact gardée (129°) |
| rafale | armement du direct (h2) et de la fente (h4) en croix (13 images) | l'autre bras vise plus bas (−28°) : plus aucune croix |
| caméra ciné | secousse et punch-in à 100 % | **dosés à 70 %** sous la caméra ciné (lecteur et module Luau, `CINEMA_DOSE`) ; caméra de jeu inchangée |
| aérien, VFX, cartes, rythme | — | inchangés |

**Découvertes en posant les clés.**
- **Blocage de cardan** : torse tourné vers −80°, le tangage du bassin
  penchait le corps DE CÔTÉ, pas vers la cible. Pour la charge, on penche la
  **racine** (rotation X monde), ce qui donne une vraie bascule vers la cible
  (croquis contre rig, 1re passe écartée à l'écran).
- **Deux règles en conflit** : casser la croix de la rafale en armant le poing
  plus haut haussait l'épaule (0,30 stud ; règle « épaules jamais haussées »,
  retour de Milan v2 « bras trop hauts »). Solution retenue : ne pas toucher
  au poing armé, et faire viser plus bas l'autre bras.

**Contrôles.**
- règles : **13/13** ;
- contacts : 0,05 stud sur les 7 coups ;
- sens : 11/11 dans les fichiers, `SENS OK` en Luau, `PACKAGE OK` ;
- aucune croix sur tout le clip (`perception.silhouette`).

**Preuves** :
- `captures/verification/2026-09-24-poing-dragon-v7-charge-contact-avant-apres.png` ;
- `captures/verification/2026-09-24-poing-dragon-v7-video-v6-contre-v7.png` ;
- `output/poing_du_dragon_v7_charge_v6_contre_v7.mp4`.

**Ce que le cerveau mesure sur la v7** (`etats.py`, avant l'avis de Milan) :
- vrai : `silhouette_non_croix` (0 % au lieu de 93 %), `torsion_charge_contact` ;
- toujours faux :
  - `bascule_competence` : p90 36°, contre 44° pour les techniques TSB ;
  - `frappe_lineaire`, `bras_libre_ramene`, `ligne_epaules` : médianes sur
    TOUS les coups, que la rafale inchangée tire vers le bas. Sur le seul coup
    chargé, ils passent : palier 0,90, bras libre −0,64 ;
- **régression mesurée** : `coup_charge` passe à faux (tenue 4 f, départ 7 f).
  - À l'écran, la charge est tenue : le poing est à 0-4 stud/s de f130 à f144.
    Puis il part à pleine vitesse en 1 image (f145) et file en palier.
  - La mesure exige un torse figé, ce qui contredit la tenue vivante, et elle
    compte tout le palier comme un départ.
  - Un assouplissement a été essayé puis écarté : il validait les v1 à v4,
    jugées sans vraie charge. On laisse la mesure telle quelle, et c'est la
    note de Milan qui tranchera.

**Prédiction notée AVANT l'avis de Milan.**
- Critique du cerveau : **7,2** (il n'a jamais vu une note bouger sur une pose).
- Mon jugement après la vidéo : **7,8** (fourchette 7,5 à 8,3).
  - **Pour** : la charge et le contact se lisent enfin comme dans les refs.
  - **Contre** : en caméra de jeu, la charge de profil reste petite et étroite ;
    la rafale n'a presque pas changé ; la bascule reste sous TSB.
- Je baisse de 0,2 par rapport à l'estimation de la fiche (8,0) après avoir vu
  la caméra de jeu.

## v8 (2026-09-25) : la rafale refaite (timing, poses, placement)

Demande de Milan : « lance, mais travaille bien les poses et le placement,
avec ce que tu as appris ». Sources :
- `../_shared/animator_brain/corpus/CARNET.md` §2.1-2.8 ;
- la relecture de ses refs (`RELECTURE_REFS_ANIMATION_2026-09-25.md`) ;
- les tutos (firytwig, Dong Chang, Wimshurst, Williams).

**Le défaut mesuré.** Dans la v7, le poing se ré-armait aussi vite qu'il
frappait. Le rapport vitesse à la frappe / vitesse pendant la préparation
valait 0,55-1,49, contre 2,3-3,7 sur les M1 de TSB, même enchaînés. La
cause :
- le ré-armement tenait en ~6 images (garde c+10 -> armé c-10 du coup
  suivant) ;
- la frappe s'étalait sur 7 images, avec une arrivée amortie (Bézier c-3 -> c).

| | v7 | v8 |
|---|---|---|
| **timing d'un coup** | armé tenu 3 f, frappe 7 f amortie, retour à la garde puis ré-armement en ~6 f | retour **direct et lent** vers l'armé suivant (~11 f) ; armé **tenu vivant** c-10 -> c-4 (le buste s'enroule encore) ; frappe en 4 f avec **un seul intervalle près de l'armé** (c-2, 30 % du trajet) ; segments **Linear** jusqu'au contact, sans amorti ; **dépassement du corps** à c+2 ; extension tenue |
| **export rafale** | une clé par image cuite depuis l'IK (103 clés sur f1-109) | **poses posées seules** (34 clés, Linear), comme TSB (clé toutes les 2-4 f) |
| **armé** | lacet d'armé | lacet d'armé x1,4 (torse plus enroulé) |
| **bras libre au contact** | garde au visage (direct, crochet, fente) | **tiré en arrière** au direct, au crochet et à la fente : il lance la rotation (Wimshurst) et sort de la silhouette du torse |
| **fente finale** | torse droit | **racine penchée** vers la cible (+18°), diagonale du pied arrière au poing |
| **garde du bras libre** | au visage | à la poitrine (au visage, avec la bascule, elle haussait l'épaule) |
| **pas** | pied arrière cloué | le pied arrière **accompagne** un placement large (petit pas glissé) |

**Comment on a choisi.** Quatre variantes, construites dans le vrai
rig et jugées sur les mêmes critères (`scripts/planche_rafale.py`,
`scripts/regard_v7_vs_tsb.py`, `scripts/tutos_vs_tsb.py`, `check_rules.py`,
lecteur à vitesse réelle) :
- **A** : timing seul. 13/13 règles.
- **B** : timing + poses x1,4. Premier essai « tout gonflé » : le bras
  traversait le corps, contact raté de 0,30 stud, pied avant hors de portée
  (0,75), épaule haussée. Refait en poussant seulement l'armé, le bras
  libre et la fente. Puis 13/13.
- **B2** : B + bras libre tiré aussi au crochet (en garde haute, il
  masquait le torse en profil). 13/13. **Retenu.**
- **C** : x1,8, « trop » (protocole Dave Hand). Fente presque horizontale,
  la plus manga. Mais le pied avant flotte à 0,2 stud au contact et la
  posture dépasse la règle (0,263 > 0,24). Écarté.

**Mesures (v7 -> v8).**
- Contraste du poing, 3D : h1 0,71 -> 1,44 ; h2 1,49 -> 2,33 ; h3 0,55 ->
  1,93 ; h4 1,26 -> 2,63. TSB M1-M4 : 2,3-4,7.
- Contraste à l'écran, caméra de jeu : 0,40-0,61 -> 1,22-1,81.
- Amplitude du lacet du torse : 53-116° -> 67-133° (TSB 77-111°).
- Bascule des coups légers : inchangée, à dessein. Les M1 TSB ne penchent
  que ~12° ; pencher plus faisait descendre le torse (règle « posture
  droite », retour v1).
- Règles 13/13. Contacts à 0,05 stud. Épaule max +0,031 (seuil 0,088).
  Sens 11/11.

**Preuves** (`captures/verification/`) :
- `2026-09-25-rafale-v8-poses-v7-contre-v8.png` (armé | contact |
  extension, de profil) ;
- `2026-09-25-rafale-v8-vitesse-reelle-v7-contre-v8.png` (lecteur,
  caméra ciné, direct et fente) ;
- `2026-09-25-rafale-v8-contraste-v7-v8-tsb.png`.

Vidéo : `output/poing_du_dragon_v8_rafale_v7_contre_v8.mp4`. v7 à gauche,
v8 à droite, ciné en haut, jeu en bas. Vitesse réelle, puis ralentie x0,5.

**Ce qui n'a pas changé, et ce qui reste à juger.**
- Coup chargé, aérien, effets, cartes, caméra : inchangés.
- Les problèmes vus au regard vitesse réelle y restent : contact recouvert
  par les cartes, charge floue sous la caméra qui bouge. Ce sont les pistes
  suivantes du carnet.
- **Point à juger par Milan** : la fente v8 plonge au point qu'on voit le
  dessus du torse. C'est le côté « un peu trop », voulu.
- En caméra de jeu (de dos), la différence se voit surtout au rythme :
  armé tenu, puis frappe sèche. Les poses se lisent mieux en ciné et de
  profil.

## v9 (2026-09-25) : le coup final aérien, fait d'après la fiche de conception

Retour de Milan sur la v8 (7,5 ; jeu 7,8 et ciné 7,2, « à part le coup
final, pas encore travaillé »). Son « coup final » est le coup chargé
**aérien** (sa note v7 : « qui part toujours d'en bas ; comme sur les
images : Deku poing vers le lecteur, poing géant ; le coup chargé de
Saitama »).
- **Méthode.** Fiche de conception d'abord
  (`../_shared/animator_brain/corpus/fiches/COUP_CHARGE.md` : toutes les
  sources du coup chargé digérées ensemble). Puis construction, variantes
  jugées à l'œil en mouvement, comparaison visuelle au Serious Punch, et les
  chiffres en garde-fou seulement.
- **La v8, revue à l'œil avant de toucher à quoi que ce soit.** La charge
  suspendue dure ~1 s et on la voit DE DOS, poing levé au-dessus de la tête,
  donc dans la colonne du corps. Plongée et contact illisibles (blocs plein
  cadre).

| temps | v8 | v9 (grammaire du Serious Punch) |
|---|---|---|
| 200-224 | charge de dos, aura dès l'apex | **calme** : il flotte à l'apex, bras relâchés, regarde la victime ; plan moyen DE FACE, fixe ; pas d'aura |
| 224-256 | — | **armé** : départ en 6 f, le buste part d'abord, dépassement, puis tenue vivante. Silhouette ouverte en K : poing armé HAUT derrière l'épaule, bras avant placé vers la victime, genou devant, jambe arrière qui traîne. Plan de profil, corps entier, lente poussée ; aura et poing qui s'allument ici |
| 256-278 | contre-plongée depuis sous la victime | **frappe vers l'objectif (obari)** : caméra CHEZ la victime, à côté d'elle, grand angle. Le corps bascule d'abord, le poing traîne (fouet). Le bras s'étend en 3 f, puis tout le corps fonce le long de l'axe, poing devant, et le poing grossit jusqu'à remplir le cadre, tête derrière |
| 279-288 | même plan | coupe après le gel du contact : la chute, de côté, les deux corps dans le cadre |
| 288 et après | — | inchangé (écrasement, planches manga, blanc, révélation) |

- **Trois variantes vues avant de choisir.**
  - 1re pose d'armé : un tas. Le bras qui « vise » la victime juste en
    dessous pendait ; le genou « levé » partait en arrière (axes locaux du
    contrôle de jambe).
  - Refaite en directions monde (nouveau mode `"d"` de `solve_pose`),
    choisie grâce au tour de la pose à 8 angles
    (`../_shared/animator_brain/outils/tour.py`, CARNET §3.8).
  - Caméra d'armé : de face, le bras avant venait dans l'objectif et
    cachait tout ; trop serrée, le genou venait dans l'objectif ; retenue
    de profil, corps entier.
- **A contre B, jugées à vitesse réelle dans les deux caméras.**
  - A = poing armé à la hanche (Serious Punch) ; B = poing armé haut
    derrière l'épaule (planche Xoaterz « akin to TSB »).
  - **B retenue** : en caméra de jeu (de dos), le poing levé qui brille sort
    de la silhouette. Avec A, le corps reste une colonne.
  - `DRAGON_FINAL=v8` rejoue l'aérien v8, `v9a` la variante A.
- **Comparé ensuite au GIF du Serious Punch** (côte à côte, temps par temps ;
  planche locale, le GIF n'est pas versionné).
  - Même grammaire : calme de face, armé, poing vers l'objectif, carte,
    blanc, conséquence tenue dans le cratère.
  - Moins bien chez nous : leur gant sombre dans la fumée est une forme
    nette et remplit la moitié du cadre ; nos anneaux dorés du dragon
    encombrent le poing. Leur armé est filmé plus près et plus bas.

**Contrôles.**
- contacts : 0,05 stud sur les 7 coups ;
- aérien : le poing ne traverse plus la victime après le contact (v8 : 0,087).
  La 1re passe visait une allonge de 2,0 studs, alors que le bras R6
  n'atteint que ~1,85 ; le poing s'arrêtait à 0,34 de la cible.
- sens : 11/11 dans les fichiers, `SENS OK` en Luau, `PACKAGE OK` ;
- règles : **12/13**. L'échec est « plongée lisible (plan sans coupe) » : 9 f
  pour un seuil de 20.
  - La plongée VERS le poing tient en un plan sans coupe de 22 f (f256-278),
    ce que demande la leçon 3b.
  - La fenêtre de la règle court jusqu'à l'écrasement au sol (f288), et la
    v9 coupe volontairement après le contact, comme le Serious Punch.
  - On garde la coupe. Une règle qui échoue est un signal à regarder, pas un
    veto (CARNET §1.9) : c'est à Milan de trancher.

**Preuves** :
- `captures/verification/2026-09-25-coup-final-aerien-v8-contre-v9.png` ;
- `captures/verification/2026-09-25-coup-final-v9-tour-de-la-pose-arme.png`
  (pose d'armé retenue, vue de 8 angles : de profil, le K est ouvert ; de
  dos, le poing sort de la silhouette).

**Ce que le cerveau mesure sur la v9** (`etats.py`, avant l'avis de Milan) :
- états mesurés **identiques à la v8**. Les mesures regardent les coups au
  sol (rafale, charge de f150), pas la mise en scène de l'aérien : calme,
  caméra, poing vers l'objectif. C'est un angle mort du cerveau, noté ici ;
- l'aérien n'est vu que par les hypothèses de jugement (`obari_poing_objectif`,
  `pose_pour_sa_camera`, `pose_vue_nette`), renseignées à l'œil ;
- honnêtement : `arme_tenu_long` passe à faux (armé tenu ~0,5 s, contre
  ~0,9 s pour la charge suspendue v8).

**Prédiction notée AVANT l'avis de Milan.**
- Critique du cerveau : **7,4**. C'est sa prédiction de la v8 : ses
  hypothèses « obari » n'ont encore jamais vu une note bouger.
- Mon jugement : **7,9** (caméra de jeu 8,0 ; ciné 7,9 ; fourchette 7,5 à 8,3).
  - **Pour** : le coup final suit enfin la grammaire du Serious Punch, que
    Milan cite depuis la v4, et ça se voit à vitesse réelle, pas seulement
    sur des images figées.
  - **Contre** :
    - les anneaux dorés encombrent le poing ;
    - le visage R6 souriant apparaît dans le plan obari ;
    - en caméra de jeu, la plongée reste un bloc vu de dos ;
    - l'armé n'est tenu que 0,5 s.

## v10 (2026-09-25) : les VFX et le SON passent au studio VFX

L'animation ne change pas (v9, mise en pause après le 7,7 de Milan). Ce qui
change : les effets et le son, faits avec le studio VFX
(`../_shared/vfx_studio/`), qui a UNE recette par effet, jouée à
l'identique par le labo, par ce lecteur et par le moteur Roblox
`VFXStudio.luau`.

| moment | avant (v9) | maintenant (recettes studio) | son |
|---|---|---|---|
| rafale, coups 1-3 (tier 1) | éclat + anneau codés à la main | étoile 2 images, anneau fin, petit croissant, éclats orientés | fouet 8 f avant, frappe sèche au contact |
| coup 4 (tier 2) | + halo, étincelles | + dôme court, croissant de vent 3D qui tourne | + coup grave léger |
| coup chargé | impact + dôme + souffle | contact tier 2 ; APRÈS les cartes, explosion cel dans l'axe du coup (feu peint, fumée 2 tons, vent) + anneau et vague au sol ; la victime projetée laisse un **sillage d'air** et de fumée | craquement au contact, **silence pendant le noir**, boum + grondement quand les cartes tombent |
| arme de l'aérien | — | (l'aura reste celle de v9) | aspiration + tonalité d'énergie |
| plongée | — | **sillage d'air** sur le trajet du poing (ruban + lignes de vitesse semées derrière) | souffle qui monte, coupé 60 ms avant le contact |
| contact aérien | impact codé à la main | explosion EN L'AIR (sans couches au sol, dôme orienté dans le sens du coup) | impact lourd |
| impact au sol | impact + dôme | explosion complète : onde en dôme, anneau, vague à dents, feu, fumée | impact lourd plus grave + long grondement |

Gardés de v9 (pas encore refaits) : aura, poing qui brille, dragon de fumée,
cratère, braises, planches manga, écran blanc, cartes.

**Réglé à l'œil sur les captures** : 1er essai aux échelles 1,1 (contact
aérien), 2,1 (sol) et 1,3 (explosion du coup chargé) ; la caméra obari est à
1,5 stud du contact et le feu cel à 2,1 fait 11 studs par particule, donc
l'effet avalait le cadre et cachait les corps. Échelles retenues : 0,55 / 1,4
/ 0,9.

**Roblox.** `DragonFist.luau` joue chaque événement « studio » avec
`VFXStudio.jouer(recette, repère de la scène)` ; les événements « impact »
ne gardent que hitstop, secousse et punch-in. Le flash du corps utilise un
seul `Highlight` créé au lancement (en créer un par coup provoque des pics de
coût). Le package contient `VFXStudio` et `VFXRecettes` ; les 9 recettes du
Dragon passent le banc de test Luau du studio
(`../_shared/vfx_studio/luau/run_test.py --recettes …`, 107 contrôles).
Textures et sons n'ont pas encore d'identifiant Roblox : ils sont listés comme
manquants (repli : texture intégrée de Roblox, aucun son).

**Lecteur.** Bouton « Son » : les mêmes WAV qu'en jeu, placés au temps réel
(hitstops compris). Vidéo avec son : `scripts/video_son.py`.

## v11 (2026-09-25) : l'aura DRAGON (Goku x Izuku)

Refs de Milan : le Poing du Dragon de Goku SSJ3 (film DBZ 13 : affiche,
illustration, GIF du ciel, GIF du coup), « à mélanger avec Izuku ». Fiche de
conception : `../_shared/animator_brain/corpus/fiches/AURA_DRAGON.md`.

- **Le dragon (Goku)** : corps = chaîne de 27 Beams avec des écailles
  peintes qui défilent (nageoires dorsales brunes, écussons dorés, ventre
  crème) ; tête = carte peinte (gueule ouverte, crocs, arcade en colère,
  moustaches, cornes, crinière de flammes) toujours face caméra. Textures :
  `../_shared/vfx_studio/peints.py`.
- **Le courant (Izuku)** : éclairs VERTS One For All qui crépitent autour du
  poing et du corps, de l'armé au contact ; éclairs verts et or à l'impact.
- **Trois temps** :
  1. armé (236-256) : le dragon SORT du poing, s'enroule autour du bras puis
     derrière le corps ; tête gueule ouverte à côté du poing (l'affiche) ;
  2. plongée : il RENTRE dans le poing (dernière image de la tête ~f262),
     il reste le sillage d'air et les éclairs ;
  3. impact : tourbillon de feu (le GIF), puis le dragon SORT du cratère,
     tourne autour en montant, rugit pendant la révélation, se dissout.
- **Son** : crépitement électrique (Izuku), rugissement à la naissance et un
  grand rugissement à la sortie du cratère.
- **Roblox** : les couches `serpent` et `eclairs` du moteur VFXStudio
  (Beams recyclés, jamais recréés ; tête = Part invisible + 2 Decals, la face
  avant porte la texture MIROIR pour que le museau suive le cou des deux
  côtés). Banc Luau : 143 contrôles dont « aucun objet créé pendant la
  lecture » et « tête face caméra, à l'endroit ».

**Essais vus à l'écran et abandonnés.**
- Tête dans l'axe du cou : en caméra obari, carte vue par la tranche,
  invisible -> carte face caméra, museau le long du cou PROJETÉ.
- Tête devant le poing à la plongée : passe derrière la caméra (qui est
  chez la victime) ; à côté : grossit et cache l'attaquant ; qui s'écarte :
  c'est le COU qui passe devant l'objectif. En obari, tout ce qui longe le
  bras bouche le plan -> le dragon rentre dans le poing et ressort à
  l'impact, comme dans le film.
- Montée en colonne de 15 studs : tête toujours hors du cadre de la
  révélation -> spirale large et basse (4,7 studs) autour du cratère.

## v12 (2026-09-25) : la pose Goku x Izuku et le dragon « premium »

Retour de Milan sur la v11 (VFX 4/10) : « mélange » voulait dire la POSE
(Goku puis Izuku), pas les éclairs d'Izuku ; le dragon est « moche, pas du
tout premium » ; les VFX construits sont loin du pack et des refs. Fiche :
`../_shared/animator_brain/corpus/fiches/AURA_DRAGON.md` §0 et §0 bis.

- **Éclairs verts retirés.** La pose raconte le mélange :
  1. invocation (Goku, affiche e92ac0d7 + GIF f254bee5) : bras droit tendu
     vers le ciel en « V », poing gauche armé à la hanche, jambes qui
     traînent, regard devant menton levé ; caméra 3/4 face ;
  2. plongée (Izuku, 0ca551a4 / 09a83af0) : le corps bascule, le poing
     passe au-dessus de la tête puis se tend vers l'objectif, épaule en
     avant, tête basse, autre bras rentré, jambes ensemble derrière.
- **Dragon 3D riggé** (`../_shared/vfx_studio/modeles/`) : écailles de
  ~0,5 stud peintes en volume, dos orange profond, ventre crème, crinière
  et nageoires brunes, gueule ouverte ; il s'enroule DERRIÈRE le perso et
  dresse la tête de profil au-dessus du poing ; à l'impact il sort du
  cratère, nimbé de FEU qui coule le long du corps (`recettes.flammes_corps`).
- **VFX construits** : débris de sol peints (4 formes, gravité) sur les
  impacts au sol ; bloom dans le lecteur (= BloomEffect du jeu) ; débris
  physiques du cratère recolorés.
- **Bug corrigé** : la forme du dragon avait 10 images d'avance sur le corps
  (temps relatifs lus comme temps de recette).
- **Roblox** : importer `../_shared/vfx_studio/modeles/dragon.fbx`
  (3D Importer de Studio : un Model avec le MeshPart et ses Bones), le
  renommer `DragonModele` et le
  poser à côté de `DragonFist` ou dans ReplicatedStorage : `DragonFist` le
  donne au moteur (`vfx.configurer({modeles = {dragon = …}})`). Absent : repli
  sur le ruban de Beams + carte. Banc Luau : 146 contrôles, TOUT OK.

**Essais vus à l'écran et abandonnés** (captures dans
`../../captures/verification/2026-09-25-v1*`).
- Invocation v10a : genou levé devant le torse, tête cachée, caméra à -22°
  sous le corps : un tas illisible.
- Bras visé à 1,55 stud : couché en travers de la tête ; à 2,4 : tendu.
- Regard visé droit au-dessus : tête basculée de 90°.
- Cou du dragon vertical (pilier doré), puis tête piquée vers la victime
  (on voyait le crâne) -> tête horizontale de profil.
- Spires autour du bras devant le visage -> décalées derrière le perso.
- Caméra obari : le bras tendu traversait l'objectif (prisme brun).

## v13 (2026-09-25) : la scène refaite — le coup DEVIENT le dragon d'or qui mange

Retour de Milan sur la v12 (note 4 ; animation 7,7, VFX 2-4) : « le dragon
apparaît 0,5 s et pas au bon endroit » ; puis : « le dragon OR est invoqué
dans les airs comme Goku, puis le coup se transforme en le dragon qui mange
le perso ; refais tout, niveau 8,5/10 ; VFX qualité dessin, pas du cube ou
cartoon ; améliore l'architecture, vérifie le jugement ».

Conception : `../_shared/animator_brain/corpus/fiches/POING_DU_DRAGON_V13.md`
(d'après Last Breath v1-v3 et le Poing du Dragon de Goku relus à 0,1 s :
`corpus/RELECTURE_LAST_BREATH_GOKU_2026-09-25.md`).

| frames | acte | ce qui se passe |
|---|---|---|
| 0-200 | rafale, coup chargé, envol | inchangés (impacts avec un trait de pinceau dessiné) |
| 200-224 | calme | il flotte au-dessus de la victime |
| 226-340 | **invocation, 1,9 s tenue** | poing au ciel ; le dragon d'or JAILLIT du poing, s'enroule dans le ciel, rugit en gros plan (gueule qui s'ouvre) |
| 340-378 | regard, armé, coup | il regarde la victime, le poing recule, il frappe À DISTANCE ; le dragon rentre dans son poing |
| 378-400 | **le coup devient le dragon** | flash, la tête sort du poing, ouvre la gueule, claque : la victime est AVALÉE (f400) |
| 420-566 | **plein écran 2,45 s** | carte manga de la gueule à l'encre (tirée de notre modèle), tourbillon de feu peint joué en 2, rouge radial, soleil à silhouette |
| 566-760 | **conséquence 3,2 s** | cratère, le dragon jaillit du sol vers le ciel, recrache la victime qui retombe ; l'attaquant atterrit en 3 appuis |
| 760-830 | retour | il se relève |

Nouveau dans la chaîne :
- `scripts/scene_v13.py` : caméra et effets après l'apex, les 3 couches
  du dragon échantillonnées sur les pistes exportées ;
- `scripts/build_planches.py` : les planches plein écran
  (`python3 build_planches.py <rendu de la gueule>` ; le rendu vient du labo,
  recette `dragon_gueule_demo`, caméra « face ») ;
- dragon (`../_shared/vfx_studio/modeles/dragon.py`) : aplats deux tons,
  écailles en trait, yeux cyan, os `Machoire` (piloté par `machoire` dans la
  recette ; Roblox : `Bone.Transform`) ; FBX réexporté ;
- `DragonFist.luau` : planches (`CONFIG.PLANCHE_IDS`, par nom ; repli en
  aplat), victime cachée (`LocalTransparencyModifier`) de la morsure au
  recrachat, teinte dorée bornée par les marqueurs ;
- juge temporel : `../_shared/animator_brain/outils/juge.py` (voir plus bas).

Roblox, en plus de la v12 : importer les 8 PNG de `output/planches/` et
mettre leurs IDs dans `DragonFist.CONFIG.PLANCHE_IDS` ; réimporter
`dragon.fbx` (os Machoire).

**Tête refaite (v13b, retour de Milan : « les yeux cassent le truc, trop
cubique, pas assez travaillé »)** : sections arrondies, museau court et
haut, arcades, œil or à fente sous l'arcade, crinière de flammes, texture
de tête ; avant/après : `../../captures/verification/2026-09-25-v13b-tete-dragon-avant-apres.png`.

**Juge temporel** (`../_shared/animator_brain/outils/juge.py`, seuils =
0,8 x médiane de 6 ultimes de référence), sur la vidéo finale
`../../captures/verification/2026-09-25-v13-scene-complete-avec-son.mp4` :

| critère | v12 | v13 | seuil |
|---|---|---|---|
| part d'effet au pic | 0,33 | 0,71 | 0,70 |
| temps plein écran | 0 s | 1,13 s | 0,66 s |
| plus longue plage plein écran | 0 s | 0,77 s | 0,48 s |
| conséquence | 0 s | 5,2 s | 3,4 s |

Porte franchie (v12 : 0 critère sur 4). Bandes à 0,1 s :
`2026-09-25-v13-bande-0.1s-*.png` ; moments clés : `2026-09-25-v13-moments-cles.png`.
Vu à la bande et corrigé avant de livrer : 2 s de plan vide et sombre dans
la conséquence (le dragon sortait du cadre) -> il s'envole en grand arc
visible, puis plan moyen sur les deux corps.

### v13c (2026-09-25) : revue sans Milan + planches dessinées

**Revue sans indication** (« revois, il y a des problèmes, je veux voir si
tu vois sans moi ») : douze défauts trouvés plan par plan et corrigés,
liste dans `../_shared/animator_brain/RETOURS.md`. Les principaux : à la
fusion, c'est le MUSEAU (6 studs devant l'os) qui touche le poing, éclat
d'or, le dragon s'engouffre, le poing garde le feu ; la tête naît derrière
l'attaquant, pas devant ; victime en contre-plongée (ciel derrière) ; flash
quand elle est avalée ; atterrissage à côté de la colonne de feu ; dernier
plan de côté ; cadrages qui coupaient l'attaquant ; en Luau le dragon 3D
ignorait sa transparence. Avant/après :
`../../captures/verification/2026-09-25-v13c-revue-sans-milan-avant-apres.png`.

**Planches plein écran redessinées** (Milan : tourbillon et rouge « trop
peinture, pas dessiné », soleil « bonne idée, à faire beaucoup mieux ») :
formes tracées (lames effilées cernées, traits du feu, lignes de vitesse),
silhouette du soleil = notre modèle (`dragon_silhouette_demo`) ; le
tourbillon est carré. Fiche : `../_shared/animator_brain/corpus/fiches/PLEIN_ECRAN.md` ;
avant/après : `../../captures/verification/2026-09-25-v13c-planches-dessinees-avant-apres.png`.
Refaire : `python3 scripts/build_planches.py <rendu_gueule.png> <rendu_silhouette.png>`.
Roblox : réimporter `output/planches/spirale_*.png`, `rouge_*.png`,
`soleil.png` (mêmes noms) dans `DragonFist.CONFIG.PLANCHE_IDS`.

Juge temporel sur la vidéo v13c
(`../../captures/verification/2026-09-25-v13c-scene-complete-avec-son.mp4`,
bandes `2026-09-25-v13c-bande-0.1s-*.png`) : part d'effet au pic 0,83
(v13 : 0,71 ; seuil 0,70), plein écran 1,13 s, plus longue plage 0,80 s,
conséquence 5,2 s : porte franchie.

### v13d (2026-09-25) : le dragon s'affiche enfin chez Milan ; planches retirées

- **Bug** (« le dragon n'apparaît pas là où il faut, et très peu ») : la
  page publiée chargeait three.js r128 (CDN) ; avant r129 un SkinnedMesh
  exige `material.skinning = true`, sans quoi le dragon restait figé en
  pose de repos. Toutes les vérifications tournaient en r134 (copie
  locale) et ne pouvaient pas le voir. Corrigé : three.js r134 est
  EMBARQUÉ dans le lecteur (`build_player.py`, `/*__THREE_JS__*/`) et
  `moteur.js` pose `skinning = true`.
- **Planches** tourbillon / rouge / soleil retirées (Milan : « ça ne rend
  pas bien pour du Roblox premium ») ; la carte de la gueule reste (0,5 s).
  Roblox : ne plus importer `spirale_*`, `rouge_*`, `soleil`.
- **Le dragon se montre** à leur place (f400-f574) : la victime dans la
  gueule, il monte en grande boucle dans le ciel au-dessus de l'arène, se
  retourne au sommet et replonge dans le cratère au blanc. Trois plans :
  très large face à la boucle, contre-plongée au sommet, depuis le cratère.

