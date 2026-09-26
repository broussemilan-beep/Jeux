# Inventaire VFX de combat : ce que le dépôt sait déjà

Je n'ai écrit aucun fichier dans le dépôt.

**Abréviations des chemins** (tous sous `/home/user/Jeux/`) :
- `AB/` = `experiments/_shared/animator_brain/`
- `C/` = `AB/corpus/`
- `PD/` = `experiments/r6_poing_dragon/`
- `DF` = `PD/luau/DragonFist.luau`
- `ST` = `PD/scripts/staging.py`
- `v3` = `docs/ARCHITECTURE_VFX_v3.md`
- `A` = `docs/ARCHITECTURE_VFX_v3_addendum_A.md`
- `CK` = `experiments/_shared/vfx_craft_checklist.md`

**Le skill roblox-vfx** : il n'y en a **aucun dans le dépôt**, ni dans `.claude/` ni dans les autres dossiers cachés. Le seul exemplaire trouvé est hors dépôt : `/home/user/astrablox/astrablox/.agents/skills/roblox-vfx/SKILL.md` (318 lignes, licence MIT). Je l'ai lu. Le dépôt n'en contient qu'une adaptation partielle, `CK`, écrite le 23/09 (commit b55d13a). Cette adaptation ne reprend que les principes (3 temps, couches, défauts d'amateur, `CK`:26-80). Les sections §2 à §8b du skill n'ont jamais été reprises : réglages des ParticleEmitter, Rate contre Emit, Beam/Trail, mesh VFX, flipbooks, bibliothèques (Effect Designer Suite, Lightning Beams, Mesh Flipbook Pack, GG Camera Shake).

---

## 1. Principes VFX appris

Statut : **V** = validé par Milan (une note ou un retour le confirme), **P** = validé en partie ou de façon confondue avec d'autres changements, **T** = resté théorique (jamais appliqué, ou appliqué sans jugement de Milan).

| Principe | Énoncé et chiffres | Sources | Statut |
|---|---|---|---|
| **Hiérarchie des effets** | L'effet est proportionnel au coup : petit coup = lignes de vitesse 2-3 f ; gros coup = étoile 1 f → anneaux 2 f → croissant 2-3 f | `AB/hypotheses.json`:525-546 ; `C/ETUDE_VISUELLE.md`:237-243, 292-295 ; `C/ETUDE_NOTES_BRUTES.md`:190, 201, 224 | **P** : appliquée en v6 (`PD/FICHE_V6.md`:27-49), note 6,8 → 7. `AB/REFLEXION.md`:46 la dit « vraie dans 100 % des parties aimées, 0 % des rejetées ». Mais le palier 1 est **invisible en caméra de jeu** (`PD/README.md`:459-462) |
| **Cartes d'impact** | 2 à 8 cartes de 2-4 f : silhouette inversée, encre, négatif, postérisation, aplat, cible | `C/ETUDE_VISUELLE.md`:51-74 ; `AB/hypotheses.json`:263-286 ; `C/tutos/rapport_video_techniques_anime.md`:55-72 (de 1 f chez Deku à ~55 f chez Chansard) | **P** : présentes dans l'aérien, que Milan aime depuis la v1 (`AB/notes_milan.jsonl`:1 ; `C/ETUDE_NOTES_BRUTES.md`:71), et au coup de f150 en v6 |
| Cartes : varier la forme d'une image à l'autre | Les nôtres sont tirées d'une seule pose ; les pros changent la forme à chaque image | `C/tutos/etude_complete_techniques_anime.md`:16-23 | **T** |
| **Blanc total** | 2 à 15 f au pic, souvent en alternance avec le noir (4 f/4 f), ou blanc qui se dissout en fumée | `AB/hypotheses.json`:308-328 ; `C/ETUDE_VISUELLE.md`:93-100 | **P** (aérien aimé, v6) |
| **Noir, le « silence »** | 2 à 10 f de noir avec une petite étoile, avant le boum | `AB/hypotheses.json`:287-307 ; `C/ETUDE_VISUELLE.md`:76-91 ; coup chapeau 8-12 f (`C/ETUDE_NOTES_BRUTES.md`:5) | **P** : appliqué en v6, jamais jugé isolément |
| **Smear graphique / trajectoire dessinée** | Traînée blanche sur 4-8 f ; croissants noirs qui restent 10 f et plus | `AB/hypotheses.json`:463-483 ; `C/ETUDE_VISUELLE.md`:179-183 | **T** en Roblox : seuls des Trails (dragon). Les smears des anciens prototypes n'existent que dans le lecteur HTML |
| Smear en R6 = objet séparé | Clones ou « multiples » du bras, maillage de smear, Trail ou Beam | `C/recherche/roblox_2026-09-25.md`:118-120 ; `C/tutos/rapport_video_techniques_anime.md`:97-102 ; `C/tutos/rapport_anime3d.md`:199-203 | **T** |
| **Fond remplacé** | Lignes de vitesse, aplat de couleur ou flou à l'impact | `AB/hypotheses.json`:398-419 ; `C/ETUDE_VISUELLE.md`:139-144 | **P** : fond de vitesse du coup h4 en v6. C'est une approximation par ScreenGui : le décor n'est pas vraiment remplacé derrière les corps (hypotheses:414) |
| **Trace persistante et tenue sur la conséquence** | Cratère, tache, anneau qui se dissipe ; tenue d'environ 1 s | `AB/hypotheses.json`:629-648 | **V** indirect : le cratère de l'aérien est dans la partie aimée |
| **Signature visuelle** | Un motif propre à chaque technique (horloge, trou noir) | `AB/hypotheses.json`:688-706 ; `C/ETUDE_NOTES_BRUTES.md`:246 | **T** : le « dragon » doré n'a jamais été jugé par Milan. Je le juge moi-même encombrant en v9 (`PD/README.md`:655-657, 697) |
| Structure en actes | Jeu → signature → cinématique → conséquence tenue → retour | `AB/hypotheses.json`:669-687 ; `C/ETUDE_VISUELLE.md`:320-333 | **T** |
| Ellipse de l'impact | On ne montre pas le coup ; les cartes le racontent | `AB/hypotheses.json`:505-524 ; `C/ETUDE_NOTES_BRUTES.md`:184-185 | **T** |
| Rafale en masse | Une rafale très rapide se montre comme une masse de poings-smears | `AB/hypotheses.json`:609-628 | **T** |
| Ralenti sur la conséquence | 1 à 2 s de ralenti ou de plan fixe après le pic | `AB/hypotheses.json`:707-725 | **T** |
| Explosion après le choc | L'image explose juste après le choc au lieu de geler | `AB/hypotheses.json`:247-262 | **T** : essayée en v5, note inchangée (« pas de différence ») |
| Tenue avant le choc (IMPACT HAVEN) | On freine avant le contact ; le flash cache le saut de pose | `C/REFERENCES_VIDEO.md`:85-108 ; rétrogradée « effet de style » (`AB/hypotheses.json`:135-154) | **T** : jamais appliquée. La scène IMPACT HAVEN n'est pas commencée (`AB/PLAN.md`:168) |
| Impact visible avant les effets plein écran | Au moins 6 f entre l'impact et le premier effet plein écran | `AB/LECONS.md`:49-60 | **V** : « auto-critique v1 validée par Milan » |
| Caméra de jeu ou cinématique | Le tier 1 doit se lire depuis la caméra du joueur ; seul l'ultime passe en cinématique | `AB/hypotheses.json`:587-608 | **V** : « ça rend assez bien en caméra jeu ; en cinéma un peu trop abusé » (`AB/notes_milan.jsonl`:7) → dose de 70 % (`ST`:275-278) |
| Règle d'usage | Cartes, noir et blanc réservés aux 1-2 plus gros impacts ; ne jamais réutiliser une carte sur deux temps forts | `AB/CERVEAU_V2.md`:160-166 ; `AB/hypotheses.json`:285 | appris sur la v6 (le X revenait deux fois) |
| 3 temps anticipation/burst/dissipation, 6 couches (forme, mouvement, débris, lumière, caméra, son), contraste, l'échelle dit l'enjeu | Principes du skill Astrablox | `CK`:26-60 | appliqués seulement dans le lecteur HTML (solar_smite). Le **son n'a jamais été fait** |
| Kutsuna lighting / lavis de couleur | La lumière recolore toute la scène pendant la technique | `C/tutos/etude_complete_techniques_anime.md`:25-33 ; `experiments/r6_solar_smite/README.md`:89-92, 110-113 | **T** (HTML seulement, jamais en Luau) |
| Yutapon, « hold and release » | Les débris restent suspendus pendant la tenue, puis partent d'un coup | `C/tutos/etude_complete_techniques_anime.md`:50-71 | **T** : nos pics de cratère sortent sans tenue |
| Perso lisible au-dessus des effets | Priorité de rendu, tramage autour du perso (GG Strive) | `C/recherche/anime3d_2026-09-25.md`:426-432 | **T** |
| Secousse de caméra | Rotation seule, bruit de Perlin, intensité trauma² | `C/CARNET.md`:412-425 ; `C/recherche/anime3d_2026-09-25.md`:364-387 | **T** (piste A/B jamais faite) |

## 2. Chiffres mesurés

**Pack 100 Combat VFX** (`C/vfx_100_combat_vfx_pack.json` ; résumé dans `C/README.md`:174-221) :
- **Contenu** : 104 effets et 2 073 ParticleEmitter, plus 27 Beam, 11 Trail, 2 Highlight et 1 PointLight.
- **Par effet** :
  - émetteurs : médiane 14 [p10 5 – p90 44] ;
  - rôles : médiane 4 [1–6] ;
  - durée : médiane 1,2 s [0,5–3,0].
- **Déclenchement** : 98 % des émetteurs sont désactivés et joués par `:Emit()`.
  - `EmitCount` est présent sur 97 % (valeurs 1/2/5/3) ;
  - `EmitDelay` vaut presque toujours 0 ;
  - `TimeScale_*` : 0,1 s, soit l'équivalent d'un hitstop sur les particules.
- **Orientation** : 46 % VelocityPerpendicular, 27 % VelocityParallel, 26 % FacingCamera. 50 % des émetteurs ont un flipbook.
- **Par rôle** (médiane [p10–p90]) :

| rôle | n | durée de vie | taille max | vitesse | drag |
|---|---|---|---|---|---|
| flash | 217 | 0,10 s [0,05–0,125] | 11,3 [3,9–33] | — | — |
| onde | 744 | 0,4 [0,1–1,48] | 11,9 [5–32,6], 11 clés de courbe | — | — |
| étincelle | 370 | 0,37 [0,115–1,15] | 4,5 | 75 [22–299] | 5,1 |
| fumée | 411 | 1,0 [0,26–2,25] | 6,4 | 62,7 | 5,4 |
| débris | 70 | 1,28 [0,59–2,96] | 2,0 | 52 | 6 |

- **Combinaison la plus fréquente** : étincelle + flash + forme + fumée + onde (13 effets), plus des débris pour les coups lourds (11).
- **Verdict écrit** : nos impacts sont « 5 à 7 fois moins denses et 3 fois trop petits » (`C/README.md`:216-218).
- **Réserve** : le pack ne dit pas quel effet sert à un M1 ; pour un M1, viser le bas de la plage (`C/README.md`:212-214).

**The Creator** (`C/vfx_the_creator.json`) : une aura de personnage, pas un impact.
- 111 émetteurs continus (0 % désactivés), 10 par membre, 86 % FacingCamera ;
- durée de vie médiane 0,6 s, taille 0,5 ;
- 7 PointLight (portée 60).

**Références vidéo** :
- **Black Flash** : écarts 15/10/7/7/10 f ; 1 f de corps teinté ; cartes de 2 f (`C/REFERENCES_VIDEO.md`:15).
- **Stagnant Rage** : flash du corps 2 f (:17).
- **Serious Punch** : blanc 6 f, planches d'1 f (:18).
- **Moon Animator** : VFX à pleine taille dès la 1re frame, effacés en 3-6 f (:19).
- **IMPACT HAVEN** : 1 f de silhouette + 1 f de blanc par impact, 19 impacts en 8,2 s (:23, 75-102).
- **MHA** : impact frames ≈ 19 images (0,8 s), à 1 image chacune (`C/tutos/rapport_anime3d.md`:178-180).
- **Clip analyzer** (`C/clips/*.json`, champ `impacts.cartes`) : IMPACT HAVEN silhouettes de 67 ms ; Black Flash 17-67 ms ; coup chapeau noir 133-467 ms ; Serious Punch TSB **1 seule carte « silhouette » de 267 ms**.
- **Hitstop** (sources de seconde main, « extrait ») :
  - SFV 8/12/15 f ;
  - Smash, formule proportionnelle aux dégâts, plafond 30 f ;
  - Vlambeer 1-2 f (`C/recherche/anime3d_2026-09-25.md`:276-352).
- **Aucune durée TSB publiée** (`C/recherche/roblox_2026-09-25.md`:191).
- **Modules communautaires** :
  - RbxCameraShaker Bump = (2.5, 4, 0.1, 0.75) ;
  - CameraKit FOV +7° en 0,04 s, retour en 0,35 s ;
  - ImpactFrame 0,1 s (`C/tutos/rapport_roblox_web.md`:232-242 ; `C/recherche/roblox_2026-09-25.md`:59).

**Ce qui a été appliqué** (`DF`:224-307, `ST`, `PD/scripts/dragon_clip.py`:90-92) :
- flash de 0,09 s (2/60 s au tier 1) ;
- étincelles VelocityParallel à 45-95×s studs/s, drag 5 ;
- fumée de 0,7-1,2 s, drag 5,4 ;
- EmitCount/EmitDelay en attributs ;
- hitstop de la rafale 0,03 → 0,085 s ; gel des cartes 0,43 s (`ST`:222-226) ; frappe aérienne 0,13 s ; impact au sol 0,16 s.

**Jamais appliqué** :
- `TimeScale` sur les particules (aucune occurrence dans `DF`, alors que `AB/SCENE_POING_DU_DRAGON.md`:56-57 le promettait) ;
- flipbooks ;
- Beam ;
- la densité de 14 émetteurs par effet (nous : 3 émetteurs + 1-2 anneaux) ;
- l'onde en particules VelocityPerpendicular (nous : une Part Neon tweenée, `DF`:280-301) ;
- les tailles p90 pour le finisher : `ST`:191-192 dit « finisher au p90 », mais le flash fait 4,2×s avec s = 2,4, soit **environ 10 studs, la médiane et non le p90 (33)**.

## 3. Retours de Milan sur les effets (texte exact, avec la version)

- **Trou noir, avant le plan du cerveau** : « tout le travail jusqu'ici c'est assez bof, pareil pour le dernier trou noir » (`AB/PLAN.md`:4-5). Demande : « essaye de faire ça exactement mais que ce soit pour les VFX l'animation etc » (`experiments/r6_black_hole/README.md`:25-27).
- **directional_punch** :
  - demande : « texturing décorés… niveau expert » (:16-18) ;
  - « le perso est censé charge son poing » (:25-27, puis le halo :226) ;
  - « Ton rendu est nul comparé à des animateurs experts » (:261) ;
  - sur l'étirement : « toujours pas compris, inverse… » (:819-821).
- **hit_combo** : « Fais une nvl animation de combo de hit avec VFX texturing inspire toi des refs » (:14-17).
- **solar_smite** :
  - brief VFX écrit par Milan (noyaux, trails, flash, explosion solaire, « doit dépasser Poing scintillant ») (:34-38) ;
  - « tes animatkon sont tjes pas ouf » (:53-54) ;
  - « 3/10 par rapport au ref envoyé » (:76).
- **rock_kick**, brief VFX (:32-33) : « poussière au spawn, burst + trail… explosion + débris + onde + flash ».
- **throne_crown** :
  - « la couronne brille », « Améliore le texturing fais du premium » (:14-18) ;
  - « va chercher des outils… texturing niveau expert » (:110-111).
- **battle_throne** : « décors qui se casse » (:17-20).
- **divine_descent** : « Plus divin, comme s'il abattait sa colère » (:193) ; « il ne tombe pas du ciel il en descend… on montre son côté divin et boum » (:75-77), ce qui a déplacé l'aura et le rayon après la révélation (:236-250). Puis, pour passer à divine_orb : « Nul, on tente un autre » (`r6_divine_orb/README.md`:13).
- **Poing du Dragon** :
  - v1 : « pas mal sur tout le jeu aérien » (`AB/notes_milan.jsonl`:1) ;
  - v6 (7/10) : « ça rend assez bien en caméra jeu ; en cinéma peut-être un peu trop abusé mais léger » (:7) ;
  - « il manque une touche manga… » (`PD/README.md`:471 attribue cette phrase à la note v6, mais elle n'est pas dans `notes_milan.jsonl`:7) ;
  - v9 : « animation en pause, chantier VFX ensuite (proposition de Milan) » (`AB/RETOURS.md`:555-556).

Aucun `accept` de Milan sur un effet n'existe. Ses seuls retours positifs sur les VFX sont l'aérien (v1) et la caméra de jeu (v6).

## 4. Erreurs et leçons VFX des prototypes

- **Flash plein écran identique sur un jab et sur le finisher** → flash radial localisé (`r6_solar_smite/README.md`:65-71 ; `CK`:96).
- **Starburst dimensionné en studs** : il remplissait le cadre quand la caméra était proche → plafond en pixels (`solar_smite`:115-124).
- **Noyau additif jamais éteint** : il noyait l'éclat (`solar_smite`:413-419).
- **Trou noir** :
  - ambiance cosmique dès la frame 0, contraire à la référence (`r6_black_hole/README.md`:377-408) ;
  - VFX qui débordait d'1 frame après l'atterrissage (:156-162) ;
  - disque noir plein qui remplissait le cadre (:209-225) ;
  - bug d'aliasing sur `THREE.Color` (:410-419).
- **battle_throne** : une capture prise pendant les 50 ms du flash a été lue à tort comme un bug de caméra (:234-243).
- **Couronne** : halo invisible à l'échelle du lecteur (:680-683). Aucune texture Roblox possible sans upload (:130-135).
- **directional_punch** :
  - étirement du bras sur le mauvais demi-temps (:818-842) ;
  - hitstop et étirement non exportables dans une KeyframeSequence (:622-630).
- **hit_combo** : l'effet disait « matière » (gravats) et pas « énergie » → éclats + anneau (:211-223).
- **Dragon** :
  - le plus gros impact était coupé dans la frame même du contact (`AB/LECONS.md`:49-60) ;
  - flash doré confondu avec le jaune du noob (`PD/README.md`:109-110) ;
  - carte X répétée, la signature du final s'effaçait (:451-454) ;
  - une image passait sous le fondu blanc (:455-457) ;
  - effets 3 studs trop haut (:91) ;
  - poing vers la caméra bouché par la victime, gros plan R6 comique (:444-448) ;
  - le flash du corps cachait la silhouette au contact (`AB/RETOURS.md`:180) ;
  - contact v7 jamais vu, recouvert par les cartes (`AB/RETOURS.md`:309-321) ;
  - anneaux dorés qui encombrent le poing (`PD/README.md`:655-657).
- **Moteur** : `EasingStyle = 1` voulait dire Constant, et le lecteur HTML ne pouvait pas le montrer (`AB/ANGLES_MORTS.md`:84-95). La leçon vaut aussi pour tout VFX jugé dans le HTML.
- **Lecteur binaire .rbxm** lu en big-endian → corrigé (`C/README.md`:166-172 ; `solar_smite`:126-137).
- **aerial_kick_combo : aucun VFX** (:508-511).

## 5. Notre pipeline VFX actuel

- **Format** : `ST` produit une chronologie `events` (frame, type, paramètres) et des clés de caméra, écrites dans `staging.json`. C'est la **seule source** pour le lecteur HTML et pour `DragonFistData.luau` (`ST`:1-5, 190-284 ; `DF`:7-11).
  - Types d'événements : `impact` (tier, échelle, hitstop, secousse), `body_flash`, `ground_burst`, `vitesse`, `aura`, `fist_glow`, `dust_trail`, `cartes`, `dome`, `whip`, `dragon`, `manga`, `white`, `crater`, `smoke_cloud`, `embers`.
- **Lecteur HTML** : Three.js, textures procédurales `CanvasTexture`, blending additif (`PD/scripts/player_template.html`:162-283, 300-624). C'est une approximation (`PD/README.md`:132-135). Les prototypes antérieurs faisaient du canvas 2D HTML seulement (`AB/PLAN.md`:52-55).
- **Luau** :
  - l'ordonnanceur lit `TimePosition` ;
  - émetteurs `Enabled = false` et `Rate = 0`, avec `EmitCount`/`EmitDelay` (`DF`:184-213) ;
  - 3 textures intégrées `rbxasset://` (`DF`:53-57) ;
  - anneaux en Part Neon, Highlight pour le flash du corps, 3 Trails animés pour le dragon (`DF`:424-473) ;
  - cratère en Parts avec graine ; ScreenGui/ImageLabel pour les cartes et les planches, **avec des IDs vides** qui se replient en noir/blanc (`DF`:35-50) ;
  - secousse en `math.random` (`DF`:877-878).
- **Cartes et planches** : générées depuis notre pose (`PD/scripts/build_cartes.py`, `build_manga.py`).
- **M1** : marqueurs `trail_on`/`hit`/`trail_off` (`experiments/r6_m1_v222/README.md`:142-155).
- **Ce qui manque** : textures maison, flipbooks, Beam, mesh VFX, TimeScale, son, ColorCorrection, test dans Studio (`PD/README.md`:126-131), réplication et pooling.

## 6. Rank Zero : ce qui est transposable et ce qui ne l'est pas

**Transposable** :
- **Les 8 couches** (`v3`:76-91), avec la règle couches protégées / dégradables et l'ordre de dégradation (`A`:11-40).
- **La recette JSON** = forme + matière + temps + palette + feedback (`v3`:218-245). `importance_tier` 1 à 6 correspond à nos tiers 1 à 3.
- **Le catalogue de 15 primitives** (`v3`:169-187 ; 16 existent en GDScript dans `src/vfx/primitives/`, 18 recettes dans `data/recipes/`) et **les 9 matières** (`v3`:204-216).
- **Le feedback** :
  - séquence d'impact (`v3`:300-307) ;
  - recul obligatoire (`v3`:89) ;
  - secousse dirigée à l'opposé de l'attaque, jamais un bruit isotrope (`v3`:298).
- **La règle « image distincte »** : une nouvelle famille change au moins 3 dimensions (`v3`:50).
- **Contrôle hitbox/visuel** à 8 % d'écart (`v3`:51).
- **Déterminisme de la graine** (`A`:75-81) : notre `math.random` le viole.
- **Cycle de vie** et nettoyage par trois voies (`A`:58-73), et **marqueurs d'animation** (`A`:42-56).
- **Budget d'overdraw** (`v3`:259), **VFX Lab** (`v3`:507-514), **captures standardisées** et **verdict humain versionné** (`v3`:474-493).

**Propre à Rank Zero** :
- Godot / GDScript, pixel art 640×360, Nearest, PixelLab / Pixel Composer, atlas ETC2/ASTC, LFS (`v3`:15-26, 93-124, 341-437).
- Les bandes de valeur en HSV (`v3`:59-74) : partiellement transposables.
- Des hit-stops courts de 12 à 95 ms (`v3`:280-286), qui viennent d'un autre registre que nos ultimes manga (0,43 s de gel).

## 7. Trous

- **Aucune fiche de conception VFX ou impact** : seule `C/fiches/COUP_CHARGE.md` existe, alors que `CLAUDE.md` exige une fiche par moment.
- **Aucune mesure des VFX de TSB** ; les textures du pack n'ont jamais été vues (proxy, `C/README.md`:219-221).
- **Les rôles de `vfx_corpus.py` n'ont jamais été validés** sur une vérité connue (règle de `AB/ANGLES_MORTS.md`:125-144).
- **La perception ne voit pas les VFX** (`AB/ANGLES_MORTS.md`:156-157). `clip_analyzer` ne distingue que blanc / noir / silhouette (`AB/clip_analyzer.py`:102) : pas l'encre ni la postérisation.
- **Jamais faits** : flipbooks, Beam, mesh VFX, défilement de texture, masques émissifs, TimeScale, son, ColorCorrection/Highlight en impact frame (bug de saturation noté dans `roblox_2026`:195), perf et réplication, VFX de victime (sang, tache au sol), secousse de Perlin, multiples, hold-and-release.
- **Jamais vus** : les vidéos Sakurai « Hit Marks », ASW effets, ByteBlox et Maplestorm (`C/recherche/anime3d_2026-09-25.md`:467, 480-481 ; `C/recherche/roblox_2026-09-25.md`:134-137).
- **Question ouverte** : le tier 1 est illisible en caméra de jeu (`PD/FICHE_V6.md`:80-83).

## Contradictions entre fichiers

1. **Serious Punch** : « 3 planches d'1 f, blanc 6 f » (`C/REFERENCES_VIDEO.md`:18) ; « 3 cartes de 4 f, blanc ~0,25 s » (`C/ETUDE_NOTES_BRUTES.md`:55 ; `C/CATALOGUE_REFS.md`:23) ; « 1 carte + 0,2-0,4 s » (`C/fiches/COUP_CHARGE.md`:61) ; l'analyseur mesure 1 carte de 267 ms. Notre implémentation (3×2 f à 60 i/s) suit la version « 1 f ».
2. **Auteur de la même vidéo** : Arikendo (`etude_complete_techniques_anime.md`:1) ou SinChi (`rapport_video_techniques_anime.md`:1).
3. **Artiste VFX du coup chapeau** : « Matchless » (`ETUDE_NOTES_BRUTES.md`:3), « @MuichimeRBXL » (`REFERENCES_VIDEO.md`:49) ou « Mouchine » (`CATALOGUE_REFS.md`:45).
4. **Comptes de clips** : ~24 (`ETUDE_VISUELLE.md`:51) contre ~22 (`hypotheses.json`) ; 88 planches (:20) contre 68 (:29).
5. **Confiance de `tenue_avant_choc`** : 0,4 (`CERVEAU_V2.md`:131-134) contre 0,25 (`hypotheses.json`:140).
6. **« Finisher au p90 »** (`ST`:191-192) : les tailles réelles sont à la médiane.
7. **TimeScale** promis (`SCENE_POING_DU_DRAGON.md`:56-57), absent du code.
8. **Étirement du bras** ×1,32 et ×1,55 dans le lecteur (`directional_punch`:612, 836), alors qu'un bloc R6 ne se met pas à l'échelle : « IMPOSSIBLE » (`rapport_video_techniques_anime.md`:98), « décision de Milan » (`C/CARNET.md`:339-342).
9. **« Notre jeu tourne sous Godot »** (`roblox_2026-09-25.md`:5-6) : confusion entre Rank Zero et la cible Roblox.
10. **Secousse** : aléatoire et en translation dans `DF`, contre la règle directionnelle et à graine de `v3`/`A` et la recommandation d'Eiserloh.
11. **Impact frames TSB** : « séquences 2D dessinées » (`roblox_2026-09-25.md`:52-57, 178) contre ColorCorrection + Highlight (`rapport_video_critique_poses.md`:79) ou ViewportFrame (`rapport_roblox_web.md`:245-248). Notre module utilise des ImageLabel.
12. **Hitstops sans échelle commune** : 12-95 ms (`v3`), 0,03-0,43 s (Dragon), 2-8 f à 30 i/s (`hit_combo`:125), 0,07 s (M1).
