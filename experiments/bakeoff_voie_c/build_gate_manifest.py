#!/usr/bin/env python3
"""Bake-off Animation, Voie C — assemble un manifeste au format attendu par
scripts/validate_morphology.py SANS toucher au script lui-même : frame 0 =
la référence réelle du jeu (idle_south/0.png), frame 1 = le rendu Voie C.
Le gate compare alors automatiquement frame 1 contre frame 0 (baseline_
animation="idle", baseline_frame_index=0 par défaut, voir
data/morphology_gate.json) — exactement la question posée par le mandat
("gate de gabarit automatique"), sans dupliquer sa logique de mesure.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--baseline", type=Path, default=REPO_ROOT / "assets/processed/sprites/cendre/idle_south/0.png")
    p.add_argument("--candidate", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()

    baseline_rel = str(args.baseline.resolve().relative_to(REPO_ROOT))
    candidate_rel = str(args.candidate.resolve().relative_to(REPO_ROOT))

    manifest = {
        "character": "bakeoff_voie_c_vs_baseline",
        "out_canvas": [64, 64],
        "anchor_px": [32, 61],
        "animations": {
            "idle": {
                "frames": [baseline_rel, candidate_rel],
                "canvas": [64, 64],
                "anchor_px": [32, 61],
            },
        },
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"OK — manifest écrit : {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
