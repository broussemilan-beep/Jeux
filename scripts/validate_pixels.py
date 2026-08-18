#!/usr/bin/env python3
"""Gate qualité — docs/ARCHITECTURE_VFX_v3.md §3, §13.4.

Vérifie qu'une capture PNG respecte :
  1. les bandes de valeur (HSV, V en %) de sa catégorie, lues dans
     data/palettes/value_bands.json — JAMAIS de seuil en dur ici, le doc
     est explicite : "Elles sont ajustables uniquement via ce fichier,
     jamais en dur dans le code." ;
  2. l'absence de bord semi-transparent non voulu (§13.4 "alpha : pas de
     bord semi-transparent non voulu" ; §12.4 "pas d'anti-aliasing/flou/
     transparence interdite").

Les pixels totalement transparents (alpha == 0) ne comptent JAMAIS dans
le calcul de bande de valeur — un fond vide n'a pas de "couleur".

Usage :
    python3 scripts/validate_pixels.py --image <png> --category <ui|character|vfx|decor>
    python3 scripts/validate_pixels.py --selftest   # vérifie le script lui-même sur des cas synthétiques connus

Sortie : rapport JSON sur stdout, code de sortie 0 (vert) / 1 (violation).
"""
from __future__ import annotations

import argparse
import colorsys
import json
import sys
from pathlib import Path

from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BANDS_FILE = REPO_ROOT / "data" / "palettes" / "value_bands.json"

# §13.4 : pas de seuil exact chiffré par le mandat pour "bord semi-
# transparent non voulu" (contrairement au 8% de check_hitbox_match.py,
# qui LUI est une formule exacte du §2). Valeur de départ raisonnable,
# à recalibrer si un vrai asset produit des faux positifs légitimes
# (ex. un dégradé de dissipation volontaire, §4 dissipationProfile).
SEMI_ALPHA_MIN = 10
SEMI_ALPHA_MAX = 245
SEMI_ALPHA_RATIO_MAX = 0.02  # 2% des pixels non-transparents, max


def load_bands(bands_file: Path, category: str) -> list[tuple[float, float]]:
    data = json.loads(bands_file.read_text(encoding="utf-8"))
    categories = data["categories"]
    if category not in categories:
        raise ValueError(f"catégorie inconnue '{category}' — attendu l'une de {sorted(categories)}")
    return [tuple(b) for b in categories[category]["bands"]]


def value_in_bands(value_pct: float, bands: list[tuple[float, float]]) -> bool:
    return any(lo <= value_pct <= hi for lo, hi in bands)


def validate_image(image_path: Path, category: str, bands_file: Path = DEFAULT_BANDS_FILE) -> dict:
    bands = load_bands(bands_file, category)
    img = Image.open(image_path).convert("RGBA")
    width, height = img.size
    pixels = img.load()

    total_opaque = 0
    band_violations: list[dict] = []
    semi_alpha_count = 0

    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if a == 0:
                continue  # transparent pur : hors de propos pour la bande de valeur
            total_opaque += 1
            if SEMI_ALPHA_MIN <= a <= SEMI_ALPHA_MAX:
                semi_alpha_count += 1
            _, _, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
            value_pct = v * 100.0
            if not value_in_bands(value_pct, bands):
                if len(band_violations) < 20:  # échantillon, jamais des milliers de lignes
                    band_violations.append({"x": x, "y": y, "value_pct": round(value_pct, 2), "rgb": [r, g, b]})

    semi_alpha_ratio = (semi_alpha_count / total_opaque) if total_opaque else 0.0
    alpha_ok = semi_alpha_ratio <= SEMI_ALPHA_RATIO_MAX

    ok = (len(band_violations) == 0) and alpha_ok
    return {
        "ok": ok,
        "image": str(image_path),
        "category": category,
        "bands": bands,
        "total_opaque_pixels": total_opaque,
        "band_violation_count": len(band_violations),
        "band_violation_sample": band_violations,
        "semi_alpha_count": semi_alpha_count,
        "semi_alpha_ratio": round(semi_alpha_ratio, 4),
        "semi_alpha_ratio_max": SEMI_ALPHA_RATIO_MAX,
        "alpha_ok": alpha_ok,
    }


def _selftest() -> int:
    """Vérifie le script sur des images synthétiques dont la réponse
    attendue est connue par construction — la seule façon fiable de
    prouver qu'un gate teste vraiment quelque chose (§16.3 : "vérifier
    avant de déclarer fini")."""
    import tempfile

    n = 0
    failures = 0

    def check(label: str, cond: bool) -> None:
        nonlocal n, failures
        n += 1
        status = "OK" if cond else "FAIL"
        if not cond:
            failures += 1
        print(f"{status}  {label}")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        # Cas 1 : gris moyen (V=50%) partout, catégorie "vfx" (bande 20-92) -> OK.
        img_ok = Image.new("RGBA", (8, 8), (128, 128, 128, 255))
        p_ok = tmp_path / "ok_vfx.png"
        img_ok.save(p_ok)
        r_ok = validate_image(p_ok, "vfx")
        check("gris moyen (V~50%) dans la bande vfx 20-92% -> ok=true", r_ok["ok"] is True)

        # Cas 2 : blanc pur (V=100%) catégorie "vfx" (jamais 100%, §3) -> violation.
        img_bad = Image.new("RGBA", (8, 8), (255, 255, 255, 255))
        p_bad = tmp_path / "bad_vfx_white.png"
        img_bad.save(p_bad)
        r_bad = validate_image(p_bad, "vfx")
        check("blanc pur (V=100%) hors bande vfx -> ok=false", r_bad["ok"] is False)
        check("...et le violateur est bien détecté (band_violation_count > 0)", r_bad["band_violation_count"] > 0)

        # Cas 3 : même blanc pur, catégorie "ui" (0-12 et 94-100 autorisés) -> OK.
        r_ui = validate_image(p_bad, "ui")
        check("le même blanc pur EST autorisé en catégorie ui (extrêmes permis)", r_ui["ok"] is True)

        # Cas 4 : pixels totalement transparents ignorés (alpha=0 partout, blanc) -> OK, 0 pixel compté.
        img_transp = Image.new("RGBA", (8, 8), (255, 255, 255, 0))
        p_transp = tmp_path / "transparent.png"
        img_transp.save(p_transp)
        r_transp = validate_image(p_transp, "vfx")
        check("image entièrement transparente -> 0 pixel opaque compté, ok=true", r_transp["ok"] is True and r_transp["total_opaque_pixels"] == 0)

        # Cas 5 : bord semi-transparent excessif (moitié de l'image à alpha=128) -> violation alpha.
        img_semi = Image.new("RGBA", (8, 8), (128, 128, 128, 255))
        px = img_semi.load()
        for yy in range(4):
            for xx in range(8):
                px[xx, yy] = (128, 128, 128, 128)
        p_semi = tmp_path / "semi.png"
        img_semi.save(p_semi)
        r_semi = validate_image(p_semi, "vfx")
        check("50% de pixels semi-transparents -> alpha_ok=false", r_semi["alpha_ok"] is False)
        check("...donc ok=false globalement", r_semi["ok"] is False)

    print(f"\n{n - failures}/{n} assertions passées")
    return 0 if failures == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--image", type=Path, help="Chemin du PNG à valider")
    parser.add_argument("--category", choices=["ui", "character", "vfx", "decor"], help="Catégorie (§3)")
    parser.add_argument("--bands-file", type=Path, default=DEFAULT_BANDS_FILE)
    parser.add_argument("--selftest", action="store_true", help="Auto-test sur cas synthétiques, ignore --image/--category")
    args = parser.parse_args()

    if args.selftest:
        return _selftest()

    if not args.image or not args.category:
        parser.error("--image et --category sont requis (ou --selftest)")

    report = validate_image(args.image, args.category, args.bands_file)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
