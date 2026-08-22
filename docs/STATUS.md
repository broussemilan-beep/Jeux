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
| Terre | 1 | Poing Tellurique | ✅ |
| Terre | 2 | Marée de Sable | ✅ (2026-08-22, MANDAT AUTONOME v3) |
| Terre | 3 | Carapace | ❌ manquante |
| Terre | 4 | Effondrement | ❌ manquante |
| Terre | 5 | Fissure Éruptive | ❌ manquante |
| Monstrification | 1 | Poing Belluaire | ✅ (fissure au sol corrigée 2026-08-22) |
| Monstrification | 3 | Bras-Faux | ✅ |
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

## Budgets (au 2026-08-22, fin de MANDAT AUTONOME v3)

PixelLab : 10 générations consommées ce mandat (plafond 300). Meshy :
0 crédit consommé ce mandat (plafond 150 — balance 866, walk Ranged
récupéré gratuitement depuis un rig déjà payé).

## Prochaine priorité recommandée

Continuer Phase 3 (compétences) dans l'ordre verrouillé : Corbeau Pâle
(Invocateur, tier 2) ensuite — même méthode que Marée de Sable,
référence déjà archivée (`docs/references/invocateur/corbeau_pale.png`).
