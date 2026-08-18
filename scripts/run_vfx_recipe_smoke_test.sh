#!/usr/bin/env bash
# Lance tools/smoke_test_vfx_recipe.tscn — vérification de correction pour
# VfxRecipeRegistry (Phase 1.5). Même mécanique headless que
# scripts/run_gameplay_smoke_test.sh (xvfb + Vulkan logiciel) et même
# écart documenté (CLAUDE.md, "Environnement de capture").
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GODOT_BIN="${GODOT_BIN:-godot4}"

if ! command -v xvfb-run >/dev/null 2>&1; then
	echo "run_vfx_recipe_smoke_test.sh: xvfb-run introuvable." >&2
	exit 1
fi
if ! command -v "$GODOT_BIN" >/dev/null 2>&1; then
	echo "run_vfx_recipe_smoke_test.sh: '$GODOT_BIN' introuvable (GODOT_BIN=$GODOT_BIN)." >&2
	exit 1
fi

# Import forcé avant tout lancement — voir scripts/run_gameplay_smoke_test.sh
# pour le détail complet du hang silencieux que ça évite.
xvfb-run --auto-servernum --server-args="-screen 0 1024x768x24" \
	"$GODOT_BIN" --path "$REPO_ROOT" --headless --rendering-driver vulkan --import

xvfb-run --auto-servernum --server-args="-screen 0 1024x768x24" \
	"$GODOT_BIN" --path "$REPO_ROOT" --rendering-driver vulkan \
	res://tools/smoke_test_vfx_recipe.tscn
