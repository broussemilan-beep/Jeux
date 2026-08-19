#!/usr/bin/env python3
"""Gate gabarit morphologique — mandat régénération Cendre (docs/worklog.md,
tâche A), point critique du diagnostic externe : "en idle le perso est
filiforme, dès qu'une pose d'action se déclenche la cage thoracique et
les membres triplent de volume, la silhouette ressemble à un autre
personnage." Ce défaut a échappé à toutes les vérifications précédentes
(aucun gate ne le contrôlait) — ce script le rend détectable.

Deux familles de vérification, sur les frames COUITES (assets/processed/
sprites/<perso>/<anim>/*.png, canvas partagé, voir cook_character_frames.py) :

1. GABARIT (largeur tête / largeur torse) : chaque frame de chaque
   animation est comparée à la frame de référence (frame 0 d'idle par
   défaut — idle est la pose neutre canonique, jamais une pose d'action,
   donc le point de départ naturel du gabarit). Tolérance en pourcentage
   d'écart, PAS de valeur absolue codée en dur (même discipline que
   validate_pixels.py — un fichier de config, jamais un seuil planqué
   dans le code).

   Limite assumée et documentée (pas cachée) : la largeur torse est
   mesurée sur la largeur TOTALE de la silhouette à hauteur d'épaule
   (bande étroite juste sous le bas de la tête), PAS séparée par couleur
   cape/corps — une vraie segmentation cape/corps demanderait de la
   classification sémantique, hors de portée d'un gate pixel. La bande
   "épaule" est choisie précisément parce que c'est la zone où la cape
   (ancrée aux épaules, mandat : "la cape... trace les lignes de force")
   a le moins de raison de s'évaser radicalement d'une pose à l'autre —
   un choix de zone, pas une élimination parfaite du confondant.

2. ALIGNEMENT SOL : `cook_character_frames.py` ancre chaque frame sur
   le pixel alpha le plus bas de la frame ENTIÈRE (bbox bottom) — si un
   pan de cape/une traînée descend sous les bottes dans une frame
   (dash, coup avec pose dynamique), ce point n'est PAS le pied, et la
   frame se retrouve décalée verticalement dans le canvas cuit une fois
   collée sur ce faux point d'ancrage : exactement le "sautillement
   visuel au changement d'état" du diagnostic. Ce gate vérifie que le
   pixel non-transparent le plus bas DANS LA BANDE CENTRALE ÉTROITE
   (là où les bottes sont, jamais la cape qui s'évase sur les côtés)
   reste à la même hauteur canvas (anchor_px[1], à tolérance près) sur
   TOUTES les frames de TOUTES les animations.

Usage :
    python3 scripts/validate_morphology.py --manifest assets/manifests/cendre_frames_cooked.json
    python3 scripts/validate_morphology.py --manifest ... --config data/morphology_gate.json
    python3 scripts/validate_morphology.py --selftest

Sortie : rapport JSON sur stdout, code de sortie 0 (vert) / 1 (violation).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_FILE = REPO_ROOT / "data" / "morphology_gate.json"

# Bande "épaule" : fraction de la hauteur totale du perso, mesurée depuis
# le haut de la tête, où l'on prend la largeur de silhouette pour le
# gabarit "torse". Valeur de départ (juste sous le cou) — ajustable via
# le fichier de config, jamais recalculée en dur ailleurs dans ce script.
DEFAULT_SHOULDER_BAND_FRAC = 0.20
# Bande centrale (fraction de la largeur totale du canvas, centrée sur
# l'axe X du personnage) dans laquelle chercher le pixel le plus bas
# pour l'ancrage sol — assez étroite pour exclure une cape qui s'évase
# sur les côtés, assez large pour couvrir les deux bottes.
DEFAULT_FOOT_BAND_FRAC = 0.35

DEFAULT_HEAD_TOLERANCE_PCT = 20.0
DEFAULT_TORSO_TOLERANCE_PCT = 25.0
DEFAULT_GROUND_TOLERANCE_PX = 3


def alpha_mask(img: Image.Image):
    img = img.convert("RGBA")
    alpha = img.split()[-1]
    w, h = img.size
    px = alpha.load()
    return [[px[x, y] > 10 for x in range(w)] for y in range(h)], w, h


def row_extent(mask_row: list[bool]) -> tuple[int, int] | None:
    xs = [x for x, v in enumerate(mask_row) if v]
    if not xs:
        return None
    return min(xs), max(xs)


def measure_head(mask, w, h) -> dict | None:
    """Bbox de la tête : le blob le plus haut, jusqu'au premier
    rétrécissement marqué (le cou) — robuste à la cape, qui ne recouvre
    jamais le sommet du crâne sur ce personnage (capuche/écharpe basses,
    voir la référence)."""
    ys_with_content = [y for y in range(h) if any(mask[y])]
    if not ys_with_content:
        return None
    y_top = ys_with_content[0]
    # première ligne où la largeur redescend sous 60% du max observé
    # dans les 25 premières lignes du blob = le cou.
    widths = []
    for y in range(y_top, min(h, y_top + max(1, h // 4))):
        ext = row_extent(mask[y])
        widths.append(ext[1] - ext[0] + 1 if ext else 0)
        if not ext:
            break
    if not widths:
        return None
    max_w = max(widths)
    neck_offset = len(widths)
    for i, wdt in enumerate(widths):
        if i > 2 and wdt < max_w * 0.6:
            neck_offset = i
            break
    y_neck = y_top + neck_offset
    xs_min, xs_max = w, 0
    for y in range(y_top, y_neck):
        ext = row_extent(mask[y])
        if ext:
            xs_min = min(xs_min, ext[0])
            xs_max = max(xs_max, ext[1])
    if xs_max < xs_min:
        return None
    return {"width_px": xs_max - xs_min + 1, "height_px": y_neck - y_top, "y_top": y_top}


def measure_torso_width(mask, w, h, y_top: int, char_height: int, band_frac: float) -> int | None:
    y = y_top + int(char_height * band_frac)
    y = max(0, min(h - 1, y))
    ext = row_extent(mask[y])
    if not ext:
        return None
    return ext[1] - ext[0] + 1


def measure_ground_y(mask, w, h, foot_band_frac: float) -> int | None:
    cx = w // 2
    half_band = int(w * foot_band_frac / 2)
    x_lo, x_hi = max(0, cx - half_band), min(w, cx + half_band)
    for y in range(h - 1, -1, -1):
        if any(mask[y][x_lo:x_hi]):
            return y
    return None


def char_extent(mask, h) -> tuple[int, int] | None:
    ys = [y for y in range(h) if any(mask[y])]
    if not ys:
        return None
    return ys[0], ys[-1]


def load_config(config_file: Path) -> dict:
    if config_file.exists():
        return json.loads(config_file.read_text(encoding="utf-8"))
    return {}


def validate_manifest(manifest_path: Path, config: dict, repo_root: Path = REPO_ROOT) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    shoulder_band_frac = config.get("shoulder_band_frac", DEFAULT_SHOULDER_BAND_FRAC)
    foot_band_frac = config.get("foot_band_frac", DEFAULT_FOOT_BAND_FRAC)
    head_tol = config.get("head_tolerance_pct", DEFAULT_HEAD_TOLERANCE_PCT)
    torso_tol = config.get("torso_tolerance_pct", DEFAULT_TORSO_TOLERANCE_PCT)
    ground_tol = config.get("ground_tolerance_px", DEFAULT_GROUND_TOLERANCE_PX)
    baseline_anim = config.get("baseline_animation", "idle")
    baseline_frame_idx = config.get("baseline_frame_index", 0)

    animations = manifest["animations"]
    if baseline_anim not in animations:
        baseline_anim = next(iter(animations))
    baseline_rel = animations[baseline_anim]["frames"][baseline_frame_idx]
    baseline_path = repo_root / baseline_rel
    b_mask, b_w, b_h = alpha_mask(Image.open(baseline_path))
    b_extent = char_extent(b_mask, b_h)
    if b_extent is None:
        raise ValueError(f"frame de référence entièrement transparente : {baseline_path}")
    b_char_h = b_extent[1] - b_extent[0] + 1
    b_head = measure_head(b_mask, b_w, b_h)
    b_torso = measure_torso_width(b_mask, b_w, b_h, b_extent[0], b_char_h, shoulder_band_frac)
    b_ground_y = measure_ground_y(b_mask, b_w, b_h, foot_band_frac)

    violations: list[dict] = []
    frame_reports: list[dict] = []

    for anim_name, anim in animations.items():
        for i, rel in enumerate(anim["frames"]):
            path = repo_root / rel
            mask, w, h = alpha_mask(Image.open(path))
            extent = char_extent(mask, h)
            entry = {"animation": anim_name, "frame": i, "path": rel}
            if extent is None:
                entry["error"] = "frame_entierement_transparente"
                frame_reports.append(entry)
                continue
            char_h = extent[1] - extent[0] + 1
            head = measure_head(mask, w, h)
            torso_w = measure_torso_width(mask, w, h, extent[0], char_h, shoulder_band_frac)
            ground_y = measure_ground_y(mask, w, h, foot_band_frac)

            entry["head_width_px"] = head["width_px"] if head else None
            entry["torso_width_px"] = torso_w
            entry["ground_y"] = ground_y

            if head and b_head:
                dev = abs(head["width_px"] - b_head["width_px"]) / b_head["width_px"] * 100.0
                entry["head_deviation_pct"] = round(dev, 1)
                if dev > head_tol:
                    violations.append({
                        "animation": anim_name, "frame": i, "check": "head_width",
                        "baseline_px": b_head["width_px"], "frame_px": head["width_px"],
                        "deviation_pct": round(dev, 1), "tolerance_pct": head_tol,
                    })
            if torso_w and b_torso:
                dev = abs(torso_w - b_torso) / b_torso * 100.0
                entry["torso_deviation_pct"] = round(dev, 1)
                if dev > torso_tol:
                    violations.append({
                        "animation": anim_name, "frame": i, "check": "torso_width",
                        "baseline_px": b_torso, "frame_px": torso_w,
                        "deviation_pct": round(dev, 1), "tolerance_pct": torso_tol,
                    })
            if ground_y is not None and b_ground_y is not None:
                dev_px = abs(ground_y - b_ground_y)
                entry["ground_deviation_px"] = dev_px
                if dev_px > ground_tol:
                    violations.append({
                        "animation": anim_name, "frame": i, "check": "ground_alignment",
                        "baseline_ground_y": b_ground_y, "frame_ground_y": ground_y,
                        "deviation_px": dev_px, "tolerance_px": ground_tol,
                    })
            frame_reports.append(entry)

    return {
        "ok": len(violations) == 0,
        "baseline": {
            "animation": baseline_anim, "frame_index": baseline_frame_idx,
            "head_width_px": b_head["width_px"] if b_head else None,
            "torso_width_px": b_torso, "ground_y": b_ground_y,
        },
        "tolerances": {
            "head_tolerance_pct": head_tol, "torso_tolerance_pct": torso_tol,
            "ground_tolerance_px": ground_tol,
        },
        "violation_count": len(violations),
        "violations": violations,
        "frame_count": len(frame_reports),
    }


def run_selftest() -> int:
    """Vérifie le script sur des cas synthétiques connus — un carré fixe
    (aucune violation attendue) et un carré qui triple de largeur sur sa
    2e frame (violation attendue), sans dépendre d'assets réels."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        canvas = (40, 40)

        def make_frame(path: Path, head_w: int, torso_w: int, ground_y: int) -> None:
            img = Image.new("RGBA", canvas, (0, 0, 0, 0))
            px = img.load()
            cx = canvas[0] // 2
            for y in range(4, 4 + 6):
                for x in range(cx - head_w // 2, cx + head_w // 2):
                    px[x, y] = (255, 255, 255, 255)
            for y in range(10, ground_y + 1):
                for x in range(cx - torso_w // 2, cx + torso_w // 2):
                    px[x, y] = (200, 200, 200, 255)
            img.save(path)

        anims = {"idle": [], "coup1": []}
        for name, specs in [
            ("idle", [(8, 10, 30), (8, 10, 30)]),
            ("coup1", [(8, 10, 30), (8, 30, 30)]),  # 2e frame: torse triple
        ]:
            out_dir = tmp_path / "sprites" / name
            out_dir.mkdir(parents=True)
            for i, (hw, tw, gy) in enumerate(specs):
                p = out_dir / f"{i}.png"
                make_frame(p, hw, tw, gy)
                anims[name].append(str(p.relative_to(tmp_path)))

        manifest = {
            "character": "selftest", "out_canvas": list(canvas), "anchor_px": [20, 34],
            "animations": {
                name: {"frames": frames, "canvas": list(canvas), "anchor_px": [20, 34]}
                for name, frames in anims.items()
            },
        }
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(json.dumps(manifest))

        # bande épaule à 0.35 : le personnage synthétique a une tête
        # proportionnellement plus grande (6px/27px ~= 22%) que la
        # référence réelle (~14%), 0.20 tomberait encore dans la tête.
        report = validate_manifest(manifest_path, {"shoulder_band_frac": 0.35}, repo_root=tmp_path)
        checks = [v["check"] for v in report["violations"]]
        assert not report["ok"], f"le selftest doit détecter la violation synthétique — report={json.dumps(report)}"
        assert "torso_width" in checks, f"violation torso_width attendue, checks={checks}"
        print("SELFTEST OK —", json.dumps(report, indent=2))
        return 0


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", type=Path)
    p.add_argument("--config", type=Path, default=DEFAULT_CONFIG_FILE)
    p.add_argument("--selftest", action="store_true")
    args = p.parse_args()

    if args.selftest:
        return run_selftest()

    if not args.manifest:
        p.error("--manifest requis (sauf --selftest)")

    config = load_config(args.config)
    report = validate_manifest(args.manifest, config)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
