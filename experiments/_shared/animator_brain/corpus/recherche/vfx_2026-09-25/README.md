# Exploration des 27 pistes VFX de Milan (2026-09-25)

La synthèse est dans `../../fiches/VFX.md`. Ce dossier garde les rapports
complets.
- **Méthode** : 5 recherches parallèles, chacune sur une famille de pistes,
  plus un inventaire de ce que le dépôt savait déjà. Les dépôts ont été
  clonés et le code lu.
- **Marquage** : [CODE LU] / [README] / [PAGE] / [DÉDUIT] / [NON TROUVÉ].
- **Vérifications** : j'ai contrôlé les points clés de chaque rapport dans le
  code ou dans la doc. Par exemple : la licence VFX-DL, `EmitDelay` et
  `EmitOnFinish` dans forge-vfx, les valeurs par défaut de Beam et
  ParticleEmitter dans le dump de l'API, les limites 400/100 dans la doc, le
  Highlight recréé à chaque coup dans DragonFist.luau, le bug de Spark, la
  licence de Qwinkle.
- Les liens d'origine de Milan étaient perdus ; les dépôts ont été retrouvés
  par leur nom.

| # | piste | rapport | verdict |
|---|---|---|---|
| 1 | VFX Editor (VirtualButFake, MIT) | 01 | s'inspirer (compression d'une courbe en 20 points) |
| 2 | VFX Forge (zilibobi, module VFX-DL + plugin payant fermé) | 01 | ADOPTER le format ; le module, seulement si Milan accepte la licence |
| 3 | VFX Forge MCP | 01 | dépôt introuvable (404) ; idée seulement |
| 14 | RobloxForge (ShugokiFable) | 01 | ignorer (aucun VFX). Pour plus tard : MCP 6xvl (capture, import rbxm) |
| 4 | Lumina | 02 | s'inspirer (graphe → génération de Luau) |
| 5 | Qwinkle's Part-Icles 2 | 02 | s'inspirer fortement (EmitTree, post-processing, gel, débris) |
| 6 | Voxel Particles | 02 | s'inspirer (préréglages Luau, budgets) |
| 7 | OpenVFX | 02 | s'inspirer (format de catalogue de flipbooks) |
| 8 | Spark | 02 | convention d'attributs seulement (le code plante) |
| 9 | TARNATlON roblox-vfx | 02 | s'inspirer (Effect Play/Cancel) |
| 10 | ROBLOX Visual Effect System | 02 | ignorer (pas de code) |
| 11 | Lightning-Beams | 03 | s'inspirer (algorithme, à porter) |
| 12 | EvLightning | 03 | s'inspirer (format des segments, fourches) |
| 13 | Particle UI Module | 03 | ignorer (dépôt vide) |
| 19 | Roblox Luau Scripting | 03 | ignorer |
| 27 | roblox-dev-notes | 03 | s'inspirer : 19 règles de performance sourcées (tableau P1-P19) |
| 15 | Roblox Skill for AI — VFX | 04 | s'inspirer (valeurs par défaut sondées) |
| 16 | roblox-suite — VFX Skill | 04 | s'inspirer (flipbooks, marqueurs ; `EffectBurst` en MIT) |
| 17 | game-designer — VFX Guide | 04 | s'inspirer (recettes chiffrées, beaucoup de défauts faux) |
| 18 | Do Big Studios Agent Docs | 04 | ADOPTER : doc officielle + dump de l'API hors ligne |
| — | robloxIA (hors liste) | 04 | s'inspirer (chronologie et budgets d'un VFX de combat) |
| 20 | GhibliGenerator (GPL) | 05 | s'inspirer (recettes de nœuds ; essai réel après une rustine d'une ligne) |
| 21 | SMEAR (CeCILL/GPL) | 05 | s'inspirer (marche sans interface, essai réel) |
| 22 | Flipbook (packer nezuo, MIT) | 05 | s'inspirer (règles de grille, à refaire en Python) |
| 23 | Babylon / three.quarks | 05 | s'inspirer (valeurs typées, matrice de parité, lecture à pas fixe) |
| 24-26 | Roblox Creator Docs (effects, curriculum, Weapons Kit) | 05 | ADOPTER comme référence normative |

**Preuve de l'essai de flipbook** :
`captures/verification/2026-09-25-vfx-essai-flipbook-blender-cycles-explosion-anneau.png`.
- Planches 4x4 de 1024², rendues par Cycles CPU en ligne de commande avec
  bpy 5.0.1. EEVEE ne marche pas ici (pas de libEGL).
- Le pipeline fonctionne. En revanche, l'explosion brute est une tache jaune
  plate : il faudra de la direction artistique.
