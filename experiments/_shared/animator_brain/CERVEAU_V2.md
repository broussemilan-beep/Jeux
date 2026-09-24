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
