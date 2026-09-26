# Réorganisation du cerveau d'animation : plan proposé à Milan

**Proposition, pas encore appliquée — 2026-09-26.**

Rien n'est déplacé, créé ni branché tant que Milan n'a pas répondu au §5.
Ce plan découle du chantier 3 (ETAT §1b). Il prépare le chantier 4 : se
renourrir de tout le contenu envoyé.

**Sources.** Ce plan s'appuie sur deux études vérifiées (scratchpad de
session, non versionnées) :
- `poing/hermes_complet.json` : Hermes Agent en 5 sous-systèmes (mémoire,
  skills, curateur, vérité, rappel), chaque mécanisme avec sa preuve de
  code ;
- `poing/audit_complet.json` : le cerveau en 8 tranches (refs, règles,
  outils pros, retours, productions, code, tutos, manga).

J'ai aussi relu en entier `ETAT.md`, `corpus/CARNET.md`, `RETOURS.md`,
`notes_milan.jsonl`, `outils/rappel.py` et les 6 fiches.

**Esprit du plan.** On apprend, on se nourrit. On ne grave aucune règle.
Seul le technique bloque un export. Tout le reste, ce sont des mesures
affichées avec les mots de Milan, et c'est l'œil de Milan qui juge.

---

## 1. Diagnostic : pourquoi on oublie, et pourquoi la mémoire se trompe

1. **Des leçons perdues à l'archivage.** Au commit 1395eb3 (26/09, 07:20),
   `LECONS.md` est passé en HISTORIQUE, et ses §10-11 (« vers le bas »)
   n'ont été reportés nulle part. Une compaction a suivi à 07:37. À 08:07,
   Un seul coup v1 refaisait « vers le bas ». CARNET 2.9 n'a été écrit
   qu'à 08:28 (7bb9526). La voie de promotion (CARNET l.10-11) mène
   toujours à ce fichier mort.
2. **Des lectures démenties toujours en place, et resservies en premier.**
   - `CATALOGUE_REFS.md:24` (« poing tiré loin derrière ») et `:31`
     (« bras alignés tendus ») sont réfutés par Milan (RETOURS:828). Ce
     sont pourtant les 2e et 9e lignes que sort `rappel.py "poing chargé"`.
   - CARNET 2.10 garde en titre « un ARC QU'ON TEND ». Sa correction est en
     sous-point, et elle a elle-même été démentie en v4.
   - CARNET 2.9 affirme un « garde-fou mis dans l'export » retiré par
     6f0539e.
   - `COUP_CHARGE.md:39` dit encore « poing armé DERRIÈRE ».
   - `UN_SEUL_COUP.md` §10 décrit un contrôle d'export qui n'existe plus.
   - Le CARNET n'a pas bougé depuis 8b768e4 (v4).
3. **Des outils perdus au passage au rig V2.22.** Sur le rig V2.22, tous
   ces outils restent muets :
   - `audit.py` (chevauchement, holds morts, glissement, équilibre),
     `tracks.offset_tracks`, `constraints.balance_margin`, `organic.py`,
     `poses.describe_pose` et `_spring_chase` (7 anciennes productions) ne
     tournent plus que dans r6_black_hole ;
   - `corps_bras.py` est prescrit par 3 documents, mais n'a jamais tourné
     sur Un seul coup ;
   - `etats.py` et `critic.py` sont gelés à la v9. `critic.py:138` ignore
     la clé `prediction` qu'utilise Un seul coup.
   `geo_pose` réinvente `describe_pose` sans le savoir.
4. **Un rappel qui sort de la prose et rate des mots.**
   - `rappel.py "poing chargé"` sort 122 lignes et 12,5 k caractères, sans
     un nombre de pose et sans aucun statut.
   - Il ignore les mots de moins de 5 lettres (« bas », « bras », « dos »).
   - « vers le bas » est rangé dans la famille « aerien » : pour « frappe
     vers le bas », LECONS sort 11e.
   - Il ne lit ni `clips/*.json`, ni `perception_*.json`, ni
     `hypotheses.json`. Il ne liste que les outils de `outils/`.
5. **Rien n'est réinjecté après une compaction.**
   - Mesuré : UNE seule session depuis le 31/08, 24 compactions (grep
     `isCompactSummary`), 197 messages de Milan. Le cerveau n'est jamais
     relu « à froid ».
   - `.claude/` est vide : aucun hook.
   - ETAT §2 ne fait relire que les « 3 dernières entrées de RETOURS » :
     RETOURS:83 et :110 (« vers le bas ») sortent de la fenêtre.
6. **Aucune preuve attachée aux affirmations.**
   - 49 entrées du CARNET sur 72 n'ont aucun des 5 statuts de l'en-tête.
   - 13 citations de Milan sur 24 ne se retrouvent pas mot pour mot dans
     RETOURS ou `notes_milan.jsonl`.
   - `verify_export.py:101` renvoie à une « fiche §11 » qui n'existe pas.
   - La docstring de `geo_pose` a le signe du lacet inversé.
   - Toute la géométrie mesurée des refs (`pro_tsb_ult`, `recon_*`,
     `fit.py`) est dans le scratchpad. Pour le cerveau, elle n'existe pas.
7. **Des mots traduits en contrôles vrai/faux, qui gravent l'erreur.**
   - `poing_derriere_pendant_la_charge` (7bb9526:99) a été exigé de la v2
     à la v4, puis inversé en 45 min.
   - `poing_a_hauteur_d_epaule` était au vert sur la v1 que Milan voyait
     « vers le bas ». Le contrôle mesurait par rapport à l'épaule, qui
     plongeait avec le buste.
   - Le Dragon a passé 13/13 règles pendant que les notes restaient entre
     6,7 et 7,5.
8. **Des leçons écrites comme le correctif du jour, pas comme ce que Milan
   voit.** « Pour frapper bas, c'est le corps qui descend » (LECONS §10) a
   produit un buste à 40°, donc encore « vers le bas ». Ce que l'œil lit,
   c'est la hauteur du poing face à la poitrine de la victime et la bascule
   du buste.

**Ce qui marche, et qu'on garde tel quel :**
- ETAT.md comme point d'entrée ;
- les fiches par moment ;
- le catalogue des refs par empreinte ;
- l'idée des statuts du CARNET ;
- RETOURS en chronique, `notes_milan.jsonl` ;
- les bandes à 0,1 s (`durees.py`), le lecteur avec three.js embarqué ;
- les captures committées ;
- la séparation « technique bloquant / mesures sans verdict » de 6f0539e ;
- la prédiction chiffrée avant de montrer.

---

## 2. La nouvelle organisation

### 2.1 Arborescence cible

`=` : chemin inchangé. `+` : nouveau. `~` : même chemin, contenu revu.

```
animator_brain/
= ETAT.md                  ~ §1 court ; « fiche_active: » ; bloc « Derniers
                             mots de Milan » GÉNÉRÉ ; journal vN -> RETOURS
+ NOYAU.md                 ≤ 3 500 caractères, déclaratif, injecté à chaque
                             démarrage et après chaque compaction
= RETOURS.md               ajout seul (la chronique)
= notes_milan.jsonl        ajout seul ; une clé unique `prediction_avant_milan`
+ PROPOSITIONS.md          ce qui attend l'accord de Milan (montré à chaque rapport)
+ ENTRETIEN/               ENTRETIEN.json (compteurs) + <date>/PROPOSITION.md, REPORT.md
  corpus/
  = CARNET.md              ~ pépites TRANSVERSES seulement ; index court en tête ;
                             format d'entrée à 5 champs (§2.3) ; ids inchangés
  = CATALOGUE_REFS.md      ~ + colonnes « mesuré » et « lectures (statut, date) »
  = fiches/                ~ deux sortes, en-tête `quand:` / `outils:` / `sorte:`
      _MODELE.md           + gabarit (liste « ne pas inscrire » en tête)
      COUP_CHARGE.md       ~ fiche de CLASSE : absorbe la charge d'UN_SEUL_COUP §7-10
      CONTACT_COUP.md      + fiche de CLASSE « arrivée d'un coup droit » (vers le bas)
      METHODE_POSE.md      + fiche de CLASSE « poser et animer en R6 » (Moon, repro,
                             corps d'abord, rôles de clés, pelure, tour)
      MESURER_UNE_REF.md   + fiche de CLASSE « mesurer une ref » (limite monoculaire,
                             arrêts 2D non validés, repères de mesure)
      AURA_DRAGON, PLEIN_ECRAN, VFX            = classes (inchangées)
      UN_SEUL_COUP, POING_DU_DRAGON_V13        = fiches de PRODUCTION (plan de scène)
  + milan_verbatim.jsonl   moisson des mots EXACTS de Milan (ajout seul)
  + motifs.json            défauts récurrents : ses mots, dates, mesure liée
  + poses/<moment>.json    poses MESURÉES des refs (garde, armé, charge, départ,
                             contact, suite), descripteurs geo_pose + provenance
  + preuves.jsonl          registre écrit PAR les outils (ajout seul)
  + refs_milan/<sha>.json  (chantier 4) une fiche par ref : phases, poses, cadrage,
                             lectures datées avec statut
  + sources/<id>.txt       (chantier 4) court extrait primaire d'un texte lu
  = clips/, tutos/, recherche/, refs/   inchangés
  outils/
  = rappel.py              ~ réparé (§2.4, point 8)
  + amorce.py, moisson_milan.py, revue.py, motifs.py, entretien.py,
    lint_cerveau.py, preuves.py, deplacer.py, archive_check.py,
    rapport_regard.py, ajuste_pose.py (versé du scratchpad), pose_live.py
= LECONS.md, CERVEAU_V2.md, PLAN.md, REFLEXION.md, ANGLES_MORTS.md, ...
                           restent EN PLACE, avec une pierre tombale par entrée
```

On ne renomme ni ne déplace rien de ce que cite CLAUDE.md : `ETAT.md`,
`outils/rappel.py`, `corpus/CATALOGUE_REFS.md`, `corpus/CARNET.md`,
`corpus/fiches/`, et le mandat `docs/PRODUCTION_MANDATE_v1.md`. Le code cite des ids (39 renvois
« CARNET § » ou « LECON » dans les .py, par exemple 2.1c, 4b.1, « LECON
6b ») : ces ids restent valides.

### 2.2 Rôle de chaque étage (routage : un savoir, un seul endroit)

| étage | fichier | ce qui y va | ce qui n'y va pas |
|---|---|---|---|
| 1. toujours lu | `NOYAU.md` | ce qui vaut pour TOUTE production : ce que Milan veut (« apprendre, pas de règles »), les 5-8 motifs actifs (une ligne chacun, avec un lien), la production et la fiche actives | le détail d'un moment ; tout ce que CLAUDE.md dit déjà |
| 2. à la demande | `fiches/` de classe | l'état COURANT de la compréhension d'un moment, réécrit en place, avec les retours de Milan sur CE moment et les poses mesurées | le journal des versions |
| 2 | `CARNET.md` | les pépites transverses (voir, juger, biais) | ce qui ne concerne qu'un moment : ça va dans sa fiche, avec une pierre tombale dans le CARNET |
| 3. source | `RETOURS.md`, `notes_milan.jsonl`, `milan_verbatim.jsonl` | la chronique et les mots exacts, jamais réécrits | une leçon qui ne vivrait QUE là |
| 3 | `preuves.jsonl`, `poses/`, `clips/` | les nombres, écrits par des outils | la prose |

Premier cas à traiter : « vers le bas » vit aujourd'hui dans 7 endroits,
et ils ne disent pas la même chose (LECONS §10, `rules.py`, CARNET 2.9,
UN_SEUL_COUP §6, RETOURS l.83/110/786, `coup_clip.py`, `notes_milan`). La
cible : `CONTACT_COUP.md` porte l'invariant et sa mesure. Les autres
endroits gardent un lien, et la source garde les mots.

### 2.3 Forme d'une entrée (CARNET et fiches)

```
**2.9 <ce que l'image dit, au présent, sans « jamais / toujours »>**
- Pourquoi (le mécanisme) : …
- Mesure : <outil> -> <json#clé> ; refs : <fourchette> ; nous : <valeur>
- Statut : mesuré | lu (texte vérifié / lu par agent / extrait) | vu dans les refs
           | essayé (résultat, note) | retour de Milan (date)
           | CONTREDIT par Milan le <date> (RETOURS:<ligne>)
- Source : Milan (<date>) : « <mots exacts, présents dans milan_verbatim> » ; <ref sha1>
- Anciennes lectures : [contredit v3, RETOURS:813] « arc tendu » …
```

On corrige la phrase fausse SUR PLACE. L'ancienne lecture passe en
sous-point marqué « contredit », au lieu de s'empiler dessous.

### 2.4 Principes repris de Hermes, et ce qu'on adapte ou inverse

| # | chez Hermes (preuve de code) | chez nous | ce qu'on inverse ou adapte |
|---|---|---|---|
| 1 | Noyau borné toujours injecté : MEMORY.md 2 200 caractères, écriture refusée au-delà (`memory_tool_store.py:99, 287`) | `NOYAU.md` ≤ 3 500 caractères ; `budget.py` signale un dépassement sans rien couper | En faits déclaratifs, jamais à l'impératif (guide mémoire de Hermes, `prompt_builder.py:225`). On AVERTIT au lieu de refuser. |
| 2 | Amorce : la mémoire est relue sur disque après une compaction (`system_prompt.py:802`) | `amorce.py` via un hook SessionStart `startup / resume / compact` (**avec l'accord de Milan**) : NOYAU, ETAT §1, 3 derniers messages de Milan (≤ 700 caractères), fiche active, motifs, PROPOSITIONS en attente, et la phrase « un détail perdu se RECHERCHE » | On réinjecte aussi à la reprise, ce que Hermes ne fait pas (il n'a pas notre contrainte de cache). Sans hook : une ligne dans CLAUDE.md. |
| 3 | Mots de l'utilisateur recopiés mot pour mot par du code dans le résumé (`context_compressor.py:980`) ; historique cherchable (`session_search`) | `moisson_milan.py` lit le transcript et écrit `milan_verbatim.jsonl` (uuid, date, texte brut, « dit » ou « collé ») ; lancé à chaque livraison, et en PreCompact si Milan le veut | Le transcript (1,1 Go, local au conteneur) n'est JAMAIS une preuve : on le moissonne vers git. |
| 4 | Provenance : qui a écrit, mais Hermes RETIRE dates et citations de la leçon (`background_review.py:373`) | Statut + source + preuve pour CHAQUE entrée (§2.3) | Inversé : chez nous, la date et les mots de Milan SONT la preuve. |
| 5 | Registre de preuves écrit par l'outil, jamais par le modèle (`verification_evidence.py`) | `preuves.jsonl` : chaque outil (`verify_export`, `durees`, `juge`, `geo_pose`, `rapport_regard`) écrit une ligne : commit, sha des sorties, type, portée (image / plan / scène / partielle) | Statut PAR type, pas « la dernière preuve gagne ». Seul le type `technique` peut échouer. On vérifie que le fichier ne fait que grandir. |
| 6 | Revue après le tour, ordre : skill en jeu, puis parapluie, puis support, puis nouvelle skill ; liste « ne pas capturer » (`background_review.py:392-500`) | `revue.py` après CHAQUE retour de Milan : (1) patcher la fiche du moment EN JEU ; (2) puis une fiche de classe ; (3) puis un support (mesure, outil) ; (4) créer en dernier. Une seule revue par retour. | On NE reprend PAS « Be ACTIVE » : « rien à inscrire » est une sortie valide, mais pas par défaut après un retour. Un essai non validé reste une « piste ». |
| 7 | Curateur : passe déclenchée par le temps (7 j), archivage après 14 et 30 jours sans usage, quota « moins de 10 archives, trop tôt » (`curator.py:31, 443`) | `entretien.py` déclenché par un COMPTEUR : ≥ 15 entrées nouvelles, ou une fiche > 12 ko, ou ≥ 3 retours non reliés, ou 3 productions. Dry-run complet (`PROPOSITION.md`), commit dédié, `REPORT.md` montré une fois au démarrage suivant. | Inversé : on n'archive JAMAIS ce qui est peu consulté (nos leçons portent sur des moments rares : coup chargé, impact). Pas de quota, pas de péremption en jours. On garde la provenance. Seul l'absorbé s'archive. |
| 8 | Pas de suppression sans `absorbed_into` vers une cible qui EXISTE (`skill_manager_guards.py:241`) | Pierre tombale « → absorbé dans fiches/X.md §n (date) » ; `archive_check.py` et `deplacer.py` | Plus fort que Hermes : on vérifie aussi que les nombres et termes clés sont bien arrivés dans la cible. |
| 9 | Rappel : repli trigram puis OU, sortie à deux niveaux, « aucun résultat ≠ aucun savoir » (`hermes_state_search.py:1129`) | `rappel.py` réparé : mots ≥ 3 lettres ; racines ou trigrammes, puis OU ; « vers le bas » dans la famille « contact » ; index d'entrées en tête (id, statut, nombres) ; meilleure fiche en entier (≤ 3 000 caractères) ; le reste en `fichier:ligne` ; lit `poses/`, `motifs.json`, `clips/*.json`, `perception_*.json` ; outils de tout le dépôt ; fichiers HISTORIQUE rétrogradés sans être exclus ; CONTREDIT affiché en dernier | Testé sur des cas connus AVANT tout branchement automatique : « frappe vers le bas » doit sortir CONTACT_COUP en 1er. |
| 10 | Le compte rendu vient des actions réelles, pas de la prose (`background_review.py:663`) | `lint_cerveau.py` vérifie qu'existent chaque chemin cité, chaque §, chaque « garde-fou » annoncé et chaque citation de Milan. Rapports encadrés par « Cerveau consulté : … » et « Cerveau mis à jour : … (commit) » | Consultatif : il avertit, il ne bloque jamais un commit (leçon de la « tempête de refus » de Hermes : ~346 refus en 2 jours, boucle affamée). |

---

## 3. Ce qui reste un APPRENTISSAGE et ce qui est un contrôle TECHNIQUE

| élément | nature | forme | bloque ? |
|---|---|---|---|
| Interpolation Linear (EasingStyle 0) à l'export | technique | vrai/faux (`verify_export`) | **oui** |
| Orientation des rigs, victime en face, sens Roblox | technique | vrai/faux | **oui** |
| Aller-retour moteur C0/C1 | technique | vrai/faux | **oui** |
| Sol (< −0,1 stud), tête non décalée | technique | aujourd'hui seulement affichés : à rendre bloquants, ou tolérance dite | **oui**, si Milan le veut |
| Intention de CETTE scène (poing devant au contact, éjection…) | technique déclaré dans la scène | bloc séparé de `sens` | oui, pour cette scène seulement |
| Capture citée comme preuve, présente dans git | process | contrôle d'existence (`lint`) | bloque le mot « livré » |
| « Vers le bas » | apprentissage | mesure affichée : poing au contact face à la poitrine de la victime, bascule du buste, à côté des fourchettes des refs | non |
| « Que les bras » | apprentissage | `corps_bras` : torse figé x/y par phase, à côté de la ref | non |
| « Aucun changement » | apprentissage | écart N−1 → N en degrés et en pixels, depuis la caméra du plan, à vitesse réelle | non |
| Pose du poing chargé | apprentissage | descripteurs `geo_pose` à côté de `poses/coup_charge.json` | non |
| Épaules, croix, transfert, affaissement (`rules.py`) | apprentissage | valeur et position dans chaque source (pack, TSB, refs), sans « ok » ni X/Y | non |
| Juge temporel (`juge.py`) | apprentissage | profil choisi selon le style déclaré, affiché | non |
| Prédiction chiffrée | œil critique | écart consigné, biais mesuré | non |
| Budget du NOYAU, statuts, citations, liens | hygiène de la mémoire | `lint` consultatif | non |

**Une leçon répétée devient une MESURE affichée avec ses mots, pas une
porte.** Exemple de ce qu'imprimera `motifs.py` dans chaque rapport de
version :

```
« vers le bas » : tu me l'as dit 6 fois
  03/09 directional_punch « on dirait que le coup part du bas alors qu'il doit aller droit »
  24/09 Dragon v3 « tu donnes des coups vers le bas » ; v3b « les coups partent toujours du bas »
  24/09 v4 « au coup final le coup part toujours d'en bas » ; 25/09 v7 « qui part toujours d'en bas »
  26/09 Un seul coup v1 « le perso frappait vers le bas »
  cette version (v5) : poing au contact 3,37 studs | buste 7,3° | fourchette des refs : à remplir (B2)
  version où tu ne l'as plus dit : USC v2 (3,4 studs, 7°)
```

Les autres motifs suivent le même format :
- « que les bras » : 3 fois de Milan (directional_punch, Dragon v9, USC v4
  « l'arrière est engagé par le buste ») ;
- « aucun changement » : 4 fois (Dragon v5, v7, v8 ciné, USC v3) ;
- mauvaise lecture de ses mots : 6 cas.

Chaque mesure est rejouée sur la version qui l'a fait naître. La v1 d'Un
seul coup doit sortir de la fourchette. Sinon, la mesure regarde la
mauvaise grandeur (c'est le cas de `check_bras_au_contact`, qui renvoie
ok=True sur cette v1).

---

## 4. Les briques de code, dans l'ordre

Les efforts sont estimés pour une session de travail, tests compris.
scipy n'est pas installé : les ajustements se feront en numpy
(Levenberg-Marquardt), ou après l'installation de scipy.

### 4.1 Maintenant (avant le chantier 4), environ 4 jours

| # | brique | effort | dépend de |
|---|---|---|---|
| A0 | **Verser le scratchpad avant qu'il disparaisse** : mesures TSB, pack et reconstructions (`pro_tsb_ult`, `pro_tsb_m1`, `pro_pack`, `recon_*`) vers `corpus/poses/` (statut « exact R6 » ou « reconstruit, non validé ») ; `fit.py`, `fitkp.py` et `pose_live_proto.py` vers `outils/` | 0,5 j | rien |
| A1 | Corrections sur place, sans code : CARNET 2.9 et 2.10 ; CATALOGUE:24, :31 ; COUP_CHARGE:39 ; UN_SEUL_COUP §10 ; voie de promotion CARNET:10-11 ; renvoi §11 de `verify_export.py:101` ; docstring du lacet de `geo_pose` ; ETAT §3 (marquer rules / etats / critic / audit « en veille depuis v9 ») | 1 h | rien |
| A2 | `archive_check.py` : chaque entrée d'un fichier HISTORIQUE a une destination vivante, ou « abandonnée : raison ». À lancer AVANT toute pierre tombale (LECONS §10-11 d'abord) | 2 h | rien |
| A3 | `moisson_milan.py` vers `milan_verbatim.jsonl` (197 messages ; filtre des résumés de compaction et des injections du harnais) | 3 h | rien |
| A4 | `rappel.py` réparé + `tests/rappel_selftest.py` (cas connus) | 0,5 j | A1 |
| A5 | `NOYAU.md` + `amorce.py` + `budget.py` (hook seulement après le oui de Milan, §5) | 3 h | A3, A4 |
| A6 | `motifs.py` + `motifs.json` (« tu me l'as dit N fois », dates, mesure liée) | 0,5 j | A3 |
| A7 | `lint_cerveau.py` consultatif : statuts, citations contre `milan_verbatim`, liens, affirmations sur le code, absolus sans source, doublons, orphelins cherchés dans TOUT le dépôt | 0,5 j | A3 |
| A8 | `preuves.py` + `preuves.jsonl`, branchés dans `verify_export` (les deux productions), `durees`, `juge`, `geo_pose` | 0,5 j | rien |
| A9 | **`rapport_regard.py` non bloquant** : il rebranche les outils perdus (`corps_bras`, pelure du torse, `audit.audit` via `corpus.to_samples` avec un `contact_eps` réglé pour V2.22, `perception` charge / torsion / arcs / silhouette, `geo_pose` aux marqueurs, `fist_path`, `timing_profile`). Sortie : JSON + planche dans `captures/verification/` + une ligne « hors plage, à DIRE » | 0,5-1 j | A6, A8 |
| A10 | `revue.py` + `fiches/_MODELE.md` (ordre de patch, liste « ne pas inscrire ») ; `deplacer.py` (pierre tombale + commit dédié) | 3 h | A2 |

Ordre : A0 et A1 d'abord (on perd ou on se trompe sinon), puis A2 à A5 (on
ne réorganise rien avant `archive_check`), puis A6 à A10. Aucune fusion de
fichiers avant A2 et A10.

### 4.2 Pendant le chantier 4 (se renourrir de tout)

Protocole de digestion (inspiré de `/learn` de Hermes) :
- une ref ou un tuto à la fois, persisté avant de passer au suivant ;
- chaque nombre avec son renvoi (outil + JSON) ;
- on étend la fiche de CLASSE qui existe avant d'en créer une ;
- on termine en réconciliant avec le CATALOGUE.

Compteur de couverture affiché par `entretien.py` : environ 66 refs au
catalogue, 21 tutos (dont 6 vus en image), refs digérées / total.

| # | brique | effort | dépend de |
|---|---|---|---|
| B1 | `tests/geo_pose_selftest.py` : 10 poses connues, rendues sous plusieurs caméras, reconstruites, erreur en degrés (exigé par ANGLES_MORTS §7, jamais fait) | 3 h | A1 |
| B2 | **Bibliothèque `corpus/poses/`**, d'abord la partie R6 exacte : les 13 anims TSB via `geo_pose.mondes_rbxm` (Stoic Bomb, Collateral Ruin et Ultimate1/2 sont des CHARGES) et le pack, rangés par moment | 1 j | A0 |
| B3 | **`ajuste_pose.py`** : pose R6 et caméra ajustées depuis 10-12 points 2D (JSON) et la silhouette. Plusieurs vues liées (Pew face et dos, TSB). Sortie : les N meilleures solutions, avec un drapeau « ambigu » quand elles divergent (bras devant ou derrière : `fitkp_290_A.log` garde 8 solutions de coût voisin, 0,28-0,43, bras droit de −46° à +136°). Résidu en pixels | 1,5-2 j | B1, A0 |
| B4 | `refs_milan/<sha>.json` : phases en temps, poses mesurées, cadrage mesuré, lectures datées avec statut (d'abord les 3 Serious Punch et Pew) | 1 j | B3 |
| B5 | **Pont `geo_pose` vers les clés V2.22** (mode `geo` de `solve_pose`) : écrire une clé en nombres d'animateur, la convertir en contrôles IK, RE-MESURER et afficher l'écart demandé / obtenu. Unifier az/el avec le mode `a` | 1 j | B1 |
| B6 | `pose_live.py` : une clé résolue en moins d'1 s, ref, nous et superposition depuis la caméra de la ref. Une planche committable SANS pixels de ref (squelette relevé + notre rendu + chiffres) | 0,5 j | B3, B5 |
| B7 | `suivi_membre.py` : trajectoire 2D d'un poing ou d'une tête dans une vidéo de ref (cv2 est installé), mêmes sorties que `fist_path.py` | 1 j | rien |
| B8 | Œil critique : planche ref, v(n−1) et v(n) depuis la caméra du plan, à vitesse réelle ; prédiction falsifiable (« le changement se verra-t-il ? oui / non » + note) ; `critic.py` réparé (clé unique, id production + version) | 1 j | A8 |
| B9 | Première passe `entretien.py` en dry-run après la digestion (pierres tombales, fusions vers les fiches de classe) | 0,5 j | A2, A10 |

Pour « pouvoir REFAIRE », chaque technique digérée donne un essai R6 :
`pose_live` + pont B5, mesuré à côté de la ref, enregistré dans
`preuves.jsonl`. Pour « l'œil critique », on prédit AVANT de comparer, et
l'écart est consigné.

### 4.3 Plus tard

- Pipeline « corps d'abord » sur V2.22 (`moon`, `tracks.offset_tracks`, FK
  des bras du rig) : 2-3 j.
- Easing par pose (Constant pour les tenues : TSB en a 67) ; retiming ;
  fenêtre « éparse » généralisée : 0,5-1 j.
- Porter en option, testés en A/B : `_spring_chase`, `balance_margin`,
  smear de r6_directional_punch : 0,5 j chacun.
- Poseur three.js pour Milan (il MONTRE la pose au lieu de l'expliquer) :
  1 j.
- Lecteur A/B : deux variantes du même moment, une seule question : 2-3 h.
- Hook UserPromptSubmit (`rappel.py --court`), seulement quand A4 a fait
  ses preuves.
- Skills natifs Claude Code, un par moment, qui pointent vers la fiche.
- Détecteur de contradictions entre entrées ; `doublons.py`.

---

## 5. Ce que Milan doit décider

1. **Hook de démarrage.** Est-ce que j'ajoute `.claude/settings.json` avec
   SessionStart (`startup / resume / compact`), qui lance `amorce.py` ? Et
   PreCompact, qui lance `moisson_milan.py` ? (Oui / non / seulement
   SessionStart.)
2. **Niveau d'automatisme.** (a) Consignes et outils lancés à la main ;
   (b) + l'amorce automatique ; (c) + un hook Stop qui AVERTIT, sans jamais
   bloquer, quand un de tes retours n'a pas eu de revue.
3. **Tes mots dans le dépôt.** OK pour verser tous tes messages bruts
   (`milan_verbatim.jsonl`), ou seulement tes retours sur les animations ?
4. **Ce qui attend ton accord.** Toute réécriture d'une de tes phrases,
   toute fusion de fiche ou tout contrôle nouveau passe par
   `PROPOSITIONS.md`, que je te montre à chaque rapport. Ou bien je fais
   librement et je te montre après ?
5. **Sessions.** Une session Claude Code par chantier ou par version, avec
   un rituel de fin (moisson, fiche, ETAT, commit), pour que le cerveau
   soit relu à froid ?

---

## 6. Risques, et comment on les tient

- **Recréer des règles en croyant organiser.**
  - Risques : le lint, les motifs ou le NOYAU deviennent des portes.
  - Parade : le lint avertit et ne bloque jamais ; le NOYAU est déclaratif ;
    les motifs sont des mesures avec ses mots ; seul le technique du §3
    bloque. Toute nouvelle porte passe par `PROPOSITIONS.md`.
- **Casser des chemins.**
  - Les chemins cités par CLAUDE.md sont gardés, et les ids du CARNET et
    de LECONS aussi (39 renvois dans le code).
  - Pas de renumérotation.
  - Les orphelins et les liens morts sont cherchés dans TOUT le dépôt.
- **Perdre quelque chose.**
  - `archive_check` passe avant tout marquage HISTORIQUE. Les déplacements
    se font par `git mv` et une pierre tombale.
  - Un commit d'entretien est séparé de la production.
  - Il ne touche jamais les fichiers en ajout seul (RETOURS, notes,
    verbatim). Sinon, un `git revert` pourrait effacer un retour de Milan.
- **Industrialiser la dérive.** On réconcilie d'abord les versions
  divergentes (« vers le bas » à 7 endroits), et ensuite seulement on
  automatise.
- **Du bruit.**
  - Un rappel injecté mais bruité est pire que rien : A4 est testé avant
    tout hook.
  - Un hook Stop mal fait boucle : il doit lire `stop_hook_active` et
    accepter « rien à inscrire ».
- **Une fausse précision.**
  - Une note globale ne dit pas quelle entrée était fausse : on n'ajuste
    que les entrées que ses mots visent.
  - Les prédictions reposent sur n = 7 : l'écart n'est pas significatif.
- **Une reconstruction fausse qui devient une « fourchette ».** Le test sur
  vérité connue (B1) passe avant. L'ambiguïté est signalée. Le statut
  « reconstruit » reste distinct de « exact R6 ».
- **Le scratchpad perdu** si la session se ferme. C'est pour ça que A0
  vient en premier.
- **Les droits.** Jamais de ref versionnée : seulement des données
  dérivées et des planches sans pixels de ref.
- **Retarder la v6.** Le chantier 1 continue en parallèle. A0 et B2 le
  nourrissent directement (la « §11 » attendue).
- **Des inconnues.** La sémantique exacte des hooks (injection de la sortie,
  pouvoirs de PreCompact) est à vérifier dans la doc de Claude Code avant
  de configurer. Hermes est sous licence MIT : on s'inspire, on ne recopie
  pas de gros blocs.
