#!/usr/bin/env bash
# Lance tools/smoke_test_gameplay.tscn — vérification de correction pour le
# squelette gameplay Phase 1.2 (pas une capture visuelle, voir docstring du
# script). Même mécanique headless que capture_headless.sh (xvfb + Vulkan
# logiciel) : ce projet a un écran ou une caméra dans sa scène de test, donc
# il a besoin d'un vrai serveur d'affichage même pour tourner en CI ici —
# écart documenté dans CLAUDE.md.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GODOT_BIN="${GODOT_BIN:-godot4}"

if ! command -v xvfb-run >/dev/null 2>&1; then
	echo "run_gameplay_smoke_test.sh: xvfb-run introuvable." >&2
	exit 1
fi
if ! command -v "$GODOT_BIN" >/dev/null 2>&1; then
	echo "run_gameplay_smoke_test.sh: '$GODOT_BIN' introuvable (GODOT_BIN=$GODOT_BIN)." >&2
	exit 1
fi

# ÉCART DOCUMENTÉ (docs/worklog.md, Phase 1.2) : un .png ajouté au repo
# hors éditeur (téléchargé via curl, comme les rotations PixelLab) n'a pas
# de ".import" — Godot ne l'importe PAS à la volée en lançant une scène
# directement. Constaté empiriquement : ça ne se contente pas d'échouer
# proprement, ça avorte le scan global de classes en cours de route (les
# `class_name` d'AUTRES scripts, sans rapport avec la texture, ne se
# résolvaient plus — "Stats" introuvable etc.), et comme le script racine
# de la scène ne charge plus, _ready() ne tourne jamais et Godot reste
# assis à tourner sans jamais quitter (aucun message, CPU à fond). D'où
# ce passage d'import forcé AVANT de lancer quoi que ce soit — sinon le
# symptôme est un hang silencieux, pas une erreur claire.
xvfb-run --auto-servernum --server-args="-screen 0 1024x768x24" \
	"$GODOT_BIN" --path "$REPO_ROOT" --headless --rendering-driver vulkan --import

xvfb-run --auto-servernum --server-args="-screen 0 1024x768x24" \
	"$GODOT_BIN" --path "$REPO_ROOT" --rendering-driver vulkan \
	res://tools/smoke_test_gameplay.tscn
