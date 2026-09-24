# Cerveau v2 : juger, réfléchir, se corriger

Demande de Milan (2026-09-24), après la v4 du Poing du Dragon :

> « Stop régler petit à petit et rajouter du jugement au cerveau, c'est le but
> de le nourrir. […] que le cerveau soit évolutif comme un algo, pas une simple
> base de données, pour qu'il y ait jugement, réflexion, correction. »

## Pourquoi changer

Quatre versions de suite ont corrigé la mesure pointée par le retour précédent :
- v2 : posture et escalade ;
- v3 : épaules et transfert de poids ;
- v3b : angle du bras ;
- v4 : trajectoire du poing.

Chaque fois, les règles passaient au vert (13/13 en v4). Les notes de Milan,
elles, n'ont presque pas bougé : 6, puis 6,7, puis 6,7.

Le cerveau v1 est une base de mesures avec des seuils. Il ne sait pas juger,
il ne se trompe jamais à ses propres yeux, et il ne relie jamais ses mesures
aux notes.

## La boucle

```
percevoir -> hypothèses -> juger (prédire la note) -> montrer à Milan
    ^                                                         |
    +-------- réfléchir (écart prédiction / note) <-----------+
```

| étape | fichier | ce qu'il fait |
|---|---|---|
| **Percevoir** | `clip_analyzer.py`, `corpus.py`, `rules.py` | mesure n'importe quel clip, référence ou production, en 1-3 s : cadence (en 1, en 2…), tenues, énergie, cartes d'impact, profil autour du choc, coupes, secousses, palette ; plus les mesures 3D de nos animations |
| **Hypothèses** | `hypotheses.json` | des principes, pas des règles, chacun avec sa **confiance_principe** (vrai en animation), son **poids_note** (fait bouger la note de Milan, appris), ses sources et sa portée (coup léger, coup droit, finisher, rafale…) ; les paroles de Milan entrent comme des pistes, avec leur source |
| **Juger** | `critic.py predict` | note prédite + critique écrite (défauts les plus lourds d'abord) ; ce qui n'est pas mesurable est jugé à l'œil sur les planches, et l'état l'indique |
| **Réfléchir** | `critic.py reflect` → `REFLEXION.md` | compare les versions notées : ce qui a changé, ce que la note a fait ; une hypothèse corrigée sans effet sur la note perd du poids ; une hypothèse toujours fausse pendant que la note stagne devient un **suspect** ; l'échelle de note est recalibrée |
| **Mémoire** | `notes_milan.jsonl` | chaque version : note, mots de Milan, état de chaque hypothèse et d'où vient cet état (mesure ou jugement) |

## Premier passage (2026-09-24)

Il a tourné sur les 3 notes existantes (v1 : 6 ; v2 : 6,7 ; v4 : 6,7).

- **v1 → v2 (+0,7)** : posture, escalade, impact visible et variété corrigés.
  Effet modéré.
- **v2 → v4 (±0)** : épaules, bras horizontal, transfert et trajectoire
  corrigés, sans aucun effet sur la note. Justes, mais ce n'est pas ça qui
  retient la note.
- **Suspects**, toujours faux pendant que la note stagne :
  1. `tenue_avant_choc` : les références pro freinent **avant** le choc puis
     explosent après ; nous, on gèle après (mesuré par `clip_analyzer`) ;
  2. `coup_charge` : le coup final ne se charge pas (piste Saitama de Milan) ;
  3. `arcs` : nos membres vont en ligne droite, parce que le contrôle IK est
     interpolé en ligne droite.
- **Plafond** : même avec toutes les hypothèses vraies, l'échelle calibrée
  plafonne à ~7,2. **Il manque des principes** au cerveau. C'est ce que les
  références d'anime, de manga et d'animation doivent apporter.

**Honnêtement** : 3 notes pour 2 paramètres d'échelle, c'est un raisonnement
guidé, pas une statistique. Le levier qui changera ça, ce sont les
**comparaisons de variantes** : Milan choisit entre A, B et C en quelques
secondes, ce qui apporte bien plus d'information que des notes isolées.

## Perception branchée au jugement (2026-09-24, suite)

Défaut du premier passage : l'état de chaque hypothèse était **rempli à la
main**. Le critique jugeait donc mes impressions, pas l'animation.

- `perception.py` mesure en 3D, sur l'export de chaque version (relu depuis
  git) et sur le pack pro :
  - les **arcs** : déviation de chaque trait par rapport à sa corde ;
  - la **fluidité** : traits par seconde de mouvement, un trait étant un
    mouvement entre deux arrêts ;
  - l'**espacement** et le **frein** avant le contact ;
  - la **charge** du coup final : tenue, départ, enroulement du buste ;
  - la **variété** : distance entre les formes des coups.
- `etats.py` calcule l'état de chaque hypothèse, avec sa preuve et son
  étalon, dans `etats_auto.json`. Ses sources sont les règles, la fiche
  vidéo de la version, la perception 3D, `corpus/perception_pro.json` pour
  le pack pro et les fiches des références de Milan. La mesure prime sur le
  jugement manuel, et les désaccords sont affichés.
- `critic.py reflect` a deux nouveautés.
  - Il **apprend de ce que Milan aime**. Les notes portent maintenant un
    verdict par partie (`parties`) : aérien +, rafale −, final −. Une
    hypothèse vraie dans l'aimé et fausse dans le rejeté gagne du poids ;
    une hypothèse qui a le même état dans les deux en perd.
  - Il est **idempotent** : il rejoue l'historique depuis `poids_a_priori`.
    Avant, chaque lancement ré-appliquait les mises à jour.
- **Alertes de style** : chaque hypothèse porte un `etalon_style`
  (`tsb_m1`, `manga_ultime` ou `universel`), et chaque partie d'une
  production porte un `style_cible` (`productions.json`).

### Ce que la mesure a corrigé

- **Arcs.** Je les jugeais faux en v4 ; la mesure les donne vrais. Les clés
  d'arc de la v3 ont suffi : déviation de 0,20 à 0,21, contre 0,14 à 0,41
  pour les M1 pro. Ce n'est donc plus un suspect. L'aérien, que Milan aime,
  a d'ailleurs des traits *plus droits* (0,10).
- **Fluidité : le vrai suspect, et il était invisible.** On mesure les
  traits par seconde de mouvement (preuve :
  `captures/verification/2026-09-24-cerveau-fluidite-arrets-pro-vs-nous.png`) :

  | quoi | traits par seconde |
  |---|---|
  | M1 pro | 4,2 à 5,7 |
  | Uppercut pro | 2,9 |
  | notre aérien (aimé) | 3,5 à 4,2 |
  | notre rafale et notre final (rejetés) | 7,5 à 11,9 |
  | une *réaction à un coup* pro | 9,2 |

  Nos coups s'arrêtent à chaque pose clé, parce que le contrôle IK ralentit
  à chaque clé. C'est la seule hypothèse qui sépare l'aimé du rejeté.
  Réserve honnête : notre rafale enchaîne 4 coups en 1,3 s, un M1 pro est un
  seul coup en 0,65 s ; une partie de l'écart vient du tempo. Contre-épreuve
  à faire : les rafales des références vidéo, par flux optique.
- **Correction de la correction (même jour, v5).** La mesure de fluidité,
  en traits par seconde, est **faussée par le tempo**. Notre rafale donne un
  coup toutes les 0,43 s, un M1 pro un coup en 0,65 s. En 3D, notre rafale
  n'est **jamais figée** (0 % de temps immobile, contre 28 à 51 % pour les M1
  pro). Les 37 % de temps figé de la vidéo viennent de la structure : gels
  d'impact, temps suspendu, longue révélation.

  Les poignées AUTO, essayées sur cette base, haussaient l'épaule (0,33
  stud). La mesure est donc **retirée du jugement** (`ANGLES_MORTS.md` §7).
  Le principe reste, à mesurer autrement : arrêts par coup, à tempo égal.
  Leçon : même une mesure qui sépare l'aimé du rejeté peut mesurer autre
  chose que ce qu'on croit.
- **Variété.** Je la jugeais bonne en v2 et en v4. Mesurée, elle est de 1,94
  stud en v4 (0,7 en v1), contre 2,73 entre les 4 M1 pro : nos coups se
  ressemblent encore plus que des M1 entre eux.
- **Tenue avant le choc.** Seules 3 références sur 9 avec cartes d'impact la
  montrent, alors que Black Flash, Rewind Clock et Serious Punch TSB non. Sa
  confiance est baissée à 0,4 : elle dépend du style, ce n'est pas un
  principe universel.
- **Alerte de style sur le coup final.** Les règles `bras_horizontal`,
  `poing_a_plat` et `transfert_poids`, étalonnées sur des M1 réalistes,
  jugeaient un final qui vise le style manga ultime. C'est l'écart que Milan
  pointait avec la piste Saitama.

Critique de la v4 après recalcul, défauts les plus lourds d'abord :
**fluidité**, variété, coup chargé, tenue avant le choc.

## Flux optique (`clip_analyzer`, bloc `mouvement`)

Le flux Farneback est calculé entre images distinctes d'un même plan, le
mouvement de caméra étant retiré par le flux médian. Il donne trois choses :
- les arrêts par seconde ;
- la direction des pics de vitesse ;
- la déviation de la trajectoire du point le plus rapide.

Validation sur vérité connue (`ANGLES_MORTS.md` §7) :
- la **direction** est validée (part des pics qui montent : v1 0,46, v3b
  0,39, v2 et v4 0,15) ;
- les **arrêts en 2D** ne le sont pas, ils contredisent la 3D. Ils ne sont
  pas utilisés pour juger.

Voir aussi **`ANGLES_MORTS.md`** : la prise de recul du 2026-09-24. Le point 1
porte sur le « coup final » : l'uppercut de f150 n'avait jamais été regardé.

## Regle d'usage (retour de Milan, 2026-09-24)

« Ce que tu decouvres doit etre bien utilise et en apprendre, pas l'appliquer n'importe comment : ca nourrit le cerveau, le jugement et la critique. »

- Chaque principe de mise en scene porte `quand` (le bon moment) et `contre_indication` (ce qui le tue) dans `hypotheses.json`.
- Les refs le montrent : les cartes, le noir et le blanc sont reserves aux 1-2 plus gros impacts ; les coups legers d'une rafale n'en ont pas. L'effet vaut par le CONTRASTE avec ce qui l'entoure.
- Le critique doit juger l'usage au bon endroit (hierarchie des temps forts, escalade), pas la presence : un principe mal place compte comme un defaut.

## Le champ des références (Milan)

- Roblox : TSB, JJS, Heroes Battlegrounds, animateurs indépendants.
- Anime : sakuga, One Punch Man, JJK, Dragon Ball, Hajime no Ippo, Mob Psycho.
- Manga et webtoon : cases, lignes d'action, raccourcis.
- Animation occidentale et indépendante : Arcane, Avatar, Alan Becker.
- Jeux de combat : données image par image (startup, active, recovery).
- Bases du métier : Richard Williams, Muybridge, mocap de boxe réelle.

Ce sont les références de nos références : les animateurs Roblox copient
l'anime.

## Outils repérés (recherche web du 2026-09-24)

- **Collecte** : `gallery-dl` (Sakugabooru, Danbooru, Reddit, Webtoons,
  MangaDex et 200 autres), `yt-dlp` ; SakugaGrabber et sakuga_scrape pour
  l'API de Sakugabooru par étiquettes.
- **Analyse** :
  - PySceneDetect (coupes) ;
  - l'idée de MultiPassDedup (animation en 2 ou en 3) ;
  - open_clip (classer un clip « coup de poing » ou « coup de pied » sans
    entraînement).
- **Poses** :
  - bizarre-pose-estimator (personnages dessinés) ;
  - rtmlib, RTMPose sans GPU (vidéo réelle, peut-être rendus 3D).
- **Données** : Awesome-Animation-Research, Sakuga-42M (images d'anime
  décrites).
- **Roblox** : anim2rbx (FBX → KeyframeSequence), qui avec de la mocap de boxe
  donnerait de vrais mouvements comme base.

Installés dans le sandbox : `gallery-dl`, `yt-dlp`, `scenedetect`,
`opencv-python-headless<4.10`, avec numpy < 2 (**bpy exige numpy < 2** ; une
installation qui monte numpy casse Blender).

## Réseau

La politique réseau de l'environnement refuse les sources : Sakugabooru,
Reddit, YouTube, Wikipedia, Giphy, Danbooru, et GitHub hors du proxy git.
Tant que les domaines ne sont pas ajoutés aux domaines autorisés de
l'environnement, le scrapeur ne peut que travailler sur les clips envoyés par
Milan.

## Prochaines étapes

0. Scrapeur écrit et testé hors ligne (`scraper/`, 11/11 avec un faux
   Sakugabooru local). `python3 scraper/scraper.py acces` dit quels domaines
   passent.
1. Réseau ouvert → scrapeur : Sakugabooru par étiquettes et score, puis les
   autres sources. Chaque clip passe dans `clip_analyzer` ; on ne garde que la
   fiche et la planche, jamais la vidéo.
2. Bibliothèque de coups (une fiche par type : intention, phases, poses clés,
   ce qui fait rater), nourrie par les références. Chaque principe entre dans
   `hypotheses.json`.
3. Rendre mesurables les suspects : profil autour du choc sur nos productions
   (fait), courbure des trajectoires (arcs), charge (durée et immobilité de la
   tenue avant le coup final).
4. Coup final à la Saitama : 3 variantes jugées par le critique ; Milan
   choisit ; la réflexion apprend du choix.
