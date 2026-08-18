#!/usr/bin/env bash
# Lance une capture via tools/capture_scene.tscn — docs/ARCHITECTURE_VFX_v3.md §13.3.
#
#   scripts/capture_headless.sh --primitive=impactFlashFrame --seed=44102 --tick=1 --out=/chemin/absolu/out.png
#
# ÉCART DOCUMENTÉ (voir CLAUDE.md "Environnement de capture") : le §13.3
# spécifie `godot4 --headless`. Vérifié par test isolé avant tout code de
# ce dépôt : dans CET environnement (sandbox sans GPU), `--headless`
# force le RenderingServer en mode "dummy" — get_viewport().get_texture()
# retourne toujours une texture nulle, aucun pixel réel produit, quel que
# soit --rendering-driver. `--display-driver headless` seul (sans le
# raccourci --headless) donne EXACTEMENT le même résultat cassé — ce
# n'est pas une histoire de flag, Godot a besoin d'un vrai serveur
# d'affichage (même virtuel) pour créer le contexte de rendu ici.
#
# Solution validée : xvfb-run (serveur X virtuel, aucune fenêtre visible,
# aucune interaction) + --rendering-driver vulkan, sur Vulkan logiciel
# (Mesa lavapipe/llvmpipe — aucun GPU dans ce sandbox, confirmé via
# `vulkaninfo --summary`). Résultat identique du point de vue du
# pipeline : un script, zéro interaction, un PNG déterministe par seed.
# Sur device réel ou une CI avec vrai GPU, ni ce script ni le renderer
# Mobile ne changent — seul cet outil de capture DEV a besoin de
# l'adaptation, jamais le jeu lui-même.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GODOT_BIN="${GODOT_BIN:-godot4}"

if ! command -v xvfb-run >/dev/null 2>&1; then
	echo "capture_headless.sh: xvfb-run introuvable — voir CLAUDE.md, écart §13.3 documenté." >&2
	exit 1
fi
if ! command -v "$GODOT_BIN" >/dev/null 2>&1; then
	echo "capture_headless.sh: '$GODOT_BIN' introuvable (GODOT_BIN=$GODOT_BIN)." >&2
	exit 1
fi

# ÉCART DOCUMENTÉ (docs/worklog.md, Phase 1.2) : un .png ajouté hors
# éditeur (assets PixelLab téléchargés via curl) n'a pas de ".import" —
# sans ce passage d'import forcé, le symptôme n'est PAS une erreur propre
# mais un hang silencieux (le scan de classes avorte en cours de route,
# le script racine de la scène ne charge plus, _ready() ne tourne jamais,
# Godot reste assis sans jamais quitter). Voir run_gameplay_smoke_test.sh
# pour le détail complet de ce qui a été observé.
xvfb-run --auto-servernum --server-args="-screen 0 1024x768x24" \
	"$GODOT_BIN" --path "$REPO_ROOT" --headless --rendering-driver vulkan --import

xvfb-run --auto-servernum --server-args="-screen 0 1024x768x24" \
	"$GODOT_BIN" --path "$REPO_ROOT" --rendering-driver vulkan \
	res://tools/capture_scene.tscn -- "$@"
