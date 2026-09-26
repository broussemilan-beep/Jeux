# `animator_brain` — le cerveau d'animateur R6 / Roblox

> Ce README documente le CODE du cerveau (mesures de mouvement, rig).
> Pour la carte complète, l'état et l'ordre de lecture : `ETAT.md`.

Né d'un retour direct de Milan (2026-09-23) : *« pourquoi tout a l'air
mécanique dans tes rendus ? »*, suivi de *« sois vraiment minutieux, le
projet derrière c'est un cerveau d'animateur Roblox »*.

La réponse honnête : jusque-là, **chaque vérification portait sur des images
fixes** (captures, poses). Or ce qui rend une animation mécanique se trouve
presque toujours **entre** les poses, dans le mouvement. Et sur les poses
elles-mêmes, plusieurs conventions d'axes n'avaient jamais été vérifiées.
Ce module transforme les principes d'animation en **outils de construction**
et en **mesures chiffrées**. Pour chaque principe : un outil qui le construit,
et une métrique qui vérifie qu'il est respecté.

Dépendances : `numpy` (+ `PIL` pour les graphes). Aucune dépendance à `bpy` ni
à un prototype : la géométrie du rig est toujours passée en argument (`Rig`).
Les mêmes outils peuvent donc servir sur n'importe quel rig R6, y compris pour
auditer une animation Roblox importée.

```python
import sys; sys.path.insert(0, "experiments/_shared")
from animator_brain import audit, constraints, organic, poses, tracks, plots
from animator_brain.rig_math import Rig
rig = Rig.from_module(r6_rig)          # r6_rig.py du prototype (PART_ORDER, PARENT, PART_SIZES, JOINTS)
```

---

## 1. Principes → outils → mesures

| Principe | Symptôme « mécanique » | Outil qui le construit | Mesure (`audit.py`) | Cible |
|---|---|---|---|---|
| **Chevauchement** (*successive breaking of joints*) | tout le corps part, culmine et s'arrête à la même frame | `tracks.offset_tracks` : décalage des clés **par membre et par phase**, dans le sens de la chaîne de pilotage du geste | retard médian du pic de vitesse enfant/parent ; fraction de pics synchrones | tête +1…4 f, membres +1…6 f ; ≤ 35 % synchrones |
| **Pas de pose-à-pose robot** | arrêts simultanés sur les clés | pistes par membre (jamais une clé « corps entier ») | `stop_clusters` : arrêts coïncidant avec ≥ 3 autres membres | ≤ 30 % |
| **Asymétrie** (*no twinning*) | gauche = miroir exact de droite | poses asymétriques écrites et relues avec `poses.describe_pose` | écart au miroir (mains/pieds dans le repère du corps), corrélation des vitesses G/D | ≤ 50 % du temps en miroir ; corrélation ≤ 0.9 |
| **Colonne en 3D** | torse/tête ne tournent que sur un axe | torsion et inclinaison latérale **en l'air** (au sol, voir §3) | `planarity` : part de l'énergie de rotation sur l'axe principal | ≤ 0.85 |
| ***Moving holds*, boucles organiques** | sinus pur, période fixe, hold figé | `organic.organic_keys` : 3 sinus à rapports irrationnels, graine par membre, clés aux extrema | pureté de fréquence (si ≥ 3 cycles), CV des intervalles ; `frozen_fraction` | pureté ≤ 0.8 ; holds morts ≤ 5 % |
| **Contacts** | pieds qui glissent ou s'enfoncent | `constraints.plant_pose_at_height` (poses clés) + `foot_lock_pass` (chaque échantillon) | glissement d'un pied **planté** (au sol et sans vitesse verticale) | ≤ 0.1 stud |
| **Équilibre / poids** | pose qui « tombe » | `constraints.balance_margin`, refus des poses hors équilibre | fraction du temps au sol où le centre de masse sort de la base d'appui | ≤ 10 % |
| **Continuité** | à-coups, cassures de vitesse | vitesse héritée des ressorts, relâchement de jambe, transfert de poids progressif | `pops` : pic d'accélération ≤ 34 ms de large, hors **snaps déclarés** | 0 |
| **Regard** (les yeux mènent) | tête posée sur un manche | `constraints.look_at_pass` (cône borné, hystérésis) | (voir `pops` sur la tête) | — |

Les seuils sont des **heuristiques** issues des principes. Ils n'ont pas
encore été calibrés sur un corpus d'animations professionnelles (voir §6).

**Règle anti-triche** : un seuil ou une règle de validité d'une métrique ne se
change qu'avec une justification écrite dans le code, et en ré-auditant
**l'avant ET l'après avec le même code**. C'est ce qui a été fait pour
r6_black_hole (§5).

---

## 2. Conventions d'axes R6 — VÉRIFIÉES, pas supposées

Repère du personnage : **AVANT = −Z, DROITE = +X, HAUT = +Y**. Preuve : la
decal `face` du rig réel (`RigR6.rbxmx`) est sur `Face=5` = `NormalId.Front`
= −Z. Et `CFrame.Angles(+x)` **relève** le lookVector.

| Part | X+ | Y+ | Z+ |
|---|---|---|---|
| Torso | penche **en ARRIÈRE** (X− = vers l'avant) | épaule droite vers l'avant | s'incline vers **sa** gauche |
| Head | lève le regard (X− = baisse la tête) | regarde vers sa gauche | incline vers sa gauche |
| Right Arm | vers l'avant puis le haut (90 = horizontal devant, 180 = au-dessus) | — | **s'écarte** (Z− = croise devant) |
| Left Arm | idem | — | **croise** (Z− = s'écarte) |
| Right / Left Leg | le pied part vers l'avant | — | R : Z+ écarte ; L : Z− écarte |

Miroir gauche↔droite d'une rotation locale : `(x, y, z) → (x, −y, −z)`.

`poses.conventions_selftest(rig)` **prouve** chaque ligne par cinématique
directe et lève une erreur si une convention est fausse pour le rig donné.

**Pourquoi c'est vital.** Sur r6_black_hole, toutes les poses clés avaient
été écrites avec la convention inverse, jamais vérifiée. Le « crouch torse
plié vers l'avant » (`Torso X=+70`) penchait le personnage **70° en
arrière**. Les « bras écartés à l'horizontale » croisaient les mains devant la
poitrine. Climax, release et atterrissage penchaient en arrière. Les captures
ne l'avaient pas montré (angle de caméra, rig sans visage).
**Règle du cerveau : toute pose clé passe par `describe_pose()` et son
intention est vérifiée EN MOTS avant d'être animée.**

```text
CROUCH (avant) : torse penché en ARRIÈRE 70 deg | regard vers le HAUT 70 deg | ...
RISE   (avant) : torse penché vers l'AVANT 22 deg | main droite : ... CROISÉE de l'autre côté du corps
```

---

## 3. Leçons propres au R6 (géométrie des jambes rigides)

Toutes ont été **mesurées** en construisant r6_black_hole ; aucune n'est
supposée.

1. **Le torse EST le bassin.** Il n'y a pas d'articulation de colonne, et les
   hanches sont attachées au torse (`C0 = (±1, −1, 0)`). Tordre le torse
   (Y) avec les pieds plantés fait partir le bassin en diagonale : 1,36 stud
   de dérive latérale mesurée à −8°. → **Au sol, torsion du torse ≤ ~3°.**
   L'asymétrie passe par les bras, la tête et l'inclinaison latérale (Z).
2. **La hauteur de bassin atteignable dépend du torse et de l'écart des
   pieds.** On ne choisit donc jamais une hauteur absolue, mais une
   **profondeur sous le maximum** (`pelvis_height_range`, voir `_grounded`
   dans `r6_black_hole/scripts/choreography.py`).
3. **Accroupissement équilibré** : pieds côte à côte (écart ~1,5 stud),
   torse plié de 60 à 75° vers l'avant, bassin qui recule. Le centre de masse
   reste alors au-dessus des pieds (recherche en grille, §5).
4. **Une jambe R6 ne peut pas « pousser » jusqu'à l'extension.** Pivotant
   sur un pied planté, la hanche décrit un arc dont la vitesse verticale tombe
   à zéro près de la verticale. Garder les pieds au sol jusqu'à l'extension
   imposait 0,55 stud de balayage horizontal du bassin **en une frame**.
   → **Le personnage jaillit du crouch, et les jambes se déplient en l'air.**
   C'est aussi ce que montrent les animations R6 de référence.
5. **Au sol, le torse fait partie du système porteur** (bassin + torse +
   jambes, résolus ensemble par l'IK). Un torse qui traîne (ressort, clé
   décalée) force l'IK à déplacer le bassin : aller-retour de 0,8 stud mesuré
   au redressement. → **Ressort du torse en l'air seulement** (`t_max` +
   retour progressif vers la courbe clé). Au sol, le suivi du torse est **clé**.
6. **Près de l'extension, l'IK amplifie toute décélération du bassin**
   (singularité). → Pas d'arrêt net juste sous l'extension : le redressement
   se termine pendant la respiration.
7. **Atterrissage : un pied, puis l'autre.** Seuls les pieds **porteurs**
   (poids plein) placent le bassin. Un pied qui arrive ne fait que ramener sa
   jambe, et la solution du bassin passe de « appui simple » à « double
   appui » au rythme de son poids (15,6 studs/s de saut mesuré sans cette
   règle). Un pied qui arrive ne passe jamais sous le sol. [CONTREDIT 2026-09-26 : les pros laissent les pieds passer sous le sol à l'impact ; le contrôle de sol reste un contrôle technique, sa tolérance est à revoir, voir corpus/etude_c4/A2_tsb_stoic_collateral.md (« Oublis importants », point 2)]
8. **Pas de cheville** : quand une jambe est inclinée, c'est le **centre**
   de la semelle qui reste planté, et l'**arête** s'enfonce de
   ½·largeur·sin(inclinaison). C'est une limite connue du R6 (visible sur les
   profils).
9. **Export Roblox** : l'Animator n'anime pas le `HumanoidRootPart` (aucun
   Motor6D ne l'a pour Part1). Le mouvement d'ensemble est donc replié sur le
   RootJoint (pose du Torso), et la translation écrite est l'**écart au
   repos** (3,000 studs, mesuré par FK). Sinon le personnage flotte en jeu.
   L'aller-retour par l'équation du moteur (`resolve_rbxmx`, C0/C1 réels)
   doit retrouver l'aperçu à < 0,01 stud.

---

## 4. Recette pour une nouvelle animation

1. **Lire la référence frame par frame** (planches `ffmpeg` → PIL). Lister
   les *beats* : quelle pose, quel membre mène, quel contact.
2. **Écrire les poses clés**, puis `describe_pose()` sur chacune. Les mots
   doivent correspondre à l'intention.
3. **Poses au sol** : `plant_pose_at_height` avec une profondeur sous le
   maximum, pieds plantés et **équilibre vérifié** (erreur sinon).
4. **Pistes** : clés par membre ; cycles organiques (`organic_keys`) pour
   chaque *hold* ; jamais de sinus à période fixe.
5. **Chevauchement** : pour chaque phase, qui mène ? (bassin au sol, bras
   pour une ouverture, pieds à l'atterrissage…) → `OVERLAP_RULES`, en frames.
6. **Ressorts** différenciés par membre. Torse et jambes **en l'air**
   seulement.
7. **Contraintes** sur les échantillons : `foot_lock_pass` (appuis, fondus
   d'entrée et de sortie, relâchement de jambe), puis `look_at_pass`.
8. **Déclarer les snaps voulus** (impacts de 1 à 2 frames) *avant* d'auditer.
9. **Auditer** (`audit.audit` + `plots.peak_chain_chart` + `plots.onion_skin`).
   On corrige la cause de chaque ligne rouge, jamais le seuil.
10. **Exporter** en KeyframeSequence et vérifier l'aller-retour moteur.

Exemple complet : `experiments/r6_black_hole/scripts/`
(`choreography.py`, `pipeline.py`, `audit_motion.py`, `export_roblox.py`).

---

## 5. Résultat sur r6_black_hole (même code d'audit avant/après)

| | avant | après |
|---|---|---|
| critères OK | **4 / 25** | **23 / 23** |
| retard médian tête / bras D / bras G (frames) | −0,5 / 0,5 / 0,5 | 2,5 / 3,5 / 2,5 |
| temps en miroir exact (bras) | 84 % | 0,6 % |
| corrélation des vitesses G/D (bras / jambes en l'air) | 0,993 / 1,0 | 0,75 / 0,76 |
| planarité du torse / de la tête | 0,998 / 1,0 | 0,83 / 0,76 |
| glissement des pieds plantés | 0,75 stud (et 2,96 studs de déplacement des pieds pendant le crouch) | 0,002 |
| temps hors équilibre au sol | 27,7 % | 0 % |
| discontinuités hors snaps déclarés | 0 | 0 |
| aller-retour moteur Roblox | — | 0,0001 stud |

Le total de critères diffère parce qu'un critère n'est compté que s'il est
applicable : pureté de fréquence à partir de 3 cycles, jambes mesurées en
l'air seulement. Preuves (même fenêtre, même échelle) :
`experiments/r6_black_hole/output/motion_audit_avant_apres_peaks.png` et
`motion_audit_avant_apres_onion.png`.

---

## 6. Limites et prochaines étapes

- **Seuils non calibrés sur des animations pro.** Prochaine étape : les
  recalibrer sur les rotations (fiables) du `battleground_animation_pack`,
  lisible par `_shared/rbxm_reader.py`. Les positions des grands tableaux
  CFrame y sont suspectes (voir `_shared/README.md`).
- **Les autres prototypes n'ont pas été audités.** `r6_hit_combo` documente
  « Torso X positif = penché vers l'avant », l'inverse de la convention
  prouvée ici : **à vérifier avec `describe_pose`** avant toute reprise.
- Le critère de pureté de boucle exige ≥ 3 cycles. Sur des *holds* courts,
  l'organicité est garantie par construction (`organic_keys`), pas mesurée.
- `pops` distingue discontinuité et geste vif par la **largeur** du pic
  d'accélération. Un geste très court voulu doit être déclaré.

## Corpus et verdict calibré (2026-09-24)

`corpus.py` lit de vraies animations Roblox (`.rbxm`), `taxonomy.py` les range
par catégorie, `build_corpus.py` produit les distributions
(`corpus/categories.json`), et `audit.calibrated_verdict()` compare une
animation à la plage pro de sa catégorie.

Premier constat : les 19 animations du pack premium échouent aux seuils fixes
de `TARGETS` (7 à 14 critères sur 21-22). Ces seuils ne valent que pour la
catégorie « cinématique » ; les sections 4 et 5 de ce README ont été mesurées
avec eux. Détail et écart chiffré de nos coups : `corpus/README.md`.
