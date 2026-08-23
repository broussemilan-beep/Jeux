# STATUS — Rank Zero (état réel, pas un historique)

Ce fichier n'existait pas avant le 2026-08-22 (MANDAT AUTONOME v3
Phase 4) — créé ici pour donner un état-des-lieux compact, à tenir à
jour à CHAQUE session plutôt que de laisser `docs/worklog.md` être la
seule source (un journal chronologique répond à "qu'est-ce qui s'est
passé", pas à "où en est-on maintenant"). Détail complet de tout ce qui
suit : `docs/worklog.md` (récent) et `docs/worklog-archive-*.md`
(archivé par période).

## Squelette gameplay

Player (`src/gameplay/player.gd`) : déplacement 8-directions, combo
léger 3 coups, dash, esquive (i-frames), critique probabiliste (5% base,
streak +3%/combo propre, plafond 40%, x1,5 dégâts). Ennemis (Crawler/
Brute/Ranged, `src/gameplay/enemy.gd`) : IA IDLE→CHASE→TELEGRAPH→
RECOVER, marche animée réelle (voir "Monstres" ci-dessous), boss
(`boss_gate_maw.tscn`) avec rotation de 4 attaques + enrage à seuil HP.
3 scènes de jeu : `gate_premiere` (parcours complet, salles Combat/
Elite/Rest/Boss), `test_arena` (bac à sable), `outpost` (hub, transition
vers gate_premiere).

## Système Pouvoir/déblocage

1 Pouvoir par run tiré au hasard (`RunState.active_power` ∈
{invocateur, monstrification, terre}). 5 compétences par Pouvoir,
débloquées par palier de niveau (1/3/6/10/15 par défaut, capstones
asymétriques pour Monstrification : 1/3/6/14/18). Slots `power1`..
`power5` génériques, résolus dynamiquement (tier = index de slot) via
`Player.get_power_slot_info()` — table `IMPLEMENTED_SKILL_HANDLERS`
= seule source de vérité sur ce qui a vraiment une fonction en code.

**Compétences réellement implémentées : 5 sur 15**
| Pouvoir | Tier | Compétence | Statut |
|---|---|---|---|
| Invocateur | 1 | Gueule Vide | ✅ |
| Invocateur | 2 | Corbeau Pâle | ❌ manquante |
| Invocateur | 3 | Poing du Colosse | ❌ manquante |
| Invocateur | 4 | Œil Sans Regard | ❌ manquante |
| Invocateur | 5 | Serpent Creux | ❌ manquante |
| Terre | 1 | Poing Tellurique | ✅ (retuning 2026-08-22 : bug de timing structurel corrigé — `groundRing` s'éteignait pile au moment du contact ; `dust_kick.gd` retuné 2026-08-23, cf. "Gaps de fidélité connus") |
| Terre | 2 | Marée de Sable | ✅ (2026-08-22, MANDAT AUTONOME v3 ; 2026-08-23 : `beamSegment` remplacé par `sandCrest`, une primitive VFX sprite-based réelle — plus un quad procédural plat, cf. "Gaps de fidélité connus") |
| Terre | 3 | Carapace | ❌ manquante |
| Terre | 4 | Effondrement | ❌ manquante |
| Terre | 5 | Fissure Éruptive | ❌ manquante |
| Monstrification | 1 | Poing Belluaire | ✅ (sprite dédié réel depuis 2026-08-22 : poing massif/rond, `create_character_state` sur le Cendre en jeu — remplace `coup3` en placeholder ; fragments VFX `converge.gd` corrigés le même jour) |
| Monstrification | 2 | Bras-Faux | ✅ (sprite dédié réel depuis 2026-08-22 ; 2026-08-23 : silhouette refaite en vraie courbe en C/crochet — Milan avait rejeté la 1ère version, "un bras en pointe bizarre" — vérifié frame par frame, cf. "Gaps de fidélité connus" ; tier corrigé le 22, `data/pouvoirs/monstrification.json` fait autorité) |
| Monstrification | 6 | Mâchoire | ❌ manquante |
| Monstrification | 14 | Forme Bestiale | ❌ manquante |
| Monstrification | 18 | Pattes de Chasse | ❌ manquante |

Les 11 manquantes ont chacune un sprite de référence archivé
(`docs/references/<pouvoir>/`) et un ordre de tier verrouillé
(`data/pouvoirs/<id>.json`) — méthode reproductible établie par Marée
de Sable (VFX recipe → gameplay → Targeting/mécanique générique si
besoin → smoke test dédié → capture réelle), aucun blocage technique
identifié pour continuer dans l'ordre.

## Monstres (Crawler/Brute/Ranged)

Rig : Crawler/Brute via armature manuelle Blender (l'auto-rig Meshy
échoue sur leurs postures non-standard) ; Ranged rigé directement par
Meshy (posture debout standard). Animations réelles : idle + attaque
(les 3) + marche (les 3, 2026-08-22) + mort (Ranged seulement). Crawler/
Brute n'ont pas encore de mort dédiée (`queue_free()` immédiat).

## Monde/décor

3 scènes avec parallaxe (`bg_ruin_arch`/`bg_pillar_silhouette`/
`bg_statue_silhouette`/`bg_tower_fragment`/`bg_banner_ruin`) + props de
sol variés (pilier/gravats/brasier/caisse/idole/torche/végétation/
poteau de bannière). Sol : `floor_terrain.tres` (vrai TerrainSet Wang)
sur les 3 scènes (uniformisé 2026-08-22, `test_arena` utilisait avant
un atlas plat sans raison).

## Pipeline outillage (tools/, experiments/, scripts/)

Génération pixel art : PixelLab (assets 2D directs, `create_map_object`
etc., journalisé `data/pixellab_usage.jsonl`). Monstres/personnage 3D→
pixel : Meshy (rig+remesh+texture, journalisé `data/meshy_usage.jsonl`)
→ Blender headless Cycles (`experiments/blender_capture/*.py`, rendu
pose-à-pose) → `quantize.py` (post-traitement pixel art) → SpriteFrames
Godot. VFX : moteur de recettes composables (`src/vfx/vfx_recipe_
registry.gd`, 15 primitives, `data/recipes/*.json`, `data/palettes/
*.json`). Tests : `scripts/run_gameplay_smoke_test.sh` (80 checks),
`scripts/run_vfx_recipe_smoke_test.sh`. Capture visuelle : `tools/
capture_scene.gd` (modes primitive/character/power/player_action/
player_action_sequence/scene), lancé via `scripts/capture_headless.sh`
(xvfb + Vulkan logiciel — `--headless` seul casse le rendu dans ce
sandbox, écart documenté dans `CLAUDE.md`).

## Bug transversal corrigé (2026-08-23, "MANDAT ROUND 2" Chantier 1)

`src/vfx/shaders/hit_flash.gdshader` : le flash blanc à l'impact
(`HitResponse.flash_sprite()`, appliqué à TOUTE cible touchée, tous
pouvoirs/combo confondus) restait épinglé à `flash_amount=1.0` (blanc
opaque plein, silhouette totalement effacée) pendant toute la durée du
hit-stop "medium" (~4 ticks, ~65ms) — un vrai bug de gameplay confirmé
sur un vrai monstre (Brute, pas seulement le Placeholder de capture),
pas un artefact d'outil. Root cause : la décroissance du flash est
gérée par une minuterie cosmétique qui reste sciemment gelée pendant
tout hit-stop (`CombatFeedback.is_frozen()`), et "medium" dure
quasiment le même nombre de ticks que le flash lui-même — la cible
restait donc "blanche" bien plus longtemps qu'un flash ne devrait.
Corrigé par un plafond `MAX_FLASH_MIX=0.6` sur la contribution du
mélange (jamais la cible ne disparaît entièrement sous un aplat, même
au pic/gelée) — effet positif secondaire : les chiffres de dégâts
(texte blanc) redeviennent lisibles pendant le flash. Preuve avant/
après : `captures/verification/2026-08-22-fix-hit-flash-round2.png`.

## Gaps de fidélité connus (mis à jour 2026-08-23, "MANDAT ROUND 2")

**Bras-Faux** : RÉSOLU. Milan avait rejeté la 1ère version ("un bras en
pointe bizarre", une tige droite) — refaite via un guide de silhouette
qui ancre explicitement une courbe en C par image (pas par texte
seul), vérifiée courbée sur les 6 frames sans exception. Capture :
`captures/verification/2026-08-22-fidelite-bras_faux-v2.png`.

**Poing Belluaire** : inchangé ce round (verdict "pas mal" de Milan,
aucune retouche demandée) — masse ronde/compacte, plus proche du corps
que la projection en diagonale de la planche.

**Gueule Vide** : composition en S toujours conforme (2e passe,
2026-08-22) + passe de détail ajoutée (2026-08-23) : crocs irréguliers,
gouttes d'encre à plusieurs points du tendon, légère texture de
surface — silhouette S vérifiée STRICTEMENT préservée (analyse en
composantes connexes + profil de largeur, après qu'un 1er essai ait
fusionné par erreur un élément de la planche dans le corps, intercepté
avant commit). Écart honnête restant : texture de mâchoire moins
organique que la référence, mares d'encre au sol plus petites. Capture :
`captures/verification/2026-08-23-fidelite-gueule_vide-v3.png`.

**Terre** : le gap "modeste" de Marée de Sable est résolu — `beamSegment`
(rangée de quads plats) remplacé par `sandCrest`, une vraie primitive
VFX sprite-based (PixelLab, teintée par la palette comme les autres
primitives) ; le nuage de poussière résiduel suit maintenant le trajet
de la vague (nouveau champ moteur optionnel `origin_offset_px` par
couche, défaut neutre, non-régression vérifiée sur les 4 autres
recettes). `dust_kick.gd` corrigé (même classe de bug que l'ancien
`converge.gd`). `ground_ring.gd` (Poing Tellurique) inspecté et jugé
suffisant, non retouché. Captures :
`captures/verification/2026-08-22-fidelite-maree_de_sable-v2.png` et
`-poing_tellurique-v2.png`.

**Combo de base** (coup1/coup2/coup3) : toujours visuellement quasi
interchangeable, aucune arme visible — non retouché (hors scope de
tous les mandats jusqu'ici), nouvelle génération d'assets nécessaire.

## Budgets (au 2026-08-23, fin "MANDAT ROUND 2")

PixelLab (compte réel, `mcp__pixellab__get_balance`) : 522/2000
générations consommées cumulées ce cycle (reset 2026-09-14), soit 1478
restantes — aucun plafond arbitraire appliqué (instruction explicite de
Milan). Round 2 : 73 générations consommées au total (chantiers 2/3/4,
mesuré sur le solde réel avant/après) — 3 agents ont tourné en
parallèle sur le même compte partagé, une répartition exacte par agent
n'est pas fiable à partir de leurs propres rapports individuels (deltas
qui se chevauchent), donc seul le total réel est retenu ici plutôt
qu'une ventilation inventée. Chantier 1 (fix `hit_flash.gdshader`) : 0
génération, recette/code uniquement. Meshy : 0 crédit consommé ce round
(aucun agent n'a eu besoin du fallback 3D).

## Prochaine priorité recommandée

Continuer Phase 3 (compétences) dans l'ordre verrouillé : Corbeau Pâle
(Invocateur, tier 2) ensuite — même méthode que Marée de Sable,
référence déjà archivée (`docs/references/invocateur/corbeau_pale.png`).
Le combo de base (coup1/coup2/coup3, visuellement interchangeable)
reste le seul gap de fidélité connu non planifié à ce jour.
