# « Un seul coup » (Serious Punch R6) — cinématique

Proposition 1 de `animator_brain/PROPOSITIONS_CINEMATIQUE_2026-09-26.md`,
choisie par Milan (« Vazy 1 »). Conçue AVANT toute clé dans la fiche
`animator_brain/corpus/fiches/UN_SEUL_COUP.md` (Serious Punch TSB, Serious
Punch 2 et Serious Punch de Pew relus à 0,1 s).

**Calme, un élan, UN coup. Puis la conséquence qui dure** : le sillon de
roches file jusqu'à l'horizon, les nuages se fendent, il se redresse.

## La scène v1 (60 i/s, 12,5 s ; départ et charge remplacés en v2, ci-dessous)

| s | moment | caméra |
|---|---|---|
| 0-1,3 | entrée : de dos, la plaine, la victime au loin | poussée jusque DANS son dos (transition) |
| 1,3-2,6 | CALME : debout, visage plat ; un voile de poussière passe | plan moyen de face, fixe |
| 2,6-3,05 | il se ramasse et part | fouet vers le ciel |
| 3,9-4,35 | armé : buste tordu, poing à la hanche, genou haut, tenue qui tremble | très gros plan, contre-plongée |
| 4,35-4,72 | frappe : le poing vient VERS l'objectif, contact sauté | regard de la victime (masquée) |
| 4,72-5,35 | 2 images inversées (4 i chacune), blanc, dissolution | 3/4 de la fente, puis la ligne vers l'horizon |
| 5,35-8,6 | conséquence 1 : fente tenue ; la vague de roches file (250 studs/s, 470 studs), colonnes de fumée | 3/4 haut, derrière lui |
| 8,6-10,3 | conséquence 2 : les nuages se fendent, le sillon apparaît dedans | au-dessus des nuages |
| 10,3-12,5 | conséquence 3 : il se redresse, regarde au loin ; fondu au noir | profil bas, la ligne derrière lui |

Seuls moments rapides : l'élan + la glissade (~1 s) et la frappe (0,37 s).

## v2 (retour de Milan sur la v1, 2026-09-26)

« Le perso doit aller ultra vite : tu casses le sol de son point de départ,
puis la scène apparaît avec la charge et la frappe » ; « il frappait vers le
bas ; il charge son poing en le ramenant à l'arrière et en tournant son
buste » (+ 4 refs anime : Gon, Saitama ×3 ; fiche §6).

| s | v2 |
|---|---|
| 2,6-2,83 | il se ramasse (profil, en entier) |
| 2,83-2,88 | il part en 3 images : le sol CASSE (trou fissuré, dalles, poussière), sillage jusqu'à la victime ; 0,27 s sur le trou vide |
| 3,1-4,52 | coupe : il est devant la victime et CHARGE (1,4 s) : appuis larges, buste qui tourne jusqu'à -66°, poing derrière, tenue qui tremble, cailloux qui se soulèvent, vent autour du poing |
| 4,52-4,72 | frappe à PLAT, vue par la victime |

Mesuré au contact : v1 buste 40°, poing à 2,5 studs (bas-ventre) ;
**v2 buste 7°, bras -5°, poing à 3,4 studs (poitrine), bras à -3° pendant
la tenue**. Nouveaux contrôles dans `verify_export.py` (bras à plat, buste
droit, poing à hauteur de poitrine, poing derrière pendant la charge).
Avant/après : `captures/verification/2026-09-26-un-seul-coup-v1-contre-v2-depart-charge-coup.png` ;
vidéo `2026-09-26-un-seul-coup-v2-scene-complete-avec-son.mp4`.

## v3 : le poing chargé (clip de Milan ; v2 notée 7/10)

La charge est refaite en ARC QU'ON TEND (fiche §7) : garde à l'arrivée ->
il s'enfonce et tourne jusqu'au profil, les deux bras s'alignent tendus
(poing loin derrière, l'autre bras vers la victime) en 0,4 s -> tenue qui
tremble (3,55-4,43 s) -> dernière compression -> détente 12 i, poing à
plat. Caméra de face côté poitrine. Contrôles d'export inchangés et tous OK
(coup à plat : buste 7°, bras -5°, poing 3,4 studs). Avant/après :
`captures/verification/2026-09-26-un-seul-coup-v2-contre-v3-poing-charge.png`.

## v4 : la pose de charge (Milan sur la v3 : « aucun changement »)

C'était la POSE : la v3 chargeait debout, bras en croix. Les refs (Pew,
TSB, SP2, revues en grand) chargent RAMASSÉES : genoux très pliés, buste
courbé en avant, tête basse, bras écartés sous le buste. v4 : buste 57°,
hanches -1,05, caméra de sa droite un peu de face (tour à 8 caméras). Coup
toujours à plat. Avant/après :
`captures/verification/2026-09-26-un-seul-coup-v3-contre-v4-pose-de-charge.png`.

## Chaîne (réutilise celle du Poing du Dragon)

```bash
B=<chemin>/Blender_R6.blend
cd experiments/r6_un_seul_coup/scripts
python3 verify_export.py $B        # anime (coup_clip.py), contrôles, exporte les 2 KeyframeSequences (~45 s)
python3 planche_poses.py $B <png>  # planche des poses clés (profil + 3/4 face), avant tout le reste
python3 build_player.py            # staging.py (caméra, décor, destruction, sons) + lecteur HTML (three.js r134 embarqué)
python3 build_roblox_package.py    # UnSeulCoupData.luau + output/UnSeulCoup.rbxmx
python3 ../luau/run_sens_test.py <luau>   # test de sens (interpréteur Luau officiel)
python3 video_son.py <mp4> 30      # vidéo avec son (~8 min)
```

- `coup_clip.py` : les poses (mêmes solveurs que `dragon_clip.py`, importé).
- `staging.py` : caméra (25 clés), décor (plaine, montagnes, 120 nuages),
  la destruction (451 roches en deux murs qui s'ouvrent en V, fond du
  sillon, 60 colonnes de fumée, nuages qui s'écartent), écran, sons.
- `player_template.html` : lecteur dédié (roches et débris en InstancedMesh,
  fumées en sprites, images inversées par échange de matériaux).
- `luau/UnSeulCoup.luau` : le module de jeu (même source `staging.json`).

## Vérifications (2026-09-26)

- Export : contact poing / torse 0,05 stud ; sol : plus bas −0,078
  (aucune image sous −0,1) ; tête jamais décalée ; aller-retour moteur
  exact ; réduction de clés ≤ 0,015 stud ; interpolation Linear partout ;
  SENS Roblox OK (7 contrôles). Clés : 134 attaquant, 58 victime.
- Package : PACKAGE OK (références uniques, pose de repos, sens, 10
  markers, 3 scripts, démo en client).
- Test de sens Luau : SENS OK (placement, roches devant / au sol / dans
  l'ordre de la distance / jusqu'à 470 studs, nuages qui s'écartent,
  caméra, images tenues, son d'impact au contact et vide avant,
  ordonnanceur, positions de fin).
- Relecture de la vidéo à 0,1 s (bandes `durees.py`) : voir
  `captures/verification/2026-09-26-un-seul-coup-bande-0.1s-*.png`.

## Corrigé en regardant (avant de montrer)

- Pieds sous le sol pendant l'élan (−0,57) et la glissade : l'élan décolle,
  la jambe arrière est moins étirée.
- Genou « haut » de l'armé impossible (point hors de portée d'une jambe R6
  rigide) : posé en direction.
- Bras qui montait à 45° juste avant le contact (cible trop proche) : il
  part à plat.
- Plan de frappe : le torse de la victime couvrait la moitié de l'image ->
  la caméra prend sa place (regard de la victime), elle est masquée.
- 1re image inversée noire aux 2/3 (plan trop serré) -> profil large.
- Sillon qui semblait s'arrêter à 60 studs (filmé dans son axe) -> 3/4 haut ;
  roches qui grandissent avec la distance (le V s'ouvre).
- Nuages qui se fendaient 3 s avant le plan qui les montre -> calés dessus.

## À vérifier dans Studio (pas de moteur Roblox dans ce bac à sable)

- Les 2 images inversées en jeu : Highlight noir opaque sur les persos et le
  sillon + ColorCorrection qui blanchit le décor (approximation).
- La tenue des ~450 CornerWedge + ~700 boules de nuages (option
  `CONFIG.NUAGES`), et les sons : importer les WAV du studio
  (`_shared/vfx_studio/sons/*.wav`) et remplir `CONFIG.SOUND_IDS`.
