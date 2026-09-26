# Dépôt 6 : Action Library (CGstuff), vu pour les « yeux » du cerveau

Étude du 2026-09-26, en lecture seule. Rien n'a été modifié dans `/home/user/Jeux`.
Scripts de test et sorties : `/tmp/claude-0/-home-user-Jeux/4796ac9e-8e41-51f7-91c4-7b92a6a187d0/scratchpad/al_test/`.

## 0. En une phrase

C'est un **outil de revue pour humains**, pas des yeux : il **juxtapose**
deux versions, synchronisées par numéro d'image, et laisse une personne
écrire et dessiner dessus. Il ne mesure rien du mouvement. Pour nous, les
idées utiles sont la mise en scène de la comparaison (version d'avant à
gauche, lecture en boucle, notes ancrées à une image) ; il faut les
**refaire nous-mêmes en petit**, en y ajoutant ce qui manque (horloge
réelle, son, synchro sur un événement, mesure de l'écart entre versions).
Le code ne se copie pas (GPL-3.0), et l'application ne tourne pas ici.

## 1. Identification du dépôt

- **Dépôt retenu** : https://github.com/CGstuff/Action-Library, cloné dans
  `/home/user/ext/action_library` (`--depth 1`).
- **Pourquoi celui-là** : son README décrit mot pour mot ce que Milan cite.
  La section « Version Comparison & Review » parle de « lineage system
  (v001 → v002 → v003) », de « side by side with synchronized playback », de
  « timestamped review notes and draw annotations directly on frames ». On y
  trouve aussi « Pose Blending » et « Ctrl + Double-click to apply mirrored ».
  Le nom « Action Library » est porté par d'autres projets (addons de
  bibliothèques de poses, bibliothèque d'assets de Blender) ; la recherche
  n'en a fait ressortir aucun autre qui ait versions, revue et annotations
  ensemble. Je n'ai pas examiné ces homonymes en détail.
- **Licence** : GPL-3.0 (`LICENSE`). **Aucune ligne de code ne doit entrer
  dans notre dépôt** : on prend les idées et on les réécrit.
- **Dernier commit** : `98c88b1`, 2026-08-27 15:41 +0300, « optmized blender addon ».
  CHANGELOG de 1.0.0 (2026-01-06) à 1.6.0 (2026-08-27). Un seul auteur,
  très actif, et un journal de corrections honnête.
- **Taille** : 346 fichiers, environ 72 000 lignes de Python. Il y a des
  doublons dans `.sync_baselines/`.
- **Deux morceaux** : une application de bureau PyQt6
  (`animation_library/`) et un addon Blender (`blender_plugin/`) qui parle à
  l'application par socket.
- **Dépendances** (`requirements.txt`) : PyQt6 ≥ 6.5, opencv-python,
  Pillow, python-dateutil. **Aucun GPU, aucun modèle, aucun réseau de
  neurones.** Il n'y a aucun test : `find -name 'test_*.py'` ne renvoie rien,
  alors que pytest figure dans les dépendances de développement.

## 2. Ce qui est RÉELLEMENT implémenté (lu dans le code)

### 2.1 Comparaison côte à côte « synchronisée »
`animation_library/widgets/dialogs/comparison_widget.py`
- l. 294-295 : `fps = max(fps_A, fps_B, 24)` et durée = la plus longue des deux.
- l. 326 : la lecture avance au rythme d'un `QTimer` réglé sur
  `int(1000 / (fps * vitesse))` ms.
- l. 339-368 (`_sync_frame_update`) : à chaque tick, les deux vidéos prennent
  **le même numéro d'image** (`+1`). La plus courte reste figée sur sa
  dernière image.
- l. 409 (`_seek_both`) : le déplacement dans le temps suit la même logique
  (même numéro d'image, borné pour chaque vidéo).
- Il n'y a **pas d'horloge réelle** : ni `QElapsedTimer`, ni
  `perf_counter`, ni saut d'images (grep vide). Si le décodage prend du
  retard, la lecture ralentit sans le signaler. À 30 fps, le tick vaut
  33 ms, soit 30,3 im/s.
- Il n'y a **pas de son du tout** : aucun `QMediaPlayer` ni
  `QAudioOutput` dans `animation_library/` (grep vide).
- Il n'y a **aucun mode superposé** : ni différence, ni volet, ni
  transparence. Le seul « ghost » concerne les **traits dessinés**
  (`compare_video_column.py` l. 308-314 : traits des images voisines, rouge
  avant et vert après), pas les images de la vidéo.

### 2.2 Notes horodatées
`animation_library/services/notes_database.py` l. 82-138 (SQLite) :
- `review_sessions(animation_uuid, version_label)` ;
- `review_notes(session_id, frame INTEGER, note, author, author_role,
  resolved, resolved_by, deleted…)` ;
- `note_audit_log` : historique de chaque action sur une note (création,
  résolution, suppression douce).
« Horodaté » veut dire en fait **ancré à un numéro d'image d'une version
précise**. Une note de v002 ne se transpose pas en v003 : aucun code de
report ou de recalage entre versions.

### 2.3 Dessin sur l'image
- `animation_library/services/drawover_storage.py` l. 28-36 : un fichier
  JSON de traits vectoriels par image et par version
  (`drawovers/{uuid}/{version}/f0125.json`), avec un cache PNG.
- `widgets/drawover_canvas.py` l. 217-221 : coordonnées normalisées (0-1),
  donc indépendantes de la résolution.
- `compare_video_column.py` l. 236-300 : dans le **lecteur**, le mode
  « hold » garde le dernier dessin affiché jusqu'au suivant, et le mode
  « ghost » montre les traits des images voisines.
- **Export MP4 annoté** (`services/annotated_export_service.py`) :
  - l. 185-215 : les traits ne sont incrustés **que sur l'image annotée**.
    Le hold du lecteur n'existe pas à l'export.
  - l. 272 et suivantes (`_encode_to_mp4`) : ffmpeg reçoit `-framerate fps`
    et une suite de PNG, **sans aucune entrée audio**.
  - Le fps vient des métadonnées de l'animation, 24 par défaut
    (`version_history_dialog.py` l. 121 et 712), et non de la vidéo.

### 2.4 Versions (« lignée »)
- `services/database/schema.py` l. 177-182 : `version_label` (v001…),
  `version_group_id`, `is_latest`, `status`.
- `config.py` l. 671-678 : statuts `wip`, `review`, `approved`,
  `needs_work`, `final`.
- Une version est un nouvel enregistrement dont l'étiquette ne change plus.
  **Aucune différence n'est calculée** entre deux versions : rien ne dit ce
  qui a changé.

### 2.5 Mélange de poses et miroir (addon Blender)
- `blender_plugin/operators/AL_slots_manager.py` l. 20-48 : mélange de
  quaternions correct. Les signes sont alignés sur le premier quaternion,
  puis une moyenne linéaire est normalisée (nlerp). `ADD` compose les
  rotations.
- `blender_plugin/utils/socket_commands.py` l. 814-885 (mélange miroir) :
  - échange des noms `.L/.R`, `_L/_R`, `Left/Right` ;
  - quaternion local `(w, x, -y, -z)` et position `x → -x` ;
  - interpolation **composante par composante, sans renormaliser** (l. 860-866).
- l. 887 et suivantes (repli pour Blender ancien) : la table de noms
  **n'a pas `Left/Right`**. Les parties R6 n'y seraient pas échangées.
- Le miroir d'une **animation entière** (`AL_apply_animation.py`
  l. 319-420) et d'une pose (`socket_commands.py` l. 458 et suivantes)
  utilisent le copier / « coller retourné » de Blender. Il faut une **zone
  d'interface** (Dope Sheet, 3D View) ; sans zone, la fonction renvoie
  `None` (l. 368-370). C'est **inutilisable en `bpy` sans interface**,
  comme chez nous.

### 2.6 Aperçus
- `blender_plugin/operators/AL_update_preview.py` l. 739-743 : le rendu passe
  par `bpy.ops.render.opengl(animation=True, view_context=True)`, un
  playblast de la vue 3D, qui demande une fenêtre.
- `AL_capture_animation.py` l. 1044 : l'action est stockée dans un `.blend`
  (`bpy.data.libraries.write`), accompagnée de métadonnées JSON.
- `services/preview_sprites.py` l. 1-30 : les aperçus animés de la grille
  sont des planches de sprites dont les images sont « sampled evenly across
  the whole clip and capped ». L'auteur l'écrit lui-même : « a flipbook of
  the motion rather than a faithful playback ». Ce n'est donc **pas la
  vitesse réelle**.

### 2.7 Maturité
C'est un outil de production sérieux pour un humain : une base SQLite en
WAL, des écritures atomiques, un verrou contre les écritures concurrentes
(`drawover_storage.py` l. 44-70) et un journal d'audit. En revanche, il n'a
aucun test, il est pensé d'abord pour Windows et construit autour d'une
interface. **Il n'y a aucune analyse** : pas de métrique, de différence, de
similarité ni de trajectoire. Dans l'application, `cv2` sert à décoder et à
faire les vignettes, rien de plus.

## 3. Ce que j'ai testé, vraiment (moins de 15 min, sans GPU)

**Impossible : installer et lancer l'application.**
`pip install PyQt6` échoue avec « No matching distribution found ».
`pip index versions numpy` échoue de la même façon : l'index pip n'est pas
joignable depuis ce conteneur à ce moment. L'addon demande Blender avec
interface pour le miroir d'animation et l'aperçu. J'ai donc **extrait et
lancé leurs fonctions sans Qt** (via `ast`), et testé leur logique sur nos
données.

**Test A : la synchro « même numéro d'image » sur nos versions**
(`test_sync.py`). Méthode : luminance et différence image à image des
vidéos d'Un seul coup v1, v2, v4, v5 et v6.
- Résultat : toutes font **393 images à 30 fps** et le **flash du contact
  commence à f146 dans chacune** (images au-dessus de 200 de luminance :
  f146 à f155, identiques d'une version à l'autre).
- Conclusion : pour comparer **nos versions entre elles**, la synchro naïve
  d'Action Library suffit, parce que notre scène garde le contact à
  l'image 146.
- Elle ne suffit plus dès que le timing interne change. Les coupes de
  caméra de la charge bougent : v1 f118/119/131, v2 f136/141, v6
  f114/126/134. Et elle ne marche pas du tout **contre une ref** (TSB, Pew)
  dont le contact tombe ailleurs.

**Test B : leur export annoté sur notre v6** (`test_burnin.py`, avec leurs
fonctions `_composite_frame_with_annotation` et `_encode_to_mp4` telles
quelles). Une flèche est posée sur f140.
- L'incrustation fonctionne (`burnin_f140.png`).
- La flèche n'est visible que sur **1 image, soit 42 ms à 24 fps** :
  invisible à vitesse réelle.
- Avec le fps par défaut (24, faute de métadonnées), le MP4 dure **16,375 s
  au lieu de 13,1 s**, donc 1,25 fois plus lent, et **n'a plus de piste
  audio** (ffprobe : un seul flux, vidéo). Notre vidéo d'origine a un flux
  audio.
- Ce défaut vient de l'usage hors de leur chaîne, où Blender fournit le
  fps. Mais c'est exactement l'usage que nous en aurions.

**Test C : leur miroir de pose appliqué au R6** (`test_miroir.py`, sur
`usc_attaquant.rbxmx`, 115 clés, 12,5 s). Je comparais deux miroirs :
- **naïf** (celui d'Action Library) : échange Left/Right, rotation locale
  du Transform `P·R·P` (quaternion `(w, x, -y, -z)`), position `x → -x` ;
- **correct** : réflexion `P = diag(-1, 1, 1)` dans l'espace du
  personnage, puis Transforms recalculés.
- Ma prédiction était que le naïf serait faux sur R6. **Elle était fausse.**
  L'écart est de **0,0°** et 0,00 stud sur les 6 parties et les 115 clés,
  et l'aller-retour vers les Transforms est exact (0,0°).
- Raison : les C0/C1 standard de Right et Left Shoulder et Hip sont
  exactement l'image miroir les uns des autres. Sur un R6 standard, le
  miroir local est donc exact. La position monde du HumanoidRootPart, la
  caméra et les effets restent à retourner à part.

**Test D : adaptation, côte à côte v5 | v6 avec son et annotation tenue**
(ffmpeg `hstack` + `overlay enable='between(n,140,155)'`, 7 s de calcul).
- Sortie : `cote_a_cote_v5_v6.mp4` en 1704×480, 30 fps, **avec audio**,
  13,12 s. Le numéro d'image est incrusté et la flèche tenue 0,5 s
  (`cote_f144.png`).

**Test E : ce qu'Action Library ne fait pas, mesurer l'écart entre deux
versions** (`diff_versions.py`). Méthode : vignettes 213×120 en niveaux de
gris ; un pixel « change » si l'écart dépasse 25 ; une image compte si plus
de 2 % de l'écran change.
- **v4 → v5** : seulement **49 images sur 393, soit 1,63 s** (f93-141,
  c'est-à-dire la charge). Le reste est identique à l'image près, ce qui
  prouve que le rendu est déterministe. Pic de 79 % à f141.
- **v5 → v6** : **213 images, soit 7,10 s**, en trois plages : f93-145
  (1,77 s), f157-257 (3,37 s, après le contact) et f309-367 (1,97 s).
- Je ne savais pas que la v6 changeait autant l'après-contact. À vérifier
  dans le code de la v6 : c'est un **fait mesuré** que je n'avais pas vu.
- C'est aussi exactement la mesure qui manquait face aux quatre « je vois
  aucun changement » de Milan. Elle dit **où et combien de temps**
  l'écran change. Elle ne dit pas si c'est mieux.

## 4. Briques utiles pour NOS yeux

Barème d'intérêt : 0 à 10, pour nous et pas dans l'absolu.

| # | Brique (idée d'Action Library, ou manque révélé) | Faiblesse | Forme adaptée R6 / Roblox | Coût | Intérêt |
|---|---|---|---|---|---|
| 1 | **Lecteur côte à côte, version d'avant à gauche**, en boucle | 1, 3, 4 | Vidéos au **cadrage réel**, avec **son**, cadencées sur une **horloge réelle** (`performance.now()` dans un lecteur HTML, ou ffmpeg `hstack` comme au test D), numéro d'image incrusté. On le montre à Milan avec chaque livraison et on le **regarde soi-même à vitesse réelle avant de prédire la note** | 1 script ffmpeg (testé : 7 s) ; lecteur HTML d'environ 150 lignes | 9 |
| 2 | **Synchro sur un ÉVÉNEMENT, pas sur un numéro d'image** (absente d'Action Library) | 1, 2, 3 | Marqueurs (départ, fin de charge, contact, fin du recul) lus dans nos `KeyframeMarker` ou `scene.json` (`contact_f`), et dans les refs à la main ou par `durees.py`. Recalage **par morceaux** entre marqueurs : ref et nous alignés au contact, durée de chaque phase affichée | Faible : interpolation linéaire par morceaux sur les images, environ 60 lignes | 8 |
| 3 | **Écart mesuré entre versions** (absent d'Action Library, testé en E) | 3, 4 | Plages de temps où plus de x % de l'écran change, pic et durée totale, avec en option un masque « perso seul » (notre moteur de rendu sait faire des silhouettes, `vues.py`) pour séparer l'animation des effets et de la caméra. **Affiché sans verdict** : « la v6 change 1,77 s de charge et 3,37 s d'après-contact » | Très faible (testé : environ 40 lignes, moins de 30 s de calcul) | 9 |
| 4 | **Notes ancrées à une plage d'images** (review_notes : frame, auteur, résolu, audit) | 4, 5, mémoire | Un `jsonl` : `{production, version, f_debut, f_fin, auteur: "milan"|"claude", source: "mots_exacts"|"mon_interpretation", texte, vu_dans_version}`. Les mots de Milan restent exacts (`milan_verbatim.jsonl`) ; l'**ancrage à une plage est mon interprétation et doit le dire**. Report automatique à la version suivante **par événement** (brique 2), pas par numéro d'image | Faible | 7 |
| 5 | **Dessin tenu et fantômes** | 2, 3 | Pas de dessin à main levée. Des **surimpressions calculées** : ligne d'épaules, hauteur du poing contre la poitrine, axe du buste, direction du coup, projetées depuis nos mondes R6 (`lire_kfseq`), **tenues au moins 0,3-0,5 s** à l'export, sinon invisibles (test B). Pour la profondeur (faiblesse 2) : un **petit encart vu de dessus** qui dit si le bras est devant ou derrière le torse | Moyen : il faut la projection caméra, déjà dans `moon.py` | 6 |
| 6 | **Un même clip sous deux caméras côte à côte** (idée tirée de la brique 1, qu'Action Library n'a pas) | 5 | Colonne A : caméra joueur de jeu (épaule, FOV Roblox 70, fixe). Colonne B : caméra écrite de la cinématique. La pose trichée pour un plan se voit tout de suite dans la colonne jeu | Faible une fois la brique 1 faite | 7 |
| 7 | **Miroir de pose/anim** | 2 | Pour comparer une ref gauchère à notre droitier, ou comme regard neuf. **Testé : le miroir local `P·R·P` + échange Left/Right est exact sur R6 standard.** Ne pas oublier le HumanoidRootPart monde, la caméra et les effets | Très faible (10 lignes) | 5 |
| 8 | **Lignée de versions immuable** (v001→v002, `is_latest`, groupe) | 4 | Un index : version → vidéo, sha du rbxmx, note prédite, note et mots de Milan, commit. Nous avons déjà l'essentiel (`notes_milan.jsonl`, vidéos `-vN-`) ; il manque le lien vers les écarts mesurés (brique 3) | Faible | 5 |
| 9 | **Mélange de poses (nlerp aligné en signe)** | 2 | Aide à VOIR : afficher notre pose à 0, 50 et 100 % vers la pose mesurée d'une ref (`geo_pose`), au cadrage réel, pour voir ce qu'une « correction » change vraiment avant de poser une clé | Faible | 3 |
| 10 | **Grille d'aperçus animés** | 1 | Si on la fait : **des MP4 à vitesse réelle en mosaïque** (ffmpeg `xstack`), jamais leurs planches de sprites (images échantillonnées et plafonnées = pas la vitesse réelle) | Faible | 3 |

## 5. Ce qu'il faut INVERSER ou IGNORER

- **Inverser les statuts « Approved / Final / Needs Work »** (`config.py`
  l. 671-678). Chez nous, c'est un verdict gravé, que Claude se poserait à
  lui-même. Seul état admissible : « montré à Milan le …, sa note, ses
  mots ». Pas de « résolu » décidé par moi : une note de Milan se ferme
  quand **il** le dit, ou reste ouverte.
- **Inverser la direction de la revue.** Action Library suppose que le
  relecteur est un humain qui dessine et l'artiste un humain qui lit. Ici,
  le relecteur qui me manque, c'est moi à vitesse réelle. L'outil doit donc
  **me forcer à regarder la vidéo côte à côte avant de chiffrer ma
  prédiction**, puis garder la trace de ce que j'avais prédit de voir.
- **Ignorer** l'application PyQt6, la base SQLite, le socket
  Blender ↔ application, les thèmes, le nommage studio, les multi-utilisateurs,
  la mise à jour automatique et la corbeille : de la plomberie de studio, sans
  valeur pour nos yeux.
- **Ignorer** le playblast (`render.opengl` avec `view_context`) et le miroir
  par copier / « coller retourné » : il faut une fenêtre Blender. Notre
  moteur de rendu et nos Transforms font déjà mieux sans interface.
- **Ignorer** le repli de mélange par composantes (`socket_commands.py`
  l. 887 et suivantes) : les quaternions n'y sont pas renormalisés et les
  noms `Left/Right` sont absents.

## 6. Pièges

1. **Juxtaposer n'est pas comparer.** Action Library ne mesure rien. Mettre
   deux vidéos côte à côte donne l'impression d'avoir comparé : c'est
   exactement notre faiblesse 4 (surestimation) sous un autre habit.
   D'où la brique 3 : l'écart se chiffre **avant** de le décrire en mots.
2. **Synchro par numéro d'image = vérité seulement si la timeline est
   figée.** Vrai pour nos versions (contact à f146 partout), faux contre
   une ref et faux dès qu'une phase est retimée. Comparer une ref à f146
   avec nous à f146 serait une fausse comparaison, avec l'air objectif.
3. **« Synchronisé » ne veut pas dire « à vitesse réelle ».** Un QTimer sans
   horloge ni saut d'images peut ralentir sans prévenir, et il n'y a pas de
   son. Or Milan juge avec le son (le coup, le sol). Tout lecteur que nous
   écrivons cadence sur l'horloge et lit la piste audio.
4. **Une annotation d'une image ne se voit pas** (test B). Une preuve
   annotée qui n'est lisible qu'en pause ramène au défaut « planches figées ».
5. **fps par défaut silencieux.** Faute de métadonnées, leur export passe à
   24 im/s : notre scène dure alors 16,4 s au lieu de 13,1. Toujours lire le
   fps **dans la vidéo** et vérifier la durée de sortie (ffprobe).
6. **Un gros écart de pixels n'est ni un progrès ni un changement
   d'animation.** La mesure du test E compte aussi la caméra, les effets et
   le décor. Il faut un masque perso pour parler d'animation, et elle ne dit
   jamais « mieux ». C'est une mesure affichée, pas une porte.
7. **Le dessin, c'est une opinion.** Si je dessine « poing trop bas » sur
   une image, j'écris un verdict qui ressemble à une mesure. Les
   surimpressions doivent être **calculées** (hauteur du poing en studs par
   rapport à la poitrine) et étiquetées comme telles.
8. **Ancrer les mots de Milan à une image, c'est les interpréter.** Il faut
   garder la marque `mon_interpretation`, sinon on reproduit les « mots cités
   de mémoire » relevés par l'audit.
9. **Licence GPL-3.0.** Copier ne serait-ce qu'une fonction (même
   `_blend_quaternions`) imposerait la GPL au dépôt. On réécrit, en citant
   l'idée.
10. **Dépendance lourde et non installable ici.** PyQt6 n'est pas
    installable depuis ce conteneur aujourd'hui, et l'application est pensée
    pour Windows et une interface. Tout ce qui est utile se refait avec
    ffmpeg, numpy, cv2 et un lecteur HTML, **déjà présents**.

## 7. Ordre suggéré (si Milan le veut)

1. Brique 3 (écart mesuré entre versions) et brique 1 (côte à côte avec son,
   horloge réelle) : moins d'une heure à elles deux, l'une et l'autre testées
   ici en prototype.
2. Brique 2 (synchro sur événements) : indispensable dès qu'on compare à une
   ref.
3. Brique 6 (même clip, caméra jeu contre caméra ciné), qui s'appuie sur la
   brique 1.
4. Brique 4 (notes ancrées) et brique 5 (surimpressions calculées tenues).

Aucune de ces briques ne bloque rien : ce sont des mesures et des vues
affichées à côté de la vidéo, à regarder avant de prédire.

## Sources

- [CGstuff/Action-Library (GitHub)](https://github.com/CGstuff/Action-Library)
- [Action Library 1.3 (vidéo YouTube)](https://www.youtube.com/watch?v=X37LhQ6t_4I)
