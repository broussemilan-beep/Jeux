# Catalogue des références de Milan : quel fichier, c'est QUOI, où c'est étudié

**Pourquoi ce fichier existe.** Retour de Milan, 2026-09-25 : « si je
t'évoque poing chargé puissant, ça devrait faire écho au Serious Punch de
Saitama, le GIF et l'anime TSB ».
- Pendant la relecture du jour, j'avais étudié le GIF du Serious Punch
  (48244687) sans le reconnaître : je l'ai appelé « perso cape jaune ».
- La mémoire existait (notes brutes, étude visuelle, fiche v7), mais rien
  ne reliait un fichier ou un mot à ce qu'on en sait.

**Ce fichier est cette liaison.**
- Les refs sont identifiées par le préfixe du fichier envoyé (dossier
  d'uploads de la session) et par l'empreinte sha1 (16 premiers
  caractères), qui est aussi celle des fiches `corpus/clips/*.json`.
- Doublons : même contenu envoyé plusieurs fois.
- Pour retrouver une ref par concept : `python3 outils/rappel.py "poing chargé"`.
- Les fichiers eux-mêmes (œuvres protégées) ne sont jamais versionnés.

## Coup chargé, poing puissant (Saitama, obari)

| fichier(s) | sha1 | ce que c'est | étudié dans |
|---|---|---|---|
| **48244687-image.gif = 91f083d4-IMG_3251.gif** | 762fae8e83adb9cc | **Serious Punch (TSB, Saitama), LE coup de ref**. Cape jaune, 10 s. Garde tenue 32 f, poussée caméra jusque dans le dos, saut vers le ciel, charge en très gros plan sur le poing dans la fumée, 3 cartes à l'encre (croquis, éclat, X) de 4 f, blanc 0,25 s qui se dissout en fumée. | `ETUDE_NOTES_BRUTES.md` « Serious Punch TSB », `REFERENCES_VIDEO.md`, `ETUDE_VISUELLE.md` (A, E, H), `RELECTURE_REFS_ANIMATION_2026-09-25.md` (48244687), fiche `clips/serious_punch_tsb.json` |
| **772ee6b0-image.gif** | 92c11db65569cadf | **« Serious Punch 2 », coup type Serious Punch (TSB)**. Manteau, 7 s. Poing armé près de la tête, accroupi très bas, poing tiré loin derrière, coup droit en gros plan vers l'objectif, cartes. | `ETUDE_NOTES_BRUTES.md` « serious punch 2 », `REFERENCES_VIDEO.md` §2, `RELECTURE…` (772ee6b0), `clips/coup_type_serious_punch_2.json` |
| **8965d689-image.webp** | d7e418577e72bc81 | Planche manga One Punch Man : le POING vers le lecteur, énorme en raccourci. | `ETUDE_NOTES_BRUTES.md` « Images fixes », essai `repro/saitama_obari.py` |
| **0ca551a4-image.webp** | ea7afcc9b89f6fcd | Deku, poing vers le lecteur (coup chargé aérien voulu par Milan, 2026-09-25). | essai obari (`repro/saitama_obari.py`, README repro) |
| 33393716-image.jpg | 815c6323115a7435 | Anime style Baki : charge BASSE et LARGE, lumière dorée du sol. | `ETUDE_NOTES_BRUTES.md` « Images fixes » |
| (sakuga) 162980 | — | OPM #12, Saitama contre Boros, « LA référence Saitama ». | `ETUDE_NOTES_BRUTES.md`, `refs/sakugabooru/` |
| (sakuga) 194936 | — | OPM #01, Saitama contre un géant : le coup MONTE, caméra sous le poing. | `ETUDE_VISUELLE.md` « coup qui part d'en bas » |
| 4e337114-image.gif | 7415a052b8f8f06e | Mannequin (Smash / Mii), coup chargé : armé ~1 s, extension tenue ~2 s. | `ETUDE_NOTES_BRUTES.md` « mii smash », `RELECTURE…` |

**Le fichier d'animations TSB** (`tsb_anim.rbxm`) ne contient PAS le
Serious Punch. Ses animations sont celles d'un autre personnage : M1-M4,
Collateral Ruin, Stoic Bomb, Swift Sweep, Ultimate1/2, WallCombo. Le Serious
Punch n'existe chez nous qu'en GIF.

## Techniques ultimes de jeux Roblox (structure en actes)

| fichier(s) | sha1 | ce que c'est | étudié dans |
|---|---|---|---|
| 12e7dae5 = b7a99d1c = f6d4785c (.mov) | 347e82b2b689555b | Black Flash (jeu type JJK). | `ETUDE_NOTES_BRUTES.md`, `ETUDE_VISUELLE.md` lot 4, `clips/black_flash_jjk.json` |
| 3ae71567 = 3d68d68c = b72851c4 | e99b8a2ab26f6765 | Rewind Clock (radios du crâne). | idem, `clips/rewind_clock.json` |
| 4fb4f776 = 74a15ce9 = b1460d93 | ad251c412c91996a | Stagnant Rage (caméra de jeu, échelle des effets). | idem, `clips/stagnant_rage.json` |
| 01f4b1d2 = 3340dc1a | 66053ffdf40a7241 | Black Hole Ability (compression/extension répétée). | `ref_15-52-25`, prototype `r6_black_hole` |
| 946bd286-image.gif | 732d4822f7e20d2e | « Coup chapeau » (LeftRight2601 + Mouchine VFX), coup vers le ciel puis cartes. | `clips/coup_chapeau_leftright.json` |
| 73cc1fb0 (.mp4) | 3a87f65bdec67a4a | Vidéo Gemini : invocation d'un soleil (IA). | `clips/gemini_soleil.json` |
| 58322fc4-image.gif | ac3458e5308aca17 | Boxeur type Ippo, ultime : esquive très basse, pose tenue en déplacement. | `ETUDE_NOTES_BRUTES.md` (58322fc4), `RELECTURE…` |
| a0341700-image.gif | 07ba7fb68f6e88b9 | Rafale « gatling » (type Luffy), caméra DE DOS : multiples autour de la silhouette. | idem |
| aafdc91d-image.gif | 96a4c3cd84d4569c | Perso orange, caméra de jeu lointaine : action, silence 0,3 s, action plus grosse. | idem |
| 6d3be6e1-image.gif | 6318e24f388d61fb | Jeu « Mythra » : saisie, projection, tenue sur la conséquence. | idem |

## Coups de poing, pro contre noob, tutos en boucle (Moon / Blender)

| fichier(s) | sha1 | ce que c'est | étudié dans |
|---|---|---|---|
| 9e47148b = afbe44bb = c8a6cffd | 8d16d0c3ac21ab6e | Pro contre noob, coup de poing (Moon, « BACK » puis « FRONT »). | `clips/pro_vs_noob_poing.json`, `ETUDE_NOTES_BRUTES.md` |
| 99a73bd5 | 5f7c3d94f572ac74 | Pro contre noob, épée (pro : 19 % de tenues, noob 0 %). | `ref_17-51-39`, `RELECTURE…` |
| f1b5bd4b | 27f7e25bc743eb21 | Pro contre noob, Blender (FRONT/BACK). | `ETUDE_NOTES_BRUTES.md` (f1b5bd4b) |
| 8556a37c (.mp4) | f4d2cc33986d20e1 | « Cross punch » (boucle d'un seul coup, extension tenue 0,13-0,2 s). | idem (8556a37c) |
| 6a0095ed (.mp4) | 495424c4d455da01 | « Punch practice » (vue de dessus : rotation du torse). | idem (6a0095ed) |
| afaa00eb | 0cf1b036d857ac93 | Tuto dessiné firytwig (armé / attaque / retour, « do not ease out », « skip the point of contact »). | idem (afaa00eb), `RELECTURE…` encadré |
| df406483 | 8a6449e2204dbf05 | « First time fighting a dummy » (ellipse, attitude tenue ~4 s). | idem (df406483) |
| fa7b867c-image.gif | 920250d54b7cc76a | Combo R6 « front » (rig coloré, rotations ~180°). | `clips/combo_r6_front.json` |
| 3ee5a405-image.gif | 8d62c92598c9d232 | Double jab R6. | `clips/double_jab_r6.json` |
| 449345ad-image.gif | 1abb7fe9ea2ce0f7 | Rue de nuit, M1 en place, vue de face. | `ETUDE_NOTES_BRUTES.md` (449345ad) |
| 37d7971a = 6e32f648 | 9f071ea001df3cca | Exemple Blender, combat à deux (projection). | `clips/exemple_blender_combat.json` |
| 85e1a98f (.mov) | 1c6f1c78be2b42be | Moon Animator combo (Linear, sans caméra / sans effets / ralenti). | `clips/moon_animator_combo.json` |
| eba5ed69 (.mp4) | efbddd20845ba72e | IMPACT HAVEN (19 impacts, silhouette + blanc d'1 f). | `clips/impact_haven.json` |

## Images d'impact et divers

- 41d7796b + a4a75c01 : même carte d'impact en deux polarités.
- 6dfb2f6c : hachures radiales à l'encre (type Serious Punch).
- 1727676e / 8d015f39 / 7263e0c8 : refs d'effets (feu, soleil).
- 095c28ec / 151f7f6d : trône et couronne (anciens projets).
- 14589186 / 50ace4b8 / 90118239 : captures de conversation.
- dfdb9286 : rig R6 Blender.
- Non identifiés dans les notes : 448c613e, 80ac271e, da606c23. À regarder
  à la prochaine relecture.
