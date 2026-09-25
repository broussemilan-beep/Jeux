# Tutos VFX à faire télécharger à Milan (2026-09-25)

Demande de Milan après la v12 (VFX 2 à 4/10) : « chercher des vidéos tuto
VFX que je compresserai comme hier ». Classées par utilité pour NOTRE écart
(effets construits maigres face au pack 100 Combat VFX et aux refs). Les
textes (DevForum, doc Roblox) je les lis moi-même ; seules les vidéos
passent par Milan.

## Priorité 1 : Roblox, style anime / battlegrounds (ce qu'on doit égaler)

| # | vidéo | pourquoi |
|---|---|---|
| 1 | Pew, Serious Punch recréé (vitrine) https://www.youtube.com/watch?v=lvB-wTylH3Y | le coup chargé de notre technique ; même artiste que la série DevForum (flipbooks de meshes, caméra animée) |
| 2 | Serious Punch VFX, Roblox Studio https://www.youtube.com/watch?v=fCSIWG87uFs | 2e lecture du même coup : comparer les couches |
| 3 | Stylized Explosion VFX Tutorial, Roblox Studio (2026) https://www.youtube.com/watch?v=J8uIGox3xfU | notre explosion est « maigre » (Stagnant Rage) |
| 4 | How to Make Slash VFX, Roblox Studio https://www.youtube.com/watch?v=zlKdwujvP2A | beam + mesh + script : les traînées de coups |
| 5 | Roblox Flipbook Particles Are Extremely Powerful https://www.youtube.com/watch?v=TdU0A8etl1o | nos flipbooks (feu, fumée) sont peu nombreux |
| 6 | Roblox Beams Can Make Amazing VFX https://www.youtube.com/watch?v=yK_BSF3p8sk | beams empilés = faux mesh qui défile (Pew, partie 4) |
| 7 | Beam VFX Kamehameha, textures After Effects + Photoshop https://www.youtube.com/watch?v=tWraodzRuZk | comment les pros PEIGNENT leurs textures |
| 8 | HOW TO Make Anime Particles in Roblox Studio https://www.youtube.com/watch?v=2OdX2k9jFY8 | lueur anime des particules |

## Priorité 2 : textures et explosions anime (Blender)

| # | vidéo | pourquoi |
|---|---|---|
| 9 | Anime Blast & Explosion VFX in Blender, partie 1 https://www.youtube.com/watch?v=AcNz0qPPR7U | explosion cel en volume (on a Blender ici) |
| 10 | idem, partie 2 https://www.youtube.com/watch?v=Hqek7M5gV88 | |
| 11 | Blender, Anime Style FX Workflow https://www.youtube.com/watch?v=fE-uDqBpXxI | chaîne complète d'un effet anime |
| 12 | Anime style Smoke & Explosion FX https://www.youtube.com/watch?v=eL6O3qN-d4E | fumée cel (la nôtre est simple) |
| 13 | Roblox Flipbook, One Shot Dissipate https://www.youtube.com/watch?v=84TSgTcCC0g | dissolution d'un flipbook |

## Priorité 3 : outillage

| # | vidéo | pourquoi |
|---|---|---|
| 14 | 2025 Roblox VFX Setup, plugins et astuces https://www.youtube.com/watch?v=9dQR7FySSLg | les plugins des VFX artists |
| 15 | 2025 Roblox VFX Scripting, moins de 10 min https://www.youtube.com/watch?v=XXCGWREKpo0 | comment ils déclenchent (modules) |

## Textes que je lis moi-même (pas besoin de Milan)

- Série DevForum de Pew (artiste VFX, effets inspirés de TSB) :
  partie 1 Stoic Bomb https://devforum.roblox.com/t/stoic-bomb-vfx-recreation-and-personal-workflow-overview/3608056 ;
  partie 2 VFX physiques https://devforum.roblox.com/t/physics-based-vfx-creation-overview-part-2/3617845 ;
  partie 3 Serious Punch https://devforum.roblox.com/t/serious-punch-recreation-creation-overview-part-3/3630207 ;
  partie 4 RUNUP https://devforum.roblox.com/t/runup-vfx-breakdown-part-4/3669430
- Full Beginner's Guide on scripting Anime/Fighting VFX https://devforum.roblox.com/t/full-beginners-guide-on-scripting-animefighting-vfxvisual-effects-part-1/1610853
- Introduction to VFX: Particles https://devforum.roblox.com/t/introduction-to-vfx-particles/2068650
- Doc Roblox, explosions https://create.roblox.com/docs/tutorials/use-case-tutorials/vfx/use-particles-for-explosions

## Déjà appris des textes de Pew (lus le 2026-09-25)

- **Flipbooks de MESHES** : découper une planche en images séparées et
  changer `TextureID` du mesh à chaque image (dossier de decals préchargés
  pour éviter le clignotement). Notre moteur le fait déjà pour le défilement
  (8 variantes) : même mécanisme, à étendre aux animations peintes.
- **Beams empilés** = illusion d'un mesh 3D avec texture qui défile.
- Impact : sphère de DISTORSION (Glass, transparence > 1), anneaux animés
  entre deux clones « Start » / « End », débris en module de roches.
- Caméra de cinématique : une Part animée avec les rigs dans le même export,
  `camera.CFrame = CameraPart.CFrame` à chaque image ; couper `AutoRotate`
  pendant la cinématique (sinon le shift-lock fait tourner).
