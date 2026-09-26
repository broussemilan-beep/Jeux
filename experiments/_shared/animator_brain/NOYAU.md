# NOYAU (relu automatiquement au démarrage et après chaque compaction)

Court par choix (≤ 3 500 caractères, `outils/budget.py`) : ce qui vaut pour
TOUTE session. Le détail vit dans les fiches ; un détail perdu se RECHERCHE
(`outils/rappel.py "<concept>"`), il ne se devine pas.

## Ce que Milan veut
- Réponses en français.
- On APPREND et on se nourrit ; pas de règles gravées dans la roche
  (2026-09-25 et 2026-09-26). Seuls les contrôles techniques bloquent
  (sol, contact, aller-retour moteur, interpolation, sens Roblox) ; le
  style se MESURE et s'affiche, sans verdict.
- Une note prédite chiffrée avant chaque livraison ; captures de preuve
  committées dans `captures/verification/` avec le changement.
- Passer à Roblox Studio seulement quand il le dit.
- Jamais de ref sous droits, de vidéo, de fichier TSB ni de frame de ref
  dans le dépôt : seulement des mesures dérivées.

## Où on en est
- Production active : « Un seul coup » (Serious Punch R6),
  `experiments/r6_un_seul_coup/`. v5 notée 7,5 ; v6 (poses MESURÉES des
  refs, fiche §11) : « c trjs pas bon ». Milan arrête l'itération sur ce
  coup et demande le chantier 4 : apprendre l'animation au sens large.
- Fiche active : `corpus/fiches/UN_SEUL_COUP.md`.
- Chantiers : 1 v6 ; 2 audit fait (`corpus/recherche/AUDIT_CERVEAU_2026-09-26.md`) ;
  3 réorganisation (`corpus/recherche/PLAN_REORGANISATION_2026-09-26.md`) ;
  4 EN COURS (2026-09-26) : se renourrir de tout le contenu envoyé
  (apprendre, comprendre, pouvoir refaire, affiner l'œil ; « pas combler
  des trous »). Étude faite : `corpus/etude_c4/SYNTHESE.md` (le cours ;
  chaque apprentissage marqué JEU ou CINÉ) ; reste les exercices.

## Ce que Milan a répété (ses mots exacts : `corpus/milan_verbatim.jsonl`)
- « Il frappe vers le bas » : 6 fois (Dragon v3-v7, Un seul coup v1). Au
  contact : poing à hauteur de poitrine, buste presque droit.
- « Tu n'animes que les bras » : 4 fois. Le corps porte le mouvement.
- « Je vois aucun changement » : 4 fois. Un changement se juge à vitesse
  réelle, au cadrage réel, à côté de la version d'avant.
- Poing chargé : « dans aucune [ref] le bras est tendu derrière » ; le
  recul vient du buste qui tourne ; jambes pas « trop abusées ».
- « Analyse visuellement, géométriquement » : mesurer les refs
  (`outils/geo_pose.py`), pas traduire des mots en clés.

## Ce qui a trompé le cerveau (audit du 2026-09-26)
- Des lectures en mots jamais mesurées, gardées après démenti : une
  lecture démentie porte la marque CONTREDIT, elle ne s'efface pas.
- Des leçons rangées en « historique » puis oubliées (« vers le bas »).
- Des outils de vigilance écrits puis jamais relancés
  (`outils/corps_bras.py`, `perception.py`, `outils/regard.py`).
- Des prédictions trop hautes (+0,3 en moyenne).

## Après chaque retour de Milan
Archiver ses mots (`outils/moisson_milan.py`), corriger la fiche du moment
en jeu d'abord, puis une fiche de classe, créer en dernier ; « rien à
inscrire » est une réponse possible. Chronique : `RETOURS.md`.
