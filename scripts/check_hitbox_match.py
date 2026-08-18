#!/usr/bin/env python3
"""Gate qualité — docs/ARCHITECTURE_VFX_v3.md §2, test 6 (formule exacte,
citée ici mot pour mot pour qu'aucune dérive silencieuse ne s'introduise
entre le doc et le code) :

    "calculer le masque alpha pondéré par opacité de l'effet, en extraire
    le rayon effectif (rayon du cercle centré sur le centroïde contenant
    90% de la masse d'opacité), comparer au rayon (ou demi-largeur) de la
    hitbox réelle. abs(r_visuel - r_hitbox) / r_hitbox <= 0.08. Pour les
    zones non circulaires, comparer les bbox sur chaque axe avec la même
    tolérance."

Deux modes :
  --hitbox-radius R     comparaison circulaire (r_visuel vs R)
  --hitbox-w W --hitbox-h H   comparaison bbox (demi-largeur/demi-hauteur
                               visuelles vs W/2, H/2, même tolérance 8%)

Usage :
    python3 scripts/check_hitbox_match.py --image <png> --hitbox-radius 20
    python3 scripts/check_hitbox_match.py --image <png> --hitbox-w 40 --hitbox-h 24
    python3 scripts/check_hitbox_match.py --selftest

Sortie : rapport JSON sur stdout, code de sortie 0 (vert, écart <= 8%) / 1.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

TOLERANCE = 0.08  # §2 test 6 : chiffre exact du mandat, jamais un autre ici.
MASS_FRACTION = 0.90  # "contenant 90% de la masse d'opacité" — idem, exact.


def _alpha_mask(image_path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Retourne (xs, ys, weights) — une entrée par pixel, weights = alpha
    normalisé [0,1]. Coordonnées en pixels, origine haut-gauche (espace
    image standard, cohérent avec le reste du pipeline PNG)."""
    img = Image.open(image_path).convert("RGBA")
    arr = np.asarray(img)
    alpha = arr[:, :, 3].astype(np.float64) / 255.0
    ys, xs = np.mgrid[0:arr.shape[0], 0:arr.shape[1]]
    return xs.ravel().astype(np.float64), ys.ravel().astype(np.float64), alpha.ravel()


def _centroid(xs: np.ndarray, ys: np.ndarray, weights: np.ndarray) -> tuple[float, float, float]:
    total = weights.sum()
    if total <= 0:
        raise ValueError("masse d'opacité totale nulle — image entièrement transparente, rien à mesurer")
    cx = float((xs * weights).sum() / total)
    cy = float((ys * weights).sum() / total)
    return cx, cy, total


def effective_radius(image_path: Path) -> dict:
    """r_visuel : rayon du cercle centré sur le centroïde contenant 90%
    de la masse d'opacité — tri par distance croissante, accumulation."""
    xs, ys, weights = _alpha_mask(image_path)
    cx, cy, total = _centroid(xs, ys, weights)
    dist = np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2)

    order = np.argsort(dist)
    sorted_dist = dist[order]
    sorted_w = weights[order]
    cumulative = np.cumsum(sorted_w)
    target = MASS_FRACTION * total
    idx = int(np.searchsorted(cumulative, target))
    idx = min(idx, len(sorted_dist) - 1)
    r_visual = float(sorted_dist[idx])

    return {"centroid": [round(cx, 2), round(cy, 2)], "r_visual": round(r_visual, 3), "total_mass": round(float(total), 2)}


def effective_half_extents(image_path: Path) -> dict:
    """Généralisation par axe pour les zones non circulaires (§2, dernière
    phrase du test 6) : même principe (90% de la masse, en distance
    depuis le centroïde), appliqué indépendamment à X et Y."""
    xs, ys, weights = _alpha_mask(image_path)
    cx, cy, total = _centroid(xs, ys, weights)
    target = MASS_FRACTION * total

    def half_extent(coords: np.ndarray, center: float) -> float:
        d = np.abs(coords - center)
        order = np.argsort(d)
        sorted_d = d[order]
        cumulative = np.cumsum(weights[order])
        idx = int(np.searchsorted(cumulative, target))
        idx = min(idx, len(sorted_d) - 1)
        return float(sorted_d[idx])

    hw = half_extent(xs, cx)
    hh = half_extent(ys, cy)
    return {"centroid": [round(cx, 2), round(cy, 2)], "half_width_visual": round(hw, 3), "half_height_visual": round(hh, 3), "total_mass": round(float(total), 2)}


def check_circular(image_path: Path, r_hitbox: float) -> dict:
    if r_hitbox <= 0:
        raise ValueError("--hitbox-radius doit être > 0")
    r = effective_radius(image_path)
    delta = abs(r["r_visual"] - r_hitbox) / r_hitbox
    ok = delta <= TOLERANCE
    return {"ok": ok, "mode": "circular", "r_visual": r["r_visual"], "r_hitbox": r_hitbox,
            "delta_ratio": round(delta, 4), "tolerance": TOLERANCE, "centroid": r["centroid"]}


def check_bbox(image_path: Path, w_hitbox: float, h_hitbox: float) -> dict:
    if w_hitbox <= 0 or h_hitbox <= 0:
        raise ValueError("--hitbox-w et --hitbox-h doivent être > 0")
    e = effective_half_extents(image_path)
    hw_hitbox, hh_hitbox = w_hitbox / 2.0, h_hitbox / 2.0
    delta_w = abs(e["half_width_visual"] - hw_hitbox) / hw_hitbox
    delta_h = abs(e["half_height_visual"] - hh_hitbox) / hh_hitbox
    ok = delta_w <= TOLERANCE and delta_h <= TOLERANCE
    return {"ok": ok, "mode": "bbox", "half_width_visual": e["half_width_visual"], "half_height_visual": e["half_height_visual"],
            "half_width_hitbox": hw_hitbox, "half_height_hitbox": hh_hitbox,
            "delta_ratio_w": round(delta_w, 4), "delta_ratio_h": round(delta_h, 4),
            "tolerance": TOLERANCE, "centroid": e["centroid"]}


def _make_disk(size: int, radius: float) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    arr = np.zeros((size, size, 4), dtype=np.uint8)
    cy = cx = size / 2.0
    yy, xx = np.mgrid[0:size, 0:size]
    mask = (xx - cx) ** 2 + (yy - cy) ** 2 <= radius ** 2
    arr[mask] = [255, 255, 255, 255]
    return Image.fromarray(arr, "RGBA")


def _make_rect(size: int, half_w: float, half_h: float) -> Image.Image:
    arr = np.zeros((size, size, 4), dtype=np.uint8)
    cy = cx = size / 2.0
    yy, xx = np.mgrid[0:size, 0:size]
    mask = (np.abs(xx - cx) <= half_w) & (np.abs(yy - cy) <= half_h)
    arr[mask] = [255, 255, 255, 255]
    return Image.fromarray(arr, "RGBA")


def _selftest() -> int:
    """Cas synthétiques à réponse connue par construction — voir le
    même principe/justification que validate_pixels.py --selftest."""
    import math
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

        # Disque plein uniforme de rayon 20 : pour une masse UNIFORME sur
        # un disque, le rayon contenant 90% de la masse (donc 90% de
        # l'aire) vaut R*sqrt(0.9) — géométrie de cercle exacte, pas une
        # approximation. R=20 -> r90 ≈ 18.974.
        R = 20.0
        p_disk = tmp_path / "disk.png"
        _make_disk(100, R).save(p_disk)
        expected_r90 = R * math.sqrt(0.90)
        r = effective_radius(p_disk)
        check("disque uniforme R=20 : r_visual ≈ R√0.9 (géométrie exacte)",
              abs(r["r_visual"] - expected_r90) < 0.6, f"r_visual={r['r_visual']}, attendu≈{expected_r90:.3f}")

        # Comparé à un hitbox de rayon 20 (le rayon RÉEL du disque, pas
        # r90) : écart = (20-18.974)/20 ≈ 5.1% <= 8% -> ok.
        c = check_circular(p_disk, R)
        check("disque R=20 vs hitbox radius=20 -> écart ~5% <= 8%, ok=true", c["ok"] is True, f"delta={c['delta_ratio']}")

        # Comparé à un hitbox bien trop petit (10) : écart ~90% -> violation.
        c_bad = check_circular(p_disk, 10.0)
        check("disque R=20 vs hitbox radius=10 (trop petit) -> ok=false", c_bad["ok"] is False, f"delta={c_bad['delta_ratio']}")

        # Rectangle plein demi-largeur=30, demi-hauteur=15 : la masse est
        # uniforme sur un rectangle, donc le r90 par axe (indépendant
        # entre X et Y ici par construction, pas de corrélation) vaut
        # demi-extent * 0.90 exactement (distribution uniforme sur
        # [-h,h] : la fraction de masse à distance <= d du centre est
        # d/h, donc d90 = 0.90*h).
        hw, hh = 30.0, 15.0
        p_rect = tmp_path / "rect.png"
        _make_rect(100, hw, hh).save(p_rect)
        e = effective_half_extents(p_rect)
        check("rectangle 60x30 : half_width_visual ≈ 0.9*30=27", abs(e["half_width_visual"] - 0.9 * hw) < 0.6, f"got={e['half_width_visual']}")
        check("rectangle 60x30 : half_height_visual ≈ 0.9*15=13.5", abs(e["half_height_visual"] - 0.9 * hh) < 0.6, f"got={e['half_height_visual']}")

        cb = check_bbox(p_rect, hw * 2, hh * 2)
        check("rectangle 60x30 vs hitbox 60x30 -> écart ~10% par axe... ", True, f"delta_w={cb['delta_ratio_w']} delta_h={cb['delta_ratio_h']}")
        # NB : 10% > tolérance 8% ICI par construction (rectangle uniforme
        # idéal, pas un vrai VFX à contour doux) — ce cas documente la
        # limite du modèle plutôt que de forcer un "ok" artificiel.
        check("...donc ok=false attendu pour ce rectangle parfaitement dur", cb["ok"] is False)

    print(f"\n{n - failures}/{n} assertions passées")
    return 0 if failures == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--image", type=Path)
    parser.add_argument("--hitbox-radius", type=float)
    parser.add_argument("--hitbox-w", type=float)
    parser.add_argument("--hitbox-h", type=float)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()

    if args.selftest:
        return _selftest()

    if not args.image:
        parser.error("--image requis (ou --selftest)")

    if args.hitbox_radius is not None:
        report = check_circular(args.image, args.hitbox_radius)
    elif args.hitbox_w is not None and args.hitbox_h is not None:
        report = check_bbox(args.image, args.hitbox_w, args.hitbox_h)
    else:
        parser.error("fournir --hitbox-radius, OU --hitbox-w + --hitbox-h")
        return 2

    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
