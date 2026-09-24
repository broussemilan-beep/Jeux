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
