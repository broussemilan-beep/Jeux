# Retours de Milan, production par production

Ce journal est relu **avant** chaque production (voir `LECONS.md`). Chaque
retour porte :
- la note ;
- ce qui plaît ;
- ce qui ne va pas ;
- la leçon qui en est tirée ;
- la preuve que la version suivante l'a traitée : rapport `rules.py` avant/après.

Ce fichier ne contient que des retours réellement donnés par Milan, jamais une
note inventée.

## Poing du Dragon v1 (2026-09-24), `experiments/r6_poing_dragon`

- **Note** : 6/10.
- **Ce qui plaît** : « c'est pas mal sur tout le jeu aérien » (uppercut, envol,
  temps suspendu, plongée).
- **Ce qui ne va pas** :
  - « des problèmes sur l'enchaînement » : la rafale ;
  - « ça manque d'un ressenti de puissance » ;
  - « il est accroupi ».
- **Auto-critique demandée avant correction** (Milan : « dis-moi ce que tu en
  penses honnêtement ») :
  - rafale 4/10, final 5/10, aérien 7/10 ;
  - impact final caché par les planches manga ;
  - pas de son : Milan s'en fiche, écarté.
- **Question de Milan** : « est-ce que le cerveau a servi, ou a été nourri ? »
  - Réponse honnête : il a servi d'outil technique et de correcteur après coup,
    pas de guide de conception.
  - Il avait l'info sur la posture et elle n'a pas été lue.
  - Rien de la production n'était reversé dans le cerveau.
  - D'où `LECONS.md`, `rules.py` et ce journal.
- **Règles sur la v1** (`output/regles_v1.json`) : 3/7. Échecs :
  - posture (affaissement médian 0,55 contre 0,12 max) ;
  - hitstop constant ;
  - un seul angle de caméra pour 6 frappes ;
  - impact final visible 0 f.

## Poing du Dragon v2 (2026-09-24) : réponse au retour v1

Pas encore revu par Milan.

Règles (`r6_poing_dragon/output/regles_v2.json`) : **7/7**, contre 3/7 en v1.
- posture : affaissement max 0,19, médian 0,11 (seuils 0,24 / 0,12) ;
- escalade du hitstop : 0,03 → 0,085 ;
- recul de la victime : 0,28 → 1,22 stud ;
- secousse : 0,14 → 0,42 ;
- caméra : 2 frappes par plan au maximum ;
- impact visible 10 f ;
- plongée : 30 f sans coupe.

Preuve visuelle : `captures/verification/2026-09-24-poing-dragon-v1-vs-v2.png`.

