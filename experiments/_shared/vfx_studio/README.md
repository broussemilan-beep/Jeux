# Studio VFX (v1, 2026-09-25)

Demande de Milan : « créer le moteur dans cette direction artistique :
particules, meshes 3D, textures animées (UV scrolling), trails / beams,
bloom, séquençage ». Tout se crée ICI (aperçu fidèle à Roblox), puis se
transfère dans le jeu.

Conception : `../animator_brain/corpus/fiches/VFX.md` et
`../animator_brain/corpus/RELECTURE_REFS_VFX_2026-09-25.md`.

| pièce | fichier | état |
|---|---|---|
| formes cel (textures, flipbooks 1024² avec marge) | `formes.py` -> `textures/` + `catalogue.json` | 13 formes : croissant, éclat, étoile à 4 branches, anneau, flash, ligne de vitesse, bruit d'énergie qui défile, arc de vent, ruban, halo ; flipbooks fumée cel 2 tons, feu cel peint, flamme d'aura |
| meshes | `meshes.py` -> `meshes/*.obj` (Roblox) + `meshes.json` (aperçu) | dôme, sphère, anneau plat, tourbillon, croissant 3D, vague au sol, tore ; UV prévus pour le défilement |
| recettes (un effet = une donnée) | `recettes.py` | `orbe_impact` (apparition -> projection -> collision -> onde + explosion + vent + fumée), `impact_m1` (tier 1) |
| moteur d'aperçu (sémantique Roblox, déterministe) | `lab/moteur.js` | particules (Emit/Rate, NumberSequence avec enveloppe, Drag, orientations, flipbook, LightEmission, gel du hitstop), meshes à texture qui défile, Trail et Beam, projectile, bloom maison, flash d'écran, secousse directionnelle à graine fixe |
| lab (page jouable) | `build_lab.py` -> `lab/studio_vfx.html` | choix de la recette, lecture / pause / curseur, ×1 ×0,25 ×0,1, caméras, bloom |
| compilation Roblox | `compile_roblox.py` -> `luau/VFXRecettes.luau` | séquences ramenées de 0 à 1 et compressées à 20 points (Ramer-Douglas-Peucker), couleurs 0-1, table des assets ; ce qui n'a pas encore de rbxassetid est listé comme MANQUANT (repli : texture intégrée à Roblox) |
| moteur d'exécution Roblox | `luau/VFXStudio.luau` | joue une recette compilée : ParticleEmitter (LightInfluence 0 explicite, Sphere/Disc, aspiration = ShapeInOut Inward), Part + SpecialMesh (FileMesh), Trail, Beam, projectile, BloomEffect animé, flash d'écran, secousse (même générateur que l'aperçu), gel (TimeScale 0), Sound ; une seule boucle pilotée par le temps ; `Annuler()` nettoie tout |
| test du moteur Roblox | `luau/run_test.py` (+ `test_vfxstudio.luau`, `references_apercu.js`) | interpréteur Luau officiel + faux objets Roblox qui REFUSENT ce que Roblox refuse ; compare secousse, bloom et flash aux valeurs calculées par le vrai `moteur.js` ; 25 contrôles |
| critique VFX (limites officielles + coût) | `critique.py` | Rate, Lifetime, séquences, flipbooks, Trail, Beam, particules vivantes instant par instant, appels de rendu estimés, défilement sans variantes |
| son (SFX) | `sons.py` -> `sons/*.wav` + `catalogue.json` | 8 sons synthétisés (numpy, graine fixe), les MÊMES WAV dans le labo (WebAudio, bouton « Son ») et dans Roblox (Sound, préchargé, joué à t0) ; `impact_lourd` réglé sur les mesures des refs (`../animator_brain/corpus/ECOUTE_REFS_SFX_2026-09-25.md`) ; `critique_son` vérifie le vide avant chaque impact |
| vidéo avec son | `video_recette.py` | images du labo + mixage des sons -> MP4 (option ralenti) |
| capture du labo | `capture_lab.js` | planche d'instants choisis (preuves, auto-évaluation) |

**Correspondance avec Roblox.**
- Particules → `ParticleEmitter`.
- Mesh → `Part` + `SpecialMesh` (FileMesh) : contrairement à un MeshPart,
  MeshId, TextureId, Scale et VertexColor y sont modifiables en jeu (doc
  officielle). Le défilement de texture n'existe pas nativement sur un
  mesh : `formes.py` écrit 8 copies décalées de 1/8 en U
  (`bruit_energie_d0..7`), et le moteur échange `TextureId`. L'aperçu
  quantifie son défilement au même pas, en U seulement : ce qu'on voit dans
  le labo est ce que Roblox fera. Sur un `Beam` / `Trail`, le défilement
  est natif (`TextureSpeed`). Le rendu additif d'un mesh (Neon ?) reste
  [À VÉRIFIER dans Studio].
- Trail / Beam → `Trail` / `Beam`.
- Bloom → `BloomEffect` animé.
- Gel → `TimeScale = 0`.

**Défauts trouvés en regardant (et corrigés).**
- Croissant et arc de vent sortaient du cadre.
- Le bruit d'énergie faisait des taches.
- L'ombre de la fumée était à l'envers.
- La flamme d'aura était un rectangle.
- Les effets de l'impact s'affichaient avant la collision (bug du gel).
- Carrés noirs du bloom (cibles en demi-flottant sous le rendu logiciel →
  8 bits).
- Orbe invisible (filaments sans cœur).
- Traînée en pointillés.
- L'anneau au sol faisait une assiette opaque.

Preuve : `captures/verification/2026-09-25-studio-vfx-v1-formes-orbe-impact-m1.png`.


## VFX dessinés (2026-09-25)

Idée de Milan : les VFX qui complètent les animations « ont l'air
dessinés » parce qu'ils passent par des meshes 3D. Dans le studio :
- `dessins.py` : textures peintes à bord net, en séries de 8 images qui
  s'érodent (`trait`, `lame`, en gris à teinter ou peintes `feu` / `bleu`),
  et encre noire (`griffure`, `veines`) ;
- `meshes.py` : `ruban_spirale`, `arc_trait`, `lame_plate` (deux plans en
  X) : la forme du trait vient de la texture ;
- couche mesh : `cadence` (i/s, « en 2 » = 12 : la pose saute d'un pas à
  l'autre) et `images` + `images_de` (la texture change image par image ;
  Roblox : TextureId) ; même calcul dans l'aperçu et dans VFXStudio.luau
  (banc : 4 contrôles « dessiné ») ;
- recettes `dessin_tornade` (réf. 0f85f7a1) et `dessin_jaillissements`
  (réf. 8005ceb1).
Limite connue : dans Roblox, une texture changée pour la 1re fois peut
clignoter le temps de se charger : précharger les images (ContentProvider)
avant la technique.

## v13 (2026-09-25) : dragon d'or DESSINÉ, mâchoire, rayons

Demande de Milan : « VFX de qualité dessin, pas du cube ou cartoon » ;
« le dragon or… le coup se transforme en le dragon qui mange le perso ».

- **Dragon d'or dessiné** (`modeles/dragon.py`) : plus de dégradés peints
  en volume (v12 : une statue) ; aplats francs deux tons, écailles en TRAIT
  d'encre (festons en U), plaques de ventre cernées, arête dorsale, yeux
  CYAN (accent complémentaire, Dragon Ball Rage). Aperçu : matériau non
  éclairé + ombre cel légère + liseré de contre-jour ; contour d'encre
  proportionnel à l'échelle. Roblox : les deux tons sont dans la texture,
  contour = Highlight.
- **Mâchoire animable** : os `Machoire` (charnière au fond de la gueule,
  repos 20°), piloté par `machoire` = [[a, degrés], …] dans une couche
  serpent (`recettes.serpent(machoire=…)`) ; aperçu et `VFXStudio.luau`
  font le même calcul (repère de la tête x charnière x rotation Z). Test
  Luau : la charnière reste sur la tête, l'ouverture = angle - repos.
  Mâchoire du bas raccourcie, menton qui remonte (vue ouverte de face :
  c'était une planche rouge).
- **Recette `dragon_gueule_demo`** : le dragon face caméra, gueule
  ouverte ; sert de modèle à la carte manga (`r6_poing_dragon/scripts/
  build_planches.py`).
- **Recette `dragon_silhouette_demo`** (v13c) : le dragon qui plonge, de
  profil, sur le ciel seul ; sa silhouette est celle de la planche
  « soleil ».
- **Dragon 3D en Luau : fondu et partie visible** (v13c) : `VFXStudio.luau`
  respecte maintenant `transparency` et `tete_visible`/`queue_visible`
  comme l'aperçu (il restait opaque en jeu) ; test dans `test_vfxstudio.luau`.
- **Beams : fondu dans le temps** (`transparency_temps`) désormais joué
  aussi par `VFXStudio.luau` (NumberSequence recalculée à chaque image).
- **Impacts de rafale** : un trait de pinceau en arc (mesh `arc_trait`,
  images `trait_feu`, en 2) autour de l'axe du coup.
