# Quand notre studio freine la qualité, et ce que Roblox Studio changerait (2026-09-26)

Question de Milan (après le 8/10 de la v13e) : « quand est-ce que notre
studio est un frein dans la qualité ? Est-ce que le passage sur Studio va
t'aider ? Vu que tu auras accès au plugin, à mes stocks de VFX, et que tu
pourras littéralement suivre un tuto de A à Z ? »

Sources : notes de Milan (`notes_milan.jsonl`), `RETOURS.md`, et la
recherche `vfx_2026-09-25/01_editeurs_moteurs_mcp.md` (MCP Studio, VFX
Forge, capture d'écran, licences).

## 1. Là où notre studio EST le frein (preuves)

| frein | preuve | ce que Studio change |
|---|---|---|
| **Les images des VFX** (textures, flipbooks, meshes) sont générées par programme (PIL, loft Python) | VFX notés 2-4 en v12 ; « cartoon », « cube », « trop peinture, pas dessiné », yeux et tête du dragon refaits deux fois | les stocks VFX de Milan (flipbooks et meshes faits par des artistes) s'utilisent directement ; c'est le plus gros gain |
| **Le rendu** : je juge dans une imitation three.js (logiciel, sans GPU), pas dans le moteur Roblox (Neon, bloom, éclairage Future, post-effets) | bug r128 : le dragon figé chez Milan, invisible dans toutes mes captures (CARNET 4b.28) | on voit le VRAI rendu ; plus d'écart aperçu / jeu |
| **La vitesse d'itération** | une vidéo = ~25 min de rendu logiciel ; une passe de corrections = 1-2 h | playtest immédiat |
| **Suivre un tuto** : je traduis chaque étape dans notre format de recettes (perte) | les tutos VFX étudiés servent de principes, jamais refaits à l'identique | on refait les étapes à l'identique, avec les mêmes objets Roblox |

## 2. Là où il N'EST PAS le frein

- **L'animation du perso** (7,7 puis 8) : rig V2.22, KeyframeSequences
  exportées et vérifiées au centième de stud ; Studio n'apporte rien ici
  (sauf voir le rendu final).
- **Le rythme, le découpage, la caméra, le goût** : les retours récents
  (dragon « dans tous les sens », plans hachés, dragon invisible au bon
  moment) sont des décisions de mise en scène. Studio ne les corrige pas ;
  le cerveau (fiches, allure, juge, relecture à 0,1 s) oui.
- **La mémoire et la preuve** : tout est versionné, mesurable et testable
  ici ; à garder quoi qu'il arrive.

## 3. Ce que Studio apporte vraiment, et à quelles conditions

1. **Il faut que je VOIE.** Le MCP Studio le plus complet étudié (6xvl,
   MIT) a `capture_screenshot`, mais seulement en mode Edit, viewport
   visible, ≥ 0,1 s par capture : impossible de filmer image par image un
   effet d'une seconde. Il faudra un mode « scrub(t) » déterministe (poser
   la scène à l'instant t, puis photographier) : c'est déjà l'architecture
   de nos lecteurs (seek), à porter dans le Luau.
2. **Claude Code doit tourner sur le PC de Milan**, avec Studio ouvert et le
   plugin MCP : la session dans le cloud ne peut pas joindre son
   `localhost`.
3. **Les plugins à interface (Moon Animator, éditeurs VFX) ne se pilotent
   pas au clic.** Je peux lire et écrire ce qu'ils produisent (instances,
   propriétés, attributs, KeyframeSequences) et exécuter du Luau ; donc
   « suivre un tuto de A à Z » = refaire chaque étape par l'API, en
   vérifiant par capture ; pas cliquer dans leur fenêtre.
4. **Licences** : les packs VFX achetés ne vont jamais dans le dépôt
   (seulement un catalogue dérivé : noms, rôle, paramètres). VFX Forge :
   licence VFX-DL restrictive (pas de harnais de test).

## 4. Recommandation

Hybride : le cerveau et le labo restent le lieu où l'on CONÇOIT et MESURE
(fiches, rappel, allure, juge, bandes 0,1 s, preuves committées) ; Studio
devient le lieu où l'on ASSEMBLE avec les vrais assets et où l'on JUGE le
rendu final. Premier chantier Studio : cataloguer les stocks VFX de Milan
(ce qui existe, pour quel moment : impact, aura, éclair, sol…) avant de
produire, comme on l'a fait pour ses refs.
