# Angles morts : ce qui manquait dans la direction et le développement

Prise de recul du 2026-09-24, à la demande de Milan : « pose-toi et vois si,
dans le développement ou la direction, il ne manque pas des choses évidentes
ou non, car c'est déjà arrivé sur la traduction que tu avais faite du
cerveau ».

Méthode : relire chaque retour de Milan contre ce qui a été *mesuré*, pas
contre ce que j'ai *cru* corriger. Classement par impact probable sur la note.

## 1. Quel « coup final » ? Le plus gros angle mort

**Constat.** Trois versions (v3, v3b, v4) ont corrigé les **4 coups de la
rafale** (f14, 40, 64, 90). Juste après, à **f150**, il y a l'**uppercut
lanceur** : aucune règle, aucune mesure ni aucune version ne l'a jamais
regardé. Or il colle mot pour mot aux retours de Milan.

| retour de Milan | ce que montre la mesure à f125-156 (v4) |
|---|---|
| v1/v2 : « il est accroupi » | de f125 à f146, torse à 1,37-1,54 stud (debout ≈ 3) : ramassé en boule pendant 0,35 s, plus bas qu'à aucun coup de la rafale |
| v3b : « le coup final : un enchaînement d'uppercut et de coup droit » | fente en coup droit à f90, puis uppercut à f150 : c'est littéralement notre montage |
| v4 : « au coup final, le coup part toujours d'en bas » | à f150-156, le poing monte de **4 studs** (1,5 → 5,9), de la hanche au-dessus de la tête |

Preuve :
`captures/verification/2026-09-24-poing-dragon-v4-uppercut-f150-vu-de-profil.png`.

**Pourquoi c'est arrivé.** J'ai traduit « coup final » par « dernier coup de
la rafale », parce que c'est la liste `hits` que mes règles parcourent. Le
cerveau ne voit que ce que ses règles regardent.

**À confirmer par Milan** (question d'une seconde) : le « coup final »,
est-ce la fente du 4e coup (f90), ou le coup de poing juste avant qu'il
décolle (f150) ? Si c'est f150, la piste Saitama prend tout son sens :
remplacer l'uppercut qui sort d'une boule par un coup chargé, buste qui
tourne, qui part droit.

**Correction de méthode.**
- Chaque retour est reformulé en **moment précis + partie du corps**, et
  confirmé avant d'agir.
- Le lecteur doit afficher le numéro de frame et le nom du temps (rafale,
  lanceur, envol, plongée…) pour que Milan puisse dire « à f150 ».
- Le cerveau mesure **tous** les temps d'une technique, pas seulement ceux
  qu'une règle liste.

## 2. La fluidité : le défaut mesuré qu'aucune règle ne voyait

> **Correction du même jour (v5).** La mesure ci-dessous est faussée par le
> tempo de la rafale. En 3D, notre rafale n'est jamais figée. Les poignées
> AUTO, essayées, haussaient l'épaule. La mesure est retirée du jugement :
> voir `CERVEAU_V2.md`. Le texte ci-dessous est gardé comme trace du
> raisonnement.

Nos coups s'arrêtent à chaque pose clé :

| quoi | traits par seconde de mouvement |
|---|---|
| rafale et final | 7,5 à 11,9 |
| M1 pro | 4,2 à 5,7 |
| notre aérien, que Milan aime | 3,5 à 4,2 |

C'est la seule hypothèse qui sépare ce que Milan aime de ce qu'il rejette
(`CERVEAU_V2.md`).

**Cause technique probable**, trouvée en lisant le code mais **pas encore
testée** : les clés sont en BEZIER avec les poignées par défaut de Blender
(AUTO_CLAMPED). Elles aplatissent la tangente à chaque clé où un canal
change de sens, donc le membre s'arrête. C'est ce qui donne le côté
robotique.

**Variante à tester** (pas de réglage à la main, le critique juge) :
- poignées AUTO non bridées, ou interpolation passant par les clés
  (Catmull-Rom) ;
- clés décalées de 1 à 2 f entre les membres (chevauchement).

Perception mesure la différence en secondes.

## 3. Jamais vu dans Roblox Studio

Milan juge le lecteur HTML. Dans le vrai moteur, on ne connaît rien : ni
l'interpolation de l'Animator, ni la caméra, ni les VFX, ni le rendu R6.
Un test de 5 minutes avec `PoingDuDragon.rbxmx` dirait si la note porte sur
l'animation ou sur l'aperçu.

**Trouvé le 2026-09-24 (doc officielle Roblox, `PoseEasingStyle.yaml`).**
Tous nos exports écrivaient `EasingStyle = 1` en le croyant « Linear ». Or
1 = **Constant** (0 = Linear). En jeu, chaque pose restait figée jusqu'à la
clé suivante puis sautait. Le Poing du Dragon a des trous de 8 à 12 f dans
l'aérien et de 36 f à la fin : il aurait saccadé dans Studio, alors que le
lecteur HTML (qui interpole toujours en linéaire) ne pouvait pas le montrer.
- **Corrigé** : 11 exporteurs, 30 fichiers `.rbxmx`.
- **Garde-fou** : `verify_export.py` échoue désormais si une pose n'est pas en
  Linear.
- **Leçon** : un test qui relit nos propres fichiers avec notre propre
  hypothèse ne prouve rien sur le moteur. Toute propriété écrite pour Roblox
  se vérifie contre la doc officielle.

## 4. Les notes ne suffisent pas à apprendre

- Il y a 3 notes pour 15 hypothèses : le problème est sous-déterminé, et la
  note mélange animation, caméra, VFX et rythme.
- **Choix entre variantes** : A, B ou C sur un temps précis. C'est 10 fois
  plus d'information par minute de Milan, et ça vise une seule question.
- **Verdict par partie** (aérien +, rafale −, final −) : ajouté aujourd'hui,
  il a immédiatement désigné la fluidité.

## 5. Le style visé n'était écrit nulle part

Le corpus 3D, ce sont 19 animations d'un seul pack, avec des M1 réalistes.
Les règles « bras horizontal », « poing à plat » et « transfert de poids »
ont jugé un final qui vise le manga ultime. Chaque hypothèse a maintenant un
`etalon_style` et chaque partie un `style_cible` (`productions.json`), et le
critique alerte en cas d'écart. Il reste un manque : aucun étalon 3D
« manga ultime ». Il viendra des références vidéo ou d'un pack TSB ultime.

## 6. Il manque le niveau « intention »

Aucun document ne dit ce que chaque temps doit **faire ressentir** :
- la rafale = pression qui monte ;
- le lanceur = rupture ;
- le final = énorme, et le spectateur doit le sentir venir.

Sans intention écrite, j'optimise des mesures. Première ligne de chaque
production : une phrase d'intention par temps, validée par Milan.

## 7. Toute mesure doit passer un test sur une vérité connue

Test du jour avec le flux optique (`clip_analyzer`, bloc `mouvement`) :

- **Direction des pics (« le coup monte-t-il ? ») : validée.** Sur la
  rafale seule, les versions dont on connaît la vérité se rangent bien :

  | version | ce qu'on sait | part des pics qui montent |
  |---|---|---|
  | v1 | uppercut au menton | 0,46 |
  | v3b | coups partis du bas | 0,39 |
  | v2 | coups à plat | 0,15 |
  | v4 | coups à plat | 0,15 |

- **Arrêts par seconde en 2D : non validés.** Ils contredisent la mesure 3D,
  car la caméra, les VFX et l'interface des captures d'écran dominent. On
  ne s'en sert pas pour juger.

Règle : aucune nouvelle mesure n'entre dans le critique sans avoir passé ce
genre de test.

## 7b. Les poids appris ne l'étaient pas

`critic.reflect` ré-appliquait ses mises à jour à chaque lancement, donc les
poids dérivaient avec le nombre de lancements. C'est corrigé : il rejoue
l'historique depuis `poids_a_priori`.

## 8. Ce que le cerveau ne sait pas encore voir

- **Silhouette** : jamais mesurée. On pourrait la mesurer par le rendu du
  masque et la surface des membres détachés du corps.
- **Caméra, VFX, rythme de la scène** : Milan les note, mais aucune
  hypothèse ne les porte.
- **Mocap de boxe réelle** comme base à exagérer (CMU, anim2rbx) : bloquée
  par le réseau.

## Ordre proposé

1. Milan confirme le « coup final » (f90 ou f150) et donne une phrase
   d'intention par temps.
2. Variantes de fluidité (poignées, chevauchement) : jugées par la
   perception, puis montrées en A/B à Milan.
3. Final à la Saitama en 3 variantes, sur le bon temps.
4. Test dans Roblox Studio, dès que possible.
