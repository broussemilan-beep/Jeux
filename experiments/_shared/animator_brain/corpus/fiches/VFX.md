# Fiche de conception : les VFX de combat (studio VFX)

**Ce qu'est cette fiche.** C'est la digestion de TOUT ce qu'on sait sur les
VFX avant d'ouvrir le chantier (demande de Milan, 2026-09-25 13:53 : « notre
propre studio de VFX qui viendra combler animation »). Ce sont des
apprentissages, pas des règles. On la lit avant de concevoir un effet.

**Sources digérées.**
- L'inventaire du dépôt : 51 fichiers qui parlent de VFX.
- Les 27 pistes de Milan, explorées en 5 groupes, code lu et cloné.
- Tout est dans `corpus/recherche/vfx_2026-09-25/`, avec le détail et les
  sources, marquées [CODE LU] / [README] / [PAGE] / [DÉDUIT].
- **Rappel** : `python3 outils/rappel.py vfx`.

---

## 1. Ce que Milan a validé, et ce qui est resté théorique

*Statut : retour de Milan pour ce qu'il a validé ; le reste est non établi (théorique).*

- **Validé** :
  - l'impact reste VISIBLE au moins 6 images avant tout effet plein écran
    (LECONS §3) ;
  - la caméra de jeu (v6), et la caméra ciné dosée à 70 % ;
  - l'aérien du Poing du Dragon, avec ses cartes, son blanc et son cratère,
    aimé depuis la v1.
- **Validé en partie** : des effets proportionnels au coup (hiérarchie en
  tiers, v6 : 6,8 → 7).
  - Mais au tier 1, les coups de base sont **invisibles en caméra de jeu**
    (question ouverte depuis la v6).
- **Jamais appliqué en Roblox** : smear graphique, ellipse de l'impact,
  signature visuelle (nos rubans « dragon » n'ont jamais été jugés, et je
  les trouve encombrants en v9), ralenti sur la conséquence, « hold and
  release » des débris, recoloration de la scène pendant la technique, son.
- **Retours de Milan sur des VFX ratés** :
  - le trou noir : « assez bof » ;
  - le coup de poing directionnel : « ton rendu est nul comparé à des
    animateurs experts » ;
  - Solar Smite : « 3/10 par rapport à la réf ».
  - Chaque fois, le rendu n'existait que dans le lecteur HTML, pas en
    Roblox.

## 2. Ce qu'un VFX de combat pro contient (sources croisées)

*Statut : mesuré (pack « 100 Combat VFX » : `corpus/vfx_100_combat_vfx_pack.json`) et lu (recherches du 2026-09-25).*

- **Une pile de couches qui naissent au même point** (un effet du pack
  « 100 Combat VFX » en compte en médiane 14 émetteurs pour 4 rôles) :
  - flash ≈ 0,1 s, grand ;
  - onde (anneau, dôme) ≈ 0,4 s ;
  - étincelles étirées dans le sens de la vitesse, ≈ 0,4 s, rapides, avec
    beaucoup de freinage (drag) ;
  - fumée ≈ 1 s ;
  - débris pour les coups lourds.
  - Chez nous : 3 émetteurs, soit « 5 à 7 fois moins dense et 3 fois trop
    petit ».
- **Une chronologie à l'image près** (robloxIA, à 60 i/s) :
  - hitstop de 2 à 6 images ;
  - flash ≤ 0,1 s ;
  - carte d'impact 1 à 2 images ;
  - flipbook des images 2 à 14 ;
  - caméra des images 3 à 20 ;
  - effets secondaires des images 4 à 30 ;
  - son avec 0,05-0,1 s de silence.
- **Des flipbooks** : la moitié des émetteurs du pack en ont. Chez nous,
  zéro.
- **La caméra et l'écran font partie du VFX** :
  - coup de zoom (+8° sur un coup léger, +15° sur un lourd) ;
  - secousse DIRECTIONNELLE, à graine fixe, en rotation (Rank Zero, Eiserloh) ;
  - Bloom et ColorCorrection animés dans le temps ;
  - cartes d'impact.
- **Le gel** : `TimeScale = 0` fige les particules pendant le hitstop. Le
  pack le fait (TimeScale 0,1 s) ; nous, jamais, alors que c'était promis
  dans la fiche du Dragon.

## 3. Les contraintes Roblox (doc officielle, lue hors ligne)

*Statut : lu (doc officielle Roblox, hors ligne).*

- `Rate` ≤ 400/s par émetteur, et 100/s sur mobile.
- `Lifetime` ≤ 20 s (Trail : de 0,01 à 20 s).
- Une `NumberSequence` ou une `ColorSequence` a **au plus 20 points**. Il
  faut compresser nos courbes (algorithme de VFX Editor, sous licence MIT).
- **Flipbook** :
  - grille 2x2, 4x4, 8x8, ou **Custom** (`FlipbookSizeX/Y`) ;
  - **texture de 1024², avec une marge transparente entre les images** ;
  - `FlipbookFramerate` ≤ 30 ;
  - en `OneShot`, les images sont réparties sur toute la durée de vie de la
    particule ;
  - les flipbooks sont **désactivés automatiquement sur les téléphones à
    court de mémoire** : il faut réutiliser les atlas.
- `Beam` : `Segments` ≥ n−1 pour n points de courbe, `FaceCamera`,
  `CurveSize` le long de l'axe X de l'Attachment. Beam et Trail n'ont pas de
  flipbook : on fait défiler la texture à la place.
- `LightInfluence` vaut **0** quand on crée l'effet par `Instance.new`, et 1
  quand on l'insère dans Studio : toujours le fixer à la main.
  `LightEmission` règle le mélange additif ; il n'éclaire pas la scène.
- **Highlight** :
  - le 1er coûte jusqu'à environ 1 ms de GPU sur mobile ;
  - **le créer ou le détruire provoque un pic** : il faut le pré-créer puis
    changer ses propriétés.
  - Notre `bodyFlash` le recrée à chaque coup : défaut à corriger.
- **Coût** :
  - c'est le remplissage (fill-rate) et le recouvrement (overdraw) qui
    coûtent : taille × couches × transparence ;
  - un appel de rendu par émetteur ;
  - budget d'environ 500 appels ;
  - les Parts semi-transparentes ne sont pas regroupées en un seul appel.
  - Aucun seuil officiel n'existe pour l'overdraw : **à mesurer nous-mêmes**.
- **Marqueurs** : `KeyframeMarker(Name, Value)` sous un `Keyframe`, reçus par
  `GetMarkerReachedSignal`. Notre exporteur peut les écrire directement. [CONTREDIT 2026-09-26 : ceci n'était connu que par le web, le chargeur ne lisait pas les KeyframeMarker ; le .rbxm TSB en a 35 réels, souvent sur des clés vides (pas le « hitreg » de M1) ; ceux du pack ne sont pas lus, présence inconnue, voir corpus/etude_c4/A2_tsb_stoic_collateral.md §6 point 1, corpus/etude_c4/A1_tsb_coups_courts.md V5, corpus/etude_c4/A4_pack_battleground.md §0]
- **Recette officielle d'explosion** : Drag 10, Lifetime 0,2-0,6, Speed
  20-40, Spread 180/180, `Emit(100)`.

## 4. Ce que les pistes nous donnent (verdicts, détails dans `recherche/`)

*Statut : lu (recherches du 2026-09-25, `recherche/`) ; un seul essai réel (flipbook Blender).*

| à adopter | à s'inspirer | à ignorer |
|---|---|---|
| doc officielle + dump de l'API hors ligne (agent-docs, creator-docs) : référence de vérité et générateur .rbxmx | **VFX Forge** : format déclaratif (instances + attributs + tags), chronologie implicite (`EmitDelay`, `EmitOnFinish`, `retime`), Beam animé, mesh à flipbook, ondes de choc, effet écran | RobloxForge (aucun VFX), Roblox Luau Scripting (débutant), ROBLOX Visual Effect System (pas de code), Particle UI Module (dépôt vide), Spark (plante au 1er appel) |
| convention d'attributs **`EmitCount` / `EmitDelay` / `EmitDuration`** (standard de fait : Forge, Qwinkle, Spark, le pack) | **Qwinkle** : un seul `EmitTree(racine) → durée`, post-processing animé dans le temps, échelle de temps / gel par arbre, débris précalculés et déterministes, imbrication | VfxFlipbookStudio (fermé) |
| pipeline flipbook **Blender Cycles CPU → planche 1024²** (essai réel : 16 images en ≈ 16 s, alpha propre) | Lumina et three.quarks : valeurs typées (constante / intervalle / courbe / dégradé) compilées vers Roblox ; matrice de parité ; lecture à pas fixe | |
| | VFX Editor : compression d'une courbe en 20 points (MIT) ; TARNATlON : Effect Play/Cancel (nettoyage si le coup est interrompu) ; Voxel : préréglages en tables Luau, budgets | |
| | GhibliGenerator (GPL) : recettes de nœuds cel à réécrire nous-mêmes ; **SMEAR** (CeCILL/GPL) : smears et lignes de mouvement, qui marchent sans interface (essai réel) | |
| | EvLightning + Lightning-Beams : notre propre générateur d'éclairs précalculés | |
| | robloxIA : la chronologie et les budgets d'un VFX de combat, script de flipbook Blender | |

**Licences** :
- **VFX Forge** (VFX-DL) : son module n'est autorisé QUE dans un jeu
  Roblox. Interdit dans un outil ou un harnais de test, et copyleft.
- **Qwinkle** : attribution obligatoire si le jeu est monétisé, pas de
  redistribution.
- GhibliGenerator, SMEAR : GPL.
- Sans licence : Voxel, OpenVFX, game-designer. On n'en reprend que les idées
  et les chiffres.

## 5. Le studio VFX qu'on assemble (proposition)

*Statut : non établi au moment de la fiche (proposition) ; construit ensuite dans `experiments/_shared/vfx_studio/`.*

1. **Recette** : un effet est une donnée (Python / JSON). Valeurs typées
   (constante, intervalle, courbe, dégradé), couches, rôles, chronologie en
   images et graine. On part des chiffres mesurés (pack, doc officielle,
   robloxIA), puis on les juge à l'œil.
2. **Compilation vers Roblox** : génération de Models `.rbxmx`.
   - Instances natives + attributs `EmitCount/EmitDelay/EmitDuration`.
   - Courbes compressées à 20 points.
   - Marqueurs écrits dans la KeyframeSequence.
   - Compatibles « VFX Forge » en option, si Milan choisit ce moteur.
3. **Moteur d'exécution** : notre propre module Luau, testé ici avec le
   binaire `luau`.
   - `EmitTree → durée`.
   - Gel pendant le hitstop (`TimeScale`).
   - Play/Cancel.
   - Highlight pré-créé.
   - Post-processing animé dans le temps.
   - Secousse directionnelle à graine fixe, avec le même générateur
     aléatoire côté Python et côté Luau.
4. **Textures** : un atelier Blender en ligne de commande (Cycles CPU).
   - Flipbooks 1024² avec marge : impact en étoile, croissant, fumée cel,
     anneau d'énergie, smear.
   - Catalogue au format `{asset, grille, résolution}`.
5. **Aperçu** : le lecteur three.js imite EXACTEMENT la sémantique Roblox
   (NumberSequence linéaire avec enveloppe, Drag en demi-vie, modes de
   flipbook), et rien de plus. Sinon, on juge un effet que Roblox ne saura
   pas faire.
6. **Critique VFX** :
   - validateur des limites officielles (Rate, 20 points, flipbook, Segments,
     Highlight, transparence partielle, appels de rendu estimés) ;
   - passe d'**overdraw** dans l'aperçu : % de l'écran couvert par au moins 4
     couches ;
   - puis l'œil, et la note de Milan.
7. **Le jour où Studio est ouvert chez Milan** : un MCP Studio ouvert (6xvl)
   permet d'importer le `.rbxm`, de le jouer, de capturer l'image à des
   instants gelés et de profiler.

## 6. Décisions qui reviennent à Milan

*Statut : non établi (décisions en attente de Milan au 2026-09-25).*

- **Moteur** : notre propre moteur (libre, testable ici, compatible avec la
  convention d'attributs), ou le module VFX Forge (plus riche, mais licence
  VFX-DL, impossible à tester ici). **Recommandé : le nôtre**, qui garde le
  format compatible.
- **Envoi des textures** : create.roblox.com est bloqué depuis le bac à
  sable. Trois options :
  - Milan télécharge nos planches et les envoie à la main ;
  - une clé Open Cloud mise dans les secrets de l'environnement ;
  - on reste sur l'aperçu seul.
- **Premier jalon** : refaire UN impact de bout en bout avec le nouveau
  pipeline (le coup final aérien du Poing du Dragon), jugé dans les deux
  caméras, plutôt que tout d'un coup.

## 7. Contradictions à trancher (relevées par l'inventaire)

*Statut : non établi (contradictions relevées, pas tranchées ici).*

- **Le Serious Punch a 3 versions des cartes** : « 3 planches d'1 image,
  blanc de 6 images » ; « 3 cartes de 4 images, blanc de 0,25 s » ; « 1 carte
  + 0,2-0,4 s ». L'analyseur mesure 1 carte de 267 ms. → À revoir image par
  image avant de refaire nos cartes.
- **« Finisher au p90 »** (staging.py) : les tailles réelles sont à la
  MÉDIANE du pack.
- **Secousse** : aléatoire, en translation, sans graine dans DragonFist,
  alors que la règle est directionnelle, en rotation, à graine fixe (Rank
  Zero, Eiserloh).
- **Hitstops** : aucune échelle commune entre projets (12-95 ms pour Rank
  Zero, 0,03-0,43 s pour le Dragon).
