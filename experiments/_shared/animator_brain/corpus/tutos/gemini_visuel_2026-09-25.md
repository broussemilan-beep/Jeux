# Description VISUELLE par Gemini de 3 tutos (2026-09-25), confrontée à mes études image par image

**Provenance.** Texte de Gemini, collé par Milan, en réponse au point 3 du
prompt (`recherche/VIDEOS_POUR_GEMINI.md`). Cette fois Gemini décrit l'image,
pas la parole.

**Occasion rare : je peux vérifier Gemini.** Deux des trois vidéos sont des
tutos que j'ai étudiés moi-même image par image :
- Charlotte (0vjAiAR-YFk) = l'uppercut Moon, `etude_complete_uppercut_moon.md` ;
- Nate.Animations (xkHILCmgbig) = le coup de poing Blender,
  `etude_complete_punch_blender.md` + `rapport_video_punch_blender.md`.

## 1. Charlotte, [OLD] How to animate R6 SMOOTHLY : vérification

| Gemini dit | Mon étude (image par image) | verdict |
|---|---|---|
| Studio + Moon Animator, cadrage fixe, R6 à faces marquées | oui (mannequin étiqueté FRONT/F/R/L/U) | ✓ |
| mannequin « gris avec carrés rouges, verts, bleus » | mannequin ROUGE étiqueté | ✗ détail faux |
| anticipation f0-10 : torse abaissé, penché en arrière et à gauche ; bras droit en arrière, bras gauche en garde | les 5 rôles (anticipation, drag, milieu, exagération, plus de drag) sont d'abord posés **sur le torse SEUL** ; les bras ne viennent qu'à 301 s | ~ générique ; **rate l'essentiel (le torse d'abord)** |
| coup f10-15, arc ascendant rapide du bras | le bras est vertical en UNE image vidéo (image 10) | ✓ en gros |
| follow-through f15-35 : les bras continuent puis reviennent ; départ lent, accélération, fin lente | pose d'après **tenue ~1 s** avec un wiggle qui s'amortit ; interpolation **Linear** (« key points of linear easing ») | ~ ; **rate le Linear et la pose tenue** |
| ghost rig (B), fantôme rouge | oui, texte à l'écran | ✓ (c'est écrit à l'écran) |
| — | pieds plantés vérifiés au fantôme ; tête en contre-rotation ; « ONLY use position to move the leg up and down » ; astuces de décalage de clés | **manqué** |

## 2. Nate.Animations, Expert Roblox Blender/Moon Punch : vérification

| Gemini dit | Mon étude | verdict |
|---|---|---|
| entièrement dans Blender, Action Editor, caméra qui tourne autour | oui (Moon Animator n'apparaît jamais ; carton « Punch tut: Made by myloe ») | ✓ |
| f0-20 : debout puis accroupi large (pré-anticipation) | clés 0, 20, 30… | ~ |
| armé f20-40 : torse pivoté à droite, **bras DROIT** loin derrière, **bras gauche TENDU en avant pour viser** | charge en « K » : bras armé loin derrière, bras avant **plié devant le visage** ; la timeline montre que le bras qui frappe est **UpperArm.L** (seul os avec une clé à 61) | ✗ **mauvais bras, mauvaise pose du bras avant** |
| frappe et suite f40-80 : pivote sur lui-même, se rattrape sur un pied, finit de dos | contact à **62** ; extension **1 image** ; pose de retour **tenue ~0,43 s**, corps plié en avant, **dos vers nous** | ~ « de dos » juste ; numéros d'image faux ; rate la tenue |
| espacement large à l'armé, très serré à la frappe | 30 → 60, 61, 62 | ✓ |
| — | charge **tenue 0,57 s**, extension **1 image**, 10 min de retouche des 3-4 mêmes poses, sous tous les angles | **manqué** |

## Calibration : ce que vaut une description visuelle de Gemini

- **Fiable** : l'outil et le cadre ; la grande forme du coup (gros armé,
  frappe très rapide, finir de dos) ; le principe d'espacement ; ce qui est
  écrit à l'écran.
- **Non fiable** :
  - quel bras ;
  - la forme exacte d'un membre (« tendu pour viser » au lieu de « plié ») ;
  - les numéros d'image (inventés : 10/15/35 et 20/40/80 alors que la
    timeline dit 30/60/61/62/90) ;
  - les couleurs.
- **Systématiquement manqué** : ce qui est TENU et combien de temps (charge
  0,57 s, extension 1 image, pose d'après), l'ORDRE de travail (torse
  d'abord), le type d'interpolation. C'est ce qui compte le plus pour nous.
- **Donc** :
  - une description visuelle de Gemini = une **carte** de la vidéo (où
    regarder, quoi chercher), jamais une mesure ;
  - ne jamais en tirer une pose ou un timing sans le voir ;
  - un chiffre d'image de Gemini ne vaut rien sans capture.

## 3. Sikasisi, How to Make Smooth Animations!! (TSB Skill Builder) : non vérifiable ici

Ce que Gemini décrit :
- **Outil.** Le TSB Skill Builder en jeu, avec une timeline flottante à
  calques (Layer 1, Layer 2…).
- **Démo.** Accroupi, puis backflip rapide.
- **Coup d'épée.**
  1. Dégainé : l'épée apparaît dans la main.
  2. Torse et bras droit reculés, lame vers le sol.
  3. Jambe gauche avancée brutalement, torse tordu, grand arc horizontal
     de droite à gauche.
- **Effets.**
  - Une traînée blanche sur la lame.
  - À l'impact, UN « Preset Mesh » : une énorme onde circulaire bleue et
    blanche autour du perso.
- **Résultat en ville.**
  1. Combo à l'épée fluide.
  2. Le mannequin est projeté en l'air.
  3. Téléport au-dessus de lui.
  4. Tempête de débris noirs cubiques qui détruit la route, flashs
     violets et blancs.

Lecture (avec la calibration ci-dessus : la grande forme est crédible, les
détails non) :
- **Calques** : rejoint le « layered » de doc7090 et les blocs invisibles
  de Tycoon. Chez TSB même, l'outil officiel pense en couches.
- **Effets** : une traînée + UNE forme forte à l'impact, cohérent avec son
  oral (« VFX simples, ne pas masquer l'animation ») et la hiérarchie des
  effets (`ETUDE_VISUELLE.md`, lot 2).
- **Enchaînement** : lancer en l'air -> téléport au-dessus -> frappe vers le
  bas, c'est la structure de notre partie aérienne. Pas de nouveauté de
  fond, une confirmation de forme.
