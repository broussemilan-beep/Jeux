#!/usr/bin/env python3
"""experiments/blender_capture/quantize.py

Post-traitement pixel-art (Python pur : Pillow + numpy, AUCUNE
dépendance Godot/GPU) — deuxième étage du pipeline de repli Blender
(voir capture_pose.py). Porte la même logique visuelle que
experiments/bakeoff_voie_c/pixel_quantize.gdshader (pixelisation par
blocs, désaturation+quantification du Value HSV remappée dans une
bande, contour par détection de bords, dithering Bayer sur les
transitions ombre/lumière) mais calculée hors-GPU sur l'image déjà
rendue par Blender.

Différence assumée avec le shader original : le shader échantillonne
les bords/contours sur la texture haute résolution AVANT
pixelisation (texels voisins du bloc), ce script les calcule sur
l'image DÉJÀ pixelisée (pixels de sortie voisins) — plus simple, un
résultat visuellement proche mais pas un rendu identique au pixel
près. Seuils (edge_strength, dither_amount) à recalibrer à l'œil si
besoin, pas une garantie de parité exacte.

Usage :
    python3 quantize.py --in raw.png --out final.png \
        [--target_pixels=64] [--color_steps=8] \
        [--target_saturation=0.10] \
        [--value_band_min=0.165] [--value_band_max=0.90] \
        [--edge_strength=0.12] [--outline_thickness=3.0] \
        [--dither_amount=0.35]
"""

import argparse
import colorsys

import numpy as np
from PIL import Image


BAYER_4X4 = np.array([
    [0, 8, 2, 10],
    [12, 4, 14, 6],
    [3, 11, 1, 9],
    [15, 7, 13, 5],
], dtype=np.float32) / 15.0


def rgb_to_hsv_np(rgb: np.ndarray) -> np.ndarray:
    # rgb: (H, W, 3) in [0,1] -> hsv (H, W, 3) in [0,1]
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    maxc = np.max(rgb, axis=-1)
    minc = np.min(rgb, axis=-1)
    v = maxc
    delta = maxc - minc
    s = np.where(maxc > 1e-8, delta / np.maximum(maxc, 1e-8), 0.0)
    h = np.zeros_like(maxc)
    mask = delta > 1e-8
    rc = np.zeros_like(maxc)
    gc = np.zeros_like(maxc)
    bc = np.zeros_like(maxc)
    with np.errstate(divide="ignore", invalid="ignore"):
        rc = np.where(mask, (maxc - r) / np.maximum(delta, 1e-8), 0.0)
        gc = np.where(mask, (maxc - g) / np.maximum(delta, 1e-8), 0.0)
        bc = np.where(mask, (maxc - b) / np.maximum(delta, 1e-8), 0.0)
    h = np.where((maxc == r) & mask, (bc - gc), h)
    h = np.where((maxc == g) & mask, 2.0 + rc - bc, h)
    h = np.where((maxc == b) & mask, 4.0 + gc - rc, h)
    h = (h / 6.0) % 1.0
    return np.stack([h, s, v], axis=-1)


def hsv_to_rgb_np(hsv: np.ndarray) -> np.ndarray:
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    i = np.floor(h * 6.0)
    f = h * 6.0 - i
    p = v * (1.0 - s)
    q = v * (1.0 - f * s)
    t = v * (1.0 - (1.0 - f) * s)
    i = i.astype(np.int32) % 6

    r = np.select(
        [i == 0, i == 1, i == 2, i == 3, i == 4, i == 5],
        [v, q, p, p, t, v],
    )
    g = np.select(
        [i == 0, i == 1, i == 2, i == 3, i == 4, i == 5],
        [t, v, v, q, p, p],
    )
    b = np.select(
        [i == 0, i == 1, i == 2, i == 3, i == 4, i == 5],
        [p, p, t, v, v, q],
    )
    return np.stack([r, g, b], axis=-1)


def pixelate_block_center(img: np.ndarray, target_pixels: int) -> np.ndarray:
    """Échantillonne le CENTRE de chaque bloc (comme le shader d'origine
    pixel_uv, pas une moyenne de bloc) pour rester fidèle au look
    "point-sample" de pixel_quantize.gdshader.

    CONSERVÉE TELLE QUELLE (non appelée par main() depuis MANDAT
    CORRECTION PILOTE ROUND 2, voir pixelate_block_average* ci-dessous)
    car `quantize_normal.py` importe explicitement CETTE fonction pour
    downscaler les normal maps (voir son en-tête) : une normal map
    encode des vecteurs (RGB = XYZ remappé), en faire la MOYENNE sans
    renormaliser fausserait l'éclairage - le point-sampling géométrique
    reste le bon choix pour ce cas précis, aucun changement nécessaire
    ni souhaitable côté normal."""
    src_h, src_w = img.shape[0], img.shape[1]
    ys = (np.arange(target_pixels) + 0.5) / target_pixels * src_h
    xs = (np.arange(target_pixels) + 0.5) / target_pixels * src_w
    ys = np.clip(ys.astype(np.int32), 0, src_h - 1)
    xs = np.clip(xs.astype(np.int32), 0, src_w - 1)
    return img[np.ix_(ys, xs)]


def _block_bounds(target_pixels: int, src_len: int) -> list:
    """Bornes [start, end) de chaque bloc le long d'un axe - gère le cas
    non-entier (512 source / 112 cible = 4.57..., pas divisible
    proprement comme 512/64=8) par arrondi des bornes cumulées, sans
    jamais produire un bloc vide (au moins 1 pixel source)."""
    edges = (np.arange(target_pixels + 1) * src_len / target_pixels)
    edges = np.round(edges).astype(np.int64)
    edges = np.clip(edges, 0, src_len)
    bounds = []
    for i in range(target_pixels):
        a, b = int(edges[i]), int(edges[i + 1])
        if b <= a:
            b = min(a + 1, src_len)
            a = max(b - 1, 0)
        bounds.append((a, b))
    return bounds


def pixelate_block_average(img: np.ndarray, target_pixels: int) -> np.ndarray:
    """MANDAT CORRECTION PILOTE ROUND 2 (voir docs/worklog.md) : moyenne
    SIMPLE (non pondérée) de tous les pixels source de chaque bloc, au
    lieu du point-sample de `pixelate_block_center`. Corrige le défaut
    mesuré au round précédent : un contour/rim light de 1-2px de large
    a une probabilité quasi nulle d'être exactement le pixel échantillonné
    par bloc de 8×8 (ou plus), et disparaît donc entièrement après
    quantification - la moyenne de bloc capture sa contribution
    proportionnelle, quelle que soit sa position dans le bloc.

    Traite alpha comme un canal ordinaire (moyenne simple, y compris les
    pixels totalement transparents du fond) - c'est le comportement
    correct pour l'alpha : un bloc à moitié couvert par la silhouette
    doit donner une opacité de sortie ~50%, pas un choix binaire.

    Limite mesurée (voir docs/worklog.md, comparaison simple vs pondérée) :
    sur un bord net (silhouette détourée sur fond transparent), moyenner
    RGB SANS pondérer par alpha mélange la couleur du sujet avec la
    couleur RGB arbitraire des pixels de fond (souvent noir/gris sombre
    même à alpha=0 dans un PNG Blender), ce qui assombrit visiblement le
    liseré de contour (halo sombre). Voir `pixelate_block_average_alpha_
    weighted` pour la variante qui corrige ça - c'est elle qui est
    utilisée par défaut dans `main()` après comparaison mesurée."""
    src_h, src_w = img.shape[0], img.shape[1]
    y_bounds = _block_bounds(target_pixels, src_h)
    x_bounds = _block_bounds(target_pixels, src_w)
    out_shape = (target_pixels, target_pixels) + img.shape[2:]
    out = np.empty(out_shape, dtype=np.float64)
    for i, (y0, y1) in enumerate(y_bounds):
        for j, (x0, x1) in enumerate(x_bounds):
            out[i, j] = img[y0:y1, x0:x1].mean(axis=(0, 1))
    return out


def pixelate_block_average_alpha_weighted(rgb: np.ndarray, alpha: np.ndarray, target_pixels: int):
    """MANDAT CORRECTION PILOTE ROUND 2 - variante PONDÉRÉE (par alpha)
    de `pixelate_block_average` : chaque pixel source contribue à la
    moyenne RGB du bloc proportionnellement à sa propre opacité
    (moyenne "prémultipliée" puis dépondérée), pour qu'un pixel de fond
    totalement transparent ne puisse plus assombrir/décolorer la
    couleur du bloc sur un contour détouré. L'alpha du bloc de sortie
    reste une moyenne SIMPLE (pas de raison de la pondérer par
    elle-même) - identique à `pixelate_block_average`.

    Retourne (rgb_block, alpha_block) séparément (pas un seul tableau
    RGBA) car la pondération ne s'applique qu'au RGB.
    """
    src_h, src_w = rgb.shape[0], rgb.shape[1]
    y_bounds = _block_bounds(target_pixels, src_h)
    x_bounds = _block_bounds(target_pixels, src_w)
    rgb_out = np.empty((target_pixels, target_pixels, rgb.shape[2]), dtype=np.float64)
    alpha_out = np.empty((target_pixels, target_pixels), dtype=np.float64)
    for i, (y0, y1) in enumerate(y_bounds):
        for j, (x0, x1) in enumerate(x_bounds):
            a_block = alpha[y0:y1, x0:x1]
            rgb_block = rgb[y0:y1, x0:x1]
            alpha_out[i, j] = a_block.mean()
            w_sum = a_block.sum()
            if w_sum > 1e-6:
                rgb_out[i, j] = (rgb_block * a_block[..., None]).sum(axis=(0, 1)) / w_sum
            else:
                # Bloc entierement (ou quasi) transparent : la couleur
                # n'a aucun impact visuel, une moyenne simple evite un
                # NaN/une valeur non definie sans consequence sur le rendu.
                rgb_out[i, j] = rgb_block.mean(axis=(0, 1))
    return rgb_out, alpha_out


def sobel_edges(rgb: np.ndarray) -> np.ndarray:
    lum = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]
    padded = np.pad(lum, 1, mode="edge")
    gx = (
        -padded[:-2, :-2] + padded[:-2, 2:]
        - 2 * padded[1:-1, :-2] + 2 * padded[1:-1, 2:]
        - padded[2:, :-2] + padded[2:, 2:]
    )
    gy = (
        -padded[:-2, :-2] - 2 * padded[:-2, 1:-1] - padded[:-2, 2:]
        + padded[2:, :-2] + 2 * padded[2:, 1:-1] + padded[2:, 2:]
    )
    return np.sqrt(gx * gx + gy * gy)


def apply_dithering(color: np.ndarray, lum: np.ndarray, dither_amount: float,
                     dither_threshold: float, dither_color: np.ndarray,
                     shadow_sensitivity: float) -> np.ndarray:
    if dither_amount <= 0.0:
        return color
    padded = np.pad(lum, 1, mode="edge")
    grad_x = np.abs(padded[1:-1, 2:] - padded[1:-1, :-2]) * 0.5
    grad_y = np.abs(padded[2:, 1:-1] - padded[:-2, 1:-1]) * 0.5
    gradient = np.sqrt(grad_x * grad_x + grad_y * grad_y) * shadow_sensitivity
    transition = np.clip((gradient - 0.05) / (0.2 - 0.05), 0.0, 1.0)
    transition = transition * transition * (3 - 2 * transition)  # smoothstep

    h, w = lum.shape
    bayer_tile = np.tile(BAYER_4X4, (h // 4 + 1, w // 4 + 1))[:h, :w]
    threshold = dither_threshold + (bayer_tile - 0.5) * dither_amount
    is_dot = (lum >= threshold).astype(np.float32)[..., None]

    dot_color = dither_color[None, None, :] * (1 - lum[..., None]) + color * 1.2 * lum[..., None]
    dithered = dot_color * (1 - is_dot) + color * is_dot
    return color * (1 - transition[..., None]) + dithered * transition[..., None]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--in", dest="in_path", required=True)
    p.add_argument("--out", dest="out_path", required=True)
    p.add_argument("--target_pixels", type=int, default=64)
    p.add_argument(
        "--pixelate_mode", choices=["center", "mean", "mean_alpha"], default="mean_alpha",
        help=(
            "MANDAT CORRECTION PILOTE ROUND 2 (docs/worklog.md) : methode "
            "d'echantillonnage par bloc. 'center' = ancien comportement "
            "(point-sample, tel quel avant ce mandat - CONSERVE pour "
            "comparaison/regression, PAS le defaut). 'mean' = moyenne "
            "simple RGB+alpha (capture le rim light/contour fin perdu par "
            "'center', mais assombrit legerement les bords detoures - RGB "
            "du fond transparent dilue dans la moyenne). 'mean_alpha' "
            "(DEFAUT, choisi apres comparaison mesuree - voir docs/"
            "worklog.md) = moyenne RGB ponderee par alpha (meme capture "
            "du contour que 'mean', sans l'assombrissement de bord)."
        ),
    )
    p.add_argument("--color_steps", type=int, default=8)
    p.add_argument("--target_saturation", type=float, default=0.10)
    p.add_argument("--value_band_min", type=float, default=0.165)
    p.add_argument("--value_band_max", type=float, default=0.90)
    p.add_argument("--edge_strength", type=float, default=0.12)
    p.add_argument("--outline_thickness", type=float, default=3.0)
    p.add_argument("--outline_color", default="0.17,0.17,0.185")
    p.add_argument("--dither_amount", type=float, default=0.35)
    p.add_argument("--dither_threshold", type=float, default=0.5)
    p.add_argument("--dither_color", default="0.17,0.17,0.185")
    p.add_argument("--shadow_sensitivity", type=float, default=1.0)
    args = p.parse_args()

    src = Image.open(args.in_path).convert("RGBA")
    arr = np.asarray(src).astype(np.float32) / 255.0
    rgb_full = arr[..., :3]
    alpha_full = arr[..., 3]

    if args.pixelate_mode == "center":
        block = pixelate_block_center(rgb_full, args.target_pixels)
        alpha_block = pixelate_block_center(alpha_full[..., None], args.target_pixels)[..., 0]
    elif args.pixelate_mode == "mean":
        block = pixelate_block_average(rgb_full, args.target_pixels)
        alpha_block = pixelate_block_average(alpha_full[..., None], args.target_pixels)[..., 0]
    else:  # mean_alpha
        block, alpha_block = pixelate_block_average_alpha_weighted(rgb_full, alpha_full, args.target_pixels)

    hsv = rgb_to_hsv_np(block)
    hsv[..., 1] = args.target_saturation
    if args.color_steps < 32:
        step_size = 1.0 / float(args.color_steps - 1)
        step_index = np.floor(hsv[..., 2] / step_size)
        v_norm = step_index * step_size
        hsv[..., 2] = args.value_band_min + v_norm * (args.value_band_max - args.value_band_min)
    color = hsv_to_rgb_np(hsv)

    outline_rgb = np.array([float(x) for x in args.outline_color.split(",")], dtype=np.float32)
    if args.outline_thickness > 0.0:
        edges = sobel_edges(block)
        outline_intensity = np.clip(args.outline_thickness / 10.0, 0.0, 1.0)
        mask = (edges > args.edge_strength).astype(np.float32)[..., None]
        color = color * (1 - mask * outline_intensity) + outline_rgb[None, None, :] * (mask * outline_intensity)

    dither_rgb = np.array([float(x) for x in args.dither_color.split(",")], dtype=np.float32)
    lum = 0.299 * block[..., 0] + 0.587 * block[..., 1] + 0.114 * block[..., 2]
    color = apply_dithering(color, lum, args.dither_amount, args.dither_threshold,
                             dither_rgb, args.shadow_sensitivity)

    color = np.clip(color, 0.0, 1.0)
    out_arr = np.concatenate([color, alpha_block[..., None]], axis=-1)
    out_img = Image.fromarray((out_arr * 255.0 + 0.5).astype(np.uint8), mode="RGBA")
    out_img.save(args.out_path)
    print(f"QUANTIZE_RESULT out={args.out_path} size={out_img.size}")


if __name__ == "__main__":
    main()
