#!/usr/bin/env python3
"""Gate qualité — docs/ARCHITECTURE_VFX_v3.md §13.3, §13.4.

"compare_reference.py diffe pixel à pixel contre la dernière capture
APPROUVÉE PAR LABEL HUMAIN — c'est ainsi que naît une "image de
référence" : c'est toujours une capture ayant reçu un verdict `accept`
de Milan, jamais une image choisie par la machine."

Et §13.4 : "seed fixe → même sortie / même capture" — une fois une
référence approuvée, toute recapture au même seed doit lui être
IDENTIQUE. Un écart signale une vraie régression, jamais un arrondi
acceptable (tolérance 0 par défaut ; --tolerance existe pour un usage
futur documenté, pas pour masquer une dérive silencieuse).

Lit data/labels/quality_labels.jsonl — une ligne JSON par verdict,
schéma : {"capture_id", "asset_id", "verdict": "accept"|"reject",
"reference_image": "<chemin relatif au repo>", "reason"?, "timestamp"?}.

CE SCRIPT NE MODIFIE JAMAIS quality_labels.jsonl — §13.2 : "Claude Code
ne s'auto-attribue jamais un verdict humain". Lecture seule, un humain
(Milan) écrit les verdicts, ce script les LIT.

Usage :
    python3 scripts/compare_reference.py --asset-id hero_attack1_v3 --candidate captures_local/out.png
    python3 scripts/compare_reference.py --selftest

Sortie : rapport JSON sur stdout.
  - Aucune référence approuvée trouvée -> ok=true, status="candidate" (pas un échec : c'est l'état attendu avant tout premier verdict).
  - Référence trouvée, diff nulle -> ok=true, status="match".
  - Référence trouvée, diff non nulle -> ok=false, status="regression".
Code de sortie 0 si ok, 1 sinon.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LABELS_FILE = REPO_ROOT / "data" / "labels" / "quality_labels.jsonl"


def _read_labels(labels_file: Path) -> list[dict]:
    if not labels_file.exists():
        return []
    entries = []
    for line_no, line in enumerate(labels_file.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError as e:
            raise ValueError(f"{labels_file}:{line_no}: ligne JSONL invalide — {e}") from e
    return entries


def find_latest_accepted_reference(asset_id: str, labels_file: Path = DEFAULT_LABELS_FILE) -> dict | None:
    entries = _read_labels(labels_file)
    accepted = [e for e in entries if e.get("asset_id") == asset_id and e.get("verdict") == "accept"]
    return accepted[-1] if accepted else None


def diff_images(reference_path: Path, candidate_path: Path) -> dict:
    ref = np.asarray(Image.open(reference_path).convert("RGBA"), dtype=np.int16)
    cand = np.asarray(Image.open(candidate_path).convert("RGBA"), dtype=np.int16)

    if ref.shape != cand.shape:
        return {
            "dimensions_match": False,
            "reference_shape": list(ref.shape),
            "candidate_shape": list(cand.shape),
            "max_diff": None, "mean_diff": None, "differing_pixels": None,
        }

    diff = np.abs(ref - cand)
    per_pixel_max = diff.max(axis=2)  # pire canal par pixel
    differing = int((per_pixel_max > 0).sum())
    total = per_pixel_max.size
    return {
        "dimensions_match": True,
        "max_diff": int(diff.max()),
        "mean_diff": round(float(diff.mean()), 4),
        "differing_pixels": differing,
        "total_pixels": int(total),
        "differing_ratio": round(differing / total, 6) if total else 0.0,
    }


def compare(asset_id: str, candidate_path: Path, labels_file: Path = DEFAULT_LABELS_FILE, tolerance: int = 0) -> dict:
    ref_entry = find_latest_accepted_reference(asset_id, labels_file)
    if ref_entry is None:
        return {
            "ok": True,
            "status": "candidate",
            "asset_id": asset_id,
            "candidate": str(candidate_path),
            "message": "aucune référence approuvée pour cet asset_id — capture CANDIDATE, en attente du verdict de Milan (data/labels/quality_labels.jsonl). Ce n'est pas un échec.",
        }

    reference_image = ref_entry.get("reference_image")
    if not reference_image:
        raise ValueError(f"l'entrée acceptée pour '{asset_id}' n'a pas de champ 'reference_image' — verdict mal formé dans {labels_file}")
    reference_path = REPO_ROOT / reference_image
    if not reference_path.exists():
        raise FileNotFoundError(f"reference_image référencée introuvable : {reference_path} (verdict {ref_entry.get('capture_id')})")

    diff = diff_images(reference_path, candidate_path)
    if not diff["dimensions_match"]:
        return {
            "ok": False, "status": "regression", "asset_id": asset_id,
            "reason": "dimensions différentes de la référence approuvée",
            **diff,
            "reference": str(reference_path), "reference_capture_id": ref_entry.get("capture_id"),
        }

    ok = diff["max_diff"] <= tolerance
    return {
        "ok": ok,
        "status": "match" if ok else "regression",
        "asset_id": asset_id,
        "candidate": str(candidate_path),
        "reference": str(reference_path),
        "reference_capture_id": ref_entry.get("capture_id"),
        "tolerance": tolerance,
        **diff,
    }


def _selftest() -> int:
    import tempfile

    n = 0
    failures = 0

    def check(label: str, cond: bool, detail: str = "") -> None:
        nonlocal n, failures
        n += 1
        status = "OK" if cond else "FAIL"
        if not cond:
            failures += 1
        print(f"{status}  {label}" + (f"  ({detail})" if detail else ""))

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        labels_file = tmp_path / "quality_labels.jsonl"

        # Cas 1 : aucun verdict du tout -> candidate, ok=true.
        img_a = Image.new("RGBA", (8, 8), (10, 20, 30, 255))
        cand_a = tmp_path / "candidate_a.png"
        img_a.save(cand_a)
        r1 = compare("asset.nope", cand_a, labels_file)
        check("aucun verdict -> status=candidate, ok=true", r1["ok"] is True and r1["status"] == "candidate")

        # Prépare une référence approuvée réelle sur disque, chemin
        # RELATIF au repo (comme en production) — on triche juste pour
        # le test en pointant reference_image vers un chemin absolu du
        # tmpdir converti en relatif via un chdir n'aurait rien de
        # propre ; on écrit donc directement dans REPO_ROOT/tmp local
        # pour rester fidèle au contrat "chemin relatif au repo".
        ref_dir = REPO_ROOT / "captures_local" / "_selftest_compare_reference"
        ref_dir.mkdir(parents=True, exist_ok=True)
        ref_rel = "captures_local/_selftest_compare_reference/ref.png"
        ref_abs = REPO_ROOT / ref_rel
        img_ref = Image.new("RGBA", (8, 8), (50, 60, 70, 255))
        img_ref.save(ref_abs)

        labels_file.write_text(json.dumps({
            "capture_id": "asset.match_seed1_v1", "asset_id": "asset.match",
            "verdict": "accept", "reference_image": ref_rel,
        }) + "\n", encoding="utf-8")

        # Cas 2 : candidat identique pixel pour pixel -> match, ok=true.
        cand_identical = tmp_path / "identical.png"
        img_ref.save(cand_identical)
        r2 = compare("asset.match", cand_identical, labels_file)
        check("candidat identique à la référence -> status=match, ok=true", r2["ok"] is True and r2["status"] == "match", json.dumps(r2))

        # Cas 3 : candidat différent (1 pixel modifié) -> regression, ok=false.
        img_diff = img_ref.copy()
        img_diff.putpixel((0, 0), (51, 60, 70, 255))  # +1 sur le rouge, 1 seul pixel
        cand_diff = tmp_path / "diff.png"
        img_diff.save(cand_diff)
        r3 = compare("asset.match", cand_diff, labels_file)
        check("candidat avec 1 pixel différent -> status=regression, ok=false", r3["ok"] is False and r3["differing_pixels"] == 1, json.dumps(r3))

        # Cas 4 : dimensions différentes -> regression explicite, jamais un crash.
        img_wrong_size = Image.new("RGBA", (4, 4), (50, 60, 70, 255))
        cand_size = tmp_path / "wrong_size.png"
        img_wrong_size.save(cand_size)
        r4 = compare("asset.match", cand_size, labels_file)
        check("candidat de dimensions différentes -> ok=false, pas de crash", r4["ok"] is False and r4["dimensions_match"] is False)

        ref_abs.unlink()
        ref_dir.rmdir()

    print(f"\n{n - failures}/{n} assertions passées")
    return 0 if failures == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--asset-id", type=str)
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--labels-file", type=Path, default=DEFAULT_LABELS_FILE)
    parser.add_argument("--tolerance", type=int, default=0, help="Écart max par canal toléré (0 = identité stricte, défaut)")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()

    if args.selftest:
        return _selftest()

    if not args.asset_id or not args.candidate:
        parser.error("--asset-id et --candidate sont requis (ou --selftest)")

    report = compare(args.asset_id, args.candidate, args.labels_file, args.tolerance)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
